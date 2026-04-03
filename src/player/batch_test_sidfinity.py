#!/usr/bin/env python3
"""
batch_test_sidfinity.py — Batch test SIDfinity pipeline on GT2 files.

For each file:
  1. decompile_gt2() to extract data
  2. pack_from_decompiled() to build SIDfinity SID
  3. compare_sids_tolerant() to grade

Produces a report with grade distribution, top scorers, and failure analysis.
"""

import sys
import os
import time
import traceback
import random
import glob
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, '..')
sys.path.insert(0, SRC_DIR)

from gt2_decompile import decompile_gt2
from sidfinity_pack import pack_from_decompiled
from gt2_compare import compare_sids_tolerant, score_results
from gt2_parse_direct import parse_gt2_direct


def find_gt2_files(base_dir, max_files=50, seed=42):
    """Find GT2 SID files by scanning MUSICIANS directories."""
    author_dirs = sorted(glob.glob(os.path.join(base_dir, 'MUSICIANS', '*', '*', '')))
    random.seed(seed)
    random.shuffle(author_dirs)

    gt2_files = []
    checked = 0
    for d in author_dirs:
        sids = sorted(glob.glob(os.path.join(d, '*.sid')))[:3]
        for f in sids:
            checked += 1
            try:
                r = parse_gt2_direct(f)
                if r is not None:
                    gt2_files.append(f)
            except Exception:
                pass
            if len(gt2_files) >= max_files:
                break
        if len(gt2_files) >= max_files:
            break
        if checked > 3000:
            break

    return gt2_files[:max_files]


def test_one_file(sid_path, duration=10):
    """Run full pipeline on one file. Returns result dict."""
    basename = os.path.basename(sid_path)
    rel_path = sid_path
    idx = sid_path.find('MUSICIANS/')
    if idx >= 0:
        rel_path = sid_path[idx:]

    result = {
        'path': rel_path,
        'basename': basename,
        'grade': 'fail',
        'score': 0.0,
        'error': None,
        'ni': 0,
        'num_patt': 0,
        'wave_size': 0,
        'comparison': None,
    }

    # Step 1: Decompile
    try:
        d = decompile_gt2(sid_path)
    except Exception as e:
        result['error'] = f'decompile: {e}'
        return result

    if d is None:
        result['error'] = 'decompile returned None'
        return result

    result['ni'] = d['ni']
    result['num_patt'] = d.get('num_patt', 0)
    result['wave_size'] = d.get('wave_size', 0)

    # Read title/author from original SID
    try:
        with open(sid_path, 'rb') as f:
            sid_data = f.read()
        d['title'] = sid_data[0x16:0x36].split(b'\x00')[0].decode('latin-1', errors='replace')
        d['author'] = sid_data[0x36:0x56].split(b'\x00')[0].decode('latin-1', errors='replace')
    except Exception:
        d['title'] = ''
        d['author'] = ''

    # Step 2: Pack with SIDfinity player
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as tf:
        output_path = tf.name

    try:
        pack_result = pack_from_decompiled(d, output_path)
    except Exception as e:
        result['error'] = f'pack: {e}'
        try:
            os.unlink(output_path)
        except OSError:
            pass
        return result

    # Step 3: Compare register output
    try:
        comp = compare_sids_tolerant(sid_path, output_path, duration)
    except Exception as e:
        result['error'] = f'compare: {e}'
        try:
            os.unlink(output_path)
        except OSError:
            pass
        return result
    finally:
        try:
            os.unlink(output_path)
        except OSError:
            pass

    if comp is None:
        result['error'] = 'compare returned None (siddump error)'
        return result

    result['grade'] = comp['grade']
    result['score'] = comp['score']
    result['comparison'] = comp

    return result


def analyze_voice_notes(results):
    """Identify files where V1 notes are 100% correct vs not."""
    v1_perfect = []
    v1_imperfect = []
    for r in results:
        if r['comparison'] is None:
            continue
        vr = r['comparison']['voices'][0]
        if vr['note_wrong'] == 0:
            v1_perfect.append(r)
        else:
            v1_imperfect.append(r)
    return v1_perfect, v1_imperfect


def analyze_failure_modes(results):
    """Categorize common failure patterns."""
    modes = {
        'decompile_fail': [],
        'pack_fail': [],
        'compare_fail': [],
        'note_errors': [],
        'wave_errors': [],
        'env_errors': [],
        'freq_fine_only': [],
        'pulse_only': [],
    }

    for r in results:
        if r['error']:
            if 'decompile' in r['error']:
                modes['decompile_fail'].append(r)
            elif 'pack' in r['error']:
                modes['pack_fail'].append(r)
            else:
                modes['compare_fail'].append(r)
            continue

        comp = r['comparison']
        if comp is None:
            continue

        has_note = any(comp['voices'][v]['note_wrong'] > 0 for v in range(3))
        has_wave = any(comp['voices'][v]['wave_wrong'] > 0 for v in range(3))
        has_env = any(comp['voices'][v]['env_wrong'] > 0 for v in range(3))
        has_fine = any(comp['voices'][v]['freq_fine'] > 0 for v in range(3))
        has_pulse = any(comp['voices'][v]['pulse_diff'] > 0 for v in range(3))

        if has_note:
            modes['note_errors'].append(r)
        if has_wave:
            modes['wave_errors'].append(r)
        if has_env:
            modes['env_errors'].append(r)
        if not has_note and not has_wave and not has_env:
            if has_fine and not has_pulse:
                modes['freq_fine_only'].append(r)
            elif has_pulse and not has_fine:
                modes['pulse_only'].append(r)

    return modes


def format_report(results, elapsed):
    """Generate the full text report."""
    lines = []
    lines.append('=' * 72)
    lines.append('SIDfinity Batch Test Report')
    lines.append(f'Date: {time.strftime("%Y-%m-%d %H:%M:%S")}')
    lines.append(f'Files tested: {len(results)}')
    lines.append(f'Elapsed: {elapsed:.1f}s')
    lines.append('=' * 72)
    lines.append('')

    # Grade distribution
    grades = {'A': [], 'B': [], 'C': [], 'F': [], 'fail': []}
    for r in results:
        grades[r['grade']].append(r)

    lines.append('GRADE DISTRIBUTION')
    lines.append('-' * 40)
    for g in ['A', 'B', 'C', 'F', 'fail']:
        count = len(grades[g])
        pct = 100 * count / len(results) if results else 0
        label = {
            'A': 'No audible difference',
            'B': 'Minor (<2% audible)',
            'C': 'Noticeable (2-10%)',
            'F': 'Broken (>10%)',
            'fail': 'Pipeline failure',
        }[g]
        lines.append(f'  {g:4s}: {count:3d} ({pct:5.1f}%) - {label}')
    lines.append('')

    # Top 10 best
    scored = [r for r in results if r['comparison'] is not None]
    scored.sort(key=lambda r: r['score'], reverse=True)

    lines.append('TOP 10 BEST-SCORING FILES')
    lines.append('-' * 72)
    for r in scored[:10]:
        lines.append(f'  {r["grade"]} {r["score"]:5.1f}  {r["basename"]:<40s} ni={r["ni"]} patt={r["num_patt"]}')
    lines.append('')

    # Worst 10
    lines.append('BOTTOM 10 WORST-SCORING FILES')
    lines.append('-' * 72)
    for r in scored[-10:]:
        lines.append(f'  {r["grade"]} {r["score"]:5.1f}  {r["basename"]:<40s} ni={r["ni"]} patt={r["num_patt"]}')
    lines.append('')

    # Failure modes
    modes = analyze_failure_modes(results)
    lines.append('COMMON FAILURE MODES')
    lines.append('-' * 72)
    for mode, files in sorted(modes.items(), key=lambda x: -len(x[1])):
        if not files:
            continue
        lines.append(f'  {mode}: {len(files)} files')
        for r in files[:3]:
            extra = r['error'] if r['error'] else ''
            lines.append(f'    - {r["basename"]} {extra}')
        if len(files) > 3:
            lines.append(f'    ... and {len(files) - 3} more')
    lines.append('')

    # V1 note accuracy
    v1_perfect, v1_imperfect = analyze_voice_notes(results)
    lines.append('V1 NOTE ACCURACY')
    lines.append('-' * 72)
    lines.append(f'  V1 notes 100% correct: {len(v1_perfect)} files')
    for r in v1_perfect[:10]:
        lines.append(f'    {r["grade"]} {r["score"]:5.1f}  {r["basename"]}')
    if len(v1_perfect) > 10:
        lines.append(f'    ... and {len(v1_perfect) - 10} more')
    lines.append('')
    lines.append(f'  V1 notes have errors: {len(v1_imperfect)} files')
    for r in v1_imperfect[:10]:
        comp = r['comparison']
        v1 = comp['voices'][0]
        total = comp['total']
        pct = 100 * v1['note_wrong'] / total
        lines.append(f'    {r["grade"]} {r["score"]:5.1f}  {r["basename"]} (V1 note wrong: {pct:.1f}%)')
    if len(v1_imperfect) > 10:
        lines.append(f'    ... and {len(v1_imperfect) - 10} more')
    lines.append('')

    # Per-file detail
    lines.append('PER-FILE DETAILS')
    lines.append('=' * 72)
    for r in results:
        lines.append(f'{r["basename"]}')
        lines.append(f'  Path: {r["path"]}')
        lines.append(f'  Grade: {r["grade"]}  Score: {r["score"]:.1f}  ni={r["ni"]} patt={r["num_patt"]} wave={r["wave_size"]}')
        if r['error']:
            lines.append(f'  ERROR: {r["error"]}')
        elif r['comparison']:
            comp = r['comparison']
            total = comp['total']
            lines.append(f'  Frames: {total}  Perfect: {comp["perfect"]}/{total} ({100*comp["perfect"]/total:.1f}%)')
            for v in range(3):
                vr = comp['voices'][v]
                parts = []
                if vr['note_wrong']:
                    parts.append(f'note:{100*vr["note_wrong"]/total:.1f}%')
                if vr['wave_wrong']:
                    parts.append(f'wave:{100*vr["wave_wrong"]/total:.1f}%')
                if vr['env_wrong']:
                    parts.append(f'env:{100*vr["env_wrong"]/total:.1f}%')
                if vr['freq_fine']:
                    parts.append(f'fine:{100*vr["freq_fine"]/total:.1f}%')
                if vr['pulse_diff']:
                    parts.append(f'pulse:{100*vr["pulse_diff"]/total:.1f}%')
                if parts:
                    lines.append(f'  V{v+1}: ok={100*vr["ok"]/total:.1f}% {" ".join(parts)}')
                else:
                    lines.append(f'  V{v+1}: 100% ok')
            if comp['filter_diff']:
                lines.append(f'  Filter: {comp["filter_diff"]} frames differ')
        lines.append('')

    return '\n'.join(lines)


def main():
    repo_root = os.environ.get('SIDFINITY_ROOT', os.path.join(SRC_DIR, '..'))
    c64music = os.path.join(repo_root, 'data', 'C64Music')

    if not os.path.isdir(c64music):
        print(f'ERROR: {c64music} not found')
        sys.exit(1)

    max_files = 50
    duration = 10

    # Parse args
    for i, a in enumerate(sys.argv[1:], 1):
        if a == '--max' and i < len(sys.argv) - 1:
            max_files = int(sys.argv[i + 1])
        if a == '--duration' and i < len(sys.argv) - 1:
            duration = int(sys.argv[i + 1])

    print(f'Finding GT2 files in {c64music}...')
    gt2_files = find_gt2_files(c64music, max_files=max_files)
    print(f'Found {len(gt2_files)} GT2 files')

    results = []
    t0 = time.time()

    for i, f in enumerate(gt2_files):
        basename = os.path.basename(f)
        print(f'[{i+1}/{len(gt2_files)}] {basename}...', end=' ', flush=True)

        r = test_one_file(f, duration)
        results.append(r)

        if r['error']:
            print(f'FAIL: {r["error"][:60]}')
        else:
            print(f'{r["grade"]} ({r["score"]:.1f})')

    elapsed = time.time() - t0

    # Print summary
    grades = {}
    for r in results:
        grades[r['grade']] = grades.get(r['grade'], 0) + 1
    print(f'\n=== Summary ({len(results)} files, {elapsed:.1f}s) ===')
    for g in ['A', 'B', 'C', 'F', 'fail']:
        count = grades.get(g, 0)
        pct = 100 * count / len(results) if results else 0
        print(f'  {g}: {count} ({pct:.1f}%)')

    # Write report
    report = format_report(results, elapsed)
    report_dir = os.path.join(repo_root, 'tmp')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, 'sidfinity_batch_report.txt')
    with open(report_path, 'w') as f:
        f.write(report)
    print(f'\nReport saved to {report_path}')


if __name__ == '__main__':
    main()
