"""
sidxray.analyze — Analyze memory traces to identify player data structures.

Key insight: we classify memory regions by HOW the player accesses them.
- Frequency table: 96 consecutive reads mapping notes to freq values
- Instrument columns: read on note triggers, indexed by instrument number
- Wave table: read every frame, stepping through sequentially
- Pulse/filter tables: similar to wave table
- Pattern data: read on tick boundaries, sequential with branches
- Orderlists: read when pattern ends, sequential
"""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from .trace import FrameTrace, MemAccess


@dataclass
class MemRegion:
    """A contiguous memory region with observed access pattern."""
    start: int
    end: int          # exclusive
    label: str = ''   # identified purpose
    access_count: int = 0
    frames_active: int = 0  # how many frames this region was read
    values: dict = field(default_factory=dict)  # addr → set of values read


@dataclass
class XRayResult:
    """Complete analysis of a player's data structures."""
    load_addr: int = 0
    binary_size: int = 0
    regions: list = field(default_factory=list)   # list of MemRegion
    addr_reads: dict = field(default_factory=dict)  # addr → total read count
    addr_frames: dict = field(default_factory=dict)  # addr → set of frame numbers
    addr_values: dict = field(default_factory=dict)  # addr → list of (frame, value)


def analyze_traces(frames, metadata=None):
    """Analyze frame traces to build an XRayResult.

    This is the core analysis: count reads per address, identify which
    addresses are read together, find sequential access patterns, etc.
    """
    result = XRayResult()
    if metadata:
        result.load_addr = metadata.get('load_addr', 0)

    # Aggregate: per-address stats
    for ft in frames:
        seen_this_frame = set()
        for r in ft.reads:
            if r.addr not in result.addr_reads:
                result.addr_reads[r.addr] = 0
                result.addr_frames[r.addr] = set()
                result.addr_values[r.addr] = []
            result.addr_reads[r.addr] += 1
            result.addr_frames[r.addr].add(ft.frame)
            result.addr_values[r.addr].append((ft.frame, r.value))
            seen_this_frame.add(r.addr)

    return result


def find_regions(result, min_reads=2):
    """Group addresses into contiguous regions.

    Returns list of MemRegion sorted by start address.
    """
    if not result.addr_reads:
        return []

    addrs = sorted(result.addr_reads.keys())
    regions = []
    region_start = addrs[0]
    prev = addrs[0]

    for a in addrs[1:]:
        if a > prev + 4:  # gap > 4 bytes = new region
            regions.append(MemRegion(
                start=region_start, end=prev + 1,
                access_count=sum(result.addr_reads.get(x, 0)
                                 for x in range(region_start, prev + 1)),
                frames_active=len(set().union(*(result.addr_frames.get(x, set())
                                                for x in range(region_start, prev + 1)))),
            ))
            region_start = a
        prev = a

    # Last region
    regions.append(MemRegion(
        start=region_start, end=prev + 1,
        access_count=sum(result.addr_reads.get(x, 0)
                         for x in range(region_start, prev + 1)),
        frames_active=len(set().union(*(result.addr_frames.get(x, set())
                                        for x in range(region_start, prev + 1)))),
    ))

    return [r for r in regions if r.access_count >= min_reads]


def classify_regions(regions, result, num_frames):
    """Attempt to classify each region by its access pattern.

    Heuristics:
    - Read every frame → wave/pulse/filter table or freq table
    - Read on some frames (note triggers) → instrument data or pattern data
    - Sequential stepping → table or pattern
    - Small region with high reads → variable/pointer area
    """
    for region in regions:
        size = region.end - region.start
        duty = region.frames_active / max(1, num_frames)  # fraction of frames active

        # Collect per-address read counts within region
        per_addr = {a: result.addr_reads.get(a, 0)
                    for a in range(region.start, region.end)}
        max_reads = max(per_addr.values()) if per_addr else 0
        avg_reads = sum(per_addr.values()) / max(1, len(per_addr))

        if size >= 90 and size <= 200 and duty > 0.3:
            # Large region read frequently — likely frequency table
            region.label = 'freq_table?'
        elif size <= 20 and max_reads > num_frames * 2:
            # Small region read many times — player variables
            region.label = 'variables'
        elif duty > 0.8 and avg_reads > num_frames * 0.5:
            # Read most frames — table being stepped (wave/pulse/filter)
            region.label = 'table_stepping'
        elif duty > 0.1 and duty < 0.5 and avg_reads < num_frames:
            # Read on some frames — instrument data or pattern
            region.label = 'instrument_or_pattern'
        elif size > 50 and duty > 0.3:
            # Medium+ region read often — orderlist or pattern data
            region.label = 'sequence_data'
        else:
            region.label = 'unknown'

    return regions


def identify_tables(result, frames):
    """Identify table-like access patterns: sequential reads that step through
    memory addresses frame by frame.

    Returns list of (base_addr, size, direction) for detected tables.
    """
    tables = []

    # For each address read on consecutive frames, check if the next frame
    # reads the next address (or next-N address for stride patterns)
    addr_by_frame = defaultdict(set)
    for ft in frames:
        for r in ft.reads:
            addr_by_frame[ft.frame].add(r.addr)

    # Find addresses that increment by 1 across consecutive frames
    # This indicates a table being stepped through
    frame_nums = sorted(addr_by_frame.keys())
    for i in range(len(frame_nums) - 1):
        f1 = frame_nums[i]
        f2 = frame_nums[i + 1]
        if f2 != f1 + 1:
            continue

        addrs1 = addr_by_frame[f1]
        addrs2 = addr_by_frame[f2]

        # Find addresses in f1 where addr+1 appears in f2
        for a in addrs1:
            if a + 1 in addrs2 and a + 1 not in addrs1:
                # Potential table step: a → a+1 across frames
                # Track how far this goes
                base = a
                pos = a
                frame = f1
                while frame in addr_by_frame and pos in addr_by_frame[frame]:
                    pos += 1
                    frame += 1
                length = pos - base
                if length >= 3:
                    tables.append((base, length))

    # Deduplicate overlapping tables
    tables.sort()
    merged = []
    for base, length in tables:
        if merged and base <= merged[-1][0] + merged[-1][1]:
            # Overlap — extend existing
            end = max(merged[-1][0] + merged[-1][1], base + length)
            merged[-1] = (merged[-1][0], end - merged[-1][0])
        else:
            merged.append((base, length))

    return merged
