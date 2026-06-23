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


def _cia_speed(sid_path: str) -> int:
    """PSID/RSID 32-bit `speed` field (bytes 0x12-0x16, big-endian). Bit N set
    => subtune N is CIA-timed (multispeed), clear => vblank. 0 for non-PSID."""
    with open(sid_path, 'rb') as f:
        b = f.read(0x16)
    if len(b) < 0x16 or b[:4] not in (b'PSID', b'RSID'):
        return 0
    return int.from_bytes(b[0x12:0x16], 'big')


def _is_cia_subtune(speed: int, st: int) -> bool:
    """True iff subtune `st` (0-indexed) is CIA-timed (bit 31 reused beyond 32)."""
    return bool((speed >> min(st, 31)) & 1)


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
        from pipelines.dmc.v4.factory import (dmc_v4_config, DMCV4Unsupported,
                                              frames_clear_adsr)
        from pipelines.dmc.v4.extract.to_usf import write_dmc_usf
        from pipelines.dmc.composer_asm import build_dmc_sid
        from pipelines.hubbard.verify_cycle import (
            writelog_capture, writelog_per_irq_capture,
            compare_instruction_stream)
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
            durs = get_durations(orig, _db)
            n = parse_psid(orig)['songs']
            speed = _cia_speed(orig)
            # Capture the original ONCE per subtune (reused for the mask_only
            # retry below — full-songlength, so the AD/SR-clear scan is reliable).
            origs = {}
            for sub in range(n):
                dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
                dur = max(5.0, min(dur, 1500.0))
                cia = _is_cia_subtune(speed, sub)
                # CIA-timed (multispeed) subtunes: play() does not align with
                # siddump's 19656-cycle frame buckets (Trap C) — capture PER
                # play(). Vblank subtunes use the flat per-frame capture.
                cap = writelog_per_irq_capture if cia else writelog_capture
                origs[sub] = (cap(orig, subtune=sub, duration=dur), dur, cia)

            def build_and_verify(hold_gateoff=None):
                usf = parse_file(write_dmc_usf(cfg, td, hvsc_root=hvsc))
                if hold_gateoff:
                    usf.params.fields['hold_gateoff'] = hold_gateoff
                tmp_sid = os.path.join(td, 'r.sid')
                open(tmp_sid, 'wb').write(build_dmc_sid(usf))
                subs = {}; ok = True; first_diff = None; flat_div = None
                for sub in range(n):
                    a, dur, cia = origs[sub]
                    cap = writelog_per_irq_capture if cia else writelog_capture
                    b = cap(tmp_sid, subtune=sub, duration=dur)
                    r = compare_instruction_stream(a, b, mode='trichotomy')
                    subs[sub] = [bool(r['is_full']), r['play_match'],
                                 r['play_overlap'], bool(r['state_match']),
                                 bool(r['close']), r['len_post_a'],
                                 r['len_post_b']]
                    if not r['is_full']:
                        ok = False
                        if first_diff is None:
                            fd = r.get('first_play_diff')
                            first_diff = ([sub, bool(r['state_match'])]
                                          + (list(map(list, fd[1:])) if fd else []))
                        # RELIABLE localization for clustering: the FLAT-prefix
                        # first (reg,val) divergence (cycle dropped). Trichotomy's
                        # first_play_diff lands on whatever reg sits at its
                        # recovered offset (spurious $D418 on shift mis-recovery);
                        # DMC inits MATCH so the flat prefix breaks at the TRUE
                        # divergence. Vblank only (CIA per-irq drops init).
                        if flat_div is None and not cia:
                            fla = [(w[1], w[2]) for fr in a for w in fr]
                            flb = [(w[1], w[2]) for fr in b for w in fr]
                            mm = 0
                            lim = min(len(fla), len(flb))
                            while mm < lim and fla[mm] == flb[mm]:
                                mm += 1
                            if mm < lim:
                                flat_div = [sub, mm, fla[mm][0], fla[mm][1],
                                            flb[mm][1]]
                return subs, ok, first_diff, flat_div

            subs, ok, first_diff, flat_div = build_and_verify()
            hold_gateoff = None
            # MASK-ONLY retry (freq-floor / sr,ad recovery): the composer defaults
            # to adsr_clear (canon sub_17EC clears AD+SR at a holding gate-off);
            # a member whose ORIGINAL never zeroes AD+SR is mask-only, and that
            # clear is a spurious extra write. Detect from the WRITE STREAM
            # (Core Tenet) — reusing the full-songlength orig captures so a
            # late-gate-off member isn't false-negatived (the 30s-probe trap that
            # regressed FULLs). Only retry NON-full members, so a FULL adsr_clear
            # member is never touched.
            if not ok and not any(frames_clear_adsr(origs[s][0])
                                  for s in range(n)):
                s2, ok2, fd2, fl2 = build_and_verify('mask_only')
                nfull = lambda ss: sum(1 for v in ss.values() if v[0])
                if ok2 or nfull(s2) > nfull(subs):
                    subs, ok, first_diff, flat_div = s2, ok2, fd2, fl2
                    hold_gateoff = 'mask_only'
            return {'path': rel, 'status': 'full' if ok else 'partial',
                    'subs': subs, 'first_diff': first_diff,
                    'flat_div': flat_div, 'hold_gateoff': hold_gateoff}
    except TimeoutError:
        return {'path': rel, 'status': 'error', 'reason': 'timeout'}
    except Exception as e:
        # extract-level refusals (offtable_live, zero_wave_table, ...) are
        # raised as RuntimeError('unsupported:<reason> ...') — a typed
        # architectural-limit refusal, not a crash. Bucket as unsupported.
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
