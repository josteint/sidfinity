---
name: feedback_header_flags_audible
description: "NEW-COMPOSER CHECKLIST: derive PSID header flags (SID model + clock) from usf.psid and diff the rebuilt header vs the orig at bring-up — the write-log verdict is blind to headers, and hardcoding FLAGS_PAL_6581 was independently repeated in 3 composers before the ear caught it."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ecfcfba7-aa57-459e-907d-2b829fe8eee8
  modified: 2026-08-30T06:47:00.635Z
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

**Fourth occurrence, and the first where a verdict COULD see it
(2026-08-30, digi_organizer):** under the cycle-strict Mode-2 verdict
the clock flag is not merely audible, it is measurable — a raster-IRQ
tick runs at the FRAME rate, so an NTSC original is a 60 Hz stream and
the PAL-defaulted rebuild runs at exactly 5/6 speed. It presents as a
perfect content prefix at every horizon with the whole stream lagging,
which is almost indistinguishable from a one-time interrupt-phase slip
— and the two Sphere members sat parked for a round as "extensively
measured first-tick phase" before anyone read the header. A slip is an
OFFSET; this is a SLOPE. When a new composer's first cycle-strict
partial looks like phase, check the four header fields before
measuring anything. Signature recorded in ledger C40's diagnosis
table.
