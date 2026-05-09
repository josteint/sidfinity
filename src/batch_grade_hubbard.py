"""batch_grade_hubbard.py — Run the writelog grader against every
Hubbard-engine SID in HVSC, in parallel.

Outputs:
  - Per-SID grade + top diverging registers (CSV)
  - Aggregate distribution (grade counts)
  - Bug-signature clustering (which register-divergence patterns are
    most common; these point at shared bugs that, when fixed, lift
    many songs at once).
"""

import os
import sys
import csv
import time
import traceback
from collections import Counter, defaultdict
from multiprocessing import Pool, cpu_count

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

DEFAULT_DURATION = 10  # seconds


def _grade_one(args: tuple[str, int]) -> dict:
    """Process one SID. Returns dict with grade, score, top divergent
    registers, and any error."""
    sid_path, duration = args
    out = {
        'path': sid_path, 'name': os.path.basename(sid_path),
        'grade': '?', 'snap_pct': 0.0, 'matched': 0, 'total': 0,
        'top_diverging': [],
        'error': '',
    }
    try:
        # Reimport in worker to avoid module-state issues
        sys.path.insert(0, os.path.join(ROOT, 'src'))
        from converters.rh_to_usf import rh_to_usf
        from converters.usf_to_sid import usf_to_sid
        from writelog_grade import grade

        # Per-worker tmp file
        tmp = f'/tmp/batch_{os.getpid()}.sid'
        usf = rh_to_usf(sid_path)
        usf_to_sid(usf, tmp)
        report = grade(sid_path, tmp, duration=duration, cycle_accurate=False)
        out['grade'] = report.grade
        out['snap_pct'] = report.snapshot_match_pct
        out['matched'] = report.snapshot_matched
        out['total'] = report.snapshot_total
        # Top 5 diverging registers (register index, count)
        sorted_div = sorted(report.diverging_registers.items(),
                            key=lambda kv: -kv[1])[:5]
        out['top_diverging'] = [(r, c) for r, c in sorted_div]
        try: os.remove(tmp)
        except OSError: pass
    except Exception as e:
        out['error'] = f'{type(e).__name__}: {e}'
        out['error'] += '\n' + traceback.format_exc()[:300]
    return out


def find_hubbard_sids() -> list[str]:
    """Use sidid to identify Hubbard-engine SIDs across HVSC."""
    sys.path.insert(0, os.path.join(ROOT, 'src'))
    from sidid import scan_directory
    results = scan_directory(os.path.join(ROOT, 'data', 'C64Music'), recursive=True)
    return sorted(r['path'] for r in results
                  if 'Hubbard' in (r.get('player') or ''))


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--duration', type=int, default=DEFAULT_DURATION)
    p.add_argument('--workers', type=int, default=64)
    p.add_argument('--limit', type=int, default=None,
                   help='Process only first N SIDs (for quick testing)')
    p.add_argument('--out-csv', default='/tmp/hubbard_grades.csv')
    args = p.parse_args()

    print(f'Identifying Hubbard SIDs across HVSC...')
    paths = find_hubbard_sids()
    print(f'  {len(paths)} found')
    if args.limit:
        paths = paths[:args.limit]
        print(f'  limited to {len(paths)}')

    print(f'\nGrading {len(paths)} SIDs with {args.workers} workers, '
          f'{args.duration}s duration each...')
    t0 = time.time()

    work = [(p, args.duration) for p in paths]
    with Pool(args.workers) as pool:
        results = pool.map(_grade_one, work)

    elapsed = time.time() - t0
    print(f'  done in {elapsed:.1f}s '
          f'({elapsed/max(len(paths),1)*1000:.0f}ms per SID avg)')

    # Aggregate by grade
    grade_counts = Counter(r['grade'] for r in results)
    print(f'\n=== Grade distribution ===')
    for g in 'ABCDF?':
        n = grade_counts.get(g, 0)
        bar = '█' * int(60 * n / max(len(paths), 1))
        print(f'  {g}: {n:4d}  {100*n/len(paths):5.1f}%  {bar}')

    err_count = sum(1 for r in results if r['error'])
    print(f'  errors: {err_count}')
    if err_count and err_count <= 5:
        print(f'  error details:')
        for r in results:
            if r['error']:
                print(f'    {r["name"]}: {r["error"][:120]}')

    # Cluster failures by bug signature: top diverging register patterns
    print(f'\n=== Bug-signature clusters (failed/F-grade SIDs) ===')
    failed = [r for r in results if r['grade'] in 'CDF']
    print(f'  {len(failed)} SIDs at C/D/F (need attention)')

    # Group by top-3 diverging registers
    sig_groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in failed:
        sig = tuple(reg for reg, _ in r['top_diverging'][:3])
        sig_groups[sig].append(r)

    # Show top 10 clusters
    clusters = sorted(sig_groups.items(), key=lambda kv: -len(kv[1]))[:10]
    from writelog_grade import _register_name
    for i, (sig, members) in enumerate(clusters):
        names = [_register_name(r) for r in sig]
        print(f'  [{i+1}] {len(members)} SIDs diverge in {names}')
        # Show 3 example SIDs
        for m in members[:3]:
            print(f'         {m["name"]} (grade {m["grade"]}, {m["snap_pct"]:.1f}%)')

    # Write CSV for downstream analysis
    with open(args.out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['path', 'name', 'grade', 'snap_pct', 'matched', 'total',
                    'top_div_regs', 'error'])
        for r in results:
            w.writerow([r['path'], r['name'], r['grade'], f'{r["snap_pct"]:.2f}',
                        r['matched'], r['total'],
                        ' '.join(f'{reg:02X}:{c}' for reg, c in r['top_diverging']),
                        r['error'][:200]])
    print(f'\nFull results: {args.out_csv}')


if __name__ == '__main__':
    main()
