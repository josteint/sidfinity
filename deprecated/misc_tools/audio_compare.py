#!/usr/bin/env python3
"""
audio_compare.py -- Spectral comparison of two SID files.

Renders both SIDs to PCM via sidrender, computes spectrograms using STFT,
and calculates a perceptual similarity score.

Falls back to weighted register comparison if sidrender is unavailable.

Reports:
  IDENTICAL     - bit-identical PCM output
  INAUDIBLE     - spectral difference below audible threshold
  NOTICEABLE    - audible but minor differences
  VERY_DIFFERENT - substantially different audio

Usage:
  python3 audio_compare.py <file_a.sid> <file_b.sid> [options]

Options:
  --duration N    Duration in seconds (default: 10)
  --subtune N     Subtune number (default: start song)
  --verbose       Show detailed per-band breakdown
  --register      Force register-based comparison (skip PCM)
"""

import argparse
import os
import struct
import subprocess
import sys
import tempfile

import numpy as np

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.join(SCRIPT_DIR, '..', 'tools')
SIDRENDER = os.path.join(TOOLS_DIR, 'sidrender')
SIDDUMP = os.path.join(TOOLS_DIR, 'siddump')

# Audio parameters
SAMPLE_RATE = 48000
FFT_SIZE = 2048
HOP_SIZE = 512

# Perceptual frequency bands (Hz) - loosely based on critical bands
# SID output range is roughly 16 Hz to 4 kHz fundamental, harmonics up to ~12 kHz
FREQ_BANDS = [
    (20, 100,    'sub-bass',    0.3),   # barely audible, mostly felt
    (100, 400,   'bass',        0.8),   # important for bass lines
    (400, 1200,  'low-mid',     1.0),   # fundamental frequencies of most SID notes
    (1200, 3000, 'mid',         1.0),   # important for timbre recognition
    (3000, 6000, 'high-mid',    0.7),   # harmonics, brightness
    (6000, 12000,'high',        0.4),   # upper harmonics, less critical
    (12000, 24000,'very-high',  0.1),   # mostly noise/artifacts for SID
]


def render_sid_to_pcm(sid_path, duration=10, subtune=0, timeout=120):
    """Render a SID file to raw 16-bit PCM using sidrender.

    Returns numpy array of float32 samples normalized to [-1, 1], or None on failure.
    """
    cmd = [SIDRENDER, sid_path, '--duration', str(duration)]
    if subtune > 0:
        cmd += ['--subtune', str(subtune)]
    if timeout > 0:
        cmd += ['--timeout', str(timeout)]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=timeout + 10)
    except subprocess.TimeoutExpired:
        print(f'  TIMEOUT rendering {sid_path}', file=sys.stderr)
        return None
    except FileNotFoundError:
        print(f'  sidrender not found at {SIDRENDER}', file=sys.stderr)
        return None

    if result.returncode != 0:
        stderr = result.stderr.decode('utf-8', errors='replace').strip()
        print(f'  sidrender failed (exit {result.returncode}): {stderr}', file=sys.stderr)
        return None

    raw = result.stdout
    if len(raw) < 2:
        return None

    # Parse 16-bit signed LE samples
    n_samples = len(raw) // 2
    samples = np.frombuffer(raw[:n_samples * 2], dtype=np.int16).astype(np.float32) / 32768.0
    return samples


def compute_spectrogram(samples, fft_size=FFT_SIZE, hop_size=HOP_SIZE):
    """Compute magnitude spectrogram using STFT with Hann window.

    Returns (magnitude_db, freqs, times) where magnitude_db is in dB.
    """
    window = np.hanning(fft_size)
    n_frames = max(1, (len(samples) - fft_size) // hop_size + 1)

    # Frequency axis
    freqs = np.fft.rfftfreq(fft_size, d=1.0 / SAMPLE_RATE)
    n_bins = len(freqs)

    mag = np.zeros((n_frames, n_bins), dtype=np.float32)

    for i in range(n_frames):
        start = i * hop_size
        frame = samples[start:start + fft_size]
        if len(frame) < fft_size:
            frame = np.pad(frame, (0, fft_size - len(frame)))
        windowed = frame * window
        spectrum = np.fft.rfft(windowed)
        mag[i] = np.abs(spectrum)

    # Convert to dB with floor at -100 dB
    mag_db = 20.0 * np.log10(np.maximum(mag, 1e-10))
    mag_db = np.maximum(mag_db, -100.0)

    times = np.arange(n_frames) * hop_size / SAMPLE_RATE
    return mag_db, freqs, times


def spectral_difference(spec_a, spec_b, freqs):
    """Compute perceptually-weighted spectral difference.

    Returns (overall_score, band_scores) where:
      overall_score: 0.0 (identical) to 1.0+ (very different)
      band_scores: list of (band_name, score, weight) tuples
    """
    # Align lengths
    min_frames = min(spec_a.shape[0], spec_b.shape[0])
    if min_frames == 0:
        return 1.0, []

    a = spec_a[:min_frames]
    b = spec_b[:min_frames]

    # Compute difference per frequency band
    band_scores = []
    weighted_sum = 0.0
    weight_sum = 0.0

    for lo_hz, hi_hz, name, weight in FREQ_BANDS:
        # Find frequency bin range
        lo_bin = np.searchsorted(freqs, lo_hz)
        hi_bin = np.searchsorted(freqs, hi_hz)
        if lo_bin >= hi_bin or hi_bin > a.shape[1]:
            continue

        # Mean absolute difference in dB for this band
        band_diff = np.mean(np.abs(a[:, lo_bin:hi_bin] - b[:, lo_bin:hi_bin]))

        # Normalize: 0 dB diff = 0.0 score, 20 dB diff = 1.0
        band_score = min(band_diff / 20.0, 2.0)
        band_scores.append((name, band_score, weight))

        weighted_sum += band_score * weight
        weight_sum += weight

    overall = weighted_sum / weight_sum if weight_sum > 0 else 1.0
    return overall, band_scores


def classify_difference(score, pcm_identical=False):
    """Classify the spectral difference score into a human-readable grade.

    Returns (grade, description).
    """
    if pcm_identical:
        return 'IDENTICAL', 'Bit-identical PCM output'
    if score < 0.005:
        return 'IDENTICAL', 'Spectrally identical (< 0.1 dB mean difference)'
    if score < 0.05:
        return 'INAUDIBLE', 'Differences below audible threshold'
    if score < 0.20:
        return 'NOTICEABLE', 'Audible but minor differences'
    return 'VERY_DIFFERENT', f'Substantially different audio (score={score:.3f})'


# --- Register-based fallback comparison ---

def dump_registers(sid_path, duration=10, subtune=0):
    """Run siddump and return list of 25-element register arrays per frame."""
    cmd = [SIDDUMP, sid_path, '--duration', str(duration)]
    if subtune > 0:
        cmd += ['--subtune', str(subtune)]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

    if result.returncode != 0:
        return None

    lines = result.stdout.strip().split('\n')
    frames = []
    for line in lines[2:]:  # skip JSON metadata + header
        parts = line.split('|')[0].strip()  # strip digi suffix
        if not parts:
            continue
        try:
            vals = [int(v, 16) for v in parts.split(',')]
            frames.append(vals)
        except ValueError:
            continue
    return frames


# Register audibility weights (index 0-24)
# Higher = more audibly important
REG_WEIGHTS = [
    # Voice 1: flo, fhi, pwlo, pwhi, ctrl, ad, sr
    0.2, 1.0, 0.05, 0.15, 1.0, 0.8, 0.8,
    # Voice 2: flo, fhi, pwlo, pwhi, ctrl, ad, sr
    0.2, 1.0, 0.05, 0.15, 1.0, 0.8, 0.8,
    # Voice 3: flo, fhi, pwlo, pwhi, ctrl, ad, sr
    0.2, 1.0, 0.05, 0.15, 1.0, 0.8, 0.8,
    # Filter: filt_lo, filt_hi, filt_ctrl, filt_mode_vol
    0.05, 0.4, 0.6, 0.9,
]


def register_compare(frames_a, frames_b):
    """Compare two register dumps with audibility weighting.

    Returns (score, details) where score is 0.0 (identical) to 1.0+ (very different).
    """
    total = min(len(frames_a), len(frames_b))
    if total == 0:
        return 1.0, {}

    n_regs = min(25, min(len(frames_a[0]), len(frames_b[0])))
    weights = REG_WEIGHTS[:n_regs]
    total_weight = sum(weights)

    # Track per-register error rates
    reg_errors = [0] * n_regs
    perfect_frames = 0
    weighted_error_sum = 0.0

    for i in range(total):
        a = frames_a[i]
        b = frames_b[i]
        frame_perfect = True

        for r in range(n_regs):
            if a[r] != b[r]:
                frame_perfect = False
                reg_errors[r] += 1

                # Scale error by register importance and magnitude
                if r in (1, 8, 15):  # freq_hi: note-level error
                    # Check if it's a semitone off or just fine tuning
                    diff = abs(a[r] - b[r])
                    if diff >= 2:
                        weighted_error_sum += weights[r] * 1.0
                    else:
                        weighted_error_sum += weights[r] * 0.3
                elif r in (4, 11, 18):  # ctrl: waveform changes are big
                    # Mask out gate bit (bit 0) for comparison
                    wav_a = a[r] & 0xFE
                    wav_b = b[r] & 0xFE
                    if wav_a != wav_b:
                        weighted_error_sum += weights[r] * 1.0
                    else:
                        weighted_error_sum += weights[r] * 0.1  # just gate timing
                else:
                    weighted_error_sum += weights[r]

        if frame_perfect:
            perfect_frames += 1

    # Normalize score: mean weighted error per frame
    score = weighted_error_sum / (total * total_weight) if total > 0 else 1.0

    details = {
        'total_frames': total,
        'perfect_frames': perfect_frames,
        'perfect_pct': 100.0 * perfect_frames / total,
        'per_register_error_pct': {
            i: 100.0 * reg_errors[i] / total for i in range(n_regs) if reg_errors[i] > 0
        },
    }

    return score, details


def classify_register_difference(score):
    """Classify register comparison score."""
    if score == 0.0:
        return 'IDENTICAL', 'All registers match perfectly'
    if score < 0.01:
        return 'INAUDIBLE', 'Only inaudible register differences (fine freq, pulse width)'
    if score < 0.05:
        return 'NOTICEABLE', 'Some audible register differences'
    return 'VERY_DIFFERENT', f'Major register differences (score={score:.3f})'


# --- Main ---

def compare_sids(path_a, path_b, duration=10, subtune=0, verbose=False,
                 force_register=False):
    """Compare two SID files. Returns dict with results."""
    result = {
        'file_a': path_a,
        'file_b': path_b,
        'duration': duration,
        'method': None,
        'grade': None,
        'description': None,
        'score': None,
    }

    # Try spectral comparison first (unless forced to register mode)
    if not force_register and os.path.isfile(SIDRENDER):
        pcm_a = render_sid_to_pcm(path_a, duration, subtune)
        pcm_b = render_sid_to_pcm(path_b, duration, subtune)

        if pcm_a is not None and pcm_b is not None:
            result['method'] = 'spectral'

            # Check for bit-identical PCM
            min_len = min(len(pcm_a), len(pcm_b))
            pcm_identical = (len(pcm_a) == len(pcm_b) and
                             np.array_equal(pcm_a, pcm_b))

            if pcm_identical:
                result['grade'] = 'IDENTICAL'
                result['description'] = 'Bit-identical PCM output'
                result['score'] = 0.0
                result['pcm_identical'] = True
                return result

            # Compute spectrograms
            spec_a, freqs, times_a = compute_spectrogram(pcm_a)
            spec_b, freqs, times_b = compute_spectrogram(pcm_b)

            # Compute perceptual difference
            score, band_scores = spectral_difference(spec_a, spec_b, freqs)
            grade, description = classify_difference(score)

            result['score'] = score
            result['grade'] = grade
            result['description'] = description
            result['band_scores'] = band_scores
            result['pcm_identical'] = False
            result['samples_a'] = len(pcm_a)
            result['samples_b'] = len(pcm_b)

            if verbose:
                result['rms_a'] = float(np.sqrt(np.mean(pcm_a[:min_len] ** 2)))
                result['rms_b'] = float(np.sqrt(np.mean(pcm_b[:min_len] ** 2)))

            return result

    # Fallback: register-based comparison
    frames_a = dump_registers(path_a, duration, subtune)
    frames_b = dump_registers(path_b, duration, subtune)

    if frames_a is None or frames_b is None:
        result['method'] = 'failed'
        result['grade'] = 'ERROR'
        result['description'] = 'Could not dump registers from one or both files'
        return result

    result['method'] = 'register'
    score, details = register_compare(frames_a, frames_b)
    grade, description = classify_register_difference(score)

    result['score'] = score
    result['grade'] = grade
    result['description'] = description
    result['details'] = details

    return result


def print_result(result, verbose=False):
    """Print comparison result to stdout."""
    grade = result['grade']
    desc = result['description']
    method = result['method']
    score = result['score']

    print(f'{grade}: {desc}')
    print(f'  Method: {method}')
    if score is not None:
        print(f'  Score: {score:.4f}')
    print(f'  File A: {result["file_a"]}')
    print(f'  File B: {result["file_b"]}')

    if method == 'spectral' and 'band_scores' in result:
        bands = result['band_scores']
        if verbose and bands:
            print(f'  Frequency band breakdown:')
            for name, bscore, weight in bands:
                bar = '#' * int(bscore * 50)
                print(f'    {name:12s}: {bscore:.4f} (weight {weight:.1f}) {bar}')

        if verbose and 'rms_a' in result:
            print(f'  RMS A: {result["rms_a"]:.6f}  RMS B: {result["rms_b"]:.6f}')
            print(f'  Samples A: {result["samples_a"]}  B: {result["samples_b"]}')

    if method == 'register' and 'details' in result:
        d = result['details']
        print(f'  Frames: {d["total_frames"]} ({d["perfect_pct"]:.1f}% perfect)')
        if verbose and d['per_register_error_pct']:
            reg_names = [
                'V1_FLO', 'V1_FHI', 'V1_PWLO', 'V1_PWHI', 'V1_CTRL', 'V1_AD', 'V1_SR',
                'V2_FLO', 'V2_FHI', 'V2_PWLO', 'V2_PWHI', 'V2_CTRL', 'V2_AD', 'V2_SR',
                'V3_FLO', 'V3_FHI', 'V3_PWLO', 'V3_PWHI', 'V3_CTRL', 'V3_AD', 'V3_SR',
                'FLT_LO', 'FLT_HI', 'FLT_CTRL', 'FLT_MODE_VOL',
            ]
            print(f'  Registers with differences:')
            for reg_idx, pct in sorted(d['per_register_error_pct'].items(),
                                       key=lambda x: -x[1]):
                name = reg_names[reg_idx] if reg_idx < len(reg_names) else f'R{reg_idx}'
                bar = '#' * int(pct / 2)
                print(f'    {name:14s}: {pct:5.1f}% {bar}')


def main():
    parser = argparse.ArgumentParser(
        description='Compare two SID files spectrally or by register analysis.')
    parser.add_argument('file_a', help='First SID file')
    parser.add_argument('file_b', help='Second SID file')
    parser.add_argument('--duration', type=int, default=10,
                        help='Duration in seconds (default: 10)')
    parser.add_argument('--subtune', type=int, default=0,
                        help='Subtune number (default: start song)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed per-band breakdown')
    parser.add_argument('--register', action='store_true',
                        help='Force register-based comparison (skip PCM rendering)')
    args = parser.parse_args()

    if not os.path.isfile(args.file_a):
        print(f'Error: {args.file_a} not found', file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.file_b):
        print(f'Error: {args.file_b} not found', file=sys.stderr)
        sys.exit(1)

    result = compare_sids(args.file_a, args.file_b,
                          duration=args.duration,
                          subtune=args.subtune,
                          verbose=args.verbose,
                          force_register=args.register)

    print_result(result, verbose=args.verbose)

    # Exit code based on grade
    exit_codes = {
        'IDENTICAL': 0,
        'INAUDIBLE': 0,
        'NOTICEABLE': 1,
        'VERY_DIFFERENT': 2,
        'ERROR': 3,
    }
    sys.exit(exit_codes.get(result['grade'], 3))


if __name__ == '__main__':
    main()
