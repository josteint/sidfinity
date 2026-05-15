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
| Grade | **B** (1418/1500 snapshots, 94.5%) |

The first frame matches exactly. Remaining mismatches are accumulated
effect-cadence drift over 1500 frames, concentrated in V2/V3 envelope
register diffs around note boundaries.

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

## What got us to Grade B (the F → B fixes)

Five tightly-coupled fixes to `codegen/HunterPatrol/Codegen.lean`,
all keyed to the annotated disassembly:

1. **Per-voice initial seeds** for `v_inst = [$04, $04, $0A]`,
   `v_fhi = [$36, $20, $10]`, and `v_durfield = [54, 54, 18]`.
   These mirror the binary-loaded $A403/$A41B/$A3FA caches that the
   original engine's first-frame effect chain depends on (the
   composer pre-baked them so frame 0 of the play loop runs as if
   a phantom "frame -1" had already loaded each voice's first note).

2. **`v_dur = [1, 1, 1]` instead of zero** in the data block, paired
   with stripping `STA v_dur,X` from `emitInitVoiceState`. This makes
   frame 0 DEC v_dur → 0 (skip note-load, run effects only), then
   frame 1 underflow and load the first real note. Matches the
   original's sub-frame tempo gate that defers the first note-load
   from frame 0 to frame 1.

3. **Frame counter seed `$1E` instead of `$FF`** in
   `emitInitFrameCounter`, so the first INC inside play gives `$1F`
   (low bit = 1). This is what the binary-loaded $A426 produces, and
   it's what gates skydive and arp on every-other-frame.

4. **Skydive guards on duration + remaining**: added
   `v_durfield ≥ 36 frames` (= 12 ticks) and `v_dur < 27 frames`
   (= remaining 9 ticks) checks ahead of the every-other-frame
   gate, mirroring the original's $A2D5 `CMP #$0C` / $A2DC `CMP #$09`
   guards. Without these, skydive over-fires on every note instead
   of just the tail of long notes.

5. **Gate-off threshold `v_dur == 2` instead of `1`**: tempo=3 means
   the original's "$A3F7 == 0" frame corresponds to v_dur ∈ {0,1,2}
   in our frame-based counter; firing on 2 catches the same musical
   moment.

Net effect: from 0/1500 snapshot match through a sequence of
runs at 64.7% → 84.3% → 94.5%, ending at Grade B.

## Remaining gap to Grade A

The remaining ~5.5% mismatch is concentrated in two regimes:

- A handful of V2 frames where our skydive doesn't fire but the
  original's does (e.g. frame 42). Suspect: subtle phase offset in
  how the global frame counter is consumed when V1 and V2 share
  instrument 4 but reach the skydive guard via different per-voice
  state cycles. Needs a py65 trace of one full $51 note cycle.

- Cumulative ~1-frame timing drift over hundreds of frames manifesting
  as ADSR-zero mismatches around note boundaries (e.g. V3 AD/SR at
  frames 487, 1969, 2142, ...). Likely root cause: our codegen runs
  the effects chain on note-LOAD frames; the original's note-load
  path JMPs straight to "next voice" and skips effects on that
  voice for that frame. Modelling that asymmetry is the next
  structural change.

## Why a separate pipeline from Commando / Monty

Hubbard's 1985 player ships in three subtly-incompatible binaries
across these three SIDs: PWM bounds, fx-flag semantics, first-frame
init quirks, and (for Hunter Patrol) load-bearing binary-loaded state
all differ. Cloning the pipeline rather than parameterising it keeps
the byte-perfect Commando invariant locked while Hunter Patrol is
being brought up. The three can be merged once Hunter Patrol grades A.

See also: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
and `reference_hubbard_pwm_bounds.md`.
