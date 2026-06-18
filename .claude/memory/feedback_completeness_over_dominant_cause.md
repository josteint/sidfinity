---
name: feedback_completeness_over_dominant_cause
description: "The user wants COMPLETE coverage (all DMC SIDs to FULL), not dominant-cause/ROI triage. Clustering is a tool to batch related fixes, not an objective — work through every failure mode, not just the biggest."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
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

Related: [[feedback_reanchor_at_decisions]] (still re-anchor on correctness), the
uready gate [[feedback_uready_vocabulary]] (completeness feeds criterion 4/6).
