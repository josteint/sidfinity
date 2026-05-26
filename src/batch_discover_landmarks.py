"""batch_discover_landmarks.py — run discover_hubbard_landmarks across
all Hubbard-engine SIDs in HVSC, compare against rh_decompile, report
per-landmark coverage and disagreement analysis."""

import os
import sys
import csv
import time
import traceback
from collections import Counter, defaultdict
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))


def _run_one(sid_path: str) -> dict:
    out = {'path': sid_path, 'name': os.path.basename(sid_path),
           'lm': None, 'rh': None, 'error': ''}
    try:
        sys.path.insert(0, os.path.join(ROOT, 'src'))
        from discover_hubbard_landmarks import discover_hubbard_landmarks
        out['lm'] = discover_hubbard_landmarks(sid_path)
    except Exception as e:
        out['error'] = f'discovery: {type(e).__name__}: {e}'
        return out
    try:
        from rh_decompile import decompile
        d = decompile(sid_path)
        out['rh'] = {
            'load_addr': d.load_addr, 'init_addr': d.init_addr,
            'play_addr': d.play_addr, 'num_songs': d.num_songs,
            'freq_table_addr': d.freq_table_addr,
            'instr_addr': d.instr_addr, 'instr_count': len(d.instruments),
            'song_table_addr': d.song_table_addr,
            'seqlo_addr': d.seqlo_addr, 'seqhi_addr': d.seqhi_addr,
            'num_sequences': d.num_sequences,
        }
    except Exception:
        pass  # rh_decompile failure is informative on its own
    return out


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=32)
    p.add_argument('--limit', type=int, default=None)
    p.add_argument('--out-csv', default='/tmp/landmark_discovery.csv')
    args = p.parse_args()

    print('Identifying Hubbard SIDs...')
    from sidid import scan_directory
    res = scan_directory(os.path.join(ROOT, 'data', 'C64Music'),
                         recursive=True)
    paths = sorted(r['path'] for r in res
                   if 'Hubbard' in (r.get('player') or ''))
    print(f'  {len(paths)} Hubbard SIDs')
    if args.limit:
        paths = paths[:args.limit]

    print(f'\nDiscovery + rh_decompile in parallel ({args.workers} workers)...')
    t0 = time.time()
    with Pool(args.workers) as pool:
        results = pool.map(_run_one, paths)
    elapsed = time.time() - t0
    print(f'  done in {elapsed:.1f}s')

    # Per-landmark coverage
    landmark_names = ['freq_table_addr', 'instr_addr', 'song_table_addr',
                      'seqlo_addr', 'seqhi_addr']
    print(f'\n=== Per-landmark coverage on {len(results)} SIDs ===')
    print(f'{"landmark":<20s}  {"discovery":<12s}  {"rh_decompile":<14s}  '
          f'{"both":<6s}  {"disc-only":<10s}  {"rh-only":<8s}  {"neither":<8s}')
    for lname in landmark_names:
        d_found = sum(1 for r in results
                      if r['lm'] and r['lm'].found.get(lname, False))
        r_found = sum(1 for r in results
                      if r['rh'] and r['rh'].get(lname) is not None)
        both = sum(1 for r in results
                   if r['lm'] and r['lm'].found.get(lname, False)
                   and r['rh'] and r['rh'].get(lname) is not None)
        d_only = d_found - both
        r_only = r_found - both
        neither = len(results) - d_found - r_only
        print(f'{lname:<20s}  {d_found:>4d} ({100*d_found/len(results):4.0f}%)  '
              f'{r_found:>4d} ({100*r_found/len(results):4.0f}%)  '
              f'{both:>4d}    {d_only:>4d}        {r_only:>4d}      {neither:>4d}')

    # All-landmarks-found counts
    full_disc = sum(1 for r in results
                    if r['lm'] and all(r['lm'].found.get(n, False)
                                       for n in landmark_names))
    full_rh = sum(1 for r in results
                  if r['rh'] and all(r['rh'].get(n) is not None
                                     for n in landmark_names))
    print(f'\nAll 5 critical landmarks found:')
    print(f'  discovery:    {full_disc:4d} / {len(results)} '
          f'({100*full_disc/len(results):.1f}%)')
    print(f'  rh_decompile: {full_rh:4d} / {len(results)} '
          f'({100*full_rh/len(results):.1f}%)')

    # CSV
    with open(args.out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        cols = ['path', 'name'] + [f'd_{n}' for n in landmark_names] + \
               [f'r_{n}' for n in landmark_names] + \
               ['d_instr_count', 'r_instr_count', 'd_num_seq', 'r_num_seq',
                'd_score', 'error']
        w.writerow(cols)
        for r in results:
            row = [r['path'], r['name']]
            for n in landmark_names:
                v = r['lm'].__dict__.get(n) if r['lm'] else None
                row.append(f'${v:04X}' if v is not None else '')
            for n in landmark_names:
                v = r['rh'].get(n) if r['rh'] else None
                row.append(f'${v:04X}' if isinstance(v, int) else '')
            row.append(r['lm'].instr_count if r['lm'] else '')
            row.append(r['rh'].get('instr_count', '') if r['rh'] else '')
            row.append(r['lm'].num_sequences if r['lm'] else '')
            row.append(r['rh'].get('num_sequences', '') if r['rh'] else '')
            row.append(f'{r["lm"].coverage_score():.2f}' if r['lm'] else '')
            row.append(r['error'][:200])
            w.writerow(row)
    print(f'\nFull results: {args.out_csv}')


if __name__ == '__main__':
    main()
