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

Usage: python3 pipelines/music_assembler/decode_check.py [--limit N] [--json OUT.jsonl]
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from concurrent.futures import ProcessPoolExecutor      # noqa: E402
from src.jobs import default_jobs                       # noqa: E402

FREQ_TABLE_NOTES = 96


def probe(rel: str) -> dict:
    from seed_disassembly import parse_psid
    from pipelines.music_assembler.locate import locate
    from pipelines.music_assembler.extract.decode import walk
    from pipelines.music_assembler.extract.presets import (preset_table,
                                                           presets)
    from pipelines.music_assembler.extract.arps import arp_tables, arp
    row = {'path': rel}
    try:
        s = parse_psid(os.path.join(ROOT, 'hvsc85', rel))
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
    # presets: only those the sequences actually select
    used = sorted({e.value for _, ev in r['sequences'].values()
                   for e in ev if e.kind == 'preset'})
    pt = preset_table(mem)
    pres = presets(mem, pt[0], max(used) + 1) if (pt and used) else []
    pres = [q for q in pres if q.id in set(used)]
    # arpeggios referenced by those presets
    at = arp_tables(mem)
    arps, arp_err = [], None
    if at and pres:
        for i in sorted({q.arp_index for q in pres if q.arp_index}):
            try:
                arps.append(arp(mem, at[0], at[1], i))
            except Exception as e:
                arp_err = repr(e)[:60]
                break
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
    if at is None and any(q.arp_index for q in pres):
        bad.append('arp_tables_not_located')
    if arp_err:
        bad.append('arp_decode:' + arp_err[:28])
    if pt is None:
        bad.append('preset_table_not_located')
    elif pres and not (lo <= pt[0] < hi):
        bad.append('preset_table_out_of_image')
    return dict(row, status='ok' if not bad else 'suspect', issues=bad,
                n_presets=len(pres), preset_base=pt[0] if pt else 0,
                vib=sum(1 for q in pres if q.vib_on),
                pslide=sum(1 for q in pres if q.pulse_slide_on),
                arp=sum(1 for q in pres if q.arp_index),
                waves=sorted({q.waveform for q in pres}),
                n_arps=len(arps),
                arp_steps=sum(len(A.steps) for A in arps),
                arp_loop=sum(1 for A in arps if A.loops),
                arp_abs=sum(1 for A in arps for st in A.steps if st.absolute),
                arp_rel=sum(1 for A in arps for st in A.steps
                            if not st.absolute),
                arp_filt=sum(1 for A in arps for st in A.steps if st.filter_lp),
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
        print('\npresets over the same members:')
        print('  %-22s %9d' % ('presets used', sum(r['n_presets'] for r in ok)))
        print('  %-22s %9d' % ('with vibrato ($10)', sum(r['vib'] for r in ok)))
        print('  %-22s %9d' % ('with pulse slide ($40)',
                               sum(r['pslide'] for r in ok)))
        print('  %-22s %9d' % ('with arpeggio', sum(r['arp'] for r in ok)))
        print('\narpeggios over the same members:')
        print('  %-22s %9d' % ('arpeggios decoded', sum(r['n_arps'] for r in ok)))
        print('  %-22s %9d' % ('steps', sum(r['arp_steps'] for r in ok)))
        print('  %-22s %9d' % ('looping ($FF)', sum(r['arp_loop'] for r in ok)))
        print('  %-22s %9d' % ('absolute steps', sum(r['arp_abs'] for r in ok)))
        print('  %-22s %9d' % ('relative steps', sum(r['arp_rel'] for r in ok)))
        print('  %-22s %9d' % ('steps setting filter',
                               sum(r['arp_filt'] for r in ok)))
        wv = collections.Counter(w for r in ok for w in r['waves'])
        print('  distinct waveform bytes, most common:',
              ['$%02X:%d' % (w, n) for w, n in wv.most_common(8)])
    if a.json:
        with open(a.json, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        print('\nwrote', a.json)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
