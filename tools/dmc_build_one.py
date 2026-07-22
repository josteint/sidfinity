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


def build(rel: str, out_sid: str, out_usf: str | None):
    """Build `rel` (HVSC-relative) to `out_sid`; copy its .usf to `out_usf`
    if given. Returns (n_chips, usf_src_path)."""
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
    if cfgs2 is not None:
        usf_src = write_dmc_2sid_usf(cfgs2, td, hvsc_root=hv)
        nch = len(cfgs2)
    elif comp is not None:
        try:
            usf_src = write_dmc_compilation_usf(rel, comp, td, hvsc_root=hv)
        except Exception:
            # unmergeable compilation -> single-player fallback (never regress)
            comp = None
            usf_src = write_dmc_usf(dmc_v4_config(rel, hvsc_root=hv), td,
                                    hvsc_root=hv)
        nch = 1
    else:
        cfg = dmc_v4_config(rel, hvsc_root=hv)
        usf_src = write_dmc_usf(cfg, td, hvsc_root=hv)
        nch = 1
    usf = parse_file(usf_src)
    open(out_sid, 'wb').write(build_dmc_sid(usf))
    if out_usf:
        import shutil
        shutil.copy(usf_src, out_usf)
    return nch, usf_src


def verify(orig: str, reb: str, nch: int):
    """Trichotomy verdict per subtune (the family-batch gate). Prints one line
    per subtune + an overall FULL/PARTIAL verdict; returns True iff FULL."""
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
    allok = True
    for sub in range(n):
        cia = bool((speed >> min(sub, 31)) & 1)
        cap = writelog_per_irq_capture if cia else writelog_capture
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
        print(f"  sub {sub}: {'FULL' if isf else 'partial'}  "
              f"play_match={r['play_match']} play_overlap={r['play_overlap']} "
              f"state_match={r['state_match']} len_a={r['len_post_a']} len_b={r['len_post_b']}")
    print("VERDICT:", "FULL" if allok else "PARTIAL")
    return allok


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('path', help='HVSC-relative path (under hvsc84/)')
    ap.add_argument('--out', help='output .sid (default tmp/<name>.sidfinity.sid)')
    ap.add_argument('--usf', help='also write the .usf here')
    ap.add_argument('--verify', action='store_true', help='run the trichotomy verdict')
    ap.add_argument('--localize', action='store_true',
                    help='run tools/find_first_divergence.py')
    ap.add_argument('--subtune', type=int, default=0, help='subtune for --localize')
    args = ap.parse_args()

    rel = args.path
    orig = os.path.join(ROOT, 'hvsc84', rel)
    if not os.path.exists(orig):
        sys.exit(f"not found: {orig}")
    name = os.path.splitext(os.path.basename(rel))[0]
    out_sid = args.out or os.path.join(ROOT, 'tmp', f'{name}.sidfinity.sid')
    os.makedirs(os.path.dirname(out_sid), exist_ok=True)

    from src.code_fingerprint import code_fingerprint
    nch, _ = build(rel, out_sid, args.usf)
    print(f"built {out_sid}"
          + (f"  usf {args.usf}" if args.usf else "")
          + f"  chips={nch}  code_hash={code_fingerprint('dmc_v4')}")

    if args.verify:
        verify(orig, out_sid, nch)
    if args.localize:
        subprocess.run([sys.executable,
                        os.path.join(ROOT, 'tools', 'find_first_divergence.py'),
                        orig, out_sid, '--subtune', str(args.subtune)])


if __name__ == '__main__':
    main()
