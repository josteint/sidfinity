#!/usr/bin/env python3
"""
Verify the Lean Das Model compiler against sidplayfp's ground truth.

Compares the Lean compiler's instruction stream output against
siddump --writelog of the original SID. Reports frame-by-frame
differences and overall match rate.

Usage:
    python3 verify.py [n_frames]
"""

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REG_NAMES = {}
for i in range(3):
    for j, name in enumerate(['flo', 'fhi', 'plo', 'phi', 'ctl', 'ad', 'sr']):
        REG_NAMES[i * 7 + j] = f'V{i+1}{name}'
REG_NAMES[0x15] = 'Flo'
REG_NAMES[0x16] = 'Fhi'
REG_NAMES[0x17] = 'Fctl'
REG_NAMES[0x18] = 'Vol'


def parse_sidplayfp_writelog(path, duration=10):
    """Capture ground truth from sidplayfp via siddump --writelog."""
    cmd = [os.path.join(ROOT, 'tools', 'siddump'), path,
           '--subtune', '1', '--duration', str(duration), '--writelog']
    result = subprocess.run(cmd, capture_output=True, text=True)

    frames = []
    for line in result.stdout.strip().split('\n')[2:]:  # skip JSON + CSV header
        if '|W:' in line:
            raw = line.split('|W:')[1]
            tokens = raw.split(':')
            writes = []
            i = 0
            while i + 2 < len(tokens):
                cycle = int(tokens[i])
                reg = int(tokens[i+1], 16)
                val = int(tokens[i+2], 16)
                writes.append((reg, val))
                i += 3
            frames.append(writes)
        else:
            frames.append([])
    return frames


def parse_lean_output(lean_output):
    """Parse the Lean compiler's output into (register, value) pairs per frame."""
    frames = []
    for line in lean_output.strip().split('\n'):
        if not line.strip().startswith('F'):
            continue
        # Parse "F0: V3fhi=3 V3flo=169 ..."
        parts = line.split(':', 1)
        if len(parts) < 2:
            continue
        writes_str = parts[1].strip()
        writes = []
        for w in writes_str.split():
            if '=' not in w:
                continue
            reg_name, val_str = w.split('=', 1)
            val_str = val_str.lstrip('$')  # Lean outputs $decimal
            val = int(val_str)
            # Map register name back to offset
            reg_off = None
            for off, name in REG_NAMES.items():
                if name == reg_name:
                    reg_off = off
                    break
            if reg_off is not None:
                writes.append((reg_off, val))
        frames.append(writes)
    return frames


def filter_changes(frames):
    """Filter to only register VALUE CHANGES (matching sidplayfp writelog behavior)."""
    state = {}
    filtered = []
    for frame in frames:
        changes = []
        for reg, val in frame:
            if state.get(reg) != val:
                changes.append((reg, val))
                state[reg] = val
        filtered.append(changes)
    return filtered


def compare(gt_frames, lean_frames, max_show=10):
    """Compare ground truth against Lean output (changes-only)."""
    # Filter Lean output to changes-only (sidplayfp already does this)
    lean_filtered = filter_changes(lean_frames)

    n = min(len(gt_frames), len(lean_filtered))
    match = 0
    shown = 0

    for f in range(n):
        gt = gt_frames[f]
        lean = lean_filtered[f]

        if gt == lean:
            match += 1
        elif shown < max_show:
            shown += 1
            gt_str = ' '.join(f'{REG_NAMES.get(r, f"r{r:02X}")}=${v}' for r, v in gt[:8])
            lean_str = ' '.join(f'{REG_NAMES.get(r, f"r{r:02X}")}=${v}' for r, v in lean[:8])
            print(f'  F{f}: GT({len(gt)})  {gt_str}')
            print(f'       Lean({len(lean)}) {lean_str}')
            print()

    print(f'Match: {match}/{n} ({100*match/n:.1f}%)')
    return match, n


if __name__ == '__main__':
    n_frames = int(sys.argv[1]) if len(sys.argv) > 1 else 10

    print(f'=== Lean Das Model vs sidplayfp ground truth ({n_frames} frames) ===')
    print()

    # Capture ground truth
    sid_path = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                            'Hubbard_Rob', 'Commando.sid')
    print('Capturing sidplayfp writelog...')
    gt = parse_sidplayfp_writelog(sid_path, duration=n_frames // 50 + 1)

    # Run Lean compiler
    print('Running Lean compiler...')
    lean_bin = os.path.join(os.path.dirname(__file__), '.lake', 'build', 'bin', 'commando')
    if os.path.exists(lean_bin):
        result = subprocess.run([lean_bin], capture_output=True, text=True)
        lean = parse_lean_output(result.stdout)
    else:
        print(f'Lean binary not found at {lean_bin}')
        sys.exit(1)

    print(f'GT frames: {len(gt)}, Lean frames: {len(lean)}')
    print()

    compare(gt[:n_frames], lean[:n_frames])
