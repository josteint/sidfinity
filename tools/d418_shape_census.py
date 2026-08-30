#!/usr/bin/env python3
"""d418_shape_census.py — how does the ORIGINAL drive $D418?

READ-ONLY measurement. Builds nothing, stamps no verdict, touches no stored
artifact — so it is immune to any pending key-definition change.

WHY: 47% of the DMC v5 verify-partials (404 of 853 clustered, 2026-08-30)
share one first-divergence signature — the original writes a voice register
where OUR rebuild writes $D418. Our composer emits $D418 per filter
note-init; several originals do not, and DMC v4 already carries a family of
C19 wedge knobs for exactly that (`master_vol_static`, `d418_noteinit_dead`,
`d418_play_wrapper`, `filter_static`). This measures which shape each
original actually has, so the residue can be attacked by class instead of
member by member.

The classification is deliberately made from the ORIGINAL alone: it needs no
build, so it cannot be skewed by a member our composer currently refuses, and
one bad member cannot take the sweep down.

  static    total $D418 <= 2 and all of them in the first frame
            -> the C19 36th shape: set once at init, never during play.
            TELL from the ledger: "orig's TOTAL $D418 count ~2 vs the
            rebuild's hundreds".
  sparse    writes $D418, but at < 0.25 per play() — far below a
            per-note-init rate; a fade, or an occasional re-assert.
  perplay   >= 0.9 per play() and low distinct values -> the $D418-every-play
            wrapper shape.
  dense     otherwise: genuinely per-note-init, i.e. what our composer
            already does. These members' divergence is NOT a $D418 shape and
            should be triaged elsewhere.
  silent    no $D418 write at all after init.

Usage:
    python3 tools/d418_shape_census.py --results tmp/dmc_v5_r3_results.jsonl
    ... --status partial        which rows to measure (default partial)
    ... --limit N               stop after N members (smoke test)
    ... --out tmp/d418_census.jsonl
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.batch_results import load_latest_rows          # noqa: E402
from src.jobs import default_jobs                        # noqa: E402
from src.tslog import phase, ts                          # noqa: E402

HVSC = os.path.join(ROOT, 'hvsc85')


def _duration(sid_path: str, sub: int) -> float:
    """The ratified verify window (songlength x 1.1), capped for the census.

    A census does not need the whole song: the $D418 RATE is stable, and the
    cap keeps one 10-minute member from dominating the sweep. This cap is a
    census convenience and must never be copied into a verdict path — that is
    ledger C20's eighth layer.
    """
    try:
        from src import songlengths
        db = songlengths.load_database(None)
        d = songlengths.get_durations(sid_path, db)
        if d and sub < len(d) and d[sub]:
            return min(float(d[sub]) * 1.1, 90.0)
    except Exception:
        pass
    return 45.0


def measure(item):
    rel, sub = item
    sid = os.path.join(HVSC, rel)
    try:
        from pipelines.hubbard.verify_cycle import writelog_capture
        frames = writelog_capture(sid, subtune=sub, duration=_duration(sid, sub))
        if not frames:
            return {'path': rel, 'sub': sub, 'shape': 'nocapture'}

        n_frames = len(frames)
        vals, per_frame, first_frame_only = collections.Counter(), 0, True
        # A Frame IS its write list: [(cycle, reg, val), ...] with `reg` a
        # 0-based chip offset, so $D418 is 0x18 (and 0x38/0x58 on a 2nd/3rd
        # chip — masking catches those too, which is what we want).
        for i, fr in enumerate(frames):
            hits = [w for w in fr if (w[1] & 0x1F) == 0x18]
            if hits:
                per_frame += len(hits)
                if i > 0:
                    first_frame_only = False
                for w in hits:
                    vals[w[2]] += 1

        total = per_frame
        rate = total / max(1, n_frames)
        if total == 0:
            shape = 'silent'
        elif total <= 2 and first_frame_only:
            shape = 'static'
        elif rate >= 0.9 and len(vals) <= 2:
            shape = 'perplay'
        elif rate < 0.25:
            shape = 'sparse'
        else:
            shape = 'dense'

        return {'path': rel, 'sub': sub, 'shape': shape, 'total_d418': total,
                'frames': n_frames, 'rate': round(rate, 4),
                'distinct_values': len(vals),
                'top_values': [f'${v:02X}x{n}' for v, n in vals.most_common(4)],
                'init_only': first_frame_only}
    except Exception as e:
        return {'path': rel, 'sub': sub, 'shape': 'error',
                'err': f'{type(e).__name__}: {e}'[:140]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', required=True)
    ap.add_argument('--status', default='partial')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--out', default='tmp/d418_shape_census.jsonl')
    a = ap.parse_args()

    rows = load_latest_rows(a.results)
    todo = []
    for r in rows:
        if str(r.get('status', '')).lower() != a.status:
            continue
        p = r.get('path') or r.get('rel')
        if not p or not os.path.exists(os.path.join(HVSC, p)):
            continue
        fd = r.get('flat_div') or []
        sub = r.get('subtune') or (fd[0] if fd and isinstance(fd[0], int) else 0)
        todo.append((p, int(sub) if isinstance(sub, int) else 0))
    if a.limit:
        todo = todo[:a.limit]

    out = os.path.join(ROOT, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tally = collections.Counter()
    with phase(f'$D418 shape census: {len(todo)} {a.status} members '
               f'from {os.path.basename(a.results)}'):
        with open(out, 'w') as f, Pool(default_jobs()) as pool:
            for i, res in enumerate(pool.imap_unordered(measure, todo, 8), 1):
                f.write(json.dumps(res) + '\n')
                f.flush()
                tally[res['shape']] += 1
                if i % 25 == 0 or i == len(todo):
                    ts(f'  {i}/{len(todo)}  ' +
                       '  '.join(f'{k}={v}' for k, v in sorted(tally.items())))

    print()
    print('=' * 70)
    print(f'$D418 SHAPE OF THE ORIGINAL — {len(todo)} {a.status} members')
    print('=' * 70)
    for shape, n in tally.most_common():
        print(f'  {shape:10s} {n:5d}  ({100*n/max(1,len(todo)):4.1f}%)')
    print()
    print('  static/perplay/sparse/silent = the original does NOT drive $D418')
    print('  per note-init as our composer does -> a C19 $D418 wedge class.')
    print('  dense = same shape as ours; triage those elsewhere.')
    print(f'\n  rows: {out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
