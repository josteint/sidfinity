#!/usr/bin/env python3
"""Family batch for Basic_Program: SID -> USF -> SID round-trip over all 486 members.

For every Basic_Program SID it: builds the semantic model, (if clean = perstep
freq-only) round-trips through a real USF v2 file, verifies the rebuilt SID's
writelog matches the original over the full-songlength window, and on FULL
mass-writes `<name>.usf` + `<name>.sidfinity.sid` next to the HVSC original.

Reports real (through-USF) coverage by status. Resumable: skips paths already in
the OUT jsonl (delete it to force a clean re-run).

  python3 pipelines/basic_program/family_batch.py [--write] [--limit N] [--stride S]

Without --write it only measures coverage (no .usf/.sidfinity.sid emitted).
"""
import os, sys, json, argparse, subprocess
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, 'src'))
from pipelines.basic_program.semantic_lift import build_model, build_psid
from pipelines.basic_program import usf_roundtrip as RT
from pipelines.basic_program.proof_multivoice import verdict_basic
from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
from src.usf import write_file, parse_file
from src.code_fingerprint import code_fingerprint

# Resume-cache invalidation on code change (see src/code_fingerprint.py).
CODE_HASH = code_fingerprint('basic_program')

OUT = os.path.join(ROOT, 'tmp/basic_program_research/family_batch.jsonl')
TMPDIR = os.path.join(ROOT, 'tmp/basic_program_research/batch')


def _dur(songlen):
    return min(max((songlen or 10) * 1.1, 15.0), 120.0)


def process(args):
    relpath, songlen, do_write = args
    dur = _dur(songlen)
    base = os.path.splitext(os.path.basename(relpath))[0]
    res = {'path': relpath}
    try:
        status, match, la, lb, usf, sid_bytes = RT.best_attempt(relpath, dur, title=base[:31])
    except Exception as e:
        res.update(status='lift_crash', detail=type(e).__name__ + ': ' + str(e)[:60]); return res
    if status.startswith('unsupported:'):
        res.update(status='unsup_' + status.split(':', 1)[1]); return res
    if status == 'too_many_pitches':
        res.update(status='build_fail', detail='too_many_pitches'); return res
    if status == 'not_clean':
        res.update(status='not_clean'); return res
    res.update(status=status, match=match, len_a=la, len_b=lb)
    if status == 'FULL' and do_write:                 # mass-write next to the HVSC original
        dst = os.path.join(ROOT, 'hvsc84', os.path.dirname(relpath))
        write_file(usf, os.path.join(dst, base + '.usf'))
        with open(os.path.join(dst, base + '.sidfinity.sid'), 'wb') as f:
            f.write(sid_bytes)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true', help='mass-write .usf+.sidfinity.sid for FULL members')
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--stride', type=int, default=1)
    a = ap.parse_args()
    rows = subprocess.run(["duckdb", "-noheader", "-list", "-c",
        "SELECT path, COALESCE(songlength_s,10) FROM read_parquet('%s/hvsc84.parquet')"
        " WHERE engine='Basic_Program' ORDER BY path" % ROOT],
        capture_output=True, text=True).stdout.strip().split("\n")
    allwork = [(r.rsplit("|", 1)[0], float(r.rsplit("|", 1)[1])) for r in rows if r]
    work = allwork[::a.stride]
    if a.limit: work = work[:a.limit]
    done = {}
    if os.path.exists(OUT):
        with open(OUT) as f:
            for line in f:
                d = json.loads(line)
                if d.get('code_hash') == CODE_HASH:   # skip stale-code verdicts
                    done[d['path']] = d
    todo = [(p, s, a.write) for p, s in work if p not in done]
    print(f"family batch: {len(work)} members, {len(done)} cached, {len(todo)} to do"
          f"{' [WRITE]' if a.write else ''}", flush=True)
    results = list(done.values())
    with open(OUT, 'a') as fo, ProcessPoolExecutor(max_workers=8) as ex:
        for i, res in enumerate(ex.map(process, todo)):
            res['code_hash'] = CODE_HASH
            fo.write(json.dumps(res) + "\n"); fo.flush(); results.append(res)
            if (i + 1) % 25 == 0: print(f"  {i+1}/{len(todo)}", flush=True)
    results = [r for r in results if r['path'] in {p for p, _ in work}]
    st = Counter(r['status'] for r in results); n = len(results)
    print(f"\n=== Basic_Program through-USF COVERAGE: {st.get('FULL',0)}/{n} FULL "
          f"({100*st.get('FULL',0)/n:.1f}%) ===")
    for s, c in st.most_common(): print(f"  {s:26s} {c}")
    byst = defaultdict(list)
    for r in results:
        if r['status'] != 'FULL': byst[r['status']].append(r)
    print("\n=== residue examples ===")
    for s, items in sorted(byst.items(), key=lambda kv: -len(kv[1])):
        print(f"  [{s}] ({len(items)})")
        for r in items[:4]:
            ln = '' if 'match' not in r else ' m=%s a=%s b=%s' % (r['match'], r['len_a'], r['len_b'])
            print(f"     {r['path']}  {r.get('detail', '')}{ln}")


if __name__ == '__main__':
    main()
