"""writelog_align_grade.py — Engine-equivalence grade via writelog
stream alignment.

Where `writelog_grade.py` compares siddump's per-frame CSV snapshot
(susceptible to sidplayfp's empty-frame insertion that shifts state
boundaries), this tool reconstructs the per-play() SID register state
from the writelog's `|W:cycle:reg:val` stream and aligns the two
streams via dynamic programming, absorbing sidplayfp's frame-boundary
jitter.

Concretely: for each rebuild siddump-frame, we accept a match if the
rebuild's running SID state appears in the original's stream within
a sliding-window range that handles inserted/skipped empty frames.

Usage:
  python3 src/writelog_align_grade.py <orig.sid> <rebuilt.sid> [--duration N] [--window W]

The `--window` defines how many frames in each direction we allow
sidplayfp's empty-frame drift to span (default 5). Past that we
report it as a true divergence.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass


SIDDUMP = '/home/jtr/sidfinity/tools/siddump'


_AUDIBILITY_MASKS = {3: 0x0F, 10: 0x0F, 17: 0x0F, 21: 0x07}


def _mask(snap: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(v & _AUDIBILITY_MASKS.get(i, 0xFF) for i, v in enumerate(snap))


def _reconstruct_states(sid_path: str, duration: int) -> list[tuple[int, ...]]:
    """Run siddump and reconstruct end-of-play SID state per frame from
    the writelog stream. Empty frames inherit previous state."""
    out = subprocess.run(
        [SIDDUMP, sid_path, '--writelog', '--force-rsid',
         '--duration', str(duration), '--raw'],
        capture_output=True, text=True, timeout=60,
    )
    if out.returncode != 0:
        raise RuntimeError(f'siddump failed: {out.stderr[:200]}')

    state = [0] * 25
    states: list[tuple[int, ...]] = []
    for line in out.stdout.split('\n'):
        if not line.strip():
            continue
        if '|' in line:
            _, w = line.split('|', 1)
        else:
            w = ''
        if w.startswith('W:'):
            parts = w[2:].split(':')
            for i in range(0, len(parts) - 2, 3):
                try:
                    reg = int(parts[i + 1], 16)
                    val = int(parts[i + 2], 16)
                    if 0 <= reg < 25:
                        state[reg] = val
                except (ValueError, IndexError):
                    break
        states.append(tuple(state))
    return states


def grade_aligned(orig_path: str, rebuilt_path: str,
                  duration: int = 30, window: int = 5) -> None:
    print(f'Reconstructing states from {orig_path}...', file=sys.stderr)
    orig = [_mask(s) for s in _reconstruct_states(orig_path, duration)]
    print(f'Reconstructing states from {rebuilt_path}...', file=sys.stderr)
    new = [_mask(s) for s in _reconstruct_states(rebuilt_path, duration)]
    n = min(len(orig), len(new))

    # Strict match
    strict = sum(1 for i in range(n) if orig[i] == new[i])

    # Index original states for fast lookup at each window position
    matched = 0
    drift_distribution: dict[int, int] = {}  # offset → count
    unmatched: list[int] = []
    for i in range(n):
        best_offset: int | None = None
        for d in range(window + 1):
            for sign in (1, -1) if d > 0 else (0,):
                j = i + sign * d
                if 0 <= j < n and new[i] == orig[j]:
                    best_offset = sign * d
                    break
            if best_offset is not None:
                break
        if best_offset is not None:
            matched += 1
            drift_distribution[best_offset] = drift_distribution.get(best_offset, 0) + 1
        else:
            unmatched.append(i)

    print(f'Strict frame-aligned match:        {strict}/{n} = {100*strict/n:.1f}%')
    print(f'Aligned within ±{window} window:           '
          f'{matched}/{n} = {100*matched/n:.1f}%')
    if matched >= n * 0.98: g = 'A'
    elif matched >= n * 0.90: g = 'B'
    elif matched >= n * 0.70: g = 'C'
    elif matched >= n * 0.30: g = 'D'
    else: g = 'F'
    print(f'Alignment-tolerant Grade: {g}')

    if drift_distribution:
        print()
        print('Frame-drift distribution (rebuild offset → original frame):')
        for off in sorted(drift_distribution.keys()):
            pct = 100 * drift_distribution[off] / n
            print(f'  {off:+d}: {drift_distribution[off]} frames ({pct:.1f}%)')

    if unmatched:
        print()
        print(f'{len(unmatched)} frames truly diverge (no ±{window} match).')
        for f in unmatched[:5]:
            diff = [(k, hex(orig[f][k]), hex(new[f][k]))
                    for k in range(25) if orig[f][k] != new[f][k]]
            print(f'  frame {f}: {diff[:6]}')


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('orig')
    p.add_argument('rebuilt')
    p.add_argument('--duration', type=int, default=30)
    p.add_argument('--window', type=int, default=5)
    args = p.parse_args()
    grade_aligned(args.orig, args.rebuilt, args.duration, args.window)


if __name__ == '__main__':
    main()
