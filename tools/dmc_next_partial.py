#!/usr/bin/env python3
"""Locate the next DMC family-1 partial to work on — fast + self-healing.

The work queue is a HINT list, tmp/dmc_f1_partials.jsonl (one {"path","status"}
per line, path-sorted). It is NOT ground truth (a fresh family batch is) — a
prior fix may have flipped its target OR a whole cluster, so the list goes
stale. This tool RE-CONFIRMS the leading `partial` entries (in path order, in
parallel) against the CURRENT code, rewrites their status, and stops at the
first member that is still partial — printing its first divergence so you can
start root-causing immediately.

Because it re-confirms, it makes NO assumption that the target is adjacent to
last session's fix, and it self-heals cluster flips: any leading member an
earlier fix already flipped to FULL is confirmed and skipped.

It is fix-AGNOSTIC — it only verifies + localizes; it never touches a fix.

Usage:
    python3 tools/dmc_next_partial.py               # find + localize next partial
    python3 tools/dmc_next_partial.py --window 8    # confirm 8 in parallel per pass
    python3 tools/dmc_next_partial.py --list PATH    # custom queue file
Confirmation uses the SAME verdict as the family batch (dmc_build_one --verify).
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from src.jobs import default_jobs  # noqa: E402

DEFAULT_LIST = os.path.join(ROOT, 'tmp', 'dmc_f1_partials.jsonl')


def _confirm(path: str) -> tuple[str, str, str]:
    """Build + verify + localize one member. Returns (path, status, localize),
    status in {'full','partial','error'}."""
    r = subprocess.run(
        [sys.executable, os.path.join(ROOT, 'tools', 'dmc_build_one.py'),
         path, '--verify', '--localize'],
        capture_output=True, text=True, cwd=ROOT)
    out = r.stdout + r.stderr
    verdict = None
    for line in out.splitlines():
        if line.startswith('VERDICT:'):
            verdict = line.split(':', 1)[1].strip().lower()
    if verdict == 'full':
        return path, 'full', ''
    if verdict == 'partial':
        lines = out.splitlines()
        # per-subtune verdict lines ("  sub N: partial ...") name the failing
        # subtune — the FIRST DIVERGENCE block is for --subtune 0 only, so for a
        # multi-subtune member whose diff is in sub N>0 the block is empty and we
        # point at the right --subtune to localize.
        subs = [ln.strip() for ln in lines if ln.strip().startswith('sub ')]
        bad = [s for s in subs if 'partial' in s]
        blk = []
        for i, ln in enumerate(lines):
            if 'FIRST DIVERGENCE' in ln:
                for ln2 in lines[i:]:
                    if ln2.startswith('built ') or ln2.startswith('VERDICT:'):
                        break
                    blk.append(ln2)
                break
        parts = []
        if bad:
            parts.append('failing subtune(s): ' + ' | '.join(bad))
        if blk:
            parts.append('\n'.join(blk).rstrip())
        elif bad:
            sub_n = bad[0].split(':', 1)[0].replace('sub', '').strip()
            parts.append(f'(divergence is in subtune {sub_n}, not 0 — localize with '
                         f'--subtune {sub_n})')
        return path, 'partial', '\n\n'.join(parts)
    return path, 'error', out.strip().splitlines()[-1] if out.strip() else ''


def _preflight() -> None:
    """Refuse to run on a broken environment.

    Without `source src/env.sh` the .pylocal path is missing and EVERY member
    fails `dmc_build_one` with ModuleNotFoundError. Those were recorded as
    per-member 'error' rows and saved — rewriting the whole 149-member hint
    queue to 'error' in one pass and destroying it (2026-07-23). An environment
    failure is not evidence about any member."""
    try:
        import lark  # noqa: F401
    except ModuleNotFoundError as e:
        raise SystemExit(
            f'environment not set up ({e}) — run `source src/env.sh` first '
            '(it puts .pylocal + src on PYTHONPATH).')


def _seed_batch() -> str | None:
    """The NEWEST f1 batch results file to seed the queue from.

    Was pinned to one filename, which silently rotted: each round writes its
    own `tmp/dmc_f1_r<N>.jsonl`, so the pinned file aged out and a re-seed
    handed the tool a round-53-era partial list. Every stale hint costs a full
    build+verify before the self-heal drops it, so "it converges eventually"
    is not good enough. Pick by mtime instead."""
    import glob
    cands = glob.glob(os.path.join(ROOT, 'tmp', 'dmc_f1_*.jsonl'))
    cands = [c for c in cands if not c.endswith('dmc_f1_partials.jsonl')]
    return max(cands, key=os.path.getmtime) if cands else None


def _load(list_path: str) -> list[dict]:
    if not os.path.exists(list_path):
        # Auto-seed from the last family batch (tmp/ may have been wiped). All
        # batch-partials start 'partial'; the tool re-confirms + self-heals as
        # it runs, so a stale seed only costs the first pass a few extra
        # verifies.
        SEED_BATCH = _seed_batch()
        if SEED_BATCH is None or not os.path.exists(SEED_BATCH):
            raise SystemExit(f'No queue at {list_path} and no f1 batch results '
                             f'in tmp/ — run a family batch first.')
        print(f'(seeding from the newest f1 batch: '
              f'{os.path.relpath(SEED_BATCH, ROOT)})')
        # Append-only jsonl -> dedupe LAST-WINS (src/batch_results). Without it
        # a member that WAS partial and is now full is seeded as partial; the
        # re-confirm below heals that, but only after paying a build+verify for
        # each stale hint.
        from batch_results import load_latest
        parts = sorted(p for p, r in load_latest(SEED_BATCH).items()
                       if r.get('status') == 'partial')
        _save(list_path, [{'path': p, 'status': 'partial'} for p in parts])
        print(f'(auto-seeded {len(parts)} partials into {list_path} from the '
              f'batch — statuses will self-heal as the tool re-confirms)')
    return [json.loads(l) for l in open(list_path) if l.strip()]


def _save(list_path: str, rows: list[dict]) -> None:
    rows = sorted(rows, key=lambda r: r['path'])
    tmp = list_path + '.tmp'
    with open(tmp, 'w') as f:
        for r in rows:
            f.write(json.dumps(r) + '\n')
    os.replace(tmp, list_path)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--list', default=DEFAULT_LIST)
    ap.add_argument('--window', type=int, default=6,
                    help='partials to re-confirm in parallel per pass')
    args = ap.parse_args()

    _preflight()
    rows = _load(args.list)
    by_path = {r['path']: r for r in rows}
    queue = [r['path'] for r in sorted(rows, key=lambda r: r['path'])
             if r['status'] == 'partial']
    if not queue:
        print('No partials left in the queue — re-seed from a fresh batch.')
        return 0

    target = None
    idx = 0
    flipped = 0
    while idx < len(queue) and target is None:
        window = queue[idx:idx + args.window]
        with ThreadPoolExecutor(
                max_workers=default_jobs(cap=len(window))) as ex:
            results = {p: (s, loc) for p, s, loc in ex.map(_confirm, window)}
        if all(results[p][0] == 'error' for p in window):
            # Systemic failure (broken env, missing tool, corrupt seed), not N
            # independent per-member build errors. Saving would overwrite real
            # 'partial' hints with 'error' and destroy the queue.
            for p in window:
                print(f'  ERROR building {p}: {results[p][1]}')
            raise SystemExit(
                f'every member in the window ({len(window)}) failed to build — '
                'treating as a systemic failure; queue NOT modified.')
        for p in window:                       # strict path order within window
            s, loc = results[p]
            by_path[p]['status'] = s
            if s == 'full':
                flipped += 1
                print(f'  confirmed FULL (stale hint): {p}')
            elif s == 'error':
                print(f'  ERROR building {p}: {loc}')
            elif s == 'partial' and target is None:
                target = (p, loc)
        idx += args.window
    _save(args.list, list(by_path.values()))

    if flipped:
        print(f'  ({flipped} leading hint(s) had already flipped FULL — list updated)\n')
    if target is None:
        print('No still-partial member found in the queue — re-seed from a fresh batch.')
        return 0
    path, loc = target
    print(f'\n=== NEXT PARTIAL (first by hvsc path): {path} ===\n')
    print(loc if loc else '(no divergence block captured — run '
          f'dmc_build_one.py "{path}" --verify --localize)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
