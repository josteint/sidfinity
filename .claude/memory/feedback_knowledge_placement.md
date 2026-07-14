---
name: feedback_knowledge_placement
description: "Where every piece of knowledge LIVES: 6 kinds → 6 homes, one home per fact (point, don't copy), the engines×members scaling law, ledger-as-index, and the no-retroactive-distill rule. Ratified 2026-07-14."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4160e01b-ee92-451b-8bf7-26ed3cacb8e7
---

The project's knowledge architecture, ratified with the user 2026-07-14
(the session that created `docs/the_core_tenet.md` / `the_principle.md` /
`the_trichotomy.md` and wired them as CLAUDE.md session-start imports).

**The placement taxonomy — 6 kinds, 6 homes.** Every fact has exactly ONE
kind and therefore ONE home; everywhere else POINTS, never copies:

| Kind | What it is | Home |
|---|---|---|
| ORACLE | the definition of "correct" | the verdict CODE (`pipelines/hubbard/verify_cycle.py`) — docs point at it, never paraphrase it |
| LAW | a standard to judge against | canon docs in `docs/` (The Core Tenet / The Principle / The Trichotomy), imported verbatim every session |
| TECHNIQUE | a solution to a recurring engine problem | `docs/the_convergence_ledger.md` |
| DISCIPLINE | how I should work / how I fail | `feedback_*` memories |
| STATUS | one engine's state, occurrences, round history | `project_<engine>.md` + `pipelines/<engine>/RE_NOTES.md` |
| OPERATION | how to run the repo | CLAUDE.md |

Placement test (first yes wins): correct-definition→code; standard→canon;
recurring-solution→ledger; how-I-behave→memory; one-engine-state→
project_<engine>; repo-convention→CLAUDE.md.

**Why:** "one home, point don't copy" IS the user's "no summaries in
context" rule — a summary is a copy that drifts. A memory may carry only
what the always-loaded canon does NOT.

**The scaling law (hundreds of engines are coming):** nothing that grows
with engines×members may live in a shared or always-loaded container. Each
shared container is bounded by a SATURATING quantity — laws: a handful;
ledger: problem-CLASSES (engine #200 CONSULTS C6, it doesn't mint C32);
feedback memories: failure-modes; CLAUDE.md: conventions. Per-engine detail
lives in per-engine files loaded ONE at a time; the roster is queryable
data (`hvsc84.parquet`), never prose.

**The ledger loads FULLY at session start (user decision 2026-07-14,
superseding an earlier index-only carve-out).** Rationale: the documented
weak link is the consult-BEFORE-solving step — an index only works if I
recognize my problem as a known class, and that recognition is exactly
what fails mid-chase (you can't look up what you don't recognize). Full
text in context makes the match passive association. The ledger saturates
by problem-CLASS (31 entries after the largest family), so this scales;
if it ever outgrows sanity, the header's escape hatch (migrate to a
queryable store) applies — revisit then, not preemptively. Entry-content
placement rule (member names / rounds / +N FULL / commit hashes →
`project_<engine>`, link from the entry) is written at the point of use:
the ledger's "How to use" RECORD step. See [[feedback_convergence_ledger]].

**How to apply — the two standing prohibitions:**
- **Never retroactively distill an existing ledger entry or canon doc.**
  Distillation of technique is lossy by construction — a 2026-07-14 trial
  distillation of ledger C11 provably dropped a failed-alternative warning
  ("pre-chain variant RAISED wave_marker_chain = 13 false rejects").
  Relocate-by-kind (lifting verified-duplicated STATUS) is lossless and
  allowed; rewording technique "to its essence" is not. If an entry is
  hard to navigate, ADD a map (C11 has one), don't delete lines.
- **Never write a prose re-definition of the oracle.** A rejected
  CONSTITUTION.md draft reintroduced Trap A ("per-frame" phrasing) while
  summarizing the verdict; the fix is to route to the code.

Related: [[feedback_reanchor_at_decisions]], [[feedback_meta_process]].
