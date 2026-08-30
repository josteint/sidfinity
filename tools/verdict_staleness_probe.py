#!/usr/bin/env python3
"""Is a family's verdict staleness REAL or merely NOMINAL? — READ-ONLY.

`code_fingerprint` must assume any change to a closure file moved the build:
it hashes content, it cannot know semantics. That is the correct default (a
PRECISION failure costs compute; the other direction is silently wrong). But
it means a byte-neutral edit — a schema addition elided at its default, a
directory move with path fixups — marks whole families stale and appears to
demand hours of re-batching.

This measures whether it actually did, the CLAUDE.md carrier-refactor way:
rebuild a stratified sample FROM THE STORED .usf under CURRENT code and
compare to the stored .sid. Byte-identical => identical write stream =>
identical verdict, which is a STRONGER statement than re-verification and
~100x cheaper.

    python3 tools/verdict_staleness_probe.py [engine ...]
    PER_BUCKET=60 python3 tools/verdict_staleness_probe.py dmc_v4

Stratified over `build_path`, because a family that dispatches several build
paths can be unchanged on one and broken on another (ledger C20 fourth layer).

⚠ It proves nothing about members with NO stored artifact (non-FULL ones) —
those get re-verified regardless. And a family with no mass-write has nothing
to compare: music_assembler / goattracker_v1 today.

Born 2026-08-30 (backlog item 31): 311/311 byte-identical across dmc_v4's
seven build paths + dmc_v5 + fc_standard proved the digi schema landing had
moved nothing — and the same run caught digi_organizer at 0/39, a genuinely
broken stored corpus (backlog item 34).
"""
from __future__ import annotations

import os
import random
import sys
from collections import defaultdict
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'src'), os.path.join(ROOT, 'tools')]

from src.batch_results import load_latest, stores_for_engine   # noqa: E402
from src.jobs import default_jobs                              # noqa: E402
from src.tslog import ts, phase                                # noqa: E402

HVSC = os.path.join(ROOT, 'hvsc85')
PER_BUCKET = int(os.environ.get('PER_BUCKET', '6'))


def sample_for(engine: str) -> list[tuple[str, str]]:
    """(rel, build_path) for FULL members that have stored artifacts,
    stratified over build_path."""
    out = []
    for s in stores_for_engine(engine):
        p = os.path.join(ROOT, s.rel)
        if not os.path.exists(p):
            continue
        rows = load_latest(p, path_key=s.id_key)
        by_bp = defaultdict(list)
        for rel, r in rows.items():
            if r.get('status') != 'full':
                continue
            base = os.path.splitext(os.path.join(HVSC, rel))[0]
            if not (os.path.exists(base + '.usf')
                    and os.path.exists(base + '.sidfinity.sid')):
                continue
            by_bp[r.get('build_path', '?')].append(rel)
        for bp, rels in sorted(by_bp.items()):
            rnd = random.Random(f'{engine}:{bp}')
            rnd.shuffle(rels)
            out.extend((r, bp) for r in rels[:PER_BUCKET])
    return out


BUILDERS = {
    'dmc_v4': 'pipelines.dmc.mass_write:_rebuild_from_usf',
    'dmc_v5': 'pipelines.dmc.v5.mass_write:_rebuild_from_usf',
    'fc_standard': 'pipelines.future_composer.mass_write:_rebuild_from_usf',
    'music_assembler': 'pipelines.music_assembler.mass_write:_rebuild_from_usf',
    'basic_program': 'pipelines.basic_program.mass_write:_rebuild_from_usf',
    'goattracker_v1': 'pipelines.goattracker.v1.mass_write:_rebuild_from_usf',
    'digi_organizer': 'pipelines.digi_organizer.mass_write:_rebuild_from_usf',
}


def _resolve(spec: str):
    mod, fn = spec.split(':')
    import importlib
    return getattr(importlib.import_module(mod), fn)


_BUILD = None
_ENG = None


def _init(engine):
    global _BUILD, _ENG
    _ENG = engine
    _BUILD = _resolve(BUILDERS[engine])


def _one(item):
    rel, bp = item
    base = os.path.splitext(os.path.join(HVSC, rel))[0]
    try:
        got = _BUILD(rel, base + '.usf')
        want = open(base + '.sidfinity.sid', 'rb').read()
        if got == want:
            return (rel, bp, 'IDENTICAL', '')
        return (rel, bp, 'DIFFERS', f'{len(got)} vs {len(want)} bytes')
    except Exception as e:
        return (rel, bp, 'ERROR', f'{type(e).__name__}: {e}'[:120])


def main():
    engines = sys.argv[1:] or ['dmc_v4', 'dmc_v5', 'fc_standard',
                               'music_assembler', 'basic_program',
                               'goattracker_v1', 'digi_organizer']
    grand = {}
    for eng in engines:
        if eng not in BUILDERS:
            ts(f'{eng}: no builder registered, skipped')
            continue
        try:
            _resolve(BUILDERS[eng])
        except Exception as e:
            ts(f'{eng}: builder unavailable ({type(e).__name__}: {e}) — skipped')
            continue
        sample = sample_for(eng)
        if not sample:
            ts(f'{eng}: no stored FULL artifacts sampled — skipped')
            continue
        bps = sorted({bp for _, bp in sample})
        with phase(f'{eng}: rebuild {len(sample)} stored .usf '
                   f'over {len(bps)} build paths {bps}'):
            n = min(default_jobs(), len(sample))
            with Pool(n, initializer=_init, initargs=(eng,)) as pool:
                res = pool.map(_one, sample)
        tally = defaultdict(int)
        for _, _, st, _ in res:
            tally[st] += 1
        grand[eng] = tally
        ts(f'{eng}: ' + '  '.join(f'{k}={v}' for k, v in sorted(tally.items())))
        for rel, bp, st, note in res:
            if st != 'IDENTICAL':
                ts(f'    {st:9s} [{bp}] {rel}  {note}')

    print()
    print('=' * 78)
    print('VERDICT — did the digi schema change move any stored build?')
    print('=' * 78)
    for eng, t in grand.items():
        total = sum(t.values())
        ok = t.get('IDENTICAL', 0)
        print(f'  {eng:16s} {ok}/{total} byte-identical'
              + (f'   ⚠ {total-ok} not' if ok != total else '   -> NOMINAL staleness'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
