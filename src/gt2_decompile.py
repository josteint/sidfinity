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


def _detect_speed_table_from_binary(binary, la, code_end, table_region_start, table_region_end):
    """Detect speed table presence and location from player binary code.

    Speed tables are referenced by LDA mt_speedlefttbl-1,Y and
    LDA mt_speedrighttbl-1,Y (opcode B9). The table addresses fall within
    the table region, after wave/pulse/filter tables.

    Returns (speed_left_addr, speed_right_addr, speed_size) or (None, None, 0)
    if no speed table detected.
    """
    # Collect all LDA abs,Y (B9) references into the table region
    table_start_addr = la + table_region_start
    table_end_addr = la + table_region_end
    lda_refs = {}
    for i in range(code_end - 3):
        if binary[i] == 0xB9:  # LDA abs,Y
            addr = binary[i + 1] | (binary[i + 2] << 8)
            if table_start_addr <= addr < table_end_addr:
                if addr not in lda_refs:
                    lda_refs[addr] = []
                lda_refs[addr].append(i)

    # Speed table operands: LDA mt_speedlefttbl-1,Y => stored to mt_temp2 ($FD)
    # and LDA mt_speedrighttbl-1,Y => stored to mt_temp1 ($FC)
    # Find pairs: B9 addr / 85 FC or B9 addr / 85 FD
    speed_l_operand = None  # mt_speedlefttbl - 1
    speed_r_operand = None  # mt_speedrighttbl - 1
    for addr, offsets in sorted(lda_refs.items()):
        for off in offsets:
            if off + 4 < code_end:
                if binary[off + 3] == 0x85 and binary[off + 4] == 0xFD:
                    # STA mt_temp2 => this is mt_speedlefttbl-1
                    if speed_l_operand is None or addr > speed_l_operand:
                        speed_l_operand = addr
                elif binary[off + 3] == 0x85 and binary[off + 4] == 0xFC:
                    # STA mt_temp1 => this could be mt_speedrighttbl-1
                    # But only if it's in the table region and after any
                    # known speed_l_operand position
                    if speed_r_operand is None or addr > speed_r_operand:
                        speed_r_operand = addr

    if speed_l_operand is not None and speed_r_operand is not None:
        # mt_speedlefttbl = speed_l_operand + 1
        # mt_speedrighttbl = speed_r_operand + 1
        # Speed size = gap between the two tables minus the $00 prefix byte
        sl_start = speed_l_operand + 1  # absolute address
        sr_start = speed_r_operand + 1
        speed_size = sr_start - sl_start - 1  # minus the $00 separator
        if speed_size > 0 and speed_size < 64:
            return (sl_start - la, sr_start - la, speed_size)

    # Fallback: toneporta-only songs don't store to $FD/$FC. Try finding
    # the speed table by looking for ANY pair of LDA abs,Y refs at the end
    # of the table region with a $00 separator between them.
    if speed_l_operand is None and speed_r_operand is None and lda_refs:
        # Get all refs in the latter half of the table region (speed is last)
        mid_addr = la + (table_region_start + table_region_end) // 2
        late_refs = sorted(a for a in lda_refs if a >= mid_addr)
        # Look for two refs with a $00 byte between them
        for i in range(len(late_refs) - 1):
            a1 = late_refs[i]
            a2 = late_refs[i + 1]
            gap = a2 - a1
            # Check for $00 separator pattern: speed_left data + $00 + speed_right data
            # a1 = mt_speedlefttbl - 1, a2 = mt_speedrighttbl - 1
            sl_start = a1 + 1  # mt_speedlefttbl
            sr_start = a2 + 1  # mt_speedrighttbl
            size = sr_start - sl_start - 1  # minus $00 separator
            if 1 <= size <= 32:
                # Verify $00 separator byte
                sep_off = sl_start + size - la
                if 0 <= sep_off < len(binary) and binary[sep_off] == 0x00:
                    speed_l_operand = a1
                    speed_r_operand = a2
                    return (sl_start - la, sr_start - la, size)

    # Fallback: only speed_r found (NOCALCULATEDSPEED=1 case -- only speedright used)
    if speed_r_operand is not None and speed_l_operand is None:
        # In NOCALCULATEDSPEED=1 mode, only mt_speedrighttbl is referenced.
        # The speed_left table is still present but not directly accessed via STA $FD.
        # Scan for a $00 byte before speed_r_operand+1 to find speed_left.
        sr_start = speed_r_operand + 1
        sr_off = sr_start - la
        # Walk backwards from sr_off-1 (the $00 separator) to find another $00
        # which would be the prefix before speed_left
        if sr_off > 0 and binary[sr_off - 1] == 0x00:
            # Found $00 separator. Now find the $00 prefix before speed_left.
            # Speed_left entries are between the two $00 bytes.
            # Search backwards for another $00 that's at the boundary
            for scan_back in range(sr_off - 2, max(0, sr_off - 66), -1):
                if binary[scan_back] == 0x00:
                    speed_size = sr_off - 1 - scan_back - 1
                    if speed_size > 0 and speed_size < 64:
                        sl_off = scan_back + 1
                        return (sl_off, sr_off, speed_size)
                    break

    return (None, None, 0)


def _extract_gt2_pattern(binary, start_off):
    """Extract a GT2 packed pattern following the original player's byte parsing.

    In GT2 packed format, $00 is only ENDPATT when it appears at a row
    boundary (the "next byte after note/rest" check).  A $00 can also appear
    as a command parameter (e.g. FX param = 0), in which case it is NOT
    the end marker.  Naive extraction that stops at the first $00 byte
    will truncate patterns that have zero-valued parameters, causing the
    player to miss notes that follow.

    This parser mirrors the GT2 V2.68 player's pattern reader logic:
      - < $40: instrument byte, then read next byte
      - $40-$4F: FX + note follows (FX cmd = byte & 0x0F, param if cmd!=0, then note)
      - $50-$5F: FXONLY (FX cmd = byte & 0x0F, param if cmd!=0, then done)
      - $60-$BC: note
      - $BD: rest
      - $BE: keyoff
      - $BF: keyon
      - >= $C0: packed rest (count in low bits)
      - $00 at row start: ENDPATT
    After each note/rest/keyon/keyoff/FXONLY, the next byte is the row
    continuation marker: $00 = ENDPATT, anything else = more rows.
    """
    result = bytearray()
    p = start_off
    limit = min(start_off + 512, len(binary))

    while p < limit:
        byte = binary[p]

        # Row start: $00 means end of pattern
        if byte == 0x00:
            result.append(byte)
            break

        # Instrument byte (< $40)
        if byte < 0x40:
            result.append(byte)
            p += 1
            if p >= limit:
                break
            byte = binary[p]
            # Fall through to check the next byte (FX / note / etc.)

        # FX + note ($40-$4F)
        if 0x40 <= byte <= 0x4F:
            result.append(byte)
            cmd = byte & 0x0F
            p += 1
            if cmd != 0 and p < limit:
                result.append(binary[p])  # FX param
                p += 1
            # Note byte follows
            if p < limit:
                note_byte = binary[p]
                result.append(note_byte)
                p += 1
                # After note: read continuation marker
                if 0x60 <= note_byte <= 0xBF:
                    if p < limit:
                        cont = binary[p]
                        result.append(cont)
                        if cont == 0x00:
                            break  # ENDPATT
                        p += 1
                    continue
                elif note_byte >= 0xC0:
                    continue  # packed rest after FX
                else:
                    continue  # unexpected byte as note
            continue

        # FXONLY ($50-$5F)
        if 0x50 <= byte <= 0x5F:
            result.append(byte)
            cmd = byte & 0x0F
            p += 1
            if cmd != 0 and p < limit:
                result.append(binary[p])  # FX param
                p += 1
            # No note follows; read continuation marker
            if p < limit:
                cont = binary[p]
                result.append(cont)
                if cont == 0x00:
                    break  # ENDPATT
                p += 1
            continue

        # Note ($60-$BC)
        if 0x60 <= byte <= 0xBC:
            result.append(byte)
            p += 1
            # Continuation marker
            if p < limit:
                cont = binary[p]
                result.append(cont)
                if cont == 0x00:
                    break  # ENDPATT
                p += 1
            continue

        # Rest ($BD), keyoff ($BE), keyon ($BF)
        if 0xBD <= byte <= 0xBF:
            result.append(byte)
            p += 1
            # Continuation marker
            if p < limit:
                cont = binary[p]
                result.append(cont)
                if cont == 0x00:
                    break  # ENDPATT
                p += 1
            continue

        # Packed rest (>= $C0)
        if byte >= 0xC0:
            result.append(byte)
            p += 1
            continue

        # Fallback: unknown byte, include and advance
        result.append(byte)
        p += 1

    return bytes(result)


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

    # Extract PSID flags (clock + SID model)
    import struct
    psid_flags = struct.unpack_from('>H', data, 0x76)[0] if len(data) > 0x77 else 0x0014

    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    code_end = ft[0]
    first_note = ft[1]
    num_notes = ft[2]
    lo_first = ft[3]

    # Detect NOWAVEDELAY from player binary: CMP #$10 / BCS → SBC #$10
    # Must verify BCS target is SBC #$10, not just any CMP #$10 / BCS.
    # Without this, Radar_Love's tempo code (CMP #$10 / BCS) falsely triggers.
    nowavedelay = True  # default: no delay feature
    for i in range(code_end - 3):
        if binary[i] == 0xC9 and binary[i + 1] == 0x10 and binary[i + 2] == 0xB0:
            bcs_offset = binary[i + 3]
            target = i + 4 + bcs_offset
            if target < code_end - 1 and binary[target] == 0xE9 and binary[target + 1] == 0x10:
                nowavedelay = False
                break

    # Detect BUFFEREDWRITES from player binary.
    # Find mt_loadregswaveonly: BD xx xx 3D xx xx 9D wave_reg 60
    # Then check if the loadregs path before it writes to AD/SR regs via BD (LDA abs,X).
    # For Group C, SID register addresses are ghost_buf+offset instead of $D400+offset.
    from gt2_parse_direct import detect_ghost_buffer
    ghost_base = detect_ghost_buffer(binary, code_end)

    def _is_wave_reg(lo, hi):
        if lo == 0x04 and hi == 0xD4:
            return True
        addr = lo | (hi << 8)
        if ghost_base is not None and ghost_base <= addr <= ghost_base + 0x18:
            return (addr - ghost_base) % 7 == 4
        return False

    def _is_freq_lo_reg(lo, hi):
        if lo == 0x00 and hi == 0xD4:
            return True
        addr = lo | (hi << 8)
        if ghost_base is not None and addr == ghost_base:
            return True
        return False

    def _is_adsr_reg(lo, hi):
        if hi == 0xD4 and lo in (0x05, 0x06):
            return True
        addr = lo | (hi << 8)
        if ghost_base is not None and ghost_base <= addr <= ghost_base + 0x18:
            return (addr - ghost_base) % 7 in (5, 6)
        return False

    buffered_writes = True  # default: assume buffered (most common)
    for i in range(code_end - 10):
        if (binary[i] == 0xBD and binary[i+3] == 0x3D and
                binary[i+6] == 0x9D and
                _is_wave_reg(binary[i+7], binary[i+8]) and
                binary[i+9] == 0x60):
            # Found mt_loadregswaveonly at offset i
            # Search backwards for freq stores
            for j in range(max(0, i - 30), i):
                if (binary[j] == 0xBD and binary[j+3] == 0x9D and
                        _is_freq_lo_reg(binary[j+4], binary[j+5])):
                    # Found freq_lo store. Check 30 bytes before for ADSR stores.
                    has_adsr = False
                    for k in range(max(0, j - 30), j):
                        if (binary[k] == 0xBD and binary[k+3] == 0x9D and
                                _is_adsr_reg(binary[k+4], binary[k+5])):
                            has_adsr = True
                            break
                    buffered_writes = has_adsr
                    break
            break

    # Detect ADPARAM/SRPARAM using the version detector
    from gt2_detect_version import detect_gt2_player_group
    ver_info = detect_gt2_player_group(sid_path)
    ad_param = ver_info['ad_param'] if ver_info else 0x0F
    sr_param = ver_info['sr_param'] if ver_info else 0x00
    # NOTE: Using detected values means some files change behavior from
    # the previous default ($0F/$00). If a file regresses, its previous
    # "passing" score was coincidental with the wrong ADPARAM.

    # Use gt2_parse_direct for reliable column detection
    r = parse_gt2_direct(sid_path)
    if r is None:
        return None

    ni = r['ni']
    col_start = r['col_operands']['ad'] + 1
    col_start_off = col_start - la

    # Compute flag-based column count for use in alternate layout detection.
    flags = r['flags']
    flag_cols = 3  # ad, sr, wave_ptr always present
    if not flags['nopulse']:
        flag_cols += 1
    if not flags['nofilter']:
        flag_cols += 1
    if not flags['noinstrvib']:
        flag_cols += 2
    if not flags['fixedparams']:
        flag_cols += 2

    pos = code_end
    freq_end = code_end + num_notes * 2

    # Detect alternate data layout used by large-code Group A players.
    # Standard layout: code | freq | song_table | pattern_table | instr_cols | tables | orderlists | patterns
    # Alternate layout: code | freq | instr_cols | tables | song_table | pattern_table | orderlists | patterns
    # Detection: if ad_operand is very close to freq_end (within ~20 bytes),
    # instrument columns are right after freq tables (alternate layout).
    # In standard layout, ad_operand is after song_table + pattern_table (50+ bytes gap).
    # In standard layout, minimum gap = 6 (song table) + 2 (1 pattern lo+hi) = 8.
    # In alternate layout, the gap is typically 4-6 (just padding/noise before
    # the Y-1 indexed AD operand).
    alternate_layout = (col_start_off - freq_end) < 8

    # num_cols: for alternate layout, use flag-based count (parse_direct's operand
    # scan fails because the stride-based column detection stops early).
    # For standard layout, trust parse_direct's operand-based count.
    if alternate_layout:
        num_cols = min(flag_cols, 9)
    else:
        num_cols = min(r['num_columns'], 9)

    result = {
        'la': la, 'code_end': code_end, 'ni': ni, 'num_cols': num_cols,
        'first_note': first_note, 'num_notes': num_notes,
        'psid_flags': psid_flags,
        'nowavedelay': nowavedelay,
        'buffered_writes': buffered_writes,
        'ad_param': ad_param,
        'sr_param': sr_param,
    }

    # Freq tables — respect lo_first flag from freq table detection.
    # lo_first=True: binary order is [freq_lo, freq_hi] (most common)
    # lo_first=False: binary order is [freq_hi, freq_lo]
    first_block = bytes(binary[pos:pos + num_notes])
    pos += num_notes
    second_block = bytes(binary[pos:pos + num_notes])
    pos += num_notes
    if lo_first:
        result['freq_lo'] = first_block
        result['freq_hi'] = second_block
    else:
        result['freq_lo'] = second_block
        result['freq_hi'] = first_block

    # Column name configs for determining column order from count
    col_name_configs = {
        3: ['ad', 'sr', 'wave_ptr'],
        4: ['ad', 'sr', 'wave_ptr', 'pulse_ptr'],
        5: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr'],
        6: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr', 'vib_param'],  # rare
        7: ['ad', 'sr', 'wave_ptr', 'vib_param', 'vib_delay', 'gate_timer', 'first_wave'],
        8: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'vib_param', 'vib_delay', 'gate_timer', 'first_wave'],
        9: ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr', 'vib_param', 'vib_delay', 'gate_timer', 'first_wave'],
    }

    def _read_columns_from_binary(pos_start):
        """Read instrument columns from binary, return (columns_dict, pos_after)."""
        # Use flag-based config when parse_direct's operand scan found fewer columns
        # than the flags indicate (common in alternate layout).
        # When parse_direct found enough columns, trust its STA-target-based naming.
        if r['col_data'] and len(r['col_data']) >= num_cols:
            col_names_for_file = list(r['col_data'].keys())[:num_cols]
        else:
            col_names_for_file = col_name_configs.get(num_cols)
            if col_names_for_file is None:
                full = ['ad', 'sr', 'wave_ptr', 'pulse_ptr', 'filter_ptr',
                        'vib_param', 'vib_delay', 'gate_timer', 'first_wave']
                col_names_for_file = full[:num_cols]

        cols = {}
        p = pos_start
        for c in range(num_cols):
            name = col_names_for_file[c] if c < len(col_names_for_file) else f'col{c}'
            cols[name] = list(binary[p:p + ni])
            p += ni
        return cols, p

    def _find_song_table_in_range(scan_start, scan_end):
        """Find the song table (6 bytes with 3 valid orderlist addresses) in a range.

        Returns (song_off, ol_addrs) or (None, None).
        """
        for scan in range(scan_start, min(scan_end, len(binary) - 6)):
            sl = [binary[scan + i] for i in range(3)]
            sh = [binary[scan + 3 + i] for i in range(3)]
            addrs = [sl[i] | (sh[i] << 8) for i in range(3)]
            # Valid: all addresses point into the data area (after freq tables)
            # and are within the binary range, and are reasonably close together.
            if all(la + freq_end < a < la + len(binary) for a in addrs):
                spread = max(addrs) - min(addrs)
                if spread < 500:
                    # Orderlist addresses must be AFTER the song table + pattern table
                    first_ol_off_cand = min(a - la for a in addrs)
                    if first_ol_off_cand <= scan + 6:
                        continue  # orderlists can't be before pattern table

                    # Validate first orderlist byte is a pattern ID, transpose, or repeat
                    # Pattern IDs: < 128. Transpose: $C0-$DF. Repeat/end: $E0-$FF.
                    if first_ol_off_cand >= len(binary):
                        continue
                    first_byte = binary[first_ol_off_cand]
                    if not (first_byte < 128 or first_byte >= 0xC0):
                        continue

                    # Validate pattern table: addresses between song table end and
                    # first orderlist must form valid pattern addresses
                    patt_tbl_off_cand = scan + 6
                    patt_space = first_ol_off_cand - patt_tbl_off_cand
                    num_patt_cand = patt_space // 2
                    if num_patt_cand < 1 or num_patt_cand > 200:
                        continue
                    # Check that pattern addresses are within the binary
                    valid_patts = True
                    for pi in range(min(num_patt_cand, 10)):
                        p_lo = binary[patt_tbl_off_cand + pi]
                        p_hi = binary[patt_tbl_off_cand + num_patt_cand + pi]
                        p_addr = p_lo | (p_hi << 8)
                        p_off = p_addr - la
                        if p_off < 0 or p_off >= len(binary):
                            valid_patts = False
                            break
                    if not valid_patts:
                        continue

                    return scan, addrs
        return None, None

    songs = 1  # TODO: detect multi-song
    song_entries = songs * 3

    if alternate_layout:
        # Alternate layout: freq | instr_cols | tables | song_table | pattern_table | orderlists | patterns
        # Instrument columns start right after freq tables (at col_start_off).
        columns, pos = _read_columns_from_binary(col_start_off)
        result['columns'] = columns

        # Table region: between instrument columns end and the song table.
        # We need to find the song table by scanning forward.
        instr_end = pos
        song_off, ol_addrs = _find_song_table_in_range(instr_end, len(binary))
        if song_off is None:
            return None

        first_ol_off = min(a - la for a in ol_addrs)
        result['orderlist_addrs'] = ol_addrs

        # Table region is between instrument columns end and song table
        table_region = bytes(binary[instr_end:song_off])
        result['table_region_start'] = instr_end
        result['table_region_size'] = len(table_region)

        # Pattern table: between song table end and first orderlist
        patt_tbl_off = song_off + 6
        patt_tbl_space = first_ol_off - patt_tbl_off
        num_patt = patt_tbl_space // 2
        patt_lo = [binary[patt_tbl_off + i] for i in range(num_patt)]
        patt_hi = [binary[patt_tbl_off + num_patt + i] for i in range(num_patt)]
        patt_addrs = [patt_lo[i] | (patt_hi[i] << 8) for i in range(num_patt)]
        result['num_patt'] = num_patt
        result['patt_addrs'] = patt_addrs

        # Update pos to the start of table region for table size calculations
        pos = instr_end

    else:
        # Standard layout: freq | song_table | pattern_table | instr_cols | tables | orderlists | patterns

        # Song table — read to find orderlist addresses
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
        columns, pos = _read_columns_from_binary(pos)
        result['columns'] = columns

        # Table region: between instrument columns end and first orderlist
        table_region = bytes(binary[pos:first_ol_off])
        result['table_region_start'] = pos
        result['table_region_size'] = len(table_region)
    result['table_region_start'] = pos
    result['table_region_size'] = len(table_region)

    has_pulse = 'pulse_ptr' in columns
    has_filter = 'filter_ptr' in columns
    has_vib = 'vib_param' in columns

    # Detect speed table from binary code (not just vib_param column).
    # Speed tables are needed for toneportamento, regular portamento, and vibrato.
    speed_detect = _detect_speed_table_from_binary(
        binary, la, code_end, pos, first_ol_off)
    has_speed = has_vib or speed_detect[2] > 0

    # Get table sizes from parse_direct's operand analysis.
    wave_size = r['wave_size']
    pulse_size = r['pulse_size'] if has_pulse else 0
    filter_size = r['filter_size'] if has_filter else 0
    speed_size = r['speed_size'] if has_speed else 0

    # If parse_direct missed the speed table but binary detection found it,
    # use the binary-detected size.
    if speed_size == 0 and speed_detect[2] > 0:
        speed_size = speed_detect[2]

    # For small ni, validate wave_size with frequency trace FIRST
    # (parse_direct is unreliable for ni<=3).
    # Skip for alternate layout: freq_trace assumes song table is at freq_end.
    if ni <= 3 and len(table_region) > 0 and not alternate_layout:
        trace_wave_size = _find_wave_size_by_freq_trace(
            sid_path, binary, la, code_end, pos, first_note, num_notes, columns)
        if trace_wave_size > 0:
            wave_size = trace_wave_size

    # Validate wave_size against max wave_ptr.
    # Wave pointers are 1-based indices into the wave table. If max(wave_ptr)
    # exceeds wave_size, the table was truncated — scan for the correct end.
    max_wave_ptr = max(columns.get('wave_ptr', [0]))
    if max_wave_ptr > wave_size and len(table_region) > max_wave_ptr:
        # Scan from max_wave_ptr-1 (0-based) for the next $FF (jump marker)
        for scan_idx in range(max_wave_ptr - 1, min(len(table_region) // 2, max_wave_ptr + 64)):
            if table_region[scan_idx] == 0xFF:
                wave_size = scan_idx + 1
                break
        else:
            wave_size = max_wave_ptr  # fallback: at least cover all pointers

    # Validate filter_size against max filter_ptr (analogous to wave_size validation).
    # Filter pointers are 1-based indices. If max(filter_ptr) exceeds filter_size,
    # the table was truncated — scan for the correct end.
    if has_filter:
        max_filter_ptr = max(columns.get('filter_ptr', [0]))
        if max_filter_ptr > filter_size:
            filter_table_offset = wave_size * 2 + pulse_size * 2
            for scan_idx in range(max_filter_ptr - 1,
                                  min(len(table_region) // 2 - filter_table_offset,
                                      max_filter_ptr + 64)):
                abs_idx = filter_table_offset + scan_idx
                if abs_idx < len(table_region) and table_region[abs_idx] == 0xFF:
                    filter_size = scan_idx + 1
                    break
            else:
                filter_size = max_filter_ptr  # fallback: cover all pointers

    # If wave_size was corrected upward, pulse/filter sizes from parse_direct
    # may be wrong (they were computed with the smaller wave_size). Recalculate
    # from the remaining space.
    speed_overhead = (2 + speed_size * 2) if speed_size > 0 else 0
    known_bytes = wave_size * 2 + pulse_size * 2 + filter_size * 2 + speed_overhead
    if known_bytes > len(table_region):
        # Table sizes overflow — recalculate pulse/filter/speed from remaining space
        remaining_for_others = len(table_region) - wave_size * 2
        # Use max ptr values as minimum sizes
        max_pp = max(columns.get('pulse_ptr', [0])) if has_pulse else 0
        max_fp = max(columns.get('filter_ptr', [0])) if has_filter else 0

        if has_pulse and has_filter and not has_speed:
            # Scan pulse table data to find its boundary.
            # Pulse table entries end with $FF (jump marker).
            # Find the last $FF that makes sense as pulse table end.
            pulse_start = wave_size * 2
            pulse_size = 0
            for scan in range(max(max_pp, 1), remaining_for_others // 2):
                if pulse_start + scan - 1 < len(table_region) and table_region[pulse_start + scan - 1] == 0xFF:
                    # Check if the remaining bytes can fit filter table
                    candidate_filter = (remaining_for_others - scan * 2) // 2
                    if candidate_filter >= max_fp:
                        pulse_size = scan
            if pulse_size == 0:
                # Fallback: split evenly based on minimum requirements
                pulse_size = max(max_pp, remaining_for_others // 4)
            filter_size = (remaining_for_others - pulse_size * 2) // 2
            speed_size = 0
        elif has_pulse and has_filter and has_speed:
            # Try to find pulse boundary, then filter, rest is speed
            pulse_start = wave_size * 2
            pulse_size = 0
            for scan in range(max(max_pp, 1), remaining_for_others // 2):
                if pulse_start + scan - 1 < len(table_region) and table_region[pulse_start + scan - 1] == 0xFF:
                    candidate_rest = remaining_for_others - scan * 2
                    # Filter must fit, and speed has 2-byte overhead
                    if candidate_rest >= max_fp * 2 + 4:
                        pulse_size = scan
            if pulse_size == 0:
                pulse_size = max(max_pp, 1)
            after_pulse = remaining_for_others - pulse_size * 2
            # Find filter boundary
            filter_start = wave_size * 2 + pulse_size * 2
            filter_size = 0
            for scan in range(max(max_fp, 1), after_pulse // 2):
                if filter_start + scan - 1 < len(table_region) and table_region[filter_start + scan - 1] == 0xFF:
                    filter_size = scan
            if filter_size == 0:
                filter_size = max(max_fp, 1)
            speed_data = after_pulse - filter_size * 2
            speed_size = max(0, (speed_data - 2) // 2) if speed_data >= 4 else 0
        else:
            # Simpler cases
            if has_pulse:
                pulse_size = max(max_pp, (remaining_for_others - (max_fp * 2 if has_filter else 0)) // 2)
            if has_filter:
                filter_size = max(max_fp, (remaining_for_others - pulse_size * 2) // 2)
            speed_size = 0
        speed_overhead = (2 + speed_size * 2) if speed_size > 0 else 0

    # Recompute after potential corrections
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

    # Fallback if still no wave_size (skip freq_trace for alternate layout)
    if wave_size <= 0 and len(table_region) > 0 and not alternate_layout:
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
        if ol_off < 0 or ol_off >= len(binary):
            orderlists.append(b'\xff\x00')
            continue
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
        if 0 <= p_off < len(binary):
            patt = _extract_gt2_pattern(binary, p_off)
        else:
            patt = b'\x00'  # empty pattern for out-of-bounds addresses
        patterns.append(patt)
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
