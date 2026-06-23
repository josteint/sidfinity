---
name: reference_siddump_frame_cycles
description: "siddump's \"frame\" ≈ 18,000 CPU cycles (event-scheduler ticks), NOT the 19,656-cycle PAL play period — matters for absolute-cycle / RSID-vs-PSID timing"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 31df618e-1d05-4346-8dfa-a60476d0a5cc
---

**siddump's per-"frame" cycle count ≠ the PSID play period. A siddump frame ≈ ~18,000
CPU cycles; the PAL play period is 19,656. They differ by ρ ≈ 0.919.** We have
re-derived this (wrongly, twice) before — keep it in context.

## The facts (measured, not theory)

- The PSID `play()` fires at the TRUE VIC frame rate: **PAL = 19,656 CPU/PHI1 cycles =
  50.125 Hz** (verified — consecutive play-entry PHI1 cycles via `--writelog-per-irq
  --per-irq-debug` are exactly 19,656 apart). The rebuild is NOT slow on hardware.
- BUT siddump's main loop calls `engine.play(cyclesPerFrame)` where `cyclesPerFrame`
  (PAL = 63·312+32 = **19688**) is a count of **event-scheduler ticks**, NOT CPU
  cycles: `c64::clock()` is `eventScheduler.clock()`, and one tick advances to the
  next scheduled event — **< 1 CPU cycle** (~0.917 CPU cyc/tick empirically). So one
  siddump "frame" advances only **~18,000 CPU cycles** (measured per-frame base deltas
  ~17,600–18,150; = 19,656 × 0.919).
- Therefore **plays-per-siddump-frame ρ ≈ 0.919** (PAL). siddump's `|P:` shows ~0.92,
  with regular `|P:0` frames — this is EXPECTED, not a counter bug (`getPlayCount`
  agrees with the player's own RAM frame-counter). A trivial `init/play=rts` PSID and
  real Hubbard rebuilds all show 0.919.
- Consequence: a siddump "N-second" capture (`totalFrames = N·fps`) emulates only
  ~0.913·N real seconds — it under-emulates wall-clock by ~9%.
- ρ is **clock-dependent** (NTSC has its own VIC frame + event density). Measure it
  per-clock from a trivial PSID's `|P:` rate; don't assume PAL's 0.919 for NTSC.

## When it bites (and when it does NOT)

- **Does NOT affect the normal Mode-1 verdict.** `compare_instruction_stream` is a flat
  `(reg,val)` prefix over concatenated frames — bucketing-agnostic. So PSID-vs-PSID
  families (Hubbard, FC, DMC) never trip on this: both sides are bucketed identically
  and the mismatch cancels. This is why it stayed hidden.
- **DOES bite** whenever you reason in ABSOLUTE CYCLES or align a **free-running RSID**
  (CPU-paced, e.g. Basic_Program's BASIC) against a **PSID** (play-paced):
  - Computing absolute cycle as `frame × cyclesPerFrame` (×19688) **overestimates by
    1/ρ ≈ 1.088** — use ~18,000, or better, the play-period clock.
  - A PSID rebuild whose note schedule is calibrated in siddump-FRAME units plays
    ~8.7% slow vs an RSID original; fix = scale targets by ρ (→ writes land at the
    original's exact cycles). See [[project_basic_program]] `measure_rho` (commit
    dd4d5bf): gate-on absolute-cycle ratio 1.088 → 1.000, length diff → 0.

## The trap that keeps re-snaring us

CLAUDE.md's Trap C said "siddump runs 19688 **cycles** per loop iteration" — read as
19,688 **CPU cycles** (> the 19,656 VBI, implying play fires *sometimes 2×*/frame).
The reality is 19,688 **event ticks ≈ 18,000 CPU cycles** (< 19,656, so play fires
*~0.92×*/frame, regularly 0). That wrong mental model caused a multi-turn wrong
conclusion ("8.7% emulation-vs-hardware difference", "don't scale") until the user
pushed back ("i doubt there is a 9% difference between emulated and real hardware").
Related but distinct from [[feedback_observation_drift]] / Trap C frame-bucket drift.
