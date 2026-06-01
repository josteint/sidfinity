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
    ROOT, 'hvsc84', 'MUSICIANS', 'H',
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

    # Top-level params — the compound engine's tune-level mechanism.
    # Read from `inputs` (the unified _Inputs already carries the
    # right values for the 5-sub compound). Plus vib_onset, which is
    # baked into each instrument's model in `inputs.models` but also
    # needed at top level so the build-side `vib_onset = get(...)`
    # applies it uniformly. All 5 subs have vib_onset=8.
    top_fields: dict = {
        'arp_interval': inputs.arp_interval,
        'arp_period': inputs.arp_period,
        'linear_pw_or': inputs.linear_pw_or,
        'incby2_step': inputs.incby2_step,
        'incby2_onset': inputs.incby2_onset,
        'speed_ctr_init': inputs.speed_ctr_init,
        'vib_onset': 8,
    }
    # Drop any that match Commando-flavor defaults so the USF stays
    # minimal and the round-trip through build_from_usf reads
    # cleanly.
    DEFAULTS = {'arp_interval': 12, 'arp_period': 2, 'linear_pw_or': 0,
                'incby2_step': 2, 'incby2_onset': 3,
                'speed_ctr_init': 0, 'vib_onset': 6}
    top_fields = {k: v for k, v in top_fields.items()
                  if v != DEFAULTS.get(k)}
    params = Params(fields=top_fields)

    # Engine-level init stays as a placeholder for per-subtune init
    # state — the codegen's per-subtune-table path uses each sub's
    # init explicitly.
    init = _init_state_from_ovseed(inputs.per_subtune_ovseed[0], instr_count)

    # _convert_instrument reads tune-level fields via getattr; pass
    # inputs directly. The fields it consults: arp_period, arp_interval,
    # arp_phase_invert (defaults to False), vib_onset (defaults to 6 —
    # 5TT's top_fields explicitly carries vib_onset=8, but the per-
    # instrument value goes into the .usf via the inputs.vib_onset
    # attribute when present, falling back to default otherwise).
    instruments = [_convert_instrument(m, inputs)
                   for m in inputs.models]

    music_subtunes = []
    for st_idx, score in enumerate(inputs.scores):
        ms = _convert_score(st_idx, score)
        ms.init = _init_state_from_ovseed(
            inputs.per_subtune_ovseed[st_idx], instr_count)
        # Per-subtune mechanism — pulled from ec.subtune_overrides into
        # each sub's params block. None values are dropped (= absent).
        ov = ec.subtune_overrides.get(st_idx, {})
        sub_fields = {k: v for k, v in ov.items() if v is not None}
        if sub_fields:
            ms.params = ParamsCls(fields=sub_fields)
        music_subtunes.append(ms)

    return UsfFile(
        psid=psid,
        params=params,
        init=init,
        instruments=instruments,
        subtunes=music_subtunes,
        freq_table=list(ec.freq_bytes),
        state_layout=None,
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
    out_dir = sys.argv[1] if len(sys.argv) > 1 else 'hvsc84/MUSICIANS/H/Hubbard_Rob'
    p = write_unified_usf(out_dir)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
