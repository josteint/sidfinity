#!/usr/bin/env python3
"""build_sid_db.py — Walk HVSC and our pipeline outputs, populate hvsc84.db.

One row per .sid file under hvsc84/, with:
  - PSID/RSID header fields (title, author, released, addresses, n_subtunes)
  - md5 of the original file
  - engine classification (from deprecated/gt2_grading/data/sidid_full.txt)
  - total HVSC songlength (from hvsc84/DOCUMENTS/Songlengths.md5)
  - which pipelines/<...>/<engine>/ handles it (NULL = unmigrated)
  - .usf / .sidfinity.sid presence + md5 (NULL when not built)
  - last verify status (set by future verify_all integration; NULL for now)

Idempotent — re-runs upsert into the same db. Skips re-hashing files
whose mtime is unchanged since the last run.

Usage:
  python3 tools/build_sid_db.py            # full sweep
  python3 tools/build_sid_db.py --rebuild  # ignore mtime cache, re-hash all
  python3 tools/build_sid_db.py --quiet    # suppress progress

Common queries:
  sqlite3 hvsc84.db "SELECT engine, COUNT(*) FROM sids
                     GROUP BY engine ORDER BY 2 DESC LIMIT 20;"
  sqlite3 hvsc84.db "SELECT path FROM sids
                     WHERE engine='Rob_Hubbard' AND pipeline IS NULL
                     ORDER BY songlength_s DESC LIMIT 20;"
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import sqlite3
import struct
import sys
import time
from pathlib import Path
from typing import Iterator

ROOT = Path(__file__).resolve().parent.parent
HVSC = ROOT / 'hvsc84'
DB_PATH = ROOT / 'hvsc84.db'
SIDID_DUMP = ROOT / 'deprecated' / 'gt2_grading' / 'data' / 'sidid_full.txt'
SONGLENGTHS = HVSC / 'DOCUMENTS' / 'Songlengths.md5'
PIPELINES = ROOT / 'pipelines'


# ---------------------------------------------------------------------------
# PSID / RSID header parser
# ---------------------------------------------------------------------------

def _decode_psid_string(raw: bytes) -> str:
    """PSID v2 strings are 32 bytes null-terminated ISO-8859-1."""
    return raw.split(b'\x00', 1)[0].decode('latin-1', errors='replace').strip()


def parse_psid_header(data: bytes) -> dict:
    """Return a dict of header fields, or {} if the magic doesn't match."""
    if len(data) < 124:
        return {}
    magic = data[:4]
    if magic not in (b'PSID', b'RSID'):
        return {}
    version, _data_off, load_addr, init_addr, play_addr, n_subs, start_sub = \
        struct.unpack('>HHHHHHH', data[4:18])
    name = _decode_psid_string(data[22:54])
    author = _decode_psid_string(data[54:86])
    released = _decode_psid_string(data[86:118])
    return {
        'is_psid': 1 if magic == b'PSID' else 0,
        'psid_version': version,
        'load_addr': load_addr,
        'init_addr': init_addr,
        'play_addr': play_addr,
        'n_subtunes': n_subs,
        'start_subtune': start_sub,
        'title': name,
        'author': author,
        'released': released,
    }


# ---------------------------------------------------------------------------
# Engine classification (from cached sidid dump)
# ---------------------------------------------------------------------------

def load_engine_map(dump_path: Path) -> dict[str, str]:
    """Parse sidid output (one line per file) into {rel_path: engine}.

    Lines look like:
      MUSICIANS/U/Ultrasyd/Havskatt.sid              Geir_Tjelta/SIDDuzz'It
      MUSICIANS/H/Hubbard_Rob/Commando.sid           Rob_Hubbard
    """
    if not dump_path.exists():
        return {}
    out: dict[str, str] = {}
    with dump_path.open() as f:
        for line in f:
            line = line.rstrip('\n')
            if not line or line.startswith('Using') or line.startswith('---'):
                continue
            # path is whitespace-separated; engine is the trailing token(s).
            # First token = path, rest = engine label.
            parts = line.split(None, 1)
            if len(parts) != 2:
                continue
            path, engine = parts[0], parts[1].strip()
            out[path] = engine
    return out


# ---------------------------------------------------------------------------
# Songlengths.md5 parser
# ---------------------------------------------------------------------------

_SONGLENGTH_LINE = re.compile(r'^([0-9a-f]{32})=(.+)$')


def load_songlengths(path: Path) -> dict[str, float]:
    """Return {md5_hex: total_seconds} from HVSC's Songlengths.md5."""
    if not path.exists():
        return {}
    out: dict[str, float] = {}
    with path.open(encoding='latin-1') as f:
        for line in f:
            line = line.rstrip()
            m = _SONGLENGTH_LINE.match(line)
            if not m:
                continue
            md5 = m.group(1)
            durations = m.group(2).split()
            total = 0.0
            for d in durations:
                # format M:SS.mmm or M:SS
                if ':' not in d:
                    continue
                mins, secs = d.split(':', 1)
                try:
                    total += int(mins) * 60 + float(secs)
                except ValueError:
                    continue
            out[md5] = total
    return out


# ---------------------------------------------------------------------------
# Pipeline lookup
# ---------------------------------------------------------------------------

def build_pipeline_map() -> dict[str, str]:
    """Map HVSC SID path → which pipelines/<...>/ handles it.

    Reads each pipeline's config.py and resolves its sid_path. Returns
    {rel_hvsc_path: 'pipelines/<...>'}.
    """
    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / 'src'))
    sys.path.insert(0, str(ROOT / 'tools' / 'py65_lib'))

    out: dict[str, str] = {}

    # Hubbard '85 + companion: import each config.py and read .sid_path
    import importlib
    candidates = []
    for cfg_dir in (PIPELINES / 'hubbard').iterdir():
        if cfg_dir.is_dir() and (cfg_dir / 'config.py').exists():
            candidates.append((f'pipelines.hubbard.{cfg_dir.name}.config',
                               f'pipelines/hubbard/{cfg_dir.name}'))
    if (PIPELINES / 'companion' / 'config.py').exists():
        candidates.append(('pipelines.companion.config',
                           'pipelines/companion'))

    for mod_name, pipeline_label in candidates:
        try:
            mod = importlib.import_module(mod_name)
        except Exception:
            continue
        for attr in dir(mod):
            if attr.startswith('_'):
                continue
            v = getattr(mod, attr)
            if hasattr(v, 'sid_path'):
                try:
                    p = Path(v.sid_path).resolve()
                    rel = p.relative_to(HVSC.resolve())
                except (ValueError, OSError):
                    continue
                out[str(rel)] = pipeline_label

    # 5_Title_Tunes uses a slightly different config layout (no
    # EngineConfig.sid_path) — its source is hardcoded in v2/write_unified_usf.py.
    five_tt = HVSC / 'MUSICIANS' / 'H' / 'Hubbard_Rob' / '5_Title_Tunes.sid'
    if five_tt.exists():
        out[str(five_tt.relative_to(HVSC))] = (
            'pipelines/hubbard/five_title_tunes')

    return out


# ---------------------------------------------------------------------------
# DB schema
# ---------------------------------------------------------------------------

SCHEMA = """
CREATE TABLE IF NOT EXISTS sids (
    path                TEXT PRIMARY KEY,    -- relative to hvsc84/
    md5                 TEXT NOT NULL,       -- original SID file md5
    size                INTEGER NOT NULL,
    mtime               REAL NOT NULL,       -- cache key for re-runs

    -- PSID/RSID header
    is_psid             INTEGER,             -- 1 = PSID, 0 = RSID
    psid_version        INTEGER,
    load_addr           INTEGER,
    init_addr           INTEGER,
    play_addr           INTEGER,
    n_subtunes          INTEGER,
    start_subtune       INTEGER,
    title               TEXT,
    author              TEXT,
    released            TEXT,

    -- classification
    engine              TEXT,                -- from sidid; NULL = unclassified
    songlength_s        REAL,                -- sum over subtunes from HVSC

    -- our migration state (NULL = not yet)
    pipeline            TEXT,                -- 'pipelines/hubbard/commando' etc.
    usf_path            TEXT,                -- e.g. 'MUSICIANS/H/Hubbard_Rob/Commando.usf'
    sidfinity_md5       TEXT,                -- md5 of our rebuilt .sidfinity.sid
    verify_status       TEXT,                -- 'ok' | 'fail' | NULL
    verify_ok_subs      INTEGER,
    verify_total_subs   INTEGER,
    last_verified_at    TEXT
);
CREATE INDEX IF NOT EXISTS idx_engine ON sids(engine);
CREATE INDEX IF NOT EXISTS idx_pipeline ON sids(pipeline);
CREATE INDEX IF NOT EXISTS idx_md5 ON sids(md5);
"""


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def md5_file(path: Path) -> str:
    h = hashlib.md5()
    with path.open('rb') as f:
        while True:
            chunk = f.read(64 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def iter_sid_paths(root: Path) -> Iterator[Path]:
    """Walk the HVSC tree, yield HVSC original .sid files.

    Skips:
      - non-music HVSC subtrees (DOCUMENTS, C64Music, update)
      - our own .sidfinity.sid outputs (we own those, they aren't sources)
    """
    for dirpath, dirnames, filenames in os.walk(root):
        rel = Path(dirpath).relative_to(root)
        if rel.parts and rel.parts[0] in ('DOCUMENTS', 'C64Music', 'update'):
            continue
        for f in filenames:
            if f.endswith('.sidfinity.sid'):
                continue        # our rebuild outputs, not HVSC sources
            if f.endswith('.sid'):
                yield Path(dirpath) / f


def upsert(cur: sqlite3.Cursor, row: dict) -> None:
    cols = list(row.keys())
    placeholders = ','.join('?' * len(cols))
    updates = ','.join(f'{c}=excluded.{c}' for c in cols if c != 'path')
    sql = (f'INSERT INTO sids ({",".join(cols)}) VALUES ({placeholders}) '
           f'ON CONFLICT(path) DO UPDATE SET {updates}')
    cur.execute(sql, [row[c] for c in cols])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rebuild', action='store_true',
                    help='ignore mtime cache, re-hash every file')
    ap.add_argument('--quiet', action='store_true',
                    help='suppress progress')
    args = ap.parse_args(argv)

    if not HVSC.is_dir():
        print(f'error: HVSC tree not found at {HVSC}', file=sys.stderr)
        return 1

    t0 = time.time()
    if not args.quiet:
        print(f'  loading engine classifications from {SIDID_DUMP.relative_to(ROOT)}...')
    engine_map = load_engine_map(SIDID_DUMP)
    if not args.quiet:
        print(f'    {len(engine_map):,} files classified by sidid')

    if not args.quiet:
        print(f'  loading songlengths from {SONGLENGTHS.relative_to(ROOT)}...')
    songlengths = load_songlengths(SONGLENGTHS)
    if not args.quiet:
        print(f'    {len(songlengths):,} entries in Songlengths.md5')

    if not args.quiet:
        print(f'  resolving pipeline mappings from pipelines/...')
    pipeline_map = build_pipeline_map()
    if not args.quiet:
        print(f'    {len(pipeline_map)} SIDs handled by active pipelines')

    # Connect DB
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    cur = db.cursor()

    # Read mtime cache
    cache: dict[str, tuple[float, str]] = {}
    if not args.rebuild:
        for row in cur.execute('SELECT path, mtime, md5 FROM sids'):
            cache[row[0]] = (row[1], row[2])

    n_files = n_hashed = n_skipped = 0
    t_sweep = time.time()

    for sid_path in iter_sid_paths(HVSC):
        n_files += 1
        rel = str(sid_path.relative_to(HVSC))

        try:
            st = sid_path.stat()
        except OSError:
            continue

        # Reuse cached md5 if mtime unchanged
        cached = cache.get(rel)
        if cached and cached[0] == st.st_mtime and not args.rebuild:
            file_md5 = cached[1]
            n_skipped += 1
        else:
            file_md5 = md5_file(sid_path)
            n_hashed += 1

        # Read header
        with sid_path.open('rb') as f:
            header = f.read(124)
        hdr = parse_psid_header(header)

        # Check for our artifacts alongside. Use string ops rather than
        # Path.with_suffix — the latter only replaces the *last* suffix and
        # mishandles 'Commando.sid' → '.sidfinity.sid' (would yield
        # 'Commando.sidfinity.sid' fine, but '.sid' → '' first then double-
        # extension is fragile). Strip '.sid' once and append explicitly.
        base = str(sid_path)[:-4]  # drop '.sid'
        usf_path = Path(base + '.usf')
        sidfinity_path = Path(base + '.sidfinity.sid')
        usf_rel = (str(usf_path.relative_to(HVSC))
                   if usf_path.exists() else None)
        sidfinity_md5 = (md5_file(sidfinity_path)
                         if sidfinity_path.exists() else None)

        row = {
            'path': rel,
            'md5': file_md5,
            'size': st.st_size,
            'mtime': st.st_mtime,
            'engine': engine_map.get(rel),
            'songlength_s': songlengths.get(file_md5),
            'pipeline': pipeline_map.get(rel),
            'usf_path': usf_rel,
            'sidfinity_md5': sidfinity_md5,
            # verify_* columns left at NULL; future verify_all writes them
            **hdr,
        }
        upsert(cur, row)

        if not args.quiet and n_files % 5000 == 0:
            dt = time.time() - t_sweep
            print(f'    {n_files:,} files | {n_hashed:,} hashed | '
                  f'{n_skipped:,} cached | {n_files/dt:.0f} files/s')

    db.commit()
    db.close()

    dt_total = time.time() - t0
    if not args.quiet:
        print()
        print(f'  done: {n_files:,} SID files indexed in {dt_total:.1f}s')
        print(f'    hashed: {n_hashed:,}   cached: {n_skipped:,}')
        print(f'    db: {DB_PATH.relative_to(ROOT)} '
              f'({DB_PATH.stat().st_size / 1024:.0f} KB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
