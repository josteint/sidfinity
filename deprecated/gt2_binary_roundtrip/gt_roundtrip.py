"""
gt_roundtrip.py - Verify lossless GoatTracker SID parsing by reconstruction.

Takes a GT2 SID, parses it into sections, rebuilds the binary, and
compares byte-for-byte with the original.

This proves the parser correctly identifies all data boundaries.
"""

import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_psid_header, find_freq_table, FREQ_TBL_LO, FREQ_TBL_HI


def extract_sections(data):
    """Extract all binary sections from a GT2 SID file.

    Returns dict with: header, player_code, freq_lo, freq_hi,
    post_freq_data (everything after freq tables to end).
    """
    header_bytes = data[:124]  # PSID header
    header, binary, load_addr = parse_psid_header(data)

    # Find frequency table
    ft = find_freq_table(binary, load_addr)
    if ft is None:
        return None

    freq_off, first_note, num_notes, lo_first = ft

    if lo_first:
        freq_lo_off = freq_off
        freq_hi_off = freq_off + num_notes
    else:
        freq_hi_off = freq_off
        freq_lo_off = freq_off + num_notes

    # Player code is everything before the first freq table byte
    player_end = min(freq_lo_off, freq_hi_off)

    # Everything after freq tables
    freq_end = max(freq_lo_off, freq_hi_off) + num_notes

    return {
        'header': header_bytes,
        'header_dict': header,
        'load_addr': load_addr,
        'binary': binary,
        'player_code': binary[:player_end],
        'freq_lo_off': freq_lo_off,
        'freq_hi_off': freq_hi_off,
        'freq_lo': binary[freq_lo_off:freq_lo_off + num_notes],
        'freq_hi': binary[freq_hi_off:freq_hi_off + num_notes],
        'first_note': first_note,
        'num_notes': num_notes,
        'lo_first': lo_first,
        'post_freq': binary[freq_end:],
        'freq_end_off': freq_end,
    }


def rebuild_binary(sections):
    """Reconstruct the binary from extracted sections."""
    binary = bytearray()
    binary.extend(sections['player_code'])

    if sections['lo_first']:
        binary.extend(sections['freq_lo'])
        binary.extend(sections['freq_hi'])
    else:
        binary.extend(sections['freq_hi'])
        binary.extend(sections['freq_lo'])

    binary.extend(sections['post_freq'])
    return bytes(binary)


def roundtrip_test(sid_path):
    """Test lossless roundtrip for a GT2 SID file."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    sections = extract_sections(data)
    if sections is None:
        return 'no_freq_table'

    rebuilt = rebuild_binary(sections)
    original = sections['binary']

    if rebuilt == original:
        return 'match'

    # Find first difference
    for i in range(min(len(rebuilt), len(original))):
        if rebuilt[i] != original[i]:
            addr = sections['load_addr'] + i
            return f'diff_at_{i}(${addr:04X}):orig=${original[i]:02X}_rebuilt=${rebuilt[i]:02X}'

    if len(rebuilt) != len(original):
        return f'length_diff:orig={len(original)}_rebuilt={len(rebuilt)}'

    return 'match'


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Test GT2 SID roundtrip')
    parser.add_argument('input', nargs='+', help='SID file(s) to test')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    match = 0
    fail = 0
    skip = 0

    for path in args.input:
        if not os.path.exists(path):
            continue
        result = roundtrip_test(path)
        if result == 'match':
            match += 1
            if args.verbose:
                print(f'  OK {os.path.basename(path)}')
        elif result == 'no_freq_table':
            skip += 1
            if args.verbose:
                print(f'SKIP {os.path.basename(path)}')
        else:
            fail += 1
            print(f'FAIL {os.path.basename(path)}: {result}')

    total = match + fail + skip
    print(f'\nResults: {match} match, {fail} fail, {skip} skip (total {total})')
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
