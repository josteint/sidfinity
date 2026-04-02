"""
gt2_parse_direct.py — Parse GoatTracker V2 packed SID by reading operands
directly from the player code.

The 6502 instructions tell us exactly where every piece of data lives:
- LDA operand,Y → STA $D405,X identifies the AD column
- LDA operand,Y → STA $D406,X identifies the SR column
- Stride between AD and SR = ni (number of instruments)
- All columns at stride ni from AD, identified by STA targets + content
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gt_parser import parse_psid_header, find_freq_table, collect_abs_addresses


def find_lda_sta_pairs(binary, la, code_end):
    """Find all LDA abs,Y → STA patterns in player code."""
    pairs = []
    i = 0
    while i < code_end - 5:
        if binary[i] == 0xB9:  # LDA abs,Y
            src = binary[i + 1] | (binary[i + 2] << 8)
            if (src - la) >= 0:
                for j in range(i + 3, min(i + 15, code_end - 2)):
                    if binary[j] in (0x9D, 0x8D):
                        dst = binary[j + 1] | (binary[j + 2] << 8)
                        mode = 'abs_x' if binary[j] == 0x9D else 'abs'
                        pairs.append((src, dst, mode))
                        break
        i += 1
    return pairs


def parse_gt2_direct(sid_path):
    """Parse a GT2 SID by reading operand addresses from the player code."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    header, binary, la = parse_psid_header(data)
    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    freq_off, first_note, num_notes, lo_first = ft
    code_end = freq_off
    freq_end = freq_off + num_notes * 2

    # Step 1: Find AD and SR columns by SID register writes
    ad_operand = sr_operand = None
    i = 0
    while i < code_end - 5:
        if binary[i] == 0xB9:  # LDA abs,Y
            src = binary[i + 1] | (binary[i + 2] << 8)
            if (src - la) >= freq_end:
                for j in range(i + 3, min(i + 12, code_end - 2)):
                    if binary[j] == 0x9D:  # STA abs,X
                        dst = binary[j + 1] | (binary[j + 2] << 8)
                        if 0xD400 <= dst <= 0xD41F:
                            reg = (dst - 0xD400) % 7
                            if reg == 5 and ad_operand is None:
                                ad_operand = src
                            elif reg == 6 and sr_operand is None:
                                sr_operand = src
                        break
        i += 1

    if ad_operand is None or sr_operand is None:
        return None

    # Step 2: ni = gap between AD and SR
    ni = sr_operand - ad_operand
    if ni < 1 or ni > 63:
        return None

    # Step 3: Find all columns at stride ni from AD.
    # Stop when we hit an address pair (addr and addr+1 both referenced as LDA sources) —
    # that's the start of table data, not instrument columns.
    # Only count LDA references (not STA) to avoid self-modifying code false positives.
    all_code_refs = set(s for s in collect_abs_addresses(binary, la, 0, code_end)
                        if s >= la + freq_end)
    lda_refs = set()
    for i in range(code_end - 3):
        if binary[i] in (0xB9, 0xBD, 0xBC, 0xBE, 0xAD, 0xAC, 0xAE):  # LDA/LDY/LDX variants
            addr = binary[i + 1] | (binary[i + 2] << 8)
            if addr >= la + freq_end:
                lda_refs.add(addr)

    col_operands = []
    for k in range(15):
        addr = ad_operand + k * ni
        if addr not in all_code_refs:
            break
        # Stop at table pair: addr AND addr+1 both LDA refs.
        # But with ni=1, consecutive columns look like pairs — skip this check.
        if ni > 1 and (addr + 1) in lda_refs:
            break
        col_operands.append(addr)

    # Step 4: Read column data (1-based Y indexing)
    raw_cols = {}
    for ci, operand in enumerate(col_operands):
        off = operand - la
        vals = [binary[off + y] for y in range(1, ni + 1) if off + y < len(binary)]
        raw_cols[ci] = vals

    # Step 5: Identify columns by STA targets.
    # Build a map: column operand → STA target
    col_sta_targets = {}
    for src, dst, mode in find_lda_sta_pairs(binary, la, code_end):
        if src in set(col_operands):
            ci = col_operands.index(src)
            if ci not in col_sta_targets:
                col_sta_targets[ci] = (dst, mode)

    columns = {'ad': 0, 'sr': 1}

    # Identify remaining columns by their STA targets.
    # The wave_ptr column shares its STA target with the wave table right column:
    # both write to mt_chnwaveptr. Find which column index has same STA target
    # as any LDA from the post-instrument area.
    post_instr_targets = {}
    for src, dst, mode in find_lda_sta_pairs(binary, la, code_end):
        if (src - la) > freq_end + ni * 7 and mode == 'abs_x':
            post_instr_targets[dst] = src

    # Wave_ptr column: the one that shares STA target $1450-equivalent with
    # the wave table right column. Pick the LOWEST column index that matches.
    wave_ptr_candidates = []
    for ci, (target, mode) in col_sta_targets.items():
        if ci <= 1:
            continue
        if target in post_instr_targets and mode == 'abs_x':
            wave_ptr_candidates.append(ci)
    if wave_ptr_candidates:
        columns['wave_ptr'] = min(wave_ptr_candidates)

    # Identify pulse_ptr: the column that writes to mt_chnpulseptr.
    # mt_chnpulseptr = mt_chnwave + 1. Find mt_chnwave from the waveform
    # register write chain: LDA mt_chnwave,X; AND mt_chngate,X; STA $D404,X.
    # Then mt_chnpulseptr = mt_chnwave + 1.
    mt_chnwave = None
    for i in range(code_end - 5):
        if binary[i] == 0x9D:
            dst = binary[i + 1] | (binary[i + 2] << 8)
            if 0xD400 <= dst <= 0xD41F and (dst - 0xD400) % 7 == 4:
                # STA $D404,X — look back for LDA abs,X
                for j in range(max(0, i - 8), i):
                    if binary[j] == 0xBD:
                        mt_chnwave = binary[j + 1] | (binary[j + 2] << 8)
                        break
                break

    if mt_chnwave is not None:
        mt_chnpulseptr = mt_chnwave + 1
        for ci, (target, mode) in col_sta_targets.items():
            if target == mt_chnpulseptr and mode == 'abs_x':
                columns['pulse_ptr'] = ci
                break

    # The first_wave column stores to mt_chnwave. Identify by: it's the column
    # immediately after wave_ptr (greloc.c always emits them adjacent).
    # Actually, just use the order: after AD, SR, wave_ptr come first_wave,
    # pulse_ptr, filter_ptr, vib_delay, vib_param. But this varies.
    # Safest: assign unidentified columns by their stride position.
    # GT2 standard order: AD, SR, wave_ptr, pulse_ptr, filt_ptr, vib_param, vib_delay
    # With FIXEDPARAMS: AD, SR, wave_ptr, first_wave, pulse_ptr, vib_delay, vib_param
    # Identify filter_ptr: column that writes to a GLOBAL variable (STA abs, not abs,X).
    # Filter is global in GT2 (shared across all channels).
    for ci, (target, mode) in col_sta_targets.items():
        if ci <= 1 or ci in columns.values():
            continue
        if mode == 'abs':  # STA abs (global, not per-channel)
            columns['filter_ptr'] = ci
            break

    # Assign remaining unidentified columns by position.
    # After wave_ptr, pulse_ptr, filter_ptr: remaining are vib_param, vib_delay
    # (matching greloc.c order: ptr[STBL], vibdelay, gatetimer, firstwave).
    unassigned = sorted(ci for ci in range(2, len(col_operands))
                        if ci not in columns.values())
    remaining_names = ['vib_param', 'vib_delay', 'gate_timer', 'first_wave']
    for ci, name in zip(unassigned, remaining_names):
        columns[name] = ci

    # Step 6: Find wave table via address pairs
    # Wave table left/right operands: both addr and addr+1 referenced
    instr_end = ad_operand + len(col_operands) * ni
    table_operands = []
    for a in sorted(all_code_refs):
        if a >= instr_end and (a + 1) in all_code_refs:
            table_operands.append(a)

    wave_left = b''
    wave_right = b''
    wt_size = 0
    # table_operands has the FIRST member of each (addr, addr+1) pair.
    # Wave left uses the first pair's first member: LDA $159F,Y
    # Extract all table pairs: wave, pulse, filter, speed
    # table_operands = [wave_left, pulse_left, filter_left, speed_left, ...]
    # Each pair: left_op and left_op+1 both referenced.
    # The right column operand = next pair's first member + 1.
    # Table size = right_op - left_op.

    # GT2 table layout: contiguous regions, each table has left+right of equal size.
    # Layout order: wave_L, wave_R, pulse_L, pulse_R, filter_L, filter_R, speed_L, speed_R
    # The table_operands (pairs) mark: wave_L, wave_R, pulse_L, filter_L (not all 8).
    # Each table's size = gap between its left operand and its right operand.
    # Wave: left at pair[0], right at pair[1]+1. size = pair[1]+1 - pair[0].
    # Pulse left at pair[2], right at pair[2] + pulse_size.
    # Pulse size = gap from pulse_left to the next table (filter at pair[3]).

    def read_table(start_off, size):
        """Read size bytes from binary at offset."""
        if start_off >= 0 and start_off + size <= len(binary):
            return bytes(binary[start_off: start_off + size])
        return b''

    wave_left = wave_right = pulse_left = pulse_right = b''
    filter_left = filter_right = speed_left = speed_right = b''
    wt_size = pt_size = ft_size = st_size = 0

    if len(table_operands) >= 2:
        # Wave table: left at pair[0]+1, right at pair[1]+2
        # (pair[1] is the wave RIGHT operand, pair[1]+1 is the -1 adj)
        wl_start = table_operands[0] + 1  # mt_wavetbl
        wr_start = table_operands[1] + 2  # mt_notetbl (pair[1]+1 gives operand, +1 for -1 adj)
        wt_size = wr_start - wl_start

        wave_left = read_table(wl_start - la, wt_size + ni)
        wave_right = read_table(wr_start - la, wt_size + ni)

    if len(table_operands) >= 4:
        # Pulse table: left at pair[2]+1, right follows immediately
        pl_start = table_operands[2] + 1  # mt_pulsetimetbl
        fl_start = table_operands[3] + 1  # mt_filttimetbl
        pulse_total = fl_start - pl_start
        pt_size = pulse_total // 2
        pr_start = pl_start + pt_size

        pulse_left = read_table(pl_start - la, pt_size + ni)
        pulse_right = read_table(pr_start - la, pt_size + ni)

        # Filter table: find the right column operand.
        # mt_filtspdtbl is accessed as LDA mt_filtspdtbl-1,Y.
        # So we look for LDA addresses past fl_start that are referenced
        # multiple times (filter right is accessed from multiple code paths).
        # The filter right operand = mt_filtspdtbl - 1.
        fr_operand = None
        lda_ref_counts = {}
        for i in range(code_end - 3):
            if binary[i] == 0xB9:  # LDA abs,Y
                addr = binary[i + 1] | (binary[i + 2] << 8)
                if fl_start < addr < fl_start + 100:
                    lda_ref_counts[addr] = lda_ref_counts.get(addr, 0) + 1

        # The filter right operand typically has 3-4 refs (from filter code paths)
        for addr, count in sorted(lda_ref_counts.items()):
            if count >= 3:
                fr_operand = addr
                break

        if fr_operand is not None:
            ft_size = (fr_operand + 1) - fl_start  # mt_filtspdtbl = fr_operand + 1
        else:
            ft_size = pt_size  # fallback: same as pulse

        filter_left = read_table(fl_start - la, ft_size)
        filter_right = read_table(fl_start + ft_size - la, ft_size)

        # Speed table: comes after filter right column.
        # Format: extra_zero + mt_speedlefttbl data + extra_zero + mt_speedrighttbl data
        # Speed table operands: LDA mt_speedlefttbl-1,Y and LDA mt_speedrighttbl-1,Y
        # The extra zero + data starts right after filter right ends.
        speed_start = fl_start + ft_size * 2  # after both filter columns
        # Find speed table operands: single-ref LDA addresses past filter
        speed_l_operand = None
        speed_r_operand = None
        for addr in sorted(lda_ref_counts.keys()):
            if addr >= speed_start - 1:
                if speed_l_operand is None:
                    speed_l_operand = addr
                elif speed_r_operand is None:
                    speed_r_operand = addr
                    break

        # Also check addresses not in lda_ref_counts (might have single refs)
        if speed_l_operand is None:
            for i in range(code_end - 3):
                if binary[i] == 0xB9:
                    addr = binary[i + 1] | (binary[i + 2] << 8)
                    if speed_start - 1 <= addr < speed_start + 50:
                        if speed_l_operand is None:
                            speed_l_operand = addr
                        elif addr != speed_l_operand and speed_r_operand is None:
                            speed_r_operand = addr
                            break

        if speed_l_operand is not None and speed_r_operand is not None:
            # mt_speedlefttbl = speed_l_operand + 1 (operand is -1 for Y indexing)
            sl_start = speed_l_operand + 1
            sr_start = speed_r_operand + 1
            st_size = sr_start - sl_start - 1  # subtract 1 for extra zero before right
            if st_size > 0:
                speed_left = read_table(sl_start - la, st_size)
                speed_right = read_table(sr_start - la, st_size)

    # Build result
    col_data = {}
    for name, ci in columns.items():
        col_data[name] = raw_cols.get(ci, [])

    return {
        'header': header,
        'la': la,
        'ni': ni,
        'num_columns': len(col_operands),
        'col_operands': {name: col_operands[ci] for name, ci in columns.items()
                         if ci < len(col_operands)},
        'col_data': col_data,
        'wave_left': wave_left,
        'wave_right': wave_right,
        'wave_size': wt_size,
        'pulse_left': pulse_left,
        'pulse_right': pulse_right,
        'pulse_size': pt_size,
        'filter_left': filter_left,
        'filter_right': filter_right,
        'filter_size': ft_size,
        'speed_left': speed_left,
        'speed_right': speed_right,
        'speed_size': st_size,
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: gt2_parse_direct.py <file.sid>")
        sys.exit(1)

    result = parse_gt2_direct(sys.argv[1])
    if result is None:
        print("Parse failed")
        sys.exit(1)

    print(f"ni={result['ni']}, columns={result['num_columns']}")
    for name, addr in sorted(result['col_operands'].items(), key=lambda x: x[1]):
        vals = result['col_data'].get(name, [])
        hex_str = ' '.join(f'{v:02x}' for v in vals[:5])
        print(f"  {name:15s} ${addr:04X}: {hex_str}")

    wl = result['wave_left']
    wr = result['wave_right']
    if wl and len(wl) > 1:
        print(f"\nWave table ({result['wave_size']} entries):")
        for i in range(1, min(6, len(wl))):
            l = wl[i]
            r = wr[i] if i < len(wr) else 0
            if l == 0xFF:
                print(f"  [{i-1}]: LOOP → {r}")
            else:
                print(f"  [{i-1}]: L=${l:02X} R=${r:02X}")
