#!/usr/bin/env python3
"""Coverage probe using the SEMANTIC lift (semantic_lift.build_model/build_player).
Compare against coverage_probe.py (the old freq+gate lift) to measure the gain.

  python3 pipelines/basic_program/semantic_probe.py [stride]   # default 6
"""
import os, sys, json, tempfile, subprocess
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))
from pipelines.basic_program import semantic_lift as S
from pipelines.basic_program.proof_twinkle import capture_real
from pipelines.basic_program.proof_multivoice import verdict_basic
from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream

REGROLE = {0x00: 'V1freq', 0x01: 'V1freq', 0x04: 'V1ctl', 0x05: 'V1ad', 0x06: 'V1sr',
           0x07: 'V2freq', 0x08: 'V2freq', 0x0b: 'V2ctl', 0x0e: 'V3freq', 0x0f: 'V3freq',
           0x12: 'V3ctl', 0x18: 'vol', 0x02: 'V1pw', 0x15: 'filt', 0x16: 'filt', 0x17: 'filt'}

def probe_one(args):
    relpath, songlen = args
    sid = os.path.join(ROOT, 'hvsc84', relpath)
    dur = min(max((songlen or 10) * 1.1, 15), 40)
    res = {'path': relpath}
    try:
        m = S.build_model(sid, dur)
    except Exception as e:
        res.update(status='lift_crash', detail=type(e).__name__ + ': ' + str(e)[:50]); return res
    if 'unsupported' in m:
        res.update(status='unsup_' + m['unsupported']); return res
    try:
        with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
            f.write(S.build_psid(m)); out = f.name
    except Exception as e:
        res.update(status='build_fail', detail=type(e).__name__ + ': ' + str(e)[:50]); return res
    try:
        a = writelog_capture(sid, 0, dur); b = writelog_capture(out, 0, dur)
        r = compare_instruction_stream(a, b, skip_init=False)
    finally:
        os.unlink(out)
    ok, ov, ln = verdict_basic(r)
    if ok:
        res.update(status='FULL'); return res
    if not ov:
        fa = [(rg, v) for fr in a for c, rg, v in fr]
        pos = r['match_all']; oreg = fa[pos][0] if pos < len(fa) else None
        res.update(status='overlap_diverge', detail=f"@{pos} {REGROLE.get(oreg, hex(oreg) if oreg is not None else '-')}")
    else:
        res.update(status='length_fail', detail=f"{abs(r['len_all_a']-r['len_all_b'])}")
    return res

def main():
    stride = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    rows = subprocess.run(["duckdb", "-noheader", "-list", "-c",
        "SELECT path, COALESCE(songlength_s,10) FROM read_parquet('%s/hvsc84.parquet')"
        " WHERE engine='Basic_Program' ORDER BY path" % ROOT],
        capture_output=True, text=True).stdout.strip().split("\n")
    allwork = [(r.rsplit("|", 1)[0], float(r.rsplit("|", 1)[1])) for r in rows if r]
    work = allwork[::stride]
    print(f"SEMANTIC probe: {len(work)}/{len(allwork)} tunes (stride {stride})", flush=True)
    results = []
    with ProcessPoolExecutor(max_workers=8) as ex:
        for i, res in enumerate(ex.map(probe_one, work)):
            results.append(res)
            if (i + 1) % 20 == 0: print(f"  {i+1}/{len(work)}", flush=True)
    with open(os.path.join(ROOT, 'tmp/basic_program_research/semantic_probe.jsonl'), 'w') as f:
        for r in results: f.write(json.dumps(r) + "\n")
    st = Counter(r['status'] for r in results); n = len(results)
    print(f"\n=== SEMANTIC COVERAGE: {st.get('FULL',0)}/{n} FULL ({100*st.get('FULL',0)/n:.0f}%) ===")
    for s, c in st.most_common(): print(f"  {s:22s} {c}")
    print("\n=== overlap_diverge first-diff regs ===")
    for k, c in Counter(r.get('detail','?').split()[-1] for r in results if r['status']=='overlap_diverge').most_common():
        print(f"  {k:8s} {c}")
    byst = defaultdict(list)
    for r in results:
        if r['status'] != 'FULL': byst[r['status']].append(r)
    print("\n=== examples ===")
    for s, items in sorted(byst.items(), key=lambda kv: -len(kv[1])):
        print(f"  [{s}] ({len(items)})")
        for r in items[:3]: print(f"     {r['path']}  {r.get('detail','')}")

if __name__ == '__main__':
    main()
