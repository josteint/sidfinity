---
name: feedback_py65_misses_dispatch_bugs
description: py65 verify_all is silent about bugs that change how often play() is called per second. md5-exact register sequence does NOT mean the SID sounds right on hardware. The ear is the final check.
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`verify_all` (in `pipelines/hubbard/verify.py`) calls play() once per
simulated frame, regardless of how a real PSID player would dispatch
it. So:

- An incorrect PSID `speed` bitmask (VBI vs CIA1 timer dispatch) is
  invisible to verify_all even though it changes the actual playback
  tempo on hardware.
- Wrong CIA timer programming would also be silent.
- A wrong RSID/PSID flag affecting NMI vs IRQ-driven dispatch would
  be silent.

md5-exact register sequence means: "if `play()` is called the same
number of times, the SID gets the same writes in the same order."
It does NOT mean: "the C64 player will call play() the same number
of times per second."

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

Things py65 verify can miss:
- PSID `speed` bitmask
- CIA1/CIA2 timer programming in init
- RSID vs PSID flag
- NMI handling
- Any per-cycle timing that drives digi (covered separately by
  cycle-strict writelog verify for digi subtunes)
