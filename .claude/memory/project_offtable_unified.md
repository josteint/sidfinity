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

⭐ GO/NO-GO VERDICT (2026-06-30, end of session) — the method SPLITS into two variants of
OPPOSITE maturity (full detail = the doc's "GO / NO-GO" section):
- **FREQ overrun-trace (`offtable_freq`) = ✅ MATURE, roll out.** Ships in FULL family-3
  members; Electric_Drum tighten-to-observed-reads proof (11→7 records, stayed FULL); GT
  V1 independent convergence (same records + ≥128-size padding Trap-B guard).
- **PROGRAM overrun-trace (`SweepEnvelope` decomposer) = ❌ NOT MATURE, go/no-go FAILED,
  do NOT roll out.** No green achievable: off-table PULSE is family-4-ONLY (0/120 family-3
  partials have one); only 3 family-4 partials are PW-first (via TRICHOTOMY first_play_diff
  — `flat_div` is init-structure-contaminated for family-4 universal-reset, so it's NOT
  reliable here, unlike family-1/2). On those 3: Jupiter41 decomposer makes it WORSE
  (play_match 56000→7416, breaks an earlier hold program); Motorway_Crash + force-observe
  change NOTHING (5252, identical) ⇒ that V1pwlo divergence is UPSTREAM (note/gating), a
  trichotomy mislabel, not the pulse. So the decomposer is double-gated: its own
  hold/re-init contour fit AND the family-4 note/freq/init foundation that precedes the
  pulse in every member's stream. FOLD IT INTO family-4 completion, not a standalone phase.
- Tools: `tmp/find_offtable_pulse_partial.py`, `tmp/jup_true_div.py`, `tmp/of_decomposer.py`
  (now trichotomy-verify + `OF_FORCE=1` force-observe). KEY METHOD LESSON: for family-4
  divergence localization use the TRICHOTOMY `first_play_diff` (state_match-aligned), NOT
  the batch `flat_div` (init-structure-contaminated by universal-reset).

⭐ REFRAME INVESTIGATION (2026-07-01, full detail in the doc's "reframe" section): user
challenged that the off-table difficulties are just mechanism-mirroring artifacts (core
tenet frees us to reproduce the write-log any way). Findings: (1) the "observe the trace,
don't parse the tables" reframe IS the project's ORIGINAL vision — `mathematical_framework.md`
§6.3 universal α_trace path — but built for the REJECTED tolerance relation (59% Grade A);
the EXACT-match decomposition tools exist in `deprecated/python_experiments/`
(`strip_decompose` residual-must-be-zero, `z3_decompose` 100%-target, `auto_effect_discover`
system-ID, `effect_detect` detectors, `info_theory_analysis` MDL) — revivable, swap capture
to `siddump --writelog`. (2) Experiment (`tmp/reframe_*.py`): observe-and-fit WINS the
stateless in-table pulse programs outright (ptr=11 287/287, ptr=19 29/29 exact contours,
off-table dissolved) but the long/off-table ptr=1/2/7 are not consistent. (3) ⭐ VERDICT FLIP — off-table pulse is
REPRESENTABLE (b), NOT residue. The probe (delta 84-94%-predictable from $1800+$1830+$182A/D)
FIRST read as "couples to external state" was WRONG. GREY-BOX check (research's rec):
disassembly ($14B4) shows plain `LDA $23A3,Y`/`$23BC,Y`, byte-indexed, no SMC (add=HI<<8|LO,
count=LO[pos+1], $90 marker on HI); TAINT check (`tmp/taint_memtrace.py`, --memtrace,
within-frame-complete per-ACCESS) proves source $23A3-$24BB is 100% STATIC (24k reads, 0
writes). So the pulse IS deterministic in {static tables + pulsepos + reinit}; the 84-94%
was a CAPTURE-TIMING artifact (segmenter snapshots $1800 at the $D403 write = POST-advance
pulsepos ≠ read-index Y). NO hidden dynamic coupling — user's thesis vindicated. NB user
correctly flagged: per-frame --memwatch snapshot has a within-frame blind spot; use
--memtrace (per-access) for taint. POSITIVE verify NOT yet green: records already captured
(full 256-entry m.pulse), but (a) hand-sim inherits the capture-timing gap (82-91%), (b)
the composer's family-4 pulse walk (`_capture_env` count8bit) reads rate=(lo<<8|hi)/count=chi
/marker-on-lo = LO/HI SWAPPED vs the engine — a fixable walk-convention bug on the
load-bearing family-4 pulse path. (4) Pivot: launched a deep-research
survey (run `wf_d87b53b2-72d`) of the vast literature on exact identification of
deterministic transducers with hidden/external state (active automata learning / L* /
register automata, Myhill-Nerode minimization, PSRs/OOMs/spectral-Hankel, Koopman, subspace
ID, smallest-grammar, CEGIS/SyGuS). Family-4 pulse state addrs (extract-only): pulsepos
$1800,x / PW accum $182A,x(lo) $182D,x(hi) / 8-bit count $1830,x / pulse tables $23BC,$23A3.

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

DECOMPOSER BUILT (2026-06-30, `tmp/of_decomposer.py`): revived strip_decompose's
`effect_detect.constant_delta` as the ramp fitter (handles holds by construction).
Pipeline: event-driven segment -> group by program (pp=ptr+1) -> per-pulsepos
constant_delta (wrap-aware adds count) -> map byte3=pp-1 -> use-on-8bit-overflow hybrid.
VALIDATED: ptr 2 (inst 17) AND ptr 7 off-table contours extracted CORRECTLY (the +$2048
/ -512 sweeps `_capture_env` missed). Re-init signal = pulsepos DROP (drop-only); the
"jump-to-ptr+1" signal false-splits because programs jump UP via $90 (ptr 7: 8->20->22,
20=ptr19+1).
✅ FIT SOLVED: reading the per-phase COUNT from the table (pulsehi[pp+1], canonical) +
the observed RATE makes the fit CONVERGE EXACTLY to `_capture_env`'s 8-bit walk (ptr 2 →
(+32,224),(+32,2),(+2048,256),(+0,8),(+512,240)). So observe-and-fit's only real job is
bounding the off-table walk; the contour representation is correct.
⛔ 7416 BLOCKER is COMPOSER pulse-COUNTER TIMING, not the fit (persists for BOTH
observe-and-fit AND `_capture_env`+horizon). Verified: orig HOLDS V2 PW=$0800 (pulsepos
8=ptr7) longer than the rebuild — the rebuild's counter hits the 256 count sooner and
ramps to $00 at 7416 while the orig still holds. TWO HYPOTHESES REFUTED: (a) layout-
sensitivity (the counts now match the canonical walk = content not size); (b) byte3=0
counter-reset (disasm $13F7 BEQ $1411 SKIPS the whole pulse init incl. the $140B counter
reset when byte3=0 — so it does NOT reset). 2-phase counter hypothesis ALSO REFUTED: orig counter $1831 increments once per
play-frame (the memwatch repeats are Trap-C 0-play siddump frames, not skips). The
counter data REVEALS the real picture: it resets at VARYING values (7C->00 then 11->00)
with pulsepos staying 08 — so the orig holds V2 PW=$0800 via REPEATED ptr-7 RE-INITS at
varying note intervals (NOT one 256-count hold). The rebuild diverges by ADVANCING/
ramping where the orig RE-INITED and held => the rebuild MISSED a ptr-7 re-init (a
note-timing / re-init-timing difference), OR its ptr-7 program advances when the orig's
re-inits. PRECISE MECHANISM UNRESOLVED after refuting 3 hypotheses (layout-sensitivity /
byte3=0-counter-reset / 2-phase-counter). NEXT (fresh diagnosis): compare orig vs rebuild
ptr-7 re-init FRAMES + the note schedule on V2 — the divergence is in WHEN ptr 7 re-inits
/ how long its notes are, not the off-table contour. THE VALIDATED WIN: the off-table
contour FIT is solved (converges to the canonical walk). Lesson: made 3 wrong mechanism
guesses; the FIT is the real result, the re-init-timing is the unresolved blocker.

STAGING: Phase 1 = observe-and-fit ALL pulse programs completely (breaks the coupling),
NOT per-instrument. Phase 2 unify offtable_freq code. Phase 3 port the contour FIT.
Defer Z3/e-graph unless greedy proves insufficient.

Relates to [[project_dmc]] (family-4 ptr-19 = the live blocker), the ledger C2/C6/C7/C11,
and `docs/the_principle.md` §7.
