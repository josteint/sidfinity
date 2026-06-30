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

PHASE-1 PROTOTYPE (2026-06-30, Jupiter41): (1) observe-don't-reimplement VALIDATED —
observing the orig's PW writes refuted 3 re-implementation theories and gave the
divergence directly (at PW_lo=$60 the orig switches PW_lo+$20 → PW_hi+$08; committed
`_capture_env` keeps ramping PW_lo). (2) ⭐ NEW PROVEN FINDING — the de-fused pulse table
is CROSS-INSTRUMENT COUPLED: changing ONLY V3's off-table inst (ptr 2) regressed V2 PW
hi at flat-7416 (different voice). Programs that outrun their captured phases walk off
into adjacent re-packed bytes (another inst's data); committed "works" by layout
accident. So per-instrument off-table fixes are ALL-OR-NOTHING — the transform MUST
capture EVERY program's COMPLETE contour (full play-sim duration), which is exactly why
observe-and-fit (self-contained contours) is the right tool. Play-sim horizon promoted
from heuristic to correctness requirement. No green verdict yet (needs the full
all-programs build). Earlier "ptr-19 walk model wrong" framing is SUPERSEDED by the
coupling — the real issue is the shared-table coupling, not just one pointer's walk.

FULL-BUILD ATTEMPT (2026-06-30): started the all-programs build; SEGMENTATION is the
core obstacle (which frames = which program, in the play()-frame model). Findings:
(1) re-init is INVISIBLE in the writelog (init writes internal $182a/$182d, not $D4xx;
only pulse_run writes once/frame) → can't segment from SID writelog alone. (2) the
play-sim is UNRELIABLE: off by 2.09× in frames + ~6× in note-count vs writelog gate-ons
(the 2-phase $1016 MAIN/TICK timing + tie/gate model). (3) robust path = EVENT-DRIVEN
`siddump --memwatch-on-write 180x 180x,182y,182z` (per-voice pulsepos+PW on each
pulsepos write = play-aligned; re-inits = pulsepos resets carrying the ptr). Exists in
siddump but needs per-voice parsing + play-frame (`--writelog-per-irq`) reconciliation.
The full family-4 build is a MULTI-SESSION effort — segmentation infra is the real work;
fit + integration are easy. Approach/design VALIDATED, implementation blocked on
segmentation. Next build order: event-driven pulsepos capture → per-segment per-irq
contour → greedy constant-delta fit (revive strip_decompose) → replace `_capture_env`
wholesale, gate on zero FULL-regression. Scripts: `tmp/of_step*.py`, `tmp/proto_*.py`.

SEGMENTER BUILT + VALIDATED (2026-06-30, `tmp/pulsepos_segmenter.py`): triggers on the
per-voice SID PW-hi write ($D403/$D40A/$D411 = one pulse_run write/play-frame), snapshots
the FULL internal accumulator as RAM (pulsepos+PWlo+PWhi, unmasked). Segments by re-init
(pulsepos drop), groups by program (pp=ptr+1), returns each program's longest play-aligned
contour. Across 3 voices it enumerates every program + flags off-table ones; V3 ptr=2
(inst 17) captures the odd-walk [3,5,7] PW_lo+$20 then PW_hi+$08, tail 7:2460 7:2C60 = the
EXACT flat-56000 values _capture_env missed. Correct by construction.

FIT structure SETTLED (the remaining work = the robust decomposer): (1) the 1-in-6 holds
are the COMPOSER's job (committed rebuild matches the verdict, so its timing reproduces
them) → SweepEnvelope count is IN FRAMES, fit doesn't model holds. (2) pulsepos is
LAYOUT-SPECIFIC (committed rebuild has a different walk) → use it for SEGMENTATION ONLY;
the CONTOUR (PW values) is the fit target. (3) instrument mapping = byte3 = pp-1; start =
orig pulse[ptr] decode. (4) inst 17 fits CLEANLY: (+32,270),(.,3),(+2048,136 self-loop) =
exactly the missed contour. (5) the SAWTOOTH programs (PW ramps then RESETS irregularly
within one pulsepos — off-table-perturbed period) need the revived `strip_decompose`
(ramp+loop+zero-residual). Coupling forces ALL programs re-fit together (can't ship just
the clean ones — re-fitting inst 17 grows the table and cascades). So: green verdict needs
the strip_decompose decomposer + all-programs integration + zero-FULL-regression gate.

STAGING: Phase 1 = observe-and-fit ALL pulse programs completely (breaks the coupling),
NOT per-instrument. Phase 2 unify offtable_freq code. Phase 3 port the contour FIT.
Defer Z3/e-graph unless greedy proves insufficient.

Relates to [[project_dmc]] (family-4 ptr-19 = the live blocker), the ledger C2/C6/C7/C11,
and `docs/usf_representation_principle.md` §7.
