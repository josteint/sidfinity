"""Chimera → USF v2 adapter.

Reads the existing in-memory extraction (`ExtractedSong`, `EngineConfig`,
`extract_digi`) and produces a `UsfFile` + sample FLAC sidecars on disk.
This is the *write* side of the USF-only pipeline; the codegen-from-USF
*read* side is a separate refactor that comes after.

What lives where:

  Chimera.usf                     — UsfFile (everything non-sample)
  Chimera.sample2.flac            — bit stream + vol envelope (Vorbis)
  Chimera.sample3.flac            — same

The codegen-from-USF (not yet built) will load `Chimera.usf`, resolve
sample sidecars by filename, and produce a SID with NO peek at the
original.
"""

from __future__ import annotations

import os

from src.hubbard_emu import load_sid
from src.usf2 import (
    UsfFile, PsidMeta, Params, InitState, InitVoice,
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
    MusicSubtune, DigiSubtune, VoiceBlock, Orderlist, Pattern,
    NoteRow, Pitch, InstrumentRef, write_file, validate,
)
from pipelines.hubbard.flac_io import write_sample
from pipelines.chimera.extract.digi import extract_digi, to_sample


# ---------------------------------------------------------------------------
# Pitch encoding
#
# The Hubbard '85 freq table has 96 entries indexed 0-95. Pitch 0 is the
# lowest note the engine can play; pitches map directly to entries.
# We treat the index as semitones-from-C0 for display purposes (so
# pitch 60 → C-5). The codegen reverses the mapping. The absolute
# octave label is purely cosmetic; what's load-bearing is that the
# round-trip is exact.
# ---------------------------------------------------------------------------

_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


def pitch_from_engine(p: int) -> Pitch:
    """Convert an engine pitch byte to a `Pitch`. Any value >= 96
    indicates a rest (or off-table — same syntactic encoding)."""
    if p >= 96:
        return Pitch.rest()
    return Pitch(name=_NOTE_NAMES[p % 12], octave=p // 12)


# ---------------------------------------------------------------------------
# Note row conversion
#
# The Hubbard engine packs a per-note "instrument" byte where bit 7
# means "do NOT load a new instrument" (the voice keeps its current
# instrument). Low 6 bits hold the instrument id when bit 7 is clear.
# We translate semantically: row carries an `iN` ref when a new
# instrument is loaded, no ref otherwise.
#
# tie + drum_trig come pre-extracted as separate Note fields.
# ---------------------------------------------------------------------------

_NO_LOAD_INSTR_BIT = 0x80


def _row_from_note(note) -> NoteRow:
    pitch = pitch_from_engine(note.pitch)
    instr = None
    if not (note.instrument & _NO_LOAD_INSTR_BIT):
        # Engine stores 0-indexed; USF stores 1-indexed (i1 = first inst).
        instr = InstrumentRef(id=(note.instrument & 0x3F) + 1)
    flags: list[str] = []
    if note.tie:
        flags.append('tie')
    if note.drum_trig:
        flags.append('fx:drum')
    return NoteRow(pitch=pitch, duration=note.duration,
                   instr=instr, fx_flags=tuple(flags))


def _convert_voice(voice_idx: int, voice) -> VoiceBlock:
    # Orderlist: existing `Voice.loop` is the position to jump to
    # after the list ends, or -1 if no loop (use `stop`).
    if voice.stop:
        ol = Orderlist(entries=list(voice.orderlist), stop=True)
    else:
        loop_to = voice.loop if voice.loop >= 0 else 0
        ol = Orderlist(entries=list(voice.orderlist), loop_to=loop_to)

    patterns: list[Pattern] = []
    for pat_id in sorted(voice.patterns.keys()):
        rows = [_row_from_note(n) for n in voice.patterns[pat_id]]
        length = sum(r.duration for r in rows)
        patterns.append(Pattern(id=pat_id, length=length, rows=rows))

    return VoiceBlock(id=voice_idx + 1, orderlist=ol, patterns=patterns)


def _convert_score(subtune_id: int, score) -> MusicSubtune:
    voices = [_convert_voice(i, v) for i, v in enumerate(score.voices)]
    return MusicSubtune(id=subtune_id, tempo=score.tempo, voices=voices)


# ---------------------------------------------------------------------------
# Instrument conversion
#
# The Hubbard `Instrument` carries the engine-extracted shape; USF v2's
# `Instrument` is the engine-agnostic parametric form. The mapping is
# mostly 1:1; arpeggio gets converted from "single offset + engine-wide
# period" to "offsets list + per-instrument period."
# ---------------------------------------------------------------------------

def _convert_instrument(inst, arp_period: int) -> Instrument:
    return Instrument(
        id=inst.id + 1,                                       # USF 1-indexed
        name=None,
        waveform=list(inst.waveform.steps),
        loop=inst.waveform.loop,
        pwm=PwmConfig(
            mode=inst.pwm.mode,
            speed=inst.pwm.speed,
            init=inst.pwm.init_pw,
            min_hi=inst.pwm.min_hi,
            max_hi=inst.pwm.max_hi,
        ),
        adsr=(inst.envelope.ad, inst.envelope.sr),
        arp=ArpConfig(offsets=[0, inst.arp_offset], period=arp_period),
        vibrato=VibratoConfig(scale=inst.vibrato_scale),
        envelope=EnvelopeConfig(
            gate_off_delta=inst.envelope.gate_off_delta,
            adsr_zero_delta=inst.envelope.adsr_zero_delta,
        ),
    )


# ---------------------------------------------------------------------------
# Init state from the freq-table overlap bytes
#
# The original engine reads engine state from bytes past the 96-entry
# musical freq table — Hubbard's space-saving trick. The shared core
# already documents which byte offsets seed which per-voice variable:
#
#   +205/206/207  →  v_durfield   (vibrato carry path)
#   +208/209/210  →  v_ctrl       (initial SID ctrl byte)
#   +214/215/216  →  v_instr      (initial instrument id, 0-indexed)
#   +229/230/231  →  pwm_period   (PWM accumulator)
#   +232/233/234  →  pwm_dir      (PWM direction byte)
#   +239/240/241  →  v_slide      (skydive cached freq-hi)
#
# In USF v2 we extract these into a clean `init:` block. The codegen
# decides where to place them in the rebuilt binary — no longer the
# freq-table overlap, just named labels.
# ---------------------------------------------------------------------------

def _derive_init_state(binary: bytes, freq_table_base: int, load: int,
                       n_instruments: int) -> InitState:
    base = freq_table_base - load

    def at(off: int) -> int:
        return binary[base + off]

    voices = []
    for i in range(3):
        instr_byte = at(214 + i)
        # Engine stores 0-indexed instrument ids; USF is 1-indexed
        # (i1 = first instrument). Skip if the byte is out of range.
        instr_ref = None
        if 0 <= instr_byte < n_instruments:
            instr_ref = InstrumentRef(id=instr_byte + 1)
        voices.append(InitVoice(
            id=i + 1,
            dur_field=at(205 + i),
            ctrl=at(208 + i),
            instr=instr_ref,
            pwm_period=at(229 + i),
            pwm_dir='up' if at(232 + i) == 0 else 'down',
            slide_v=at(239 + i),
        ))
    return InitState(voices=voices)


# ---------------------------------------------------------------------------
# PSID header
# ---------------------------------------------------------------------------

def _read_psid_meta(sid_path: str) -> PsidMeta:
    raw = open(sid_path, 'rb').read()
    title    = raw[22:54].rstrip(b'\x00').decode('latin-1', errors='replace')
    author   = raw[54:86].rstrip(b'\x00').decode('latin-1', errors='replace')
    released = raw[86:118].rstrip(b'\x00').decode('latin-1', errors='replace')
    flags = int.from_bytes(raw[118:120], 'big')
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[(flags >> 2) & 3]
    sid = {0: 0, 1: 6581, 2: 8580, 3: 0}[(flags >> 4) & 3]
    start_song = int.from_bytes(raw[16:18], 'big')
    return PsidMeta(title=title, author=author, released=released,
                    clock=clock, sid=sid, start_song=start_song)


# ---------------------------------------------------------------------------
# Top-level adapter
# ---------------------------------------------------------------------------

def chimera_to_usf_v2(config) -> UsfFile:
    """Build a `UsfFile` from a Chimera `EngineConfig`. Pulls metadata
    from the SID header, params from the EngineConfig, init state from
    the freq-table overlap bytes, instruments from the existing
    extract, and music/digi subtunes from the existing extract +
    `extract_digi`."""
    _, binary, load = load_sid(config.sid_path)

    psid = _read_psid_meta(config.sid_path)

    params = Params(fields={
        'arp_interval':    config.arp_interval,
        'arp_period':      config.arp_period,
        'linear_pw_or':    config.linear_pw_or,
        'vib_onset':       config.vib_onset,
        'speed_ctr_init':  config.speed_ctr_init,
        'incby2_step':     config.incby2_step,
        'incby2_onset':    config.incby2_onset,
    })

    init = _derive_init_state(binary, config.freq_table_base, load,
                              config.instr_count)

    first_song = config.extract(subtune=config.subtunes[0])
    instruments = [_convert_instrument(i, config.arp_period)
                   for i in first_song.instruments]

    music_subtunes = []
    for st in config.subtunes:
        song = config.extract(subtune=st)
        music_subtunes.append(_convert_score(st, song.score))

    digi_subtunes = [DigiSubtune(id=st, sample=f'Chimera.sample{st}.flac')
                     for st in (config.digi_subtunes or ())]

    return UsfFile(
        version=2, engine=config.name,
        psid=psid, params=params, init=init,
        instruments=instruments,
        subtunes=music_subtunes + digi_subtunes,
    )


def write_chimera_usf(config, out_dir: str) -> str:
    """Write `Chimera.usf` + the digi sample FLAC sidecars into
    `out_dir`. Returns the path to the .usf file. Validates before
    writing."""
    os.makedirs(out_dir, exist_ok=True)
    usf = chimera_to_usf_v2(config)
    validate(usf)
    usf_path = os.path.join(out_dir, 'Chimera.usf')
    write_file(usf, usf_path)

    for st in (config.digi_subtunes or ()):
        sample = to_sample(extract_digi(config.sid_path, st))
        flac_path = os.path.join(out_dir, f'Chimera.sample{st}.flac')
        write_sample(sample, flac_path)

    # Re-validate with the sidecar check now that FLACs exist.
    validate(usf, usf_dir=out_dir)
    return usf_path
