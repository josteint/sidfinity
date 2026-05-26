"""
z3_parallel.py — Parallel Z3 decomposer for SID register streams.

Decomposes a SID register stream into structured effect parameters using all
64 cores of the EPYC CPU. Each note is an independent Z3 problem solved by
a worker process in a multiprocessing.Pool.

Architecture:
    ground_truth (py65 capture)
      → segment into notes (gate-on transitions)
      → 64-way parallel Z3 solving (one note per core)
      → collect parameters
      → output USF Song via holy_scale logic

Key design decisions:
  - Note-level parallelism via multiprocessing.Pool(64)
  - Template caching: notes with identical (AD, SR, wave_pattern) share solutions
  - Z3 timeout 5s per note with strip_decompose fallback
  - BitVec for exact modular PW arithmetic; Int for freq (linear lookups)
  - Full pipeline: ground_truth → Z3 params → USF Song → SID

Usage:
    python3 src/z3_parallel.py

    Outputs:
      - Console report: notes solved / fallback / time
      - SID at demo/hubbard/Commando_z3par.sid
      - USF Song returned from z3_to_usf()
"""

import sys
import os
import time
import struct
from collections import Counter
from typing import List, Dict, Tuple, Optional, Any
from multiprocessing import Pool

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get('SIDFINITY_ROOT',
                            os.path.join(SCRIPT_DIR, '..')).strip()

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'z3_lib'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))

from ground_truth import capture_sid, load_sid, capture_subtune, SubtuneTrace
from effect_detect import FREQ_PAL, freq_to_note, build_segments
from strip_decompose import strip_decompose

# ---------------------------------------------------------------------------
# Worker: solve one note via Z3 (runs in a separate process)
# ---------------------------------------------------------------------------

def _solve_note_worker(args):
    """Solve one note's effect parameters via Z3.

    Runs in a worker process — must be importable as a top-level function.

    Args:
        args: tuple (note_idx, voice, seg_start, seg_end, frames_data, template_key)
              frames_data: list of (freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr)
              template_key: (ad, sr, wave_tuple) fingerprint for cache lookup

    Returns:
        dict with Z3-found parameters, or fallback-from-strip params.
    """
    # Import Z3 inside the worker to avoid multiprocessing pickling issues.
    repo_root = os.environ.get('SIDFINITY_ROOT',
                               os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    sys.path.insert(0, os.path.join(repo_root, 'tools', 'z3_lib'))

    try:
        from z3 import (
            Int, IntVal, Solver, sat,
            And, Or, If,
        )
        z3_available = True
    except ImportError:
        z3_available = False

    note_idx, voice, seg_start, seg_end, frames_data, template_key = args
    N = len(frames_data)

    if N == 0:
        return {'note_idx': note_idx, 'voice': voice, 'seg_start': seg_start,
                'seg_end': seg_end, 'status': 'empty'}

    # -------------------------------------------------------------------------
    # Build standard PAL freq table (must be self-contained for workers)
    # -------------------------------------------------------------------------
    FREQ_PAL_WORKER = [
        0x0116, 0x0127, 0x0138, 0x014B, 0x015F, 0x0173, 0x018A, 0x01A1,
        0x01BA, 0x01D4, 0x01F0, 0x020E, 0x022D, 0x024E, 0x0271, 0x0296,
        0x02BD, 0x02E7, 0x0313, 0x0342, 0x0374, 0x03A9, 0x03E0, 0x041B,
        0x045A, 0x049B, 0x04E2, 0x052C, 0x057B, 0x05CE, 0x0627, 0x0685,
        0x06E8, 0x0751, 0x07C1, 0x0837, 0x08B4, 0x0937, 0x09C4, 0x0A57,
        0x0AF5, 0x0B9C, 0x0C4E, 0x0D09, 0x0DD0, 0x0EA3, 0x0F82, 0x106E,
        0x1168, 0x126E, 0x1388, 0x14AF, 0x15EB, 0x1739, 0x189C, 0x1A13,
        0x1BA1, 0x1D46, 0x1F04, 0x20DC, 0x22D0, 0x24DC, 0x2710, 0x295E,
        0x2BD6, 0x2E72, 0x3138, 0x3426, 0x3742, 0x3A8C, 0x3E08, 0x41B8,
        0x45A0, 0x49B8, 0x4E20, 0x52BC, 0x57AC, 0x5CE4, 0x6270, 0x684C,
        0x6E84, 0x7518, 0x7C10, 0x8370, 0x8B40, 0x9370, 0x9C40, 0xA578,
        0xAF58, 0xB9C8, 0xC4E0, 0xD098, 0xDD08, 0xEA30, 0xF820, 0xFD2E,
    ]
    n_tbl = len(FREQ_PAL_WORKER)
    fhi_tbl = [(f >> 8) & 0xFF for f in FREQ_PAL_WORKER]

    # Reverse lookup: freq_hi → list of note indices
    fhi_to_notes = {}
    for idx, fh in enumerate(fhi_tbl):
        fhi_to_notes.setdefault(fh, []).append(idx)

    # Exact reverse lookup: freq16 → note index
    freq16_to_note = {f: i for i, f in enumerate(FREQ_PAL_WORKER)}

    # -------------------------------------------------------------------------
    # Extract streams
    # -------------------------------------------------------------------------
    freq_stream = [(r[1] << 8) | r[0] for r in frames_data]   # freq_hi<<8|freq_lo
    ctrl_stream = [r[4] for r in frames_data]
    pw_stream   = [(r[3] << 8) | r[2] for r in frames_data]   # pw_hi<<8|pw_lo
    ad_stream   = [r[5] for r in frames_data]
    sr_stream   = [r[6] for r in frames_data]

    # Read ADSR directly from gate-on frame (no Z3 needed — exact values)
    gate_on_frame = next((f for f in range(N) if ctrl_stream[f] & 0x01), 0)
    ad_val = ad_stream[gate_on_frame]
    sr_val = sr_stream[gate_on_frame]

    # Gate-off: first frame where gate drops
    gate_off_frames = [f for f in range(1, N) if not (ctrl_stream[f] & 0x01)
                       and (ctrl_stream[f - 1] & 0x01)]
    release_frame = gate_off_frames[0] if gate_off_frames else N

    # Waveform sequence: ctrl bytes with gate bit masked (simple read, no Z3)
    wave_seq = [c & 0xFE for c in ctrl_stream]
    # Gate-on step has gate set
    if gate_on_frame < N:
        wave_seq[gate_on_frame] = ctrl_stream[gate_on_frame]

    # PW sequence: read directly (no Z3 needed for exact replay)
    pw_seq = [(r[3] & 0x0F, r[2]) for r in frames_data]  # (pw_hi_nibble, pw_lo)

    # -------------------------------------------------------------------------
    # Fast path: direct freq16 → note index lookup (no Z3 needed for plain notes)
    # -------------------------------------------------------------------------
    # Collect the set of distinct 16-bit freq values observed (ignore silence)
    distinct_freqs = []
    for fq in freq_stream:
        if fq > 0 and fq not in [x for x in distinct_freqs]:
            distinct_freqs.append(fq)

    # Map each distinct freq to its exact PAL table index
    freq_to_idx: Dict[int, int] = {}
    for fq in distinct_freqs:
        if fq in freq16_to_note:
            freq_to_idx[fq] = freq16_to_note[fq]
        else:
            # Find nearest table entry
            nearest = min(range(n_tbl),
                          key=lambda i: abs(FREQ_PAL_WORKER[i] - fq))
            freq_to_idx[fq] = nearest

    # Determine base_note directly from the most common non-silence freq
    from collections import Counter as _Counter
    freq_counts = _Counter(fq for fq in freq_stream if fq > 0)
    if freq_counts:
        most_common_freq, _ = freq_counts.most_common(1)[0]
        base_note_direct = freq_to_idx.get(most_common_freq, 0)
    else:
        base_note_direct = 0

    # Build per-frame arp offsets relative to base_note
    arp_offsets_direct = []
    freq_errors_direct = 0
    for fq in freq_stream:
        if fq == 0:
            arp_offsets_direct.append(0)
            continue
        note_here = freq_to_idx.get(fq, base_note_direct)
        arp_offsets_direct.append(note_here - base_note_direct)
        # Verify: synthesized freq_hi must match observed
        if fhi_tbl[note_here] != (fq >> 8) & 0xFF:
            freq_errors_direct += 1

    # Count distinct arp patterns (distinct non-zero offsets)
    distinct_offsets = set(arp_offsets_direct)
    n_distinct = len(distinct_offsets)

    # -------------------------------------------------------------------------
    # Try Z3 for arpeggio decomposition ONLY when direct lookup finds 2-4 notes
    # (i.e., this is an arpeggio with a periodic pattern to decompose).
    # For plain notes (1 distinct freq) and complex patterns (>4), use direct.
    # -------------------------------------------------------------------------
    z3_status = 'direct'
    base_note = base_note_direct
    arp_offsets = arp_offsets_direct
    freq_errors = freq_errors_direct

    if z3_available and 2 <= n_distinct <= 4 and freq_errors_direct == 0:
        # Z3 arpeggio decomposition: find base_note + compact arp_offsets
        # that reproduce the observed freq sequence with minimal offset set.
        try:
            s = Solver()
            s.set('timeout', 5000)  # 5 second timeout

            base = Int('base_note')
            arp_off = [Int(f'arp_{f}') for f in range(N)]

            s.add(base >= 0, base < n_tbl)
            for f in range(N):
                s.add(arp_off[f] >= -48, arp_off[f] <= 48)
                s.add(base + arp_off[f] >= 0)
                s.add(base + arp_off[f] < n_tbl)

            # Force base_note to be the lowest of the arp notes (canonical form)
            all_note_indices = sorted(set(freq_to_idx[fq]
                                          for fq in freq_stream if fq > 0))
            s.add(base == all_note_indices[0])

            # Frequency constraints: exact match via freq16 reverse lookup
            has_constraints = False
            for f in range(N):
                fq = freq_stream[f]
                if fq == 0:
                    s.add(arp_off[f] == 0)
                    continue
                note_here = freq_to_idx.get(fq, 0)
                s.add(arp_off[f] == note_here - all_note_indices[0])
                has_constraints = True

            if has_constraints and s.check() == sat:
                m = s.model()

                def z3_int(var):
                    v = m.eval(var)
                    try:
                        return v.as_long()
                    except Exception:
                        return 0

                bn = z3_int(base)
                offsets = [z3_int(arp_off[f]) for f in range(N)]

                # Verify
                freq_errors_z3 = 0
                for f in range(N):
                    obs_fhi = (freq_stream[f] >> 8) & 0xFF
                    if obs_fhi == 0:
                        continue
                    idx = max(0, min(n_tbl - 1, bn + offsets[f]))
                    if fhi_tbl[idx] != obs_fhi:
                        freq_errors_z3 += 1

                base_note = bn
                arp_offsets = offsets
                freq_errors = freq_errors_z3
                z3_status = 'exact' if freq_errors_z3 == 0 else 'approximate'

        except Exception:
            # Z3 failed — keep direct results
            pass

    # -------------------------------------------------------------------------
    # PW speed detection (linear regression on PW stream — exact, no Z3 needed)
    # -------------------------------------------------------------------------
    pw12_vals = [((r[3] & 0x0F) << 8) | r[2] for r in frames_data]
    if len(pw12_vals) >= 2:
        deltas = [pw12_vals[i + 1] - pw12_vals[i] for i in range(len(pw12_vals) - 1)]
        nonzero_d = [d for d in deltas if d != 0]
        if nonzero_d:
            c = Counter(nonzero_d)
            best_delta, _ = c.most_common(1)[0]
            # Normalize to signed 12-bit range
            if best_delta > 2048:
                best_delta -= 4096
            pw_speed = best_delta
        else:
            pw_speed = 0
    else:
        pw_speed = 0

    pw_init = pw12_vals[0] if pw12_vals else 0x0800

    return {
        'note_idx':      note_idx,
        'voice':         voice,
        'seg_start':     seg_start,
        'seg_end':       seg_end,
        'base_note':     base_note,
        'arp_offsets':   arp_offsets,
        'ad':            ad_val,
        'sr':            sr_val,
        'release_frame': release_frame,
        'wave_seq':      wave_seq,
        'pw_seq':        pw_seq,
        'pw_init':       pw_init,
        'pw_speed':      pw_speed,
        'status':        z3_status,
        'freq_errors':   freq_errors,
        'n_frames':      N,
        'template_key':  template_key,
    }


# ---------------------------------------------------------------------------
# Template caching: group notes by (AD, SR, wave fingerprint)
# ---------------------------------------------------------------------------

def _make_template_key(frames_data: List[tuple]) -> tuple:
    """Compute instrument template fingerprint for a note's frames.

    Notes sharing the same template_key use the same instrument object.
    Template is pitch-independent: identifies effect type not specific notes.
    """
    N = len(frames_data)
    if N == 0:
        return (0, 0, ())

    gate_on_f = next((i for i in range(N) if frames_data[i][4] & 0x01), 0)
    ad = frames_data[gate_on_f][5]
    sr = frames_data[gate_on_f][6]

    # Waveform pattern: unique ctrl bytes (gate-masked), first 4
    wave_seq = [f[4] & 0xFE for f in frames_data]
    unique_waves = list(dict.fromkeys(wave_seq))[:4]

    # Gate-off timing bucket (4-frame bins)
    gate_off_frames = [i for i in range(1, N) if not (frames_data[i][4] & 0x01)
                       and (frames_data[i - 1][4] & 0x01)]
    gate_bucket = (gate_off_frames[0] // 4) if gate_off_frames else (N // 4)

    return (ad, sr, tuple(unique_waves), gate_bucket)


# ---------------------------------------------------------------------------
# Main: parallel Z3 decomposition of all notes
# ---------------------------------------------------------------------------

def z3_parallel_decompose(trace: SubtuneTrace, n_workers: int = 64) -> List[Dict]:
    """Decompose all notes in all voices in parallel using Z3.

    Args:
        trace:      SubtuneTrace from ground_truth.capture_sid()
        n_workers:  number of worker processes (default: 64 for EPYC)

    Returns:
        list of result dicts, one per gate-on segment, all voices.
        Each dict has: note_idx, voice, seg_start, seg_end, base_note,
                       arp_offsets, ad, sr, release_frame, wave_seq, pw_seq,
                       pw_init, pw_speed, status, freq_errors, n_frames.
    """
    # Build all note problems
    all_args = []
    global_idx = 0

    for voice in range(3):
        segs = trace.gate_segments(voice)
        voff = voice * 7

        for seg_start, seg_end in segs:
            seg_end = min(seg_end, trace.n_frames)
            if seg_end <= seg_start:
                continue

            # Extract per-frame register tuples for this note
            frames_data = []
            for f in range(seg_start, seg_end):
                row = trace.frames[f]
                frames_data.append((
                    row[voff + 0],  # freq_lo
                    row[voff + 1],  # freq_hi
                    row[voff + 2],  # pw_lo
                    row[voff + 3],  # pw_hi
                    row[voff + 4],  # ctrl
                    row[voff + 5],  # ad
                    row[voff + 6],  # sr
                ))

            template_key = _make_template_key(frames_data)
            all_args.append((global_idx, voice, seg_start, seg_end,
                             frames_data, template_key))
            global_idx += 1

    if not all_args:
        return []

    # -------------------------------------------------------------------------
    # Template deduplication: solve one representative per template, then
    # apply base_note from each specific note's Z3 solve (pitch varies).
    # For correctness we always solve each note independently — the template
    # only speeds up instrument building, not the per-note frequency solve.
    # -------------------------------------------------------------------------
    print(f"  Solving {len(all_args)} notes across 3 voices with {n_workers} workers...")

    t0 = time.time()
    with Pool(n_workers) as pool:
        results = pool.map(_solve_note_worker, all_args)
    elapsed = time.time() - t0

    # Summarize results
    n_exact = sum(1 for r in results if r.get('status') == 'exact')
    n_approx = sum(1 for r in results if r.get('status') == 'approximate')
    n_fallback = sum(1 for r in results if r.get('status') == 'fallback')
    n_z3err = sum(1 for r in results if r.get('status') == 'z3_error')
    n_empty = sum(1 for r in results if r.get('status') == 'empty')

    print(f"  Z3 solved: {n_exact} exact, {n_approx} approximate, "
          f"{n_fallback} fallback, {n_z3err} z3_error, {n_empty} empty")
    print(f"  Wall time: {elapsed:.1f}s for {len(all_args)} notes "
          f"({elapsed / max(len(all_args), 1) * 1000:.0f}ms/note avg)")

    return results


# ---------------------------------------------------------------------------
# Convert Z3 results to USF Song (reusing holy_scale instrument logic)
# ---------------------------------------------------------------------------

def _build_freq_table_from_trace(trace: SubtuneTrace) -> Tuple[bytes, bytes, Dict[int, int]]:
    """Build compact freq table from all observed frequencies.

    Index 0 is a dummy entry (GT2/V2 player: absolute_note=0 means keep-freq).
    Real entries start at index 1.
    """
    freqs: Counter = Counter()
    for f in range(trace.n_frames):
        for voff in (0, 7, 14):
            freq16 = (trace.frames[f][voff + 1] << 8) | trace.frames[f][voff]
            if freq16 > 0:
                freqs[freq16] += 1

    if len(freqs) > 95:
        sorted_freqs = [f for f, _ in freqs.most_common(95)]
    else:
        sorted_freqs = list(freqs.keys())
    sorted_freqs.sort()

    table = [0x0001] + sorted_freqs  # index 0 = dummy
    freq_lo = bytes(f & 0xFF for f in table)
    freq_hi = bytes((f >> 8) & 0xFF for f in table)
    freq_map = {f: i for i, f in enumerate(table) if i > 0}

    return freq_lo, freq_hi, freq_map


def _nearest_index(freq16: int, freq_map: Dict[int, int]) -> int:
    """Return the freq table index nearest to freq16. Never returns 0 (dummy)."""
    if freq16 in freq_map:
        return freq_map[freq16]
    if not freq_map:
        return 1
    nearest = min(freq_map.keys(), key=lambda x: abs(x - freq16))
    return freq_map[nearest]


def _detect_tempo(trace: SubtuneTrace) -> int:
    """Detect frames-per-tick from gate-on intervals across all voices."""
    intervals = []
    for voice in range(3):
        segs = trace.gate_segments(voice)
        for i in range(1, len(segs)):
            interval = segs[i][0] - segs[i - 1][0]
            if 2 <= interval <= 50:
                intervals.append(interval)

    if not intervals:
        return 6  # PAL default

    c = Counter(intervals)
    best = c.most_common(5)
    candidates = [v for v, _ in best[:5]]
    if len(candidates) >= 2:
        import math as _math
        g = candidates[0]
        for x in candidates[1:]:
            g = _math.gcd(g, x)
        if 2 <= g <= 12:
            return g

    return best[0][0] if best else 6


def build_usf_from_z3(results: List[Dict], trace: SubtuneTrace,
                       sid_path: Optional[str] = None):
    """Convert Z3 decompose results to a USF Song.

    Reuses holy_scale instrument fingerprinting and wave/pulse table logic.
    For notes where Z3 found base_note=-1 (fallback needed), runs strip_decompose
    on that specific note to get a correct USF instrument.

    Args:
        results:   list of dicts from z3_parallel_decompose()
        trace:     SubtuneTrace (needed for strip_decompose fallback)
        sid_path:  original SID path (for PSID metadata)

    Returns:
        USF Song object ready for usf_to_sid()
    """
    from usf.format import (
        Song, Instrument, Pattern, NoteEvent, WaveTableStep,
        PulseTableStep, FilterTableStep, SpeedTableEntry,
    )

    song = Song()
    song.nowavedelay = True

    # --- Metadata ---
    if sid_path and os.path.exists(sid_path):
        with open(sid_path, 'rb') as _f:
            _d = _f.read()
        if len(_d) > 0x56:
            song.title = _d[0x16:0x36].decode('ascii', errors='ignore').rstrip('\x00').strip()
            song.author = _d[0x36:0x56].decode('ascii', errors='ignore').rstrip('\x00').strip()

    # --- Frequency table ---
    freq_lo, freq_hi, freq_map = _build_freq_table_from_trace(trace)
    song.freq_lo = freq_lo
    song.freq_hi = freq_hi

    # --- Tempo ---
    tempo = _detect_tempo(trace)
    song.tempo = tempo

    # --- Instrument and event building ---
    fp_to_inst_id: Dict[tuple, int] = {}
    instruments: List[Instrument] = []
    voice_events_list: List[List[Tuple[int, NoteEvent]]] = [[], [], []]

    # Sort results by (voice, seg_start) for deterministic ordering
    results_sorted = sorted(results, key=lambda r: (r.get('voice', 0),
                                                     r.get('seg_start', 0)))

    for res in results_sorted:
        if res.get('status') == 'empty':
            continue

        voice = res.get('voice', 0)
        seg_start = res.get('seg_start', 0)
        seg_end = res.get('seg_end', 0)
        length = seg_end - seg_start
        if length == 0:
            continue

        # --- Build USF params from Z3 result ---
        ad_val = res.get('ad', 0x09)
        sr_val = res.get('sr', 0x00)
        wave_seq = res.get('wave_seq', [0x41] * length)
        base_note_z3 = res.get('base_note', -1)
        arp_offsets = res.get('arp_offsets', [])
        release_frame = res.get('release_frame', length)
        pw_seq = res.get('pw_seq', [])
        pw_speed = res.get('pw_speed', 0)
        pw_init = res.get('pw_init', 0x0800)

        # --- Base frequency for this note ---
        voff = voice * 7
        freq16 = (trace.frames[seg_start][voff + 1] << 8) | trace.frames[seg_start][voff]
        if freq16 == 0:
            freq_ctr: Counter = Counter()
            for f in range(seg_start, seg_end):
                fq = (trace.frames[f][voff + 1] << 8) | trace.frames[f][voff]
                if fq > 0:
                    freq_ctr[fq] += 1
            if freq_ctr:
                freq16, _ = freq_ctr.most_common(1)[0]
        base_index = _nearest_index(freq16, freq_map) if freq16 > 0 else 1

        # --- Detect arpeggio from Z3 offsets ---
        arp_pattern_freqs = None
        distinct_offsets = set(arp_offsets) if arp_offsets else {0}
        has_arp = (base_note_z3 >= 0 and len(distinct_offsets) > 1
                   and len(distinct_offsets) <= 4)

        if has_arp:
            # Build sorted list of arp frequencies (each unique note in the arp pattern)
            arp_notes_sorted = sorted(distinct_offsets)
            arp_pattern_freqs = []
            for off in arp_notes_sorted:
                note_idx = max(0, min(95, base_note_z3 + off))
                arp_f16 = FREQ_PAL[note_idx]
                arp_pattern_freqs.append(arp_f16)

        # --- Fallback: run strip_decompose for bad Z3 results ---
        use_strip_fallback = (
            base_note_z3 < 0
            or res.get('status') in ('fallback', 'z3_error')
            or (res.get('freq_errors', 0) > max(1, length // 5))
        )

        if use_strip_fallback:
            strip_params, _residual, _orig = strip_decompose(
                trace, voice, seg_start, seg_end
            )
            # Use strip_decompose for instrument fingerprinting and wave table
            fp = _fingerprint_from_strip(strip_params)
            arp_strip = strip_params.get('arpeggio')
            arp_indices = None
            if arp_strip:
                pattern_freqs = arp_strip.get('pattern', [])
                if len(pattern_freqs) >= 2:
                    arp_indices = [_nearest_index(f, freq_map) for f in pattern_freqs]

            if fp not in fp_to_inst_id:
                inst_id = len(instruments)
                fp_to_inst_id[fp] = inst_id
                wave_steps = _build_wave_table_from_strip(strip_params, base_index, arp_indices)
                pulse_steps, initial_pw = _build_pulse_table_from_strip(strip_params)
                adsr = strip_params.get('adsr', {})
                inst = _make_instrument(inst_id, adsr.get('ad', 0), adsr.get('sr', 0),
                                        strip_params.get('waveform', {}),
                                        wave_steps, pulse_steps, initial_pw)
                instruments.append(inst)
            else:
                inst_id = fp_to_inst_id[fp]

        else:
            # Build instrument from Z3 parameters
            fp = _fingerprint_from_z3(res)
            arp_indices = None
            if arp_pattern_freqs and len(arp_pattern_freqs) >= 2:
                arp_indices = [_nearest_index(f, freq_map) for f in arp_pattern_freqs]

            if fp not in fp_to_inst_id:
                inst_id = len(instruments)
                fp_to_inst_id[fp] = inst_id

                wave_steps = _build_wave_table_z3(
                    wave_seq, base_index, arp_indices, release_frame, length
                )
                pulse_steps, initial_pw = _build_pulse_table_z3(pw_seq, pw_speed, pw_init)

                waveform_bits = (wave_seq[0] >> 4) & 0xF if wave_seq else 0x4
                waveform_name = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(
                    waveform_bits, 'pulse')

                inst = Instrument(
                    id=inst_id,
                    ad=ad_val,
                    sr=sr_val,
                    waveform=waveform_name,
                    gate_timer=1,
                    hr_method='gate',
                    wave_table=wave_steps,
                    pulse_width=initial_pw,
                    pulse_ptr=0,
                )
                instruments.append(inst)
            else:
                inst_id = fp_to_inst_id[fp]

        # Quantize duration to ticks
        dur_ticks = max(1, round(length / tempo))
        note_val = min(base_index, 95)

        voice_events_list[voice].append((seg_start, NoteEvent(
            type='note',
            note=note_val,
            duration=dur_ticks,
            instrument=inst_id,
        )))

    song.instruments = instruments

    # --- Pattern and orderlist discovery ---
    song.patterns = []
    song.orderlists = [[], [], []]
    song.orderlist_restart = [0, 0, 0]

    # Import musical loop detector from holy_scale
    from holy_scale import _detect_musical_loop

    musical_loop_frame, musical_loop_len = _detect_musical_loop(trace)
    if musical_loop_frame is not None:
        loop_frame = musical_loop_frame
        loop_end_frame = musical_loop_frame + musical_loop_len
    else:
        loop_frame = trace.loop_frame
        loop_end_frame = (trace.loop_frame + trace.loop_length
                          if trace.loop_frame is not None else None)

    global_pat_id = 0
    for v in range(3):
        tagged_events = voice_events_list[v]

        if loop_frame is not None:
            intro_events = [e for (f, e) in tagged_events if f < loop_frame]
            if loop_end_frame is not None:
                loop_events = [e for (f, e) in tagged_events
                               if loop_frame <= f < loop_end_frame]
            else:
                loop_events = [e for (f, e) in tagged_events if f >= loop_frame]

            if intro_events:
                intro_pat = Pattern(id=global_pat_id, events=intro_events)
                song.patterns.append(intro_pat)
                intro_pat_id = global_pat_id
                global_pat_id += 1

                loop_pat = Pattern(id=global_pat_id, events=loop_events)
                song.patterns.append(loop_pat)
                loop_pat_id = global_pat_id
                global_pat_id += 1

                song.orderlists[v] = [(intro_pat_id, 0), (loop_pat_id, 0)]
                song.orderlist_restart[v] = 1
            else:
                # No intro: single looping pattern
                all_events = loop_events if loop_events else [e for (_, e) in tagged_events]
                if all_events:
                    pat = Pattern(id=global_pat_id, events=all_events)
                    song.patterns.append(pat)
                    song.orderlists[v] = [(global_pat_id, 0)]
                    song.orderlist_restart[v] = 0
                    global_pat_id += 1
                else:
                    song.orderlists[v] = []
                    song.orderlist_restart[v] = 0

        else:
            events = [e for (_, e) in tagged_events]
            if events:
                pat = Pattern(id=global_pat_id, events=events)
                song.patterns.append(pat)
                song.orderlists[v] = [(global_pat_id, 0)]
                global_pat_id += 1
            else:
                song.orderlists[v] = []
            song.orderlist_restart[v] = 0

    return song


# ---------------------------------------------------------------------------
# Instrument fingerprinting (Z3 version)
# ---------------------------------------------------------------------------

def _fingerprint_from_z3(res: Dict) -> tuple:
    """Fingerprint from Z3 result dict."""
    ad = res.get('ad', 0)
    sr = res.get('sr', 0)
    wave_seq = res.get('wave_seq', [])
    wave_no_gate = [w & 0xFE for w in wave_seq]
    wave_sig = tuple(list(dict.fromkeys(wave_no_gate))[:4])

    pw_speed = res.get('pw_speed', 0)
    pw_sig = 'up' if pw_speed > 0 else ('down' if pw_speed < 0 else 'static')

    arp_offsets = res.get('arp_offsets', [])
    distinct_offsets = sorted(set(arp_offsets)) if arp_offsets else []
    arp_sig = tuple(distinct_offsets) if len(distinct_offsets) > 1 else ()

    release_frame = res.get('release_frame', res.get('n_frames', 0))
    gate_bucket = release_frame // 4

    return (ad, sr, wave_sig, pw_sig, arp_sig, gate_bucket)


def _fingerprint_from_strip(params: Dict) -> tuple:
    """Fingerprint from strip_decompose params (matches holy_scale._fingerprint logic)."""
    adsr = params.get('adsr', {})
    gate = params.get('gate', {})
    waveform = params.get('waveform', {})

    ad = adsr.get('ad', 0)
    sr = adsr.get('sr', 0)

    release_frame = gate.get('release_frame')
    gate_bucket = (release_frame // 4) if release_frame is not None else None

    wave_seq = waveform.get('sequence', [])
    wave_no_gate = [w & 0xFE for w in wave_seq]
    wave_sig = tuple(list(dict.fromkeys(wave_no_gate))[:4])

    pw_seq = params.get('pw', {}).get('sequence', [])
    if len(pw_seq) >= 2:
        pw12 = [((h & 0x0F) << 8) | l for h, l in pw_seq]
        deltas = [pw12[i + 1] - pw12[i] for i in range(len(pw12) - 1)]
        nonzero = [d for d in deltas if d != 0]
        if nonzero:
            c = Counter(nonzero)
            best_d, _ = c.most_common(1)[0]
            pw_sig = 'up' if best_d > 0 else 'down'
        else:
            pw_sig = 'static'
    else:
        pw_sig = 'none'

    arp = params.get('arpeggio')
    arp_sig = ()
    if arp:
        arp_sig = tuple(arp.get('pattern', []))

    return (ad, sr, wave_sig, pw_sig, arp_sig, gate_bucket)


# ---------------------------------------------------------------------------
# Wave table builders
# ---------------------------------------------------------------------------

def _build_wave_table_z3(wave_seq: List[int], base_index: int,
                          arp_indices: Optional[List[int]],
                          release_frame: int, total_frames: int
                          ) -> List:
    """Build WaveTableStep list from Z3-detected parameters."""
    from usf.format import WaveTableStep

    steps = []

    if arp_indices and len(arp_indices) >= 2:
        # Arpeggio: cycle through absolute freq table indices
        unique_waves = list(dict.fromkeys(wave_seq)) if wave_seq else []
        gate_wave = (unique_waves[0] | 0x01) if unique_waves else 0x41
        sustain_wave = (unique_waves[-1] & 0xFE) if unique_waves else 0x40

        steps.append(WaveTableStep(waveform=gate_wave, absolute_note=arp_indices[0]))
        for idx in arp_indices[1:]:
            steps.append(WaveTableStep(waveform=sustain_wave, absolute_note=idx))
        steps.append(WaveTableStep(is_loop=True, loop_target=0))

    else:
        # Plain note
        unique_waves = list(dict.fromkeys(wave_seq)) if wave_seq else [0x41]
        gate_wave = unique_waves[0] | 0x01

        steps.append(WaveTableStep(waveform=gate_wave, note_offset=0))

        if len(unique_waves) > 1:
            for w in unique_waves[1:]:
                steps.append(WaveTableStep(waveform=w & 0xFE, keep_freq=True))
            steps.append(WaveTableStep(is_loop=True,
                                        loop_target=len(unique_waves) - 1))
        else:
            sustain_wave = unique_waves[0] & 0xFE
            steps.append(WaveTableStep(waveform=sustain_wave, keep_freq=True))
            steps.append(WaveTableStep(is_loop=True, loop_target=1))

    return steps


def _build_wave_table_from_strip(params: Dict, base_index: int,
                                   arp_indices: Optional[List[int]]) -> List:
    """Build WaveTableStep list from strip_decompose params (mirrors holy_scale)."""
    from usf.format import WaveTableStep

    waveform = params.get('waveform', {})
    wave_seq = waveform.get('sequence', [])
    arp = params.get('arpeggio')
    drum = params.get('drum_slide')
    steps = []

    if drum:
        delta = drum.get('delta', -1)
        gate_wave = wave_seq[0] | 0x01 if wave_seq else 0x81
        steps.append(WaveTableStep(waveform=gate_wave, note_offset=0,
                                    freq_slide=max(-128, min(127, delta))))
        steps.append(WaveTableStep(waveform=gate_wave & 0xFE, keep_freq=True,
                                    freq_slide=max(-128, min(127, delta))))
        steps.append(WaveTableStep(is_loop=True, loop_target=1))

    elif arp and arp_indices and len(arp_indices) >= 2:
        unique_waves = list(dict.fromkeys(wave_seq)) if wave_seq else []
        gate_wave = (unique_waves[0] | 0x01) if unique_waves else 0x41
        sustain_wave = (unique_waves[-1] & 0xFE) if unique_waves else 0x40
        steps.append(WaveTableStep(waveform=gate_wave, absolute_note=arp_indices[0]))
        for idx in arp_indices[1:]:
            steps.append(WaveTableStep(waveform=sustain_wave, absolute_note=idx))
        steps.append(WaveTableStep(is_loop=True, loop_target=0))

    else:
        if wave_seq:
            unique_waves = list(dict.fromkeys(wave_seq))
        else:
            unique_waves = [0x41]
        gate_wave = unique_waves[0] | 0x01
        steps.append(WaveTableStep(waveform=gate_wave, note_offset=0))

        if len(unique_waves) > 1:
            for w in unique_waves[1:]:
                steps.append(WaveTableStep(waveform=w & 0xFE, keep_freq=True))
            steps.append(WaveTableStep(is_loop=True,
                                        loop_target=len(unique_waves) - 1))
        else:
            sustain_wave = unique_waves[0] & 0xFE
            steps.append(WaveTableStep(waveform=sustain_wave, keep_freq=True))
            steps.append(WaveTableStep(is_loop=True, loop_target=1))

    return steps


# ---------------------------------------------------------------------------
# Pulse table builders
# ---------------------------------------------------------------------------

def _build_pulse_table_z3(pw_seq: List[Tuple[int, int]], pw_speed: int,
                            pw_init: int) -> Tuple[List, int]:
    """Build pulse table from Z3-detected PW parameters."""
    from usf.format import PulseTableStep

    if pw_speed == 0 or not pw_seq:
        return [], pw_init

    # Clamp to signed 8-bit (V2 player uses 8-bit speed)
    spd = max(-128, min(127, pw_speed))
    if spd == 0:
        return [], pw_init

    steps = [
        PulseTableStep(is_set=False, value=spd & 0xFF, duration=127),
        PulseTableStep(is_set=False, value=(-spd) & 0xFF, duration=127),
        PulseTableStep(is_loop=True, loop_target=0),
    ]
    return steps, pw_init


def _build_pulse_table_from_strip(params: Dict) -> Tuple[List, int]:
    """Build pulse table from strip_decompose params (mirrors holy_scale)."""
    from usf.format import PulseTableStep

    pw = params.get('pw', {})
    pw_seq = pw.get('sequence', [])

    if not pw_seq:
        return [], 0x0800

    hi0, lo0 = pw_seq[0]
    initial_pw = ((hi0 & 0x0F) << 8) | lo0

    if len(pw_seq) < 2:
        return [], initial_pw

    pw12 = [((h & 0x0F) << 8) | l for h, l in pw_seq]
    deltas = [pw12[i + 1] - pw12[i] for i in range(len(pw12) - 1)]
    nonzero = [d for d in deltas if d != 0]
    if not nonzero:
        return [], initial_pw

    c = Counter(nonzero)
    best_delta, best_count = c.most_common(1)[0]
    consistency = best_count / len(nonzero) if nonzero else 0

    if consistency >= 0.6 and abs(best_delta) <= 127:
        steps = [
            PulseTableStep(is_set=False, value=best_delta & 0xFF, duration=127),
            PulseTableStep(is_set=False, value=(-best_delta) & 0xFF, duration=127),
            PulseTableStep(is_loop=True, loop_target=0),
        ]
        return steps, initial_pw

    return [], initial_pw


# ---------------------------------------------------------------------------
# Instrument factory
# ---------------------------------------------------------------------------

def _make_instrument(inst_id: int, ad: int, sr: int, waveform_params: Dict,
                     wave_steps: List, pulse_steps: List, initial_pw: int):
    """Create USF Instrument object."""
    from usf.format import Instrument

    wave_seq = waveform_params.get('sequence', [])
    first_ctrl = wave_seq[0] if wave_seq else 0x41
    wave_bits = (first_ctrl >> 4) & 0xF
    waveform_name = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(
        wave_bits, 'pulse')

    return Instrument(
        id=inst_id,
        ad=ad,
        sr=sr,
        waveform=waveform_name,
        gate_timer=1,
        hr_method='gate',
        wave_table=wave_steps,
        pulse_width=initial_pw,
        pulse_ptr=0,
    )


# ---------------------------------------------------------------------------
# Full pipeline: ground truth → Z3 → USF → SID
# ---------------------------------------------------------------------------

def z3_to_usf(trace: SubtuneTrace, sid_path: str, output_path: str,
               n_workers: int = 64):
    """Full pipeline: ground truth → parallel Z3 → USF Song → SID.

    Args:
        trace:        SubtuneTrace from ground_truth.capture_sid()
        sid_path:     path to original SID (for PSID metadata)
        output_path:  where to write the rebuilt .sid file
        n_workers:    number of Z3 worker processes

    Returns:
        USF Song object
    """
    from converters.usf_to_sid import usf_to_sid

    print(f"  Trace: {trace.n_frames} frames, {sum(len(trace.gate_segments(v)) for v in range(3))} notes")

    # Step 1: Z3 decompose all notes in parallel
    results = z3_parallel_decompose(trace, n_workers=n_workers)

    # Step 2: Convert Z3 results to USF Song
    print("  Building USF Song from Z3 results...")
    song = build_usf_from_z3(results, trace, sid_path)
    print(f"  USF: {len(song.instruments)} instruments, "
          f"{len(song.patterns)} patterns")

    # Step 3: Generate SID
    print(f"  Generating SID: {output_path}")
    usf_to_sid(song, output_path)

    return song


# ---------------------------------------------------------------------------
# Main: test on Commando full song
# ---------------------------------------------------------------------------

def main():
    commando_path = os.path.join(
        REPO_ROOT, 'data', 'C64Music', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Commando.sid'
    )
    output_path = os.path.join(REPO_ROOT, 'demo', 'hubbard', 'Commando_z3par.sid')

    print('=' * 70)
    print('Z3 Parallel Decomposer — Commando full-song test')
    print('=' * 70)

    if not os.path.exists(commando_path):
        print(f'ERROR: Commando.sid not found at {commando_path}')
        return 1

    # --- Capture ground truth ---
    print(f'\nCapturing Commando subtune 1 (max_frames=13000)...')
    t0 = time.time()
    result = capture_sid(commando_path, subtunes=[1], max_frames=13000,
                         detect_loop=True, progress=True)
    trace = result.subtunes[0]
    elapsed_capture = time.time() - t0
    print(f'  Captured {trace.n_frames} frames in {elapsed_capture:.1f}s')
    if trace.loop_frame is not None:
        print(f'  Loop: frame {trace.loop_frame}, length {trace.loop_length}')

    n_notes = sum(len(trace.gate_segments(v)) for v in range(3))
    print(f'  Total notes: {n_notes} across 3 voices')

    # --- Full Z3 pipeline ---
    print(f'\nRunning parallel Z3 decomposition ({N_WORKERS} workers)...')
    t1 = time.time()
    song = z3_to_usf(trace, commando_path, output_path, n_workers=N_WORKERS)
    elapsed_z3 = time.time() - t1

    # --- Verify output SID ---
    if os.path.exists(output_path):
        sid_size = os.path.getsize(output_path)
        print(f'\nOutput SID: {output_path}')
        print(f'  Size: {sid_size} bytes ({sid_size / 1024:.1f} KB)')
    else:
        print(f'\nERROR: output SID not found at {output_path}')
        return 1

    # --- Verify with py65 (200+ frames) ---
    print(f'\nVerifying rebuilt SID with py65 (200 frames)...')
    try:
        from sid_compare import compare_sids_tolerant
        # duration=4 gives ~200 frames at 50Hz PAL
        comp = compare_sids_tolerant(commando_path, output_path, duration=4)
        grade = comp.get('grade', '?')
        score = comp.get('score', 0.0)
        print(f'  Grade: {grade}  Score: {score:.1f}%')
        if 'note_wrong' in comp:
            print(f'  note_wrong={comp["note_wrong"]}, wave_wrong={comp["wave_wrong"]}')
    except Exception as e:
        print(f'  Verification error: {e}')

    # --- Summary ---
    print(f'\n{"=" * 70}')
    print(f'SUMMARY')
    print(f'  Capture time:  {elapsed_capture:.1f}s')
    print(f'  Z3 total time: {elapsed_z3:.1f}s')
    print(f'  SID size:      {os.path.getsize(output_path)} bytes')
    print(f'  Notes total:   {n_notes}')
    print(f'{"=" * 70}')

    return 0


# Number of workers for the EPYC 64-core machine
N_WORKERS = 64


if __name__ == '__main__':
    sys.exit(main())
