"""
dmc_parser.py - Parse DMC (Demo Music Creator) SID files.

Uses the universal address analysis technique: find the freq table,
then use player code references to locate all data tables.

DMC sector encoding:
  $00-$5F: Note (C-0 through B-7, 96 notes)
  $60-$7C: Duration (AND $1F = ticks)
  $7D: Continuation (no ADSR reset on next note)
  $7E: Gate off
  $7F: End of sector (V4) / also $FF for some versions
  $80-$9F: Instrument select (AND $1F)
  $A0-$BF: Glide command ($A0 + semitones)
  $C0-$DF: Additional commands
"""

import struct
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sid_data_extractor import (parse_sid_header, find_freq_table,
                                 collect_addresses, cluster_addresses,
                                 _INST_LEN)

NOTE_NAMES = ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']

# DMC constants
DMC_NOTE_MAX = 0x5F
DMC_DUR_MIN = 0x60
DMC_DUR_MAX = 0x7C
DMC_CONT = 0x7D
DMC_GATEOFF = 0x7E
DMC_SECTOR_END_V4 = 0x7F
DMC_INST_MIN = 0x80
DMC_INST_MAX = 0x9F
DMC_GLIDE_MIN = 0xA0
DMC_GLIDE_MAX = 0xBF
DMC_SECTOR_END_V5 = 0xFF


def find_dmc_layout(binary, load_addr):
    """Find DMC data sections using freq table + address analysis.

    Returns dict with all section offsets, or None if not DMC.
    """
    ft = find_freq_table(binary)
    if ft is None:
        return None

    freq_off, freq_order = ft
    freq_end = freq_off + 192

    # Instrument table is consistently at freq_hi + $0248
    if freq_order == 'hi_lo':
        fhi_off = freq_off
    else:
        fhi_off = freq_off + 96
    instr_off = fhi_off + 0x0248

    if instr_off + 352 > len(binary):
        return None

    # Verify: check that instruments look valid (not all zeros, not all code)
    instr_region = binary[instr_off:instr_off + 352]
    nonzero_instrs = sum(1 for i in range(32)
                         if any(instr_region[i*11+j] != 0 for j in range(11)))
    if nonzero_instrs < 2:
        return None

    # Collect all data addresses referenced by player code
    # Code is in multiple regions: before freq, and between freq and instruments
    code_regions = [
        (0, freq_off),
        (freq_end, instr_off),
    ]
    refs = collect_addresses(binary, load_addr, code_regions)

    # Find all data-access references after instruments
    instr_end = instr_off + 352
    data_addrs = sorted(a for a, r in refs.items()
                        if r['is_data'] and (a - load_addr) >= instr_end)

    # Find sector pointer table: a pair of referenced addresses where
    # the gap = N (sector count), and the N addresses they contain
    # point to valid sector data locations.
    sector_ptr_lo = None
    sector_ptr_hi = None
    num_sectors = 0

    best_score = 0
    for i in range(len(data_addrs)):
        for j in range(i + 1, len(data_addrs)):
            lo_addr = data_addrs[i]
            hi_addr = data_addrs[j]
            n = hi_addr - lo_addr
            if n < 3 or n > 64:
                continue

            lo_off = lo_addr - load_addr
            hi_off = hi_addr - load_addr
            if hi_off + n > len(binary):
                continue

            # Read addresses and check validity
            valid = True
            addrs = []
            for k in range(n):
                addr = binary[lo_off + k] | (binary[hi_off + k] << 8)
                if not (load_addr <= addr < load_addr + len(binary)):
                    valid = False
                    break
                addrs.append(addr)

            if not valid or len(addrs) != n:
                continue

            # Score: how many pointed-to locations look like sector data?
            # Sector data starts with note ($00-$5F), duration ($60-$7C),
            # instrument ($80-$9F), glide ($A0-$BF), gate off ($7E), or cmd ($C0+)
            score = 0
            for addr in addrs:
                off = addr - load_addr
                if off < len(binary):
                    b = binary[off]
                    if b <= 0xBF or b == 0x7E:
                        score += 1

            if score > best_score and score >= n * 0.7:
                best_score = score
                sector_ptr_lo = lo_addr
                sector_ptr_hi = hi_addr
                num_sectors = n

    # Read sector addresses
    sector_addrs = []
    if sector_ptr_lo:
        lo_off = sector_ptr_lo - load_addr
        hi_off = sector_ptr_hi - load_addr
        for k in range(num_sectors):
            addr = binary[lo_off + k] | (binary[hi_off + k] << 8)
            sector_addrs.append(addr)

    return {
        'freq_off': freq_off,
        'freq_order': freq_order,
        'freq_end': freq_end,
        'instr_off': instr_off,
        'instr_end': instr_end,
        'sector_ptr_lo': sector_ptr_lo,
        'sector_ptr_hi': sector_ptr_hi,
        'num_sectors': num_sectors,
        'sector_addrs': sector_addrs,
        'data_addrs': data_addrs,
    }


def parse_instruments(binary, instr_off):
    """Parse 32 DMC instruments (11 bytes each)."""
    instruments = []
    for i in range(32):
        base = instr_off + i * 11
        raw = list(binary[base:base + 11])
        if all(b == 0 for b in raw):
            instruments.append(None)
            continue
        instruments.append({
            'index': i,
            'ad': raw[0],
            'sr': raw[1],
            'wave_ptr': raw[2],
            'pw1': raw[3],
            'pw2': raw[4],
            'pw3': raw[5],
            'pw_limit': raw[6],
            'vib1': raw[7],
            'vib2': raw[8],
            'filter': raw[9],
            'fx': raw[10],
        })
    return instruments


def decode_sector(binary, load_addr, sector_addr, next_sector_addr=None):
    """Decode a single DMC sector into events.

    Returns list of event dicts.
    """
    off = sector_addr - load_addr
    if off < 0 or off >= len(binary):
        return []

    max_off = (next_sector_addr - load_addr) if next_sector_addr else len(binary)
    events = []
    i = off

    while i < max_off and i < len(binary):
        b = binary[i]

        if b == DMC_SECTOR_END_V4 or b == DMC_SECTOR_END_V5:
            break

        if b <= DMC_NOTE_MAX:
            note_num = b
            octave = note_num // 12
            name = NOTE_NAMES[note_num % 12]
            events.append({'type': 'note', 'value': note_num,
                          'name': f'{name}{octave}'})
        elif DMC_DUR_MIN <= b <= DMC_DUR_MAX:
            events.append({'type': 'duration', 'value': b & 0x1F})
        elif b == DMC_CONT:
            events.append({'type': 'continuation'})
        elif b == DMC_GATEOFF:
            events.append({'type': 'gate_off'})
        elif DMC_INST_MIN <= b <= DMC_INST_MAX:
            events.append({'type': 'instrument', 'value': b & 0x1F})
        elif DMC_GLIDE_MIN <= b <= DMC_GLIDE_MAX:
            events.append({'type': 'glide', 'value': b - DMC_GLIDE_MIN})
        else:
            events.append({'type': 'command', 'value': b})

        i += 1

    return events


def parse_dmc_sid(sid_path):
    """Parse a DMC SID file into structured data.

    Returns dict with header, instruments, sectors, or None.
    """
    with open(sid_path, 'rb') as f:
        data = f.read()

    header, binary, load_addr = parse_sid_header(data)

    layout = find_dmc_layout(binary, load_addr)
    if layout is None:
        return None

    # Parse instruments
    instruments = parse_instruments(binary, layout['instr_off'])
    active_instruments = [i for i in instruments if i is not None]

    # Parse sectors
    sectors = []
    sorted_addrs = sorted(set(layout['sector_addrs']))
    for idx, addr in enumerate(layout['sector_addrs']):
        # Find next sector for boundary
        sa_idx = sorted_addrs.index(addr)
        next_addr = sorted_addrs[sa_idx + 1] if sa_idx + 1 < len(sorted_addrs) else None
        events = decode_sector(binary, load_addr, addr, next_addr)
        sectors.append(events)

    # Count notes
    total_notes = sum(sum(1 for e in sec if e['type'] == 'note') for sec in sectors)

    return {
        'file': os.path.basename(sid_path),
        'header': header,
        'load_addr': load_addr,
        'binary_size': len(binary),
        'layout': {k: v for k, v in layout.items()
                   if k not in ('data_addrs',) and not isinstance(v, list)},
        'num_sectors': layout['num_sectors'],
        'sector_addrs': [f'${a:04X}' for a in layout['sector_addrs']],
        'instruments': active_instruments,
        'num_instruments': len(active_instruments),
        'sectors': sectors,
        'total_notes': total_notes,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parse DMC SID files')
    parser.add_argument('input', nargs='+', help='SID file(s)')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-o', '--output', help='Output JSON file')
    args = parser.parse_args()

    results = []
    for path in args.input:
        if not os.path.exists(path):
            continue
        result = parse_dmc_sid(path)
        if result is None:
            print(f'SKIP {os.path.basename(path)}: not DMC or parse failed')
            continue

        results.append(result)
        h = result['header']
        print(f'{result["file"]:40s} sectors={result["num_sectors"]:3d} '
              f'instr={result["num_instruments"]:2d} notes={result["total_notes"]:5d}')

        if args.verbose:
            print(f'  {h["title"]} by {h["author"]}')
            print(f'  Load=${result["load_addr"]:04X} Size={result["binary_size"]}')
            for i, sec in enumerate(result['sectors'][:5]):
                notes = [e['name'] for e in sec if e['type'] == 'note']
                print(f'  S{i:02d}: {len(sec)} events, notes: {notes[:8]}')
            if result['num_sectors'] > 5:
                print(f'  ... ({result["num_sectors"]} total sectors)')

    if args.output and results:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

    print(f'\nParsed: {len(results)} files')


if __name__ == '__main__':
    main()
