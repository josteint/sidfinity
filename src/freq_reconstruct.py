#!/usr/bin/env python3
"""
freq_reconstruct.py — Frequency table reconstruction from played SID output.

Runs siddump to capture register output, extracts frequency values from all
3 voices, clusters into semitone bins, and reconstructs the freq table.

Usage:
    python3 src/freq_reconstruct.py <sid_file> [--duration 30] [--verbose]
"""

import math
import os
import subprocess
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from gt_parser import parse_psid_header, FREQ_TBL_LO, FREQ_TBL_HI

SIDDUMP = os.path.join(os.path.dirname(__file__), '..', 'tools', 'siddump')
SEMITONE_RATIO = 2 ** (1 / 12)  # ~1.05946


def _run_siddump(sid_path, duration=30):
    """Run siddump and parse CSV output into per-frame register dicts."""
    r = subprocess.run(
        [SIDDUMP, sid_path, '--duration', str(duration)],
        capture_output=True, text=True, timeout=120
    )
    if r.returncode not in (0,):
        raise RuntimeError(f'siddump failed (exit {r.returncode}): {r.stderr.strip()}')

    lines = r.stdout.strip().split('\n')
    if len(lines) < 3:
        raise RuntimeError(f'siddump produced too few lines ({len(lines)})')

    # Line 0 = JSON metadata, line 1 = CSV header, line 2+ = data
    header_line = lines[1]
    fields = header_line.split(',')

    frames = []
    for line in lines[2:]:
        vals = line.split(',')
        if len(vals) != len(fields):
            continue
        row = {}
        for f, v in zip(fields, vals):
            row[f] = int(v, 16)
        frames.append(row)
    return frames


def _extract_frequencies(frames, min_hold=2):
    """Extract freq values from 3 voices, filtering transients.

    Only keeps frequencies held for >= min_hold consecutive frames.
    Returns (set of stable freqs, Counter of all freqs).
    """
    all_freqs = Counter()
    stable_freqs = set()

    for v in range(1, 4):
        prev_freq = 0
        hold_count = 0
        for frame in frames:
            lo = frame.get(f'V{v}_FREQ_LO', 0)
            hi = frame.get(f'V{v}_FREQ_HI', 0)
            freq = lo | (hi << 8)

            # Skip very low frequencies (likely silence or noise)
            if freq < 0x0080:
                prev_freq = 0
                hold_count = 0
                continue

            all_freqs[freq] += 1

            if freq == prev_freq:
                hold_count += 1
                if hold_count >= min_hold:
                    stable_freqs.add(freq)
            else:
                prev_freq = freq
                hold_count = 1

    return stable_freqs, all_freqs


def _cluster_to_notes(freqs, verbose=False):
    """Cluster raw frequencies into 12-TET semitone bins.

    Uses log2 binning: each semitone spans +-0.5 semitones around its center.
    Returns dict mapping semitone_number -> median frequency.
    """
    if not freqs:
        return {}

    freq_list = sorted(freqs)
    base = freq_list[0]

    note_bins = {}
    for f in freq_list:
        semitones = 12 * math.log2(f / base)
        note_num = round(semitones)
        note_bins.setdefault(note_num, []).append(f)

    notes = {}
    for note_num, bin_freqs in sorted(note_bins.items()):
        median = sorted(bin_freqs)[len(bin_freqs) // 2]
        notes[note_num] = median

    if verbose:
        print(f"  Base freq: {base} (0x{base:04X})")
        print(f"  Raw unique freqs: {len(freqs)}")
        print(f"  Clustered notes: {len(notes)}")
        for n, f in sorted(notes.items()):
            print(f"    Note +{n:3d}: freq=0x{f:04X} ({f})")

    return notes


def _build_table(notes, verbose=False):
    """Build lo/hi freq table arrays from clustered notes.

    Fills gaps with 12-TET interpolation using the ratio from known notes.
    Returns (lo_bytes, hi_bytes, first_note_offset, num_notes).
    """
    if not notes:
        return b'', b'', 0, 0

    sorted_notes = sorted(notes.items())
    min_note = sorted_notes[0][0]
    max_note = sorted_notes[-1][0]
    num_notes = max_note - min_note + 1

    lo = bytearray(num_notes)
    hi = bytearray(num_notes)

    for i in range(num_notes):
        note_num = min_note + i
        if note_num in notes:
            freq = notes[note_num]
        else:
            # Interpolate from nearest known note below
            known_below = max((k for k in notes if k <= note_num), default=None)
            if known_below is not None:
                freq = round(notes[known_below] * (SEMITONE_RATIO ** (note_num - known_below)))
            else:
                known_above = min(k for k in notes if k > note_num)
                freq = round(notes[known_above] / (SEMITONE_RATIO ** (known_above - note_num)))

        freq = max(0, min(0xFFFF, freq))
        lo[i] = freq & 0xFF
        hi[i] = (freq >> 8) & 0xFF

    if verbose:
        print(f"\n  Reconstructed table: {num_notes} notes (offsets {min_note}..{max_note})")
        for i in range(num_notes):
            freq = lo[i] | (hi[i] << 8)
            marker = '*' if (min_note + i) in notes else ' '
            print(f"    [{i:3d}] freq=0x{freq:04X} ({freq:5d}) {marker}")

    return bytes(lo), bytes(hi), min_note, num_notes


def compare_to_pal(notes):
    """Compare reconstructed frequencies to the standard PAL freq table.

    Args:
        notes: list of (note_number, frequency) tuples, or dict mapping note->freq.

    Returns dict with:
        - tuning: 'PAL', 'NTSC', or 'custom'
        - ratio_to_pal: float (1.0 = exact PAL)
        - cents_offset: float (0 = exact PAL)
        - pal_exact_matches: int
        - total_notes: int
    """
    # Accept both dict and list-of-tuples
    if isinstance(notes, dict):
        note_items = sorted(notes.items())
    else:
        note_items = sorted(notes)

    if not note_items:
        return {'tuning': 'unknown', 'ratio_to_pal': 0.0, 'cents_offset': 0.0,
                'pal_exact_matches': 0, 'total_notes': 0}

    base_semitone = note_items[0][0]

    best_offset = None
    best_ratio = None
    best_matches = 0

    for pal_start in range(96):
        matches = 0
        ratios = []
        for obs_semi, obs_freq in note_items:
            pal_note = pal_start + (obs_semi - base_semitone)
            if 0 <= pal_note < 96:
                pal_freq = FREQ_TBL_LO[pal_note] | (FREQ_TBL_HI[pal_note] << 8)
                if pal_freq > 0:
                    r = obs_freq / pal_freq
                    ratios.append(r)
                    if 0.99 <= r <= 1.01:
                        matches += 1

        if matches > best_matches:
            best_matches = matches
            best_offset = pal_start - base_semitone
            if ratios:
                best_ratio = sum(ratios) / len(ratios)

    total = len(note_items)
    result = {
        'pal_exact_matches': best_matches,
        'total_notes': total,
        'pal_offset': best_offset,
        'ratio_to_pal': best_ratio if best_ratio is not None else 0.0,
    }

    if best_ratio is not None:
        cents_off = 1200 * math.log2(best_ratio) if best_ratio > 0 else 0.0
        result['cents_offset'] = cents_off

        if best_matches >= total * 0.9:
            result['tuning'] = 'PAL'
        elif 0.93 <= best_ratio <= 0.97:
            result['tuning'] = 'NTSC'
        else:
            result['tuning'] = 'custom'
    else:
        result['tuning'] = 'unknown'
        result['cents_offset'] = 0.0

    return result


def _search_binary(binary, load_addr, lo, hi, stable_freqs, notes, verbose=False):
    """Search binary for freq table.

    Returns offset in binary where table was found, or None.
    """
    # Strategy 1: Scan for any monotonic 12-TET block
    for N in (96, 48, 32):
        if len(binary) < N * 2:
            continue
        for pos in range(len(binary) - N * 2 + 1):
            bin_lo = binary[pos:pos + N]
            bin_hi = binary[pos + N:pos + N * 2]

            # Quick reject: hi byte range check
            if bin_hi[0] > 0x08:
                continue
            if bin_hi[N - 1] < 0x40:
                continue

            f_first = bin_lo[0] | (bin_hi[0] << 8)
            f_last = bin_lo[N - 1] | (bin_hi[N - 1] << 8)
            if f_first < 0x0080 or f_first > 0x0800:
                continue
            if f_last < 0x4000:
                continue
            if f_last <= f_first * 16:
                continue

            # Check monotonic + semitone ratios
            ascending = 0
            good_ratio = 0
            prev = f_first
            for i in range(1, N):
                cur = bin_lo[i] | (bin_hi[i] << 8)
                if cur > prev:
                    ascending += 1
                    if prev > 0:
                        ratio = cur / prev
                        if 1.02 <= ratio <= 1.12:
                            good_ratio += 1
                prev = cur

            if ascending < N - 2:
                continue
            if good_ratio < (N - 1) * 80 // 100:
                continue

            # Octave check
            octave_ok = 0
            octave_checks = 0
            for i in range(0, N - 12, 12):
                f_lo_v = bin_lo[i] | (bin_hi[i] << 8)
                f_hi_v = bin_lo[i + 12] | (bin_hi[i + 12] << 8)
                if f_lo_v > 0:
                    octave_checks += 1
                    r = f_hi_v / f_lo_v
                    if 1.8 <= r <= 2.2:
                        octave_ok += 1

            if octave_checks < 2 or octave_ok < octave_checks * 80 // 100:
                continue

            # Validate against observed frequencies
            cand_freqs = [bin_lo[i] | (bin_hi[i] << 8) for i in range(N)]
            matched = 0
            for obs in stable_freqs:
                for cf in cand_freqs:
                    if cf == 0:
                        continue
                    if 0.98 <= obs / cf <= 1.02:
                        matched += 1
                        break
            match_rate = matched / len(stable_freqs) if stable_freqs else 0

            if match_rate >= 0.5:
                if verbose:
                    print(f"  Found table at binary offset {pos} "
                          f"(${load_addr + pos:04X}), size={N}, "
                          f"match={matched}/{len(stable_freqs)} ({match_rate:.0%})")
                return pos

    # Strategy 2: Exact substring match of reconstructed lo bytes
    n = len(lo)
    if n >= 12:
        for window in range(n, 11, -1):
            for start in range(n - window + 1):
                needle = lo[start:start + window]
                pos = binary.find(needle)
                if pos != -1:
                    if verbose:
                        print(f"  Found lo bytes at binary offset {pos} "
                              f"(${load_addr + pos:04X}), matched {window} bytes")
                    return pos - start

    return None


def reconstruct_freq_table(sid_path, duration=30, verbose=False):
    """Reconstruct frequency table from siddump register output.

    Args:
        sid_path: path to .sid file
        duration: seconds to capture (default 30)
        verbose: print progress info

    Returns dict with:
        - notes: list of (note_number, frequency) tuples
        - tuning: 'PAL', 'NTSC', or 'custom'
        - ratio_to_pal: float (1.0 = exact PAL)
        - lo_bytes: reconstructed lo table bytes
        - hi_bytes: reconstructed hi table bytes
        - binary_match_offset: offset in binary where table was found (or None)
    """
    if verbose:
        print(f"Reconstructing freq table from: {sid_path}")

    with open(sid_path, 'rb') as f:
        data = f.read()
    header, binary, load_addr = parse_psid_header(data)

    if verbose:
        print(f"  Load addr: ${load_addr:04X}, binary size: {len(binary)} bytes")
        print(f"  Running siddump for {duration} seconds...")

    frames = _run_siddump(sid_path, duration)
    if verbose:
        print(f"  Captured {len(frames)} frames")

    stable_freqs, all_freqs = _extract_frequencies(frames)
    if verbose:
        print(f"  Unique stable frequencies: {len(stable_freqs)}")
        print(f"  Unique total frequencies: {len(all_freqs)}")

    if not stable_freqs:
        return {
            'notes': [],
            'tuning': 'unknown',
            'ratio_to_pal': 0.0,
            'lo_bytes': b'',
            'hi_bytes': b'',
            'binary_match_offset': None,
        }

    note_dict = _cluster_to_notes(stable_freqs, verbose=verbose)
    pal_result = compare_to_pal(note_dict)

    lo, hi, first_note, num_notes = _build_table(note_dict, verbose=verbose)

    # Build notes list as (note_number, frequency) tuples
    notes_list = sorted(note_dict.items())

    if num_notes < 12:
        return {
            'notes': notes_list,
            'tuning': pal_result['tuning'],
            'ratio_to_pal': pal_result['ratio_to_pal'],
            'lo_bytes': lo,
            'hi_bytes': hi,
            'binary_match_offset': None,
        }

    # Search binary for the table
    if verbose:
        print(f"\n  Searching binary for freq table...")
    match_offset = _search_binary(binary, load_addr, lo, hi,
                                   stable_freqs, note_dict, verbose=verbose)

    return {
        'notes': notes_list,
        'tuning': pal_result['tuning'],
        'ratio_to_pal': pal_result['ratio_to_pal'],
        'lo_bytes': lo,
        'hi_bytes': hi,
        'binary_match_offset': match_offset,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Reconstruct freq table from siddump output')
    parser.add_argument('sid_file', help='Path to SID file')
    parser.add_argument('--duration', type=int, default=30,
                        help='Seconds to capture (default: 30)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose output')
    args = parser.parse_args()

    if not os.path.exists(args.sid_file):
        print(f'ERROR: {args.sid_file} not found', file=sys.stderr)
        sys.exit(1)

    result = reconstruct_freq_table(args.sid_file, duration=args.duration,
                                     verbose=args.verbose)

    print(f"\n{'='*60}")
    print(f"Frequency Reconstruction: {os.path.basename(args.sid_file)}")
    print(f"{'='*60}")

    if not result['notes']:
        print("No frequencies observed in siddump output.")
        return

    print(f"Notes found: {len(result['notes'])}")
    print(f"Tuning: {result['tuning']}")
    print(f"Ratio to PAL: {result['ratio_to_pal']:.6f}")

    if result['ratio_to_pal'] > 0:
        cents = 1200 * math.log2(result['ratio_to_pal'])
        print(f"Cents offset from PAL: {cents:.1f}")

    print(f"Table size: {len(result['lo_bytes'])} bytes")

    if result['binary_match_offset'] is not None:
        print(f"Found in binary: YES (offset {result['binary_match_offset']})")
    else:
        print(f"Found in binary: NO (frequencies likely computed at runtime)")

    # Show first/last few notes
    if result['notes']:
        print(f"\nNote samples:")
        for note_num, freq in result['notes'][:5]:
            print(f"  Note {note_num:3d}: freq=0x{freq:04X} ({freq})")
        if len(result['notes']) > 10:
            print(f"  ...")
        for note_num, freq in result['notes'][-3:]:
            print(f"  Note {note_num:3d}: freq=0x{freq:04X} ({freq})")


if __name__ == '__main__':
    main()
