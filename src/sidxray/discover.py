"""Generic structure discovery from a siddump --memtrace.

Goal: given a memory access trace from siddump, figure out which bytes
of the loaded SID are code, which are data tables, and roughly what
shape each table has — without knowing which engine produced the SID.

This is the validation experiment for the "discovery-first decompiler"
architecture. If it can rediscover Commando's known layout (code
$5000-$5FFF, instruments at $5591, song table at $56FF, sequence
pointers at $5711/$573E) from the memtrace alone, the approach is
viable for unknown engines.

Usage:
    python3 src/sidxray/discover.py <sid_file>
"""

import sys
import re
from collections import defaultdict
from dataclasses import dataclass


def parse_memtrace(path: str) -> tuple[dict[int, int], dict[int, int]]:
    """Parse a siddump --memtrace dump.

    Returns (read_counts, write_counts) — each a dict mapping address
    to access count over the whole trace.

    The trace is a sequence of `ADDR=BYTE` pairs separated by spaces.
    Lines correspond to frames. We don't distinguish reads from writes
    yet because siddump's format doesn't tag them — they all look the
    same. For SID register addresses ($D400-$D41C) every access is a
    write; for everything else every access is a read (since 6502
    instructions either fetch or load).

    Actually that's not quite right — STA writes to RAM produce traces
    too, with the value being what was written. We'll lump them
    together and split later if needed.
    """
    pat = re.compile(r'([0-9A-F]{4})=([0-9A-F]{2})')
    counts: dict[int, int] = defaultdict(int)
    with open(path) as f:
        for line in f:
            for m in pat.finditer(line):
                addr = int(m.group(1), 16)
                counts[addr] += 1
    return counts, {}


def get_sid_load_range(sid_path: str) -> tuple[int, int]:
    """Read PSID header to find the loaded address range."""
    with open(sid_path, 'rb') as f:
        data = f.read()
    # PSID v2 header: load address at offset 0x08 (big-endian), but if
    # zero it means load address is at start of data after dataOffset.
    data_offset = int.from_bytes(data[0x06:0x08], 'big')
    load_addr = int.from_bytes(data[0x08:0x0A], 'big')
    if load_addr == 0:
        # Load address is little-endian at the start of the data section
        load_addr = data[data_offset] | (data[data_offset + 1] << 8)
        payload_size = len(data) - data_offset - 2
    else:
        payload_size = len(data) - data_offset
    return load_addr, load_addr + payload_size - 1


@dataclass
class Region:
    start: int
    end: int          # inclusive
    accesses: int
    role_guess: str
    notes: str = ''

    @property
    def size(self) -> int:
        return self.end - self.start + 1


def classify_addresses(counts: dict[int, int], load_lo: int, load_hi: int) -> list[Region]:
    """Walk the loaded address range, grouping consecutive accessed
    addresses into regions. Each region gets a heuristic role guess
    based on access count and density.

    Heuristics:
      - Very high access count (>>1 per frame): hot — likely code in
        the play loop or a heavily-read table (e.g. freq table).
      - Moderate access count (around 1-3 per frame): probably code or
        per-frame data lookups.
      - Low access count (handful over whole trace): probably init-only
        code, song table, or pattern data read once per pattern start.
      - Zero accesses: dead bytes — pad, dead code, unused tables, OR
        possibly data that was never reached because the song's loop
        didn't visit that subtune / pattern in our trace duration.
    """
    in_range = {a: c for a, c in counts.items() if load_lo <= a <= load_hi}
    if not in_range:
        return []

    sorted_addrs = sorted(in_range.keys())
    regions: list[Region] = []
    cur_start = sorted_addrs[0]
    cur_end = cur_start
    cur_total = in_range[cur_start]

    # Group consecutive (adjacent or near-adjacent) addresses into runs.
    # Allow a small gap (≤ 4 bytes of zero-access in between) to merge,
    # since a read pattern like "read every 4th byte of a stride-4 table"
    # would otherwise fragment.
    GAP_TOLERANCE = 4

    for a in sorted_addrs[1:]:
        if a <= cur_end + GAP_TOLERANCE + 1:
            cur_end = a
            cur_total += in_range[a]
        else:
            regions.append(Region(
                start=cur_start, end=cur_end,
                accesses=cur_total,
                role_guess='?'
            ))
            cur_start = a
            cur_end = a
            cur_total = in_range[a]
    regions.append(Region(
        start=cur_start, end=cur_end,
        accesses=cur_total,
        role_guess='?'
    ))

    return regions


def annotate_regions(regions: list[Region], n_frames: int) -> list[Region]:
    """Add role guesses based on access density."""
    for r in regions:
        per_frame = r.accesses / max(n_frames, 1)
        per_byte_per_frame = per_frame / r.size
        if per_frame > 50:
            r.role_guess = 'hot_code_or_lookup_table'
        elif per_frame > 5:
            r.role_guess = 'play_loop_code_or_voice_state_table'
        elif per_frame > 0.5:
            r.role_guess = 'periodic_lookup'
        else:
            r.role_guess = 'cold_data_or_init_code'
        r.notes = f'{per_frame:.1f} accesses/frame, {per_byte_per_frame:.2f}/byte/frame'
    return regions


def count_frames(path: str) -> int:
    """Count frames in the memtrace (one frame per line)."""
    n = 0
    with open(path) as f:
        for _ in f:
            n += 1
    return n


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    sid_path = sys.argv[1]

    print(f'SID: {sid_path}')
    load_lo, load_hi = get_sid_load_range(sid_path)
    print(f'Loaded range: ${load_lo:04X}-${load_hi:04X} ({load_hi-load_lo+1} bytes)')

    # Capture memtrace (assume already done if file exists)
    import os
    trace_path = '/tmp/' + os.path.basename(sid_path).replace('.sid', '_memtrace.txt')
    if not os.path.exists(trace_path):
        print(f'Capturing memtrace to {trace_path}...')
        os.system(f'/home/jtr/sidfinity/tools/siddump "{sid_path}" --memtrace --duration 30 --raw > "{trace_path}" 2>/dev/null')

    print(f'Parsing {trace_path}...')
    counts, _ = parse_memtrace(trace_path)
    n_frames = count_frames(trace_path)
    print(f'Frames: {n_frames}, total accesses: {sum(counts.values()):,}, unique addresses: {len(counts):,}')

    regions = classify_addresses(counts, load_lo, load_hi)
    regions = annotate_regions(regions, n_frames)

    print(f'\nDiscovered {len(regions)} contiguous regions in $payload range:\n')
    print(f'{"start":>6} {"end":>6} {"size":>5} {"accs":>10} {"role":<35} notes')
    print('-' * 100)
    for r in regions:
        print(f'${r.start:04X}  ${r.end:04X}  {r.size:>5}  {r.accesses:>10,}  {r.role_guess:<35} {r.notes}')


if __name__ == '__main__':
    main()
