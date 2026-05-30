---
name: observation-drift-not-music-drift
description: "When the rebuild's per-VBI-frame writes don't match the original's, check whether the GLOBAL cycle-ordered write stream matches. Frame-boundary bucketing is observation, not music."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

When my rebuild's writelog "per-frame" comparison fails but the audio
sounds identical, the failure is almost always **siddump frame-bucket
shift**, not a real difference in what the SID receives.

**Rule:** The SID chip sees a continuous stream of writes in cycle
order. siddump groups them by VBI frame (50 Hz) for reporting. A
play() call that takes even ~12 cycles less than the original's
shifts when subsequent writes land relative to a VBI boundary. Over a
long song, this can move many writes from "frame K" to "frame K+1"
in siddump's output — looking like divergence to per-frame compares,
but the actual instruction stream into the SID is identical.

**Why:** Confirmed empirically on the bowden_canonical family. Five
SIDs showed FAIL on per-frame ordered comparison but PASS on global
cycle-ordered comparison (init-skipping). User caught this and
called it correctly: *"this turned out to be not a drift in music
but a drift in how we observed the music."*

**How to apply:** Use `compare_instruction_stream` in
`pipelines/hubbard/verify_cycle.py` (default `skip_init=True`).
Concatenate all writes across all frames in cycle order, compare
position by position. Init order is allowed to differ between rebuild
and original (engines often write D418/AD/SR in different sequences
but reach the same final state); the test should focus on music
writes.

A length mismatch with full prefix match means the test window
contains different counts of music ticks on each side due to small
init duration drift — equivalent musically, just differently
truncated.

**Don't be misled by per-VBI-frame "FAIL" reports** when the
cycle-ordered stream matches.

## Related
- [[feedback_py65_misses_dispatch_bugs]] — py65 snapshot misses
  things; writelog is authoritative. But even writelog needs the
  right comparator.
- [[reference_writelog_verify]] — `tools/siddump --writelog` is the
  ground truth for the SID instruction stream.
