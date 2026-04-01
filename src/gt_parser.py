"""
gt_parser.py - Parse GoatTracker V2 SID files to extract native music data.

Extracts instruments, wave/pulse/filter/speed tables, orderlists, and patterns
from GoatTracker V2 SID binaries (PSID format).

The packed SID format differs from the .sng editor format — it's produced by
greloc.c which conditionally compiles the player and packs the data.
"""

import json
import struct
import sys
import os
from dataclasses import dataclass, field, asdict
from typing import Optional

# GoatTracker PAL frequency table (96 notes, C-0 to B-7)
FREQ_TBL_LO = bytes([
    0x17,0x27,0x39,0x4b,0x5f,0x74,0x8a,0xa1,0xba,0xd4,0xf0,0x0e,
    0x2d,0x4e,0x71,0x96,0xbe,0xe8,0x14,0x43,0x74,0xa9,0xe1,0x1c,
    0x5a,0x9c,0xe2,0x2d,0x7c,0xcf,0x28,0x85,0xe8,0x52,0xc1,0x37,
    0xb4,0x39,0xc5,0x5a,0xf7,0x9e,0x4f,0x0a,0xd1,0xa3,0x82,0x6e,
    0x68,0x71,0x8a,0xb3,0xee,0x3c,0x9e,0x15,0xa2,0x46,0x04,0xdc,
    0xd0,0xe2,0x14,0x67,0xdd,0x79,0x3c,0x29,0x44,0x8d,0x08,0xb8,
    0xa1,0xc5,0x28,0xcd,0xba,0xf1,0x78,0x53,0x87,0x1a,0x10,0x71,
    0x42,0x89,0x4f,0x9b,0x74,0xe2,0xf0,0xa6,0x0e,0x33,0x20,0xff,
])

FREQ_TBL_HI = bytes([
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0a,0x0a,0x0b,0x0c,0x0d,0x0d,0x0e,0x0f,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1a,0x1b,0x1d,0x1f,0x20,
    0x22,0x24,0x27,0x29,0x2b,0x2e,0x31,0x34,0x37,0x3a,0x3e,0x41,
    0x45,0x49,0x4e,0x52,0x57,0x5c,0x62,0x68,0x6e,0x75,0x7c,0x83,
    0x8b,0x93,0x9c,0xa5,0xaf,0xb9,0xc4,0xd0,0xdd,0xea,0xf8,0xff,
])

# Packed pattern byte ranges
ENDPATT = 0x00
FX = 0x40
FXONLY = 0x50
FIRSTNOTE = 0x60
LASTNOTE = 0xBC
REST = 0xBD
KEYOFF = 0xBE
KEYON = 0xBF
FIRSTPACKEDREST = 0xC0

NOTE_NAMES = ['C-','C#','D-','D#','E-','F-','F#','G-','G#','A-','A#','B-']

def note_name(n):
    """Convert note number (0-95) to name like C-0, A#4."""
    if n < 0 or n > 95:
        return f'?{n}'
    return f'{NOTE_NAMES[n % 12]}{n // 12}'


# 6502 instruction lengths
_INST_LEN = [0] * 256
for _op in [0x00,0x08,0x0A,0x18,0x28,0x2A,0x38,0x40,0x48,0x4A,0x58,0x60,
            0x68,0x6A,0x78,0x88,0x8A,0x98,0x9A,0xA8,0xAA,0xB8,0xBA,0xC8,
            0xCA,0xD8,0xE8,0xEA,0xF8]:
    _INST_LEN[_op] = 1
for _op in range(256):
    if _INST_LEN[_op] > 0:
        continue
    _mode = _op & 0x1F
    if _mode in (0x00,0x01,0x02,0x04,0x05,0x06,0x09,0x0A,0x10,0x11,0x12,0x14,0x15,0x16):
        _INST_LEN[_op] = 2
for _i in range(256):
    if _INST_LEN[_i] == 0:
        _INST_LEN[_i] = 3


def parse_psid_header(data):
    """Parse PSID/RSID header, return dict + binary payload."""
    magic = data[:4]
    if magic not in (b'PSID', b'RSID'):
        raise ValueError(f'Not a SID file: magic={magic!r}')
    version = struct.unpack('>H', data[4:6])[0]
    data_offset = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    songs = struct.unpack('>H', data[14:16])[0]
    start_song = struct.unpack('>H', data[16:18])[0]
    title = data[22:54].split(b'\x00')[0].decode('latin-1')
    author = data[54:86].split(b'\x00')[0].decode('latin-1')
    released = data[86:118].split(b'\x00')[0].decode('latin-1')

    payload = data[data_offset:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary = payload[2:]
    else:
        binary = payload

    return {
        'magic': magic.decode('ascii'),
        'version': version,
        'load_addr': load_addr,
        'init_addr': init_addr,
        'play_addr': play_addr,
        'songs': songs,
        'start_song': start_song,
        'title': title,
        'author': author,
        'released': released,
    }, binary, load_addr


def find_freq_table(binary, load_addr):
    """Find the GoatTracker frequency table in the binary.

    Returns (offset, first_note, num_notes, lo_first) or None.
    lo_first indicates whether lo bytes come before hi bytes.
    """
    # Try finding a slice of the lo table (at least 12 consecutive bytes)
    for first_note in range(84):  # can't start later than note 84 for 12 bytes
        for window in range(min(96 - first_note, 48), 11, -1):  # try longest match first
            needle = FREQ_TBL_LO[first_note:first_note + window]
            pos = binary.find(needle)
            if pos == -1:
                continue

            # Found lo bytes at pos. Check if hi bytes are adjacent.
            num_notes = window

            # Try to extend the match
            while (first_note + num_notes < 96 and
                   pos + num_notes < len(binary) and
                   binary[pos + num_notes] == FREQ_TBL_LO[first_note + num_notes]):
                num_notes += 1

            # Check hi bytes right after lo
            hi_pos = pos + num_notes
            if hi_pos + num_notes <= len(binary):
                hi_match = all(
                    binary[hi_pos + i] == FREQ_TBL_HI[first_note + i]
                    for i in range(num_notes)
                )
                if hi_match:
                    return (pos, first_note, num_notes, True)

            # Check hi bytes right before lo
            hi_pos = pos - num_notes
            if hi_pos >= 0:
                hi_match = all(
                    binary[hi_pos + i] == FREQ_TBL_HI[first_note + i]
                    for i in range(num_notes)
                )
                if hi_match:
                    return (hi_pos, first_note, num_notes, False)

    return None


def collect_abs_addresses(binary, load_addr, start_off, end_off):
    """Collect all absolute address operands from 6502 code in range.

    Returns sorted list of unique addresses that point into the data area.
    """
    addresses = set()
    data_start_addr = load_addr + end_off
    data_end_addr = load_addr + len(binary)

    i = start_off
    while i < end_off and i < len(binary):
        op = binary[i]
        ln = _INST_LEN[op]
        if ln == 3 and i + 2 < len(binary):
            addr = binary[i + 1] | (binary[i + 2] << 8)
            if data_start_addr <= addr < data_end_addr:
                addresses.add(addr)
        i += ln

    return sorted(addresses)


def find_song_and_pattern_tables(binary, load_addr, data_addrs, songs):
    """Find song table and pattern table addresses from the collected addresses.

    The song table has songs*3 lo bytes followed by songs*3 hi bytes.
    We look for address pairs where the gap = songs*3.
    """
    num_song_entries = songs * 3

    # Look for pairs of addresses with the right gap
    candidates = []
    for i, a1 in enumerate(data_addrs):
        target = a1 + num_song_entries
        if target in data_addrs:
            candidates.append(a1)

    # The song table usually comes first (before pattern table)
    # Validate: addresses pointed to by the song table should be in the data area
    for song_lo_addr in candidates:
        song_hi_addr = song_lo_addr + num_song_entries
        off_lo = song_lo_addr - load_addr
        off_hi = song_hi_addr - load_addr

        if off_lo + num_song_entries > len(binary) or off_hi + num_song_entries > len(binary):
            continue

        # Read orderlist addresses and check they're reasonable
        valid = True
        for j in range(num_song_entries):
            ol_addr = binary[off_lo + j] | (binary[off_hi + j] << 8)
            if not (load_addr <= ol_addr < load_addr + len(binary)):
                valid = False
                break

        if valid:
            return song_lo_addr, song_hi_addr

    return None, None


def find_pattern_table(binary, load_addr, data_addrs, song_hi_addr, songs):
    """Find the pattern table, which should come after the song table."""
    # Pattern table starts after song hi bytes
    search_start = song_hi_addr + songs * 3

    # Look for pairs of addresses where addresses pointed to are valid
    for i, a1 in enumerate(data_addrs):
        if a1 < search_start:
            continue
        # Try different pattern counts
        for num_patt in range(1, 209):
            a2 = a1 + num_patt
            if a2 in data_addrs:
                off_lo = a1 - load_addr
                off_hi = a2 - load_addr
                if off_lo + num_patt > len(binary) or off_hi + num_patt > len(binary):
                    continue
                # Validate pattern addresses
                valid = True
                for j in range(num_patt):
                    p_addr = binary[off_lo + j] | (binary[off_hi + j] << 8)
                    if not (load_addr <= p_addr < load_addr + len(binary)):
                        valid = False
                        break
                if valid:
                    return a1, a2, num_patt

    return None, None, 0


def extract_orderlists(binary, load_addr, song_lo_addr, song_hi_addr, songs, channels=3):
    """Extract orderlists for all songs/channels."""
    num_entries = songs * channels
    off_lo = song_lo_addr - load_addr
    off_hi = song_hi_addr - load_addr

    orderlists = []
    for s in range(songs):
        song_ols = []
        for c in range(channels):
            idx = s * channels + c
            ol_addr = binary[off_lo + idx] | (binary[off_hi + idx] << 8)
            ol_off = ol_addr - load_addr

            # Read until $FF
            entries = []
            i = ol_off
            while i < len(binary) and binary[i] != 0xFF:
                entries.append(binary[i])
                i += 1

            restart = binary[i + 1] if i + 1 < len(binary) else 0

            # Decode entries
            decoded = []
            j = 0
            while j < len(entries):
                b = entries[j]
                if b <= 0xCF:
                    decoded.append({'type': 'pattern', 'pattern': b})
                elif 0xD0 <= b <= 0xDF:
                    # In packed format, repeat: pattern byte comes first, then repeat
                    # Actually in packed orderlists the pattern is BEFORE the repeat marker
                    decoded.append({'type': 'repeat', 'count': (b & 0x0F) + 1})
                elif 0xE0 <= b <= 0xEF:
                    decoded.append({'type': 'transpose', 'value': (b & 0x0F) - 16})
                elif 0xF0 <= b <= 0xFE:
                    decoded.append({'type': 'transpose', 'value': b - 0xF0})
                j += 1

            song_ols.append({
                'entries': decoded,
                'restart': restart,
                'raw': list(entries),
            })
        orderlists.append(song_ols)

    return orderlists


def unpack_pattern(binary, load_addr, patt_addr, max_bytes=256):
    """Unpack a single packed GoatTracker pattern.

    Mirrors the player.s mt_getnewnote logic exactly:
    1. Read byte. If < FX($40): instrument change, read next byte.
    2. If NOEFFECTS==0 and byte < NOTE($60): it's FX.
       - cmp #FXONLY($50): if >= $50, it's FXONLY (rest after), else FX (note after)
       - and #$0F: command number. If != 0, read param byte.
       - FXONLY: done (rest). FX: read next byte as note.
    3. If byte >= FIRSTPACKEDREST($C0): packed rest.
    4. If byte >= NOTE($60) and < FIRSTPACKEDREST: note/rest/keyoff/keyon.
    5. After note/rest, advance pointer. If next byte == $00, end of pattern.

    After instrument change, the NEXT byte goes through the same FX/note check
    but skipping the instrument test (it checks cmp #NOTE directly, and if < NOTE
    falls to FX processing).

    Returns list of row dicts.
    """
    off = patt_addr - load_addr
    if off < 0 or off >= len(binary):
        return []

    # Find pattern's own $00 terminator
    patt_size = 0
    while off + patt_size < len(binary) and binary[off + patt_size] != 0x00:
        patt_size += 1
    patt_size += 1  # include the $00

    rows = []
    y = 0  # mirrors the Y register in player
    # allow_overshoot: when an FX command at the end of a pattern needs to
    # read its note from beyond the $00 terminator (cross-pattern sharing),
    # we allow reading a few bytes past the boundary.
    allow_overshoot = 0

    def readbyte():
        nonlocal y
        pos = off + y
        if pos >= len(binary):
            return None
        if y >= patt_size + allow_overshoot:
            return None
        return binary[pos]

    while True:
        if y >= max_bytes:
            break

        force_end = False
        b = readbyte()
        if b is None:
            break

        new_instr = None
        new_cmd = None
        new_param = None

        # Check instrument change (< FX = $40)
        # Note: $00 here is instrument 0 (empty), NOT endpatt.
        # ENDPATT is only checked AFTER processing a note/rest.
        if b < FX:
            new_instr = b
            y += 1
            b = readbyte()
            if b is None:
                break
            # After instrument, player checks: cmp #NOTE, if < NOTE -> fx

        # Check for FX/FXONLY (byte < NOTE = $60)
        # This handles both: first byte in $40-$5F range, and post-instrument byte < $60
        if b is not None and b < FIRSTNOTE:
            if b >= FIRSTPACKEDREST:
                pass  # shouldn't happen (FIRSTPACKEDREST > FIRSTNOTE)
            else:
                is_fxonly = (b >= FXONLY)  # >= $50
                cmd = b & 0x0F
                new_cmd = cmd
                y += 1
                if cmd != 0:
                    param_b = readbyte()
                    if param_b is not None:
                        new_param = param_b
                        y += 1
                if is_fxonly:
                    # FXONLY: this row is a rest, done
                    rows.append({
                        'note': 'REST',
                        'instrument': new_instr,
                        'command': new_cmd,
                        'param': new_param,
                    })
                    # Check next byte for ENDPATT
                    nb = readbyte()
                    if nb is not None and nb == ENDPATT:
                        break
                    continue
                # FX (not FXONLY): read note
                b = readbyte()
                if b is None:
                    # Note is past pattern boundary (cross-pattern sharing).
                    # Record as FXONLY rest — the note lives in adjacent memory
                    # and will be provided by the memory layout, not the USF.
                    rows.append({
                        'note': 'REST',
                        'instrument': new_instr,
                        'command': new_cmd,
                        'param': new_param,
                    })
                    break

        # Now b should be note ($60-$BC), REST($BD), KEYOFF($BE), KEYON($BF),
        # or packed rest ($C0-$FF)
        if b is None:
            break

        if b >= FIRSTPACKEDREST:
            # Packed rest: player uses a counter that counts up from the byte value
            # When counter wraps to 0 (256-b iterations), the rest is done
            count = 256 - b
            for _ in range(count):
                rows.append({
                    'note': 'REST',
                    'instrument': new_instr if _ == 0 else None,
                    'command': new_cmd if _ == 0 else None,
                    'param': new_param if _ == 0 else None,
                })
            y += 1
            # After packed rest, check next byte for ENDPATT
            nb = readbyte()
            if nb is not None and nb == ENDPATT:
                break
        elif FIRSTNOTE <= b <= LASTNOTE:
            note_num = b - FIRSTNOTE
            rows.append({
                'note': note_name(note_num),
                'note_num': note_num,
                'instrument': new_instr,
                'command': new_cmd,
                'param': new_param,
            })
            y += 1
            if force_end:
                break
            nb = readbyte()
            if nb is not None and nb == ENDPATT:
                break
        elif b == REST:
            rows.append({
                'note': 'REST',
                'instrument': new_instr,
                'command': new_cmd,
                'param': new_param,
            })
            y += 1
            nb = readbyte()
            if nb is not None and nb == ENDPATT:
                break
        elif b == KEYOFF:
            rows.append({
                'note': 'KEYOFF',
                'instrument': new_instr,
                'command': new_cmd,
                'param': new_param,
            })
            y += 1
            nb = readbyte()
            if nb is not None and nb == ENDPATT:
                break
        elif b == KEYON:
            rows.append({
                'note': 'KEYON',
                'instrument': new_instr,
                'command': new_cmd,
                'param': new_param,
            })
            y += 1
            nb = readbyte()
            if nb is not None and nb == ENDPATT:
                break
        else:
            # Unknown — skip
            y += 1

    return rows


def extract_patterns(binary, load_addr, patt_lo_addr, patt_hi_addr, num_patterns):
    """Extract and unpack all patterns."""
    off_lo = patt_lo_addr - load_addr
    off_hi = patt_hi_addr - load_addr

    # Get all pattern addresses and compute sizes from gaps
    patt_addrs = []
    for p in range(num_patterns):
        p_addr = binary[off_lo + p] | (binary[off_hi + p] << 8)
        patt_addrs.append(p_addr)

    patterns = []
    for p in range(num_patterns):
        p_addr = patt_addrs[p]
        # Compute max bytes for this pattern from gap to next pattern
        if p + 1 < num_patterns:
            max_bytes = patt_addrs[p + 1] - p_addr
        else:
            max_bytes = 256
        rows = unpack_pattern(binary, load_addr, p_addr, max_bytes)
        patterns.append(rows)

    return patterns


def parse_goattracker_sid(data):
    """Parse a GoatTracker V2 SID file.

    Returns dict with header, instruments, tables, orderlists, patterns.
    """
    header, binary, load_addr = parse_psid_header(data)

    # Find frequency table (our anchor point)
    ft = find_freq_table(binary, load_addr)
    if ft is None:
        raise ValueError('Could not find GoatTracker frequency table')

    freq_off, first_note, num_notes, lo_first = ft
    if lo_first:
        freq_lo_off = freq_off
        freq_hi_off = freq_off + num_notes
    else:
        freq_hi_off = freq_off
        freq_lo_off = freq_off + num_notes

    # Everything before freq table is player code
    player_end_off = freq_off
    data_start_off = freq_off + num_notes * 2  # after both lo and hi tables

    # Collect absolute addresses referenced by player code
    data_addrs = collect_abs_addresses(binary, load_addr, 0, player_end_off)

    # Find song and pattern tables
    songs = header['songs']
    song_lo, song_hi = find_song_and_pattern_tables(binary, load_addr, data_addrs, songs)

    if song_lo is None:
        raise ValueError('Could not find song table')

    patt_lo, patt_hi, num_patterns = find_pattern_table(
        binary, load_addr, data_addrs, song_hi, songs)

    if patt_lo is None:
        raise ValueError('Could not find pattern table')

    # Extract orderlists
    orderlists = extract_orderlists(binary, load_addr, song_lo, song_hi, songs)

    # Extract patterns
    patterns = extract_patterns(binary, load_addr, patt_lo, patt_hi, num_patterns)

    # Extract instrument data (between freq table end and song table)
    # Instruments are stored column-major: all AD[N], all SR[N], all waveptr[N], ...
    instr_start_off = data_start_off
    instr_end_off = song_lo - load_addr

    # Collect addresses between freq end and song table that are referenced by player
    instr_addrs = [a for a in data_addrs
                   if load_addr + instr_start_off <= a < song_lo]

    # Determine number of instruments from spacing between first two instrument column addresses
    num_instr = 0
    instr_columns = {}
    if len(instr_addrs) >= 2:
        num_instr = instr_addrs[1] - instr_addrs[0]
        # Read each column
        col_names = ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr',
                     'vib_param', 'vib_delay', 'gate_timer', 'first_wave']
        for ci, addr in enumerate(instr_addrs):
            off = addr - load_addr
            if ci < len(col_names) and off + num_instr <= len(binary):
                instr_columns[col_names[ci]] = list(binary[off:off + num_instr])

    # Build per-instrument records
    instruments = []
    for i in range(num_instr):
        instr = {'index': i}
        for col_name, col_data in instr_columns.items():
            if i < len(col_data):
                instr[col_name] = col_data[i]
        instruments.append(instr)

    # Extract tables (wave, pulse, filter, speed)
    # These are between instrument columns and orderlists
    # For now, collect raw table data
    tables = {}
    # Find table addresses: they're referenced by player code and come after instruments
    table_addrs = [a for a in data_addrs
                   if song_lo <= a or (instr_addrs and a > instr_addrs[-1] + num_instr)]
    # Filter to addresses between last instrument column and song table orderlists
    # This is complex — for now, skip detailed table extraction

    result = {
        'header': header,
        'freq_table': {
            'first_note': first_note,
            'num_notes': num_notes,
        },
        'num_instruments': num_instr,
        'instruments': instruments,
        'num_patterns': num_patterns,
        'orderlists': orderlists,
        'patterns': patterns,
        'debug': {
            'player_size': player_end_off,
            'freq_table_offset': freq_off,
            'song_table': f'${song_lo:04X}/${song_hi:04X}',
            'pattern_table': f'${patt_lo:04X}/${patt_hi:04X}',
            'instr_addrs': [f'${a:04X}' for a in instr_addrs],
        },
    }

    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Parse GoatTracker V2 SID files')
    parser.add_argument('input', help='SID file path')
    parser.add_argument('-o', '--output', help='Output JSON file (default: stdout)')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    with open(args.input, 'rb') as f:
        data = f.read()

    try:
        result = parse_goattracker_sid(data)
    except ValueError as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        h = result['header']
        print(f"Title: {h['title']}", file=sys.stderr)
        print(f"Author: {h['author']}", file=sys.stderr)
        print(f"Songs: {h['songs']}", file=sys.stderr)
        print(f"Player size: {result['debug']['player_size']} bytes", file=sys.stderr)
        print(f"Instruments: {result['num_instruments']}", file=sys.stderr)
        print(f"Patterns: {result['num_patterns']}", file=sys.stderr)
        for si, song in enumerate(result['orderlists']):
            for ci, ol in enumerate(song):
                pats = [e['pattern'] for e in ol['entries'] if e['type'] == 'pattern']
                print(f"  Song {si} Ch {ci}: {len(ol['entries'])} entries, "
                      f"patterns: {pats}", file=sys.stderr)

    output = json.dumps(result, indent=2)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main()
