#!/usr/bin/env python3
"""write_timing_delta.py — MEASURE what Mode-1 verification deliberately
does not constrain: WHERE inside its play() invocation each SID write lands.

    THE CLAIM UNDER TEST (the_core_tenet.md, Trap B)
    "Within-frame cycle position is observation, not signal ... same writes
     in the same order at different cycles within a frame are equivalent",
    because "a normal player does all of its work in ONE burst per frame, so
    where inside that burst a write lands is inaudible."

The doctrine is sound and its boundary is documented (Techno-Rap, ledger
C27 — work deliberately spread sub-frame). What has never existed is a
NUMBER behind the word "inaudible". This tool produces it, for any member
whose rebuild verifies FULL under Mode 1.

=== WHAT IS MEASURED ===

For play invocation n of the original and of the rebuild, with writes
w[0..k] at absolute PHI1 cycles and play entry E(n):

  ONSET   d_onset(n) = (w_o[0] - E_o(n)) - (w_r[0] - E_r(n))
          How much later/earlier the whole burst starts after the IRQ.
          A CONSTANT onset delta is pure latency (inaudible by
          construction — it shifts the entire song); its VARIANCE across
          plays is jitter, and jitter is what a listener could hear.

  SPREAD  d_spread(n,i) = (w_o[i] - w_o[0]) - (w_r[i] - w_r[0])
          How much the burst's INTERNAL shape changed: the relative
          timing of gate edges, test bits and envelope starts against
          each other. This is Trap B's own quantity.

Both are reported against the 19656-cycle PAL frame, because "a fraction
of a frame" is the unit the claim is stated in.

=== WHY IT IS BUILT THIS WAY (four traps, all previously hit) ===

* siddump `--writelog` cycles are RELATIVE to a per-frame base, and a
  siddump frame advances ~18,000 CPU cycles while the PSID play() period
  is 19,656 (Trap C). So raw cycles DRIFT ~1,650/frame and cannot be
  compared across frames, let alone across two runs.
* The cure needs no siddump change: `--writelog-per-irq --per-irq-debug`
  already prints, on stderr, the per-frame `base` (absolute PHI1 at frame
  start) and `entry0` (absolute PHI1 of the frame's first play entry).
  base + relative = ABSOLUTE, and entries give a true per-play split.
  (siddump is inside `code_fingerprint`'s toolchain hash, so rebuilding
  it would invalidate every family's stored verdict rows — a read-only
  measurement must not pay that.)
* A frame with writes but NO play entry (the straddle tail of a play that
  entered in the previous frame) gets no stderr line, hence no base. Its
  writes are unplaceable, so the play that owns them is EXCLUDED and
  counted, never silently half-measured.
* Orig and rebuild are aligned by PLAY INDEX (entries since the first),
  not by siddump frame — the rebuild emits its own init (the trichotomy),
  so frame k of one is not frame k of the other.

The per-play regrouping is also a check the flat verdict structurally
cannot make: it compares each play's write sequence INDIVIDUALLY, so a
member that matches flat but redistributes writes across play boundaries
(the Trap B boundary class) is reported as a content mismatch, not as a
pass.
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.tslog import ts, phase  # noqa: E402

SIDDUMP = os.path.join(ROOT, 'tools', 'siddump')

# PAL play period in CPU cycles (63 cycles/line x 312 lines).  The unit the
# core tenet's claim is stated in: "within a frame".
PAL_FRAME_CYCLES = 19656


@dataclass
class Play:
    """One PSID play() invocation."""
    index: int
    entry: int                      # absolute PHI1 cycle of the play entry
    writes: list = field(default_factory=list)   # (abs_cycle, reg, val)
    clean: bool = True              # False if any of its writes were
                                    # unplaceable (base-less frame)
    exact_entry: bool = True        # False if the entry was interpolated
                                    # (multispeed frame, only entry0 printed)


@dataclass
class Capture:
    plays: list
    n_frames: int
    n_baseless_frames_with_writes: int
    period: float                   # measured play period in CPU cycles


def _parse_stderr(text: str) -> dict:
    """frame -> (base, nentries, entry0) from the `[per-irq]` debug lines."""
    out = {}
    for line in text.splitlines():
        if not line.startswith('[per-irq]'):
            continue
        kv = {}
        for tok in line.split()[1:]:
            if '=' in tok:
                k, v = tok.split('=', 1)
                kv[k] = v
        try:
            out[int(kv['frame'])] = (int(kv['base']), int(kv['nentries']),
                                     int(kv['entry0']))
        except (KeyError, ValueError):
            pass
    return out


def _parse_stdout(text: str) -> list:
    """One entry per siddump frame: the frame's writes in cycle order as
    (rel_cycle, reg, val).  `|N` (init prefix) chunks are dropped — the
    trichotomy compares play streams, not inits."""
    frames = []
    for line in text.splitlines():
        writes = []
        for seg in line.split('|')[1:]:
            if not seg.startswith('I'):
                continue          # |N = init prefix; anything else not ours
            toks = [t for t in seg[1:].split(':') if t != '']
            for i in range(0, len(toks) - 2, 3):
                try:
                    writes.append((int(toks[i]), int(toks[i + 1], 16),
                                   int(toks[i + 2], 16)))
                except ValueError:
                    pass
        frames.append(writes)
    return frames


def capture_plays(sid_path: str, subtune: int, duration: float) -> Capture:
    """Run siddump and regroup its write log into true play() invocations
    with ABSOLUTE cycle stamps.  `subtune` is 0-indexed (project
    convention); siddump's --subtune is 1-based."""
    cmd = [SIDDUMP, sid_path, '--subtune', str(subtune + 1),
           '--duration', str(duration),
           '--writelog-per-irq', '--per-irq-debug', '--raw']
    r = subprocess.run(cmd, capture_output=True, text=True)
    meta = _parse_stderr(r.stderr)
    frames = _parse_stdout(r.stdout)

    # --- the play period, measured, not assumed -------------------------
    # entry0(f+1) - entry0(f) spans exactly nentries(f) play periods.
    ordered = sorted(meta.items())
    ratios = []
    for (f0, (_b0, n0, e0)), (f1, (_b1, _n1, e1)) in zip(ordered, ordered[1:]):
        if f1 == f0 + 1 and n0 >= 1 and e1 > e0:
            ratios.append((e1 - e0) / n0)
    period = statistics.median(ratios) if ratios else float(PAL_FRAME_CYCLES)

    # --- reconstruct every play entry, absolute -------------------------
    entries = []            # (abs_cycle, exact)
    for f, (_base, nent, e0) in ordered:
        for j in range(nent):
            entries.append((e0 + int(round(j * period)), j == 0))
    entries.sort()

    plays = [Play(index=i, entry=e, exact_entry=ex)
             for i, (e, ex) in enumerate(entries)]

    # --- place every write, absolute; flag the unplaceable --------------
    baseless_with_writes = 0
    entry_cycles = [p.entry for p in plays]

    import bisect
    for f, writes in enumerate(frames):
        if not writes:
            continue
        info = meta.get(f)
        if info is None:
            # No play entry in this frame => no base printed.  These writes
            # are the straddle tail of the play that entered before this
            # frame.  Unplaceable: mark that play unclean.
            baseless_with_writes += 1
            # The owning play is the last entry before this frame.  We do
            # not know this frame's absolute window, but frames are ordered,
            # so it is the last play whose entry precedes the NEXT frame's
            # base.  Conservative: mark the last play seen so far unclean.
            nxt = None
            for g in range(f + 1, len(frames) + 1):
                if g in meta:
                    nxt = meta[g][0]
                    break
            if nxt is None:
                if plays:
                    plays[-1].clean = False
                continue
            k = bisect.bisect_left(entry_cycles, nxt) - 1
            if 0 <= k < len(plays):
                plays[k].clean = False
            continue
        base = info[0]
        for rel, reg, val in writes:
            absc = base + rel
            k = bisect.bisect_right(entry_cycles, absc) - 1
            if k < 0:
                continue        # before the first play entry: init residue
            plays[k].writes.append((absc, reg, val))

    return Capture(plays=plays, n_frames=len(frames),
                   n_baseless_frames_with_writes=baseless_with_writes,
                   period=period)


def _pctl(xs: list, q: float) -> float:
    if not xs:
        return 0.0
    s = sorted(xs)
    i = min(len(s) - 1, max(0, int(round(q * (len(s) - 1)))))
    return float(s[i])


def compare(orig_sid: str, rebuild_sid: str, subtune: int,
            duration: float) -> dict:
    """Measure onset + spread deltas between an original and its rebuild."""
    co = capture_plays(orig_sid, subtune, duration)
    cr = capture_plays(rebuild_sid, subtune, duration)

    n = min(len(co.plays), len(cr.plays))
    onset = []
    spread = []
    compared = 0
    skipped_unclean = 0
    content_mismatch = 0
    empty = 0

    for i in range(n):
        po, pr = co.plays[i], cr.plays[i]
        if not po.clean or not pr.clean:
            skipped_unclean += 1
            continue
        if not po.writes or not pr.writes:
            empty += 1
            continue
        if [(w[1], w[2]) for w in po.writes] != [(w[1], w[2]) for w in pr.writes]:
            content_mismatch += 1
            continue
        compared += 1
        onset.append((po.writes[0][0] - po.entry)
                     - (pr.writes[0][0] - pr.entry))
        o0, r0 = po.writes[0][0], pr.writes[0][0]
        for j in range(1, len(po.writes)):
            spread.append((po.writes[j][0] - o0) - (pr.writes[j][0] - r0))

    abs_spread = [abs(x) for x in spread]
    onset_med = statistics.median(onset) if onset else 0.0
    # Jitter = onset delta with the constant (median) latency removed.
    jitter = [abs(x - onset_med) for x in onset]

    # The explanatory variable behind any spread delta: how WIDE each
    # side's per-play write burst is.  Trap B's justification is "a normal
    # player does all of its work in ONE burst"; a rebuild whose burst is
    # several times wider than the original's is where the claim strains.
    def _widths(cap):
        return [p.writes[-1][0] - p.writes[0][0]
                for p in cap.plays if p.clean and len(p.writes) > 1]
    wo, wr = _widths(co), _widths(cr)

    return {
        'orig': os.path.relpath(orig_sid, ROOT),
        'rebuild': os.path.relpath(rebuild_sid, ROOT),
        'subtune': subtune,
        'duration': duration,
        'plays_orig': len(co.plays),
        'plays_rebuild': len(cr.plays),
        'plays_compared': compared,
        'plays_skipped_unclean': skipped_unclean,
        'plays_content_mismatch': content_mismatch,
        'plays_empty': empty,
        'period_orig': round(co.period, 1),
        'period_rebuild': round(cr.period, 1),
        'writes_compared': len(spread) + compared,
        # --- the two distributions -------------------------------------
        'onset_median': onset_med,
        'onset_min': min(onset) if onset else 0,
        'onset_max': max(onset) if onset else 0,
        'jitter_p50': _pctl(jitter, 0.50),
        'jitter_p99': _pctl(jitter, 0.99),
        'jitter_max': max(jitter) if jitter else 0,
        'spread_p50': _pctl(abs_spread, 0.50),
        'spread_p95': _pctl(abs_spread, 0.95),
        'spread_p99': _pctl(abs_spread, 0.99),
        'spread_max': max(abs_spread) if abs_spread else 0,
        # --- the same numbers as a fraction of a PAL frame --------------
        'spread_p99_frac': round(_pctl(abs_spread, 0.99) / PAL_FRAME_CYCLES, 5),
        'spread_max_frac': round((max(abs_spread) if abs_spread else 0)
                                 / PAL_FRAME_CYCLES, 5),
        'jitter_p99_frac': round(_pctl(jitter, 0.99) / PAL_FRAME_CYCLES, 5),
        # --- burst width, both sides ------------------------------------
        'burst_orig_p50': _pctl(wo, 0.50),
        'burst_orig_max': max(wo) if wo else 0,
        'burst_rebuild_p50': _pctl(wr, 0.50),
        'burst_rebuild_p95': _pctl(wr, 0.95),
        'burst_rebuild_max': max(wr) if wr else 0,
        # entries the multispeed path had to interpolate (only entry0 is
        # printed per frame); 0 for every single-speed member.
        'entries_interpolated': sum(1 for p in co.plays if not p.exact_entry),
    }


def _fmt(res: dict) -> str:
    tot = (res['plays_compared'] + res['plays_skipped_unclean']
           + res['plays_content_mismatch'] + res['plays_empty'])
    keep = 100.0 * res['plays_compared'] / tot if tot else 0.0
    return (
        f"{res['orig']} sub {res['subtune']}\n"
        f"  plays {res['plays_compared']}/{tot} compared ({keep:.1f}%; "
        f"unclean {res['plays_skipped_unclean']}, "
        f"content-mismatch {res['plays_content_mismatch']}, "
        f"empty {res['plays_empty']})\n"
        f"  onset   median {res['onset_median']:+.0f} cyc   "
        f"range [{res['onset_min']:+d}, {res['onset_max']:+d}]\n"
        f"  jitter  p50 {res['jitter_p50']:.0f}  p99 {res['jitter_p99']:.0f}  "
        f"max {res['jitter_max']:.0f} cyc  "
        f"(p99 = {res['jitter_p99_frac'] * 100:.3f}% of a frame)\n"
        f"  spread  p50 {res['spread_p50']:.0f}  p95 {res['spread_p95']:.0f}  "
        f"p99 {res['spread_p99']:.0f}  max {res['spread_max']:.0f} cyc  "
        f"(p99 = {res['spread_p99_frac'] * 100:.3f}% of a frame)\n"
        f"  burst   orig p50 {res['burst_orig_p50']:.0f} max "
        f"{res['burst_orig_max']:.0f}  |  rebuild p50 "
        f"{res['burst_rebuild_p50']:.0f} p95 {res['burst_rebuild_p95']:.0f} "
        f"max {res['burst_rebuild_max']:.0f} cyc"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('orig', help='the HVSC original .sid')
    ap.add_argument('rebuild', nargs='?',
                    help='the rebuild (default: <orig>.sidfinity.sid)')
    ap.add_argument('--subtune', type=int, default=0, help='0-indexed')
    ap.add_argument('--duration', type=float, default=10.0)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()

    rebuild = a.rebuild or (a.orig[:-4] + '.sidfinity.sid')
    with phase(f'measure {os.path.basename(a.orig)} sub {a.subtune} '
               f'({a.duration}s x2 captures)'):
        res = compare(a.orig, rebuild, a.subtune, a.duration)
    print(json.dumps(res) if a.json else _fmt(res))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
