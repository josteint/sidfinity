"""
regression_test.py — Regression test for the SIDfinity pipeline.

The baseline is stored in grades.db (protected=1 songs). It is a FROZEN
set of known-good songs. The test checks if those songs still pass.
The baseline NEVER changes during a test run.

Updating the baseline is a separate, deliberate action:
  --add-new     Verify and add newly Grade A/S songs to baseline
  --remove-flaky  Identify and quarantine songs that fluctuate between runs

Usage:
    python3 src/player/regression_test.py              # run tests against baseline
    python3 src/player/regression_test.py --add-new    # grow baseline with verified songs
"""

import sys
import os
import multiprocessing

_src_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
_repo_dir = os.path.abspath(os.path.join(_src_dir, '..'))
if _src_dir not in sys.path:
    sys.path.insert(0, _src_dir)
os.chdir(_repo_dir)

from sid_compare import compare_sids_tolerant


def run_pipeline(sid_path):
    """Run the full pipeline: SID → USF → SID → compare."""
    try:
        from converters.usf_to_sid import usf_to_sid
        tmp = f'/tmp/sf_regression_{os.getpid()}.sid'

        song = None
        try:
            from gt2_to_usf import gt2_to_usf
            song = gt2_to_usf(sid_path)
        except:
            pass
        if song is None:
            try:
                from converters.rh_to_usf import rh_to_usf
                song = rh_to_usf(sid_path)
            except:
                pass
        if song is None:
            try:
                from converters.regtrace_to_usf import regtrace_to_usf
                song = regtrace_to_usf(sid_path, duration=10)
            except:
                pass
        if song is None:
            return None

        sid_bytes, _ = usf_to_sid(song, tmp)
        if not sid_bytes:
            return None
        comp = compare_sids_tolerant(sid_path, tmp, 10)
        if not comp:
            return None
        return comp['grade'], comp['score'], comp
    except Exception:
        return None


def _test_one(args):
    """Test one protected song."""
    path, min_grade, min_score = args[0], args[1], args[2]
    engine = args[3] if len(args) > 3 else 'gt2'
    import sys, os
    _sd = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
    if _sd not in sys.path:
        sys.path.insert(0, _sd)
    os.chdir(os.path.join(_sd, '..'))

    name = os.path.basename(path)
    if not os.path.exists(path):
        return (path, name, None, None, None, min_grade, 'not found', engine)

    result = run_pipeline(path)
    if result is None:
        return (path, name, False, None, None, min_grade, 'pipeline error', engine)

    grade, score, comp = result
    grade_order = {'S': 0, 'A': 1, 'B': 2, 'C': 3, 'F': 4}
    grade_ok = grade_order.get(grade, 9) <= grade_order.get(min_grade, 9)
    score_ok = score >= (min_score or 96.0) - 0.5

    if grade_ok and score_ok:
        return (path, name, True, grade, score, min_grade, None, engine)
    else:
        details = f'Grade {grade} ({score:.1f}) — expected >= {min_grade} ({min_score:.1f})'
        return (path, name, False, grade, score, min_grade, details, engine)


def _detect_scope():
    """Detect which engines need testing based on uncommitted changes.

    Checks git diff (staged + unstaged) to determine which files changed.
    Returns a set of engine names to test, or None for ALL.
    """
    import subprocess
    try:
        r = subprocess.run(['git', 'diff', '--name-only', 'HEAD'],
                           capture_output=True, text=True, timeout=5)
        r2 = subprocess.run(['git', 'diff', '--name-only', '--cached'],
                            capture_output=True, text=True, timeout=5)
        changed = set((r.stdout + r2.stdout).strip().split('\n'))
        changed.discard('')
    except:
        return None  # can't determine, test all

    if not changed:
        return None  # no changes, test all

    # Files that affect ALL engines
    global_files = {
        'src/sid_compare.py', 'src/converters/usf_to_sid.py',
        'src/player/codegen_v2.py', 'src/player/codegen.py',
        'src/player/peephole.py', 'src/usf/format.py',
        'src/sidfinity_pack.py',
    }
    if any(f in changed for f in global_files):
        return None  # test all

    # Engine-specific files
    engine_map = {
        'gt2': {'src/gt2_to_usf.py', 'src/converters/gt2_to_usf.py',
                'src/gt2_decompile.py', 'src/gt2_parse_direct.py',
                'src/gt2_detect_version.py', 'src/gt2_packer.py'},
        'hubbard': {'src/rh_decompile.py', 'src/rh_to_usf.py',
                    'src/converters/rh_to_usf.py'},
        'dmc': {'src/dmc_parser.py', 'src/dmc_to_usf.py',
                'src/converters/dmc_to_usf.py'},
        'universal': {'src/regtrace_to_usf.py',
                      'src/converters/regtrace_to_usf.py'},
    }

    engines = set()
    for engine, files in engine_map.items():
        if any(f in changed for f in files):
            engines.add(engine)

    if 'universal' in engines:
        # Universal pipeline affects non-GT2 engines
        engines.update(['hubbard', 'dmc', 'jch'])
        engines.discard('universal')

    return engines if engines else None


def run_tests():
    """Run regression tests against the frozen baseline.

    Smart scoping: only tests engines affected by changed files.
    """
    from grade_db import connect, protected_count

    db = connect()
    total_protected, grade_s, grade_a = protected_count(db)

    scope = None if globals().get('_force_all') else _detect_scope()

    if scope is None:
        # Test everything
        rows = db.execute('''SELECT path, min_grade, COALESCE(min_score, 96.0), engine
                             FROM songs WHERE protected = 1
                             ORDER BY path''').fetchall()
        scope_desc = "all engines"
    else:
        # Filter by engine
        placeholders = ','.join('?' * len(scope))
        rows = db.execute(f'''SELECT path, min_grade, COALESCE(min_score, 96.0), engine
                              FROM songs WHERE protected = 1
                              AND engine IN ({placeholders})
                              ORDER BY path''', list(scope)).fetchall()
        scope_desc = ', '.join(sorted(scope))

    db.close()

    if not rows:
        print('No baseline songs in scope. Run with --add-new to establish baseline.')
        return True

    num_workers = os.cpu_count() or 4
    print(f'Running {len(rows)} regression tests [{scope_desc}] ({num_workers} workers)...\n')

    with multiprocessing.Pool(num_workers) as pool:
        results = pool.map(_test_one, rows)

    passed = failed = skipped = 0
    failures = []

    for path, name, ok, grade, score, min_grade, details, *_ in results:
        if ok is None:
            skipped += 1
        elif ok:
            passed += 1
        else:
            failed += 1
            failures.append((name, grade, score, min_grade, details))

    for name, grade, score, min_grade, details in failures[:20]:
        print(f'  FAIL  {name:40s} {details or "pipeline error"}')
    if len(failures) > 20:
        print(f'  ... and {len(failures) - 20} more failures')

    s = sum(1 for r in results if r[2] and r[3] == 'S')
    a = sum(1 for r in results if r[2] and r[3] == 'A')
    print(f'\n{passed} passed, {failed} failed, {skipped} skipped '
          f'out of {len(rows)} tests ({s} S + {a} A = {s + a})')

    # Update grades.db with test results (does NOT change baseline)
    try:
        from grade_db import connect, record_batch
        db = connect()
        batch = [(p, eng, g, sc) for p, _, ok, g, sc, _, _, eng in results if g and g != 'ERR']
        if batch:
            record_batch(db, batch)
        db.close()
        from update_readme import update_readme
        update_readme()
    except:
        pass

    return failed == 0


def add_new():
    """Add verified Grade A/S songs to the baseline.

    Only adds songs that:
    1. Are Grade A/S in grades.db
    2. Are NOT already in the baseline
    3. Pass the pipeline RIGHT NOW (verified, not just from DB)
    """
    from grade_db import connect

    db = connect()
    candidates = db.execute('''SELECT path FROM songs
                               WHERE grade IN ('S', 'A')
                               AND protected != 1
                               ORDER BY path''').fetchall()
    db.close()

    if not candidates:
        print('No new Grade A/S songs to add.')
        return

    print(f'Verifying {len(candidates)} candidate songs...')
    args = [(path, 'A', 96.0) for (path,) in candidates]

    with multiprocessing.Pool(os.cpu_count() or 4) as pool:
        results = pool.map(_test_one, args)

    verified = [(path, grade, score)
                for path, name, ok, grade, score, *_ in results
                if ok and grade in ('S', 'A')]

    if not verified:
        print('No songs passed verification.')
        return

    db = connect()
    for path, grade, score in verified:
        db.execute('''UPDATE songs SET protected = 1, min_grade = 'A', min_score = 96.0
                      WHERE path = ?''', (path,))
    db.commit()

    total = db.execute('SELECT COUNT(*) FROM songs WHERE protected = 1').fetchone()[0]
    db.close()

    print(f'{len(verified)} songs added to baseline. Total protected: {total}')


def main():
    import argparse
    parser = argparse.ArgumentParser(description='SIDfinity regression tests')
    parser.add_argument('--add-new', action='store_true',
                        help='Verify and add new Grade A/S songs to baseline')
    parser.add_argument('--all', action='store_true',
                        help='Test all engines (ignore git diff scoping)')
    args = parser.parse_args()

    if args.add_new:
        add_new()
        return

    global _force_all
    _force_all = args.all

    success = run_tests()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
