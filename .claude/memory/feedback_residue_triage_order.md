---
name: feedback_residue_triage_order
description: "Triaging a large wide-family residue — fully census first, then attack in DEPENDENCY order (measure→verdict→unblock-builds→effects→accept-limit-last), never biggest-bucket-first"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
---

When a wide engine family has a large non-FULL residue (hundreds of members),
do NOT attack the biggest bucket first. **Fully census, then attack in
dependency order** — because each earlier class RE-BUCKETS the residue, so the
"biggest bucket" you'd have chased is often a measurement artifact that a
cheaper upstream fix dissolves.

**Why:** a verdict/measurement fix can silently flip ~150 "partials" to FULL
with zero composer work, and it changes what every downstream bucket count
*means*. Doing per-effect composer work before that runs is wasted effort on
members that were never actually broken.

**How to apply — the order (foundation → per-SID specifics):**

0. **MEASURE / fully re-localize first.** Before any fix, drive every non-FULL
   member to a concrete root-cause bucket — no opaque "uncategorized" residue.
   The trap that motivated this: a partial whose `first_play_diff` is None looks
   uncategorized, but it's actually length/CIA or init-state — distinguishable
   from `state_match`+`close`+`len_post_a/b` WITHOUT a re-verify, once the batch
   records them (folded into `tools/dmc_family_batch.py`). See
   [[reference_divergence_census]] for the clustering tool.
1. **FIX THE VERDICT.** Measurement bugs first (CIA-aware per-IRQ capture for
   multispeed; tail `close_tol`). Converts false-partials → FULL at zero
   composer cost AND re-buckets everything below it. Biggest single lever,
   usually. (CORE TENET still holds — the verdict is always the writelog; a
   "verdict fix" makes the writelog comparison *correct*, it never relaxes it.)
2. **UNBLOCK BUILDS.** Detection / extract fixes that let a member BUILD at all
   (dataflow operand locator, JT-less base locator). A member that can't build
   can't be a FULL no matter how good the composer is.
3. **FIX EFFECTS.** The actual per-effect composer/data divergences — the
   expensive per-SID work. Only now, on accurate counts.
4. **ACCEPT THE ARCHITECTURAL LIMIT LAST.** Genuinely-dynamic / unrepresentable
   residue is accepted only after everything cheaper above is exhausted — never
   used as an early excuse to stop (see [[feedback_completeness_over_dominant_cause]]:
   the user wants ALL members to FULL, not ROI triage).

The tell of drift: "the biggest bucket is X, so fix X" *before* steps 0-1 have
run. Census the dependency, not the headcount. Related:
[[feedback_bug_investigation]] (one member, first wrong frame) is the per-member
method; this is the across-residue method that decides WHICH member.
