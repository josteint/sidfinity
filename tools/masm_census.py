#!/usr/bin/env python3
"""Music Assembler family census — locate the player in every HVSC member.

The documented first migration task (pipelines/music_assembler/docs/README.md
"What remains"): fingerprint the 6,351 members into version groups BEFORE
bulk extraction, the way the FC standard-player census did.

Reports, over every `engine='Music_Assembler'` member:
  - how many carry a locatable player (and the failure reasons)
  - the signature's OFFSET FROM BASE, which is the build discriminator
  - the PSID vector convention (init=base+$48/play=base+$21 vs +$00/+$03)
  - the song-speed distribution

Usage: python3 tools/masm_census.py [--limit N] [--json OUT.jsonl]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, os.path.join(ROOT, "tools", "py65_lib"))
from concurrent.futures import ProcessPoolExecutor      # noqa: E402
from src import sid_db                                  # noqa: E402
from src.jobs import default_jobs                       # noqa: E402


def _run_init(s, max_steps: int = 2_000_000):
    """64K RAM after running the member's init under py65, or None."""
    try:
        from py65.devices.mpu6502 import MPU
        mpu = MPU()
        for i, b in enumerate(s['payload']):
            if s['load'] + i < 0x10000:
                mpu.memory[s['load'] + i] = b
        mpu.stPush(0x00)
        mpu.stPush(0x00)                       # RTS sentinel -> PC = $0001
        mpu.pc = s['init']
        mpu.a = (s.get('start', 1) or 1) - 1
        for _ in range(max_steps):
            if mpu.pc == 0x0001:
                return bytearray(mpu.memory[k] for k in range(0x10000))
            mpu.step()
    except Exception:
        pass
    return None


def probe(rel: str) -> dict:
    from seed_disassembly import parse_psid
    from pipelines.music_assembler.locate import locate, song_speed
    row = {'path': rel}
    try:
        s = parse_psid(os.path.join(ROOT, 'hvsc85', rel))
    except Exception as e:
        return dict(row, status='parse_error', reason=repr(e)[:60])
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    lay = locate(mem)
    materialised = False
    if lay is None:
        # PACKED / multi-loader member (ledger C26 + the DMC C31 relocating
        # wrapper): the player is unpacked or copied into RAM by init, so it
        # is not in the file image. Read what the ENGINE reads — run init
        # under py65 and retry.
        post = _run_init(s)
        if post is not None:
            lay = locate(post)
            materialised = lay is not None
            if lay is not None:
                mem = post
    if lay is None:
        return dict(row, status='no_player', load=s['load'],
                    init=s['init'], play=s['play'])
    # which PSID vector convention does the header use?
    if s['init'] == lay.base + 0x48 and s['play'] == lay.base + 0x21:
        conv = 'entry48'
    elif s['init'] == lay.base and s['play'] == lay.base + 3:
        conv = 'entry00'
    else:
        conv = 'other'
    return dict(row, status='ok', base=lay.base, sig_off=lay.sig_off,
                conv=conv, speed=song_speed(mem, lay), packed=materialised,
                seqptr_lo=lay.seqptr_lo, seqptr_hi=lay.seqptr_hi,
                load=s['load'], songs=s.get('songs', 1))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int)
    ap.add_argument('--json')
    a = ap.parse_args()
    members = [r[0] for r in sid_db.query(
        "SELECT path FROM sids WHERE engine='Music_Assembler' ORDER BY path")]
    if a.limit:
        members = members[:a.limit]
    with ProcessPoolExecutor(max_workers=default_jobs()) as ex:
        rows = list(ex.map(probe, members, chunksize=8))
    st = collections.Counter(r['status'] for r in rows)
    print('Music_Assembler census: %d members' % len(rows))
    for k, v in st.most_common():
        print('  %-12s %5d  (%.1f%%)' % (k, v, 100 * v / len(rows)))
    ok = [r for r in rows if r['status'] == 'ok']
    print('\nsignature offset from base (the build discriminator):')
    for off, n in collections.Counter(r['sig_off'] for r in ok).most_common(10):
        print('  +$%-5X %5d' % (off, n))
    print('\nPSID vector convention:')
    for c, n in collections.Counter(r['conv'] for r in ok).most_common():
        print('  %-8s %5d' % (c, n))
    print('\nsong speed:')
    for sp, n in collections.Counter(r['speed'] for r in ok).most_common(8):
        print('  %-5s %5d' % (sp, n))
    print('\npacked (player materialised by init):',
          sum(1 for r in ok if r.get('packed')))
    print('\nsubtunes:')
    for sn, n in collections.Counter(r['songs'] for r in ok).most_common(6):
        print('  %-5s %5d' % (sn, n))
    if a.json:
        with open(a.json, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        print('\nwrote', a.json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
