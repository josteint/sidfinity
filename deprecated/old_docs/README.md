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
  "in progress") is out of date. Replaced by `docs/canary_picker.md`
  + `docs/refactor_1_remaining.md` as the operational plan;
  `docs/PLAN.md` is now a thin pointer to those two.
- `usf_instrument_program_plan_2026_v1era.md` — USF v1 era blueprint
  for "instruments as 6502 programs" with Lean-codegen verification.
  Superseded by the principled-instrument refactor (typed musical
  parameters per `docs/usf_representation_principle.md`) and the
  feature-driven composer in `pipelines/composer.py`. References
  long-removed concepts: `engineQuirks`, `dynamicFreqEntries`,
  `preserveNoteFlags`, Grade A grading, `Codegen2.lean`.
