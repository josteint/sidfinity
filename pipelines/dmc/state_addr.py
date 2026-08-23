#!/usr/bin/env python3
"""DMC state-address resolver — the ORIG address and OUR composer label for
any engine state variable, for ONE member, relocation-aware.

WHY THIS EXISTS. CLAUDE.md already says "DO NOT hand-craft state maps (wrong
addresses bit hard last session)" and points at pipelines/future_composer/state_map_gen.py — but
that tool is FC-shaped, so DMC investigations kept hand-rolling addresses. The
DMC player is usually RELOCATED (base != $1000), so probing the canon $17xx
address watches unrelated RAM and returns a coherent-looking LIE. On
Industrial_Sci-Fi (base $9000) that produced fxf=$FF / route=$00 / claim always
0 while $D417=$F1 said voice 1 WAS routed — read as a genuine engine
difference, and it took a contradiction with the write stream to catch. TELL
for that failure: watched bytes that contradict the write stream, or a state
byte reading $FF where the code only ever stores small values.

Everything here is DERIVED, never transcribed: DMC_OFFTABLE_STATE is already
the canonical name -> address table, the factory already knows the member's
`base`, and assemble(..., return_labels=True) already knows our side.

Usage:
    # what does off-table window index 121 sonify on this member?
    python3 pipelines/dmc/state_addr.py MUSICIANS/B/Bayliss_Richard/Industrial_Sci-Fi.sid --idx 121

    # where do the orig and our rebuild keep the filter claim flag?
    python3 pipelines/dmc/state_addr.py <path> --var fclaim

    # every mapped variable, plus ready-to-paste siddump probes
    python3 pipelines/dmc/state_addr.py <path> --all --reg D40F

`--reg R` prints the paired `siddump --memwatch-on-write R <addr>` commands for
the orig and the rebuild — the C11 tracking measurement: run both, compare the
watched value event-by-event, and 0 mismatches means the var tracks and may be
mapped into the off-table redirect.
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

CANON_BASE = 0x1000


def _state_rows():
    """(orig_canon_addr, label, n_bytes) for every mapped state var, plus the
    two GATED rows — flagged, since they are emitted only for members that
    carry the corresponding feature."""
    from pipelines.dmc.composer_asm import (DMC_OFFTABLE_STATE,
                                            DMC_SECTPOS_ROW, DMC_WAVEPOS_ROW)
    rows = [(a, lbl, nb, '') for a, lbl, nb in DMC_OFFTABLE_STATE]
    for a, lbl, nb in (DMC_SECTPOS_ROW, DMC_WAVEPOS_ROW):
        rows.append((a, lbl, nb, ' (gated)'))
    return sorted(rows)


def _find_var(canon_addr: int):
    """The (label, base_addr, byte_index, note) owning a canon address."""
    for a, lbl, nb, note in _state_rows():
        if a <= canon_addr < a + nb:
            return lbl, a, canon_addr - a, note
    return None, None, None, ''


def _our_labels(rel: str):
    """Our composer's label -> address map for this member, or (None, why).

    Mirrors build_dmc_sid's OWN dispatch checks rather than re-deriving them
    (ledger C20 fourth layer: a tool that reconstructs a member by a different
    path than the builder reports confident nonsense). Labels are only
    meaningful for the single-chip asm; the multi-SID / compilation / hetero
    builders compose differently, so we say so instead of guessing."""
    from pipelines.dmc.build_one import build
    from src.usf.parser import parse_file
    from pipelines.dmc import composer_asm as CA
    from src.composer_runtime.xa65 import assemble
    # repo-local tmp/, never system /tmp (which gets wiped) — feedback_repo_tmp_dir
    scratch = os.path.join(ROOT, 'tmp')
    os.makedirs(scratch, exist_ok=True)
    td = tempfile.mkdtemp(dir=scratch)
    out_sid = os.path.join(td, 'reb.sid')
    out_usf = os.path.join(td, 'reb.usf')
    n_chips, _, _path = build(rel, out_sid, out_usf)
    usf = parse_file(out_usf)
    if getattr(usf, 'dmc_sfx', None) is not None:
        return None, out_sid, 'heterogeneous compilation build — labels N/A'
    if usf.subtunes and getattr(usf.subtunes[0], 'voices', None) \
            and len(usf.subtunes[0].voices) > 3:
        return None, out_sid, f'multi-SID build ({n_chips} chips) — labels N/A'
    asm = CA._sanitize_asm(CA.compose_dmc_asm(usf))
    _code, labels = assemble(asm, return_labels=True)
    return labels, out_sid, None


def main() -> int:
    ap = argparse.ArgumentParser(
        description='DMC engine state addresses for one member '
                    '(orig, relocation-aware) + our composer labels.')
    ap.add_argument('member', help='HVSC-relative path, e.g. '
                                   'MUSICIANS/B/Bayliss_Richard/Foo.sid')
    ap.add_argument('--var', help='state var name (e.g. fclaim, fcut, dur)')
    ap.add_argument('--idx', type=int,
                    help='off-table freq window index (0-255): report which '
                         'state var the hi AND lo reads at that index hit')
    ap.add_argument('--all', action='store_true',
                    help='list every mapped state var')
    ap.add_argument('--reg', help='SID register for the paired siddump probe '
                                  'command, e.g. D40F')
    ap.add_argument('--no-labels', action='store_true',
                    help='skip building the rebuild (orig addresses only)')
    args = ap.parse_args()
    os.chdir(ROOT)

    from pipelines.dmc.v4.factory import dmc_v4_config
    from pipelines.dmc.composer_asm import ORIG_FLO, ORIG_FHI, offtable_live_idx
    from pipelines.dmc.v4.extract.engine_model import (_canon_state_geometry,
                                                       _verify_window)

    cfg = dmc_v4_config(args.member, hvsc_root='hvsc85')
    if cfg is None:
        print(f'{args.member}: factory refused the member (not DMC v4 f1)')
        return 2
    base = cfg.base
    shift = base - CANON_BASE
    sid_path = os.path.join('hvsc85', args.member)

    print(f'member      : {args.member}')
    print(f'player base : ${base:04X}   canon $1000   shift '
          f'{"+" if shift >= 0 else "-"}${abs(shift):04X}'
          f'{"   ** RELOCATED **" if shift else ""}')
    print(f'freq tables : lo ${cfg.freq_lo_addr:04X}  hi ${cfg.freq_hi_addr:04X}')

    # MULTI-PLAYER members. A COMPILATION (ledger C31) packs N complete
    # players, each with its OWN state block and freq tables; a 2SID/3SID
    # member (C27) has one player per chip. The factory's `cfg.base` names only
    # ONE of them, so a canon offset resolves to N DIFFERENT addresses and
    # reporting a single one is exactly the confident-wrong-answer this tool
    # exists to refuse — the relocation trap in the docstring, one level out.
    # Para_Lander_DX cost ~20 min of treating an off-table byte as dynamic:
    # this printed `base $1000 / CANON / shift +$0000` while the divergent read
    # was at $2707, the OTHER player's slot.
    players = [(base, '')]
    submap = {}
    try:
        from pipelines.dmc.v4.compilation import detect_compilation
        from pipelines.dmc.v4.factory import dmc_v4_config_2sid
        cfgs2 = dmc_v4_config_2sid(args.member, hvsc_root='hvsc85')
        comp = None if cfgs2 else detect_compilation(args.member,
                                                     hvsc_root='hvsc85')
        if comp and len(comp.get('bases') or []) > 1:
            players = [(b, f'player {i}')
                       for i, b in enumerate(comp['bases'])]
            for k, (pi, song) in enumerate(comp['map']):
                submap.setdefault(pi, []).append(f'{k}(song {song})')
            kind = 'COMPILATION'
        elif cfgs2 and len(cfgs2) > 1:
            players = [(c.base, f'chip {i}') for i, c in enumerate(cfgs2)]
            kind = 'MULTI-SID'
        else:
            kind = None
        if kind:
            print(f'players     : {len(players)} players ({kind}) '
                  f'** every canon offset resolves ONCE PER PLAYER — the base '
                  f'above is only one of them **')
            for i, (b, tag) in enumerate(players):
                sub = ('  <- subtune ' + ', '.join(submap[i])
                       if i in submap else '')
                print(f'   {tag:9s} base ${b:04X}   shift '
                      f'{"+" if b >= CANON_BASE else "-"}'
                      f'${abs(b - CANON_BASE):04X}{sub}')
    except Exception as exc:                           # noqa: BLE001
        print(f'players     : multi-player check unavailable ({exc})')

    # Canon state GEOMETRY decides whether the redirect map means anything for
    # this member at all (page-3 variant builds moved the per-voice state, so
    # window idx N is unrelated code/data there — ledger C6 non-canon boundary).
    canon_geom = True
    try:
        from pipelines.dmc.v4.factory import _load
        mem = _load(sid_path)[0]
        canon_geom = _canon_state_geometry(mem, cfg)
        warn = ('' if canon_geom else
                '  ** the state block moved — the redirect map does NOT '
                'apply to this member **')
        print(f'state geom  : {"CANON" if canon_geom else "NON-CANON"}{warn}')
    except Exception as exc:                           # noqa: BLE001
        print(f'state geom  : unavailable ({exc})')

    labels, reb_sid, why = (None, None, 'skipped (--no-labels)')
    if not args.no_labels:
        try:
            labels, reb_sid, why = _our_labels(args.member)
        except Exception as exc:                       # noqa: BLE001
            labels, reb_sid, why = None, None, f'build failed: {exc}'
    if labels is None:
        print(f'our labels  : {why}')
    else:
        print(f'rebuild     : {reb_sid}')
    print()

    live = offtable_live_idx()

    def show(canon_addr: int, prefix: str = '') -> None:
        # one line per packed player (see the multi-player block above) — a
        # single address would be right for at most one of them.
        for pbase, ptag in players:
            _show_one(canon_addr, prefix, pbase - CANON_BASE,
                      f'[{ptag}] ' if ptag else '')

    def _show_one(canon_addr: int, prefix: str, shift: int, ptag: str) -> None:
        lbl, vbase, k, note = _find_var(canon_addr)
        addr = canon_addr + shift
        prefix = prefix + ptag
        if not canon_geom:
            # Refuse to name a variable we cannot locate. The whole point of
            # this tool is not to hand someone a confident wrong address, and
            # on a non-canon build the canon offset is unrelated code/data.
            print(f'{prefix}${addr:04X}  — NON-CANON geometry: this member '
                  f'does NOT keep its state at the canon offset. No address '
                  f'can be resolved from the map.')
            return
        if lbl is None:
            print(f'{prefix}${addr:04X}  (canon ${canon_addr:04X})  '
                  f'— not a mapped state var')
            return
        ours = ''
        if labels is not None and lbl in labels:
            ours = f'   ours: {lbl}+{k} @ ${labels[lbl] + k:04X}'
        print(f'{prefix}${addr:04X}  (canon ${canon_addr:04X})  '
              f'{lbl}+{k}{note}{ours}')

    if args.idx is not None:
        i = args.idx & 0xFF
        print(f'off-table window index {i}:')
        for name, tbl_canon, tbl_addr in (('hi', ORIG_FHI, cfg.freq_hi_addr),
                                          ('lo', ORIG_FLO, cfg.freq_lo_addr)):
            canon_addr = tbl_canon + i
            tag = '  [LIVE-served]' if i in live else '  [static window byte]'
            if len(players) > 1:
                # each packed player overruns into its OWN state block
                for pbase, ptag in players:
                    print(f'  {name} read -> '
                          f'${tbl_canon + i + pbase - CANON_BASE:04X}'
                          f'  [{ptag}]{tag}')
            else:
                print(f'  {name} read -> ${tbl_addr + i:04X}{tag}')
            show(canon_addr, prefix='       ')
        print()

    if args.var:
        hits = [(a, lbl, nb, note) for a, lbl, nb, note in _state_rows()
                if lbl == args.var]
        if not hits:
            print(f'no state var named {args.var!r}. Known: '
                  f'{", ".join(sorted({l for _, l, _, _ in _state_rows()}))}')
            return 2
        for a, lbl, nb, _note in hits:
            print(f'{lbl} ({nb} byte{"s" if nb > 1 else ""}):')
            for k in range(nb):
                show(a + k, prefix='  ')
            if canon_geom:
                for k in range(nb):
                    for name, tbl_canon in (('hi', ORIG_FHI), ('lo', ORIG_FLO)):
                        idx = (a + k) - tbl_canon
                        if 0 <= idx <= 255:
                            print(f'  sonified by off-table {name} index {idx}'
                                  f'{"  [LIVE-served]" if idx in live else ""}')
        print()

    if args.all:
        print('all mapped state vars (orig address, this member):')
        for a, lbl, nb, note in _state_rows():
            for k in range(nb):
                show(a + k, prefix='  ')
        print()

    if args.reg:
        dur = int(_verify_window(sid_path))
        targets = []
        if args.idx is not None:
            targets = [ORIG_FHI + (args.idx & 0xFF)]
        elif args.var:
            targets = [a + k for a, lbl, nb, _ in _state_rows()
                       if lbl == args.var for k in range(nb)]
        if not targets:
            print('(--reg needs --idx or --var to know what to watch)')
            return 0
        # watch the target in EVERY packed player — which one the subtune under
        # investigation actually runs is the thing you are trying to find out.
        orig_addrs = ','.join(f'{t + pbase - CANON_BASE:04X}'
                              for pbase, _tag in players for t in targets)
        print('tracking measurement (ledger C11) — run both, compare the '
              'watched value event-by-event:')
        print(f'  tools/siddump {sid_path} --duration {dur} '
              f'--memwatch-on-write {args.reg} {orig_addrs}')
        if labels is not None:
            ours = []
            for t in targets:
                lbl, _vb, k, _n = _find_var(t)
                if lbl in labels:
                    ours.append(f'{labels[lbl] + k:04X}')
            if ours:
                print(f'  tools/siddump {reb_sid} --duration {dur} '
                      f'--memwatch-on-write {args.reg} {",".join(ours)}')
        print('  0 mismatches over every event => the var tracks and may be '
              'mapped into DMC_OFFTABLE_STATE.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
