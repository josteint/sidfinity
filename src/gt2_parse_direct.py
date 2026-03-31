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
    # Stop when we hit an address pair (addr and addr+1 both referenced) —
    # that's the start of table data, not instrument columns.
    all_code_refs = set(s for s in collect_abs_addresses(binary, la, 0, code_end)
                        if s >= la + freq_end)
    col_operands = []
    for k in range(15):
        addr = ad_operand + k * ni
        if addr in all_code_refs and (addr + 1) not in all_code_refs:
            col_operands.append(addr)
        else:
            break

    # Step 4: Read column data (1-based Y indexing)
    raw_cols = {}
    for ci, operand in enumerate(col_operands):
        off = operand - la
        vals = [binary[off + y] for y in range(1, ni + 1) if off + y < len(binary)]
        raw_cols[ci] = vals

    # Step 5: Identify columns by content and STA targets
    columns = {'ad': 0, 'sr': 1}

    # Find wave_ptr: it feeds the same STA target as the wave table right column
    # Find first_wave: values look like SID waveform bytes ($00, $09, $10-$81)
    for ci in range(2, len(col_operands)):
        vals = raw_cols.get(ci, [])
        if not vals:
            continue

        # Check if values look like waveform bytes
        waveform_like = sum(1 for v in vals if v in (0, 0x09, 0x10, 0x11, 0x13,
                            0x17, 0x20, 0x21, 0x23, 0x40, 0x41, 0x42, 0x80, 0x81))
        if waveform_like > len(vals) * 0.4 and 'first_wave' not in columns:
            columns['first_wave'] = ci
            continue

        # Check if values look like small table indices (0-30ish)
        small_indices = sum(1 for v in vals if v < 40)
        if small_indices > len(vals) * 0.6 and 'wave_ptr' not in columns:
            columns['wave_ptr'] = ci
            continue

    # Assign remaining columns by position
    for ci in range(2, len(col_operands)):
        if ci not in columns.values():
            if 'pulse_ptr' not in columns:
                columns['pulse_ptr'] = ci
            elif 'filter_ptr' not in columns:
                columns['filter_ptr'] = ci
            elif 'vib_param' not in columns:
                columns['vib_param'] = ci
            elif 'vib_delay' not in columns:
                columns['vib_delay'] = ci
            elif 'gate_timer' not in columns:
                columns['gate_timer'] = ci

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
    # Wave right uses the second pair's SECOND member: LDA $15C0,Y
    # (because the right column also uses -1 addressing independently)
    if len(table_operands) >= 2:
        wl_op = table_operands[0]         # $159F
        wr_op = table_operands[1] + 1     # $15BF + 1 = $15C0
        wt_size = wr_op - wl_op           # $15C0 - $159F = 33
        wl_off = wl_op - la
        wr_off = wr_op - la
        if wl_off >= 0 and wr_off + wt_size < len(binary):
            wave_left = bytes(binary[wl_off: wl_off + wt_size + ni])
            wave_right = bytes(binary[wr_off: wr_off + wt_size + ni])

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
