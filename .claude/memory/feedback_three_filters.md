---
name: feedback_three_filters
description: "Every new technique must pass THREE filters — CORE TENET (permissive), USF PRINCIPLES (schema-restrictive), and Move-1 unification-readiness (composer-restrictive); the third is the test to remember going forward."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: b632f6d3-9d96-4623-9ee1-b5354ba2f9a3
---

Every time we introduce ANYTHING new to solve a writelog-equality problem,
run it through THREE filters — not one:

1. **CORE TENET (permissive filter):** does it achieve `$D400-$D418`
   writelog equality? Opens the door to ANY runtime technique — including
   reproducing techniques from the original SID. It grants freedom; it
   forbids nothing. (See docs/the_core_tenet.md; it is NOT "don't mirror the
   original" — it's "you may use any code.")

2. **USF PRINCIPLES (restrictive filter on the SCHEMA):** does the USF stay
   parametric/musical and ML-optimal? Constrains only what the USF *carries*
   (no engine-positional artifacts, no content-by-reference byte blobs).
   Mechanism goes in the COMPOSER, never the USF. See
   docs/the_principle.md.

3. **MOVE-1 UNIFICATION-READINESS (restrictive filter on the COMPOSER):**
   **the one the user asked to remember going forward.** Ask: *"if 50 uready
   engines each needed a slightly-different version of this, would they still
   unify in Move-1?"* They unify IFF the technique is introduced as
   **`shared_mechanism(per_engine_config)`** — one mechanism + per-engine
   DATA — never 50 ad-hoc code variants. This is exactly the convergence-
   ledger reflex ([[feedback_convergence_ledger]]): before solving, find the
   canonical parametric form; after, record it so engine #2 reuses the
   mechanism with just its own data.

**Why:** the CORE TENET alone (filter 1) would let you write a correct but
un-unifiable mechanism; the user wants every new technique to ALSO be born in
its unifiable shape, so Move-1 (the cross-engine composer-skeleton unification)
isn't a 50-variant untangling job later.

**How to apply:** worked example — off-table reads (freqlo/freqhi[idx>95]
sonify live engine state). Filter-3 rejected the elegant-for-one **layout-
mirror** (couples the composer's MEMORY LAYOUT to each engine) in favour of the
**parametric read-redirect**: uniform composer state layout (shared) + a
per-engine `idx → state-variable` map (config). "Elegant for one engine ≠
unifiable for fifty." See [[project_dmc]] off-table section, [[feedback_uready_vocabulary]].
