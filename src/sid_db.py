"""sid_db.py — write-through helpers for hvsc84.db.

Producers in pipelines/ call these after writing their outputs so
the index stays current without needing a manual
`python3 tools/build_sid_db.py` re-run. Silent no-op if the db
doesn't exist or the output isn't under hvsc84/.

Wired into:
  - pipelines/hubbard/to_usf.write_usf      → record_usf
  - pipelines/hubbard/build_from_usf.build_from_usf → record_rebuild
  - pipelines/hubbard/verify.verify_all        → record_verify
  - pipelines/companion/to_usf.write_usf    → record_usf
  - pipelines/companion/build_from_usf.build_from_usf → record_rebuild

Schema lives in tools/build_sid_db.py — these helpers only UPDATE
columns on rows that already exist (created by build_sid_db.py).
If a row is missing (e.g. a brand-new HVSC SID not yet indexed),
the writes are skipped silently; re-run build_sid_db.py to insert it.
"""

from __future__ import annotations

import datetime
import hashlib
import os
import sqlite3
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent.parent
HVSC = ROOT / 'hvsc84'
DB_PATH = ROOT / 'hvsc84.db'


def _hvsc_relpath(output_path: str | os.PathLike) -> str | None:
    """Map an output path under hvsc84/ to its source SID's HVSC relpath.

    Examples:
      hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid
        → 'MUSICIANS/H/Hubbard_Rob/Commando.sid'
      hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.usf
        → 'MUSICIANS/H/Hubbard_Rob/Commando.sid'
      /tmp/foo.sid                       → None (not in HVSC tree)
      hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sid → None (this IS a source,
                                                     not a derived output)
    """
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
        while True:
            chunk = f.read(64 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _connect() -> sqlite3.Connection | None:
    """Return a DB connection, or None if the db doesn't exist."""
    if not DB_PATH.exists():
        return None
    return sqlite3.connect(DB_PATH)


def record_usf(usf_path: str | os.PathLike) -> None:
    """Record that a .usf was written next to its HVSC source."""
    rel = _hvsc_relpath(usf_path)
    if rel is None:
        return
    db = _connect()
    if db is None:
        return
    try:
        usf_rel = str(Path(usf_path).resolve().relative_to(HVSC.resolve()))
        db.execute('UPDATE sids SET usf_path=? WHERE path=?',
                   (usf_rel, rel))
        db.commit()
    finally:
        db.close()


def record_rebuild(sidfinity_path: str | os.PathLike) -> None:
    """Record that a .sidfinity.sid was written next to its HVSC source."""
    rel = _hvsc_relpath(sidfinity_path)
    if rel is None:
        return
    db = _connect()
    if db is None:
        return
    try:
        md5 = _md5(sidfinity_path)
        db.execute('UPDATE sids SET sidfinity_md5=? WHERE path=?',
                   (md5, rel))
        db.commit()
    finally:
        db.close()


def record_verify(rebuilt_path: str | os.PathLike,
                  per_subtune: Iterable[tuple[int, bool]]) -> None:
    """Record verify_all results for one engine.

    `rebuilt_path` is the path to our .sidfinity.sid (used to identify the
    HVSC source). `per_subtune` is a list of (subtune_index, ok_bool).
    """
    rel = _hvsc_relpath(rebuilt_path)
    if rel is None:
        return
    db = _connect()
    if db is None:
        return
    try:
        results = list(per_subtune)
        ok_subs = sum(1 for _, ok in results if ok)
        total_subs = len(results)
        status = 'ok' if (total_subs > 0 and ok_subs == total_subs) else 'fail'
        now = datetime.datetime.now().isoformat(timespec='seconds')
        db.execute("""
            UPDATE sids SET
                verify_status=?, verify_ok_subs=?,
                verify_total_subs=?, last_verified_at=?
            WHERE path=?""",
            (status, ok_subs, total_subs, now, rel))
        db.commit()
    finally:
        db.close()
