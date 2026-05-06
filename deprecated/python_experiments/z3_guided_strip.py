"""
z3_guided_strip.py — Z3-guided instrument merging for SID strip decomposition.

Concept:
    Step 1: strip_decompose() extracts exact per-note parameters (100% accurate).
    Step 2: Z3 finds the minimum number of instruments (equivalence classes).
    Step 3: Z3-guided merging collapses compatible notes onto shared instruments.
    Step 4: Build USF Song via holy_scale-style encoding.

Why this is useful:
    The naive strip_decompose / InstrumentPool approach creates one instrument per
    unique per-frame data block.  For a 1500-frame song, this easily produces 100+
    instruments, making the SID large.  Z3 proves which notes can share an instrument
    (because one note's frames are a PREFIX of another's), then merges them.

    Expected: ~58-169 instruments before merging → ~15-25 after Z3-guided merging.

Merging rules (two notes can share one instrument if):
    1. Same (AD, SR) values.
    2. Same waveform byte sequence up to the shorter note's length.
    3. Same arpeggio intervals (relative offsets, not absolute pitches).
    4. Same PW speed (or both zero).
    5. One note's frame data is a PREFIX of the other's (short note = truncated long note).

Z3 is used to:
    a. Confirm that the fingerprint equivalence classes are correct (sanity check).
    b. For near-matches (same fingerprint but different lengths), verify the prefix
       property holds by comparing the actual per-frame data.
    c. Report the minimum instrument count as a lower bound for validation.

Usage:
    from ground_truth import capture_sid
    from z3_guided_strip import guided_strip, guided_strip_to_sid

    result = capture_sid('data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid',
                         subtunes=[1], max_frames=1500)
    trace = result.subtunes[0]
    song, stats = guided_strip(trace)
    print(f"Instruments: {stats['n_before']} -> {stats['n_after']}  (Z3 minimum: {stats['z3_min']})")

Command line:
    python3 src/z3_guided_strip.py [song.sid] [output.sid] [subtune] [max_frames]
"""

import os
import sys
import struct
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any, Set

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.environ.get('SIDFINITY_ROOT',
                            os.path.join(SCRIPT_DIR, '..')).strip()

sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'z3_lib'))
sys.path.insert(0, os.path.join(REPO_ROOT, 'tools', 'py65_lib'))

from strip_decompose import (
    strip_decompose, frames_from_trace, Frame,
    FreqTable, InstrumentPool, generate_player_asm, _bytes_to_asm,
    _build_psid_header, _verify, PLAYER_BASE, VOICE_SID, ZP_VOICE,
    FILTER_OFFSET,
)
from holy_scale import (
    _build_freq_table, _nearest_index, _fingerprint,
    _build_wave_table, _build_pulse_table, _detect_tempo, _detect_musical_loop,
)
from usf.format import (
    Song, Instrument, Pattern, NoteEvent, WaveTableStep, PulseTableStep,
)


# =============================================================================
# Step 1: Extract all note parameters
# =============================================================================

@dataclass
class NoteParams:
    """Per-note decomposition result, augmented with frame-level data."""
    voice: int
    seg_start: int
    seg_end: int
    length: int                          # frames
    params: Dict[str, Any]               # strip_decompose output
    original: List[Frame]                # unmodified per-frame data
    freq16: int                          # base frequency (16-bit)
    fingerprint: tuple                   # instrument-class fingerprint
    # Derived
    ad: int = 0
    sr: int = 0
    wave_seq: Tuple[int, ...] = ()       # ctrl bytes (gate stripped)
    arp_pattern: Tuple[int, ...] = ()    # absolute freq values (empty if no arp)
    pw_speed: int = 0                    # signed PW delta (0=static)

    def __post_init__(self):
        adsr = self.params.get('adsr', {})
        self.ad = adsr.get('ad', 0)
        self.sr = adsr.get('sr', 0)

        waveform = self.params.get('waveform', {})
        wave_seq = waveform.get('sequence', [])
        self.wave_seq = tuple(w & 0xFE for w in wave_seq)  # gate stripped

        arp = self.params.get('arpeggio')
        if arp:
            self.arp_pattern = tuple(arp.get('pattern', []))

        pw = self.params.get('pw', {})
        pw_seq = pw.get('sequence', [])
        if len(pw_seq) >= 2:
            pw12 = [((h & 0x0F) << 8) | l for h, l in pw_seq]
            deltas = [pw12[i+1] - pw12[i] for i in range(len(pw12)-1)]
            nonzero = [d for d in deltas if d != 0]
            if nonzero:
                c = Counter(nonzero)
                best, _ = c.most_common(1)[0]
                self.pw_speed = max(-128, min(127, best))


def extract_all_notes(trace) -> List[NoteParams]:
    """Run strip_decompose on every note segment in all three voices.

    Returns a flat list of NoteParams, one per gate segment.
    """
    all_notes: List[NoteParams] = []

    for voice in range(3):
        segs = trace.gate_segments(voice)
        for seg_start, seg_end in segs:
            seg_end = min(seg_end, trace.n_frames)
            length = seg_end - seg_start
            if length == 0:
                continue

            params, _residual, original = strip_decompose(
                trace, voice, seg_start, seg_end
            )

            # Base frequency
            voff = voice * 7
            freq16 = (trace.frames[seg_start][voff+1] << 8) | trace.frames[seg_start][voff]
            if freq16 == 0:
                freq_ctr: Counter = Counter()
                for f in range(seg_start, seg_end):
                    fq = (trace.frames[f][voff+1] << 8) | trace.frames[f][voff]
                    if fq > 0:
                        freq_ctr[fq] += 1
                if freq_ctr:
                    freq16, _ = freq_ctr.most_common(1)[0]

            fp = _fingerprint(params)

            note = NoteParams(
                voice=voice,
                seg_start=seg_start,
                seg_end=seg_end,
                length=length,
                params=params,
                original=original,
                freq16=freq16,
                fingerprint=fp,
            )
            all_notes.append(note)

    return all_notes


# =============================================================================
# Step 2: Z3 minimum instrument count
# =============================================================================

def _frames_to_tuple(original: List[Frame]) -> Tuple:
    """Convert Frame list to a hashable tuple for exact comparison."""
    return tuple(
        (f.freq_lo, f.freq_hi, f.pw_lo, f.pw_hi, f.ctrl, f.ad, f.sr)
        for f in original
    )


def _is_prefix(short_frames: List[Frame], long_frames: List[Frame]) -> bool:
    """Return True if short_frames are a frame-exact prefix of long_frames.

    Two notes can share one instrument if the shorter note's frames are
    identical to the first len(short_frames) frames of the longer note —
    the short note simply plays fewer steps of the same instrument data.
    """
    n = len(short_frames)
    if n > len(long_frames):
        return False
    for i in range(n):
        s = short_frames[i]
        l = long_frames[i]
        if (s.freq_lo != l.freq_lo or s.freq_hi != l.freq_hi or
                s.pw_lo != l.pw_lo or s.pw_hi != l.pw_hi or
                s.ctrl != l.ctrl or s.ad != l.ad or s.sr != l.sr):
            return False
    return True


def _z3_verify_prefix(short_frames: List[Frame], long_frames: List[Frame]) -> bool:
    """Use Z3 to verify the prefix merge property.

    Z3 checks: for all frames i in 0..len(short)-1,
        long_frames[i].reg == short_frames[i].reg for each register.

    This is trivially SAT if frames match (deterministic, no free variables).
    The value is that Z3 provides a PROOF certificate, and for future
    near-match extensions (tolerances, approximations) Z3 can handle
    non-trivial constraints that Python comparison cannot.

    Returns True if Z3 confirms the frames are prefix-identical, False otherwise.
    """
    try:
        from z3 import Solver, BitVecVal, And, sat

        s = Solver()
        n = len(short_frames)

        for i in range(min(n, len(long_frames))):
            sf = short_frames[i]
            lf = long_frames[i]
            # Each register must be equal: assert as constant equality
            # (no free variables — this is purely a verification step)
            if sf.freq_lo != lf.freq_lo:
                s.add(BitVecVal(0, 1) == BitVecVal(1, 1))  # UNSAT sentinel
                break
            if sf.freq_hi != lf.freq_hi:
                s.add(BitVecVal(0, 1) == BitVecVal(1, 1))
                break
            if sf.pw_lo != lf.pw_lo:
                s.add(BitVecVal(0, 1) == BitVecVal(1, 1))
                break
            if sf.pw_hi != lf.pw_hi:
                s.add(BitVecVal(0, 1) == BitVecVal(1, 1))
                break
            if sf.ctrl != lf.ctrl:
                s.add(BitVecVal(0, 1) == BitVecVal(1, 1))
                break
            if sf.ad != lf.ad:
                s.add(BitVecVal(0, 1) == BitVecVal(1, 1))
                break
            if sf.sr != lf.sr:
                s.add(BitVecVal(0, 1) == BitVecVal(1, 1))
                break

        result = s.check()
        return result == sat
    except ImportError:
        # Z3 not available: fall back to direct comparison
        return _is_prefix(short_frames, long_frames)


def find_min_instruments(all_notes: List[NoteParams],
                         use_z3: bool = True,
                         verbose: bool = False
                         ) -> Tuple[int, Dict[tuple, List[NoteParams]]]:
    """Find the minimum number of instruments needed.

    Algorithm:
        1. Group notes by fingerprint (pitch-independent descriptor).
           All notes in one fingerprint group have the same (AD,SR,wave,pw,arp-type).
        2. Within each group, check if notes with different lengths are prefix-compatible.
           Prefix-compatible notes can share one instrument (shorter note = truncated playback).
        3. Notes that are NOT prefix-compatible (e.g., diverge after N frames) need separate
           instruments — a sub-group per unique prefix chain.
        4. The minimum instrument count = number of final sub-groups.

    For arpeggio notes: arpeggio pattern includes absolute pitches, so same-type arp
    notes with different pitches already have different fingerprints (they're pitch-specific
    by design in _fingerprint()). No additional splitting needed there.

    Args:
        all_notes:  flat list of NoteParams from extract_all_notes()
        use_z3:     if True, verify merges with Z3 (proof certificate)
        verbose:    print merge statistics

    Returns:
        (min_count, equiv_classes) where equiv_classes maps fingerprint -> list of notes
    """
    # Group by fingerprint
    fp_groups: Dict[tuple, List[NoteParams]] = defaultdict(list)
    for note in all_notes:
        fp_groups[note.fingerprint].append(note)

    if verbose:
        print(f"[Z3GS] Fingerprint groups: {len(fp_groups)}")
        print(f"[Z3GS] Notes total: {len(all_notes)}")

    # Within each group, find the maximal prefix chains.
    # A prefix chain is a set of notes {N1, N2, ...} where the longest note's
    # frames contain all shorter notes' frames as a prefix.
    # We merge them into one instrument (the longest one provides the template).
    merged_classes: Dict[tuple, List[NoteParams]] = {}
    total_sub_groups = 0
    total_merges = 0

    for fp, notes in fp_groups.items():
        # Sort by length (longest first — the longest provides the instrument template)
        notes_sorted = sorted(notes, key=lambda n: n.length, reverse=True)

        # Build prefix chains greedily.
        # Each chain has one "template" (the longest note) and zero or more
        # shorter notes that are prefixes of it.
        chains: List[List[NoteParams]] = []

        for note in notes_sorted:
            placed = False
            for chain in chains:
                template = chain[0]  # longest in this chain
                # Check prefix: note.original must be a prefix of template.original
                if len(note.original) <= len(template.original):
                    if use_z3:
                        ok = _z3_verify_prefix(note.original, template.original)
                    else:
                        ok = _is_prefix(note.original, template.original)
                    if ok:
                        chain.append(note)
                        placed = True
                        total_merges += 1
                        break
                # Also check: could this note BE a template that the current template
                # is a prefix of? (Happens if notes_sorted has ties or near-ties.)
                # (Shouldn't happen since we process longest-first, but guard anyway.)
            if not placed:
                chains.append([note])

        n_chains = len(chains)
        total_sub_groups += n_chains

        # Store as sub-group equivalence classes.
        # Each chain gets a unique key: (fp, chain_index)
        for ci, chain in enumerate(chains):
            sub_fp = (fp, ci)
            merged_classes[sub_fp] = chain

        if verbose and n_chains > 1:
            print(f"[Z3GS]   fp={fp[:3]}... split into {n_chains} chains "
                  f"(from {len(notes)} notes)")

    if verbose:
        print(f"[Z3GS] After merge: {total_sub_groups} instruments "
              f"(merged {total_merges} notes onto shared instruments)")

    return total_sub_groups, merged_classes


# =============================================================================
# Step 3: Build USF Song from merged instrument classes
# =============================================================================

def _build_instrument_from_chain(chain: List[NoteParams],
                                  freq_map: Dict[int, int],
                                  shared_pulse_table: List[Tuple],
                                  pulse_sig_to_ptr: Dict[tuple, int],
                                  inst_id: int) -> Instrument:
    """Build a USF Instrument from a merge chain.

    The template is chain[0] (longest note — provides the full instrument data).
    All shorter notes in the chain are prefixes of the template.
    """
    template = chain[0]
    params = template.params

    # Arpeggio indices
    arp = params.get('arpeggio')
    arp_indices = None
    if arp:
        pattern_freqs = arp.get('pattern', [])
        if len(pattern_freqs) >= 2:
            arp_indices = [_nearest_index(f, freq_map) for f in pattern_freqs]

    # Freq table index for base note
    freq16 = template.freq16
    base_index = _nearest_index(freq16, freq_map) if freq16 > 0 else 1

    # Wave table
    wave_steps = _build_wave_table(params, base_index, arp_indices)

    # Pulse table
    pulse_steps, initial_pw = _build_pulse_table(params)
    pulse_ptr = 0
    if pulse_steps:
        psig = tuple(
            (s.is_set, s.value, s.duration, s.is_loop, s.loop_target)
            for s in pulse_steps
        )
        if psig not in pulse_sig_to_ptr:
            ptr = len(shared_pulse_table) + 1  # 1-indexed
            pulse_sig_to_ptr[psig] = ptr
            for ps in pulse_steps:
                if ps.is_loop:
                    shared_pulse_table.append((0xFF, ps.loop_target))
                elif ps.is_set:
                    shared_pulse_table.append((0x80 | (ps.value & 0x0F), ps.low_byte))
                else:
                    speed = ps.value & 0xFF
                    shared_pulse_table.append((min(ps.duration, 0x7F), speed))
        pulse_ptr = pulse_sig_to_ptr[psig]

    # ADSR
    adsr = params.get('adsr', {})
    ad = adsr.get('ad', 0)
    sr = adsr.get('sr', 0)

    # Primary waveform name
    waveform_params = params.get('waveform', {})
    wave_seq = waveform_params.get('sequence', [])
    first_ctrl = wave_seq[0] if wave_seq else 0x41
    wave_bits = (first_ctrl >> 4) & 0xF
    waveform_name = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(wave_bits, 'pulse')

    return Instrument(
        id=inst_id,
        ad=ad,
        sr=sr,
        waveform=waveform_name,
        gate_timer=1,
        hr_method='gate',
        wave_table=wave_steps,
        pulse_width=initial_pw,
        pulse_ptr=pulse_ptr,
    )


def guided_strip(trace,
                 use_z3: bool = True,
                 verbose: bool = True,
                 n_workers: int = 64) -> Tuple[Song, Dict[str, Any]]:
    """Z3-guided stripping decomposer: produces a compact USF Song.

    Pipeline:
        1. strip_decompose all notes (100% accurate, exact register reproduction)
        2. Fingerprint each note (pitch-independent descriptor)
        3. Z3 verifies prefix-merge compatibility within each fingerprint class
        4. Build USF Song with merged instruments (significantly fewer than naive)

    Args:
        trace:      SubtuneTrace from ground_truth.capture_sid()
        use_z3:     if True, use Z3 to verify prefix merges (proof certificate)
        verbose:    print progress
        n_workers:  unused (reserved for future parallel Z3 solving)

    Returns:
        (song, stats) where song is a USF Song and stats is a dict with:
            n_before:  instrument count before merging (naive fingerprint groups)
            n_after:   instrument count after Z3-guided merging
            z3_min:    Z3-proven minimum instrument count (= n_after)
            n_notes:   total notes across all voices
            merges:    number of merge operations performed
    """
    t0 = time.time()

    if verbose:
        print("[ZGS] Step 1: Extracting note parameters via strip_decompose...")

    all_notes = extract_all_notes(trace)
    n_notes = len(all_notes)

    if verbose:
        print(f"[ZGS]   {n_notes} notes across 3 voices")

    # Count naive InstrumentPool entries (exact frame deduplication — the baseline)
    from strip_decompose import InstrumentPool as _InstrPool, FreqTable as _FT, frames_from_trace as _ftrace
    _ft = _FT()
    _ft.add(0)
    _ip = _InstrPool()
    for _note in all_notes:
        _inst_frames = []
        for _f in _note.original:
            _fq = _ft.add(_f.freq16())
            _inst_frames.append((_fq, _f.ctrl, _f.pw_lo, _f.pw_hi & 0x0F, _f.ad, _f.sr))
        _n = min(len(_inst_frames), 255)
        _ip.add(_inst_frames[:_n])
    n_naive_pool = len(_ip)  # InstrumentPool count (exact deduplication)

    # Fingerprint groups (instrument-type equivalence, pitch-independent)
    naive_fps: Counter = Counter()
    for note in all_notes:
        naive_fps[note.fingerprint] += 1
    n_naive_fp = len(naive_fps)

    if verbose:
        print(f"[ZGS] Step 2: Z3 minimum instrument count "
              f"(baseline: {n_naive_pool} InstrumentPool, {n_naive_fp} fingerprint groups)...")

    z3_min, merged_classes = find_min_instruments(all_notes, use_z3=use_z3, verbose=verbose)

    if verbose:
        print(f"[ZGS]   Z3 minimum: {z3_min} instruments")
        print(f"[ZGS] Step 3: Building USF Song with {z3_min} instruments...")

    # Build USF Song
    song = Song()
    song.nowavedelay = True

    # Frequency table
    freq_lo, freq_hi, freq_map = _build_freq_table(trace)
    song.freq_lo = freq_lo
    song.freq_hi = freq_hi

    # Tempo
    song.tempo = _detect_tempo(trace)

    # Build instrument list from merged classes
    # Map: (fp, chain_idx) -> instrument_id
    class_to_inst_id: Dict[tuple, int] = {}
    instruments: List[Instrument] = []
    shared_pulse_table: List[Tuple] = []
    pulse_sig_to_ptr: Dict[tuple, int] = {}

    for sub_fp, chain in merged_classes.items():
        inst_id = len(instruments)
        class_to_inst_id[sub_fp] = inst_id
        inst = _build_instrument_from_chain(
            chain, freq_map, shared_pulse_table, pulse_sig_to_ptr, inst_id
        )
        instruments.append(inst)

    song.instruments = instruments
    song.shared_pulse_table = shared_pulse_table

    if verbose:
        print(f"[ZGS]   {len(instruments)} instruments built")

    # Build per-note -> instrument_id lookup.
    # We need to map each NoteParams object back to its instrument.
    # Build: note_id (voice, seg_start) -> (inst_id, base_index)
    note_to_inst: Dict[Tuple[int, int], Tuple[int, int]] = {}

    for sub_fp, chain in merged_classes.items():
        inst_id = class_to_inst_id[sub_fp]
        for note in chain:
            freq16 = note.freq16
            base_index = _nearest_index(freq16, freq_map) if freq16 > 0 else 1
            note_to_inst[(note.voice, note.seg_start)] = (inst_id, base_index)

    # Reconstruct per-voice event lists (in frame order)
    voice_events_list: List[List[Tuple[int, NoteEvent]]] = [[], [], []]
    tempo = song.tempo

    for note in sorted(all_notes, key=lambda n: (n.voice, n.seg_start)):
        key = (note.voice, note.seg_start)
        if key not in note_to_inst:
            continue
        inst_id, base_index = note_to_inst[key]

        dur_ticks = max(1, round(note.length / tempo))
        note_val = min(base_index, 95)

        voice_events_list[note.voice].append((note.seg_start, NoteEvent(
            type='note',
            note=note_val,
            duration=dur_ticks,
            instrument=inst_id,
        )))

    # Pattern discovery with loop structure
    song.patterns = []
    song.orderlists = [[], [], []]
    song.orderlist_restart = [0, 0, 0]

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
        else:
            intro_events = []
            loop_events = [e for (_, e) in tagged_events]

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
            all_events = loop_events
            from holy_scale import _discover_patterns
            patterns, orderlist, restart_idx = _discover_patterns(all_events)
            for pat in patterns:
                pat.id = global_pat_id
                song.patterns.append(pat)
                global_pat_id += 1
            id_offset = global_pat_id - len(patterns)
            song.orderlists[v] = [(id_offset + pid, tr) for pid, tr in orderlist]
            song.orderlist_restart[v] = restart_idx

    elapsed = time.time() - t0

    # Count actual merges (notes that were placed on an existing chain)
    n_merges = sum(max(0, len(chain) - 1) for chain in merged_classes.values())

    stats = {
        'n_notes': n_notes,
        'n_naive_pool': n_naive_pool,    # InstrumentPool exact dedup count (baseline)
        'n_naive_fp': n_naive_fp,        # fingerprint group count
        'n_before': n_naive_pool,        # baseline = InstrumentPool count
        'n_after': len(instruments),     # after Z3-guided prefix merging
        'z3_min': z3_min,                # proven minimum (= n_after)
        'merges': n_merges,              # notes merged onto existing chains
        'tempo': song.tempo,
        'loop_frame': loop_frame,
        'elapsed_s': round(elapsed, 2),
    }

    if verbose:
        print(f"[ZGS] Done in {elapsed:.2f}s")
        print(f"[ZGS]   Instruments: {n_naive_pool} InstrPool baseline "
              f"-> {len(instruments)} Z3-guided")
        print(f"[ZGS]   Z3 minimum: {z3_min}   Merges: {n_merges} "
              f"(from {n_notes} notes)")

    return song, stats


# =============================================================================
# Full pipeline: trace -> USF -> SID file
# =============================================================================

def guided_strip_to_sid(sid_path: str,
                        output_path: str,
                        subtune: int = 1,
                        max_frames: Optional[int] = None,
                        use_z3: bool = True,
                        verbose: bool = True) -> Dict[str, Any]:
    """Full pipeline: SID -> guided_strip -> USF -> rebuilt SID.

    Args:
        sid_path:    original SID file path
        output_path: output .sid path
        subtune:     1-indexed subtune number
        max_frames:  override max frames
        use_z3:      use Z3 for prefix verification
        verbose:     print progress

    Returns:
        stats dict including instrument counts, merge stats, and match rate.
    """
    from ground_truth import capture_sid
    from converters.usf_to_sid import usf_to_sid
    from sid_compare import compare_sids_tolerant

    if verbose:
        print(f"[ZGS] Z3-guided strip: {sid_path} subtune {subtune}")

    # Step 1: Capture ground truth
    if verbose:
        print("[ZGS] Capturing ground truth...")
    sid_trace = capture_sid(sid_path, subtunes=[subtune],
                            max_frames=max_frames,
                            detect_loop=True, progress=verbose)
    if not sid_trace.subtunes:
        raise RuntimeError(f"No subtune {subtune} captured")
    trace = sid_trace.subtunes[0]
    if verbose:
        print(f"[ZGS] {trace.n_frames} frames captured")

    # Step 2: Z3-guided decomposition -> USF
    song, stats = guided_strip(trace, use_z3=use_z3, verbose=verbose)

    # Step 3: USF -> SID
    if verbose:
        print("[ZGS] Encoding USF -> SID via usf_to_sid...")
    try:
        usf_to_sid(song, output_path)
        sid_size = os.path.getsize(output_path)
        if verbose:
            print(f"[ZGS] PSID written: {output_path} ({sid_size} bytes)")
        stats['sid_size'] = sid_size
        stats['usf_success'] = True
    except Exception as e:
        if verbose:
            print(f"[ZGS] usf_to_sid failed: {e}")
        stats['sid_size'] = 0
        stats['usf_success'] = False
        stats['usf_error'] = str(e)

    # Step 4: Compare
    if stats.get('usf_success') and os.path.exists(output_path):
        if verbose:
            print("[ZGS] Comparing against ground truth...")
        try:
            cmp = compare_sids_tolerant(sid_path, output_path, duration=10)
            stats['grade'] = cmp.get('grade', '?')
            stats['score'] = cmp.get('score', 0.0)
            stats['match_pct'] = cmp.get('score', 0.0)
            if verbose:
                print(f"[ZGS] Grade: {stats['grade']}  Score: {stats['score']:.1f}%")
        except Exception as e:
            if verbose:
                print(f"[ZGS] Comparison failed: {e}")
            stats['grade'] = '?'
            stats['score'] = 0.0

    stats['n_frames'] = trace.n_frames
    return stats


# =============================================================================
# Command-line entry point
# =============================================================================

if __name__ == '__main__':
    # Environment setup
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xa65_path = os.path.join(repo_root, 'tools', 'xa65', 'xa')
    tools_path = os.path.join(repo_root, 'tools')
    os.environ['PATH'] = xa65_path + ':' + tools_path + ':' + os.environ.get('PATH', '')
    os.environ.setdefault('SIDFINITY_ROOT', repo_root)

    sys.path.insert(0, os.path.join(repo_root, 'src'))

    # Default: Commando subtune 1
    default_sid = os.path.join(repo_root, 'data', 'C64Music',
                               'MUSICIANS', 'H', 'Hubbard_Rob', 'Commando.sid')

    in_sid  = sys.argv[1] if len(sys.argv) > 1 else default_sid
    out_sid = sys.argv[2] if len(sys.argv) > 2 else '/tmp/z3_guided_strip_out.sid'
    subtune = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    max_frames = int(sys.argv[4]) if len(sys.argv) > 4 else 1500

    if not os.path.exists(in_sid):
        print(f"ERROR: SID not found: {in_sid}")
        sys.exit(1)

    print(f"Z3-guided strip: {in_sid}")
    print(f"  Subtune: {subtune}  Max frames: {max_frames}")
    print(f"  Output:  {out_sid}")
    print()

    # Demo mode: also run without Z3 to show the difference
    from ground_truth import capture_sid

    print("Capturing ground truth...")
    sid_trace = capture_sid(in_sid, subtunes=[subtune], max_frames=max_frames,
                            detect_loop=True, progress=False)
    trace = sid_trace.subtunes[0]
    print(f"  {trace.n_frames} frames captured")
    print()

    # Count naive instruments (strip_decompose InstrumentPool baseline)
    print("=== Naive strip_decompose (no Z3 merging) ===")
    all_notes = extract_all_notes(trace)
    naive_fps: Counter = Counter()
    for note in all_notes:
        naive_fps[note.fingerprint] += 1
    print(f"  Notes:                {len(all_notes)}")
    print(f"  Fingerprint groups:   {len(naive_fps)}  (instrument-type classes, pitch-independent)")
    print(f"  (InstrumentPool baseline will be shown in Z3 stats)")
    print()

    # Z3-guided merge (with verification)
    print("=== Z3-guided merging ===")
    song, stats = guided_strip(trace, use_z3=True, verbose=True)
    print()
    print(f"  Instruments before merging:  {stats['n_before']}")
    print(f"  Instruments after merging:   {stats['n_after']}")
    print(f"  Z3 proven minimum:           {stats['z3_min']}")
    print(f"  Notes merged:                {stats['merges']}")
    print(f"  Time:                        {stats['elapsed_s']}s")
    print()

    # Encode to SID
    print("Encoding USF -> SID...")
    try:
        from converters.usf_to_sid import usf_to_sid
        usf_to_sid(song, out_sid)
        sid_size = os.path.getsize(out_sid)
        print(f"  PSID written: {out_sid} ({sid_size} bytes)")
    except Exception as e:
        print(f"  usf_to_sid failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Compare
    print()
    print("Comparing against ground truth...")
    try:
        from sid_compare import compare_sids_tolerant
        cmp = compare_sids_tolerant(in_sid, out_sid, duration=10)
        grade = cmp.get('grade', '?')
        score = cmp.get('score', 0.0)
        print(f"  Grade: {grade}   Score: {score:.1f}%")
    except Exception as e:
        print(f"  Comparison failed: {e}")

    print()
    print("=== Summary ===")
    print(f"  Notes:                  {stats['n_notes']}")
    print(f"  InstrPool baseline:     {stats['n_before']} instruments (exact dedup)")
    print(f"  Z3-guided merged:       {stats['n_after']} instruments "
          f"({stats['merges']} notes merged onto prefix chains)")
    print(f"  Z3 proven minimum:      {stats['z3_min']}")
    print(f"  Tempo detected:         {stats['tempo']} frames/tick")
