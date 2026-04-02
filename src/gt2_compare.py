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
    r = subprocess.run([SIDDUMP, path, '--duration', str(duration)],
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
    Categories:
      - note_wrong: freq_hi differs (audible: wrong note)
      - wave_wrong: waveform ctrl byte differs (audible: wrong timbre)
      - env_wrong: AD or SR differs (audible: wrong envelope)
      - freq_fine: only freq_lo differs (likely inaudible: vibrato phase)
      - pulse_diff: only pulse width differs (often inaudible: mod phase)
      - filter_diff: only filter regs differ
      - perfect: registers match exactly
    """
    total = min(len(orig_frames), len(new_frames))
    if total == 0:
        return None

    # Per-voice register indices: flo, fhi, pwlo, pwhi, wav, ad, sr
    voice_offsets = [0, 7, 14]
    # Filter: indices 21-24 (filt_lo, filt_hi, filt_ctrl, filt_mode_vol)

    results = {
        'total': total,
        'perfect': 0,
        'voices': [{
            'note_wrong': 0,
            'wave_wrong': 0,
            'env_wrong': 0,
            'freq_fine': 0,
            'pulse_diff': 0,
            'ok': 0,
        } for _ in range(3)],
        'filter_diff': 0,
    }

    for i in range(total):
        o = orig_frames[i]
        n = new_frames[i]

        if o == n:
            results['perfect'] += 1
            for v in range(3):
                results['voices'][v]['ok'] += 1
            continue

        # Check filter
        if o[21:25] != n[21:25]:
            results['filter_diff'] += 1

        # Check each voice
        for v in range(3):
            base = voice_offsets[v]
            o_flo = o[base]
            o_fhi = o[base + 1]
            o_pwlo = o[base + 2]
            o_pwhi = o[base + 3]
            o_wav = o[base + 4]
            o_ad = o[base + 5]
            o_sr = o[base + 6]

            n_flo = n[base]
            n_fhi = n[base + 1]
            n_pwlo = n[base + 2]
            n_pwhi = n[base + 3]
            n_wav = n[base + 4]
            n_ad = n[base + 5]
            n_sr = n[base + 6]

            vr = results['voices'][v]

            if o_fhi != n_fhi:
                vr['note_wrong'] += 1
            elif o_wav != n_wav:
                vr['wave_wrong'] += 1
            elif o_ad != n_ad or o_sr != n_sr:
                vr['env_wrong'] += 1
            elif o_flo != n_flo:
                vr['freq_fine'] += 1
            elif o_pwlo != n_pwlo or o_pwhi != n_pwhi:
                vr['pulse_diff'] += 1
            else:
                vr['ok'] += 1

    return results


def score_results(results):
    """Compute an overall musicality score from comparison results.

    Returns (score, grade) where:
      score: 0-100 (100 = identical)
      grade: 'A' (inaudible diff), 'B' (minor diff), 'C' (audible diff), 'F' (broken)
    """
    total = results['total']

    # Audible errors: wrong notes, wrong waveforms, wrong envelopes
    audible = 0
    for v in range(3):
        vr = results['voices'][v]
        audible += vr['note_wrong'] + vr['wave_wrong'] + vr['env_wrong']

    # Inaudible differences: freq_fine, pulse_diff, filter
    inaudible = 0
    for v in range(3):
        vr = results['voices'][v]
        inaudible += vr['freq_fine'] + vr['pulse_diff']

    # Score: penalize audible errors heavily, inaudible lightly
    audible_pct = audible / (total * 3)  # fraction of voice-frames with audible error
    inaudible_pct = inaudible / (total * 3)

    score = max(0, 100 - audible_pct * 100 - inaudible_pct * 5)

    if audible_pct == 0:
        grade = 'A'  # no audible differences
    elif audible_pct < 0.02:
        grade = 'B'  # <2% audible (probably just startup/transient)
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

        issues = []
        if vr['note_wrong']: issues.append(f'note:{note_pct:.1f}%')
        if vr['wave_wrong']: issues.append(f'wave:{wave_pct:.1f}%')
        if vr['env_wrong']: issues.append(f'env:{env_pct:.1f}%')
        if vr['freq_fine']: issues.append(f'fine:{fine_pct:.1f}%')
        if vr['pulse_diff']: issues.append(f'pulse:{pulse_pct:.1f}%')

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
