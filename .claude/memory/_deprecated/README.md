# Deprecated memories

Memories from earlier project phases — moved out of `MEMORY.md`'s index so
they no longer load on session start. Source preserved for archaeology.

## Categories

**Pre-USF era (Lean codegen, Grade A counting, das_model):**
- `project_das_model.md` — Lean 4 verified compiler architecture
- `project_pipeline_status.md` — Grade A status from before byte-exact
- `project_hubbard_strategy_2026_05.md` — pre-byte-exact "generalize das_model_gen" strategy
- `project_hubbard_diagnosis.md` — F-grade-from-TEMPO-detection era diagnosis
- `project_hubbard_table_arp.md` — Commando F→A analysis (pre-byte-exact)
- `project_math_formalization.md` — Lean formal work
- `reference_das_model_asm.md` — das_model.s asm reference (V3 codegen era)
- `reference_grading_tools_2026_05.md` — writelog_grade vs sid_compare grading
- `reference_engine_image_verbatim.md` — dragons_lair Lean verbatim path
- `reference_formal_tools.md` — Lean formal tools
- `reference_codegen_tools.md` — GT2 V2 codegen tools
- `reference_reverse_engineering_tools.md` — pre-byte-exact RE tools

**Engines moved to deprecated/usf1_pipelines/:**
- `project_last_v8_pipeline.md`
- `project_gremlins.md`
- `project_crazy_comets.md`

**Old debug logs (one-time investigations, since resolved):**
- `project_multisong_fix.md`
- `project_subtune_testing.md`
- `project_toneporta_bug.md`

**Completed migration / refactor phases (superseded by current code):**
- `project_usf_refactor.md` — USF refactor; superseded by composer dissolution
- `project_usf3.md` — references deleted `usf3_build_from_usf.py`; "v3" terminology no longer used
- `project_pipelines_layout.md` — duplicates CLAUDE.md's layout section; some paths outdated
- `project_hubbard_principled_usf.md` — Phase 2 mechanism-fields-to-engine_constants migration
- `project_companion_principled_usf.md` — Phase 1 companion forbidden-shape cleanup
- `project_math_brainstorm.md` — Das Model era math ideas (Das Model deprecated)

## If you need to revive one

Move it back up one level and add a line to `../MEMORY.md` pointing at it.
The memory body is unchanged from when it was active — just check that the
file paths, status numbers and architectural claims still match reality
before trusting it.

## premigration_2026-06/

31 memories recovered 2026-07-14 from the PRE-REPO memory location
(`~/.claude/projects/-home-jtr-sidfinity/memory/`), which was silently
orphaned when `autoMemoryDirectory` moved into the repo (~2026-06-06).
Mostly per-engine Hubbard-era project memories (Monty, Hawkeye,
Action_Biker, ...) and USF-design-era notes, frozen at their 2026-06
state. Four actively-referenced feedback memories from the same orphan
set were restored LIVE (verification_modes, sid_hidden_state_write_order, smc_disasm_check,
check_existing_engine_docs, writelog_divergence_recipe) — the rest live
here. Same caveat as above: verify claims against current reality
before trusting.
