#!/usr/bin/env python3
"""dmc_canon_diff.py — enumerate DMC family-1 player-code deviations from canon.

Every DMC family-1 SID is (canonical player + relocation + per-member WEDGES) +
song data. The DMC editor's packer patches only the player's data-table OPERANDS
per song (they point at the member's tables); a hand-patch WEDGE instead flips an
OPCODE, or repoints an operand INTO the player's own code/state region. So
aligning each member's reachable player instructions to the canonical player
(pipelines/dmc/docs/dmc4_player_embedded_1000.bin) and diffing OPCODES +
in-player OPERAND targets surfaces the wedges A PRIORI — the exact deviations the
factory's `_*_probe` functions detect reactively, but enumerated in ONE pass over
the whole family, clustered by canonical site, and tagged handled-vs-NEW.

This is the proactive complement to the reactive one-wedge-at-a-time cadence:
instead of waiting for a write-log divergence, localizing it, and hand-writing a
probe, this lists every code deviation and every carrier up front — including
wedges hiding inside members that still verify FULL, and the true carrier count
of each (so a probe's coverage can be audited against ground truth).

Two deviation classes it detects (both relocation-invariant via linear align):
  * OPCODE   — a reachable instr whose opcode != canon at the aligned address
               (hold_gateoff $BC->$60, hr_prep_skip $20->$2C, pw_bound
               $4A->$17, dual $BD->$A6, d418_tail $8D->$20/$2C, ...).
  * REPOINT  — same opcode, but the 16-bit operand targets the player's own
               code/state ($1000-$17FF, minus the fixed freq/vibdepth tables)
               at a DIFFERENT address than canon (pw_dir_persist STA $1765->$17AB,
               pw_hi_const). Packer patches never point there (canon's data
               operands point BELOW $1000, at $09xx-$0Exx), so this is clean.

NOT detected (documented gaps): IMMEDIATE-value wedges (hr_preset LDA #$0F->#$XX,
cymbal_burst #$FF->#$XX) — same opcode, 1-byte immediate operand, a value tweak
not a structural patch; and INTERNALLY RE-ASSEMBLED members (their whole layout
moved so linear align doesn't hold) — reported as a separate count for a future
opcode-skeleton-align pass. DMC hand-patches are IN-PLACE (no byte insertion), so
linear alignment holds for canon-layout members.

Alignment: canon-layout members carry the canonical jump table
(`JMP base+$1D / JMP base+$85`); their addresses map linearly
(canon_addr = member_addr - base + $1000). A member without that JT (relocated
dispatch / family-2 / re-assembled) is counted separately, not linearly diffed.
A canon-base member with an implausibly large diff is flagged `anomalous` and
kept out of the clusters.

Usage:
    source src/env.sh
    python3 tools/dmc_canon_diff.py                       # family1, all
    python3 tools/dmc_canon_diff.py --members FILE.json    # explicit path list
    python3 tools/dmc_canon_diff.py --limit 300 --jobs 8   # quick sample
    python3 tools/dmc_canon_diff.py --new-only             # hide handled clusters
    python3 tools/dmc_canon_diff.py --csv tmp/wedges.csv   # per-carrier rows
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.jobs import default_jobs  # noqa: E402

# 16-bit operand targets that are LEGITIMATE per-song packer patches (never a
# wedge): canon's data operands point below $1000 ($09xx-$0Exx song tables), and
# the four code-addressed fixed tables. A REPOINT is only flagged when the canon
# operand sits in the player's own code/state window and is none of these.
_FIXED_TABLES = {0x1647, 0x16A7, 0x1018}          # freq_lo, freq_hi, d417 shadow
_PLAYER_LO, _PLAYER_HI = 0x1000, 0x17FF           # code + per-voice state window

# --family2 mode: diff against the carved family-2 reference player
# (pipelines/dmc/docs/dmc4_family2_player_1000.bin, from Kajun_Klog,
# $1000-$17B0). Family-2 keeps the 4-entry JT shape but init JMPs base+$37
# (canon $1D); play/all-off/sfx offsets $85/$62F/$63E are canon-shared. The
# $D417 routing shadow lives at $1034 (canon $1018); the instrument table at
# $17B0 is read via the canon $1227 operand site and is IN the player window,
# so per-member instr relocations surface as (bulk-filtered) repoints.
_F2 = False
_F2_CANON_PATH = os.path.join('pipelines', 'dmc', 'docs',
                              'dmc4_family2_player_1000.bin')
_F2_FIXED_TABLES = {0x1647, 0x16A7, 0x1034}
_F2_INIT_OFF = 0x37

# Known wedge INSTRUCTION sites (canonical address -> the factory probe that
# HANDLES it), from the `_*_probe` docstrings + the PoC + this tool's own
# validation. Windows over the instruction site (NOT the operand target); used
# only for the handled/NEW convenience tag, not for detection. Refine as the
# full-family sweep reveals each cluster's true site.
_KNOWN_SITES = [
    (0x1000, 0x100B, 'play-vector (every_play/unit_repeat/repeat)'),
    (0x10AC, 0x10AF, 'master_vol_reassert_filter_tail'),
    (0x10DD, 0x10E1, 'track_loop_hook (C13 dataflow)'),
    (0x11D9, 0x11DF, 'hardrestart_prep_skip'),
    (0x1255, 0x125F, 'hardrestart_smc_variant'),
    (0x1263, 0x1269, 'pulsewidth_dir_persist'),
    (0x124A, 0x1251, 'pulsewidth_bound_shift'),
    (0x12A5, 0x12AB, 'master_vol_reassert_filter_tail'),
    (0x172B, 0x1738, 'dual_freq_generator'),
    (0x17EF, 0x17EF, 'hold_gateoff'),
    (0x17FB, 0x17FF, 'hardrestart_preset/smc'),
    (0x1630, 0x1646, 'injected-wrapper ($16xx: d418/play_unit)'),
    (0x1174, 0x1185, 'rest/switch dispatch (rest_effects)'),
    (0x1848, 0x184E, 'hardrestart_smc_variant (sub_184B)'),
]

# Family-2 known sites: the 5 factory-probed write-stream knobs (RE_NOTES) +
# the generic wrapper windows. Refined as the f2 sweep reveals true sites.
_F2_KNOWN_SITES = [
    (0x1000, 0x100B, 'play-vector (every_play/unit_repeat/repeat)'),
    (0x10DD, 0x10E1, 'track_loop_hook (C13 dataflow)'),
    (0x11D9, 0x11DF, 'hard_restart (probed: none/helper)'),
    (0x1174, 0x1185, 'rest/switch dispatch (rest_effects probe)'),
    (0x129F, 0x12A3, 'filter-mode AND variant (probed)'),
    (0x12C9, 0x1300, 'note-init tail (cymbal_onset/vib_ramp probes)'),
    (0x133D, 0x1341, 'hold_gateoff (probed: mask_only/helper)'),
    (0x1630, 0x1646, 'injected-wrapper ($16xx: d418/play_unit)'),
]

_MNE = {0x8D: 'STA a', 0x9D: 'STA a,x', 0x99: 'STA a,y', 0xB9: 'LDA a,y',
        0xBD: 'LDA a,x', 0xAD: 'LDA a', 0xA9: 'LDA #', 0xA6: 'LDX z',
        0xBC: 'LDY a,x', 0x20: 'JSR', 0x4C: 'JMP', 0x2C: 'BIT', 0x60: 'RTS',
        0x4A: 'LSR A', 0x17: 'SLO z,x', 0xC8: 'INY', 0xE8: 'INX', 0xF0: 'BEQ',
        0xD0: 'BNE', 0xC9: 'CMP #', 0xEE: 'INC a', 0x48: 'PHA', 0x98: 'TYA',
        0x8A: 'TXA', 0x0D: 'ORA a', 0xE0: 'CPX #'}


def _mne(op):
    return _MNE.get(op, f'${op:02X}')


def _known(addr):
    for lo, hi, lbl in (_F2_KNOWN_SITES if _F2 else _KNOWN_SITES):
        if lo <= addr <= hi:
            return lbl
    return None


_CANON = None


def _canon_map():
    """{canon_addr: (opcode, operand16|None)} for the reference player's
    reachable instructions (cached per process)."""
    global _CANON
    if _CANON is None:
        from pipelines.dmc.v4 import dataflow as D
        if _F2:
            ref = open(os.path.join(ROOT, _F2_CANON_PATH), 'rb').read()
            cm = bytearray(0x10000)
            cm[0x1000:0x1000 + len(ref)] = ref
            _CANON = {a: (o, v) for a, o, v in
                      D._instrs(cm, 0x1000, 0x1003, (0x1006, 0x1009))}
        else:
            _CANON = {a: (o, v) for a, o, v in D._canon_instrs()}
    return _CANON


def _canon_base(mem, s):
    """The member's base iff it carries the canonical jump table
    (`JMP base+$1D / JMP base+$85`); else None (relocated dispatch / family-2 /
    re-assembled — not linearly alignable)."""
    load = s['load']
    init_off = _F2_INIT_OFF if _F2 else 0x1D
    for b in (s['play'] - 3, load):
        if (0 < b <= 0xFFFF - 6 and load <= b and mem[b] == 0x4C
                and mem[b + 3] == 0x4C
                and (mem[b + 1] | (mem[b + 2] << 8)) == (b + init_off) & 0xFFFF):
            return b
    return None


# opcode-diff count above which a "canon-base" member is treated as a variant,
# not a wedge carrier (keeps mis-detected family-2 / re-assembled out of the
# clusters). A real wedge carrier has a handful of diffs; the Groove wrapper
# (the busiest genuine case) is 10.
_ANOMALY_THRESHOLD = 40

# A moved state block / relocated table repoints MANY operand sites by the SAME
# delta (mv-cv); a WEDGE is an ISOLATED repoint. So within one member, any
# repoint-delta that recurs >= _RELOC_MIN times is a bulk relocation, not a
# wedge — its repoints are dropped (the state-block move is already handled by
# the extract's curnote/gatemask/dual_parity locating). Isolated repoints
# (e.g. pw_dir_persist's single store to an unused byte) survive.
_RELOC_MIN = 4


def _diff_member(rel: str) -> dict:
    """Diff one HVSC-relative member's reachable player code against canon.
    Returns {status, opcode:[(addr,co,mo)], repoint:[(addr,op,cv,mv)]}."""
    from pipelines.dmc.v4 import dataflow as D
    from pipelines.dmc.v4.factory import _load
    try:
        mem, s = _load(os.path.join(ROOT, 'hvsc85', rel))
    except Exception as e:
        return {'rel': rel, 'status': 'error', 'detail': f'{type(e).__name__}'}
    base = _canon_base(mem, s)
    if base is None:
        return {'rel': rel, 'status': 'reassembled'}
    try:
        # family-2 has a 2-entry JT sub-build (all-off/sfx slots zeroed) —
        # trace only from slots that actually hold a JMP.
        extras = tuple(e for e in (base + 6, base + 9) if mem[e] == 0x4C)
        mI = D._instrs(mem, base, base + 3, extras)
    except Exception:
        return {'rel': rel, 'status': 'error', 'detail': 'trace'}
    canon = _canon_map()
    shift = base - 0x1000
    opcode, repoint = [], []
    for a, mo, mv in mI:
        ca = a - shift
        cel = canon.get(ca)
        if cel is None:
            continue                         # member-only (post-wedge tail); skip
        co, cv = cel
        if co != mo:
            opcode.append((ca, co, mo))
        elif (cv is not None and mv is not None and mv != cv
                and _PLAYER_LO <= cv <= _PLAYER_HI
                and cv not in (_F2_FIXED_TABLES if _F2 else _FIXED_TABLES)):
            repoint.append((ca, mo, cv, mv))
    # drop bulk state-block/table relocations (a delta recurring >= _RELOC_MIN
    # times), keep isolated wedge repoints.
    reloc = 0
    if repoint:
        deltas = collections.Counter(mv - cv for _, _, cv, mv in repoint)
        bulk = {d for d, n in deltas.items() if n >= _RELOC_MIN}
        if bulk:
            kept = [t for t in repoint if (t[3] - t[2]) not in bulk]
            reloc = len(repoint) - len(kept)
            repoint = kept
    anomalous = len(opcode) > _ANOMALY_THRESHOLD
    return {'rel': rel, 'status': 'anomalous' if anomalous else 'canon',
            'opcode': opcode, 'repoint': repoint, 'reloc': reloc}


def _load_members(spec):
    if spec and spec != 'family1':
        return json.load(open(spec))
    fams = json.load(open(os.path.join(ROOT, 'tmp', 'dmc_families.json')))
    return sorted(fams.items(), key=lambda kv: -len(kv[1]))[0][1]


def _load_status(path):
    """{member_path: status} from a batch results jsonl (last row per path).
    Used to split each cluster's carriers into partial (= real conversion
    targets) vs full (= wedge already handled / write-neutral)."""
    st = {}
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        p = r.get('path')
        if p:
            st[p] = r.get('status')
    return st


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--members', default='family1',
                    help="'family1' (default) or a JSON path list")
    ap.add_argument('--jobs', type=int, default=default_jobs())
    ap.add_argument('--limit', type=int, default=0, help='diff only first N')
    ap.add_argument('--new-only', action='store_true',
                    help='hide clusters already handled by a probe')
    ap.add_argument('--csv', default='', help='write per-carrier rows to CSV')
    ap.add_argument('--status', default='',
                    help='batch results jsonl -> split each cluster into '
                         'partial/full carriers')
    ap.add_argument('--family2', action='store_true',
                    help='diff against the family-2 reference player '
                         '(init JMP base+$37; default members = '
                         'tmp/dmc_f2_members_85.json)')
    args = ap.parse_args()
    if args.family2:
        global _F2
        _F2 = True
        if args.members == 'family1':
            args.members = os.path.join(ROOT, 'tmp', 'dmc_f2_members_85.json')
    status_map = _load_status(args.status) if args.status else None

    members = _load_members(args.members)
    if args.limit:
        members = members[:args.limit]
    print(f'{len(members)} members, jobs={args.jobs}', flush=True)

    status = collections.Counter()
    n_reloc = 0
    # cluster -> set(members).  cluster key = ('op', addr, co, mo)  or
    #                                         ('repoint', addr, opcode)
    clusters = collections.defaultdict(set)
    rows = []                                            # for --csv
    with Pool(args.jobs) as pool:
        for i, r in enumerate(pool.imap_unordered(_diff_member, members,
                                                  chunksize=8)):
            status[r['status']] += 1
            if r.get('reloc'):
                n_reloc += 1
            if r['status'] in ('canon', 'anomalous'):
                for a, co, mo in r.get('opcode', []):
                    clusters[('op', a, co, mo)].add(r['rel'])
                    rows.append((r['rel'], f'${a:04X}', 'opcode',
                                 f'{_mne(co)}->{_mne(mo)}', f'${co:02X}->${mo:02X}'))
                for a, op, cv, mv in r.get('repoint', []):
                    clusters[('repoint', a, op)].add(r['rel'])
                    rows.append((r['rel'], f'${a:04X}', 'repoint',
                                 f'{_mne(op)} {cv:04X}->{mv:04X}', ''))
            if (i + 1) % 500 == 0:
                print(f'  {i+1}/{len(members)}  {dict(status)}', flush=True)

    print(f'\nstatus: {dict(status)}')
    print(f'canon-layout diffed: {status["canon"]}   '
          f'reassembled(not diffed): {status["reassembled"]}   '
          f'anomalous(>{_ANOMALY_THRESHOLD} diffs): {status["anomalous"]}   '
          f'error: {status["error"]}')
    print(f'members with a bulk state/table relocation filtered out: {n_reloc}')

    ranked = sorted(clusters.items(), key=lambda kv: -len(kv[1]))
    n_new = sum(1 for k, v in ranked if _known(k[1]) is None)
    print(f'\n{len(ranked)} deviation clusters ({n_new} NEW / unhandled):\n')
    print(f'  {"carriers":>8}  {"site":6} {"kind":8} {"transition":22}  tag')
    print('  ' + '-' * 64)
    for k, mem_set in ranked:
        addr = k[1]
        tag = _known(addr) or '*** NEW ***'
        if args.new_only and tag != '*** NEW ***':
            continue
        if k[0] == 'op':
            trans = f'{_mne(k[2])}->{_mne(k[3])} (${k[2]:02X}->${k[3]:02X})'
            kind = 'opcode'
        else:
            kind = 'repoint'
            trans = f'{_mne(k[2])} @operand'
        ex = sorted(mem_set)[0].rsplit('/', 1)[-1]
        split = ''
        if status_map is not None:
            sc = collections.Counter(status_map.get(m) for m in mem_set)
            split = (f'  [part={sc["partial"]} full={sc["full"]}'
                     f' err={sc["error"]} ?={sc[None]}]')
        print(f'  {len(mem_set):>8}  ${addr:04X} {kind:8} {trans:22}  {tag}'
              f'{split}   e.g. {ex}')

    if args.csv:
        with open(args.csv, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['member', 'canon_site', 'kind', 'transition', 'bytes'])
            w.writerows(sorted(rows))
        print(f'\nwrote {len(rows)} carrier rows -> {args.csv}')


if __name__ == '__main__':
    main()
