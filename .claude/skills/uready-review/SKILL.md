---
name: uready-review
description: Audit migrated engine families for "uready" (unification-readiness, the 6-criteria gate) AND do the cross-engine feature-reuse review that docs/the_move-1_plan.md Move 1 depends on. Read-only analysis — surfaces decisions, never changes representations. Run periodically to keep the composer-skeleton unification honest.
argument-hint: "[engine-family | all]  (default: all migrated families)"
user-invocable: true
allowed-tools: Agent Bash Read Grep Glob Edit Write
effort: high
---

# uready + cross-engine reuse review — $ARGUMENTS

You are running the **periodic unification-readiness audit**. Its job is the
safeguard `docs/the_move-1_plan.md` (Move 1) relies on but that nothing
exercises automatically: keep the per-family composers + per-family USF features
from quietly diverging while we defer the composer-skeleton unification.

**This is a REVIEW, not a fix.** You produce a report, update the scoreboard +
the Move-1 ledger, and **surface reconciliation decisions for the human**. You
do NOT change USF representations, composers, or extracts during a review —
those are deliberate decisions the human makes with the report in hand. (If you
spot a one-line obvious doc/comment fix, note it; don't refactor.)

Read FIRST, in full:
- `docs/the_move-1_plan.md` (Move 1, the §8 risk, the open principle question)
- `docs/the_principle.md` (§7 forbidden shape, §8 composer twin, §9 four tests)
- `.claude/memory/feedback_uready_vocabulary.md` (the 6 criteria + the live scoreboard)

## The 6 uready criteria (per engine family) — all checkable

1. **Orig-free builds (§9):** the build path reads only the model-generated USF
   (no original-binary reads beyond synthesized metadata). No verbatim/relocated
   engine bytes emitted.
2. **No escape hatches (§7/§8):** no opaque/engine-positional USF field
   (`*Kind:int`, `*Ptr`, `*_idx`, unjustified `bytes`-typed blocks); no
   engine-identity dispatch in the composer; per-family knobs behavior-named +
   factory-derivable from the SID itself.
3. **Factored & reversible USF:** techniques explicit, no lossy folds; any
   bytes-shaped/by-reference capture justified and reachability-minimal.
4. **Representative verification:** variant-spread sample FULL (play-stream +
   trichotomy audio✓), variant axes censused, wide-batch pass-rate known,
   failure buckets triaged; canaries wired into `tools/regression.py`.
5. **Feature-dimension accounting:** the family's behaviors mapped onto existing
   USF dimensions where they coincide (cluster-by-behavior receipts) and new
   dimensions named. **This is the evidence Move 1 consumes — see Phase 2.**
6. **Documented residue:** latents/quirks/accepted losses in `RE_NOTES.md` +
   project memory.

## Phase 0 — scope

`$ARGUMENTS` names one family (review it + its cross-engine reuse against the
rest) or is `all`/empty (review every migrated family). Discover the migrated
families from `pipelines/` (each top-level/`<engine>` dir with an extract +
composer path) and the `engine_docs` table / CLAUDE.md. List them, then proceed.

## Phase 1 — per-family uready scorecard (fan out)

Spawn **one subagent per family** (Explore or general-purpose), in parallel, each
scoring its family against the 6 criteria and returning a structured verdict.
**Forbid the subagents from any git mutation and from writing files**; open any
shared DB read-only (`mode=ro`). Each subagent reports, per criterion:
`PASS / GAP(detail) / N-A`, with the evidence (file:line, batch pass-rate, the
residue buckets). Tell each agent the concrete checks:

- C1/C2/C3: grep the family's composer + `from_usf` for verbatim-byte emission,
  engine-name strings, `if engine ==`, `_emit_<engine>_*`, `_needs_<engine>`,
  and the schema shapes (`Kind`, `Ptr`, `_idx`, `: bytes`). Confirm round-trip
  reversibility (extract↔USF) is asserted somewhere.
- C3 spec conformance (mechanical): run `python3 tools/usf_spec_lint.py` —
  round-trip equality, canonical fixpoint, the default-noise elidability
  census, §7 forbidden-shape scan. Errors are criterion-3 GAPs; census
  warnings are elidability-cleanup findings to list in the report (each is
  either a writer-elision fix or a reviewed ALLOWLIST entry with a reason —
  never leave one unclassified). Added 2026-08-03 after the init.voice_state
  default-emission showed a declared spec principle with no enforcing check.
- C4: find the family's wide-batch result + pass-rate; the variant census; the
  regression canaries.
- C5: which `UsfFile`/`Instrument` USF features the family's `to_usf` populates
  (this feeds Phase 2 — have each agent return its **feature list**).
- C6: does `RE_NOTES.md` + the `project_<engine>` memory document the residue?

## Phase 2 — cross-engine reuse review (the part Move 1 needs)

Collect the per-family feature lists into a **FEATURE × FAMILY matrix** (a quick
`tools/`-style script or inline Python over `src/usf/types.py` fields + each
`to_usf` is fine; build `tools/uready_matrix.py` if this becomes routine). Then
classify every USF feature:

- **Reused (≥2 families, same form):** a vindicated dimension. Good.
- **Single-consumer:** only one family uses it → flag as a possible §7 engine
  artifact. Decision needed: is it a real musical feature other engines will use,
  or an engine-specific leak to refactor?
- **DIVERGENT representations — the most important output:** two families
  representing the *same musical concept* with *different* USF forms. The known
  live example: DMC's `SweepEnvelope` (rate/frames phases) vs FC's
  `filter_programs`/`pulse_programs` (threshold/seg) — both are "cutoff/PW
  sweep." Each divergence is a **unify-vs-keep-separate decision for Move 1**
  (per §4: one parametric form spanning the musical DOF, or genuinely two
  behaviors?). List every one; do NOT decide it yourself — surface it.

Also run the principle's §9.2 leak scans across **all** composers/schema:
`grep -rn "Kind\b\|_ptr\b\|_idx\b\|: bytes\|bytes(" src/usf/types.py pipelines/`
and the §8 composer-dispatch scan
`grep -rn "if .*engine\|_emit_[a-z0-9]*_\|_needs_" pipelines/`.

## Phase 3 — verdict, scoreboard, decisions

Produce a report (to the user) with:
1. **Per-family scorecard** — uready ✓ or the failing criteria + what's needed.
2. **Cross-engine matrix** — reused / single-consumer / divergent features.
3. **Pending reconciliation decisions** — the divergences + single-consumers,
   each phrased as a crisp choice for the human (unify into form X / keep
   separate because genuinely-different-behavior / refactor the leak).
4. **Move-1 trigger status** — how many families are uready (the doc revisits
   Move 1 at ≥2 uready); whether the dispatch is growing branches (move needed)
   or absorbing engines into existing dimensions (dimensions sound).
5. **Diff vs last review** — what changed since the scoreboard's last date.

Then **update** (these writes are the only mutations a review makes):
- the **per-family uready status** in each family's `project_<engine>` memory
  (body-head STATUS section) + its MEMORY.md index line.
  `feedback_uready_vocabulary.md` holds ONLY the vocabulary + a durable
  pointer — do NOT append scoreboards there (they accumulate and rot;
  trimmed 2026-07-16 per the placement rule).
- the **Move-1 ledger** in `docs/the_move-1_plan.md` (criterion-5 feature
  accounting + the pending divergence decisions).
- the **[convergence ledger](../../../docs/the_convergence_ledger.md)** — the review
  is the periodic maintainer (per-solve recording is the everyday CLAUDE.md
  reflex). The ledger is TWO layers (since 2026-07-18): the imported
  recognition layer (index + cards in the main file) and the full entries in
  `docs/ledger/C<n>.md`. Ensure EVERY solution the Phase-2 matrix surfaces has
  an entry (log any missing as `logged`: entry file + index row + recognition
  card); then PROMOTE the ones used **≥2×** (reused OR divergent) to
  `recurring` — pick the one canonical form, set its shared-code location or
  `factor-candidate` status + occurrence count + boundary, in BOTH layers.
  **Card-sync check:** for every entry updated since the last review, re-read
  its card — does the card still carry the entry's tells and current status?
  (A stale card silently breaks recognition; `tools/memory_lint.py` checks the
  mechanical card↔file↔index consistency, but tell-coverage is judgment.)
  This is how the review pre-decides Move-1 convergence incrementally.
  (Record only — do NOT factor code; that's Move 1.)

## Memory-hygiene pass (part of every review)

The mechanical half is `python3 tools/memory_lint.py` — run it first and fix
any errors. The SEMANTIC half is this review's job (grep can't catch it).
Over the active memories in `.claude/memory/` (skip `_deprecated/`), check:

1. **Contradicts canon?** Any memory whose claims conflict with the four
   canon docs (verification modes, the principle, the trichotomy, ledger
   entries) — canon wins; fix or archive the memory with a "CONTRADICTS
   CANON" header (precedent: `_deprecated/project_timing_requirements.md`).
2. **Status frozen at write-time?** Frontmatter descriptions / MEMORY.md
   lines / "Next steps" sections asserting a state the body's newest entries
   (or the repo) have since overturned. Fix per CLAUDE.md "Memory hygiene":
   timeless description, status at body head + index line, supersession
   markers on stale tails.
3. **Wrong home?** Technique that belongs in the convergence ledger,
   status scoreboards in discipline memories, law duplicated outside canon —
   move per `feedback_knowledge_placement`'s 6-home rule.
4. **Resolved-but-lingering?** Fully-resolved project memories with nothing
   open and no load-bearing engine knowledge → `_deprecated/` + README note
   + drop the index line.

Report the findings with the scorecard; apply the fixes (memory files are
within this review's write scope).

## What "good" looks like

A review that ends in "every migrated family is uready, here are the 3 pending
divergence decisions for Move 1, trigger is met (N≥2)" — i.e. the unification
design has honest evidence and a short, explicit decision list, instead of
silently-forking dimensions discovered too late. And a memory store where the
lint is clean and every index line matches its file's head.
