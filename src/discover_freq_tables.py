"""discover_freq_tables.py — batch freq-table detection across SIDs
using the engine-agnostic discovery script.

For each SID:
  1. Capture a short memtrace via siddump --memtrace (cached per file).
  2. Run discovery analysis (static disasm + dynamic trace).
  3. Identify tables whose role-via-SID-dataflow is freq_lo or freq_hi.
  4. Return the lowest such cluster's base address.

Cross-checks against rh_decompile.freq_table_addr where available.
"""
import os
import sys
import csv
import time
import traceback
from collections import Counter
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

# Per-process cached memtrace dir to avoid hitting same path concurrently
_MEMTRACE_CACHE = '/tmp/freq_disc_traces'
os.makedirs(_MEMTRACE_CACHE, exist_ok=True)


def _capture_memtrace(sid_path: str, duration: int = 5) -> str:
    """Capture a short memtrace (cached). Returns path to trace file."""
    base = os.path.basename(sid_path).replace('.sid', '')
    out = os.path.join(_MEMTRACE_CACHE, f'{base}_d{duration}.txt')
    if os.path.exists(out) and os.path.getsize(out) > 0:
        return out
    rc = os.system(
        f'/home/jtr/sidfinity/tools/siddump "{sid_path}" '
        f'--memtrace --duration {duration} --raw > "{out}" 2>/dev/null'
    )
    if rc != 0 or not os.path.exists(out) or os.path.getsize(out) == 0:
        return ''
    return out


def find_freq_table(sid_path: str, duration: int = 5) -> int | None:
    """Discover the freq-table base address for a SID. Returns None if
    not found (e.g., RSID, init failure, no SID-bound freq writes detected)."""
    sys.path.insert(0, os.path.join(ROOT, 'src'))
    from sidxray.discover import (
        parse_psid_header, parse_memtrace, trace_code_with_refs,
        infer_tables, trace_sid_dataflow,
    )
    h = parse_psid_header(sid_path)
    payload = h['payload']
    trace_path = _capture_memtrace(sid_path, duration)
    if not trace_path:
        return None
    code_offs, refs = trace_code_with_refs(
        payload, h['load_addr'], h['init_addr'], h['play_addr'])
    counts, _ = parse_memtrace(trace_path)
    tables = infer_tables(refs, counts, h['load_addr'], h['load_end'])
    sid_flow = trace_sid_dataflow(payload, h['load_addr'],
                                  h['init_addr'], h['play_addr'])

    # Find tables with freq_lo or freq_hi role
    freq_bases: list[int] = []
    for base, _t in tables.items():
        roles = sid_flow.get(base, set())
        if 'freq_lo' in roles or 'freq_hi' in roles:
            freq_bases.append(base)
    if not freq_bases:
        return None
    return min(freq_bases)


def _run_one(sid_path: str) -> dict:
    out = {'path': sid_path, 'name': os.path.basename(sid_path),
           'discovered': None, 'rh_found': None, 'agree': None,
           'error': ''}
    try:
        # Discovery
        try:
            disc = find_freq_table(sid_path)
            out['discovered'] = disc
        except Exception as e:
            out['error'] = f'discovery: {type(e).__name__}: {e}'
            return out
        # rh_decompile ground truth
        try:
            sys.path.insert(0, os.path.join(ROOT, 'src'))
            from rh_decompile import decompile
            d = decompile(sid_path)
            out['rh_found'] = d.freq_table_addr
        except Exception:
            pass  # rh_decompile failure isn't a discovery failure
        if out['rh_found'] is not None and out['discovered'] is not None:
            out['agree'] = (out['discovered'] == out['rh_found'])
    except Exception as e:
        out['error'] = traceback.format_exc()[:200]
    return out


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=None)
    p.add_argument('--workers', type=int, default=32)
    p.add_argument('--out-csv', default='/tmp/freq_discovery.csv')
    args = p.parse_args()

    print('Identifying Hubbard SIDs...')
    sys.path.insert(0, os.path.join(ROOT, 'src'))
    from sidid import scan_directory
    results = scan_directory(os.path.join(ROOT, 'data', 'C64Music'),
                             recursive=True)
    paths = sorted(r['path'] for r in results
                   if 'Hubbard' in (r.get('player') or ''))
    print(f'  {len(paths)} Hubbard SIDs')
    if args.limit:
        paths = paths[:args.limit]
        print(f'  limited to {len(paths)}')

    print(f'\nRunning discovery freq-table detection with {args.workers} workers...')
    t0 = time.time()
    with Pool(args.workers) as pool:
        results = pool.map(_run_one, paths)
    elapsed = time.time() - t0
    print(f'  done in {elapsed:.1f}s')

    # Summary
    n = len(results)
    disc_found = sum(1 for r in results if r['discovered'] is not None)
    rh_found = sum(1 for r in results if r['rh_found'] is not None)
    both_found = sum(1 for r in results
                     if r['discovered'] is not None and r['rh_found'] is not None)
    agree = sum(1 for r in results if r['agree'] is True)
    disagree = sum(1 for r in results if r['agree'] is False)
    disc_only = sum(1 for r in results
                    if r['discovered'] is not None and r['rh_found'] is None)
    rh_only = sum(1 for r in results
                  if r['discovered'] is None and r['rh_found'] is not None)
    neither = sum(1 for r in results
                  if r['discovered'] is None and r['rh_found'] is None)

    print(f'\n=== Detection summary ({n} Hubbard SIDs) ===')
    print(f'  rh_decompile.freq_table_addr found:     {rh_found:4d}  ({100*rh_found/n:.1f}%)')
    print(f'  discovery freq table found:             {disc_found:4d}  ({100*disc_found/n:.1f}%)')
    print(f'  both methods agree on address:          {agree:4d}  ({100*agree/max(both_found,1):.0f}% of overlap)')
    print(f'  both found but disagree:                {disagree:4d}')
    print(f'  discovery found, rh_decompile missed it:  {disc_only:4d}  <-- new unlocks')
    print(f'  rh_decompile found, discovery missed it:  {rh_only:4d}')
    print(f'  neither found:                          {neither:4d}')

    # Show some disagreements for inspection
    if disagree:
        print(f'\nDisagreements (first 5):')
        for r in results:
            if r['agree'] is False:
                print(f'  {r["name"]}: disc=${r["discovered"]:04X}  rh=${r["rh_found"]:04X}')
                if disagree <= 0: break

    # Show what the new unlocks look like
    if disc_only:
        print(f'\nDiscovery-only freq tables (first 10):')
        cnt = 0
        for r in results:
            if r['discovered'] is not None and r['rh_found'] is None:
                print(f'  {r["name"]}: discovered=${r["discovered"]:04X}')
                cnt += 1
                if cnt >= 10: break

    # CSV output for downstream analysis
    with open(args.out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['path', 'name', 'discovered_hex', 'rh_found_hex',
                    'agree', 'error'])
        for r in results:
            w.writerow([r['path'], r['name'],
                        f'${r["discovered"]:04X}' if r['discovered'] is not None else '',
                        f'${r["rh_found"]:04X}' if r['rh_found'] is not None else '',
                        '' if r['agree'] is None else ('T' if r['agree'] else 'F'),
                        r['error']])
    print(f'\nFull results: {args.out_csv}')


if __name__ == '__main__':
    main()
