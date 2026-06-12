#!/usr/bin/env python3
"""DMC family-1 wide batch — factory + full pipeline + verify per member.

Streams results to tmp/dmc_wide_results.jsonl (crash-safe; resumes by
skipping already-done paths). Statuses: full / partial (with
first_play_diff signature for bucketing) / unsupported (typed factory
reason) / error.

Usage:
    PYTHONPATH=tools/py65_lib:tools:src python3 tools/dmc_family_batch.py \
        [--sample N] [--members FILE.json]

--sample N    : run only every len/N-th member (load-spread triage)
--members F   : JSON file with the member path list (default: family 1
                from tmp/dmc_families.json)
"""
from __future__ import annotations

import json
import os
import signal
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

OUT = os.path.join(ROOT, 'tmp', 'dmc_wide_results.jsonl')

_db = None


def _worker_init():
    global _db
    from src.songlengths import load_database
    _db = load_database(os.path.join(ROOT, 'hvsc84', 'DOCUMENTS',
                                     'Songlengths.md5'))


def run_member(rel: str) -> dict:
    import tempfile
    signal.signal(signal.SIGALRM,
                  lambda *a: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(1500)
    try:
        from pipelines.dmc.v4.factory import dmc_v4_config, DMCV4Unsupported
        from pipelines.dmc.v4.extract.to_usf import write_dmc_usf
        from pipelines.dmc.composer_asm import build_dmc_sid
        from pipelines.hubbard.verify_cycle import (
            writelog_capture, compare_instruction_stream)
        from src.songlengths import get_durations
        from src.usf.parser import parse_file
        from seed_disassembly import parse_psid

        hvsc = os.path.join(ROOT, 'hvsc84')
        try:
            cfg = dmc_v4_config(rel, hvsc_root=hvsc)
        except DMCV4Unsupported as e:
            return {'path': rel, 'status': 'unsupported',
                    'reason': e.reason, 'detail': e.detail[:80]}
        orig = os.path.join(hvsc, rel)
        with tempfile.TemporaryDirectory() as td:
            usf_path = write_dmc_usf(cfg, td, hvsc_root=hvsc)
            rebuilt = build_dmc_sid(parse_file(usf_path))
            tmp_sid = os.path.join(td, 'r.sid')
            open(tmp_sid, 'wb').write(rebuilt)
            durs = get_durations(orig, _db)
            n = parse_psid(orig)['songs']
            subs = {}
            ok = True
            first_diff = None
            for sub in range(n):
                dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
                dur = max(5.0, min(dur, 1500.0))
                a = writelog_capture(orig, subtune=sub, duration=dur)
                b = writelog_capture(tmp_sid, subtune=sub, duration=dur)
                r = compare_instruction_stream(a, b, mode='trichotomy')
                subs[sub] = [bool(r['is_full']), r['play_match'],
                             r['play_overlap']]
                if not r['is_full']:
                    ok = False
                    if first_diff is None:
                        fd = r.get('first_play_diff')
                        first_diff = ([sub, bool(r['state_match'])]
                                      + (list(map(list, fd[1:])) if fd else []))
            return {'path': rel, 'status': 'full' if ok else 'partial',
                    'subs': subs, 'first_diff': first_diff}
    except TimeoutError:
        return {'path': rel, 'status': 'error', 'reason': 'timeout'}
    except Exception as e:
        return {'path': rel, 'status': 'error',
                'reason': f'{type(e).__name__}: {e}'[:160]}
    finally:
        signal.alarm(0)


def main():
    members_file = None
    sample = 0
    args = sys.argv[1:]
    while args:
        a = args.pop(0)
        if a == '--sample':
            sample = int(args.pop(0))
        elif a == '--members':
            members_file = args.pop(0)
    if members_file:
        members = json.load(open(members_file))
    else:
        fams = json.load(open(os.path.join(ROOT, 'tmp', 'dmc_families.json')))
        members = sorted(fams.items(), key=lambda kv: -len(kv[1]))[0][1]
    if sample:
        members = members[::max(1, len(members) // sample)][:sample]

    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            done = {json.loads(l)['path'] for l in f if l.strip()}
    todo = [m for m in members if m not in done]
    print(f'{len(members)} members, {len(done)} done, {len(todo)} to go',
          flush=True)

    import collections
    stats = collections.Counter()
    with open(OUT, 'a') as f, Pool(8, initializer=_worker_init) as pool:
        for i, rec in enumerate(pool.imap_unordered(run_member, todo,
                                                    chunksize=1)):
            f.write(json.dumps(rec) + '\n')
            f.flush()
            stats[rec['status'] if rec['status'] != 'unsupported'
                  else f"unsup:{rec['reason']}"] += 1
            if (i + 1) % 25 == 0 or i + 1 == len(todo):
                print(f'  {i+1}/{len(todo)}  {dict(stats)}', flush=True)
    print('DONE', dict(stats), flush=True)


if __name__ == '__main__':
    main()
