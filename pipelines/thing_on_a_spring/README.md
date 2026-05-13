# ThingOnASpring on the Run pipeline

End-to-end rebuild of Rob Hubbard's *ThingOnASpring on the Run* (1985) SID. Same shape
as the Commando pipeline; cloned and extended for ThingOnASpring's engine quirks
(skydive effect, pulsedelay/pulsedir initial state, notenum/freq-table
overlap aliasing, different HR threshold).

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 3 (the music tracks; PSID #1–#3 in the original) |
| Verification | siddump 98.8% snapshot match; py65 0-divergence over 1500 frames |
| Grade | A |

The remaining ~1.2% siddump gap is `libsidplayfp` emulator subtleties
(CIA timer, cycle-exact bus contention) that don't affect what the SID
chip outputs.

The original PSID claims 19 subtunes; the other 16 are sound effects
this pipeline doesn't ship.

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the layout
explanation. The ThingOnASpring-specific differences are inside the codegen:

| File | ThingOnASpring-only addition |
|---|---|
| `codegen/ThingOnASpring/USF.lean` | `skydive : Bool` field on `USFInstrument` |
| `codegen/ThingOnASpring/Codegen.lean` | Skydive emit block; v_pitch alias-store into freq table; PWM init data extracted from binary; HR threshold = 1 |
| `extract/engine_model.py` | Extracts `has_skydive` from fx_flags bit 1 |
| `extract/emit_usf.py` | Emits `skydive := true/false` for each instrument |

## How to run

Regenerate `SongData.lean` from the original — by default rebuilds subtune 0
(the title music PSID #1). Pass comma-separated 0-indexed subtune numbers
to override:

```bash
python -m pipelines.thing_on_a_spring.extract.emit_usf            # subtune 0 only
python -m pipelines.thing_on_a_spring.extract.emit_usf 0,1,2       # all three music tracks
```

Build and run:

```bash
lake build sidgen_thing_on_a_spring
./.lake/build/bin/sidgen_thing_on_a_spring
```

Grade against the original:

```bash
python src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Thing_on_a_Spring.sid \
    thing_on_a_spring.sid
# Expected: Grade A, snapshots 98.8% (1482/1500)
```

## Why a separate pipeline from Commando

Two Hubbard SIDs from the same player era still differ in load-bearing
ways (PW bounds, pulsedelay init, fx-flag semantics). Cloning the
pipeline rather than parameterising it kept the Commando byte-perfect
invariant safe while ThingOnASpring was being developed. The two pipelines can
be merged once a third Hubbard SID is wired through to validate the
abstraction.

See also: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
and `reference_hubbard_pwm_bounds.md` for the load-bearing quirks.
