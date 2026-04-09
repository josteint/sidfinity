"""
Audio A/B comparator for SID files.

Renders two SID files (or raw PCM files) to audio via sidrender and computes
perceptual similarity using time-domain cross-correlation and spectral analysis.

Raw PCM format: 16-bit signed little-endian mono at 48000 Hz.
"""

import os
import struct
import subprocess
import sys
import tempfile

import numpy as np

SAMPLE_RATE = 48000
SIDRENDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         "tools", "sidrender")


def render_sid(sid_path, duration=10, subtune=0):
    """Render a SID file to a numpy int16 array via sidrender."""
    cmd = [SIDRENDER, sid_path, "--duration", str(duration)]
    if subtune:
        cmd += ["--subtune", str(subtune)]
    result = subprocess.run(cmd, capture_output=True, timeout=duration + 30)
    if result.returncode != 0:
        raise RuntimeError(
            f"sidrender failed (exit {result.returncode}): "
            f"{result.stderr.decode('utf-8', errors='replace').strip()}"
        )
    raw = result.stdout
    if len(raw) < 2:
        raise RuntimeError("sidrender produced no audio")
    samples = np.frombuffer(raw, dtype=np.int16)
    return samples


def load_raw_pcm(path):
    """Load raw 16-bit signed LE mono PCM from a file."""
    with open(path, "rb") as f:
        raw = f.read()
    if len(raw) < 2:
        raise RuntimeError(f"Empty or too-small PCM file: {path}")
    return np.frombuffer(raw, dtype=np.int16)


def _normalize(samples):
    """Convert to float64 and normalize to [-1, 1]."""
    f = samples.astype(np.float64)
    peak = np.max(np.abs(f))
    if peak > 0:
        f /= peak
    return f


def _trim_to_shorter(a, b):
    """Trim both arrays to the length of the shorter one."""
    n = min(len(a), len(b))
    return a[:n], b[:n]


def correlation(a, b):
    """Compute normalized cross-correlation (Pearson) of two float arrays."""
    if len(a) == 0:
        return 0.0
    a_mean = a - np.mean(a)
    b_mean = b - np.mean(b)
    num = np.dot(a_mean, b_mean)
    denom = np.sqrt(np.dot(a_mean, a_mean) * np.dot(b_mean, b_mean))
    if denom < 1e-12:
        return 1.0 if np.dot(a_mean, a_mean) < 1e-12 and np.dot(b_mean, b_mean) < 1e-12 else 0.0
    return float(num / denom)


def _make_band_edges(n_bins, n_bands):
    """Create log-spaced band edges for spectral analysis."""
    edges = np.logspace(0, np.log10(n_bins), n_bands + 1).astype(int)
    edges = np.clip(edges, 0, n_bins)
    for j in range(1, len(edges)):
        if edges[j] <= edges[j - 1]:
            edges[j] = edges[j - 1] + 1
    return np.clip(edges, 0, n_bins)


def _band_energies(fft_mag, edges, n_bands):
    """Compute log band energies from FFT magnitudes."""
    n_bins = len(fft_mag)
    energies = np.zeros(n_bands)
    for j in range(n_bands):
        lo, hi = edges[j], edges[j + 1]
        if lo < n_bins and hi <= n_bins and lo < hi:
            energies[j] = np.sum(fft_mag[lo:hi] ** 2)
    return np.log10(energies + 1e-10)


def spectral_similarity(a, b, n_bands=32):
    """
    Compare spectrograms frame-by-frame using log-band energies.

    For each short-time frame, compute log-band energies and measure
    per-frame cosine similarity. Returns the median similarity across frames.
    This preserves temporal structure so that two different songs on the
    same chip will score low.
    """
    chunk_size = 2048
    hop = chunk_size // 2  # 50% overlap
    n = min(len(a), len(b))
    n_frames = max(1, (n - chunk_size) // hop)

    if n_frames == 0:
        return 1.0

    window = np.hanning(chunk_size)
    n_bins = chunk_size // 2 + 1
    edges = _make_band_edges(n_bins, n_bands)

    similarities = []
    for i in range(n_frames):
        start = i * hop
        end = start + chunk_size
        if end > n:
            break

        fft_a = np.abs(np.fft.rfft(a[start:end] * window))
        fft_b = np.abs(np.fft.rfft(b[start:end] * window))

        log_a = _band_energies(fft_a, edges, n_bands)
        log_b = _band_energies(fft_b, edges, n_bands)

        # Per-frame cosine similarity
        dot = np.dot(log_a, log_b)
        na = np.sqrt(np.dot(log_a, log_a))
        nb = np.sqrt(np.dot(log_b, log_b))
        if na < 1e-12 or nb < 1e-12:
            sim = 1.0 if na < 1e-12 and nb < 1e-12 else 0.0
        else:
            sim = dot / (na * nb)
        similarities.append(sim)

    if not similarities:
        return 1.0

    # Use median to be robust against outlier frames
    return float(np.median(similarities))


def compute_score(corr, spec_sim):
    """
    Combine correlation and spectral similarity into a 0-100 score.

    Weights: 40% time-domain correlation, 60% spectral similarity.
    Spectral matters more because it captures tonal/harmonic differences
    even when waveforms are phase-shifted.
    """
    # Clamp to [0, 1]
    corr = max(0.0, min(1.0, corr))
    spec_sim = max(0.0, min(1.0, spec_sim))

    score = (0.4 * corr + 0.6 * spec_sim) * 100.0
    return round(score, 2)


def compare_audio(path_a, path_b, duration=10, subtune=0):
    """
    Compare two audio sources (SID files or raw PCM files).

    If a path ends with .sid, it's rendered via sidrender.
    Otherwise it's loaded as raw 16-bit signed LE mono PCM at 48kHz.

    Returns:
        dict with keys:
            correlation: float (-1 to 1, typically 0 to 1)
            spectral_similarity: float (0 to 1)
            score: float (0 to 100)
            identical: bool (score >= 95)
            samples_a: int
            samples_b: int
    """
    # Load audio
    if path_a.lower().endswith(".sid"):
        samples_a = render_sid(path_a, duration, subtune)
    else:
        samples_a = load_raw_pcm(path_a)

    if path_b.lower().endswith(".sid"):
        samples_b = render_sid(path_b, duration, subtune)
    else:
        samples_b = load_raw_pcm(path_b)

    n_a, n_b = len(samples_a), len(samples_b)

    # Normalize and trim
    fa = _normalize(samples_a)
    fb = _normalize(samples_b)
    fa, fb = _trim_to_shorter(fa, fb)

    # Compute metrics
    corr = correlation(fa, fb)
    spec = spectral_similarity(fa, fb)
    score = compute_score(corr, spec)

    return {
        "correlation": round(corr, 6),
        "spectral_similarity": round(spec, 6),
        "score": score,
        "identical": score >= 95.0,
        "samples_a": n_a,
        "samples_b": n_b,
    }


def compare_sid_files(sid_a, sid_b, duration=10, subtune=0):
    """Convenience: compare two .sid files directly."""
    return compare_audio(sid_a, sid_b, duration, subtune)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="A/B audio comparison for SID files")
    parser.add_argument("file_a", help="First SID or raw PCM file")
    parser.add_argument("file_b", help="Second SID or raw PCM file")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds (default: 10)")
    parser.add_argument("--subtune", type=int, default=0, help="Subtune number (default: start song)")
    args = parser.parse_args()

    result = compare_audio(args.file_a, args.file_b, args.duration, args.subtune)

    print(f"Correlation:          {result['correlation']:+.6f}")
    print(f"Spectral similarity:  {result['spectral_similarity']:.6f}")
    print(f"Score:                {result['score']:.2f}/100")
    print(f"Identical:            {result['identical']}")
    print(f"Samples A:            {result['samples_a']}")
    print(f"Samples B:            {result['samples_b']}")


if __name__ == "__main__":
    main()
