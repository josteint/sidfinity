"""
grade_db.py — SQLite grade database for HVSC pipeline tracking.

Stores current grades and full history for every song across all engines.

Schema:
  songs   — current state of each song (path, engine, grade, score, etc.)
  history — append-only log of every grade change

Grades (quality):  S, A, B, C, F
Grades (pipeline): USF, PARSE, ID
"""

import sqlite3
import os
import subprocess
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'grades.db')


def _get_commit():
    """Get current git commit hash."""
    try:
        r = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
                           capture_output=True, text=True, timeout=5,
                           cwd=os.path.dirname(os.path.abspath(__file__)))
        return r.stdout.strip() if r.returncode == 0 else None
    except:
        return None


def connect(db_path=None):
    """Connect to the grade database, creating tables if needed."""
    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    db = sqlite3.connect(path)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('''CREATE TABLE IF NOT EXISTS songs (
        path        TEXT PRIMARY KEY,
        engine      TEXT,
        grade       TEXT,
        score       REAL,
        last_tested TEXT,
        commit_hash TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS history (
        path        TEXT,
        grade       TEXT,
        score       REAL,
        tested_at   TEXT,
        commit_hash TEXT
    )''')
    db.execute('CREATE INDEX IF NOT EXISTS idx_history_path ON history(path)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_songs_engine ON songs(engine)')
    db.execute('CREATE INDEX IF NOT EXISTS idx_songs_grade ON songs(grade)')
    db.commit()
    return db


def record(db, path, engine, grade, score=None, commit_hash=None):
    """Record a grade for a song. Updates songs table and appends to history."""
    now = datetime.now().isoformat(timespec='seconds')
    commit = commit_hash or _get_commit()

    # Get previous grade
    row = db.execute('SELECT grade, score FROM songs WHERE path = ?', (path,)).fetchone()
    old_grade = row[0] if row else None

    # Update current state
    db.execute('''INSERT OR REPLACE INTO songs (path, engine, grade, score, last_tested, commit_hash)
                  VALUES (?, ?, ?, ?, ?, ?)''',
               (path, engine, grade, score, now, commit))

    # Append to history only if grade changed or first entry
    if old_grade != grade:
        db.execute('''INSERT INTO history (path, grade, score, tested_at, commit_hash)
                      VALUES (?, ?, ?, ?, ?)''',
                   (path, grade, score, now, commit))

    return old_grade


def record_batch(db, entries, commit_hash=None):
    """Record grades for many songs at once. Returns (updated, regressions, improvements).

    entries: list of (path, engine, grade, score) tuples
    """
    now = datetime.now().isoformat(timespec='seconds')
    commit = commit_hash or _get_commit()

    GRADE_ORDER = {'S': 0, 'A': 1, 'B': 2, 'C': 3, 'F': 4,
                   'USF': 5, 'PARSE': 6, 'ID': 7}

    # Load all current grades in one query
    old_grades = {}
    for row in db.execute('SELECT path, grade FROM songs'):
        old_grades[row[0]] = row[1]

    updated = 0
    regressions = []
    improvements = []
    history_rows = []

    for path, engine, grade, score in entries:
        old = old_grades.get(path)
        old_rank = GRADE_ORDER.get(old, 99)
        new_rank = GRADE_ORDER.get(grade, 99)

        if old != grade:
            history_rows.append((path, grade, score, now, commit))
            if old is not None:
                if new_rank > old_rank:
                    regressions.append((path, old, grade))
                elif new_rank < old_rank:
                    improvements.append((path, old, grade))

        db.execute('''INSERT OR REPLACE INTO songs (path, engine, grade, score, last_tested, commit_hash)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (path, engine, grade, score, now, commit))
        updated += 1

    if history_rows:
        db.executemany('''INSERT INTO history (path, grade, score, tested_at, commit_hash)
                          VALUES (?, ?, ?, ?, ?)''', history_rows)

    db.commit()
    return updated, regressions, improvements


def grade_summary(db, engine=None):
    """Get grade counts, optionally filtered by engine."""
    if engine:
        rows = db.execute('SELECT grade, COUNT(*) FROM songs WHERE engine = ? GROUP BY grade',
                          (engine,)).fetchall()
    else:
        rows = db.execute('SELECT grade, COUNT(*) FROM songs GROUP BY grade').fetchall()
    return dict(rows)


def engine_summary(db):
    """Get grade counts per engine."""
    rows = db.execute('SELECT engine, grade, COUNT(*) FROM songs GROUP BY engine, grade').fetchall()
    result = {}
    for engine, grade, count in rows:
        result.setdefault(engine, {})[grade] = count
    return result


def regressions_since(db, since_commit=None, since_date=None):
    """Find songs that regressed since a given commit or date."""
    GRADE_ORDER = {'S': 0, 'A': 1, 'B': 2, 'C': 3, 'F': 4,
                   'USF': 5, 'PARSE': 6, 'ID': 7}

    if since_commit:
        rows = db.execute('''SELECT h1.path, h1.grade as old_grade, s.grade as new_grade
                             FROM history h1
                             JOIN songs s ON h1.path = s.path
                             WHERE h1.commit_hash = ?
                             AND h1.grade != s.grade''',
                          (since_commit,)).fetchall()
    elif since_date:
        rows = db.execute('''SELECT DISTINCT h1.path, h1.grade as old_grade, s.grade as new_grade
                             FROM history h1
                             JOIN songs s ON h1.path = s.path
                             WHERE h1.tested_at <= ?
                             AND h1.grade != s.grade
                             ORDER BY h1.tested_at DESC''',
                          (since_date,)).fetchall()
    else:
        return []

    regs = []
    for path, old, new in rows:
        old_rank = GRADE_ORDER.get(old, 99)
        new_rank = GRADE_ORDER.get(new, 99)
        if new_rank > old_rank:
            regs.append((path, old, new))
    return regs


def migrate_from_json(db, json_path, engine='gt2'):
    """Import entries from the old JSON regression registry."""
    import json
    with open(json_path) as f:
        entries = json.load(f)

    batch = []
    for entry in entries:
        path = entry['path']
        grade = entry['min_grade']
        score = entry.get('min_score', 0)
        batch.append((path, engine, grade, score))

    updated, regs, imps = record_batch(db, batch)
    return updated
