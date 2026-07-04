#!/usr/bin/env python3
"""Mass-write DMC V5 (family-3/5) FULL members alongside the HVSC originals.

Reads tmp/dmc_v5_full_results.jsonl and, for every member with status 'full'
whose code_hash matches the current code (stale rows skipped + warned), writes
its .usf + .sidfinity.sid via the real SID -> USF -> SID pipeline.

Usage:
    PYTHONPATH=tools/py65_lib:tools:src python3 tools/dmc_v5_mass_write.py \
        [--results FILE.jsonl]
"""
from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

RESULTS = os.path.join(ROOT, 'tmp', 'dmc_v5_full_results.jsonl')


def write_member(rel: str) -> tuple:
    try:
        from pipelines.dmc.v5.factory import dmc_v5_config
        from pipelines.dmc.v5.extract.to_usf import write_v5_usf
        from pipelines.dmc.v5.from_usf import usf_to_model
        from pipelines.dmc.v5.composer_v5 import build_v5_sid
        from src.usf.parser import parse_file
        hvsc = os.path.join(ROOT, 'hvsc84')
        cfg = dmc_v5_config(rel, hvsc_root=hvsc)
        out_dir = os.path.dirname(os.path.join(hvsc, rel))
        usf_path = write_v5_usf(cfg, out_dir, hvsc_root=hvsc)
        sid = build_v5_sid(usf_to_model(parse_file(usf_path)))
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
    code_hash = code_fingerprint('dmc_v5')
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
        full.append(d['path'])
    print(f'{len(full)} current-code FULL members to write', flush=True)
    if stale:
        print(f'  WARNING: skipped {stale} FULL rows with stale/absent code_hash. '
              f'Re-run tools/dmc_v5_family_batch.py to refresh before mass-write.',
              flush=True)
    ok = err = 0
    errs = []
    with Pool(8) as pool:
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
    print('\nNow refresh the DB: python3 tools/build_sid_db.py', flush=True)


if __name__ == '__main__':
    main()
