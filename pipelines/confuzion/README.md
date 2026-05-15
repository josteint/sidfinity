# Confuzion pipeline

Rebuild of Rob Hubbard's *Confuzion* (1985 Incentive) SID. Scaffold
cloned from the Monty / Action Biker pipelines via
`tools/clone_hubbard_pipeline.py`; needs per-SID investigation to reach
Grade A.

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 1 (PSID claims 1; the original is a single-shot tune with no orderlist loop) |
| Grade | F (3.3%, 49/1500 snapshots) |
| Build / run | Lake build OK; `sidgen_confuzion` produces a valid SID |
| Extract | OK — 12 instruments, 25 patterns, 3 voices |

The grade is low because the Codegen.lean inherited from
Action Biker/Monty produces a *Commando-style* player binary that
doesn't match Confuzion's structurally different engine (see below).
The extract path works, the build chain works, but the generated player
diverges almost everywhere on the freq registers.

## What's different about Confuzion (vs Commando/Monty)

Documented in detail in `docs/hubbard_confuzion_disassembly.s`. The
load-bearing differences that the current codegen does NOT yet handle:

| Aspect | Commando/Monty | Confuzion |
|---|---|---|
| Load address | `$C000` | `$0858` |
| Player style | Pure PSID subroutine | Raster-IRQ player with init that self-modifies CLI/JMP/SEI sites to become PSID-callable |
| Init/play overlap | None | Play's `STA $a2`-RTS and init's `LDX #$60` share bytes at `$0867-$0868` (Hubbard space trick) |
| Frame counter | Static word | Self-modifying immediate operand at `$085C` (incremented every play) |
| Tick gate | `$C3E7`/`$C3E8` | `$0BE8`/`$0BE9` (same shape, different addresses) |
| Orderlist looping | Yes (`$FE` rewind marker) | None — first voice to hit `$FF` triggers song-end mute |
| HR threshold | 1 frame (Action Biker) / 3 (Commando) | 0 (immediate gate kill + envelope zero at duration end) |
| Master volume | Static `$0F` | `clamp($A0 - $0BC2, $0F)` with `$0BC2 = $1B` baseline |
| Freq table | `$5428` (Commando) | `$0AFD` (already wired through `CONFUZION_FT_BASE` in `extract/emit_usf.py`) |
| PWM bounds | `$08`/`$0E` | `$08`/`$0E` (matches) |
| Skydive / drum / table-arp | Various | None — Confuzion is a stripped-down classic engine |

## How to run

Regenerate `SongData.lean` from the original SID:

```bash
python3 -m pipelines.confuzion.extract.emit_usf
```

Build and run:

```bash
source src/env.sh
lake build sidgen_confuzion
./.lake/build/bin/sidgen_confuzion         # writes pipelines/confuzion/build/confuzion.sid
```

Grade against the original:

```bash
python3 src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Confuzion.sid \
    pipelines/confuzion/build/confuzion.sid
# Current: Grade F, 3.3% snapshot match (49/1500)
```

## Path to Grade A

Two approaches, ordered by effort:

1. **Adapt the inherited codegen** — disable Monty-isms (skydive,
   notenum aliasing) and add Confuzion-specific behaviors (HR threshold
   0, master volume fade-down formula, single-shot orderlist). Goal:
   match what the Confuzion engine *would* produce as a register stream,
   accepting that the rebuilt binary lives at `$C000` not `$0858`.
   Grades on snapshot match, not bytes.

2. **Faithful byte-perfect rebuild** — emit the actual Confuzion
   binary at `$0858`, including the self-modifying init patch sequence
   and the raster-IRQ structure. Much more work; produces a binary that
   could in principle match Confuzion frame-for-frame like Commando does.

The annotated disassembly in `docs/hubbard_confuzion_disassembly.s`
is the reference for either path.

See also: `docs/hubbard_1985_status.md` for cross-pipeline context.
