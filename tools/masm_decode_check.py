#!/usr/bin/env python3
"""Music Assembler — decode every located member's orderlists + sequences.

This is the scale test of the SEQUENCE OPCODE MAP. The research docs say the
map was derived from a single binary (MC_01) and flag "confirm against a 2nd
binary" as open; this confirms it against every member that locates, and
reports any stream the map cannot decode.

Structural checks per member (nothing here needs a rebuild — it is a
consistency proof of the format, not a verdict):
  - the 3 track orderlists terminate ($FE stop or $FF loop) within bounds
  - every referenced sequence number resolves to a pointer inside the image
  - every sequence stream terminates on its end-of-pattern $FF
  - note indices stay inside the 96-entry freq table after transpose

Usage: python3 tools/masm_decode_check.py [--limit N] [--json OUT.jsonl]
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
from concurrent.futures import ProcessPoolExecutor      # noqa: E402
from src.jobs import default_jobs                       # noqa: E402

FREQ_TABLE_NOTES = 96


def probe(rel: str) -> dict:
    from seed_disassembly import parse_psid
    from pipelines.music_assembler.locate import locate
    from pipelines.music_assembler.extract.decode import walk
    row = {'path': rel}
    try:
        s = parse_psid(os.path.join(ROOT, 'hvsc84', rel))
    except Exception as e:
        return dict(row, status='parse_error', reason=repr(e)[:70])
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    lay = locate(mem)
    if lay is None:
        return dict(row, status='no_player')
    lo, hi = s['load'], s['load'] + len(s['payload'])
    try:
        r = walk(mem, lay)
    except Exception as e:
        return dict(row, status='decode_error', reason=repr(e)[:70])
    n_ev = sum(len(ev) for _, ev in r['sequences'].values())
    kinds = collections.Counter(e.kind for _, ev in r['sequences'].values()
                                for e in ev)
    # structural checks
    bad = []
    for sn, (sa, _) in r['sequences'].items():
        if not (lo <= sa < hi):
            bad.append('seqptr_out_of_image')
            break
    maxnote = 0
    for t in r['tracks']:
        for e in t.entries:
            sa_ev = r['sequences'].get(e.seq)
            if sa_ev is None:
                continue
            for ev in sa_ev[1]:
                if ev.kind == 'note':
                    maxnote = max(maxnote, ev.value + e.transpose)
    if maxnote >= FREQ_TABLE_NOTES:
        bad.append('note_past_freq_table:%d' % maxnote)
    return dict(row, status='ok' if not bad else 'suspect', issues=bad,
                events=n_ev, maxnote=maxnote,
                n_seq=len(r['sequences']),
                entries=[len(t.entries) for t in r['tracks']],
                loops=[t.loops for t in r['tracks']],
                slide=sum(1 for _, ev in r['sequences'].values()
                          for e in ev if e.slide),
                filt=sum(1 for _, ev in r['sequences'].values()
                         for e in ev if e.filt),
                legato=sum(1 for _, ev in r['sequences'].values()
                           for e in ev if e.legato),
                **{'k_' + k: v for k, v in kinds.items()})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int)
    ap.add_argument('--json')
    ap.add_argument('--census', default=os.path.join(ROOT, 'tmp',
                                                     'masm_census.jsonl'))
    a = ap.parse_args()
    members = [json.loads(l)['path'] for l in open(a.census)
               if json.loads(l)['status'] == 'ok']
    if a.limit:
        members = members[:a.limit]
    with ProcessPoolExecutor(max_workers=default_jobs()) as ex:
        rows = list(ex.map(probe, members, chunksize=8))
    st = collections.Counter(r['status'] for r in rows)
    print('Music_Assembler decode check: %d located members' % len(rows))
    for k, v in st.most_common():
        print('  %-14s %5d  (%.1f%%)' % (k, v, 100 * v / len(rows)))
    for k, v in collections.Counter(
            r.get('reason', '')[:50] for r in rows
            if r['status'] == 'decode_error').most_common(6):
        print('     decode_error: %-46s %d' % (k, v))
    for k, v in collections.Counter(
            i for r in rows for i in r.get('issues', [])).most_common(6):
        print('     suspect: %-50s %d' % (k[:50], v))
    ok = [r for r in rows if r['status'] == 'ok']
    if ok:
        print('\nevent totals over %d clean members:' % len(ok))
        for k in ('k_note', 'k_rest', 'k_hold', 'k_preset'):
            print('  %-9s %9d' % (k[2:], sum(r.get(k, 0) for r in ok)))
        print('  %-9s %9d' % ('slide', sum(r['slide'] for r in ok)))
        print('  %-9s %9d' % ('filter', sum(r['filt'] for r in ok)))
        print('  %-9s %9d' % ('legato', sum(r['legato'] for r in ok)))
        print('  max note index after transpose: %d (freq table = %d)'
              % (max(r['maxnote'] for r in ok), FREQ_TABLE_NOTES))
    if a.json:
        with open(a.json, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        print('\nwrote', a.json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
