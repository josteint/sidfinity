#!/usr/bin/env python3
"""DMC V5 (family-3/5) wide batch — factory + USF pipeline + verify per member.

Streams results to tmp/dmc_v5_results.jsonl (crash-safe; resumes by skipping
done paths). Statuses: full / partial (with first_diff signature for
bucketing) / unsupported (typed factory reason) / error.

Usage:
    PYTHONPATH=tools/py65_lib:tools:src python3 tools/dmc_v5_family_batch.py \
        [--sample N] [--members FILE.json] [--out FILE.jsonl]
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

OUT = os.path.join(ROOT, 'tmp', 'dmc_v5_results.jsonl')
_F3 = '004e82fa5908e2706df85f5c4b500477e0b1bf96'   # family-3 (Katusha), 1461
_F5 = '18bcb61eaea9d835e99840b205489273f1e181a1'   # family-5 sibling, 34
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
    signal.alarm(900)
    try:
        from pipelines.dmc.v5.factory import dmc_v5_config, DMCV5Unsupported
        from pipelines.dmc.v5.verify_v5 import build_from_cfg
        from pipelines.hubbard.verify_cycle import (
            writelog_capture, writelog_per_irq_capture,
            compare_instruction_stream)
        from src.songlengths import get_durations
        from seed_disassembly import parse_psid
        import struct

        hvsc = os.path.join(ROOT, 'hvsc84')
        try:
            cfg = dmc_v5_config(rel, hvsc_root=hvsc)
        except DMCV5Unsupported as e:
            return {'path': rel, 'status': 'unsupported',
                    'reason': e.reason, 'detail': e.detail[:80]}
        orig = os.path.join(hvsc, rel)
        rebuilt = build_from_cfg(cfg, hvsc_root=hvsc)
        with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
            f.write(rebuilt)
            tmp = f.name
        try:
            durs = get_durations(orig, _db)
            n = parse_psid(orig)['songs']
            # PSID speed bits (offset $12): a set bit => that subtune runs off
            # the CIA1 timer (multispeed). Capture those PER play() (Trap C for
            # CIA — the flat per-frame capture phases init+play differently for
            # orig vs a rebuild with a different init length).
            speed = struct.unpack('>I', open(orig, 'rb').read()[0x12:0x16])[0]
            subs = {}
            ok = True
            first_diff = None
            flat_div = None
            for sub in range(n):
                dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
                dur = max(5.0, min(dur, 1500.0))
                cia = bool(speed & (1 << sub)) if sub < 32 else bool(speed & 1)
                cap = writelog_per_irq_capture if cia else writelog_capture
                a = cap(orig, subtune=sub, duration=dur)
                b = cap(tmp, subtune=sub, duration=dur)
                r = compare_instruction_stream(a, b, mode='trichotomy')
                subs[sub] = [bool(r['is_full']), r['play_match'],
                             r['play_overlap']]
                if not r['is_full']:
                    ok = False
                    if first_diff is None:
                        fd = r.get('first_play_diff')
                        first_diff = ([sub, bool(r['state_match'])]
                                      + (list(map(list, fd[1:])) if fd else []))
                    # RELIABLE clustering localizer (trichotomy first_diff has
                    # phantom-D418 noise): the FLAT-prefix first (reg,val)
                    # divergence of the PLAY stream. SKIP frame 0 (init) for the
                    # vblank capture (composer emits its own universal-reset
                    # init); the per-IRQ (CIA) capture already drops the init.
                    if flat_div is None:
                        skip0 = 0 if cia else 1
                        fla = [(w[1], w[2]) for k, fr in enumerate(a)
                               if k >= skip0 for w in fr]
                        flb = [(w[1], w[2]) for k, fr in enumerate(b)
                               if k >= skip0 for w in fr]
                        mm = 0
                        lim = min(len(fla), len(flb))
                        while mm < lim and fla[mm] == flb[mm]:
                            mm += 1
                        if mm < lim:
                            flat_div = [sub, mm, fla[mm][0], fla[mm][1],
                                        flb[mm][1]]
            return {'path': rel, 'status': 'full' if ok else 'partial',
                    'subs': subs, 'first_diff': first_diff,
                    'flat_div': flat_div}
        finally:
            os.unlink(tmp)
    except TimeoutError:
        return {'path': rel, 'status': 'error', 'reason': 'timeout'}
    except Exception as e:
        msg = str(e)
        if msg.startswith('unsupported:'):
            return {'path': rel, 'status': 'unsupported',
                    'reason': msg[len('unsupported:'):].split()[0],
                    'detail': msg[:80]}
        return {'path': rel, 'status': 'error',
                'reason': f'{type(e).__name__}: {e}'[:160]}
    finally:
        signal.alarm(0)


def main():
    global OUT
    members_file = None
    sample = 0
    args = sys.argv[1:]
    while args:
        a = args.pop(0)
        if a == '--sample':
            sample = int(args.pop(0))
        elif a == '--members':
            members_file = args.pop(0)
        elif a == '--out':
            OUT = args.pop(0)
    if members_file:
        members = json.load(open(members_file))
    else:
        fams = json.load(open(os.path.join(ROOT, 'tmp', 'dmc_families.json')))
        members = sorted(fams[_F3]) + sorted(fams[_F5])
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
