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

4. INCONSISTENT PAIR — the stored `.usf` does not REBUILD the stored `.sid`.
   Writer and verifier can take the same build path and still disagree, when
   the build consumes a parameter that is not IN the `.usf`: DMC's batch
   write-stream retry set `hold_gateoff` on the PARSED object and the writer
   re-injected it post-parse, so the verdict was right, the `.sid` was right,
   and the `.usf` beside them specified a different build. Every other gate
   passes — the batch is green, the code_hash matches, the file parses, it is
   byte-identical to a fresh extract, and re-verifying the stored `.sid`
   succeeds, because the `.sid` really is correct. The inconsistency lives
   strictly BETWEEN the two stored files. `audit_rebuild` below is the
   detector, and it is general: it catches ANY build input that leaks outside
   the USF (the Principle §8 invariant, corpus-side).

The remaining check — that the stored artifact reproduces its VERDICT — still
cannot live here, because each family's verify signature differs; each
mass-writer audits a stratified sample itself, re-verifying FROM DISK. That
is the only check that exercises writer and verifier against each other.
(`audit_rebuild` needs no verify signature — only the family's builder — so
it belongs here, and `sample_by_build_path` lets a family feed both audits
the same stratified sample.)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from batch_results import load_latest

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
         require_build_path: bool = False, path_key: str = 'path',
         out_of_scope: tuple = ()) -> SyncPlan:
    """Build the sync plan for `engine` from a batch results jsonl.

    `engine` names the `code_fingerprint` dependency set. Only rows whose
    code_hash matches it are authoritative — for writing AND for deleting,
    so a superseded row can never delete a live artifact. `path_key` is the
    row field holding the HVSC-relative path (FC's batch calls it 'sid').

    `out_of_scope` lists statuses meaning "this member is NOT MINE" — the
    batch swept it but its extractor refused it, so another pipeline owns it.
    Such rows are skipped ENTIRELY: neither written nor orphaned. A batch may
    only delete artifacts of members it OWNS. FC's batch sweeps every HVSC
    FutureComposer SID, but `fc_standard_config` refuses the Tel-variant
    canaries ('flagged'), which are built by their own configs — without this
    they are read as not-full and their artifacts DELETED, taking out
    Cybernoid_II / Hawkeye / Adrenalin and breaking the regression. Contrast
    a status like DMC's 'unsupported', which means "this IS my member and I
    cannot build it" — that one IS an orphan.
    """
    from src.code_fingerprint import code_fingerprint
    code_hash = code_fingerprint(engine)
    p = SyncPlan()
    # DEDUPE BY PATH, LAST ROW WINS — the shared rule for every consumer of an
    # append-only batch jsonl; rationale + the incidents that motivate it live
    # in src/batch_results. NOT the stale-verdict layer: duplicates can all
    # carry the current code_hash, so the hash gate below is not a substitute.
    latest = load_latest(results_path, path_key)
    for d in latest.values():
        if d.get('status') in out_of_scope:
            continue                      # not this batch's member — hands off
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


def sample_by_build_path(written: list, n: int) -> list:
    """Pick <=`n` of `written` (a list of `(rel, build_path)`), spread evenly
    over the distinct build paths.

    Stratifying by build path is what makes a small sample worth running: the
    failure modes this module exists to catch are path-specific, so a sample
    that happens to miss the one multi-SID member tells you nothing about the
    layer that broke there. A family with one build path may pass any constant
    (e.g. `''`) as the path.
    """
    by_path = {}
    for rel, bp in written:
        by_path.setdefault(bp, []).append(rel)
    per = max(1, n // max(1, len(by_path)))
    out = []
    for bp, rels in sorted(by_path.items(), key=lambda kv: str(kv[0])):
        step = max(1, len(rels) // per)
        out += [(r, bp) for r in rels[::step][:per]]
    return out


def audit_rebuild(sample: list, hvsc_root: str, build) -> list:
    """The stored `.usf` must REBUILD the stored `.sid`, byte for byte.

    `build(rel, usf_path) -> bytes` is the family's builder, pointed at the
    STORED `.usf` (not at a fresh extract — regenerating would test the
    extractor, which is a different question). Returns a list of failure
    descriptions; empty means the pair is self-consistent.

    See item 4 in the module docstring for why nothing else detects this. Note
    the direction of the check: it does NOT ask whether the artifacts are
    *correct* — the caller's verify audit does that — only whether the two
    stored files agree on what the rebuild IS. A member can pass this and be
    wrong, but it cannot fail this and have a `.usf` worth publishing.
    """
    fails = []
    for rel, bp in sample:
        base = os.path.splitext(os.path.join(hvsc_root, rel))[0]
        try:
            if build(rel, base + '.usf') != open(base + '.sidfinity.sid',
                                                 'rb').read():
                fails.append(f'[{bp}] {rel} — the stored .usf does not '
                             f'rebuild the stored .sid')
        except Exception as e:
            fails.append(f'[{bp}] {rel} — .usf rebuild raised '
                         f'{type(e).__name__}: {e}'[:160])
    return fails
