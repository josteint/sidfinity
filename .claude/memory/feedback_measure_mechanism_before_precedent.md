---
name: feedback_measure_mechanism_before_precedent
description: "Diagnostic ordering for a writelog divergence: MEASURE the actual read (pc-trace) before matching it to a prior round's index, and READ the whole multi-stage pipeline before instrumenting one stage. Retrospective from round 91 (Rogue_Ninja)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a39c97da-4a8d-4aa8-957f-229bc5830b84
  modified: 2026-07-22T23:53:17.778Z
---

Two time-wasters recur when diagnosing a DMC (or any) writelog divergence.
Both are "orient before diving in" failures; both cost ~10 tool-calls each
in round 91 (Rogue_Ninja, an off-table freq divergence).

## 1. Measure the mechanism BEFORE invoking a precedent

I saw an off-table freq-hi divergence, remembered round 89 (Para_Lander_DX,
off-table **idx 96** = V1 track-ptr lo), and ASSUMED idx 96. I measured
`$2707` (constant `$91`) to confirm — it wasn't idx 96. Several measurements
later, a pc-trace showed the real answer: **idx 97** (`$2708`). The
definitive measurement — pc-trace the diverging store, walk to the indexed
`LDA <freqbase>,Y`, read `Y` — should have been step 1, not step 10.

**Why:** a prior round tells you the CLASS (off-table freq read, per-player
window) but almost never the exact index/address — those vary per member.
Reaching for the precedent's specific value to avoid a measurement is the
"citing a precedent to defend an easy choice" drift ([[feedback_reanchor_at_decisions]]).

**How to apply:** for any freq lo/hi divergence, the FIRST action is the
pc-trace upstream walk to get the index + effective address. Then match the
CLASS to a precedent (C6/C11/C31), never the index. Tool that does the whole
chain now: `tools/dmc_offtable_probe.py <member>` (localize -> pc-trace the
off-table read -> static/live -> per-player value). Use it before recalling
"which idx was it last time".

## 2. Read the WHOLE pipeline before instrumenting ONE stage

The off-table capture is THREE stages in `extract()`: `_assign_offtable_freq`
(file image) -> `_correct_offtable_postinit` (siddump, per-song) ->
`_correct_offtable_eventdriven` (siddump, read-moment). I instrumented the
MIDDLE stage, saw the value was right there, and then chased a phantom
"non-determinism" (my spy wrapper's extra siddump calls changed the result)
before realising a THIRD stage ran afterward and clobbered it. Reading the
call sequence (the ~30 lines that list all three stages in order) FIRST would
have pointed at stage 3 immediately.

**Why:** a value that is correct at stage N but wrong in the output means a
LATER stage changed it. Instrumenting one stage in isolation makes a
downstream overwrite look like non-determinism or a capture bug.

**How to apply:** before wrapping/printing inside one function, read the full
feature pipeline (the caller that chains the stages) and enumerate every stage
that can touch the value. Instrument the LAST stage first, or print the value
after each stage in one pass. When "the value is right before the bug",
suspect a later stage, not the measurement.

## Tools built from this retrospective (round 91)
- `dmc_offtable_probe.py` — the whole off-table diagnosis in one command.
- `effect_chain_profiler.py --find-write REG=VAL` — locate a write by VALUE,
  not a guessed frame (kills the siddump-frame vs play()-index confusion;
  see [[reference_siddump_frame_cycles]]).
- `dmc_build_one.py --localize` — now auto-localizes the FAILING subtune from
  the verify capture (a compilation's sub 0 is often FULL; the old default
  localized sub 0 and found nothing), with no second full-songlength siddump.

See [[feedback_writelog_divergence_recipe]] for the base protocol these refine.
