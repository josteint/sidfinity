---
name: project_hubbard_remaining_partials
description: "The 3 Hubbard subtune families still write-log-partial after Monty was fixed (2026-06-07): Human_Race(4)+Battle(1) = CIA-timed note-onset one-frame timing shift (90% byte-exact, py65 logic is correct); Devils_Galop(1) = a dropped V3 freq write. All were false-passed by the old snapshot verdict."
metadata: 
  node_type: memory
  type: project
  originSessionId: 34baf59d-942f-49ab-b1d7-123e07963888
---

After Monty went 19/19 (the `master_vol_every_frame` fix), the write-log
verdict leaves **6 Hubbard subtunes** failing — all previously false-passed by
the deleted py65 snapshot verdict ([[feedback_no_snapshot_verdict]]). Two
distinct causes:

## Human_Race (4) + Battle_of_Britain (1) — CIA-timed note-onset timing shift
- **Both are CIA-timed**: `Human_Race` PSID speed=`0x0f` (subtunes 1-4 CIA),
  `Battle_of_Britain` speed=`0x01`. (Commando/Monty/Devils are vblank speed=0
  and that's the discriminator — the timing shift tracks CIA timing.)
- Human_Race sub0: **180/199 per-`play()` chunks are byte-identical (90%)**
  with the play streams ALIGNED (shifting ±1 play → 0% match, so it is NOT a
  dispatch/capture offset; the plays line up). The 19 mismatches are: chunk 1
  (V1's first note loads one frame late) + **9 regular pairs `(i,i+1)` at note
  onsets** (~every 10-50 chunks) — i.e. the note-onset timing is one frame off
  at note boundaries.
- **py65 (logic, RAM-independent — tested RAM=$00 and $FF identical) loads V1
  correctly on the first play.** So the rebuilt ENGINE LOGIC is right; the
  divergence is in the first-play / CIA-dispatch interaction that py65
  structurally cannot model (`feedback_py65_misses_dispatch_bugs`).
- Ruled out: uninitialized-RAM read (RAM fill makes no difference; init zeros
  v_dur via the `ini1` loop at composer.py ~1574); missing CIA-timer write
  (neither orig nor rebuild writes $DC04/$DC05 — both use libsidplayfp's
  default ~50Hz CIA); global play-offset (aligned beats both shifts).
- Orig mechanism (`disassembly.s`): init silences V1+V2 ctrl + vol=$0F + sets
  `$0DD6=$40` (bit-6 "first-frame setup pending"); play frame 1 zeros per-voice
  state then the tick fires so both voices load on the first tick. The rebuild
  also omits the init's V1+V2 ctrl-silence.
- **Next step if resumed:** trace libsidplayfp's PSID-CIA dispatch of the
  first play vs py65 (why the first/onset play loads V1 a frame later under
  CIA), and/or replicate the orig's bit-6 "zero per-voice state on frame 1" +
  init ctrl-silence in the composer. This is a deep CIA-dispatch/first-frame
  dig, not a one-line fix like Monty.

## Devils_Galop (1) — dropped V3 frequency write (DIFFERENT bug)
- Devils is **vblank** (speed=0), so NOT the CIA issue. Per-IRQ sub0 chunk 5:
  orig `V3flo=4e V3fhi=03 V3fhi=0d V3flo=09` (a glide/double-step on V3), the
  rebuild writes only `V3flo=4e V3fhi=03` — it drops the second V3 freq update.
  A glide/effect-emit divergence on V3. Separate investigation.

## Tooling note
`tools/find_first_divergence.py` had a duration-parse bug (crashed on
Songlengths `M:SS.mmm` fractional seconds via `int(s)`); fixed to `float(s)`
2026-06-07.
