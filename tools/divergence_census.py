#!/usr/bin/env python3
"""divergence_census.py — residue triage for a wide engine family.

Turns a flat batch-results jsonl into a ranked set of ROOT-CAUSE CLUSTERS:

  (1) CENSUS  — bucket every member by status + reason category, so the
                composer/data residue (verify partials) is separated from
                the factory/layout residue (detect-rejects) at a glance.
  (2) CLUSTER — for one chosen detect-reject category, re-run the engine's
                non-raising `diagnose` LIVE and histogram by FIRST-DIVERGENCE
                site. N opaque "player_code_mismatch" collapse into a few
                actionable clusters, each with a representative + the bytes at
                the divergence site (ref vs member) so the cause is readable.

Because the cluster step runs diagnose against the CURRENT factory (not the
stale jsonl), re-running it after a factory fix shows the cluster shrink — a
cheap fix-impact measurement that needs no full re-batch (an 'ok' bucket
counts members the current factory now accepts).

This automates the "stratify by first-diff bucket" methodology (CLAUDE.md
wide-family iteration) previously done by hand each family.

Wired today: dmc_v5. Adding a family = one ENGINES entry: a diagnose(path)
-> dict (carrying 'status', and for code mismatches 'site'/'kind'), a
cluster_key(result) and a context(path, result) string.
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# ----------------------------------------------------------------------------
# per-engine registry
# ----------------------------------------------------------------------------
def _dmc_v5_diagnose(path):
    from pipelines.dmc.v5 import factory as F
    return F.v5_diagnose(path)


def _dmc_v5_cluster_key(r):
    st = r['status']
    if st == 'player_code_mismatch':
        # split opcode mismatches by the differing member byte, so a trampoline
        # (4C JMP) doesn't lump with an LDA-abs sub-version at the same site.
        suffix = f"=${r['member']:02X}" if r['kind'] == 'opcode' else ''
        return (f"${r['site']:04X}", r['kind'] + suffix)
    if st == 'init_skeleton':
        return ('init_skeleton', f"${r['site']:04X}")
    return (st, '')


def _dmc_v5_context(path, r):
    from pipelines.dmc.v5 import factory as F
    mem, s = F._load(os.path.join('hvsc84', path))
    base, it, jt, layout = F._detect_v5(mem, s)
    if base is None:
        return f"status={r['status']} (no base; load=${s['load']:04X} play=${s['play']:04X})"
    delta = base - 0x1000
    out = (f"base=${base:04X} delta=${delta & 0xFFFF:04X} init=${it:04X} "
           f"play=${s['play']:04X} load=${s['load']:04X}")
    if r['status'] == 'player_code_mismatch':
        ref = {pc: (L, rb, cls) for pc, L, rb, cls in F._v5_play_ref()}
        site = r['site']
        if site in ref:
            L, rb, cls = ref[site]
            a = site + delta
            out += (f"  |  @${site:04X} [{cls}] ref={rb.hex()} "
                    f"member={bytes(mem[a:a + L]).hex()}")
    return out


ENGINES = {
    'dmc_v5': {
        'diagnose': _dmc_v5_diagnose,
        'cluster_key': _dmc_v5_cluster_key,
        'context': _dmc_v5_context,
    },
}


# ----------------------------------------------------------------------------
# stage 1 — census (family-agnostic; reads the batch jsonl)
# ----------------------------------------------------------------------------
def _norm_reason(reason):
    """Collapse per-member noise (hex addresses, line/col numbers) so error
    messages of the same shape bucket together in the census."""
    import re
    reason = reason.split('\n', 1)[0]
    reason = re.sub(r'\$[0-9A-Fa-f]+', '$?', reason)
    reason = re.sub(r'line \d+, column \d+', 'line N, column M', reason)
    return reason.strip()


def _census_key(r):
    st = r.get('status')
    if st in ('full', 'partial'):
        return st
    return _norm_reason(r.get('reason') or st or 'unknown')


def census(rows):
    cat = collections.Counter(_census_key(r) for r in rows)
    return cat


def print_census(cat, total):
    print(f"=== census ({total} members) ===")
    # order: full, partial, then detect-rejects by size
    head = [k for k in ('full', 'partial') if k in cat]
    rest = sorted((k for k in cat if k not in head),
                  key=lambda k: -cat[k])
    for k in head + rest:
        tag = ('verify' if k == 'partial' else
               'OK' if k == 'full' else 'detect-reject/error')
        print(f"  {cat[k]:5d}  {k:<28} [{tag}]")
    print()


# ----------------------------------------------------------------------------
# stage 2b — cluster VERIFY PARTIALS by first writelog divergence (universal:
# the batch tools record first_diff = [sub, state_match, [reg,val], [reg,val]];
# the SID register index maps to a chip-role independent of engine family).
# ----------------------------------------------------------------------------
_REG_PARAM = ['freqlo', 'freqhi', 'pwlo', 'pwhi', 'ctrl', 'AD', 'SR']
_REG_GLOBAL = {21: 'filt cutoff lo', 22: 'filt cutoff hi',
               23: 'res/filt route', 24: 'mode/vol'}


def _reg_role(reg):
    if reg <= 20:
        return f"V{reg // 7 + 1} {_REG_PARAM[reg % 7]}"
    return _REG_GLOBAL.get(reg, f'reg{reg}')


def _partial_key(first_diff):
    if not first_diff:
        return ('no_first_diff', '')
    state_match = first_diff[1]
    if len(first_diff) < 4:          # [sub, state_match] only
        return ('check_A_state_only', '') if not state_match else ('unknown', '')
    reg = first_diff[2][0]
    return (f'${0xD400 + reg:04X}', _reg_role(reg))


def cluster_partials(rows, top, reps):
    parts = [r for r in rows if r.get('status') == 'partial']
    if not parts:
        print("(no verify partials)")
        return
    print(f"=== verify-partial clusters by first writelog divergence "
          f"({len(parts)} partials) ===")
    hist = collections.Counter()
    by_key = collections.defaultdict(list)
    for r in parts:
        key = _partial_key(r.get('first_diff'))
        hist[key] += 1
        by_key[key].append(r)
    for (reg, role), n in hist.most_common(top):
        print(f"  {n:4d}  {reg:>10}  {role}")
        for r in by_key[(reg, role)][:reps]:
            fd = r.get('first_diff') or []
            tail = f"  orig={fd[2]} mine={fd[3]}" if len(fd) >= 4 else ""
            print(f"          {r['path']}{tail}")
    shown = sum(n for _, n in hist.most_common(top))
    tail = sum(hist.values()) - shown
    if tail > 0:
        print(f"\n  ... {tail} more in {len(hist) - top} smaller clusters")


# ----------------------------------------------------------------------------
# stage 2 — cluster one detect-reject category by live first-divergence
# ----------------------------------------------------------------------------
def cluster(engine, rows, category, top, reps):
    eng = ENGINES[engine]
    members = [r['path'] for r in rows if _census_key(r) == category]
    if not members:
        print(f"(no members with reason {category!r})")
        return
    print(f"=== live re-cluster of {len(members)} '{category}' members "
          f"(current factory) ===")
    hist = collections.Counter()
    by_key = collections.defaultdict(list)
    diag = {}
    for p in members:
        r = eng['diagnose'](p)
        diag[p] = r
        key = eng['cluster_key'](r)
        hist[key] += 1
        by_key[key].append(p)

    now_ok = sum(n for k, n in hist.items() if k[0] == 'ok')
    if now_ok:
        print(f"  ** {now_ok} now ACCEPTED by the current factory "
              f"(cluster resolved) **\n")
    for (site, kind), n in hist.most_common(top):
        label = f"{site} {kind}".strip()
        print(f"  {n:4d}  {label}")
        for p in by_key[(site, kind)][:reps]:
            print(f"          {p}")
            print(f"            {eng['context'](p, diag[p])}")
    shown = sum(n for _, n in hist.most_common(top))
    tail = sum(hist.values()) - shown
    if tail > 0:
        print(f"\n  ... {tail} more in {len(hist) - top} smaller clusters")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--engine', required=True, choices=sorted(ENGINES))
    ap.add_argument('--results', required=True,
                    help='batch results jsonl (one {path,status,reason} per line)')
    ap.add_argument('--cluster', default=None,
                    help="detect-reject reason to re-cluster live "
                         "(default: largest detect-reject category)")
    ap.add_argument('--partials', action='store_true',
                    help="cluster verify PARTIALS by first writelog divergence "
                         "(from the jsonl first_diff; no live re-run) instead "
                         "of the detect-reject residue")
    ap.add_argument('--top', type=int, default=10,
                    help='number of clusters to show (default 10)')
    ap.add_argument('--reps', type=int, default=2,
                    help='representatives per cluster (default 2)')
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.results) if l.strip()]
    cat = census(rows)
    print_census(cat, len(rows))

    if args.partials:
        cluster_partials(rows, args.top, args.reps)
        return

    category = args.cluster
    if category is None:
        rejects = [(k, v) for k, v in cat.items() if k not in ('full', 'partial')]
        if not rejects:
            print("no detect-reject residue to cluster.")
            return
        category = max(rejects, key=lambda kv: kv[1])[0]
        print(f"(auto-selected largest detect-reject category: {category!r})\n")
    cluster(args.engine, rows, category, args.top, args.reps)


if __name__ == '__main__':
    main()
