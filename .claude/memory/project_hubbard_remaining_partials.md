---
name: project_hubbard_remaining_partials
description: "The 3 Hubbard subtune families still write-log-partial after Monty was fixed (2026-06-07): Human_Race(4)[+probably Battle(1)] = spurious bidirectional PWM because the composer zeros the per-voice PWM counters (v_pwperiod/v_pwdir) that the engine seeds from the binary $0DC8 (root found via pc-trace; NOT the CIA/timing red herring); Devils_Galop(1) = a dropped V3 freq write. All were false-passed by the old snapshot verdict."
metadata: 
  node_type: memory
  type: project
  originSessionId: 34baf59d-942f-49ab-b1d7-123e07963888
---

After Monty went 19/19 (the `master_vol_every_frame` fix), the write-log
verdict leaves **6 Hubbard subtunes** failing — all previously false-passed by
the deleted py65 snapshot verdict ([[feedback_no_snapshot_verdict]]). Two
distinct causes:

## Human_Race (4) [+ probably Battle (1)] — PWM-counter seed not replicated
ROOT CAUSE FOUND 2026-06-07 via a pc-trace dig (siddump `--pc-trace FILE
START END`, ground truth). **It is NOT a CIA/timing/first-frame issue** — earlier
"V1 one play late" / "CIA dispatch phase" theories were ALL wrong, artifacts of
an error-prone per-IRQ writelog comparison. CIA (speed=0x0f) is fine; ignore it.

Method that worked: pc-trace BOTH orig (play entry `$0986`) and rebuild (`$1003`),
segment by play entry, extract the per-`play()` SID-write sequence from the trace
(reg = store base + Y; the trace line carries PC, A, X, Y). The trace shows PC +
registers so you can follow exact branches. This per-`play()` ground-truth
comparison is the right tool — NOT my ad-hoc `--writelog-per-irq` parsing (which
was mis-aligned and produced the bogus "V1 late" + "88%/90%" numbers).

The real divergence (Human_Race sub0):
- **play[0] is byte-identical** (V1 and V2 both load correctly — "V1 late" was false).
- PW-writes per play: **orig `[4,0,0,0,0,0,0,0,0,0]`** (PW written only on the
  note-load), **rebuild `[4,4,0,4,0,4,0,4,0,4]`** (modulates PW every other frame).
- So the rebuild runs **spurious bidirectional PWM** on instrument 0 (`pwm_speed=
  0x81`, `fx_flags=0x00`; used by V1/V2's first notes: ctrl=41 AD=3c SR=9f).

ROOT (disasm `pipelines/hubbard/human_race/disassembly.s` lines 158-159):
the engine seeds the per-voice PWM counters from the BINARY at `$0DC8..$0DCD`:
`v_pwperiod=[0,1,$1D]`, `v_pwdir=[1,0,0]`. The composer ZEROS them — Human_Race
has `seed_overlap=False`, and the `ini1` loop (composer.py ~1574) zeros
`v_pwperiod`/`v_pwdir`. With `v_pwperiod=0` the bidir PWM (period = pwm_speed &
$1F = 1) underflows immediately → modulates every other frame.

CAVEAT (not fully resolved): seeding explains V2 ([1] vs 0) and V3 ([$1D] vs 0),
but V1's seed is 0 in BOTH orig and rebuild, yet orig still doesn't modulate V1.
So there is likely a SECOND factor for V1 — probably the bounded-PWM
write-at-bound behavior (inst 0's pw_hi=08 = min bound; orig may flip direction
WITHOUT writing when a step would exceed the bound, while the composer's
`fxp_bidir` always writes via `fxp_wr`). Verify both.

**Next step if resumed:** (1) seed `v_pwperiod`/`v_pwdir` from the binary
`$0DC8` for Human_Race instead of zeroing (the ovseed/seed_overlap path, or a
dedicated seed); (2) check whether the composer's bounded PWM writes at the
bound when it shouldn't. Verify with the per-`play()` pc-trace comparison above
(target: rebuild PW-per-play == orig `[4,0,0,...]`).

## Devils_Galop (1) — dropped V3 frequency write (DIFFERENT bug)
- Devils is **vblank** (speed=0), so NOT the CIA issue. Per-IRQ sub0 chunk 5:
  orig `V3flo=4e V3fhi=03 V3fhi=0d V3flo=09` (a glide/double-step on V3), the
  rebuild writes only `V3flo=4e V3fhi=03` — it drops the second V3 freq update.
  A glide/effect-emit divergence on V3. Separate investigation.

## Tooling note
`tools/find_first_divergence.py` had a duration-parse bug (crashed on
Songlengths `M:SS.mmm` fractional seconds via `int(s)`); fixed to `float(s)`
2026-06-07.
