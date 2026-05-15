# One Man and his Droid pipeline

End-to-end rebuild of Rob Hubbard's *One Man and his Droid* (1985 Mastertronic) SID.
Independent clone of the Commando/Monty pipeline; extended with the engine
quirks documented in `docs/hubbard_one_man_and_his_droid_disassembly.s`.

## Status

| Metric | Value |
|---|---|
| Subtune rebuilt | 0 (the main song; PSID subtune #1 of 14) |
| Other subtunes | 13 drum/SFX patterns played through the secondary drum engine ($139F+) — not currently rebuilt |
| Build | `lake build sidgen_one_man_and_his_droid` succeeds |
| Extract | 15 instruments, 38 patterns, 3 voices, tempo=2 |
| Verification | `writelog_grade.py` ≈ Grade D, snapshots 37.5% (563/1500) |

Significant divergence remains; the codegen was cloned from Monty and
not yet tuned to OMHD-specific behaviour. Likely culprits to investigate
(in priority order):

1. Drum/percussion engine at `$139F`. OMHD has a *secondary* sample
   engine that hijacks V1+V2 freq writes from $1600 recipe tables;
   the Monty-derived codegen does not model it. This alone is
   responsible for most of the freq_hi divergence on V1/V2.
2. Pattern byte format: OMHD uses bit 7 of the extension byte to
   distinguish a PITCHBEND descriptor (stored at $1517,X) from an
   instrument index. The current extractor treats the high byte as
   `porta` but the runtime semantics in `Codegen.lean` were copied
   from Monty's tie-flag handling.
3. fx_flags bit 3 = LINEAR PWM (one-way ramp) vs bouncing PWM
   ($08/$0E bounds). OMHD instruments 0 and 1 use linear PWM.
4. Octave-trill arpeggio (fx_flags bit 2): 4-frame on / 4-frame off
   toggle between pitch and pitch+12 — distinctive Hubbard sound.

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the layout
explanation. OMHD-specific differences live inside `extract/` and `codegen/`:

| File | OMHD-specific addition |
|---|---|
| `codegen/OneManAndHisDroid/USF.lean` | `skydive : Bool` field on `USFInstrument` |
| `codegen/OneManAndHisDroid/Codegen.lean` | Skydive emit block; HR threshold = 1 |
| `extract/engine_model.py` | Extracts `has_skydive` from fx_flags bit 1 |
| `extract/emit_usf.py` | Emits `skydive := true/false` per instrument |

## Disassembly reference

`docs/hubbard_one_man_and_his_droid_disassembly.s` — annotated 6502
disassembly of the original engine. Reads as the ground truth for what
the codegen must reproduce: per-voice state at $14E2..$1527, freq
table at $1422, instrument table at $1588 (8-byte stride), drum
recipes at $1600 (16-byte stride), orderlist ptrs at $16E0,X, pattern
table at $16EC/$1712.

## How to run

```bash
# Extract: SID → SongData.lean (default = subtune 0, the main song).
python -m pipelines.one_man_and_his_droid.extract            # subtune 0
python -m pipelines.one_man_and_his_droid.extract 0,1,2      # plus drum patterns

# Build the Lean codegen.
lake build sidgen_one_man_and_his_droid

# Generate the rebuilt SID.
./.lake/build/bin/sidgen_one_man_and_his_droid
# → pipelines/one_man_and_his_droid/build/one_man_and_his_droid.sid

# Grade against the original.
source src/env.sh
python src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/One_Man_and_his_Droid.sid \
    pipelines/one_man_and_his_droid/build/one_man_and_his_droid.sid
```

## Why a separate pipeline from Commando/Monty

The OMHD engine introduces a secondary drum/sample engine and a
distinct pattern-byte format (pitchbend extension byte) that neither
Commando nor Monty has. Cloning the pipeline rather than parameterising
keeps the Commando/Monty byte-perfect invariants safe while OMHD's
divergent paths get reverse-engineered.

See also:
- `docs/hubbard_one_man_and_his_droid_disassembly.s` — annotated disassembly
- `~/.claude/projects/-home-jtr-sidfinity/memory/reference_hubbard_pwm_bounds.md`
- `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
