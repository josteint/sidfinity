#!/usr/bin/env python3
"""derive_deps.py — MEASURE each engine's real build+verify dependency set.

Writes `tools/engine_deps.json` = {engine: {consumer: [repo-relative files]}},
which `src/code_fingerprint` prefers over its hand-declared `DEPS`.

=== WHY ===
Hand-declaring dependencies and not enforcing them is the one combination
nobody ships. On 2026-08-22 the declared sets were measured wrong in BOTH
directions at once:

  * 18 declared-but-unused files (all of dmc/v5 and dmc/v6 inside the `dmc_v4`
    set) — a PRECISION failure. Costs compute; one v5 edit invalidated all
    8,369 v4 verdicts. Cannot produce a wrong answer.
  * 42 USED-but-undeclared files — an INCLUSIVENESS failure, which CAN. Among
    them `src/composer_runtime/{xa65,psid}.py` (they emit the bytes),
    `src/songlengths.py` (the verify window), `tools/seed_disassembly.py`, the
    py65 interpreter that runs extraction probes, and `lark` itself.

A `sys.modules` snapshot after real work captures function-local imports by
construction, which a static import walk cannot.

=== THE TRAP THIS TOOL IS BUILT AROUND ===
A closure measured on ONE member UNDER-APPROXIMATES, and under-approximating is
the unsafe direction. A family's members take different build paths — DMC f1
alone dispatches single / compilation / multisid / hetero_v5 / hetero_masm /
medley — and each pulls different modules. So the sample is STRATIFIED over the
recorded `build_path` (every distinct path, twice) plus a random remainder, and
the result is the UNION over all of them, each measured in its own clean
subprocess.

Two further guards live in `code_fingerprint` itself: `_ALWAYS` is unioned into
every fingerprint regardless of what was derived, and `check_derived_closure()`
lets a batch assert at runtime that it loaded nothing outside the stored set.

=== USAGE ===
    python3 tools/derive_deps.py                     # every wired consumer
    python3 tools/derive_deps.py --engine dmc_v4     # one engine
    python3 tools/derive_deps.py --per-path 2 --random 6
    python3 tools/derive_deps.py --dry-run           # measure, print, no write

⚠ Re-run whenever a build path is added, or a consumer grows an import that a
sampled member does not exercise. `check_derived_closure` reports the miss
loudly rather than silently reusing a stale verdict, but re-deriving is the fix.
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.jobs import default_jobs           # noqa: E402
from src.tslog import ts, phase             # noqa: E402
from src.batch_results import load_latest    # noqa: E402

OUT_PATH = os.path.join(ROOT, 'tools', 'engine_deps.json')

from src.batch_results import stores_for_engine  # noqa: E402


def _stores(engine: str) -> list:
    """The engine's results files, from the ONE registry (src/batch_results).

    These were hardcoded per consumer and drifted — this table still named
    `tmp/dmc_v5_merged.jsonl`, a historical snapshot, as v5's live store.
    """
    return [s.rel for s in stores_for_engine(engine)]


# One entry per consumer that STAMPS or CHECKS a code_hash. `arg` turns a
# results row into the per-member argument that consumer's function takes.
CONSUMERS = {
    'dmc_v4': {
        'consumer': 'dmc_family_batch',
        'module': 'pipelines.dmc.family_batch', 'fn': 'run_member',
        'results': _stores('dmc_v4'),
        'path_key': 'path',
        'arg': lambda r: r['path'],
    },
    'dmc_v5': {
        'consumer': 'dmc_v5_family_batch',
        'module': 'pipelines.dmc.v5.family_batch', 'fn': 'run_member',
        'results': _stores('dmc_v5'),
        'path_key': 'path',
        'arg': lambda r: r['path'],
    },
    'fc_standard': {
        'consumer': 'fc_family_batch',
        'module': 'pipelines.future_composer.family_batch', 'fn': 'run',
        'results': _stores('fc_standard'),
        'path_key': 'sid',
        'arg': lambda r: r['sid'],
    },
    'music_assembler': {
        'consumer': 'masm_family_batch',
        'module': 'pipelines.music_assembler.family_batch', 'fn': 'run',
        'results': _stores('music_assembler'),
        'path_key': 'sid',
        'arg': lambda r: r['sid'],
    },
    'goattracker_v1': {
        'consumer': 'goattracker_v1_family_batch',
        'module': 'pipelines.goattracker.v1.family_batch', 'fn': 'run_member',
        'results': _stores('goattracker_v1'),
        'path_key': 'path',
        'arg': lambda r: [r['path'], r.get('songlength') or 0],
    },
    'basic_program': {
        'consumer': 'basic_program_batch',
        'module': 'pipelines.basic_program.family_batch', 'fn': 'process',
        'results': _stores('basic_program'),
        'path_key': 'path',
        'arg': lambda r: [r['path'], r.get('songlength') or 10, False],
    },
}

# Runs ONE member in a clean interpreter and prints the repo files that ended
# up in sys.modules, together with the member's own verdict status.
#
# ⚠ `_worker_init()` MUST run first where a consumer has one. The batch pools
# call it per worker to load the songlength database into a module global;
# without it `run_member` raises on its first use and returns in ~0.3s having
# loaded only the import-time modules. That produced a plausible, uniform,
# SILENTLY TOO-NARROW closure on the first run of this tool — exactly the
# under-approximation it exists to prevent. The status is reported back so a
# member that never reached a verdict is visible rather than averaged in.
_CHILD = r'''
import sys, os, json, importlib
ROOT = %(root)r
sys.path[:0] = [os.path.join(ROOT,'tools','py65_lib'), os.path.join(ROOT,'tools'),
                os.path.join(ROOT,'src'), ROOT]
os.chdir(ROOT)
mod = importlib.import_module(%(module)r)
if hasattr(mod, '_worker_init'):
    mod._worker_init()
fn = getattr(mod, %(fn)r)
arg = json.loads(%(arg)r)
if isinstance(arg, list):
    arg = tuple(arg)
status = 'raised'
try:
    r = fn(arg)
    status = (r or {}).get('status', 'none') if isinstance(r, dict) else 'ok'
except BaseException as e:
    sys.stderr.write('member raised %%s: %%s\n' %% (type(e).__name__, e))
from src.code_fingerprint import repo_modules_loaded
sys.stdout.write('@@DEPS@@' + json.dumps(
    {'status': status, 'files': sorted(repo_modules_loaded())}))
'''

# A member reaching one of these exercised the whole path through to a verdict.
# Anything else (unsupported / detect_fail / build_fail / raised) bailed early
# and loaded only part of the closure. Compared case-insensitively: the
# families do not agree on case (basic_program returns 'FULL', DMC 'full'), and
# a case mismatch made every basic_program member read as "reached nothing".
_REACHED_VERDICT = {'full', 'partial', 'ok', 'length_fail', 'none'}


def _sample(spec, per_path: int, n_random: int, seed: int) -> list:
    """Members stratified over the recorded build_path, plus a random tail."""
    rows = {}
    for rel in spec['results']:
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            rows.update(load_latest(p, path_key=spec['path_key']))
    if not rows:
        return []
    by_path: dict = {}
    for r in rows.values():
        by_path.setdefault(r.get('build_path'), []).append(r)
    rnd = random.Random(seed)
    picked, seen = [], set()

    def take(r):
        k = r[spec['path_key']]
        if k not in seen:
            seen.add(k)
            picked.append(r)

    # Every distinct build path, `per_path` members each — prefer FULL members
    # (they exercise the whole path through to a verdict).
    for bp, group in sorted(by_path.items(), key=lambda kv: str(kv[0])):
        full = [r for r in group if r.get('status') == 'full'] or group
        for r in rnd.sample(full, min(per_path, len(full))):
            take(r)
    # ... plus a random stratum over everything, which is the only mitigation
    # for a build path nobody recorded.
    allrows = list(rows.values())
    for r in rnd.sample(allrows, min(n_random, len(allrows))):
        take(r)
    return picked


def _run_one(spec, arg) -> tuple[set, str]:
    code = _CHILD % {'root': ROOT, 'module': spec['module'],
                     'fn': spec['fn'], 'arg': json.dumps(arg)}
    try:
        p = subprocess.run([sys.executable, '-c', code], capture_output=True,
                           text=True, timeout=1800, cwd=ROOT)
    except subprocess.TimeoutExpired:
        ts(f'  TIMEOUT on {arg}')
        return set(), 'timeout'
    tag = '@@DEPS@@'
    i = p.stdout.find(tag)
    if i < 0:
        ts(f'  NO RESULT for {arg}: {p.stderr.strip()[-300:]}')
        return set(), 'no-result'
    got = json.loads(p.stdout[i + len(tag):])
    return set(got['files']), got['status']


def derive(engine: str, per_path: int, n_random: int, seed: int) -> dict | None:
    spec = CONSUMERS[engine]
    members = _sample(spec, per_path, n_random, seed)
    if not members:
        ts(f'{engine}: no results file to sample from — SKIPPED')
        return None
    paths = [spec['arg'](r) for r in members]
    bps = sorted({str(r.get('build_path')) for r in members})
    with phase(f'{engine}/{spec["consumer"]}: {len(paths)} members '
               f'over build paths {bps}'):
        union: set = set()
        per_member, reached = {}, 0
        with ThreadPoolExecutor(max_workers=min(default_jobs(), len(paths))) as ex:
            futs = {ex.submit(_run_one, spec, a): a for a in paths}
            for f, a in futs.items():
                got, status = f.result()
                key = a if isinstance(a, str) else a[0]
                per_member[key] = {'n': len(got), 'status': status}
                union |= got
                reached += status.lower() in _REACHED_VERDICT
                mark = ' ' if status.lower() in _REACHED_VERDICT else '!'
                ts(f' {mark}{key[:56]:56s} {len(got):3d} modules '
                   f'[{status}] (union {len(union)})')
        if not reached:
            ts(f'  ⚠ {engine}: NO sampled member reached a verdict — the '
               f'closure is import-time only and MUST NOT be stored')
            return None
        if reached < len(paths):
            ts(f'  ⚠ {engine}: only {reached}/{len(paths)} members reached a '
               f'verdict; the rest contributed a partial closure')
    return {'consumer': spec['consumer'], 'files': sorted(union),
            'sampled': [a if isinstance(a, str) else a[0] for a in paths],
            'reached_verdict': reached, 'per_member': per_member}


def check(engines, per_path: int, n_random: int, seed: int) -> int:
    """Pre-flight audit: does anything escape the STORED dependency set?

    Azure TIA's "safe fallback" property, arranged so it costs nothing. The
    obvious implementation — have each batch call `check_derived_closure()`
    after its first member — puts the call site INSIDE that family's own
    dependency closure, so adding it changes the fingerprint and invalidates
    every verdict the batch was about to reuse. Enforcement that destroys the
    cache it protects is not enforcement.

    So it runs OUTSIDE instead: same stratified sample, same clean
    subprocesses, compared against the stored set. Run it before a batch (or
    after any change that might have added an import); a non-empty result means
    the stored set under-approximates and every row stamped under it is
    suspect, which is the loud failure the property asks for.
    """
    from src.code_fingerprint import _derived, _ALWAYS, _iter_files, \
        _KEY_MANAGEMENT, ROOT as CF_ROOT
    bad = 0
    for eng in engines:
        spec = CONSUMERS[eng]
        stored = (_derived().get(eng, {}) or {}).get(spec['consumer'])
        if stored is None:
            ts(f'{eng}: no derived set stored — declared fallback in force '
               f'(over-broad, therefore safe); nothing to audit')
            continue
        covered = set(_KEY_MANAGEMENT)
        for rel in set(stored) | set(_ALWAYS):
            for f in _iter_files(CF_ROOT / rel):
                covered.add(f.relative_to(CF_ROOT).as_posix())
        got = derive(eng, per_path, n_random, seed)
        if got is None:
            ts(f'{eng}: could not measure — treat as UNAUDITED')
            bad += 1
            continue
        escapees = sorted(set(got['files']) - covered)
        if escapees:
            bad += 1
            ts(f'  ⚠ {eng}: {len(escapees)} MODULES ESCAPE THE STORED SET — '
               f'every row stamped under it is suspect. Re-derive.')
            for f in escapees[:20]:
                ts(f'      + {f}')
        else:
            ts(f'  {eng}: clean ({len(got["files"])} modules, all inside the '
               f'stored set)')
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', action='append',
                    help='engine key (repeatable); default = all wired')
    ap.add_argument('--per-path', type=int, default=2,
                    help='members per distinct build_path (default 2)')
    ap.add_argument('--random', type=int, default=6,
                    help='extra random members (default 6)')
    ap.add_argument('--seed', type=int, default=20260822)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--check', action='store_true',
                    help='PRE-FLIGHT AUDIT: re-measure and report modules that '
                         'escape the STORED set, without writing. Exit 1 on any '
                         'escapee. Run before a batch, not inside one.')
    a = ap.parse_args()

    if a.check:
        return check(a.engine or list(CONSUMERS), a.per_path, a.random, a.seed)

    engines = a.engine or list(CONSUMERS)
    existing = {}
    if os.path.exists(OUT_PATH):
        existing = json.load(open(OUT_PATH))

    for eng in engines:
        got = derive(eng, a.per_path, a.random, a.seed)
        if got is None:
            continue
        prev = (existing.get(eng) or {}).get(got['consumer'])
        if prev is not None:
            added = sorted(set(got['files']) - set(prev))
            dropped = sorted(set(prev) - set(got['files']))
            ts(f'{eng}: vs stored  +{len(added)} -{len(dropped)}')
            for f in added[:12]:
                ts(f'    + {f}')
            for f in dropped[:12]:
                ts(f'    - {f}')
        existing.setdefault(eng, {})[got['consumer']] = got['files']
        existing.setdefault('_meta', {})[eng] = {
            'consumer': got['consumer'], 'sampled': got['sampled'],
            'per_member': got['per_member'],
            'reached_verdict': got['reached_verdict'],
        }

    if a.dry_run:
        ts('--dry-run: not writing')
        return
    with open(OUT_PATH, 'w') as f:
        json.dump(existing, f, indent=1, sort_keys=True)
    ts(f'wrote {OUT_PATH}')


if __name__ == '__main__':
    main()
