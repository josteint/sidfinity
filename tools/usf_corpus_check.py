#!/usr/bin/env python3
"""Can the CURRENT grammar still read every stored .usf?

The blind spot this closes: `tools/regression.py` builds from a handful of
portfolio members, so a USF SCHEMA change can orphan thousands of stored
artifacts while regression stays fully green. On 2026-07-21 a typed-field
move (`speed_ctr_init`, commit 718ade06) left 1,182 of 11,943 stored .usf
files (9.9%) unparseable — invisible to every existing check, and fatal to
`verify_usf` (the production-path verdict, which builds from a stored .usf)
and to any downstream ML consumer of the corpus.

That is the C20 palimpsest class one layer out: not a stale VERDICT, but a
stale ARTIFACT. The cure is the same shape — re-run the owning family's
batch, then its mass-write — but you have to know it happened.

Run after ANY grammar/writer/types change, and before trusting the corpus:

    python3 tools/usf_corpus_check.py            # scan, group, exit 1 on failures
    python3 tools/usf_corpus_check.py --quiet    # counts only
    python3 tools/usf_corpus_check.py --list 40  # show N failing paths

Groups failures by DMC family (tmp/dmc_families.json) when available, since
the fix is per-family: `dmc_family_batch.py --members <f>.json --out <f>.jsonl`
then `dmc_mass_write.py --results <f>.jsonl`. Members that are NOT full will
never be refreshed by a mass-write — a leftover .usf from when older code
judged them full is a genuine palimpsest and wants deleting, not rebuilding.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'src'), ROOT]

from src.jobs import default_jobs  # noqa: E402


def _check(path: str):
    """Parse one .usf. Returns None on success, (path, short_reason) on failure."""
    sys.path[:0] = [os.path.join(ROOT, 'src'), ROOT]
    from src.usf import parse_file
    try:
        parse_file(path)
        return None
    except Exception as e:                       # parse error OR typed-AST error
        reason = str(e).split('\n')[0]
        # drop the position so identical causes group together
        return (path, reason.split(' at line')[0][:60])


def _family_map():
    """sid-relpath -> DMC family id, from tmp/dmc_families.json (if present)."""
    p = os.path.join(ROOT, 'tmp', 'dmc_families.json')
    if not os.path.exists(p):
        return {}
    try:
        fams = json.load(open(p))
    except Exception:
        return {}
    return {m: k for k, v in fams.items() for m in v}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', default=os.path.join(ROOT, 'hvsc84'))
    ap.add_argument('--quiet', action='store_true', help='counts only')
    ap.add_argument('--list', type=int, default=0, metavar='N',
                    help='print N failing paths')
    a = ap.parse_args()

    usfs = sorted(glob.glob(os.path.join(a.root, '**', '*.usf'), recursive=True))
    if not usfs:
        print(f'no .usf files under {a.root}')
        return 0

    with Pool(default_jobs(cap=len(usfs))) as pool:
        bad = [r for r in pool.map(_check, usfs, chunksize=8) if r]

    ok = len(usfs) - len(bad)
    pct = 100.0 * len(bad) / len(usfs)
    print(f'stored .usf : {len(usfs)}')
    print(f'  parse OK  : {ok}')
    print(f'  FAIL      : {len(bad)}  ({pct:.1f}%)')

    if bad and not a.quiet:
        print('\nby cause:')
        for reason, n in collections.Counter(r for _, r in bad).most_common(10):
            print(f'  {n:6d}  {reason}')

        fam = _family_map()
        if fam:
            print('\nby DMC family (re-run that family\'s batch + mass-write):')
            counts = collections.Counter()
            prefix = a.root.rstrip('/') + '/'
            for p, _ in bad:
                rel = p[len(prefix):] if p.startswith(prefix) else p
                counts[fam.get(rel.replace('.usf', '.sid'), 'not-in-dmc-families')] += 1
            for k, n in counts.most_common(10):
                print(f'  {n:6d}  {k[:16]}')

    if bad and a.list:
        print(f'\nfirst {min(a.list, len(bad))} failing files:')
        for p, r in bad[:a.list]:
            print(f'  {p}\n      {r}')

    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
