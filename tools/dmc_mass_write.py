#!/usr/bin/env python3
"""Mass-write DMC FULL members alongside the HVSC originals.

Reads tmp/dmc_wide_results.jsonl and, for every member with status 'full'
WHOSE VERDICT WAS EARNED BY THE CURRENT CODE (code_hash match), writes its
.usf + .sidfinity.sid. Rows whose code_hash is stale/absent are SKIPPED (with a
warning) — writing them would re-create the on-disk .usf palimpsest this whole
scheme exists to prevent. Re-run tools/dmc_family_batch.py to refresh them.

Usage:
    PYTHONPATH=tools/py65_lib:tools:src python3 tools/dmc_mass_write.py
"""
from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.jobs import default_jobs  # noqa: E402

RESULTS = os.path.join(ROOT, 'tmp', 'dmc_wide_results.jsonl')


def write_member(item) -> tuple:
    rel, hold_gateoff = item if isinstance(item, (list, tuple)) else (item, None)
    try:
        from pipelines.dmc.v4.factory import dmc_v4_config, dmc_v4_config_2sid
        from pipelines.dmc.v4.extract.to_usf import (write_dmc_usf,
                                                     write_dmc_2sid_usf,
                                                     write_dmc_compilation_usf)
        from pipelines.dmc.v4.compilation import detect_compilation
        from pipelines.dmc.composer_asm import build_dmc_sid
        from src.usf.parser import parse_file
        hvsc = os.path.join(ROOT, 'hvsc84')
        out_dir = os.path.dirname(os.path.join(hvsc, rel))
        # SAME build dispatch the batch verified with (multi-SID -> compilation
        # -> single player). Writing every member through the single-player
        # constructor would store an artifact that is NOT what earned the FULL
        # verdict — the C20 palimpsest, in the one tool whose whole job is to
        # avoid it. (It did exactly that for the multi-SID members until
        # 2026-07-21: Dark_Knight_2SID.usf on disk was a 3-voice single-chip
        # extraction of a 6-voice tune.)
        cfgs2 = dmc_v4_config_2sid(rel, hvsc_root=hvsc)
        comp = (None if cfgs2 is not None
                else detect_compilation(rel, hvsc_root=hvsc))
        if cfgs2 is not None:
            usf_path = write_dmc_2sid_usf(cfgs2, out_dir, hvsc_root=hvsc)
        elif comp is not None:
            try:
                usf_path = write_dmc_compilation_usf(rel, comp, out_dir,
                                                     hvsc_root=hvsc)
            except Exception:      # unmergeable -> the batch's same fallback
                usf_path = write_dmc_usf(dmc_v4_config(rel, hvsc_root=hvsc),
                                         out_dir, hvsc_root=hvsc)
        else:
            usf_path = write_dmc_usf(dmc_v4_config(rel, hvsc_root=hvsc),
                                     out_dir, hvsc_root=hvsc)
        usf = parse_file(usf_path)
        # the batch's write-stream retry may have chosen mask_only (a member
        # whose original never clears AD+SR) — apply it so the written SID
        # matches the verified verdict.
        if hold_gateoff:
            usf.params.fields['hold_gateoff'] = hold_gateoff
        sid = build_dmc_sid(usf)
        base = os.path.splitext(os.path.join(hvsc, rel))[0]
        open(base + '.sidfinity.sid', 'wb').write(sid)
        return (rel, True, '')
    except Exception as e:
        return (rel, False, f'{type(e).__name__}: {e}'[:120])


def main():
    results = RESULTS
    if '--results' in sys.argv:
        results = sys.argv[sys.argv.index('--results') + 1]
    from src.code_fingerprint import code_fingerprint
    code_hash = code_fingerprint('dmc_v4')
    full, stale = [], 0
    for l in open(results):
        if not l.strip():
            continue
        d = json.loads(l)
        if d.get('status') != 'full':
            continue
        if d.get('code_hash') != code_hash:
            stale += 1                 # verdict predates current code — DON'T write
            continue
        full.append((d['path'], d.get('hold_gateoff')))
    print(f'{len(full)} current-code FULL members to write', flush=True)
    if stale:
        print(f'  WARNING: skipped {stale} FULL rows with stale/absent code_hash '
              f'(verdict predates current code). Re-run tools/dmc_family_batch.py '
              f'to refresh them before mass-write.', flush=True)
    ok = err = 0
    errs = []
    with Pool(default_jobs(cap=len(full))) as pool:
        for i, (rel, good, msg) in enumerate(
                pool.imap_unordered(write_member, full, chunksize=8)):
            if good:
                ok += 1
            else:
                err += 1
                errs.append((rel, msg))
            if (i + 1) % 250 == 0:
                print(f'  {i+1}/{len(full)}  ok={ok} err={err}', flush=True)
    print(f'DONE  ok={ok}  err={err}', flush=True)
    for rel, msg in errs[:20]:
        print(f'  ERR {rel}: {msg}')


if __name__ == '__main__':
    main()
