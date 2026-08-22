#!/usr/bin/env python3
"""fbdl_measure.py — would tier 1 have caught what tier 2 found?

FBDL (fault-detection loss) is the fraction of real regressions that the
reduced suite misses. Shi et al. (ISSTA'18, 1,478 real failed builds) found it
is the ONLY thing that predicts a reduced suite's value: size reduction had
R^2 = 0.00 against real faults, and coverage loss was non-predictive too. We
compute coverage numbers we cannot validate and have never computed this one.

It is computable retrospectively, because we keep every batch generation. For
each consecutive pair of a family's results files, find the members that went
full -> non-full (the regressions tier 2 caught), and ask how many are in the
tier-1 portfolio. The answer is the fraction tier 1 would have caught at the
moment the breaking change landed, instead of a week later.

⚠ ANACHRONISM, STATED: the portfolio applied is TODAY's. A July regression is
scored against a portfolio derived in August, so this measures "would a
portfolio of this shape catch it", not "did the portfolio of the day catch
it". That is still the decision-relevant question — we are choosing a shape —
but it is not a historical audit.

⚠ Pairs are ordered by mtime, which is when a file was last APPENDED to, not
when its generation began. Treat a pair whose regression list looks absurd
(hundreds of members) as a member-set change or a key change rather than a
code regression, and exclude it — the tool flags those.

Usage:
    python3 tools/fbdl_measure.py --engine dmc_v4
    python3 tools/fbdl_measure.py --engine dmc_v4 --pair OLD.jsonl NEW.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.batch_results import load_latest        # noqa: E402
from src.tslog import ts                         # noqa: E402

# Chronological generations per family, oldest first. Hand-ordered rather than
# globbed: the tmp/ directory mixes working files, snapshots and one-off
# experiment outputs, and a wrong ordering silently inverts every transition.
GENERATIONS = {
    'dmc_v4': {
        'portfolios': ['tools/dmc_regression_portfolio.json',
                       'tools/dmc_f2_regression_portfolio.json'],
        'key': 'path',
        'files': [
            'tmp/dmc_f1_r83.jsonl',
            'tmp/dmc_f1_r84.jsonl',
            'tmp/dmc_f1_r86.jsonl',
            'tmp/dmc_f1_r87.jsonl',
            'tmp/dmc_f1_qc.jsonl',
            'tmp/dmc_f1_fullbatch_verify.jsonl',
            'tmp/dmc_f1_85b_results.jsonl',
            'tmp/dmc_f1_85c_results.jsonl',
            'tmp/dmc_f1_85d_results.jsonl',
            'tmp/dmc_f1_prev_batch.jsonl',
            'tmp/dmc_f1_prev_snapshot.jsonl',
            'tmp/dmc_f1_85_results.jsonl',
        ],
    },
    'dmc_f2': {
        'portfolios': ['tools/dmc_f2_regression_portfolio.json'],
        'key': 'path',
        'files': [
            'tmp/dmc_f2_85_prev.jsonl',
            'tmp/dmc_f2_pre0820.jsonl',
            'tmp/dmc_f2_85_results.pre_close.jsonl',
            'tmp/dmc_f2_85_results.jsonl',
        ],
    },
}


def portfolio_members(paths) -> set:
    out = set()
    for rel in paths:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        for m in d.get('portfolio', []):
            out.add(m['sid'] if isinstance(m, dict) else m)
    return out


def transitions(old_p, new_p, key):
    a = load_latest(old_p, path_key=key)
    b = load_latest(new_p, path_key=key)
    common = set(a) & set(b)
    regressed = sorted(m for m in common
                       if a[m].get('status') == 'full'
                       and b[m].get('status') != 'full')
    gained = sorted(m for m in common
                    if a[m].get('status') != 'full'
                    and b[m].get('status') == 'full')
    return regressed, gained, len(common)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', default='dmc_v4', choices=sorted(GENERATIONS))
    ap.add_argument('--pair', nargs=2, help='OLD.jsonl NEW.jsonl')
    ap.add_argument('--absurd', type=int, default=200,
                    help='regression counts above this are treated as a '
                         'member-set/key change, not a code regression')
    a = ap.parse_args()
    spec = GENERATIONS[a.engine]
    pf = portfolio_members(spec['portfolios'])
    ts(f'{a.engine}: portfolio = {len(pf)} members')

    if a.pair:
        pairs = [tuple(a.pair)]
    else:
        files = [f for f in spec['files']
                 if os.path.exists(os.path.join(ROOT, f))]
        pairs = list(zip(files, files[1:]))
    ts(f'{len(pairs)} consecutive generation pairs')

    tot_reg = tot_caught = 0
    excluded = 0
    for old, new in pairs:
        reg, gain, n = transitions(os.path.join(ROOT, old),
                                   os.path.join(ROOT, new), spec['key'])
        if len(reg) > a.absurd:
            ts(f'  {os.path.basename(old):34s} -> '
               f'{os.path.basename(new):34s} '
               f'EXCLUDED ({len(reg)} regressions = member-set/key change)')
            excluded += 1
            continue
        caught = [m for m in reg if m in pf]
        tot_reg += len(reg)
        tot_caught += len(caught)
        if reg:
            ts(f'  {os.path.basename(old):34s} -> '
               f'{os.path.basename(new):34s} '
               f'+{len(gain):<4d} REGRESSED {len(reg):<3d} '
               f'of which tier-1 would catch {len(caught)}')
            for m in reg[:6]:
                ts(f'        {"[IN PORTFOLIO]" if m in pf else "              "} '
                   f'{m}')
        else:
            ts(f'  {os.path.basename(old):34s} -> '
               f'{os.path.basename(new):34s} '
               f'+{len(gain):<4d} no regressions')
    ts('')
    if tot_reg:
        ts(f'FBDL over {len(pairs) - excluded} pairs: tier 1 would have caught '
           f'{tot_caught}/{tot_reg} regressions '
           f'({100 * tot_caught / tot_reg:.0f}%) — '
           f'LOSS {100 * (tot_reg - tot_caught) / tot_reg:.0f}%')
    else:
        ts('no regressions found in the compared generations — FBDL undefined')
    if excluded:
        ts(f'({excluded} pairs excluded as member-set/key changes)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
