#!/usr/bin/env python3
"""Search a siddump --memdump file for frequency tables.

Usage:
    python3 src/memdump_freq.py <sid_file> [--frames N] [--memdump FILE]

If --memdump is not given, runs siddump automatically with --memdump to a temp file.
Reports whether a freq table is found in the memdump (runtime-computed) vs the
static SID binary.
"""

import argparse
import os
import struct
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(__file__))
from gt_parser import _find_freq_table_pal, _find_freq_table_generic, find_freq_table


def load_sid_binary(sid_path):
    """Load a SID file and return (binary_data, load_addr)."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    # Parse PSID/RSID header
    magic = data[:4]
    if magic not in (b'PSID', b'RSID'):
        raise ValueError(f"Not a SID file: {sid_path}")

    version = struct.unpack('>H', data[4:6])[0]
    data_offset = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]

    binary = data[data_offset:]

    # If load_addr is 0, it's stored in the first 2 bytes of data (little-endian)
    if load_addr == 0 and len(binary) >= 2:
        load_addr = binary[0] | (binary[1] << 8)
        binary = binary[2:]

    return binary, load_addr


def run_memdump(sid_path, frames=10):
    """Run siddump --memdump and return path to the memdump file."""
    # Find siddump
    script_dir = os.path.dirname(os.path.abspath(__file__))
    siddump = os.path.join(script_dir, '..', 'tools', 'siddump')
    if not os.path.exists(siddump):
        raise FileNotFoundError(f"siddump not found at {siddump}")

    tmp = tempfile.NamedTemporaryFile(suffix='.bin', delete=False)
    tmp.close()

    # duration=1 second gives 50 frames for PAL, plenty for freq table init
    duration = max(1, (frames + 49) // 50)
    cmd = [siddump, sid_path, '--memdump', tmp.name, '--duration', str(duration)]
    result = subprocess.run(cmd, capture_output=True, timeout=30)

    if result.returncode not in (0, 2):  # 2 = silent tune, still has memdump
        os.unlink(tmp.name)
        raise RuntimeError(f"siddump failed (exit {result.returncode}): {result.stderr.decode()}")

    return tmp.name


def main():
    parser = argparse.ArgumentParser(description='Search memdump for frequency tables')
    parser.add_argument('sid_file', help='SID file to analyze')
    parser.add_argument('--frames', type=int, default=10, help='Number of frames to run (default: 10)')
    parser.add_argument('--memdump', help='Pre-existing memdump file (skip running siddump)')
    args = parser.parse_args()

    # --- Static binary analysis ---
    binary, load_addr = load_sid_binary(args.sid_file)
    static_result = find_freq_table(binary, load_addr)

    if static_result:
        offset, first_note, num_notes, lo_first = static_result
        addr = load_addr + offset
        print(f"STATIC: Found freq table at ${addr:04X} (offset {offset}), "
              f"notes {first_note}-{first_note + num_notes - 1}, "
              f"{'lo-first' if lo_first else 'hi-first'}")
    else:
        print("STATIC: No freq table found in binary")

    # --- Memdump analysis ---
    if args.memdump:
        memdump_path = args.memdump
        cleanup = False
    else:
        memdump_path = run_memdump(args.sid_file, args.frames)
        cleanup = True

    try:
        with open(memdump_path, 'rb') as f:
            memdump = f.read()

        if len(memdump) != 65536:
            print(f"WARNING: memdump is {len(memdump)} bytes, expected 65536")
            return 1

        # Search the full 64KB for freq tables
        # load_addr=0 since memdump addresses are absolute
        pal_result = _find_freq_table_pal(memdump, 0)
        generic_result = _find_freq_table_generic(memdump, 0)

        if pal_result:
            offset, first_note, num_notes, lo_first = pal_result
            print(f"MEMDUMP PAL: Found freq table at ${offset:04X}, "
                  f"notes {first_note}-{first_note + num_notes - 1}, "
                  f"{'lo-first' if lo_first else 'hi-first'}")
        else:
            print("MEMDUMP PAL: No PAL freq table found")

        if generic_result:
            offset, first_note, num_notes, lo_first = generic_result
            print(f"MEMDUMP GENERIC: Found freq table at ${offset:04X}, "
                  f"notes {first_note}-{first_note + num_notes - 1}, "
                  f"{'lo-first' if lo_first else 'hi-first'}")
        else:
            print("MEMDUMP GENERIC: No generic freq table found")

        found_in_memdump = pal_result is not None or generic_result is not None
        if not static_result and found_in_memdump:
            print("\n*** RUNTIME-COMPUTED FREQ TABLE DETECTED ***")
            print("This SID computes its frequency table at runtime.")
        elif static_result and found_in_memdump:
            print("\nFreq table found in both static binary and memdump (expected).")
        elif not static_result and not found_in_memdump:
            print("\nNo freq table found anywhere. May use a non-standard format.")
    finally:
        if cleanup and os.path.exists(memdump_path):
            os.unlink(memdump_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
