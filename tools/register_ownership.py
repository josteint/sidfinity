#!/usr/bin/env python3
"""register_ownership.py — MEASURE which code writes which SID register, so a
music+digi member can be given a SPLIT verdict.

=== WHY ===

A member that plays digi CONCURRENTLY with music carries both verification
modes in one stream: the music is Mode 1 (flat `(reg,val)`, cycles are
observation) and the digi is Mode 2 (cycle-strict, because the write timing
IS the waveform).  `docs/digi_parametrization_proposal.md` §5 proposes
splitting the captured stream BY REGISTER — the C27/C28 "verify each
substream in its own mode" shape applied to register ownership instead of
chip tag — on the premise that **the digi engine owns $D418 exclusively
during play**.

That premise is a measurement, and the proposal says so:

    "PRECONDITION to confirm per family: ... any member where music still
     writes $D418 needs an attribution rule before this verdict shape is
     trusted."

This tool is that confirmation.  It answers, per member: which PCs write
each SID register, and is the digi register set disjoint from the music's?

=== HOW (engine-blind) ===

1. Capture `--writelog --raw` and find the frame window with the most
   activity in the candidate digi register.  ⚠ Index by RAW siddump frame:
   `writelog_capture`'s frame list is COMPACTED to writes-only frames
   (ledger C36), so its index is NOT a siddump frame and a window chosen
   from it lands somewhere else entirely — measured here on
   Lady_with_the_Red_Dress, where compacted 200-202 is a silent window and
   raw 204-206 is the busy one.
2. `--pc-trace` that window and attribute every $D4xx store to the exact PC
   of its store instruction.
3. Classify each PC as DIGI-RATE or FRAME-RATE by how often it fires per
   frame.  A digi player writes its output register hundreds of times a
   frame; a music player writes any register a handful of times.  No engine
   name, no address range, no signature — the pacing is the discriminator.
4. Report ownership: for each register, which rate-class writes it; and the
   verdict `exclusive` / `shared` / `no_digi`.

RSID is handled (`--force-rsid`): every self-driven digi member is RSID and
siddump skips those by default.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.tslog import ts, phase          # noqa: E402

SIDDUMP = os.path.join(ROOT, 'tools', 'siddump')

_PC = re.compile(r'^\s*([0-9a-fA-F]{4})\s+\S\s+[0-9a-fA-F]{2}\s')
# The pc-trace prints an indexed store as `STAay d400,Y [d400]` and an
# absolute store as `STAa  d418`.  Both forms must be matched or the
# attribution silently misses a whole engine.
_EFF = re.compile(r'\[d([4-7])([0-9a-fA-F]{2})\]', re.I)
_ABS = re.compile(r'\bST[AXY]a\s+d([4-7])([0-9a-fA-F]{2})\s*$', re.I)

# A PC firing more often than this per frame is paced by an interrupt faster
# than the frame — i.e. a digi player.  A music player's busiest register
# store runs a few times per frame (per voice, per effect).  The gap between
# the two populations is two orders of magnitude, so the threshold is not a
# tuned knob; it is reported alongside the raw rate so the split is visible.
DIGI_RATE_PER_FRAME = 8.0


def busiest_window(sid: str, subtune: int, reg: int, duration: float,
                   width: int = 3) -> tuple:
    """(start_frame, end_frame, writes_in_window, total_writes_to_reg),
    in RAW siddump frame indices."""
    r = subprocess.run([SIDDUMP, sid, '--subtune', str(subtune + 1),
                        '--duration', str(duration), '--writelog', '--raw',
                        '--force-rsid'], capture_output=True, text=True)
    per = []
    for line in r.stdout.splitlines():
        n = 0
        if '|W:' in line:
            t = line.split('|W:', 1)[1].split(':')
            for i in range(0, len(t) - 2, 3):
                try:
                    if int(t[i + 1], 16) == reg:
                        n += 1
                except ValueError:
                    pass
        per.append(n)
    if not per:
        return (0, 0, 0, 0)
    best, bi = -1, 1
    for i in range(1, max(2, len(per) - width)):
        s = sum(per[i:i + width])
        if s > best:
            best, bi = s, i
    return (bi, bi + width - 1, best, sum(per))


def stores_in_window(sid: str, subtune: int, start: int, end: int) -> list:
    """[(pc, reg)] for every $D4xx store executed in raw frames start..end."""
    with tempfile.NamedTemporaryFile(suffix='.pc', delete=False) as f:
        pc_path = f.name
    try:
        subprocess.run([SIDDUMP, sid, '--subtune', str(subtune + 1),
                        '--duration', str((end + 3) / 50.0),
                        '--pc-trace', pc_path, str(start), str(end),
                        '--force-rsid'], capture_output=True, text=True)
        out = []
        pc = None
        with open(pc_path, errors='replace') as f:
            for line in f:
                m = _PC.match(line)
                if not m:
                    continue
                pc = int(m.group(1), 16)
                me = _EFF.search(line) or _ABS.search(line)
                if me:
                    out.append((pc, int(me.group(2), 16) & 0x1F))
        return out
    finally:
        try:
            os.unlink(pc_path)
        except OSError:
            pass


def measure(sid: str, subtune: int = 0, duration: float = 20.0,
            digi_reg: int = 0x18, width: int = 3) -> dict:
    s, e, n_win, n_tot = busiest_window(sid, subtune, digi_reg, duration,
                                        width)
    res = {'sid': os.path.relpath(sid, ROOT), 'subtune': subtune,
           'window': [s, e], f'reg{digi_reg:02X}_total': n_tot,
           f'reg{digi_reg:02X}_in_window': n_win}
    if n_tot == 0:
        res['verdict'] = 'no_digi'
        return res

    stores = stores_in_window(sid, subtune, s, e)
    if not stores:
        res['verdict'] = 'no_trace'
        return res

    frames = max(1, e - s + 1)
    per_pc = Counter(pc for pc, _ in stores)
    pc_regs = defaultdict(set)
    for pc, reg in stores:
        pc_regs[pc].add(reg)

    fast = {pc for pc, n in per_pc.items() if n / frames > DIGI_RATE_PER_FRAME}
    slow = set(per_pc) - fast

    fast_regs = set()
    for pc in fast:
        fast_regs |= pc_regs[pc]
    slow_regs = set()
    for pc in slow:
        slow_regs |= pc_regs[pc]

    res.update({
        'stores_in_window': len(stores),
        'frames_in_window': frames,
        'fast_pcs': sorted(f'{p:04X}' for p in fast),
        'fast_rate_per_frame': round(
            sum(per_pc[p] for p in fast) / frames, 1),
        'slow_rate_per_frame': round(
            sum(per_pc[p] for p in slow) / frames, 1),
        'fast_regs': sorted(f'{r:02X}' for r in fast_regs),
        'slow_regs': sorted(f'{r:02X}' for r in slow_regs),
        'overlap_regs': sorted(f'{r:02X}' for r in (fast_regs & slow_regs)),
    })
    if not fast:
        # The digi register is written, but by nothing running faster than
        # the frame — this is not a concurrent digi player.
        res['verdict'] = 'no_fast_writer'
    elif fast_regs & slow_regs:
        res['verdict'] = 'shared'
    elif fast_regs != {digi_reg}:
        # Exclusive, but the digi touches more than the assumed register —
        # the split is still clean, it just owns a bigger set.
        res['verdict'] = 'exclusive_wider'
    else:
        res['verdict'] = 'exclusive'
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('sids', nargs='*', help='HVSC-relative or absolute paths')
    ap.add_argument('--family', default=None,
                    help="measure a whole population: 'digi_organizer_paired'"
                         " | 'rayden' | 'digi_organizer_standalone'")
    ap.add_argument('--subtune', type=int, default=0)
    ap.add_argument('--duration', type=float, default=20.0)
    ap.add_argument('--digi-reg', default='18')
    ap.add_argument('--jobs', type=int, default=0)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()

    sids = list(a.sids)
    if a.family:
        from src import sid_db
        rows = sid_db.query("SELECT path, engines FROM sids "
                            "WHERE engines LIKE '%Digi-Organizer%' "
                            "OR path LIKE 'MUSICIANS/R/Rayden/%'")
        if a.family == 'digi_organizer_paired':
            sids = ['hvsc85/' + p for p, e in rows
                    if 'Digi-Organizer' in (e or '') and e != 'Digi-Organizer']
        elif a.family == 'digi_organizer_standalone':
            sids = ['hvsc85/' + p for p, e in rows if e == 'Digi-Organizer']
        elif a.family == 'rayden':
            sids = ['hvsc85/' + p for p, e in rows
                    if p.startswith('MUSICIANS/R/Rayden/')
                    and 'Digi' in (e or '')]
        else:
            print(f'unknown --family {a.family}', file=sys.stderr)
            return 1
        sids.sort()

    digi_reg = int(a.digi_reg, 16) & 0x1F
    from concurrent.futures import ProcessPoolExecutor, as_completed
    from src.jobs import default_jobs
    jobs = a.jobs or default_jobs('REGOWN_JOBS', cap=max(1, len(sids)))

    results = []
    with phase(f'measuring register ownership on {len(sids)} member(s), '
               f'{a.duration}s scan + a 3-frame pc-trace ({jobs} workers)'):
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            futs = {ex.submit(measure, os.path.join(ROOT, s) if not
                              os.path.isabs(s) else s,
                              a.subtune, a.duration, digi_reg): s
                    for s in sids}
            for k, fut in enumerate(as_completed(futs), 1):
                try:
                    results.append(fut.result())
                except Exception as e:
                    results.append({'sid': futs[fut],
                                    'verdict': f'error: {type(e).__name__}: {e}'})
                if k % 20 == 0:
                    ts(f'  {k}/{len(sids)}')

    results.sort(key=lambda r: r['sid'])
    if a.out:
        with open(os.path.join(ROOT, a.out), 'w') as fh:
            for r in results:
                fh.write(json.dumps(r) + '\n')

    print()
    print(f'=== ${digi_reg:02X} OWNERSHIP over {len(results)} member(s) ===')
    for v, n in Counter(r['verdict'] for r in results).most_common():
        print(f'  {n:5d}  {v}')
    bad = [r for r in results if r['verdict'] not in
           ('exclusive', 'exclusive_wider')]
    if bad:
        print('\n  members NOT cleanly split:')
        for r in bad[:40]:
            print(f"    {r['verdict']:<22} overlap="
                  f"{r.get('overlap_regs')} fast={r.get('fast_regs')} "
                  f"{r['sid']}")
    wider = [r for r in results if r['verdict'] == 'exclusive_wider']
    if wider:
        print('\n  digi owns MORE than the assumed register '
              '(still a clean split):')
        for r in wider[:20]:
            print(f"    fast={r['fast_regs']}  {r['sid']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
