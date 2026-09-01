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
3. Ask whether the code that writes the digi register is DISJOINT from the
   code that writes everything else, by comparing the two sets of writer PC
   PAGES.  Ownership is a statement about which ENGINE owns a register, and
   an engine is a contiguous region of code — so locality is the honest
   discriminator.
4. Report the verdict `exclusive` / `shared` / `no_digi`, plus the raw PC
   sets so a caller can see exactly what was decided and why.

⚠ THE FIRST VERSION OF THIS TOOL CLASSIFIED BY PER-PC WRITE RATE ("a PC
firing >8x/frame is the digi") AND IT WAS WRONG — recorded here because the
wrong answer looked entirely plausible.  It reported 16 of the 92 paired
members `shared`; inspecting the PCs showed most were not shared at all:

  * Boot_Zak_v2's digi is an UNROLLED burst — 42 distinct PCs from $2218 to
    $2498, each writing $D418 twice per window, beside the main $0F09 loop.
    Every one of them falls under the rate threshold, so an unrolled digi
    read as "a slow writer therefore music".
  * Embarassed_Emotions writes $D418 from two zero-page NMI handlers plus a
    once-per-window $0A18 — again all digi.

Only Nibbles and Frogs_and_Flies were genuinely shared, and locality says
so cleanly: their $D418 writers include a PC in the same page as the
music's other-register writers ($85xx, $26xx), while Boot_Zak's $D418 pages
{$0F,$22-$24} are disjoint from its music pages {$10,$16}.  Rate is a
property of a LOOP; ownership is a property of an ENGINE.

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

# The scan window defaults to the member's own SONGLENGTH x 1.1 — the
# project's ratified verify window (feedback_subtune_frames_not_arbitrary),
# never an arbitrary N seconds.
# ⚠ IT WAS AN ARBITRARY 25s UNTIL 2026-09-01 AND THAT PRODUCED A WRONG
# ANSWER: six paired members reported `no_digi_in_window`, and re-scanning
# at 60s showed THREE of them running 31k-119k $D418 writes — their digi
# simply starts later. A fixed window turns "I did not look there" into a
# statement about the member.
def _songlength(sid_path: str, subtune: int) -> float:
    try:
        import glob
        from src import songlengths as SL
        db = SL.load_database(
            glob.glob(os.path.join(ROOT, 'hvsc85', 'DOCUMENTS',
                                   'Songlengths.md5'))[0])
        return max(20.0, SL.get_durations(sid_path, db)[subtune] * 1.1)
    except Exception:
        return 120.0

_PC = re.compile(r'^\s*([0-9a-fA-F]{4})\s+\S\s+[0-9a-fA-F]{2}\s')
# The pc-trace prints an indexed store as `STAay d400,Y [d400]` and an
# absolute store as `STAa  d418`.  Both forms must be matched or the
# attribution silently misses a whole engine.
_EFF = re.compile(r'\[d([4-7])([0-9a-fA-F]{2})\]', re.I)
_ABS = re.compile(r'\bST[AXY]a\s+d([4-7])([0-9a-fA-F]{2})\s*$', re.I)

# Writer PCs are grouped into code regions at this granularity.  A 6502
# player is a contiguous blob well under a page in its hot loop, and the
# music and digi engines in these members sit in different pages by
# construction (the digi core is copied to its own page at init).  Coarser
# than the true region, deliberately: an overlap then means "these two
# engines are close enough that we cannot tell them apart from the trace" —
# it flags for inspection instead of asserting a clean split.
PC_REGION_SHIFT = 8            # one page


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


def measure(sid: str, subtune: int = 0, duration: float = 0.0,
            digi_reg: int = 0x18, width: int = 3) -> dict:
    if not duration:
        duration = _songlength(sid, subtune)
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
    digi_pcs = {pc for pc, r in stores if r == digi_reg}
    other_pcs = {pc for pc, r in stores if r != digi_reg}
    digi_pages = {pc >> PC_REGION_SHIFT for pc in digi_pcs}
    other_pages = {pc >> PC_REGION_SHIFT for pc in other_pcs}
    shared_pages = digi_pages & other_pages
    # A PC that writes BOTH the digi register and another one is the
    # strongest possible evidence of a shared writer, independent of the
    # page grouping.
    dual_pcs = digi_pcs & other_pcs

    n_digi_writes = sum(1 for _, r in stores if r == digi_reg)
    res.update({
        'stores_in_window': len(stores),
        'frames_in_window': frames,
        'digi_writes_in_window': n_digi_writes,
        'digi_rate_per_frame': round(n_digi_writes / frames, 1),
        'digi_pcs': sorted(f'{p:04X}' for p in digi_pcs)[:64],
        'n_digi_pcs': len(digi_pcs),
        'digi_pages': sorted(f'{p:02X}xx' for p in digi_pages),
        'other_pages': sorted(f'{p:02X}xx' for p in other_pages),
        'shared_pages': sorted(f'{p:02X}xx' for p in shared_pages),
        'dual_pcs': sorted(f'{p:04X}' for p in dual_pcs),
        # writes to the digi register coming from a page that also writes
        # something else — the size of the exception, not just its presence
        'foreign_digi_writes': sum(
            1 for pc, r in stores
            if r == digi_reg and (pc >> PC_REGION_SHIFT) in shared_pages),
    })
    if n_digi_writes <= frames:
        # ⚠ NOT A THRESHOLD OVER A DERIVED QUANTITY — a physical argument.
        # Sample playback needs MANY samples per frame; at one write per
        # frame even at the member's DENSEST point, there is no digi to own
        # anything, and calling the result `exclusive` would dress two stray
        # $D418 writes up as evidence. (Measured: Xanadu and
        # Leave_the_Brain_with_Samples write $D418 2-3 times in 60 s and
        # were reported `exclusive` before this check existed.)
        res['verdict'] = 'no_digi_in_window'
    elif not other_pcs:
        # Nothing else writes the SID at all: this is a digi-ONLY member,
        # so "exclusive" would be vacuously true and would inflate any
        # count of members the split is PROVEN clean for.
        res['verdict'] = 'digi_only'
    elif shared_pages:
        res['verdict'] = 'shared'
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
    ap.add_argument('--duration', type=float, default=0.0,
                    help='seconds to scan; 0 = the member''s own '
                         'songlength x 1.1 (the ratified window)')
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
    win = f'{a.duration}s' if a.duration else 'full-songlength'
    with phase(f'measuring register ownership on {len(sids)} member(s), '
               f'{win} scan + a 3-frame pc-trace ({jobs} workers)'):
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
    bad = [r for r in results
           if r['verdict'] not in ('exclusive', 'digi_only')]
    if bad:
        print('\n  members NOT cleanly split:')
        for r in bad[:40]:
            print(f"    {r['verdict']:<18} "
                  f"digi {r.get('digi_rate_per_frame', 0):6.1f}/f from "
                  f"{r.get('n_digi_pcs', 0):3d} PC(s)  "
                  f"shared_pages={r.get('shared_pages')} "
                  f"foreign={r.get('foreign_digi_writes')} "
                  f"dual={r.get('dual_pcs')}  {r['sid']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
