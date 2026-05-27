"""py65_grade.py — Engine-equivalence grade using py65 simulation.

Unlike `writelog_grade.py` (which compares siddump's CSV — sidplayfp's
sampled SID register state at end of each play()), this grader runs
the 6502 directly via py65 and captures SID state per play() call.
The result is independent of libsidplayfp's frame-boundary timing
quirks (empty-frame insertion, VBI sampling cycle), so it measures
true engine equivalence.

Useful when writelog_grade reports a B/C-grade ceiling that's actually
the sidplayfp emulation, not the codegen. py65_grade is the honest
"do these two SIDs produce the same per-frame SID writes?" metric.

Usage:
    PYTHONPATH=tools/py65_lib python3 src/py65_grade.py <orig.sid> <rebuilt.sid> [-n FRAMES]

Slow: ~5-10 seconds per 100 frames.
"""
from __future__ import annotations

import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from py65.devices.mpu6502 import MPU


def _parse_psid(path: str) -> tuple[int, int, int, bytes]:
    """Return (load, init, play, payload). Strips PSID header + 2-byte
    embedded load addr if loadAddr == 0."""
    sid = open(path, 'rb').read()
    data_off = int.from_bytes(sid[6:8], 'big')
    init = int.from_bytes(sid[10:12], 'big')
    play = int.from_bytes(sid[12:14], 'big')
    load = int.from_bytes(sid[8:10], 'big')
    payload = sid[data_off:]
    if load == 0:
        load = payload[0] | (payload[1] << 8)
        payload = payload[2:]
    return load, init, play, payload


def _run_until_rts(mpu: MPU, max_steps: int = 100_000) -> None:
    """Step the MPU until it RTSes back to the sentinel (SP=$FF)."""
    for _ in range(max_steps):
        if mpu.memory[mpu.pc] == 0x60 and mpu.sp == 0xFF:
            break
        try:
            mpu.step()
        except Exception:
            break


def simulate(path: str, frames: int) -> list[tuple[int, ...]]:
    """Run init then `frames` play() calls; return list of 25-byte SID
    register snapshots (one per frame)."""
    load, init, play, payload = _parse_psid(path)
    mpu = MPU()
    for i, b in enumerate(payload):
        if load + i < 0x10000:
            mpu.memory[load + i] = b
    # Init
    mpu.pc = init
    mpu.stPush(0xFF); mpu.stPush(0xFF)
    _run_until_rts(mpu, max_steps=200_000)
    # Play frames
    states: list[tuple[int, ...]] = []
    for _ in range(frames):
        mpu.pc = play
        mpu.stPush(0xFF); mpu.stPush(0xFF)
        _run_until_rts(mpu, max_steps=200_000)
        states.append(tuple(mpu.memory[0xD400 + i] for i in range(25)))
    return states


_AUDIBILITY_MASKS = {3: 0x0F, 10: 0x0F, 17: 0x0F, 21: 0x07}


def _mask(snap: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(v & _AUDIBILITY_MASKS.get(i, 0xFF) for i, v in enumerate(snap))


def grade(orig_sid: str, rebuilt_sid: str, frames: int = 1500) -> None:
    print(f'Simulating {frames} frames of {orig_sid}...', file=sys.stderr)
    orig = [_mask(s) for s in simulate(orig_sid, frames)]
    print(f'Simulating {frames} frames of {rebuilt_sid}...', file=sys.stderr)
    new = [_mask(s) for s in simulate(rebuilt_sid, frames)]
    n = min(len(orig), len(new))
    match = sum(1 for i in range(n) if orig[i] == new[i])
    pct = 100.0 * match / max(n, 1)
    print(f'py65 engine-equivalence: {match}/{n} = {pct:.2f}%')
    if pct >= 99.5:
        grade_letter = 'A+'
    elif pct >= 98:
        grade_letter = 'A'
    elif pct >= 90:
        grade_letter = 'B'
    elif pct >= 70:
        grade_letter = 'C'
    elif pct >= 30:
        grade_letter = 'D'
    else:
        grade_letter = 'F'
    print(f'Grade: {grade_letter}')
    # First divergence
    for i in range(n):
        if orig[i] != new[i]:
            diffs = [(k, hex(orig[i][k]), hex(new[i][k]))
                     for k in range(25) if orig[i][k] != new[i][k]]
            print(f'First diverge at engine frame {i}: {diffs}')
            break


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('orig')
    p.add_argument('rebuilt')
    p.add_argument('-n', '--frames', type=int, default=1500,
                   help='Engine frames to simulate (default 1500 = 30s PAL)')
    args = p.parse_args()
    grade(args.orig, args.rebuilt, args.frames)


if __name__ == '__main__':
    main()
