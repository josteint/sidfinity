---
name: feedback_header_flags_audible
description: "NEW-COMPOSER CHECKLIST: derive PSID header flags (SID model + clock) from usf.psid and diff the rebuilt header vs the orig at bring-up — the write-log verdict is blind to headers, and hardcoding FLAGS_PAL_6581 was independently repeated in 3 composers before the ear caught it."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ecfcfba7-aa57-459e-907d-2b829fe8eee8
---

When bringing up a NEW engine's composer (`build_*_sid`): (1) derive the PSID
header flags from `usf.psid` — `(clock_bits << 2) | (sid_bits << 4)`, the FC
composer_asm form — never hardcode `FLAGS_PAL_6581`; (2) diff the rebuilt
header (flags, speed, songs, start_song) against the orig header as part of
first verification.

**Why:** the write-log verdict is structurally blind to header metadata, yet
the SID-model flag (6581/8580 filter + combined waves) and clock flag
(PAL/NTSC dispatch rate + pitch) change how the identical stream SOUNDS. The
hardcode was made independently in DMC v4, DMC v5 and GoatTracker v1 (+ a
lossy both/unknown→6581 collapse in FC) and survived 4,998 verified-FULL
members until a user ear-test on Taurus_02 (2026-07-06). No automated verdict
covers this dimension — the header diff at bring-up and the mandatory
new-engine ear-test ([[feedback_py65_misses_dispatch_bugs]]) are the only
nets. All in-tree composers were fixed 2026-07-06; extracts capture
clock/sid losslessly (USF grammar admits `sid: both`/0).
