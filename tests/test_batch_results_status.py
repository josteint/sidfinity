"""`load_latest` must normalise `status` — the one boundary every reader of a
verdict store passes through.

WHY THIS EXISTS (backlog item 36, measured 2026-08-31). basic_program's batch
stamped `'FULL'` for its pass status and lowercase for every failure, while
every shared tool compares `status == 'full'` literally. Consequences, all
real:

  * `batch_diff` read 489 FULL members as full=0, so for that family it could
    never report a gain or a regression — and CLAUDE.md mandates it at every
    closeout as THE regression detector (ledger C20's sixth layer, which
    exists precisely because net counts masked four real regressions for a
    week).
  * `corpus_sync` decides what is FULL the same way and DELETES the stored
    artifacts of everything else as orphans. basic_program does not use
    corpus_sync yet, so this was armed rather than firing: wiring the family
    to it would have deleted all 489 stored `.usf`.
  * `divergence_census` would have labelled every row a detect-reject.

The fix normalises at the boundary rather than at each call site, so rows
ALREADY ON DISK in the old form are correct too. This test is the mechanical
guard on that — a declared invariant with no check eventually drifts.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.batch_results import load_latest          # noqa: E402


def _write(tmp_path, rows):
    p = tmp_path / 'results.jsonl'
    p.write_text('\n'.join(json.dumps(r) for r in rows) + '\n')
    return str(p)


def test_status_is_lowercased(tmp_path):
    p = _write(tmp_path, [{'path': 'a.sid', 'status': 'FULL'},
                          {'path': 'b.sid', 'status': 'Partial'},
                          {'path': 'c.sid', 'status': 'full'}])
    got = load_latest(p)
    assert [got[k]['status'] for k in ('a.sid', 'b.sid', 'c.sid')] == \
        ['full', 'partial', 'full']


def test_non_string_status_survives(tmp_path):
    """A row with no status, or a non-string one, must not raise — a
    partially-written row should never take down a read-only tool."""
    p = _write(tmp_path, [{'path': 'a.sid'},
                          {'path': 'b.sid', 'status': None},
                          {'path': 'c.sid', 'status': 3}])
    got = load_latest(p)
    assert got['a.sid'].get('status') is None
    assert got['b.sid']['status'] is None
    assert got['c.sid']['status'] == 3


def test_last_row_wins_is_unchanged(tmp_path):
    """The module's other invariant: the file is append-only, so one member
    routinely has several rows and the LAST one is the verdict."""
    p = _write(tmp_path, [{'path': 'a.sid', 'status': 'partial'},
                          {'path': 'a.sid', 'status': 'FULL'}])
    assert load_latest(p)['a.sid']['status'] == 'full'


def test_the_real_basic_program_store_reads_as_full():
    """The regression this test was written for, on the actual store."""
    p = os.path.join(ROOT, 'tmp', 'basic_program_research',
                     'family_batch.jsonl')
    if not os.path.exists(p):
        import pytest
        pytest.skip('basic_program store not present')
    rows = load_latest(p)
    n_full = sum(1 for r in rows.values() if r.get('status') == 'full')
    assert n_full > 0, ('basic_program store reads as zero FULL members — '
                        'the item-36 regression is back')
