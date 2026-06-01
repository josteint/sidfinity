"""Shared `extract → USF v2` adapter for Hubbard '85 engines.

Most of the conversion (PSID metadata, params, instruments, music
subtune scores, init state from the freq-table overlap) is engine-
agnostic. Per-engine code only adds:

  - Digi subtunes (e.g. Chimera): the engine's own `to_usf.py`
    extracts each digi via the engine-specific extractor and writes
    the FLAC sidecars; this shared adapter sees them as
    `DigiSubtune` entries already injected into the UsfFile.

  - SFX subtunes (e.g. Commando, Monty): once the SfxSubtune schema is
    fleshed out, those flow through `config.extract_sfx` into the
    USF via this adapter. Until then, this adapter just doesn't emit
    SFX subtunes — engines with SFX rebuild only their music subtunes
    through the USF path.

`to_usf(config) -> UsfFile` is the entry point. Each engine has a
thin `pipelines/<engine>/extract/to_usf.py` that calls this with
its own config + writes the file with the engine's basename.
"""

from __future__ import annotations

import os

from src.hubbard_emu import load_sid
from src.usf import (
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

def _convert_instrument(model, config) -> Instrument:
    """Build a USF `Instrument` from an `InstrumentModel` + engine
    `EngineConfig`.

    Phase 2 of the principled-instrument refactor: populates the new
    per-instrument sub-configs (`freq_slide_config`, `inc_by2_config`,
    `envelope.release_ctrl`, `arp.{interval,period,phase_invert}`,
    `vibrato.onset`) from the engine config's tune-level values. The
    legacy fields (`freq_slide: bool`, `inc_by2: bool`) stay populated
    for back-compat through Phase 2; Phase 3 drops them.

    For tunes that share one engine-level value across all instruments
    (every Hubbard '85 — engine hardcoded), the per-tune value is
    copied verbatim onto every instrument.

    `config` may be any object exposing the required EngineConfig
    field names — the 5TT unified writer's `_Inputs` shape lacks a
    few of them, hence the `getattr` defaults for the optional ones.
    """
    from src.usf.types import FreqSlideConfig, IncBy2Config

    # Tune-level fields — getattr with safe defaults so non-EngineConfig
    # callers (5TT's _Inputs) can pass their own shapes.
    arp_period       = getattr(config, 'arp_period',       2)
    arp_interval     = getattr(config, 'arp_interval',     12)
    arp_phase_invert = getattr(config, 'arp_phase_invert', False)
    vib_onset        = getattr(config, 'vib_onset',        6)
    incby2_step      = getattr(config, 'incby2_step',      2)
    incby2_onset     = getattr(config, 'incby2_onset',     3)
    incby2_late_gate = getattr(config, 'incby2_late_gate', None)

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

    # Phase 2: per-instrument musical sub-configs replace the legacy
    # `freq_slide: bool` / `inc_by2: bool` + per-tune params shape.

    # Hubbard's skydive is one-shot: v_slide decrements by 1 each frame
    # until it reaches 0, then halts. step=1 captures that. Bounds
    # default to 0 (target = 0 freq delta = freq drops to note value).
    # initial_dir='down' because v_slide DECREMENTS.
    freq_slide_config = FreqSlideConfig()
    if model.freq_slide:
        freq_slide_config = FreqSlideConfig(
            mode='one_shot_halt',
            initial_dir='down',
            upper_delta=0, lower_delta=0,
            step=1,
            high_oct_arp=False,
        )

    inc_by2_config = IncBy2Config()
    if model.inc_by2:
        # Hunter Patrol uses late_gated (config.incby2_late_gate set);
        # the rest use plain 'on'.
        mode = 'late_gated' if incby2_late_gate else 'on'
        inc_by2_config = IncBy2Config(
            mode=mode,
            step=incby2_step,
            onset=incby2_onset,
            late_gate=incby2_late_gate or 0,
        )

    # Hubbard's release CTRL is gate-on CTRL with the gate bit cleared.
    release_ctrl = model.init_ctrl & 0xFE

    return Instrument(
        id=model.inst + 1,                                  # USF 1-indexed
        name=None,
        waveform=[model.init_ctrl],
        loop=0,
        pwm=pwm,
        adsr=(model.init_ad, model.init_sr),
        arp=ArpConfig(
            offsets=offsets,
            period=arp_period,
            interval=arp_interval,
            phase_invert=arp_phase_invert,
        ),
        vibrato=VibratoConfig(scale=vibrato_scale, onset=vib_onset),
        envelope=EnvelopeConfig(release_ctrl=release_ctrl),
        freq_slide_config=freq_slide_config,
        inc_by2_config=inc_by2_config,
        # Phase 3b — legacy bools no longer written; the per-inst
        # sub-configs carry the same musical content. The composer
        # reads from the configs in preference to the bools.
    )


# ---------------------------------------------------------------------------
# Init state — the freq-table overlap bytes (see project_chimera.md /
# project_monty.md for the offset reasoning).
# ---------------------------------------------------------------------------

def _derive_init_state(binary: bytes, freq_table_base: int, load: int,
                       n_instruments: int) -> InitState:
    """Hubbard '85's per-voice init state is the byte the engine reads
    from the freq-table overlap region at runtime — the same bytes
    that are already stored in `engine_constants.freq_bytes` keyed by
    engine name. The values are 100% derivable from the engine
    constants, so the USF emits an empty init block and the codegen
    reads from engine constants at build time (see
    [[project_hubbard_principled_usf]] Phase 3).
    """
    return InitState(voices=[])


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

# EngineConfig fields that are NOT tune-level mechanism — extract-side
# concerns (callables, paths), memory-layout addresses the codegen
# embeds, or shape-incompatible fields handled outside this block.
_PARAMS_SKIP_CONFIG = {
    'name', 'sid_path', 'extract', 'resetspd', 'extract_sfx',
    'subtunes', 'instr_base', 'instr_count', 'freq_table_base',
    'voice_starts', 'digi_subtunes', 'is_rsid',
    # Phase 3b — these tune-level fields are now per-instrument
    # (vibrato.onset, arp.interval/period/phase_invert,
    # inc_by2_config.{step,onset,late_gate}). Composer reads them
    # from any instrument. Stop emitting into params { } entirely.
    'vib_onset', 'arp_interval', 'arp_period', 'arp_phase_invert',
    'incby2_step', 'incby2_onset', 'incby2_late_gate',
}

# Engine name → tune-level `digi_player` name in the v3 USF. The
# registry that resolves the name back to a DigiCode lives in
# `pipelines/build_from_usf.py`.
_DIGI_NAMES = {
    'chimera': 'chimera_1bit',
}


def _params_from_config(config) -> Params:
    """Build the top-level USF `params { }` block for a v3 extract.

    Carries every `EngineConfig` field that DIFFERS from the engine's
    own defaults (Commando-flavor) — named scalars/booleans, no opaque
    kinds. Memory-layout fields and structured data
    (state_layout, freq_bytes, digi) flow in from `EngineConstants`
    separately.
    """
    from dataclasses import fields as dataclass_fields, MISSING
    from pipelines.hubbard.engine_constants import ENGINE_CONSTANTS

    out: dict = {}
    for f in dataclass_fields(type(config)):
        if f.name in _PARAMS_SKIP_CONFIG:
            continue
        if f.default is MISSING:
            continue
        v = getattr(config, f.name)
        if v != f.default and v is not None:
            out[f.name] = v
    # EngineConstants-only fields (no EngineConfig counterpart) that
    # still belong in the v3 USF's params: `ns_offtab_decr_offset`
    # (Thing on a Spring) and `hubidx_wrap_at_patend` (ToaS, default
    # False breaks the codec's wrap behavior).
    ec = ENGINE_CONSTANTS.get(config.name)
    if ec is not None:
        if ec.ns_offtab_decr_offset is not None:
            out['ns_offtab_decr_offset'] = ec.ns_offtab_decr_offset
        if ec.hubidx_wrap_at_patend is not True:
            out['hubidx_wrap_at_patend'] = ec.hubidx_wrap_at_patend
        if ec.digi is not None and config.name in _DIGI_NAMES:
            out['digi_player'] = _DIGI_NAMES[config.name]
    return Params(fields=out)


# Canonical Commando-family seed offsets — engines that deviate get
# their freq_table normalised at extract time so the v3 codegen reads
# at fixed positions.
_DEFAULT_SEEDS = {
    'v_ctrl': 208, 'pwm_period': 229, 'pwm_dir': 232,
    'v_instr': 214, 'v_durfield': 205, 'v_slide': 239,
}


def _normalize_freq_table(freq_bytes: bytes, seed_offsets) -> bytes:
    """Move engine-specific seed_offset bytes to canonical positions.

    The v3 USF carries the normalised table; the universal codegen
    reads voice state at the canonical positions for every engine.
    Bytes that get overwritten by the move keep their original values
    in the source positions (which the codegen never reads anyway).
    """
    if not seed_offsets:
        return bytes(freq_bytes)
    fb = bytearray(freq_bytes)
    for name, src_off in seed_offsets.items():
        dst_off = _DEFAULT_SEEDS[name]
        if src_off != dst_off:
            for v in range(3):
                fb[dst_off + v] = freq_bytes[src_off + v]
    return bytes(fb)


def _state_layout_dict(state_layout) -> dict | None:
    if state_layout is None:
        return None

    def slot_dict(s):
        if s.kind == 'const':
            return {'offset': s.offset, 'kind': 'const', 'value': s.value}
        return {'offset': s.offset, 'kind': 'var', 'var': s.var}

    return {
        'n_voices': state_layout.n_voices,
        'scalars': [slot_dict(s) for s in state_layout.scalars],
        'per_voice': [slot_dict(s) for s in state_layout.per_voice],
    }


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

def to_usf(config, extra_subtunes: list | None = None) -> UsfFile:
    """Build a v3 `UsfFile` from an `EngineConfig` — engine-name-blind,
    self-contained. The name is historical; it now emits version 3.

    A v3 UsfFile carries:
      - inlined freq_table (normalised so seed_offsets land at canonical
        positions)
      - state_layout block for engines with non-default scratch layout
      - named param overrides (only fields differing from defaults)
      - per-subtune `voice_start` params (e.g. Action Biker)
      - digi_player named reference (e.g. Chimera)

    Engine-specific extras (digi subtunes for Chimera) flow in via
    `extra_subtunes`.
    """
    from pipelines.hubbard.engine_constants import ENGINE_CONSTANTS

    _, binary, load = load_sid(config.sid_path)

    psid = _read_psid_meta(config.sid_path)
    params = _params_from_config(config)
    # Phase 3: per-voice init bytes are derivable from freq_bytes;
    # emit an empty init block.
    init = InitState(voices=[])

    models = decode_all(config.sid_path, config.instr_base,
                        config.instr_count, config.arp_interval,
                        config.vib_onset, config.arp_period)
    instruments = [_convert_instrument(m, config) for m in models]

    music_subtunes = []
    for st in config.subtunes:
        song = config.extract(subtune=st)
        ms = _convert_score(st, song.score)
        music_subtunes.append(ms)

    # SFX subtunes — Hubbard '85 SFX records (Commando-style). PSID
    # subtunes len(config.subtunes)..len(config.subtunes)+15.
    sfx_subtunes = []
    if config.has_sfx and config.extract_sfx is not None:
        sfx_list, _ = config.extract_sfx(config.sid_path)
        for offset, sfx in enumerate(sfx_list):
            sfx_id = len(config.subtunes) + offset
            sfx_subtunes.append(_convert_sfx(sfx, sfx_id))

    subtunes = music_subtunes + sfx_subtunes + list(extra_subtunes or [])

    # Pull freq_table and state_layout from engine_constants. Engines
    # without a registered EngineConstants entry produce a USF without
    # these blocks (rare path used by tests).
    ec = ENGINE_CONSTANTS.get(config.name)
    freq_table = None
    state_layout = None
    if ec is not None:
        freq_table = list(_normalize_freq_table(ec.freq_bytes,
                                                 ec.seed_offsets))
        state_layout = _state_layout_dict(ec.state_layout)
        # Per-subtune voice_start.
        for ms in music_subtunes:
            vs = ec.voice_starts.get(ms.id, None)
            if vs is not None and vs != 2:
                if ms.params is None:
                    ms.params = Params(fields={})
                ms.params.fields['voice_start'] = vs

    return UsfFile(
        psid=psid, params=params, init=init,
        instruments=instruments, subtunes=subtunes,
        freq_table=freq_table, state_layout=state_layout,
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
    usf = to_usf(config, extra_subtunes=extra_subtunes)
    validate(usf)

    basename = _basename_for(config.name)
    usf_path = os.path.join(out_dir, f'{basename}.usf')
    write_file(usf, usf_path)

    for fname, writer in (extra_sidecar_writes or []):
        writer(os.path.join(out_dir, fname))

    validate(usf, usf_dir=out_dir)

    try:
        from src.sid_db import record_usf
        record_usf(usf_path)
    except Exception:
        pass    # db update is best-effort; never break the build

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
        'battle_of_britain': 'Battle_of_Britain',
        'confuzion': 'Confuzion',
        'five_tt_sub0': '5_Title_Tunes_0',
        'five_tt_sub1': '5_Title_Tunes_1',
        'five_tt_sub2': '5_Title_Tunes_2',
        'five_tt_sub3': '5_Title_Tunes_3',
        'five_tt_sub4': '5_Title_Tunes_4',
        'five_title_tunes': '5_Title_Tunes',
    }.get(engine_name, engine_name.title())
