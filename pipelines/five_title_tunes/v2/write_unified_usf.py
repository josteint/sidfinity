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
from pipelines.five_title_tunes.v2.unified_inputs import build_unified_inputs
from src.usf2 import (
    UsfFile, Params, InitState, InitVoice, InstrumentRef, write_file,
    validate,
)


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
PARENT_SID = os.path.join(
    ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
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
    """Build a UsfFile mirroring `build_unified_inputs()`."""
    inputs = build_unified_inputs()
    instr_count = len(inputs.models)

    # PSID metadata from the parent SID.
    psid = _read_psid_meta(PARENT_SID)

    # Engine-level params — the values shared across all subtunes.
    # Per-subtune overrides go on each MusicSubtune.params.
    params = Params(fields={
        'arp_interval': inputs.arp_interval,
        'arp_period': inputs.arp_period,
        'vib_onset': 8,
        'linear_pw_or': inputs.linear_pw_or,
        'incby2_step': inputs.incby2_step,           # scalar fallback
        'incby2_onset': inputs.incby2_onset,
        'speed_ctr_init': inputs.speed_ctr_init,
        # Bookkeeping fields the codegen reads from the USF; values
        # are placeholders for the unified build (it uses the absolute
        # instrument table emitted from `inputs.models`, no instr_base
        # lookup needed). Kept for schema completeness.
        'instr_base': 0x1000,
        'instr_count': instr_count,
        'freq_table_base': 0x1000,
    })

    # Engine-level init — placeholder (sub_0's values). The codegen's
    # unified path uses each subtune's own init block instead.
    init = _init_state_from_ovseed(inputs.per_subtune_ovseed[0], instr_count)

    instruments = [_convert_instrument(m, inputs.arp_period)
                   for m in inputs.models]

    # 5 music subtunes.
    music_subtunes = []
    for st_idx, score in enumerate(inputs.scores):
        ms = _convert_score(st_idx, score)
        ms.params = Params(fields={
            'speed_ctr_init': inputs.per_subtune_speed_ctr_init[st_idx],
            'incby2_step': inputs.per_subtune_incby2_step[st_idx] & 0xFF,
            'incby2_late_gate': inputs.per_subtune_incby2_late_gate[st_idx],
            'tick_divider': inputs.resetspds[st_idx],
            'voice_start': inputs.voice_starts[st_idx],
        })
        ms.init = _init_state_from_ovseed(
            inputs.per_subtune_ovseed[st_idx], instr_count)
        music_subtunes.append(ms)

    return UsfFile(
        version=2,
        engine='five_title_tunes',
        psid=psid,
        params=params,
        init=init,
        instruments=instruments,
        subtunes=music_subtunes,
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
    out_dir = sys.argv[1] if len(sys.argv) > 1 else 'demo/hubbard'
    p = write_unified_usf(out_dir)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
