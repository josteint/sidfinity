"""Shared `extract → USF v2` adapter for Hubbard '85 engines.

Most of the conversion (PSID metadata, params, instruments, music
subtune scores, init state from the freq-table overlap) is engine-
agnostic. Per-engine code only adds:

  - Digi subtunes (e.g. Chimera): the engine's own `to_usf_v2.py`
    extracts each digi via the engine-specific extractor and writes
    the FLAC sidecars; this shared adapter sees them as
    `DigiSubtune` entries already injected into the UsfFile.

  - SFX subtunes (e.g. Commando, Monty): once the SfxSubtune schema is
    fleshed out, those flow through `config.extract_sfx` into the
    USF via this adapter. Until then, this adapter just doesn't emit
    SFX subtunes — engines with SFX rebuild only their music subtunes
    through the USF path.

`to_usf_v2(config) -> UsfFile` is the entry point. Each engine has a
thin `pipelines/<engine>/extract/to_usf_v2.py` that calls this with
its own config + writes the file with the engine's basename.
"""

from __future__ import annotations

import os

from src.hubbard_emu import load_sid
from src.usf2 import (
    UsfFile, PsidMeta, Params, InitState, InitVoice,
    Instrument, PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig,
    MusicSubtune, DigiSubtune, SfxSubtune, VoiceBlock, Orderlist,
    Pattern, NoteRow, Pitch, InstrumentRef, write_file, validate,
)
from pipelines.hubbard.inst_generalize import decode_all


# ---------------------------------------------------------------------------
# Pitch encoding (engine 0-95 → musical name + octave)
# ---------------------------------------------------------------------------

_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


def pitch_from_engine(p: int) -> Pitch:
    """Engine pitch byte → `Pitch`. Pitches 0..95 sit inside the 96-
    entry musical freq table; pitches 96+ are *off-table* — the engine
    reads past the table into the state region for arpeggio extension
    notes. Both encode as note-name + octave; octave can go past 7."""
    return Pitch(name=_NOTE_NAMES[p % 12], octave=p // 12)


# ---------------------------------------------------------------------------
# Note row conversion — Hubbard's instrument-byte encoding
#
# The per-note `instrument` byte: bit 7 = "don't load a new instrument"
# (the voice keeps its current). Low 6 bits = the instrument id when
# bit 7 is clear. tie + drum_trig are pre-extracted into separate
# Note fields. drum_trig is multi-bit: bit 7 = no_release, bits 0-6 =
# portamento amount.
# ---------------------------------------------------------------------------

_NO_LOAD_INSTR_BIT = 0x80


def _row_from_note(note) -> NoteRow:
    pitch = pitch_from_engine(note.pitch)
    instr = None
    if not (note.instrument & _NO_LOAD_INSTR_BIT):
        instr = InstrumentRef(id=(note.instrument & 0x3F) + 1)
    flags: list[str] = []
    if note.tie:
        flags.append('tie')
    if note.drum_trig & 0x80:
        flags.append('no_release')
    porta_amt = note.drum_trig & 0x7F
    if porta_amt:
        flags.append(f'porta={porta_amt}')
    return NoteRow(pitch=pitch, duration=note.duration,
                   instr=instr, fx_flags=tuple(flags))


def _convert_voice(voice_idx: int, voice) -> VoiceBlock:
    if voice.stop or not voice.orderlist:
        # Empty orderlists encode as `stop=True` (codegen emits a bare
        # $FE terminator). HR's V3 is silent across all subtunes.
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
# Instrument conversion — `InstrumentModel` → USF v2 `Instrument`
# ---------------------------------------------------------------------------

def _convert_instrument(model, arp_period: int) -> Instrument:
    init_pw = (model.init_pw_hi << 8) | model.init_pw_lo
    if model.pwm is None:
        pwm = PwmConfig(mode='none', speed=0, init=init_pw)
    elif model.pwm.mode == 'linear':
        pwm = PwmConfig(
            mode='linear', speed=model.pwm.speed, init=init_pw,
            min_hi=model.pwm.lo_bound, max_hi=model.pwm.hi_bound,
        )
    else:
        pwm = PwmConfig(
            mode='bidirectional',
            speed=(model.pwm.period | model.pwm.step), init=init_pw,
            min_hi=model.pwm.lo_bound, max_hi=model.pwm.hi_bound,
        )

    offsets = (list(model.arpeggio.intervals)
               if model.arpeggio is not None else [0])
    vibrato_scale = model.vibrato.depth if model.vibrato else 0

    return Instrument(
        id=model.inst + 1,                                  # USF 1-indexed
        name=None,
        waveform=[model.init_ctrl],
        loop=0,
        pwm=pwm,
        adsr=(model.init_ad, model.init_sr),
        arp=ArpConfig(offsets=offsets, period=arp_period),
        vibrato=VibratoConfig(scale=vibrato_scale),
        envelope=EnvelopeConfig(gate_off_delta=0, adsr_zero_delta=0),
        freq_slide=model.freq_slide,
        inc_by2=model.inc_by2,
    )


# ---------------------------------------------------------------------------
# Init state — the freq-table overlap bytes (see project_chimera.md /
# project_monty.md for the offset reasoning).
# ---------------------------------------------------------------------------

def _derive_init_state(binary: bytes, freq_table_base: int, load: int,
                       n_instruments: int) -> InitState:
    base = freq_table_base - load

    def at(off: int) -> int:
        return binary[base + off]

    voices = []
    for i in range(3):
        instr_byte = at(214 + i)
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
# PSID header — title / author / released / clock / sid / start_song.
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
    speed = int.from_bytes(raw[18:22], 'big')
    return PsidMeta(title=title, author=author, released=released,
                    clock=clock, sid=sid, start_song=start_song,
                    speed=speed)


# ---------------------------------------------------------------------------
# Params — the EngineConfig fields the codegen reads.
# ---------------------------------------------------------------------------

def _params_from_config(config) -> Params:
    """Project each EngineConfig field onto the USF `params:` block.

    Engine-specific defaults are preserved in `EngineConfig`; this
    function carries them through into the USF unconditionally. The
    codegen's `_inputs_from_usf` reads these back, falling back on a
    sensible default when a field is absent (legacy engines that
    were extracted before a field existed).
    """
    return Params(fields={
        'arp_interval':              config.arp_interval,
        'arp_period':                config.arp_period,
        'arp_phase_invert':          config.arp_phase_invert,
        'linear_pw_or':              config.linear_pw_or,
        'vib_onset':                 config.vib_onset,
        'speed_ctr_init':            config.speed_ctr_init,
        'incby2_step':               config.incby2_step,
        'incby2_every_frame':        config.incby2_every_frame,
        'incby2_onset':              config.incby2_onset,
        'suppress_first_notestart':  config.suppress_first_notestart,
        'freeze_on_stop':            config.freeze_on_stop,
        'first_frame_gate_off':      config.first_frame_gate_off,
        'seed_overlap':              config.seed_overlap,
        'frame_ctr_init':            config.frame_ctr_init,
        'incby2_late_gate':          (config.incby2_late_gate
                                      if config.incby2_late_gate is not None
                                      else -1),
        'has_incby2_late_gate':      (config.incby2_late_gate is not None),
        'stop_fill':                 (config.stop_fill
                                      if config.stop_fill is not None
                                      else 0),
        'has_stop_fill':             (config.stop_fill is not None),
    })


# ---------------------------------------------------------------------------
# SFX conversion — Hubbard '85 SoundEffect → USF v2 SfxSubtune
#
# The SoundEffect's `v1` and `v2` are 7-byte lists (freq_lo, freq_hi,
# pw_lo, pw_hi, ctrl, ad, sr). In USF v2 we drop the freq_lo bytes —
# v1.freq_lo is aliased with start_index, v2.freq_lo is aliased with
# the gate flags + v2_offset. Both are derived at codegen time.
# ---------------------------------------------------------------------------

def _convert_sfx(sfx, sfx_id: int) -> SfxSubtune:
    return SfxSubtune(
        id=sfx_id,
        v1=tuple(sfx.v1[1:7]),          # freq_hi, pw_lo, pw_hi, ctrl, ad, sr
        v2=tuple(sfx.v2[1:7]),
        start_index=sfx.start_index,
        end_index=sfx.end_index,
        rate=sfx.rate,
        direction=sfx.direction,
        v2_offset=sfx.v2_byte_offset,
        toggle_v1=sfx.toggle_v1,
        toggle_v2=sfx.toggle_v2,
        skip_v1=sfx.skip_v1,
        skip_both=sfx.skip_both,
    )


# ---------------------------------------------------------------------------
# Top-level adapter
# ---------------------------------------------------------------------------

def to_usf_v2(config, extra_subtunes: list | None = None) -> UsfFile:
    """Build a `UsfFile` from an `EngineConfig`. Engine-specific extras
    (digi subtunes for Chimera, SFX records for Commando/Monty in
    future) are passed via `extra_subtunes`."""
    _, binary, load = load_sid(config.sid_path)

    psid = _read_psid_meta(config.sid_path)
    params = _params_from_config(config)
    init = _derive_init_state(binary, config.freq_table_base, load,
                              config.instr_count)

    models = decode_all(config.sid_path, config.instr_base,
                        config.instr_count, config.arp_interval,
                        config.vib_onset, config.arp_period)
    instruments = [_convert_instrument(m, config.arp_period) for m in models]

    music_subtunes = []
    for st in config.subtunes:
        song = config.extract(subtune=st)
        music_subtunes.append(_convert_score(st, song.score))

    # SFX subtunes — Hubbard '85 SFX records (Commando-style). PSID
    # subtunes len(config.subtunes)..len(config.subtunes)+15.
    sfx_subtunes = []
    if config.has_sfx and config.extract_sfx is not None:
        sfx_list, _ = config.extract_sfx(config.sid_path)
        for offset, sfx in enumerate(sfx_list):
            sfx_id = len(config.subtunes) + offset
            sfx_subtunes.append(_convert_sfx(sfx, sfx_id))

    subtunes = music_subtunes + sfx_subtunes + list(extra_subtunes or [])

    return UsfFile(
        version=2, engine=config.name,
        psid=psid, params=params, init=init,
        instruments=instruments, subtunes=subtunes,
    )


def write_usf(config, out_dir: str,
              extra_subtunes: list | None = None,
              extra_sidecar_writes=None) -> str:
    """Write `<config.name with first letter capitalised>.usf` plus
    any sample sidecars to `out_dir`. Returns the .usf path.

    `extra_sidecar_writes` is a list of `(filename, write_callable)`
    tuples for sample sidecars (e.g. Chimera's two `.flac` files).
    """
    os.makedirs(out_dir, exist_ok=True)
    usf = to_usf_v2(config, extra_subtunes=extra_subtunes)
    validate(usf)

    basename = _basename_for(config.name)
    usf_path = os.path.join(out_dir, f'{basename}.usf')
    write_file(usf, usf_path)

    for fname, writer in (extra_sidecar_writes or []):
        writer(os.path.join(out_dir, fname))

    validate(usf, usf_dir=out_dir)
    return usf_path


def _basename_for(engine_name: str) -> str:
    """Engine name → user-visible USF basename. Matches the original
    SID's filename convention (e.g. 'commando' → 'Commando',
    'devils_galop' → 'Devils_Galop', 'action_biker' → 'Action_Biker',
    'monty' → 'Monty_on_the_Run', 'chimera' → 'Chimera').
    """
    return {
        'chimera': 'Chimera',
        'commando': 'Commando',
        'devils_galop': 'Devils_Galop',
        'action_biker': 'Action_Biker',
        'monty': 'Monty_on_the_Run',
        'human_race': 'Human_Race',
        'hunter_patrol': 'Hunter_Patrol',
        'thing_on_a_spring': 'Thing_on_a_Spring',
        'one_man_and_his_droid': 'One_Man_and_his_Droid',
        'five_tt_sub0': '5_Title_Tunes_0',
        'five_tt_sub1': '5_Title_Tunes_1',
        'five_tt_sub2': '5_Title_Tunes_2',
        'five_tt_sub3': '5_Title_Tunes_3',
        'five_tt_sub4': '5_Title_Tunes_4',
    }.get(engine_name, engine_name.title())
