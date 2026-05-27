"""
emu_test.py — Python-native 6502 emulator test harness for V2 player code.

Uses py65 to execute the assembled V2 player in a Python-debuggable
environment. Builds a SID via the normal pipeline, loads the binary
into py65, runs init + N play calls, and compares SID register output
against siddump.

Usage:
    PYTHONPATH=tools/py65_lib:$PYTHONPATH python3 src/player/emu_test.py <input.sid> [--frames N] [--verbose]

The input SID must be a GT2-format SID that our pipeline can convert.
"""

import sys
import os
import struct
import argparse

# Ensure project paths are available
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'src'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'src', 'player'))

from py65.devices.mpu6502 import MPU

SIDDUMP = os.path.join(REPO_ROOT, 'tools', 'siddump')

# SID register base in C64 memory map
SID_BASE = 0xD400
SID_REGS = 25  # $D400-$D418

# Register names for display
REG_NAMES = [
    'V1_FLO', 'V1_FHI', 'V1_PWL', 'V1_PWH', 'V1_CTL', 'V1_AD', 'V1_SR',
    'V2_FLO', 'V2_FHI', 'V2_PWL', 'V2_PWH', 'V2_CTL', 'V2_AD', 'V2_SR',
    'V3_FLO', 'V3_FHI', 'V3_PWL', 'V3_PWH', 'V3_CTL', 'V3_AD', 'V3_SR',
    'FLT_LO', 'FLT_HI', 'FLT_CTL', 'FLT_VOL',
]


def parse_sid_file(sid_path):
    """Parse a PSID file and return (load_addr, init_addr, play_addr, binary_data)."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    magic = data[0:4]
    if magic not in (b'PSID', b'RSID'):
        raise ValueError(f'Not a SID file: magic={magic}')

    version = struct.unpack_from('>H', data, 4)[0]
    data_offset = struct.unpack_from('>H', data, 6)[0]
    load_addr = struct.unpack_from('>H', data, 8)[0]
    init_addr = struct.unpack_from('>H', data, 10)[0]
    play_addr = struct.unpack_from('>H', data, 12)[0]

    binary = data[data_offset:]

    # If load_addr == 0, first two bytes of data are the load address (little-endian)
    if load_addr == 0:
        load_addr = struct.unpack_from('<H', binary, 0)[0]
        binary = binary[2:]

    return load_addr, init_addr, play_addr, binary


def build_rebuilt_sid(input_sid_path):
    """Run the GT2->USF->SID pipeline and return the rebuilt SID file path."""
    from gt2_to_usf import gt2_to_usf
    from usf_to_sid import usf_to_sid

    song = gt2_to_usf(input_sid_path)
    if song is None:
        raise RuntimeError(f'gt2_to_usf failed for {input_sid_path}')

    output_path = f'/tmp/emu_test_{os.getpid()}.sid'
    sid_bytes, player_size = usf_to_sid(song, output_path)
    if not sid_bytes:
        raise RuntimeError('usf_to_sid returned empty')

    return output_path, player_size


def run_siddump(sid_path, frames):
    """Run siddump and return list of 25-element lists (hex values as ints)."""
    import subprocess
    # Convert frames to seconds (50 fps PAL)
    duration = max(1, (frames + 49) // 50)
    r = subprocess.run(
        [SIDDUMP, sid_path, '--duration', str(duration)],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode != 0:
        raise RuntimeError(f'siddump failed (exit {r.returncode}): {r.stderr[:200]}')

    lines = r.stdout.strip().split('\n')[2:]  # skip JSON header + column header
    result = []
    for line in lines[:frames]:
        vals = [int(v, 16) for v in line.split(',')]
        result.append(vals)
    return result


class SIDCapture:
    """Wraps py65 MPU to capture SID register writes.

    The C64 SID chip has write-only registers. py65 treats all memory as
    RAM, so writes to $D400-$D418 are readable. We track them here for
    clarity and to detect which registers were actually written each frame.
    """

    def __init__(self):
        self.cpu = MPU()
        self.regs = [0] * SID_REGS
        self._writes_this_frame = set()

    def load_binary(self, load_addr, binary):
        """Load binary data into CPU memory at the given address."""
        for i, b in enumerate(binary):
            self.cpu.memory[load_addr + i] = b

    def _snapshot_sid(self):
        """Read current SID register values from memory."""
        return [self.cpu.memory[SID_BASE + i] for i in range(SID_REGS)]

    def call_subroutine(self, addr, a=0, x=0, y=0, max_steps=500000):
        """Call a 6502 subroutine at addr with given register values.

        Sets up the stack, pushes a return address, and steps until RTS
        brings us back or we hit the step limit.

        Returns the number of steps executed.
        """
        # Set registers
        self.cpu.a = a & 0xFF
        self.cpu.x = x & 0xFF
        self.cpu.y = y & 0xFF

        # Push a sentinel return address on the stack.
        # RTS pops address and adds 1, so push (sentinel - 1).
        # We use $FFF0 as sentinel: push $FFEF (hi=$FF, lo=$EF).
        sentinel = 0xFFF0
        ret_addr = sentinel - 1
        # Push high byte first (6502 stack is LIFO, RTS pops lo then hi)
        self.cpu.memory[0x0100 + self.cpu.sp] = (ret_addr >> 8) & 0xFF
        self.cpu.sp = (self.cpu.sp - 1) & 0xFF
        self.cpu.memory[0x0100 + self.cpu.sp] = ret_addr & 0xFF
        self.cpu.sp = (self.cpu.sp - 1) & 0xFF

        # Put a sentinel instruction at the return point (BRK or similar)
        self.cpu.memory[sentinel] = 0x00  # BRK

        self.cpu.pc = addr

        steps = 0
        while steps < max_steps:
            if self.cpu.pc == sentinel:
                return steps
            self.cpu.step()
            steps += 1

        raise RuntimeError(
            f'Subroutine at ${addr:04X} did not return after {max_steps} steps '
            f'(PC=${self.cpu.pc:04X}, SP=${self.cpu.sp:02X})'
        )

    def run_init(self, init_addr, subtune=0):
        """Call the init routine with subtune number in A."""
        steps = self.call_subroutine(init_addr, a=subtune)
        return steps

    def run_play(self, play_addr):
        """Call the play routine once and capture SID registers after."""
        steps = self.call_subroutine(play_addr)
        self.regs = self._snapshot_sid()
        return steps, list(self.regs)


def compare_frames(emu_frames, dump_frames, verbose=False):
    """Compare emulator output against siddump. Returns (match, total, diffs).

    Uses a +/-1 frame window for matching to account for VBI timing drift
    between py65 (instant play calls) and siddump (PSID driver overhead).
    A register value is considered matching if it appears in frame f-1, f, or f+1
    of the reference.
    """
    total = min(len(emu_frames), len(dump_frames))
    match = 0
    exact_match = 0
    diffs = []

    for f in range(total):
        emu = emu_frames[f]
        ref = dump_frames[f]
        frame_exact = True
        frame_match = True
        frame_diffs = []

        for r in range(SID_REGS):
            if emu[r] != ref[r]:
                frame_exact = False
                # Check +/-1 frame window
                window_match = False
                for delta in [-1, 1]:
                    adj = f + delta
                    if 0 <= adj < len(dump_frames):
                        if emu[r] == dump_frames[adj][r]:
                            window_match = True
                            break
                if not window_match:
                    frame_match = False
                    frame_diffs.append((r, REG_NAMES[r], emu[r], ref[r]))

        if frame_exact:
            exact_match += 1
        if frame_match or frame_exact:
            match += 1
        elif verbose or len(diffs) < 20:
            diffs.append((f, frame_diffs))

    return match, total, diffs, exact_match


def main():
    parser = argparse.ArgumentParser(description='V2 player 6502 emulator test')
    parser.add_argument('input_sid', help='Input GT2 SID file')
    parser.add_argument('--frames', type=int, default=200,
                        help='Number of frames to emulate (default: 200)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show all frame diffs')
    parser.add_argument('--trace', action='store_true',
                        help='Print register state every frame')
    args = parser.parse_args()

    if not os.path.exists(args.input_sid):
        print(f'ERROR: {args.input_sid} not found')
        sys.exit(1)

    # Step 1: Build rebuilt SID via pipeline
    print(f'Building SID from {os.path.basename(args.input_sid)}...')
    rebuilt_path, player_size = build_rebuilt_sid(args.input_sid)
    print(f'  Rebuilt SID: {rebuilt_path} (player: {player_size} bytes)')

    # Step 2: Parse the rebuilt SID
    load_addr, init_addr, play_addr, binary = parse_sid_file(rebuilt_path)
    print(f'  Load: ${load_addr:04X}, Init: ${init_addr:04X}, Play: ${play_addr:04X}')
    print(f'  Binary: {len(binary)} bytes (${load_addr:04X}-${load_addr + len(binary) - 1:04X})')

    # Step 3: Load into py65 emulator
    print(f'Loading into py65 emulator...')
    emu = SIDCapture()
    emu.load_binary(load_addr, binary)

    # Step 4: Run init
    init_steps = emu.run_init(init_addr, subtune=0)
    print(f'  Init: {init_steps} steps')

    # Step 5: Run play N times, capturing SID regs each frame
    print(f'Running {args.frames} play calls...')
    emu_frames = []
    total_steps = 0
    for f in range(args.frames):
        steps, regs = emu.run_play(play_addr)
        emu_frames.append(regs)
        total_steps += steps

        if args.trace:
            reg_str = ','.join(f'{v:02X}' for v in regs)
            print(f'  Frame {f:4d} ({steps:5d} steps): {reg_str}')

    avg_steps = total_steps / args.frames if args.frames else 0
    print(f'  Total: {total_steps} steps, avg: {avg_steps:.0f} steps/frame')

    # Step 6: Run siddump on rebuilt SID for reference
    print(f'Running siddump on rebuilt SID...')
    dump_frames = run_siddump(rebuilt_path, args.frames)
    print(f'  Got {len(dump_frames)} frames from siddump')

    # Step 7: Compare
    match, total, diffs, exact = compare_frames(emu_frames, dump_frames, args.verbose)
    pct = 100.0 * match / total if total > 0 else 0.0
    exact_pct = 100.0 * exact / total if total > 0 else 0.0
    print(f'\nResults: {match}/{total} frames match with +/-1 window ({pct:.1f}%)')
    print(f'  Exact match: {exact}/{total} ({exact_pct:.1f}%)')

    if diffs:
        print(f'\nMismatches (beyond +/-1 frame window):')
        for frame_idx, frame_diffs in diffs:
            diff_strs = []
            for reg_idx, reg_name, emu_val, ref_val in frame_diffs:
                diff_strs.append(f'{reg_name}:{emu_val:02X}!={ref_val:02X}')
            print(f'  Frame {frame_idx}: {" ".join(diff_strs)}')

    # Cleanup
    if os.path.exists(rebuilt_path):
        os.unlink(rebuilt_path)

    if match == total:
        print('\nPASS: py65 emulation matches siddump (within timing tolerance).')
        return 0
    else:
        print(f'\n{total - match} frames differ beyond timing tolerance.')
        return 1


if __name__ == '__main__':
    sys.exit(main())
