#!/usr/bin/env python3
"""
memdiff.py — Memory region classifier using siddump --memdump.

Compares 64KB C64 memory snapshots at different points in time to classify
memory regions as static, dynamic, init-only, or self-modifying code.

Usage:
    python3 src/memdiff.py <file.sid> [--verbose] [--json]
"""

import argparse
import json
import os
import struct
import subprocess
import sys
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SIDDUMP = os.path.join(SCRIPT_DIR, '..', 'tools', 'siddump')
sys.path.insert(0, SCRIPT_DIR)
from gt_parser import parse_psid_header


def _memdump(sid_path, duration, dump_path):
    """Run siddump with --memdump and return the 64KB snapshot."""
    r = subprocess.run(
        [SIDDUMP, sid_path, '--memdump', dump_path, '--duration', str(duration)],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode not in (0, 2):  # 2 = silent tune, still writes memdump
        raise RuntimeError(f'siddump failed (exit {r.returncode}): {r.stderr.strip()}')
    with open(dump_path, 'rb') as f:
        data = f.read()
    if len(data) != 65536:
        raise RuntimeError(f'Expected 65536 bytes, got {len(data)}')
    return data


def _find_ranges(changed_set, start=0, end=65536):
    """Convert a set of addresses to a list of (start, end) inclusive ranges."""
    if not changed_set:
        return []
    addrs = sorted(a for a in changed_set if start <= a < end)
    if not addrs:
        return []
    ranges = []
    rng_start = addrs[0]
    prev = addrs[0]
    for a in addrs[1:]:
        if a == prev + 1:
            prev = a
        else:
            ranges.append((rng_start, prev))
            rng_start = a
            prev = a
    ranges.append((rng_start, prev))
    return ranges


def _merge_nearby(ranges, gap=4):
    """Merge ranges that are within `gap` bytes of each other."""
    if not ranges:
        return []
    merged = [list(ranges[0])]
    for start, end in ranges[1:]:
        if start <= merged[-1][1] + gap + 1:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(r) for r in merged]


def _get_code_range(sid_path):
    """Determine the code/data area from the SID file header.

    Returns (load_addr, end_addr, header_dict).
    """
    with open(sid_path, 'rb') as f:
        data = f.read()
    header, binary, load_addr = parse_psid_header(data)
    end_addr = load_addr + len(binary)
    return load_addr, end_addr, header


def classify_memory(sid_path):
    """Classify 64KB C64 memory into regions based on behavior over time.

    Takes three memory snapshots:
      - After init only (duration=0, 0 play frames)
      - After ~50 frames / 1 second (duration=1)
      - After ~250 frames / 5 seconds (duration=5)

    Returns dict with:
      - static_regions: list of (start, end) byte ranges that never change
      - dynamic_regions: list of (start, end) that change between snapshots
      - init_only_regions: changed by init but not by continued play
      - self_modifying: list of addresses in the code area that change
      - code_range: (load_addr, end_addr)
      - header: PSID header dict
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        dump0 = os.path.join(tmpdir, 'memdump_0.bin')
        dump1 = os.path.join(tmpdir, 'memdump_1.bin')
        dump5 = os.path.join(tmpdir, 'memdump_5.bin')

        mem0 = _memdump(sid_path, 0, dump0)
        mem1 = _memdump(sid_path, 1, dump1)
        mem5 = _memdump(sid_path, 5, dump5)

    # Get code range from PSID header
    load_addr, end_addr, header = _get_code_range(sid_path)

    # Per-byte change classification
    changed_init_to_1s = set()   # changed between init and 1s
    changed_1s_to_5s = set()     # changed between 1s and 5s

    for i in range(65536):
        if mem0[i] != mem1[i]:
            changed_init_to_1s.add(i)
        if mem1[i] != mem5[i]:
            changed_1s_to_5s.add(i)

    # Dynamic: changed during play (any play snapshot pair)
    all_dynamic = changed_init_to_1s | changed_1s_to_5s

    # Init-only: changed between init and 1s, but stable during continued play
    init_only = changed_init_to_1s - changed_1s_to_5s

    # Any change across all three snapshots
    any_change = set()
    for i in range(65536):
        if mem0[i] != mem1[i] or mem1[i] != mem5[i] or mem0[i] != mem5[i]:
            any_change.add(i)

    # Static: addresses that never change (within the loaded data range only)
    static_addrs = set()
    for i in range(load_addr, min(end_addr, 65536)):
        if i not in any_change:
            static_addrs.add(i)

    # Self-modifying code: addresses within the code/data area that are dynamic
    self_mod_addrs = sorted(a for a in all_dynamic if load_addr <= a < end_addr)

    # Convert to merged ranges
    static_ranges = _merge_nearby(
        _find_ranges(static_addrs, load_addr, min(end_addr, 65536)), gap=0)
    dynamic_ranges = _merge_nearby(
        _find_ranges(all_dynamic, 0, 65536), gap=2)
    init_only_ranges = _merge_nearby(
        _find_ranges(init_only, 0, 65536), gap=2)

    return {
        'static_regions': static_ranges,
        'dynamic_regions': dynamic_ranges,
        'init_only_regions': init_only_ranges,
        'self_modifying': self_mod_addrs,
        'code_range': (load_addr, end_addr),
        'header': header,
    }


def print_report(result):
    """Print a human-readable report of the memory classification."""
    h = result['header']
    load_addr, end_addr = result['code_range']
    print(f"SID: {h.get('title', '?')} by {h.get('author', '?')}")
    print(f"Load: ${load_addr:04X}-${end_addr:04X} "
          f"({end_addr - load_addr} bytes)")
    print(f"Init: ${h['init_addr']:04X}  Play: ${h['play_addr']:04X}")
    print()

    # Static regions (only show non-trivial ones)
    big_static = [(s, e) for s, e in result['static_regions'] if e - s >= 16]
    print(f"Static regions: {len(result['static_regions'])} "
          f"({len(big_static)} with >= 16 bytes)")
    for start, end in big_static[:20]:
        print(f"  ${start:04X}-${end:04X} ({end - start + 1} bytes)")
    if len(big_static) > 20:
        print(f"  ... ({len(big_static)} total)")

    print(f"\nDynamic regions: {len(result['dynamic_regions'])}")
    for start, end in result['dynamic_regions']:
        print(f"  ${start:04X}-${end:04X} ({end - start + 1} bytes)")

    print(f"\nInit-only regions: {len(result['init_only_regions'])}")
    for start, end in result['init_only_regions']:
        print(f"  ${start:04X}-${end:04X} ({end - start + 1} bytes)")

    smc = result['self_modifying']
    print(f"\nSelf-modifying code addresses: {len(smc)}")
    if smc:
        smc_ranges = _merge_nearby([(a, a) for a in smc], gap=2)
        for start, end in smc_ranges[:20]:
            if start == end:
                print(f"  ${start:04X}")
            else:
                print(f"  ${start:04X}-${end:04X} ({end - start + 1} bytes)")
        if len(smc_ranges) > 20:
            print(f"  ... ({len(smc_ranges)} ranges total)")


def main():
    parser = argparse.ArgumentParser(
        description='Memory region classifier for C64 SID files using siddump --memdump')
    parser.add_argument('sid_file', help='Input SID file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    parser.add_argument('--json', action='store_true',
                        help='Output results as JSON')
    args = parser.parse_args()

    if not os.path.exists(args.sid_file):
        print(f'ERROR: {args.sid_file} not found', file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(SIDDUMP):
        print(f'ERROR: siddump not found at {SIDDUMP}', file=sys.stderr)
        print('Run: source src/env.sh && bash tools/build.sh', file=sys.stderr)
        sys.exit(1)

    result = classify_memory(args.sid_file)

    if args.json:
        # JSON-serializable version
        out = {
            'static_regions': [(f'${s:04X}', f'${e:04X}') for s, e in result['static_regions']],
            'dynamic_regions': [(f'${s:04X}', f'${e:04X}') for s, e in result['dynamic_regions']],
            'init_only_regions': [(f'${s:04X}', f'${e:04X}') for s, e in result['init_only_regions']],
            'self_modifying': [f'${a:04X}' for a in result['self_modifying']],
            'code_range': (f'${result["code_range"][0]:04X}', f'${result["code_range"][1]:04X}'),
        }
        print(json.dumps(out, indent=2))
    else:
        print_report(result)


if __name__ == '__main__':
    main()
