"""corpus_sync.py — plan a mass-write as a SYNC of the on-disk corpus to a
batch results file.

A mass-writer's job is not "write the FULL members"; it is "make what is
STORED be exactly what was VERIFIED". Those differ in three ways, each of
which has bitten this project (ledger C20), and each of which this module
closes once so every family gets it:

1. STALE VERDICT — a row whose `code_hash` no longer matches the engine's
   current dependency set describes code that no longer exists. Skip it and
   tell the caller to re-run the batch. (This layer already existed.)

2. WRONG BUILD PATH — when a batch dispatches over several build paths
   (multi-SID / compilation / single player), a writer that RE-DERIVES the
   dispatch can pick a different one, and produces a well-formed,
   code_hash-blessed, WRONG artifact that no other gate can see: DMC stored
   every multi-SID member as a single-chip extraction of a multi-chip tune.
   Re-derivation also cannot match a fallback triggered by a VERIFY-time
   exception, which no writer can observe. So the batch RECORDS `build_path`
   and the writer REPLAYS it; a row missing it is refused, never guessed.
   A family with exactly one build path may pass `require_build_path=False`
   — but the moment it grows a second, it must record one.

3. ORPHANED ARTIFACT — a member that is not FULL must have NO stored
   artifact. Nothing else removes one: a mass-write only ever revisits FULL
   members, so an artifact written when older code judged a member FULL
   survives every subsequent run, and `usf_corpus_check` cannot see it
   because the file parses perfectly well. 56 such files had accumulated in
   DMC family 1.

The complementary check — that the stored artifact actually reproduces its
verdict — cannot live here because each family's verify signature differs;
each mass-writer audits a stratified sample itself, re-verifying FROM DISK.
That is the only check that exercises writer and verifier against each
other.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

# What a member's rebuild stores next to the HVSC original. Every family
# writes exactly these two (plus digi sidecars, which ride the .usf).
ARTIFACT_SUFFIXES = ('.usf', '.sidfinity.sid')


@dataclass
class SyncPlan:
    write: list = field(default_factory=list)    # full rows to rebuild
    orphans: list = field(default_factory=list)  # artifact paths to delete
    stale: int = 0                               # rows from superseded code
    nopath: int = 0                              # FULL rows with no build_path

    def report(self, batch_tool: str) -> list:
        """Human-readable warnings, most alarming first."""
        out = [f'{len(self.write)} current-code FULL members to write']
        if self.stale:
            out.append(f'  WARNING: skipped {self.stale} FULL rows with '
                       f'stale/absent code_hash (verdict predates current '
                       f'code). Re-run {batch_tool} to refresh them.')
        if self.nopath:
            out.append(f'  WARNING: skipped {self.nopath} FULL rows with no '
                       f'recorded build_path (batch predates it). Re-run '
                       f'{batch_tool}.')
        if self.orphans:
            out.append(f'  SYNC: deleting {len(self.orphans)} orphaned '
                       f'artifacts of members that are NOT full')
        return out


def plan(results_path: str, engine: str, hvsc_root: str,
         require_build_path: bool = False, path_key: str = 'path') -> SyncPlan:
    """Build the sync plan for `engine` from a batch results jsonl.

    `engine` names the `code_fingerprint` dependency set. Only rows whose
    code_hash matches it are authoritative — for writing AND for deleting,
    so a superseded row can never delete a live artifact. `path_key` is the
    row field holding the HVSC-relative path (FC's batch calls it 'sid').
    """
    from src.code_fingerprint import code_fingerprint
    code_hash = code_fingerprint(engine)
    p = SyncPlan()
    with open(results_path) as f:
        for line in f:
            if not line.strip():
                continue
            d = json.loads(line)
            if d.get('code_hash') != code_hash:
                p.stale += 1
                continue
            base = os.path.splitext(os.path.join(hvsc_root, d[path_key]))[0]
            if d.get('status') == 'full':
                if require_build_path and not d.get('build_path'):
                    p.nopath += 1
                    continue
                p.write.append(d)
            else:
                p.orphans += [base + s for s in ARTIFACT_SUFFIXES
                              if os.path.exists(base + s)]
    return p


def remove_orphans(plan_: SyncPlan) -> int:
    for path in plan_.orphans:
        os.unlink(path)
    return len(plan_.orphans)
