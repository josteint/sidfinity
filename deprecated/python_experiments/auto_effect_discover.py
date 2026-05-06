#!/usr/bin/env python3
"""
auto_effect_discover.py — Automatic effect discovery from SID register traces.

Method: compare the ACTUAL register trace against a "naive" baseline
(notes + ADSR only, no effects) and classify every deviation.

This is the systematic alternative to hand-coded detectors: instead of
enumerating 17 known effects, we let the data tell us what effects exist.

Algorithm:
  1. Capture actual register trace via py65
  2. Build naive baseline: for each voice, find "base note" at gate-on,
     hold it constant, hold PW constant, hold ctrl = init waveform | gate
  3. Compute per-register per-frame residuals (actual - baseline)
  4. Classify residuals by mathematical structure:
     - freq_residual periodic     → vibrato or arpeggio
     - freq_residual monotonic    → portamento / skydive / drum slide
     - freq_residual discrete     → arpeggio
     - pw_residual linear         → PWM sweep
     - pw_residual oscillating    → PWM bidirectional
     - ctrl_residual pattern      → W-program / waveform sequence
  5. Extract parameters for each discovered effect

Usage:
    python3 src/auto_effect_discover.py <file.sid> [subtune] [n_frames]

    Or import:
        from auto_effect_discover import discover_effects
        effects = discover_effects('path/to/song.sid', subtune=1, n_frames=200)
"""

import math
import os
import sys
import struct
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'tools', 'py65_lib'))

# ---- SID register layout ----
# Per-voice offsets (each voice = 7 bytes)
# 0=freq_lo, 1=freq_hi, 2=pw_lo, 3=pw_hi, 4=ctrl, 5=ad, 6=sr
VOICE_REGS = 7
N_VOICES = 3

# PAL frequency table (96 entries, standard C64 PAL tuning)
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

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def freq_to_note(freq16):
    """Map 16-bit SID frequency to nearest PAL note index. Returns (idx, cents) or (None, None)."""
    if freq16 == 0:
        return None, None
    best_idx = min(range(len(FREQ_PAL)), key=lambda i: abs(freq16 - FREQ_PAL[i]))
    ratio = freq16 / FREQ_PAL[best_idx] if FREQ_PAL[best_idx] > 0 else 1.0
    cents = 1200.0 * math.log2(ratio) if ratio > 0 else 0.0
    return best_idx, cents


def note_name(idx):
    if idx is None:
        return '?'
    octave = idx // 12
    semitone = idx % 12
    return f'{NOTE_NAMES[semitone]}{octave}'


def real_dft(signal, sample_rate=50.0, min_hz=0.5, max_hz=25.0):
    """Compute DFT, return list of (freq_hz, magnitude) for bins in [min_hz, max_hz]."""
    N = len(signal)
    if N < 4:
        return []
    mean = sum(signal) / N
    x = [s - mean for s in signal]
    results = []
    for k in range(1, N // 2 + 1):
        fhz = k * sample_rate / N
        if fhz < min_hz or fhz > max_hz:
            continue
        re = im = 0.0
        w = 2.0 * math.pi * k / N
        for n in range(N):
            re += x[n] * math.cos(w * n)
            im += x[n] * math.sin(w * n)
        mag = math.sqrt(re * re + im * im) / N
        results.append((fhz, mag))
    return results


def dominant_peak(spectrum):
    """Return (freq_hz, magnitude, energy_fraction) for the strongest spectral peak."""
    if not spectrum:
        return 0.0, 0.0, 0.0
    total = sum(m for _, m in spectrum)
    best_f, best_m = max(spectrum, key=lambda x: x[1])
    return best_f, best_m, best_m / total if total > 0 else 0.0


# ---- Capture ----

def load_sid(sid_path):
    with open(sid_path, 'rb') as f:
        data = f.read()
    if data[:4] not in (b'PSID', b'RSID'):
        raise ValueError(f'Not a SID file: {sid_path}')
    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    n_songs = struct.unpack('>H', data[14:16])[0]
    code = data[header_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code
    mem = bytearray(65536)
    end = min(load_addr + len(binary), 65536)
    mem[load_addr:end] = binary[:end - load_addr]
    return mem, init_addr, play_addr, load_addr, n_songs


def capture_frames(sid_path, subtune=1, n_frames=200):
    """Run the SID via py65 for n_frames. Returns list of 25-byte register tuples."""
    from py65.devices.mpu6502 import MPU

    mem, init_addr, play_addr, load_addr, n_songs = load_sid(sid_path)

    mpu = MPU()
    mpu.memory = bytearray(mem)
    mpu.memory[0xFFF0] = 0x00  # BRK sentinel

    # Init with (subtune-1) in A
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = subtune - 1
    for _ in range(200000):
        if mpu.memory[mpu.pc] == 0x00:
            break
        mpu.step()

    frames = []
    ret_addr = 0xFFF0 - 1
    for _ in range(n_frames):
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr
        for _ in range(100000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()
        regs = tuple(mpu.memory[0xD400 + i] for i in range(25))
        frames.append(regs)

    return frames


# ---- Baseline construction ----

@dataclass
class NoteEvent:
    """A gate-on event with its base parameters."""
    voice: int
    start: int           # frame index
    end: int             # frame index (exclusive) — filled in later
    base_freq: int       # 16-bit freq at gate-on
    base_note: Optional[int]   # nearest PAL note index
    base_note_cents: float     # cents error from PAL table
    base_pw: int         # PW at gate-on
    base_ctrl: int       # ctrl at gate-on (waveform byte)
    base_ad: int
    base_sr: int
    is_noise: bool


def build_baseline(frames):
    """
    For each frame and voice, compute the "naive" baseline:
      - freq = base_freq for current note (gate-on value, held constant)
      - pw   = base_pw for current note (gate-on value, held constant)
      - ctrl = base_ctrl | gate_bit (waveform + current gate state, no waveform changes)
      - ad   = base_ad, sr = base_sr

    Returns (notes, baseline_frames) where:
      - notes[voice] = list of NoteEvent
      - baseline_frames[f][v] = (freq16, pw16, ctrl, ad, sr) for frame f, voice v
    """
    n_frames = len(frames)
    notes = [[] for _ in range(N_VOICES)]
    baseline_frames = [[None] * N_VOICES for _ in range(n_frames)]

    for v in range(N_VOICES):
        off = v * VOICE_REGS
        prev_gate = 0
        current_note = None

        for f, fr in enumerate(frames):
            freq = (fr[off + 1] << 8) | fr[off]
            pw = (fr[off + 3] << 8) | fr[off + 2]
            ctrl = fr[off + 4]
            ad = fr[off + 5]
            sr = fr[off + 6]
            gate = ctrl & 1

            if gate and not prev_gate:
                # Gate-on: start new note
                if current_note is not None:
                    current_note.end = f
                note_idx, cents = freq_to_note(freq)
                current_note = NoteEvent(
                    voice=v, start=f, end=n_frames,
                    base_freq=freq, base_note=note_idx,
                    base_note_cents=cents if cents is not None else 0.0,
                    base_pw=pw, base_ctrl=ctrl,
                    base_ad=ad, base_sr=sr,
                    is_noise=bool(ctrl & 0x80),
                )
                notes[v].append(current_note)

            prev_gate = gate

            # Build baseline for this frame
            if current_note is not None:
                base_ctrl = (current_note.base_ctrl & 0xFE) | gate  # waveform + current gate
                baseline_frames[f][v] = (
                    current_note.base_freq,
                    current_note.base_pw,
                    base_ctrl,
                    current_note.base_ad,
                    current_note.base_sr,
                )
            else:
                # Before first gate-on: baseline = actual (no effect to discover yet)
                baseline_frames[f][v] = (freq, pw, ctrl, ad, sr)

    return notes, baseline_frames


# ---- Residual extraction ----

@dataclass
class VoiceResiduals:
    """Per-voice residual streams (actual - baseline)."""
    voice: int
    n_frames: int
    freq_residual: list    # signed 16-bit: actual_freq - baseline_freq per frame
    pw_residual: list      # signed 16-bit: actual_pw - baseline_pw per frame
    ctrl_xor: list         # actual_ctrl XOR baseline_ctrl (bit changes)
    # Gate-on segments within this voice
    note_starts: list      # frame indices of gate-on events
    note_ends: list        # frame indices of note end (next gate-on or n_frames)


def compute_residuals(frames, baseline_frames, notes):
    """Subtract baseline from actual, return per-voice VoiceResiduals."""
    n_frames = len(frames)
    residuals = []

    for v in range(N_VOICES):
        off = v * VOICE_REGS
        freq_res = []
        pw_res = []
        ctrl_xor = []

        for f, fr in enumerate(frames):
            actual_freq = (fr[off + 1] << 8) | fr[off]
            actual_pw = (fr[off + 3] << 8) | fr[off + 2]
            actual_ctrl = fr[off + 4]

            base_freq, base_pw, base_ctrl, _, _ = baseline_frames[f][v]

            # Signed residuals (wrapping at 16-bit boundary)
            df = actual_freq - base_freq
            if df > 32767:
                df -= 65536
            elif df < -32768:
                df += 65536

            dpw = actual_pw - base_pw
            if dpw > 32767:
                dpw -= 65536
            elif dpw < -32768:
                dpw += 65536

            freq_res.append(df)
            pw_res.append(dpw)
            ctrl_xor.append(actual_ctrl ^ base_ctrl)

        starts = [n.start for n in notes[v]]
        ends = [n.end for n in notes[v]]

        residuals.append(VoiceResiduals(
            voice=v,
            n_frames=n_frames,
            freq_residual=freq_res,
            pw_residual=pw_res,
            ctrl_xor=ctrl_xor,
            note_starts=starts,
            note_ends=ends,
        ))

    return residuals


# ---- Effect classification ----

@dataclass
class DiscoveredEffect:
    """An effect discovered via residual analysis."""
    voice: int
    note_start: int      # frame index (for context)
    note_end: int
    category: str        # 'freq_periodic', 'freq_monotonic', 'freq_discrete',
                         # 'pw_linear', 'pw_oscillating', 'ctrl_sequence',
                         # 'freq_fine', 'no_effect'
    subcategory: str     # more specific: 'vibrato', 'arpeggio', 'portamento', etc.
    confidence: float
    params: dict

    def __str__(self):
        p = ', '.join(f'{k}={v}' for k, v in self.params.items())
        return f'{self.subcategory}({p}) [{self.confidence:.0%}]'


def classify_freq_residual(res_segment, note_freq, frame_start, frame_end, voice):
    """
    Classify a freq residual segment into an effect category.

    Returns DiscoveredEffect or None if no significant effect.
    """
    if not res_segment:
        return None

    n = len(res_segment)
    total_var = sum(abs(r) for r in res_segment)

    # Threshold: if residuals are tiny, no effect
    if total_var < n * 2:
        return None

    mean_abs = total_var / n
    unique_vals = sorted(set(res_segment))
    n_unique = len(unique_vals)

    # ---- Test 1: purely discrete (arpeggio or vibrato with 3 values) ----
    # Arpeggio: freq jumps between a few specific offsets from the base note
    # The residual would be: alternating between 0 and some fixed offset(s)
    # Vibrato (Hubbard style): alternates [−d, 0, +d] = 3 values, all same semitone
    discreteness = n_unique / n
    if discreteness < 0.25 and n_unique >= 2 and n_unique <= 6:
        # First: check if all unique values map to the SAME note (= vibrato, not arpeggio)
        # Hubbard vibrato: base ± depth oscillate around same pitch
        if n_unique <= 4:
            note_indices = set()
            all_mapped = True
            for rv in unique_vals:
                candidate_freq = note_freq + rv
                if 0 < candidate_freq <= 0xFFFF:
                    idx, _ = freq_to_note(candidate_freq)
                    if idx is not None:
                        note_indices.add(idx)
                    else:
                        all_mapped = False
                        break
                else:
                    all_mapped = False
                    break
            if all_mapped and len(note_indices) == 1 and n_unique >= 2:
                # All residual values map to the same note — this is vibrato
                # But verify the depth is small (< 3 semitones); large 2-value
                # alternation that stays on the same note might be a rare arpeggio.
                depth = max(unique_vals) - min(unique_vals)
                spectrum = real_dft(res_segment, min_hz=1.5, max_hz=12.0)
                pk_hz, pk_mag, pk_frac = dominant_peak(spectrum)
                period = round(50.0 / pk_hz) if pk_hz > 0 else 0
                depth_semitones = 0.0
                if note_freq > 0 and depth > 0:
                    try:
                        depth_semitones = round(1200 * math.log2(1 + depth / note_freq) / 100, 2)
                    except (ValueError, ZeroDivisionError):
                        pass
                return DiscoveredEffect(
                    voice=voice, note_start=frame_start, note_end=frame_end,
                    category='freq_periodic', subcategory='vibrato',
                    confidence=min(1.0, 0.7 + pk_frac),
                    params={
                        'rate_hz': round(pk_hz, 2),
                        'period_frames': period,
                        'depth_raw': depth,
                        'depth_semitones': depth_semitones,
                        'n_values': n_unique,
                        'residual_pattern': unique_vals,
                    },
                )

        # Check the values snap to note intervals (arpeggio)
        # Each residual value should correspond to a semitone offset
        snaps = []
        for rv in unique_vals:
            # What note is base_note + residual?
            candidate_freq = note_freq + rv
            if 0 < candidate_freq <= 0xFFFF:
                idx, cents = freq_to_note(candidate_freq)
                if idx is not None and abs(cents) < 30:
                    snaps.append((rv, idx, cents))

        if len(snaps) >= 2:
            # Confirm periodicity via DFT
            spectrum = real_dft(res_segment, min_hz=5.0, max_hz=25.0)
            pk_hz, pk_mag, pk_frac = dominant_peak(spectrum)
            period = round(50.0 / pk_hz) if pk_hz > 0 else 0
            offsets = [s[1] - snaps[0][1] for s in snaps]
            return DiscoveredEffect(
                voice=voice, note_start=frame_start, note_end=frame_end,
                category='freq_discrete', subcategory='arpeggio',
                confidence=min(1.0, pk_frac * 3 + 0.3),
                params={
                    'n_notes': len(snaps),
                    'note_offsets_semitones': offsets,
                    'residual_values': [s[0] for s in snaps],
                    'period_frames': period,
                    'rate_hz': round(pk_hz, 1),
                },
            )

    # ---- Test 2: periodic oscillation (vibrato) ----
    # Vibrato: smooth sinusoidal oscillation, many unique values
    if discreteness > 0.35 and n >= 10:
        spectrum = real_dft(res_segment, min_hz=1.5, max_hz=12.0)
        pk_hz, pk_mag, pk_frac = dominant_peak(spectrum)

        if pk_frac > 0.20 and pk_mag > 5.0:
            depth = max(res_segment) - min(res_segment)
            period = round(50.0 / pk_hz) if pk_hz > 0 else 0
            return DiscoveredEffect(
                voice=voice, note_start=frame_start, note_end=frame_end,
                category='freq_periodic', subcategory='vibrato',
                confidence=min(1.0, pk_frac * 2.5),
                params={
                    'rate_hz': round(pk_hz, 2),
                    'period_frames': period,
                    'depth_raw': depth,
                    'depth_semitones': round(1200 * math.log2(1 + depth / note_freq) / 100, 2)
                                       if note_freq > 0 else 0,
                    'mean_offset': round(sum(res_segment) / n),
                },
            )

    # ---- Test 3: monotonic drift (portamento, skydive, drum slide) ----
    # Check if residual is consistently increasing or decreasing
    if n >= 4:
        deltas = [res_segment[i + 1] - res_segment[i] for i in range(n - 1)]
        non_zero = [d for d in deltas if d != 0]
        if non_zero:
            c = Counter(non_zero)
            best_delta, best_count = c.most_common(1)[0]
            consistency = best_count / len(non_zero)

            if consistency >= 0.60 and abs(best_delta) >= 1:
                direction = 'up' if best_delta > 0 else 'down'
                # Classify: drum slide = noise + fast, skydive = every 2 frames, portamento = slow
                speed = abs(best_delta)
                if speed >= 100:
                    sub = 'drum_freq_slide'
                elif speed == 256:  # freq_hi decrement = 256 in 16-bit
                    sub = 'drum_freq_slide'
                else:
                    sub = 'portamento'

                return DiscoveredEffect(
                    voice=voice, note_start=frame_start, note_end=frame_end,
                    category='freq_monotonic', subcategory=sub,
                    confidence=consistency,
                    params={
                        'direction': direction,
                        'speed_per_frame': best_delta,
                        'total_drift': res_segment[-1] - res_segment[0],
                    },
                )

    # ---- Test 4: mixed / unclassified ----
    if mean_abs > 10:
        return DiscoveredEffect(
            voice=voice, note_start=frame_start, note_end=frame_end,
            category='freq_unclassified', subcategory='unknown_freq_effect',
            confidence=0.3,
            params={
                'mean_abs_residual': round(mean_abs),
                'n_unique_values': n_unique,
                'range': max(res_segment) - min(res_segment),
            },
        )

    return None


def classify_pw_residual(res_segment, frame_start, frame_end, voice):
    """Classify PW residual into an effect category."""
    if not res_segment:
        return None

    n = len(res_segment)
    total_var = sum(abs(r) for r in res_segment)
    if total_var < n * 3:
        return None

    # ---- Test 1: linear sweep (constant delta) ----
    deltas = [res_segment[i + 1] - res_segment[i] for i in range(n - 1)]
    non_zero = [d for d in deltas if d != 0]
    if non_zero:
        c = Counter(non_zero)
        best_delta, best_count = c.most_common(1)[0]
        consistency = best_count / len(non_zero)

        if consistency >= 0.65:
            return DiscoveredEffect(
                voice=voice, note_start=frame_start, note_end=frame_end,
                category='pw_linear', subcategory='pwm_sweep',
                confidence=consistency,
                params={
                    'speed_per_frame': best_delta,
                    'initial_pw_offset': res_segment[0],
                    'total_drift': res_segment[-1] - res_segment[0],
                },
            )

    # ---- Test 2: oscillating PW (bidirectional sweep) ----
    if n >= 8:
        sign_changes = sum(
            1 for i in range(1, len(deltas))
            if deltas[i] * deltas[i - 1] < 0
        )
        if sign_changes >= 2:
            spectrum = real_dft(res_segment, min_hz=0.5, max_hz=20.0)
            pk_hz, pk_mag, pk_frac = dominant_peak(spectrum)
            if pk_frac > 0.10:
                return DiscoveredEffect(
                    voice=voice, note_start=frame_start, note_end=frame_end,
                    category='pw_oscillating', subcategory='pwm_oscillate',
                    confidence=min(1.0, pk_frac * 2),
                    params={
                        'rate_hz': round(pk_hz, 2),
                        'min_offset': min(res_segment),
                        'max_offset': max(res_segment),
                        'n_reversals': sign_changes,
                    },
                )

    return None


def classify_ctrl_changes(xor_segment, frame_start, frame_end, voice):
    """Classify ctrl XOR residual (waveform changes, gate changes)."""
    if not xor_segment:
        return None

    n = len(xor_segment)
    # Ignore pure gate changes (bit 0 only)
    wave_changes = [x & 0xFE for x in xor_segment]
    significant = [x for x in wave_changes if x != 0]

    if not significant:
        return None

    # How frequent are waveform changes?
    change_rate = len(significant) / n
    unique_wave_changes = sorted(set(significant))

    # Collect the sequence of actual ctrl values at change points
    return DiscoveredEffect(
        voice=voice, note_start=frame_start, note_end=frame_end,
        category='ctrl_sequence', subcategory='waveform_program',
        confidence=min(1.0, change_rate * 3 + 0.4),
        params={
            'change_rate': round(change_rate, 3),
            'n_changes': len(significant),
            'unique_ctrl_xor': [f'${x:02X}' for x in unique_wave_changes],
        },
    )


# ---- Per-note analysis ----

def analyze_note_residuals(res, note, actual_frames):
    """
    Analyze all residuals for a single note interval.
    Returns list of DiscoveredEffect.
    """
    v = note.voice
    s, e = note.start, note.end
    n = e - s
    if n <= 0:
        return []

    freq_seg = res.freq_residual[s:e]
    pw_seg = res.pw_residual[s:e]
    ctrl_seg = res.ctrl_xor[s:e]

    effects = []

    # Freq effect
    freq_eff = classify_freq_residual(freq_seg, note.base_freq, s, e, v)
    if freq_eff:
        effects.append(freq_eff)

    # PW effect
    pw_eff = classify_pw_residual(pw_seg, s, e, v)
    if pw_eff:
        effects.append(pw_eff)

    # Ctrl effect
    ctrl_eff = classify_ctrl_changes(ctrl_seg, s, e, v)
    if ctrl_eff:
        effects.append(ctrl_eff)

    return effects


# ---- Global-level effect analysis ----

def analyze_global_effects(frames, residuals, notes):
    """
    Analyze effects that span multiple notes (song-level patterns).

    Returns dict with:
      - tempo: detected frames-per-tick
      - filter_modulation: if filter cutoff changes periodically
      - volume_changes: if master volume changes
    """
    results = {}

    # ---- Tempo detection from gate-on intervals ----
    all_intervals = []
    for v in range(N_VOICES):
        starts = residuals[v].note_starts
        if len(starts) >= 3:
            for i in range(len(starts) - 1):
                iv = starts[i + 1] - starts[i]
                if 1 <= iv <= 64:
                    all_intervals.append(iv)

    if all_intervals:
        c = Counter(all_intervals)
        # Find GCD
        from math import gcd
        from functools import reduce
        g = reduce(gcd, all_intervals)
        multiples = sum(1 for iv in all_intervals if iv % g == 0)
        consistency = multiples / len(all_intervals)
        results['tempo'] = {
            'frames_per_tick': g,
            'bpm': round(50 * 60 / g) if g > 0 else 0,
            'consistency': round(consistency, 3),
            'sample_intervals': sorted(c.most_common(5)),
        }

    # ---- Filter cutoff modulation (reg 22 = fc_hi) ----
    cutoff_hi = [fr[22] for fr in frames]
    if len(set(cutoff_hi)) > 3:
        spectrum = real_dft(cutoff_hi, min_hz=0.5, max_hz=20.0)
        pk_hz, pk_mag, pk_frac = dominant_peak(spectrum)
        if pk_frac > 0.15:
            results['filter_modulation'] = {
                'rate_hz': round(pk_hz, 2),
                'min_val': min(cutoff_hi),
                'max_val': max(cutoff_hi),
                'confidence': round(min(1.0, pk_frac * 2), 3),
            }

    # ---- Volume changes (reg 24, bits 0-3) ----
    vol = [fr[24] & 0xF for fr in frames]
    unique_vols = set(vol)
    if len(unique_vols) > 1:
        results['volume_changes'] = {
            'unique_values': sorted(unique_vols),
            'n_changes': sum(1 for i in range(len(vol) - 1) if vol[i] != vol[i + 1]),
        }

    return results


# ---- Summary aggregation ----

def aggregate_effects(all_voice_effects, notes, n_frames):
    """
    Aggregate per-note effects into per-voice summaries.

    Returns dict: voice_index → effect_type_counts + representative params.
    """
    summary = {}
    for v in range(N_VOICES):
        by_type = defaultdict(list)
        for note, effects in zip(notes[v], all_voice_effects[v]):
            for eff in effects:
                by_type[eff.subcategory].append(eff)

        voice_summary = {}
        for subcat, effs in by_type.items():
            # Weighted average params for numeric params
            best = max(effs, key=lambda e: e.confidence)
            voice_summary[subcat] = {
                'count': len(effs),
                'fraction_of_notes': round(len(effs) / max(len(notes[v]), 1), 3),
                'confidence': round(sum(e.confidence for e in effs) / len(effs), 3),
                'representative_params': best.params,
            }

        summary[v] = voice_summary

    return summary


# ---- Top-level entry point ----

def discover_effects(sid_path, subtune=1, n_frames=200, verbose=False):
    """
    Automatically discover all effects in a SID by comparing actual
    register trace against the naive baseline.

    Returns a dict with full analysis results.
    """
    if verbose:
        print(f'Capturing {n_frames} frames from {os.path.basename(sid_path)} subtune {subtune}...')

    frames = capture_frames(sid_path, subtune=subtune, n_frames=n_frames)

    if verbose:
        print(f'Building naive baseline...')

    notes, baseline_frames = build_baseline(frames)

    if verbose:
        print(f'Computing residuals...')

    residuals = compute_residuals(frames, baseline_frames, notes)

    if verbose:
        print(f'Classifying effects per note...')

    # Analyze each note
    all_voice_effects = []
    for v in range(N_VOICES):
        voice_effects = []
        for note in notes[v]:
            res = residuals[v]
            effs = analyze_note_residuals(res, note, frames)
            voice_effects.append(effs)
        all_voice_effects.append(voice_effects)

    # Global analysis
    global_effects = analyze_global_effects(frames, residuals, notes)

    # Aggregate
    summary = aggregate_effects(all_voice_effects, notes, n_frames)

    return {
        'sid_path': sid_path,
        'subtune': subtune,
        'n_frames': n_frames,
        'n_notes': [len(notes[v]) for v in range(N_VOICES)],
        'notes': notes,
        'baseline_frames': baseline_frames,
        'residuals': residuals,
        'voice_effects': all_voice_effects,
        'global': global_effects,
        'summary': summary,
    }


# ---- Reporting ----

def print_report(result):
    """Print a human-readable discovery report."""
    sid = os.path.basename(result['sid_path'])
    print(f'\n{"="*60}')
    print(f'AUTO EFFECT DISCOVERY: {sid} subtune {result["subtune"]}')
    print(f'{"="*60}')
    print(f'Frames analyzed: {result["n_frames"]}')
    print(f'Notes per voice: V1={result["n_notes"][0]} V2={result["n_notes"][1]} V3={result["n_notes"][2]}')

    g = result['global']
    if 'tempo' in g:
        t = g['tempo']
        print(f'\nTempo: {t["frames_per_tick"]} frames/tick = {t["bpm"]} BPM '
              f'[consistency={t["consistency"]:.0%}]')
    if 'filter_modulation' in g:
        fm = g['filter_modulation']
        print(f'Filter mod: {fm["rate_hz"]} Hz, range {fm["min_val"]}-{fm["max_val"]} '
              f'[{fm["confidence"]:.0%}]')
    if 'volume_changes' in g:
        vc = g['volume_changes']
        print(f'Volume: {vc["n_changes"]} changes, values={vc["unique_values"]}')

    for v in range(N_VOICES):
        print(f'\n--- Voice {v + 1} ---')
        s = result['summary'][v]
        if not s:
            print('  No effects detected (pure notes + ADSR)')
            continue

        for subcat, info in sorted(s.items()):
            print(f'  {subcat}: found in {info["count"]}/{result["n_notes"][v]} notes '
                  f'({info["fraction_of_notes"]:.0%}), confidence={info["confidence"]:.0%}')
            p = info['representative_params']
            for k, val in p.items():
                print(f'    {k}: {val}')

    # Show first 5 notes in detail for each voice
    print(f'\n--- Per-note detail (first 5 notes per voice) ---')
    for v in range(N_VOICES):
        notes = result['notes'][v]
        effs = result['voice_effects'][v]
        if not notes:
            continue
        print(f'\nVoice {v + 1}:')
        for i, (note, note_effs) in enumerate(zip(notes[:5], effs[:5])):
            note_str = note_name(note.base_note)
            base_str = f'{note_str}(f={note.base_freq:04X})'
            eff_str = ' + '.join(str(e) for e in note_effs) if note_effs else 'none'
            print(f'  Note {i} [f{note.start}-f{note.end}]: base={base_str} '
                  f'effects=[{eff_str}]')


def print_residual_debug(result, voice=0, n_frames=30):
    """Print raw residuals for debugging — shows what the baseline subtraction gives."""
    print(f'\n--- Raw residuals for Voice {voice + 1}, first {n_frames} frames ---')
    print(f'{"Frame":>5}  {"ActFreq":>7}  {"BaseFreq":>8}  {"FreqRes":>7}  '
          f'{"ActPW":>6}  {"BasePW":>6}  {"PWRes":>6}  {"CtrlXOR":>7}')

    frames = result.get('_raw_frames')
    if frames is None:
        print('  (set result["_raw_frames"] = frames to enable raw debug)')
        return

    baseline = result['baseline_frames']
    res = result['residuals'][voice]
    off = voice * VOICE_REGS

    for f in range(min(n_frames, result['n_frames'])):
        fr = frames[f]
        actual_freq = (fr[off + 1] << 8) | fr[off]
        actual_pw = (fr[off + 3] << 8) | fr[off + 2]
        base_freq, base_pw, base_ctrl, _, _ = baseline[f][voice]
        print(f'{f:5d}  {actual_freq:7d}  {base_freq:8d}  {res.freq_residual[f]:7d}  '
              f'{actual_pw:6d}  {base_pw:6d}  {res.pw_residual[f]:6d}  '
              f'${res.ctrl_xor[f]:02X}')


# ---- CLI ----

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 auto_effect_discover.py <file.sid> [subtune] [n_frames]')
        print()
        print('Automatically discovers musical effects by comparing the actual')
        print('SID register trace against a naive baseline (notes + ADSR only).')
        sys.exit(1)

    sid_path = sys.argv[1]
    subtune = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    n_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 200

    result = discover_effects(sid_path, subtune=subtune, n_frames=n_frames, verbose=True)

    # Stash raw frames for debug output
    frames = capture_frames(sid_path, subtune=subtune, n_frames=n_frames)
    result['_raw_frames'] = frames

    print_report(result)
    print()

    # Show residual debug for all 3 voices
    for v in range(N_VOICES):
        print_residual_debug(result, voice=v, n_frames=30)
