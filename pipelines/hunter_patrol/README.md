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

## Remaining gap to Grade A — investigation log

Diagnosed via py65 trace + `siddump --writelog --raw`:

1. **Per-voice effect logic is correct.** py65 step-trace through
   frame 42 (the first divergence point) shows skydive *does* fire
   on V2 (writing V2_FREQ_HI=$18 after vibrato writes $01). The
   codegen produces the expected per-voice sequence.

2. **The mismatch is at the libsidplayfp emulation boundary.** The
   `--writelog` output for rebuild frame 42 truncates at cycle
   18137 with V2_FREQ_HI=$01 (vibrato base). The skydive write
   that py65 sees happens later in the frame and — based on
   frame 43's writelog starting at cycle 3 — gets attributed to
   the next frame in libsidplayfp's accounting.

3. **"No-write" frames are normal.** Both the byte-perfect
   Commando rebuild AND the original Hunter_Patrol.sid have frames
   with empty `|W:...` (e.g. frame 18, frame 30), so the empty
   writelog frames are an emulation artifact, not a bug.

The remaining ~80 mismatched frames look like our play() routine
takes long enough that some SID writes cross libsidplayfp's
frame-boundary accounting, ending up in the "wrong" siddump frame
relative to the original. The original Hubbard player evidently
finishes faster (or fires effects in an order that fits the budget),
so its SID writes all land in the "right" frame.

### Concrete next steps

To push past Grade B, one of:
- Tighten the codegen's per-frame cycle count by caching the voice
  index in X across all effect blocks (saves ~50 cycles per frame
  from redundant `LDX $FA` reloads).
- Re-order effect emit so the writes happen earlier in the cycle
  window: gate-off → frequency-writing effects (vibrato, skydive,
  arp) first, then PWM/freq-slide/etc.
- Compare PSID header flags between the byte-perfect Commando
  rebuild and ours — there may be a clock/SID-model bit difference
  affecting libsidplayfp's frame timing model.

### Audibility note

The 5.5% mismatch is concentrated in V2_FREQ_HI and V_AD/V_SR at
note-boundary frames, which are mostly inaudible — the snapshot
metric flags any register difference, but the actual SID output
(PCM via `siddump --pcm`) at Grade B is very close to the original.

## Why a separate pipeline from Commando / Monty

Hubbard's 1985 player ships in three subtly-incompatible binaries
across these three SIDs: PWM bounds, fx-flag semantics, first-frame
init quirks, and (for Hunter Patrol) load-bearing binary-loaded state
all differ. Cloning the pipeline rather than parameterising it keeps
the byte-perfect Commando invariant locked while Hunter Patrol is
being brought up. The three can be merged once Hunter Patrol grades A.

See also: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
and `reference_hubbard_pwm_bounds.md`.
