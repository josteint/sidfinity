"""USF v2 → SID codegen.

The *read* side of the USF-only pipeline. Reads `<basename>.usf` and
the sibling `<basename>.sampleN.flac` files; does NOT peek at the
original SID. Produces a SID functionally equivalent to the original
(verified via verify_all: py65 frame-exact for music, writelog
cycle-strict for digi).

Per-engine constants (instrument-table address, freq-table addresses,
the 320-byte freq-table region) live in
`pipelines/hubbard/engine_constants.py` — these are engine *code*
properties, the same across all tunes of one engine. Tune data is
entirely in the USF + sidecar FLACs.
"""

from __future__ import annotations

import os

from src.usf2 import (
    UsfFile, MusicSubtune, DigiSubtune, parse_file, validate,
)
from pipelines.hubbard.codegen import _Inputs, _emit_sid
from pipelines.hubbard.engine_constants import ENGINE_CONSTANTS
from pipelines.hubbard.inst_generalize import (
    InstrumentModel, ArpSpec, VibratoSpec, PwmSpec,
)
from pipelines.hubbard.types import (
    Score, Voice, Note, Instrument as HubInstrument,
)


# ---------------------------------------------------------------------------
# USF → InstrumentModel (the inverse of pipelines/chimera/extract/to_usf_v2.
# _convert_instrument)
# ---------------------------------------------------------------------------

def _model_from_usf_instrument(u, vib_onset: int) -> InstrumentModel:
    init_ctrl = u.waveform[0] if u.waveform else 0
    init_pw_lo = u.pwm.init & 0xFF
    init_pw_hi = (u.pwm.init >> 8) & 0xFF

    pwm = None
    pw_lo_kind = 'const'
    pw_hi_kind = 'const'
    if u.pwm.mode == 'linear':
        pwm = PwmSpec(mode='linear', speed=u.pwm.speed,
                      seed_lo=init_pw_lo, seed_hi=init_pw_hi,
                      lo_bound=u.pwm.min_hi, hi_bound=u.pwm.max_hi)
        pw_lo_kind = 'accumulator'
    elif u.pwm.mode == 'bidirectional':
        pwm = PwmSpec(mode='bidirectional',
                      period=u.pwm.speed & 0x1F,
                      step=u.pwm.speed & 0xE0,
                      seed_lo=init_pw_lo, seed_hi=init_pw_hi,
                      lo_bound=u.pwm.min_hi, hi_bound=u.pwm.max_hi)
        pw_lo_kind = pw_hi_kind = 'accumulator'

    # Arpeggio: USF stores [0] when off, full offsets list when on.
    has_arp = len(u.arp.offsets) > 1
    arpeggio = (ArpSpec(intervals=tuple(u.arp.offsets), step_every=1)
                if has_arp else None)

    vibrato = (VibratoSpec(depth=u.vibrato.scale, onset_dur=vib_onset)
               if u.vibrato.scale != 0 else None)

    # Reconstruct the engine's fx_flags byte from the structured fields.
    fx_flags = ((1 if u.freq_slide else 0)
                | (2 if u.inc_by2 else 0)
                | (4 if has_arp else 0)
                | (8 if u.pwm.mode == 'linear' else 0))

    return InstrumentModel(
        inst=u.id - 1,                              # back to 0-indexed
        init_ctrl=init_ctrl,
        init_pw_lo=init_pw_lo,
        init_pw_hi=init_pw_hi,
        init_ad=u.adsr[0],
        init_sr=u.adsr[1],
        hr_ctrl=init_ctrl & 0xFE,
        pw_lo_kind=pw_lo_kind, pw_hi_kind=pw_hi_kind,
        fx_flags=fx_flags,
        freq_slide=u.freq_slide, inc_by2=u.inc_by2,
        arpeggio=arpeggio, vibrato=vibrato, pwm=pwm,
    )


# ---------------------------------------------------------------------------
# USF → Score (the extract-output shape the codegen consumes)
# ---------------------------------------------------------------------------

_NOTE_TO_NUM = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

# A pitch byte the engine treats as "no fresh note." Hubbard '85 uses
# values past the 96-entry musical freq table as off-table / rest. We
# use a sentinel that's safely past 95 and won't collide with arpeggio
# extensions.
_REST_PITCH = 0xFF


def _pitch_to_engine(p) -> int:
    if p.is_rest:
        return _REST_PITCH
    semis = _NOTE_TO_NUM[p.name] + 12 * p.octave
    return semis


def _instr_to_engine_byte(instr_ref, current_instr: int) -> int:
    """Convert a USF NoteRow's `instr` field back to the engine's
    per-note instrument byte. When no ref is present, set the high bit
    ('do not load new instrument'). When a ref is present, emit the
    instrument's 0-indexed id with high bit clear."""
    if instr_ref is None:
        return current_instr | 0x80
    # USF is 1-indexed; engine is 0-indexed.
    return (instr_ref.id - 1) & 0x3F


def _flags_to_engine(fx_flags: tuple) -> tuple[bool, int]:
    """Translate USF fx flag tokens back to (tie_bool, drum_trig_byte).

    Inverse of `to_usf_v2._row_from_note`:
      tie         <- 'tie' token
      drum_trig   <- (0x80 if 'no_release') | porta_amount
    """
    tie = 'tie' in fx_flags
    drum_trig = 0x80 if 'no_release' in fx_flags else 0
    for flag in fx_flags:
        if flag.startswith('porta='):
            drum_trig |= int(flag[len('porta='):]) & 0x7F
    return tie, drum_trig


def _score_from_subtune(sub: MusicSubtune) -> Score:
    voices = []
    for vb in sub.voices:
        orderlist = list(vb.orderlist.entries)
        loop = vb.orderlist.loop_to if vb.orderlist.loop_to is not None else -1
        stop = vb.orderlist.stop
        patterns = {}
        for pat in vb.patterns:
            current_instr = 0
            notes = []
            for row in pat.rows:
                if row.instr is not None:
                    current_instr = row.instr.id - 1
                inst_byte = _instr_to_engine_byte(row.instr, current_instr)
                tie, drum = _flags_to_engine(row.fx_flags)
                notes.append(Note(
                    pitch=_pitch_to_engine(row.pitch),
                    duration=row.duration,
                    instrument=inst_byte,
                    tie=tie,
                    drum_trig=drum,
                ))
            patterns[pat.id] = notes
        voices.append(Voice(orderlist=orderlist, patterns=patterns,
                            loop=loop, stop=stop))
    return Score(tempo=sub.tempo, voices=voices)


# ---------------------------------------------------------------------------
# Freq bytes: 320 bytes that go at freqtab. First 192 = standard PAL
# musical freq table (engine constant). Bytes at +205, +208, +214,
# +229, +232, +239 come from USF init. Remaining engine state may also
# come from the per-engine constant (scratch values etc.) — we let the
# engine constants supply EVERYTHING, then overlay the init values.
# ---------------------------------------------------------------------------

def _freq_bytes_from_usf(usf: UsfFile, engine_const) -> bytes:
    fb = bytearray(engine_const.freq_bytes)
    for v in usf.init.voices:
        i = v.id - 1
        fb[205 + i] = v.dur_field
        fb[208 + i] = v.ctrl
        if v.instr is not None:
            fb[214 + i] = (v.instr.id - 1) & 0xFF
        fb[229 + i] = v.pwm_period
        fb[232 + i] = 0x00 if v.pwm_dir == 'up' else 0xFF
        fb[239 + i] = v.slide_v
    return bytes(fb)


# ---------------------------------------------------------------------------
# USF → _Inputs
# ---------------------------------------------------------------------------

def _inputs_from_usf(usf: UsfFile) -> _Inputs:
    """Build codegen `_Inputs` purely from a parsed UsfFile + the
    per-engine constants. No binary or sid_path access."""
    if usf.engine not in ENGINE_CONSTANTS:
        raise ValueError(
            f'no engine constants registered for engine {usf.engine!r}; '
            f'add to pipelines/hubbard/engine_constants.py')
    ec = ENGINE_CONSTANTS[usf.engine]

    # PSID metadata
    def latin1(s: str) -> bytes:
        return s.encode('latin-1', errors='replace')

    # Engine equates / asm flags
    p = usf.params.fields

    def get(key: str, default):
        return p.get(key, default)

    # Instruments — convert USF → InstrumentModel
    models = [_model_from_usf_instrument(u, get('vib_onset', 6))
              for u in usf.instruments]

    # Music subtunes only (digi handled elsewhere for now)
    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    music_subs.sort(key=lambda s: s.id)
    subtune_ids = tuple(s.id for s in music_subs)
    scores = [_score_from_subtune(s) for s in music_subs]
    resetspds = [s.tempo - 1 for s in music_subs]
    voice_starts = [ec.voice_starts.get(s.id, 2) for s in music_subs]

    freq_bytes = _freq_bytes_from_usf(usf, ec)

    return _Inputs(
        title=latin1(usf.psid.title),
        author=latin1(usf.psid.author),
        released=latin1(usf.psid.released),
        start_song=usf.psid.start_song,
        arp_interval=get('arp_interval', 12),
        arp_period=get('arp_period', 2),
        linear_pw_or=get('linear_pw_or', 0),
        incby2_step=get('incby2_step', 2),
        incby2_every_frame=get('incby2_every_frame', False),
        incby2_onset=get('incby2_onset', 3),
        suppress_first_notestart=get('suppress_first_notestart', False),
        freeze_on_stop=get('freeze_on_stop', False),
        speed_ctr_init=get('speed_ctr_init', 0),
        first_frame_gate_off=get('first_frame_gate_off', False),
        stop_fill=get('stop_fill', None),
        sfx_framectr_ofs=ec.sfx_framectr_ofs,
        sfx_state_ofs=ec.sfx_state_ofs,
        has_sfx=ec.has_sfx,
        subtunes=subtune_ids,
        models=models, scores=scores, resetspds=resetspds,
        voice_starts=voice_starts, freq_bytes=freq_bytes,
        sfx_list=[],                # SFX from USF: TBD (not Chimera)
    )


def build_from_usf(usf_path: str, out_path: str, codec=None) -> str:
    """Read `usf_path` + its sample sidecars, produce a SID at `out_path`.
    No access to the original SID — this is the principled path."""
    from pipelines.hubbard.note_codec import BitPackCodec
    if codec is None:
        codec = BitPackCodec()
    usf = parse_file(usf_path)
    validate(usf, usf_dir=os.path.dirname(os.path.abspath(usf_path)))
    inputs = _inputs_from_usf(usf)
    return _emit_sid(inputs, out_path, codec)
