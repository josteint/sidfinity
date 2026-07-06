---
name: feedback_header_flags_audible
description: "The write-log verdict is BLIND to PSID header flags (SID model 6581/8580, clock) — identical write streams sound different under a different chip model. Every composer must derive flags from the orig header via usf.psid; never hardcode FLAGS_PAL_6581."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ecfcfba7-aa57-459e-907d-2b829fe8eee8
---

The write-log verdict (Mode 1/2) compares only the `$D400-$D418` stream. It is
structurally BLIND to the PSID header's clock + SID-model flags — yet those
flags change how sidplayfp RENDERS the identical stream (6581 vs 8580 filter
curve, combined waveforms). A verified-FULL rebuild of an 8580 tune with a
hardcoded 6581 header sounds audibly wrong. Caught by the USER'S EAR on
Taurus_02 (2026-07-06) after the write stream verified FULL 86118/86118;
63% of the DMC corpus (6,729/10,676) is 8580-flagged, so nearly every shipped
DMC artifact had a wrong header.

**Why:** header metadata is part of artifact fidelity but outside the verify
target. Same class as [[feedback_py65_misses_dispatch_bugs]] (dispatch-rate
blindness) — the ear-test catches what the verdict can't.

**How to apply:**
- Every engine's extract captures header clock + SID model losslessly
  (`unknown`/PAL/NTSC/`both`, 0/6581/8580/`both`) into `PsidMeta.clock`/`.sid`
  (USF grammar admits INT or CNAME for `sid` since 2026-07-06).
- Every composer derives flags as `(clock_bits << 2) | (sid_bits << 4)` from
  `usf.psid` (the FC composer_asm form) — NEVER `flags=FLAGS_PAL_6581`.
- When bringing up a NEW engine's composer, diff the rebuilt header (flags,
  speed, songs, start) against the orig header as part of first verification.
- Ear-test remains mandatory for new engines: it is the only check covering
  verdict-blind dimensions.
