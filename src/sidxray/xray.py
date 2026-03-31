#!/usr/bin/env python3
"""
sidxray — Main entry point.

Usage: python3 -m sidxray.xray <file.sid> [--duration N]

Runs the SID under emulation, traces all memory reads, and reports
the identified data structures.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sidxray.trace import capture
from sidxray.analyze import analyze_traces, find_regions, classify_regions, identify_tables


def main():
    parser = argparse.ArgumentParser(description='SID X-Ray: observe player data access')
    parser.add_argument('input', help='SID file to analyze')
    parser.add_argument('--duration', type=int, default=5, help='Duration in seconds')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

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

    # Total unique addresses read
    all_addrs = set()
    total_reads = 0
    for ft in frames:
        for r in ft.reads:
            all_addrs.add(r.addr)
            total_reads += 1
    print(f'{len(all_addrs)} unique addresses, {total_reads} total reads')
    if all_addrs:
        print(f'Address range: ${min(all_addrs):04X}-${max(all_addrs):04X}')

    # Analyze
    result = analyze_traces(frames, metadata)
    regions = find_regions(result)
    classify_regions(regions, result, num_frames)
    tables = identify_tables(result, frames)

    # Report regions
    print(f'\n=== Memory Regions ({len(regions)}) ===')
    for r in regions:
        size = r.end - r.start
        duty = r.frames_active / max(1, num_frames) * 100
        print(f'  ${r.start:04X}-${r.end - 1:04X} ({size:4d} bytes) '
              f'reads={r.access_count:6d} duty={duty:5.1f}% [{r.label}]')

    # Report detected tables (sequential stepping)
    if tables:
        print(f'\n=== Sequential Table Access ({len(tables)}) ===')
        for base, length in tables:
            # Read the values
            vals = []
            for a in range(base, base + min(length, 16)):
                entries = result.addr_values.get(a, [])
                if entries:
                    vals.append(f'{entries[0][1]:02X}')
            val_str = ' '.join(vals)
            print(f'  ${base:04X} len={length:3d}: [{val_str}]')

    # Detailed per-address info for verbose mode
    if args.verbose:
        print(f'\n=== Per-Address Detail (top 50 by reads) ===')
        top = sorted(result.addr_reads.items(), key=lambda x: -x[1])[:50]
        for addr, count in top:
            nframes = len(result.addr_frames[addr])
            vals = set(v for _, v in result.addr_values[addr])
            val_str = ','.join(f'{v:02X}' for v in sorted(vals)[:8])
            print(f'  ${addr:04X}: {count:5d} reads in {nframes:4d} frames  vals=[{val_str}]')


if __name__ == '__main__':
    main()
