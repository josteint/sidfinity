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

from src.jobs import default_jobs  # noqa: E402

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
    # SYNC the stored corpus to the verdicts (src/corpus_sync): current-code
    # rows only, and a member that is NOT full must have no stored artifact.
    # FC has ONE build path, so build_path is not required — the moment it
    # grows a second, the batch must record one and this must require it.
    from src import corpus_sync
    p = corpus_sync.plan(results, 'fc_standard', os.path.join(ROOT, 'hvsc84'),
                         path_key='sid')
    for line in p.report('tools/fc_family_batch.py'):
        print(line, flush=True)
    full = [d['sid'] for d in p.write]
    corpus_sync.remove_orphans(p)
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
    print('\nNow refresh the DB: python3 tools/build_sid_db.py', flush=True)


if __name__ == '__main__':
    main()
