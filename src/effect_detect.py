"""
effect_detect.py — Universal SID effect detection from ground truth register traces.

Automatically discovers which musical effects are present in each note by analyzing
the mathematical structure of SID register streams. Engine-agnostic: works on any SID.

Detection methods:
  - DFT (Fourier): periodic effects (arpeggio, vibrato, PWM, filter modulation)
  - Differencing: cumulative effects (portamento, drum slide, skydive)
  - Reverse lookup: freq table → note index mapping
  - Edge detection: gate control, hard restart, waveform sequences
  - Direct read: ADSR, waveform select, filter routing

Usage:
    from ground_truth import capture_sid
    from effect_detect import analyze_effects
    result = capture_sid('path/to/song.sid', subtunes=[1])
    effects = analyze_effects(result.subtunes[0])
"""

import math
import os
import sys
from collections import Counter
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# PAL frequency table (standard C64 PAL tuning, 96 entries)
# Matches GT2/Hubbard/most engines
FREQ_PAL = [
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

WAVEFORM_NAMES = {
    0x10: 'triangle', 0x20: 'sawtooth', 0x40: 'pulse', 0x80: 'noise',
    0x50: 'tri_pulse', 0x60: 'saw_pulse', 0x30: 'tri_saw',
    0x14: 'tri_ring', 0x24: 'saw_ring', 0x44: 'pulse_ring',
    0x12: 'tri_sync', 0x22: 'saw_sync', 0x42: 'pulse_sync',
}


# --- Data structures ---

@dataclass
class EffectDetection:
    effect: str
    confidence: float
    params: dict
    frame_start: int
    frame_end: int
    voice: int = -1  # -1 for global

    def __repr__(self):
        p = ', '.join(f'{k}={v}' for k, v in self.params.items())
        return f'{self.effect}({p}) [{self.confidence:.0%}]'


@dataclass
class NoteSegment:
    voice: int
    start: int          # absolute frame index
    end: int            # absolute frame index (exclusive)
    freq: list          # 16-bit freq per frame
    freq_hi: list       # freq high byte per frame
    freq_lo: list       # freq low byte per frame
    pw: list            # 16-bit pulse width per frame
    ctrl: list          # control register per frame
    ad: list
    sr: list

    @property
    def length(self):
        return self.end - self.start


# --- Math utilities (pure Python) ---

def real_dft(signal, sample_rate=50.0):
    """Compute magnitude spectrum of a real signal via DFT.

    Returns list of (freq_hz, magnitude) for bins 1..N//2.
    O(N^2) but fine for N < 1000 (typical note segments).
    """
    N = len(signal)
    if N < 4:
        return []
    mean = sum(signal) / N
    x = [s - mean for s in signal]

    results = []
    for k in range(1, N // 2 + 1):
        re = 0.0
        im = 0.0
        w = 2.0 * math.pi * k / N
        for n in range(N):
            re += x[n] * math.cos(w * n)
            im += x[n] * math.sin(w * n)
        mag = math.sqrt(re * re + im * im) / N
        freq_hz = k * sample_rate / N
        results.append((freq_hz, mag))
    return results


def dft_dominant_peak(signal, min_hz=0.0, max_hz=25.0, sample_rate=50.0):
    """Find the dominant spectral peak in a frequency range.

    Returns (peak_hz, peak_magnitude, total_energy) or (0, 0, 0) if no signal.
    """
    spectrum = real_dft(signal, sample_rate)
    if not spectrum:
        return 0.0, 0.0, 0.0

    total = sum(m for _, m in spectrum)
    filtered = [(f, m) for f, m in spectrum if min_hz <= f <= max_hz]
    if not filtered:
        return 0.0, 0.0, total

    best_f, best_m = max(filtered, key=lambda x: x[1])
    return best_f, best_m, total


def constant_delta(signal):
    """Check if signal changes by a constant amount per frame.

    Returns (dominant_delta, consistency_ratio).
    consistency_ratio = fraction of deltas matching the dominant non-zero delta.
    """
    if len(signal) < 3:
        return 0, 0.0
    deltas = [signal[i + 1] - signal[i] for i in range(len(signal) - 1)]
    non_zero = [d for d in deltas if d != 0]
    if not non_zero:
        return 0, 1.0
    counter = Counter(non_zero)
    best_delta, best_count = counter.most_common(1)[0]
    return best_delta, best_count / len(non_zero)


def freq_to_note(freq16):
    """Map a 16-bit SID frequency to the nearest PAL note index.

    Returns (note_index, cents_error) or (None, None) if freq is 0.
    """
    if freq16 == 0:
        return None, None
    best_idx = 0
    best_dist = abs(freq16 - FREQ_PAL[0])
    for i in range(1, len(FREQ_PAL)):
        d = abs(freq16 - FREQ_PAL[i])
        if d < best_dist:
            best_dist = d
            best_idx = i
    # Compute cents error
    if FREQ_PAL[best_idx] > 0 and freq16 > 0:
        ratio = freq16 / FREQ_PAL[best_idx]
        cents = 1200 * math.log2(ratio) if ratio > 0 else 0
    else:
        cents = 0
    return best_idx, cents


def discreteness(values):
    """How discrete is a signal? Low ratio = few unique values = discrete/arpeggio."""
    if len(values) < 2:
        return 1.0
    return len(set(values)) / len(values)


# --- Build NoteSegments from trace ---

def build_segments(trace):
    """Extract NoteSegments from a SubtuneTrace for all 3 voices.

    Returns list of lists: segments[voice] = [NoteSegment, ...]
    """
    all_segments = []
    for v in range(3):
        segs = trace.gate_segments(v)
        voff = v * 7
        voice_segments = []
        for start, end in segs:
            end = min(end, trace.n_frames)
            if start >= trace.n_frames:
                break
            voice_segments.append(NoteSegment(
                voice=v, start=start, end=end,
                freq=[(trace.frames[f][voff + 1] << 8) | trace.frames[f][voff]
                      for f in range(start, end)],
                freq_hi=[trace.frames[f][voff + 1] for f in range(start, end)],
                freq_lo=[trace.frames[f][voff] for f in range(start, end)],
                pw=[(trace.frames[f][voff + 3] << 8) | trace.frames[f][voff + 2]
                    for f in range(start, end)],
                ctrl=[trace.frames[f][voff + 4] for f in range(start, end)],
                ad=[trace.frames[f][voff + 5] for f in range(start, end)],
                sr=[trace.frames[f][voff + 6] for f in range(start, end)],
            ))
        all_segments.append(voice_segments)
    return all_segments


# --- PERIODIC DETECTORS (DFT) ---

def detect_arpeggio(seg):
    """Detect arpeggio: freq alternates between discrete note values."""
    if seg.length < 4:
        return None

    # Map each frame's freq to nearest note
    notes = []
    for f in seg.freq:
        idx, _ = freq_to_note(f)
        if idx is not None:
            notes.append(idx)
    if len(notes) < 4:
        return None

    unique_notes = sorted(set(notes))
    if len(unique_notes) < 2:
        return None

    # Check discreteness: arpeggio snaps between a few values
    disc = discreteness(notes)
    if disc > 0.3:  # too many unique values = vibrato not arpeggio
        return None

    # Find the pattern period via DFT
    peak_hz, peak_mag, total = dft_dominant_peak(notes, min_hz=8.0, max_hz=25.0)
    if total == 0:
        return None

    spectral_purity = peak_mag / total if total > 0 else 0
    if spectral_purity < 0.2:
        return None

    # Determine arpeggio interval
    intervals = sorted(set(b - a for a, b in zip(unique_notes, unique_notes[1:])))

    return EffectDetection(
        effect='arpeggio',
        confidence=min(1.0, spectral_purity * 2),
        params={
            'notes': unique_notes,
            'intervals': intervals,
            'rate_hz': round(peak_hz, 1),
            'pattern_len': round(50.0 / peak_hz) if peak_hz > 0 else 0,
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_vibrato(seg):
    """Detect vibrato: freq oscillates sinusoidally around center."""
    if seg.length < 10:
        return None

    # Skip if discrete (arpeggio territory)
    disc = discreteness(seg.freq)
    if disc < 0.3:
        return None

    # Look for sinusoidal peak in freq stream
    peak_hz, peak_mag, total = dft_dominant_peak(seg.freq, min_hz=2.0, max_hz=12.0)
    if total == 0 or peak_mag < 1.0:
        return None

    spectral_purity = peak_mag / total
    if spectral_purity < 0.15:
        return None

    center = sum(seg.freq) / len(seg.freq)
    center_note, cents = freq_to_note(int(center))
    depth = max(seg.freq) - min(seg.freq)

    return EffectDetection(
        effect='vibrato',
        confidence=min(1.0, spectral_purity * 2),
        params={
            'rate_hz': round(peak_hz, 1),
            'depth_freq': depth,
            'center_note': center_note,
            'center_freq': int(center),
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_pwm_direct(seg):
    """Detect direct/linear PWM: PW increases by constant delta each frame."""
    if seg.length < 4:
        return None

    # Check PW_lo for constant delta (handle 8-bit wrapping)
    pw_lo = [p & 0xFF for p in seg.pw]
    deltas = [(pw_lo[i + 1] - pw_lo[i]) & 0xFF for i in range(len(pw_lo) - 1)]
    # Convert to signed
    deltas = [d if d < 128 else d - 256 for d in deltas]

    non_zero = [d for d in deltas if d != 0]
    if not non_zero:
        return None

    counter = Counter(non_zero)
    best_delta, best_count = counter.most_common(1)[0]
    consistency = best_count / len(non_zero)

    if consistency < 0.7:
        return None

    # Check PW_hi doesn't change much (direct PWM only changes lo byte)
    pw_hi_vals = set(p >> 8 for p in seg.pw)

    return EffectDetection(
        effect='pwm_direct',
        confidence=consistency,
        params={
            'speed': best_delta,
            'initial_pw': seg.pw[0],
            'pw_hi_values': sorted(pw_hi_vals),
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_pwm_sweep(seg):
    """Detect triangle/sweep PWM: PW oscillates with direction reversals."""
    if seg.length < 8:
        return None

    pw = seg.pw
    # Count direction changes
    deltas = [pw[i + 1] - pw[i] for i in range(len(pw) - 1)]
    sign_changes = 0
    for i in range(1, len(deltas)):
        if deltas[i] * deltas[i - 1] < 0:  # sign change
            sign_changes += 1

    if sign_changes < 1:
        return None

    # DFT on PW stream
    peak_hz, peak_mag, total = dft_dominant_peak(pw, min_hz=0.5, max_hz=15.0)
    if total == 0 or peak_mag / total < 0.1:
        return None

    # Estimate speed from median absolute delta
    abs_deltas = sorted(abs(d) for d in deltas if d != 0)
    speed = abs_deltas[len(abs_deltas) // 2] if abs_deltas else 0

    return EffectDetection(
        effect='pwm_sweep',
        confidence=min(1.0, peak_mag / total * 2),
        params={
            'speed': speed,
            'rate_hz': round(peak_hz, 2),
            'min_pw': min(pw),
            'max_pw': max(pw),
            'reversals': sign_changes,
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_filter_modulation(trace, frame_start, frame_end, voice=-1):
    """Detect periodic filter cutoff modulation."""
    if frame_end - frame_start < 8:
        return None

    # $D416 = filter cutoff high byte (register index 22)
    cutoff = [trace.frames[f][22] for f in range(frame_start, min(frame_end, trace.n_frames))]

    if len(set(cutoff)) < 2:
        return None

    peak_hz, peak_mag, total = dft_dominant_peak(cutoff, min_hz=0.5, max_hz=20.0)
    if total == 0 or peak_mag / total < 0.15:
        return None

    return EffectDetection(
        effect='filter_modulation',
        confidence=min(1.0, peak_mag / total * 2),
        params={
            'rate_hz': round(peak_hz, 2),
            'min_cutoff': min(cutoff),
            'max_cutoff': max(cutoff),
        },
        frame_start=frame_start, frame_end=frame_end, voice=voice,
    )


# --- CUMULATIVE DETECTORS (differencing) ---

def detect_portamento(seg):
    """Detect portamento: freq changes by constant delta per frame."""
    if seg.length < 4:
        return None

    delta, consistency = constant_delta(seg.freq)
    if delta == 0 or consistency < 0.6:
        return None

    # Must be monotonic (not oscillating)
    disc = discreteness(seg.freq)
    if disc < 0.4:  # too few unique values = probably arpeggio
        return None

    direction = 'up' if delta > 0 else 'down'
    start_note, _ = freq_to_note(seg.freq[0])
    end_note, _ = freq_to_note(seg.freq[-1])

    return EffectDetection(
        effect='portamento',
        confidence=consistency,
        params={
            'direction': direction,
            'speed': abs(delta),
            'start_note': start_note,
            'end_note': end_note,
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_drum_freq_slide(seg):
    """Detect drum frequency slide: freq_hi decreases by 1 per frame, noise waveform."""
    if seg.length < 3:
        return None

    # Check noise waveform on first frame
    if not (seg.ctrl[0] & 0x80):
        return None

    delta, consistency = constant_delta(seg.freq_hi)
    if delta != -1 or consistency < 0.6:
        return None

    return EffectDetection(
        effect='drum_freq_slide',
        confidence=consistency,
        params={
            'start_freq_hi': seg.freq_hi[0],
            'end_freq_hi': seg.freq_hi[-1],
            'length': seg.length,
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_skydive(seg):
    """Detect skydive: freq_hi decreases by 1 every 2nd frame."""
    if seg.length < 6:
        return None

    fh = seg.freq_hi
    # Check alternating pattern: [0, -1, 0, -1, ...] or [-1, 0, -1, 0, ...]
    deltas = [fh[i + 1] - fh[i] for i in range(len(fh) - 1)]

    # Check even-frame pattern
    even_match = sum(1 for i in range(0, len(deltas), 2) if deltas[i] == 0)
    odd_match = sum(1 for i in range(1, len(deltas), 2) if deltas[i] == -1)
    pattern1 = (even_match + odd_match) / len(deltas) if deltas else 0

    # Check odd-frame pattern
    even_match2 = sum(1 for i in range(0, len(deltas), 2) if deltas[i] == -1)
    odd_match2 = sum(1 for i in range(1, len(deltas), 2) if deltas[i] == 0)
    pattern2 = (even_match2 + odd_match2) / len(deltas) if deltas else 0

    best = max(pattern1, pattern2)
    if best < 0.7:
        return None

    return EffectDetection(
        effect='skydive',
        confidence=best,
        params={
            'start_freq_hi': fh[0],
            'rate': 'every_2_frames',
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_tone_portamento(seg, prev_seg=None):
    """Detect tone portamento: freq converges toward a target."""
    if seg.length < 6 or prev_seg is None:
        return None

    freq = seg.freq
    # Check if freq monotonically approaches a stable value
    # The last few frames should be stable (reached target)
    tail = freq[-3:]
    if len(set(tail)) > 2:
        return None  # still moving at end

    target = tail[-1]
    # Check monotonic approach
    if freq[0] < target:
        monotonic = all(freq[i] <= freq[i + 1] for i in range(len(freq) - 1))
    elif freq[0] > target:
        monotonic = all(freq[i] >= freq[i + 1] for i in range(len(freq) - 1))
    else:
        return None  # already at target

    if not monotonic:
        return None

    target_note, _ = freq_to_note(target)
    start_note, _ = freq_to_note(freq[0])

    return EffectDetection(
        effect='tone_portamento',
        confidence=0.8,
        params={
            'start_note': start_note,
            'target_note': target_note,
            'frames_to_reach': next((i for i in range(len(freq)) if freq[i] == target), len(freq)),
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


# --- LOOKUP DETECTOR ---

def detect_freq_table_entry(seg):
    """Map the note's base frequency to the nearest PAL freq table entry."""
    if not seg.freq:
        return None

    # Use the first gate-on frame's frequency
    base_freq = seg.freq[0]
    if base_freq == 0:
        # Try next frame
        base_freq = seg.freq[1] if len(seg.freq) > 1 else 0
    if base_freq == 0:
        return None

    note_idx, cents = freq_to_note(base_freq)
    if note_idx is None:
        return None

    conf = 1.0 if abs(cents) < 5 else (0.8 if abs(cents) < 20 else 0.5)

    return EffectDetection(
        effect='note',
        confidence=conf,
        params={
            'note': note_idx,
            'freq16': base_freq,
            'cents_error': round(cents, 1),
            'octave': note_idx // 12,
            'semitone': note_idx % 12,
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


# --- STATE MACHINE DETECTORS ---

def detect_gate_control(seg):
    """Detect gate on/off timing within a note."""
    gate_bits = [c & 1 for c in seg.ctrl]
    # Find release point (gate goes off)
    release = None
    for i, g in enumerate(gate_bits):
        if not g and i > 0:
            release = i
            break

    sustain = release if release else seg.length

    return EffectDetection(
        effect='gate',
        confidence=1.0,
        params={
            'sustain_frames': sustain,
            'total_frames': seg.length,
            'release_frame': release,
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_hard_restart(seg, prev_seg):
    """Detect hard restart gap between notes."""
    if prev_seg is None or prev_seg.length < 2:
        return None

    # Check last frames of previous segment for test bit ($08) or gate-off gap
    gap = 0
    for i in range(prev_seg.length - 1, max(prev_seg.length - 5, -1), -1):
        if i < 0:
            break
        ctrl = prev_seg.ctrl[i]
        if ctrl & 0x08:  # test bit
            gap += 1
        elif not (ctrl & 0x01):  # gate off
            gap += 1
        else:
            break

    if gap < 1:
        return None

    method = 'test' if any(prev_seg.ctrl[i] & 0x08 for i in range(max(0, prev_seg.length - gap), prev_seg.length)) else 'gate'

    return EffectDetection(
        effect='hard_restart',
        confidence=0.9 if gap >= 2 else 0.6,
        params={
            'gap_frames': gap,
            'method': method,
        },
        frame_start=prev_seg.end - gap, frame_end=seg.start, voice=seg.voice,
    )


def detect_waveform_sequence(seg):
    """Detect multi-frame waveform changes (drum bursts, attack transients)."""
    if seg.length < 2:
        return None

    # Extract waveform upper nibble per frame
    waves = [c & 0xF0 for c in seg.ctrl[:min(8, seg.length)]]
    unique_waves = list(dict.fromkeys(waves))  # preserves order

    if len(unique_waves) < 2:
        return None

    is_drum = 0x80 in unique_waves  # noise waveform present

    return EffectDetection(
        effect='waveform_sequence',
        confidence=0.9,
        params={
            'sequence': [f'${w:02X}' for w in waves],
            'unique_waveforms': [f'${w:02X}' for w in unique_waves],
            'is_drum': is_drum,
            'length': len(waves),
        },
        frame_start=seg.start, frame_end=min(seg.start + 8, seg.end), voice=seg.voice,
    )


# --- CONSTANT DETECTORS ---

def detect_adsr(seg):
    """Read ADSR values from note-on frame."""
    return EffectDetection(
        effect='adsr',
        confidence=1.0,
        params={
            'ad': seg.ad[0],
            'sr': seg.sr[0],
            'attack': seg.ad[0] >> 4,
            'decay': seg.ad[0] & 0xF,
            'sustain': seg.sr[0] >> 4,
            'release': seg.sr[0] & 0xF,
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_waveform_select(seg):
    """Identify the primary waveform used in a note."""
    # Use the most common waveform (excluding first frame which may be transient)
    if seg.length > 2:
        wave_upper = Counter(c & 0xF0 for c in seg.ctrl[1:])
    else:
        wave_upper = Counter(c & 0xF0 for c in seg.ctrl)

    primary = wave_upper.most_common(1)[0][0]
    name = WAVEFORM_NAMES.get(primary, f'unknown_${primary:02X}')

    return EffectDetection(
        effect='waveform',
        confidence=1.0,
        params={
            'waveform_byte': primary,
            'name': name,
            'ring': bool(seg.ctrl[0] & 0x04),
            'sync': bool(seg.ctrl[0] & 0x02),
        },
        frame_start=seg.start, frame_end=seg.end, voice=seg.voice,
    )


def detect_filter_routing(trace, frame):
    """Read filter routing at a specific frame."""
    if frame >= trace.n_frames:
        return None

    # $D417 = register index 23 (res_route)
    res_route = trace.frames[frame][23]
    # $D418 = register index 24 (vol_mode)
    vol_mode = trace.frames[frame][24]

    return EffectDetection(
        effect='filter',
        confidence=1.0,
        params={
            'resonance': res_route >> 4,
            'voice1': bool(res_route & 1),
            'voice2': bool(res_route & 2),
            'voice3': bool(res_route & 4),
            'filter_type': (vol_mode >> 4) & 0x7,
            'volume': vol_mode & 0xF,
        },
        frame_start=frame, frame_end=frame + 1, voice=-1,
    )


# --- TEMPO DETECTOR ---

def detect_tempo(trace, voice=0):
    """Detect tempo from gate-on timing via autocorrelation."""
    segs = trace.gate_segments(voice)
    if len(segs) < 4:
        return None

    gate_ons = [s for s, e in segs]
    intervals = [gate_ons[i + 1] - gate_ons[i] for i in range(len(gate_ons) - 1)]

    if not intervals:
        return None

    # Find GCD of intervals as tempo candidate
    from math import gcd
    from functools import reduce
    g = reduce(gcd, intervals)

    # Score: what fraction of intervals are multiples of g?
    multiples = sum(1 for iv in intervals if iv % g == 0)
    consistency = multiples / len(intervals)

    return EffectDetection(
        effect='tempo',
        confidence=consistency,
        params={
            'frames_per_tick': g,
            'bpm': round(50 * 60 / g) if g > 0 else 0,
            'tick_hz': round(50 / g, 2) if g > 0 else 0,
            'intervals_sampled': len(intervals),
        },
        frame_start=0, frame_end=trace.n_frames, voice=voice,
    )


# --- TOP-LEVEL ORCHESTRATOR ---

def analyze_note(seg, prev_seg=None):
    """Run all detectors on a single note segment.

    Returns list of EffectDetections, ordered by importance.
    """
    results = []

    # Always: base note, ADSR, waveform, gate
    det = detect_freq_table_entry(seg)
    if det:
        results.append(det)

    results.append(detect_adsr(seg))
    results.append(detect_waveform_select(seg))
    results.append(detect_gate_control(seg))

    # State detectors
    det = detect_hard_restart(seg, prev_seg)
    if det:
        results.append(det)

    det = detect_waveform_sequence(seg)
    if det:
        results.append(det)

    # Cumulative detectors (specific before general)
    det = detect_drum_freq_slide(seg)
    if det:
        results.append(det)
        return results  # drum slide is the whole effect for this note

    det = detect_skydive(seg)
    if det:
        results.append(det)

    det = detect_tone_portamento(seg, prev_seg)
    if det:
        results.append(det)

    det = detect_portamento(seg)
    if det:
        results.append(det)

    # Periodic detectors
    det = detect_arpeggio(seg)
    if det:
        results.append(det)
    else:
        # Only check vibrato if no arpeggio
        det = detect_vibrato(seg)
        if det:
            results.append(det)

    # PWM (check direct first, sweep if not direct)
    det = detect_pwm_direct(seg)
    if det:
        results.append(det)
    else:
        det = detect_pwm_sweep(seg)
        if det:
            results.append(det)

    return results


def analyze_effects(trace):
    """Run all detectors on a full subtune trace.

    Returns dict with:
      'tempo': EffectDetection
      'filter': EffectDetection or None
      'voices': [
        {'notes': [{'segment': (start, end), 'effects': [EffectDetection, ...]}, ...]},
        ...
      ]
    """
    segments = build_segments(trace)

    result = {
        'tempo': detect_tempo(trace),
        'filter': detect_filter_routing(trace, 0),
        'voices': [],
    }

    # Collect all unique effects across the song
    effect_catalog = Counter()

    for v in range(3):
        voice_data = {'notes': []}
        prev_seg = None
        for seg in segments[v]:
            effects = analyze_note(seg, prev_seg)
            voice_data['notes'].append({
                'segment': (seg.start, seg.end),
                'length': seg.length,
                'effects': effects,
            })
            for e in effects:
                effect_catalog[e.effect] += 1
            prev_seg = seg

        # Check for filter modulation on this voice
        if segments[v]:
            filt = detect_filter_modulation(trace, segments[v][0].start,
                                            segments[v][-1].end, voice=v)
            if filt:
                voice_data['filter_mod'] = filt

        result['voices'].append(voice_data)

    result['effect_summary'] = dict(effect_catalog)
    return result


def print_analysis(result):
    """Pretty-print analysis results."""
    print("=== Effect Analysis ===\n")

    if result['tempo']:
        t = result['tempo']
        print(f"Tempo: {t.params['frames_per_tick']} frames/tick "
              f"({t.params['tick_hz']} Hz, ~{t.params['bpm']} BPM) "
              f"[{t.confidence:.0%}]")

    if result['filter']:
        f = result['filter']
        ftype = {0: 'off', 1: 'LP', 2: 'BP', 3: 'LP+BP', 4: 'HP', 5: 'HP+LP', 6: 'HP+BP', 7: 'notch'}
        print(f"Filter: {ftype.get(f.params['filter_type'], '?')}, "
              f"res={f.params['resonance']}, "
              f"routing={''.join(str(v+1) for v in range(3) if f.params[f'voice{v+1}'])}")
        print(f"Volume: {f.params['volume']}")

    print()

    for v in range(3):
        voice = result['voices'][v]
        notes = voice['notes']
        print(f"--- Voice {v + 1}: {len(notes)} notes ---")

        # Summarize effects used
        effect_counts = Counter()
        for n in notes:
            for e in n['effects']:
                if e.effect not in ('note', 'adsr', 'waveform', 'gate'):
                    effect_counts[e.effect] += 1

        if effect_counts:
            print(f"  Effects: {', '.join(f'{e}({c})' for e, c in effect_counts.most_common())}")

        if 'filter_mod' in voice:
            fm = voice['filter_mod']
            print(f"  Filter mod: {fm.params['rate_hz']} Hz, "
                  f"range {fm.params['min_cutoff']}-{fm.params['max_cutoff']}")

        # Show first 5 notes in detail
        for i, n in enumerate(notes[:5]):
            effects_str = ' + '.join(str(e) for e in n['effects']
                                     if e.effect not in ('gate',))
            print(f"  Note {i} (f{n['segment'][0]}-f{n['segment'][1]}, "
                  f"{n['length']}fr): {effects_str}")

        if len(notes) > 5:
            print(f"  ... ({len(notes) - 5} more notes)")

        print()

    print(f"Effect summary: {result['effect_summary']}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 effect_detect.py <file.sid> [subtune]")
        sys.exit(1)

    from ground_truth import capture_sid

    sid_path = sys.argv[1]
    subtune = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    max_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 1500

    result = capture_sid(sid_path, subtunes=[subtune], max_frames=max_frames)
    if not result.subtunes:
        print("No subtune captured")
        sys.exit(1)

    analysis = analyze_effects(result.subtunes[0])
    print_analysis(analysis)
