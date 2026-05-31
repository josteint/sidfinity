---
name: subtune-frames-not-arbitrary
description: "Verify with songlength × 1.5 frames (subtune_frames), never an arbitrary N. User has had to remind me multiple times."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

When comparing rebuilt SID vs original via py65 snapshots, the frame
count is **songlength × 1.5 × 50 Hz** — never an arbitrary 500 / 1000
/ 2000. The Hubbard verify path uses
`pipelines.hubbard.verify.subtune_frames(config, passes=1.5)`; the
companion / new-engine paths get the same number by reading
`songlength_s` from `hvsc84.db` and computing
`round(1.5 * songlen * 50)`.

**Why:** Arbitrary frame counts either (a) cut off the song before
verifying the loops and tail, or (b) run for so long that the
post-song-end garbage past the engine's terminator dominates and
introduces false failures. The songlength × 1.5 window is exactly
calibrated for "play the whole song with a small safety margin."

**How to apply:** Any time I'm about to write `n_frames=500` or
similar, stop and look up the HVSC songlength from `hvsc84.db`. For
ad-hoc smoke tests during iteration a short window is fine, but for
"is this engine done?" the only legitimate question is **does every
subtune match for the full songlength × 1.5 window**. The skill
`migrate-hubbard-engine` already requires this; the rule applies to
all engines.

User has reminded me of this multiple times — last
nudge: *"why 500? Arbitrary! do subtunelength x 1.5! we have talked
about this many times"*.
