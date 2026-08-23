#!/usr/bin/env python3
"""Which DMC pipeline claims a member — and the roster that accounts for ALL of them.

WHY THIS EXISTS
---------------
Until now the v4/v5 split was carried by FROZEN member lists (`tmp/dmc_f1_members_85.json`
& friends), derived once from the 2026-06-12 opcode-skeleton fingerprint census against
HVSC **#84**. Nothing re-derived them, so the lists drifted away from what the detectors
actually claim, and three things went wrong at once:

1. **238 DMC members (2.2%) were in NO list** — so they appeared in no batch, and a
   coverage number like "1,174/2,151 FULL" silently excluded them. They were not counted
   as failing; they were simply absent. That is the accounting hole this module closes.
2. **57 of those 238 are claimed by the CURRENT detectors** (48 v4, 9 v5) — buildable
   today, invisible purely through stale bookkeeping.
3. A frozen classification is exactly what ledger **C13** warns against: dispatch on the
   PLAYER SIGNATURE, never on a stored label. This module asks the detectors instead.

WHAT A "PIPELINE" IS HERE
-------------------------
A pipeline is a COMPOSER, not a bucket — the boundary the Principle §8 / ledger C35 draw
("more than one COMPOSER", not "more than one engine"). So:

  * `v4`  — census families 1 + 2. family-2 is NOT its own pipeline: same composer,
            relocated tables + a parametric sector format + probed knobs.
  * `v5`  — census families 3 + 4 + 5. family-4 is NOT its own pipeline either: same
            composer, 14 named mechanism knobs.
  * `v6`  — a genuinely different player (~0.01 Jaccard to everything else). Player RE
            done, extract/composer NOT started, so it claims members by signature but
            cannot build them yet.

There is deliberately no `vX` pipeline. An unclaimed member has no composer, so there
would be nothing to put in the directory; the moment one is REd it turns out to be either
a variant of an existing pipeline (→ knobs) or a genuinely new player (→ its own pipeline,
named for what it is). "Unclaimed" is a WORKLIST, and it lives in the roster below.

`family-N` is OUR census cluster id (numbered by size), not a DMC concept. It belongs in
RE notes, never in routing.

USAGE
-----
    from pipelines.dmc.route import route
    r = route('MUSICIANS/B/Brian/Bach.sid')
    r.pipeline, r.variant          # 'v5', 'family4'

    python3 pipelines/dmc/route.py                 # build + summarise the roster
    python3 pipelines/dmc/route.py --paths         # also detect each v4 member's build path
    python3 pipelines/dmc/route.py --members F.json --out R.json
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
from dataclasses import dataclass, asdict, field

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.tslog import ts, phase                                    # noqa: E402

ROSTER = os.path.join(ROOT, 'pipelines', 'dmc', 'roster.json')

# sidid engine strings that mean "this is a DMC member at all".
DMC_ENGINE_SQL = "engine LIKE 'DMC%'"


@dataclass
class Route:
    """Which pipeline claims `rel`, or why none does."""
    rel: str
    pipeline: str | None = None        # 'v4' | 'v5' | 'v6' | None
    variant: str | None = None         # 'canonical'|'family2' | 'f3'|'family4'
    build_path: str | None = None      # v4 only, and only with --paths
    base: int | None = None
    refusals: dict = field(default_factory=dict)   # pipeline -> refusal reason
    claims: list = field(default_factory=list)     # every pipeline that claimed it

    @property
    def ambiguous(self) -> bool:
        return len(self.claims) > 1


def _reason(e: Exception) -> str:
    return f'{type(e).__name__}: {e}'.strip()[:120]


# Refusals that mean "I RECOGNISED this player and then rejected the member"
# (the jump table / vectors matched; something past that did not). They are a
# different kind of unclaimed from "this is not my player at all", and the
# distinction is ledger C20's orphan rule one level up: MINE-AND-FAILED is
# work to do, NOT MINE is somebody else's player. Derived from the refusal
# itself, so it needs no frozen classification to stay true.
_NEAR_MISS = ('player_code_mismatch', 'nonstandard_instr_base',
              'loop_site_unknown', 'no_base', 'oob')


def near_miss_of(refusals: dict) -> str | None:
    """Which pipeline RECOGNISED the player but refused the member, if any."""
    for p, why in sorted(refusals.items()):
        if any(k in (why or '') for k in _NEAR_MISS):
            return p
    return None


def norm_reason(reason: str) -> str:
    """Collapse per-member noise so refusals of the same SHAPE bucket together
    (same idea as tools/divergence_census._norm_reason)."""
    reason = (reason or '').split('\n', 1)[0]
    reason = re.sub(r'\$[0-9A-Fa-f]+', '$?', reason)
    reason = re.sub(r'\b\d{3,}\b', 'N', reason)
    return reason.strip()


def route(rel: str, hvsc_root: str | None = None,
          engine: str | None = None, want_path: bool = False) -> Route:
    """Ask every DMC pipeline whether it claims `rel`.

    Deliberately asks ALL of them rather than returning the first hit: a member
    both v4 and v5 claim is a real problem (overlapping detectors) and must be
    visible, not silently resolved by ordering. `claims` records everyone who
    said yes; `pipeline` is the winner under the documented precedence.

    Never raises — a router that dies on a malformed member cannot account for
    the corpus, and accounting for the whole corpus is the entire point.
    """
    root = hvsc_root or os.path.join(ROOT, 'hvsc85')
    r = Route(rel=rel)

    # v6 has no factory yet: it is identified by its sidid signature, which is
    # exact (a distinct player, ~0.01 Jaccard to every other DMC family). It
    # claims its members so they are ACCOUNTED FOR, and `buildable` stays False.
    if (engine or '').startswith('DMC_V6'):
        r.claims.append('v6')

    try:
        from pipelines.dmc.v4.factory import dmc_v4_config
        cfg = dmc_v4_config(rel, hvsc_root=root)
        r.claims.append('v4')
        # family-2 is marked by its SECTOR ENCODING, not a boolean: the two
        # differ by a re-laid-out table set + a different command map, and
        # `sector_format` is the field that actually carries it.
        r.variant = ('family2' if getattr(cfg, 'sector_format', 'v4') == 'family2'
                     else 'canonical')
        r.base = int(getattr(cfg, 'base', 0)) or None
    except Exception as e:                       # noqa: BLE001 - router must not die
        r.refusals['v4'] = _reason(e)

    try:
        from pipelines.dmc.v5.factory import dmc_v5_config
        cfg5 = dmc_v5_config(rel, hvsc_root=root)
        r.claims.append('v5')
        if 'v4' not in r.claims:
            r.variant = 'family4' if getattr(cfg5, 'family4', False) else 'f3'
            r.base = int(getattr(cfg5, 'base', 0)) or None
    except Exception as e:                       # noqa: BLE001
        r.refusals['v5'] = _reason(e)

    # Precedence when more than one claims. v4 first — and that order is
    # MEASURED, not assumed: the only two collisions in the whole 10,774-member
    # corpus (Bayliss/Grid_Zone_Remix, Bayliss/Last_Amazon) build and verify
    # through v4 at relocated bases ($8200/$2900), while their v5 CONFIG
    # succeeds and the v5 EXTRACT then dies ("orderlist never ends"). So v5's
    # claim is a config-level false positive on both. `ambiguous` still records
    # the collision — a detector drifting loose is exactly what it is for.
    for p in ('v4', 'v5', 'v6'):
        if p in r.claims:
            r.pipeline = p
            break

    if want_path and r.pipeline == 'v4':
        try:
            from pipelines.dmc.verify import detect_v4_build_path
            r.build_path = detect_v4_build_path(rel, hvsc_root=root)['kind']
        except Exception as e:                   # noqa: BLE001
            r.build_path = 'path-error: ' + _reason(e)
    return r


def _dmc_members() -> list:
    from src import sid_db
    return sorted(p for (p,) in sid_db.query(
        f'SELECT path FROM sids WHERE {DMC_ENGINE_SQL}'))


def _engines() -> dict:
    from src import sid_db
    return {p: e for p, e in sid_db.query(
        f'SELECT path, engine FROM sids WHERE {DMC_ENGINE_SQL}')}


_ENG: dict = {}
_PATHS = False


def _worker(rel: str) -> dict:
    return asdict(route(rel, engine=_ENG.get(rel), want_path=_PATHS))


def _init(eng: dict, paths: bool) -> None:
    global _ENG, _PATHS
    _ENG, _PATHS = eng, paths


def build_roster(members: list, engines: dict, want_paths: bool = False,
                 jobs: int | None = None) -> list:
    from concurrent.futures import ProcessPoolExecutor
    from src.jobs import default_jobs
    n = jobs or default_jobs()
    rows = []
    with phase(f'route {len(members)} DMC members ({n} workers'
               f'{", + build paths" if want_paths else ""})'):
        with ProcessPoolExecutor(max_workers=n, initializer=_init,
                                 initargs=(engines, want_paths)) as ex:
            for i, row in enumerate(ex.map(_worker, members), 1):
                rows.append(row)
                if i % 500 == 0:
                    ts(f'  {i}/{len(members)}')
    return rows


def summarise(rows: list) -> None:
    total = len(rows)
    claimed = collections.Counter()
    unclaimed = collections.Counter()
    amb = [r for r in rows if len(r['claims']) > 1]
    for r in rows:
        if r['pipeline']:
            claimed[(r['pipeline'], r['variant'] or '-')] += 1
        else:
            # a member both refused: bucket by the SHAPE of the pair
            v4 = norm_reason(r['refusals'].get('v4', ''))
            v5 = norm_reason(r['refusals'].get('v5', ''))
            unclaimed[(v4, v5)] += 1
    nclaimed = sum(claimed.values())
    nunc = sum(unclaimed.values())
    print(f'\n=== DMC roster — {total} members ===')
    print(f'{"pipeline":<10}{"variant":<12}{"members":>9}')
    for (p, v), n in sorted(claimed.items(), key=lambda kv: -kv[1]):
        print(f'{p:<10}{v:<12}{n:>9}')
    print(f'{"":<10}{"CLAIMED":<12}{nclaimed:>9}   ({100*nclaimed/total:.1f}%)')
    print(f'{"":<10}{"UNCLAIMED":<12}{nunc:>9}   ({100*nunc/total:.1f}%)')
    if amb:
        print(f'\n⚠ AMBIGUOUS (more than one pipeline claims): {len(amb)}')
        for r in amb[:10]:
            print(f'    {r["rel"]}  claims={r["claims"]}')
    if nunc:
        near = collections.Counter(
            near_miss_of(r['refusals']) or 'unknown-player'
            for r in rows if not r['pipeline'])
        print('\n--- unclaimed, split by WHAT KIND of unclaimed ---')
        for k, n in near.most_common():
            label = ('recognised by %s, member refused (work to do)' % k
                     if k != 'unknown-player'
                     else 'no pipeline recognises the player')
            print(f'  {n:5d}  {label}')
        print('\n--- unclaimed, by refusal shape (top 12) ---')
        for (v4, v5), n in unclaimed.most_common(12):
            print(f'  {n:5d}  v4: {v4[:52]}')
            print(f'         v5: {v5[:52]}')
    paths = collections.Counter(r['build_path'] for r in rows if r['build_path'])
    if paths:
        print('\n--- v4 build paths ---')
        for k, n in paths.most_common():
            print(f'  {n:5d}  {k}')
    # The roster's whole contract: every member lands in exactly one bucket.
    assert nclaimed + nunc == total, 'roster does not partition the corpus'


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--members', help='JSON list of rel paths (default: all DMC)')
    ap.add_argument('--out', default=ROSTER)
    ap.add_argument('--paths', action='store_true',
                    help="also detect each v4 member's build path (slower)")
    ap.add_argument('--jobs', type=int, default=None)
    ap.add_argument('--summary', action='store_true',
                    help='re-summarise an existing roster without re-routing')
    args = ap.parse_args()

    if args.summary:
        summarise(json.load(open(args.out)))
        return 0

    engines = _engines()
    members = (json.load(open(args.members)) if args.members else _dmc_members())
    ts(f'DMC corpus: {len(members)} members')
    rows = build_roster(members, engines, args.paths, args.jobs)
    with open(args.out, 'w') as f:
        json.dump(rows, f, indent=0)
    ts(f'roster -> {args.out}')
    summarise(rows)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
