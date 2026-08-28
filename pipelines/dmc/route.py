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

# Engines whose detectors decide the routing. Stamped into the roster so a
# stale roster ANNOUNCES itself: the frozen member lists this replaces went
# wrong precisely because nothing could tell they had drifted (ledger C20).
_FINGERPRINTED = ('dmc_v4', 'dmc_v5')


def _fingerprints() -> dict:
    from src.code_fingerprint import code_fingerprint
    out = {}
    for e in _FINGERPRINTED:
        try:
            out[e] = code_fingerprint(e)
        except Exception as ex:                  # noqa: BLE001
            out[e] = 'ERR:' + type(ex).__name__
    return out


def load_roster(path: str = ROSTER) -> tuple:
    """(meta, rows). Accepts the original flat-list roster too."""
    with open(path) as f:
        d = json.load(f)
    if isinstance(d, list):                      # pre-meta format
        return {}, d
    return d.get('meta', {}), d.get('rows', [])


def roster_staleness(meta: dict) -> list:
    """Which routing engines have changed since the roster was built.

    CONSERVATIVE BY DESIGN: keyed to the whole `dmc_v4`/`dmc_v5` closure, so it
    also fires when something in `pipelines/dmc` that routing never imports
    changed (a batch tool, a mass-writer, this file). That direction is the
    safe one — C20's ninth layer: too broad costs compute and cannot lie, too
    narrow is silently wrong. When it fires spuriously, `--restamp` proves the
    routing closure specifically is untouched instead of re-running the roster.
    """
    was = (meta or {}).get('fingerprints') or {}
    now = _fingerprints()
    return [e for e in _FINGERPRINTED if was.get(e) and was[e] != now.get(e)]


def route_closure(sample_rel: str) -> set:
    """Repo files a ROUTING DECISION actually imports — MEASURED, not declared.

    Same method as `tools/derive_deps.py`: exercise the real call and snapshot
    `sys.modules`. Declaring the set by hand is what C20's ninth layer calls
    under-inclusive-and-silently-wrong; `dmc_v4_config` reaches well past
    `factory.py` into the extract, and a hand-written list would miss it.
    """
    import importlib
    before = set(sys.modules)
    route(sample_rel)
    out = set()
    for name in set(sys.modules) - before:
        mod = sys.modules.get(name)
        f = getattr(mod, '__file__', None)
        if not f:
            continue
        f = os.path.abspath(f)
        if f.startswith(ROOT + os.sep) and f.endswith('.py'):
            out.add(os.path.relpath(f, ROOT))
    return out


def restamp(path: str = ROSTER) -> int:
    """Refresh the roster's fingerprints IF the routing closure is unchanged.

    The roster costs ~110 minutes to rebuild. Re-running it to satisfy a hash
    that moved for an unrelated reason is the waste this repo already warns
    about for verdict rows — so prove it instead, the way
    `tools/migrate_verdict_rows.py` does: compare CONTENT via git (never
    mtime) between the commit that was HEAD when the roster was generated and
    now, restricted to the measured routing closure. Refuses on any real
    change; then a re-run is the only honest answer.
    """
    import subprocess
    meta, rows = load_roster(path)
    when = (meta or {}).get('generated_utc')
    if not when or not rows:
        print('roster has no generated_utc — re-run route.py', file=sys.stderr)
        return 1
    closure = route_closure(rows[0]['rel'])
    # ⚠ A sys.modules SNAPSHOT only sees modules imported DURING the call, so
    # in a process that already imported the factories it measures a short (or
    # empty) closure — and a proof over an empty set passes trivially. That is
    # C20's ninth layer verbatim ("a derivation that 'ran' may have measured
    # nothing — refuse a sample that reached none"), so require the detectors
    # themselves to be in it before trusting the result.
    need = {'pipelines/dmc/v4/factory.py', 'pipelines/dmc/v5/factory.py'}
    missing = need - closure
    if missing:
        print(f'REFUSED — the routing closure measured {len(closure)} files and '
              f'is missing {sorted(missing)}; it was measured in a process that '
              f'had already imported them, so the proof would be vacuous.',
              file=sys.stderr)
        return 1
    base = subprocess.run(['git', 'rev-list', '-1', f'--before={when}', 'HEAD'],
                          cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if not base:
        print('no commit at the roster timestamp — re-run route.py', file=sys.stderr)
        return 1
    changed = subprocess.run(['git', 'diff', '--name-only', base, 'HEAD', '--',
                              *sorted(closure)],
                             cwd=ROOT, capture_output=True, text=True).stdout.split()
    ts(f'routing closure: {len(closure)} files measured, base {base[:8]}')
    if changed:
        print('REFUSED — these routing files changed since the roster:',
              file=sys.stderr)
        for c in changed:
            print('   ' + c, file=sys.stderr)
        print('re-run pipelines/dmc/route.py', file=sys.stderr)
        return 1
    meta['fingerprints'] = _fingerprints()
    meta.setdefault('restamps', []).append(
        {'at': base, 'closure_files': len(closure)})
    with open(path, 'w') as f:
        json.dump({'meta': meta, 'rows': rows}, f, indent=0)
    ts(f'restamped: routing closure unchanged since {base[:8]} '
       f'({len(closure)} files compared by content)')
    return 0


def members_for(pipeline: str, variant: str | None = None,
                path: str = ROSTER, warn: bool = True) -> list:
    """The members a pipeline CLAIMS, from the roster.

    This is what a family batch should iterate instead of a frozen list. The
    difference is not cosmetic: a frozen list both MISSES members the detector
    now claims (57 of them when this landed) and CONTAINS members the detector
    refuses (128), and neither shows up anywhere.

    Members no pipeline claims are deliberately NOT returned by anyone — they
    are accounted for in the roster's unclaimed bucket (and split there into
    near-miss vs unrecognised), which is the ledger C20 orphan distinction:
    a batch must not silently own members its extractor refuses.
    """
    meta, rows = load_roster(path)
    if warn:
        stale = roster_staleness(meta)
        if stale:
            print(f'⚠ roster {os.path.basename(path)} predates changes to '
                  f'{", ".join(stale)} — re-run pipelines/dmc/route.py',
                  file=sys.stderr, flush=True)
    return sorted(r['rel'] for r in rows
                  if r['pipeline'] == pipeline
                  and (variant is None or r['variant'] == variant))


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
        # MULTI-SID (ledger C27): the single-player probe can land on the WRONG
        # CHIP'S player and refuse it for being chip-relocated. Nice_Dream_2SID:
        # chip 1's jump table points into the 2SID dispatch wrapper, so base
        # detection found chip 2 at $3000 and the chipless masked compare died
        # on `STA $D425,Y` vs canon `STA $D405,Y` — a normal chip-2 relocation
        # the 2SID path masks. The BATCH dispatches `dmc_v4_config_2sid` FIRST,
        # so it built and verified the member FULL while the roster called it
        # unclaimed — the C20 palimpsest the --gaps mirror check surfaced. The
        # router must probe the same paths the batch dispatches (C20 4th layer:
        # a consumer taking a different build path than the verifier).
        try:
            from pipelines.dmc.v4.factory import dmc_v4_config_2sid
            cfgs = dmc_v4_config_2sid(rel, hvsc_root=root)
            if cfgs:
                r.claims.append('v4')
                del r.refusals['v4']
                c0 = cfgs[0]
                r.variant = ('family2'
                             if getattr(c0, 'sector_format', 'v4') == 'family2'
                             else 'canonical')
                r.base = int(getattr(c0, 'base', 0)) or None
        except Exception:                        # noqa: BLE001
            pass                                 # keep the single-player refusal

    try:
        from pipelines.dmc.v5.factory import dmc_v5_config
        cfg5 = dmc_v5_config(rel, hvsc_root=root)
        r.claims.append('v5')
        if 'v4' not in r.claims:
            # Name the PLAYER, not a boolean: three wear a V5 head. `f3` is
            # the canonical family-3/5 body; `family4` the Jupiter41 variant;
            # `ed_kids` a hand-built player that wears the family-4 HEAD over
            # family-3/5 SEMANTICS (ledger C13 — a head shape is not a player
            # identity). Left as `f3` it would read as canonical and hide the
            # only member the ed site map serves.
            r.variant = ('family4' if getattr(cfg5, 'family4', False)
                         else 'ed_kids' if getattr(cfg5, 'ed_variant', False)
                         else 'f3')
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


def enrich_build_paths(rows: list, results: list) -> int:
    """Fold each member's RECORDED build path in from batch results.

    Why recorded and not re-derived: a compilation's build path costs a py65
    observation per member, and — more importantly — ledger C20's fourth layer
    is precisely a consumer RE-DERIVING the dispatch instead of taking the one
    the verdict was earned on. The batch already records `build_path`, so the
    roster reads it.

    This is also how a HETEROGENEOUS file becomes visible. One DMC `.sid` can
    pack players from DIFFERENT engine families behind a per-subtune wrapper
    (ledger C31; the C35 `origin_engine` case when it needs more than one
    COMPOSER) — e.g. Bayliss/Freespace_2075 packs one DMC player and TWO
    Music_Assembler players, and Bayliss/Super_Tau-Zeta and The_Syndrom/
    Black_It each pack DMC v4 beside v5. The router answers "who OWNS this
    member" and the answer is legitimately `v4` for all three (v4's
    compilation machinery drives the build and pulls in the other families'
    extractors). But owner alone HIDES that the file's musical content spans
    families, so the build path is recorded beside it: `hetero_masm` /
    `hetero_v5` name exactly which.
    """
    from src.batch_results import load_latest
    by_rel = {}
    for f in results:
        if not os.path.exists(f):
            continue
        for rel, row in load_latest(f).items():
            bp = row.get('build_path')
            if bp:
                by_rel[rel] = bp
    n = 0
    for r in rows:
        bp = by_rel.get(r['rel'])
        if bp and r.get('build_path') != bp:
            r['build_path'] = bp
            n += 1
    return n


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


# Which batch store holds each roster group's verdicts. `None` = the group has
# NO store, i.e. its members carry no verdict at all and appear in no coverage
# number anywhere (DMC's v6 today: extract exists, composer never started).
# A group MISSING from this map is reported too, loudly — an unregistered
# pipeline/variant is the same bug one step earlier.
_VERDICT_STORES = {
    ('v4', 'canonical'): 'dmc_v4',
    ('v4', 'family2'): 'dmc_v4_family2',
    ('v5', 'f3'): 'dmc_v5',          # one store covers every v5 variant
    ('v5', 'family4'): 'dmc_v5',
    ('v5', 'ed_kids'): 'dmc_v5',
    ('v6', None): None,
}
_UNREGISTERED = object()


def verdict_gaps(rows: list) -> list:
    """Members this roster CLAIMS that have no verdict row anywhere.

    THE GAP NOTHING ELSE CAN SEE. A batch reports `full / len(rows)` and its
    rows are its OWN file, so a member the detector claims but that was never
    batched lowers no percentage, fails no gate and appears in no census.
    `summarise` above reports roster membership; each batch reports its own
    rows; the two were never compared. `roster_staleness` does not cover it —
    that watches the routing CODE, not membership-vs-verdicts.

    Measured 2026-08-27: DMC f1/f2 had stood at "5,445/5,445 + 2,924/2,924 =
    100%, family closed" while 50 roster-claimed members had NO row at all —
    the roster was regenerated the day AFTER the last f1/f2 batch and the v4
    detector's claim grew by 50. Batching them returned 5 full / 37 partial /
    3 error, so neither family was closed and both published figures were
    denominator artifacts.

    Cheap by construction: reads the roster (already in memory) and each
    store's key set. Returns one dict per group with a gap, worst first.
    """
    from src.batch_results import STORES, load_latest, store
    groups: dict = collections.defaultdict(list)
    for r in rows:
        if r.get('pipeline'):
            groups[(r['pipeline'], r.get('variant'))].append(r['rel'])
    seen: dict = {}
    out = []
    for key, members in sorted(groups.items()):
        sid = _VERDICT_STORES.get(key, _UNREGISTERED)
        kind = None
        if sid is _UNREGISTERED:
            kind = 'unregistered'          # nobody declared where its verdicts live
        elif sid is None:
            kind = 'no_store'              # declared to have none (v6)
        else:
            if sid not in seen:
                st = store(sid) if sid in STORES else None
                seen[sid] = (set(load_latest(st.path, st.id_key))
                             if st and os.path.exists(st.path) else None)
            have = seen[sid]
            if have is None:
                kind = 'no_results_file'
            else:
                members = [m for m in members if m not in have]
                kind = 'unverified' if members else None
        if kind:
            out.append({'group': key, 'store': sid if sid is not _UNREGISTERED
                        else None, 'kind': kind, 'missing': sorted(members)})
    out.sort(key=lambda d: -len(d['missing']))
    return out


def orphan_verdicts(rows: list) -> list:
    """THE MIRROR of `verdict_gaps`: verdict rows the roster does not claim.

    `verdict_gaps` asks "is every claimed member verified?". This asks "is
    every verdict still owned?", and it catches a different animal — ledger
    C20's stale-FULL palimpsest. A member that WAS claimed and verified FULL,
    whose detector now refuses it, keeps its row and its stored `.usf`/`.sid`
    forever: no mass-write revisits it (its `code_hash` is stale, so the writer
    SKIPS it), its orphan removal only iterates members it knows about, and no
    census counts it. It is invisible from every direction at once.

    Found on the first run: `Surgeon/Nice_Dream_2SID`, FULL as a `multisid`
    member under a dead hash, refused today by `dmc_v4_config`
    (`player_code_mismatch at $1235`), artifacts still on disk.

    Two severities, because they need different actions:
      `unowned`   the roster claims it for NOBODY — a real palimpsest; either
                  the detector regressed or the member genuinely left the
                  family, and the artifacts are orphans nothing will remove.
      `elsewhere` the roster routes it to a DIFFERENT group — a stale row in
                  the wrong store, harmless to coverage but it will confuse
                  any per-store count.
    """
    from src.batch_results import STORES, load_latest, store
    # ⚠ Ownership is per STORE, not per roster group: one store serves several
    # groups (all three v5 variants batch into `dmc_v5`), so comparing against
    # the group made each variant read the others' rows as misfiled — 4,063
    # false positives on the first run, swamping the 1 real finding.
    owner = {}
    for r in rows:
        if r.get('pipeline'):
            sid = _VERDICT_STORES.get((r['pipeline'], r.get('variant')))
            if sid:
                owner[r['rel']] = sid
    out = []
    for sid in sorted({s for s in _VERDICT_STORES.values() if s}):
        if sid not in STORES:
            continue
        st = store(sid)
        if not os.path.exists(st.path):
            continue
        unowned, elsewhere = [], []
        for rel in load_latest(st.path, st.id_key):
            own = owner.get(rel)
            if own == sid:
                continue
            (elsewhere if own else unowned).append(rel)
        for kind, members in (('unowned', unowned), ('elsewhere', elsewhere)):
            if members:
                out.append({'group': (sid, None), 'store': sid, 'kind': kind,
                            'missing': sorted(members)})
    out.sort(key=lambda d: (d['kind'] != 'unowned', -len(d['missing'])))
    return out


_GAP_LABEL = {
    'unowned': 'has a VERDICT ROW but the roster claims it for no pipeline '
               '(C20 stale-FULL palimpsest — artifacts nothing will remove)',
    'elsewhere': 'has a row in this store but the roster routes it elsewhere',
    'unverified': 'claimed by the detector, never batched — no verdict row',
    'no_store': 'routed to a pipeline with NO results store (0 verdicts)',
    'no_results_file': 'store registered but its results file does not exist',
    'unregistered': 'group absent from route._VERDICT_STORES — nobody '
                    'declared where its verdicts live',
}


def _print_group(title: str, gaps: list) -> int:
    n = sum(len(g['missing']) for g in gaps)
    if not gaps:
        return 0
    print(f'\n⚠ {title} — {n} member(s):')
    for g in gaps:
        p, v = g['group']
        print(f'  {len(g["missing"]):5d}  {p}/{v or "-":<10} '
              f'{_GAP_LABEL[g["kind"]]}')
        for m in g['missing'][:5]:
            print(f'            {m}')
        if len(g['missing']) > 5:
            print(f'            ... +{len(g["missing"]) - 5} more')
    return n


def report_verdict_gaps(rows: list) -> int:
    """Print both directions of the roster<->verdicts join; return the count.

    A batch reports `full / len(rows)` over its OWN file, so BOTH directions
    are invisible to every other gate: a claimed member with no row lowers no
    percentage, and a row whose member nothing claims is never revisited.
    """
    gaps, orph = verdict_gaps(rows), orphan_verdicts(rows)
    if not gaps and not orph:
        print('\n✅ every claimed member has a verdict row, and every verdict '
              'row is claimed')
        return 0
    n = _print_group(
        "CLAIMED BUT UNVERIFIED — no verdict row, so they lower no percentage "
        "and appear in no census", gaps)
    n += _print_group(
        "VERDICT BUT UNCLAIMED — the mirror: a row nothing owns is never "
        "revisited by a mass-write or a census", orph)
    return n


def summarise(rows: list, meta: dict | None = None) -> None:
    stale = roster_staleness(meta or {})
    if stale:
        print(f'⚠ STALE: this roster predates changes to {", ".join(stale)} '
              f'— re-run pipelines/dmc/route.py')
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
        print('\n--- build paths (recorded by the batches) ---')
        for k, n in paths.most_common():
            print(f'  {n:5d}  {k}')
        het = [r for r in rows if str(r.get('build_path') or '').startswith('hetero')]
        if het:
            print(f'\n--- HETEROGENEOUS: one file, players from >1 engine family '
                  f'({len(het)}) ---')
            for r in sorted(het, key=lambda r: r['rel']):
                print(f'  {r["rel"]}   owner={r["pipeline"]}  '
                      f'path={r["build_path"]}')
    report_verdict_gaps(rows)
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
    ap.add_argument('--gaps', action='store_true',
                    help='ONLY report roster-claimed members that have no '
                         'verdict row (the closeout check; seconds, no '
                         're-routing). Exit 1 if any.')
    ap.add_argument('--restamp', action='store_true',
                    help='refresh the roster fingerprints if the MEASURED '
                         'routing closure is unchanged by content (else refuse)')
    ap.add_argument('--enrich', action='store_true',
                    help='fold RECORDED build paths in from the batch results '
                         '(surfaces heterogeneous files); updates the roster '
                         'in place, no re-routing')
    args = ap.parse_args()

    _RESULTS = [os.path.join(ROOT, 'tmp', n) for n in
                ('dmc_f1_85_results.jsonl', 'dmc_f2_85_results.jsonl',
                 'dmc_v5_r3_results.jsonl')]

    if args.gaps:
        _meta, rows = load_roster(args.out)
        return 1 if report_verdict_gaps(rows) else 0

    if args.restamp:
        return restamp(args.out)

    if args.summary or args.enrich:
        meta, rows = load_roster(args.out)
        if args.enrich:
            n = enrich_build_paths(rows, _RESULTS)
            with open(args.out, 'w') as f:
                json.dump({'meta': meta, 'rows': rows}, f, indent=0)
            ts(f'enriched {n} build paths -> {args.out}')
        summarise(rows, meta)
        return 0

    engines = _engines()
    members = (json.load(open(args.members)) if args.members else _dmc_members())
    ts(f'DMC corpus: {len(members)} members')
    rows = build_roster(members, engines, args.paths, args.jobs)
    enrich_build_paths(rows, _RESULTS)
    meta = {'generated_utc': __import__('datetime').datetime.now(
                __import__('datetime').timezone.utc).isoformat(timespec='seconds'),
            'corpus': len(rows), 'fingerprints': _fingerprints()}
    with open(args.out, 'w') as f:
        json.dump({'meta': meta, 'rows': rows}, f, indent=0)
    ts(f'roster -> {args.out}')
    summarise(rows, meta)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
