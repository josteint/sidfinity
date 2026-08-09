# One Man and his Droid pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild of Rob Hubbard's *One Man and his Droid* (1985 Mastertronic) SID.
Independent clone of the Commando/Monty pipeline; extended with the engine
quirks documented in `pipelines/hubbard/one_man_and_his_droid/disassembly.s`.

## Status

| Metric | Value |
|---|---|
| Subtune rebuilt | 0 (the main song; PSID subtune #1 of 14) |
| Other subtunes | 13 drum/SFX patterns played through the secondary drum engine ($139F+) — not currently rebuilt |
| Build | `lake build sidgen_one_man_and_his_droid` succeeds |
| Extract | 15 instruments, 38 patterns, 3 voices, tempo=2 |
| Verification | `writelog_grade.py` ≈ Grade B, snapshots 93.8% (1407/1500) |

What's tuned to OMHD already:
- Octave-trill arpeggio period (8 frames via `$50 AND #$04`,
  matching disassembly $1362 — was 2 frames in Monty clone).
- Skydive emission gated on `durationFrames >= 34` AND `v_dur < 48`
  (= OMHD's orig_dur >= 16 ticks AND v_dur < 24 ticks at tempo=2).
- freqSlide Path B→A transition tuned with `sbc_imm 3` to match
  OMHD's tick-based gate at $130F.

Remaining gaps to Grade A — diagnosis:

Sparse-sample comparison shows V1/V2 freq AND pw_lo match exactly at
frames 100, 200, 300, ..., 1250. The 6% mismatch is at *transition*
frames where the original's play call cycle-budget spills writes into
the next 50Hz snapshot, while the rebuild's faster player keeps them
within frame. E.g., at f54 the original's V1 writes happen at cycles
17790-17833 (very late), and V1's freq/PW updates fall into f55's
snapshot; the rebuild's V1 writes happen earlier and fall into f54.
The end-of-frame *semantic* state is the same (visible at f55+),
but the snapshot at f54 disagrees.

To reach Grade A under `writelog_grade.py` (the un-tolerant grader),
we'd need to match the original player's cycle-per-frame budget
exactly — i.e., emit the *same* number of cycles per play call as
the original. The current codegen optimises for size/clarity and is
faster than the original, so its writes happen earlier in each frame.
That's a separate, larger refactor.

What is still genuinely semantic (small numbers):
1. **Drum/sample engine** at $139F: 13 drum patterns (subtunes 1-13)
   are not rebuilt at all. The codegen would need new sub-engine
   support to play them.
2. **Pattern byte format**: OMHD's bit-7-of-extension-byte =
   pitchbend descriptor (stored at $1517,X). Not yet handled in
   codegen. Likely affects some V1/V2 freq divergences (~10-15
   frames) when notes carry porta bytes.

Tempo=2 is hardcoded for the duration gates (`>= 34`, `< 48`).
Future cleanup: parameterise from `song.tempo`.

## Layout

Identical to Commando — see `pipelines/hubbard/commando/README.md` for the layout
explanation. OMHD-specific differences live inside `extract/` and `codegen/`:

| File | OMHD-specific addition |
|---|---|
| `codegen/OneManAndHisDroid/USF.lean` | `skydive : Bool` field on `USFInstrument` |
| `codegen/OneManAndHisDroid/Codegen.lean` | Skydive emit block; HR threshold = 1 |
| `extract/engine_model.py` | Extracts `has_skydive` from fx_flags bit 1 |
| `extract/emit_usf.py` | Emits `skydive := true/false` per instrument |

## Disassembly reference

`pipelines/hubbard/one_man_and_his_droid/disassembly.s` — annotated 6502
disassembly of the original engine. Reads as the ground truth for what
the codegen must reproduce: per-voice state at $14E2..$1527, freq
table at $1422, instrument table at $1588 (8-byte stride), drum
recipes at $1600 (16-byte stride), orderlist ptrs at $16E0,X, pattern
table at $16EC/$1712.

## How to run

```bash
# Extract: SID → SongData.lean (default = subtune 0, the main song).
python -m pipelines.hubbard.one_man_and_his_droid.extract            # subtune 0
python -m pipelines.hubbard.one_man_and_his_droid.extract 0,1,2      # plus drum patterns

# Build the Lean codegen.
lake build sidgen_one_man_and_his_droid

# Generate the rebuilt SID.
./.lake/build/bin/sidgen_one_man_and_his_droid
# → pipelines/hubbard/one_man_and_his_droid/build/one_man_and_his_droid.sid

# Grade against the original.
source src/env.sh
python src/writelog_grade.py \
    hvsc85/MUSICIANS/H/Hubbard_Rob/One_Man_and_his_Droid.sid \
    pipelines/hubbard/one_man_and_his_droid/build/one_man_and_his_droid.sid
```

## Why a separate pipeline from Commando/Monty

The OMHD engine introduces a secondary drum/sample engine and a
distinct pattern-byte format (pitchbend extension byte) that neither
Commando nor Monty has. Cloning the pipeline rather than parameterising
keeps the Commando/Monty byte-perfect invariants safe while OMHD's
divergent paths get reverse-engineered.

See also:
- `pipelines/hubbard/one_man_and_his_droid/disassembly.s` — annotated disassembly
- `~/.claude/projects/-home-jtr-sidfinity/memory/reference_hubbard_pwm_bounds.md`
- `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
