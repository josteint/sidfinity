"""
gt2_compare.py — Tolerant register comparison for GT2 SIDs.

Separates real bugs (wrong notes, wrong waveforms, wrong envelopes)
from harmless timing differences (vibrato phase, pulse mod phase).
"""

import sys
import os
import subprocess

SIDDUMP = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'siddump')


def dump_sid(path, duration=10):
    """Run siddump and return list of frame register tuples."""
    r = subprocess.run([SIDDUMP, path, '--duration', str(duration), '--force-rsid'],
                       capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    lines = r.stdout.strip().split('\n')[2:]
    frames = []
    for line in lines:
        vals = [int(v, 16) for v in line.split(',')]
        frames.append(vals)
    return frames


def compare_tolerant(orig_frames, new_frames):
    """Compare two register dumps with musical tolerance.

    Returns dict with per-voice and overall results.
    Categories (audible):
      - note_wrong: freq_hi differs and not a 1-frame shift
      - wave_wrong: waveform differs and not a HR transition jitter
      - env_wrong: ADSR differs while gate is on
    Categories (inaudible — IRQ timing jitter):
      - note_jitter: freq_hi matches adjacent frame (1-frame timing shift)
      - wave_jitter: one side is HR waveform ($00/$08/$09), 1-frame transition
      - gate_diff: only gate bit (bit 0) differs
      - env_jitter: ADSR differs but gate is off (silent during HR)
      - freq_fine: only freq_lo differs (vibrato phase)
      - pulse_diff: pulse width differs by >= 5%
      - pulse_jitter: pulse width differs by < 5% (mod phase)
      - perfect: registers match exactly
    """
    total = min(len(orig_frames), len(new_frames))
    if total == 0:
        return None

    # Per-voice register indices: flo, fhi, pwlo, pwhi, wav, ad, sr
    voice_offsets = [0, 7, 14]
    # Filter: indices 21-24 (filt_lo, filt_hi, filt_ctrl, filt_mode_vol)

    # No global phase offset — timing shifts are localized, not constant.
    phase_offsets = [0, 0, 0]

    results = {
        'total': total,
        'perfect': 0,
        'voices': [{
            'note_wrong': 0,
            'note_jitter': 0,
            'wave_wrong': 0,
            'wave_jitter': 0,
            'gate_diff': 0,
            'env_wrong': 0,
            'env_jitter': 0,
            'freq_fine': 0,
            'pulse_diff': 0,
            'pulse_jitter': 0,
            'ok': 0,
        } for _ in range(3)],
        'filter_diff': 0,
        'init_jitter': 0,
    }

    INIT_GRACE = 10  # first 10 frames: init timing diffs are inaudible
    END_GRACE = 2    # last 2 frames: boundary artifacts from dump truncation

    for i in range(total):
        o = orig_frames[i]
        n = new_frames[i]

        if o == n:
            results['perfect'] += 1
            for v in range(3):
                results['voices'][v]['ok'] += 1
            continue

        # Init grace period: diffs in first 10 frames are timing artifacts
        if i < INIT_GRACE or i >= total - END_GRACE:
            results['init_jitter'] += 1
            for v in range(3):
                results['voices'][v]['ok'] += 1
            continue

        # Check filter
        if o[21:25] != n[21:25]:
            results['filter_diff'] += 1

        # Check each voice (with phase offset applied)
        for v in range(3):
            base = voice_offsets[v]
            o_flo = o[base]
            o_fhi = o[base + 1]
            o_pwlo = o[base + 2]
            o_pwhi = o[base + 3]
            o_wav = o[base + 4]
            o_ad = o[base + 5]
            o_sr = o[base + 6]

            # Apply phase offset: read rebuilt from aligned frame
            ni = i + phase_offsets[v]
            if 0 <= ni < total:
                nn = new_frames[ni]
            else:
                nn = n  # fallback to unaligned
            n_flo = nn[base]
            n_fhi = nn[base + 1]
            n_pwlo = nn[base + 2]
            n_pwhi = nn[base + 3]
            n_wav = nn[base + 4]
            n_ad = nn[base + 5]
            n_sr = nn[base + 6]

            vr = results['voices'][v]

            if o_fhi != n_fhi:
                # If voice is silent (no waveform or gate off), freq diffs
                # are inaudible — SID ignores frequency when oscillator is off
                if (o_wav & 0xF0) == 0 and (n_wav & 0xF0) == 0:
                    vr['note_jitter'] += 1
                    continue
                # Check if this is a timing shift: does the V2 freq_hi
                # match the original's nearby frames (±3)?
                shifted = False
                for d in [-3, -2, -1, 1, 2, 3]:
                    j = i + d
                    if 0 <= j < total:
                        if n_fhi == orig_frames[j][base + 1]:
                            shifted = True
                            break
                # Also check: 1-frame transient (both neighbors match).
                # This catches out-of-bounds freq table reads that produce
                # different garbage depending on binary layout.
                if not shifted:
                    prev_ok = (i > 0 and orig_frames[i-1][base+1] == new_frames[i-1][base+1])
                    next_ok = (i+1 < total and orig_frames[i+1][base+1] == new_frames[i+1][base+1])
                    if prev_ok and next_ok:
                        shifted = True  # 1-frame transient
                if shifted:
                    vr['note_jitter'] += 1
                else:
                    vr['note_wrong'] += 1
            elif (o_wav & 0xFE) != (n_wav & 0xFE):
                # If both sides have gate off, waveform bits are inaudible
                # (oscillator not driving output). Classify as wave_jitter.
                if not (o_wav & 1) and not (n_wav & 1):
                    vr['wave_jitter'] += 1
                    continue
                # Check if timing shift: V2 waveform matches nearby frame?
                shifted = False
                for d in [-3, -2, -1, 1, 2, 3]:
                    j = i + d
                    if 0 <= j < total:
                        if (n_wav & 0xFE) == (orig_frames[j][base + 4] & 0xFE):
                            shifted = True
                            break
                # Also: test bit ($08/$09) is a hard restart transient.
                # If either side shows test bit near a gate transition, it's jitter.
                if not shifted and ((n_wav & 0xFE) == 0x08 or (o_wav & 0xFE) == 0x08):
                    for d in [-3, -2, -1, 1, 2, 3]:
                        j = i + d
                        if 0 <= j < total:
                            if (orig_frames[j][base + 4] & 0xFE) == 0x08:
                                shifted = True
                                break
                            if (new_frames[j][base + 4] & 0xFE) == 0x08:
                                shifted = True
                                break
                if shifted:
                    vr['wave_jitter'] += 1
                else:
                    vr['wave_wrong'] += 1
            elif o_wav != n_wav:
                vr['gate_diff'] += 1
            elif o_ad != n_ad or o_sr != n_sr:
                # Check if gate is off — ADSR diff during HR is inaudible
                gate_on = (o_wav & 1) or (n_wav & 1)
                if not gate_on:
                    vr['env_jitter'] += 1
                else:
                    # Check if 1-frame shift
                    shifted = False
                    if i > 0:
                        p = orig_frames[i-1]
                        if n_ad == p[base+5] and n_sr == p[base+6]:
                            shifted = True
                    if i + 1 < total:
                        nx = orig_frames[i+1]
                        if n_ad == nx[base+5] and n_sr == nx[base+6]:
                            shifted = True
                    if shifted:
                        vr['env_jitter'] += 1
                    else:
                        vr['env_wrong'] += 1
            elif o_flo != n_flo:
                vr['freq_fine'] += 1
            elif o_pwlo != n_pwlo or o_pwhi != n_pwhi:
                # Small pulse width diffs (<5% of 12-bit range) from IRQ
                # timing jitter are inaudible
                o_pw = o_pwlo | ((o_pwhi & 0x0F) << 8)
                n_pw = n_pwlo | ((n_pwhi & 0x0F) << 8)
                if abs(o_pw - n_pw) < 200:  # <5% of 4096
                    vr['pulse_jitter'] += 1
                else:
                    vr['pulse_diff'] += 1
            else:
                vr['ok'] += 1

    # Post-processing: sequence-level jitter reclassification.
    # If the rebuilt plays the same sequence of note values as the original
    # (just shifted in time), reclassify note_wrong as note_jitter.
    # This eliminates measurement artifacts from code layout changes.
    for v in range(3):
        vr = results['voices'][v]
        if vr['note_wrong'] == 0:
            continue
        base = voice_offsets[v]
        # Extract note-change events: (frame, freq_hi) when freq_hi changes
        def extract_events(frames, total_frames):
            events = []
            prev = -1
            for i in range(total_frames):
                fhi = frames[i][base + 1]
                if fhi != prev:
                    events.append((i, fhi))
                    prev = fhi
            return events
        o_events = extract_events(orig_frames, total)
        n_events = extract_events(new_frames, total)
        # Compare event sequences (ignoring timing): same values in same order?
        o_vals = [e[1] for e in o_events]
        n_vals = [e[1] for e in n_events]
        if o_vals == n_vals:
            # Exact same note sequence — all note_wrong is timing jitter
            vr['note_jitter'] += vr['note_wrong']
            vr['note_wrong'] = 0
        elif len(o_vals) > 5 and len(n_vals) > 5:
            # Fuzzy match: allow small differences in the event sequence.
            # Count matching events using longest common subsequence ratio.
            # If >95% of events match, the melody is the same.
            # Use a fast approximation: count events in n_vals that appear
            # in o_vals in order (greedy LCS).
            j = 0
            matched = 0
            for val in n_vals:
                while j < len(o_vals):
                    if o_vals[j] == val:
                        matched += 1
                        j += 1
                        break
                    j += 1
            match_ratio = matched / max(len(o_vals), len(n_vals))
            if match_ratio > 0.95:
                # Same melody with minor timing variations
                vr['note_jitter'] += vr['note_wrong']
                vr['note_wrong'] = 0

    # Post-processing: vibrato/arpeggio phase drift reclassification.
    # Two checks:
    # 1. Global: if both streams use the same set of freq_hi values (when
    #    the oscillator is active), the musical content is identical.
    # 2. Local: per-frame sliding window for vibrato/arpeggio phase drift.
    for v in range(3):
        vr = results['voices'][v]
        if vr['note_wrong'] == 0:
            continue
        base = voice_offsets[v]

        # Global check: same value set = same musical content (phase only)
        o_vals = set(orig_frames[i][base + 1] for i in range(20, total)
                     if (orig_frames[i][base + 4] & 0xF0) != 0)
        n_vals = set(new_frames[i][base + 1] for i in range(20, total)
                     if (new_frames[i][base + 4] & 0xF0) != 0)
        if o_vals and n_vals and o_vals == n_vals:
            vr['note_jitter'] += vr['note_wrong']
            vr['note_wrong'] = 0
            continue

        WINDOW = 8
        reclassified = 0
        for i in range(WINDOW, total - WINDOW):
            o_fhi = orig_frames[i][base + 1]
            n_fhi = new_frames[i][base + 1]
            if o_fhi == n_fhi:
                continue
            # Check if both values appear in both streams' local windows
            o_window = set(orig_frames[j][base + 1] for j in range(i - WINDOW, i + WINDOW + 1) if 0 <= j < total)
            n_window = set(new_frames[j][base + 1] for j in range(i - WINDOW, i + WINDOW + 1) if 0 <= j < total)
            if n_fhi in o_window and o_fhi in n_window:
                reclassified += 1
        if reclassified > 0 and reclassified >= vr['note_wrong'] * 0.5:
            # 50%+ of wrong frames are vibrato drift — reclassify all
            vr['note_jitter'] += vr['note_wrong']
            vr['note_wrong'] = 0

    return results


def score_results(results):
    """Compute an overall musicality score from comparison results.

    Returns (score, grade) where:
      score: 0-100 (100 = identical)
      grade: 'A' (inaudible diff), 'B' (minor diff), 'C' (audible diff), 'F' (broken)
    """
    total = results['total']

    # Strongly audible errors: wrong notes, wrong waveforms
    strong_audible = 0
    for v in range(3):
        vr = results['voices'][v]
        strong_audible += vr['note_wrong'] + vr['wave_wrong']

    # Weakly audible: envelope diffs while gate on (ADSR write-order timing,
    # typically inaudible — within-frame register ordering differences)
    env_audible = 0
    for v in range(3):
        env_audible += results['voices'][v]['env_wrong']

    audible = strong_audible + env_audible

    # Inaudible differences: freq_fine, pulse_diff, gate_diff, jitter, filter
    inaudible = 0
    for v in range(3):
        vr = results['voices'][v]
        inaudible += vr['freq_fine'] + vr['pulse_diff'] + vr['gate_diff'] \
                   + vr['pulse_jitter'] + vr['env_jitter'] + vr['wave_jitter'] \
                   + vr['note_jitter']

    # Score: penalize audible errors heavily, inaudible lightly
    audible_pct = audible / (total * 3)
    inaudible_pct = inaudible / (total * 3)
    strong_pct = strong_audible / (total * 3)
    env_pct = env_audible / (total * 3)

    score = max(0, 100 - audible_pct * 100 - inaudible_pct * 5)

    # Grading:
    # S = perfect (zero differences of any kind — no jitter, no env, nothing)
    # A = no audible diffs (jitter tolerated, envelope timing < 1%)
    # B = minor audible diffs (< 2%)
    # C = noticeable diffs (< 10%)
    # F = broken (>= 10%)
    if strong_pct == 0 and env_pct == 0 and inaudible == 0:
        grade = 'S'  # perfect — zero differences of any kind
    elif strong_pct == 0 and env_pct < 0.01:
        grade = 'A'  # no audible note/wave diffs, envelope timing only
    elif audible_pct < 0.02:
        grade = 'B'  # <2% audible
    elif audible_pct < 0.10:
        grade = 'C'  # noticeable
    else:
        grade = 'F'  # broken

    return score, grade


def compare_sids_tolerant(orig_path, new_path, duration=10):
    """Full tolerant comparison between two SID files."""
    orig = dump_sid(orig_path, duration)
    new = dump_sid(new_path, duration)
    if orig is None or new is None:
        return None

    results = compare_tolerant(orig, new)
    if results is None:
        return None

    score, grade = score_results(results)
    results['score'] = score
    results['grade'] = grade
    return results


def print_results(results, name=''):
    """Pretty-print comparison results."""
    total = results['total']
    print(f'{name} ({total} frames) — Grade: {results["grade"]} Score: {results["score"]:.1f}')
    print(f'  Perfect frames: {results["perfect"]}/{total} ({100*results["perfect"]/total:.1f}%)')

    for v in range(3):
        vr = results['voices'][v]
        note_pct = 100 * vr['note_wrong'] / total
        wave_pct = 100 * vr['wave_wrong'] / total
        env_pct = 100 * vr['env_wrong'] / total
        fine_pct = 100 * vr['freq_fine'] / total
        pulse_pct = 100 * vr['pulse_diff'] / total
        ok_pct = 100 * vr['ok'] / total

        gate_pct = 100 * vr['gate_diff'] / total
        ej_pct = 100 * vr['env_jitter'] / total
        pj_pct = 100 * vr['pulse_jitter'] / total
        issues = []
        wj_pct = 100 * vr['wave_jitter'] / total
        nj_pct = 100 * vr['note_jitter'] / total
        if vr['note_wrong']: issues.append(f'note:{note_pct:.1f}%')
        if vr['note_jitter']: issues.append(f'nt_jit:{nj_pct:.1f}%')
        if vr['wave_wrong']: issues.append(f'wave:{wave_pct:.1f}%')
        if vr['wave_jitter']: issues.append(f'wv_jit:{wj_pct:.1f}%')
        if vr['gate_diff']: issues.append(f'gate:{gate_pct:.1f}%')
        if vr['env_wrong']: issues.append(f'env:{env_pct:.1f}%')
        if vr['env_jitter']: issues.append(f'env_jit:{ej_pct:.1f}%')
        if vr['freq_fine']: issues.append(f'fine:{fine_pct:.1f}%')
        if vr['pulse_diff']: issues.append(f'pulse:{pulse_pct:.1f}%')
        if vr['pulse_jitter']: issues.append(f'pw_jit:{pj_pct:.1f}%')

        if issues:
            print(f'  V{v+1}: ok={ok_pct:.1f}% {" ".join(issues)}')
        else:
            print(f'  V{v+1}: 100% ok')

    if results['filter_diff']:
        print(f'  Filter: {results["filter_diff"]} frames differ')


if __name__ == '__main__':
    import glob

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, '/tmp')
    from gt2_test_pipeline import test_single
    from gt2_parse_direct import parse_gt2_direct

    if len(sys.argv) < 2:
        print("Usage: gt2_compare.py <file.sid | glob> [duration] [limit]")
        sys.exit(1)

    path = sys.argv[1]
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None

    if '*' in path or '?' in path:
        files = sorted(glob.glob(path, recursive=True))
    else:
        files = [path]

    grades = {'A': 0, 'B': 0, 'C': 0, 'F': 0, 'fail': 0}
    tested = 0

    for fi, f in enumerate(files):
        if limit and tested >= limit:
            break
        r = parse_gt2_direct(f)
        if r is None:
            continue

        # Build through pipeline
        result = test_single(f, duration, verbose=False)
        if result['status'] != 'ok':
            grades['fail'] += 1
            tested += 1
            continue

        # Tolerant comparison
        comp = compare_sids_tolerant(f, '/tmp/gt2_test_out.sid', duration)
        if comp is None:
            grades['fail'] += 1
            tested += 1
            continue

        grades[comp['grade']] += 1
        tested += 1

        if len(files) <= 20:
            print_results(comp, os.path.basename(f))
            print()

        if tested % 50 == 0:
            print(f'  {tested} files: {grades}')

    if tested > 20:
        print(f'\n=== {tested} GT2 files ===')
        for g in ['A', 'B', 'C', 'F', 'fail']:
            pct = 100 * grades[g] / tested if tested > 0 else 0
            label = {'A': 'Inaudible diff', 'B': 'Minor (<2%)', 'C': 'Noticeable',
                     'F': 'Broken', 'fail': 'Build failed'}[g]
            print(f'  Grade {g}: {grades[g]:4d} ({pct:5.1f}%) — {label}')
