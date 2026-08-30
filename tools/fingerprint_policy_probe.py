#!/usr/bin/env python3
"""What would a change to the code_fingerprint CLOSURE actually cost?

READ-ONLY: writes nothing, lands nothing. Run it BEFORE any key-definition
change (a new exclusion, a widened filter, an EPOCH bump) — the cost of such
a change is never obvious, and is usually not what it looks like.

Answers, per family:
  1. What does the closure actually contain today, and what is the key?
  2. Which candidate exclusion policy MOVES that key (= costs a re-batch)?
  3. Are the rows already stale anyway (= the change costs that family nothing)?
  4. Would migrate_verdict_rows carry the rows under each policy?

Edit POLICIES to describe the change you are considering. The replica hasher
SELF-CHECKS against the real `code_fingerprint()` for every engine before
reporting anything, so a drift in code_fingerprint invalidates the run loudly
instead of producing plausible wrong numbers.

Born 2026-08-30 measuring backlog item 31, where it showed the stated blocker
(~16 h of re-batching) had already evaporated: 8 of 9 stores were 100% stale
for an unrelated reason, so the feared cost was zero.
"""
from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / 'src'), str(ROOT / 'tools')]

from src import code_fingerprint as CF
from src.batch_results import load_latest, stores_for_engine, STORES as REGISTRY

ENGINES = list(CF.DEPS)

# ---------------------------------------------------------------- policies
# Each policy is a predicate over a repo-relative path: True = EXCLUDE.


def pol_current(rel: str) -> bool:
    return rel in CF._KEY_MANAGEMENT or rel.endswith(CF._SELECTION_SUFFIXES)


SUFFIX_FIXED = ('regression_portfolio.json', 'roster.json')


def pol_suffix_fix(rel: str) -> bool:
    return rel in CF._KEY_MANAGEMENT or rel.endswith(SUFFIX_FIXED)


def pol_plus_writer(rel: str) -> bool:
    return pol_suffix_fix(rel) or Path(rel).name == 'mass_write.py'


def pol_plus_docs(rel: str) -> bool:
    return pol_plus_writer(rel) or '/docs/' in f'/{rel}'


POLICIES = [
    ('A current',      pol_current),
    ('B suffix-fix',   pol_suffix_fix),
    ('C +mass_write',  pol_plus_writer),
    ('D +docs/',       pol_plus_docs),
]


# ------------------------------------------------- replica of the hasher
# Mirrors _iter_files/_hash_roots exactly, with the exclusion predicate
# lifted out. Self-checked against the real code_fingerprint() below.

def iter_files(root: Path, excl):
    if root.is_file():
        try:
            rel = root.relative_to(CF.ROOT).as_posix()
            if excl(rel):
                return
        except ValueError:
            pass
        yield root
        return
    if not root.is_dir():
        return
    out = []
    for f in root.rglob('*'):
        if not f.is_file() or '__pycache__' in f.parts or f.name.startswith('.'):
            continue
        if f.suffix.lower() in CF._INERT_SUFFIXES:
            continue
        rel = f.relative_to(CF.ROOT).as_posix()
        if excl(rel):
            continue
        out.append(f)
    yield from sorted(out)


def hash_roots(roots, excl) -> str:
    h = hashlib.sha256()
    h.update(f'epoch={CF.EPOCH}\0'.encode())
    for rel in roots:
        p = CF.ROOT / rel
        if p.is_file() or p.is_dir():
            for f in iter_files(p, excl):
                h.update(f.relative_to(CF.ROOT).as_posix().encode())
                h.update(b'\0')
                h.update(f.read_bytes())
                h.update(b'\0')
        else:
            h.update(f'{rel}\0<ABSENT>\0'.encode())
    return h.hexdigest()[:16]


def closure_files(engine: str, excl) -> list[Path]:
    roots, _ = CF.resolve_roots(engine)
    out = []
    for rel in roots:
        out.extend(iter_files(CF.ROOT / rel, excl))
    return out


# ------------------------------------------------------------------ main
def main():
    print('=' * 78)
    print('SELF-CHECK: replica(policy A) must equal the real code_fingerprint()')
    print('=' * 78)
    ok = True
    for eng in ENGINES:
        roots, prov = CF.resolve_roots(eng)
        mine = hash_roots(roots, pol_current)
        real = CF.code_fingerprint(eng)
        flag = 'OK ' if mine == real else 'MISMATCH'
        ok &= mine == real
        print(f'  {flag} {eng:16s} {mine} vs {real}   ({prov})')
    if not ok:
        print('\n!! replica does not reproduce the hasher — results below are void')
        return 1

    print()
    print('=' * 78)
    print('1. CLOSURE SHAPE + WHICH POLICY MOVES THE KEY')
    print('=' * 78)
    moves = {}
    for eng in ENGINES:
        roots, prov = CF.resolve_roots(eng)
        print(f'\n{eng}   provenance={prov}  roots={len(roots)}')
        base = None
        for name, excl in POLICIES:
            fp = hash_roots(roots, excl)
            n = len(closure_files(eng, excl))
            if base is None:
                base = fp
            tag = 'same' if fp == base else 'MOVES'
            print(f'    {name:15s} {fp}  {n:4d} files   {tag}')
            moves.setdefault(eng, {})[name] = (fp, n, fp != base)

    print()
    print('=' * 78)
    print('2. WHAT EACH POLICY ACTUALLY REMOVES (per family)')
    print('=' * 78)
    for eng in ENGINES:
        cur = {f.relative_to(CF.ROOT).as_posix()
               for f in closure_files(eng, pol_current)}
        for name, excl in POLICIES[1:]:
            nxt = {f.relative_to(CF.ROOT).as_posix()
                   for f in closure_files(eng, excl)}
            gone = sorted(cur - nxt)
            if gone:
                print(f'  {eng:16s} {name:15s} drops {len(gone)}:')
                for g in gone[:12]:
                    print(f'      - {g}')
                if len(gone) > 12:
                    print(f'      ... +{len(gone)-12} more')

    print()
    print('=' * 78)
    print('3. ARE THE ROWS CURRENT TODAY? (does the fix cost this family anything)')
    print('=' * 78)
    import time
    state = {}
    for eng in ENGINES:
        cur_fp = CF.code_fingerprint(eng)
        for s in stores_for_engine(eng):
            p = CF.ROOT / s.rel
            if not p.exists():
                print(f'  {eng:16s} {s.rel:44s} ABSENT')
                continue
            rows = load_latest(str(p), path_key=s.id_key)
            stale = sum(1 for r in rows.values() if r.get('code_hash') != cur_fp)
            stamp = time.strftime('%Y-%m-%d %H:%M',
                                  time.localtime(p.stat().st_mtime))
            verdict = 'ALL CURRENT' if stale == 0 else f'{stale}/{len(rows)} STALE'
            print(f'  {eng:16s} {s.rel:44s} {len(rows):6d} rows  '
                  f'stamped {stamp}  {verdict}')
            state[(eng, s.rel)] = (s.id_key, len(rows), stale)

    print()
    print('=' * 78)
    print('4. WOULD THE MIGRATION CARRY THE ROWS? (per policy, per store)')
    print('=' * 78)
    from tools.migrate_verdict_rows import changed_after
    for eng in ENGINES:
        for s in stores_for_engine(eng):
            p = CF.ROOT / s.rel
            if not p.exists():
                continue
            stamp = p.stat().st_mtime
            print(f'\n  {eng} :: {s.rel}')
            for name, excl in POLICIES:
                files = closure_files(eng, excl)
                changed, unver = changed_after(files, stamp)
                if changed:
                    verdict = f'REFUSE ({len(changed)} changed)'
                elif unver:
                    verdict = f'refuse-untracked ({len(unver)})'
                else:
                    verdict = 'CARRIES'
                print(f'      {name:15s} {len(files):4d} files -> {verdict}')
                for c in changed[:6]:
                    print(f'          changed: {c}')
                for u in unver[:6]:
                    print(f'          untracked mtime moved: {u}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
