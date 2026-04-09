"""
gt2_triage.py -- Automated F-grade GT2 song triager.

Runs all GT2 SIDs through the pipeline, identifies F-grade songs,
and categorizes them into bug buckets for investigation.

Usage:
    cd /home/jtr/sidfinity && source src/env.sh
    python3 src/gt2_triage.py [--limit N] [--duration D] 2>/dev/null
"""

import sys
import os
import json
import time
import multiprocessing
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HVSC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'C64Music')
SIDID_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sidid_full.txt')
OUTPUT_PATH = '/tmp/gt2_triage.json'


def find_gt2_sids():
    """Find all GoatTracker V2 SIDs using sidid_full.txt."""
    sids = []
    with open(SIDID_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('Using '):
                continue
            parts = line.split()
            if len(parts) >= 2 and 'GoatTracker_V2' in parts[-1]:
                rel_path = parts[0]
                full_path = os.path.join(HVSC_ROOT, rel_path)
                if os.path.exists(full_path):
                    sids.append(full_path)
    return sids


def _process_one(args):
    """Process a single SID file. Returns result dict or None."""
    sid_path, duration = args
    try:
        from gt2_to_usf import gt2_to_usf
        from usf_to_sid import usf_to_sid
        from gt2_compare import compare_tolerant, score_results, dump_sid
        from gt2_detect_version import detect_gt2_player_group
        from detect_flags import detect_gt2_flags

        # Step 1: Convert SID -> USF
        song = gt2_to_usf(sid_path)
        if song is None:
            return {'path': sid_path, 'status': 'parse_fail'}

        # Detect group
        ver = detect_gt2_player_group(sid_path)
        group = ver['group'] if ver else '?'

        # Detect features from USF
        flags = detect_gt2_flags(song)
        features = {
            'toneporta': flags.get('NOTONEPORTA', 1) == 0,
            'portamento': flags.get('NOPORTAMENTO', 1) == 0,
            'vibrato': flags.get('NOVIB', 1) == 0,
            'funktempo': flags.get('NOFUNKTEMPO', 1) == 0,
            'wave_cmd': flags.get('NOWAVECMD', 1) == 0,
            'filter': flags.get('NOFILTER', 1) == 0,
            'pulse': flags.get('NOPULSE', 1) == 0,
            'wave_delay': flags.get('NOWAVEDELAY', 1) == 0,
        }

        # Step 2: USF -> SID
        tmp_sid = f'/tmp/gt2_triage_{os.getpid()}.sid'
        sid_bytes, _ = usf_to_sid(song, tmp_sid)
        if not sid_bytes:
            return {'path': sid_path, 'status': 'build_fail', 'group': group, 'features': features}

        # Step 3: Dump and compare
        orig_frames = dump_sid(sid_path, duration)
        new_frames = dump_sid(tmp_sid, duration)

        if orig_frames is None:
            return {'path': sid_path, 'status': 'dump_fail_orig', 'group': group, 'features': features}
        if new_frames is None:
            return {'path': sid_path, 'status': 'dump_fail_new', 'group': group, 'features': features}

        results = compare_tolerant(orig_frames, new_frames)
        if results is None:
            return {'path': sid_path, 'status': 'compare_fail', 'group': group, 'features': features}

        score, grade = score_results(results)

        # Per-voice error details
        voice_errors = []
        total = results['total']
        for v in range(3):
            vr = results['voices'][v]
            # Find first error frame
            first_error = _find_first_error_frame(orig_frames, new_frames, v, total)

            # Check if original voice is silent (all-zero fhi when waveform active)
            base = v * 7
            silent_orig = True
            for fi in range(min(total, len(orig_frames))):
                fhi = orig_frames[fi][base + 1]
                wav = orig_frames[fi][base + 4]
                if (wav & 0xF0) != 0 and fhi != 0:
                    silent_orig = False
                    break

            voice_errors.append({
                'note_wrong': vr['note_wrong'],
                'wave_wrong': vr['wave_wrong'],
                'env_wrong': vr['env_wrong'],
                'note_jitter': vr['note_jitter'],
                'wave_jitter': vr['wave_jitter'],
                'first_error_frame': first_error,
                'silent_orig': silent_orig,
            })

        # Determine value set overlap for timing_drift detection
        value_overlaps = []
        for v in range(3):
            base = v * 7
            o_vals = set(orig_frames[i][base + 1] for i in range(min(20, total), total)
                         if (orig_frames[i][base + 4] & 0xF0) != 0)
            n_vals = set(new_frames[i][base + 1] for i in range(min(20, total), total)
                         if i < len(new_frames) and (new_frames[i][base + 4] & 0xF0) != 0)
            if o_vals and n_vals:
                overlap = len(o_vals & n_vals) / max(len(o_vals | n_vals), 1)
            else:
                overlap = 1.0
            value_overlaps.append(overlap)

        return {
            'path': sid_path,
            'status': 'ok',
            'group': group,
            'score': round(score, 1),
            'grade': grade,
            'total_frames': total,
            'features': features,
            'voices': voice_errors,
            'value_overlaps': value_overlaps,
        }

    except Exception as e:
        return {
            'path': sid_path,
            'status': 'error',
            'error': f'{type(e).__name__}: {str(e)[:200]}',
        }


def _find_first_error_frame(orig_frames, new_frames, voice, total):
    """Find the first frame where this voice has a real error (note_wrong or wave_wrong)."""
    base = voice * 7
    INIT_GRACE = 10
    for i in range(INIT_GRACE, total):
        if i >= len(orig_frames) or i >= len(new_frames):
            break
        o = orig_frames[i]
        n = new_frames[i]
        o_fhi = o[base + 1]
        n_fhi = n[base + 1]
        o_wav = o[base + 4]
        n_wav = n[base + 4]

        if o_fhi != n_fhi and ((o_wav & 0xF0) != 0 or (n_wav & 0xF0) != 0):
            return i
        if (o_wav & 0xFE) != (n_wav & 0xFE):
            return i
    return -1  # no error found


def categorize(result):
    """Assign bug bucket categories to an F-grade result."""
    if result.get('grade') != 'F':
        return []

    categories = []
    voices = result.get('voices', [])
    if not voices:
        return ['unknown']

    # Count voices with errors
    voices_with_note_errors = sum(1 for v in voices if v['note_wrong'] > 0)
    voices_with_wave_errors = sum(1 for v in voices if v['wave_wrong'] > 0)
    voices_with_any_error = sum(1 for v in voices if v['note_wrong'] > 0 or v['wave_wrong'] > 0 or v['env_wrong'] > 0)

    total_note_wrong = sum(v['note_wrong'] for v in voices)
    total_wave_wrong = sum(v['wave_wrong'] for v in voices)

    # Timing drift: same note values, different timing
    overlaps = result.get('value_overlaps', [])
    if overlaps and all(o > 0.80 for o in overlaps) and total_note_wrong > 0:
        categories.append('timing_drift')

    # Early vs late errors
    first_errors = [v['first_error_frame'] for v in voices if v['first_error_frame'] >= 0]
    if first_errors:
        earliest = min(first_errors)
        if earliest < 50:
            categories.append('wrong_notes_early')
        elif earliest > 200:
            categories.append('wrong_notes_late')

    # Voice distribution
    if voices_with_any_error == 1:
        categories.append('single_voice')
    elif voices_with_any_error == 3:
        categories.append('all_voices')

    # Wave vs note dominant
    if total_wave_wrong > total_note_wrong and total_wave_wrong > 0:
        categories.append('wave_dominant')

    if not categories:
        categories.append('uncategorized')

    return categories


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Triage F-grade GT2 SIDs')
    parser.add_argument('--limit', type=int, default=0, help='Max songs to process (0=all)')
    parser.add_argument('--duration', type=int, default=10, help='Dump duration in seconds')
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 64, help='Worker count')
    args = parser.parse_args()

    print('Finding GT2 SIDs...')
    all_sids = find_gt2_sids()
    print(f'Found {len(all_sids)} GT2 SIDs in sidid list')

    if args.limit > 0:
        all_sids = all_sids[:args.limit]

    work = [(sid, args.duration) for sid in all_sids]

    print(f'Processing {len(work)} SIDs with {args.jobs} workers...')
    t0 = time.time()

    with multiprocessing.Pool(args.jobs) as pool:
        results = pool.map(_process_one, work, chunksize=4)

    elapsed = time.time() - t0
    print(f'Done in {elapsed:.1f}s\n')

    # Separate by grade
    grades = {'A': [], 'B': [], 'C': [], 'F': []}
    errors = []
    for r in results:
        if r is None:
            continue
        if r['status'] != 'ok':
            errors.append(r)
            continue
        g = r['grade']
        if g in grades:
            grades[g].append(r)
        else:
            grades.setdefault(g, []).append(r)

    # Categorize F-grade songs
    bucket_counts = {}
    f_results = grades['F']
    for r in f_results:
        cats = categorize(r)
        r['categories'] = cats
        for c in cats:
            bucket_counts[c] = bucket_counts.get(c, 0) + 1

    # Feature correlation for F-grade
    feature_counts = {}
    for r in f_results:
        feats = r.get('features', {})
        for fname, fval in feats.items():
            if fval:
                feature_counts[fname] = feature_counts.get(fname, 0) + 1

    # Group distribution for F-grade
    group_counts = {}
    for r in f_results:
        g = r.get('group', '?')
        group_counts[g] = group_counts.get(g, 0) + 1

    # Print summary
    total_ok = sum(len(v) for v in grades.values())
    print(f'=== GT2 Triage Summary ===')
    print(f'Total processed: {len(results)} ({len(errors)} errors, {total_ok} graded)')
    print()
    for g in ['A', 'B', 'C', 'F']:
        n = len(grades[g])
        pct = 100 * n / total_ok if total_ok else 0
        print(f'  Grade {g}: {n:5d} ({pct:5.1f}%)')
    print()

    print(f'=== F-Grade Analysis ({len(f_results)} songs) ===')
    print()

    print('Bug Buckets:')
    for bucket, count in sorted(bucket_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(f_results) if f_results else 0
        print(f'  {bucket:25s}: {count:4d} ({pct:5.1f}%)')
    print()

    print('Features used by F-grade songs:')
    for fname, count in sorted(feature_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(f_results) if f_results else 0
        print(f'  {fname:20s}: {count:4d} ({pct:5.1f}%)')
    print()

    print('Player groups in F-grade:')
    for g, count in sorted(group_counts.items(), key=lambda x: -x[1]):
        pct = 100 * count / len(f_results) if f_results else 0
        print(f'  Group {g}: {count:4d} ({pct:5.1f}%)')
    print()

    # Error breakdown
    if errors:
        error_types = {}
        for e in errors:
            s = e.get('status', 'unknown')
            error_types[s] = error_types.get(s, 0) + 1
        print(f'Pipeline errors ({len(errors)}):')
        for s, c in sorted(error_types.items(), key=lambda x: -x[1]):
            print(f'  {s:20s}: {c}')
        print()

    # Top 10 worst F-grade songs (lowest score)
    f_sorted = sorted(f_results, key=lambda r: r['score'])
    print('Worst 10 F-grade songs:')
    for r in f_sorted[:10]:
        name = os.path.basename(r['path'])
        cats = ', '.join(r.get('categories', []))
        voice_summary = []
        for vi, v in enumerate(r['voices']):
            errs = []
            if v['note_wrong']: errs.append(f'n={v["note_wrong"]}')
            if v['wave_wrong']: errs.append(f'w={v["wave_wrong"]}')
            if v['env_wrong']: errs.append(f'e={v["env_wrong"]}')
            if errs:
                voice_summary.append(f'V{vi+1}({",".join(errs)})')
        print(f'  {r["score"]:5.1f}  {name:40s} [{cats}] {" ".join(voice_summary)}')
    print()

    # Save full results
    output = {
        'summary': {
            'total': len(results),
            'errors': len(errors),
            'grades': {g: len(v) for g, v in grades.items()},
            'buckets': bucket_counts,
            'feature_correlation': feature_counts,
            'group_distribution': group_counts,
        },
        'f_grade': [{
            'path': r['path'],
            'score': r['score'],
            'group': r['group'],
            'features': r['features'],
            'categories': r.get('categories', []),
            'voices': r['voices'],
            'value_overlaps': r['value_overlaps'],
        } for r in f_results],
        'errors': [{
            'path': e['path'],
            'status': e['status'],
            'error': e.get('error', ''),
        } for e in errors],
    }

    with open(OUTPUT_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    print(f'Full results saved to {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
