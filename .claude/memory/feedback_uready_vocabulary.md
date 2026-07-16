---
name: feedback_uready_vocabulary
description: "VOCABULARY: 'uready' (unification-ready) — the checkable maturity gate for leaving an engine family and for the future composer-skeleton unification (Move 1). Six criteria. Use it: 'is this engine uready?'"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: f210d7ad-650b-4049-9ac8-2670d5a54726
---

**uready** (adj., unification-ready) — project vocabulary coined by the
user 2026-06-11. An engine family is *uready* when its migration follows
the principles well enough that (a) we can leave it and move to another
engine, and (b) the composer-skeleton unification
([`docs/refactor_1_remaining.md`](../../docs/refactor_1_remaining.md)
Move 1, a.k.a. the grand-unification/tokenization stage) doesn't have to
struggle more than necessary because of it.

**Why:** the unification is the project's planned future re-foundation;
every family migrated before it either feeds it clean evidence or buries
it in surprises. "uready" makes the gate one question instead of a
paragraph.

**How to apply — the six criteria (all checkable):**
1. **Orig-free builds (§9):** a model-generated USF builds a verified SID
   with no original-binary reads beyond synthesized metadata.
2. **No escape hatches (§7/§8):** no opaque/engine-positional USF fields
   except documented, minimized by-reference captures; no engine-identity
   dispatch in the composer; per-family knobs behavior-named + derivable
   from the SID itself.
3. **Factored & reversible USF** (the user's grand-unification directive,
   recorded in [[project_fc_principled_composer]]): techniques explicit,
   no lossy folds; bytes-shaped blocks justified and reachability-minimal.
4. **Representative verification:** a variant-spread sample FULL
   (play-stream + trichotomy audio✓), variant axes censused +
   factory-probed, wide-batch pass-rate known, failure buckets triaged or
   documented.
5. **Feature-dimension accounting:** the family's behaviors mapped onto
   existing USF/composer dimensions where they coincide (cluster-by-
   behavior receipts) and new dimensions named — the evidence Move 1
   consumes.
6. **Documented residue:** latents/quirks/accepted losses in RE_NOTES +
   memory; canaries wired into tools/regression.py.

**Status (pointer, not a scoreboard — trimmed 2026-07-16):** per-family
uready state is STATUS knowledge and lives in each family's
`project_<engine>` memory + the latest `/uready-review` output, NOT here
(this file kept accumulating per-review scoreboards that drifted stale —
the exact failure mode [[feedback_knowledge_placement]] names). Durable
facts only: **four families are uready** (Hubbard '85 · Companion strains ·
FC Tel · FC standard), so the Move-1 trigger (≥2 uready) is MET; **DMC is
not yet uready** — its remaining blockers are process (C4 batch freshness,
C6 RE_NOTES repo-residence), not representation; see [[project_dmc]] for
the current counts. The dual_freq_generator leak audit and its resolution
are recorded in ledger C7. `/uready-review` is this gate's periodic
maintainer — its findings go to the family files and the ledger, not into
this memory.
