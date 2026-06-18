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

**Scoreboard (2026-06-12):** Hubbard '85 ✓ uready (71/71, §9 closed) ·
Companion strains ✓ · FC Tel (Cyb II + Hawkeye) ✓ (§9 closed, fully
de-verbatim) · **FC standard ✓ uready** — criterion 3: freq_overrun
reachable-window (paired orderlist walk, most members 0 bytes);
criterion 4: WIDE BATCH 2528/2672 FULL (94.6%) at full songlength,
residue = 90 one-off buckets all signature-documented; criterion 6:
the 11-member exact feature-cover portfolio (35 dimensions) wired into
tools/regression.py (tier 1) + tools/fc_family_batch.py (tier 2);
criterion 5's ledger entry in docs/refactor_1_remaining.md (pre-
existing). Adrenalin subs 1-3: explicitly not attempted (documented
outlier).

**Scoreboard update (2026-06-18, `/uready-review` all-families):** the four
above remain ✓ uready (FC Tel de-verbatim RE-CONFIRMED against an agent
false-positive — the live verdict `verify_featuredriven` builds via
`build_via_asm_featuredriven`; `build_via_asm`+`_emit_verbatim_region` are
session-1 legacy/dead, flag for removal). **DMC (v4+v5) added — NOT yet
uready:** C1✓ (build orig-free), C2✓ (no engine-dispatch, parametric USF),
**C3 GAP** (`freq_overrun` capture not reachability-minimal — conservative
full-160 for high-melodic members; FC minimized in its uready-round-A),
**C4 GAP** (wide batch ~1041/1495 ~70%, residue censused but not fully
triaged — freq wave-stepping 119, filter 24, cia_multispeed ~39; no v5
regression portfolio derived), C5✓ (cross-engine review + convergence
ledger), C6✓ (RE_NOTES 11 rounds + [[project_dmc]]). Move-1 trigger still
MET (4 uready ≥ 2); DMC adds the richest divergence evidence (first family
with an INTRA-family fork, v4↔v5). Cross-engine: `freq_overrun` flipped
single-consumer→REUSED (FC std + DMC v5). The convergence ledger
([`docs/convergence_ledger.md`](../../docs/convergence_ledger.md), new this
session) is now the incremental pre-decider Move 1 consumes; this review is
its periodic maintainer.
