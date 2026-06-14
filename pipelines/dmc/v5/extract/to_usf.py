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
    UsfFile, PsidMeta, Params, InitState, InitSid, InitFilter,
    Instrument, PwmConfig, VibratoConfig, PulseSweepConfig,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
)
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


# --- pulse program: init pair + (step, count) segment pairs + $90 loop --
def _decode_pulse(pulse: list, ptr: int) -> PulseSweepConfig:
    """Decode the pulse-table slice at `ptr` into a PulseSweepConfig.

    Entry layout (V5): pulse[P] = init PW (stored lo=PW-hi, hi=PW-lo);
    then alternating step/count entries. A step entry contributes a
    signed 16-bit per-frame `add` (lo<<8|hi); the following count entry
    is the 16-bit frame count (lo<<8|hi). A $90 in a step position is a
    loop marker (jump to the parallel hi byte, absolute index). A $90 in
    a count position is the engine's near-infinite count -> the segment
    holds for the whole note (the program's last segment).
    """
    start = (pulse[ptr][0] << 8) | pulse[ptr][1]    # PW-hi<<8 | PW-lo
    segs = []
    loop = None
    pos = ptr + 1
    guard = 0
    while pos < len(pulse):
        guard += 1
        if guard > 256:
            raise RuntimeError(f'unsupported:pulse runaway @{ptr}')
        lo, hi = pulse[pos]
        if lo == 0x90:                       # loop marker at a step slot
            loop = hi - ptr
            break
        add = (lo << 8) | hi
        if add >= 0x8000:
            add -= 0x10000
        if pos + 1 >= len(pulse):
            raise RuntimeError(f'unsupported:pulse truncated @{ptr}')
        clo, chi = pulse[pos + 1]
        frames = (clo << 8) | chi
        segs.append((add, frames))
        if clo == 0x90:                      # near-infinite count: last seg
            break
        pos += 2
    else:
        raise RuntimeError(f'unsupported:pulse no terminator @{ptr}')
    return PulseSweepConfig(start=start, segments=segs, loop=loop)


# --- sectors -> pattern rows ---------------------------------------------
# Each note/gate becomes a row; the leading dur ($FD) / instrument-select
# ($FC) commands attach to the FOLLOWING row as ORDERED prefix flags
# (`set_dur` / `set_instr`). Their byte position is preserved verbatim
# because the engine's gate-off lookahead reads the raw next byte -- so a
# command may not be reshuffled relative to the notes/gates around it.
# Katusha's vocabulary is dur/snd/note/gate/end; other sector commands
# (vol/slide/glide/frq/flt/fade/gate_toggle/srr/adr) are family residue
# and raise here so a member that uses them is flagged, not mis-encoded.
_HANDLED = {'dur', 'snd', 'note', 'gate', 'end'}


def _sector_rows(events: list) -> list:
    rows = []
    dur = 1
    pending = []                         # leading commands, in order
    for e in events:
        cmd = e[0]
        if cmd not in _HANDLED:
            raise RuntimeError(f'unsupported:sector_cmd {cmd}')
        if cmd == 'dur':
            dur = e[1]
            pending.append(f'set_dur=${dur:02X}')
        elif cmd == 'snd':
            pending.append(f'set_instr={e[1]}')
        elif cmd == 'note':
            rows.append(NoteRow(pitch=_pitch(e[1]), duration=dur,
                                fx_flags=tuple(pending)))
            pending = []
        elif cmd == 'gate':              # $FE: hold current note, no retrigger
            rows.append(NoteRow(pitch=Pitch.rest(), duration=dur,
                                fx_flags=tuple(pending) + ('tie',)))
            pending = []
        elif cmd == 'end':
            break
    if pending:                          # trailing commands before $FF
        raise RuntimeError(f'unsupported:trailing_sector_cmds {pending}')
    return rows


def _orderlist(events: list) -> Orderlist:
    entries, transposes = [], []
    transpose = 0
    loop_to = None
    stop = False
    # byte offset -> entry index, so a loop target (a byte offset in the
    # raw stream) maps to the orderlist position.
    byte_of_entry = []
    byte_pos = 0
    for e in events:
        if e[0] == 'sector':
            byte_of_entry.append(byte_pos)
            entries.append(e[1])
            transposes.append(transpose)
            byte_pos += 1
        elif e[0] == 'transpose':
            t = e[1]
            transpose = t - 256 if t >= 128 else t   # signed
            byte_pos += 2
        elif e[0] == 'loop':
            tgt = e[1]                                # raw byte offset
            loop_to = byte_of_entry.index(tgt) if tgt in byte_of_entry else 0
        elif e[0] == 'end':
            stop = True
    ol = Orderlist(entries=entries, loop_to=loop_to, stop=stop,
                   transposes=transposes if any(transposes) else [])
    return ol


def _instrument_to_usf(ins, model: V5Model):
    """Map a V5Instrument to a USF Instrument (wave + pulse decoded
    away). `model` supplies the shared wave/pulse tables."""
    wc, wf, wl = _slice_wave(model.wave, ins.wave_ptr)
    pwm = PwmConfig()
    pulse_sweep = None
    if ins.pulse_ptr:
        pulse_sweep = _decode_pulse(model.pulse, ins.pulse_ptr)
    else:
        pwm = PwmConfig(keep_running=True)
    return Instrument(
        id=ins.id,
        waveform=list(wc),
        loop=wl,
        wave_freq=[b & 0xFF for b in wf],
        adsr=(ins.ad, ins.sr),
        pwm=pwm,
        pulse_sweep=pulse_sweep,
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

    voices = []
    for vi in range(3):
        ol = _orderlist(m.orderlists[vi])
        used = sorted(set(ol.entries))
        pats = [sector_pat[s] for s in used]
        voices.append(VoiceBlock(id=vi + 1, orderlist=ol, patterns=pats))

    sub = MusicSubtune(
        id=1, tempo=m.speed, voices=voices,
        init=InitState(sid=InitSid(
            master_vol=m.master_vol,
            filter=InitFilter(cutoff_lo=m.lo_fclo, cutoff_hi=m.lo_fchi,
                              res_routing=m.lo_filtmode))))

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
        subtunes=[sub],
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
