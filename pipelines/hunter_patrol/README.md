# Hunter Patrol pipeline

End-to-end rebuild of Rob Hubbard's *Hunter Patrol* (1985 Mastertronic) SID.
Original is parsed, lifted into structured USF, then re-emitted as a fresh
PSID driven by our own V3 player. Same shape as the Commando and Monty
pipelines.

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 1 (PSID single-subtune SID) |
| Build | end-to-end clean: `python -m pipelines.hunter_patrol.extract` → `lake build sidgen_hunter_patrol` → SID at `pipelines/hunter_patrol/build/hunter_patrol.sid` |
| Grade | F (0/1500 snapshots) — starting state, not byte-faithful |

This is the **bring-up state** of the pipeline: scaffolding is in place,
the Hubbard binary parses, the Lean codegen produces a SID, and grading
runs. The rebuild does not yet match the original musically — see
**Known divergences** below.

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the
layout walkthrough. Hunter-Patrol-specific bits live in:

| File | Hunter-Patrol-only content |
|---|---|
| `extract/engine_model.py` | `SID_PATH` points at `Hunter_Patrol.sid`; `has_skydive` propagated from fx_flags bit 1 |
| `extract/emit_usf.py` | `HUNTER_PATROL_FT_BASE = 0xA32D` (freq table); 1-subtune defaults; `engineQuirks.dynamicFreqEntries = []` (Hunter Patrol doesn't alias freq slots) |
| `codegen/HunterPatrol/USF.lean` | `skydive` field on `USFInstrument` |
| `codegen/HunterPatrol/Codegen.lean` | Skydive emit; PWM bounds $08/$0E |

The annotated disassembly that drives engine understanding is at
`docs/hubbard_hunter_patrol_disassembly.s`.

## How to run

Regenerate `SongData.lean` from the original:

```bash
python -m pipelines.hunter_patrol.extract              # subtune 0 (the only one)
```

Build and run:

```bash
lake build sidgen_hunter_patrol
./.lake/build/bin/sidgen_hunter_patrol
```

Grade against the original:

```bash
source src/env.sh
python3 src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Hunter_Patrol.sid \
    pipelines/hunter_patrol/build/hunter_patrol.sid
# Currently: Grade F, snapshots 0/1500
```

## Known divergences (work items)

Decoded from a writelog diff at frame 0 (orig vs rebuild). All trace
back to the engine's reliance on **binary-loaded initial state** that
the current rebuild does not preserve:

1. **Sub-frame tempo gate.** Original $A418/$A419 = $01/$02, so the
   first note-load fires on frame 2 (period 3). The rebuild fires note
   loads on frame 0 for all three voices, writing full instrument
   bytes (PW, ctrl, AD, SR) before any vibrato/skydive runs. Fix: emit
   the tempo counter with initial `counter=1, reload=2` (per
   `Hunter_Patrol.sid` bytes at $A418/$A419) instead of resetting at
   note-load time.

2. **Binary-loaded effect caches.** `$A41B-$A41D` (freq HI per voice)
   and `$A3FA-$A3FC` (raw note byte per voice) are NOT zeroed by the
   engine's init — they hold leftover values from the binary. On
   frame 0 the skydive effect reads `$A41B = $36` and decrements it,
   producing V1 FREQ_HI = $36 in the original output. The rebuild's
   skydive runs against zero-initialised state and produces nothing.
   Fix: codegen needs to seed these state cells from the disassembled
   binary, or emit a one-time init block that mirrors the load-time
   values.

3. **No per-frame "tween" path in the rebuilt player.** Our V3 player
   re-loads instrument state every note frame; the original interleaves
   tween/note frames at 2:1. Without modelling this, vibrato phase and
   PWM counter drift across the 1500-frame window.

See `docs/hubbard_hunter_patrol_disassembly.s` HIGH-LEVEL FLOW section
for the bit-exact tempo-gating + effects-only-on-tween-frame logic
the rebuild needs to match.

## Why a separate pipeline from Commando / Monty

Hubbard's 1985 player ships in three subtly-incompatible binaries
across these three SIDs: PWM bounds, fx-flag semantics, first-frame
init quirks, and (for Hunter Patrol) load-bearing binary-loaded state
all differ. Cloning the pipeline rather than parameterising it keeps
the byte-perfect Commando invariant locked while Hunter Patrol is
being brought up. The three can be merged once Hunter Patrol grades A.

See also: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
and `reference_hubbard_pwm_bounds.md`.
