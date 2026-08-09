"""sid_db.py — the HVSC index (static catalogue), stored as a compact Parquet
file and queried via the DuckDB CLI.

The catalogue is one row per HVSC .sid:
  - hvsc85.parquet   built by tools/build_sid_db.py (zstd; ~3.4 MB)
  - engine_docs.csv  per-engine-family research state (tiny; stays CSV)

It holds ONLY static catalogue data — path, PSID header, engine classification,
songlength, exclusion. It deliberately does NOT cache per-build verdicts. Build
status (which SIDs verify FULL, their rebuilt md5, .usf path) was removed
2026-07-04: those columns had zero readers, were 99.9% empty, and — crucially —
were a palimpsest surface (a persisted verdict goes stale the moment
extract/composer code changes) whose full-file-rewrite write-through was a
concurrency hazard for parallel sessions. Derive coverage on demand from a
fresh family batch, never from a cached column. (Removed along with the
`record_usf`/`record_rebuild`/`record_verify` write-through helpers.)

Read/query: `query(sql, params)` and `connect().execute(sql, params)` shell out
to the **DuckDB CLI binary** (found on PATH, then ~/.local/bin/duckdb),
returning sqlite3-style tuples. This deliberately does NOT use the duckdb Python
module — so DB reads need only `duckdb` on PATH, with no env.sh / PYTHONPATH /
.pylocal dependency. The `sids` view reads the parquet; `engine_docs` reads the
CSV. Ad-hoc: `duckdb -c "SELECT … FROM read_parquet('hvsc85.parquet')"`.

The catalogue is regenerated wholesale (not incrementally written) by
build_sid_db.py, so in normal development nothing writes it — it is read-mostly
and parallel-safe. Schema (columns/types) is defined here and consumed by
build_sid_db.py.
"""

from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
HVSC = ROOT / 'hvsc85'
PARQUET_PATH = ROOT / 'hvsc85.parquet'
ENGINE_DOCS_CSV = ROOT / 'engine_docs.csv'

# ---------------------------------------------------------------------------
# Schema — column order + DuckDB types. Static catalogue only (no build status).
# ---------------------------------------------------------------------------
SIDS_TYPES: dict[str, str] = {
    'path': 'VARCHAR', 'md5': 'VARCHAR', 'size': 'BIGINT', 'mtime': 'DOUBLE',
    'is_psid': 'INTEGER', 'psid_version': 'INTEGER', 'load_addr': 'INTEGER',
    'init_addr': 'INTEGER', 'play_addr': 'INTEGER', 'n_subtunes': 'INTEGER',
    'start_subtune': 'INTEGER', 'title': 'VARCHAR', 'author': 'VARCHAR',
    'released': 'VARCHAR', 'engine': 'VARCHAR', 'songlength_s': 'DOUBLE',
    'excluded': 'INTEGER', 'exclusion_reason': 'VARCHAR',
}
SIDS_COLUMNS = list(SIDS_TYPES)
# integer/float columns that need '' <-> None and numeric coercion in the CSV
# intermediate used by write_all.
_NUMERIC = {c for c, t in SIDS_TYPES.items()
            if t in ('BIGINT', 'INTEGER', 'DOUBLE')}

ENGINE_DOCS_TYPES: dict[str, str] = {
    'family': 'VARCHAR', 'doc_state': 'VARCHAR', 'notes': 'VARCHAR',
    'updated': 'VARCHAR', 'engines': 'VARCHAR', 'sid_count': 'BIGINT',
}
ENGINE_DOCS_COLUMNS = list(ENGINE_DOCS_TYPES)


def _colspec(types: dict[str, str]) -> str:
    return '{' + ', '.join(f"'{k}': '{v}'" for k, v in types.items()) + '}'


def _read_csv_clause(path: Path, types: dict[str, str]) -> str:
    """DuckDB read_csv(...) call with our dialect (RFC-4180 doubled quotes,
    empty == NULL, explicit columns so the schema is data-independent). Used for
    engine_docs.csv and the temp CSV that write_all COPYs into parquet."""
    return (f"read_csv('{path}', header=true, nullstr='', auto_detect=false, "
            f"escape='\"', columns={_colspec(types)})")


def _read_parquet_clause(path: Path) -> str:
    return f"read_parquet('{path}')"


# ---------------------------------------------------------------------------
# Query side — shell out to the DuckDB CLI binary.
#
# Reads go through the `duckdb` CLI (found on PATH / ~/.local/bin), NOT the
# Python module — so DB queries need only `duckdb` on PATH. Each query() spawns
# one `duckdb` process that reads the parquet, so don't call query() inside a
# tight per-row loop — read_all() + filter in Python for that.
# ---------------------------------------------------------------------------
_DUCKDB_BIN = None


def _duckdb_bin() -> str:
    """Locate the DuckDB CLI: PATH, then ~/.local/bin, then the snap inner
    binary. Cached. Raises with install guidance if absent."""
    global _DUCKDB_BIN
    if _DUCKDB_BIN:
        return _DUCKDB_BIN
    cand = shutil.which('duckdb')
    if not cand:
        for p in (Path.home() / '.local' / 'bin' / 'duckdb',
                  Path('/snap/duckdb/current/duckdb')):
            if p.exists():
                cand = str(p)
                break
    if not cand:
        raise RuntimeError(
            'duckdb CLI not found (PATH / ~/.local/bin/duckdb). Install the '
            'standalone CLI, e.g. download duckdb_cli-linux-amd64.zip to '
            '~/.local/bin/duckdb.')
    _DUCKDB_BIN = cand
    return cand


def _lit(v) -> str:
    """SQL literal for a bound param (internal/trusted inputs only)."""
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, float)):
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def _bind(sql: str, params: Iterable) -> str:
    """Substitute `?` placeholders with escaped literals (no literal `?` may
    appear inside the query's own strings — none of ours do)."""
    params = list(params)
    if not params:
        return sql
    parts = sql.split('?')
    if len(parts) - 1 != len(params):
        raise ValueError(f'{len(parts) - 1} placeholders vs {len(params)} params')
    return parts[0] + ''.join(_lit(p) + seg for p, seg in zip(params, parts[1:]))


def _setup_sql() -> str:
    """CREATE VIEW sids (parquet) / engine_docs (csv)."""
    s = []
    if PARQUET_PATH.exists():
        s.append('CREATE VIEW sids AS SELECT * FROM '
                 + _read_parquet_clause(PARQUET_PATH) + ';')
    if ENGINE_DOCS_CSV.exists():
        s.append('CREATE VIEW engine_docs AS SELECT * FROM '
                 + _read_csv_clause(ENGINE_DOCS_CSV, ENGINE_DOCS_TYPES) + ';')
    return ' '.join(s)


def query(sql: str, params: Iterable = ()) -> list[tuple]:
    """Run `sql` (with `?` params) against the index via the duckdb CLI;
    return a list of tuples (columns in SELECT order, sqlite3-style)."""
    full = _setup_sql() + ' ' + _bind(sql, params)
    proc = subprocess.run([_duckdb_bin(), '-json', '-c', full],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f'duckdb query failed: {proc.stderr.strip()}\nSQL: {sql}')
    out = proc.stdout.strip()
    rows = json.loads(out) if out else []
    return [tuple(r.values()) for r in rows]


class _Result(list):
    """sqlite3-cursor-ish: iterable list of tuples + fetchall/fetchone."""
    def fetchall(self):
        return list(self)

    def fetchone(self):
        return self[0] if self else None


class _Conn:
    """Adapter so consumers keep the sqlite3-style `db.execute(sql, params)`
    -> iterable-of-tuples API. Each execute() is one CLI query."""
    def execute(self, sql: str, params: Iterable = ()):
        return _Result(query(sql, params))

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


def connect() -> _Conn:
    """Return a connection-like adapter; `.execute(sql, params)` runs against
    the index via the duckdb CLI. No persistent state (each query reopens the
    parquet), so `.close()` is a no-op."""
    return _Conn()


# ---------------------------------------------------------------------------
# Bulk read/write (used by build_sid_db.py)
# ---------------------------------------------------------------------------
def read_all() -> dict[str, dict]:
    """Read hvsc85.parquet into {path: {col: value}} (DuckDB-typed; missing
    field -> None). Empty dict if the parquet is absent. Uses one duckdb -json
    process — cheap enough for the once-per-rebuild mtime/md5 cache load."""
    if not PARQUET_PATH.exists():
        return {}
    proc = subprocess.run(
        [_duckdb_bin(), '-json', '-c',
         'SELECT * FROM ' + _read_parquet_clause(PARQUET_PATH)],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f'duckdb read_all failed: {proc.stderr.strip()}')
    out = proc.stdout.strip()
    recs = json.loads(out) if out else []
    return {r['path']: {c: r.get(c) for c in SIDS_COLUMNS} for r in recs}


def _fmt(val) -> str:
    return '' if val is None else str(val)


def _write_csv(path: Path, columns: list[str], rows: Iterable[dict]) -> None:
    """Atomically write `rows` (dicts) to `path` with `columns` order."""
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(columns)
            for r in rows:
                w.writerow([_fmt(r.get(c)) for c in columns])
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _csv_to_parquet(csv_path: Path, types: dict[str, str], out: Path) -> None:
    """COPY a typed read_csv of `csv_path` into `out` as zstd parquet (atomic)."""
    fd, tmp = tempfile.mkstemp(dir=str(out.parent), suffix='.parquet.tmp')
    os.close(fd)
    sql = (f"COPY (SELECT * FROM {_read_csv_clause(csv_path, types)}) "
           f"TO '{tmp}' (FORMAT parquet, COMPRESSION zstd);")
    proc = subprocess.run([_duckdb_bin(), '-c', sql],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise RuntimeError(f'parquet write failed: {proc.stderr.strip()}')
    os.replace(tmp, out)


def write_all(rows) -> None:
    """Write the sids catalogue to hvsc85.parquet (path-sorted). Serialises
    through a typed temp CSV so DuckDB assigns the exact declared column types
    (no auto-detect surprises on all-NULL columns)."""
    items = rows.values() if isinstance(rows, dict) else rows
    ordered = sorted(items, key=lambda r: r['path'])
    tmpdir = ROOT / 'tmp'
    tmpdir.mkdir(exist_ok=True)
    fd, tmp_csv = tempfile.mkstemp(dir=str(tmpdir), suffix='.csv')
    os.close(fd)
    tmp_csv = Path(tmp_csv)
    try:
        _write_csv(tmp_csv, SIDS_COLUMNS, ordered)
        _csv_to_parquet(tmp_csv, SIDS_TYPES, PARQUET_PATH)
    finally:
        try:
            tmp_csv.unlink()
        except OSError:
            pass


def write_engine_docs(rows: list[dict]) -> None:
    """Write engine_docs.csv (family-sorted; stays CSV — tiny + occasionally
    hand-inspected)."""
    _write_csv(ENGINE_DOCS_CSV, ENGINE_DOCS_COLUMNS,
               sorted(rows, key=lambda r: r['family']))
