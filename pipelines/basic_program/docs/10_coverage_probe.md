---
source_url: local: pipelines/basic_program/coverage_probe.py over a stratified sample
fetched_via: local read
fetch_date: 2026-06-23
author: SIDfinity orchestrator
content_date: 2026-06-23
reliability: primary
---

# Coverage probe — current lift over a stratified 81/486 sample

`pipelines/basic_program/coverage_probe.py` runs lift -> build -> verify over a
stride-6 sample (81 of 486) and clusters the failures. Raw:
`tmp/basic_program_research/coverage_probe.jsonl`.

## Result: 8/81 FULL (10%) with the current freq+gate lift

| bucket | n | meaning |
|---|---|---|
| overlap_diverge | 42 | write stream diverges. First-diff reg: **V1/V2/V3ctl 23**, freq 11, ad 3, vol/pw 2 |
| lift_crash | 16 | `IndexError` in the lift (Ahoy-style legato + odd shapes) |
| build_fail | 6 | xa65 "Branch out of range" (the old ±127 trampoline bug, more voices/writes per step) |
| lift_no_gate | 4 | no gate-on at all (gate set once / freq-only / GET) |
| too_many_steps | 4 | N>255 (8-bit stepidx) |
| length_fail | 1 | overlap exact, length off (loop-detect miss) |

FULL skews single-voice (6 of 8); 3-voice dominates overlap_diverge (22) — the more
voices, the more per-step content my narrow model misses.

## The dominant gap (~52%): the per-step writes are RICHER than freq+gate

The current lift models a step as exactly `[gate-on] + freq + [gate-off]`. Real BASIC
tunes poke much more **per note**:

- **Per-note volume / accent** — e.g. `Deutschlandlied`: `vol=0F … vol=08 … vol=06`
  changes every step (a volume envelope), interleaved with freq+gate.
- **Per-note ADSR re-poke** — `V1ad`/`V1sr` rewritten each step.
- **Gate value variants** — `ctl=$11`→`$00` (full clear) vs my assumed `$10`; and
  freq-vs-gate order varies per tune.
- **Legato** — gate set ONCE, then only freq changes (Ahoy) → no per-note gate edge,
  so the current gate-segmentation crashes or mis-segments.

So the failures are NOT one variant ("legato") — they're all facets of **"a step is an
arbitrary set of register writes, in a tune-specific order,"** not just freq+gate. The
freq+gate model is a special case.

## Cheap robustness wins (independent of the model)

- **16-bit stepidx** → fixes `too_many_steps` (4).
- **Branch trampolines** in the attack/release emit → fixes `build_fail` (6).
- **Graceful no-gate** → stop crashing; route to the richer model.

## The design decision this surfaces (for the user)

To cover the ~52% overlap_diverge, the lift must capture the FULL per-step register
write-set, not just freq+gate. The fork is HOW to represent that in USF without it
becoming raw write-log replay ([[feedback_no_writelog_replay]] — rejected):

- **(A) Generic per-step register-deltas** — capture each step's `(reg->val)` set +
  duration; the engine replays them at the step's absolute frame. Powerful, covers
  everything; but per-step register dumps border on raw replay (USF-principle risk).
- **(B) Semantic per-step model** — interpret each register class musically: freq->note,
  ctrl->waveform/gate, AD/SR->envelope, vol->dynamics, PW/filter->timbre; store as
  structured USF note events with per-note timbre. Principled/ML-friendly; more work,
  and some BASIC tunes poke registers in ways that don't map to a clean instrument.
- **(C) Hybrid** — semantic for the recognizable classes (freq/gate/ADSR/vol), with a
  typed "extra per-step pokes" escape for the rest; keeps most content musical.

Recommendation: **(C) hybrid** — it keeps pitch/dynamics/envelope as musical USF (the
ML-valuable part) while not crashing on the long tail. But this is a USF-representation
call; see `docs/usf_representation_principle.md`.
