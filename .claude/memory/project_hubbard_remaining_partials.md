---
name: project_hubbard_remaining_partials
description: "FULLY RESOLVED 2026-06-07: the entire Hubbard family is instruction-sequence exact (regression 71/71 ok, 0 partial, 0 regressed). Two fixes this day: (1) CIA-aware per-play() verdict (Human_Race 5/5 + Battle 1/1 — verify_all routes PSID speed!=0 subtunes through siddump --writelog-per-irq, cycle-base-corrected, frame-0 init drop); (2) Devils_Galop master_vol_every_note knob (1/1). Devils was NOT a 'dropped V3 freq write' (that came from the unreliable per-irq tooling) — the engine writes $D418=$0F on every note-load and the rebuild only wrote it at init."
metadata: 
  node_type: memory
  type: project
  originSessionId: 34baf59d-942f-49ab-b1d7-123e07963888
---

## CIA-aware verdict — IMPLEMENTED 2026-06-07 (option (a), the per-play verdict)
Plan `docs/cia_aware_verdict_plan.md` is now DONE. HR 5/5 + Battle 1/1 pass.
What shipped (all in this repo now, not reverted):
- **siddump per-irq splitter fixed** (`tools/siddump.cpp`). The bug was a
  cycle-origin mismatch: play-entry cycles are ABSOLUTE (PHI1 clock, recorded in
  `c64cpu.h::cpuRead`), write-log cycles are RELATIVE to a per-frame
  `m_cycleBase` (`c64sid.h`). The splitter now subtracts the base
  (`rel = abs - base`). Base plumbed out via new `getWriteLogCycleBase()`
  (c64sid.h → player.{h,cpp} → sidplayfp.{h,cpp}), mirroring `getWriteLog`.
- **Init prefix dropped, frame-0 ONLY.** Empirically (via temporary
  `--per-irq-debug`, kept as a diagnostic flag): frame 0's write-log holds 4
  init writes (gate-off/vol-set tail) BEFORE the first play-entry; those are
  dropped once. Pre-entry writes in LATER frames are legitimate straddle tails
  (a play that began in the prior frame) and are KEPT — `firstIrqChunkPending`
  guards this. Defensive: a zero-entry frame's writes are emitted as a
  continuation chunk so nothing is ever silently dropped (matters only for
  slower-than-50Hz CIA; HR/Battle are faster so never hit it).
- **Comparison = flatten + flat-prefix.** The per-irq chunk boundaries are used
  ONLY to drop init; the verdict flattens all `|I` chunks and compares the flat
  `(reg,val)` sequence (flattening preserves global cycle order, so straddle
  tails landing in the "wrong" chunk are still in the right global position).
  This is `compare_instruction_stream`/`_music_ok` reused unchanged.
- **verify.py integration.** `verify_all` classifies each subtune by the PSID
  `speed` bit (`_cia_speed` + `_is_cia_subtune`): CIA→`writelog_per_irq_capture`
  (`_capture_music_irq`, cache kind `music_irq`); vblank→flat `music_wl`
  unchanged; digi unchanged. Gated tightly on the original's speed field.
- **Validated against the pc-trace oracle** (`/tmp/validate_perirq.py` pattern,
  §4): per-irq flattened stream == oracle, write-for-write, for HR (54/54, 352
  writes) AND Battle (54/54, 489 writes), orig + rebuild. Orig-vs-rebuild flat
  matches at full-song scale (HR 8938/10571, Battle 30101 writes).

KEY INSIGHT that unlocked it: the straddle problem (a play() spanning two
siddump frames) is a NON-ISSUE for a FLAT comparison — only per-chunk alignment
would care. So the per-irq tool only needs to mark where init ends; everything
else flattens. The first reverted attempt failed by trying to align per-chunk
and by adding a too-broad init-skip; the fix is frame-0-only skip + flat compare.

After Monty went 19/19 (the `master_vol_every_frame` fix), the write-log
verdict leaves **6 Hubbard subtunes** failing — all previously false-passed by
the deleted py65 snapshot verdict ([[feedback_no_snapshot_verdict]]). Two
distinct causes:

## Human_Race (4) [+ probably Battle (1)] — ENGINE IS CORRECT; verdict is CIA-confounded
FINAL CONCLUSION 2026-06-07: **there is no engine bug.** A correct per-`play()`
comparison (pc-trace, segment by play-entry `$0986`/`$1003`, extract SID writes
via the EFFECTIVE address in the trace's `[d4xx]` brackets) shows the rebuild's
write sequence **matches the original write-for-write over 54/54 plays**. py65 (logic)
agrees. Human_Race is instruction-sequence exact in the Mode-1 sense.

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
- **play[0] matches write-for-write** (V1 and V2 both load correctly — "V1 late" was false).
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

## Devils_Galop (1) — RESOLVED: master-vol written on every note-load
NOT a dropped V3 freq write (that was the unreliable per-irq tooling lying —
same lesson as Human_Race). Ground-truth `find_first_divergence` showed at flat
pos 572 the orig writes `$D418=$0F` (master vol) that the rebuild omits; the
rebuild's V3 note-load then matches orig write-for-write, just shifted by one.
ROOT: the engine writes `$D418=$0F` on EVERY note-load — once per voice that
advances a pattern entry — from `$13B7`, inline in the pattern-advance path
(`L_138B`), with the clamp NOP'd at runtime so the value is constant $0F. The
rebuild only wrote $D418 at init.
FIX: new knob `master_vol_every_note` (EngineConfig + USF init_behavior),
mirroring `master_vol_every_frame` but per-note. Fills the codec's existing
`; %%MASTER_VOL_EVERY_NOTE%%` sentinel with a fixed `lda #$0F; sta $d418`,
resolved in `_resolve_codec_note_asm` BEFORE the fade pass (else the fade's
empty-replacement clobbers it). The progressive-fade path can't model it (its
vol_progress would drop volume; Devils stays $0F). devils_galop config sets
`master_vol_every_note=0x0F`. Also added both every_frame/every_note to
`_PARAMS_SKIP_CONFIG` (they belong in init_behavior, not params — the params
copy was a dead duplicate, an oversight from when every_frame was added).
Result: Devils 1/1, Hubbard 71/71.

## Tooling note
`tools/find_first_divergence.py` had a duration-parse bug (crashed on
Songlengths `M:SS.mmm` fractional seconds via `int(s)`); fixed to `float(s)`
2026-06-07.
