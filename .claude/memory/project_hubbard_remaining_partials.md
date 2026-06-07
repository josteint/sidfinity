---
name: project_hubbard_remaining_partials
description: "Hubbard subtunes the regression marks partial after Monty was fixed (2026-06-07). Human_Race(4)[+prob Battle(1)]: ENGINE IS CORRECT — per-play() write sequence is byte-identical to orig (54/54 via pc-trace); they fail only because they are CIA-timed (speed!=0) and siddump's flat 50Hz capture buckets init/first-play out of phase. Fix is the VERDICT (verify CIA tunes per-play), not the engine. (Earlier 'CIA-dispatch' and 'PWM-seed' theories were both wrong — buggy trace parsing.) Devils_Galop(1): a genuine dropped-V3-freq-write bug (vblank, separate)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 34baf59d-942f-49ab-b1d7-123e07963888
---

## CIA-aware verdict — full implementation plan in `docs/cia_aware_verdict_plan.md`
A complete, self-contained plan for option (a) (reliable per-play verdict) is in
`docs/cia_aware_verdict_plan.md`: root cause of the `--writelog-per-irq`
cycle-origin bug, the exact fix + plumbing, the pc-trace validation oracle, the
verify.py integration, the test matrix, and the session's pitfalls. Start there.

## CIA-aware verdict — ATTEMPTED, hit a tooling obstacle (2026-06-07)
Tried to make `verify_all` verify CIA tunes per-`play()` so HR/Battle pass.
Reverted; the lightweight per-`play()` segmentation tools are not reliable enough:
- `siddump --writelog-per-irq` splits the per-frame write-log by play-entry
  cycles, but: (a) the play-entry cycles are ABSOLUTE while write-log cycles are
  RELATIVE to a per-frame `m_cycleBase` (c64sid.h) — different origin; (b) the
  init/first-play boundary (whether init writes land in frame 0's write-log) is
  unclear; (c) fixing (a) via subtracting `m_cycleBase` STILL mis-split orig vs
  rebuild (chunks ≠ the pc-trace play boundaries). Play-detection is 1/frame
  (not spurious), so the issue is the cycle/boundary mapping, which I couldn't
  nail empirically this session.
- `siddump --pc-trace` (segment by play-entry PC) is RELIABLE (it's what proved
  54/54) but is far too heavy for a full-song verdict (~16k trace lines/frame).
- All overlay/siddump WIP was reverted to keep the tree clean.
Options for next time: (a) nail the per-irq cycle/boundary mapping with careful
empirical checks against the pc-trace ground truth; (b) a Python flat-stream
ALIGNMENT verdict (find the offset that aligns orig vs rebuild flat write-logs,
since the play streams are identical modulo the init prefix); or (c) pragmatic:
mark HR/Battle engine-verified via the one-time pc-trace proof and exempt them
from the siddump-flat verdict with a documented justification (the engine is
proven correct; the gap is purely the observation tool).

After Monty went 19/19 (the `master_vol_every_frame` fix), the write-log
verdict leaves **6 Hubbard subtunes** failing — all previously false-passed by
the deleted py65 snapshot verdict ([[feedback_no_snapshot_verdict]]). Two
distinct causes:

## Human_Race (4) [+ probably Battle (1)] — ENGINE IS CORRECT; verdict is CIA-confounded
FINAL CONCLUSION 2026-06-07: **there is no engine bug.** A correct per-`play()`
comparison (pc-trace, segment by play-entry `$0986`/`$1003`, extract SID writes
via the EFFECTIVE address in the trace's `[d4xx]` brackets) shows the rebuild's
write sequence is **byte-identical to the original over 54/54 plays**. py65 (logic)
agrees. Human_Race is byte-exact in the Mode-1 sense.

Everything below this line was a WRONG theory caused by buggy trace parsing —
kept only as a cautionary trail. The verdict (`verify_all` / `find_first_divergence`
via `siddump --writelog` flat) FAILS Human_Race because it is **CIA-timed**
(speed=0x0f): siddump's 50Hz-frame flat capture buckets the init + first play()
differently for orig (long init → first play at cycle ~15714) vs rebuild (short
init → cycle ~1403), so the two flat streams start at different points and
"diverge" at position 0. That's a capture/observation artifact (Trap C for CIA
tunes), not the engine.

THREE parsing bugs burned a long session here — beware:
1. `--writelog-per-irq` chunk0 ≠ play[0] (it folds init in, differently per
   tune) → bogus "V1 one play late" + "88%/90% match".
2. A PW-write regex that matched only `STAay` (store abs,Y) and missed the
   bounded-PWM `STAax` (store abs,X at orig $0BF7/$0BFE) → bogus "orig
   [4,0,0,..] vs reb [4,4,0,..] PWM modulation bug".
3. The disasm COMMENT "v_pwperiod=[0,1,$1D]" is a runtime value; the load-time
   bytes at $0DC8 are all zero (same as the composer) — the "seed" was a non-fix.
THE RELIABLE METHOD: pc-trace both, segment by play-entry, compare the
effective-address `[d4xx]` writes per play. Use THAT, not `--writelog-per-irq`
parsing or instruction-mnemonic regexes.

REAL fix needed (verdict, not engine): make `verify_all` verify CIA-timed tunes
(speed != 0) via the per-`play()` comparison above instead of the siddump-flat
stream, OR ear-test + accept. This fixes Human_Race + Battle (both CIA) together.

--- OBSOLETE WRONG THEORY BELOW (PWM seed) — ignore, kept as cautionary trail ---
## (WRONG) PWM-counter seed not replicated
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
