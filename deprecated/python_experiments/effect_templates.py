"""
effect_templates.py — Template-matching approach to SID engine behavior extraction.

Instead of understanding engine CODE, we observe engine BEHAVIOR and match it against a
library of known effect templates. Each template defines:
  - The signal(s) to observe (register field or derived value)
  - A DETECTOR function: (frames_dict) -> (params, confidence) or None
  - Human-readable metadata

This is complementary to effect_detect.py (which uses ad-hoc per-detector logic).
Here the templates are data-driven: you add a new effect by registering a new template,
not by writing ad-hoc code paths.

Usage:
    from ground_truth import capture_sid
    from effect_templates import match_all_templates, print_template_matches

    result = capture_sid('path/to/song.sid', subtunes=[1])
    trace = result.subtunes[0]
    matches = match_all_templates(trace)
    print_template_matches(matches)
"""

import math
import os
import sys
from collections import Counter, namedtuple
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Any

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# PAL frequency table (standard C64 PAL tuning, 96 entries)
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

# --- Shared math utilities ---

def _dft_magnitude(signal, sample_rate=50.0):
    """Return list of (freq_hz, magnitude) for positive frequencies."""
    N = len(signal)
    if N < 4:
        return []
    mean = sum(signal) / N
    x = [v - mean for v in signal]
    out = []
    for k in range(1, N // 2 + 1):
        re = im = 0.0
        w = 2.0 * math.pi * k / N
        for n in range(N):
            re += x[n] * math.cos(w * n)
            im += x[n] * math.sin(w * n)
        out.append((k * sample_rate / N, math.sqrt(re * re + im * im) / N))
    return out


def _dominant_peak(signal, min_hz, max_hz, sample_rate=50.0):
    """Return (peak_hz, peak_mag, total_energy)."""
    spec = _dft_magnitude(signal, sample_rate)
    if not spec:
        return 0.0, 0.0, 0.0
    total = sum(m for _, m in spec)
    band = [(f, m) for f, m in spec if min_hz <= f <= max_hz]
    if not band:
        return 0.0, 0.0, total
    best_f, best_m = max(band, key=lambda x: x[1])
    return best_f, best_m, total


def _freq_to_note(freq16):
    """Return (note_index, cents_error) or (None, None)."""
    if freq16 == 0:
        return None, None
    best_idx = min(range(len(FREQ_PAL)), key=lambda i: abs(freq16 - FREQ_PAL[i]))
    ratio = freq16 / FREQ_PAL[best_idx] if FREQ_PAL[best_idx] else 0
    cents = 1200 * math.log2(ratio) if ratio > 0 else 0
    return best_idx, cents


def _modal_delta(signal):
    """Return (dominant_nonzero_delta, consistency_ratio)."""
    if len(signal) < 3:
        return 0, 0.0
    deltas = [signal[i + 1] - signal[i] for i in range(len(signal) - 1)]
    non_zero = [d for d in deltas if d != 0]
    if not non_zero:
        return 0, 1.0
    best, cnt = Counter(non_zero).most_common(1)[0]
    return best, cnt / len(non_zero)


def _signed8(x):
    return x if x < 128 else x - 256


# --- Data structures ---

@dataclass
class TemplateMatch:
    """Result of applying one effect template to a register window."""
    template_name: str
    description: str
    confidence: float        # 0.0 – 1.0
    params: Dict[str, Any]  # template-specific extracted parameters
    frame_start: int
    frame_end: int
    voice: int               # 0-2, or -1 for global

    def __repr__(self):
        p = ', '.join(f'{k}={v}' for k, v in self.params.items())
        return (f'[{self.template_name}] {self.description} '
                f'({p}) conf={self.confidence:.0%} '
                f'frames={self.frame_start}-{self.frame_end} v={self.voice}')


@dataclass
class EffectTemplate:
    """
    Declarative effect template.

    name        — short identifier, e.g. 'octave_arp'
    description — human-readable, e.g. 'Octave arpeggio (freq doubles each step)'
    min_frames  — minimum segment length required
    detect      — callable(frames_dict) -> (params, confidence) or None
                  frames_dict keys: 'freq', 'freq_hi', 'freq_lo', 'pw', 'ctrl', 'ad', 'sr'
                  Each value is a list of ints, one per frame.
    """
    name: str
    description: str
    min_frames: int
    detect: Callable


# --- Helper: extract per-voice signal arrays from a trace ---

def _extract_voice_signals(trace, voice, frame_start, frame_end):
    """Return a dict of signal arrays for one voice over [frame_start, frame_end)."""
    voff = voice * 7
    frames = []
    for f in range(frame_start, min(frame_end, trace.n_frames)):
        row = trace.frames[f]
        frames.append(row)

    def col(offset):
        return [row[voff + offset] for row in frames]

    freq_lo = col(0)
    freq_hi = col(1)
    freq    = [(hi << 8) | lo for hi, lo in zip(freq_hi, freq_lo)]
    pw_lo   = col(2)
    pw_hi   = col(3)
    pw      = [(hi << 8) | lo for hi, lo in zip(pw_hi, pw_lo)]
    ctrl    = col(4)
    ad      = col(5)
    sr      = col(6)

    # Filter registers (global, not per voice)
    fc_lo    = [row[21] for row in frames]
    fc_hi    = [row[22] for row in frames]
    cutoff   = [(hi << 3) | (lo & 0x07) for hi, lo in zip(fc_hi, fc_lo)]
    res_route = [row[23] for row in frames]
    vol_mode  = [row[24] for row in frames]

    return dict(
        freq=freq, freq_hi=freq_hi, freq_lo=freq_lo,
        pw=pw, pw_lo=pw_lo, pw_hi=pw_hi,
        ctrl=ctrl, ad=ad, sr=sr,
        cutoff=cutoff, fc_lo=fc_lo, fc_hi=fc_hi,
        res_route=res_route, vol_mode=vol_mode,
    )


# ============================================================
# EFFECT TEMPLATES (the library)
# ============================================================

def _detect_octave_arp(sigs):
    """
    Octave arpeggio: freq alternates between F and ~2*F each step.
    The ratio between the two most common freq_hi values is ~2:1 (one octave).
    """
    freq = sigs['freq']
    if len(freq) < 4:
        return None

    # Map to nearest note indices
    notes = []
    for f in freq:
        if f == 0:
            continue
        idx, cents = _freq_to_note(f)
        if idx is not None and abs(cents) < 30:
            notes.append(idx)
    if len(notes) < 4:
        return None

    unique_notes = sorted(set(notes))
    if len(unique_notes) < 2 or len(unique_notes) > 4:
        return None

    # Discreteness check: arpeggio snaps between few values
    disc = len(set(notes)) / len(notes)
    if disc > 0.35:
        return None

    # Check for octave intervals (12 semitones apart)
    octave_pairs = []
    for i, a in enumerate(unique_notes):
        for b in unique_notes[i + 1:]:
            if (b - a) % 12 == 0:
                octave_pairs.append((a, b))

    if not octave_pairs:
        return None

    # Measure periodicity via DFT
    peak_hz, peak_mag, total = _dominant_peak(notes, 8.0, 25.0)
    if total == 0 or peak_mag / total < 0.15:
        return None

    pattern_len = round(50.0 / peak_hz) if peak_hz > 0 else 0
    return {
        'notes': unique_notes,
        'octave_pairs': octave_pairs,
        'rate_hz': round(peak_hz, 1),
        'pattern_len': pattern_len,
    }, min(1.0, (peak_mag / total) * 2.5)


TEMPLATE_OCTAVE_ARP = EffectTemplate(
    name='octave_arp',
    description='Octave arpeggio (freq steps by 12 semitones)',
    min_frames=4,
    detect=_detect_octave_arp,
)


def _detect_vibrato(sigs):
    """
    Vibrato: freq oscillates sinusoidally around a stable center note.
    Characteristics:
      - Many unique freq values (not discrete like arpeggio)
      - Strong DFT peak in 2-12 Hz band
      - Smooth transitions (no large jumps)
    """
    freq = sigs['freq']
    if len(freq) < 10:
        return None

    # Exclude silence
    active = [f for f in freq if f > 0]
    if len(active) < 10:
        return None

    # Not discrete (vibrato is smooth, arpeggio snaps)
    disc = len(set(active)) / len(active)
    if disc < 0.3:
        return None

    # Check transitions are small: no abrupt jumps > 1 octave
    diffs = [abs(active[i + 1] - active[i]) for i in range(len(active) - 1)]
    max_jump = max(diffs) if diffs else 0
    center = sum(active) / len(active)
    if center == 0:
        return None
    if max_jump > center * 0.5:  # jump > half an octave = not vibrato
        return None

    # DFT: vibrato rate is typically 4-8 Hz
    peak_hz, peak_mag, total = _dominant_peak(freq, 2.0, 12.0)
    if total == 0 or peak_mag < 1.0:
        return None

    purity = peak_mag / total
    if purity < 0.15:
        return None

    depth = max(active) - min(active)
    center_note, cents = _freq_to_note(int(center))

    # Depth in cents (approximate)
    if center > 0 and depth > 0:
        depth_cents = round(1200 * math.log2((center + depth / 2) / (center - depth / 2 + 1e-9)))
    else:
        depth_cents = 0

    return {
        'rate_hz': round(peak_hz, 1),
        'depth_freq': depth,
        'depth_cents': depth_cents,
        'center_note': center_note,
        'center_freq': int(center),
    }, min(1.0, purity * 2.5)


TEMPLATE_VIBRATO = EffectTemplate(
    name='vibrato',
    description='Vibrato (sinusoidal freq oscillation around center note)',
    min_frames=10,
    detect=_detect_vibrato,
)


def _detect_pw_sweep(sigs):
    """
    PW sweep: pulse width increases or decreases by constant delta per frame.
    The low byte changes monotonically (linear ramp up or down).
    High byte may carry over.
    """
    pw_lo = sigs['pw_lo']
    if len(pw_lo) < 4:
        return None

    # Compute signed deltas (handle 8-bit wrap)
    deltas = [_signed8((pw_lo[i + 1] - pw_lo[i]) & 0xFF)
              for i in range(len(pw_lo) - 1)]
    non_zero = [d for d in deltas if d != 0]
    if not non_zero:
        return None

    best_delta, cnt = Counter(non_zero).most_common(1)[0]
    consistency = cnt / len(non_zero)
    if consistency < 0.65:
        return None

    pw = sigs['pw']
    direction = 'up' if best_delta > 0 else 'down'

    return {
        'speed': best_delta,
        'direction': direction,
        'initial_pw': pw[0],
        'final_pw': pw[-1],
        'consistency': round(consistency, 2),
    }, consistency


TEMPLATE_PW_SWEEP = EffectTemplate(
    name='pw_sweep',
    description='Pulse width linear sweep (constant PW delta per frame)',
    min_frames=4,
    detect=_detect_pw_sweep,
)


def _detect_hard_restart(sigs):
    """
    Hard restart: ADSR is zeroed and/or test bit is set 1-3 frames before gate-off,
    then a new note fires. Appears at the tail of a note segment.
    We look at the last 4 frames for: ctrl & $08 (test bit) set, or sudden AD=00 SR=00.
    """
    ctrl = sigs['ctrl']
    ad   = sigs['ad']
    sr   = sigs['sr']
    n    = len(ctrl)
    if n < 3:
        return None

    # Look at last 5 frames
    tail_len = min(5, n)
    tail_ctrl = ctrl[n - tail_len:]
    tail_ad   = ad[n - tail_len:]
    tail_sr   = sr[n - tail_len:]

    # Test bit in tail?
    test_frames = sum(1 for c in tail_ctrl if c & 0x08)
    # ADSR zero in tail?
    adsr_zero_frames = sum(1 for a, s in zip(tail_ad, tail_sr) if a == 0 and s == 0)
    # Gate off in tail?
    gate_off_frames = sum(1 for c in tail_ctrl if not (c & 0x01))

    hr_score = max(test_frames, adsr_zero_frames)
    if hr_score < 1 and gate_off_frames < 2:
        return None

    method = []
    if test_frames >= 1:
        method.append('test_bit')
    if adsr_zero_frames >= 1:
        method.append('adsr_zero')

    return {
        'gap_frames': hr_score or gate_off_frames,
        'method': '+'.join(method) if method else 'gate_off',
        'tail_ctrl': [f'${c:02X}' for c in tail_ctrl],
    }, 0.9 if hr_score >= 2 else (0.7 if hr_score == 1 else 0.5)


TEMPLATE_HARD_RESTART = EffectTemplate(
    name='hard_restart',
    description='Hard restart (test bit / ADSR zeroed before note end)',
    min_frames=3,
    detect=_detect_hard_restart,
)


def _detect_drum_burst(sigs):
    """
    Drum burst: noise waveform ($80/$81) on the first 1-4 frames, possibly
    followed by silence or a different waveform. Freq_hi typically starts high
    and decreases (pitch slide downward).
    """
    ctrl = sigs['ctrl']
    freq_hi = sigs['freq_hi']
    if len(ctrl) < 2:
        return None

    # Must open with noise waveform
    if not (ctrl[0] & 0x80):
        return None

    # Count consecutive noise frames
    noise_frames = 0
    for c in ctrl:
        if c & 0x80:
            noise_frames += 1
        else:
            break

    # Check for freq_hi slide (decreasing)
    if len(freq_hi) >= 2:
        delta, consistency = _modal_delta(freq_hi[:min(noise_frames + 2, len(freq_hi))])
    else:
        delta, consistency = 0, 0.0

    has_slide = delta < 0 and consistency >= 0.5

    if noise_frames < 1:
        return None

    return {
        'noise_frames': noise_frames,
        'start_freq_hi': freq_hi[0],
        'has_pitch_slide': has_slide,
        'slide_delta': delta if has_slide else 0,
        'total_length': len(ctrl),
    }, 0.95 if noise_frames >= 2 else 0.7


TEMPLATE_DRUM_BURST = EffectTemplate(
    name='drum_burst',
    description='Drum burst (noise waveform at note start, optional freq slide)',
    min_frames=2,
    detect=_detect_drum_burst,
)


def _detect_portamento(sigs):
    """
    Portamento: freq_hi changes by a constant signed delta each frame,
    sliding monotonically from one note to another over several frames.
    Not an arpeggio (too many unique values) and not vibrato (monotonic).
    """
    freq = sigs['freq']
    freq_hi = sigs['freq_hi']
    if len(freq) < 4:
        return None

    delta, consistency = _modal_delta(freq_hi)
    if delta == 0 or consistency < 0.55:
        return None

    # Monotonic test on full freq (not just hi byte)
    if delta > 0:
        mono = sum(1 for i in range(len(freq) - 1) if freq[i + 1] >= freq[i])
    else:
        mono = sum(1 for i in range(len(freq) - 1) if freq[i + 1] <= freq[i])
    mono_ratio = mono / max(1, len(freq) - 1)
    if mono_ratio < 0.6:
        return None

    start_note, _ = _freq_to_note(freq[0])
    end_note, _ = _freq_to_note(freq[-1])

    return {
        'direction': 'up' if delta > 0 else 'down',
        'speed': abs(delta),
        'start_note': start_note,
        'end_note': end_note,
        'consistency': round(consistency, 2),
    }, min(1.0, consistency * mono_ratio * 1.5)


TEMPLATE_PORTAMENTO = EffectTemplate(
    name='portamento',
    description='Portamento (monotonic freq slide between notes)',
    min_frames=4,
    detect=_detect_portamento,
)


def _detect_filter_sweep(sigs):
    """
    Filter sweep: cutoff frequency increases or decreases linearly.
    Distinct from filter modulation (which is periodic oscillation).
    """
    cutoff = sigs['cutoff']
    if len(cutoff) < 4:
        return None

    # Remove frames where filter is not active
    fc_hi = sigs['fc_hi']
    if len(set(fc_hi)) < 2:
        return None

    delta, consistency = _modal_delta(fc_hi)
    if delta == 0 or consistency < 0.55:
        return None

    # Must be at least somewhat monotonic
    if delta > 0:
        mono = sum(1 for i in range(len(fc_hi) - 1) if fc_hi[i + 1] >= fc_hi[i])
    else:
        mono = sum(1 for i in range(len(fc_hi) - 1) if fc_hi[i + 1] <= fc_hi[i])
    mono_ratio = mono / max(1, len(fc_hi) - 1)
    if mono_ratio < 0.55:
        return None

    return {
        'direction': 'up' if delta > 0 else 'down',
        'speed': abs(delta),
        'cutoff_start': fc_hi[0],
        'cutoff_end': fc_hi[-1],
        'consistency': round(consistency, 2),
    }, min(1.0, consistency * mono_ratio * 1.5)


TEMPLATE_FILTER_SWEEP = EffectTemplate(
    name='filter_sweep',
    description='Filter cutoff linear sweep',
    min_frames=4,
    detect=_detect_filter_sweep,
)


def _detect_chord_arp(sigs):
    """
    Chord arpeggio: freq cycles through 3-4 notes forming a musical chord
    (intervals of 3-5 semitones = minor/major third, fifth).
    """
    freq = sigs['freq']
    if len(freq) < 6:
        return None

    notes = []
    for f in freq:
        if f == 0:
            continue
        idx, cents = _freq_to_note(f)
        if idx is not None and abs(cents) < 25:
            notes.append(idx)
    if len(notes) < 6:
        return None

    unique_notes = sorted(set(notes))
    n_unique = len(unique_notes)
    if n_unique < 2 or n_unique > 4:
        return None

    disc = n_unique / len(notes)
    if disc > 0.35:
        return None

    # Check intervals — chord = 3rd (3-4 st), 5th (7 st), octave (12 st)
    intervals = [unique_notes[i + 1] - unique_notes[i] for i in range(len(unique_notes) - 1)]
    chord_intervals = {3, 4, 7, 12}
    chord_match = sum(1 for iv in intervals if iv in chord_intervals)
    if chord_match == 0:
        return None

    peak_hz, peak_mag, total = _dominant_peak(notes, 4.0, 25.0)
    if total == 0 or peak_mag / total < 0.12:
        return None

    chord_type = 'unknown'
    if intervals == [4, 3]:
        chord_type = 'major'
    elif intervals == [3, 4]:
        chord_type = 'minor'
    elif intervals == [4, 3, 3]:
        chord_type = 'dominant7'
    elif intervals == [3, 4, 3]:
        chord_type = 'minor7'
    elif 12 in intervals and n_unique == 2:
        chord_type = 'octave'
    elif set(intervals) <= chord_intervals:
        chord_type = 'chord'

    return {
        'notes': unique_notes,
        'intervals': intervals,
        'chord_type': chord_type,
        'rate_hz': round(peak_hz, 1),
        'n_steps': n_unique,
    }, min(1.0, (peak_mag / total) * 2.5 * (chord_match / len(intervals)))


TEMPLATE_CHORD_ARP = EffectTemplate(
    name='chord_arp',
    description='Chord arpeggio (notes form a 3rd/5th/7th interval)',
    min_frames=6,
    detect=_detect_chord_arp,
)


def _detect_pw_oscillate(sigs):
    """
    PW oscillation: pulse width oscillates back and forth (triangle wave LFO).
    Direction reverses at least twice, and DFT shows a clear periodic peak.
    """
    pw = sigs['pw']
    if len(pw) < 8:
        return None

    deltas = [pw[i + 1] - pw[i] for i in range(len(pw) - 1)]
    # Count sign changes
    reversals = 0
    for i in range(1, len(deltas)):
        if deltas[i] != 0 and deltas[i - 1] != 0:
            if (deltas[i] > 0) != (deltas[i - 1] > 0):
                reversals += 1

    if reversals < 2:
        return None

    peak_hz, peak_mag, total = _dominant_peak(pw, 0.5, 15.0)
    if total == 0 or peak_mag / total < 0.10:
        return None

    abs_deltas = sorted(abs(d) for d in deltas if d != 0)
    speed = abs_deltas[len(abs_deltas) // 2] if abs_deltas else 0

    return {
        'rate_hz': round(peak_hz, 2),
        'speed': speed,
        'min_pw': min(pw),
        'max_pw': max(pw),
        'reversals': reversals,
    }, min(1.0, peak_mag / total * 2.5)


TEMPLATE_PW_OSCILLATE = EffectTemplate(
    name='pw_oscillate',
    description='Pulse width oscillation (triangle LFO on PW)',
    min_frames=8,
    detect=_detect_pw_oscillate,
)


# --- Registry ---

ALL_TEMPLATES: List[EffectTemplate] = [
    TEMPLATE_OCTAVE_ARP,
    TEMPLATE_CHORD_ARP,
    TEMPLATE_VIBRATO,
    TEMPLATE_PW_SWEEP,
    TEMPLATE_PW_OSCILLATE,
    TEMPLATE_HARD_RESTART,
    TEMPLATE_DRUM_BURST,
    TEMPLATE_PORTAMENTO,
    TEMPLATE_FILTER_SWEEP,
]


# --- Gate segment extraction ---

def _gate_segments(trace, voice):
    """Return list of (start_frame, end_frame) for gate-on periods."""
    voff = voice * 7 + 4  # ctrl register
    segs = []
    in_gate = False
    start = 0
    for f in range(trace.n_frames):
        gate = bool(trace.frames[f][voff] & 0x01)
        if gate and not in_gate:
            in_gate = True
            start = f
        elif not gate and in_gate:
            in_gate = False
            segs.append((start, f))
    if in_gate:
        segs.append((start, trace.n_frames))
    return segs


# --- Core matching function ---

def match_template(template, sigs, frame_start, frame_end, voice):
    """Apply one template to pre-extracted signal arrays.

    Returns a TemplateMatch or None.
    """
    if len(sigs.get('freq', [])) < template.min_frames:
        return None

    result = template.detect(sigs)
    if result is None:
        return None

    params, confidence = result
    return TemplateMatch(
        template_name=template.name,
        description=template.description,
        confidence=confidence,
        params=params,
        frame_start=frame_start,
        frame_end=frame_end,
        voice=voice,
    )


def match_all_templates(trace, templates=None, min_confidence=0.4):
    """Run all templates against every note segment in the trace.

    Returns:
        dict with:
          'global_filter': TemplateMatch or None (filter sweep over full song)
          'voices': list of 3 dicts, each with:
            'notes': list of {'frames': (start, end), 'matches': [TemplateMatch, ...]}
            'voice_level': [TemplateMatch, ...]  (whole-voice effects)
    """
    if templates is None:
        templates = ALL_TEMPLATES

    result = {
        'global_filter': None,
        'voices': [],
    }

    # Global filter sweep check over first 500 frames
    n_frames = min(trace.n_frames, 500)
    if n_frames >= 4:
        # Use voice 0 for filter signals
        gsigs = _extract_voice_signals(trace, 0, 0, n_frames)
        for tmpl in templates:
            if tmpl.name == 'filter_sweep':
                m = match_template(tmpl, gsigs, 0, n_frames, -1)
                if m and m.confidence >= min_confidence:
                    result['global_filter'] = m
                break

    for v in range(3):
        segs = _gate_segments(trace, v)
        voice_data = {'notes': [], 'voice_level': []}

        for seg_start, seg_end in segs:
            seg_len = seg_end - seg_start
            if seg_len < 2:
                continue

            sigs = _extract_voice_signals(trace, v, seg_start, seg_end)
            note_matches = []

            for tmpl in templates:
                if tmpl.name == 'filter_sweep':
                    continue  # handled globally
                if seg_len < tmpl.min_frames:
                    continue
                m = match_template(tmpl, sigs, seg_start, seg_end, v)
                if m and m.confidence >= min_confidence:
                    note_matches.append(m)

            # Sort by confidence descending
            note_matches.sort(key=lambda x: -x.confidence)

            voice_data['notes'].append({
                'frames': (seg_start, seg_end),
                'length': seg_len,
                'matches': note_matches,
            })

        result['voices'].append(voice_data)

    return result


def summarize_matches(result):
    """Return a summary: which effects appear and how often, per voice."""
    summary = {'global': [], 'voices': []}

    if result['global_filter']:
        summary['global'].append(result['global_filter'])

    for v, vdata in enumerate(result['voices']):
        voice_summary = Counter()
        for note in vdata['notes']:
            for m in note['matches']:
                voice_summary[m.template_name] += 1
        summary['voices'].append({
            'voice': v,
            'effect_counts': dict(voice_summary),
            'n_notes': len(vdata['notes']),
        })

    return summary


def print_template_matches(result, max_notes=5):
    """Pretty-print template matching results."""
    print("=== Effect Template Matches ===\n")

    if result['global_filter']:
        gf = result['global_filter']
        print(f"Global filter sweep: {gf.params}")
        print()

    for v, vdata in enumerate(result['voices']):
        notes = vdata['notes']
        if not notes:
            continue

        all_effects = Counter()
        for note in notes:
            for m in note['matches']:
                all_effects[m.template_name] += 1

        print(f"--- Voice {v + 1}: {len(notes)} notes ---")
        if all_effects:
            print(f"  Effects found: {dict(all_effects.most_common())}")

        shown = 0
        for note in notes:
            if not note['matches']:
                continue
            if shown >= max_notes:
                break
            print(f"  Note f{note['frames'][0]}-{note['frames'][1]} "
                  f"({note['length']}fr):")
            for m in note['matches']:
                p = ', '.join(f'{k}={v}' for k, v in m.params.items()
                              if k not in ('tail_ctrl',))
                print(f"    [{m.template_name}] {p} ({m.confidence:.0%})")
            shown += 1

        if len(notes) > shown:
            remaining_with_effects = sum(1 for n in notes[shown:]
                                         if n['matches'])
            if remaining_with_effects:
                print(f"  ... ({remaining_with_effects} more notes with effects)")
        print()

    summ = summarize_matches(result)
    print("Effect summary by voice:")
    for vs in summ['voices']:
        if vs['effect_counts']:
            print(f"  Voice {vs['voice'] + 1}: {vs['effect_counts']}")


# --- CLI entry point ---

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 effect_templates.py <file.sid> [subtune] [max_frames]")
        sys.exit(1)

    from ground_truth import capture_sid

    sid_path = sys.argv[1]
    subtune = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    max_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 2000

    print(f"Capturing {sid_path} subtune {subtune} ({max_frames} frames)...")
    result = capture_sid(sid_path, subtunes=[subtune], max_frames=max_frames)

    if not result.subtunes:
        print("No subtune captured")
        sys.exit(1)

    trace = result.subtunes[0]
    print(f"Captured {trace.n_frames} frames\n")

    matches = match_all_templates(trace)
    print_template_matches(matches)
