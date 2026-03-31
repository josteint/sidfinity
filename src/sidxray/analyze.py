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
from math import sqrt
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


def autocorrelate(signal, max_lag=None):
    """Compute normalized autocorrelation of a binary signal.

    signal: list of 0/1 values (one per frame).
    Returns list of (lag, correlation) for lag 1..max_lag.
    Correlation is normalized to [-1, 1] where 1 = perfect periodicity.
    """
    n = len(signal)
    if max_lag is None:
        max_lag = min(n // 2, 200)

    mean = sum(signal) / n
    var = sum((s - mean) ** 2 for s in signal)
    if var == 0:
        return []

    result = []
    for lag in range(1, max_lag + 1):
        cov = sum((signal[i] - mean) * (signal[i + lag] - mean)
                  for i in range(n - lag))
        # Normalize
        corr = cov / var if var > 0 else 0
        result.append((lag, corr))

    return result


def find_periodicities(frames, result, max_lag=200):
    """Find periodic access patterns using autocorrelation.

    For each memory region, builds a per-frame binary signal (was this region
    read on this frame?) and autocorrelates it. Strong peaks indicate
    periodic behavior.

    Returns dict mapping region description to list of (period, strength).
    """
    num_frames = max(ft.frame for ft in frames) + 1 if frames else 0
    if num_frames < 20:
        return {}

    # Build per-address frame presence signals
    addr_signal = defaultdict(lambda: [0] * num_frames)
    for ft in frames:
        for r in ft.reads:
            if ft.frame < num_frames:
                addr_signal[r.addr][ft.frame] = 1

    # Group addresses into regions (reuse find_regions logic)
    regions = find_regions(result, min_reads=5)

    periodicities = {}
    for region in regions:
        # Build region-level signal: 1 if ANY address in region was read
        signal = [0] * num_frames
        for addr in range(region.start, region.end):
            if addr in addr_signal:
                for f in range(num_frames):
                    signal[f] |= addr_signal[addr][f]

        duty = sum(signal) / num_frames
        if duty < 0.02 or duty > 0.98:
            continue  # skip near-constant signals

        ac = autocorrelate(signal, max_lag)
        if not ac:
            continue

        # Find peaks: local maxima above threshold
        peaks = []
        threshold = 0.3
        for i in range(1, len(ac) - 1):
            lag, corr = ac[i]
            if corr > threshold:
                prev_corr = ac[i - 1][1]
                next_corr = ac[i + 1][1]
                if corr >= prev_corr and corr >= next_corr:
                    peaks.append((lag, corr))

        if peaks:
            label = f'${region.start:04X}-${region.end - 1:04X}'
            periodicities[label] = peaks

    # Also do autocorrelation on individual high-traffic addresses
    for addr in sorted(addr_signal.keys()):
        signal = addr_signal[addr]
        duty = sum(signal) / num_frames
        if duty < 0.05 or duty > 0.95:
            continue

        ac = autocorrelate(signal, max_lag)
        if not ac:
            continue

        peaks = []
        for i in range(1, len(ac) - 1):
            lag, corr = ac[i]
            if corr > 0.4:
                prev_corr = ac[i - 1][1]
                next_corr = ac[i + 1][1]
                if corr >= prev_corr and corr >= next_corr:
                    peaks.append((lag, corr))

        if peaks:
            label = f'${addr:04X}'
            if label not in periodicities:
                periodicities[label] = peaks

    return periodicities


def detect_tempo(frames, result, max_lag=100):
    """Detect player tempo by autocorrelating read activity patterns.

    The tempo = number of frames between consecutive tick processing.
    On tick frames, the player reads more data addresses (pattern bytes,
    instrument lookups) than on non-tick frames (just table stepping).

    We autocorrelate the "number of distinct addresses read per frame"
    signal — tick frames have spikes.

    Returns (tempo, confidence) or (0, 0) if not detected.
    """
    num_frames = max(ft.frame for ft in frames) + 1 if frames else 0
    if num_frames < 30:
        return 0, 0

    # Build signal: number of distinct addresses read per frame
    reads_per_frame = [0] * num_frames
    for ft in frames:
        if ft.frame < num_frames:
            reads_per_frame[ft.frame] = len(set(r.addr for r in ft.reads))

    # Convert to binary: above-median = 1, below = 0
    median = sorted(reads_per_frame)[num_frames // 2]
    if median == 0:
        return 0, 0
    signal = [1 if r > median else 0 for r in reads_per_frame]

    ac = autocorrelate(signal, max_lag)
    if not ac:
        return 0, 0

    # Find ALL peaks
    peaks = []
    for i in range(1, len(ac) - 1):
        lag, corr = ac[i]
        if corr > 0.15 and lag >= 2:
            prev_corr = ac[i - 1][1]
            next_corr = ac[i + 1][1]
            if corr >= prev_corr and corr >= next_corr:
                peaks.append((lag, corr))

    if not peaks:
        return 0, 0, []

    # The strongest peak is the note rhythm. The tempo divides it evenly.
    # Try small lags (2-10) — the tempo is typically in this range.
    # If a small lag has decent correlation AND divides a strong peak, it's the tempo.
    best_peak = max(peaks, key=lambda p: p[1])

    for lag, corr in sorted(peaks):
        if lag <= 10 and corr > 0.1:
            return lag, corr, peaks

    # Fallback: return the strongest peak
    return best_peak[0], best_peak[1], peaks
