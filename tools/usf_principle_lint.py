#!/usr/bin/env python3
"""The Principle's materialization pressure — corpus-content censuses.

Why this exists (2026-08-03): the project has a mechanical ratchet for
FIDELITY (the write-stream verify) but had none for REPRESENTATION QUALITY.
The Principle's §9 names four ML-readiness tests; only test 1 (completeness)
ever had enforcement. This tool gives hands to the corpus-content half:

CHECK 1 — CARDINALITY / DISJOINTNESS CENSUS (§9.2's own prescribed check,
verbatim: "cross-engine cardinality analysis (group field values by engine,
flag fields with disjoint value sets per engine)"). Walks every stored
.usf's parsed object tree, collects scalar field values, groups by ENGINE
FAMILY (attributed via the hvsc84.parquet catalogue — the USF itself
deliberately carries no engine tag), and flags:
  - DISJOINT: >=2 families populate the field and their value sets are
    pairwise disjoint with >1 value each — the fingerprint of a
    kind-in-disguise (a model could reconstruct engine identity from the
    field, which §7 forbids).
  - SINGLE-FAMILY: exactly one family populates it — a possible engine
    artifact (§7) OR a legitimate not-yet-shared dimension; judgment call,
    surfaced for uready Phase 2.
  - NEAR-CONSTANT: one value covers >=99.9% of occurrences corpus-wide —
    a dead dimension or a disguised boolean.
Findings are WARNINGS with a reviewed ALLOWLIST — the allowlist's reasons
are the Principle accumulating case law.

CHECK 2 — ESCAPE-HATCH MASS RATCHET: one number — the fraction of the
corpus's field instances living in UNTYPED carriers (params.fields keys,
NoteRow fx_flags strings) vs typed schema fields. The counter-pressure to
wedge-knob accumulation: the C33 recipe burns keys down one at a time;
this makes the AGGREGATE visible. `--write-baseline` stores the current
numbers in tools/usf_ratchet_baseline.json (git-tracked); subsequent runs
compare and WARN on growth.

(CHECK 3, the §9.3 interpolation probe, is a separate heavier harness —
see the cleanup plan E3; not part of this lint.)

Usage:
    python3 tools/usf_principle_lint.py [--sample N] [--full] [--seed S]
                                        [--write-baseline]

Exit is always 0 unless the ratchet REGRESSES vs the stored baseline
(untyped share grew) — censuses are flags for review, not gates.
"""
from __future__ import annotations

import argparse
import dataclasses
import glob
import json
import os
import random
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))

BASELINE = os.path.join(ROOT, 'tools', 'usf_ratchet_baseline.json')

# Reviewed findings — the Principle's case law. key = the finding line's
# stable id ("<flag>:<field_path>"); value = the reason it is acceptable.
ALLOWLIST: dict[str, str] = {
    # (empty at birth — populate via review, never to silence unread flags)
}

NEAR_CONSTANT_SHARE = 0.999
MIN_OCC = 200

# Free-text metadata — content identifiers, not representation dimensions;
# trivially disjoint across families and meaningless to census.
METADATA_FIELDS = {'psid.title', 'psid.author', 'psid.released',
                   'instruments[].name', 'subtunes[].name'}


def _families() -> dict[str, str]:
    """sid path (HVSC-relative, .sid) -> engine family, via the catalogue."""
    from src import sid_db
    fam = {}
    for path, engine in sid_db.query(
            'SELECT path, engine FROM sids WHERE engine IS NOT NULL'):
        fam[path] = engine
    return fam


def _walk(obj, path: str, out: list):
    """Collect (field_path, scalar_value) from a parsed UsfFile tree.
    Scalars only — content tables (lists of ints) are musical data, not
    dimensions; lists of dataclasses recurse WITHOUT the index (all
    elements are instances of the same dimension)."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        for f in dataclasses.fields(obj):
            v = getattr(obj, f.name)
            p = f'{path}.{f.name}' if path else f.name
            if isinstance(v, (bool, int, float, str)) and v is not None:
                out.append((p, v))
            elif isinstance(v, (list, tuple)):
                for el in v:
                    if dataclasses.is_dataclass(el) and not isinstance(el, type):
                        _walk(el, p + '[]', out)
            elif dataclasses.is_dataclass(v):
                _walk(v, p, out)
            elif isinstance(v, dict):
                # untyped bags are counted by check 2, not censused by name
                pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int, default=400)
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--seed', type=int, default=7)
    ap.add_argument('--write-baseline', action='store_true')
    args = ap.parse_args()

    from src.usf.parser import parse_file

    fam_of = _families()
    files = []
    for pat in ('hvsc84/MUSICIANS/*/*/*.usf', 'hvsc84/MUSICIANS/*/*/*/*.usf',
                'hvsc84/DEMOS/*/*.usf', 'hvsc84/GAMES/*/*.usf'):
        files.extend(glob.glob(os.path.join(ROOT, pat)))
    files.sort()
    if not args.full:
        rng = random.Random(args.seed)
        files = rng.sample(files, min(args.sample, len(files)))
    print(f'usf_principle_lint: {len(files)} stored .usf '
          f'({"full corpus" if args.full else "sample"})')

    # field_path -> family -> Counter(value)
    census: dict[str, dict[str, Counter]] = defaultdict(
        lambda: defaultdict(Counter))
    typed_instances = 0
    untyped_instances = 0
    rowcmd_instances = 0        # fx_flags — C14 canonical row commands
    bag_inst: Counter = Counter()      # params-bag key -> instances
    bag_members: Counter = Counter()   # params-bag key -> carrier members
    unattributed = 0
    parse_fail = 0
    for f in files:
        rel = os.path.relpath(f, os.path.join(ROOT, 'hvsc84'))
        family = fam_of.get(rel[:-4] + '.sid')
        if family is None:
            unattributed += 1
            continue
        try:
            u = parse_file(f)
        except Exception:
            parse_fail += 1
            continue
        vals: list = []
        _walk(u, '', vals)
        typed_instances += len(vals)
        for p, v in vals:
            census[p][family][v] += 1
        # UNTYPED carriers = params.fields keys only (file + per-subtune).
        # fx_flags is counted SEPARATELY: it is the C14 CANONICAL form for
        # row commands (a small behavior-named vocabulary — tie, vol=,
        # glide=, glide_up, no_release …), not an escape hatch; lumping it
        # into the untyped mass made the ratchet number meaningless
        # (the P4 census, 2026-08-04).
        pf = getattr(getattr(u, 'params', None), 'fields', None) or {}
        untyped_instances += len(pf)
        _file_bag = set(pf)
        for k in pf:
            bag_inst[k] += 1
        for sub in getattr(u, 'subtunes', []) or []:
            spf = getattr(getattr(sub, 'params', None), 'fields', None) or {}
            untyped_instances += len(spf)
            _file_bag |= set(spf)
            for k in spf:
                bag_inst[k] += 1
            for v in getattr(sub, 'voices', []) or []:
                for pat_rows in getattr(v, 'patterns', []) or []:
                    rows = pat_rows if isinstance(pat_rows, list) else \
                        getattr(pat_rows, 'rows', [])
                    for r in rows or []:
                        fx = getattr(r, 'fx_flags', None)
                        if fx:
                            rowcmd_instances += (len(fx) if
                                                 isinstance(fx, list) else 1)
        bag_members.update(_file_bag)
    if parse_fail or unattributed:
        print(f'  (skipped: {parse_fail} parse-fail, '
              f'{unattributed} not in catalogue)')

    # ---- check 1: cardinality / disjointness ----
    flags: list[tuple[str, str, str]] = []       # (flag, field, detail)
    for p, byfam in sorted(census.items()):
        if p in METADATA_FIELDS:
            continue
        total = sum(sum(c.values()) for c in byfam.values())
        if total < MIN_OCC:
            continue
        all_vals = Counter()
        for c in byfam.values():
            all_vals.update(c)
        top, n = all_vals.most_common(1)[0]
        if n / total >= NEAR_CONSTANT_SHARE:
            flags.append(('NEAR-CONSTANT', p,
                          f'value {top!r} = {n}/{total}'))
            continue
        fams = [f for f, c in byfam.items() if c]
        if len(fams) == 1:
            flags.append(('SINGLE-FAMILY', p, f'only {fams[0]} ({total})'))
            continue
        sets = {f: set(c) for f, c in byfam.items() if c}
        if all(len(s) > 1 for s in sets.values()):
            pairwise_disjoint = all(
                not (sets[a] & sets[b])
                for i, a in enumerate(fams) for b in fams[i + 1:])
            if pairwise_disjoint:
                flags.append(('DISJOINT', p,
                              'value sets pairwise disjoint across ' +
                              ', '.join(sorted(fams))))
    shown = [(fl, p, d) for fl, p, d in flags
             if f'{fl}:{p}' not in ALLOWLIST]
    print(f'check 1 cardinality census : {len(shown)} finding(s) '
          f'({len(flags) - len(shown)} allowlisted)')
    for fl, p, d in shown:
        print(f'  ⚠ {fl:14} {p}: {d}')

    # ---- check 2: escape-hatch mass ratchet ----
    total_inst = typed_instances + untyped_instances + rowcmd_instances
    share = untyped_instances / total_inst if total_inst else 0.0
    print(f'check 2 escape-hatch mass  : {untyped_instances} params-bag / '
          f'{rowcmd_instances} row-cmd (C14 canonical) / '
          f'{typed_instances} typed = {share:.4%} untyped')
    rc = 0
    if os.path.exists(BASELINE):
        base = json.load(open(BASELINE))
        prev = base.get('untyped_share', 0.0)
        delta = share - prev
        marker = '⚠ GREW' if delta > 0.0005 else 'ok'
        print(f'  vs baseline {prev:.4%} ({base.get("date","?")}): '
              f'{delta:+.4%}  [{marker}]')
        if delta > 0.0005:
            rc = 1
    else:
        print(f'  (no baseline — write one with --write-baseline)')
    if args.write_baseline:
        import datetime
        json.dump({'untyped_share': share,
                   'untyped': untyped_instances, 'total': total_inst,
                   'sampled': len(files), 'full': args.full,
                   'date': datetime.date.today().isoformat()},
                  open(BASELINE, 'w'), indent=1)

    # ---- check 2b: the params-bag JUSTIFICATION LEDGER (I2, 2026-08-05) ----
    # Every bag key must fall under a documented block. The I2 census showed
    # the bag is NOT a wedge tail: ~2/3 is Basic_Program's trace-lift
    # template representation, most of the rest is old-form f2/v5 stored
    # corpora that converge mechanically at their campaigns' mass-writes.
    # Keys matching NO block are the tripwire: a small-carrier key is the
    # legitimate C19 wedge-knob floor (reported as a count); a key carried
    # by >= UNJUSTIFIED_MASS members is an UNJUSTIFIED MASS — exit 1.
    import re as _re
    BAG_BLOCKS = [
        ('basic_program templates', r'^bp(_|$)',
         'trace-lift template representation lives in the bag — a '
         'FAMILY-level representation question (BP review)'),
        ('otrk fitted forms', r'^otrk_(pad|period|rcmd|legacy)_',
         'f1 = the 22 documented C32 design refusals; f2/4/v5 = old-form '
         'stored corpora, converge at their campaigns\' mass-writes'),
        ('init_behavior old-form (typed r182)',
         r'^(hold_gateoff|rest_effects|hard_restart|cymbal_onset|'
         r'vib_ramp)$',
         'typed into init_behavior (r182); params form = the f2 June '
         'corpora, converge at the f2 mass-write'),
        ('FC std_* (C7-A3)', r'^std_',
         'FC param-shaped leapfrog — recorded ledger C7 class A3, '
         'closes at the FC campaign'),
        ('slide_phase old-form', r'^slide_phase$',
         'typed as init.slide_phase; params form = old-form corpora'),
        ('play-dispatch schedules', r'^(play_phases|play_repeat|'
         r'play_unit_repeat|fphase_repeat)$',
         'observed C18/C24 play-wrapper mechanism — mechanism-'
         'descriptive, correctly untyped'),
    ]
    UNJUSTIFIED_MASS = 50
    block_inst = Counter()
    block_members = Counter()
    floor_keys = 0
    floor_inst = 0
    unjustified = []
    for k, inst in bag_inst.items():
        for name, pat, _ in BAG_BLOCKS:
            if _re.match(pat, k):
                block_inst[name] += inst
                block_members[name] += bag_members[k]
                break
        else:
            if bag_members[k] >= UNJUSTIFIED_MASS:
                unjustified.append((k, bag_members[k], inst))
            else:
                floor_keys += 1
                floor_inst += inst
    print('check 2b bag justification :')
    for name, pat, why in BAG_BLOCKS:
        if block_inst[name]:
            print(f'  {block_inst[name]:7d} inst  {name}: {why}')
    print(f'  {floor_inst:7d} inst  wedge-knob floor '
          f'({floor_keys} keys, each < {UNJUSTIFIED_MASS} members — '
          f'the intentional C19 singleton tail)')
    if unjustified:
        rc = 1
        for k, m, inst in sorted(unjustified, key=lambda t: -t[1]):
            print(f'  ⚠ UNJUSTIFIED MASS  {k}: {m} members / {inst} inst '
                  f'— matches no documented block (type it or document it)')
        print(f'  baseline written -> {os.path.relpath(BASELINE, ROOT)}')
    return rc


if __name__ == '__main__':
    sys.exit(main())
