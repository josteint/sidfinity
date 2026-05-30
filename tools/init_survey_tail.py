"""Tail survey — the 11% of HVSC beyond the top 100 engines.

  - Long tail (6.6%): 542 classified engines with ≤39 SIDs each.
    Sample 1 SID from each of the 100 highest-ranked tail engines.
  - Unclassified (4.4%): 2,639 SIDs with engine = NULL. Random
    sample of 200.

Stress-test the trichotomy: do these weirder SIDs fit the same
buckets, or does the long tail surface something new?
"""

import sqlite3
import sys
import os
import random
from collections import Counter

sys.path.insert(0, '.')

from pipelines.hubbard.verify_cycle import writelog_capture


def classify(frame0):
    counts = Counter()
    final = {}
    for cyc, reg, val in frame0:
        counts[reg] += 1
        final[reg] = val
    return {
        'n_writes': len(frame0),
        'regs_touched': set(counts),
        'final': final,
        'transients': {r: n for r, n in counts.items() if n > 1},
    }


def bucket_for(feat, n_eng_writes):
    if n_eng_writes == 0:
        return 'deferred (no SID writes)'
    if n_eng_writes <= 3:
        return 'minimal touch (≤3 writes)'
    if 24 <= n_eng_writes <= 30:
        return 'clean reset (silence-clear + $D418)'
    voice_ctrl_transients = sum(
        1 for r in (0x04, 0x0B, 0x12) if r in feat['transients'])
    if voice_ctrl_transients >= 2:
        return 'noise-burst / test-bit / multi-pass reset'
    if n_eng_writes > 30:
        return 'thorough setup (>30 writes)'
    return 'partial setup (4-23 writes)'


def survey(rows, label):
    print(f'\n{"=" * 70}\n{label} ({len(rows)} samples)\n{"=" * 70}')
    bucket_counts = Counter()
    surprises = []
    n_d418_nondefault = 0
    n_filter = 0
    extra_regs = []

    for engine, path, songlen in rows:
        full = f'/home/jtr/sidfinity/hvsc84/{path}'
        if not os.path.exists(full):
            continue
        try:
            frames = writelog_capture(full, 0, duration=1.0)
        except Exception:
            continue
        if not frames:
            continue
        f0 = frames[0]
        feat = classify(f0)
        engine_writes = [
            w for w in f0
            if not (w[0] < 100 and w[1] == 0x18 and w[2] == 0x0F)]
        n_eng = len(engine_writes)
        bucket = bucket_for(feat, n_eng)
        bucket_counts[bucket] += 1

        # Track outliers
        d418 = feat['final'].get(0x18)
        if d418 not in (None, 0x0F):
            n_d418_nondefault += 1
        if feat['final'].get(0x16, 0) or feat['final'].get(0x17, 0):
            n_filter += 1

        # Look for surprises: any register outside $D400-$D418
        # (shouldn't happen — siddump only reports SID)
        for r in feat['regs_touched']:
            if r > 0x18:
                extra_regs.append((engine, path, r))

        # Look for extreme write counts (potentially novel patterns)
        if n_eng > 300:
            surprises.append((n_eng, engine, path, 'huge init'))
        if len(feat['transients']) > 25 and max(feat['transients'].values()) > 10:
            mx = max(feat['transients'].values())
            surprises.append((n_eng, engine, path,
                              f'extreme transient (max ×{mx})'))

    print(f'\nBucket distribution:')
    for b, n in bucket_counts.most_common():
        pct = 100 * n / sum(bucket_counts.values())
        print(f'  {n:4d} ({pct:5.1f}%)  {b}')

    total = sum(bucket_counts.values())
    print(f'\nAggregate:')
    print(f'  {n_d418_nondefault}/{total} ({100*n_d418_nondefault/total:.0f}%) '
          f'use non-default $D418')
    print(f'  {n_filter}/{total} ({100*n_filter/total:.0f}%) set filter')
    if extra_regs:
        print(f'\nRegisters outside $D400-$D418 (UNEXPECTED):')
        for eng, p, r in extra_regs[:10]:
            print(f'  ${r:02X} in {eng}/{p}')
    if surprises:
        print(f'\nSurprises (extreme write counts or transients):')
        for n, eng, p, note in sorted(surprises, reverse=True)[:15]:
            print(f'  {n:4d} writes — {note:40s} {eng}/{p}')


def main():
    db = sqlite3.connect('hvsc84.db')

    # 1. Long tail — top 100 of the tail engines (ranks 101-200)
    tail_rows = db.execute(
        "SELECT engine, COUNT(*) FROM sids WHERE engine IS NOT NULL "
        "GROUP BY engine ORDER BY COUNT(*) DESC LIMIT 200 OFFSET 100"
    ).fetchall()
    tail_samples = []
    for eng, _ in tail_rows:
        # Pick a longer-than-30s tune; fall back to any
        r = db.execute(
            "SELECT path, songlength_s FROM sids "
            "WHERE engine = ? AND songlength_s > 30 "
            "ORDER BY RANDOM() LIMIT 1", (eng,)).fetchone()
        if not r:
            r = db.execute(
                "SELECT path, songlength_s FROM sids WHERE engine = ? "
                "LIMIT 1", (eng,)).fetchone()
        if r:
            tail_samples.append((eng, r[0], r[1]))

    # 2. Deep tail — engines beyond rank 200 (just one random each, 100 of them)
    deep_engines = db.execute(
        "SELECT engine FROM sids WHERE engine IS NOT NULL "
        "GROUP BY engine ORDER BY COUNT(*) DESC LIMIT 1000 OFFSET 200"
    ).fetchall()
    deep_engines = [e[0] for e in deep_engines]
    random.shuffle(deep_engines)
    deep_samples = []
    for eng in deep_engines[:100]:
        r = db.execute(
            "SELECT path, songlength_s FROM sids WHERE engine = ? "
            "ORDER BY RANDOM() LIMIT 1", (eng,)).fetchone()
        if r:
            deep_samples.append((eng, r[0], r[1]))

    # 3. Unclassified — 200 random
    unclass = db.execute(
        "SELECT path, songlength_s FROM sids WHERE engine IS NULL "
        "AND songlength_s > 30 "
        "ORDER BY RANDOM() LIMIT 200").fetchall()
    unclass_samples = [('<unclassified>', p, s) for p, s in unclass]

    survey(tail_samples, 'LONG TAIL (engine ranks 101-200)')
    survey(deep_samples, 'DEEP TAIL (engine ranks 201-1000, random sample)')
    survey(unclass_samples, 'UNCLASSIFIED (sidid had no fingerprint, random sample)')


if __name__ == '__main__':
    main()
