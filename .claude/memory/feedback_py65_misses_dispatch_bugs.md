---
name: feedback_py65_misses_dispatch_bugs
description: py65 verify_all is silent about bugs that change how often play() is called per second. md5-exact register sequence does NOT mean the SID sounds right on hardware. The ear is the final check.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

(2026-07 mechanics update: `verify_all` is no longer a py65 per-frame
verdict — it compares SID write-log streams from libsidplayfp, and
CIA-timed subtunes are captured per-play() via `--writelog-per-irq`.
The lesson below SURVIVES the rewrite: the flat `(reg,val)` verdict
is still blind to dimensions that don't change the write VALUES.)

The write-stream verdict compares what the engine WRITES, not how the
host DISPATCHES or RENDERS it. So:

- A wrong PSID `speed` bitmask on the REBUILD's header shows up only
  as a length/rate tail (same flat sequence, fewer plays in the
  window) — easy to misread, and historically it shipped unnoticed.
- A wrong SID-model / PAL-NTSC clock flag is COMPLETELY invisible to
  the verdict (same writes, different rendering) — see
  [[feedback_header_flags_audible]].
- Wrong CIA timer programming / RSID-vs-PSID dispatch differences can
  hide the same way.

A matching write sequence means: "if `play()` is called the same
number of times, the SID gets the same writes in the same order."
It does NOT mean: "the C64 player will call play() the same number
of times per second, on the same chip model."

**Why this matters:** I shipped HR's rebuild as `verify_all` all_ok
and the user pointed out by ear that subtune 0 played slower than
the original. Root cause: PSID speed field was hardcoded to $00
(all VBI 50 Hz), but HR's original is $0F (subtunes 1-4 = CIA timer
default 60 Hz from KERNAL). Fix in commit `325d211`.

**How to apply:** when shipping any rebuild to the user, especially
for new engines or after touching PSID header / dispatch logic,
suggest an ear-test. The user has called this out as the final
judge of correctness ([[feedback_ground_truth]]).

The principle layer: `verify_all` is a necessary but not sufficient
check. It's a regression net for register-stream correctness. It is
not a replacement for hearing the music on a real player.

Things the write-stream verdict can miss:
- PSID header flags: SID model, PAL/NTSC clock (fully invisible)
- PSID `speed` bitmask / CIA timer rate (shows only as a length tail)
- RSID vs PSID flag, NMI handling
- Any per-cycle timing that drives digi (covered separately by
  cycle-strict writelog verify for digi subtunes)
