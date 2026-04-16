"""
hvsc_dashboard.py — HVSC coverage dashboard.

Shows pipeline progress and quality grades for each player engine.

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
  python3 src/hvsc_dashboard.py                    # quick mode (cached data)
  python3 src/hvsc_dashboard.py --live             # live scan (slow, recomputes everything)
  python3 src/hvsc_dashboard.py --live --engine dmc # live scan for one engine only
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


def _check_dmc(f):
    """Check single DMC file pipeline status."""
    try:
        from dmc_parser import parse_dmc_sid
        from dmc_to_usf import dmc_to_usf
        dmc = parse_dmc_sid(f)
        if dmc is None:
            return 'ID'
        if dmc['num_sectors'] == 0 or dmc['total_notes'] == 0:
            return 'PARSE'
        song = dmc_to_usf(f)
        return 'USF'
    except:
        return 'ID'


def scan_dmc(files, jobs=64):
    """Scan DMC files and return grade distribution."""
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as ex:
        results = list(ex.map(_check_dmc, files, chunksize=50))
    return Counter(results)


def scan_gt2(files, jobs=64):
    """Scan GT2 files and return grade distribution.

    Uses regression registry for cached grades, falls back to pipeline.
    """
    registry_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'player', 'regression_registry.json')
    # Load registry for cached grades
    registry = {}
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            for entry in json.load(f):
                p = entry.get('path', '')
                registry[p] = entry.get('min_grade', 'F')

    grades = Counter()
    for f in files:
        # Check registry first
        matched = False
        for rpath, grade in registry.items():
            if f.endswith(rpath) or rpath in f:
                grades[grade] += 1
                matched = True
                break
        if not matched:
            # Try parsing
            try:
                from gt2_to_usf import gt2_to_usf
                song = gt2_to_usf(f)
                if song:
                    grades['USF'] += 1
                else:
                    grades['PARSE'] += 1
            except:
                grades['ID'] += 1

    return grades


def scan_hubbard(files, jobs=64):
    """Scan Hubbard files — mostly at ID stage, a few through pipeline."""
    # For now, just count. We know ~84 files, 3 Grade A, 3 Grade C from CLAUDE.md
    grades = Counter()
    try:
        from rh_decompile import decompile_hubbard
        for f in files:
            try:
                result = decompile_hubbard(f)
                if result:
                    grades['PARSE'] += 1
                else:
                    grades['ID'] += 1
            except:
                grades['ID'] += 1
    except ImportError:
        grades['ID'] = len(files)
    return grades


def scan_jch(files, jobs=64):
    """Scan JCH files — currently all at ID stage."""
    return Counter({'ID': len(files)})


ENGINE_SCANNERS = {
    'dmc': scan_dmc,
    'gt2': scan_gt2,
    'hubbard': scan_hubbard,
    'jch': scan_jch,
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


def main():
    import argparse
    parser = argparse.ArgumentParser(description='HVSC Coverage Dashboard')
    parser.add_argument('--live', action='store_true',
                        help='Live scan (slow, recomputes everything)')
    parser.add_argument('--engine', type=str,
                        help='Only scan one engine (dmc, gt2, hubbard, jch)')
    parser.add_argument('--jobs', type=int, default=64,
                        help='Parallel workers')
    args = parser.parse_args()

    # Load sidid data
    print('Loading sidid data...', file=sys.stderr)
    sidid_data = load_sidid_full()
    total_sids = len(sidid_data)
    engine_files = get_engine_files(sidid_data)

    # Load cache
    cache = {}
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            cache = json.load(f)

    # Scan engines
    engine_grades = {}
    engines_to_scan = [args.engine] if args.engine else list(ENGINE_SCANNERS.keys())

    for engine in engines_to_scan:
        if engine not in engine_files:
            continue
        files = engine_files[engine]

        if args.live:
            print(f'Scanning {ENGINE_NAMES.get(engine, engine)} ({len(files)} files)...',
                  file=sys.stderr)
            scanner = ENGINE_SCANNERS.get(engine)
            if scanner:
                grades = scanner(files, jobs=args.jobs)
                engine_grades[engine] = dict(grades)
                cache[engine] = dict(grades)
        elif engine in cache:
            engine_grades[engine] = cache[engine]
        else:
            # No cache, quick estimate
            engine_grades[engine] = {'ID': len(files)}

    # Load non-scanned engines from cache
    for engine in ENGINE_SCANNERS:
        if engine not in engine_grades and engine in cache:
            engine_grades[engine] = cache[engine]

    # Save cache
    if args.live:
        os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
        with open(CACHE_PATH, 'w') as f:
            json.dump(cache, f, indent=2)

    # Display
    print(format_dashboard(engine_grades, total_sids))


if __name__ == '__main__':
    main()
