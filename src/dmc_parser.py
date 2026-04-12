"""
dmc_parser.py - Parse DMC (Demo Music Creator) SID files.

Uses the universal address analysis technique: find the freq table,
then use player code references to locate all data tables.

Supports DMC V2/V3/V4 (11-byte instruments, 64 sectors, $7F end)
and DMC V5 (8-byte instruments, 96 sectors, $FF end).
See src/dmc/docs/README.md for full format documentation.

DMC sector encoding:
  $00-$5F: Note (C-0 through B-7, 96 notes)
  $60-$7C: Duration (AND $1F = ticks)
  $7D: Continuation (no ADSR reset on next note)
  $7E: Gate off
  $7F: End of sector (V4) / $FF: End of sector (V5)
  $80-$9F: Instrument select (AND $1F)
  $A0-$BF: Glide command ($A0 + semitones)
  $C0-$DF: Extended commands (V5/V7.1: filter/ADSR/volume)

FX byte flags (instrument byte 10 for V4, varies for V5):
  Bit 0: DRUM EFFECT    Bit 4: HOLDING FX
  Bit 1: NO FILT RES    Bit 5: FILTER FX
  Bit 2: NO PULS RES    Bit 6: DUAL EFFECT
  Bit 3: NO GATE FX     Bit 7: CYMBAL FX
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
DMC_CMD_MIN = 0xC0
DMC_CMD_MAX = 0xDF
DMC_SECTOR_END_V5 = 0xFF

# Version-specific constants
DMC_V4_INSTR_SIZE = 11  # AD, SR, wave_ptr, PW1, PW2, PW3, PW-L, Vib1, Vib2, Filter, FX
DMC_V5_INSTR_SIZE = 8   # AD, SR, vib*3, wave/pulse/filter table pointers
DMC_V4_MAX_SECTORS = 64
DMC_V5_MAX_SECTORS = 96
DMC_MAX_INSTRUMENTS = 32


def detect_dmc_version(binary, freq_off):
    """Detect DMC version from player code signatures.

    V5.x: BC ?? ?? B9 ?? ?? C9 90 (wave table LDY,X + LDA,Y + CMP #$90)
    V4.x: FE ?? ?? BD ?? ?? 18 7D (INC + LDA,X + CLC + ADC,Y — pulse width code)
    V2/V3: same as V4 (Brian: "practically the same program")

    Returns 'v4' or 'v5'.
    """
    # Search only in player code (before freq table)
    code_end = min(freq_off, len(binary) - 8)
    for i in range(code_end):
        if (binary[i] == 0xBC and binary[i+3] == 0xB9 and
            binary[i+6] == 0xC9 and binary[i+7] == 0x90):
            return 'v5'
    return 'v4'


def find_sector_pointers(binary, load_addr, search_start, max_sectors):
    """Find sector pointer table by brute-force scanning data region.

    DMC stores sector addresses as parallel lo/hi byte arrays.
    The lo array is at some offset, the hi array is lo + N (where N = sector count).
    Each (lo[k], hi[k]) pair forms a 16-bit address pointing to sector data.

    We score candidates by checking how many pointed-to addresses contain
    valid sector start bytes.
    """
    best = None
    best_score = 0

    for lo_off in range(search_start, len(binary) - 6):
        for n in range(3, min(max_sectors + 1, (len(binary) - lo_off) // 2 + 1)):
            hi_off = lo_off + n
            if hi_off + n > len(binary):
                break

            # Quick check: all reconstructed addresses must be in range
            valid = 0
            total_valid = True
            addrs = []
            for k in range(n):
                addr = binary[lo_off + k] | (binary[hi_off + k] << 8)
                if not (load_addr <= addr < load_addr + len(binary)):
                    total_valid = False
                    break
                addrs.append(addr)
                # Check if pointed-to byte looks like sector data start
                aoff = addr - load_addr
                b = binary[aoff]
                if b <= DMC_GLIDE_MAX or b == DMC_GATEOFF or b == DMC_SECTOR_END_V5:
                    valid += 1

            if not total_valid:
                continue

            # Need high validity rate and reasonable sector count
            if valid >= n * 0.8 and valid > best_score:
                best_score = valid
                best = (lo_off, hi_off, n, addrs)

    return best


def find_dmc_layout(binary, load_addr):
    """Find DMC data sections using freq table + address analysis.

    Returns dict with all section offsets, or None if not DMC.
    """
    ft = find_freq_table(binary)
    if ft is None:
        return None

    freq_off, freq_order = ft
    freq_end = freq_off + 192

    if freq_order == 'hi_lo':
        fhi_off = freq_off
    else:
        fhi_off = freq_off + 96

    dmc_version = detect_dmc_version(binary, freq_off)
    instr_size = DMC_V5_INSTR_SIZE if dmc_version == 'v5' else DMC_V4_INSTR_SIZE
    max_sectors = DMC_V5_MAX_SECTORS if dmc_version == 'v5' else DMC_V4_MAX_SECTORS
    instr_table_size = DMC_MAX_INSTRUMENTS * instr_size

    # Instrument table location
    # V4: fixed at fhi + $0248
    # V5: try fhi + $0248 first, then search via player code refs
    instr_off = fhi_off + 0x0248
    if instr_off + instr_table_size > len(binary):
        # Fallback: search for instrument table via Y-indexed refs
        code_end = freq_off
        instr_refs = set()
        for i in range(code_end - 2):
            if binary[i] == 0xB9:  # LDA abs,Y
                addr = binary[i+1] | (binary[i+2] << 8)
                off = addr - load_addr
                if freq_end < off < len(binary) - instr_table_size:
                    instr_refs.add(off)
        if instr_refs:
            instr_off = min(instr_refs)
        else:
            return None

    if instr_off + instr_table_size > len(binary):
        return None

    # Verify: check that instruments look valid
    instr_region = binary[instr_off:instr_off + instr_table_size]
    nonzero_instrs = sum(1 for i in range(DMC_MAX_INSTRUMENTS)
                         if any(instr_region[i*instr_size+j] != 0
                                for j in range(instr_size)))
    if nonzero_instrs < 2:
        return None

    instr_end = instr_off + instr_table_size

    # Find sector pointer table using two strategies:
    # 1. Code-referenced address pairs (original approach)
    # 2. Brute-force scan of data region (fallback for V5)

    # Strategy 1: code-referenced addresses
    code_regions = [
        (0, freq_off),
        (freq_end, instr_off),
    ]
    refs = collect_addresses(binary, load_addr, code_regions)
    data_addrs = sorted(a for a, r in refs.items()
                        if r['is_data'] and (a - load_addr) >= instr_end)

    sector_ptr_lo = None
    sector_ptr_hi = None
    num_sectors = 0
    sector_addrs = []

    # Try code-referenced address pairs first
    best_score = 0
    for i in range(len(data_addrs)):
        for j in range(i + 1, len(data_addrs)):
            lo_addr = data_addrs[i]
            hi_addr = data_addrs[j]
            n = hi_addr - lo_addr
            if n < 3 or n > max_sectors:
                continue

            lo_off = lo_addr - load_addr
            hi_off = hi_addr - load_addr
            if hi_off + n > len(binary):
                continue

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

            score = 0
            for addr in addrs:
                off = addr - load_addr
                if off < len(binary):
                    b = binary[off]
                    if b <= DMC_GLIDE_MAX or b == DMC_GATEOFF:
                        score += 1

            if score > best_score and score >= n * 0.7:
                best_score = score
                sector_ptr_lo = lo_addr
                sector_ptr_hi = hi_addr
                num_sectors = n

    # Strategy 2: brute-force scan if code refs didn't find enough sectors
    if num_sectors == 0:
        result = find_sector_pointers(binary, load_addr, instr_end, max_sectors)
        if result:
            lo_off, hi_off, n, addrs = result
            sector_ptr_lo = load_addr + lo_off
            sector_ptr_hi = load_addr + hi_off
            num_sectors = n

    # Read sector addresses
    if sector_ptr_lo:
        lo_off = sector_ptr_lo - load_addr
        hi_off = sector_ptr_hi - load_addr
        sector_addrs = []
        for k in range(num_sectors):
            addr = binary[lo_off + k] | (binary[hi_off + k] << 8)
            sector_addrs.append(addr)

    return {
        'dmc_version': dmc_version,
        'instr_size': instr_size,
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


def parse_instruments(binary, instr_off, instr_size=DMC_V4_INSTR_SIZE):
    """Parse 32 DMC instruments.

    V4: 11 bytes — AD, SR, wave_ptr, PW1, PW2, PW3, PW-L, Vib1, Vib2, Filter, FX
    V5: 8 bytes  — AD, SR, Vib1, Vib2, Vib3, wave_ptr, pulse_ptr, filter_ptr
    """
    instruments = []
    for i in range(DMC_MAX_INSTRUMENTS):
        base = instr_off + i * instr_size
        if base + instr_size > len(binary):
            instruments.append(None)
            continue
        raw = list(binary[base:base + instr_size])
        if all(b == 0 for b in raw):
            instruments.append(None)
            continue

        if instr_size == DMC_V4_INSTR_SIZE:
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
        else:  # V5: 8 bytes
            instruments.append({
                'index': i,
                'ad': raw[0],
                'sr': raw[1],
                'vib1': raw[2],
                'vib2': raw[3],
                'vib3': raw[4],
                'wave_ptr': raw[5],
                'pulse_ptr': raw[6],
                'filter_ptr': raw[7],
                # V5 has no per-instrument FX byte or pulse params
                'fx': 0,
                'pw1': 0, 'pw2': 0, 'pw3': 0, 'pw_limit': 0,
                'filter': 0,
            })
    return instruments


def decode_sector(binary, load_addr, sector_addr, next_sector_addr=None,
                   dmc_version='v4'):
    """Decode a single DMC sector into events.

    V4 sector end: $7F. V5 sector end: $FF.
    Returns list of event dicts.
    """
    off = sector_addr - load_addr
    if off < 0 or off >= len(binary):
        return []

    max_off = (next_sector_addr - load_addr) if next_sector_addr else len(binary)
    sector_end = DMC_SECTOR_END_V5 if dmc_version == 'v5' else DMC_SECTOR_END_V4
    events = []
    i = off

    while i < max_off and i < len(binary):
        b = binary[i]

        if b == sector_end:
            break
        # V4 also stops at $7F even when parsing as generic
        if dmc_version == 'v4' and b == DMC_SECTOR_END_V4:
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
        elif DMC_CMD_MIN <= b <= DMC_CMD_MAX:
            # V5/V7.1 extended commands (filter/ADSR/volume)
            events.append({'type': 'command', 'value': b})
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

    dmc_version = layout['dmc_version']
    instr_size = layout['instr_size']

    # Parse instruments (keep full 32-element array to preserve index mapping)
    instruments = parse_instruments(binary, layout['instr_off'], instr_size)

    # Parse sectors
    sectors = []
    sorted_addrs = sorted(set(layout['sector_addrs']))
    for idx, addr in enumerate(layout['sector_addrs']):
        # Find next sector for boundary
        sa_idx = sorted_addrs.index(addr)
        next_addr = sorted_addrs[sa_idx + 1] if sa_idx + 1 < len(sorted_addrs) else None
        events = decode_sector(binary, load_addr, addr, next_addr,
                               dmc_version=dmc_version)
        sectors.append(events)

    # Count notes
    total_notes = sum(sum(1 for e in sec if e['type'] == 'note') for sec in sectors)

    return {
        'file': os.path.basename(sid_path),
        'header': header,
        'load_addr': load_addr,
        'binary_size': len(binary),
        'dmc_version': dmc_version,
        'layout': {k: v for k, v in layout.items()
                   if k not in ('data_addrs',) and not isinstance(v, list)},
        'num_sectors': layout['num_sectors'],
        'sector_addrs': [f'${a:04X}' for a in layout['sector_addrs']],
        'instruments': instruments,
        'num_instruments': sum(1 for i in instruments if i is not None),
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
