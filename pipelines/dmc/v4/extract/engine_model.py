"""DMC V4 binary → semantic model.

Decodes the dominant DMC V4 player's song data (see
pipelines/dmc/v4/disassembly.s for the authoritative format reference)
into engine-neutral musical structures ready for USF emission.

Design notes (all grounded in the disassembly):

- Table addresses are read from the player's PACKER-PATCHED operands
  (dataflow), never from fixed offsets.

- Sector (pattern) decoding replicates the player's exact 5-stage
  dispatch order — including the ghost path where a `$7F` byte reached
  through dispatch (i.e. NOT via the post-event peek) reads as
  "instrument 31". A sector only ENDS at the `$7F` peek that follows a
  duration-consuming event (note / rest / switch / slide).

- Sticky state (duration reload, instrument, VOL override, transpose)
  crosses sector and even track-loop boundaries. Patterns are therefore
  PATH-RESOLVED: each track entry yields a pattern instance with every
  row stamped with its effective duration/instrument/vol, and instances
  dedup by content. Track loops are unrolled until the sticky state at
  the wrap point repeats (cycle detection) — the FC loop-pickup lesson.

- The soft-start toggle ($7C) is reset at every sector end by the
  player, so it never crosses sectors; rows carry it as `noretrig`.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tools', 'py65_lib'))

from pipelines.dmc.v4.config import DMCV4Config

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


# ---------------------------------------------------------------------------
# Decoded structures
# ---------------------------------------------------------------------------

@dataclass
class DmcInstrument:
    """Semantic fields of an 11-byte V4 instrument record."""
    id: int
    ad: int
    sr: int
    pw_init_hi: int          # PW hi initial (byte2 lo nibble)
    pw_bound_a: int          # byte2 hi nibble
    pw_bound_b: int          # = bound_a EOR $0F
    pw_steps: list           # 6 effective per-phase step bytes
    pw_keep_running: bool    # flag $04
    filter_def: int          # byte6 lo nibble (meaningful iff filter_on)
    filter_on: bool          # flag $20
    filter_keep_running: bool  # flag $02
    vib_delay: int           # frames (byte7 hi nibble * 8)
    vib_width: int           # byte7 lo nibble
    vib_ramp: int            # byte8 (when not dual)
    dual: bool               # flag $40 — half-rate per-note slide
    slide_step: int          # byte8 & $7F (when dual)
    slide_dir: str           # 'up' (byte8 bit7 set) | 'down'
    gate_mode: str           # 'release_early' | 'hold' ($10) | 'open' ($08)
    drum: bool               # flag $01 — wave freq bytes are absolute
    noise_attack: bool       # flag $80 — cymbal
    wave_start: int          # byte9 (raw index into the shared wave table)
    wave_ctrl: list = field(default_factory=list)   # sliced program
    wave_freq: list = field(default_factory=list)   # parallel
    wave_loop: int = 0


@dataclass
class DmcRow:
    """One path-resolved pattern event."""
    note: int | None         # raw 0-95, or None for rest/switch rows
    duration: int            # ticks
    instr: int               # effective instrument (stamped)
    vol: int = 0             # sustain override (0 = instrument default)
    soft: bool = False       # no hard restart ($7C mode)
    gate_toggle: bool = False  # $7D SWITCH event
    glide_speed: int = 0     # 0 = no glide
    glide_to: int | None = None   # raw target note (mode 0)
    glide_slide: bool = False     # mode 1: slide current note to `note`


@dataclass
class DmcSong:
    """One subtune, fully path-resolved."""
    id: int
    speed: int
    master_vol: int
    voices: list = field(default_factory=list)   # 3 × DmcVoice


@dataclass
class DmcVoice:
    patterns: list = field(default_factory=list)     # list[list[DmcRow]]
    entries: list = field(default_factory=list)      # indices into patterns
    transposes: list = field(default_factory=list)   # signed, per entry
    loop_to: int | None = None
    stop: bool = False


@dataclass
class DmcModel:
    instruments: dict = field(default_factory=dict)  # id -> DmcInstrument
    filter_defs: dict = field(default_factory=dict)  # def# -> dict
    songs: list = field(default_factory=list)        # list[DmcSong]
    freq_lo: list = field(default_factory=list)
    freq_hi: list = field(default_factory=list)
    vibdepth: list = field(default_factory=list)     # 96 bytes incl. overlap
    d417_shadow: int = 0
    idle_notes: tuple = (0, 0, 0)    # $1012-$1014 work-file leftovers
    idle_masks: tuple = (0, 0, 0)    # $100F-$1011 gate-mask leftovers
    title: str = ''
    author: str = ''
    released: str = ''
    n_subtunes: int = 1
    start_song: int = 1


# ---------------------------------------------------------------------------
# Binary loading
# ---------------------------------------------------------------------------

def _load_image(sid_path: str):
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mem = bytearray(0x10000)
    load = s['load']
    for i, b in enumerate(s['payload']):
        if load + i < 0x10000:
            mem[load + i] = b
    return mem, s


def _rd16(mem, addr):
    return mem[addr] | (mem[addr + 1] << 8)


# ---------------------------------------------------------------------------
# Sector (pattern) simulation
# ---------------------------------------------------------------------------

class _Sticky:
    """The state that crosses sector / loop boundaries."""
    __slots__ = ('dur', 'instr', 'vol')

    def __init__(self, dur=1, instr=0, vol=0):
        self.dur, self.instr, self.vol = dur, instr, vol

    def key(self):
        return (self.dur, self.instr, self.vol)

    def copy(self):
        return _Sticky(self.dur, self.instr, self.vol)


def _simulate_sector(mem, sec_addr: int, st: _Sticky) -> list:
    """Walk one sector with the player's exact dispatch; mutate `st`;
    return the row list. The player's soft-start toggle starts at 0 in
    every sector (reset at each $7F) and is carried per-row as `soft`.
    """
    rows = []
    pos = 0
    soft = False
    guard = 0

    def peek_end():
        nonlocal pos
        if mem[sec_addr + pos] == 0x7F:
            return True
        return False

    while True:
        guard += 1
        if guard > 4096:
            raise RuntimeError(f'sector at ${sec_addr:04X} never ends')
        b = mem[sec_addr + pos]
        # stage 1: $F0+ = VOL override prefix
        if b >= 0xF0:
            st.vol = b & 0x0F
            pos += 1
            continue
        # stage 2: $7C = soft-start toggle prefix
        if b == 0x7C:
            soft = not soft
            pos += 1
            continue
        # stage 3: rest / switch / glide
        if b == 0x7E:
            rows.append(DmcRow(note=None, duration=st.dur, instr=st.instr,
                               vol=st.vol))
            pos += 1
            if peek_end():
                return rows
            continue
        if b == 0x7D:
            rows.append(DmcRow(note=None, duration=st.dur, instr=st.instr,
                               vol=st.vol, gate_toggle=True))
            pos += 1
            if peek_end():
                return rows
            continue
        if b >= 0xC0:
            speed = b & 0x0F
            if b & 0x10:             # mode 1: slide current note to target
                target = mem[sec_addr + pos + 1]
                pos += 2
                rows.append(DmcRow(note=target, duration=st.dur,
                                   instr=st.instr, vol=st.vol,
                                   glide_speed=speed, glide_slide=True))
                if peek_end():
                    return rows
                continue
            else:                    # mode 0: play A, glide to B
                a = mem[sec_addr + pos + 1]
                t = mem[sec_addr + pos + 2]
                pos += 3
                rows.append(DmcRow(note=a, duration=st.dur, instr=st.instr,
                                   vol=st.vol, soft=soft,
                                   glide_speed=speed, glide_to=t))
                if peek_end():
                    return rows
                continue
        # stage 4: duration prefix
        if b >= 0x80:
            st.dur = b & 0x3F
            pos += 1
            continue
        # stage 5: instrument prefix (NB: a dispatched $7F lands here
        # as instrument 31 — the ghost path) / note
        if b >= 0x60:
            st.instr = b & 0x1F
            pos += 1
            continue
        # note
        rows.append(DmcRow(note=b, duration=st.dur, instr=st.instr,
                           vol=st.vol, soft=soft))
        pos += 1
        if peek_end():
            return rows


def _walk_track(mem, track_addr: int, secp_lo: int, secp_hi: int) -> DmcVoice:
    """Walk one voice's track (orderlist), path-resolving every sector
    instance. Unrolls $FF loops until the sticky state at the wrap
    repeats. Returns a DmcVoice with content-deduped patterns."""
    v = DmcVoice()
    pat_key_to_id = {}
    st = _Sticky()
    transpose = 0
    pos = 0
    wrap_states = {}        # sticky key at wrap -> entry index of that wrap
    guard = 0
    while True:
        guard += 1
        if guard > 8192:
            raise RuntimeError(f'track at ${track_addr:04X} never settles')
        b = mem[track_addr + pos]
        if b == 0xFE:
            v.stop = True
            return v
        if b == 0xFF:
            key = st.key()
            if key in wrap_states:
                v.loop_to = wrap_states[key]
                return v
            wrap_states[key] = len(v.entries)
            pos = 0
            continue
        if b >= 0x80:
            # mirror the 6502: SEC SBC #$A0; on borrow EOR #$1F, ADC #$01
            if b >= 0xA0:
                transpose = b - 0xA0
            else:
                t8 = ((((b - 0xA0) & 0xFF) ^ 0x1F) + 1) & 0xFF
                transpose = t8 - 256 if t8 >= 128 else t8
            pos += 1
            b = mem[track_addr + pos]
        sec = b
        sec_addr = mem[secp_lo + sec] | (mem[secp_hi + sec] << 8)
        rows = _simulate_sector(mem, sec_addr, st)
        key = tuple((r.note, r.duration, r.instr, r.vol, r.soft,
                     r.gate_toggle, r.glide_speed, r.glide_to,
                     r.glide_slide) for r in rows)
        pid = pat_key_to_id.get(key)
        if pid is None:
            pid = len(v.patterns)
            v.patterns.append(rows)
            pat_key_to_id[key] = pid
        v.entries.append(pid)
        v.transposes.append(transpose)
        pos += 1


# ---------------------------------------------------------------------------
# Instruments / wave / filter
# ---------------------------------------------------------------------------

def _signed8(b):
    return b - 256 if b >= 128 else b


def _slice_wave(ctrl_tab: list, freq_tab: list, start: int):
    """Follow the wave table from `start` to its first jump-back byte
    (>= $90); return (ctrl, freq, loop) with the cyclic region
    normalized into the slice (see disassembly: >= $90 jumps back
    (val - $90) positions and re-reads)."""
    n = len(ctrl_tab)
    pos = start
    end = None
    while pos < n:
        if ctrl_tab[pos] >= 0x90:
            end = pos
            break
        pos += 1
    if end is None:                      # runaway — cap at table end, hold
        ctrl = ctrl_tab[start:n]
        freq = freq_tab[start:n]
        return ctrl, freq, max(0, len(ctrl) - 1)
    back = ctrl_tab[end] - 0x90
    loop_pos = end - back
    if loop_pos >= start:
        return (ctrl_tab[start:end], freq_tab[start:end], loop_pos - start)
    # loop target before the start: cycle = [loop_pos..end-1]; the
    # heard sequence is [start..end-1] then the cycle repeating, which
    # equals list [start..end-1]+[loop_pos..start-1] with loop=0.
    return (ctrl_tab[start:end] + ctrl_tab[loop_pos:start],
            freq_tab[start:end] + freq_tab[loop_pos:start], 0)


def _decode_instrument(mem, base: int, iid: int,
                       ctrl_tab, freq_tab) -> DmcInstrument:
    b = [mem[base + iid * 11 + k] for k in range(11)]
    fx = b[10]
    pw_base = b[6] >> 4
    nibs = [b[3] & 0xF0, (b[3] & 0x0F) << 4,
            b[4] & 0xF0, (b[4] & 0x0F) << 4,
            b[5] & 0xF0, (b[5] & 0x0F) << 4]
    if fx & 0x10:
        gate = 'hold'
    elif fx & 0x08:
        gate = 'open'
    else:
        gate = 'release_early'
    wc, wf, wl = _slice_wave(ctrl_tab, freq_tab, b[9])
    return DmcInstrument(
        id=iid, ad=b[0], sr=b[1],
        pw_init_hi=b[2] & 0x0F, pw_bound_a=b[2] >> 4,
        pw_bound_b=(b[2] >> 4) ^ 0x0F,
        pw_steps=[(x + pw_base) & 0xFF for x in nibs],
        pw_keep_running=bool(fx & 0x04),
        filter_def=b[6] & 0x0F, filter_on=bool(fx & 0x20),
        filter_keep_running=bool(fx & 0x02),
        vib_delay=(b[7] >> 4) * 8, vib_width=b[7] & 0x0F,
        vib_ramp=b[8], dual=bool(fx & 0x40),
        slide_step=b[8] & 0x7F, slide_dir='up' if b[8] & 0x80 else 'down',
        gate_mode=gate, drum=bool(fx & 0x01),
        noise_attack=bool(fx & 0x80), wave_start=b[9],
        wave_ctrl=wc, wave_freq=wf, wave_loop=wl)


def _decode_filter_def(mem, base: int, n: int) -> dict:
    r = [mem[base + n * 16 + k] for k in range(16)]
    return {'res': r[0] >> 4, 'mode': r[0] & 0x0F, 'init': r[1],
            'repeat': r[2], 'stop': r[3],
            'steps': [(_signed8(r[4 + k]), r[10 + k]) for k in range(6)]}


# ---------------------------------------------------------------------------
# Top-level extraction
# ---------------------------------------------------------------------------

def extract(cfg: DMCV4Config, hvsc_root: str = 'hvsc84') -> DmcModel:
    path = os.path.join(hvsc_root, cfg.sid_path)
    mem, s = _load_image(path)

    # dataflow: the packer-patched table addresses
    instr_base = _rd16(mem, cfg.op_instr)
    wavectrl = _rd16(mem, cfg.op_wavectrl)
    wavefreq = _rd16(mem, cfg.op_wavefreq)
    filtdef = _rd16(mem, cfg.op_filtdef)
    tunetab = _rd16(mem, cfg.op_tunetab)
    secp_lo = _rd16(mem, cfg.op_secp_lo)
    secp_hi = _rd16(mem, cfg.op_secp_hi)
    assert instr_base == 0x18F0, f'non-standard instrument base ${instr_base:04X}'

    n_wave = wavefreq - wavectrl
    ctrl_tab = [mem[wavectrl + i] for i in range(n_wave)]
    freq_tab = [mem[wavefreq + i] for i in range(n_wave)]

    m = DmcModel(
        freq_lo=[mem[cfg.freq_lo_addr + i] for i in range(96)],
        freq_hi=[mem[cfg.freq_hi_addr + i] for i in range(96)],
        vibdepth=[mem[cfg.vibdepth_addr + i] for i in range(96)],
        d417_shadow=mem[cfg.d417_shadow_addr],
        idle_notes=(mem[0x1012], mem[0x1013], mem[0x1014]),
        idle_masks=(mem[0x100F], mem[0x1010], mem[0x1011]),
        title=s.get('name', ''), author=s.get('author', ''),
        released=s.get('released', ''),
        n_subtunes=s.get('songs', 1), start_song=s.get('start', 1),
    )

    n_filter = (instr_base if filtdef < instr_base else tunetab)  # unused
    # decode subtunes; collect referenced instruments + filter defs as
    # they surface
    used_instr = set()
    for sub in range(m.n_subtunes):
        rec = tunetab + sub * 8
        voices = []
        for vi in range(3):
            tp = _rd16(mem, rec + vi * 2)
            voices.append(_walk_track(mem, tp, secp_lo, secp_hi))
        song = DmcSong(id=sub + 1, speed=mem[rec + 6],
                       master_vol=mem[rec + 7], voices=voices)
        m.songs.append(song)
        for v in voices:
            for rows in v.patterns:
                for r in rows:
                    used_instr.add(r.instr)

    # The engine's note-init cache is cleared to 0 by init, so a voice
    # idling before its first note runs record 0's pulse/wave mechanism.
    # Record 0 must therefore always ship (and sit first in the list).
    used_instr.add(0)
    for iid in sorted(used_instr):
        inst = _decode_instrument(mem, instr_base, iid, ctrl_tab, freq_tab)
        m.instruments[iid] = inst
        if inst.filter_on:
            d = inst.filter_def
            if d not in m.filter_defs:
                m.filter_defs[d] = _decode_filter_def(mem, filtdef, d)
    _offtable_check(m)
    return m


def _offtable_check(m: DmcModel) -> None:
    """Certify reachable off-table reads. The original reads past its
    96-entry freq tables into the engine state block; the composer
    mirrors the STABLE prefix of that window (track-ptr slots excluded,
    constants + speed + master vol included, k = 6..16). Reads landing
    on live state (k >= 17) or the track-ptr slots (k <= 5) cannot be
    reproduced without mirroring the original's whole runtime state —
    flagged unsupported. Vibdepth overrun (note > 95 at note init,
    reading into the instrument records) is likewise flagged."""
    ks = set()
    vib = set()

    def add_note(n, inst):
        if n > 95:
            vib.add(n)              # note-load freq read + vibdepth read
            ks.add(n - 96)
        if inst is not None and not inst.drum:
            for off in inst.wave_freq:
                y = (n + off) & 0xFF
                if y > 95:
                    ks.add(y - 96)

    for song in m.songs:
        for vi, v in enumerate(song.voices):
            # (idle-path reads before a voice's first hard note are NOT
            # certified here: they land on early-song state that is
            # still zero — matching the composer's zero window — and
            # the verify gate catches the rare exception.)
            for ei, e in enumerate(v.entries):
                tr = v.transposes[ei] if v.transposes else 0
                for r in v.patterns[e]:
                    inst = m.instruments.get(r.instr)
                    if r.note is not None:
                        add_note(r.note + tr, inst)
                    if r.glide_to is not None:
                        add_note(r.glide_to + tr, inst)
    bad = sorted(k for k in ks if k <= 5 or k >= 17)
    if bad:
        raise RuntimeError(f'unsupported:offtable_live k={bad[:8]}')
    if vib:
        raise RuntimeError(f'unsupported:offtable_vibdepth n={sorted(vib)[:8]}')
