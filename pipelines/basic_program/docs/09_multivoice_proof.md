---
source_url: local: pipelines/basic_program/proof_multivoice.py
fetched_via: local read
fetch_date: 2026-06-23
author: SIDfinity orchestrator
content_date: 2026-06-23
reliability: primary
---

# Multi-voice generalization — Baby_Elephant_Walk (+ Twinkle regression)

`pipelines/basic_program/proof_multivoice.py` generalizes the single-voice Twinkle
lift to N voices with an arbitrary per-tune write order.

## Result

```
Baby_Elephant_Walk : voices=[1,2,3] order=gate_then_freq waves={1:$20,2:$40,3:$20}
                     overlap=EXACT (1677/1677)   FULL
Twinkle (regress.) : voices=[1]     order=freq_then_gate waves={1:$10}
                     overlap=EXACT (60/60)       FULL
```

**Overlap is EXACT for both** — every `(reg,val)` the original emits is reproduced
in the exact order, across all 3 voices. That is the CORE TENET's target (the
write-log stream).

## What generalized

- **Step model.** The music is a list of STEPS, each `[attack] · hold · [release] · gap`.
  Baby = chord-per-step (all 3 voices gate on, 6 freq writes, hold, all gate off);
  Twinkle = the 1-voice degenerate case. Same code path.
- **Write ORDER is a per-tune structural parameter, derived from the capture** —
  Baby is **gate-then-freq**, Twinkle is **freq-then-gate**; the order of voices and
  of ctrl-vs-freq writes within a step is captured as a template and replayed. (This
  is the engine's write model — NOT musical content; it never enters USF.)
- **Per-voice waveforms** ($20 saw / $40 pulse / $20 saw for Baby) read from the
  gate-on ctrl bytes → instruments. Freq 0 = a silent-but-gated voice (reproduced
  verbatim; no special rest handling).
- **Init boundary.** Music starts at the first gate-on, backing up over any freq
  writes that feed it (handles freq-then-gate vs gate-then-freq + the 25-write
  `FOR T=0 TO 24:POKE S+T,0` clear loop that writes the freq registers to 0).
- **Loop detection.** Baby does `I=9:GOTO42` (loops to step 9). `_find_loop` finds the
  period from the chord signature (intro=9, period=134); the player loops back to the
  intro skip. Twinkle `END`s → the player halts (`loop_to=None`).
- **Initial delay.** Baby spends ~444 frames (~9 s) on its `FOR Z..READ` DATA scan
  before the first note; a 16-bit initial-delay countdown reproduces that so the
  rebuild doesn't skip the dead-air intro.

## Verdict for the family — overlap-exact + strict |len|<=64

`verdict_basic` = `match_all == min(len)` (overlap exact) AND `|len_a-len_b| <= 64`
(Hubbard's strict tolerance). After the absolute-frame scheduling + `rho` unit
conversion below, the rebuild's writes land at the original's exact cycles, so the
length diff is **0** (Baby 1902/1902, Twinkle 60/60) — no loose duration tolerance
is needed. (An earlier draft of this proof used a proportional `duration_tol` to
absorb what turned out to be a fixable unit bug; see below.)

## Absolute-frame scheduling + the rho unit-conversion (cycle-exact tempo)

The player uses **absolute-frame scheduling**: a 16-bit frame counter fires each
step's attack/release at its **captured frame** (`atk[k]`/`rel[k]`), and a `loopbase`
advances by the measured loop period each wrap — no per-step `dur+gap` summation, so
rounding can't accumulate and each loop stays anchored.

That exposed a real tempo bug — and chasing it down corrected an earlier WRONG
conclusion (there is **no** emulation-vs-hardware difference):

- The rebuild's `play()` fires at the **true VIC frame rate** — PAL 19,656 CPU cycles
  = 50 Hz (verified: consecutive play-entry PHI1 cycles are exactly 19,656 apart). The
  rebuild is NOT slow on hardware.
- But siddump steps the emulator via `engine.play(cyclesPerFrame=19688)`, where
  `cyclesPerFrame` counts **event-scheduler ticks** (`c64::clock()` =
  `eventScheduler.clock()`), and one tick is **< 1 CPU cycle** — so a siddump "frame"
  advances only ~18,000 CPU cycles, NOT one 19,656-cycle play period.
- So an onset measured in **siddump-frame units** (~18,000 cyc) is in the wrong clock
  for a player that advances per **play-period** (19,656 cyc). The fix is a unit
  conversion: scale targets by **rho = plays-per-siddump-frame** (= CPU-cyc-per-frame /
  play-period ≈ **0.919** PAL; `measure_rho` derives it per-clock from a trivial PSID's
  `|P:` rate, so it tracks NTSC too).
- With rho, the rebuild's writes land at the original's **exact emulated cycles**:
  gate-on absolute-cycle ratio reb/orig → **1.000** (from 1.088), and the verdict
  length diff → **0** (Baby 1902/1902, Twinkle 60/60). Verdict tightened to the strict
  Hubbard `|len|<=64`.

Earlier I wrongly called the 1.088 a "measurement bias" and declined to scale, on the
false premise that the PSID plays at 50 Hz in siddump but the rebuild would be 8.7%
fast on hardware. It does play at 50 Hz; the 1.088 was the siddump-frame-vs-play-period
unit mismatch, and scaling by rho is the correct, hardware-faithful fix.

Hubbard tunes never hit this because there BOTH original and rebuild are PSIDs, so the
flat `(reg,val)` comparison is bucketing-agnostic and the unit mismatch cancels.

## Honest residue / refinements

- `rho` corrects a siddump emulation-timing detail (event-tick "frame" ≠ CPU-cycle
  play period); it's self-calibrated per clock from a trivial PSID's `|P:` rate.
- Lockstep-chord assumption: all voices share step boundaries (true for Baby and the
  common BASIC idiom). Tunes with independent per-voice timing (rare in BASIC — hard
  to write) would need per-voice step clocks.
- Still proof-grade scripts (`proof_twinkle.py` + `proof_multivoice.py`), not yet the
  folded `pipelines/basic_program/{extract,build,verify}` + regression wiring.
