"""
regression_test.py — Regression test for the SIDfinity pipeline.

Maintains a list of SIDs that are known-good. Each has a minimum
grade and score that must be maintained. When fixing a new SID,
run this first to ensure nothing regressed, then add the new SID
to the list.

Usage:
    python3 src/player/regression_test.py              # run all tests
    python3 src/player/regression_test.py --add <sid>  # add a new SID after verifying it
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sid_compare import compare_sids_tolerant

REGISTRY_PATH = os.path.join(os.path.dirname(__file__), 'regression_registry.json')
TEMP_SID = '/tmp/sf_regression_test.sid'


def load_registry():
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return []


def save_registry(entries):
    with open(REGISTRY_PATH, 'w') as f:
        json.dump(entries, f, indent=2)


def run_pipeline(sid_path):
    """Run the full pipeline THROUGH TOKENS: SID → USF → Tokens → USF → SID → compare.

    This is the definitive test: if the token roundtrip produces the same quality
    as the direct USF path, the tokenization is lossless. Any score drop reveals
    information lost in tokenize→detokenize.
    """
    try:
        # SID → USF
        from gt2_to_usf import gt2_to_usf
        song = gt2_to_usf(sid_path)
        if not song:
            return None
        # USF → Tokens → USF (the critical roundtrip)
        from usf import tokenize, detokenize
        tokens = tokenize(song)
        song = detokenize(tokens)
        # USF → SID (via SIDfinity player)
        from usf_to_sid import usf_to_sid
        tmp = f'/tmp/sf_regression_{os.getpid()}.sid'
        sid_bytes, _ = usf_to_sid(song, tmp)
        if not sid_bytes:
            return None
        comp = compare_sids_tolerant(sid_path, tmp, 10)
        if not comp:
            return None
        return comp['grade'], comp['score'], comp
    except Exception as e:
        return None


def _test_one_entry(entry):
    """Test one registry entry. Returns (name, passed, grade, score, min_grade, min_score, details)."""
    path = entry['path']
    min_grade = entry['min_grade']
    min_score = entry['min_score']
    name = os.path.basename(path)

    if not os.path.exists(path):
        return (name, None, None, None, min_grade, min_score, 'not found')

    result = run_pipeline(path)
    if result is None:
        if min_grade == 'ERR':
            return (name, True, 'ERR', 0, min_grade, min_score, None)  # expected to fail
        return (name, False, None, None, min_grade, min_score, 'pipeline error')

    grade, score, comp = result
    grade_order = {'S': 0, 'A': 1, 'B': 2, 'C': 3, 'F': 4, 'ERR': 5}
    grade_ok = grade_order.get(grade, 9) <= grade_order.get(min_grade, 9)
    score_ok = score >= min_score - 0.5

    if grade_ok and score_ok:
        return (name, True, grade, score, min_grade, min_score, None)
    else:
        # Collect failure details
        details = []
        for v in range(3):
            vr = comp['voices'][v]
            issues = []
            for k in ['note_wrong', 'wave_wrong', 'env_wrong']:
                if vr.get(k, 0) > 0:
                    issues.append(f'{k}={vr[k]}')
            if issues:
                details.append(f'V{v+1}: {" ".join(issues)}')
        return (name, False, grade, score, min_grade, min_score, '; '.join(details))


def run_tests():
    """Run all regression tests in parallel. Returns True if all pass."""
    import multiprocessing
    entries = load_registry()
    if not entries:
        print('No regression tests registered. Use --add <sid_path> to add one.')
        return True

    num_workers = os.cpu_count() or 4
    print(f'Running {len(entries)} regression tests ({num_workers} workers)...\n')

    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(_test_one_entry, entries)

    passed = 0
    failed = 0
    skipped = 0
    failures = []

    for name, ok, grade, score, min_grade, min_score, details in results:
        if ok is None:
            skipped += 1
        elif ok:
            passed += 1
        else:
            failed += 1
            failures.append((name, grade, score, min_grade, min_score, details))

    # Print failures (keep output manageable)
    for name, grade, score, min_grade, min_score, details in failures[:20]:
        if grade:
            print(f'  FAIL  {name:40s} Grade {grade} ({score:.1f}) — expected >= {min_grade} ({min_score:.1f})')
        else:
            print(f'  FAIL  {name:40s} — {details}')

    if len(failures) > 20:
        print(f'  ... and {len(failures) - 20} more failures')

    grade_a_count = sum(1 for _, ok, grade, *_ in results if ok and grade == 'A')
    print(f'\n{passed} passed, {failed} failed, {skipped} skipped out of {len(entries)} tests ({grade_a_count} Grade A)')
    return failed == 0


def add_sid(sid_path):
    """Add a SID to the regression registry after verifying it works."""
    if not os.path.exists(sid_path):
        print(f'File not found: {sid_path}')
        return False

    # Resolve to absolute path
    sid_path = os.path.abspath(sid_path)
    name = os.path.basename(sid_path)

    print(f'Testing {name}...')
    result = run_pipeline(sid_path)

    if result is None:
        print(f'Pipeline failed for {name}')
        return False

    grade, score, comp = result

    print(f'  Grade {grade}, Score {score:.1f}')
    for v in range(3):
        vr = comp['voices'][v]
        ok_pct = 100 * vr['ok'] / comp['total']
        print(f'  V{v+1}: {ok_pct:.1f}% ok')

    if grade not in ('A', 'B'):
        print(f'\n  WARNING: Grade {grade} — only Grade A/B should be added to regression tests.')
        resp = input('  Add anyway? [y/N] ')
        if resp.lower() != 'y':
            return False

    entries = load_registry()

    # Check if already registered
    for e in entries:
        if os.path.basename(e['path']) == name:
            print(f'  Already registered. Updating...')
            e['min_grade'] = grade
            e['min_score'] = round(score, 1)
            save_registry(entries)
            print(f'  Updated: Grade >= {grade}, Score >= {score:.1f}')
            return True

    entries.append({
        'path': sid_path,
        'min_grade': grade,
        'min_score': round(score, 1),
    })
    save_registry(entries)
    print(f'  Added: Grade >= {grade}, Score >= {score:.1f}')
    return True


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--add':
        if len(sys.argv) < 3:
            print('Usage: regression_test.py --add <sid_path>')
            sys.exit(1)
        ok = add_sid(sys.argv[2])
        sys.exit(0 if ok else 1)
    else:
        ok = run_tests()
        sys.exit(0 if ok else 1)
