# Gremlins pipeline

End-to-end rebuild of Rob Hubbard's *Gremlins* (1985, Adventure
International). Same shape as the Commando pipeline; bulk-cloned from
the Monty pipeline in commit `cbb86f6` and not yet ported to Gremlins's
actual engine semantics.

## Status (2026-05-15)

| Metric | Value |
|---|---|
| `lake build sidgen_gremlins` | passes (4 unused-variable warnings) |
| `sidgen_gremlins` writes | `pipelines/gremlins/build/gremlins.sid` |
| `writelog_grade.py` vs original | **Grade F, 5.8% snapshot match (87/1500)** |
| Hand-annotated disassembly | `docs/hubbard_gremlins_disassembly.s` |

The pipeline scaffold is in place (lakefile entry, codegen tree, extract
tree), but the codegen still encodes Monty/Commando engine behavior. It
fires note-load on frame 0; the original Gremlins engine defers it by
~2 frames via the `$16EB`/`$16EC` shared tempo counter. Driving to
Grade A is the next chunk of work.

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the
layout explanation.

## Roadmap to Grade A

Use `docs/hubbard_gremlins_disassembly.s` as the source of truth. Top
divergences vs the cloned codegen:

1. **First-frame note-load defer.** Gremlins's binary initialises
   `$16EB = $02` and `$16EC = $02`. `play`'s tempo counter starts at
   `$02`; after the first `DEC` it's `$01 ≠ $16EC`, so the note-load
   gate at `$1066-$106C` SKIPS for all three voices on frame 0. The
   note-load only fires when `$16EB` cycles back to `$02` (≈ frame 2).
   The V3 codegen currently fires on frame 0 unconditionally — this is
   the source of the massive frame-0 register divergence.
2. **`fx_flags` bit semantics.** Verified from the disassembly:
   - bit 0 ($01) — drum: kill envelope + ramp `freq_hi` down past mid-note
     (block at `$12F0-$132B`). Same as Action Biker / Commando.
   - bit 1 ($02) — skydive: DEC `v_fhi` on every odd `frame_counter`
     when `orig_dur >= $0C` and `v_dur < $08` (block at
     `$132C-$1357`). Currently emitted, double-check guards match.
   - bit 2 ($04) — octave arpeggio: alternate pitch ↔ pitch+12 by
     frame counter bit 0 (block at `$1358-$1388`).
   - bit 3 ($08) — linear PWM (`pw_lo += pwm_speed`, 8-bit wrap);
     cleared = bidirectional bounce $08/$0E in `pw_hi`. Cloned from
     Commando — verify Gremlins still picks this branch correctly.
3. **Per-note portamento (`v_porta`, `$16F5,X`).** Encoded in the
   pattern's "new-info" byte when its bit 7 is set: bits 1..6 = step
   delta, bit 0 = direction. Processed at `$12A9-$12EF`. NOT a per-
   instrument flag — must be carried through the USF score.
4. **Stale Monty leftovers in `Codegen.lean`.** Inline comments still
   reference `$84E5..$84EA` for PWM init values; those are Monty
   addresses. The actual Gremlins values come from `$16E5..$16EA`
   (verified from binary): `v_pwperiod = [$01, $01, $01]`, `v_pwdir =
   [$01, $00, $01]`. The emitted bytes are correct; the comments are
   wrong.
5. **`emitNL_SavePitchFhi` notenum-overlap alias-store.** Mirrors
   `v_pitch` into freq table slots 105/106 — a Monty quirk
   (`$84D3..$84D5` aliases V1/V2/V3 notenum). I saw NO equivalent
   overlap in Gremlins's disassembly. Verify and remove if the
   `$1789..$178B` instrument-effects bytes do not collide with
   `freq_table + 105/106`.
6. **PSID metadata.** Generated SID still has 7 subtunes (the music
   ones only). Original PSID has 26 (7 music + 19 sfx). Pipeline does
   not currently emit the sfx engine; restrict default subtune set or
   add a sfx codegen path.

## How to run

```bash
# 0-indexed; pass comma-separated subtune numbers to extract.
python -m pipelines.gremlins.extract.emit_usf            # subtune 0 only
python -m pipelines.gremlins.extract.emit_usf 0,1,2       # all three music
```

```bash
lake build sidgen_gremlins
./.lake/build/bin/sidgen_gremlins
```

```bash
python src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Gremlins.sid \
    pipelines/gremlins/build/gremlins.sid
```

## Why a separate pipeline from Commando

Two Hubbard SIDs from the same player era still differ in load-bearing
ways (PW bounds, pulsedelay init, fx-flag semantics). Cloning the
pipeline rather than parameterising it kept the Commando byte-perfect
invariant safe while Gremlins was being developed. The two pipelines
can be merged once a third Hubbard SID is wired through to validate
the abstraction.

See also: `docs/hubbard_gremlins_disassembly.s`,
`~/.claude/projects/-home-jtr-sidfinity/memory/project_gremlins.md`,
`reference_hubbard_pwm_bounds.md`.
