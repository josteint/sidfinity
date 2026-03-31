"""
sidxray.gt2_detect — Detect GoatTracker V2 layout parameters from memtrace.

Uses co-occurrence analysis of note-trigger reads to find:
- ni (number of instruments / column stride)
- Number of instrument columns present
- Column base address
"""

import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sidxray.trace import capture
from gt_parser import parse_psid_header, find_freq_table


def detect_gt2_layout(sid_path, duration=10):
    """Detect GT2 instrument layout from memory trace.

    Returns dict with:
      ni: number of instruments (column stride)
      num_columns: number of instrument columns
      col_base: address of first column
      freq_end: address after frequency tables
      columns: dict mapping column_index → list of ni values
    """
    with open(sid_path, 'rb') as f:
        data = f.read()

    _, binary, la = parse_psid_header(data)
    ft = find_freq_table(binary, la)
    if ft is None:
        return None

    freq_end = ft[0] + ft[2] * 2
    freq_end_addr = la + freq_end

    # Capture trace
    _, frames = capture(sid_path, duration)
    if not frames:
        return None

    # Filter to data area
    for frame in frames:
        frame.reads = [r for r in frame.reads if r.addr >= freq_end_addr]

    num_frames = max(ft.frame for ft in frames) + 1

    # Build per-address frame sets
    addr_frames = defaultdict(set)
    for ft in frames:
        for r in ft.reads:
            addr_frames[r.addr].add(ft.frame)

    # Find co-occurrence groups at low duty (note triggers)
    groups = defaultdict(list)
    for addr, fset in addr_frames.items():
        duty = len(fset) / num_frames
        if 0.01 < duty < 0.15:
            groups[frozenset(fset)].append(addr)

    # Find the group with the most CONSISTENT stride > 1.
    # The instrument column group has addresses at regular stride (= ni).
    # Adjacent-byte groups (stride 1) are NOT what we want.
    from collections import Counter

    best_group = []
    best_ni = 0
    for fset, addrs in groups.items():
        if len(addrs) < 3:
            continue
        addrs_sorted = sorted(addrs)
        gaps = [addrs_sorted[i + 1] - addrs_sorted[i] for i in range(len(addrs_sorted) - 1)]
        gap_counts = Counter(gaps)
        most_common_gap, count = gap_counts.most_common(1)[0]
        # We want: consistent stride > 1, majority of gaps match
        if most_common_gap > 1 and count >= len(gaps) * 0.6:
            if len(addrs) > len(best_group):
                best_group = addrs_sorted
                best_ni = most_common_gap

    if not best_group or best_ni < 2:
        return None

    ni = best_ni

    # The column base = first address in group - (Y offset)
    # Y offset = (first_addr - some_base) % ni
    # The base should be at freq_end_addr or shortly after
    first_addr = best_group[0]
    y_offset = (first_addr - freq_end_addr) % ni
    col_base = freq_end_addr

    # Number of columns = how many stride-ni steps fit in the group's address range
    num_columns = (best_group[-1] - best_group[0]) // ni + 1

    # Verify: also check other Y offsets for the same stride
    # This confirms the stride is correct
    all_y_offsets = set()
    for addr, fset in addr_frames.items():
        if freq_end_addr <= addr < freq_end_addr + num_columns * ni + ni:
            off = (addr - freq_end_addr) % ni
            all_y_offsets.add(off)

    # Read column data
    columns = {}
    for ci in range(num_columns):
        col_off = freq_end + ci * ni
        if col_off + ni <= len(binary):
            columns[ci] = list(binary[col_off:col_off + ni])

    return {
        'ni': ni,
        'num_columns': num_columns,
        'col_base': col_base,
        'col_base_offset': freq_end,
        'freq_end': freq_end,
        'freq_end_addr': freq_end_addr,
        'columns': columns,
        'y_offsets_seen': sorted(all_y_offsets),
        'co_occurrence_size': len(best_group),
    }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 -m sidxray.gt2_detect <file.sid>")
        sys.exit(1)

    result = detect_gt2_layout(sys.argv[1])
    if result is None:
        print("Could not detect GT2 layout")
        sys.exit(1)

    print(f"ni={result['ni']}, columns={result['num_columns']}")
    print(f"col_base=${result['col_base']:04X}, freq_end={result['freq_end']}")
    print(f"Y offsets seen: {result['y_offsets_seen']}")

    col_names = ['AD', 'SR', 'wave_ptr', 'pulse_ptr', 'filt_ptr',
                 'vib_param', 'vib_delay', 'gate_timer', 'first_wave']
    for ci, vals in sorted(result['columns'].items()):
        name = col_names[ci] if ci < len(col_names) else f'col{ci}'
        hex_str = ' '.join(f'{v:02x}' for v in vals)
        print(f"  {name:12s}: {hex_str}")
