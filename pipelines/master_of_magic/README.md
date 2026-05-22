# Master of Magic pipeline

End-to-end rebuild scaffold for Rob Hubbard's *The Master of Magic* (1985,
MAD/Mastertronic). Same shape as the Commando and Monty pipelines —
a Python `extract/` step reads the original SID and emits a Lean
`SongData.lean`; a Lean `codegen/` step compiles that into a 6502 player
and packs a fresh PSID.

## Status

| Metric | Value |
|---|---|
| Pipeline scaffold | present (extract + codegen + lake target wired) |
| Build | `lake build sidgen_master_of_magic` succeeds |
| Codegen output | `pipelines/master_of_magic/build/master_of_magic.sid` (~4.7 KB) |
| Subtunes extracted | 1 (subtune 0; PSID #1 of 3 music tracks) |
| Verification | siddump 2.8% snapshot match (Grade F) — **codegen not yet adapted** |

The codegen currently emits Monty's player logic with renamed
identifiers. To move toward Grade A, `codegen/MasterOfMagic/Codegen.lean`
needs to be adapted to Master of Magic's distinct semantics — see
**Codegen porting checklist** below.

## How to run

Regenerate `SongData.lean` from the original (default = subtune 0):

```bash
python -m pipelines.master_of_magic.extract              # subtune 0
python -m pipelines.master_of_magic.extract 0,1,2        # all three music tracks
```

Build and run:

```bash
lake build sidgen_master_of_magic
./.lake/build/bin/sidgen_master_of_magic
```

Grade against the original:

```bash
source src/env.sh
python src/writelog_grade.py \
    demo/hubbard/Master_of_Magic_original.sid \
    pipelines/master_of_magic/build/master_of_magic.sid
```

## Reference: annotated player disassembly

A hand-annotated 6502 disassembly of the original player lives at
`docs/hubbard_master_of_magic_disassembly.s`. It documents the
state-byte layout, frame-dispatch logic, per-voice loop, and effect
blocks — derived from static analysis with cross-reference to the
Action Biker player (very similar topology).

## Codegen porting checklist

Differences from Monty/Commando that the Lean codegen must reproduce:

- **State byte $C41D** (engine-state): bit 7 = end-of-song, bit 6 =
  first-frame setup. Init writes `$40`; song-end writes `$C0` →
  collapses to sticky `$80` after one silence pass.
- **Voice-slot order**: player runs slots X = 2 → 1 → 0 (V3 first).
  Slot 0 holds SID offset $00 (V1), slot 1 = $07 (V2), slot 2 = $0E (V3).
- **End-of-song volume fade**: every note-load, write VOL =
  `clamp($75 - v_olpos[V3], $00, $0F)`. Fade kicks in at v_olpos[V3] > $66.
- **Note-load gate**: `($C41A == $C41B)` test — first note fires one
  frame later than naive.
- **fx_flags semantics** (instrument byte +7):
  - bit 0 → drum/skydive (DEC freq_hi after midpoint of note)
  - bit 1 → slow descent on long sustained notes (every other frame, while
    orig_dur >= $10 and v_dur < $12)
  - bit 2 → table-arp at +12 semitones when `(frame & 7) != 0`
  - bit 3 → simple PWM mode: `pw_lo += vib_period` per frame (no bounds)
- **Standard PWM bounds**: hardcoded `$08`/`$0E` in pulse_hi (Hubbard
  invariant — see `reference_hubbard_pwm_bounds.md`).

Once the codegen reproduces these, expect the writelog match to climb
out of the F band. The smoke tests in `tests/test_extract.py` already
pin down the extract-side fields the codegen consumes.

## Tests

```bash
PYTHONPATH=tools/py_test_lib python -m pytest pipelines/master_of_magic/tests/
```

For codegen invariants (compile-time theorems), see
`codegen/MasterOfMagic/Properties.lean` — Lake runs those automatically
on build.
