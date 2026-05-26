"""
hvsc_dashboard.py — HVSC coverage dashboard.

Shows pipeline progress and quality grades for each player engine.
Reads from the SQLite grade database (data/grades.db).

Grading system:
  S     Perfect — zero differences of any kind (no jitter)
  A     Excellent — no audible errors (jitter tolerated, env < 1%)
  B     Good — < 2% audible errors
  C     Fair — < 10% audible errors
  F     Fail — >= 10% audible errors
  USF   Converted to USF but no rebuilt SID yet
  PARSE Parsed but no USF conversion
  ID    Identified but not parsed

Usage:
  python3 src/hvsc_dashboard.py              # from database (instant)
  python3 src/hvsc_dashboard.py --refresh    # re-scan and update database
  python3 src/hvsc_dashboard.py --refresh dmc # re-scan one engine only
"""

import sys
import os
import json
import glob
import concurrent.futures
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HVSC_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'C64Music')
SIDID_FULL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'sidid_full.txt')
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'dashboard_cache.json')

# Map sidid player names to our engine names
PLAYER_MAP = {
    'GoatTracker_V2.x': 'gt2',
    'DMC': 'dmc',
    'DMC_V6.x': 'dmc',
    'Rob_Hubbard': 'hubbard',
    'JCH_NewPlayer': 'jch',
}

GRADE_ORDER = ['S', 'A', 'B', 'C', 'F', 'USF', 'PARSE', 'ID']


def load_sidid_full():
    """Load the full sidid scan results."""
    if not os.path.exists(SIDID_FULL):
        return {}
    players = {}
    with open(SIDID_FULL) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('Using'):
                continue
            parts = line.rsplit(None, 1)
            if len(parts) == 2:
                path, player = parts
                players[path.strip()] = player.strip()
    return players


def get_engine_files(sidid_data):
    """Group files by engine."""
    engines = {}
    for path, player in sidid_data.items():
        engine = PLAYER_MAP.get(player)
        if engine:
            engines.setdefault(engine, []).append(
                os.path.join(HVSC_ROOT, path))
    return engines


def _check_one(args):
    """Check a single SID through the full pipeline. Returns (path, engine, grade, score)."""
    f, engine = args
    import sys, os
    _sd = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__))))
    if _sd not in sys.path:
        sys.path.insert(0, _sd)

    # Try engine-specific static parser first
    song = None
    try:
        if engine == 'gt2':
            from gt2_to_usf import gt2_to_usf
            song = gt2_to_usf(f)
        elif engine == 'dmc':
            from converters.dmc_to_usf import dmc_to_usf
            song = dmc_to_usf(f)
        elif engine == 'hubbard':
            from converters.rh_to_usf import rh_to_usf
            song = rh_to_usf(f)
    except:
        pass

    # Fallback: universal register trace pipeline
    if song is None:
        try:
            from converters.regtrace_to_usf import regtrace_to_usf
            song = regtrace_to_usf(f, duration=10)
        except:
            pass

    if song is None:
        # Check if we can at least parse the binary
        try:
            if engine == 'dmc':
                from dmc_parser import parse_dmc_sid
                if parse_dmc_sid(f):
                    return (f, engine, 'PARSE', None)
        except:
            pass
        return (f, engine, 'ID', None)

    # Try to build and compare
    try:
        from converters.usf_to_sid import usf_to_sid
        from sid_compare import compare_sids_tolerant
        tmp = f'/tmp/dashboard_{os.getpid()}.sid'
        usf_to_sid(song, tmp)
        comp = compare_sids_tolerant(f, tmp, 10)
        if comp:
            return (f, engine, comp['grade'], comp['score'])
        return (f, engine, 'USF', None)
    except:
        return (f, engine, 'USF', None)


def scan_engine(files, engine, jobs=64):
    """Scan files for any engine through the universal pipeline."""
    args = [(f, engine) for f in files]
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as ex:
        results = list(ex.map(_check_one, args, chunksize=10))
    return results


ENGINE_SCANNERS = {
    'dmc': 'dmc',
    'gt2': 'gt2',
    'hubbard': 'hubbard',
    'jch': 'jch',
}

ENGINE_NAMES = {
    'gt2': 'GoatTracker V2',
    'dmc': 'DMC',
    'hubbard': 'Rob Hubbard',
    'jch': 'JCH NewPlayer',
}


def format_dashboard(engine_grades, total_sids):
    """Format the dashboard as text."""
    lines = []
    lines.append(f'HVSC Coverage Dashboard — {total_sids:,} SIDs')
    lines.append('═' * 78)
    lines.append('')

    quality_grades = ['S', 'A', 'B', 'C', 'F']
    pipeline_stages = ['USF', 'PARSE', 'ID']

    # Header
    lines.append(f'{"Engine":<18} {"SIDs":>6}   '
                 f'{"S":>5} {"A":>5} {"B":>5} {"C":>5} {"F":>5}'
                 f'  │ {"USF":>5} {"PARSE":>5} {"ID":>5}')
    lines.append('─' * 78)

    processed = 0
    for engine in ['gt2', 'dmc', 'hubbard', 'jch']:
        if engine not in engine_grades:
            continue
        grades = engine_grades[engine]
        total = sum(grades.values())
        processed += total
        name = ENGINE_NAMES.get(engine, engine)

        # Format grade counts
        qvals = []
        for g in quality_grades:
            n = grades.get(g, 0)
            qvals.append(f'{n:>5}' if n > 0 else '    —')

        pvals = []
        for g in pipeline_stages:
            n = grades.get(g, 0)
            pvals.append(f'{n:>5}' if n > 0 else '    —')

        lines.append(f'{name:<18} {total:>6}   '
                     f'{qvals[0]} {qvals[1]} {qvals[2]} {qvals[3]} {qvals[4]}'
                     f'  │ {pvals[0]} {pvals[1]} {pvals[2]}')

    lines.append('─' * 78)
    unprocessed = total_sids - processed
    lines.append(f'{"Unprocessed":<18} {unprocessed:>6}   ({100*unprocessed/total_sids:.1f}%)')
    lines.append('')

    return '\n'.join(lines)


def refresh_engine(engine, engine_files, db, jobs=64):
    """Re-scan an engine and update the database."""
    from grade_db import record_batch
    files = engine_files.get(engine, [])
    if not files:
        return

    print(f'Scanning {ENGINE_NAMES.get(engine, engine)} ({len(files)} files)...',
          file=sys.stderr)

    results = scan_engine(files, engine, jobs=jobs)

    # Convert to record_batch format
    entries = [(path, eng, grade, score) for path, eng, grade, score in results]

    updated, regs, imps = record_batch(db, entries)

    # Summary
    grades = Counter(grade for _, _, grade, _ in results)
    quality = sum(grades.get(g, 0) for g in ['S', 'A', 'B', 'C', 'F'])
    print(f'  {quality} graded (S={grades.get("S",0)} A={grades.get("A",0)} '
          f'B={grades.get("B",0)} C={grades.get("C",0)} F={grades.get("F",0)}), '
          f'{grades.get("USF",0)} USF, {grades.get("PARSE",0)} PARSE, '
          f'{grades.get("ID",0)} ID', file=sys.stderr)
    if regs:
        print(f'  Regressions: {len(regs)}', file=sys.stderr)
        for path, old, new in regs[:5]:
            print(f'    {os.path.basename(path)}: {old} → {new}', file=sys.stderr)
    if imps:
        print(f'  Improvements: {len(imps)}', file=sys.stderr)


def main():
    import argparse
    from grade_db import connect, engine_summary

    parser = argparse.ArgumentParser(description='HVSC Coverage Dashboard')
    parser.add_argument('--refresh', nargs='?', const='all', default=None,
                        help='Re-scan and update database (optionally specify engine)')
    parser.add_argument('--jobs', type=int, default=64,
                        help='Parallel workers')
    args = parser.parse_args()

    # Load sidid data for total count and engine file lists
    sidid_data = load_sidid_full()
    total_sids = len(sidid_data)

    db = connect()

    if args.refresh:
        engine_files = get_engine_files(sidid_data)
        if args.refresh == 'all':
            for engine in ENGINE_SCANNERS:
                refresh_engine(engine, engine_files, db, args.jobs)
        else:
            refresh_engine(args.refresh, engine_files, db, args.jobs)

    # Build dashboard from database
    engine_grades = engine_summary(db)

    # Add engines that are in sidid but not in DB (as ID)
    all_engine_files = get_engine_files(sidid_data)
    for engine, files in all_engine_files.items():
        if engine not in engine_grades:
            engine_grades[engine] = {'ID': len(files)}

    db.close()

    print(format_dashboard(engine_grades, total_sids))


if __name__ == '__main__':
    main()
