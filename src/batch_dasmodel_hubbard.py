"""batch_dasmodel_hubbard.py — for each Hubbard SID where discovery
finds all critical landmarks, run das_model_gen.extract → generate_asm
→ build_sid → grade. Report how many actually produce Grade A rebuilds.

This is the real test of the "generalize das_model_gen via discovery"
strategy. The structural-coverage win (86.3% all-landmarks) is
necessary but not sufficient — we need to know how many of those 246
actually rebuild correctly when fed through das_model_gen.
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


def _process_one(sid_path: str) -> dict:
    """Discovery → extract → asm → SID → grade for one SID."""
    out = {'path': sid_path, 'name': os.path.basename(sid_path),
           'coverage': 0.0,
           'grade': '?', 'snap_pct': 0.0,
           'top_diverging': [],
           'phase': '', 'error': ''}
    try:
        sys.path.insert(0, os.path.join(ROOT, 'src'))
        # Phase 1: discover landmarks
        out['phase'] = 'discover'
        from discover_hubbard_landmarks import discover_hubbard_landmarks
        lm = discover_hubbard_landmarks(sid_path)
        out['coverage'] = lm.coverage_score()
        if lm.coverage_score() < 1.0:
            out['error'] = 'incomplete landmarks; skipping'
            return out

        # Phase 2: extract (T, I, S)
        out['phase'] = 'extract'
        from das_model_gen import extract
        T, instrs, score = extract(subtune=0,
                                    sid_path=sid_path,
                                    ft_base=lm.freq_table_addr)

        # Phase 3: generate_asm + build_sid
        out['phase'] = 'asm'
        from das_model_gen import generate_asm, build_sid
        asm = generate_asm(T, instrs, score)
        rebuilt = f'/tmp/dasm_batch_{os.getpid()}.sid'
        ok = build_sid(asm, rebuilt, source_sid_path=sid_path)
        if not ok:
            out['error'] = 'build_sid failed (likely assembly error)'
            return out

        # Phase 4: grade
        out['phase'] = 'grade'
        from writelog_grade import grade
        report = grade(sid_path, rebuilt, duration=10)
        out['grade'] = report.grade
        out['snap_pct'] = report.snapshot_match_pct
        sorted_div = sorted(report.diverging_registers.items(),
                            key=lambda kv: -kv[1])[:5]
        out['top_diverging'] = [(r, c) for r, c in sorted_div]

        try: os.remove(rebuilt)
        except OSError: pass
    except Exception as e:
        out['error'] = f'{type(e).__name__}: {e}'
    return out


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, default=32)
    p.add_argument('--limit', type=int, default=None)
    p.add_argument('--out-csv', default='/tmp/dasm_batch.csv')
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

    print(f'\nDiscovery → das_model_gen → grade ({args.workers} workers)...')
    t0 = time.time()
    with Pool(args.workers) as pool:
        results = pool.map(_process_one, paths)
    elapsed = time.time() - t0
    print(f'  done in {elapsed:.1f}s')

    grade_counts = Counter(r['grade'] for r in results)
    phase_counts = Counter(r['phase'] for r in results if r['error'])

    print(f'\n=== Grade distribution ({len(results)} Hubbard SIDs) ===')
    for g in 'ABCDF?':
        n = grade_counts.get(g, 0)
        bar = '█' * int(60 * n / max(len(results), 1))
        print(f'  {g}: {n:4d}  {100*n/len(results):5.1f}%  {bar}')

    print(f'\n=== Failure modes ({sum(1 for r in results if r["error"])} errors) ===')
    for phase, n in phase_counts.most_common():
        print(f'  {phase or "(unknown)"}: {n}')

    # Show specific A and B grade names
    a_grades = [r for r in results if r['grade'] == 'A']
    b_grades = [r for r in results if r['grade'] == 'B']
    if a_grades:
        print(f'\n=== Grade A SIDs ({len(a_grades)}) ===')
        for r in a_grades[:20]:
            print(f'  {r["name"]} ({r["snap_pct"]:.1f}%)')
    if b_grades:
        print(f'\n=== Grade B SIDs ({len(b_grades)}) ===')
        for r in b_grades[:20]:
            print(f'  {r["name"]} ({r["snap_pct"]:.1f}%)')

    # CSV
    with open(args.out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['path', 'name', 'coverage', 'grade', 'snap_pct',
                    'top_div_regs', 'phase', 'error'])
        for r in results:
            w.writerow([r['path'], r['name'], f'{r["coverage"]:.2f}',
                        r['grade'], f'{r["snap_pct"]:.2f}',
                        ' '.join(f'{reg:02X}:{c}' for reg, c in r['top_diverging']),
                        r['phase'], r['error'][:200]])
    print(f'\nFull results: {args.out_csv}')


if __name__ == '__main__':
    main()
