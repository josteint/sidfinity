---
name: feedback_strict_writestream_always
description: "USER POLICY: every SID always gets the STRICT write-stream match. Never propose relaxing the verdict (audio-equivalence / inaudible-write drops). Ledger C15 removed; design parked in the_move-1_plan.md for the Move-1 era only."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: c3f0029a-29c7-430e-af15-2357c5061c39
---

**Every SID always gets the STRICT `(reg,val)` write-stream match.** (User
decision 2026-07-01, given while reviewing the DMC family-4 leadin.)

**Why:** the write-log verdict is the project's sacred ground truth
([[feedback_no_snapshot_verdict]], [[feedback_ground_truth]]). Verdict
relaxations — "audio-equivalence", dropping inaudible idle-freewheel writes,
tolerance criteria — erode that ground truth one exception at a time, and each
one is a criterion change that would silently redefine what "FULL" means
mid-corpus.

**How to apply:**
- Never propose an audio-equivalence / inaudible-writes verdict relaxation
  during per-engine migration work. The former ledger C15 is REMOVED (a ⛔
  tombstone remains in the ledger index); its design is parked in
  `docs/the_move-1_plan.md` under "Move-1-era considerations" and may be
  *considered* only around Move 1, when most/all engines are uready — not before.
- When an idle/gate-off freewheel divergence blocks a member, the answer is to
  REPRODUCE the writes: the CORE TENET explicitly permits reproducing the
  original's mechanism in the COMPOSER (DMC `idle_wave`/resting-voice, family-4
  `f4_idle_notes` are precedents). USF stays clean — derive or carry the
  mechanism composer-side, never as opaque USF leftovers.
- The same instinct applies to any other verdict-tolerance idea (cf. the
  song_exact/1.0x lever, still pending ratification): criterion changes are the
  user's call, surfaced BEFORE use, never adopted to make a number go up.
