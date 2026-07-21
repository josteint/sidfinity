"""
songlengths.py - Parse HVSC Songlengths.md5 database.

Format of Songlengths.md5:
  ; /MUSICIANS/H/Hubbard_Rob/Commando.sid
  ab3a108b0be65e521a33b2b4e474624b=3:23 0:41 1:02

Lines starting with ; are path comments. The next non-blank line is:
  md5hash=m:ss m:ss ...
where each duration corresponds to a subtune (1-indexed in SID files).
Durations can also have milliseconds: m:ss.mmm
"""

import hashlib
import os
import sys


# Parsing Songlengths.md5 walks ~60,000 lines and ~87,000 duration fields —
# about 0.5s. Both the extract and the verify paths call it once PER MEMBER, so
# a batch over thousands of members re-parsed the same unchanged file thousands
# of times (~40 min of CPU across a full DMC v4 batch, and 0.5s on every
# regression task). Cache it.
#
# Keyed on (path, mtime, size) so an updated HVSC drop is re-read rather than
# served stale. The cached dict is SHARED, not copied: it is ~60k entries and
# the only consumer (get_durations) just reads. Treat it as read-only.
#
# Two callers grew their own ad-hoc `_SL_DB` caches around this function
# (dmc/v4/extract/engine_model.py, dmc/v5/extract/to_usf.py); they still work
# and now simply hit this cache instead. Four other call sites had none.
_DB_CACHE: dict = {}


def load_database(path):
    """Parse Songlengths.md5 into a dict keyed by MD5 hash.

    Returns: {md5_hex: [duration_seconds, ...], ...} — cached, read-only.
    """
    try:
        st = os.stat(path)
        key = (os.path.abspath(path), st.st_mtime_ns, st.st_size)
    except OSError:
        key = None
    if key is not None:
        cached = _DB_CACHE.get(key)
        if cached is not None:
            return cached

    db = {}
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('[') or line.startswith(';'):
                continue
            if '=' not in line:
                continue
            md5, durations_str = line.split('=', 1)
            md5 = md5.strip().lower()
            durations = []
            for d in durations_str.strip().split():
                durations.append(_parse_duration(d))
            db[md5] = durations
    if key is not None:
        _DB_CACHE[key] = db
    return db


def _parse_duration(s):
    """Parse 'm:ss' or 'm:ss.mmm' into seconds as float."""
    if '.' in s:
        time_part, ms_part = s.rsplit('.', 1)
        frac = int(ms_part) / (10 ** len(ms_part))
    else:
        time_part = s
        frac = 0.0
    parts = time_part.split(':')
    minutes = int(parts[0])
    seconds = int(parts[1])
    return minutes * 60 + seconds + frac


def compute_md5(sid_path):
    """Compute MD5 of a .sid file (full file hash)."""
    with open(sid_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def get_durations(sid_path, db):
    """Look up durations for a .sid file.

    Returns: list of durations in seconds, one per subtune.
    Raises KeyError if not found in database.
    """
    md5 = compute_md5(sid_path)
    if md5 not in db:
        raise KeyError(f"MD5 {md5} not found in songlengths database: {sid_path}")
    return db[md5]


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 songlengths.py <Songlengths.md5> <file.sid> [subtune]")
        sys.exit(1)

    db = load_database(sys.argv[1])
    sid_path = sys.argv[2]
    durations = get_durations(sid_path, db)

    if len(sys.argv) > 3:
        subtune = int(sys.argv[3])
        print(f"Subtune {subtune}: {durations[subtune - 1]:.1f}s")
    else:
        for i, d in enumerate(durations, 1):
            print(f"Subtune {i}: {d:.1f}s")
