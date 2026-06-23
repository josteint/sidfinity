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

## Verdict for the family — overlap-exact + duration_tol

The Hubbard strict `|len_a-len_b| <= 64` does NOT fit free-running BASIC: a 50Hz
player can't frame-exactly match BASIC's `FOR/NEXT` timing (per-step sub-frame
rounding + siddump Trap-C bucketing accumulate over a multi-minute loop). So the
family verdict is **overlap-exact + a proportional `duration_tol`** (the tolerance
the C6 research anticipated). `verdict_basic` = `match_all == min(len)` AND
`|len_a-len_b| <= max(64, 0.15·max(len))`. Baby's length diff is 225 (~12%, the
accumulated tempo quantization over ~3 loops); the write STREAM itself is exact.

## Absolute-frame scheduling + the siddump rate-bias finding

The player now uses **absolute-frame scheduling**: a 16-bit frame counter fires each
step's attack/release at its **captured absolute frame** (`atk[k]`/`rel[k]`), and a
`loopbase` advances by the measured loop period each wrap. This removes the per-step
`dur+gap` summation, so per-step rounding no longer accumulates and each loop stays
anchored to the original.

It exposed the real cause of the residual length diff — **a siddump measurement
bias, not a rebuild error**:

- The RSID-BASIC original runs FREE (no `play()` vector; `|P:0` every frame — its
  writes fall into siddump's 19,688-cycle frame buckets at BASIC's pace).
- The PSID rebuild's `play()` is invoked by siddump at **~0.92×/frame** — and this
  rate is UNIVERSAL: a trivial `init/play=rts` PSID and real Hubbard rebuilds show
  the identical 0.92 (every PSID's `play()` effectively fires every ~21,400 cycles in
  siddump, not VBI's 19,656).
- So siddump frames a free-running RSID and a VBI PSID at **different frame rates** —
  an ~8.7% bias. **Scaling the rebuild's targets by 0.92 makes the verdict length
  diff EXACTLY 0** (overlap still 1902/1902) — proving the residual IS this rate bias.
- We do **NOT** scale: the unscaled rebuild is tempo-faithful on real hardware (a step
  ≈ 211,302 cycles via VBI vs the original's ≈ 211,646); scaling would make it ~8.7%
  fast on hardware (the ear is the final judge). So `verdict_basic` keeps a
  proportional `duration_tol` to absorb the *tool* bias.

Hubbard tunes are unaffected because there BOTH the original and the rebuild are
PSIDs, played at the same 0.92 rate.

## Honest residue / refinements

- The verdict's length comparison is biased by the siddump RSID-vs-PSID play-rate
  (~8.7%); `duration_tol=0.15` absorbs it. A tighter, hardware-faithful verdict would
  normalize the length by the known PSID-play-rate in the COMPARATOR (not the
  rebuild) — a production-verify refinement.
- Lockstep-chord assumption: all voices share step boundaries (true for Baby and the
  common BASIC idiom). Tunes with independent per-voice timing (rare in BASIC — hard
  to write) would need per-voice step clocks.
- Still proof-grade scripts (`proof_twinkle.py` + `proof_multivoice.py`), not yet the
  folded `pipelines/basic_program/{extract,build,verify}` + regression wiring.
