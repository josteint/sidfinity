#!/usr/bin/env python3
"""Mass-write DMC FULL members; then refresh the index (hvsc84.csv).

Reads tmp/dmc_wide_results.jsonl, and for every member with status
'full' writes its .usf + .sidfinity.sid alongside the HVSC original.
Then run `python3 tools/build_sid_db.py` to refresh sidfinity_md5 /
usf_path in hvsc84.csv (the CSV index — DuckDB-queried via src/sid_db).

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

RESULTS = os.path.join(ROOT, 'tmp', 'dmc_wide_results.jsonl')


def write_member(item) -> tuple:
    rel, hold_gateoff = item if isinstance(item, (list, tuple)) else (item, None)
    try:
        from pipelines.dmc.v4.factory import dmc_v4_config
        from pipelines.dmc.v4.extract.to_usf import write_dmc_usf
        from pipelines.dmc.composer_asm import build_dmc_sid
        from src.usf.parser import parse_file
        hvsc = os.path.join(ROOT, 'hvsc84')
        cfg = dmc_v4_config(rel, hvsc_root=hvsc)
        out_dir = os.path.dirname(os.path.join(hvsc, rel))
        usf_path = write_dmc_usf(cfg, out_dir, hvsc_root=hvsc)
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
    full = [(json.loads(l)['path'], json.loads(l).get('hold_gateoff'))
            for l in open(results) if json.loads(l)['status'] == 'full']
    print(f'{len(full)} FULL members to write', flush=True)
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


if __name__ == '__main__':
    main()
