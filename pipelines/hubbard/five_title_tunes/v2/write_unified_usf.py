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

from pipelines.hubbard.to_usf_v2 import (
    _convert_instrument, _convert_score, _read_psid_meta,
)
from pipelines.hubbard.five_title_tunes.v2.unified_inputs import build_unified_inputs
from src.usf2 import (
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
    from pipelines.hubbard.engine_constants import (
        ENGINE_CONSTANTS, EngineConstants,
    )
    from dataclasses import fields as dataclass_fields
    from src.usf2.types import Params as ParamsCls

    inputs = build_unified_inputs()
    instr_count = len(inputs.models)
    ec = ENGINE_CONSTANTS['five_title_tunes']

    psid = _read_psid_meta(PARENT_SID)

    # Top-level params — engine_constants deltas (Commando-default
    # diffs only). Per-subtune mechanism overrides live on each
    # MusicSubtune.params.
    defaults = EngineConstants(instr_base=0, instr_count=0,
                               freq_table_base=0, freq_bytes=bytes(320))
    SKIP = {'instr_base', 'instr_count', 'freq_table_base', 'freq_bytes',
            'voice_starts', 'state_layout', 'seed_offsets', 'digi',
            'is_rsid', 'subtune_overrides'}
    top_fields: dict = {}
    for f in dataclass_fields(EngineConstants):
        if f.name in SKIP: continue
        v_ec = getattr(ec, f.name); v_def = getattr(defaults, f.name)
        if v_ec != v_def and v_ec is not None:
            top_fields[f.name] = v_ec
    params = Params(fields=top_fields)

    # Engine-level init stays as a placeholder for per-subtune init
    # state — the codegen's per-subtune-table path uses each sub's
    # init explicitly.
    init = _init_state_from_ovseed(inputs.per_subtune_ovseed[0], instr_count)

    instruments = [_convert_instrument(m, inputs.arp_period)
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
        version=3,
        engine='five_title_tunes',
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
