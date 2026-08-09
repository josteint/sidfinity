"""Emit the unified `5_Title_Tunes.usf` file.

Converts the in-memory unified `_Inputs` (5 subtunes, 56 absolute
instruments, per-subtune params + ovseed) into a USF v2 file with:

  - one engine block ('five_title_tunes')
  - one engine-level params block (the values shared across subs)
  - one engine-level init (placeholder using sub_0's ovseed)
  - 56 instruments (concatenated from the 5 subs, renumbered)
  - 5 music subtunes, each with its own `params { ... }` and
    `init { voice 1 ... voice 2 ... voice 3 ... }` blocks

The per-subtune init blocks carry the renumbered ovseed in the
existing `InitVoice` fields (ctrl / dur_field / pwm_period / pwm_dir
/ instr / slide_v), one block per subtune.
"""

from __future__ import annotations

import os
import struct

from pipelines.hubbard.to_usf import (
    _convert_instrument, _convert_score, _read_psid_meta,
)
from pipelines.hubbard.five_title_tunes.unified.unified_inputs import build_unified_inputs
from src.usf import (
    UsfFile, Params, InitState, InitVoice, InstrumentRef, write_file,
    validate,
)


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))
PARENT_SID = os.path.join(
    ROOT, 'hvsc85', 'MUSICIANS', 'H',
    'Hubbard_Rob', '5_Title_Tunes.sid')


def _init_state_from_ovseed(ov: bytes, instr_count: int) -> InitState:
    """Convert an 18-byte ovseed (v_ctrl[3], pwm_period[3], pwm_dir[3],
    v_instr[3], v_durfield[3], v_slide[3]) into an InitState."""
    assert len(ov) == 18
    voices = []
    for i in range(3):
        instr_byte = ov[9 + i]   # v_instr[i]
        instr_ref = None
        if 0 <= instr_byte < instr_count:
            instr_ref = InstrumentRef(id=instr_byte + 1)
        voices.append(InitVoice(
            id=i + 1,
            ctrl=ov[0 + i],
            pwm_period=ov[3 + i],
            pwm_dir='up' if ov[6 + i] == 0 else 'down',
            instr=instr_ref,
            dur_field=ov[12 + i],
            slide_v=ov[15 + i],
        ))
    return InitState(voices=voices)


def build_unified_usf() -> UsfFile:
    """Build a v3 UsfFile mirroring `build_unified_inputs()`."""
    from pipelines.hubbard.engine_constants import ENGINE_CONSTANTS
    from src.usf.types import Params as ParamsCls

    inputs = build_unified_inputs()
    instr_count = len(inputs.models)
    ec = ENGINE_CONSTANTS['five_title_tunes']

    psid = _read_psid_meta(PARENT_SID)

    # Phase 3b — tune-level musical fields (vib_onset, arp_*,
    # incby2_*) are now per-instrument. Composer reads them from any
    # instrument's per-inst slot. Only emit genuinely-per-tune fields
    # here: linear_pw_or + speed_ctr_init.
    # speed_ctr_init now rides the typed init block (file-level here).
    top_fields: dict = {
        'linear_pw_or': inputs.linear_pw_or,
    }
    DEFAULTS = {'linear_pw_or': 0}
    top_fields = {k: v for k, v in top_fields.items()
                  if v != DEFAULTS.get(k)}
    params = Params(fields=top_fields)

    # Engine-level init stays as a placeholder for per-subtune init
    # state — the codegen's per-subtune-table path uses each sub's
    # init explicitly.
    init = _init_state_from_ovseed(inputs.per_subtune_ovseed[0], instr_count)
    init.speed_ctr_init = inputs.speed_ctr_init

    # _convert_instrument reads tune-level fields via getattr from
    # config. `inputs` (the unified _Inputs) HAS arp_interval +
    # arp_period + incby2_* but LACKS `vib_onset` and
    # `arp_phase_invert`. Pass a shim that delegates to inputs and
    # supplies the missing fields with the engine's true values.
    class _5TTConfig:
        def __init__(self, base):
            self._base = base
        def __getattr__(self, name):
            missing = {'vib_onset': 8, 'arp_phase_invert': False}
            if name in missing:
                return missing[name]
            return getattr(self._base, name)
    cfg_shim = _5TTConfig(inputs)
    instruments = [_convert_instrument(m, cfg_shim)
                   for m in inputs.models]

    music_subtunes = []
    for st_idx, score in enumerate(inputs.scores):
        ms = _convert_score(st_idx, score)
        ms.init = _init_state_from_ovseed(
            inputs.per_subtune_ovseed[st_idx], instr_count)
        # Per-subtune mechanism — pulled from ec.subtune_overrides into
        # each sub's params block. None values are dropped (= absent).
        # speed_ctr_init now rides the typed per-subtune init block.
        ov = ec.subtune_overrides.get(st_idx, {})
        if ov.get('speed_ctr_init') is not None:
            ms.init.speed_ctr_init = ov['speed_ctr_init']
        sub_fields = {k: v for k, v in ov.items()
                      if v is not None and k != 'speed_ctr_init'}
        if sub_fields:
            ms.params = ParamsCls(fields=sub_fields)
        music_subtunes.append(ms)

    # song_end + init_behavior + master_vol blocks — derive from
    # inputs (5TT's _Inputs has same flat fields as EngineConfig).
    # None when all defaults apply.
    from pipelines.hubbard.to_usf import (
        _song_end_from_config, _init_behavior_from_config,
        _master_vol_from_config, _sfx_from_config,
    )
    song_end = _song_end_from_config(inputs)
    init_behavior = _init_behavior_from_config(inputs)
    master_vol = _master_vol_from_config(inputs)
    sfx = _sfx_from_config(inputs)

    return UsfFile(
        psid=psid,
        params=params,
        init=init,
        instruments=instruments,
        subtunes=music_subtunes,
        # New schema: 192-byte musical PAL only. The state-region bytes
        # 5TT's sub-engines need are carried as per-subtune init.voice
        # overlays (the per_subtune_ovseed mechanism, populated above).
        # No SFX, no extended_freq.
        freq_table=list(ec.freq_bytes[:192]),
        state_layout=None,
        song_end=song_end,
        init_behavior=init_behavior,
        master_vol=master_vol,
        sfx=sfx,
    )


def write_unified_usf(out_dir: str) -> str:
    """Write `5_Title_Tunes.usf` to `out_dir` and return its path."""
    usf = build_unified_usf()
    validate(usf)
    out_path = os.path.join(out_dir, '5_Title_Tunes.usf')
    write_file(usf, out_path)
    validate(usf, usf_dir=out_dir)
    return out_path


if __name__ == '__main__':
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else 'hvsc85/MUSICIANS/H/Hubbard_Rob'
    p = write_unified_usf(out_dir)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
