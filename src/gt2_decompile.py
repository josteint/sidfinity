"""
gt2_decompile.py — Decompile GT2 packed SID binary to .sng-equivalent data.

Walks the data section in layout order (per docs/gt2_data_layout.md),
extracting each section at its correct size. Reverses all greloc.c
transformations to recover .sng-equivalent data.

Wave table size is determined by frequency tracing: run the SID,
capture the first note's frequency, trace it backwards through
the freq table and wave table to find mt_notetbl's exact position.
"""

import sys
import os
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_psid_header, find_freq_table
from gt2_packer import FREQ_HI_PAL, FREQ_LO_PAL

SIDDUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'siddump')


def _find_wave_size_by_freq_trace(sid_path, binary, la, code_end, table_start_off,
                                    first_note, num_notes, columns, songs=1):
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
    song_entries = songs * 3
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
        song_hi_off = freq_end + song_entries
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
        patt_tbl_off = freq_end + song_entries * 2  # after song table
        num_patt_est = (columns['ad'][0] if 'ad' in columns else 0)  # rough
        # Actually: pattern table is at freq_end + song_entries*2, we know its structure
        patt_lo = binary[patt_tbl_off + first_patt_id]
        col_start_off = (la + code_end + num_notes * 2 + 6)  # approx
        # We need the column start to know pattern table size.
        # Use the ad_operand from the columns dict position:
        # columns start at table_start_off - num_cols * ni
        # Actually we passed table_start_off as 'pos' which is after columns.
        # Pattern hi bytes start at patt_tbl_off + num_patt
        # We don't know num_patt here. Let's compute from known positions.
        ad_col_off = table_start_off - len(columns) * len(columns.get('ad', []))
        num_patt_space = ad_col_off - (freq_end + song_entries * 2)
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
    song_hi_off = freq_end + song_entries
    ol_addrs = [binary[song_lo_off + v] | (binary[song_hi_off + v] << 8) for v in range(song_entries)]
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

    # Read songs count from PSID header
    songs = header['songs']

    # Use gt2_parse_direct for reliable column detection
    r = parse_gt2_direct(sid_path)
    if r is None:
        return None

    ni = r['ni']
    num_cols = min(r['num_columns'], 9)  # GT2 max is 9 columns
    col_start = r['col_operands']['ad'] + 1  # first byte of AD column
    col_start_off = col_start - la

    # For ni=1, the stride-based column detection can overcount (wave table
    # accesses look like columns). Validate by checking that the table region
    # between columns end and orderlists is large enough for a wave table.
    if ni == 1:
        freq_end_v = ft[0] + ft[2] * 2
        song_entries_v = songs * 3
        if freq_end_v + song_entries_v * 2 < len(binary):
            sl = [binary[freq_end_v + i] for i in range(song_entries_v)]
            sh = [binary[freq_end_v + song_entries_v + i] for i in range(song_entries_v)]
            first_ol_v = min(sl[i] | (sh[i] << 8) for i in range(song_entries_v))
            while num_cols > 3:
                instr_end_v = (col_start - la) + num_cols * ni
                table_region_v = first_ol_v - la - instr_end_v
                if table_region_v >= 2 and table_region_v % 2 == 0:
                    break
                num_cols -= 1

    # === Step 3: Walk the data section sequentially ===
    pos = code_end  # start of data
    result = {
        'la': la, 'code_end': code_end, 'ni': ni, 'num_cols': num_cols,
        'first_note': first_note, 'num_notes': num_notes, 'songs': songs,
    }

    # Freq tables
    result['freq_lo'] = bytes(binary[pos:pos + num_notes])
    pos += num_notes
    result['freq_hi'] = bytes(binary[pos:pos + num_notes])
    pos += num_notes

    # Song table — read to find orderlist addresses
    # songs already set from PSID header above
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

    # Use gt2_parse_direct's identified columns if available and reliable (ni > 1)
    if ni > 1 and r['col_data']:
        col_names_for_file = list(r['col_data'].keys())[:num_cols]
    else:
        # For ni=1 or unreliable detection: use standard configs
        col_names_for_file = col_name_configs.get(num_cols)
        if col_names_for_file is None:
            # Fallback: fill from full order
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

    # === Wave table size via frequency trace ===
    # Run the original SID and capture the first note's freq_hi.
    # Trace backwards: fhi → absolute note → wave_right byte value →
    # search binary to find mt_notetbl position.

    # Prefer parse_direct's operand-based wave_size (exact from code analysis).
    wave_size = r['wave_size']

    if wave_size <= 0:
        wave_size = _find_wave_size_by_freq_trace(
            sid_path, binary, la, code_end, pos, first_note, num_notes, columns, songs)

    # Fallback: if both fail, estimate wave_size from table region.
    if wave_size <= 0:
        other_bytes = 0
        # Speed table: $00 prefix + data + $00 prefix + data (minimum 4 bytes if present)
        if has_speed and len(table_region) > 4:
            # Check if there's a $00 byte that could be a speed prefix
            # Speed is at the END of the table region
            # Try: assume speed has at least 1 entry (4 bytes: $00+L+$00+R)
            other_bytes += 4
        # Pulse and filter: each has left+right (minimum 2 bytes if present)
        if has_pulse:
            other_bytes += 2  # minimum pulse table
        if has_filter:
            other_bytes += 2  # minimum filter table
        wave_bytes = len(table_region) - other_bytes
        wave_size = max(1, wave_bytes // 2)

    result['wave_size'] = wave_size
    tp = 0
    result['wave_left'] = bytes(table_region[tp:tp + wave_size])
    tp += wave_size
    result['wave_right'] = bytes(table_region[tp:tp + wave_size])
    tp += wave_size

    # Extract pulse and filter tables using sizes from parse_direct
    result['pulse_left'] = b''
    result['pulse_right'] = b''
    result['filter_left'] = b''
    result['filter_right'] = b''
    result['speed_left'] = b''
    result['speed_right'] = b''

    pulse_size = r['pulse_size'] if has_pulse else 0
    filter_size = r['filter_size'] if has_filter else 0

    if has_pulse and pulse_size > 0:
        result['pulse_left'] = bytes(table_region[tp:tp + pulse_size])
        tp += pulse_size
        result['pulse_right'] = bytes(table_region[tp:tp + pulse_size])
        tp += pulse_size

    if has_filter and filter_size > 0:
        result['filter_left'] = bytes(table_region[tp:tp + filter_size])
        tp += filter_size
        result['filter_right'] = bytes(table_region[tp:tp + filter_size])
        tp += filter_size

    # Speed table: remaining bytes after wave+pulse+filter in the table region.
    # Format: $00 prefix + left_data + $00 prefix + right_data
    # speed_size = (remaining_bytes - 2) / 2
    remaining = len(table_region) - tp
    if remaining >= 4:
        if table_region[tp] == 0x00:  # validate first $00 prefix
            st_size = (remaining - 2) // 2
            if st_size > 0:
                second_prefix_pos = tp + 1 + st_size
                if (second_prefix_pos < len(table_region)
                        and table_region[second_prefix_pos] == 0x00):
                    result['speed_left'] = bytes(
                        table_region[tp + 1:tp + 1 + st_size])
                    result['speed_right'] = bytes(
                        table_region[second_prefix_pos + 1:
                                     second_prefix_pos + 1 + st_size])

    result['table_remaining'] = b''  # everything parsed

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

    songs = r['songs']
    print(f"songs={songs}, ni={r['ni']}, cols={r['num_cols']}, patterns={r['num_patt']}")
    print(f"first_note={r['first_note']}, num_notes={r['num_notes']}")
    print(f"wave_size={r['wave_size']}")
    print(f"pulse: {len(r['pulse_left'])}B, filter: {len(r['filter_left'])}B, speed: {len(r['speed_left'])}B")
    print(f"table_remaining={len(r['table_remaining'])}B")

    print(f"\nColumns:")
    for name, vals in r['columns'].items():
        print(f"  {name}: {[f'{v:02x}' for v in vals]}")

    print(f"\nWave left:  {r['wave_left'].hex()}")
    print(f"Wave right: {r['wave_right'].hex()}")

    if r['speed_left']:
        print(f"\nSpeed left:  {r['speed_left'].hex()}")
        print(f"Speed right: {r['speed_right'].hex()}")

    print(f"\nOrderlists ({songs} song(s), {songs * 3} channels):")
    for si in range(songs):
        print(f"  Song {si}:")
        for ch in range(3):
            vi = si * 3 + ch
            if vi < len(r['orderlists']):
                ol = r['orderlists'][vi]
                print(f"    V{ch+1}: {ol.hex()}")
