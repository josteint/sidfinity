---
name: feedback_physical_constant_over_threshold
description: "When a census/detector needs a magic number, suspect it — key on a physical constant of the C64 instead; worked example is the raster-burst detector that took three tries."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 67372d23-f0c0-44b4-b011-ad9fac9257b6
  modified: 2026-08-31T19:02:23.113Z
---

When building a DETECTOR over a wide family — "which members do X?" — a
threshold over a DERIVED QUANTITY will look like it works and be wrong. Key
on a PHYSICAL CONSTANT of the machine instead (a PAL rasterline = 63 cycles,
a frame = 19,656, the CIA latch the member itself programmed). If no physical
constant is available, report the RAW MEASUREMENT and let a human read it —
do not manufacture a bucket.

**Why:** a threshold tells you where a number FELL, never what MECHANISM put
it there, so it cannot distinguish "the effect I am hunting" from "an
unrelated quantity that happens to land in my window". Both failure
directions are silent: the census returns a tidy table either way.

Worked example (Rayden_Digi, 2026-08-31 — three attempts, same question):

1. **"share of inter-write deltas in 55-70 cycles"** → flagged
   Spelling_Around at 42.7%. FALSE POSITIVE: its programmed CIA latch is
   `$42` = 66 cycles, so that window was simply its own NMI rate. A fixed
   cycle window cannot separate "runs a raster burst" from "has a fast
   timer".
2. **"deltas no programmed latch explains"** → flagged 15 of 17. FALSE
   POSITIVE twice over: the unexplained mass was inter-burst SILENCE (263c,
   488c — longer than any latch), and the latch set itself was polluted by
   non-digi `$DD04` writes, yielding an impossible "5-cycle latch".
3. **"a population at 63 ±2 cycles"** (one PAL rasterline) → Boot_Zak_v2
   21.1%, every other member ≤0.7%. A 30× gap, and it needed no tuning.

Note both failures were *plausible* and *self-consistent*. Only the third
had a reason to exist independent of the data.

**How to apply:** before shipping a census, ask "what physical fact of the
C64 makes this number mean what I claim?" No answer ⇒ either find one or
demote the classifier to a reported measurement with its constants printed.
Then check the separation: a real discriminator shows a GAP (0.7% vs 21.1%),
a tuned one shows a gradient. If you have already shipped a threshold tool,
say so in its docstring rather than leaving the buckets looking authoritative
(`tools/d418_shape_census.py` carries exactly that warning).

Related: [[feedback_ground_truth]] (measure from libsidplayfp, not py65) and
[[feedback_measure_mechanism_before_precedent]] (pc-trace the actual read
before matching it to a prior round's index) — same family of error, one step
earlier in the pipeline.
