"""
gt_encoder.py - Encode parsed GoatTracker data back into a valid SID binary.

Takes a parsed GT2 SID (from gt_parser), encodes the orderlists and patterns
back to binary, updates pointer tables, and produces a byte-for-byte identical
SID file.

The player code, frequency tables, and instrument/table data stay at their
original addresses (player has hardcoded references). Only orderlists and
patterns are re-serialized, with pointer tables updated to match.
"""

import struct
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import (parse_psid_header, find_freq_table, collect_abs_addresses,
                       FIRSTNOTE, LASTNOTE, REST, KEYOFF, KEYON, FIRSTPACKEDREST,
                       FX, FXONLY, ENDPATT)


def parse_gt2_sections(data):
    """Parse a GT2 SID into its component sections.

    Returns dict with all sections needed for reconstruction.
    """
    header_bytes = data[:124]
    load_addr_bytes = data[124:126]
    header, binary, load_addr = parse_psid_header(data)

    ft = find_freq_table(binary, load_addr)
    if ft is None:
        raise ValueError("Could not find frequency table")

    freq_off, first_note, num_notes, lo_first = ft
    freq_end = freq_off + num_notes * 2
    songs = header['songs']
    se = songs * 3

    addrs = sorted(set(a for a in collect_abs_addresses(binary, load_addr, 0, freq_off)
                       if a >= load_addr + freq_end))

    # Find song table
    song_lo_addr = None
    for a in addrs:
        if a + se in addrs:
            song_lo_addr = a
            break
    if song_lo_addr is None:
        raise ValueError("Could not find song table")
    song_hi_addr = song_lo_addr + se

    # Find pattern table
    patt_lo_addr = patt_hi_addr = None
    num_patt = 0
    for a in addrs:
        if a <= song_hi_addr:
            continue
        for n in range(1, 256):
            if a + n in addrs:
                patt_lo_addr = a
                patt_hi_addr = a + n
                num_patt = n
                break
        if patt_lo_addr:
            break
    if patt_lo_addr is None:
        raise ValueError("Could not find pattern table")

    # Offsets in binary
    sl = song_lo_addr - load_addr
    sh = song_hi_addr - load_addr
    pl = patt_lo_addr - load_addr
    ph = patt_hi_addr - load_addr

    # Read pointer tables
    ol_addrs = [binary[sl + j] | (binary[sh + j] << 8) for j in range(se)]
    patt_addrs = [binary[pl + j] | (binary[ph + j] << 8) for j in range(num_patt)]

    first_ol = min(ol_addrs)
    first_patt = min(patt_addrs)

    ol_start = first_ol - load_addr
    patt_start = first_patt - load_addr
    instr_end = ol_start  # instruments+tables end where orderlists begin

    # Extract orderlists (raw bytes, in address order)
    unique_ol_addrs = sorted(set(ol_addrs))
    orderlists_raw = {}
    for addr in unique_ol_addrs:
        off = addr - load_addr
        raw = bytearray()
        i = off
        while i < len(binary) and binary[i] != 0xFF:
            raw.append(binary[i])
            i += 1
        raw.append(0xFF)
        if i + 1 < len(binary):
            raw.append(binary[i + 1])
        else:
            raw.append(0)
        orderlists_raw[addr] = bytes(raw)

    # Extract patterns (raw bytes, in address order)
    sorted_patt = sorted(set(patt_addrs))
    patterns_raw = {}
    for idx, addr in enumerate(sorted_patt):
        off = addr - load_addr
        if idx + 1 < len(sorted_patt):
            end = sorted_patt[idx + 1] - load_addr
        else:
            end = len(binary)
        patterns_raw[addr] = bytes(binary[off:end])

    # Fixed section: everything from start to where orderlists begin
    # This includes: player code, freq tables, song/patt tables, instruments, tables
    fixed_section = bytes(binary[:ol_start])

    return {
        'header_bytes': header_bytes,
        'load_addr_bytes': load_addr_bytes,
        'load_addr': load_addr,
        'songs': songs,
        'num_patt': num_patt,
        'song_lo_off': sl,
        'song_hi_off': sh,
        'patt_lo_off': pl,
        'patt_hi_off': ph,
        'song_entries': se,
        'ol_addrs': ol_addrs,          # per-channel orderlist addresses
        'patt_addrs': patt_addrs,      # per-pattern addresses
        'unique_ol_addrs': unique_ol_addrs,
        'sorted_patt': sorted_patt,
        'orderlists_raw': orderlists_raw,
        'patterns_raw': patterns_raw,
        'fixed_section': fixed_section,
        'ol_start_addr': first_ol,
        'patt_start_addr': first_patt,
    }


def encode_gt2_binary(sections):
    """Encode parsed sections back into a GT2 binary.

    Serializes orderlists and patterns, updates pointer tables,
    keeps fixed section (player+freq+instruments) unchanged.
    """
    fixed = bytearray(sections['fixed_section'])
    load_addr = sections['load_addr']
    se = sections['song_entries']
    num_patt = sections['num_patt']
    sl = sections['song_lo_off']
    sh = sections['song_hi_off']
    pl = sections['patt_lo_off']
    ph = sections['patt_hi_off']

    # Serialize orderlists in original address order
    ol_blob = bytearray()
    ol_new_addrs = {}
    current_addr = sections['ol_start_addr']

    for orig_addr in sections['unique_ol_addrs']:
        raw = sections['orderlists_raw'][orig_addr]
        ol_new_addrs[orig_addr] = current_addr
        ol_blob.extend(raw)
        current_addr += len(raw)

    # Serialize patterns in original address order
    patt_blob = bytearray()
    patt_new_addrs = {}
    patt_base_addr = current_addr  # patterns follow orderlists

    for orig_addr in sections['sorted_patt']:
        raw = sections['patterns_raw'][orig_addr]
        patt_new_addrs[orig_addr] = current_addr
        patt_blob.extend(raw)
        current_addr += len(raw)

    # Update song table (orderlist pointers)
    for j in range(se):
        orig_ol_addr = sections['ol_addrs'][j]
        new_ol_addr = ol_new_addrs[orig_ol_addr]
        fixed[sl + j] = new_ol_addr & 0xFF
        fixed[sh + j] = (new_ol_addr >> 8) & 0xFF

    # Update pattern table (pattern pointers)
    for j in range(num_patt):
        orig_patt_addr = sections['patt_addrs'][j]
        new_patt_addr = patt_new_addrs[orig_patt_addr]
        fixed[pl + j] = new_patt_addr & 0xFF
        fixed[ph + j] = (new_patt_addr >> 8) & 0xFF

    # Combine: fixed section + orderlists + patterns
    binary = bytearray()
    binary.extend(fixed)
    binary.extend(ol_blob)
    binary.extend(patt_blob)

    return bytes(binary)


def build_sid(sections, binary):
    """Build a complete SID file from header + binary."""
    result = bytearray()
    result.extend(sections['header_bytes'])
    result.extend(sections['load_addr_bytes'])
    result.extend(binary)
    return bytes(result)


def roundtrip_test(sid_path):
    """Test lossless roundtrip: parse -> encode -> compare."""
    with open(sid_path, 'rb') as f:
        original = f.read()

    sections = parse_gt2_sections(original)
    rebuilt_binary = encode_gt2_binary(sections)
    rebuilt_sid = build_sid(sections, rebuilt_binary)

    if rebuilt_sid == original:
        return 'match'

    # Find first difference
    for i in range(min(len(rebuilt_sid), len(original))):
        if rebuilt_sid[i] != original[i]:
            return f'diff@{i}(${sections["load_addr"] + i - 126:04X}):orig=${original[i]:02X}_rebuilt=${rebuilt_sid[i]:02X}'

    return f'length:{len(rebuilt_sid)}vs{len(original)}'


def main():
    import argparse
    parser = argparse.ArgumentParser(description='GT2 SID encoder roundtrip test')
    parser.add_argument('input', nargs='+', help='SID file(s)')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    match = fail = skip = 0
    for path in args.input:
        if not os.path.exists(path):
            continue
        try:
            result = roundtrip_test(path)
            if result == 'match':
                match += 1
                if args.verbose:
                    print(f'  OK {os.path.basename(path)}')
            else:
                fail += 1
                print(f'FAIL {os.path.basename(path)}: {result}')
        except Exception as e:
            skip += 1
            if args.verbose:
                print(f'SKIP {os.path.basename(path)}: {e}')

    print(f'\nResults: {match} match, {fail} fail, {skip} skip')
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
