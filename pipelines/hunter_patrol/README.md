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

## Remaining gap to Grade A — diagnosed

The 5.5% mismatch is **NOT a logic bug** in the per-voice effect
chain; the per-voice logic matches the original perfectly when given
the same CPU state. The root cause is structural:

**Our generated `play()` exceeds the per-frame cycle budget.** PAL is
19656 cycles per VBI; our play() takes ~22000+ cycles for some
voice/effect combinations (vibrato + skydive + drum + arp guards
across three voices, each re-doing `LDX $FA` and per-effect zp
reload). libsidplayfp interrupts our play() at the cycle boundary
and resumes next frame — visible in the `--writelog` output as
frames with **zero SID writes** (e.g. frame 18, frame 29).

When play() spans two frames, the original's "would-have-fired" per-
frame SID write moves to the next frame in our rebuild — so V2 sees a
skydive write where the original had vibrato (and vice-versa). The
two outputs are bit-identical up to where play() first overruns, then
phase-drift accumulates.

### The fix is codegen optimization, not codegen semantics

To close the gap to Grade A, the per-voice exec_voice needs to fit
in ~19656/3 ≈ 6500 cycles. The current emit can be tightened by:

1. Cache the voice index `$FA` once in X for the whole effect chain
   instead of `LDX $FA` at every block entry (~3 cycles × ~6 reloads
   × 3 voices = ~54 cycles saved per frame).
2. Skip the entire vibrato block (jump to `vib_write_base` only if
   needed) when `i_vib_shift[v_inst] == 0` — saves the LSR/ROR
   sequence and base-freq scratch loads.
3. Merge the freq-slide (drum) and skydive duration guards: both
   gate on `v_dur < N` and `v_durfield ≥ M` with overlapping
   constants; emit the shared compare once.
4. Use a Y-register-resident SID voice offset instead of repeatedly
   reloading `v_sidoff,X` into Y across blocks.

A trace via `tools/siddump --writelog` confirms which frames are
overruns: any line with no `|W:...` suffix is a frame our play()
didn't finish. Optimization is done when none exist.

See also: `docs/hubbard_hunter_patrol_disassembly.s` for the
original Hubbard player's reference cycle count (~6000 cycles per
play for all three voices) — that's the budget the codegen needs
to match.

## Why a separate pipeline from Commando / Monty

Hubbard's 1985 player ships in three subtly-incompatible binaries
across these three SIDs: PWM bounds, fx-flag semantics, first-frame
init quirks, and (for Hunter Patrol) load-bearing binary-loaded state
all differ. Cloning the pipeline rather than parameterising it keeps
the byte-perfect Commando invariant locked while Hunter Patrol is
being brought up. The three can be merged once Hunter Patrol grades A.

See also: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
and `reference_hubbard_pwm_bounds.md`.
