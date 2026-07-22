#!/usr/bin/env python3
"""Fast crash smoke-test for the DMC build pipeline.

Builds a small, DELIBERATELY DIVERSE set of DMC members through the full
config -> USF -> compose path (NO verify) and reports OK / CRASH per member.
Its ONLY job is to catch exceptions (a probe that assumes a field, a shape
mismatch, a None operand) in seconds, BEFORE the ~10-minute regression — so a
factory/composer change never dies mid-run and forces a second full pass.

The default set spans the config/compose variants that a family-1 change can
crash on even though it targets a canonical member:
  - canonical family-1        (the common path)
  - family-2                  (gatemask_addr / other fields are None here)
  - page-3 relocated family-1 (state block moved off $17xx)
  - out-of-image loop sector  (ledger C29 low-RAM overlay path)
  - 2SID                      (the dmc_v4_config_2sid path)

It is fix-AGNOSTIC: it exercises the pipeline, not any particular fix.

Usage:
    python3 tools/dmc_smoke.py                 # default diverse set
    python3 tools/dmc_smoke.py PATH [PATH...]  # custom members (HVSC-relative)
Exit code is nonzero if ANY member crashed.
"""
from __future__ import annotations

import os
import sys
import tempfile
import traceback

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

# (tag, hvsc-relative path, mode). mode 'build' = full config->USF->compose;
# 'config2sid' = the per-chip config only (dmc_v4_config_2sid, which runs the
# per-chip probe path = the crash class) — used for the 2SID slot because every
# 2SID member in HVSC is multi-subtune, an unrelated 'unsupported' the full
# merge rejects; config-only still exercises the code a family-1 change touches.
DEFAULT_MEMBERS = [
    ('canonical-f1',  'MUSICIANS/B/Bax/Music_for_Game.sid', 'build'),
    ('family-2',      'MUSICIANS/A/Albartus_Jan/Lameness.sid', 'build'),
    ('page3-reloc',   'MUSICIANS/B/Bakewell_Dwayne/Journey.sid', 'build'),
    ('oob-C29',       'MUSICIANS/P/PVCF/Worktunes/Centric_tune_4_version_8.sid', 'build'),
    ('2SID-config',   'MUSICIANS/R/Rayden/Bamse_Bert_2SID.sid', 'config2sid'),
    # heterogeneous compilation: DMC players + a dmc_sfx sub-player (C31)
    ('hetero-sfx',    'MUSICIANS/B/Bayliss_Richard/Canyon_Tank_Duel.sid', 'build'),
]


def _build_one(rel: str, mode: str = 'build') -> str:
    """Exercise rel through the DMC pipeline; return an info tag. Raises on any
    pipeline exception (that is what we are testing for)."""
    if mode == 'config2sid':
        from pipelines.dmc.v4.factory import dmc_v4_config_2sid
        cfgs = dmc_v4_config_2sid(rel, hvsc_root=os.path.join(ROOT, 'hvsc84'))
        return f'config ok ({len(cfgs) if cfgs else 0} chip(s))'
    from tools.dmc_build_one import build
    td = tempfile.mkdtemp()
    out_sid = os.path.join(td, 'smoke.sid')
    nch, _, path = build(rel, out_sid, None)
    # the build PATH is part of what this smoke test pins: a member that
    # silently falls off its dispatch branch is a defect the chip count hides.
    return f'{nch} chip(s)  [{path}]'


def main() -> int:
    args = sys.argv[1:]
    members = ([('cli', a, 'build') for a in args] if args else DEFAULT_MEMBERS)
    width = max(len(t) for t, *_ in members)
    fails = 0
    for tag, rel, mode in members:
        try:
            info = _build_one(rel, mode)
            print(f'  ok    {tag:<{width}}  {rel}  ({info})')
        except Exception as e:                              # noqa: BLE001
            fails += 1
            print(f'  CRASH {tag:<{width}}  {rel}')
            print(f'        {type(e).__name__}: {e}')
            tb = traceback.format_exc().strip().splitlines()
            for line in tb[-3:]:
                print(f'        {line}')
    print(f'\n{len(members) - fails}/{len(members)} built; {fails} crashed')
    return 1 if fails else 0


if __name__ == '__main__':
    raise SystemExit(main())
