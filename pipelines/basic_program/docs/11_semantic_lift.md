---
source_url: local: pipelines/basic_program/semantic_lift.py + semantic_probe.py
fetched_via: local read
fetch_date: 2026-06-23
author: SIDfinity orchestrator
content_date: 2026-06-23
reliability: primary
---

# Semantic richer lift — writelog -> per-step register model (10% -> 22%)

`pipelines/basic_program/semantic_lift.py`. Ported the idea of
`gt2_pipeline/regtrace_to_usf.py` onto the **`--writelog` ordered (reg,val) stream**
(NOT the old per-frame snapshots — those lose the within-frame write ORDER the flat
verdict checks).

## Model

Segment the writelog (real frames) into bursts ("active runs") separated by the
silent FOR/NEXT holds. A **step** = an attack run (note start: freq/gate-on + any
per-note timbre) + an optional trailing **release** run (the gate-off group). Each
step's writes form a per-step **template**; per register slot:

- **const** (same value every step) = the instrument / waveform / fixed envelope —
  factored out, emitted inline by the player.
- **perstep** (varies) = the note (freq), dynamics ($D418), or per-note timbre —
  stored in the packed step record, emitted via `(sp),y`.

This is principled (musical content, not a raw write dump): const = instrument,
perstep freq = notes, perstep $D418 = dynamics. The player reuses the absolute-frame
+ rho + 16-bit-step-pointer + loop infra from `proof_multivoice`.

## Result (stratified 81/486 probe — `semantic_probe.py`)

`SEMANTIC COVERAGE: 18/81 FULL (22%)` — up from 8/81 (10%) with the freq+gate lift.
The opaque overlap_diverge 52 bucket resolved into clean, named levers:

| status | n | meaning / next action |
|---|---|---|
| FULL | 18 | — |
| unsup_variable_template | 31 | **#1 lever: RESTS** — voices conditionally silent, so the per-step register set varies. Needs per-step voice-active mask (a voice rests = its slots skipped). |
| unsup_legato | 19 | **#2 lever** — gate set once, then freq-only changes; no per-note gate edge. 1-phase (attack-only) step model, note boundary = freq change. |
| too_few_steps / after_trim | 8 | degenerate/short or trim removed too much; revisit segmentation floor. |
| overlap_diverge | 3 | near-misses (V1ctl/V1freq/vol @ deep positions) — small per-tune quirks. |
| length_fail | 2 | overlap exact, length off — loop-detection miss on long tunes. |

## Known-deferred (the lift returns `unsupported:<reason>` rather than a wrong build)

- **variable_template (rests):** a step omits a silent voice's writes. The fixed
  consistent-template requires every step to write the same registers. Fix: derive a
  superset template + a per-step active-slot mask (the mask = which voices play =
  musical note pattern), emit only active slots.
- **legato:** segment by freq-change (gate-on once); attack-only steps, no release.
- The lift trims trailing capture-cut steps before the consistency check (so a window
  artifact doesn't fail an otherwise-consistent tune — e.g. Baby's last release).

## Net

The semantic lift ~doubled coverage and converted the bottleneck into two clear,
sizeable levers (rests 31 + legato 19 = ~62% of the sample). Handling both should push
coverage well past 50%. Still proof-grade (no USF-file round-trip yet — that's the
productionize step, mapping const->instrument / perstep-freq->notes / $D418->dynamics
into USF v2 + a regression).
