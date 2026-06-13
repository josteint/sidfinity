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
# Per-family documentation state (tools/engine_docs.json -> engine_docs table)
# ---------------------------------------------------------------------------
#
# doc_state is a research-PROGRESS ladder, NOT a content-volume measure:
#   NONE   no pipelines/<family>/ dir; never researched (absent from the table)
#   LITTLE single stub research.md; no real sweep yet
#   SOME   research-engine run / substantial corpus, with known gaps to chase
#   OK     research-engine sweep complete; cleared to start disassembling
# A family reaches OK by COMPLETING a research-engine sweep, regardless of how
# much was found. The durable source of truth is tools/engine_docs.json; this
# table just materialises it (re-applied on every build, and cheaply via
# tools/apply_engine_docs.py after editing the JSON).

# sids.engine (sidid string) -> pipelines/<family> dir, for the names that
# don't fall out of plain normalisation (version suffixes, group/author
# prefixes, punctuation). Plain cases are handled by engine_to_family().
ENGINE_FAMILY_ALIAS = {
    'GoatTracker_V2.x': 'goattracker', 'GoatTracker_V1.x': 'goattracker',
    'MoN/FutureComposer': 'future_composer', 'MoN/Deenen': 'mon_deenen',
    'JCH_NewPlayer': 'jch_newplayer', 'HardTrack_Composer': 'hardtrack',
    'Hermit/SidWizard_V1.x': 'sidwizard', "Geir_Tjelta/SIDDuzz'It": 'sidduzzit',
    'RoMuzak_V6.x': 'romuzak', 'RoMuzak_V7.x': 'romuzak',
    'Digitalizer_V2.x': 'digitalizer', 'Digitalizer_V3.0': 'digitalizer',
    'GMC/Superiors': 'gmc', 'X-Ample': 'xample',
    'SidFactory_II/Laxity': 'sidfactory_ii', 'Laxity_NewPlayer_V21': 'laxity_newplayer',
    'CheeseCutter_2.x': 'cheesecutter', "Ubik's_Musik": 'ubiks_musik',
    'Rob_Hubbard': 'hubbard',
    'DefleMask_v12': 'deflemask', 'DefleMask_v2': 'deflemask', 'DefleMask_v1': 'deflemask',
    'Cyberlogic_SoundStudio': 'cyberlogic', 'EMS/Odie': 'ems_odie',
    'Vibrants/Laxity': 'vibrants_laxity', 'Vibrants/JO': 'vibrants_jo',
    'CyberTracker_exe': 'cybertracker', 'CyberTracker': 'cybertracker',
    'LordsOfSonics/MS': 'lords_of_sonics', 'SynC': 'sync',
    'NinjaTracker_V2.x': 'ninjatracker', 'NinjaTracker_V1.x': 'ninjatracker',
    'Loadstar_SongSmith': 'loadstar_songsmith',
    'Loadstar_SongSmith_v1': 'loadstar_songsmith',
    'Loadstar_SongSmith_v2': 'loadstar_songsmith',
    'Loadstar_SongSmith_v3': 'loadstar_songsmith',
    'DMC_V6.x': 'dmc',
}


def engine_to_family(engine: str | None) -> str | None:
    """Map a sids.engine string to its pipelines/<family> dir name."""
    if engine is None:
        return None
    if engine in ENGINE_FAMILY_ALIAS:
        return ENGINE_FAMILY_ALIAS[engine]
    n = engine.lower()
    n = re.sub(r'_v\d+(\.\w+)?$', '', n)                 # strip _V2.x / _V21
    n = n.replace('/', '_').replace('-', '_').replace(' ', '_').replace("'", '')
    return n


def load_engine_docs() -> dict:
    """Read tools/engine_docs.json: {family: {state, notes, updated}}."""
    import json
    p = ROOT / 'tools' / 'engine_docs.json'
    if not p.exists():
        return {}
    return json.loads(p.read_text())


def populate_engine_docs(db: sqlite3.Connection) -> int:
    """Rebuild the engine_docs table from tools/engine_docs.json.

    One row per family listed in the JSON, annotated with the sids.engine
    strings that resolve to it and their total SID count. Idempotent: the
    table is cleared and rewritten, so removing a family from the JSON drops
    its row. Families absent from the JSON are, by convention, NONE.
    """
    import json
    docs = load_engine_docs()
    cur = db.cursor()
    fam_engines: dict[str, list[str]] = {}
    fam_count: dict[str, int] = {}
    for engine, cnt in cur.execute('SELECT engine, COUNT(*) FROM sids GROUP BY engine'):
        fam = engine_to_family(engine)
        if fam is None:
            continue
        fam_engines.setdefault(fam, []).append(engine)
        fam_count[fam] = fam_count.get(fam, 0) + cnt
    cur.execute('DELETE FROM engine_docs')
    for fam, meta in sorted(docs.items()):
        engines = sorted(fam_engines.get(fam, []))
        cur.execute(
            'INSERT INTO engine_docs '
            '(family, doc_state, notes, updated, engines, sid_count) '
            'VALUES (?,?,?,?,?,?)',
            (fam, meta.get('state', 'NONE'), meta.get('notes'),
             meta.get('updated'), json.dumps(engines), fam_count.get(fam, 0)))
    return len(docs)


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
    last_verified_at    TEXT,

    -- exclusion (from tools/excluded_sids.json — SIDs that don't fit
    -- the principled USF and are deliberately kept out of the pipeline).
    -- The pipeline (build_from_usf / write_usf) refuses these with a
    -- clear error. See src/exclusions.py.
    excluded            INTEGER DEFAULT 0,   -- 1 = listed in excluded_sids.json
    exclusion_reason    TEXT
);
CREATE INDEX IF NOT EXISTS idx_engine ON sids(engine);
CREATE INDEX IF NOT EXISTS idx_pipeline ON sids(pipeline);
CREATE INDEX IF NOT EXISTS idx_md5 ON sids(md5);
CREATE INDEX IF NOT EXISTS idx_excluded ON sids(excluded);

-- Per-engine-family documentation state (see populate_engine_docs + the
-- tools/engine_docs.json source of truth). One row per family.
CREATE TABLE IF NOT EXISTS engine_docs (
    family      TEXT PRIMARY KEY,    -- pipelines/<family> dir name
    doc_state   TEXT NOT NULL,       -- NONE | LITTLE | SOME | OK
    notes       TEXT,
    updated     TEXT,                -- YYYY-MM-DD
    engines     TEXT,                -- JSON array of sids.engine strings mapped here
    sid_count   INTEGER              -- total SIDs across those engine strings
);
CREATE INDEX IF NOT EXISTS idx_doc_state ON engine_docs(doc_state);
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

    # Local overrides — applied AFTER HVSC ingest. Used to correct anomalous
    # HVSC entries (e.g. defaulted 4-second values for tunes whose natural
    # loop is much longer). Survives HVSC re-fetches; the corresponding
    # edits to Songlengths.md5 itself are local-only.
    overrides_path = ROOT / 'tools' / 'songlength_overrides.json'
    if overrides_path.exists():
        import json
        overrides = json.loads(overrides_path.read_text())
        n_applied = 0
        for md5, entry in overrides.items():
            if not isinstance(entry, dict) or 'seconds' not in entry:
                continue
            songlengths[md5] = entry['seconds']
            n_applied += 1
        if not args.quiet:
            print(f'    {n_applied} songlength overrides applied from '
                  f'{overrides_path.relative_to(ROOT)}')

    if not args.quiet:
        print(f'  resolving pipeline mappings from pipelines/...')
    pipeline_map = build_pipeline_map()
    if not args.quiet:
        print(f'    {len(pipeline_map)} SIDs handled by active pipelines')

    # Load exclusions (SIDs deliberately kept out of the pipeline).
    if not args.quiet:
        print(f'  loading exclusions from tools/excluded_sids.json...')
    from src.exclusions import all_excluded
    excluded_map = all_excluded()      # {rel-from-repo-root: reason}
    # Normalize keys to HVSC-relative paths (drop 'hvsc84/' prefix).
    excluded_hvsc = {
        p[len('hvsc84/'):] if p.startswith('hvsc84/') else p: r
        for p, r in excluded_map.items()
    }
    if not args.quiet:
        print(f'    {len(excluded_hvsc)} SIDs in the exclusion list')

    # Connect DB
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    # In-place migrations for columns added after the original table.
    # SQLite's CREATE TABLE IF NOT EXISTS skips changes when the table
    # already exists, so any new column needs an explicit ALTER. Run
    # these BEFORE the schema (the schema references these columns in
    # an index). The try/except shrugs off "already exists".
    cur.execute('CREATE TABLE IF NOT EXISTS sids (path TEXT PRIMARY KEY)')
    for alter in (
        'ALTER TABLE sids ADD COLUMN excluded INTEGER DEFAULT 0',
        'ALTER TABLE sids ADD COLUMN exclusion_reason TEXT',
    ):
        try:
            cur.execute(alter)
        except sqlite3.OperationalError as e:
            if 'duplicate column' not in str(e).lower():
                raise
    db.executescript(SCHEMA)

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

        excl_reason = excluded_hvsc.get(rel)
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
            'excluded': 1 if excl_reason else 0,
            'exclusion_reason': excl_reason,
            **hdr,
        }
        upsert(cur, row)

        if not args.quiet and n_files % 5000 == 0:
            dt = time.time() - t_sweep
            print(f'    {n_files:,} files | {n_hashed:,} hashed | '
                  f'{n_skipped:,} cached | {n_files/dt:.0f} files/s')

    n_docs = populate_engine_docs(db)
    if not args.quiet:
        print(f'  engine_docs: {n_docs} families from tools/engine_docs.json')

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
