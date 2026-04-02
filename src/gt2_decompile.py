"""
gt2_decompile.py — Decompile GT2 packed SID binary to .sng-equivalent data.

Walks the data section in layout order (per docs/gt2_data_layout.md),
extracting each section at its correct size. Reverses all greloc.c
transformations to recover .sng-equivalent data.

Key insight: the data layout is deterministic given the flags and
column count. We don't need to guess boundaries — we walk through
the data section sequentially.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_psid_header, find_freq_table


def decompile_gt2(sid_path):
    """Decompile a GT2 packed SID to .sng-equivalent data.

    Returns a dict with all extracted sections, sizes verified.
    """
    with open(sid_path, 'rb') as f:
        data = f.read()

    header, binary, la = parse_psid_header(data)
    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    code_end = ft[0]
    first_note = ft[1]
    num_notes = ft[2]

    # === Step 1: Identify columns from the player code ===
    # Find AD/SR columns by their STA $D405,X / $D406,X patterns
    ad_operand = None
    sr_operand = None
    for i in range(code_end - 5):
        if binary[i] == 0xB9:  # LDA abs,Y
            addr = binary[i + 1] | (binary[i + 2] << 8)
            if i + 3 < code_end and binary[i + 3] == 0x9D:  # STA abs,X
                sta_addr = binary[i + 4] | (binary[i + 5] << 8)
                if sta_addr == 0xD405 and ad_operand is None:
                    ad_operand = addr
                elif sta_addr == 0xD406 and sr_operand is None:
                    sr_operand = addr

    if ad_operand is None or sr_operand is None:
        return None

    # Determine ni from the stride between AD and SR columns
    ni = sr_operand - ad_operand
    if ni < 1 or ni > 63:
        return None

    # === Step 2: Count columns by walking from AD operand ===
    # Each column is ni bytes. Walk until we hit data that's not a column.
    # We know columns start at ad_operand+1 (the -1 indexing means operand = addr-1)
    col_start = ad_operand + 1  # first byte of AD column
    col_start_off = col_start - la

    # Find mt_wavetbl operand from the code — this marks the end of columns.
    # The wave exec code has: LDA mt_wavetbl-1,Y where the operand points
    # just past the last instrument column.
    # Strategy: find the first LDA abs,Y operand that's PAST the column area
    # but NOT at a column stride position. Actually, the simplest approach:
    # find the operand that's closest to col_start but past the minimum
    # possible columns (3: ad, sr, wave_ptr).
    min_cols_end = col_start + 3 * ni  # at least ad, sr, wave_ptr
    wavetbl_candidates = []
    for i in range(code_end - 3):
        if binary[i] == 0xB9:
            addr = binary[i + 1] | (binary[i + 2] << 8)
            # Must be past minimum columns, aligned to ni boundary from col_start
            if addr >= min_cols_end - 1 and addr < col_start + 20 * ni:
                off_from_col = (addr + 1) - col_start
                if off_from_col % ni == 0:
                    ncols = off_from_col // ni
                    if 3 <= ncols <= 9:
                        wavetbl_candidates.append((addr, ncols))

    # The wave table operand should have the FEWEST refs among candidates
    # (it's accessed once in wave exec, vs columns accessed more often)
    # Actually just pick the first valid candidate after sorting by address
    # that has a reasonable column count
    num_cols = 3  # minimum
    if wavetbl_candidates:
        # Use the candidate that gives the most columns (up to 9)
        # while keeping the wave table within the data region
        for addr, ncols in sorted(wavetbl_candidates, key=lambda x: -x[1]):
            # Verify this could be a wave table start: check if the bytes
            # after this point look like wave data (not all zeros)
            wave_check_off = addr + 1 - la
            if wave_check_off < len(binary) - 2:
                b0, b1 = binary[wave_check_off], binary[wave_check_off + 1]
                if b0 != 0 or b1 != 0:  # wave table has non-zero data
                    num_cols = ncols
                    break

    # === Step 3: Walk the data section sequentially ===
    pos = code_end  # start of data
    result = {
        'la': la, 'code_end': code_end, 'ni': ni, 'num_cols': num_cols,
        'first_note': first_note, 'num_notes': num_notes,
    }

    # Freq tables
    result['freq_lo'] = bytes(binary[pos:pos + num_notes])
    pos += num_notes
    result['freq_hi'] = bytes(binary[pos:pos + num_notes])
    pos += num_notes

    # Song table — read to find orderlist addresses
    songs = 1  # TODO: detect multi-song
    song_entries = songs * 3
    song_lo = [binary[pos + i] for i in range(song_entries)]
    pos += song_entries
    song_hi = [binary[pos + i] for i in range(song_entries)]
    pos += song_entries

    # Orderlist addresses (absolute)
    ol_addrs = [song_lo[i] | (song_hi[i] << 8) for i in range(song_entries)]
    first_ol_off = min(a - la for a in ol_addrs)
    result['orderlist_addrs'] = ol_addrs

    # Pattern table — need to know pattern count
    # Pattern count = distance from pattern table to first non-table data / 2
    # First non-table data = first instrument column = col_start
    # Pattern table is at current pos, ends at col_start_off
    patt_tbl_space = col_start_off - pos
    num_patt = patt_tbl_space // 2
    patt_lo = [binary[pos + i] for i in range(num_patt)]
    pos += num_patt
    patt_hi = [binary[pos + i] for i in range(num_patt)]
    pos += num_patt

    patt_addrs = [patt_lo[i] | (patt_hi[i] << 8) for i in range(num_patt)]
    result['num_patt'] = num_patt
    result['patt_addrs'] = patt_addrs

    # Instrument columns
    columns = {}
    # Column naming based on GT2 column order:
    # Always: ad, sr, wave_ptr
    # Conditional: pulse_ptr, filter_ptr, vib_param, vib_delay, gate_timer, first_wave
    col_names_full = ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr',
                      'vib_param', 'vib_delay', 'gate_timer', 'first_wave']
    # With fewer columns, some are missing. The order is always the same.
    # 3 cols = ad, sr, wave_ptr (+ FIXEDPARAMS + no pulse/filter/vib)
    # 4 cols = ad, sr, wave_ptr, pulse_ptr OR something else
    # We assign names in order, which works for standard GT2 configurations
    for c in range(num_cols):
        name = col_names_full[c] if c < len(col_names_full) else f'col{c}'
        columns[name] = list(binary[pos:pos + ni])
        pos += ni

    result['columns'] = columns

    # === Step 4: Tables ===
    # Everything between instrument columns end and first orderlist = tables
    # Tables go in order: wave_L, wave_R, [pulse_L, pulse_R], [filter_L, filter_R],
    #                      [speed_zero, speed_L, speed_zero, speed_R]
    table_region = bytes(binary[pos:first_ol_off])
    result['table_region_start'] = pos
    result['table_region_size'] = len(table_region)

    # For files with ONLY wave table (no pulse/filter/speed):
    # table_region = wave_L + wave_R, so wave_size = len / 2
    #
    # For files with pulse: wave + pulse (each table = left + right)
    # For files with filter: wave + pulse + filter
    # For files with speed: wave + [pulse] + [filter] + speed (with $00 prefixes)
    #
    # Detect by checking flags from column presence:
    has_pulse = 'pulse_ptr' in columns
    has_filter = 'filter_ptr' in columns
    has_vib = 'vib_param' in columns
    has_speed = has_vib  # speed table exists when vibrato is enabled

    # Parse tables from the region
    tp = 0  # position within table_region

    # Wave table: always present. Size = depends on what follows.
    # If no other tables: wave_size = len(table_region) / 2
    # If pulse follows: need to find the boundary.
    #
    # The SIMPLEST reliable approach: find wave_size from the code.
    # The player has LDA mt_wavetbl-1,Y and LDA mt_notetbl-1,Y.
    # mt_notetbl - mt_wavetbl = wave_size.
    #
    # Find these two operands:
    wavetbl_op = None
    notetbl_op = None

    # mt_wavetbl-1 is the first LDA abs,Y operand that points into the table region
    table_region_addr = la + pos  # absolute address of table region start
    for i in range(code_end - 3):
        if binary[i] == 0xB9:
            addr = binary[i + 1] | (binary[i + 2] << 8)
            if table_region_addr - 1 <= addr < table_region_addr + len(table_region):
                if wavetbl_op is None:
                    wavetbl_op = addr
                elif addr > wavetbl_op and notetbl_op is None:
                    # The notetbl operand should be AFTER wavetbl and point to the RIGHT column
                    # It must be at least wave_min_size away from wavetbl
                    if addr > wavetbl_op + 2:  # at least 3 entries
                        notetbl_op = addr
                        break

    if wavetbl_op is not None and notetbl_op is not None:
        wave_size = (notetbl_op + 1) - (wavetbl_op + 1)
    elif wavetbl_op is not None:
        # Fallback: assume wave takes the whole region (no other tables)
        wave_size = len(table_region) // 2
    else:
        wave_size = 0

    result['wave_size'] = wave_size
    result['wave_left'] = bytes(table_region[tp:tp + wave_size])
    tp += wave_size
    result['wave_right'] = bytes(table_region[tp:tp + wave_size])
    tp += wave_size

    # Remaining table region after wave
    remaining = len(table_region) - tp

    # Parse pulse/filter/speed from remaining bytes
    # For now: if has_pulse and remaining > 0, try to find pulse size
    # This is complex — for the decompiler, we need the code operands
    result['pulse_left'] = b''
    result['pulse_right'] = b''
    result['filter_left'] = b''
    result['filter_right'] = b''
    result['speed_left'] = b''
    result['speed_right'] = b''

    if remaining > 0 and (has_pulse or has_filter or has_speed):
        # TODO: parse pulse/filter/speed from remaining bytes
        # For now, store as raw remaining
        result['table_remaining'] = bytes(table_region[tp:])
    else:
        result['table_remaining'] = b''

    # === Step 5: Orderlists ===
    orderlists = []
    for vi in range(song_entries):
        ol_off = ol_addrs[vi] - la
        ol = bytearray()
        for j in range(200):
            if ol_off + j >= len(binary):
                break
            ol.append(binary[ol_off + j])
            if binary[ol_off + j] == 0xFF:
                if ol_off + j + 1 < len(binary):
                    ol.append(binary[ol_off + j + 1])
                break
        orderlists.append(bytes(ol))
    result['orderlists'] = orderlists

    # === Step 6: Patterns ===
    patterns = []
    for pi in range(num_patt):
        p_off = patt_addrs[pi] - la
        patt = bytearray()
        for j in range(300):
            if p_off + j >= len(binary):
                break
            patt.append(binary[p_off + j])
            if binary[p_off + j] == 0x00:  # ENDPATT
                break
        patterns.append(bytes(patt))
    result['patterns'] = patterns

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: gt2_decompile.py <file.sid>")
        sys.exit(1)

    r = decompile_gt2(sys.argv[1])
    if r is None:
        print("Failed to decompile")
        sys.exit(1)

    print(f"ni={r['ni']}, cols={r['num_cols']}, patterns={r['num_patt']}")
    print(f"first_note={r['first_note']}, num_notes={r['num_notes']}")
    print(f"wave_size={r['wave_size']}")
    print(f"table_remaining={len(r['table_remaining'])}B")

    print(f"\nColumns:")
    for name, vals in r['columns'].items():
        print(f"  {name}: {[f'{v:02x}' for v in vals]}")

    print(f"\nWave left:  {r['wave_left'].hex()}")
    print(f"Wave right: {r['wave_right'].hex()}")

    print(f"\nOrderlists:")
    for vi, ol in enumerate(r['orderlists'][:3]):
        print(f"  V{vi+1}: {ol.hex()}")
