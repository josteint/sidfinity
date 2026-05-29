"""USF → SID build path WITHOUT engine-name dispatch.

Proof of concept: a single codegen path that produces a byte-exact
rebuild (instruction-stream-per-frame contract) reading ONLY from the
USF. No `ENGINE_CONSTANTS[usf.engine]` lookup; the engine name is
ignored. Per-tune freq table comes from `usf.freq_table` (the new
optional grammar block); per-tune mechanism flags come from
`usf.params.fields` with Commando-flavor defaults; instrument quirks
come from the per-instrument fields already in USF.

Started for Commando — establishes whether the USF representation is
rich enough to be self-contained. If this rebuilds Commando byte-
exact, we know we can extend the same path to other engines whose
USFs we'd also enrich with `freq_table` + flags.

This sits ALONGSIDE the existing engine-name-dispatch build path
(`build_from_usf.py`) — that one is unchanged. Other engines that
haven't been re-extracted with the universal extras keep using the
old path.
"""

from __future__ import annotations

import os
import struct

from src.usf2 import UsfFile, MusicSubtune, SfxSubtune, parse_file, validate
from pipelines.hubbard.codegen import _emit_sid, LOAD
from pipelines.hubbard.build_from_usf import (
    _model_from_usf_instrument,
    _score_from_subtune,
    _soundeffect_from_usf,
)
from pipelines.hubbard.codegen import _Inputs


def _inputs_from_universal_usf(usf: UsfFile) -> _Inputs:
    """Build codegen `_Inputs` from USF alone — no engine lookup."""
    if usf.freq_table is None:
        raise ValueError(
            'universal_build requires a freq_table block in the USF')
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
    voice_starts_map = get('voice_starts', {})
    voice_starts = [voice_starts_map.get(s.id, 2) for s in music_subs]

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

    # Tune-level mechanism flags (Commando defaults).
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
        per_subtune_speed_ctr_init=None,
        per_subtune_incby2_step=None,
        per_subtune_incby2_late_gate=None,
        per_subtune_ovseed=None,
        master_vol_subtrahend_voice=get('master_vol_subtrahend_voice', None),
        master_vol_base=get('master_vol_base', 0xA0),
        master_vol_trigger=get('master_vol_trigger', 'inst_change'),
        tie_preserves_slide=get('tie_preserves_slide', False),
    )


def build_universal(usf_path: str, out_path: str, codec=None) -> str:
    """Read a USF that carries its own freq_table + flags, produce a
    SID with no engine-name dispatch.
    """
    from pipelines.hubbard.note_codec import BitPackCodec
    if codec is None:
        codec = BitPackCodec()
    usf = parse_file(usf_path)
    usf_dir = os.path.dirname(os.path.abspath(usf_path))
    validate(usf, usf_dir=usf_dir)
    inputs = _inputs_from_universal_usf(usf)
    return _emit_sid(inputs, out_path, codec)
