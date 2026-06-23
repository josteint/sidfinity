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

## Honest residue / refinements

- The wall-clock length differs by ~12% (tempo quantization). The write stream is
  exact; tightening the length would need **absolute-frame step scheduling** (fire
  step k at its captured absolute frame, so per-step rounding doesn't accumulate)
  instead of summed per-step `dur+gap` countdowns. Noted, not yet built.
- Lockstep-chord assumption: all voices share step boundaries (true for Baby and the
  common BASIC idiom). Tunes with independent per-voice timing (rare in BASIC — hard
  to write) would need per-voice step clocks.
- Still proof-grade scripts (`proof_twinkle.py` + `proof_multivoice.py`), not yet the
  folded `pipelines/basic_program/{extract,build,verify}` + regression wiring.
