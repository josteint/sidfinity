#!/usr/bin/env python3
"""write_timing_sweep.py — run `write_timing_delta` over the stored corpus
and rank members by how far their rebuild's within-frame write timing
departs from the original's.

The pair set is every `*.sidfinity.sid` beside its HVSC original.  That set
IS the FULL set: `src/corpus_sync` deletes the artifact of any member that
is not FULL (ledger C20's orphan rule), so a stored rebuild is a member the
Mode-1 (or Mode-2) verdict passed.

Output: one JSON row per (member, subtune) to `--out`, plus a ranked
summary.  The ranking key is `spread_p99` — how far, at the 99th
percentile, a write moved WITHIN its play() burst relative to the burst
start.  That is the quantity the core tenet's Trap B declares inaudible.

    python3 tools/write_timing_sweep.py --sample 400
    python3 tools/write_timing_sweep.py            # the whole corpus

⚠ Read-only.  Nothing here builds, writes an artifact, or touches a verdict
store.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.tslog import ts, phase           # noqa: E402
from src.jobs import default_jobs         # noqa: E402
from tools.write_timing_delta import compare, PAL_FRAME_CYCLES   # noqa: E402

HVSC = os.path.join(ROOT, 'hvsc85')


def pairs() -> list:
    """Every (orig, rebuild) pair in the stored corpus, as HVSC-relative
    paths."""
    out = []
    for dirpath, _dirs, files in os.walk(HVSC):
        for f in files:
            if not f.endswith('.sidfinity.sid'):
                continue
            orig = os.path.join(dirpath, f[:-len('.sidfinity.sid')] + '.sid')
            if os.path.exists(orig):
                out.append((os.path.relpath(orig, ROOT),
                            os.path.relpath(os.path.join(dirpath, f), ROOT)))
    out.sort()
    return out


def engine_map(rels: list) -> dict:
    """HVSC-relative path -> sidid engine string, from the catalogue."""
    try:
        from src import sid_db
        rows = sid_db.query("SELECT path, engine FROM sids")
    except Exception as e:                       # catalogue optional
        ts(f'engine map unavailable ({e}); families will read "?"')
        return {}
    m = {p: (e or '?') for p, e in rows}
    return {r: m.get(r[len('hvsc85/'):], '?') for r in rels}


def _one(job):
    orig, rebuild, subtune, duration = job
    try:
        res = compare(os.path.join(ROOT, orig), os.path.join(ROOT, rebuild),
                      subtune, duration)
        res['ok'] = True
        return res
    except Exception as e:
        return {'ok': False, 'orig': orig, 'rebuild': rebuild,
                'subtune': subtune, 'error': f'{type(e).__name__}: {e}'}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='tmp/write_timing_sweep.jsonl')
    ap.add_argument('--sample', type=int, default=0,
                    help='measure only N randomly chosen members (0 = all)')
    ap.add_argument('--seed', type=int, default=20260901)
    ap.add_argument('--subtune', type=int, default=0)
    ap.add_argument('--duration', type=float, default=15.0)
    ap.add_argument('--jobs', type=int, default=0)
    ap.add_argument('--resume', action='store_true',
                    help='skip members already present in --out')
    a = ap.parse_args()

    with phase('enumerating stored (orig, rebuild) pairs'):
        ps = pairs()
    ts(f'{len(ps)} stored rebuilds found')

    if a.sample and a.sample < len(ps):
        random.Random(a.seed).shuffle(ps)
        ps = sorted(ps[:a.sample])
        ts(f'sampling {len(ps)} of them (seed {a.seed})')

    done = set()
    out_path = os.path.join(ROOT, a.out)
    if a.resume and os.path.exists(out_path):
        with open(out_path) as fh:
            for line in fh:
                try:
                    done.add(json.loads(line)['orig'])
                except Exception:
                    pass
        ps = [p for p in ps if p[0] not in done]
        ts(f'{len(done)} already measured; {len(ps)} to go')

    jobs = a.jobs or default_jobs('WRITE_TIMING_JOBS', cap=max(1, len(ps)))
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    results = []
    with phase(f'measuring {len(ps)} members x2 captures of {a.duration}s '
               f'({jobs} workers)'):
        with open(out_path, 'a') as fh, \
                ProcessPoolExecutor(max_workers=jobs) as ex:
            futs = [ex.submit(_one, (o, r, a.subtune, a.duration))
                    for o, r in ps]
            for k, fut in enumerate(as_completed(futs), 1):
                res = fut.result()
                fh.write(json.dumps(res) + '\n')
                fh.flush()
                results.append(res)
                if k % 200 == 0:
                    ts(f'  {k}/{len(ps)}')

    report(out_path)
    return 0


def report(out_path: str, top: int = 25) -> None:
    rows = []
    with open(out_path) as fh:
        for line in fh:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    good = [r for r in rows if r.get('ok') and r.get('plays_compared', 0) >= 20]
    bad = [r for r in rows if not r.get('ok')]
    thin = [r for r in rows if r.get('ok') and r.get('plays_compared', 0) < 20]
    ts(f'{len(good)} measured, {len(thin)} too-few-plays, {len(bad)} errored')
    if not good:
        return

    em = engine_map([r['orig'] for r in good])
    for r in good:
        r['engine'] = em.get(r['orig'], '?')

    import statistics as st

    def pct(xs, q):
        s = sorted(xs)
        return s[min(len(s) - 1, int(round(q * (len(s) - 1))))]

    sp = [r['spread_p99'] for r in good]
    ji = [r['jitter_p99'] for r in good]
    mm = [r for r in good if r['plays_content_mismatch'] > 0]

    print()
    print('=== CORPUS-WIDE within-play write-timing delta '
          f'({len(good)} FULL members) ===')
    print(f"  spread p99 per member: median {st.median(sp):.0f} cyc "
          f"({st.median(sp) / PAL_FRAME_CYCLES * 100:.2f}% of a frame), "
          f"p90 {pct(sp, .90):.0f}, p99 {pct(sp, .99):.0f}, "
          f"max {max(sp):.0f}")
    print(f"  jitter p99 per member: median {st.median(ji):.0f} cyc, "
          f"p90 {pct(ji, .90):.0f}, max {max(ji):.0f}")
    print(f"  members with ANY per-play content mismatch: {len(mm)}")

    by_eng = {}
    for r in good:
        by_eng.setdefault(r['engine'], []).append(r['spread_p99'])
    print('\n  by engine (median spread p99, cycles):')
    for eng, xs in sorted(by_eng.items(), key=lambda kv: -st.median(kv[1])):
        if len(xs) < 3:
            continue
        print(f"    {eng:<28} n={len(xs):<5} median {st.median(xs):7.0f}  "
              f"max {max(xs):7.0f}")

    print(f'\n=== WORST {top} BY spread_p99 (candidates for a listening '
          f'test) ===')
    for r in sorted(good, key=lambda r: -r['spread_p99'])[:top]:
        print(f"  {r['spread_p99']:7.0f} cyc "
              f"({r['spread_p99'] / PAL_FRAME_CYCLES * 100:5.2f}% frame)  "
              f"burst o/r {r['burst_orig_p50']:.0f}/"
              f"{r['burst_rebuild_p50']:.0f}  {r['engine']:<20} "
              f"{r['orig']} sub {r['subtune']}")


if __name__ == '__main__':
    raise SystemExit(main())
