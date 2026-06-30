# Unified off-table-read transform — design proposal (2026-06-30)

Status: **proposal** (not yet implemented). Synthesised from a 3-agent sweep of the
codebase, the convergence ledger, and the full git history. Decision pending.

## The recurring problem

A C64 music engine indexes a musical table (freq / wave / pulse / filter / note /
vibdepth) with an **8-bit** register or a byte program-counter. When the index walks
past the nominal end of the table, the engine keeps reading adjacent image bytes and
emits them to `$D400-$D418` as continued musical data. We have hit this in Hubbard,
DMC (v4, v5, family-2, family-4), and Future Composer, and it is the current
family-4 (Jupiter41) blocker. Each engine solves it ad-hoc in its own extract code.

The convergence ledger already tracks it as **C2** (off-table *program* table),
**C6** (off-table *freq data* lookup), **C7** (the opaque-blob anti-pattern), and
**C11** (8-bit wrap + the hard-residue boundary). Both C2 and C6 are flagged as
"Move-1 factor-candidates" — i.e. the project's own roadmap already wants this
factored into shared infrastructure.

## Census taxonomy (20 occurrences; full table in the session record)

The decisive axis is **what lies past the table end**, because that determines both
the representation and whether the read is solvable at all:

| region content past the end | representation | solvable? |
|---|---|---|
| another musical table (overlapping lo/hi/filter arrays) | `SweepEnvelope` phases (resolve the walk) | yes |
| static instrument-record bytes | exact value capture (`offtable_vibdepth`) | yes (exact) |
| per-voice work RAM at its init/file-image value | `offtable_freq = [(offset,note,lo,hi)]` | yes |
| **engine-positional / dynamic** — a memory *address* (`trkptr`), the engine's own *absolute position* (`wavepos`), or a live *flag* | — | **HARD RESIDUE** |

The four *representation classes* the project has used, and the convergent answer:

- **(a) verbatim byte blob + raw index** — `freq_overrun`. The FORBIDDEN shape
  (USF principle §7, ledger C7-Class-B). Both FC and DMC v5 used it, both migrated
  off it, the schema field was **removed** 2026-06-21.
- **(b) content-by-reference value capture** — acceptable only for *static* bytes
  (`offtable_vibdepth`, Hubbard SFX `extended_freq`).
- **(c) per-entity parametric** — THE canonical solution: `offtable_freq` for data
  lookups (C6), `SweepEnvelope` for off-table programs (C2 + C1). Engine-blind,
  musical, ML-legible.
- **(d) hard residue** — engine-positional/dynamic bytes; the core tenet forbids
  matching the orig's layout/state-evolution, so these are a documented limit, not
  a bug (DMC family-2 claim-flag, Object_of_Art `wavepos`, the 84% `trkptr` subset).

## The core reframe — two mistakes we keep making

Every hard off-table bug we have hit (the family-4 ptr-19 regression, the
reach-horizon guessing, the parity/loop errors) is one of two avoidable mistakes:

1. **We RE-IMPLEMENT the walk instead of OBSERVING it.** `_capture_env` re-derives
   the engine's index-advance / count / `$90`-loop / parity rules in Python and is
   bit-exact for some pointers but not others (ptr 2 ✓, ptr 19 ✗). The ground truth
   — the actual value sequence — is already produced by the orig and observable via
   `siddump --writelog` / `--memwatch-on-write`. **Observe, don't re-implement.**
2. **We capture with a STATIC reach over-approximation instead of REALIZING the
   sequence.** The `reach = songlen*1.1*playrate` horizon is a heuristic bound; when
   it is wrong the program truncates (family-4) or overflows. The realized sequence
   is deterministic — get it by execution, not by guessing a window.

Both py65 (`src/code_flow.py`, `src/hubbard_emu.py`) and libsidplayfp
(`siddump --writelog/--memwatch-on-write`) already run at factory/extract time. The
infrastructure to observe is present; we just are not using it for off-table capture.

## Proposed transform: REALIZE → CLASSIFY → FIT

A new pre-USF pass operating model→model (`extract` → **transform** → `to_usf`).
Agent-confirmed principled: it emits only the existing musical schema, adds **zero**
new USF fields, and is exactly the C2/C6 Move-1 factor the ledger anticipates.

1. **REALIZE** — produce the exact realized (value, duration) sequence for each
   off-table program, by **observation** (segment the orig `--writelog` by the play
   schedule so each instrument/program's frames are isolated) with the play-sim
   schedule (the family-4 re-init horizon work) telling us which frames belong to
   which program. Correct-by-construction: no walk-model can be wrong because we
   read the orig's actual writes. Where observation is impractical, fall back to a
   *single* shared walk simulator with **cycle detection** (Brent) on the index —
   which finds the true `$90` loop deterministically (fixing the ptr-19 class) and
   uses the play-horizon only for genuinely acyclic (off-table-forever) walks.
2. **CLASSIFY** — identify what the walk read (another table / static bytes /
   work-RAM-at-init / engine-positional-or-dynamic). This is the solvability gate;
   positional/dynamic → flag HARD RESIDUE (exclude or accept-divergence), never
   absorb into an engine-state window (the C11 boundary, the real design constraint).
3. **FIT** — decompose the realized contour into the minimal parametric form,
   **zero-residual-or-fall-back**: greedy constant-delta (linear ramp) + DFT fit
   first; if residual ≠ 0 it is not a clean sweep → store explicit values
   (`offtable_freq`); MDL test decides parametric-vs-raw so we never over-fit a
   sweep model to genuinely high-entropy bytes.

This collapses the duplicated code — three `_*offtable_freq` extractors, three
composer-side window rebuilders, the `min(256,…)` bound written 3×, the two
`_capture_env` forks, and the Hubbard state-mirror lineage — into one walker + one
classifier + one fitter + one composer reconstruction. After it runs, `to_usf`
becomes trivial (the off-table reads are already resolved into `SweepEnvelope` /
`offtable_freq` on the clean model).

## Reusable assets from git history (the abandoned mathematics)

The conceptual scaffolding is one rediscovered doc:
`deprecated/lean_codegen/formal/docs/mathematical_framework.md` — frames extract→USF
as an inverse-map / constraint-satisfaction / abstract-interpretation problem (§7
enumerates which math applies where). **Read it first.**

Ranked reusable assets (all in `deprecated/`):

1. **`strip_decompose.py` + `effect_detect.py`** (the gold) — a PROVEN-LOSSLESS
   parametric contour decomposer: 100% match on full-song Commando (500 frames). Its
   `constant_delta` (linear-ramp) fitter, real-DFT vibrato fitter, and **zero-residual
   invariant** map almost directly onto the FIT step. `effect_detect.FREQ_PAL` already
   survives into `engine_constants.py`, so the lineage is partly live.
2. **`z3_decompose.py`** — exact-reproduction SMT solver ("does a compact (start,
   rate, count, loop) reproduce all N values?"). Use as a **fallback ORACLE only**:
   the cheap greedy stripper *beat* it on its own benchmark (100% vs 95.9%) and was
   far slower — lesson: greedy first, Z3 only when greedy leaves residual.
3. **`taint_tracker.py`** (`deprecated/lean_codegen/formal/`) — instrumented 6502
   execution mapping each read→register-write; the REALIZE half: positively confirms
   a read went off-table (effective address ≥ table end) and captures the sequence.
   This is the principled basis for the CLASSIFY gate (distinguishes adjacent-data
   from positional/dynamic).
4. **`info_theory_analysis.py`** — MDL / entropy metric; the objective accept test
   for "is the parametric form actually shorter than raw bytes + index?"
5. **`structured_pack.py` / `holy_scale.py`** — dictionary/codebook dedup of repeated
   frame-programs (the existing wave-pool dedup, ledger C8, is a descendant) and the
   worked precedent for "parametric decomposition → USF with byte-exact re-simulation."

Dead ends confirmed (do not revive): the Lean `Properties.lean` proofs (structural
only), the GPU/CUDA 6502 cycle optimiser (minimises player code, not data), the
`regtrace_to_usf.py` universal register-trace fallback (deliberately lossy, ~59%
Grade A — violates the through-USF/ML purpose), Grade-S/A/B/C/F snapshot tolerance
(the rejected Trap-A verdict).

## Staging (recommended)

- **Phase 1 — REALIZE-by-observation/cycle-detection, replacing `_capture_env`.**
  This alone fixes the family-4 ptr-19 blocker (the current stuck case) and is the
  correct-by-construction foundation. Validate: zero regression on existing FULL
  members + Jupiter41 past 56000.
- **Phase 2 — unify the `offtable_freq` extract + composer reconstruction** (schema
  already shared; only the code is triplicated). Cross-engine regression.
- **Phase 3 — port `strip_decompose`'s contour FIT + MDL gate.** Improves
  compactness/robustness; lower urgency.
- **Defer** — Z3 oracle + e-graph canonicalisation; document as fallbacks, build only
  if greedy fit proves insufficient (history says it usually won't).

## Risks / honest scope

- Substantial refactor touching DMC v4/v5, FC, Hubbard extract paths; migration must
  be zero-regression-gated against current FULL members.
- The hard-residue cases (positional/dynamic) are **not** solved by this — they remain
  the documented architectural limit. The win is unifying + correct-by-construction
  for the solvable ~majority, not eliminating the residue.
- Over-engineering risk: the Z3/e-graph/MDL layers may be gold-plating. The proven
  cheap path (observe + greedy contour fit) is likely sufficient; add the heavy math
  only behind a demonstrated need.
