"""DMC V6 model -> USF.

Maps the extracted V6Model onto the engine-neutral USF schema, reusing the
DMC v5 dimensions (USF representation principle §9.4: V6's instances land as
points in the SAME parameter space, no new opaque kinds):

- WAVE program: each instrument's wave-program slice (ctrl + note-offset,
  followed through the $FF loop marker) -> `waveform`/`wave_freq`/`loop`,
  decoding away the engine's wave-program pointer. Same shape as v5.
- PW: V6's pulse width is an OSCILLATOR — a per-frame phase
  `accum = pw_init + t*pw_step` (8-bit, wrapping) indexed into a shared 12-bit
  triangle LUT. The LUT is a clean triangle (2 linear runs), so the resulting
  per-frame PW value stream is piecewise-linear -> we SIMULATE it and convert
  to a `SweepEnvelope` (start + (rate,frames) phases + loop) — the ledger-D1
  canonical PW form. pw_step==0 -> a constant (start only).
- FILTER (V2-owned): (cutoff, count, step) is a one-shot linear ramp ->
  `SweepEnvelope(start=cutoff, phases=[(step,count)])`.
- PATTERNS -> per-voice `Pattern`s (note rows; sticky duration/instrument as
  ordered prefix flags). ORDERLISTS -> `Orderlist` (wrap to 0). FREQ table +
  tempo -> top-level / subtune. meta -> psid.

DEFERRED (handled in the composer+verify loop, like v5 was built): the
per-instrument octave pitch-slide (`pitch_delay` -> the $FE/$FF detune blip).
Instruments that use it are flagged so the gap is explicit, not silent.
"""
from __future__ import annotations

import os
import warnings
from math import gcd

from src.usf.types import (
    UsfFile, PsidMeta, Params, InitState, InitSid, InitFilter,
    Instrument, PwmConfig, SweepEnvelope,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
)
from src.usf.writer import write_file
from pipelines.dmc.v6.extract.engine_model import (
    extract, V6Model, V6PatNote, V6PatDuration, V6PatInstrument,
)

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
_PW_SIM_CAP = 4096          # frame cap for PW period detection (seatbelt)


def _pitch(note: int) -> Pitch:
    return Pitch(name=NOTE_NAMES[note % 12], octave=note // 12)


# --- PW oscillator -> SweepEnvelope (simulate-and-convert, ledger D1) ------
def _pw_env(m: V6Model, pw_init: int, pw_step: int) -> SweepEnvelope | None:
    """Simulate V6's PW oscillator one period and express it as a SweepEnvelope.

    Per frame: accum = (pw_init + t*pw_step) & $FF; PW16 = (LUThi[accum] & $0F)
    << 8 | LUTlo[(accum&$1F)|($20 if accum&$80)]. Group the per-frame PW16 value
    stream into maximal constant-difference runs -> (rate, frames) phases; one
    accumulator period -> loop=0. pw_step==0 -> constant (start only)."""
    lo, hi = m.pw_lut_lo, m.pw_lut_hi
    if not lo or not hi:
        return None

    def pw16(accum):
        idx = (accum & 0x1F) | (0x20 if accum & 0x80 else 0)
        return ((hi[accum] & 0x0F) << 8) | lo[idx]

    start = pw16(pw_init)
    if pw_step == 0:
        return SweepEnvelope(start=start, phases=[], loop=None)

    period = 256 // gcd(pw_step, 256)        # frames for accum to return to init
    period = min(period, _PW_SIM_CAP)
    vals = [pw16((pw_init + t * pw_step) & 0xFF) for t in range(period + 1)]
    diffs = [vals[t + 1] - vals[t] for t in range(period)]
    phases = []
    i = 0
    while i < len(diffs):
        j = i
        while j < len(diffs) and diffs[j] == diffs[i]:
            j += 1
        phases.append((diffs[i], j - i))
        i = j
    return SweepEnvelope(start=start, phases=phases, loop=0)


def _filter_env(cut: int, count: int, step: int) -> SweepEnvelope | None:
    """V6 filter sweep: a one-shot linear cutoff ramp. (count==0 = no sweep —
    a static cutoff at `cut`; step!=0 needs a count to ramp.)"""
    if count == 0:
        return SweepEnvelope(start=cut, phases=[], loop=None)
    s = step - 256 if step >= 128 else step
    return SweepEnvelope(start=cut, phases=[(s, count)], loop=None)


# --- wave program -> waveform/wave_freq/loop -------------------------------
def _wave_to_usf(prog) -> tuple[list, list, int]:
    ctrl = [s.ctrl for s in prog.steps]
    freq = [s.offset & 0xFF for s in prog.steps]
    return ctrl, freq, prog.loop


# --- pattern events -> note rows -------------------------------------------
def _pattern_rows(events: list) -> list:
    rows = []
    dur = 1
    pending = []
    for e in events:
        if isinstance(e, V6PatDuration):
            dur = e.dur
            pending.append(f'set_dur=${e.dur:02X}')
        elif isinstance(e, V6PatInstrument):
            pending.append(f'set_instr={e.instr}')
        elif isinstance(e, V6PatNote):
            rows.append(NoteRow(pitch=_pitch(e.note), duration=dur,
                                fx_flags=tuple(pending)))
            pending = []
    return rows


def _orderlist(ol: list) -> Orderlist:
    # V6 orderlists are a flat pattern-id list, $FF-terminated -> wrap to 0.
    return Orderlist(entries=list(ol), loop_to=0, stop=False)


def _instrument_to_usf(m: V6Model, ins) -> Instrument:
    prog = m.wave_programs.get(ins.wave_ptr)
    wc, wf, wl = _wave_to_usf(prog) if prog else ([], [], 0)
    if ins.pitch_delay:
        warnings.warn(
            f'dmc_v6: instrument {ins.id} uses pitch_delay='
            f'{ins.pitch_delay} (octave pitch-slide) — not yet mapped to USF '
            f'(deferred to composer+verify).')
    return Instrument(
        id=ins.id,
        waveform=wc,
        loop=wl,
        wave_freq=wf,
        adsr=(ins.ad, ins.sr),
        # pw_step==0 -> static PW (the oscillator does not move); keep_running
        # mirrors v5's "no restart" — the V6 oscillator phase is continuous.
        pwm=PwmConfig(keep_running=(ins.pw_step == 0)),
        pulse_env=_pw_env(m, ins.pw_init, ins.pw_step),
        filter_env=(_filter_env(ins.filt_cut, ins.filt_count, ins.filt_step)
                    if (ins.filt_count or ins.filt_cut) else None),
    )


def model_to_usf(m: V6Model) -> UsfFile:
    # one Pattern per pattern id (shared across voices that reference it).
    pat = {pid: Pattern(id=pid, length=0, rows=_pattern_rows(ev))
           for pid, ev in m.patterns.items()}
    for p in pat.values():
        p.length = sum(r.duration for r in p.rows)

    voices = []
    for vi in range(3):
        ol = _orderlist(m.orderlists[vi])
        used = sorted({s for s in ol.entries if s in pat})
        voices.append(VoiceBlock(id=vi + 1, orderlist=ol,
                                 patterns=[pat[s] for s in used]))

    instruments = [_instrument_to_usf(m, ins) for ins in m.instruments]

    sub = MusicSubtune(
        id=1, tempo=m.tempo, voices=voices,
        init=InitState(
            sid=InitSid(master_vol=0x0F,
                        filter=InitFilter(cutoff_lo=0, cutoff_hi=0,
                                          res_routing=0xF2))))

    return UsfFile(
        psid=PsidMeta(title=m.title, author=m.author, released=m.released,
                      start_song=1),
        params=Params(),
        init=InitState(),
        instruments=instruments,
        subtunes=[sub],
        freq_table=list(m.freq_lo) + list(m.freq_hi),
    )


def write_v6_usf(path: str, out_dir: str) -> str:
    m = extract(path)
    usf = model_to_usf(m)
    base = os.path.splitext(os.path.basename(path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out
