---
name: project_offtable_unified
description: "Unified off-table-read transform proposal — the recurring \"engine reads past the freq/wave/pulse table\" problem across all engines"
metadata: 
  node_type: memory
  type: project
  originSessionId: b632f6d3-9d96-4623-9ee1-b5354ba2f9a3
---

The "engine indexes a table with an 8-bit reg / byte program-counter and walks PAST
the table end, emitting adjacent image bytes as music" phenomenon recurs across
Hubbard, DMC (v4/v5/family-2/family-4), Future Composer — and is the current
family-4 (Jupiter41) blocker. 3-agent sweep (2026-06-30: census + git-history math
archaeology + pipeline/principle map) → **proposal doc `docs/offtable_unified_transform.md`**.

KEY FINDINGS:
- **20 occurrences** censused. Decisive axis = WHAT lies past the end: another
  musical table → `SweepEnvelope`; static instr bytes → exact value; work-RAM at
  init value → `offtable_freq=[(offset,note,lo,hi)]`; **engine-positional/dynamic**
  (a memory address `trkptr`, the engine's own `wavepos`, a live flag) → **HARD
  RESIDUE** (core tenet forbids matching orig layout — a limit, not a bug).
- Schema is ALREADY unified (`offtable_freq` + `offtable_vibdepth` + `SweepEnvelope`,
  shared types); only the CODE is triplicated (three `_*offtable_freq` extractors +
  three composer rebuilders + `min(256,…)` ×3 + two `_capture_env` forks). Ledger
  C2/C6 already flag this as a Move-1 factor-candidate.
- A pre-USF model→model transform IS principled (Agent C: emits only existing schema,
  zero new fields, blessed by the core tenet's "restructure to produce the stream").
- **The two mistakes we keep making:** (1) we RE-IMPLEMENT the walk (`_capture_env`
  bit-exact for ptr 2, WRONG for ptr 19) instead of OBSERVING the orig's actual
  writes (`siddump --writelog/--memwatch`); (2) we use a STATIC `reach` horizon
  instead of REALIZING the sequence. Both py65 + libsidplayfp already run at extract
  time. **Observe, don't re-implement; realize, don't static-approximate.**
- Design = **REALIZE (observe writelog, segmented by play-sim schedule; cycle-detect
  the $90 loop) → CLASSIFY (solvability gate) → FIT (greedy constant-delta+DFT
  contour decompose, zero-residual-or-explicit, MDL-gated)**.
- **Reusable abandoned math** (the user's "math stuff"): `deprecated/python_experiments/
  strip_decompose.py`+`effect_detect.py` = PROVEN-LOSSLESS contour decomposer (100%
  full-song Commando) — the FIT engine. `deprecated/.../mathematical_framework.md` =
  the scaffolding doc. `z3_decompose.py` = exact-reproduction fallback ORACLE (but
  greedy BEAT Z3 100% vs 95.9% — greedy first). `taint_tracker.py` = REALIZE+CLASSIFY.
  `info_theory_analysis.py` = MDL accept test.

STAGING: Phase 1 (REALIZE-by-observation/cycle-detection, replace `_capture_env`)
alone unblocks family-4 ptr-19. Phase 2 unify offtable_freq code. Phase 3 port the
contour FIT. Defer Z3/e-graph unless greedy proves insufficient.

Relates to [[project_dmc]] (family-4 ptr-19 = the live blocker), the ledger C2/C6/C7/C11,
and `docs/usf_representation_principle.md` §7.
