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

### Principle guards (from the re-anchor check — load-bearing, not optional)

The transform changes the EXTRACTION METHOD, not the USF SCHEMA: its output is the
already-vetted `SweepEnvelope` / `offtable_freq`, so §7 and the trichotomy pass at the
schema level by construction. The risk is entirely in the METHOD, and three guards
keep it on the right side of the principles, the core tenet, and ledger C11:

- **G1 — no trajectory dump (core tenet / no-writelog-replay).** Observation is a
  MEASUREMENT INSTRUMENT at extract time; the STORED form is always the parametric
  musical fit. FIT is zero-residual-or-fall-back, and the fallback is **bounded
  `offtable_freq` or HARD RESIDUE — never explicit per-frame phases.** A `SweepEnvelope`
  of N single-frame `(delta,1)` phases is a write-log replay in disguise = the
  C7-Class-B blob we deleted (`freq_overrun`).
- **G2 — CLASSIFY by READ ADDRESS, not fit quality (§7 / ledger C11 hard boundary).**
  A successful clean fit is NOT evidence of reproducibility: an engine-positional value
  (`trkptr`, `wavepos`) fits a PERFECT linear ramp yet cannot be reproduced by the
  re-packed composer. The gate keys on the orig read's effective address (taint /
  memwatch): inside a musical table region → reproducible (resolve); work-RAM /
  pointer / live flag → HARD RESIDUE (exclude). This is the most important guard —
  without it the transform is WORSE than today, smuggling in residue cases that
  currently fail loudly.
- **G3 — segment on the trichotomy init boundary, not the frame counter.** The play-sim
  attribution must split init from play with the same init-aware alignment
  `compare_instruction_stream` uses, or differing init lengths (family-4) re-create the
  phantom-divergence mis-attribution.

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

## Phase-1 prototype outcome (2026-06-30, Jupiter41)

Prototyped the observe-and-fit REALIZE step on the family-4 blocker. Two results:

**1. Observe-don't-reimplement is validated.** Observing the orig's actual `$D4xx`
writes (vs re-implementing the walk) refuted three of my re-implementation-based
theories in a row and gave the divergence *directly*: at PW_lo=`$60` the orig switches
from ramping PW_lo (+$20) to ramping **PW_hi (+$08)** — the off-table sweep — while the
committed `_capture_env` keeps ramping PW_lo. The observed contour is unambiguous;
no walk-model can be wrong because it reads ground truth.

**2. NEW load-bearing finding — the de-fusion/off-table COUPLING (proven).** In the
de-fused representation each program is captured independently and re-packed into a
SHARED pulse table at a composer-chosen offset. Family-4 programs that run longer than
their captured phases walk off their own end into the ADJACENT re-packed bytes — which
are *another instrument's* data. So instruments are COUPLED through the shared layout,
and the committed code "works" partly by accident (the re-packed layout coincidentally
supplies the right off-table-tail bytes). **Proof:** changing ONLY V3's off-table
instrument (ptr 2) — growing its env by a few phases — shifted the shared table and
regressed a DIFFERENT VOICE (**V2 PW hi at flat-7416**), far before V3's own divergence
at 56000. Every per-instrument / horizon fix this session regressed for exactly this
reason.

**Design implication (refines the proposal):** a per-instrument off-table fix CANNOT
work for a coupled table — any layout change cascades cross-voice. The transform must
capture EVERY program's COMPLETE contour (to its full play-sim duration) so the
composer NEVER walks off a program's end into adjacent data. This makes the off-table
fix **all-or-nothing per tune**, and promotes the play-sim re-init horizon from a
heuristic bound to a **correctness requirement** (capture ≥ the longest each program
actually plays). It is also the strongest argument FOR observe-and-fit: an observed
complete contour is self-contained, which *breaks* the layout coupling that the
current independent-capture-into-shared-table approach cannot escape.

**Status:** thesis validated + the coupling structure uncovered; no green verdict yet
(a passing fix requires the full all-programs observe-and-fit build, which the coupling
finding now shows is necessary — not optional). Prototype scripts: `tmp/proto_*.py`.

### Full-build attempt (2026-06-30) — SEGMENTATION is the core obstacle

Began the full all-programs build. The REALIZE (observe the PW contour) and FIT steps
are straightforward; the hard part is **segmenting** the per-voice PW contour by
program (which frames belong to which instrument's pulse program) in the *play()-frame*
model the verdict uses. Three concrete findings:

1. **The re-init is INVISIBLE in the writelog.** The pulse init writes the engine's
   INTERNAL PW state ($182a/$182d), not the SID registers; only `pulse_run` writes
   `$D4xx`, once per frame. So a re-init (byte3≠0 load) produces NO distinct writelog
   signal (no double-write). Segmentation cannot be done from the SID writelog alone.
2. **The play-sim is UNRELIABLE for segmentation.** Its note-on schedule is off from
   the writelog gate-on edges by a consistent **2.09× in frame count** AND **~6× in
   note count** (761 play-sim note-ons vs 118 writelog gate-ons over the same span).
   Cause: the engine's 2-phase `$1016` (MAIN/TICK) timing (~2 frames per tick) plus a
   tie/gate model the simple `frame += cur_dur` sim doesn't capture. So the play-sim
   can't supply reliable segment boundaries without first nailing the exact tick→frame
   and note/tie semantics.
3. **The robust path is EVENT-DRIVEN internal-state capture** (the C11 "correct by
   construction"): `siddump --memwatch-on-write 180x 180x,182y,182z` snapshots the
   per-voice pulsepos + PW on every write to `$180x` (the pulsepos store) — one event
   per `pulse_run` advance = play-aligned, and re-inits show as pulsepos resets that
   directly carry the ptr. This exists in siddump (output: `|E<n>:addr=val:…` appended
   per frame) but needs: per-voice trigger handling, output parsing, and reconciliation
   with the play()-frame model (`--writelog-per-irq`) for the contour durations.

**Honest scope:** the full family-4 build is a multi-session engineering effort — the
segmentation infrastructure (event-driven internal capture + play-frame alignment +
the 2-phase timing model) is the real work, on top of the (easy) fit and the
all-instruments integration + zero-regression gate. The APPROACH and DESIGN are
validated; the IMPLEMENTATION is blocked on this segmentation layer. Recommended next
build order: (a) event-driven pulsepos capture per voice → reliable segments tagged by
ptr; (b) `--writelog-per-irq` contour per segment → play-frame deltas; (c) greedy
constant-delta fit (revive `strip_decompose`); (d) replace `_capture_env` wholesale for
family-4, gate on zero regression across FULL members. Build scripts: `tmp/of_step*.py`,
`tmp/proto_*.py`.

### ✅ Event-driven pulsepos segmenter — BUILT + VALIDATED (2026-06-30)

Step (a) is done — `tmp/pulsepos_segmenter.py`. It triggers on the per-voice SID PW-hi
write (`$D403/$D40A/$D411` = one `pulse_run` SID write per play-frame) and snapshots the
FULL internal accumulator as RAM (`pulsepos`, `PW-lo`, `PW-hi` — readable/unmasked,
unlike the 12-bit-masked `$D4xx`). It segments by re-init (pulsepos drop), groups by
program (post-reinit pulsepos = ptr+1), and returns each program's longest realized
contour — play-aligned, no walk re-implementation, no frame-model guessing.

VALIDATED on Jupiter41 across all 3 voices: it cleanly enumerates every pulse program
and flags the off-table ones (V2 ptr=7 maxPWhi=$FE, V2 default $FE, **V3 ptr=2 / inst 17
maxPWhi=$FC**). V3 ptr=2's contour is the odd-position walk `[3,5,7]` ramping PW_lo +$20
then PW_hi +$08 — its tail is `7:2460 7:2C60 7:3460…`, the EXACT values from the
flat-56000 divergence `_capture_env` missed. So the realize step is correct by
construction and the off-table sweeps are captured.

### The FIT — structure settled, robust decomposer is the remaining work (2026-06-30)

Explored the observed-contour → SweepEnvelope mapping. Findings that pin the fit's shape:

- **The holds are the composer's job, not the fit's.** The observed contour has a
  consistent **1-in-6** hold cadence (a frame where PW doesn't change). The COMMITTED
  rebuild matches the verdict, so the composer already reproduces these holds via its
  own timing. ⇒ the SweepEnvelope encodes count IN FRAMES (the engine count, holds
  included); the fit does NOT model holds.
- **pulsepos is layout-specific — segmentation only.** The committed rebuild has a
  DIFFERENT pulsepos walk (its de-fused re-pack chooses its own offsets), so the orig's
  pulsepos can't be carried into USF. It's used only to SEGMENT the orig and tag the
  program; the **contour** (the PW value sequence) is the fit target, and the composer
  plays it via its own walk.
- **Instrument mapping is byte3 = pp − 1** (post-reinit pulsepos = ptr+1). For each
  instrument with byte3=B, its pulse_env = the program segmented at pp=B+1. Start =
  the orig `pulse[ptr]` decode (`pulselo[ptr]<<8 | pulsehi[ptr]`).
- **Inst 17 (the blocker) fits cleanly:** start `$0020`, `(+32, 270)` [pulsepos 3,
  PW_lo +$20], a 3-frame transition [pulsepos 5], `(+2048, 136+)` [pulsepos 7, PW_hi
  +$08 off-table], last phase self-loops. Exactly the contour `_capture_env` missed.
- **The sawtooth programs are messier** (PW ramps then RESETS irregularly within one
  pulsepos — a loop with off-table-perturbed period), which is precisely where the
  revived `strip_decompose` (ramp + loop + zero-residual) earns its place.

So the fit = group contour by pulsepos → per-phase (rate = dominant non-zero delta,
count = frames) → loop = pulsepos cycle (or self-loop for off-table-forever) → map by
byte3=pp−1 → replace `_capture_env` for ALL programs at once (self-contained contours
break the coupling). The clean cases are mechanical; the sawtooth/irregular cases need
the `strip_decompose` decomposer + the MDL/zero-residual gate. That robust decomposer +
the all-programs integration + the zero-FULL-regression gate is the remaining dedicated
chunk. Build scripts: `tmp/of_fit_explore.py`, `tmp/of_check_holds.py`,
`tmp/pulsepos_segmenter.py`.

### DECOMPOSER BUILT — strip_decompose pulled in; ptr-2 validated, ptr-7 is the edge case (2026-06-30)

`tmp/of_decomposer.py`. Revives `effect_detect.constant_delta` (the proven ramp fitter)
as the per-phase primitive: it returns the dominant non-zero delta + consistency, which
HANDLES THE HOLDS by construction (consistency is over non-zero deltas). The decomposer:
segment by re-init → group runs by program (pp=ptr+1) → per pulsepos-group emit
(rate=dominant Δ, count=number-of-adds via wrap-aware sdelta) → map byte3=pp−1 → and
(HYBRID) use the observed fit ONLY when `_capture_env` 8-bit OVERFLOWS (the fragile /
layout-dependent programs); clean looping programs keep `_capture_env` (its `$90` loop
the contour can't reveal — observe-and-fit can't tell a loop-back from a re-init).

**Validated:** ptr 2 (inst 17) decomposes CORRECTLY: `(+32,223),(+32,1),(+2048,255),…`
— the off-table `+$08` sweep `_capture_env` missed, with the right wrap-aware count.
constant_delta is the right tool. Bugs found+fixed along the way: count must be
adds-not-frames AND wrap-aware (net/rate collapses on the wrapping PW); run-selection
must prefer the most-off-table run; hybrid criterion is "8-bit overflows" not
"PW off-table" (ptr 19 looks in-table but its 16-bit fallback reads garbage).

**RESOLVED diagnosis (2026-06-30, supersedes the layout-sensitivity guess below):**
the FIT IS SOLVED, and the 7416 blocker is composer/de-fusion, not the fit. Reading the
per-phase COUNT from the table (`pulsehi[pp+1]`, the fixed canonical value) while keeping
the observed RATE makes the fit CONVERGE EXACTLY to `_capture_env`'s 8-bit walk:
ptr 2 → `(+32,224),(+32,2),(+2048,256),(+0,8),(+512,240)`, ptr 7 → `(+0,256),(+0,1),
(-512,256)`. (The earlier 7416-causing bug was the OBSERVED hold count undercounting —
ptr 7 holds pulsepos 8 for a 256-frame table count but a cut run saw only 30; fixed by
the table-count read.) Since the fit now equals the canonical walk, observe-and-fit's
only real contribution is BOUNDING the off-table walk — and **7416 persists for BOTH
observe-and-fit AND `_capture_env`+horizon**, proving it is not the fit method but a
composer / de-fusion issue. VERIFIED observation (memwatch): the orig HOLDS V2 PW=$0800
(pulsepos 8 = ptr 7) for a long time; the rebuild's hold ends EARLIER (advances and ramps
PW to $00 at flat-7416 while the orig is still holding) — i.e. the rebuild's pulse
COUNTER reaches the 256 count sooner than the orig's. **The precise mechanism is NOT yet
nailed** — two hypotheses were tested and REFUTED: (a) de-fusion layout-sensitivity (the
fit content, not just size, is what matters — the counts now match the canonical walk);
(b) byte3=0 note-load resetting the counter (disasm `$13F7 BEQ $1411` SKIPS the whole
pulse init incl. the `$140B` counter reset when byte3=0 — so byte3=0 does NOT reset it).
A third hypothesis (2-phase counter timing) was ALSO REFUTED: the orig counter `$1831`
increments once per play-frame (the memwatch repeats are Trap-C 0-play frames). The
counter data instead reveals the orig holds `$0800` via REPEATED ptr-7 RE-INITS at
VARYING note intervals (counter resets 7C→00 then 11→00, pulsepos stays 08) — so the
rebuild diverges by ADVANCING where the orig RE-INITED; i.e. a re-init / note-timing
difference on V2, NOT the contour. PRECISE MECHANISM UNRESOLVED after 3 refuted guesses. So: the off-table contour FIT is solved & validated
(converges to the canonical walk); the remaining blocker is a composer pulse-counter
timing issue that needs dedicated diagnosis (capture the orig's counter `$1830` + the
`$1016` phase per frame vs the rebuild's).

**(superseded guess) Not yet passing (match=7416) — "layout-sensitivity":**
Worked through the segmentation thoroughly: the correct re-init signal for Jupiter41 is
a pulsepos DROP (a program's own off-table walk advances +2 or jumps UP via a `$90`
marker — e.g. ptr 7 walks 8→20→22 — so only a DOWNWARD jump is a re-init; the
"jump-to-ptr+1" signal false-splits because ptr 7 jumps up to pulsepos 20 = ptr 19's
+1). With drop-only, ptr 2 AND ptr 7 are captured. **But the verdict is stuck at exactly
7416 regardless of which fits are used** — meaning it is NOT a specific fit being wrong,
it is the **de-fusion table-growth side-effect itself**: the correct (larger) off-table
envs grow the shared pulse table (119→127), shifting the de-fused layout, and a
`byte3=0` V2 note at ~frame 50 *continues* a PW that now reads differently (`$08` orig
vs `$00` rebuild). So the coupling is not just "fit every program" — it is that the
de-fused re-pack is **layout-sensitive**, and any size change cascades through the
byte3=0 PW-continuation chain.

**The real remaining work** is therefore on the COMPOSER / de-fusion side, not the fit:
make the pulse playback NOT layout-sensitive — e.g. fixed-size per-program slots so a
program's size change doesn't shift others, or a byte3=0 continuation that reads the
self-contained envelope rather than the shared table tail. The observe-and-fit REALIZE
+ FIT pipeline is VALIDATED (ptr 2 + ptr 7 off-table contours extracted correctly via
`constant_delta`); the blocker is the de-fusion layout-sensitivity that makes the
all-programs swap cascade. Scripts: `tmp/of_decomposer.py`, `tmp/diag_ptr7.py`,
`tmp/pulsepos_segmenter.py`.

## Risks / honest scope

- Substantial refactor touching DMC v4/v5, FC, Hubbard extract paths; migration must
  be zero-regression-gated against current FULL members.
- The hard-residue cases (positional/dynamic) are **not** solved by this — they remain
  the documented architectural limit. The win is unifying + correct-by-construction
  for the solvable ~majority, not eliminating the residue.
- Over-engineering risk: the Z3/e-graph/MDL layers may be gold-plating. The proven
  cheap path (observe + greedy contour fit) is likely sufficient; add the heavy math
  only behind a demonstrated need.
