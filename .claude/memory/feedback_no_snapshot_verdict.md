---
name: feedback_no_snapshot_verdict
description: "The verdict is ALWAYS the SID write-log, NEVER a per-frame register-state snapshot. Snapshot-per-frame verification is Trap A — it was reinvented in pipelines/hubbard/verify.py and removed 2026-06-07 after false-passing 25 Hubbard subtunes (incl. all of Monty's multispeed)."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 34baf59d-942f-49ab-b1d7-123e07963888
---

NEVER verify a rebuild by snapshotting per-frame SID register STATE
(md5 of `$D400-$D418` at each frame boundary). That is Trap A from the
CORE TENET. The user has fought this repeatedly and deleted such tools
before. The verdict is ALWAYS the SID WRITE-LOG stream via
`siddump --writelog` (libsidplayfp = ground truth), compared as the
`(reg,val)` sequence over the overlap (the `find_first_divergence` /
`compare_instruction_stream` method).

**Why:** a per-frame STATE snapshot loses (a) within-frame write ORDER
(gate edges, $D418 clicks, ADSR delay) and (b) anything py65 can't model
— above all MULTISPEED (CIA-paced play()). Two SIDs can reach the same
end-of-frame state via different write sequences or different play()
rates, so the snapshot gives FALSE PASSES on real bugs.

**How to apply:** if you ever find yourself capturing register state per
frame and md5-ing it for a verdict, STOP — you are reinventing the
deleted tool. Use the write-log. py65 `capture()` is fine for EXTRACTION
(decoding instruments from a trace) but must NEVER be the verdict.

**The 2026-06-07 incident:** `pipelines/hubbard/verify.py`'s `verify_all`
was still a py65 per-frame-snapshot md5 verdict (it was never deleted).
It reported "71/71 Hubbard subtunes OK." Converging the verdict on the
write-log revealed it had been silently FALSE-PASSING 25 subtunes:
- Monty_on_the_Run (all 19) — multispeed (CIA); the rebuild's play()
  rate differs from the original. py65 is frame-granular and can't see
  multispeed, so it emulated both identically-wrongly → snapshot matched.
- Human_Race (4), Battle_of_Britain (1), Devils_Galop (1) — the rebuild's
  write stream diverges (e.g. first note loads one play() late / within-
  frame order), but the end-of-frame STATE reconverged so the snapshot
  passed.
These are REAL divergences (not byte-exact under ground truth), now
correctly flagged. See [[feedback_verification_modes]] and
[[feedback_py65_misses_dispatch_bugs]].
