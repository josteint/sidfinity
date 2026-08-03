#!/usr/bin/env python3
"""Diff two family-batch results jsonls — surface REGRESSIONS loudly.

Why this exists (2026-08-03, DMC r178 post-mortem): between the Jul-22 (r88)
and Jul-26 family batches, 4 members regressed full->partial (cdfa9c42's C29
CPU-eye overlay contaminated 3 Flash members; d80c1b94's glide-arrival record
creation broke Tomace/Other_Side). Both batches RECORDED the truth, but the
closeout reports NET aggregate counts — +57 net FULLs masked the -4 — and the
partials were folded into the work queue undifferentiated, where an
alphabetical march that had already passed their letters left them unnoticed
for a week. A regression is a SIGNAL (an exposure set some fix's census
missed); it must be surfaced as one, not averaged away.

Usage:
    python3 tools/batch_diff.py OLD.jsonl NEW.jsonl [--fail-on-regression]

Prints full->partial (REGRESSIONS), partial->full (gains), status changes
involving error/unsupported, and members present in only one batch. Rows are
deduped per src.batch_results.load_latest (append-only, last-wins).
Exit code 1 with --fail-on-regression when any full->partial exists — wire it
into a closeout to make the gate hard.
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.batch_results import load_latest  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('old')
    ap.add_argument('new')
    ap.add_argument('--fail-on-regression', action='store_true')
    args = ap.parse_args()
    old = load_latest(args.old)
    new = load_latest(args.new)

    def st(rows, p):
        r = rows.get(p)
        return r.get('status') if r else None

    regressions, gains, other, only_old, only_new = [], [], [], [], []
    for p in sorted(set(old) | set(new)):
        a, b = st(old, p), st(new, p)
        if a == b:
            continue
        if a is None:
            only_new.append((p, b))
        elif b is None:
            only_old.append((p, a))
        elif a == 'full' and b != 'full':
            regressions.append((p, b))
        elif a != 'full' and b == 'full':
            gains.append((p, a))
        else:
            other.append((p, a, b))

    def _n(rows, s):
        return sum(1 for r in rows.values() if r.get('status') == s)

    print(f"old: {os.path.basename(args.old)}  "
          f"full={_n(old, 'full')} partial={_n(old, 'partial')} "
          f"({len(old)} members)")
    print(f"new: {os.path.basename(args.new)}  "
          f"full={_n(new, 'full')} partial={_n(new, 'partial')} "
          f"({len(new)} members)")
    print()
    if regressions:
        print(f"⚠ REGRESSIONS (full -> not-full): {len(regressions)}")
        for p, b in regressions:
            print(f"    {p}  -> {b}")
    else:
        print("REGRESSIONS: 0")
    print(f"gains (not-full -> full): {len(gains)}")
    if other:
        print(f"other status changes: {len(other)}")
        for p, a, b in other[:20]:
            print(f"    {p}  {a} -> {b}")
    if only_old:
        print(f"members only in OLD: {len(only_old)}")
    if only_new:
        print(f"members only in NEW: {len(only_new)}")
    if regressions and args.fail_on_regression:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
