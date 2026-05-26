"""
sid_data_extractor.py - Universal SID data table discovery.

Finds all data tables in any SID file by analyzing the 6502 player code's
address references. Works for any player engine — GoatTracker, DMC, JCH,
Hubbard, or any of the 642 identified players.

The technique:
1. Identify the player code region (before the frequency table)
2. Disassemble and collect all absolute address operands
3. Cluster referenced addresses into data tables
4. Extract each table's raw bytes

This is version-independent — the player code tells us where its data is.
"""

import struct
import sys
import os
import json
from collections import defaultdict

# 6502 instruction lengths by opcode
_INST_LEN = [0] * 256
for _op in [0x00,0x08,0x0A,0x18,0x28,0x2A,0x38,0x40,0x48,0x4A,0x58,0x60,
            0x68,0x6A,0x78,0x88,0x8A,0x98,0x9A,0xA8,0xAA,0xB8,0xBA,0xC8,
            0xCA,0xD8,0xE8,0xEA,0xF8]:
    _INST_LEN[_op] = 1
for _op in range(256):
    if _INST_LEN[_op] > 0:
        continue
    _mode = _op & 0x1F
    if _mode in (0x00,0x01,0x02,0x04,0x05,0x06,0x09,0x0A,
                 0x10,0x11,0x12,0x14,0x15,0x16):
        _INST_LEN[_op] = 2
for _i in range(256):
    if _INST_LEN[_i] == 0:
        _INST_LEN[_i] = 3

# 3-byte instructions that reference absolute addresses (not branches/jumps to code)
# These are the data access instructions: LDA, STA, LDX, LDY, STX, STY, etc.
_ABS_READ_OPS = {
    0x0D, 0x0E,  # ORA abs, ASL abs
    0x19, 0x1D, 0x1E,  # ORA abs,Y, ORA abs,X, ASL abs,X
    0x2C, 0x2D, 0x2E,  # BIT abs, AND abs, ROL abs
    0x39, 0x3D, 0x3E,  # AND abs,Y, AND abs,X, ROL abs,X
    0x4D, 0x4E,  # EOR abs, LSR abs
    0x59, 0x5D, 0x5E,  # EOR abs,Y, EOR abs,X, LSR abs,X
    0x6D, 0x6E,  # ADC abs, ROR abs
    0x79, 0x7D, 0x7E,  # ADC abs,Y, ADC abs,X, ROR abs,X
    0x8C, 0x8D, 0x8E,  # STY abs, STA abs, STX abs
    0x99, 0x9D,  # STA abs,Y, STA abs,X
    0xAC, 0xAD, 0xAE,  # LDY abs, LDA abs, LDX abs
    0xB9, 0xBC, 0xBD, 0xBE,  # LDA abs,Y, LDY abs,X, LDA abs,X, LDX abs,Y
    0xCC, 0xCD, 0xCE,  # CPY abs, CMP abs, DEC abs
    0xD9, 0xDD, 0xDE,  # CMP abs,Y, CMP abs,X, DEC abs,X
    0xEC, 0xED, 0xEE,  # CPX abs, SBC abs, INC abs
    0xF9, 0xFD, 0xFE,  # SBC abs,Y, SBC abs,X, INC abs,X
}

# JMP and JSR (code references, not data)
_CODE_JUMP_OPS = {0x4C, 0x20}  # JMP abs, JSR abs

# PAL frequency table patterns (for finding the code/data boundary)
FREQ_HI_NEEDLE = bytes([
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
])

FREQ_LO_NEEDLE = bytes([
    0x17,0x27,0x39,0x4B,0x5F,0x74,0x8A,0xA1,0xBA,0xD4,0xF0,0x0E,
    0x2D,0x4E,0x71,0x96,0xBE,0xE8,0x14,0x43,0x74,0xA9,0xE1,0x1C,
])


def parse_sid_header(data):
    """Parse PSID/RSID header."""
    if data[:4] not in (b'PSID', b'RSID'):
        raise ValueError("Not a SID file")
    data_offset = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    songs = struct.unpack('>H', data[14:16])[0]
    title = data[22:54].split(b'\x00')[0].decode('latin-1')
    author = data[54:86].split(b'\x00')[0].decode('latin-1')

    payload = data[data_offset:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary = payload[2:]
    else:
        binary = payload

    return {
        'title': title,
        'author': author,
        'load_addr': load_addr,
        'init_addr': init_addr,
        'play_addr': play_addr,
        'songs': songs,
    }, binary, load_addr


def find_freq_table(binary):
    """Find the frequency table in the binary. Returns (offset, order) or None.

    Searches for the distinctive PAL frequency table pattern.
    Uses a sliding window with fuzzy matching (>= 20/24 bytes match).
    """
    # Phase 1: Try both hi and lo needles with fuzzy matching, require both
    for needle, name in [(FREQ_HI_NEEDLE, 'hi'), (FREQ_LO_NEEDLE, 'lo')]:
        for pos in range(len(binary) - 24):
            match = sum(1 for i in range(24) if binary[pos + i] == needle[i])
            if match < 20:
                continue

            other_needle = FREQ_LO_NEEDLE if name == 'hi' else FREQ_HI_NEEDLE

            for other_pos in [pos + 96, pos - 96]:
                if other_pos < 0 or other_pos + 24 > len(binary):
                    continue
                other_match = sum(1 for i in range(24)
                                  if binary[other_pos + i] == other_needle[i])
                if other_match >= 20:
                    if name == 'hi':
                        if other_pos > pos:
                            return pos, 'hi_lo'
                        else:
                            return other_pos, 'lo_hi'
                    else:
                        if other_pos > pos:
                            return pos, 'lo_hi'
                        else:
                            return other_pos, 'hi_lo'

    # Phase 2: Hi-only matching (DMC uses custom lo tables sometimes)
    # The hi table is always standard (octave relationships are fixed)
    for pos in range(len(binary) - 24):
        match = sum(1 for i in range(24) if binary[pos + i] == FREQ_HI_NEEDLE[i])
        if match >= 22:  # stricter threshold since we only have one table
            # Assume hi-lo order (most common for DMC)
            return pos, 'hi_lo'

    return None


def collect_addresses(binary, load_addr, code_regions):
    """Collect all absolute address references from code regions.

    Returns dict mapping each referenced address to:
    - count: how many times referenced
    - ops: which opcodes reference it
    - is_data: True if referenced by data-access instruction
    - is_code: True if referenced by JMP/JSR
    """
    refs = defaultdict(lambda: {'count': 0, 'ops': set(), 'is_data': False, 'is_code': False})

    for start, end in code_regions:
        i = start
        while i < end and i < len(binary):
            op = binary[i]
            ln = _INST_LEN[op]
            if ln == 3 and i + 2 < len(binary):
                addr = binary[i + 1] | (binary[i + 2] << 8)
                # Only count references within the binary's address range
                if load_addr <= addr < load_addr + len(binary):
                    refs[addr]['count'] += 1
                    refs[addr]['ops'].add(op)
                    if op in _ABS_READ_OPS:
                        refs[addr]['is_data'] = True
                    if op in _CODE_JUMP_OPS:
                        refs[addr]['is_code'] = True
            i += ln

    return dict(refs)


def cluster_addresses(refs, load_addr, binary_len, min_gap=8):
    """Cluster referenced addresses into table regions.

    Addresses within min_gap bytes of each other are grouped.
    Returns list of (start_addr, end_addr, num_refs, is_data, is_code).
    """
    data_addrs = sorted(a for a, r in refs.items() if r['is_data'])
    if not data_addrs:
        return []

    clusters = []
    cluster_start = data_addrs[0]
    cluster_end = data_addrs[0]
    cluster_refs = refs[data_addrs[0]]['count']
    cluster_is_code = refs[data_addrs[0]]['is_code']

    for addr in data_addrs[1:]:
        if addr - cluster_end <= min_gap:
            cluster_end = addr
            cluster_refs += refs[addr]['count']
            if refs[addr]['is_code']:
                cluster_is_code = True
        else:
            clusters.append({
                'start': cluster_start,
                'end': cluster_end,
                'refs': cluster_refs,
                'is_code': cluster_is_code,
                'size_hint': cluster_end - cluster_start + 1,
            })
            cluster_start = addr
            cluster_end = addr
            cluster_refs = refs[addr]['count']
            cluster_is_code = refs[addr]['is_code']

    clusters.append({
        'start': cluster_start,
        'end': cluster_end,
        'refs': cluster_refs,
        'is_code': cluster_is_code,
        'size_hint': cluster_end - cluster_start + 1,
    })

    return clusters


def extract_data_tables(sid_path):
    """Extract all data tables from a SID file.

    Returns dict with header info, code regions, data table clusters,
    and raw bytes for each identified table.
    """
    with open(sid_path, 'rb') as f:
        data = f.read()

    header, binary, load_addr = parse_sid_header(data)

    # Find frequency table
    ft = find_freq_table(binary)
    if ft is None:
        # No freq table found — treat everything as one blob
        freq_off = len(binary)
        freq_end = len(binary)
        freq_order = None
    else:
        freq_off, freq_order = ft
        freq_end = freq_off + 192  # 96 hi + 96 lo bytes

    # Identify code regions
    # Primary code: from start to freq table
    code_regions = [(0, freq_off)]

    # Some players (like DMC) have code between freq table and data tables
    # We detect this by looking for JMP/JSR targets in the post-freq area
    # For now, also scan a region after freq tables for code
    if freq_end < len(binary):
        # Scan post-freq area for code (limited to ~1KB)
        extra_code_end = min(freq_end + 1024, len(binary))
        code_regions.append((freq_end, extra_code_end))

    # Collect all address references
    refs = collect_addresses(binary, load_addr, code_regions)

    # All data-access references
    all_data_refs = {a: r for a, r in refs.items() if r['is_data']}

    # Cluster ALL data references into tables
    clusters = cluster_addresses(refs, load_addr, len(binary))

    # Include all clusters — let the caller decide what's code vs data
    data_clusters = clusters

    # Extract raw bytes for each cluster
    for cluster in data_clusters:
        start_off = cluster['start'] - load_addr
        # Estimate table size: distance to next cluster or end of binary
        idx = data_clusters.index(cluster)
        if idx + 1 < len(data_clusters):
            end_off = data_clusters[idx + 1]['start'] - load_addr
        else:
            end_off = len(binary)
        cluster['raw'] = bytes(binary[start_off:end_off])
        cluster['offset'] = start_off

    result = {
        'file': os.path.basename(sid_path),
        'header': header,
        'load_addr': load_addr,
        'binary_size': len(binary),
        'freq_table': {
            'offset': freq_off,
            'order': freq_order,
        } if ft else None,
        'code_regions': code_regions,
        'num_data_refs': len(all_data_refs),
        'data_tables': [{
            'start_addr': f'${c["start"]:04X}',
            'offset': c['offset'],
            'refs': c['refs'],
            'size_hint': c['size_hint'],
            'is_code': c['is_code'],
            'raw_size': len(c.get('raw', b'')),
        } for c in data_clusters],
    }

    return result, data_clusters


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Extract data tables from SID files')
    parser.add_argument('input', nargs='+', help='SID file(s)')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--output', help='Output JSON file')
    args = parser.parse_args()

    all_results = []
    for path in args.input:
        if not os.path.exists(path):
            continue
        try:
            result, clusters = extract_data_tables(path)
            all_results.append(result)

            if args.verbose:
                h = result['header']
                print(f'\n=== {h["title"]} by {h["author"]} ===')
                print(f'  Load: ${result["load_addr"]:04X}, Size: {result["binary_size"]}')
                if result['freq_table']:
                    ft = result['freq_table']
                    print(f'  Freq table: +${ft["offset"]:04X} ({ft["order"]})')
                print(f'  Data references: {result["num_data_refs"]}')
                print(f'  Data tables: {len(result["data_tables"])}')
                for t in result['data_tables']:
                    code_flag = ' [+code]' if t['is_code'] else ''
                    print(f'    {t["start_addr"]} +${t["offset"]:04X} '
                          f'({t["raw_size"]:5d} bytes, {t["refs"]:3d} refs){code_flag}')
            else:
                print(f'{result["file"]:40s} tables={len(result["data_tables"]):2d} '
                      f'refs={result["num_data_refs"]:3d}')
        except Exception as e:
            print(f'ERROR {os.path.basename(path)}: {e}')

    if args.output:
        # Strip raw bytes for JSON serialization
        for r in all_results:
            for t in r['data_tables']:
                if 'raw' in t:
                    del t['raw']
        with open(args.output, 'w') as f:
            json.dump(all_results, f, indent=2)


if __name__ == '__main__':
    main()
