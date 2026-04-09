"""
validate_hvsc.py - Batch validation of sid → symbolic → sid roundtrip.

Runs the full pipeline on every single-SID PSID in HVSC:
  1. Look up duration from Songlengths
  2. Run siddump to get register CSV
  3. Parse CSV → decode_frame() → encode_frame() → compare (with bit masking)
  4. Record result in SQLite

Parallelized across all available CPU cores.
"""

import argparse
import csv
import hashlib
import json
import multiprocessing
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sid_symbolic import decode_frame, encode_frame, PAL_CLOCK, NTSC_CLOCK
from songlengths import load_database, compute_md5

# Status values
PASS = 'pass'
FAIL = 'fail'
CRASH = 'crash'
TIMEOUT = 'timeout'
SILENT = 'silent'
SKIP = 'skip'

# Bit masks for register comparison
# PW_HI registers (3, 10, 17) only use lower 4 bits
# Filter cutoff lo (21) only uses lower 3 bits
REG_MASK = [0xFF] * 25
for _pw in (3, 10, 17):
    REG_MASK[_pw] = 0x0F
REG_MASK[21] = 0x07


def find_siddump():
    """Find the siddump binary."""
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tools', 'siddump'),
        'tools/siddump',
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return os.path.abspath(c)
    raise FileNotFoundError("siddump binary not found")


def find_all_sids(hvsc_root):
    """Find all .sid files in HVSC, excluding DOCUMENTS."""
    sids = []
    for root, dirs, files in os.walk(hvsc_root):
        # Skip DOCUMENTS directory
        dirs[:] = [d for d in dirs if d != 'DOCUMENTS']
        for f in files:
            if f.lower().endswith('.sid'):
                sids.append(os.path.join(root, f))
    return sorted(sids)


def validate_one(args):
    """Validate a single SID file. Returns (path, status, error_count, frames, elapsed, detail)."""
    sid_path, duration, siddump_bin, max_duration = args
    t0 = time.monotonic()

    # Cap duration
    dur = min(duration, max_duration) if max_duration else duration

    try:
        result = subprocess.run(
            [siddump_bin, sid_path, '--duration', str(int(dur + 1)), '--timeout', '120'],
            capture_output=True, text=True, timeout=130
        )
    except subprocess.TimeoutExpired:
        return (sid_path, TIMEOUT, 0, 0, time.monotonic() - t0, 'subprocess timeout')
    except Exception as e:
        return (sid_path, CRASH, 0, 0, time.monotonic() - t0, str(e))

    if result.returncode == 2:
        return (sid_path, SILENT, 0, 0, time.monotonic() - t0, 'silent tune')
    if result.returncode == 3:
        return (sid_path, SKIP, 0, 0, time.monotonic() - t0, 'RSID or multi-SID')
    if result.returncode == 4:
        return (sid_path, TIMEOUT, 0, 0, time.monotonic() - t0, 'siddump timeout')
    if result.returncode != 0:
        return (sid_path, CRASH, 0, 0, time.monotonic() - t0,
                f'exit {result.returncode}: {result.stderr.strip()[:200]}')

    stdout = result.stdout
    if not stdout.strip():
        return (sid_path, CRASH, 0, 0, time.monotonic() - t0, 'empty output')

    try:
        lines = stdout.strip().split('\n')
        if len(lines) < 3:
            return (sid_path, CRASH, 0, 0, time.monotonic() - t0, f'only {len(lines)} lines')

        # Parse metadata
        metadata = json.loads(lines[0])
        clock = PAL_CLOCK if metadata.get('clock') == 'PAL' else NTSC_CLOCK

        # Skip header line (lines[1])
        # Parse register lines
        error_count = 0
        frame_count = 0

        for line in lines[2:]:
            line = line.strip()
            if not line:
                continue

            # Strip digi suffix if present
            if '|' in line:
                line = line.split('|')[0].rstrip(',').strip()

            hex_vals = line.split(',')
            if len(hex_vals) != 25:
                error_count += 1
                frame_count += 1
                continue

            regs = [int(h, 16) for h in hex_vals]
            frame = decode_frame(regs, clock)
            recon = encode_frame(frame, clock)

            for r in range(25):
                if (regs[r] & REG_MASK[r]) != (recon[r] & REG_MASK[r]):
                    error_count += 1
                    break

            frame_count += 1

    except json.JSONDecodeError as e:
        return (sid_path, CRASH, 0, 0, time.monotonic() - t0, f'JSON parse error: {e}')
    except Exception as e:
        return (sid_path, CRASH, 0, 0, time.monotonic() - t0, f'roundtrip error: {e}')

    elapsed = time.monotonic() - t0
    if error_count > 0:
        return (sid_path, FAIL, error_count, frame_count, elapsed,
                f'{error_count}/{frame_count} frames with errors')
    return (sid_path, PASS, 0, frame_count, elapsed, '')


def init_db(db_path):
    """Create SQLite database for results."""
    conn = sqlite3.connect(db_path)
    conn.execute('''CREATE TABLE IF NOT EXISTS results (
        path TEXT PRIMARY KEY,
        status TEXT,
        error_count INTEGER,
        frames INTEGER,
        elapsed_s REAL,
        detail TEXT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    return conn


def get_processed(conn):
    """Get set of already-processed file paths."""
    cursor = conn.execute('SELECT path FROM results')
    return {row[0] for row in cursor.fetchall()}


def main():
    parser = argparse.ArgumentParser(description='Validate HVSC symbolic roundtrip')
    parser.add_argument('hvsc_root', help='Path to C64Music directory')
    parser.add_argument('--songlengths', help='Path to Songlengths.md5')
    parser.add_argument('--db', default='validation.db', help='SQLite database path')
    parser.add_argument('--jobs', '-j', type=int, default=multiprocessing.cpu_count(),
                        help='Number of parallel workers')
    parser.add_argument('--resume', action='store_true', help='Skip already-processed files')
    parser.add_argument('--filter', help='Only process paths matching this pattern')
    parser.add_argument('--max-duration', type=float, default=300,
                        help='Max duration in seconds per file (default: 300)')
    parser.add_argument('--default-duration', type=float, default=60,
                        help='Duration when not in songlengths (default: 60)')
    args = parser.parse_args()

    hvsc_root = os.path.abspath(args.hvsc_root)
    siddump_bin = find_siddump()
    print(f"Using siddump: {siddump_bin}")

    # Load songlengths
    sl_path = args.songlengths
    if not sl_path:
        sl_path = os.path.join(hvsc_root, 'DOCUMENTS', 'Songlengths.md5')
    print(f"Loading songlengths from {sl_path}...")
    sl_db = load_database(sl_path)
    print(f"  Loaded {len(sl_db)} entries")

    # Find all SID files
    print(f"Scanning {hvsc_root} for .sid files...")
    all_sids = find_all_sids(hvsc_root)
    print(f"  Found {len(all_sids)} .sid files")

    # Set up database
    db_path = os.path.abspath(args.db)
    conn = init_db(db_path)

    # Filter already-processed if resuming
    if args.resume:
        processed = get_processed(conn)
        all_sids = [s for s in all_sids if s not in processed]
        print(f"  After resume filter: {len(all_sids)} remaining")

    # Apply path filter
    if args.filter:
        pattern = re.compile(args.filter)
        all_sids = [s for s in all_sids if pattern.search(s)]
        print(f"  After path filter: {len(all_sids)} remaining")

    if not all_sids:
        print("No files to process.")
        conn.close()
        return

    # Build work items: (sid_path, duration, siddump_bin, max_duration)
    work_items = []
    no_duration_count = 0
    for sid_path in all_sids:
        try:
            md5 = compute_md5(sid_path)
            if md5 in sl_db:
                duration = sl_db[md5][0]  # First subtune duration
            else:
                duration = args.default_duration
                no_duration_count += 1
        except Exception:
            duration = args.default_duration
            no_duration_count += 1
        work_items.append((sid_path, duration, siddump_bin, args.max_duration))

    if no_duration_count > 0:
        print(f"  {no_duration_count} files not in songlengths (using {args.default_duration}s default)")

    print(f"\nProcessing {len(work_items)} files with {args.jobs} workers...")
    print()

    # Process in parallel
    counts = {PASS: 0, FAIL: 0, CRASH: 0, TIMEOUT: 0, SILENT: 0, SKIP: 0}
    total = len(work_items)
    done = 0
    t_start = time.monotonic()

    with multiprocessing.Pool(args.jobs) as pool:
        for result in pool.imap_unordered(validate_one, work_items, chunksize=8):
            path, status, error_count, frames, elapsed, detail = result
            counts[status] = counts.get(status, 0) + 1
            done += 1

            # Store result
            conn.execute(
                'INSERT OR REPLACE INTO results (path, status, error_count, frames, elapsed_s, detail) '
                'VALUES (?, ?, ?, ?, ?, ?)',
                (path, status, error_count, frames, elapsed, detail)
            )

            # Progress update every 500 files
            if done % 500 == 0 or done == total:
                conn.commit()
                elapsed_total = time.monotonic() - t_start
                rate = done / elapsed_total if elapsed_total > 0 else 0
                eta = (total - done) / rate if rate > 0 else 0
                print(f"  [{done}/{total}] "
                      f"pass={counts[PASS]} fail={counts[FAIL]} crash={counts[CRASH]} "
                      f"silent={counts[SILENT]} skip={counts[SKIP]} timeout={counts[TIMEOUT]} "
                      f"({rate:.0f}/s, ETA {eta:.0f}s)")

    conn.commit()
    conn.close()

    # Summary
    elapsed_total = time.monotonic() - t_start
    print(f"\n{'='*60}")
    print(f"Completed {total} files in {elapsed_total:.1f}s")
    print(f"  Pass:    {counts[PASS]:6d} ({100*counts[PASS]/total:.1f}%)")
    print(f"  Fail:    {counts[FAIL]:6d} ({100*counts[FAIL]/total:.1f}%)")
    print(f"  Crash:   {counts[CRASH]:6d} ({100*counts[CRASH]/total:.1f}%)")
    print(f"  Silent:  {counts[SILENT]:6d} ({100*counts[SILENT]/total:.1f}%)")
    print(f"  Skip:    {counts[SKIP]:6d} ({100*counts[SKIP]/total:.1f}%)")
    print(f"  Timeout: {counts[TIMEOUT]:6d} ({100*counts[TIMEOUT]/total:.1f}%)")

    relevant = counts[PASS] + counts[FAIL]
    if relevant > 0:
        print(f"\n  Pass rate (excl. skip/silent/crash/timeout): "
              f"{counts[PASS]}/{relevant} = {100*counts[PASS]/relevant:.2f}%")


if __name__ == '__main__':
    main()
