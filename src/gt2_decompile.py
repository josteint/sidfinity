"""
gt2_decompile.py — Decompile GT2 packed SID binary to .sng-equivalent data.

Walks the data section in layout order (per docs/gt2_data_layout.md),
extracting each section at its correct size. Reverses all greloc.c
transformations to recover .sng-equivalent data.

Table sizes are determined from parse_direct's operand analysis of
the player code (exact). Frequency tracing is used as a fallback
only when operand analysis fails.
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_psid_header, find_freq_table
from gt2_packer import FREQ_HI_PAL, FREQ_LO_PAL

SIDDUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'siddump')


def _find_wave_size_by_freq_trace(sid_path, binary, la, code_end, table_start_off,
                                    first_note, num_notes, columns):
    """Determine wave table size by tracing the first note's frequency output.

    Strategy:
    1. Run siddump to get the first note's freq_hi for each voice
    2. Look up that fhi in the PAL freq table → absolute note number
    3. Get the stored note from the pattern data (note_byte - $60)
    4. Determine what wave_right[0] must be to produce that freq output
    5. Search the table region for that byte → find mt_notetbl position
    6. wave_size = mt_notetbl - mt_wavetbl
    """
    # Step 1: Get first note's freq_hi from siddump
    try:
        r = subprocess.run([SIDDUMP, sid_path, '--duration', '3'],
                           capture_output=True, text=True, timeout=30)
        if r.returncode not in (0, 2):
            return 0
    except Exception:
        return 0

    lines = r.stdout.strip().split('\n')[2:]  # skip header

    # Find first frame where any voice has fhi != 0 and wav not in (0, 9)
    # (wav=9 is test bit during hard restart, not a real note)
    first_notes = {}  # voice → (fhi, frame_idx)
    for fi, line in enumerate(lines):
        vals = [int(v, 16) for v in line.split(',')]
        for voice in range(3):
            if voice in first_notes:
                continue
            fhi = vals[voice * 7 + 1]
            wav = vals[voice * 7 + 4]
            if fhi > 0 and wav not in (0x00, 0x09):
                first_notes[voice] = (fhi, fi)
        if len(first_notes) == 3:
            break

    if not first_notes:
        return 0

    # Step 2: Find the absolute note for each voice's first fhi
    # The player accesses freq_hi at mt_freqtblhi - FIRSTNOTE + Y
    # where Y = absolute_note. We need: which Y gives this fhi value?
    freq_hi_start = code_end + num_notes  # offset in binary
    for voice, (fhi, frame_idx) in first_notes.items():
        # Search freq_hi table for this value
        for idx in range(num_notes):
            if binary[freq_hi_start + idx] == fhi:
                absolute_note = first_note + idx
                break
        else:
            continue  # fhi not found in freq table

        # Step 3: Get the stored note from the pattern
        # Voice N plays pattern from orderlist entry 0.
        # We need to find the first NOTE byte in that pattern.
        # The pattern data is in the binary at patt_addrs[orderlist[voice][0]].
        # For now, extract from the orderlists we already parsed.

        # Read orderlist for this voice to get first pattern ID
        freq_end = code_end + num_notes * 2
        song_lo_off = freq_end
        song_hi_off = freq_end + 3
        ol_addr = binary[song_lo_off + voice] | (binary[song_hi_off + voice] << 8)
        ol_off = ol_addr - la

        # Skip transpose markers to find first pattern ID
        ol_pos = 0
        while ol_off + ol_pos < len(binary):
            byte = binary[ol_off + ol_pos]
            if byte >= 0xE0:  # transpose marker
                ol_pos += 1
                continue
            break  # this is the pattern ID
        first_patt_id = binary[ol_off + ol_pos]

        # Find pattern address from pattern table
        patt_tbl_off = freq_end + 6  # after song table
        num_patt_est = (columns['ad'][0] if 'ad' in columns else 0)  # rough
        # Actually: pattern table is at freq_end + 6, we know its structure
        patt_lo = binary[patt_tbl_off + first_patt_id]
        col_start_off = (la + code_end + num_notes * 2 + 6)  # approx
        # We need the column start to know pattern table size.
        # Use the ad_operand from the columns dict position:
        # columns start at table_start_off - num_cols * ni
        # Actually we passed table_start_off as 'pos' which is after columns.
        # Pattern hi bytes start at patt_tbl_off + num_patt
        # We don't know num_patt here. Let's compute from known positions.
        ad_col_off = table_start_off - len(columns) * len(columns.get('ad', []))
        num_patt_space = ad_col_off - (freq_end + 6)
        num_patt = num_patt_space // 2

        patt_addr = (binary[patt_tbl_off + first_patt_id] |
                     (binary[patt_tbl_off + num_patt + first_patt_id] << 8))
        patt_off = patt_addr - la

        # Find first NOTE byte in this pattern (bytes $60-$BC are notes)
        stored_note = None
        p = patt_off
        while p < len(binary):
            byte = binary[p]
            if byte == 0x00:
                break  # ENDPATT
            if 0x60 <= byte <= 0xBC:
                stored_note = byte - 0x60
                break
            elif byte < 0x40:
                p += 1  # instrument byte, skip
                continue
            elif byte < 0x50:
                # FX byte: $40+cmd. If cmd != 0, next byte is param
                cmd = byte - 0x40
                p += 1
                if cmd != 0:
                    p += 1  # skip param
                continue
            elif byte < 0x60:
                # FXONLY: $50+cmd
                cmd = byte - 0x50
                p += 1
                if cmd != 0:
                    p += 1
                continue
            elif byte == 0xBD:
                p += 1  # REST
                continue
            elif byte >= 0xC0:
                p += 1  # packed rest
                continue
            else:
                p += 1
                continue
            # If we get here, we found a note
            break

        if stored_note is None:
            continue  # no note in first pattern for this voice

        # Step 4: What wave_right value produces absolute_note from stored_note?
        # The first instrument for this voice: read from pattern
        # Get wave_ptr for this instrument
        wp_col = columns.get('wave_ptr', [])
        # First instrument in the pattern: scan for instrument byte
        inst_idx = 0  # default
        p2 = patt_off
        while p2 < patt_off + 20:
            byte = binary[p2]
            if byte < 0x40 and byte > 0:
                inst_idx = byte - 1  # 1-based in pattern
                break
            p2 += 1

        wave_ptr = wp_col[inst_idx] if inst_idx < len(wp_col) else 1

        # The wave table right column at index (wave_ptr - 1) must produce
        # Y = absolute_note from the player code:
        #   BPL → absolute: right_value = absolute_note (bit7 clear)
        #   BMI → relative: right_value + stored_note [+ carry] AND $7F = absolute_note

        # Case 1: absolute (most common for first entry)
        expected_right_absolute = absolute_note  # must have bit7 clear (< $80)

        # Case 2: relative
        # Relative is trickier due to carry flag. Try both.
        diff = absolute_note - stored_note
        expected_right_relative = (diff + 0x80) & 0xFF  # bit7 set = relative in packed format

        # Step 5: Search for the expected byte in the table region
        mt_wavetbl_off = table_start_off  # wave_left starts here
        search_offset = wave_ptr - 1  # the entry index to check

        # Try absolute first (bit7 clear, simpler)
        found_wave_size = 0
        if expected_right_absolute < 0x80:
            # mt_notetbl[search_offset] should be expected_right_absolute
            # mt_notetbl = mt_wavetbl + wave_size
            # So binary[mt_wavetbl_off + wave_size + search_offset] = expected_right_absolute
            for ws in range(1, len(binary) - mt_wavetbl_off - search_offset):
                check_off = mt_wavetbl_off + ws + search_offset
                if check_off >= len(binary):
                    break
                if binary[check_off] == expected_right_absolute:
                    # Validate: wave_left[search_offset] should be a valid waveform
                    wl_val = binary[mt_wavetbl_off + search_offset]
                    if 0x10 <= wl_val <= 0xFF and wl_val != 0xBD:
                        found_wave_size = ws
                        break

        # If absolute didn't work, try relative
        if found_wave_size == 0 and (expected_right_relative & 0x80):
            for ws in range(1, len(binary) - mt_wavetbl_off - search_offset):
                check_off = mt_wavetbl_off + ws + search_offset
                if check_off >= len(binary):
                    break
                if binary[check_off] == expected_right_relative:
                    wl_val = binary[mt_wavetbl_off + search_offset]
                    if 0x10 <= wl_val <= 0xFF and wl_val != 0xBD:
                        found_wave_size = ws
                        break

        if found_wave_size > 0:
            return found_wave_size

    # Fallback: freq trace didn't find a match (wave table preserves note,
    # or no notes play in the first 3 seconds). Walk the wave table from
    # each instrument's wave_ptr to find the highest accessed entry.
    # Bound by: wave table can't exceed half the table region.
    wp_col = columns.get('wave_ptr', [])
    if not wp_col:
        return 0

    # Calculate total table region size and max wave size.
    # Other tables (pulse, filter, speed) share the region with wave.
    freq_end = code_end + num_notes * 2
    song_lo_off = freq_end
    song_hi_off = freq_end + 3
    ol_addrs = [binary[song_lo_off + v] | (binary[song_hi_off + v] << 8) for v in range(3)]
    first_ol_off = min(a - la for a in ol_addrs)
    table_region_size = first_ol_off - table_start_off

    # Estimate bytes used by other tables to bound the wave walk
    has_pulse_col = 'pulse_ptr' in columns
    has_filter_col = 'filter_ptr' in columns
    has_vib_col = 'vib_param' in columns
    other_bytes = 0
    if has_vib_col and table_region_size > 4:
        other_bytes += 4  # speed table minimum ($00 + 1 entry + $00 + 1 entry)
    if has_pulse_col:
        other_bytes += 2  # pulse minimum
    if has_filter_col:
        other_bytes += 2  # filter minimum
    max_possible_wave = (table_region_size - other_bytes) // 2

    max_entry = 0
    for wp in wp_col:
        if wp <= 0:
            continue
        idx = wp - 1  # 0-based
        visited = set()
        while 0 <= idx < max_possible_wave and idx not in visited:
            visited.add(idx)
            left = binary[table_start_off + idx] if table_start_off + idx < len(binary) else 0
            if left == 0xFF:
                max_entry = max(max_entry, idx + 1)
                break
            max_entry = max(max_entry, idx + 1)
            idx += 1

    return max_entry if max_entry > 0 else min(max(wp_col), max_possible_wave)


def decompile_gt2(sid_path):
    """Decompile a GT2 packed SID to .sng-equivalent data.

    Uses gt2_parse_direct for reliable column detection, then walks
    the data section sequentially. Wave table size is determined by
    frequency tracing.

    Returns a dict with all extracted sections.
    """
    from gt2_parse_direct import parse_gt2_direct

    with open(sid_path, 'rb') as f:
        data = f.read()

    header, binary, la = parse_psid_header(data)
    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    code_end = ft[0]
    first_note = ft[1]
    num_notes = ft[2]

    # Use gt2_parse_direct for reliable column detection
    r = parse_gt2_direct(sid_path)
    if r is None:
        return None

    ni = r['ni']
    num_cols = min(r['num_columns'], 9)  # GT2 max is 9 columns
    col_start = r['col_operands']['ad'] + 1  # first byte of AD column
    col_start_off = col_start - la

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

    # Instrument columns — determine names from column count.
    # GT2 column order: ad, sr, wave_ptr, [pulse_ptr], [filter_ptr],
    #   [vib_param, vib_delay], [gate_timer, first_wave]
    # Brackets = conditional on flags. Columns come in groups:
    #   pulse_ptr alone, filter_ptr alone, vib_param+vib_delay together,
    #   gate_timer+first_wave together.
    # Standard configurations by column count:
    col_name_configs = {
        3: ['ad', 'sr', 'wave_ptr'],
        4: ['ad', 'sr', 'wave_ptr', 'pulse_ptr'],
        5: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr'],
        6: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr', 'vib_param'],  # rare
        7: ['ad', 'sr', 'wave_ptr', 'vib_param', 'vib_delay', 'gate_timer', 'first_wave'],
        8: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'vib_param', 'vib_delay', 'gate_timer', 'first_wave'],
        9: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr', 'vib_param', 'vib_delay', 'gate_timer', 'first_wave'],
    }

    # Use gt2_parse_direct's identified columns (now reliable for all ni values,
    # including ni=1 where flag detection determines the correct layout).
    if r['col_data']:
        col_names_for_file = list(r['col_data'].keys())[:num_cols]
    else:
        # Fallback: use standard configs by column count
        col_names_for_file = col_name_configs.get(num_cols)
        if col_names_for_file is None:
            full = ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr',
                    'vib_param', 'vib_delay', 'gate_timer', 'first_wave']
            col_names_for_file = full[:num_cols]

    columns = {}
    for c in range(num_cols):
        name = col_names_for_file[c] if c < len(col_names_for_file) else f'col{c}'
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

    has_pulse = 'pulse_ptr' in columns
    has_filter = 'filter_ptr' in columns
    has_vib = 'vib_param' in columns
    has_speed = has_vib

    # Get table sizes from parse_direct's operand analysis.
    # When parse_direct reports 0 for a table that should exist (column present),
    # calculate its size from the remaining table region after known tables.
    wave_size = r['wave_size']
    pulse_size = r['pulse_size'] if has_pulse else 0
    filter_size = r['filter_size'] if has_filter else 0
    speed_size = r['speed_size'] if has_speed else 0

    # Compute expected total and check for missing table sizes
    speed_overhead = (2 + speed_size * 2) if speed_size > 0 else 0
    known_bytes = wave_size * 2 + pulse_size * 2 + filter_size * 2 + speed_overhead
    remaining_after_known = len(table_region) - known_bytes

    if remaining_after_known > 0:
        # Identify which tables have 0 size but should exist
        missing = []
        if has_pulse and pulse_size == 0:
            missing.append('pulse')
        if has_filter and filter_size == 0:
            missing.append('filter')
        if has_speed and speed_size == 0:
            missing.append('speed')

        if missing:
            # Speed table has 2 extra $00 prefix bytes
            speed_prefix = 2 if 'speed' in missing else 0
            data_for_missing = remaining_after_known - speed_prefix
            # Each missing table has left + right of equal size
            num_missing = len(missing)
            per_table = data_for_missing // (num_missing * 2) if num_missing > 0 else 0
            for name in missing:
                if name == 'pulse':
                    pulse_size = per_table
                elif name == 'filter':
                    filter_size = per_table
                elif name == 'speed':
                    speed_size = per_table

    # For small ni (1-3), parse_direct's operand pair detection is unreliable
    # (addresses too close together → false positives). Use freq trace to validate.
    if ni <= 3 and len(table_region) > 0:
        trace_wave_size = _find_wave_size_by_freq_trace(
            sid_path, binary, la, code_end, pos, first_note, num_notes, columns)
        if trace_wave_size > 0 and trace_wave_size != wave_size:
            wave_size = trace_wave_size
            # Recompute other table sizes with corrected wave_size
            remaining_after_wave = len(table_region) - wave_size * 2
            pulse_size = min(pulse_size, remaining_after_wave // 2)
            filter_size = 0
            speed_size = 0
            rest = remaining_after_wave - pulse_size * 2
            if rest >= 4 and has_speed:
                speed_size = (rest - 2) // 2
    # Fallback if still no wave_size
    if wave_size <= 0 and len(table_region) > 0:
        wave_size = _find_wave_size_by_freq_trace(
            sid_path, binary, la, code_end, pos, first_note, num_notes, columns)
    if wave_size <= 0:
        speed_overhead = (2 + speed_size * 2) if speed_size > 0 else 0
        other = pulse_size * 2 + filter_size * 2 + speed_overhead
        wave_size = max(1, (len(table_region) - other) // 2)

    result['wave_size'] = wave_size
    tp = 0
    result['wave_left'] = bytes(table_region[tp:tp + wave_size])
    tp += wave_size
    result['wave_right'] = bytes(table_region[tp:tp + wave_size])
    tp += wave_size

    # Pulse table
    if has_pulse and pulse_size > 0:
        result['pulse_left'] = bytes(table_region[tp:tp + pulse_size])
        tp += pulse_size
        result['pulse_right'] = bytes(table_region[tp:tp + pulse_size])
        tp += pulse_size
    else:
        result['pulse_left'] = b''
        result['pulse_right'] = b''

    # Filter table
    if has_filter and filter_size > 0:
        result['filter_left'] = bytes(table_region[tp:tp + filter_size])
        tp += filter_size
        result['filter_right'] = bytes(table_region[tp:tp + filter_size])
        tp += filter_size
    else:
        result['filter_left'] = b''
        result['filter_right'] = b''

    # Speed table (with $00 prefix per column when data exists)
    if has_speed and speed_size > 0:
        tp += 1  # skip $00 prefix before speed_left
        result['speed_left'] = bytes(table_region[tp:tp + speed_size])
        tp += speed_size
        tp += 1  # skip $00 prefix before speed_right
        result['speed_right'] = bytes(table_region[tp:tp + speed_size])
        tp += speed_size
    else:
        result['speed_left'] = b''
        result['speed_right'] = b''

    result['table_remaining'] = bytes(table_region[tp:])

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

    print(f"\nWave left  ({len(r['wave_left'])}): {r['wave_left'].hex()}")
    print(f"Wave right ({len(r['wave_right'])}): {r['wave_right'].hex()}")
    if r['pulse_left']:
        print(f"Pulse left ({len(r['pulse_left'])}): {r['pulse_left'].hex()}")
        print(f"Pulse right({len(r['pulse_right'])}): {r['pulse_right'].hex()}")
    if r['filter_left']:
        print(f"Filter left ({len(r['filter_left'])}): {r['filter_left'].hex()}")
        print(f"Filter right({len(r['filter_right'])}): {r['filter_right'].hex()}")
    if r['speed_left']:
        print(f"Speed left ({len(r['speed_left'])}): {r['speed_left'].hex()}")
        print(f"Speed right({len(r['speed_right'])}): {r['speed_right'].hex()}")

    print(f"\nOrderlists:")
    for vi, ol in enumerate(r['orderlists'][:3]):
        print(f"  V{vi+1}: {ol.hex()}")
