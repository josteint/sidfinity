"""Digi-Organizer standalone batch: SID → USF → SID, Mode-2 cycle-strict.

Rows append to tmp/digi_organizer_results.jsonl (register in
src/batch_results.STORES). Verify window = songlength × 1.1 (ratified;
no cap — C20 eighth layer).
"""
from __future__ import annotations

import glob
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src import sid_db  # noqa: E402
from src.tslog import ts, phase  # noqa: E402
from src import songlengths as SL  # noqa: E402
from src.code_fingerprint import code_fingerprint  # noqa: E402
from pipelines.digi_organizer.extract import DigiOrganizerUnsupported  # noqa: E402
from pipelines.digi_organizer.to_usf import write_usf  # noqa: E402
from pipelines.digi_organizer.composer_asm import (  # noqa: E402
    build_sid, DigiComposeError)
from pipelines.hubbard.verify_cycle import (  # noqa: E402
    writelog_capture, compare_strict)

RESULTS = 'tmp/digi_organizer_results.jsonl'
WORK = 'tmp/digiorg'


def members():
    rows = sid_db.query(
        "SELECT path, engines FROM sids WHERE engines LIKE '%Digi-Organizer%'")
    return [p for p, e in rows if e == 'Digi-Organizer']


_DB = None


def _worker_init():
    """Load the songlength database into a module global.

    `tools/derive_deps.py` calls this before running one member in a clean
    interpreter; without it `run_member` would be handed no database, fall
    back to the 120 s default window and derive a closure that never touched
    `src.songlengths` — the silently-too-narrow dependency set that tool
    exists to prevent."""
    global _DB
    if _DB is None:
        _DB = SL.load_database(glob.glob('hvsc85/DOCUMENTS/Songlengths.md5')[0])
    return _DB


def run_member(rel: str, db=None) -> dict:
    if db is None:
        db = _worker_init()
    row = {'path': rel, 'ts': time.strftime('%Y-%m-%dT%H:%M:%S')}
    try:
        base = os.path.splitext(os.path.basename(rel))[0]
        usf = write_usf('hvsc85/' + rel, WORK)
        reb = build_sid(usf, os.path.join(WORK, base + '.sidfinity.sid'))
        try:
            dur = SL.get_durations('hvsc85/' + rel, db)[0] * 1.1
        except Exception:
            dur = 120.0
        a = writelog_capture('hvsc85/' + rel, 0, dur, force_rsid=True)
        b = writelog_capture(reb, 0, dur, force_rsid=True)
        r = compare_strict(a, b)
        na, nb = sum(map(len, a)), sum(map(len, b))
        full = r['first_diff'] is None and na == nb
        row.update(status='full' if full else 'partial',
                   build_path='standalone', dur=round(dur, 1),
                   frames=r['frames'], match=r['match'],
                   len_a=na, len_b=nb,
                   first_diff_frame=(None if r['first_diff'] is None
                                     else r['first_diff'][0]))
    except (DigiOrganizerUnsupported, DigiComposeError) as e:
        row.update(status='unsupported', reason=str(e)[:160])
    except Exception as e:
        row.update(status='error', reason=f'{type(e).__name__}: {e}'[:160])
    return row


def main():
    os.makedirs(WORK, exist_ok=True)
    db = SL.load_database(glob.glob('hvsc85/DOCUMENTS/Songlengths.md5')[0])
    ch = code_fingerprint('digi_organizer')
    mem = members()
    # RESUME GATE: a row counts as done only if its verdict was earned by
    # the CURRENT code (C20). Keying on the path alone silently reuses
    # verdicts across a composer change — this batch reported a tidy
    # "0 of 39 members" and TOTALS from stale rows right after a fold,
    # and the mass-write (which DOES check the hash) then refused all 39.
    done = set()
    if os.path.exists(RESULTS):
        with open(RESULTS) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if ch and r.get('code_hash') != ch:
                        continue
                    done.add(r['path'])
                except Exception:
                    pass
    todo = [m for m in mem if m not in done]
    phase_name = f'digi_organizer batch: {len(todo)} of {len(mem)} members'
    with phase(phase_name):
        with open(RESULTS, 'a') as out:
            for i, rel in enumerate(todo):
                ts(f'[{i + 1}/{len(todo)}] {rel}')
                row = run_member(rel, db)
                if ch:
                    row['code_hash'] = ch
                out.write(json.dumps(row) + '\n')
                out.flush()
                ts(f'  -> {row["status"]}'
                   + (f' ({row.get("reason", "")[:60]})'
                      if row['status'] != 'full' else ''))
    import collections
    c = collections.Counter()
    with open(RESULTS) as f:
        latest = {}
        for line in f:
            r = json.loads(line)
            latest[r['path']] = r
    for r in latest.values():
        c[r['status']] += 1
    ts(f'TOTALS {dict(c)}')


if __name__ == '__main__':
    main()
