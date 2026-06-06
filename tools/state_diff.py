#!/usr/bin/env python3
"""state_diff.py — find first frame where engine state diverges between
an HVSC original and a rebuild.

Given two SIDs + an address map (orig_addr ↔ rebuild_addr pairs), runs
`siddump --memwatch` on both and reports the first frame at which any
mapped pair differs.

Usage:
    python3 tools/state_diff.py ORIG.sid REBUILD.sid --map MAP_FILE
            [--subtune N] [--duration S] [--start F] [--end F]

MAP_FILE is a Python dict literal mapping orig addresses to rebuild
addresses, with optional labels:
    {
        # voice 1 state
        0xA654: (0xB86A, "pulsestolo[V1]"),
        0xA657: (0xB86D, "pulsesto_hi[V1]"),
        # ...
    }

Output:
    For each frame in [start, end), checks all mapped pairs. Reports
    the first frame where any pair has unequal values + the diverging
    pairs with their labels.

The point: collapse the "build a custom py65 trace from scratch"
diagnostic into one command using libsidplayfp (ground truth, not py65).

============================================================
CAVEAT — this tool produces HINTS, not verdicts (Trap C)
============================================================

`siddump --memwatch` samples RAM at the end of each
`engine.play(cyclesPerFrame)` call. cyclesPerFrame=19688 (PAL VBI=19656,
+32 margin), so each siddump "frame" processes usually 1, sometimes 0,
sometimes 2 PSID `play()` invocations. State sampled at siddump-frame N
is NOT necessarily what the engine had after IRQ N.

A reported "state divergence at frame N" may be:
  (a) a real engine bug, OR
  (b) an IRQ-count misalignment between mine and orig (Trap C)

ALWAYS cross-check against `tools/find_first_divergence.py` (the
writelog flat-sequence ground truth). If writelog matches but state_diff
reports a divergence, you're in Trap C — ignore the state hint.

See `feedback_verification_modes.md` (under `.claude/memory/`) for the
full Mode 1 / Mode 2 / Traps A,B,C framing.
"""
from __future__ import annotations

import argparse
import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIDDUMP = ROOT / 'tools' / 'siddump'


def _run_memwatch(sid_path: str, subtune: int, duration: float,
                  addrs: list[int]
                  ) -> tuple[list[dict[int, int]], list[int]]:
    """Run siddump --memwatch and parse the per-frame snapshots.
    Returns (frames, play_counts):
      frames       — list of dicts (one per frame) mapping addr → byte value
      play_counts  — list of ints (one per frame): how many PSID play()
                     invocations fired in that siddump frame. Used to
                     detect Trap C (memwatch alignment).
    """
    addr_arg = ','.join(f'{a:04X}' for a in addrs)
    cmd = [str(SIDDUMP), sid_path,
           '--subtune', str(subtune + 1),  # convert to 1-indexed
           '--duration', str(duration),
           '--raw',
           '--memwatch', addr_arg]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode not in (0, 2):  # 2 = "silent tune" — still has data
        print(f'siddump error (rc={r.returncode}): {r.stderr}',
              file=sys.stderr)
        return [], []
    frames: list[dict[int, int]] = []
    play_counts: list[int] = []
    for line in r.stdout.splitlines():
        if '|M:' not in line:
            frames.append({})
            play_counts.append(0)
            continue
        # Parse the |M: snapshot and the |P: play count
        snap = {}
        rest = line.split('|M:', 1)[1]
        # |P: comes after |M: when present
        play_count = 0
        if '|P:' in rest:
            m_section, p_section = rest.split('|P:', 1)
            # P count may have a |W: writelog after it
            if '|' in p_section:
                p_section = p_section.split('|', 1)[0]
            try:
                play_count = int(p_section.strip())
            except ValueError:
                pass
        else:
            m_section = rest
            if '|W' in m_section:
                m_section = m_section.split('|W', 1)[0]
        for tok in m_section.split(':'):
            if '=' not in tok:
                continue
            a_str, v_str = tok.split('=', 1)
            try:
                snap[int(a_str, 16)] = int(v_str, 16)
            except ValueError:
                pass
        frames.append(snap)
        play_counts.append(play_count)
    return frames, play_counts


def state_diff(orig_path: str, rebuild_path: str,
               mapping: dict[int, tuple[int, str]],
               subtune: int = 0, duration: float = 60.0,
               start_frame: int = 0,
               end_frame: int | None = None) -> dict:
    """Run memwatch on both SIDs and find first divergence.

    `mapping` keys are orig RAM addresses; values are
    `(rebuild_addr, label)` tuples.

    Cumulative play_count delta (orig vs rebuild) is computed per frame.
    If non-zero at the divergence point, this is Trap C noise — the
    "divergence" reflects siddump frame-bucket misalignment with PSID
    play() invocations, not a real engine bug.
    """
    orig_addrs = list(mapping.keys())
    rebuild_addrs = [m[0] for m in mapping.values()]
    orig_frames, orig_pc = _run_memwatch(orig_path, subtune, duration, orig_addrs)
    rebuild_frames, rebuild_pc = _run_memwatch(rebuild_path, subtune, duration,
                                                rebuild_addrs)
    n = min(len(orig_frames), len(rebuild_frames))
    if end_frame is None or end_frame > n:
        end_frame = n

    # Cumulative play count for each frame index.
    orig_cum = [0] * len(orig_pc)
    rebuild_cum = [0] * len(rebuild_pc)
    s = 0
    for i, c in enumerate(orig_pc):
        s += c; orig_cum[i] = s
    s = 0
    for i, c in enumerate(rebuild_pc):
        s += c; rebuild_cum[i] = s

    first_div = None
    for f in range(start_frame, end_frame):
        o = orig_frames[f]
        r = rebuild_frames[f]
        diffs = []
        for orig_a, (reb_a, label) in mapping.items():
            ov = o.get(orig_a)
            rv = r.get(reb_a)
            if ov is None or rv is None or ov != rv:
                diffs.append((label, orig_a, reb_a, ov, rv))
        if diffs:
            irq_delta = orig_cum[f] - rebuild_cum[f]
            first_div = (f, diffs, irq_delta, orig_cum[f], rebuild_cum[f])
            break
    return {
        'orig_frames': len(orig_frames),
        'rebuild_frames': len(rebuild_frames),
        'range_examined': (start_frame, end_frame),
        'first_div': first_div,
        'orig_total_irqs': sum(orig_pc),
        'rebuild_total_irqs': sum(rebuild_pc),
    }


def _format(result: dict) -> str:
    lines = [
        f'orig frames:    {result["orig_frames"]}',
        f'rebuild frames: {result["rebuild_frames"]}',
        f'range examined: f{result["range_examined"][0]}'
        f'..f{result["range_examined"][1]}',
    ]
    # Total IRQ counts (for context)
    if 'orig_total_irqs' in result:
        lines.append(
            f'orig total IRQs: {result["orig_total_irqs"]}  '
            f'rebuild total IRQs: {result["rebuild_total_irqs"]}')
    fd = result['first_div']
    if fd is None:
        lines.append('NO STATE DIVERGENCE in mapped pairs across the range.')
    else:
        f, diffs, irq_delta, o_cum, r_cum = fd
        lines.append(f'\nFIRST STATE DIVERGENCE at frame {f}:')
        for label, oa, ra, ov, rv in diffs:
            ov_s = f'${ov:02X}' if ov is not None else 'MISSING'
            rv_s = f'${rv:02X}' if rv is not None else 'MISSING'
            lines.append(
                f'  {label:30s}  orig ${oa:04X}={ov_s}  '
                f'rebuild ${ra:04X}={rv_s}')
        lines.append('')
        lines.append(
            f'IRQ alignment at f{f}: orig cumulative={o_cum}, '
            f'rebuild cumulative={r_cum}, delta={irq_delta}')
        if irq_delta != 0:
            lines.append('')
            lines.append(
                f'>>> TRAP C DETECTED — IRQ counts differ by {irq_delta} at '
                f'this frame. <<<')
            lines.append(
                'This means siddump frame buckets are misaligned with PSID')
            lines.append(
                'play() invocations between mine and orig. The state values')
            lines.append(
                'reflect different points in the IRQ schedule, not a real bug.')
            lines.append(
                'IGNORE this state divergence — re-run with a later --start frame')
            lines.append(
                'or use find_first_divergence.py (writelog flat-prefix verdict).')
        else:
            lines.append(
                'IRQ counts agree at this frame — the divergence is likely real.')
            lines.append(
                'Still cross-check with find_first_divergence.py to confirm.')
    return '\n'.join(lines)


def _load_map(path: str) -> dict:
    """Load a Python-literal map file. Accepts either:
       - {0xORIG: (0xREB, "label"), ...}
       - {0xORIG: 0xREB, ...}  (label defaults to hex addresses)
    """
    with open(path) as f:
        raw = ast.literal_eval(f.read())
    out: dict[int, tuple[int, str]] = {}
    for k, v in raw.items():
        if isinstance(v, tuple):
            out[k] = (v[0], v[1] if len(v) > 1 else f'${k:04X}↔${v[0]:04X}')
        else:
            out[k] = (v, f'${k:04X}↔${v:04X}')
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('orig')
    p.add_argument('rebuild')
    p.add_argument('--map', required=True,
                   help='Path to Python-literal state-map file')
    p.add_argument('--subtune', type=int, default=0,
                   help='0-indexed subtune (default 0)')
    p.add_argument('--duration', type=float, default=10.0,
                   help='seconds (default 10)')
    p.add_argument('--start', type=int, default=0,
                   help='start frame (inclusive, default 0)')
    p.add_argument('--end', type=int, default=None,
                   help='end frame (exclusive, default min(orig,rebuild) frames)')
    args = p.parse_args()
    if not os.path.exists(args.orig):
        print(f'orig not found: {args.orig}', file=sys.stderr); return 1
    if not os.path.exists(args.rebuild):
        print(f'rebuild not found: {args.rebuild}', file=sys.stderr); return 1
    mapping = _load_map(args.map)
    result = state_diff(args.orig, args.rebuild, mapping,
                        args.subtune, args.duration,
                        args.start, args.end)
    print(_format(result))
    return 0 if result['first_div'] is None else 2


if __name__ == '__main__':
    sys.exit(main())
