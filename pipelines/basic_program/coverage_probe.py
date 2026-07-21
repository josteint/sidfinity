#!/usr/bin/env python3
"""Coverage probe for the Basic_Program family.

Run the current lift -> build -> verify over a STRATIFIED sample of the 486
RSID-BASIC tunes and report how many reach FULL, clustering the failures by
root cause. Data-driven: tells us which structural variants actually matter
(and how often) before we productionize. The lift currently handles
single-voice + chord-per-step (gate-on/off per step); everything else should
fall into a labelled bucket here.

  python3 pipelines/basic_program/coverage_probe.py [stride]   # default 6 (~81 tunes)
"""
import os, sys, json, struct, tempfile, subprocess
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))
from pipelines.basic_program.proof_multivoice import (
    lift_mv, build_psid, verdict_basic, CTRL)
from pipelines.basic_program.proof_twinkle import capture_real
from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
from src.jobs import default_jobs

REGROLE = {0x00: 'V1freq', 0x01: 'V1freq', 0x04: 'V1ctl', 0x05: 'V1ad', 0x06: 'V1sr',
           0x07: 'V2freq', 0x08: 'V2freq', 0x0b: 'V2ctl', 0x0c: 'V2ad', 0x0d: 'V2sr',
           0x0e: 'V3freq', 0x0f: 'V3freq', 0x12: 'V3ctl', 0x18: 'vol',
           0x15: 'filt', 0x16: 'filt', 0x17: 'filt'}

def clock_of(sid):
    d = open(sid, 'rb').read()
    fl = struct.unpack('>H', d[118:120])[0]
    return {1: 'PAL', 2: 'NTSC', 3: 'PAL'}.get((fl >> 2) & 3, 'PAL')

def flat(frames):
    return [(r, v) for fr in frames for c, r, v in fr]

def probe_one(args):
    relpath, songlen = args
    sid = os.path.join(ROOT, 'hvsc84', relpath)
    dur = min(max((songlen or 10) * 1.1, 15), 40)
    res = {'path': relpath}
    try:
        clock = clock_of(sid)
        L = lift_mv(capture_real(sid, dur), clock=clock)
    except StopIteration:
        res.update(status='lift_no_gate'); return res
    except Exception as e:
        res.update(status='lift_crash', detail=type(e).__name__ + ': ' + str(e)[:60]); return res
    N = len(L['steps'])
    res['voices'] = len(L['voices']); res['steps'] = N; res['order'] = L['order']
    if N == 0:
        res.update(status='no_steps'); return res
    try:
        sidbytes = build_psid(L, 'probe')
        with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
            f.write(sidbytes); out = f.name
    except Exception as e:
        res.update(status='build_fail', detail=type(e).__name__ + ': ' + str(e)[:60]); return res
    try:
        orig = writelog_capture(sid, 0, dur)
        reb = writelog_capture(out, 0, dur)
        r = compare_instruction_stream(orig, reb, skip_init=False)
    finally:
        os.unlink(out)
    ok, overlap_ok, length_ok = verdict_basic(r)
    if ok:
        res.update(status='FULL'); return res
    if not overlap_ok:
        a, b = flat(orig), flat(reb)
        pos = r['match_all']
        oreg = a[pos][0] if pos < len(a) else None
        breg = b[pos][0] if pos < len(b) else None
        res.update(status='overlap_diverge', pos=pos,
                   detail=f"@{pos}/{min(len(a),len(b))} orig={REGROLE.get(oreg,hex(oreg) if oreg is not None else '-')} "
                          f"reb={REGROLE.get(breg,hex(breg) if breg is not None else '-')}")
    else:
        res.update(status='length_fail', detail=f"|{r['len_all_a']}-{r['len_all_b']}|={abs(r['len_all_a']-r['len_all_b'])}")
    return res

def main():
    stride = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    rows = subprocess.run(["duckdb", "-noheader", "-list", "-c",
        "SELECT path, COALESCE(songlength_s,10) FROM read_parquet('%s/hvsc84.parquet')"
        " WHERE engine='Basic_Program' ORDER BY path" % ROOT],
        capture_output=True, text=True).stdout.strip().split("\n")
    allwork = []
    for r in rows:
        if not r: continue
        p, sl = r.rsplit("|", 1); allwork.append((p, float(sl)))
    work = allwork[::stride]
    print(f"probing {len(work)}/{len(allwork)} tunes (stride {stride})", flush=True)
    results = []
    with ProcessPoolExecutor(max_workers=default_jobs(cap=len(work))) as ex:
        for i, res in enumerate(ex.map(probe_one, work)):
            results.append(res)
            if (i + 1) % 20 == 0: print(f"  {i+1}/{len(work)}", flush=True)
    out = os.path.join(ROOT, 'tmp/basic_program_research/coverage_probe.jsonl')
    with open(out, 'w') as f:
        for r in results: f.write(json.dumps(r) + "\n")
    # report
    st = Counter(r['status'] for r in results)
    n = len(results)
    print(f"\n=== COVERAGE: {st.get('FULL',0)}/{n} FULL ({100*st.get('FULL',0)/n:.0f}%) ===")
    for s, c in st.most_common():
        print(f"  {s:18s} {c}")
    # failure sub-clusters
    print("\n=== overlap_diverge sub-clusters (by first-diff reg role) ===")
    dv = Counter(r['detail'].split('orig=')[1].split(' reb=')[0] if 'orig=' in r.get('detail','') else '?'
                 for r in results if r['status'] == 'overlap_diverge')
    for k, c in dv.most_common(): print(f"  orig-reg {k:8s} {c}")
    print("\n=== voices among FULL vs non-FULL ===")
    for s in ('FULL', 'overlap_diverge'):
        vc = Counter(r.get('voices') for r in results if r['status'] == s)
        print(f"  {s}: {dict(sorted((k,v) for k,v in vc.items() if k is not None))}")
    # a few examples per failure status
    print("\n=== examples per failure bucket ===")
    byst = defaultdict(list)
    for r in results:
        if r['status'] != 'FULL': byst[r['status']].append(r)
    for s, items in byst.items():
        print(f"  [{s}]")
        for r in items[:4]:
            print(f"     {r['path']}  {r.get('detail','')}")
    print(f"\nfull results -> {out}")

if __name__ == '__main__':
    main()
