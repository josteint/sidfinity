#!/usr/bin/env python3
"""GoatTracker V1 wide batch — full pipeline + FULL-songlength verify per tune.

Streams to tmp/gt_v1_results.jsonl (crash-safe; resumes by skipping done paths).
Verifies the $D400-$D418 instruction-sequence at FULL songlength (songlength_s *
1.1) — NEVER a duration cap. Caps undercount: they mask FULL on long tunes and
truncate the song-end tail (this bit twice — duration=None gave 0 frames, a 75s
cap masked Yummy_Pizza's FULL). The flat per-frame stream (frame 0 = init,
dropped) is the Mode-1 verdict, same as pipelines.goattracker.v1.verify.

Statuses: full / partial (with div_sig for bucketing) / detect_fail (extract
anchor miss / wave runaway) / build_fail / error / timeout. Records player
(tracker=player1 / gamemusic=player2) for per-player rates.

Usage:
    PYTHONPATH=src:. python3 pipelines/goattracker/v1/family_batch.py [--sample N] [--out FILE]

--sample N : run only every len/N-th member (load-spread triage)
"""
from __future__ import annotations

import collections
import json
import os
import signal
import sys
import tempfile
from multiprocessing import Pool

# this file lives at pipelines/goattracker/v1/ → repo root is 4 dirs up
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path[:0] = [os.path.join(ROOT, 'src'), ROOT]

OUT = os.path.join(ROOT, 'tmp', 'gt_v1_results.jsonl')

# Resume-cache invalidation on code change (see src/code_fingerprint.py).
from src.code_fingerprint import code_fingerprint  # noqa: E402
from src.jobs import default_jobs  # noqa: E402
CODE_HASH = code_fingerprint('goattracker_v1')


def run_member(item) -> dict:
    rel, sl = item
    signal.signal(signal.SIGALRM,
                  lambda *a: (_ for _ in ()).throw(TimeoutError()))
    signal.alarm(600)
    try:
        from pipelines.goattracker.v1.extract.engine_model import (
            parse_sid, extract)
        from pipelines.goattracker.v1.extract.to_usf import model_to_usf
        from pipelines.goattracker.v1.composer import build_v1_sid
        from pipelines.hubbard.verify_cycle import writelog_capture

        orig = os.path.join(ROOT, 'hvsc84', rel)
        try:
            song = extract(parse_sid(orig))
        except Exception as e:
            return {'path': rel, 'status': 'detect_fail',
                    'reason': f'{type(e).__name__}: {e}'[:120]}
        player = song.layout.player
        try:
            sid_bytes = build_v1_sid(model_to_usf(song))
        except Exception as e:
            return {'path': rel, 'status': 'build_fail', 'player': player,
                    'reason': f'{type(e).__name__}: {e}'[:120]}
        # FULL songlength (×1.1). Floor 8s for missing-songlength tunes; 600s
        # hard ceiling guards a runaway. NO small cap (the whole point).
        dur = max(8.0, min(float(sl) * 1.1 if sl else 40.0, 600.0))
        with tempfile.TemporaryDirectory() as td:
            tmp_sid = os.path.join(td, 'r.sid')
            open(tmp_sid, 'wb').write(sid_bytes)

            def flat(fr):
                return [(w[1], w[2]) for f in fr[1:] for w in f]
            a = flat(writelog_capture(orig, 0, duration=dur))
            b = flat(writelog_capture(tmp_sid, 0, duration=dur))
        n = min(len(a), len(b))
        first = next((i for i in range(n) if a[i] != b[i]), None)
        full = first is None and len(a) == len(b)
        rec = {'path': rel, 'status': 'full' if full else 'partial',
               'player': player, 'olen': len(a), 'rlen': len(b),
               'dur': round(dur, 1)}
        if not full:
            rec['first_div'] = first
            # div_sig: (reg, orig_val, reb_val) at the first mismatch — for
            # bucketing; 'len' = matched over the overlap, only total len differs
            # (often a song-end capture-boundary tail, near-converged).
            rec['div_sig'] = ([a[first][0], a[first][1], b[first][1]]
                              if first is not None else 'len')
        return rec
    except TimeoutError:
        return {'path': rel, 'status': 'timeout'}
    except Exception as e:
        return {'path': rel, 'status': 'error',
                'reason': f'{type(e).__name__}: {e}'[:160]}
    finally:
        signal.alarm(0)


def main():
    global OUT
    sample = 0
    args = sys.argv[1:]
    while args:
        a = args.pop(0)
        if a == '--sample':
            sample = int(args.pop(0))
        elif a == '--out':
            OUT = args.pop(0)

    from src import sid_db
    rows = sid_db.query("SELECT path, songlength_s FROM sids "
                        "WHERE engine='GoatTracker_V1.x' ORDER BY path")
    members = [(p, s or 0) for p, s in rows]
    if sample:
        members = members[::max(1, len(members) // sample)][:sample]

    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            for l in f:
                if not l.strip():
                    continue
                d = json.loads(l)
                if d.get('code_hash') == CODE_HASH:
                    done.add(d['path'])
    todo = [m for m in members if m[0] not in done]
    print(f'{len(members)} members, {len(done)} done, {len(todo)} to go',
          flush=True)

    stats = collections.Counter()
    with open(OUT, 'a') as f, Pool(default_jobs(cap=len(todo))) as pool:
        for i, rec in enumerate(pool.imap_unordered(run_member, todo,
                                                    chunksize=1)):
            rec['code_hash'] = CODE_HASH
            f.write(json.dumps(rec) + '\n')
            f.flush()
            key = (f"{rec['player'][:4]}:{rec['status']}"
                   if rec.get('player') else rec['status'])
            stats[key] += 1
            if (i + 1) % 50 == 0 or i + 1 == len(todo):
                print(f'  {i+1}/{len(todo)}  {dict(sorted(stats.items()))}',
                      flush=True)
    print('DONE', dict(sorted(stats.items())), flush=True)


if __name__ == '__main__':
    main()
