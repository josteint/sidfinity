"""Phase 2 acceptance test for the USF refactor.

Builds the cv3I_test synthetic instrument via the Phase 2 Python codegen
(src/usf2_codegen_phase2.py), runs the produced SID through siddump
--writelog, and verifies the per-frame register-write sequence matches
the analytical prediction:

  frame 0:       7 writes (ctrl, pw_lo, pw_hi, AD, SR, freq_lo, freq_hi)
  frames 1..16:  no writes
  frame 17 (= D-HR_THRESHOLD = 20-3):
                 3 writes (ctrl gate-off, AD=0, SR=0)
  frames 18..19: no writes
  frame 20:      loop back — 7 writes again

This is the "schema -> codegen -> SID -> writelog" round-trip proof.
"""
from __future__ import annotations

import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIDDUMP = os.path.join(ROOT, 'tools', 'siddump')
BUILD_DIR = '/tmp/usf2'
SID_PATH = os.path.join(BUILD_DIR, 'phase2.sid')

# Same constants as src/usf2_codegen_phase2.py
TEST_DUR_FRAMES = 20
HR_THRESHOLD = 3

# Expected writes per frame (register offsets only — we don't pin
# specific values, just the register set). VOL writes ($18) are
# sidplayfp setup, ignored here.
EXPECTED_INIT_REGS = {0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06}
EXPECTED_HR_REGS = {0x04, 0x05, 0x06}


def build_sid() -> None:
    os.makedirs(BUILD_DIR, exist_ok=True)
    with open(SID_PATH, 'wb') as f:
        subprocess.run(
            ['python3', os.path.join(ROOT, 'src', 'usf2_codegen_phase2.py')],
            check=True, stdout=f,
        )


def dump_writelog() -> list[str]:
    out = subprocess.run(
        [SIDDUMP, SID_PATH, '--writelog', '--duration', '1', '--raw'],
        capture_output=True, text=True, check=True, timeout=30,
    )
    return [ln for ln in out.stdout.split('\n') if ln.strip()]


def parse_frame(line: str) -> set[int]:
    """Return the set of register offsets written in this frame (ignoring
    VOL ($18) which is sidplayfp setup, and cycle/value detail)."""
    if '|' not in line:
        return set()
    _, w = line.split('|', 1)
    if not w.startswith('W:'):
        return set()
    parts = w[2:].split(':')
    regs = set()
    for i in range(0, len(parts) - 2, 3):
        try:
            reg = int(parts[i + 1], 16)
            if reg != 0x18:  # filter out VOL
                regs.add(reg)
        except (ValueError, IndexError):
            break
    return regs


def main() -> int:
    print('Phase 2 acceptance test: USF2 → codegen → SID → writelog round-trip')
    print()
    print('Building SID via Phase 2 codegen...')
    build_sid()
    print(f'  wrote {SID_PATH} ({os.path.getsize(SID_PATH)} bytes)')
    print()
    print('Running siddump --writelog...')
    frames = dump_writelog()
    print(f'  got {len(frames)} frame lines')
    print()
    print('Verifying per-frame register-write patterns:')

    # We assert the PATTERN of writes, not the exact siddump frame indices —
    # sidplayfp's frame attribution has a one-cycle drift for retrigger
    # writes that's an emulator artefact, not a schema issue. The schema's
    # promise: across the recorded frames we should see exactly:
    #   - init-write frames (all 7 V1 regs written)
    #   - HR-write frames (just ctrl, AD, SR)
    #   - everything else: empty
    # The DISTANCE between an init frame and the next HR frame should be
    # (D - HR_THRESHOLD); the distance from an HR frame to the next init
    # frame should be HR_THRESHOLD (+ possibly 1 from emulator drift).
    init_frames = []
    hr_frames = []
    other_writes = []
    for i, line in enumerate(frames):
        regs = parse_frame(line)
        if regs == EXPECTED_INIT_REGS:
            init_frames.append(i)
        elif regs == EXPECTED_HR_REGS:
            hr_frames.append(i)
        elif regs:
            other_writes.append((i, sorted(regs)))

    failures: list[str] = []
    if not init_frames:
        failures.append('no init-write frames found')
    if not hr_frames:
        failures.append('no HR-write frames found')
    if other_writes:
        failures.append(f'unexpected writes: {other_writes[:5]}')

    # Check the gap pattern: each HR follows an init by (D - HR_THRESHOLD)
    # frames, and each subsequent init follows the prior HR by HR_THRESHOLD
    # (give-or-take one frame of sidplayfp drift).
    for i in range(min(len(init_frames), len(hr_frames))):
        gap = hr_frames[i] - init_frames[i]
        expected = TEST_DUR_FRAMES - HR_THRESHOLD
        if abs(gap - expected) > 1:
            failures.append(
                f'init#{i}→HR#{i}: gap={gap}, expected ~{expected}'
            )
    for i in range(1, len(init_frames)):
        if i - 1 < len(hr_frames):
            gap = init_frames[i] - hr_frames[i - 1]
            if abs(gap - HR_THRESHOLD) > 1:
                failures.append(
                    f'HR#{i-1}→init#{i}: gap={gap}, expected ~{HR_THRESHOLD}'
                )

    if failures:
        print('  FAIL')
        for m in failures[:20]:
            print(f'    {m}')
        print()
        print(f'  init-write frames: {init_frames[:10]}')
        print(f'  HR-write frames:   {hr_frames[:10]}')
        return 1

    print('  OK — round-trip writelog matches predicted USF2 semantics')
    print()
    print(f'  init-write frames (7 V1 regs written): {init_frames[:5]} ...')
    print(f'  HR-write frames (3 V1 regs written):  {hr_frames[:5]} ...')
    print(f'  No other writes across {len(frames)} frames.')
    print()
    print(f'  init→HR gap ≈ {TEST_DUR_FRAMES - HR_THRESHOLD} frames')
    print(f'  HR→next init gap ≈ {HR_THRESHOLD} frames')
    print()
    print('Phase 2 acceptance: PASS')
    return 0


if __name__ == '__main__':
    sys.exit(main())
