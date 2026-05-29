"""USF v3 → SID build path.

USF v3 is the engine-name-blind, self-contained version. A v3 USF
declares `version: 3` and carries:

  - `freq_table { ... }` — the per-tune 320-byte freq region
  - `params { ... }` — named tune-level mechanism overrides (only
    fields that deviate from the Commando-flavor defaults)
  - Per-instrument effect fields, per-voice patterns, SFX records —
    all already principled at v2.

This build path reads ONLY from the USF — no `ENGINE_CONSTANTS[name]`
lookup. The `engine:` token is metadata; the build never consumes it.

Proves the universal target: the USF representation is rich enough
to host every detail a build needs. As more engines are migrated,
each becomes a v3 USF + tune-specific param overrides — no new
codegen path, no new engine constants entry.

Verified on Commando (19/19 subtunes byte-exact via verify_all).
The existing v2 dispatched-build path (`build_from_usf.py`) stays
alongside until all engines are migrated to v3.
"""

from __future__ import annotations

import os
import struct

from src.usf2 import (
    UsfFile, MusicSubtune, SfxSubtune, DigiSubtune, parse_file, validate,
)
from pipelines.hubbard.codegen import _emit_sid, LOAD
from pipelines.hubbard.build_from_usf import (
    _model_from_usf_instrument,
    _score_from_subtune,
    _soundeffect_from_usf,
    _ovseed_from_init_state,
    _emit_combined_sid,
)
from pipelines.hubbard.codegen import _Inputs


# Registered digi players — named handles for the few distinct digi
# techniques in the SID corpus. Each entry maps a tune-level
# `digi_player: <name>` to its DigiCode (which describes where the
# dispatcher + player live in the rebuild's address space). The bytes
# of the player asm itself live in engine_constants.py — they're
# engine-side code, not USF data, so they don't belong inline in the
# .usf file. Adding a new digi technique = registering one entry.
def _digi_player_registry():
    from pipelines.hubbard.engine_constants import CHIMERA_DIGI
    return {
        'chimera_1bit': CHIMERA_DIGI,
    }


def _inputs_from_usf3(usf: UsfFile) -> _Inputs:
    """Build codegen `_Inputs` from a v3 USF — no engine lookup."""
    if usf.version != 3:
        raise ValueError(
            f'usf3 build expects version 3, got {usf.version}')
    if usf.freq_table is None:
        raise ValueError(
            'usf3 build requires a freq_table block in the USF')
    if len(usf.freq_table) != 320:
        raise ValueError(
            f'expected 320-byte freq_table, got {len(usf.freq_table)}')

    # Tune-level params with Commando-flavor defaults. Engines that
    # diverge from these set the field in the USF's params block.
    p = usf.params.fields if usf.params else {}

    def get(key, default):
        return p.get(key, default)

    def latin1(s: str) -> bytes:
        return s.encode('latin-1', errors='replace')

    # Per-instrument effect onset stays on each instrument (the
    # InstrumentModel carries vibrato.onset implicitly via vib_onset
    # at model-build time). Default Commando vibrato onset = 6.
    vib_onset = get('vib_onset', 6)

    models = [_model_from_usf_instrument(u, vib_onset)
              for u in usf.instruments]

    # Music subtunes
    music_subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    music_subs.sort(key=lambda s: s.id)
    subtune_ids = tuple(s.id for s in music_subs)
    scores = [_score_from_subtune(s) for s in music_subs]
    resetspds = [s.tempo - 1 for s in music_subs]
    # Per-subtune voice_start: when an Action-Biker-style subtune
    # skips a voice, the subtune's own `params { voice_start: N }`
    # carries the override. Default 2 = V3 starts the play loop.
    voice_starts = []
    for s in music_subs:
        sp = s.params.fields if s.params else {}
        voice_starts.append(sp.get('voice_start', 2))

    # Per-subtune mechanism mode: 5_Title_Tunes-style compound engines
    # carry per-subtune deltas on each MusicSubtune.params + per-sub
    # init state on each MusicSubtune.init. Only the keys below trigger
    # the codegen's per-subtune-table mode; per-subtune `voice_start`
    # alone is read independently and doesn't flip the mode.
    _PER_SUBTUNE_MECHANISM = {
        'speed_ctr_init', 'incby2_step', 'incby2_late_gate', 'tick_divider',
    }
    has_per_subtune = any(
        s.init is not None or
        (s.params is not None and
         _PER_SUBTUNE_MECHANISM & s.params.fields.keys())
        for s in music_subs)
    per_subtune_speed_ctr_init = None
    per_subtune_incby2_step = None
    per_subtune_incby2_late_gate = None
    per_subtune_ovseed = None
    if has_per_subtune:
        per_subtune_speed_ctr_init = []
        per_subtune_incby2_step = []
        per_subtune_incby2_late_gate = []
        per_subtune_ovseed = []
        # Engine-level defaults to fall back on per subtune.
        top_speed_ctr_init = get('speed_ctr_init', 0)
        top_incby2_step = get('incby2_step', 2)
        top_incby2_late_gate = get('incby2_late_gate', None)
        for i, s in enumerate(music_subs):
            sp = s.params.fields if s.params is not None else {}
            per_subtune_speed_ctr_init.append(
                sp.get('speed_ctr_init', top_speed_ctr_init))
            per_subtune_incby2_step.append(
                sp.get('incby2_step', top_incby2_step) & 0xFF)
            late_gate = sp.get('incby2_late_gate', top_incby2_late_gate)
            per_subtune_incby2_late_gate.append(
                (0xFF if late_gate is None else late_gate) & 0xFF)
            per_subtune_ovseed.append(
                _ovseed_from_init_state(s.init, len(usf.instruments)))
            if 'tick_divider' in sp:
                resetspds[i] = sp['tick_divider']

    # SFX subtunes
    sfx_subs = sorted(
        (s for s in usf.subtunes if isinstance(s, SfxSubtune)),
        key=lambda s: s.id)
    sfx_list = [_soundeffect_from_usf(s, idx)
                for idx, s in enumerate(sfx_subs)]

    # Freq bytes come from USF, with per-voice init overlay (if the
    # USF still carries an init block — when empty, the freq_table
    # bytes are used verbatim).
    fb = bytearray(usf.freq_table)
    for v in usf.init.voices:
        i = v.id - 1
        fb[205 + i] = v.dur_field
        fb[208 + i] = v.ctrl
        if v.instr is not None:
            fb[214 + i] = (v.instr.id - 1) & 0xFF
        fb[229 + i] = v.pwm_period
        fb[232 + i] = 0x00 if v.pwm_dir == 'up' else 0xFF
        fb[239 + i] = v.slide_v
    freq_bytes = bytes(fb)

    # Optional state_layout for engines whose off-table-arp scratch
    # region has a non-Commando shape (Human Race).
    state_layout = None
    if usf.state_layout is not None:
        from pipelines.hubbard.codegen import StatebufLayout, StatebufSlot
        d = usf.state_layout
        scalars = [StatebufSlot(offset=s['offset'], kind=s['kind'],
                                value=s.get('value', 0),
                                var=s.get('var', ''))
                   for s in d['scalars']]
        per_voice = [StatebufSlot(offset=s['offset'], kind=s['kind'],
                                  value=s.get('value', 0),
                                  var=s.get('var', ''))
                     for s in d['per_voice']]
        state_layout = StatebufLayout(
            n_voices=d['n_voices'], scalars=scalars, per_voice=per_voice)

    # Tune-level mechanism flags (Commando defaults).
    ns_offtab_decr_offset = get('ns_offtab_decr_offset', None)
    return _Inputs(
        title=latin1(usf.psid.title),
        author=latin1(usf.psid.author),
        released=latin1(usf.psid.released),
        start_song=usf.psid.start_song,
        arp_interval=get('arp_interval', 12),
        arp_period=get('arp_period', 2),
        arp_phase_invert=get('arp_phase_invert', False),
        linear_pw_or=get('linear_pw_or', 0),
        incby2_step=get('incby2_step', 2),
        incby2_every_frame=get('incby2_every_frame', False),
        incby2_onset=get('incby2_onset', 3),
        suppress_first_notestart=get('suppress_first_notestart', False),
        freeze_on_stop=get('freeze_on_stop', False),
        speed_ctr_init=get('speed_ctr_init', 0),
        first_frame_gate_off=get('first_frame_gate_off', False),
        seed_overlap=get('seed_overlap', True),
        psid_speed=usf.psid.speed,
        frame_ctr_init=get('frame_ctr_init', 0xFF),
        incby2_late_gate=get('incby2_late_gate', None),
        stop_fill=get('stop_fill', None),
        sfx_framectr_ofs=get('sfx_framectr_ofs', 253),
        sfx_state_ofs=get('sfx_state_ofs', None),
        has_sfx=get('has_sfx', False),
        subtunes=subtune_ids,
        models=models, scores=scores, resetspds=resetspds,
        voice_starts=voice_starts, freq_bytes=freq_bytes,
        sfx_list=sfx_list,
        per_subtune_speed_ctr_init=per_subtune_speed_ctr_init,
        per_subtune_incby2_step=per_subtune_incby2_step,
        per_subtune_incby2_late_gate=per_subtune_incby2_late_gate,
        per_subtune_ovseed=per_subtune_ovseed,
        master_vol_subtrahend_voice=get('master_vol_subtrahend_voice', None),
        master_vol_base=get('master_vol_base', 0xA0),
        master_vol_trigger=get('master_vol_trigger', 'inst_change'),
        tie_preserves_slide=get('tie_preserves_slide', False),
        hubidx_wrap_at_patend=get('hubidx_wrap_at_patend', True),
        **({'ns_offtab_decr_offset': ns_offtab_decr_offset}
           if ns_offtab_decr_offset is not None else {}),
        **({'state_layout': state_layout} if state_layout is not None else {}),
    )


def build_from_usf3(usf_path: str, out_path: str, codec=None) -> str:
    """Read a v3 USF, produce a SID with no engine-name dispatch.

    Music-only USFs build directly. Tunes with digi subtunes also
    specify `digi_player: <name>` in `params` — the build looks up
    the named player from the small in-process registry.
    """
    from pipelines.hubbard.note_codec import BitPackCodec
    if codec is None:
        codec = BitPackCodec()
    usf = parse_file(usf_path)
    usf_dir = os.path.dirname(os.path.abspath(usf_path))
    validate(usf, usf_dir=usf_dir)
    inputs = _inputs_from_usf3(usf)

    digi_subs = sorted(
        (s for s in usf.subtunes if isinstance(s, DigiSubtune)),
        key=lambda s: s.id)
    if not digi_subs:
        return _emit_sid(inputs, out_path, codec)

    # Combined music + digi
    name = usf.params.fields.get('digi_player') if usf.params else None
    if name is None:
        raise ValueError(
            f'USF has digi subtunes but no `digi_player` in params')
    registry = _digi_player_registry()
    if name not in registry:
        raise ValueError(
            f'unknown digi_player {name!r}; '
            f'register in `_digi_player_registry`')
    return _emit_combined_sid(inputs, usf, digi_subs, registry[name],
                              out_path, usf_dir, codec)
