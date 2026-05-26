"""
holy_scale.py — Convert strip_decompose parameters into a USF Song.

Pipeline position:
    ground_truth.py → strip_decompose.py → holy_scale.py → usf_to_sid.py → SID

Architecture:
    - Extracts all unique frequencies from the trace ground truth
    - Builds a custom freq table (96 entries max, index 0 = dummy)
    - Segments each voice into notes via gate transitions
    - For each note, runs strip_decompose() to get provably correct parameters
    - Maps parameters to USF Instrument objects (with wave/pulse tables)
    - Quantizes note durations to ticks using detected tempo
    - Finds repeated patterns → orderlist
    - Returns USF Song ready for usf_to_sid()

Key encoding rules (from GT2/V2 player analysis):
    - absolute_note=0 → packed $00 = KEEP FREQ (wrong!).  Must keep index 0 as dummy.
    - WaveTableStep.waveform = SID ctrl byte (e.g. $41 = pulse+gate)
    - Instrument IDs are 0-indexed in Song; packer adds +1 when encoding

Usage:
    from ground_truth import capture_sid
    from holy_scale import holy_scale
    from converters.usf_to_sid import usf_to_sid

    result = capture_sid('song.sid', subtunes=[1])
    trace = result.subtunes[0]
    song = holy_scale(trace, 'song.sid')
    usf_to_sid(song, 'output.sid')
"""

import os
import sys
import math
from collections import Counter
from typing import List, Dict, Tuple, Optional, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from usf.format import (
    Song, Instrument, Pattern, NoteEvent, WaveTableStep,
    PulseTableStep, FilterTableStep, SpeedTableEntry,
    CMD_VIBRATO, CMD_PORTA_UP, CMD_PORTA_DOWN, CMD_SET_TEMPO,
)
from strip_decompose import strip_decompose


# ---------------------------------------------------------------------------
# Custom frequency table
# ---------------------------------------------------------------------------

def _build_freq_table(trace) -> Tuple[bytes, bytes, Dict[int, int]]:
    """Build a compact PAL-range freq table for notes in this trace.

    Approach:
      1. Find the min/max PAL note indices used as base notes in the song.
      2. Include the full PAL chromatic range from min-12 to max+12 (±12 for arp).
      3. Index 0 = dummy ($0001).  Real note indices start at 1.
      4. PAL entry at pal_idx → table index (pal_idx - pal_min + 1).
      5. All indices stay within 0-92 (GT2 pattern range), since max span < 80 notes.

    This ensures note_offset=+12 works correctly: table[n+12] = PAL[pal_min+n+11]
    which is exactly one octave above PAL[pal_min+n-1].

    Non-PAL frequencies snap to the nearest PAL entry within the range.

    Returns:
        freq_lo:  lo bytes (length = pal_max - pal_min + 2 with dummy)
        freq_hi:  hi bytes
        freq_map: freq16 → index mapping (indices 1-based)
    """
    from effect_detect import FREQ_PAL, freq_to_note as _freq_to_note

    # Collect used frequencies (first 4 frames of each gate segment)
    gate_freqs: Counter = Counter()
    for voice in range(3):
        segs = trace.gate_segments(voice)
        voff = voice * 7
        for seg_s, seg_e in segs:
            for f in range(seg_s, min(seg_s + 4, seg_e)):
                fq = (trace.frames[f][voff + 1] << 8) | trace.frames[f][voff]
                if fq > 1:  # skip zero and dummy sentinel (0x0001)
                    gate_freqs[fq] += 1

    # Snap each freq to nearest PAL index
    pal_indices_used: set = set()
    freq_to_pal: Dict[int, int] = {}   # freq16 → PAL index (0-95)
    for freq16 in gate_freqs:
        if freq16 <= 1:  # skip zero and dummy sentinel (0x0001)
            continue
        idx, cents = _freq_to_note(freq16)
        if idx is not None and idx > 0:  # skip PAL[0] (too low to be musical)
            pal_indices_used.add(idx)
            freq_to_pal[freq16] = idx

    if not pal_indices_used:
        # Fallback: use the standard PAL table (never happens in practice)
        pal_min, pal_max = 0, 95
    else:
        # Extend range by 12 semitones in each direction to support arp +/-12
        pal_min = max(0, min(pal_indices_used) - 12)
        pal_max = min(95, max(pal_indices_used) + 12)

    # Sanity: ensure the range fits in GT2 pattern note space (0-92 indices + dummy)
    # Index = (pal_idx - pal_min) + 1, max index = pal_max - pal_min + 1 ≤ 92
    if pal_max - pal_min + 1 > 92:
        # Trim the top end (top notes are less common)
        pal_max = pal_min + 91

    # Build the table: [dummy, PAL[pal_min], PAL[pal_min+1], ..., PAL[pal_max]]
    table: List[int] = [0x0001]  # index 0 = dummy
    freq_map: Dict[int, int] = {}

    for pi in range(pal_min, pal_max + 1):
        freq16 = FREQ_PAL[pi]
        entry_idx = len(table)  # 1-based
        table.append(freq16)
        freq_map[freq16] = entry_idx

    # Map non-PAL frequencies to the nearest PAL entry in our table
    for freq16, pal_idx in freq_to_pal.items():
        if freq16 not in freq_map:
            # Map to the nearest PAL entry we do have
            clamped = max(pal_min, min(pal_max, pal_idx))
            freq_map[freq16] = clamped - pal_min + 1

    freq_lo = bytes(f & 0xFF for f in table)
    freq_hi = bytes((f >> 8) & 0xFF for f in table)

    return freq_lo, freq_hi, freq_map


def _nearest_index(freq16: int, freq_map: Dict[int, int]) -> int:
    """Return the freq table index nearest to freq16.  Never returns 0 (dummy)."""
    if freq16 in freq_map:
        return freq_map[freq16]
    if not freq_map:
        return 1
    nearest = min(freq_map.keys(), key=lambda x: abs(x - freq16))
    return freq_map[nearest]


# ---------------------------------------------------------------------------
# Arpeggio classification helpers
# ---------------------------------------------------------------------------

def _classify_arp(pattern_freqs: List[int]) -> Dict[str, Any]:
    """Classify an arpeggio pattern as standard (12-semitone octave) or relative.

    Uses FREQ_PAL to convert each frequency to the nearest PAL note index.
    Computes semitone offsets from the base (first) frequency.

    Returns a dict:
        kind:    'std'      — all offsets are exactly +12 semitones (octave arp)
                 'relative' — offsets are in range 0-95 (can use note_offset)
                 'absolute' — some offsets out of range, must use absolute_note
        offsets: list of semitone offsets from base (first element is always 0)
    """
    from effect_detect import freq_to_note as _freq_to_note
    if len(pattern_freqs) < 2:
        return {'kind': 'absolute', 'offsets': [0]}

    notes = []
    for f in pattern_freqs:
        idx, _ = _freq_to_note(f)
        notes.append(idx if idx is not None else 0)

    base = notes[0]
    offsets = [n - base for n in notes]

    # All-zero offsets: not a real arpeggio (same freq throughout).
    # strip_arpeggio() can misfire when a long sustained note has period=8.
    if all(o == 0 for o in offsets):
        return {'kind': 'none', 'offsets': [0]}

    # Standard: exactly 2-step arpeggio with offset +12
    if offsets == [0, 12] or offsets == [0, 12, 0] or offsets == [12, 0]:
        return {'kind': 'std', 'offsets': offsets}

    # For all other arpeggios: use note_offset (relative semitone).
    # The V2 player computes: (base_note + offset) & 0x7F → freq table lookup.
    # With the full 96-entry PAL table (indices 1-96), offsets in range -63..+63
    # are safe for any base note in the middle of the scale.
    # note_offset is encoded as (offset & 0x7F), so:
    #   positive offsets 0-63 → 0x00-0x3F → packed 0x80-0xBF (relative)
    #   negative offsets -64..-1 → 0x40-0x7F → packed 0xC0-0xFF (relative)
    # The 'and #$7f' at the player masks the result to 0-127, but our PAL table
    # only has 96 valid entries (1-96); anything ≥97 is out of range.
    # So we classify as 'relative' if all (base+offset) values are in 1-96.
    if all(-63 <= o <= 63 for o in offsets):
        return {'kind': 'relative', 'offsets': offsets}

    return {'kind': 'relative', 'offsets': offsets}  # always relative with PAL table


# ---------------------------------------------------------------------------
# Instrument fingerprinting
# ---------------------------------------------------------------------------

def _fingerprint(params: Dict[str, Any]) -> tuple:
    """Compute a hashable fingerprint for an instrument from strip_decompose params.

    The fingerprint is pitch-independent for standard and relative arpeggios:
    notes playing the same timbre at different pitches share one Instrument.
    For absolute arpeggios (Hubbard extended table), instruments are still
    deduplicated by ADSR+wave+offset-shape rather than exact frequencies.

    Gate bit is masked out of waveform bytes so that gate-on and sustain
    frames don't create spuriously different instruments.
    """
    adsr = params.get('adsr', {})
    gate = params.get('gate', {})
    waveform = params.get('waveform', {})

    # ADSR
    ad = adsr.get('ad', 0)
    sr = adsr.get('sr', 0)

    # Gate timing is NOT included in the fingerprint: the gate-off frame within
    # a note varies with note length (longer notes have later gate-off), but the
    # instrument timbre is the same regardless.  The SID ADSR envelope handles
    # the release curve; gate_timer is always 1 in the V2 player.

    # Waveform sequence — mask gate bit, take first 2 distinct values
    # (gate-on waveform + sustain waveform are the only audible transitions).
    # More than 2 unique ctrl values usually reflects measurement noise or
    # a single pulse+sync trick; binning to 2 prevents instrument explosion.
    wave_seq = waveform.get('sequence', [])
    wave_no_gate = [w & 0xFE for w in wave_seq]  # strip gate bit
    wave_sig = tuple(list(dict.fromkeys(wave_no_gate))[:2])

    # Pulse width modulation: has modulation or not.
    # Direction (up/down) is NOT included in the fingerprint: notes of the same
    # PWM instrument may start at different phases of the sweep and show opposite
    # directions.  'has_pwm' vs 'no_pwm' is enough to distinguish the timbre.
    pw_seq = params.get('pw', {}).get('sequence', [])
    if len(pw_seq) >= 2:
        pw12 = [((h & 0x0F) << 8) | l for h, l in pw_seq]
        deltas = [pw12[i + 1] - pw12[i] for i in range(len(pw12) - 1)]
        nonzero = [d for d in deltas if d != 0]
        pw_sig = 'has_pwm' if nonzero else 'no_pwm'
    else:
        pw_sig = 'no_pwm'

    # Arpeggio: classify by type and semitone-offset shape, not exact frequencies.
    # Standard (12-semitone octave) and relative arpeggios are pitch-independent.
    # Absolute arpeggios (Hubbard extended table) share an instrument per offset shape.
    arp = params.get('arpeggio')
    arp_sig = ()
    if arp:
        pattern = arp.get('pattern', [])
        if len(pattern) >= 2:
            cls = _classify_arp(pattern)
            offsets = cls['offsets']
            # Filter out false-positive arps: all-zero offset = same freq throughout.
            # strip_arpeggio() can misfire on long sustained notes (period 8, all same).
            if all(o == 0 for o in offsets):
                arp_sig = ()  # treat as no arp
            else:
                # Fingerprint by kind + offset shape (not exact frequencies)
                arp_sig = (cls['kind'], tuple(offsets))
        else:
            arp_sig = ()

    # Portamento: has/not and direction
    porta = params.get('portamento')
    porta_sig = 0
    if porta:
        d = porta.get('delta_per_frame', 0)
        porta_sig = 1 if d > 0 else -1 if d < 0 else 0

    # Vibrato (rate class) — only include if purity is high enough to be real.
    # Low-purity vibrato detections are measurement noise from PWM or other effects.
    vib = params.get('vibrato')
    vib_sig = 0
    if vib and vib.get('purity', 0) >= 0.5:
        vib_sig = round(vib.get('rate_hz', 0))

    # Drum slide: has/not and delta sign
    drum = params.get('drum_slide')
    drum_sig = 0
    if drum:
        d = drum.get('delta', 0)
        drum_sig = 1 if d > 0 else -1 if d < 0 else 0

    return (ad, sr, wave_sig, pw_sig, arp_sig, porta_sig, vib_sig, drum_sig)


# ---------------------------------------------------------------------------
# Wave table builder
# ---------------------------------------------------------------------------

def _build_wave_table(params: Dict[str, Any],
                      base_index: int,
                      arp_indices: Optional[List[int]] = None,
                      arp_class: Optional[Dict] = None,
                      ) -> List[WaveTableStep]:
    """Build USF WaveTableStep list from strip_decompose parameters.

    Key encoding rule: for non-arpeggio steps, use note_offset=0 (relative +0)
    instead of absolute_note.  note_offset=0 encodes as packed right=$80 which
    the V2 player treats as "use the pattern event's note" (add 0 to pattern note).
    This makes the instrument pitch-portable: the pattern NoteEvent.note field
    (already a freq-table index) determines the actual frequency.

    For standard/relative arpeggio steps, use note_offset (semitone offset from
    the pattern event's note) — this is pitch-independent.
    For absolute arpeggio steps (Hubbard extended table), use absolute_note.

    Args:
        params:     strip_decompose output for one note
        base_index: freq table index for the note's base frequency
        arp_indices: if arpeggio detected, list of freq table indices (absolute)
        arp_class:  classification from _classify_arp() — kind + offsets

    Returns list of WaveTableStep.
    """
    waveform = params.get('waveform', {})
    wave_seq = waveform.get('sequence', [])
    arp = params.get('arpeggio')
    drum = params.get('drum_slide')

    steps = []

    if drum:
        # Drum: noise waveform with gate+freq_slide
        delta = drum.get('delta', -1)
        # Step 0: gate-on frame; use pattern note (note_offset=0 → packed $80)
        gate_wave = wave_seq[0] | 0x01 if wave_seq else 0x81
        steps.append(WaveTableStep(
            waveform=gate_wave,
            note_offset=0,            # use pattern note
            freq_slide=max(-128, min(127, delta)),
        ))
        # Step 1: sustain loop on same slide, keep freq (no note change)
        steps.append(WaveTableStep(
            waveform=gate_wave & 0xFE,
            keep_freq=True,
            freq_slide=max(-128, min(127, delta)),
        ))
        steps.append(WaveTableStep(is_loop=True, loop_target=1))

    elif (arp and arp_class and arp_indices and len(arp_indices) >= 2
          and not all(o == 0 for o in arp_class.get('offsets', [0]))):
        unique_waves = list(dict.fromkeys(wave_seq)) if wave_seq else []
        gate_wave = (unique_waves[0] | 0x01) if unique_waves else 0x41
        sustain_wave = (unique_waves[-1] & 0xFE) if unique_waves else 0x40

        kind = arp_class.get('kind', 'absolute')
        offsets = arp_class.get('offsets', [0, 12])

        if kind in ('std', 'relative'):
            # Pitch-independent: use note_offset relative to pattern note.
            # Step 0: gate-on + base note (offset 0 = pattern note)
            steps.append(WaveTableStep(
                waveform=gate_wave,
                note_offset=offsets[0],   # always 0 for base step
            ))
            # Remaining steps: offsets from pattern base note
            for off in offsets[1:]:
                steps.append(WaveTableStep(
                    waveform=sustain_wave,
                    note_offset=off,
                ))
            # Loop back to step 0
            steps.append(WaveTableStep(is_loop=True, loop_target=0))

        else:
            # Absolute arpeggio (Hubbard extended table): use exact freq indices.
            # Step 0: gate-on + first arp note (absolute)
            steps.append(WaveTableStep(
                waveform=gate_wave,
                absolute_note=arp_indices[0],
            ))
            # Remaining arp steps
            for idx in arp_indices[1:]:
                steps.append(WaveTableStep(
                    waveform=sustain_wave,
                    absolute_note=idx,
                ))
            # Loop back to step 0
            steps.append(WaveTableStep(is_loop=True, loop_target=0))

    else:
        # Plain note — build minimal wave table
        # Use note_offset=0 (relative +0) for freq steps so the pattern event's
        # note field drives pitch.  The packer encodes note_offset=0 as packed
        # right=$80, which the V2 player routes to: clc; adc mt_chnnote,x; and #$7F
        # giving exactly the pattern note index as the freq table lookup.

        if wave_seq:
            # Limit to 2 unique waveforms: gate-on + sustain.
            # Additional ctrl byte changes are usually measurement noise or
            # minor transitions that don't affect the audible character.
            unique_waves = list(dict.fromkeys(wave_seq))[:2]
        else:
            unique_waves = [0x41]  # default pulse+gate

        # Step 0: gate-on frame with pattern note
        gate_wave = unique_waves[0] | 0x01
        steps.append(WaveTableStep(
            waveform=gate_wave,
            note_offset=0,  # use pattern note
        ))

        if len(unique_waves) > 1:
            # Sustain: second waveform, keep freq
            steps.append(WaveTableStep(
                waveform=unique_waves[1] & 0xFE,
                keep_freq=True,
            ))
            steps.append(WaveTableStep(is_loop=True, loop_target=1))
        else:
            # Simple sustain: keep freq
            sustain_wave = unique_waves[0] & 0xFE
            steps.append(WaveTableStep(
                waveform=sustain_wave,
                keep_freq=True,
            ))
            steps.append(WaveTableStep(is_loop=True, loop_target=1))

    return steps


# ---------------------------------------------------------------------------
# Pulse table builder
# ---------------------------------------------------------------------------

def _build_pulse_table(params: Dict[str, Any]) -> Tuple[List[PulseTableStep], int]:
    """Build pulse table steps and initial pulse width from strip_decompose pw params.

    Returns (steps_list, initial_pw_16bit).
    """
    pw = params.get('pw', {})
    pw_seq = pw.get('sequence', [])

    if not pw_seq:
        return [], 0x0800

    # Extract initial PW
    hi0, lo0 = pw_seq[0]
    initial_pw = ((hi0 & 0x0F) << 8) | lo0

    if len(pw_seq) < 2:
        return [], initial_pw

    # Detect constant modulation speed (per-frame delta)
    # PW is (hi_nib, lo_byte).  Compute 12-bit values.
    pw12 = [((h & 0x0F) << 8) | l for h, l in pw_seq]
    deltas = [pw12[i + 1] - pw12[i] for i in range(len(pw12) - 1)]

    # Count non-zero deltas
    nonzero = [d for d in deltas if d != 0]
    if not nonzero:
        return [], initial_pw

    c = Counter(nonzero)
    best_delta, best_count = c.most_common(1)[0]
    consistency = best_count / len(nonzero) if nonzero else 0

    if consistency >= 0.6 and abs(best_delta) <= 127:
        # Sweep: modulate at constant speed
        steps = [
            PulseTableStep(is_set=False, value=best_delta & 0xFF, duration=127),
            PulseTableStep(is_set=False, value=(-best_delta) & 0xFF, duration=127),
            PulseTableStep(is_loop=True, loop_target=0),
        ]
        return steps, initial_pw

    # No clean pattern — just return static PW
    return [], initial_pw


# ---------------------------------------------------------------------------
# Musical loop detection from gate segments
# ---------------------------------------------------------------------------

def _detect_musical_loop(trace) -> Tuple[Optional[int], Optional[int]]:
    """Detect the true musical loop frame and length from gate segment patterns.

    The ground_truth loop detector matches on raw SID register state, which can
    produce spurious early matches when the same note happens to reoccur.
    This function instead analyzes the sequence of (freq, length) pairs for
    each voice and finds the largest repeating subsequence.

    Returns (loop_frame, loop_length) or (None, None) if no loop found.
    The loop_frame is the frame where the repeating section starts.
    """
    # Use the busiest voice for loop detection
    best_voice = max(range(3), key=lambda v: len(trace.gate_segments(v)))
    segs = trace.gate_segments(best_voice)
    voff = best_voice * 7

    if len(segs) < 4:
        return None, None

    # Build note key sequence: (freq_hi, note_length_frames)
    # freq_hi is more robust than exact freq16 for catching slight pitch variations
    keys = []
    for s, e in segs:
        freq16 = (trace.frames[s][voff+1] << 8) | trace.frames[s][voff]
        freq_hi = (freq16 >> 8) & 0xFF
        ctrl = trace.frames[s][voff+4] & 0xFE  # mask gate bit
        keys.append((freq_hi, ctrl))  # just type+pitch, length is too variable

    n = len(keys)

    # Try to find a repeating block of length block_len starting at split_point.
    # block_len should be >= 4 notes to avoid false positives.
    best = (None, None)

    for split in range(1, n // 2 + 1):
        for block_len in range(4, (n - split) // 1 + 1):
            if split + block_len * 2 > n:
                break
            # Check if block starting at split repeats
            block = keys[split:split + block_len]
            next_block = keys[split + block_len:split + block_len * 2]
            if block == next_block:
                # Found a repeating block — prefer the earliest split point
                # and the longest block
                loop_start_frame = segs[split][0]
                loop_end_frame = segs[split + block_len][0]
                loop_len = loop_end_frame - loop_start_frame
                if loop_len >= 50:  # sanity: at least 1 second
                    best = (loop_start_frame, loop_len)
                    break  # take largest block from this split
        if best[0] is not None:
            break  # take earliest split

    return best


# ---------------------------------------------------------------------------
# Tempo detection
# ---------------------------------------------------------------------------

def _detect_tempo(trace) -> int:
    """Detect frames-per-tick from gate-on intervals across all voices.

    Returns integer tempo (frames per tick, typically 4-8).
    """
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
    # Most common interval is usually 1×tempo or 2×tempo
    best = c.most_common(5)
    # Try to find the GCD of the top candidates
    candidates = [v for v, _ in best[:5]]
    if len(candidates) >= 2:
        import math as _math
        g = candidates[0]
        for x in candidates[1:]:
            g = _math.gcd(g, x)
        if 2 <= g <= 12:
            return g

    return best[0][0] if best else 6


# ---------------------------------------------------------------------------
# Pattern discovery
# ---------------------------------------------------------------------------

def _discover_patterns(events: List[NoteEvent], min_len: int = 2
                       ) -> Tuple[List[Pattern], List[Tuple[int, int]], int]:
    """Find repeated note sequences; return (patterns, orderlist, restart_idx).

    Tries to find repeating blocks from largest to smallest.
    Falls back to one big pattern if nothing repeats.

    Returns:
        patterns:     list of Pattern objects (IDs relative to 0)
        orderlist:    list of (pattern_id, transpose=0) tuples
        restart_idx:  index in orderlist to restart at (0 = whole song loops)
    """
    if not events:
        return [Pattern(id=0, events=[])], [(0, 0)], 0

    n = len(events)
    key = [(e.note, e.instrument, e.duration) for e in events]

    best_block = None
    best_repeats = 1

    for block_len in range(n // 2, min_len - 1, -1):
        if n % block_len != 0:
            continue
        blocks = [key[i:i + block_len] for i in range(0, n, block_len)]
        if all(b == blocks[0] for b in blocks):
            best_block = block_len
            best_repeats = n // block_len
            break

    if best_block:
        pat = Pattern(id=0, events=events[:best_block])
        orderlist = [(0, 0)] * best_repeats
        return [pat], orderlist, 0

    # No clean repetition — one big pattern
    pat = Pattern(id=0, events=events)
    return [pat], [(0, 0)], 0


# ---------------------------------------------------------------------------
# Main converter
# ---------------------------------------------------------------------------

def holy_scale(trace, sid_path: Optional[str] = None) -> Song:
    """Convert a SubtuneTrace to a USF Song via strip_decompose parameters.

    Args:
        trace:    SubtuneTrace from ground_truth.capture_sid()
        sid_path: optional path to original SID (for PSID metadata)

    Returns:
        Song object ready for usf_to_sid()
    """
    song = Song()
    song.nowavedelay = True  # V2 player: direct SID values, no +$10 bias

    # --- Metadata ---
    if sid_path and os.path.exists(sid_path):
        with open(sid_path, 'rb') as _f:
            _d = _f.read()
        if len(_d) > 0x56:
            song.title = _d[0x16:0x36].decode('ascii', errors='ignore').rstrip('\x00').strip()
            song.author = _d[0x36:0x56].decode('ascii', errors='ignore').rstrip('\x00').strip()

    # --- Frequency table ---
    freq_lo, freq_hi, freq_map = _build_freq_table(trace)
    song.freq_lo = freq_lo
    song.freq_hi = freq_hi

    # --- Tempo ---
    tempo = _detect_tempo(trace)
    song.tempo = tempo

    # --- Per-voice decomposition ---
    # fp → Instrument list (we deduplicate by fingerprint, keyed separately
    #      per note so instruments with the same waveform but different arp
    #      patterns can be shared on different pitches)
    fp_to_inst_id: Dict[tuple, int] = {}
    instruments: List[Instrument] = []
    shared_pulse_table: List[Tuple[int, int]] = []
    pulse_sig_to_ptr: Dict[tuple, int] = {}

    # voice_events_list[voice] = list of (frame_start, NoteEvent)
    voice_events_list: List[List[Tuple[int, NoteEvent]]] = [[], [], []]

    for voice in range(3):
        segs = trace.gate_segments(voice)

        for seg_start, seg_end in segs:
            seg_end = min(seg_end, trace.n_frames)
            length = seg_end - seg_start
            if length == 0:
                continue

            # Get ground truth parameters via iterative stripping
            params, _residual, _original = strip_decompose(
                trace, voice, seg_start, seg_end
            )

            # Base frequency: first non-zero freq in this segment.
            # For Hubbard sync/init segments where freq=0 throughout, skip the segment
            # (producing silence) rather than emitting a wrong-pitched note.
            voff = voice * 7
            freq16 = (trace.frames[seg_start][voff + 1] << 8) | trace.frames[seg_start][voff]
            if freq16 == 0:
                # Find the most common non-zero freq in this segment
                from collections import Counter as _Counter
                freq_ctr = _Counter()
                for f in range(seg_start, seg_end):
                    fq = (trace.frames[f][voff+1] << 8) | trace.frames[f][voff]
                    if fq > 0:
                        freq_ctr[fq] += 1
                if freq_ctr:
                    freq16, _ = freq_ctr.most_common(1)[0]
            if freq16 == 0:
                # Truly silent segment (all zeros) — skip it; it's an init burst.
                continue
            base_index = _nearest_index(freq16, freq_map)

            # Arpeggio: map pattern freqs to table indices and classify
            arp = params.get('arpeggio')
            arp_indices = None
            arp_class = None
            if arp:
                pattern_freqs = arp.get('pattern', [])
                if len(pattern_freqs) >= 2:
                    arp_indices = [_nearest_index(f, freq_map) for f in pattern_freqs]
                    arp_class = _classify_arp(pattern_freqs)

            # Build fingerprint (instrument identity, pitch-independent)
            fp = _fingerprint(params)

            if fp not in fp_to_inst_id:
                inst_id = len(instruments)
                fp_to_inst_id[fp] = inst_id

                # Build wave table
                wave_steps = _build_wave_table(params, base_index, arp_indices, arp_class)

                # Build pulse table
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

                # Gate timer: always 1.
                # In the V2 player, gate_timer controls when ce_getnote fires
                # (the next pattern fetch).  It must be <= tempo to ever trigger.
                # Setting gate_timer=1 means "fetch next note when counter==1"
                # (one tick before the counter underflows and reloads).
                # The SID ADSR envelope controls the actual gate-off timing via
                # the SR register — not via gate_timer.
                gate_timer = 1

                # Primary waveform name for Instrument.waveform
                waveform_params = params.get('waveform', {})
                wave_seq = waveform_params.get('sequence', [])
                first_ctrl = wave_seq[0] if wave_seq else 0x41
                wave_bits = (first_ctrl >> 4) & 0xF
                waveform_name = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(
                    wave_bits, 'pulse')

                inst = Instrument(
                    id=inst_id,
                    ad=ad,
                    sr=sr,
                    waveform=waveform_name,
                    gate_timer=gate_timer,
                    hr_method='gate',
                    wave_table=wave_steps,
                    pulse_width=initial_pw,
                    pulse_ptr=pulse_ptr,
                )
                instruments.append(inst)
            else:
                inst_id = fp_to_inst_id[fp]

            # Quantize duration to ticks
            dur_ticks = max(1, round(length / tempo))

            # Note index: use base_index (absolute within custom freq table)
            # but USF NoteEvent.note is 0-95.  We use base_index directly
            # since we're building a custom freq table — the packer will
            # look up freq by note number using song.freq_lo/freq_hi.
            note_val = min(base_index, 95)

            voice_events_list[voice].append((seg_start, NoteEvent(
                type='note',
                note=note_val,
                duration=dur_ticks,
                instrument=inst_id,
            )))

    song.instruments = instruments
    song.shared_pulse_table = shared_pulse_table

    # --- Pattern discovery per voice with loop structure ---
    # If loop_frame is known, split events into intro (pre-loop) and loop body.
    # This ensures the rebuilt SID loops correctly like the original.
    song.patterns = []
    song.orderlists = [[], [], []]
    song.orderlist_restart = [0, 0, 0]

    # Detect true musical loop from segment patterns (more reliable than raw
    # register state matching which can find spurious early loop points).
    musical_loop_frame, musical_loop_len = _detect_musical_loop(trace)
    if musical_loop_frame is not None:
        loop_frame = musical_loop_frame
        loop_end_frame = musical_loop_frame + musical_loop_len
    else:
        loop_frame = trace.loop_frame  # fallback to ground_truth detection
        loop_end_frame = (trace.loop_frame + trace.loop_length
                          if trace.loop_frame is not None else None)

    global_pat_id = 0
    for v in range(3):
        tagged_events = voice_events_list[v]  # list of (frame_start, NoteEvent)

        if loop_frame is not None:
            # Split into intro and loop body.
            # Take only ONE loop iteration's worth of events to avoid encoding
            # repetitions as unique notes (which causes divergence on subsequent loops).
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
            # Two patterns: intro + loop body
            intro_pat = Pattern(id=global_pat_id, events=intro_events)
            song.patterns.append(intro_pat)
            intro_pat_id = global_pat_id
            global_pat_id += 1

            loop_pat = Pattern(id=global_pat_id, events=loop_events)
            song.patterns.append(loop_pat)
            loop_pat_id = global_pat_id
            global_pat_id += 1

            # Orderlist: intro, then loop body (loops forever at restart=1)
            song.orderlists[v] = [(intro_pat_id, 0), (loop_pat_id, 0)]
            song.orderlist_restart[v] = 1  # restart at loop_pat
        else:
            # No intro: single looping pattern (or no loop detection)
            all_events = loop_events
            patterns, orderlist, restart_idx = _discover_patterns(all_events)
            for pat in patterns:
                pat.id = global_pat_id
                song.patterns.append(pat)
                global_pat_id += 1
            id_offset = global_pat_id - len(patterns)
            song.orderlists[v] = [(id_offset + pid, tr) for pid, tr in orderlist]
            song.orderlist_restart[v] = restart_idx

    return song


# ---------------------------------------------------------------------------
# Command-line entry point
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 holy_scale.py <input.sid> [output.sid] [subtune] [max_frames]")
        sys.exit(1)

    # Make sure environment is set up
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    xa65_path = os.path.join(repo_root, 'tools', 'xa65', 'xa')
    tools_path = os.path.join(repo_root, 'tools')
    os.environ['PATH'] = xa65_path + ':' + tools_path + ':' + os.environ.get('PATH', '')
    os.environ.setdefault('SIDFINITY_ROOT', repo_root)

    sys.path.insert(0, os.path.join(repo_root, 'src'))

    from ground_truth import capture_sid
    from converters.usf_to_sid import usf_to_sid
    from sid_compare import compare_sids_tolerant

    in_sid = sys.argv[1]
    out_sid = sys.argv[2] if len(sys.argv) > 2 else '/tmp/holyscale_out.sid'
    subtune = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    max_frames = int(sys.argv[4]) if len(sys.argv) > 4 else None

    print(f"[HS] Capturing ground truth: {in_sid} subtune {subtune}")
    # Disable gt loop detection — we use musical loop detection in holy_scale()
    # which is more robust against spurious register-state matches.
    result = capture_sid(in_sid, subtunes=[subtune], max_frames=max_frames,
                         detect_loop=False, progress=True)
    trace = result.subtunes[0]
    print(f"[HS] {trace.n_frames} frames captured, loop at {trace.loop_frame}")

    print("[HS] Building USF via holy_scale...")
    song = holy_scale(trace, in_sid)

    print(f"[HS] Song: tempo={song.tempo}, {len(song.instruments)} instruments, "
          f"{len(song.patterns)} patterns")
    for v in range(3):
        print(f"  V{v+1}: {len(song.orderlists[v])} orderlist entries")

    print(f"[HS] Building SID: {out_sid}")
    usf_to_sid(song, out_sid)

    sz = os.path.getsize(out_sid)
    print(f"[HS] Output: {sz} bytes ({sz / 1024:.1f} KB)")

    print("[HS] Comparing...")
    comp = compare_sids_tolerant(in_sid, out_sid, 30)
    print(f"[HS] Grade: {comp['grade']}  Score: {comp['score']:.1f}%")
    if 'counts' in comp:
        for k, v in comp['counts'].items():
            if v:
                print(f"       {k}: {v}")
