---
name: feedback_verification_modes
description: "TRIPWIRE — the project has EXACTLY TWO verification modes. Mode 1 (frame-by-frame instruction sequence) for tracker music. Mode 2 (cycle-exact) for digi. Three traps to avoid — A: snapshot SID registers instead of capturing the write sequence; B: chase cycle-exactness when only Mode 1 is needed; C: misread siddump frame-bucket misalignment as engine divergence. Pinned because falling into A/B/C burns sessions for nothing."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

The project has EXACTLY TWO modes for declaring a rebuild byte-exact.
Anything else is wrong. Most of the failure modes we've burned hours
on were attempts to do something more (or less) than these two.

## Mode 1 — frame-by-frame instruction sequence (tracker music)

**Every time the PSID `play()` vector is invoked, the engine emits a
finite, ordered sequence of writes to `$D400-$D418`. Mode 1 declares
the rebuild equivalent if and only if that per-play() sequence matches
the original, frame by frame, for the entire song.**

- Within a frame: the ORDER of writes matters (per
  [[feedback_sid_hidden_state_write_order]] — gate edges, test bit,
  ADSR delay bug, $D418 clicks all observe order).
- Within a frame: the CYCLE TIMESTAMPS of writes do NOT matter. Same
  writes in the same order at slightly different cycles within the
  frame produce the same audible output.
- Across frames: per-frame sequences must match in order.

Mode 1 is what 99% of HVSC needs. All FC, Hubbard, Companion, etc.
tracker engines verify under Mode 1.

**Tooling for Mode 1:**
- `tools/siddump --writelog` — captures `(cycle, reg, val)` per frame.
- `pipelines.hubbard.verify_cycle.compare_instruction_stream` — flat-
  prefix match over `(reg, val)` (cycle dropped). The right comparator.
- `tools/find_first_divergence.py` — locates the first mismatching
  `(reg, val)` position; reports the frame and the register's role.

## Mode 2 — cycle-exact (digi only)

For tunes with digi (sample playback via $D418 strobe, $D40C-style
1-bit, etc.), the cycle-precise timing of writes IS the signal. Mode 2
requires every `(cycle, reg, val)` tuple to match exactly.

**Tooling for Mode 2:**
- `tools/siddump --writelog` — same capture, used differently.
- `pipelines.hubbard.verify_cycle.compare_strict` — full per-frame
  `(cycle, reg, val)` equality. The right comparator FOR DIGI ONLY.

Chimera is the worked example. See [[project_chimera]].

## Trap A — snapshot the SID registers instead of the write sequence

The early-project verifier captured a per-frame snapshot of the SID
register state (`getSidStatus(0, regs)`) and md5'd the sequence of
snapshots. This LOSES within-frame writes and within-frame ORDER.
Two engines that converge to the same final state per frame can
still produce audibly different output if the WAY they get there
differs (test-bit strobe, $D418 click, etc.).

We did this for half the project before realising it was not strict
enough. The fix was to capture the full write log
(`engine.enableWriteLog`) and compare sequences, not snapshots.

**Rule: never trust register-snapshot-based verification for Mode 1.**
The verdict is the WRITE SEQUENCE, not the END STATE.

## Trap B — chase cycle-exactness for music

When investigating a Mode-1 divergence, the temptation is to look at
cycle timestamps and call mine "30 cycles late" or similar. For
tracker music, cycle position WITHIN a frame is observation, not
signal. mine's effect chain may take a different cycle count than
orig's and still be musically equivalent. Don't try to make cycles
match for music.

**Rule: in Mode 1 investigations, ignore within-frame cycle deltas
unless you're investigating digi.**

## Trap C — observation misalignment (siddump frame buckets vs IRQs)

`tools/siddump` runs `engine.play(cyclesPerFrame)` per loop iteration
with `cyclesPerFrame = 63×312 + 32 = 19688` — but that value counts
**event-scheduler ticks** (`c64::clock()` events, each <1 CPU cycle),
NOT CPU cycles. A siddump "frame" therefore advances only **~18,000
CPU cycles**, LESS than the 19,656-cycle PAL play period, so the PSID
`play()` runs ~0.92× per siddump frame: usually 1, regularly 0,
rarely 2. (An earlier version of this memory derived the drift from
"+32 margin, 19688 > 19656, so sometimes 2" — that is the WRONG
DIRECTION; see docs/the_core_tenet.md Trap C and
[[reference_siddump_frame_cycles]], which records this was mis-derived
twice.)

This affects two things:

1. **Writelog per-frame buckets are misaligned with PSID play()
   invocations.** Same (reg, val, order) sequence can land in
   slightly different siddump "frame" buckets between mine and orig.
   `compare_instruction_stream`'s flat-sequence comparison is ROBUST
   to this (it concatenates across frames; the flat sequence is
   identical). So writelog ground truth is fine.

   **NEW (commit ca1623f):** `siddump --writelog-per-irq` emits one
   `|I:` chunk per PSID `play()` invocation by hooking the play
   vector entry and bucketing writes by IRQ cycle. This eliminates
   the misalignment at the source for writelog observation. Use it
   when you want IRQ-aligned writelog comparison.

2. **`tools/state_diff.py` (memwatch snapshots) ARE NOT ROBUST.**
   memwatch reads RAM at the end of each `engine.play()` call. If
   mine processed 1 IRQ and orig processed 2 IRQs (or 0) in the same
   siddump frame, the captured state can differ even when both engines
   are equivalent under Mode 1. Hawkeye sub 10 burned a chunk of one
   session on a `nootcount[V1]` "divergence" at f277 that turned out
   to be IRQ-count drift (orig's `$90F6` per-frame counter was frozen
   at f278 — 0 IRQs that siddump-frame).

   Partially mitigated (commit c97ec9b): `siddump --memwatch` now
   appends `|P:<count>` per frame with the PSID `play()` invocation
   count, and `state_diff.py` warns when cumulative IRQ counts differ
   between mine and orig at a reported "divergence" frame (the
   smoking-gun signal that you're in Trap C). Full mitigation
   (IRQ-aligned memwatch sampling) is the same approach as
   `--writelog-per-irq` but for memwatch — TODO.

**Rule: state_diff produces HINTS, not verdicts.** A state divergence
at a specific siddump frame may be real OR may be IRQ misalignment.
Cross-check against the writelog first-divergence position
(`find_first_divergence.py`) — if writelog matches but state_diff
"finds" a divergence, it's Trap C. The IRQ-count delta printed by
state_diff is the deciding signal.

The principled fix is play()-synchronous sampling: hook the PSID
play() entry, buffer writes/memwatch per invocation, emit one record
per play() call. Tracked in [[tools/INVESTIGATION_BACKLOG.md]].

## Quick decision tree

| Question | Answer |
|---|---|
| Mode 1 or Mode 2 for this tune? | Digi → 2. Otherwise → 1. |
| What's the comparator? | Mode 1: `compare_instruction_stream`. Mode 2: `compare_strict`. |
| What's ground truth? | `tools/siddump --writelog`. ALWAYS. |
| Memwatch state diverged but writelog matches? | Trap C. Ignore the state hint; the engines are equivalent. |
| Per-frame writelog buckets differ but flat sequence matches? | Trap C. Mode 1 verdict is PASS. |
| Two writelog (reg, val) sequences differ at position N? | Real divergence. Use the divergence position to localize. |

## Related

- [[feedback_observation_drift]] — original framing of Trap C for
  writelog buckets (this memory absorbs and extends it).
- [[feedback_sid_hidden_state_write_order]] — Mode 1's
  within-frame ORDER constraint.
- [[feedback_py65_misses_dispatch_bugs]] — py65 lacks CIA modelling
  → never the verdict; libsidplayfp is.
- [[feedback_ground_truth]] — sidplayfp is ground truth, not py65.
- [[feedback_writelog_divergence_recipe]] — the investigation
  protocol for Mode 1 divergences.
- [[feedback_deconstruct_not_reproduce]] — CORE TENET: the writelog
  stream is the target. This memory operationalises that into the
  two modes.
