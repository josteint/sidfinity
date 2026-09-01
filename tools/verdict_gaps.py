#!/usr/bin/env python3
"""verdict_gaps.py — for EVERY family, diff what the batch enumerates against
what its verdict store holds, in both directions.

    python3 tools/verdict_gaps.py            # all families, exit 1 on a gap
    python3 tools/verdict_gaps.py fc_standard

Two directions, and they fail differently:

  UNVERIFIED   a member the batch enumerates with no row in the store. It is
               invisible from every direction: it lowers no percentage and
               appears in no census, so a family reads "closed" while some of
               its members have never been judged. Measured 2026-08-27 on
               DMC — f1/f2 had stood at "100%, family closed" while 50
               roster-claimed members had no verdict row at all; batching
               them returned 37 partial + 3 error.

  ORPHAN ROWS  a row nobody enumerates. Rows are keyed by PATH; a batch that
               stops enumerating a path simply never revisits it, and no gate
               looks for a row nobody claims. This is ledger C20's stale-FULL
               palimpsest, and it SILENTLY INFLATES THE DENOMINATOR AND THE
               NUMERATOR. Measured 2026-08-31 on fc_standard: the store held
               4,140 members and the batch enumerated 4,093, the 47
               difference all pre-HVSC-#85 paths whose .sid is gone from
               disk. MEMORY.md recorded FC at "2,604 FULL"; the re-batch
               measured 2,572, and 2,604 - 2,572 = 32 = exactly the vanished
               FULLs. The recorded figure counted 32 members that no longer
               exist.

`route.py --gaps` already does this for DMC, against its roster, and it is
the authority there (it also reports `no_store` / `unregistered`, which are
routing facts only the router knows). This tool covers every OTHER family —
the measurement said the rows-with-no-member direction is the one that
actually bit, and it bites families with no roster at all.

⚠ The enumeration comes from each batch's own `members()`. Do not re-write
the query here: a gap check that duplicates the enumeration drifts away from
it, and the drift is invisible in exactly the direction that matters.

Read-only. Nothing is deleted or restamped; `orphan_rows` is a REPORT, and
what to do about each one (a rename to carry over vs a member that is really
gone) is a judgement — see backlog item 37 and ledger C20's seventh layer,
which is explicit that matching members across an HVSC update by whole-file
hash reads 46 RENAMES as deletions.
"""
from __future__ import annotations

import argparse
import importlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (os.path.join(ROOT, 'src'), ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from src.tslog import ts                                   # noqa: E402
from src.batch_results import load_latest, store, STORES   # noqa: E402

# store_id -> (batch module, how to turn one members() element into a path)
#
# DMC's four stores are absent on purpose: `pipelines/dmc/route.py --gaps` is
# their check and knows things this tool cannot (which pipeline a member is
# routed to, and whether that pipeline has a store at all).
ENUMERATORS = {
    'fc_standard':     ('pipelines.future_composer.family_batch',
                        lambda m: m),
    'music_assembler': ('pipelines.music_assembler.family_batch',
                        lambda m: m),
    'goattracker_v1':  ('pipelines.goattracker.v1.family_batch',
                        lambda m: m[0]),
    'basic_program':   ('pipelines.basic_program.family_batch',
                        lambda m: m[0]),
    'digi_organizer':  ('pipelines.digi_organizer.family_batch',
                        lambda m: m),
}

DMC_STORES = ('dmc_v4', 'dmc_v4_family2', 'dmc_v5', 'dmc_v6')


def check(store_id: str) -> dict:
    mod_name, to_path = ENUMERATORS[store_id]
    st = store(store_id)
    mod = importlib.import_module(mod_name)
    claimed = [to_path(m) for m in mod.members()]
    claimed_set = set(claimed)

    path = os.path.join(ROOT, st.path)
    if not os.path.exists(path):
        return {'store': store_id, 'error': f'no results file: {st.path}'}
    rows = load_latest(path, st.id_key)

    unverified = sorted(claimed_set - set(rows))
    orphans = sorted(set(rows) - claimed_set)
    # An orphan whose BASENAME is covered by a claimed path is almost
    # certainly a rename (HVSC re-files on a credit fix — C20 seventh
    # layer), so it is verified, just at a new path. Separating the two
    # matters: the renames are noise, the uncovered ones are the finding.
    by_base = {os.path.basename(p) for p in claimed_set}
    renamed = [p for p in orphans if os.path.basename(p) in by_base]
    uncovered = [p for p in orphans if os.path.basename(p) not in by_base]
    # How many of the uncovered rows were recorded FULL — the number that
    # silently inflated the family's coverage figure.
    lost_full = [p for p in uncovered if rows[p].get('status') == 'full']
    on_disk = [p for p in uncovered
               if os.path.exists(os.path.join(ROOT, 'hvsc85', p))]
    # The honest coverage: FULL among CLAIMED members, beside the figure a
    # naive read of the store gives. The gap between them is what the dead
    # rows were inflating.
    full_rows = [p for p, r in rows.items() if r.get('status') == 'full']
    full_claimed = [p for p in full_rows if p in claimed_set]
    return {'store': store_id, 'claimed': len(claimed_set),
            'full_in_store': len(full_rows),
            'full_claimed': len(full_claimed),
            'rows': len(rows), 'unverified': unverified,
            'orphan_rows': orphans, 'renamed': renamed,
            'uncovered': uncovered, 'lost_full': lost_full,
            'uncovered_still_on_disk': on_disk}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('stores', nargs='*',
                    help=f'default: all of {", ".join(sorted(ENUMERATORS))}')
    ap.add_argument('--list', type=int, default=12,
                    help='how many paths to print per bucket (0 = all)')
    a = ap.parse_args()

    ids = a.stores or sorted(ENUMERATORS)
    bad = [s for s in ids if s not in ENUMERATORS]
    if bad:
        if any(s in DMC_STORES for s in bad):
            print('DMC families are covered by `pipelines/dmc/route.py '
                  '--gaps`, which knows their routing.', file=sys.stderr)
        print(f'unknown store(s): {bad}; known: {sorted(ENUMERATORS)}',
              file=sys.stderr)
        return 2

    fail = False
    print(f'{"store":<18} {"claimed":>8} {"rows":>7} {"unverified":>11} '
          f'{"orphans":>8} {"(renamed":>9} {"uncovered":>10} '
          f'{"lost FULL)":>11}')
    results = []
    for sid in ids:
        r = check(sid)
        results.append(r)
        if 'error' in r:
            print(f'{sid:<18} {r["error"]}')
            fail = True
            continue
        print(f'{sid:<18} {r["claimed"]:8d} {r["rows"]:7d} '
              f'{len(r["unverified"]):11d} {len(r["orphan_rows"]):8d} '
              f'{len(r["renamed"]):9d} {len(r["uncovered"]):10d} '
              f'{len(r["lost_full"]):11d}')
        if r['unverified'] or r['uncovered']:
            fail = True

    print()
    print(f'{"store":<18} {"FULL in store":>14} {"FULL claimed":>13} '
          f'{"inflation":>10}   coverage over claimed')
    for r in results:
        if 'error' in r:
            continue
        infl = r['full_in_store'] - r['full_claimed']
        pct = 100.0 * r['full_claimed'] / r['claimed'] if r['claimed'] else 0
        print(f'{r["store"]:<18} {r["full_in_store"]:14d} '
              f'{r["full_claimed"]:13d} {infl:10d}   '
              f'{r["full_claimed"]}/{r["claimed"]} = {pct:.1f}%')

    for r in results:
        if 'error' in r:
            continue
        for name, xs in (('UNVERIFIED (enumerated, never batched)',
                          r['unverified']),
                         ('ORPHAN ROWS, uncovered (no member claims them)',
                          r['uncovered'])):
            if not xs:
                continue
            print(f'\n[{r["store"]}] {name}: {len(xs)}')
            show = xs if a.list == 0 else xs[:a.list]
            for p in show:
                tag = ''
                if p in r['lost_full']:
                    tag += ' [was FULL]'
                if p in r['uncovered_still_on_disk']:
                    tag += ' [.sid STILL ON DISK -> reclassified, not removed]'
                print(f'    {p}{tag}')
            if len(xs) > len(show):
                print(f'    ... and {len(xs) - len(show)} more '
                      f'(--list 0 for all)')

    if fail:
        ts('GAPS FOUND — see above. Read-only: nothing was changed.')
    else:
        ts('no gaps: every enumerated member has a row, '
           'every row has a member.')
    return 1 if fail else 0


if __name__ == '__main__':
    raise SystemExit(main())
