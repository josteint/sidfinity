#!/usr/bin/env python3
"""
sidxray — Main entry point.

Usage: python3 -m sidxray.xray <file.sid> [--duration N]

Runs the SID under emulation, traces all memory reads, and reports
the identified data structures.
"""

import sys
import os
import struct
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sidxray.trace import capture
from sidxray.analyze import analyze_traces, find_regions, classify_regions, identify_tables


def find_data_start(sid_path):
    """Find where data area starts (after player code) using freq table detection.

    Returns (load_addr, data_start_addr) or (0, 0) on failure.
    """
    with open(sid_path, 'rb') as f:
        raw = f.read()

    # Parse PSID header
    if raw[:4] not in (b'PSID', b'RSID'):
        return 0, 0
    data_offset = struct.unpack('>H', raw[6:8])[0]
    load_addr = struct.unpack('>H', raw[8:10])[0]
    payload = raw[data_offset:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary = payload[2:]
    else:
        binary = payload

    # Find freq table (look for known PAL freq lo bytes)
    PAL_LO = bytes([0x17,0x27,0x39,0x4b,0x5f,0x74,0x8a,0xa1,0xba,0xd4,0xf0,0x0e])
    pos = binary.find(PAL_LO)
    if pos >= 0:
        return load_addr, load_addr + pos
    # Try with fewer bytes
    for window in range(12, 7, -1):
        pos = binary.find(PAL_LO[:window])
        if pos >= 0:
            return load_addr, load_addr + pos
    return load_addr, load_addr


def main():
    parser = argparse.ArgumentParser(description='SID X-Ray: observe player data access')
    parser.add_argument('input', help='SID file to analyze')
    parser.add_argument('--duration', type=int, default=5, help='Duration in seconds')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    # Find code/data boundary
    load_addr, data_start = find_data_start(args.input)
    print(f'Load: ${load_addr:04X}, data starts: ${data_start:04X}')

    print(f'Capturing {args.duration}s of memory trace...')
    metadata, frames = capture(args.input, args.duration)

    if not frames:
        print('No trace data captured.')
        return

    title = metadata.get('title', '?')
    author = metadata.get('author', '?')
    num_frames = len(frames)
    print(f'"{title}" by {author}')
    print(f'{num_frames} frames captured')

    # Filter: only keep reads from data area (after freq table)
    for ft in frames:
        ft.reads = [r for r in ft.reads if r.addr >= data_start]

    # Total unique addresses read
    all_addrs = set()
    total_reads = 0
    for ft in frames:
        for r in ft.reads:
            all_addrs.add(r.addr)
            total_reads += 1
    print(f'{len(all_addrs)} unique data addresses, {total_reads} total data reads')
    if all_addrs:
        print(f'Data range: ${min(all_addrs):04X}-${max(all_addrs):04X}')

    # Analyze
    result = analyze_traces(frames, metadata)
    regions = find_regions(result)
    classify_regions(regions, result, num_frames)
    tables = identify_tables(result, frames)

    # Report regions
    print(f'\n=== Data Regions ({len(regions)}) ===')
    for r in regions:
        size = r.end - r.start
        duty = r.frames_active / max(1, num_frames) * 100
        print(f'  ${r.start:04X}-${r.end - 1:04X} ({size:4d} bytes) '
              f'reads={r.access_count:6d} duty={duty:5.1f}% [{r.label}]')

    # Report detected tables
    if tables:
        print(f'\n=== Sequential Table Access ({len(tables)}) ===')
        for base, length in tables:
            vals = []
            for a in range(base, base + min(length, 16)):
                entries = result.addr_values.get(a, [])
                if entries:
                    vals.append(f'{entries[0][1]:02X}')
            val_str = ' '.join(vals)
            print(f'  ${base:04X} len={length:3d}: [{val_str}]')

    # Verbose: per-address detail
    if args.verbose:
        print(f'\n=== Per-Address Detail (top 40 by reads) ===')
        top = sorted(result.addr_reads.items(), key=lambda x: -x[1])[:40]
        for addr, count in top:
            nframes = len(result.addr_frames[addr])
            vals = set(v for _, v in result.addr_values[addr])
            val_str = ','.join(f'{v:02X}' for v in sorted(vals)[:8])
            duty = nframes / num_frames * 100
            print(f'  ${addr:04X}: {count:5d} reads in {nframes:4d} frames ({duty:5.1f}%)  vals=[{val_str}]')


if __name__ == '__main__':
    main()
