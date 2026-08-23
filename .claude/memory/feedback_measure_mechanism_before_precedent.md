---
name: feedback_measure_mechanism_before_precedent
description: "Orient-before-diving diagnostic ordering: ask what a parameter IS FOR before mapping where its bytes are readable; measure the actual read before invoking a prior round's index; read the whole pipeline before instrumenting one stage."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a39c97da-4a8d-4aa8-957f-229bc5830b84
  modified: 2026-08-07T18:54:02.493Z
---

Three time-wasters recur when diagnosing a DMC (or any) writelog divergence,
or when judging whether a parameter is needed. All are "orient before diving
in" failures. §1 and §2 each cost ~10 tool-calls in round 91 (Rogue_Ninja, an
off-table freq divergence); §3 cost a whole investigation and produced a
proposal that would have broken thousands of members (B4 onset, 2026-08-07).

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
chain now: `pipelines/dmc/offtable_probe.py <member>` (localize -> pc-trace the
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

## 3. ASK WHAT THE PARAMETER IS FOR before mapping where its bytes can be read

Added 2026-08-07 (B4 onset, user challenge). Asked "can this value be
removed?", I enumerated every path by which its BYTES could reach the write
stream — memory layout, record-image packing, off-table reads — ran three
expensive measurements, and built a whole elision proposal on the finding
that only 47 of 12,064 members could observe it. All correct, all beside the
point: I never read what the player DOES with the value on the ORDINARY path.

`onset` is the DMC editor's **vibrato delay** (instrument byte 7 hi nibble x8
frames, lo nibble = width). `fx_vibdel` gates the ENTIRE effects branch —
dual-slide included — while it counts down, and `fx_vib` is not inert at
width 0 (it advances the freq accumulator every frame; width only sets when
the direction flips). So the premise "width 0 => the delay is meaningless"
was false, and "unreachable on 99.6% of members" had closed only the exotic
door. Measurement: forcing the value moved the stream on **27 of 60 ordinary
members with no off-table read at all**. The proposal would have broken
thousands.

The user caught it in one question — *"what IS this counter? how is it
defined? did the composer do something in the editor to create it?"* — after
I had spent three measurement rounds inside the mechanism.

**How to apply:** before asking "where can this byte be read from", answer
"what did the MUSICIAN set, and what does the player DO with it". Read the
editor-format docs (`pipelines/<family>/docs/`) for the field's meaning and
the player's consuming branch, THEN map reachability. A reachability census
over the exotic paths is worthless while the normal path is unexamined —
and it looks rigorous, which is what makes it dangerous. Corollary: a field
that turns out to be a NAMED EDITOR KNOB is musical content by default;
the burden shifts to proving it inert, not to proving it reachable.

## Tools built from this retrospective (round 91)
- `pipelines/dmc/offtable_probe.py` — the whole off-table diagnosis in one command.
- `effect_chain_profiler.py --find-write REG=VAL` — locate a write by VALUE,
  not a guessed frame (kills the siddump-frame vs play()-index confusion;
  see [[reference_siddump_frame_cycles]]).
- `pipelines/dmc/build_one.py --localize` — now auto-localizes the FAILING subtune from
  the verify capture (a compilation's sub 0 is often FULL; the old default
  localized sub 0 and found nothing), with no second full-songlength siddump.

See [[feedback_writelog_divergence_recipe]] for the base protocol these refine.
