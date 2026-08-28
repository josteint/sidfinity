"""Reading a family-batch results jsonl — one place, one rule.

A batch results file is **APPEND-ONLY**. A batch resumes by appending, and a
`code_hash` invalidation re-runs members and appends their fresh rows beside
the old ones. So the same member path routinely appears SEVERAL TIMES in one
file, carrying different verdicts from different generations.

**The rule: dedupe by path, LAST ROW WINS.** Every consumer needs it, and the
`code_hash` gate is NOT a substitute — duplicates can all carry the current
hash (a plain resume adds no new hash), so filtering on the hash still leaves
several live rows for one member.

What reading naively costs, from real incidents:

- **corpus_sync** — FC's results carried BOTH a `full` and a non-full row for
  63 paths. Read naively, one member is simultaneously a write AND an orphan:
  its artifact is deleted and then rewritten, which only survives because
  orphan removal happens to run before the writes, and leaves a FULL member
  with NO artifact if its write then fails.
- **select_regression_portfolio** — a member that was `full` in an older
  generation and is now `partial` still enters the FULL pool and can be
  SELECTED into the tier-1 regression portfolio, where it fails forever. It
  also feature-extracts every re-run member twice and records an inflated
  `corpus_full` (the stored dmc_v4 portfolio says 5654 against a true 5252).
- **divergence_census** — counted superseded rows (10,802 "members" for a
  5,401-member family) and listed already-FULL members as partial cluster
  representatives, which reads as "this bug is still open".

Consumers that are safe WITHOUT this helper, so nobody "fixes" them into
churn: a resume gate that builds a `set()` of done paths (duplicates collapse,
and the code_hash filter is the real gate), and any loop whose last statement
is `d[path] = row` (last-wins by construction — but call this instead, so the
property is stated rather than incidental).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass(frozen=True)
class Store:
    """One family's authoritative batch-results file."""
    store: str          # id used by producers and consumers
    rel: str            # repo-relative path
    engine: str         # code_fingerprint key that stamps its rows
    id_key: str         # the member-path field: 'path' or 'sid'

    @property
    def path(self) -> str:
        return os.path.join(ROOT, self.rel)


# ---------------------------------------------------------------------------
# THE REGISTRY — which file holds a family's current verdicts.
#
# It exists because five independent consumer groups each hardcoded their own
# answer and drifted apart: the family batches (which WRITE), the mass-writers
# (which read to decide what to store AND WHAT TO DELETE), migrate_verdict_rows,
# select_regression_portfolio and derive_deps. By 2026-08-23 they disagreed in
# ways no gate could see:
#
#   * DMC v4's batch default OUT and its mass-writer both pointed at
#     `tmp/dmc_wide_results.jsonl` — the PRE-#85 working file (5,401 rows) —
#     while migrate and the portfolio used the current #85 file (5,445 rows).
#     The mass-writer DELETES the artifacts of members it does not see as
#     full, so it was deciding deletions from a superseded collection.
#   * DMC v5's mass-writer pointed at `tmp/dmc_v5_full_results.jsonl`, last
#     written 2026-06-29 — two months stale.
#   * migrate and the portfolio pointed at `dmc_v5_r2`, superseded by `r3`.
#
# This is the same disease as the frozen member lists that `pipelines/dmc/
# route.py` replaced: a fact about "what is current" copied into several
# places, where nothing can notice the copies diverging. One home, and the
# `id_key` rides along so consumers stop rediscovering that FC and MA name the
# member field `sid` while everyone else names it `path`.
#
# ⚠ A family's store is APPEND-ONLY and resumable, so pointing a producer at
# the right file matters as much as pointing a reader: a batch run with the
# wrong default appends fresh verdicts into a stale file nobody reads.
# ---------------------------------------------------------------------------
STORES: dict[str, Store] = {
    'dmc_v4':          Store('dmc_v4', 'tmp/dmc_f1_85_results.jsonl',
                             'dmc_v4', 'path'),
    'dmc_v4_family2':  Store('dmc_v4_family2', 'tmp/dmc_f2_85_results.jsonl',
                             'dmc_v4', 'path'),
    'dmc_v5':          Store('dmc_v5', 'tmp/dmc_v5_r3_results.jsonl',
                             'dmc_v5', 'path'),
    'fc_standard':     Store('fc_standard', 'tmp/fc_std_wide_results.jsonl',
                             'fc_standard', 'sid'),
    'music_assembler': Store('music_assembler', 'tmp/masm_wide_results.jsonl',
                             'music_assembler', 'sid'),
    'goattracker_v1':  Store('goattracker_v1', 'tmp/gt_v1_results.jsonl',
                             'goattracker_v1', 'path'),
    'basic_program':   Store('basic_program',
                             'tmp/basic_program_research/family_batch.jsonl',
                             'basic_program', 'path'),
    # v6 has NO composer yet (extract + player RE exist; see
    # pipelines/dmc/v6/RE_NOTES.md). The store exists anyway so its 16 members
    # COUNT — every coverage number is computed from results files, so a
    # family without one is invisible rather than 0% (they were the last
    # `no_store` bucket in `route.py --gaps`). Its batch records each member
    # `unsupported: no_composer` until the composer is built.
    'dmc_v6':          Store('dmc_v6', 'tmp/dmc_v6_results.jsonl',
                             'dmc_v6', 'path'),
}


def store(store_id: str) -> Store:
    try:
        return STORES[store_id]
    except KeyError:
        raise KeyError(f'unknown batch store {store_id!r}; add it to '
                       f'src/batch_results.STORES') from None


def store_path(store_id: str) -> str:
    """Absolute path to a family's current results file."""
    return store(store_id).path


def stores_for_engine(engine: str) -> list:
    """Every store whose rows are stamped with `engine`'s fingerprint.

    One engine can own several (dmc_v4 batches its canonical and family-2
    variants into separate files).
    """
    return [s for s in STORES.values() if s.engine == engine]


def load_store(store_id: str) -> dict:
    """`load_latest` for a registered store, with its own `id_key`."""
    s = store(store_id)
    return load_latest(s.path, s.id_key)


def load_latest(results_path: str, path_key: str = 'path') -> dict:
    """`{path: row}` for a batch results jsonl, LAST ROW WINS per path.

    Blank lines are skipped. Rows without `path_key` are skipped rather than
    raising — a partially-flushed final line from a killed batch should not
    take down a read-only analysis tool.
    """
    latest: dict = {}
    with open(results_path) as f:
        for line in f:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            key = row.get(path_key)
            if key is not None:
                latest[key] = row
    return latest


def load_latest_rows(results_path: str, path_key: str = 'path') -> list:
    """The deduped rows as a list (order: first appearance of each path)."""
    return list(load_latest(results_path, path_key).values())
