#!/usr/bin/env python3
"""dmc_v5_build_one.py — build + verify + localize ONE DMC V5 member.

The v5 counterpart of `dmc_build_one.py`. v5 had no per-member tool at all, so
every investigation hand-rolled the same cfg -> extract -> USF -> compose ->
capture -> compare chain in a throwaway script — three times in one session
before this existed.

Prints the DISPATCH FACTS first (base, player variant, CIA latch, subtune
count), because on this family they decide how to read everything after:
family-4 (the Jupiter41 variant, play +$95) is a DIFFERENT PLAYER sharing the
v5 data format, with its own 2-phase timing, $D416-only filter and no play-skip
counter. A canon-offset assumption made against a family-4 member is a
confidently wrong answer, the same way `dmc_state_addr` refuses a
non-canon-geometry v4 member.

`--localize` reports, per FAILING subtune, the first divergence of the
FLATTENED PLAY STREAM captured PER play() — not per siddump frame. That
matters here: v5's family-4 has a short init that fits init+play1 into siddump
frame 0 while our universal-reset init pushes play1 into frame 1, so a flat
per-frame compare misaligns by a whole frame and reports a meaningless
position 0 (Trap C via differing init length; ledger C21).

Usage:
    python3 tools/dmc_v5_build_one.py MUSICIANS/G/Ganja/Silicon_Dreams.sid \
        --verify --localize
    python3 tools/dmc_v5_build_one.py <rel> --usf out.usf --out out.sid
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.tslog import ts, phase                     # noqa: E402


def _flat(chunks):
    return [(w[-2], w[-1]) for c in chunks for w in c]


def localize(orig: str, rebuilt_path: str, sub: int, dur: float,
             window: int = 6) -> None:
    """First flat divergence of the per-play() stream, with context."""
    from pipelines.hubbard.verify_cycle import writelog_per_irq_capture
    a = writelog_per_irq_capture(orig, subtune=sub, duration=dur,
                                 keep_init=True)
    b = writelog_per_irq_capture(rebuilt_path, subtune=sub, duration=dur,
                                 keep_init=True)
    ts(f'  sub {sub}: orig play-chunk sizes {[len(c) for c in a[1:9]]}')
    ts(f'  sub {sub}: mine play-chunk sizes {[len(c) for c in b[1:9]]}')
    fa, fb = _flat(a[1:]), _flat(b[1:])
    n = min(len(fa), len(fb))
    d = next((i for i in range(n) if fa[i] != fb[i]), None)
    if d is None:
        ts(f'  sub {sub}: play streams agree over {n} writes; '
           f'lengths orig={len(fa)} mine={len(fb)} '
           f'({"LENGTH divergence" if len(fa) != len(fb) else "identical"})')
        return
    lo, hi = max(0, d - window), d + window
    ts(f'  sub {sub}: FIRST DIVERGENCE at flat play position {d} '
       f'(of orig {len(fa)} / mine {len(fb)})')
    ts(f'      orig ' + ' '.join(f'{r:02X}={v:02X}' for r, v in fa[lo:hi]))
    ts(f'      mine ' + ' '.join(f'{r:02X}={v:02X}' for r, v in fb[lo:hi]))
    r, v = fa[d]
    r2, v2 = fb[d]
    role = {0: 'V1 freq lo', 1: 'V1 freq hi', 2: 'V1 PW lo', 3: 'V1 PW hi',
            4: 'V1 ctrl', 5: 'V1 AD', 6: 'V1 SR',
            7: 'V2 freq lo', 8: 'V2 freq hi', 9: 'V2 PW lo', 10: 'V2 PW hi',
            11: 'V2 ctrl', 12: 'V2 AD', 13: 'V2 SR',
            14: 'V3 freq lo', 15: 'V3 freq hi', 16: 'V3 PW lo',
            17: 'V3 PW hi', 18: 'V3 ctrl', 19: 'V3 AD', 20: 'V3 SR',
            21: 'filter cut lo', 22: 'filter cut hi', 23: 'filter res/route',
            24: 'mode/volume'}
    ts(f'      orig ${0xD400 + r:04X} ({role.get(r, "?")}) = ${v:02X}   '
       f'mine ${0xD400 + r2:04X} ({role.get(r2, "?")}) = ${v2:02X}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sid', help='HVSC-relative path')
    ap.add_argument('--verify', action='store_true')
    ap.add_argument('--localize', action='store_true',
                    help='implies --verify; localize every FAILING subtune')
    ap.add_argument('--out', help='write the rebuilt .sid here')
    ap.add_argument('--usf', help='write the intermediate .usf here')
    a = ap.parse_args()
    hvsc = os.path.join(ROOT, 'hvsc85')
    orig = os.path.join(hvsc, a.sid)
    if not os.path.exists(orig):
        ts(f'no such member: {orig}')
        return 2

    from pipelines.dmc.v5.factory import dmc_v5_config, DMCV5Unsupported
    from pipelines.dmc.v5.extract.to_usf import write_v5_usf
    from pipelines.dmc.v5.from_usf import usf_to_model
    from pipelines.dmc.v5.composer_v5 import build_v5_sid
    from src.usf.parser import parse_file
    from seed_disassembly import parse_psid

    with phase(f'config {a.sid}'):
        try:
            cfg = dmc_v5_config(a.sid, hvsc_root=hvsc)
        except DMCV5Unsupported as e:
            ts(f'UNSUPPORTED: {e.reason}: {e.detail}')
            return 1
    variant = 'family-4 (Jupiter41, play +$95)' if getattr(
        cfg, 'family4', False) else 'family-3/5 (canon)'
    songs = parse_psid(orig)['songs']
    ts(f'BUILD PATH   base=${cfg.base:04X}  variant={variant}')
    ts(f'             cia_period=${cfg.cia_period:04X}  header songs={songs}'
       f'  n_songs={getattr(cfg, "n_songs", None)}'
       f'  post_init_sub={getattr(cfg, "post_init_sub", None)}')

    td = tempfile.mkdtemp(prefix='dmcv5_')
    with phase('extract -> USF'):
        usf_path = write_v5_usf(cfg, td, hvsc_root=hvsc)
        if a.usf:
            with open(a.usf, 'w') as f:
                f.write(open(usf_path).read())
            ts(f'usf -> {a.usf}')
    with phase('USF -> compose'):
        m = usf_to_model(parse_file(usf_path))
        sid = build_v5_sid(m)
        ts(f'{len(sid)} bytes')
    out = a.out
    if not out:
        out = os.path.join(td, 'rebuilt.sid')
    with open(out, 'wb') as f:
        f.write(sid)
    if a.out:
        ts(f'sid -> {a.out}')

    if not (a.verify or a.localize):
        return 0

    from pipelines.dmc.v5.verify_v5 import verify_v5
    from src.songlengths import load_database, get_durations
    with phase('verify (siddump ground truth)'):
        r = verify_v5(cfg, hvsc_root=hvsc)
    nf = sum(1 for s in r['subtunes'].values() if s['is_full'])
    ts(f'VERDICT {nf}/{len(r["subtunes"])} subtunes FULL  ok={r["ok"]}')
    for sub, s in sorted(r['subtunes'].items()):
        ts(f'  sub {sub}: full={s["is_full"]} state={s.get("state_match")} '
           f'play={s.get("play_match")}/{s.get("overlap")} '
           f'via={s.get("via", "flat")} fpd={s.get("first_play_diff")}')
    if a.localize:
        db = load_database(os.path.join(hvsc, 'DOCUMENTS', 'Songlengths.md5'))
        durs = get_durations(orig, db)
        with phase('localize failing subtunes'):
            for sub, s in sorted(r['subtunes'].items()):
                if s['is_full']:
                    continue
                dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
                localize(orig, out, sub, dur)
    return 0 if r['ok'] else 1


if __name__ == '__main__':
    sys.exit(main())
