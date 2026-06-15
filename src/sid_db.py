"""sid_db.py — the HVSC index, stored as a git-trackable CSV + queried via DuckDB.

The catalogue lives in two CSVs at the repo root (committed, so git tracks
content changes as readable line diffs instead of a binary blob):
  - hvsc84.csv      one row per HVSC .sid (built by tools/build_sid_db.py)
  - engine_docs.csv per-engine-family research state (from tools/engine_docs.json)

Read/query: `connect()` returns a DuckDB connection with `sids` + `engine_docs`
registered as views over the CSVs, wrapped so consumers keep the sqlite3-style
`db.execute(sql, params)` -> iterable-of-tuples API. `query(sql, params)` is a
one-shot helper. The DuckDB CLI can also read these CSVs directly for ad-hoc
analysis (e.g. `read_csv('hvsc84.csv', header=true, nullstr='')`).

Write-through: producers call `record_usf` / `record_rebuild` / `record_verify`
after writing outputs so the index stays current without a full rebuild. These
do a CSV read-modify-write (the file has no row-level update) — fine for the
single-threaded, low-frequency interactive-build / regression paths that use
them (the parallel batches build to tmp/ and never write-through). Silent no-op
if the CSV doesn't exist or the output isn't under hvsc84/. For a brand-new SID
not yet in the CSV the write is skipped; re-run tools/build_sid_db.py to insert
it. Schema (columns/types) is defined here and consumed by build_sid_db.py.
"""

from __future__ import annotations

import csv
import datetime
import hashlib
import os
import tempfile
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
HVSC = ROOT / 'hvsc84'
CSV_PATH = ROOT / 'hvsc84.csv'
ENGINE_DOCS_CSV = ROOT / 'engine_docs.csv'

# ---------------------------------------------------------------------------
# Schema — column order + DuckDB types. Empty CSV field == SQL NULL.
# ---------------------------------------------------------------------------
SIDS_TYPES: dict[str, str] = {
    'path': 'VARCHAR', 'md5': 'VARCHAR', 'size': 'BIGINT', 'mtime': 'DOUBLE',
    'is_psid': 'INTEGER', 'psid_version': 'INTEGER', 'load_addr': 'INTEGER',
    'init_addr': 'INTEGER', 'play_addr': 'INTEGER', 'n_subtunes': 'INTEGER',
    'start_subtune': 'INTEGER', 'title': 'VARCHAR', 'author': 'VARCHAR',
    'released': 'VARCHAR', 'engine': 'VARCHAR', 'songlength_s': 'DOUBLE',
    'pipeline': 'VARCHAR', 'usf_path': 'VARCHAR', 'sidfinity_md5': 'VARCHAR',
    'verify_status': 'VARCHAR', 'verify_ok_subs': 'INTEGER',
    'verify_total_subs': 'INTEGER', 'last_verified_at': 'VARCHAR',
    'excluded': 'INTEGER', 'exclusion_reason': 'VARCHAR',
}
SIDS_COLUMNS = list(SIDS_TYPES)
# integer/float columns that need '' <-> None and numeric coercion on read
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
    empty == NULL, explicit columns so the schema is data-independent)."""
    return (f"read_csv('{path}', header=true, nullstr='', auto_detect=false, "
            f"escape='\"', columns={_colspec(types)})")


# ---------------------------------------------------------------------------
# Query side — DuckDB views over the CSVs
# ---------------------------------------------------------------------------
class _Result(list):
    """sqlite3-cursor-ish: iterable list of tuples + fetchall/fetchone."""
    def fetchall(self):
        return list(self)

    def fetchone(self):
        return self[0] if self else None


class _Conn:
    """Adapter so consumers keep `db.execute(sql, params)` returning rows."""
    def __init__(self, con):
        self._con = con

    def execute(self, sql: str, params: Iterable = ()):
        return _Result(self._con.execute(sql, list(params)).fetchall())

    def close(self):
        self._con.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def connect() -> _Conn:
    """DuckDB connection with `sids` + `engine_docs` views over the CSVs.
    Missing CSVs simply mean the view is absent (queries then raise, as a
    missing SQLite db would)."""
    import duckdb
    con = duckdb.connect()
    if CSV_PATH.exists():
        con.execute('CREATE VIEW sids AS SELECT * FROM '
                    + _read_csv_clause(CSV_PATH, SIDS_TYPES))
    if ENGINE_DOCS_CSV.exists():
        con.execute('CREATE VIEW engine_docs AS SELECT * FROM '
                    + _read_csv_clause(ENGINE_DOCS_CSV, ENGINE_DOCS_TYPES))
    return _Conn(con)


def query(sql: str, params: Iterable = ()) -> list[tuple]:
    """One-shot query; opens a connection, runs `sql`, returns rows."""
    con = connect()
    try:
        return con.execute(sql, params).fetchall()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# CSV read/write (used by build_sid_db.py + the write-through helpers)
# ---------------------------------------------------------------------------
def _coerce(col: str, val: str):
    if val == '':
        return None
    if col in _NUMERIC:
        f = float(val)
        return f if SIDS_TYPES[col] == 'DOUBLE' else int(f)
    return val


def read_all() -> dict[str, dict]:
    """Read hvsc84.csv into {path: {col: value}} with '' -> None and numeric
    columns coerced to int/float. Empty dict if the CSV is absent."""
    if not CSV_PATH.exists():
        return {}
    out: dict[str, dict] = {}
    with CSV_PATH.open(newline='') as f:
        for row in csv.DictReader(f):
            out[row['path']] = {c: _coerce(c, row.get(c, '')) for c in SIDS_COLUMNS}
    return out


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


def write_all(rows) -> None:
    """Write the sids CSV (path-sorted for stable git diffs)."""
    items = rows.values() if isinstance(rows, dict) else rows
    _write_csv(CSV_PATH, SIDS_COLUMNS, sorted(items, key=lambda r: r['path']))


def write_engine_docs(rows: list[dict]) -> None:
    """Write engine_docs.csv (family-sorted)."""
    _write_csv(ENGINE_DOCS_CSV, ENGINE_DOCS_COLUMNS,
               sorted(rows, key=lambda r: r['family']))


# ---------------------------------------------------------------------------
# Write-through (single-threaded, low-frequency: interactive builds + regression)
# ---------------------------------------------------------------------------
def _hvsc_relpath(output_path: str | os.PathLike) -> str | None:
    """Map a derived output under hvsc84/ to its source SID's HVSC relpath
    (Foo.usf / Foo.sidfinity.sid -> Foo.sid). None if not a derived output."""
    try:
        p = Path(output_path).resolve()
        rel = p.relative_to(HVSC.resolve())
    except (ValueError, OSError):
        return None
    name = rel.name
    if name.endswith('.sidfinity.sid'):
        base = name[: -len('.sidfinity.sid')]
    elif name.endswith('.usf'):
        base = name[: -len('.usf')]
    else:
        return None
    return str(rel.parent / (base + '.sid'))


def _md5(path: str | os.PathLike) -> str:
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(64 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def _update_row(rel: str, updates: dict) -> None:
    """Apply `updates` to the row with path==rel and rewrite the CSV.
    No-op if the CSV or the row is absent (re-run build_sid_db.py to insert)."""
    rows = read_all()
    if rel not in rows:
        return
    rows[rel].update(updates)
    write_all(rows)


def record_usf(usf_path: str | os.PathLike) -> None:
    """Record that a .usf was written next to its HVSC source."""
    rel = _hvsc_relpath(usf_path)
    if rel is None or not CSV_PATH.exists():
        return
    usf_rel = str(Path(usf_path).resolve().relative_to(HVSC.resolve()))
    _update_row(rel, {'usf_path': usf_rel})


def record_rebuild(sidfinity_path: str | os.PathLike) -> None:
    """Record that a .sidfinity.sid was written next to its HVSC source."""
    rel = _hvsc_relpath(sidfinity_path)
    if rel is None or not CSV_PATH.exists():
        return
    _update_row(rel, {'sidfinity_md5': _md5(sidfinity_path)})


def record_verify(rebuilt_path: str | os.PathLike,
                  per_subtune: Iterable[tuple[int, bool]]) -> None:
    """Record verify_all results for one engine. `per_subtune` is a list of
    (subtune_index, ok_bool)."""
    rel = _hvsc_relpath(rebuilt_path)
    if rel is None or not CSV_PATH.exists():
        return
    results = list(per_subtune)
    ok_subs = sum(1 for _, ok in results if ok)
    total = len(results)
    status = 'ok' if (total > 0 and ok_subs == total) else 'fail'
    _update_row(rel, {
        'verify_status': status, 'verify_ok_subs': ok_subs,
        'verify_total_subs': total,
        'last_verified_at': datetime.datetime.now().isoformat(timespec='seconds'),
    })
