"""
taint_tracker.py — Extract driver structure from any SID via instrumented 6502 execution.

Runs the SID's play routine in py65 with instrumentation to track which
memory reads feed each SID register write. This reveals:
- Frequency table location and contents
- Voice loop structure
- Data table locations

Usage:
    from formal.taint_tracker import extract_freq_table
    freq_lo, freq_hi = extract_freq_table('path/to/song.sid')
"""

import sys
import os
import struct
from collections import defaultdict, Counter

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'py65_lib'))

from py65.devices.mpu6502 import MPU


def load_sid(sid_path):
    """Load a SID file, return (memory_image, init_addr, play_addr, load_addr)."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    magic = data[:4]
    if magic not in (b'PSID', b'RSID'):
        raise ValueError(f"Not a PSID/RSID file: {magic}")

    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]

    code = data[header_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code

    # Build 64KB memory image
    mem = bytearray(65536)
    end = min(load_addr + len(binary), 65536)
    mem[load_addr:end] = binary[:end - load_addr]

    return mem, init_addr, play_addr, load_addr


class TaintMPU(MPU):
    """6502 CPU with memory read tracking for taint analysis."""

    def __init__(self):
        super().__init__()
        self.reads = []         # (addr, value) for current frame
        self.sid_writes = []    # (addr, value, reads_snapshot) for current frame

    def ByteAt(self, addr):
        val = super().ByteAt(addr)
        # Track non-stack, non-register reads
        if addr < 0x0100 or (0x0200 <= addr < 0xD400) or addr >= 0xD420:
            self.reads.append((addr, val))
        return val

    def WordAt(self, addr):
        # WordAt calls ByteAt twice, so reads are tracked automatically
        return super().WordAt(addr)

    def ByteAt_direct(self, addr):
        """Read without tracking (for internal use)."""
        return self.memory[addr]

    def reset_tracking(self):
        self.reads = []
        self.sid_writes = []


def run_play(mpu, play_addr, frames=50):
    """Run the play routine for N frames, collecting taint data.

    Returns list of per-frame SID write records:
    [{'reg': reg_offset, 'val': value, 'reads': [(addr, val), ...]}]
    """
    all_writes = []

    for frame in range(frames):
        mpu.reset_tracking()

        # JSR to play routine
        # Push return address - 1 onto stack (6502 convention)
        ret_addr = 0xFFF0 - 1  # we'll put a BRK at $FFF0
        mpu.memory[0xFFF0] = 0x00  # BRK
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr

        # Execute until BRK or too many cycles
        max_cycles = 30000
        cycles = 0
        current_reads = []

        while cycles < max_cycles:
            old_pc = mpu.pc
            opcode = mpu.ByteAt_direct(mpu.pc)

            if opcode == 0x00:  # BRK
                break

            # Check for SID write BEFORE executing (STA $D4xx)
            # We detect writes by checking if the instruction writes to $D400-$D418
            pre_sid = [mpu.ByteAt_direct(0xD400 + i) for i in range(25)]

            mpu.step()
            cycles += 1

            # Check for SID register changes
            for reg in range(25):
                new_val = mpu.ByteAt_direct(0xD400 + reg)
                if new_val != pre_sid[reg]:
                    # SID write detected — record which reads led here
                    all_writes.append({
                        'frame': frame,
                        'reg': reg,
                        'val': new_val,
                        'reads': list(mpu.reads),  # snapshot of all reads so far this frame
                    })

            if mpu.pc == old_pc:
                break  # stuck

    return all_writes


def extract_freq_table(sid_path, frames=50):
    """Extract the frequency table from a SID by taint tracking.

    Handles two common layouts:
    1. Separate tables: freq_lo[96] then freq_hi[96] (GT2-style)
    2. Interleaved: (lo, hi, lo, hi, ...) pairs (Hubbard-style)

    Returns (freq_lo_bytes, freq_hi_bytes, table_addr_lo, table_addr_hi) or None.
    """
    mem, init_addr, play_addr, load_addr = load_sid(sid_path)

    if play_addr == 0:
        return None

    mpu = TaintMPU()
    mpu.memory = bytearray(mem)

    mpu.memory[0xFFF0] = 0x00
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = 0
    for _ in range(50000):
        if mpu.ByteAt_direct(mpu.pc) == 0x00:
            break
        mpu.step()

    writes = run_play(mpu, play_addr, frames=frames)

    freq_hi_regs = {1, 8, 15}
    freq_lo_regs = {0, 7, 14}

    # Collect read addresses that feed freq_hi and freq_lo writes
    hi_read_addrs = Counter()
    lo_read_addrs = Counter()

    for w in writes:
        if w['val'] == 0:
            continue
        reads_with_match = [(a, v) for a, v in w['reads']
                            if 0x0200 <= a < 0xD400 and v == w['val']]
        if w['reg'] in freq_hi_regs:
            for addr, val in reads_with_match:
                hi_read_addrs[addr] += 1
        elif w['reg'] in freq_lo_regs:
            for addr, val in reads_with_match:
                lo_read_addrs[addr] += 1

    if len(hi_read_addrs) < 3:
        return None

    # Strategy: find the freq table by looking at the ADDRESS PATTERN
    # of reads. For a table at base+index, reads will be at
    # base+n1, base+n2, base+n3... where n1,n2,n3 are note indices.
    #
    # For interleaved (stride 2): reads at base+n1*2+1, base+n2*2+1, ...
    # For separate: reads at base+n1, base+n2, ...

    sorted_hi_addrs = sorted(hi_read_addrs.keys())

    # Try to find the base address by checking if the memory region
    # starting at (min_addr - some_offset) contains a valid freq table.
    # A freq table has monotonically increasing hi bytes.
    min_addr = sorted_hi_addrs[0]
    max_addr = sorted_hi_addrs[-1]

    # Try both layouts
    best = None
    best_score = 0

    from converters.regtrace_to_usf import FREQ_HI_PAL, FREQ_LO_PAL, FREQ_TABLE_PAL

    # Layout 1: Separate tables (stride 1)
    for base_offset in range(min(96, min_addr - 0x200)):
        base = min_addr - base_offset
        # Read 96 bytes as freq_hi
        hi_bytes = bytes(mem[base:base + 96])
        if len(hi_bytes) < 48:
            continue
        # Check monotonic + match against PAL
        matches = sum(1 for i in range(min(96, len(hi_bytes)))
                      if hi_bytes[i] == FREQ_HI_PAL[i])
        if matches > best_score:
            best_score = matches
            # Find freq_lo: try adjacent regions
            for lo_base in [base - 96, base + 96]:
                lo_bytes = bytes(mem[lo_base:lo_base + 96])
                lo_matches = sum(1 for i in range(min(96, len(lo_bytes)))
                                 if lo_bytes[i] == FREQ_LO_PAL[i])
                if lo_matches > 20:
                    best = (lo_bytes[:96], hi_bytes[:96], lo_base, base)

    # Layout 2: Interleaved (lo, hi, lo, hi) with stride 2
    for base_offset in range(min(192, min_addr - 0x200)):
        base = min_addr - base_offset
        if base < 0x200:
            continue
        # Read 192 bytes as interleaved pairs
        n_notes = min(96, (0xD400 - base) // 2)
        hi_bytes = bytes(mem[base + 1:base + n_notes * 2:2])
        lo_bytes = bytes(mem[base:base + n_notes * 2:2])
        if len(hi_bytes) < 24:
            continue
        # Match against PAL
        matches = sum(1 for i in range(min(len(hi_bytes), 96))
                      if hi_bytes[i] == FREQ_HI_PAL[i])
        # Also try with note offset
        for note_off in range(48):
            off_matches = sum(1 for i in range(min(len(hi_bytes), 96 - note_off))
                              if hi_bytes[i] == FREQ_HI_PAL[note_off + i])
            if off_matches > matches:
                matches = off_matches
        if matches > best_score and matches >= 8:
            best_score = matches
            best = (lo_bytes, hi_bytes, base, base + 1)

    return best


def extract_driver_info(sid_path, frames=50):
    """Extract comprehensive driver information from a SID.

    Returns dict with freq_table, voice_structure, tempo_info, etc.
    """
    mem, init_addr, play_addr, load_addr = load_sid(sid_path)

    if play_addr == 0:
        return {'error': 'CIA-driven (play_addr=0)', 'play_addr': 0}

    mpu = TaintMPU()
    mpu.memory = bytearray(mem)

    # Run init
    mpu.memory[0xFFF0] = 0x00
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = 0
    for _ in range(50000):
        if mpu.ByteAt_direct(mpu.pc) == 0x00:
            break
        mpu.step()

    # Run play
    writes = run_play(mpu, play_addr, frames=frames)

    info = {
        'play_addr': play_addr,
        'sid_writes': len(writes),
        'frames': frames,
    }

    # Freq table extraction
    ft = extract_freq_table(sid_path, frames=frames)
    if ft:
        freq_lo, freq_hi, addr_lo, addr_hi = ft
        info['freq_table'] = {
            'addr_lo': addr_lo,
            'addr_hi': addr_hi,
            'length': len(freq_hi),
            'freq_lo': freq_lo,
            'freq_hi': freq_hi,
        }

    # Voice loop detection (from SID write patterns)
    voice_offsets = Counter()
    for w in writes:
        voice_offsets[w['reg'] % 7] += 1
    if voice_offsets:
        # If writes are distributed across 0-6, 7-13, 14-20 → indexed loop
        v1 = sum(1 for w in writes if 0 <= w['reg'] < 7)
        v2 = sum(1 for w in writes if 7 <= w['reg'] < 14)
        v3 = sum(1 for w in writes if 14 <= w['reg'] < 21)
        if v1 > 0 and v2 > 0 and v3 > 0:
            ratio = min(v1, v2, v3) / max(v1, v2, v3)
            info['voice_balance'] = ratio
            info['voice_type'] = 'balanced' if ratio > 0.5 else 'unbalanced'

    return info


if __name__ == '__main__':
    import json

    if len(sys.argv) < 2:
        print("Usage: python3 src/formal/taint_tracker.py <sid_path>")
        sys.exit(1)

    sid_path = sys.argv[1]

    result = extract_freq_table(sid_path)
    if result:
        freq_lo, freq_hi, addr_lo, addr_hi = result
        print(f"Freq table found:")
        print(f"  freq_lo at ${addr_lo:04X} ({len(freq_lo)} bytes)")
        print(f"  freq_hi at ${addr_hi:04X} ({len(freq_hi)} bytes)")
        print(f"  freq_hi values: {' '.join(f'${b:02X}' for b in freq_hi[:16])}")
    else:
        print("No freq table found")

    info = extract_driver_info(sid_path)
    print(f"\nDriver info:")
    for k, v in info.items():
        if k != 'freq_table':
            print(f"  {k}: {v}")
