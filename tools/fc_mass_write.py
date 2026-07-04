#!/usr/bin/env python3
"""Mass-write FC-standard FULL members alongside the HVSC originals.

Reads tmp/fc_std_wide_results.jsonl and, for every member with status 'full'
whose code_hash matches the current code (stale rows skipped + warned), writes
its .usf + .sidfinity.sid via the real SID -> USF -> SID featuredriven pipeline.

Usage:
    PYTHONPATH=src:. python3 tools/fc_mass_write.py [--results FILE.jsonl]
"""
from __future__ import annotations

import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'src'), ROOT]

RESULTS = os.path.join(ROOT, 'tmp', 'fc_std_wide_results.jsonl')


def write_member(rel: str) -> tuple:
    try:
        from pipelines.future_composer.standard.config import fc_standard_config
        from pipelines.future_composer.to_usf import write_canary_usf
        from pipelines.future_composer.composer_asm import (
            build_via_asm_featuredriven)
        cfg = fc_standard_config('hvsc84/' + rel)
        usf_path = write_canary_usf(cfg)            # .usf alongside the .sid
        sid = build_via_asm_featuredriven(cfg)      # reads that .usf
        base = os.path.splitext(os.path.join(ROOT, 'hvsc84', rel))[0]
        open(base + '.sidfinity.sid', 'wb').write(sid)
        return (rel, True, '')
    except Exception as e:
        return (rel, False, f'{type(e).__name__}: {e}'[:120])


def main():
    results = RESULTS
    if '--results' in sys.argv:
        results = sys.argv[sys.argv.index('--results') + 1]
    from src.code_fingerprint import code_fingerprint
    code_hash = code_fingerprint('fc_standard')
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
        full.append(d['sid'])
    print(f'{len(full)} current-code FULL members to write', flush=True)
    if stale:
        print(f'  WARNING: skipped {stale} FULL rows with stale/absent code_hash. '
              f'Re-run tools/fc_family_batch.py to refresh before mass-write.',
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
