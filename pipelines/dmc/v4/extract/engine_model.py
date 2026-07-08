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
    pw_bound_a: int          # byte2 >> pulse-bound shift (canon 4 = hi nibble)
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
    wave_pool_pos: int | None = None  # table position of the program's first
                                      # step (== wave_start unless byte9 sits
                                      # on the own-end marker); set only when
                                      # DmcModel.wavepos_layout fires
    wave_ctrl: list = field(default_factory=list)   # sliced program
    wave_freq: list = field(default_factory=list)   # parallel
    wave_loop: int = 0
    # off-table arpeggio frequencies (the v5 `offtable_freq` form, ported to
    # v4): per (wave-program offset, played note) the explicit (lo, hi) the freq
    # read produces when `(note + offset) & $FF` runs past the 96-entry table.
    # idx = (offset + note) & $FF; entry = (offset, note, lo, hi). Replaces the
    # conservative `offtable_live` rejection for the STABLE-when-read reads.
    offtable_freq: list = field(default_factory=list)
    # The editor placed wave byte9 ON this program's own loop marker
    # ($90+n, loop 0): the engine chases it back n on the first read every
    # note-init, writing the shared $171F scratch (= n). Set only for members
    # whose off-table freq reads sonify $171F (the wjmp window); the composer
    # then re-asserts wjmp=n at note-init. See extract() + composer wchase.
    wave_start_on_marker: bool = False


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
    # STATED-command flags: this editor row physically carries a duration /
    # instrument / volume command (or N soft-start toggles) in the sector
    # bytes — the composer's command PLACEMENT (arrangement, §8), incl. the
    # redundant re-statements that a value-change derivation cannot see.
    # Consumed by the sectpos shadow ($1729,x = per-byte sector position,
    # read off-table): per-row byte width = base(kind) + stated commands.
    dcmd: bool = False       # $80-$BF duration command on this row
    icmd: bool = False       # $60-$7B instrument command on this row
    vcmd: bool = False       # $Fx volume/sustain command on this row
    softcmd: int = 0         # count of $7C soft-start toggles on this row


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
    entry_offsets: list = field(default_factory=list)  # orig track byte offset
                                                     # of each entry's sector
                                                     # byte (walk-time ground
                                                     # truth for otrk_pad)
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
    # off-table vibrato-depth reads (note > 95): {note: depth} — the value the
    # engine reads past the 96-entry vibdepth table (lands on static instr
    # records). The vibdepth analog of offtable_freq.
    offtable_vibdepth: dict = field(default_factory=dict)
    d417_shadow: int = 0
    dual_phase: int = 0              # $1019 leftover & 1 — initial phase
                                     # of the half-rate slide clock
    cia_period: int = 0              # CIA1 timer A latch (multispeed); 0=VBI
    play_repeat: int = 1             # INTERNAL multispeed: the play wrapper
                                     # JSRs the inner play N x per VBI with NO
                                     # PSID speed bit (vblank-dispatched). 1=once.
    family2: bool = False            # the V4-derived family-2 build
    extra_params: dict = field(default_factory=dict)  # factory-probed knobs
    wavepos_layout: bool = False     # an off-table freq read sonifies a live
                                     # wave position ($177A-$177C) AND every
                                     # wave program is a verbatim contiguous
                                     # slice of the orig table: carry each
                                     # instrument's editor wave-table position
                                     # so the composer packs its pool at the
                                     # orig positions (wavepos == orig $177A)
    idle_wave: tuple = ((), (), 0)   # wave walk from table index 0 (the
                                     # cleared-cache idle path): ctrl,
                                     # freq, loop
    idle_notes: tuple = (0, 0, 0)    # $1012-$1014 work-file leftovers
    idle_masks: tuple = (0, 0, 0)    # $100F-$1011 gate-mask leftovers
    idle_guards: tuple = (0, 0, 0)   # $1786-$1788 post-note-guard leftovers
    durrel_init: tuple = (0, 0, 0)   # $173E-$1740 duration-reload leftovers
                                     # (init never writes $173E; the leftover
                                     # is read via off-table freq idx 247-249
                                     # lo / 151-153 hi until the voice's first
                                     # event stores its row duration)
                                     # (uncleared until the voice's first
                                     # note-init; sonified by off-table reads)
    title: str = ''
    author: str = ''
    released: str = ''
    clock: str = 'PAL'               # PSID header clock flag (audio metadata)
    sid_model: int = 6581            # PSID header SID model — the write-log
                                     # verdict is BLIND to this; a 6581 build
                                     # of an 8580 tune sounds wrong (filters)
    n_subtunes: int = 1
    start_song: int = 1


# ---------------------------------------------------------------------------
# Binary loading
# ---------------------------------------------------------------------------

def _hdr_flags(sid_path: str) -> int:
    """PSID v2+ header flags word (0 for v1/RSID-without-flags)."""
    with open(sid_path, 'rb') as f:
        b = f.read(0x78)
    if len(b) < 0x78 or int.from_bytes(b[4:6], 'big') < 2:
        return 0
    return int.from_bytes(b[0x76:0x78], 'big')


def _hdr_clock(sid_path: str) -> str:
    return {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[
        (_hdr_flags(sid_path) >> 2) & 3]


def _hdr_sid_model(sid_path: str):
    # int 6581/8580, or the strings the USF psid block also admits —
    # lossless round-trip of the orig header flag
    return {0: 0, 1: 6581, 2: 8580, 3: 'both'}[
        (_hdr_flags(sid_path) >> 4) & 3]


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


def _postinit_window(s, lo: int, n: int):
    """Bytes [lo, lo+n) AFTER running the member's init under py65 (subtune =
    start song). Some inits REWRITE static data the extract reads from the
    file image (e.g. the 'Ed' members' init stamps res/mode + initial cutoff
    over every filter def record) — the engine then reads the rewritten bytes,
    so the file-image capture is wrong. Returns None when py65 can't complete
    the init (C9 territory; caller keeps the file image)."""
    try:
        from py65.devices.mpu6502 import MPU
        mpu = MPU()
        load = s['load']
        for i, b in enumerate(s['payload']):
            if load + i < 0x10000:
                mpu.memory[load + i] = b
        mpu.stPush(0x00)
        mpu.stPush(0x00)             # RTS sentinel -> PC = $0001
        mpu.pc = s['init']
        mpu.a = (s.get('start', 1) or 1) - 1
        for _ in range(1_000_000):
            if mpu.pc == 0x0001:
                return [mpu.memory[(lo + k) & 0xFFFF] for k in range(n)]
            mpu.step()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Sector (pattern) simulation
# ---------------------------------------------------------------------------

class _Sticky:
    """The state that crosses sector / loop boundaries.

    The duration reload defaults to 0, NOT 1: the note-load reads the duration
    reload from $173E,x, and the engine's INIT clears $1718-$179D (which spans
    $173E-$1740) to 0 — so a first note reached before any sector $80-$BF
    duration command plays for reload 0 (the counter DECs 0->$FF, i.e. a held
    256-tick note), not 1. The old default 1 gave such notes a too-short life,
    hitting the track terminator one play early and dropping a frame (e.g.
    Klepkomania's single-note decorative subtunes)."""
    __slots__ = ('dur', 'instr', 'vol')

    def __init__(self, dur=0, instr=0, vol=0):
        self.dur, self.instr, self.vol = dur, instr, vol

    def key(self):
        return (self.dur, self.instr, self.vol)

    def copy(self):
        return _Sticky(self.dur, self.instr, self.vol)


@dataclass
class _SecFmt:
    """Sector-command byte map. canon V4 and the family-2 V4-derived
    build share the engine but remap the command bytes (family 2 moves
    the terminator to $FF, drops VOL + soft-start, extends the
    instrument range to $7F). The terminator is only checked in the
    post-event PEEK — a terminator reached via DISPATCH is the ghost
    path (canon $7F → instr 31; family2 $FF → glide), preserved by
    letting it fall through to its range."""
    term: int = 0x7F                 # sector terminator (peeked)
    rest: int = 0x7E
    switch: int = 0x7D
    soft: 'int | None' = 0x7C        # soft-start toggle ($7C); None = none
    vol_min: 'int | None' = 0xF0     # VOL prefix range start; None = none
    instr_lo: int = 0x60
    glide_min: int = 0xC0
    dur_min: int = 0x80


_SECFMT = {
    'v4': _SecFmt(),
    'family2': _SecFmt(term=0xFF, rest=0xFE, switch=0xFD, soft=None,
                       vol_min=None),
}


def _simulate_sector(mem, sec_addr: int, st: _Sticky,
                     fmt: _SecFmt = _SECFMT['v4']) -> list:
    """Walk one sector with the player's dispatch; mutate `st`; return
    the row list. Parametric over `fmt` (the command byte map).

    The player's sector position is ONE byte (`LDY $1729,x / LDA ($f8),y`),
    so a sector with no terminator wraps mod 256 and plays forever — the
    voice never fetches another track entry (ledger C11: mirror the 8-bit
    wrap). Seen on header-overstated subtunes whose garbage track selects a
    sector number past the real pointer table (address $0000, zero fill).
    For that case the walk detects the wrapped cycle by (pos, sticky, soft,
    pending-prefix) state repeat and returns `('endless', lead, period)` —
    the rows before the first repeated state, and one full period. A
    terminated sector never revisits a loop-top state (pos is strictly
    increasing until the terminator), so the terminated path is untouched."""
    rows = []
    pos = 0
    soft = False
    guard = 0
    seen = {}               # loop-top (pos, sticky, soft, pending) -> len(rows)
    # pending STATED-command flags: prefix bytes consumed since the last row
    # event belong to the NEXT row's fetch (each INCs $1729,x). Recorded as
    # byte FACTS of the sector (not change-vs-sticky), so the same sector
    # always yields the same flags regardless of entry context.
    p_d = p_i = p_v = False
    p_s = 0

    def _take():
        nonlocal p_d, p_i, p_v, p_s
        d, i, v, s = p_d, p_i, p_v, p_s
        p_d = p_i = p_v = False
        p_s = 0
        return {'dcmd': d, 'icmd': i, 'vcmd': v, 'softcmd': s}

    def rd(off):
        return mem[sec_addr + (off & 0xFF)]     # 8-bit sectpos, as the player

    def peek_end():
        return rd(pos) == fmt.term

    while True:
        guard += 1
        if guard > 4096:
            # no terminator within bounds: the secp table / track points
            # at non-sector data (a corrupt or differently-laid-out
            # member). Refuse cleanly rather than crash.
            raise RuntimeError(
                f'unsupported:sector_decode no end at ${sec_addr:04X}')
        pos &= 0xFF
        key = (pos, st.key(), soft, p_d, p_i, p_v, p_s)
        if key in seen:
            i = seen[key]
            return ('endless', rows[:i], rows[i:])
        seen[key] = len(rows)
        b = rd(pos)
        # VOL prefix (canon $F0+; family 2 has none)
        if fmt.vol_min is not None and b >= fmt.vol_min:
            st.vol = b & 0x0F
            p_v = True
            pos += 1
            continue
        # soft-start toggle (canon $7C; family 2 has none)
        if fmt.soft is not None and b == fmt.soft:
            soft = not soft
            p_s += 1
            pos += 1
            continue
        # rest / switch (exact bytes, checked before the glide range so
        # family 2's $FE/$FD are caught above $C0)
        if b == fmt.rest:
            rows.append(DmcRow(note=None, duration=st.dur, instr=st.instr,
                               vol=st.vol, **_take()))
            pos += 1
            if peek_end():
                return rows
            continue
        if b == fmt.switch:
            rows.append(DmcRow(note=None, duration=st.dur, instr=st.instr,
                               vol=st.vol, gate_toggle=True, **_take()))
            pos += 1
            if peek_end():
                return rows
            continue
        # glide / slide
        if b >= fmt.glide_min:
            speed = b & 0x0F
            if b & 0x10:             # mode 1: slide current note to target
                target = rd(pos + 1)
                pos += 2
                rows.append(DmcRow(note=target, duration=st.dur,
                                   instr=st.instr, vol=st.vol,
                                   glide_speed=speed, glide_slide=True,
                                   **_take()))
                if peek_end():
                    return rows
                continue
            else:                    # mode 0: play A, glide to B
                a = rd(pos + 1)
                t = rd(pos + 2)
                pos += 3
                rows.append(DmcRow(note=a, duration=st.dur, instr=st.instr,
                                   vol=st.vol, soft=soft,
                                   glide_speed=speed, glide_to=t,
                                   **_take()))
                if peek_end():
                    return rows
                continue
        # duration prefix
        if b >= fmt.dur_min:
            st.dur = b & 0x3F
            p_d = True
            pos += 1
            continue
        # instrument prefix (a dispatched terminator falls here for
        # canon = instr 31, the ghost path) / note
        if b >= fmt.instr_lo:
            st.instr = b & 0x1F
            p_i = True
            pos += 1
            continue
        # note
        rows.append(DmcRow(note=b, duration=st.dur, instr=st.instr,
                           vol=st.vol, soft=soft, **_take()))
        pos += 1
        if peek_end():
            return rows


def _walk_track(mem, track_addr: int, secp_lo: int, secp_hi: int,
                loop_target: bool = False,
                fmt: _SecFmt = _SECFMT['v4']) -> DmcVoice:
    """Walk one voice's track (orderlist), path-resolving every sector
    instance. Unrolls $FF loops until (wrap position, sticky state)
    repeats. `loop_target`: the JSR-$1042 player variant reads the byte
    after $FF as the loop position (canonical loops to 0).

    The engine's track position is ONE byte (`LDY $1726,x` / `INC $1726,x`),
    so a track with no $FF/$FE terminator wraps mod 256 in hardware and the
    walk becomes a 256-byte loop (ledger C11: mirror the 8-bit index wrap in
    the extractor). Seen on header-overstated subtunes (Bayliss: PSID says 6
    songs, the tune table has 1 real record; subtunes 1-5 point at zero-fill
    and march sector 0 forever). The wrap is a NO-OP for every track that
    terminates before pos 256 — a real track walking past 255 unwrapped
    could never have verified — and the mod-256 cycle detection engages only
    after an actual wrap, so terminated tracks take the exact old path."""
    v = DmcVoice()
    pat_key_to_id = {}
    st = _Sticky()
    transpose = 0
    pos = 0
    wrap_states = {}        # (pos, sticky) at wrap -> entry index
    mod_states = {}         # (pos, sticky, transpose) after a mod-256 wrap
    wrapped = False
    guard = 0
    while True:
        guard += 1
        if guard > 8192:
            raise RuntimeError(f'track at ${track_addr:04X} never settles')
        if pos > 0xFF:                 # 8-bit otrk: wrap like the hardware
            pos &= 0xFF
            wrapped = True
        if wrapped:
            key = (pos, st.key(), transpose)
            if key in mod_states:
                v.loop_to = mod_states[key]
                return v
            mod_states[key] = len(v.entries)
        b = mem[track_addr + pos]
        if b == 0xFE:
            v.stop = True
            return v
        if b == 0xFF:
            tgt = mem[track_addr + ((pos + 1) & 0xFF)] if loop_target else 0
            key = (tgt, st.key())
            if key in wrap_states:
                v.loop_to = wrap_states[key]
                return v
            wrap_states[key] = len(v.entries)
            pos = tgt
            continue
        if b >= 0x80:
            # mirror the 6502: SEC SBC #$A0; on borrow EOR #$1F, ADC #$01
            if b >= 0xA0:
                transpose = b - 0xA0
            else:
                t8 = ((((b - 0xA0) & 0xFF) ^ 0x1F) + 1) & 0xFF
                transpose = t8 - 256 if t8 >= 128 else t8
            pos += 1
            if pos > 0xFF:
                pos &= 0xFF
                wrapped = True
            b = mem[track_addr + pos]
        sec = b
        v.entry_offsets.append(pos)
        sec_addr = mem[secp_lo + sec] | (mem[secp_hi + sec] << 8)
        rows = _simulate_sector(mem, sec_addr, st, fmt)
        if isinstance(rows, tuple) and rows[0] == 'endless':
            # unterminated sector (8-bit sectpos wrap): the voice never
            # leaves it — encode lead rows (once) + one period, self-loop.
            _, lead, period = rows
            for chunk in ([lead] if lead else []) + [period]:
                v.patterns.append(chunk)
                v.entries.append(len(v.patterns) - 1)
                v.transposes.append(transpose)
            v.loop_to = len(v.entries) - 1
            return v
        key = tuple((r.note, r.duration, r.instr, r.vol, r.soft,
                     r.gate_toggle, r.glide_speed, r.glide_to,
                     r.glide_slide, r.dcmd, r.icmd, r.vcmd, r.softcmd)
                    for r in rows)
        pid = pat_key_to_id.get(key)
        if pid is None:
            pid = len(v.patterns)
            v.patterns.append(rows)
            pat_key_to_id[key] = pid
        v.entries.append(pid)
        v.transposes.append(transpose)
        pos += 1


def _loops_offimage(mem, secp_lo: int, secp_hi: int, tunetab: int,
                    n_sub: int, load: int, loop_target: bool) -> bool:
    """Does any voice's track LOOP to a sector whose pointer resolves BELOW the
    load address (out of the file image)?

    Such a sector reads RAM the file image doesn't hold — for the '$0000' case
    (a $FF loop into a garbage sector number past the pointer table → $0000) the
    engine sonifies live ZEROPAGE as note data (the 6510 I/O port $2F/$37 at
    offset 0/1, then static zp). The file image is all-zero there, so the naive
    decode is note-0-forever; the extract must instead read the runtime low RAM.
    This is the detector that gates that capture. Follows each $FF once (mirrors
    _walk_track) and reports on the FIRST out-of-image sector it reaches; a
    normal in-image track returns False immediately (byte-identical build)."""
    for sub in range(n_sub):
        rec = tunetab + sub * 8
        for vi in range(3):
            tp = _rd16(mem, rec + vi * 2)
            pos = 0
            guard = 0
            seen_loop = set()
            while guard < 1024:
                guard += 1
                pos &= 0xFF
                b = mem[(tp + pos) & 0xFFFF]
                if b == 0xFE:
                    break
                if b == 0xFF:
                    tgt = mem[(tp + ((pos + 1) & 0xFF)) & 0xFFFF] if loop_target \
                        else 0
                    if tgt in seen_loop:
                        break
                    seen_loop.add(tgt)
                    pos = tgt
                    continue
                if b >= 0x80:              # transpose byte, not a sector number
                    pos += 1
                    continue
                sec_addr = mem[(secp_lo + b) & 0xFFFF] | \
                    (mem[(secp_hi + b) & 0xFFFF] << 8)
                if sec_addr < load:
                    return True
                pos += 1
    return False


# ---------------------------------------------------------------------------
# Instruments / wave / filter
# ---------------------------------------------------------------------------

def _signed8(b):
    return b - 256 if b >= 128 else b


def _slice_wave(ctrl_tab: list, freq_tab: list, start: int, n_inbound=None):
    """Follow the wave table from `start` to its first jump-back byte
    (>= $90); return (ctrl, freq, loop) with the cyclic region
    normalized into the slice (see disassembly: >= $90 jumps back
    (val - $90) positions and re-reads).

    `ctrl_tab`/`freq_tab` may be EXTENDED past the wave table (covering the
    bytes the original reads when an instrument's wave_start sits past the
    table — an off-table WAVE read, the wave analogue of off-table freq).
    `n_inbound` is the real wave-table size: an IN-TABLE start (< n_inbound)
    is sliced bounded to n_inbound, byte-identical to the unextended call (so
    no built member regresses); an OFF-TABLE start (>= n_inbound) is sliced
    over the full extended length, capturing the off-table program. Defaults
    to len(ctrl_tab) (the unextended single-table behaviour)."""
    if n_inbound is None:
        n_inbound = len(ctrl_tab)
    # In-table slices stay bounded to the real table (today's behaviour);
    # off-table slices use the extended window.
    n = n_inbound if start < n_inbound else len(ctrl_tab)
    # OFF-table starts are resolved by simulating the engine's wave-position
    # walk (markers hop back and re-read, possibly multi-hop) until the walk
    # SETTLES into a loop — recovering the flat program even when the chain
    # re-enters a marker (Jim inst 10: off-table bytes then a 1-step ping-pong
    # = a sustained byte). The in-table path below is the proven, byte-identical
    # slice (no built member regresses).
    if start >= n_inbound:
        return _resolve_wave_chain(ctrl_tab, freq_tab, start)
    # a start sitting on a marker re-dispatches immediately (the
    # original checks the marker before reading) — follow the chain
    guard = 0
    while start < n and ctrl_tab[start] >= 0x90:
        back = ctrl_tab[start] - 0x90
        if back == 0:
            raise RuntimeError(f'unsupported:wave_marker_chain @{start}')
        if start - back < 0:
            # the engine's SBC is 8-bit: the hop UNDERFLOWS and wraps to a
            # high position in the 256-byte read window (Cool_Compo_Tune:
            # marker $FF at pos $26 -> $B7). Resolve by simulating the
            # mod-256 walk over the extended window.
            return _resolve_wave_chain(ctrl_tab, freq_tab, start)
        start -= back
        guard += 1
        if guard > 64:
            raise RuntimeError('unsupported:wave_marker_chain loop')
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
    if loop_pos < 0:
        # 8-bit underflow: the engine wraps to a high window position and
        # keeps playing from there (NOT a Python negative slice — that read
        # the extended table's TAIL, garbage far past the real window).
        # Simulate the mod-256 walk instead (family-1 deep-tail round 18).
        return _resolve_wave_chain(ctrl_tab, freq_tab, start)
    if loop_pos >= start:
        return (ctrl_tab[start:end], freq_tab[start:end], loop_pos - start)
    # loop target before the start: cycle = [loop_pos..end-1]; the
    # heard sequence is [start..end-1] then the cycle repeating, which
    # equals list [start..end-1]+[loop_pos..start-1] with loop=0.
    if any(b >= 0x90 for b in ctrl_tab[loop_pos:start]):
        # the pre-start region holds ANOTHER marker (chained hop, e.g.
        # $94 -> $91 -> settle) — the flat concatenation would emit the
        # marker byte as a step; simulate the engine's walk instead
        # (Tichelmann_03 inst 12: [$14,$14,$14,$94] settles on $41/hold).
        return _resolve_wave_chain(ctrl_tab, freq_tab, start)
    return (ctrl_tab[start:end] + ctrl_tab[loop_pos:start],
            freq_tab[start:end] + freq_tab[loop_pos:start], 0)


def _resolve_wave_chain(ctrl_tab: list, freq_tab: list, start: int):
    """Flatten an OFF-table wave read by SIMULATING the engine's wave-position
    walk: each step resolves markers (>= $90 hops back val-$90 and re-reads,
    possibly several times), then emits (ctrl, freq) at the settled position
    and advances +1. The walk SETTLES into a loop once it revisits a position
    already emitted — that revisit is the loop point. Returns (ctrl, freq, loop)
    or raises wave_marker_chain for a degenerate chain (hops out of range, or
    no settle within the guard). This recovers chains the flat slicer can't —
    e.g. Jim inst 10: [$0D,$08,$06,$04,$02,$00] then a $FF->$91 hop pair that
    ping-pongs index 4<->5 = a sustained $11 (program loops on the final byte).
    """
    n = len(ctrl_tab)
    ctrl, freq = [], []
    seen = {}                       # settled position -> emit index (loop pt)
    # The engine's wave position is an 8-BIT byte (INC $177A,x wraps
    # $FF -> $00; the marker hop SBC wraps too) — so the walk is mod 256
    # (ledger C11: 8-bit index wrap, the wave-walk instance). Attah_2 inst 22:
    # wave_start $FF reads (ctrl $03, +17) then WRAPS to $00 for the real
    # program [(41,+0)] loop; the old linear walk read past index 255 into
    # the extended window and produced a bogus program. Positions are
    # wrapped; reads stay within the first 256 bytes of the window.
    pos = start & 0xFF
    for _ in range(512):
        hops = 0
        while pos < min(n, 256) and ctrl_tab[pos] >= 0x90:
            pos = (pos - (ctrl_tab[pos] - 0x90)) & 0xFF
            hops += 1
            if hops > 128:
                raise RuntimeError(f'unsupported:wave_marker_chain @{start}')
        if pos >= min(n, 256):       # beyond the readable window -> hold
            break
        if pos in seen:
            return ctrl, freq, seen[pos]
        seen[pos] = len(ctrl)
        ctrl.append(ctrl_tab[pos])
        freq.append(freq_tab[pos])
        pos = (pos + 1) & 0xFF
    if not ctrl:
        raise RuntimeError(f'unsupported:wave_marker_chain @{start}')
    return ctrl, freq, max(0, len(ctrl) - 1)


def _decode_instrument(mem, base: int, iid: int,
                       ctrl_tab, freq_tab, n_inbound=None,
                       pw_bound_shift: int = 4) -> DmcInstrument:
    # the player computes the record offset in the 8-bit accumulator
    # ($1213-$121F: CLC / ASL x3 / ADC #n x3), so it WRAPS mod 256 — but NOT
    # as a clean (iid*11) & 0xFF: the CLC runs only once, so a carry out of
    # an INTERMEDIATE ADC feeds the NEXT one (+1). E.g. iid=26: $D0+$1A=$EA,
    # $EA+$1A=$104 -> A=$04 c=1, $04+$1A+1 = $1F (31), where (26*11)&$FF
    # gives 30 (Techno's V1 first-note class, family-1 round 16). And a
    # final ASL carry-out feeds the FIRST ADC (iid >= 32). Emulate the exact
    # 6502 chain. iid 0-23 (offset < 256, no wraps) are unaffected.
    off = iid
    c = 0
    for _ in range(3):
        c = (off >> 7) & 1
        off = (off << 1) & 0xFF
    for _ in range(3):
        off = off + iid + c
        c = 1 if off > 0xFF else 0
        off &= 0xFF
    b = [mem[base + off + k] for k in range(11)]
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
    wc, wf, wl = _slice_wave(ctrl_tab, freq_tab, b[9], n_inbound)
    return DmcInstrument(
        id=iid, ad=b[0], sr=b[1],
        pw_init_hi=b[2] & 0x0F, pw_bound_a=b[2] >> pw_bound_shift,
        pw_bound_b=(b[2] >> pw_bound_shift) ^ 0x0F,
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
    # INIT-UNPACKER member (factory-detected): every data table lives
    # OUTSIDE the loaded image, generated by init in high RAM. The bytes
    # the engine reads are the post-init RAM, so extract from that — the
    # file image has nothing at the table addresses. (Priming reads —
    # d417 shadow, idle notes/masks — likewise come out post-init, which
    # is exactly the state the play loop starts from.)
    if getattr(cfg, 'data_post_init', False):
        post = _postinit_window(s, 0, 0x10000)
        assert post is not None, \
            'init-unpacker member: py65 could not complete init'
        mem = bytearray(post)

    # dataflow: the packer-patched table addresses
    instr_base = _rd16(mem, cfg.op_instr)
    wavectrl = _rd16(mem, cfg.op_wavectrl)
    wavefreq = _rd16(mem, cfg.op_wavefreq)
    filtdef = _rd16(mem, cfg.op_filtdef)
    tunetab = _rd16(mem, cfg.op_tunetab)
    secp_lo = _rd16(mem, cfg.op_secp_lo)
    secp_hi = _rd16(mem, cfg.op_secp_hi)
    # canon/2-entry put the instrument table at base+$8F0; family 2
    # relocates it ($17B0). Trust the operand read, bounded to the
    # LOADED IMAGE as a sanity floor (the factory validates the player
    # identity separately; the verify gates a mislocation). Members with a
    # data prefix below the player put the table there (Mothafucka_2SID:
    # load $0900, instruments at $0A00 — a genuine record array).
    assert s['load'] <= instr_base < 0x10000, \
        f'non-standard instrument base ${instr_base:04X}'

    n_wave = wavefreq - wavectrl
    # Extend the read window past the wave table so an instrument whose
    # wave_start sits past it (an off-table WAVE read — the wave analogue of
    # off-table freq) is sliced from the bytes the original actually reads
    # (the freq table + following data region). _slice_wave bounds IN-table
    # starts to n_wave (byte-identical to the unextended slice), so the
    # extension only affects the previously-refused off-table instruments.
    ext = min(0x10000 - max(wavectrl, wavefreq), max(n_wave, 0) + 0x180)
    ctrl_tab = [mem[wavectrl + i] for i in range(ext)]
    freq_tab = [mem[wavefreq + i] for i in range(ext)]

    b = cfg.base
    # idle note / gate-mask = the file-image initial values of the per-voice
    # curnote / gatemask STATE blocks. Canon: base+0x12 / base+0x0F; a
    # re-assembled variant lays them out differently and the dataflow extractor
    # LOCATES them (cfg.curnote_addr / cfg.gatemask_addr) — fall back to canon.
    cn = cfg.curnote_addr if cfg.curnote_addr is not None else b + 0x12
    gm = cfg.gatemask_addr if cfg.gatemask_addr is not None else b + 0x0F
    dp = (getattr(cfg, 'dual_parity_addr', None)
          if getattr(cfg, 'dual_parity_addr', None) is not None
          else b + 0x19)
    # Leftover priming: prefer the factory's POST-INIT capture (dataflow /
    # re-assembled members whose init may clear these bytes — canon init
    # provably never touches them, so canon has no post_init_state and
    # keeps reading the file image).
    pis = getattr(cfg, 'post_init_state', None) or {}
    m = DmcModel(
        freq_lo=[mem[cfg.freq_lo_addr + i] for i in range(96)],
        freq_hi=[mem[cfg.freq_hi_addr + i] for i in range(96)],
        vibdepth=[mem[cfg.vibdepth_addr + i] for i in range(96)],
        d417_shadow=pis.get('d417_shadow', mem[cfg.d417_shadow_addr]),
        idle_notes=tuple(pis.get('idle_notes',
                                 (mem[cn], mem[cn + 1], mem[cn + 2]))),
        idle_masks=tuple(pis.get('idle_masks',
                                 (mem[gm], mem[gm + 1], mem[gm + 2]))),
        idle_guards=tuple(pis.get('idle_guards',
                                  (mem[b + 0x786], mem[b + 0x787],
                                   mem[b + 0x788]))),
        durrel_init=tuple(pis.get('durrel_init',
                                  (mem[b + 0x73E], mem[b + 0x73F],
                                   mem[b + 0x740]))),
        dual_phase=pis.get('dual_phase', mem[dp] & 1),
        cia_period=cfg.cia_period,
        play_repeat=cfg.play_repeat,
        title=s.get('name', ''), author=s.get('author', ''),
        released=s.get('released', ''),
        clock=_hdr_clock(path), sid_model=_hdr_sid_model(path),
        n_subtunes=s.get('songs', 1), start_song=s.get('start', 1),
    )

    m.idle_wave = _slice_wave(ctrl_tab, freq_tab, 0, n_wave)

    # OUT-OF-IMAGE loop sector ($0000 bucket): a $FF track loop lands on a
    # garbage sector number past the pointer table whose pointer is $0000, so
    # the sector reads live ZEROPAGE as note data. The file image is all-zero
    # below the load address, so the naive decode is note-0-forever; the engine
    # actually plays the 6510 I/O port ($00=$2F DDR, $01=$37 port under the PSID
    # environment) then static zp bytes. Capture that low RAM from libsidplayfp
    # (py65 can't reproduce the environment's zeropage — ledger C9) and overlay
    # it so _walk_track / _simulate_sector read what the engine reads (C26: read
    # the runtime RAM, not the image). Gated on an out-of-image loop, so every
    # in-image track is byte-identical (the overlay only touches $00-$FF, which
    # nothing else reads). Regression-safe by construction: a played out-of-image
    # sector was always mis-decoded (image zeros != runtime), so any member this
    # changes was already non-FULL; an unplayed sector's decode never reaches the
    # write-log.
    if _loops_offimage(mem, secp_lo, secp_hi, tunetab, s.get('songs', 1),
                       s['load'], cfg.track_loop_target):
        zpvals = _postinit_values(path, list(range(0x100)))
        for a in range(0x100):
            mem[a] = zpvals.get(a, 0)
        # 6510 processor port: reads return the port register, not RAM. Standard
        # PSID reset = DDR $2F / port $37 (this tune never banks; confirmed by
        # pc-trace [0000]{2f}/[0001]{37}).
        mem[0x00], mem[0x01] = 0x2F, 0x37
        # the sector pointer ($F8/$F9) holds the sector base ($0000) during the
        # read, so those two offsets read $00 (not the post-play snapshot value).
        mem[0xF8], mem[0xF9] = 0x00, 0x00

    # decode subtunes; collect referenced instruments + filter defs as
    # they surface
    used_instr = set()
    for sub in range(m.n_subtunes):
        rec = tunetab + sub * 8
        voices = []
        for vi in range(3):
            tp = _rd16(mem, rec + vi * 2)
            voices.append(_walk_track(mem, tp, secp_lo, secp_hi,
                                      loop_target=cfg.track_loop_target,
                                      fmt=_SECFMT[cfg.sector_format]))
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
    # PWM bound-A extraction shift: canon note-init does LSR x4 (bound A =
    # byte+2 hi nibble); a wedge variant (factory._pw_bound_shift_probe) drops
    # one LSR to >>2, widening the PWM sweep band. Extract-only knob — the
    # resulting bound VALUES ride in USF min_hi/max_hi, so it never enters USF.
    pw_shift = int(getattr(cfg, 'extra_params', {}).get('pw_bound_shift', 4))
    for iid in sorted(used_instr):
        inst = _decode_instrument(mem, instr_base, iid, ctrl_tab, freq_tab,
                                  n_wave, pw_bound_shift=pw_shift)
        m.instruments[iid] = inst
    # Filter defs: capture the ENTIRE 8-bit walk window, not just the defs
    # instruments reference. The engine's repeat reload ($1719 = def+2) can be
    # > 5; the step index then walks UPWARD forever (INC + CMP #6 exact-match
    # never fires again), reading size/duration bytes at def-table offsets that
    # cross into ADJACENT records (and, via the +10 durations view, up to
    # def-table+265). Emitting the composer's table in the orig's 16-byte
    # record layout (composer fdrec) makes every walked read byte-exact — so
    # ship all 16 records (typed, byte-lossless) + the 10-byte tail. C2 class.
    # 17 records = 272 bytes >= the 266-byte window (16*16 + the 10 bytes the
    # +10 durations view reaches at walk index 250..255); the 17th record's
    # last 6 bytes are unreachable padding, kept typed for uniformity.
    # POST-INIT ground truth: some inits rewrite the def records (the 'Ed'
    # members stamp res/mode + initial cutoff over every def) — decode what
    # the engine reads, not the file image; py65-fail keeps the file image.
    if any(m.instruments[i].filter_on for i in m.instruments):
        post = _postinit_window(s, filtdef, 272)
        fmem = mem
        if post is not None and list(mem[filtdef:filtdef + 272]) != post:
            fmem = bytearray(mem)
            fmem[filtdef:filtdef + 272] = bytes(post)
        for d in range(17):
            if filtdef + d * 16 + 16 <= 0x10000:
                m.filter_defs[d] = _decode_filter_def(fmem, filtdef, d)
    # family 2: cymbal fires one frame later (frame 2, params.cymbal_onset),
    # and the vibrato swells differently — note-init stores freq_hi(note)>>1
    # to $178C and RAMPS the 16-bit step ($1792/$1795) by it each half-cycle
    # (canon instead loads a fixed step from the $1888 VIBDEPTH table and
    # doubles the WIDTH). The composer derives the increment from the freq
    # table; the swell mechanism is the build-level params.vib_ramp flag.
    m.family2 = (cfg.sector_format == 'family2')
    # pw_bound_shift is consumed above (extract-only); keep it out of USF so
    # the params block carries only musical content, never the derivation knob.
    m.extra_params = {k: v for k, v in getattr(cfg, 'extra_params', {}).items()
                      if k != 'pw_bound_shift'}
    if m.extra_params.get('dual_freq_generator'):
        # Dual-generator members (factory._dual_freq_gen_probe) force pwphase to
        # P0/P0+1 on every dual frame (P0 = $19 + ph_add), so the pulse
        # machine's speed fetch reads instr_base + ioff + 3 + (P>>1) — past
        # the instrument's own record. Those are STATIC table bytes; capture
        # them per dual instrument so the composer can extend its stride-8
        # isteps/irawsp tables at the reachable indices (P0..P0+3 — at most
        # two direction-flip INCs before the next dual-frame reset).
        from pipelines.dmc.composer_asm import _inst_offset
        ph_add = int(m.extra_params['dual_freq_generator'].split(',')[1])
        p0 = (0x19 + ph_add) & 0xFF
        ents = []
        for iid, ins in sorted(m.instruments.items()):
            if not ins.dual:
                continue
            ioff = _inst_offset(iid)
            raws = [mem[instr_base + ioff + 3 + (p0 >> 1) + k]
                    for k in range(3)]
            ents.append(':'.join([str(iid + 1)] + [str(r) for r in raws]))
        if ents:
            m.extra_params['dual_gen_steps'] = ','.join(ents)
    _assign_offtable_freq(m, mem, cfg.freq_lo_addr, cfg.freq_hi_addr,
                          cfg.vibdepth_addr)
    # off-table source bytes are in the engine's work RAM; init writes them, so
    # the runtime value differs from the file image. Correct to what the engine
    # actually reads (post-init, ground truth) — recovers the constant reads the
    # file-image capture mis-valued (the "dynamic residue" that wasn't).
    varying = _correct_offtable_postinit(m, path, cfg.freq_lo_addr,
                                         cfg.freq_hi_addr, cfg.vibdepth_addr)
    # State-geometry probe: the composer's off-table redirect map
    # (DMC_OFFTABLE_STATE) + the sectpos shadow identify window idx with the
    # canon live state vars via the CANON table→state geometry (state block at
    # canon offsets from the freq tables — invariant under whole-image
    # relocation). Variant builds move the state elsewhere (the page-3 builds:
    # Viiskyt_vuotta_humppaa keeps per-voice state at $03xx) — their window
    # bytes are unrelated STATIC code/data, exactly what the post-init capture
    # above serves, and every live redirect there would shadow a correct
    # static value (idx 130 "sectpos" = an opcode byte; idx 208 "cvram" = an
    # INY). Probe statically (C19: read the member's instructions): the canon
    # player DECs its per-voice duration counter at freq_hi + ($173B-$16A7);
    # no `DEC <that addr>,x` in the image ⇒ non-canon geometry ⇒ redirect map
    # + sectpos shadow off, event-driven correction unrestricted.
    canon_geom = _canon_state_geometry(mem, cfg)
    # If any off-table byte varied over the post-init time-sample, some read may
    # land on a globally-varying byte that is nonetheless STABLE at the moment a
    # given note reads it (sector-position, a settled track pointer). Recover
    # those with an event-driven capture (the value read AT the access). Gated so
    # members whose off-table reads are all init-constant skip the extra siddump.
    # Canon geometry only: the capture memwatches the CANON state addresses
    # ($1783/$1012/$1015/$172F/$1732), which on a non-canon member are unrelated
    # bytes — it would fabricate constant bogus keys that can poison correct
    # records. Non-canon members keep the post-init static values (their
    # window bytes are static code/data; a varying one stays honest residue).
    if varying and canon_geom:
        _correct_offtable_eventdriven(m, path)
    # sectpos shadow gating: an off-table freq read landing on $1729-$172B
    # (per-voice sector position — INC per consumed sector byte, reset at the
    # $7F end check) cannot be served statically (the value cycles) nor by the
    # event-driven capture (varies per key). The composer maintains a live
    # sectpos,x shadow instead, its per-row values derived from row kind +
    # the stated-command flags (dcmd/icmd/vcmd/softcmd) — enable it when any
    # captured read hits those bytes (flo idx 226-228 / fhi idx 130-132),
    # canon geometry only (see the probe above).
    _SECTPOS_IDX = {(0x1729 + k) - 0x16A7 for k in range(3)} \
        | {(0x1729 + k) - 0x1647 for k in range(3)}
    if canon_geom and any((off + note) & 0xFF in _SECTPOS_IDX
                          for ins in m.instruments.values()
                          for off, note, _lo, _hi in ins.offtable_freq):
        m.extra_params['sectpos_shadow'] = '1'
    if not canon_geom and any(ins.offtable_freq
                              for ins in m.instruments.values()):
        m.extra_params['offtable_redirect'] = '0'
    # wavepos live serving: an off-table freq read on $177A-$177C (fhi idx
    # 211-213) sonifies a voice's LIVE wave position — it varies at the read
    # (neither the static capture nor the event-driven one can serve it), and
    # the composer's own wavepos runs on ITS re-packed pool offsets. When
    # every wave program (idle walk included) is a verbatim contiguous slice
    # of the orig table, carry each instrument's editor wave-table position
    # (arrangement, §8) so the composer packs its pool at the orig positions —
    # then its wavepos state EQUALS orig $177A,x and the DMC_WAVEPOS_ROW
    # redirect serves the read live. Canon geometry only (ledger C6 note).
    _WAVEPOS_IDX = {(0x177A + k) - 0x16A7 for k in range(3)}
    if canon_geom and any((off + note) & 0xFF in _WAVEPOS_IDX
                          for ins in m.instruments.values()
                          for off, note, _lo, _hi in ins.offtable_freq):
        pos = _wave_layout_verbatim(m, ctrl_tab, freq_tab, n_wave)
        if pos is not None:
            for iid, c in pos.items():
                m.instruments[iid].wave_pool_pos = c
            m.wavepos_layout = True
    # wjmp chase shadow: an off-table freq read on $171F (fhi idx 120 / flo
    # idx 216) sonifies the shared effect scratch — the LAST value written to
    # it that frame. One writer is a chasing instrument's first-read hop: an
    # instrument whose wave byte9 sits ON its own loop marker ($90+n, loop 0)
    # chases back n every note-init, storing $171F=n. The composer packs the
    # SETTLED program (skips the transient chase), so it misses that one write
    # — mark such instruments so the composer re-asserts wjmp=n at note-init
    # (the hop repeats every settled frame anyway; only note-init is missed).
    # Canon geometry only; layout-independent (the value is the distance n,
    # not a pool position), so unaffected by / orthogonal to wavepos_layout.
    _WJMP_IDX = {(0x171F - 0x16A7) & 0xFF, (0x171F - 0x1647) & 0xFF}
    if canon_geom and any((off + note) & 0xFF in _WJMP_IDX
                          for ins in m.instruments.values()
                          for off, note, _lo, _hi in ins.offtable_freq):
        _wlim = min(n_wave, 256)
        for ins in m.instruments.values():
            ws, n = ins.wave_start, len(ins.wave_ctrl)
            if (ins.wave_loop == 0 and n and ws < _wlim
                    and ctrl_tab[ws] == 0x90 + n):
                ins.wave_start_on_marker = True
    return m


def _wave_layout_verbatim(m: DmcModel, ctrl_tab, freq_tab, n_wave):
    """Layout-preserving-pool precondition. Returns `{iid: table position of
    the program's first step}` when the idle walk AND every instrument's wave
    program are verbatim contiguous slices of the original wave table, ending
    on an orig marker byte equal to the composer's synthesized `$90+(n-loop)`
    — then a pool placed at these positions makes the runtime wavepos equal
    orig $177A at every SETTLED (observable) moment, marker hops included.
    None -> the member stays honest residue.

    A wave_start may sit ON the program's own end marker (the editor idiom
    "start at the loop marker": the engine chases it back n positions on the
    first read, settling on the same step span — inst byte9 = slice start + n,
    loop 0). That's admitted; the composer skips the transient chase (iwst =
    first-step position), which is unobservable EXCEPT through the chase's
    $171F wjmp write — so a member that ALSO reads the wjmp window (flo idx
    216 / fhi idx 120) with any chasing instrument is rejected."""
    progs = [(None, 0, list(m.idle_wave[0]), list(m.idle_wave[1]),
              m.idle_wave[2])]
    progs += [(iid, ins.wave_start, list(ins.wave_ctrl),
               list(ins.wave_freq), ins.wave_loop)
              for iid, ins in m.instruments.items()]
    lim = min(n_wave, 256)
    out, chased = {}, False
    for iid, start, ctrl, freq, loop in progs:
        n = len(ctrl)
        if n == 0 or not 0 <= loop < n or n - loop > 0x6F:
            return None
        if start < lim and ctrl_tab[start] >= 0x90:
            # start on a marker: admit ONLY the own-end-marker form
            # (back distance n, i.e. loop 0 with the slice right before it)
            if loop != 0 or ctrl_tab[start] != 0x90 + n or start < n:
                return None
            start -= n
            chased = True
        if start + n >= lim:             # marker must sit inside the table
            return None
        if any(b >= 0x90 for b in ctrl):
            return None                  # embedded marker (resolved chain)
        if ctrl != ctrl_tab[start:start + n]:
            return None
        f = freq if freq else [0] * n
        if f != freq_tab[start:start + n]:
            return None
        if ctrl_tab[start + n] != 0x90 + (n - loop):
            return None
        if iid is not None:
            out[iid] = start
    if chased:
        _WJMP_IDX = {(0x171F - 0x16A7) & 0xFF, (0x171F - 0x1647) & 0xFF}
        if any((off + note) & 0xFF in _WJMP_IDX
               for ins in m.instruments.values()
               for off, note, _lo, _hi in ins.offtable_freq):
            return None
    return out


def _assign_offtable_freq(m: DmcModel, mem, flo_addr: int,
                          fhi_addr: int, vibdepth_addr: int) -> None:
    """Capture each reachable off-table freq read as a per-instrument
    `(offset, note, lo, hi)` record — the v5 `offtable_freq` form, ported to v4.

    The original reads past its 96-entry freq tables into the engine state
    block; v4's old `_offtable_check` mirrored only the STABLE prefix (k=6..16:
    constants + speed + master vol) via the composer's co-located window and
    REJECTED any read on the track-ptr slots (k<=5) or live state (k>=17). This
    instead records the EXPLICIT (lo, hi) the read produces (read from the file
    image), so the composer can place those exact values at the matching window
    positions — recovering the STABLE-when-read reads (the value the original
    reads early, before the state evolves; the v5 read-before-evolution result).
    Genuinely per-frame-dynamic reads (a track pointer that has advanced) stay a
    verify residue, not a build error.

    The k=6..16 records are still emitted but the composer keeps those positions
    co-located (live spd/mvol/constants) — so members that only read there are
    byte-identical to before (no regression).

    Note-load reads past the table (note > 95, via transpose) make TWO off-table
    reads: the note's own freq (captured here as an offset-0 offtable_freq
    record) AND the separate vibdepth table (the vibrato step) — captured into
    `m.offtable_vibdepth` ({note: depth}), which `to_usf` emits as
    `UsfFile.offtable_vibdepth` for the composer's vibdepth overrun window. Both
    land on STATIC bytes (freq tail / instrument records), so the captured values
    are exact. No more `offtable_vibdepth` rejection."""
    from collections import defaultdict
    recs = defaultdict(set)            # inst id -> {(off, note, lo, hi)}
    vibovr = {}                        # note>95 -> off-table vibdepth byte

    def add_note(n, inst_id):
        inst = m.instruments.get(inst_id)
        if n > 95:
            # the note's OWN off-table freq (offset-0 base read): the pitch the
            # note plays at when it overshoots the 96-entry table (via transpose).
            recs[inst_id].add((0, n & 0xFF, mem[(flo_addr + n) & 0xFFFF],
                               mem[(fhi_addr + n) & 0xFFFF]))
            # the note's off-table VIBDEPTH read (vibdepth[note], note>95) —
            # lands on static instr-record bytes, used as the vibrato step.
            vibovr[n & 0xFF] = mem[(vibdepth_addr + n) & 0xFFFF]
        if inst is None or inst.drum:
            return
        for off in inst.wave_freq:
            y = (n + off) & 0xFF
            if y > 95:
                recs[inst_id].add((off & 0xFF, n & 0xFF,
                                   mem[(flo_addr + y) & 0xFFFF],
                                   mem[(fhi_addr + y) & 0xFFFF]))

    for song in m.songs:
        for v in song.voices:
            # `running` = the instrument whose wave program is LIVE before a
            # row's note-init runs. Notes are FETCHED on a P call (curnote +
            # base update at $11A3-$11B3) but note-init (wave restart) is
            # DEFERRED to the pending frame — an intervening wave-step call
            # ($1591 F entry) steps the OLD program with the NEW curnote. And
            # a SOFT ($7C) row skips note-init entirely, so the old program
            # runs for its whole duration. Both make off-table reads at
            # (old-program offset + new note) — enumerate them too, else the
            # window byte for that idx stays the file-image leftover
            # (Bladeswede: inst-13 noise-arp off 52 + soft note 47 = idx 99
            # reads $170A = V1 track-ptr hi, runtime $1B vs file $00).
            running = None
            for ei, e in enumerate(v.entries):
                tr = v.transposes[ei] if v.transposes else 0
                for r in v.patterns[e]:
                    if r.note is not None:
                        add_note(r.note + tr, r.instr)
                        if running is not None and running != r.instr:
                            add_note(r.note + tr, running)
                        if not r.soft:
                            running = r.instr
                    if r.glide_to is not None:
                        add_note(r.glide_to + tr, r.instr)
    # IDLE-WAVE off-table reads: a voice that starts on rests freewheels the
    # idle wave (m.idle_wave, the cleared-cache path) with curnote = its idle
    # note — and the idle-wave freq offsets + idle note can overshoot the
    # 96-entry table (e.g. Funky_Witch idle_note 50 + offset 51 = idx 101). The
    # per-instrument note loop above never covers the idle path, so capture it
    # here (curnote = each voice's idle note). Records go to instr 0 (always
    # shipped) — the off-table window is instrument-agnostic (idx -> value).
    idle_freq = list(m.idle_wave[1]) if m.idle_wave and m.idle_wave[1] else []
    for cn in set(m.idle_notes):
        for off in idle_freq:
            y = (cn + off) & 0xFF
            if y > 95:
                recs[0].add((off & 0xFF, cn & 0xFF,
                             mem[(flo_addr + y) & 0xFFFF],
                             mem[(fhi_addr + y) & 0xFFFF]))
    for iid, s in recs.items():
        if iid in m.instruments:
            m.instruments[iid].offtable_freq = sorted(s)
    m.offtable_vibdepth = vibovr


def _postinit_values(sid_path: str, addrs) -> dict:
    """Post-init values of work-RAM bytes via siddump --memwatch (libsidplayfp
    = ground truth). The off-table source bytes live in the engine's work RAM
    AFTER the freq tables; the engine's INIT writes them, so the value the
    original actually READS at runtime is NOT the file-image byte. Capture what
    the engine reads (Core Tenet: observe the writes, don't mirror the
    mechanism). Returns {addr: value} only for bytes CONSTANT across the sample
    (init-written-then-stable -> reproducible); bytes that VARY frame-to-frame
    are genuinely dynamic and omitted (caller keeps the file image; they remain
    honest residue)."""
    if not addrs:
        return {}
    import subprocess
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                      'tools', 'siddump')
    al = sorted(set(a & 0xFFFF for a in addrs))
    try:
        out = subprocess.run(
            [sd, sid_path, '--duration', '6', '--raw',
             '--memwatch', ','.join(f'{a:04X}' for a in al)],
            capture_output=True, text=True, timeout=90).stdout
    except Exception:
        return {}
    seen = {}
    for line in out.splitlines():
        if 'M:' not in line:
            continue
        for tok in line.split('M:')[1].split('|')[0].split(':'):
            if '=' in tok:
                a, v = tok.split('=')
                seen.setdefault(int(a, 16), set()).add(int(v, 16))
    return {a: next(iter(vs)) for a, vs in seen.items() if len(vs) == 1}


def _correct_offtable_postinit(m: DmcModel, sid_path: str, flo_addr: int,
                               fhi_addr: int, vibdepth_addr: int) -> None:
    """Replace the file-image off-table values with the original's POST-INIT
    values (the bytes the engine actually reads). Recovers the
    init-written-then-constant reads that the file-image capture got wrong."""
    addrs = set()
    for ins in m.instruments.values():
        for off, note, lo, hi in ins.offtable_freq:
            idx = (off + note) & 0xFF
            if idx > 95:
                addrs.add(flo_addr + idx)
                addrs.add(fhi_addr + idx)
    for note in m.offtable_vibdepth:
        addrs.add(vibdepth_addr + note)
    post = _postinit_values(sid_path, addrs)
    if not post:
        return addrs                      # siddump failed → all unresolved
    for ins in m.instruments.values():
        new = []
        for off, note, lo, hi in ins.offtable_freq:
            idx = (off + note) & 0xFF
            new.append((off, note, post.get((flo_addr + idx) & 0xFFFF, lo),
                        post.get((fhi_addr + idx) & 0xFFFF, hi)))
        ins.offtable_freq = sorted(set(new))
    m.offtable_vibdepth = {n: post.get((vibdepth_addr + n) & 0xFFFF, d)
                           for n, d in m.offtable_vibdepth.items()}
    # addrs whose byte VARIED over the post-init time-sample (post omitted them,
    # keeping the file image). These are the candidates for the event-driven
    # correction below: a globally-varying byte can still be STABLE at the moment
    # a given note reads it (e.g. sector-position $1729).
    return {a & 0xFFFF for a in addrs} - set(post)


_SL_DB: dict = {}


def _verify_window(sid_path: str) -> float:
    """songlength × 1.1 (the verify window) for the longest subtune, used as the
    event-driven capture duration so every read the verdict checks is observed.
    Falls back to 150s if the Songlengths DB can't be located."""
    root = sid_path
    db_path = None
    for _ in range(8):
        root = os.path.dirname(root)
        cand = os.path.join(root, 'DOCUMENTS', 'Songlengths.md5')
        if os.path.exists(cand):
            db_path = cand
            break
    if db_path is None:
        return 150.0
    if db_path not in _SL_DB:
        from src.songlengths import load_database
        _SL_DB[db_path] = load_database(db_path)
    from src.songlengths import get_durations
    durs = get_durations(sid_path, _SL_DB[db_path])
    return min((max(durs) if durs else 130) * 1.1, 300.0)


def _offtable_eventdriven(sid_path: str, duration: float) -> dict:
    """EVENT-DRIVEN off-table capture: record the value each off-table freq read
    produces AT THE ACCESS, keyed by `(inst, off, note)`. Recovers reads on a
    byte that varies GLOBALLY but is STABLE when this note reads it (the
    file-image / post-init-constant captures both miss these).

    The engine computes each voice's freq base into `$172F/$1732,x` from the
    (possibly off-table) index `$1783,x = curnote + wave_offset`. Snapshot all
    three voices' `(y, curnote, inst, base_lo, base_hi)` at every `$D416` write
    (once per play() — CIA-safe, per-play() not per-frame). Returns
    `{(inst, off, note): (lo, hi)}` for keys whose value is the SAME across every
    occurrence; keys that vary are omitted (they stay honest residue)."""
    import subprocess
    import re
    from collections import defaultdict
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                      'tools', 'siddump')
    Y = (0x1783, 0x1784, 0x1785)      # offset-note = curnote + wave_offset
    CN = (0x1012, 0x1013, 0x1014)     # current note
    INS = (0x1015, 0x1016, 0x1017)    # current instrument
    BLO = (0x172F, 0x1730, 0x1731)    # freq base lo (freqlo read result)
    BHI = (0x1732, 0x1733, 0x1734)    # freq base hi (freqhi read result)
    addrs = Y + CN + INS + BLO + BHI
    try:
        out = subprocess.run(
            [sd, sid_path, '--duration', str(int(duration)),
             '--memwatch-on-write', 'D416',
             ','.join(f'{a:04X}' for a in addrs)],
            capture_output=True, text=True, timeout=int(duration) + 120).stdout
    except Exception:
        return {}
    pat = re.compile(r'([0-9A-F]{4})=([0-9A-F]+)')
    vals = defaultdict(set)
    for line in out.splitlines():
        if '|E' not in line:
            continue
        for ev in line.split('|'):
            if not ev.startswith('E'):
                continue
            d = {a: int(v, 16) for a, v in pat.findall(ev)}
            for x in range(3):
                y = d.get(f'{Y[x]:04X}')
                if y is None or y < 96:            # in-table read: not off-table
                    continue
                cn = d.get(f'{CN[x]:04X}', 0)
                blo = d.get(f'{BLO[x]:04X}')
                bhi = d.get(f'{BHI[x]:04X}')
                if blo is None or bhi is None:
                    continue
                key = (d.get(f'{INS[x]:04X}', 0), (y - cn) & 0xFF, cn & 0xFF)
                vals[key].add((blo, bhi))
    return {k: next(iter(vs)) for k, vs in vals.items() if len(vs) == 1}


def _canon_state_geometry(mem, cfg) -> bool:
    """True iff the member keeps its per-voice state block at the CANON offset
    from its freq tables (the premise of the composer's off-table redirect map
    + the sectpos shadow: window idx N = the canon state var at fhi+N).
    Static opcode probe (C19): the canon player DECs its per-voice duration
    counter every tick via `DEC $173B,x` ($10BD) — expect `DE lo hi` with
    addr = freq_hi + ($173B − $16A7) somewhere in the player image. Variant
    builds that moved the state (e.g. to $03xx) DEC a different address.
    Fail-open: a stray data match keeps today's behavior (redirect on)."""
    dur = (cfg.freq_hi_addr + (0x173B - 0x16A7)) & 0xFFFF
    pat = bytes((0xDE, dur & 0xFF, dur >> 8))
    lo = max(0, cfg.base)
    return pat in bytes(mem[lo:min(0x10000, lo + 0x4000)])


def _redirect_mapped_idx() -> set:
    """The off-table freq idx positions the composer serves from a LIVE redirect
    var (DMC_OFFTABLE_STATE), not the static window. A read landing there reads
    the tracked var, and its static window value is used only to SEED that var at
    init (round-25 gla/glb) — which must be the file-image LEFTOVER, never the
    deep runtime value. So the event-driven correction must skip these idx (a
    runtime override there breaks the seed — the Calimero regression)."""
    from pipelines.dmc.composer_asm import (DMC_OFFTABLE_STATE,
                                            DMC_SECTPOS_ROW, ORIG_FHI)
    return {(addr + k - ORIG_FHI) & 0xFF
            for addr, _label, n in DMC_OFFTABLE_STATE + [DMC_SECTPOS_ROW]
            for k in range(n)}


def _correct_offtable_eventdriven(m: DmcModel, sid_path: str) -> None:
    """Override off-table records with the event-driven read-moment value where
    it is STABLE per `(inst, off, note)`, EXCEPT positions the composer serves
    from a live redirect var (those are live-tracked + seeded from the leftover,
    so the static value must stay the file image — see `_redirect_mapped_idx`).
    Canon-geometry members only (the caller gates on `_canon_state_geometry`;
    the capture memwatches canon state addresses).
    On the remaining (window-served) positions this is regression-safe: a FULL
    member's reads already match, so the read-moment value equals the record → no
    change; only currently-wrong reads move. A key that VARIES is not in `ev`."""
    ev = _offtable_eventdriven(sid_path, _verify_window(sid_path))
    if not ev:
        return
    mapped = _redirect_mapped_idx()
    for iid, ins in m.instruments.items():
        changed = False
        new = []
        for off, note, lo, hi in ins.offtable_freq:
            rv = ev.get((iid, off & 0xFF, note & 0xFF))
            if (off + note) & 0xFF not in mapped and rv is not None \
                    and rv != (lo, hi):
                new.append((off, note, rv[0], rv[1])); changed = True
            else:
                new.append((off, note, lo, hi))
        if changed:
            ins.offtable_freq = sorted(set(new))
