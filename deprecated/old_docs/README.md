# Old Planning Documents

Session plans and codegen plans from earlier phases. Kept for historical context.

- `next_session_plan.md` — decompiler fix tracks (all 5 completed)
- `player_codegen_plan.md` — V2 codegen development plan (completed)
- `composer_rewrite_plan.md` — the universal_codegen-to-composer
  decomposition plan. Superseded by the composer dissolution
  (Phase 8) — Hubbard '85 now lives entirely in `pipelines/composer.py`.
- `usf2_emit_rules.md` — `InstSource` → 6502 codegen contract from
  the Lean-codegen era (Phase 2's `Codegen2.lean`). Lean codegen is
  deprecated; the current composer is feature-driven asm composition
  in Python.
- `PLAN_2026_04.md` — the project's top-level development plan as
  of 2026-04-09. Captures the long-term vision (neural net → USF →
  SIDfinity player) but the per-step status (GT2/DMC transpilers
  "in progress") is out of date. The operational plan is now
  `docs/refactor_1_remaining.md` (Move 1) + CLAUDE.md's Project goal;
  `PLAN.md` and `canary_picker.md` were both retired (below).
- `usf_instrument_program_plan_2026_v1era.md` — USF v1 era blueprint
  for "instruments as 6502 programs" with Lean-codegen verification.
  Superseded by the principled-instrument refactor (typed musical
  parameters per `docs/the_principle.md`) and the
  feature-driven composer in `pipelines/composer.py`. References
  long-removed concepts: `engineQuirks`, `dynamicFreqEntries`,
  `preserveNoteFlags`, Grade A grading, `Codegen2.lean`.

Moved 2026-07-14 (repo deprecation sweep):

- `deconstruct_offtable_freq_plan.md` + `offtable_statebuf_plan.md` —
  the two interim off-table-read plans, each superseded (their own
  banners) by `offtable_freq_plan.md`.
- `offtable_freq_plan.md` — the final off-table-freq plan; all 7 phases
  ✅ DONE 2026-06-21 (absolute-freq wave steps, FC unification, schema
  cleanup). Still cited by ledger C6 + DMC/FC memories as the design
  rationale. The living successor doc on the recurring class is
  `docs/offtable_unified_transform.md`.
- `cia_aware_verdict_plan.md` — CIA-aware per-play() verdict for
  `verify_all`; IMPLEMENTED 2026-06-07 (commit f82b347). The shipped
  behaviour is documented in `docs/the_core_tenet.md` (Mode 1, CIA
  bullet).
- `refactor_plan_principled_instrument.md` — principled Instrument
  schema refactor; DONE 2026-06-01 (Hubbard 71/71 + Companion +
  Jay_Derrett through the new schema).
- `ml_architecture_analysis.md` — 2026-04 ML-architecture proposal,
  pre-representation-principle era. The Principle + the tokenization
  memory (`reference_tokenization`) govern this territory now.
- `sid_chip_edge_cases.md` — SID chip edge-case research compiled for
  Das Model validation (Das Model era is deprecated). Chip-behaviour
  reference material; revive if cycle-level chip modelling returns.
- `engine_model.md` — the composable-codegen spec for
  `pipelines/engine_model.py`. The dataclass-tree part lives on in that
  file; the codegen layer this doc describes (`universal_codegen`) was
  dissolved into `pipelines/composer.py` (Phase 8).

Moved 2026-07-18/19 (docs de-rot sweep — each carries its own banner):

- `canary_picker.md` — the per-family canary-selection strategy.
  Superseded by the whole-family grind (canaries can't represent a
  family; grinding gives Move 1 a complete oracle). Selection method now
  lives in CLAUDE.md's Project goal.
- `usf_digi_plan.md` — USF digi-support plan; phases D0-D4 shipped 2026-05
  (Chimera 4/4). Durable successor: `reference_digi_pipeline` memory.
- `principled_fc_composer_plan.md` — the FC principled-composer plan;
  completed (FC §9 closed, model-USF buildable). Status lives in the
  `project_fc_principled_composer` memory.
- `dmc_composer_to_extract_plan.md` — the DMC composer→extract carrier
  moves; all phases done/superseded. Status lives in `project_dmc`.

Moved 2026-07-20:

- `adrenalin_multisong_plan.md` — plan to finish FC Adrenalin subs 1/2/3
  via 5TT-style unification. Subsumed by ledger C31 (COMPILATION); the
  Adrenalin-specific analysis + open target live in the
  `project_adrenalin` memory. Sub 0 done (Adrenalin[0] 1/1 in
  `tools/regression.py`).
