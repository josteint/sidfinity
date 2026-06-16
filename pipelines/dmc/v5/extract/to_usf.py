"""DMC V5 model -> USF.

Maps the extracted V5Model onto the engine-neutral USF schema so the
pipeline runs SID -> USF -> SID (the project's "always through USF"
rule). The composer stays model-driven; `from_usf` rebuilds the model
from the parsed USF (the inverse of this module).

Representation choices (USF representation principle):

- WAVE program: each instrument's wave-table slice (followed through the
  engine's $90 jump-back marker) becomes the instrument's
  `waveform`/`wave_freq`/`loop` -- decoding away the engine's wave-table
  pointer. The idle walk (table index 0, the engine's cleared wave
  position before a voice's first note) is carried as `wave_programs[0]`.
  `wave_freq` bytes are kept RAW: each step's mode (melodic offset vs
  absolute freq-hi) is the step's own ctrl bit 3 ($08), visible in
  `waveform`.

- PULSE program: each restarting instrument's pulse-table slice becomes
  an inline `pulse_sweep` (start PW + (add, frames) segments + loop) --
  decoding away the pulse-table pointer. Non-restarting instruments
  (pointer 0) carry `pwm.keep_running` (the running oscillator continues;
  position-persistence is engine mechanism, not stored content).

- SECTORS -> per-voice `Pattern`s (note rows + `hold` gate rows; sticky
  dur/instrument stamped per row). ORDERLISTS -> `Orderlist`
  (sector entries + signed transposes + loop). FREQ table, speed->tempo,
  master vol + filter leftovers -> init.sid; meta -> psid.

FILTER sweeps (voice-3-only) are residue: Katusha uses no filter
program (the model's filter table is a single null entry, no instrument
points into it). A filter-using V5 member needs a `filter_sweep` field
of the same shape as `pulse_sweep`.
"""
from __future__ import annotations

import os

from src.usf.types import (
    UsfFile, PsidMeta, Params, InitState, InitSid, InitFilter, InitVoice,
    Instrument, PwmConfig, VibratoConfig, SweepEnvelope,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
)

# A sweep program advances by `count` frames per segment; bound the
# reachable-phase capture so the engine's table-fusion (programs bleeding
# into one another) is dissolved — beyond this many frames no realistic
# note (or keep-running continuation over a song) reaches.
_REACH_FRAMES = 30000     # ~600s at 50Hz — longer than any real song
_PHASE_CAP = 48
from src.usf.writer import write_file
from pipelines.dmc.v5.config import DMCV5Config
from pipelines.dmc.v5.extract.engine_model import extract, V5Model

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def _pitch(note: int) -> Pitch:
    return Pitch(name=NOTE_NAMES[note % 12], octave=note // 12)


# --- wave program: follow the $90 jump-back marker (V5: ctrl==$90 -> the
#     parallel freq byte is the ABSOLUTE loop-target index). --------------
def _slice_wave(wave: list, start: int):
    """Return (ctrl, freq, loop) for the wave program at `start`. `loop`
    is the relative index the marker jumps back to."""
    n = len(wave)
    ctrl, freq = [], []
    pos = start
    guard = 0
    while pos < n:
        guard += 1
        if guard > 256:
            raise RuntimeError(f'unsupported:wave_slice runaway @{start}')
        c, f = wave[pos]
        if c == 0x90:
            target = f                       # absolute loop-target index
            if target >= start:
                return ctrl, freq, target - start
            # loop target before the slice: unroll the cyclic tail so the
            # heard sequence is [start..pos) + [target..start) with loop 0
            return (ctrl + [wave[k][0] for k in range(target, start)],
                    freq + [wave[k][1] for k in range(target, start)], 0)
        ctrl.append(c)
        freq.append(f)
        pos += 1
    raise RuntimeError(f'unsupported:wave_slice no $90 @{start}')


# --- sweep envelope capture (pulse OR filter) ----------------------------
# Walk the engine's (step, count) phase stream from `ptr`, capturing the
# REACHABLE phases (the table is a shared/fused resource; the bleeding past
# the reachable horizon is the packer's space-saving mechanism — Rule 1).
def _capture_env(table: list, ptr: int) -> SweepEnvelope:
    start = (table[ptr][0] << 8) | table[ptr][1]
    phases = []
    loop = None
    pos = ptr + 1
    cum = 0
    pos_phase = {}                # table position a phase started at -> index
    while pos < len(table):
        if len(phases) >= _PHASE_CAP:
            raise RuntimeError(f'unsupported:sweep_too_long @{ptr}')
        lo, hi = table[pos]
        if lo == 0x90:            # jump to the target byte position
            tgt = hi
            if tgt in pos_phase:  # revisiting a captured phase = a real cycle
                loop = pos_phase[tgt]
                break
            pos = tgt              # otherwise FOLLOW it (the target may be a
            continue               # count slot the engine re-reads as a step)
        if pos + 1 >= len(table):  # step without its count
            break
        pos_phase[pos] = len(phases)
        rate = (lo << 8) | hi
        if rate >= 0x8000:
            rate -= 0x10000
        clo, chi = table[pos + 1]
        frames = (clo << 8) | chi
        # count==0 means the engine's 16-bit phase counter wraps (65536
        # frames) before advancing — i.e. a terminal hold. This is also what
        # the off-table zero-region of a small (last-table) filter program
        # decodes to; without this the (0,0) entries spin forever -> PHASE_CAP.
        if frames == 0:
            frames = 0x10000
        phases.append((rate, frames))
        cum += frames
        pos += 2
        if frames >= 0x9000 or cum > _REACH_FRAMES:   # terminal / reached
            break
    return SweepEnvelope(start=start, phases=phases, loop=loop)


# --- sectors -> pattern rows ---------------------------------------------
# Each note/gate becomes a row; the leading parameter commands ($FD dur,
# $FC snd, $F3 vol, $F8 frq, $F7/$F6 fade, $F2/$F1 adr/srr, $F9 flt,
# $F5 gate_toggle) attach to the FOLLOWING row as ORDERED prefix flags.
# Their byte position is preserved verbatim because the engine's gate-off
# lookahead reads the raw next byte -- a command may not be reshuffled
# relative to the notes/gates around it. The note/gate main events:
# note (<$80), gate ($FE)=tie, gate_tie ($F4), glide ($FB)=note+glide,
# slide ($FA)=tie+glide.

# event name -> (prefix flag formatter): single-arg positioned commands
_PREFIX = {
    'dur': lambda v: f'set_dur=${v:02X}',
    'snd': lambda v: f'set_instr={v}',
    'vol': lambda v: f'vol={v}',
    'frq': lambda v: f'frq=${v:02X}',
    'fade_in': lambda v: f'fade_in=${v:02X}',
    'fade_out': lambda v: f'fade_out=${v:02X}',
    'adr': lambda v: f'adr=${v:02X}',
    'srr': lambda v: f'srr=${v:02X}',
    'flt': lambda v: f'filter=${v:02X}',
}


def _note_byte(n: int) -> Pitch:
    if n > 119:
        raise RuntimeError(f'unsupported:note_out_of_range {n}')
    return _pitch(n)


def _sector_rows(events: list) -> list:
    rows = []
    dur = 1
    pending = []                         # leading commands, in order
    for e in events:
        cmd = e[0]
        if cmd in _PREFIX:
            if cmd == 'dur':
                dur = e[1]
            pending.append(_PREFIX[cmd](e[1]))
        elif cmd == 'gate_toggle':       # $F5: flip gate flag (no duration)
            pending.append('gate_toggle')
        elif cmd == 'note':
            rows.append(NoteRow(pitch=_note_byte(e[1]), duration=dur,
                                fx_flags=tuple(pending)))
            pending = []
        elif cmd == 'gate':              # $FE: hold current note, no retrigger
            rows.append(NoteRow(pitch=Pitch.rest(), duration=dur,
                                fx_flags=tuple(pending) + ('tie',)))
            pending = []
        elif cmd == 'gate_tie':          # $F4: hold + toggle gate-mask bit
            rows.append(NoteRow(pitch=Pitch.rest(), duration=dur,
                                fx_flags=tuple(pending) + ('gate_tie',)))
            pending = []
        elif cmd == 'glide':             # $FB spd cur tgt: note + glide
            _, spd, cur, tgt = e
            rows.append(NoteRow(
                pitch=_note_byte(cur), duration=dur,
                fx_flags=tuple(pending)
                + (f'glide={spd}', f'glide_to={_note_byte(tgt)}')))
            pending = []
        elif cmd == 'slide':             # $FA spd tgt: hold + glide to target
            _, spd, tgt = e
            rows.append(NoteRow(
                pitch=Pitch.rest(), duration=dur,
                fx_flags=tuple(pending)
                + (f'glide={spd}', f'glide_to={_note_byte(tgt)}')))
            pending = []
        elif cmd == 'end':
            break
        else:
            raise RuntimeError(f'unsupported:sector_cmd {cmd}')
    if pending:                          # trailing commands before $FF
        raise RuntimeError(f'unsupported:trailing_sector_cmds {pending}')
    return rows


def _orderlist(events: list) -> Orderlist:
    entries, transposes = [], []
    transpose = 0
    loop_to = None
    loop_reestablish = False
    stop = False
    # Map raw byte offset -> (entry index, is_transpose_prefix). A loop target
    # is a byte offset that lands on ONE of two things (byte offsets are
    # unique): an entry's SECTOR byte, or an entry's leading $FD/$FC transpose
    # PREFIX. The distinction is the loop's transpose semantics:
    #   - target = PREFIX byte  -> the player re-dispatches the transpose each
    #     wrap (RE-ESTABLISH); loop_transpose carries the value.
    #   - target = SECTOR byte (past the prefix, or an unprefixed entry) -> the
    #     player CARRIES the running transpose over the wrap; loop_transpose
    #     stays None.
    # Recording only the prefix byte sent past-the-prefix targets to loop_to=0;
    # recording only the sector byte sent prefix targets there. Record both.
    byte_map = {}
    byte_pos = 0
    prefix_start = None       # byte where the pending entry's $FD/$FC prefix began
    for e in events:
        if e[0] == 'sector':
            i = len(entries)
            byte_map[byte_pos] = (i, False)           # sector byte = carry
            if prefix_start is not None:
                byte_map[prefix_start] = (i, True)    # prefix byte = re-establish
            prefix_start = None
            entries.append(e[1])
            transposes.append(transpose)
            byte_pos += 1
        elif e[0] == 'transpose':
            if prefix_start is None:
                prefix_start = byte_pos               # transpose prefix start
            t = e[1]
            transpose = t - 256 if t >= 128 else t   # signed
            byte_pos += 2
        elif e[0] == 'loop':
            tgt = e[1]                                # raw byte offset
            loop_to, loop_reestablish = byte_map.get(tgt, (0, False))
        elif e[0] == 'end':
            stop = True
    loop_transpose = (transposes[loop_to]
                      if (loop_reestablish and loop_to is not None
                          and loop_to < len(transposes)) else None)
    ol = Orderlist(entries=entries, loop_to=loop_to, stop=stop,
                   loop_transpose=loop_transpose,
                   transposes=transposes if any(transposes) else [])
    return ol


def _instrument_to_usf(ins, model: V5Model):
    """Map a V5Instrument to a USF Instrument. The wave program is decoded
    inline (self-looping, separable); pulse/filter are entry indices into
    the tune's shared tables (carried whole by model_to_usf)."""
    wc, wf, wl = _slice_wave(model.wave, ins.wave_ptr)
    # pulse_ptr == 0 = no restart (the PW oscillator keeps running across
    # the note); a real entry index restarts the sweep there.
    return Instrument(
        id=ins.id,
        waveform=list(wc),
        loop=wl,
        wave_freq=[b & 0xFF for b in wf],
        adsr=(ins.ad, ins.sr),
        pwm=PwmConfig(keep_running=(ins.pulse_ptr == 0)),
        pulse_env=(_capture_env(model.pulse, ins.pulse_ptr)
                   if ins.pulse_ptr else None),
        filter_env=(_capture_env(model.filter, ins.filter_ptr)
                    if ins.filter_ptr else None),
        vibrato=VibratoConfig(onset=ins.vib_delay, speed=ins.vib_speed,
                              amplitude=ins.vib_width),
    )


def model_to_usf(m: V5Model) -> UsfFile:
    # one Pattern per global sector (shared across voices); each voice
    # carries the Patterns its orderlist references.
    sector_pat = {i: Pattern(id=i, length=0, rows=_sector_rows(ev))
                  for i, ev in enumerate(m.sectors)}
    for p in sector_pat.values():
        p.length = sum(r.duration for r in p.rows)

    # one MusicSubtune per orderlist record. The data tables (sectors above,
    # instruments/freq/wave_programs below) are SHARED at the top level; each
    # subtune carries only its 3 voices (orderlists) + tempo + master vol.
    # The file-image leftovers (filter cutoff, $1013 speed-counter / $101C
    # fade-frac startup phases, $100F idle notes) are GLOBAL -> subtune 0.
    sub_data = m.subtunes or [m]
    usf_subs = []
    for si, st in enumerate(sub_data):
        voices = []
        for vi in range(3):
            ol = _orderlist(st.orderlists[vi])
            used = sorted(set(ol.entries))
            pats = [sector_pat[s] for s in used]
            voices.append(VoiceBlock(id=vi + 1, orderlist=ol, patterns=pats))
        sid = InitSid(
            master_vol=st.master_vol,
            filter=(InitFilter(cutoff_lo=m.lo_fclo, cutoff_hi=m.lo_fchi,
                               res_routing=m.lo_filtmode) if si == 0 else None))
        usf_subs.append(MusicSubtune(
            id=si + 1, tempo=st.speed, voices=voices,
            # speed_ctr_init = the Hubbard/Title-Tunes init speed-counter key.
            params=(Params(fields={'speed_ctr_init': m.lo_spdctr,
                                   'fade_frac_init': m.lo_mvolfrac})
                    if si == 0 else None),
            init=InitState(
                sid=sid,
                voices=([InitVoice(id=v + 1, note=m.lo_notes[v])
                         for v in range(3)] if si == 0 else []))))

    instruments = [_instrument_to_usf(ins, m) for ins in m.instruments]
    # idle wave walk (cleared wave position 0 -> what a voice's effects
    # read before its first note).
    idle_c, idle_f, idle_l = _slice_wave(m.wave, 0)

    return UsfFile(
        psid=PsidMeta(title=m.title, author=m.author, released=m.released,
                      start_song=1),
        params=Params(),
        init=InitState(),
        instruments=instruments,
        subtunes=usf_subs,
        # per-tune tuning: 96 lo + 96 hi
        freq_table=list(m.freq_lo) + list(m.freq_hi),
        wave_programs={0: {'ctrl': list(idle_c),
                           'freq': [b & 0xFF for b in idle_f],
                           'loop': idle_l}},
    )


def write_v5_usf(cfg: DMCV5Config, out_dir: str,
                 hvsc_root: str = 'hvsc84') -> str:
    m = extract(cfg, hvsc_root=hvsc_root)
    usf = model_to_usf(m)
    base = os.path.splitext(os.path.basename(cfg.sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out
