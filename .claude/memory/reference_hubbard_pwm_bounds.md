---
name: Hubbard PWM bounds are hardcoded $08/$0E
description: Rob Hubbard's pulsework routine uses cmp #$08 / cmp #$0E as bidir PWM direction-flip thresholds — NOT per-instrument
type: reference
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
In Rob Hubbard's bidirectional PWM (`pulsework` routine, e.g.
`src/hubbard/docs/hubbard_monty_disassembly_acme.asm:454`), the PW
high-nibble direction-flip thresholds are HARDCODED:

  - going UP flips at `cmp #$0e` → if pwhi (after `and #$0f`) == $0E
  - going DOWN flips at `cmp #$08` → if pwhi == $08

These are NOT per-instrument values. Any Hubbard codegen / extractor
must use `i_pwmin = $08, i_pwmax = $0E` for ALL instruments on this
engine, regardless of what the observed steady-state PW range looks
like in the warmup phase.

**Why this matters:** PW takes ~40+ frames to walk all the way from
init value down to $08 (with step $E0, 8 frames per step). Observing
only the first 40 frames can show a misleading range like $0B..$0E,
which is *transient* — not the actual bounds.

**How to apply:** When generalizing `das_model_gen` to a new Hubbard
SID, pass `default_pw_min=0x08, default_pw_max=0x0E` to `extract()`.
Do not guess from siddump frames 1-40.
