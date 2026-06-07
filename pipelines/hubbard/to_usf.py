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
    SongEndConfig, InitBehaviorConfig, MasterVolConfig, SfxConfig,
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

def _scale_byte_to_depth_semitones(scale: int) -> float:
    """Convert Hubbard's per-instrument vibrato `scale` byte to its
    musical depth in semitones (descriptive metadata for the model).

    Hubbard's `fx_vibrato` runs a `dec ctr; bpl` shift loop with
    `ctr` starting at the scale byte. The loop body shifts a 16-bit
    "semitone-delta" register right by one bit each iteration. Net
    amplitude = `(semitone_delta * 3) / 2^N` where N = number of
    shifts and 3 is the max triangle-LFO step. In semitones, the
    one-semitone reference value cancels to `3 / 2^N`.

    Loop iteration count `N`:
      scale 0..127        → N = scale + 1
      scale 128           → N = 129 (loop iterates with $7F..$00 + $FF)
      scale 129..255      → N = 1   (first `dec` produces a negative
                                     value, BPL doesn't branch)

    For N >= 16 the semitone value is effectively zero (16-bit value
    fully shifted out). Conventionally returns 0.0 in that case.
    """
    if scale <= 127:
        shifts = scale + 1
    elif scale == 128:
        shifts = 129
    else:  # 129..255
        shifts = 1
    if shifts >= 16:
        return 0.0
    return 3.0 / (2 ** shifts)


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
    incby2_every_frame = getattr(config, 'incby2_every_frame', False)
    linear_pw_or     = getattr(config, 'linear_pw_or',     0)

    init_pw = (model.init_pw_hi << 8) | model.init_pw_lo
    # lo_or_mask only applies to linear-PWM instruments (engine ORs it
    # in the linear-PW update routine). Bidirectional + no-PWM don't
    # read it; default 0.
    if model.pwm is None:
        pwm = PwmConfig(mode='none', speed=0, init=init_pw)
    elif model.pwm.mode == 'linear':
        pwm = PwmConfig(
            mode='linear', speed=model.pwm.speed, init=init_pw,
            min_hi=model.pwm.lo_bound, max_hi=model.pwm.hi_bound,
            lo_or_mask=linear_pw_or,
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
            every_frame=incby2_every_frame,
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
        vibrato=VibratoConfig(
            scale=vibrato_scale, onset=vib_onset,
            depth_semitones=_scale_byte_to_depth_semitones(vibrato_scale)
            if model.vibrato else 0.0,
        ),
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
    'incby2_step', 'incby2_onset', 'incby2_late_gate', 'incby2_every_frame',
    # song-end refactor — these three flat keys now live in the
    # typed `song_end` block at top-level.
    'freeze_on_stop', 'stop_fill', 'loop_silences_song',
    # init_behavior refactor — these flat keys now live in the typed
    # `init_behavior { silence_all_voices_on_frame_0,
    # no_first_attack_voice }` block at top-level.
    'first_frame_gate_off', 'suppress_first_notestart',
    'master_vol_every_frame', 'master_vol_every_note',
    # linear_pw_or now lives per-instrument as pwm.lo_or_mask
    # (only meaningful for linear-PWM instruments).
    'linear_pw_or',
    # master_vol_* now live in the typed master_vol {} block.
    'master_vol_subtrahend_voice', 'master_vol_base', 'master_vol_trigger',
    'master_vol_reset_on_loop', 'master_vol_underflow_clamp',
    # SFX bookkeeping now lives in the typed sfx {} block. Block
    # presence signals has_sfx=True; default Commando layout when
    # state_ofs is None.
    'has_sfx', 'sfx_framectr_ofs', 'sfx_state_ofs',
}


def _sfx_from_config(config) -> SfxConfig | None:
    """Derive an `SfxConfig` from per-engine SFX bookkeeping. None when
    the engine has no SFX sub-engine."""
    if not getattr(config, 'has_sfx', False):
        return None
    return SfxConfig(
        framectr_ofs=getattr(config, 'sfx_framectr_ofs', 253),
        state_ofs=getattr(config, 'sfx_state_ofs', None),
    )


def _master_vol_from_config(config) -> MasterVolConfig | None:
    """Derive a `MasterVolConfig` from the per-engine flat keys. None
    when subtrahend_voice is unset (= no modulation active)."""
    sv = getattr(config, 'master_vol_subtrahend_voice', None)
    if sv is None:
        return None
    return MasterVolConfig(
        subtrahend_voice=sv,
        base=getattr(config, 'master_vol_base', 0xA0),
        trigger=getattr(config, 'master_vol_trigger', 'inst_change'),
        reset_on_loop=getattr(config, 'master_vol_reset_on_loop', False),
        underflow_clamp=getattr(config, 'master_vol_underflow_clamp', False),
    )


def _init_behavior_from_config(config) -> InitBehaviorConfig | None:
    """Derive an `InitBehaviorConfig` from the per-engine flat flags.
    Returns None when all defaults apply (most Hubbard engines).

    `no_first_attack_voice` translation: the legacy
    `suppress_first_notestart=True` always meant "voice 3" (engine's
    drum-priority gate suppresses V3's frame-0 note — see Devils Galop
    config comment). We encode that explicitly.
    """
    silence_all = getattr(config, 'first_frame_gate_off', False)
    suppress = getattr(config, 'suppress_first_notestart', False)
    mvol = getattr(config, 'master_vol_every_frame', 0)
    mvol_note = getattr(config, 'master_vol_every_note', 0)
    if not silence_all and not suppress and not mvol and not mvol_note:
        return None
    return InitBehaviorConfig(
        silence_all_voices_on_frame_0=silence_all,
        no_first_attack_voice=(3 if suppress else 0),
        master_vol_every_frame=mvol,
        master_vol_every_note=mvol_note,
    )


def _song_end_from_config(config) -> SongEndConfig | None:
    """Derive a `SongEndConfig` from the per-engine flat flags. Returns
    None when all defaults apply (composer's defaults match)."""
    freeze = getattr(config, 'freeze_on_stop', False)
    fill = getattr(config, 'stop_fill', None)
    loop_silence = getattr(config, 'loop_silences_song', False)
    if not freeze and fill is None and not loop_silence:
        return None
    cfg = SongEndConfig()
    if fill is not None:
        cfg.stop_marker = 'fill'
        cfg.fill_value = fill
    elif freeze:
        cfg.stop_marker = 'freeze'
    if loop_silence:
        cfg.loop_marker = 'silence_all'
    return cfg

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

def _simulate_sfx_sweep_reads(sfx, freq_bytes: bytes,
                              implicit_defaults: dict) -> dict:
    """Replay the SFX sweep state machine; collect every freqtab read at
    offset ≥ 192 (the engine-state region beyond the 96-entry musical
    freq table). These bytes are the V1/V2 frequencies the SFX emits at
    extreme sweep positions; the principled USF carries them on the SFX
    that actually reads them.

    Matches `_HUBBARD_SFX_STEP_ASM` in `pipelines/composer.py`:
      - sfx_y = (index*2) & $FF
      - V1 reads freqtab[sfx_y], freqtab[sfx_y+1] unless skip_v1/skip_both
      - V2 reads freqtab[(sfx_y - v2_offset) & $FF], freqtab[...+1]
      - direction=up: index += 1; down: index -= 1
      - terminates when index == end_index (8-bit equality)

    `implicit_defaults` maps offset → the byte the composer would place
    there from init.voice slots (or 0 elsewhere). Entries equal to the
    implicit default are dropped — the composer recovers them without
    USF help.
    """
    overlay: dict[int, int] = {}
    index = sfx.start_index & 0xFF
    end = sfx.end_index & 0xFF
    step = 1 if sfx.direction == 'up' else -1
    for _ in range(257):
        if index == end:
            break
        sfx_y = (index * 2) & 0xFF
        if not sfx.skip_both:
            # 6502 indexed reads use 16-bit address arithmetic for the
            # `base+1, Y` form — `lda freqtab+1,y` with Y=$FF reads
            # freqtab[256], not freqtab[0]. So the +1 read offsets are
            # plain `y + 1`, not `(y + 1) & $FF`.
            if not sfx.skip_v1:
                for off in (sfx_y, sfx_y + 1):
                    if 192 <= off < len(freq_bytes):
                        overlay[off] = freq_bytes[off]
            v2_y = (sfx_y - sfx.v2_byte_offset) & 0xFF
            for off in (v2_y, v2_y + 1):
                if 192 <= off < len(freq_bytes):
                    overlay[off] = freq_bytes[off]
        index = (index + step) & 0xFF
    # Drop entries equal to the implicit default — those bytes are
    # already supplied by init.voice overlay (or by the zero-pad).
    return {off: val for off, val in overlay.items()
            if val != implicit_defaults.get(off, 0)}


def _convert_sfx(sfx, sfx_id: int, freq_bytes: bytes,
                 implicit_defaults: dict) -> SfxSubtune:
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
        extended_freq=_simulate_sfx_sweep_reads(
            sfx, freq_bytes, implicit_defaults),
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

    # Pull engine_constants up front — we need freq_bytes to (1) populate
    # init.voice from named state-region slots and (2) simulate each
    # SFX's sweep to capture extended_freq overlays.
    ec = ENGINE_CONSTANTS.get(config.name)
    state_layout = None
    freq_bytes_normalised: bytes | None = None
    if ec is not None:
        freq_bytes_normalised = _normalize_freq_table(
            ec.freq_bytes, ec.seed_offsets)
        state_layout = _state_layout_dict(ec.state_layout)

    # Init.voice — populate from the six named state-region offsets
    # (canonical positions after _normalize_freq_table). Composer
    # overlays these onto its synthesized freq-table block.
    if freq_bytes_normalised is not None:
        init_voices = []
        for i in range(3):
            init_voices.append(InitVoice(
                id=i + 1,
                dur_field=freq_bytes_normalised[205 + i],
                ctrl=freq_bytes_normalised[208 + i],
                instr=InstrumentRef(
                    id=(freq_bytes_normalised[214 + i] & 0xFF) + 1),
                pwm_period=freq_bytes_normalised[229 + i],
                pwm_dir=('up' if freq_bytes_normalised[232 + i] == 0
                         else 'down'),
                slide_v=freq_bytes_normalised[239 + i],
            ))
        init = InitState(voices=init_voices)
    else:
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
        sfx_freq = (bytes(freq_bytes_normalised) if freq_bytes_normalised
                    is not None else b'\x00' * 320)
        # implicit_defaults: the bytes the composer will already place
        # via init.voice overlay (everything else is 0 from zero-pad).
        # SFX entries equal to these defaults are dropped — no need to
        # carry them in USF, the composer already produces them.
        implicit_defaults: dict[int, int] = {}
        for v in init.voices:
            i = v.id - 1
            implicit_defaults[205 + i] = v.dur_field
            implicit_defaults[208 + i] = v.ctrl
            if v.instr is not None:
                implicit_defaults[214 + i] = (v.instr.id - 1) & 0xFF
            implicit_defaults[229 + i] = v.pwm_period
            implicit_defaults[232 + i] = 0 if v.pwm_dir == 'up' else 0xFF
            implicit_defaults[239 + i] = v.slide_v
        for offset, sfx in enumerate(sfx_list):
            sfx_id = len(config.subtunes) + offset
            sfx_subtunes.append(_convert_sfx(
                sfx, sfx_id, sfx_freq, implicit_defaults))

    subtunes = music_subtunes + sfx_subtunes + list(extra_subtunes or [])

    # USF freq_table: just the 192-byte musical PAL prefix. The
    # state-region tail (offsets 192..319) is now decomposed into
    # init.voice slots (named musical content) + per-SFX extended_freq
    # overlays (the SFX-sweep musical content) + dropped engine
    # mechanism / dead bytes. See `docs/usf_representation_principle.md`
    # — bytes that aren't read by the rebuild aren't music, so they
    # leave USF.
    freq_table = None
    if freq_bytes_normalised is not None:
        freq_table = list(freq_bytes_normalised[:192])
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
        song_end=_song_end_from_config(config),
        init_behavior=_init_behavior_from_config(config),
        master_vol=_master_vol_from_config(config),
        sfx=_sfx_from_config(config),
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
