#!/usr/bin/env python3
"""
gt2_batch_test.py — Batch test gt2_decompile on GT2 SID files from HVSC.

Scans MUSICIANS/ for .sid files, attempts gt2_parse_direct on each to identify
GT2 files, then runs decompile_gt2 on up to 500 GT2 files and reports results.

Usage:
    source src/env.sh
    python3 src/gt2_batch_test.py [--limit N] [--report PATH]
"""

import sys
import os
import argparse
import time
import traceback
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gt2_parse_direct import parse_gt2_direct
from gt2_decompile import decompile_gt2
from gt_parser import parse_psid_header, find_freq_table


def collect_sid_files(root):
    """Collect all .sid files under root."""
    sids = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if fn.lower().endswith('.sid'):
                sids.append(os.path.join(dirpath, fn))
    sids.sort()
    return sids


def identify_gt2_files(sid_files, limit=500):
    """Identify GT2 files by trying parse_gt2_direct on each.

    Returns list of (path, parse_result) for GT2 files, up to limit.
    Also returns count of files scanned.
    """
    gt2_files = []
    scanned = 0
    for path in sid_files:
        if len(gt2_files) >= limit:
            break
        scanned += 1
        try:
            r = parse_gt2_direct(path)
            if r is not None:
                gt2_files.append((path, r))
        except Exception:
            pass
    return gt2_files, scanned


def test_decompile(sid_path, parse_result):
    """Run decompile_gt2 and categorize the result.

    Returns a dict with:
        status: 'success', 'parse_failure', 'wave_size_zero',
                'assembly_failure', 'table_anomaly', 'exception'
        details: dict of extracted metrics or error info
    """
    result = {
        'status': 'unknown',
        'ni': parse_result['ni'],
        'num_columns': parse_result['num_columns'],
        'wave_size_direct': parse_result.get('wave_size', 0),
        'has_pulse': parse_result.get('pulse_size', 0) > 0,
        'has_filter': parse_result.get('filter_size', 0) > 0,
        'has_speed': parse_result.get('speed_size', 0) > 0,
    }

    try:
        d = decompile_gt2(sid_path)
    except Exception as e:
        result['status'] = 'exception'
        result['error'] = f"{type(e).__name__}: {e}"
        return result

    if d is None:
        result['status'] = 'parse_failure'
        return result

    wave_size = d.get('wave_size', 0)
    result['wave_size'] = wave_size
    result['num_cols_decompile'] = d.get('num_cols', 0)
    result['num_patt'] = d.get('num_patt', 0)
    result['table_region_size'] = d.get('table_region_size', 0)

    if wave_size <= 0:
        result['status'] = 'wave_size_zero'
        return result

    # Check table region anomalies
    table_region_size = d.get('table_region_size', 0)
    if table_region_size < 0:
        result['status'] = 'table_anomaly'
        result['anomaly'] = f'negative table region: {table_region_size}'
        return result
    if table_region_size % 2 != 0 and table_region_size > 0:
        # Odd table region size is suspicious but not fatal
        result['table_odd'] = True
    else:
        result['table_odd'] = False

    # Check if wave_size * 2 exceeds table region
    if wave_size * 2 > table_region_size:
        result['status'] = 'table_anomaly'
        result['anomaly'] = f'wave_size*2={wave_size*2} > table_region={table_region_size}'
        return result

    # Check for negative pattern count or other oddities
    if d.get('num_patt', 0) <= 0:
        result['status'] = 'table_anomaly'
        result['anomaly'] = f'num_patt={d.get("num_patt", 0)}'
        return result

    result['status'] = 'success'
    result['pulse_left_len'] = len(d.get('pulse_left', b''))
    result['filter_left_len'] = len(d.get('filter_left', b''))
    result['speed_left_len'] = len(d.get('speed_left', b''))

    return result


def generate_report(results, scan_count, gt2_count, elapsed):
    """Generate the text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("GT2 Decompiler Batch Test Report")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"SID files scanned to find GT2: {scan_count}")
    lines.append(f"GT2 files identified: {gt2_count}")
    lines.append(f"GT2 files tested: {len(results)}")
    lines.append(f"Elapsed time: {elapsed:.1f}s")
    lines.append("")

    # 1. Overall success rate
    status_counts = Counter(r['status'] for r in results)
    total = len(results)
    success = status_counts.get('success', 0)
    lines.append("-" * 70)
    lines.append("1. OVERALL SUCCESS RATE")
    lines.append("-" * 70)
    lines.append(f"  Success: {success}/{total} ({100*success/total:.1f}%)")
    lines.append("")

    # 2. Failure breakdown
    lines.append("-" * 70)
    lines.append("2. FAILURE BREAKDOWN BY CATEGORY")
    lines.append("-" * 70)
    for status in ['success', 'parse_failure', 'wave_size_zero',
                    'assembly_failure', 'table_anomaly', 'exception']:
        count = status_counts.get(status, 0)
        pct = 100 * count / total if total > 0 else 0
        lines.append(f"  {status:25s} {count:5d}  ({pct:5.1f}%)")
    lines.append("")

    # Show anomaly details - categorize by type
    anomalies = [r for r in results if r['status'] == 'table_anomaly']
    if anomalies:
        # Categorize anomalies
        wave_overflow = [r for r in anomalies if 'wave_size*2' in r.get('anomaly', '')]
        neg_region = [r for r in anomalies if 'table_region=0' in r.get('anomaly', '')]
        bad_patt = [r for r in anomalies if 'num_patt' in r.get('anomaly', '')]
        lines.append("  Table anomaly breakdown:")
        lines.append(f"    wave_size exceeds table region:  {len(wave_overflow)}")
        lines.append(f"      (of which table_region=0):     {len(neg_region)}")
        lines.append(f"    invalid pattern count:           {len(bad_patt)}")
        lines.append("")

    # Show exception details
    exceptions = [r for r in results if r['status'] == 'exception']
    if exceptions:
        exc_types = Counter(r.get('error', 'unknown').split(':')[0] for r in exceptions)
        lines.append("  Exception types:")
        for etype, cnt in exc_types.most_common():
            lines.append(f"    {etype}: {cnt}")
        lines.append("")

    # 3. Distribution of ni values
    lines.append("-" * 70)
    lines.append("3. DISTRIBUTION OF ni VALUES (instrument count)")
    lines.append("-" * 70)
    ni_raw = Counter(r['ni'] for r in results)
    # Bucket 20+ together
    ni_counts = Counter()
    for ni, count in ni_raw.items():
        if ni >= 20:
            ni_counts[20] += count
        else:
            ni_counts[ni] = count
    for ni in sorted(ni_counts.keys()):
        label = f"{ni}" if ni < 20 else "20+"
        count = ni_counts[ni]
        bar = "#" * min(count, 60)
        lines.append(f"  ni={label:>3s}: {count:4d}  {bar}")
    lines.append("")

    # 4. Distribution of column counts
    lines.append("-" * 70)
    lines.append("4. DISTRIBUTION OF COLUMN COUNTS")
    lines.append("-" * 70)
    col_counts = Counter(r['num_columns'] for r in results)
    for nc in sorted(col_counts.keys()):
        count = col_counts[nc]
        bar = "#" * min(count, 60)
        lines.append(f"  cols={nc}: {count:4d}  {bar}")
    lines.append("")

    # 5. Distribution of wave table sizes
    lines.append("-" * 70)
    lines.append("5. DISTRIBUTION OF WAVE TABLE SIZES")
    lines.append("-" * 70)
    wave_sizes = [r.get('wave_size', 0) for r in results if r.get('wave_size', 0) > 0]
    if wave_sizes:
        # Bucket into ranges
        buckets = Counter()
        for ws in wave_sizes:
            if ws == 0:
                buckets['0'] += 1
            elif ws <= 5:
                buckets['1-5'] += 1
            elif ws <= 10:
                buckets['6-10'] += 1
            elif ws <= 20:
                buckets['11-20'] += 1
            elif ws <= 50:
                buckets['21-50'] += 1
            elif ws <= 100:
                buckets['51-100'] += 1
            elif ws <= 200:
                buckets['101-200'] += 1
            else:
                buckets['201+'] += 1
        bucket_order = ['0', '1-5', '6-10', '11-20', '21-50', '51-100', '101-200', '201+']
        for b in bucket_order:
            count = buckets.get(b, 0)
            if count > 0:
                bar = "#" * min(count, 60)
                lines.append(f"  {b:>8s}: {count:4d}  {bar}")
        lines.append(f"  min={min(wave_sizes)}, max={max(wave_sizes)}, "
                      f"median={sorted(wave_sizes)[len(wave_sizes)//2]}, "
                      f"mean={sum(wave_sizes)/len(wave_sizes):.1f}")
    else:
        lines.append("  No wave sizes detected")
    lines.append("")

    # 6. Files with pulse/filter/speed tables
    lines.append("-" * 70)
    lines.append("6. FILES WITH PULSE / FILTER / SPEED TABLES")
    lines.append("-" * 70)
    has_pulse = sum(1 for r in results if r.get('has_pulse', False))
    has_filter = sum(1 for r in results if r.get('has_filter', False))
    has_speed = sum(1 for r in results if r.get('has_speed', False))
    lines.append(f"  Has pulse table:  {has_pulse:4d}  ({100*has_pulse/total:.1f}%)")
    lines.append(f"  Has filter table: {has_filter:4d}  ({100*has_filter/total:.1f}%)")
    lines.append(f"  Has speed table:  {has_speed:4d}  ({100*has_speed/total:.1f}%)")
    lines.append("")

    # Also show from decompile results (successful only)
    successful = [r for r in results if r['status'] == 'success']
    if successful:
        dc_pulse = sum(1 for r in successful if r.get('pulse_left_len', 0) > 0)
        dc_filter = sum(1 for r in successful if r.get('filter_left_len', 0) > 0)
        dc_speed = sum(1 for r in successful if r.get('speed_left_len', 0) > 0)
        lines.append(f"  Decompile extracted (success only, n={len(successful)}):")
        lines.append(f"    pulse data present:  {dc_pulse}")
        lines.append(f"    filter data present: {dc_filter}")
        lines.append(f"    speed data present:  {dc_speed}")
        lines.append("")

        # Odd table region count
        odd_tables = sum(1 for r in successful if r.get('table_odd', False))
        if odd_tables:
            lines.append(f"  Odd table region sizes (success): {odd_tables}")
            lines.append("")

    # Sample failures
    for status_name in ['parse_failure', 'wave_size_zero', 'table_anomaly', 'exception']:
        failures = [(p, r) for p, r in zip(
            [res.get('_path', '?') for res in results], results)
            if r['status'] == status_name]
        if failures:
            lines.append(f"  Sample {status_name} files (up to 5):")
            for _, r in failures[:5]:
                path = r.get('_path', '?')
                extra = r.get('anomaly', r.get('error', ''))
                lines.append(f"    {path}")
                if extra:
                    lines.append(f"      -> {extra}")
            lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Batch test GT2 decompiler")
    parser.add_argument('--limit', type=int, default=500,
                        help="Max GT2 files to test (default: 500)")
    parser.add_argument('--report', type=str,
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                             '..', 'tmp', 'decompile_report.txt'),
                        help="Output report path")
    args = parser.parse_args()

    hvsc_root = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             '..', 'data', 'C64Music', 'MUSICIANS')
    if not os.path.isdir(hvsc_root):
        print(f"HVSC MUSICIANS directory not found at: {hvsc_root}")
        sys.exit(1)

    print(f"Collecting .sid files from {hvsc_root}...")
    sid_files = collect_sid_files(hvsc_root)
    print(f"Found {len(sid_files)} .sid files")

    print(f"Identifying GT2 files (limit={args.limit})...")
    t0 = time.time()
    gt2_files, scanned = identify_gt2_files(sid_files, limit=args.limit)
    t_identify = time.time() - t0
    print(f"Identified {len(gt2_files)} GT2 files after scanning {scanned} files ({t_identify:.1f}s)")

    print(f"Running decompiler on {len(gt2_files)} GT2 files...")
    results = []
    t0 = time.time()
    for i, (path, parse_r) in enumerate(gt2_files):
        if (i + 1) % 50 == 0:
            print(f"  [{i+1}/{len(gt2_files)}]...")
        r = test_decompile(path, parse_r)
        r['_path'] = path
        results.append(r)
    elapsed = time.time() - t0
    print(f"Decompilation complete ({elapsed:.1f}s)")

    report = generate_report(results, scanned, len(gt2_files), elapsed)

    os.makedirs(os.path.dirname(os.path.abspath(args.report)), exist_ok=True)
    with open(args.report, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {args.report}")
    print()
    print(report)


if __name__ == '__main__':
    main()
