#!/usr/bin/env python3
"""Census of the GoatTracker V1 wide-batch results (tools/gt_v1_family_batch.py).

Reads tmp/gt_v1_results.jsonl and reports the accurate FULL rate per player +
clusters the partials by first-divergence REGISTER ROLE (which SID write diverges
first) and depth band, with representatives — to rank real buckets for the
convergence grind. The 'len' bucket (matched over the overlap, only total length
differs) is reported separately: these are near-converged (often a song-end
capture-boundary tail).

Usage:  PYTHONPATH=src:. python3 pipelines/goattracker/v1/census.py [--results FILE] [--player tracker|gamemusic]
"""
from __future__ import annotations

import collections
import json
import os
import sys

# this file lives at pipelines/goattracker/v1/ → repo root is 4 dirs up
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


def reg_role(reg: int) -> str:
    """SID register -> voice/role label."""
    if 0x15 <= reg <= 0x18:
        return {0x15: 'filt_cutlo', 0x16: 'filt_cuthi',
                0x17: 'filt_res', 0x18: 'mode/vol'}[reg]
    if reg > 0x18:
        return f'reg_{reg:02x}'
    v, off = divmod(reg, 7)
    return f'v{v + 1}_' + ['freqlo', 'freqhi', 'pwlo', 'pwhi',
                           'ctrl', 'AD', 'SR'][off]


def depth_band(d) -> str:
    if d is None:
        return 'len'
    if d < 50:
        return 'div<50'
    if d < 200:
        return 'div<200'
    if d < 1000:
        return 'div<1k'
    if d < 10000:
        return 'div<10k'
    return 'div>=10k'


def main():
    results = os.path.join(ROOT, 'tmp', 'gt_v1_results.jsonl')
    pf = None
    args = sys.argv[1:]
    while args:
        a = args.pop(0)
        if a == '--results':
            results = args.pop(0)
        elif a == '--player':
            pf = args.pop(0)

    recs = [json.loads(l) for l in open(results) if l.strip()]
    if pf:
        recs = [r for r in recs if r.get('player') == pf]

    print(f'=== {len(recs)} records'
          f'{" (player=" + pf + ")" if pf else ""} ===')

    # overall by player x status
    by = collections.Counter()
    for r in recs:
        by[(r.get('player', '-'), r['status'])] += 1
    for player in ('tracker', 'gamemusic', '-'):
        ps = {s: c for (p, s), c in by.items() if p == player}
        if not ps:
            continue
        tot = sum(ps.values())
        full = ps.get('full', 0)
        print(f'  {player:10s}: {full}/{tot} FULL ({100*full/tot:.1f}%)  '
              f'{dict(sorted(ps.items()))}')

    # partial clustering by (player, role, depth band)
    parts = [r for r in recs if r['status'] == 'partial']
    print(f'\n=== {len(parts)} partials — by (player, first-div role, depth) ===')
    buckets = collections.defaultdict(list)
    for r in parts:
        sig = r.get('div_sig')
        if sig == 'len' or r.get('first_div') is None:
            role = 'len'
        elif isinstance(sig, list):
            role = reg_role(sig[0])
        else:
            role = '?'
        buckets[(r.get('player', '-')[:4], role,
                 depth_band(r.get('first_div')))].append(r)
    for key, rs in sorted(buckets.items(), key=lambda kv: -len(kv[1])):
        ex = rs[0]
        exsig = ex.get('div_sig')
        sigtxt = (f"{exsig[1]:02x}->{exsig[2]:02x}"
                  if isinstance(exsig, list) else exsig)
        print(f'  {key[0]:5s} {key[1]:14s} {key[2]:9s} x{len(rs):4d}  '
              f'eg {os.path.basename(ex["path"])} '
              f'(div@{ex.get("first_div")} {sigtxt})')

    # detect/build failures
    for st in ('detect_fail', 'build_fail', 'error', 'timeout'):
        fails = [r for r in recs if r['status'] == st]
        if not fails:
            continue
        reasons = collections.Counter(r.get('reason', '?').split(':')[0]
                                      for r in fails)
        print(f'\n=== {len(fails)} {st} — by reason ===')
        for reason, c in reasons.most_common(10):
            ex = next(r for r in fails if r.get('reason', '').startswith(reason))
            print(f'  {reason:30s} x{c:4d}  eg {os.path.basename(ex["path"])}'
                  f'  {ex.get("reason", "")[:70]}')


if __name__ == '__main__':
    main()
