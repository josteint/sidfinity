---
name: feedback_completeness_over_dominant_cause
description: "The user wants COMPLETENESS, not dominant-cause/ROI triage — for coverage (all DMC SIDs to FULL) AND for representation quality. Clustering is a tool to batch related fixes, not an objective; never argue against work by counting how few members it touches."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
  modified: 2026-08-07T17:18:45.825Z
---

The user's north star for DMC (and the catalogue generally) is **succeed with
ALL the SIDs** — drive every member to FULL (write-log exact). They explicitly
said discovering "dominant causes" is NOT important to them.

**Why:** the project goal is the whole HVSC catalogue translated to USF. Picking
the biggest cluster each round (the divergence_census / leverage-ranking loop)
makes visible progress but leaves a permanent long tail — and the long tail IS
the goal too. Constant ROI-hedging ("is this worth it / the highest lever /
should we defer") reads as reluctance and is the wrong frame.

**How to apply:**
- Use census/clustering ONLY to ORGANIZE — batch members that share a bug so one
  fix recovers many. Don't present "which cluster is biggest" as the deliverable;
  the deliverable is FULL members.
- When a cluster is heterogeneous (e.g. the V5 freq cluster = timing-shift +
  value-divergence sub-bugs), fix ALL the sub-bugs in turn, not just one. Keep
  going until the cluster is drained.
- Work through every failure mode — partials, player_code_mismatch, errors — not
  just the top bucket. The residue should shrink to only genuinely-unsupportable
  members, documented via tools/excluded_sids.json (e.g. aperiodic engines).
- Drop the "honest scope, maybe defer, is it worth it" hedging on DMC coverage
  work. Commit to driving it to completeness. Honest scope is still fine for
  flagging genuinely-huge or genuinely-impossible work — not for ordinary bugs.

**EXTENDED 2026-08-07 (user correction, repeat offence): the rule is NOT
coverage-only — it binds REPRESENTATION-QUALITY work too, and the banned move
is specifically the SMALL-N ARGUMENT.** During the B4 onset investigation I
repeatedly qualified a fix with "the payoff is negligible — 36 files out of
12,064" / "almost nothing in training-data terms". The user: *"you keep nagging
about how something only affecting a few songs compared to all songs is so
small. please stop that."* Note this memory ALREADY said to drop the hedging;
it was read as coverage-scoped and so not applied to a schema/representation
question. It is not scoped that way.

- **Never weigh a fix by carrier count.** "Only N members" is not an argument
  against doing something, at any N — including N=1. Report the carrier count
  as a FACT (C7 requires it: measure, don't guess) and then stop; do not
  editorialize it into a cost/benefit verdict.
- The correct axis is whether the representation states something TRUE — an
  unverified claim in the data (e.g. a read marked "this value moves" that
  nobody measured moving) is worth fixing regardless of how many files carry it.
- Present options by what they'd COST and what they'd MAKE TRUE, and give a
  recommendation. Let the user weigh significance; that call is theirs.

Related: [[feedback_reanchor_at_decisions]] (still re-anchor on correctness), the
uready gate [[feedback_uready_vocabulary]] (completeness feeds criterion 4/6).
