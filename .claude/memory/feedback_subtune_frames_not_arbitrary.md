---
name: subtune-frames-not-arbitrary
description: "Verify at songlength × 1.1 (the RATIFIED standard, 2026-07-02) — never an arbitrary N, never 1.0x. The overshoot verifies cross-songlength/loop behaviour. song_exact (1.0x) lever REJECTED."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

The verify window is **songlength × 1.1 × 50 Hz** — never an arbitrary
500 / 1000 / 2000, and **never 1.0x**. (Historically 1.5x in the early
Hubbard era; the project-wide standard is 1.1x, ratified explicitly by
the user 2026-07-02.)

**Why (user's rationale, 2026-07-02):** the rebuilt SID must match the
original's **cross-songlength behaviour** — at least 10% past the
songlength — because that is what covers correct audio for **looping
songs** (the wrap into the loop's next iteration, carried modulation
phase, etc.). A 1.0x window verifies only the first pass.

**song_exact (1.0x) lever REJECTED (2026-07-02):** the June "+32
family-1 FULLs at 1.0x" (byte-exact for the song, tiny modulation-phase
drift in the loop's 2nd iteration) was pending ratification; the user
rejected it — those 32 were reverted to partial and their written
.usf/.sidfinity.sid removed. Fixing them means making the loop wrap
match too (reproduce the carried phase — core tenet permits reproducing
the mechanism), not shrinking the window. Related: [[feedback_strict_writestream_always]].

**How to apply:** any time I'm about to write `n_frames=500` or
`duration=song`, stop — the verdict window is `songlength * 1.1`
(from `hvsc84.csv` / Songlengths.md5). Short windows are fine only for
ad-hoc iteration probes, never for a FULL verdict.

User has reminded me of the no-arbitrary-N rule multiple times — one
nudge: *"why 500? Arbitrary! do subtunelength x 1.5! we have talked
about this many times"*.
