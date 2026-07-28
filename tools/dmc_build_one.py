#!/usr/bin/env python3
"""Build ONE DMC (family-1 / 2SID) member through the full pipeline.

The DMC build path is a three-step Python API with no single CLI entry:
    dmc_v4_config / dmc_v4_config_2sid   (binary -> config)
    write_dmc_usf / write_dmc_2sid_usf   (config  -> .usf)
    build_dmc_sid                        (.usf    -> .sid bytes)
This wraps those for a single member so you can rebuild + diff against the
HVSC original in one command (the family batch only runs in bulk). It is the
promoted form of the throwaway tmp/build_one.py scratch helper.

Usage:
    python3 tools/dmc_build_one.py MUSICIANS/S/SilverFox/Seaside_99.sid
    python3 tools/dmc_build_one.py <path> --verify           # trichotomy verdict
    python3 tools/dmc_build_one.py <path> --localize          # first divergence
    python3 tools/dmc_build_one.py <path> --out foo.sid --usf foo.usf

<path> is HVSC-relative (under hvsc84/). --verify uses the SAME comparator the
family batch does (compare_instruction_stream, mode='trichotomy', per-IRQ
capture + scaled tolerance for CIA subtunes, per-chip for multi-SID).
"""
from __future__ import annotations

import argparse
import functools
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]


def _cia_speed(sid_path: str) -> int:
    b = open(sid_path, 'rb').read(0x16)
    if len(b) < 0x16 or b[:4] not in (b'PSID', b'RSID'):
        return 0
    return int.from_bytes(b[0x12:0x16], 'big')


def _path_note(kind: str, bases, submap) -> str:
    """One-line build-path description: which dispatch branch built this member
    and which player bases it packs. Printed always — see main()."""
    txt = f'{kind} ({len(bases)} players: ' + \
          ', '.join(f'${b:04X}' for b in bases) + ')'
    if submap:
        txt += '  subtune->player ' + ', '.join(
            f'{k}->{pi}(song {song})' for k, (pi, song) in enumerate(submap))
    return txt


def build(rel: str, out_sid: str, out_usf: str | None):
    """Build `rel` (HVSC-relative) to `out_sid`; copy its .usf to `out_usf`
    if given. Returns (n_chips, usf_src_path, build_path_description)."""
    from pipelines.dmc.v4.factory import dmc_v4_config, dmc_v4_config_2sid
    from pipelines.dmc.v4.extract.to_usf import (write_dmc_usf,
                                                 write_dmc_2sid_usf,
                                                 write_dmc_compilation_usf)
    from pipelines.dmc.v4.compilation import detect_compilation
    from pipelines.dmc.composer_asm import build_dmc_sid
    from src.usf.parser import parse_file
    hv = os.path.join(ROOT, 'hvsc84')
    td = tempfile.mkdtemp()
    cfgs2 = dmc_v4_config_2sid(rel, hvsc_root=hv)
    comp = None if cfgs2 is not None else detect_compilation(rel, hvsc_root=hv)
    builder = build_dmc_sid
    _kinds = (comp.get('kinds') or []) if comp else []
    if comp is not None and any(k != 'dmc' for k in _kinds):
        # HETEROGENEOUS (ledger C31/C35): the packed players are from
        # DIFFERENT families/composers (Music Assembler, or a DMC V5 player
        # beside V4 ones), so one DMC model cannot hold them. One UsfFile
        # whose subtunes name their engine; the engine-aware builder
        # dispatches. Same branch the family batch + the mass-write take —
        # this tool is the localizer they are read against, so its dispatch
        # must match.
        from pipelines.music_assembler.heterogeneous import (
            heterogeneous_to_usf, build_from_usf)
        from src.usf.writer import write_file
        usf_src = os.path.join(td, os.path.basename(rel)[:-4] + '.usf')
        write_file(heterogeneous_to_usf(rel, comp, hvsc_root=hv), usf_src)
        builder, nch = build_from_usf, 1
        path = _path_note('hetero_masm' if 'masm' in _kinds else 'hetero_v5',
                          comp['bases'], comp['map'])
    elif cfgs2 is not None:
        usf_src = write_dmc_2sid_usf(cfgs2, td, hvsc_root=hv)
        nch = len(cfgs2)
        path = _path_note('multisid', [c.base for c in cfgs2], None)
    elif comp is not None:
        try:
            usf_src = write_dmc_compilation_usf(rel, comp, td, hvsc_root=hv)
            path = _path_note('compilation', comp['bases'], comp['map'])
        except Exception as exc:
            # unmergeable compilation -> single-player fallback (never regress)
            usf_src = write_dmc_usf(dmc_v4_config(rel, hvsc_root=hv), td,
                                    hvsc_root=hv)
            path = (f"single (UNMERGEABLE compilation, "
                    f"{len(comp['bases'])} players: {exc})")
            comp = None
        nch = 1
    else:
        cfg = dmc_v4_config(rel, hvsc_root=hv)
        usf_src = write_dmc_usf(cfg, td, hvsc_root=hv)
        nch = 1
        path = f'single (base ${cfg.base:04X})'
    usf = parse_file(usf_src)
    open(out_sid, 'wb').write(builder(usf))
    if out_usf:
        import shutil
        shutil.copy(usf_src, out_usf)
    return nch, usf_src, path


def _localize_from_streams(a, b, dur: float, cia: bool, context: int = 8):
    """Print the first (reg, val) divergence from ALREADY-captured writelog
    streams — reusing verify()'s capture instead of a second full-songlength
    siddump run (the redundant re-capture that motivated this). Reuses
    find_first_divergence's flatten + formatter so the output matches the
    standalone tool. skip_init: vblank frame 0 IS the init (trichotomy differs
    there) → skip; per-IRQ capture already drops the init prefix → keep."""
    from find_first_divergence import _flatten, _format_div
    skip_init = not cia
    fo = _flatten(a, skip_init)
    fr = _flatten(b, skip_init)
    n = min(len(fo), len(fr))
    div = next((i for i in range(n) if fo[i][:2] != fr[i][:2]), None)
    print(_format_div({
        'duration_s': dur, 'orig_writes': len(fo), 'rebuild_writes': len(fr),
        'match_prefix': div if div is not None else n, 'first_div': div,
        'orig_flat': fo, 'rebuild_flat': fr}, context))


def verify(orig: str, reb: str, nch: int, localize: bool = False,
           only_sub: int | None = None):
    """Trichotomy verdict per subtune (the family-batch gate). Prints one line
    per subtune + an overall FULL/PARTIAL verdict; returns (allok, fails) where
    `fails` is the list of partial subtune indices. When `localize` is set, the
    first divergence of each failing subtune (or `only_sub`) is printed inline
    from the SAME capture — no second siddump run, and it always targets the
    subtune that actually diverges (sub 0 is often FULL in a compilation)."""
    from pipelines.hubbard.verify_cycle import (writelog_capture,
                                                writelog_per_irq_capture,
                                                compare_instruction_stream)
    from src.songlengths import load_database, get_durations
    from seed_disassembly import parse_psid
    db = load_database(os.path.join(ROOT, 'hvsc84', 'DOCUMENTS', 'Songlengths.md5'))
    durs = get_durations(orig, db)
    n = parse_psid(orig)['songs']
    speed = _cia_speed(orig)
    # siddump SKIPS an RSID original unless forced, and a skipped capture is
    # empty — a partial with nothing to localize. The rebuild is always PSID.
    rsid = open(orig, 'rb').read(4) == b'RSID'
    allok, fails = True, []
    for sub in range(n):
        cia = bool((speed >> min(sub, 31)) & 1)
        # keep_init: retain the |N init prefix so trichotomy Check A compares
        # REAL end-of-init chip states (a deferred per-chip init burst in the
        # orig is otherwise judged against invisible defaults — Kordiaukis).
        cap = (functools.partial(writelog_per_irq_capture, keep_init=True)
               if cia else writelog_capture)
        dur = max(5.0, min((durs[sub] if durs and sub < len(durs) else 110) * 1.1, 1500.0))
        a = cap(orig, subtune=sub, duration=dur, force_rsid=rsid)
        b = cap(reb, subtune=sub, duration=dur)
        ctol = 176
        if cia:
            ctol = max(176, 256 * max(1, round(len(a) / (dur * 50.0))))
        r = compare_instruction_stream(a, b, mode='trichotomy', close_tol=ctol,
                                       n_chips=nch)
        isf = bool(r['is_full'])
        if isf and abs(r['len_post_a'] - r['len_post_b']) > 176 and not r['audio_guaranteed']:
            isf = False
        allok = allok and isf
        if not isf:
            fails.append(sub)
        print(f"  sub {sub}: {'FULL' if isf else 'partial'}  "
              f"play_match={r['play_match']} play_overlap={r['play_overlap']} "
              f"state_match={r['state_match']} len_a={r['len_post_a']} len_b={r['len_post_b']}")
        if localize and not isf and (only_sub is None or sub == only_sub):
            if nch > 1:
                print("  (multi-chip: the flat localize below does not split by "
                      "chip — a cross-chip adjacency may show as the diff; C28)")
            print(f"  --- first divergence, subtune {sub} "
                  f"(from the capture above) ---")
            _localize_from_streams(a, b, dur, cia)
    print("VERDICT:", "FULL" if allok else "PARTIAL")
    return allok, fails


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', help='HVSC-relative path (under hvsc84/)')
    ap.add_argument('--out', help='output .sid (default tmp/<name>.sidfinity.sid)')
    ap.add_argument('--usf', help='also write the .usf here')
    ap.add_argument('--verify', action='store_true', help='run the trichotomy verdict')
    ap.add_argument('--localize', action='store_true',
                    help='localize the first divergence of the FAILING subtune, '
                         'inline from the verify capture (implies --verify)')
    ap.add_argument('--subtune', type=int, default=None,
                    help='localize only this subtune (default: every failing one)')
    args = ap.parse_args()

    rel = args.path
    orig = os.path.join(ROOT, 'hvsc84', rel)
    if not os.path.exists(orig):
        sys.exit(f"not found: {orig}")
    name = os.path.splitext(os.path.basename(rel))[0]
    out_sid = args.out or os.path.join(ROOT, 'tmp', f'{name}.sidfinity.sid')
    os.makedirs(os.path.dirname(out_sid), exist_ok=True)

    from src.code_fingerprint import code_fingerprint
    nch, _, path = build(rel, out_sid, args.usf)
    print(f"built {out_sid}"
          + (f"  usf {args.usf}" if args.usf else "")
          + f"  chips={nch}  code_hash={code_fingerprint('dmc_v4')}")
    # The BUILD PATH, always. A member packing several players resolves every
    # canon $17xx offset once per player, so an investigation that does not
    # know the path chases the wrong address (Para_Lander_DX, 2026-07-23).
    print(f"build path: {path}")

    if args.verify or args.localize:
        # --localize implies verify (it needs the per-subtune verdict to know
        # WHICH subtune to localize, and reuses that capture to do it).
        verify(orig, out_sid, nch, localize=args.localize, only_sub=args.subtune)


if __name__ == '__main__':
    main()
