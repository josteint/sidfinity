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
