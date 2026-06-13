#!/usr/bin/env python3
"""Refresh ONLY the engine_docs table from tools/engine_docs.json.

The full tools/build_sid_db.py also (re)populates engine_docs, but it re-walks
and re-hashes 60k SIDs. This is the cheap path: after editing engine_docs.json
(e.g. bumping a family LITTLE -> OK once its research-engine sweep lands), run
this to update just the one table in seconds.

Uses a 30s busy_timeout so it waits politely if another process holds the DB
write lock (the catalogue is a single-writer SQLite file in 'delete' journal
mode — do not run this while a large build_sid_db.py / pipeline write is mid
-transaction; it will block, not corrupt).
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # tools/ on path
import build_sid_db as b


def main() -> int:
    db = sqlite3.connect(b.DB_PATH, timeout=30)
    db.execute('PRAGMA busy_timeout=30000')
    db.executescript(b.SCHEMA)              # ensure engine_docs table exists
    n = b.populate_engine_docs(db)
    db.commit()
    db.close()
    print(f'engine_docs: {n} families applied to {b.DB_PATH}')
    # quick tally for confirmation
    db = sqlite3.connect(f'file:{b.DB_PATH}?mode=ro', uri=True)
    rows = db.execute(
        'SELECT doc_state, COUNT(*) FROM engine_docs GROUP BY doc_state '
        "ORDER BY CASE doc_state WHEN 'OK' THEN 0 WHEN 'SOME' THEN 1 "
        "WHEN 'LITTLE' THEN 2 ELSE 3 END").fetchall()
    print('  tally:', {s: c for s, c in rows})
    return 0


if __name__ == '__main__':
    sys.exit(main())
