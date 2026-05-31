# Thing on a Spring pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild of Rob Hubbard's *Thing on a Spring* (1985 Gremlin Graphics).
Same shape as the Commando / Monty pipelines.

## Status (2026-05-15)

| Metric | Value |
|---|---|
| Subtunes extracted | 1 (the title music — PSID #1, 0-indexed 0) |
| Lean build | green (`lake build sidgen_thing_on_a_spring`) |
| Codegen runs | yes, produces `build/thing_on_a_spring.sid` |
| Grade vs original | **B — 96.0% snapshots (1440/1500)** |

Reference disassembly: `pipelines/hubbard/thing_on_a_spring/disassembly.s`.

60 frames out of 1500 still diverge — mostly V1/V3 freq-hi on a few
short runs (F767-773, F1185-1191, F872-877, F1194-1199). To reach
Grade A (≥98%) those need engine-trace investigation; everything else
about the song now matches frame-for-frame.

## Layout

Identical to Commando — see `pipelines/hubbard/commando/README.md` for the layout
explanation. The Thing-on-a-Spring-specific differences (vs Monty):

| File | Thing-on-a-Spring-only change |
|---|---|
| `extract/emit_usf.py` | `ft_base = $C3A9`; pitches 96..127 emitted as `.pitched` (not `.percussion .dynamicCtrl` — the freq table at $C3A9 overlaps the voice-offset table at $C469 and those slots are real pitched lookups in the engine) |
| `extract/engine_model.py` | `arp_offset = 24` (engine adds 2 octaves, not 1) |
| `codegen/ThingOnASpring/Codegen.lean` | (1) init: no SID-silence (engine's init only sets $C497); (2) `v_dur` init = 1 + `v_inst` init = [14, 5, 6] from binary $C47F-$C481 → frame-0 effects-only path matches engine's tempo gate; (3) freqSlide thresholds: skip-when v_dur < 2 and Path-B-when v_dur ≥ durfield-3 (engine's exact switch points); (4) skydive (fx_flags bit 1) is INC v_fhi + write OLD, not DEC, and runs every frame (no $50-bit-0 gate) |
| `codegen/ThingOnASpring/USF.lean` | identical to Monty |

## How to run

```bash
source src/env.sh
python -m pipelines.hubbard.thing_on_a_spring.extract.emit_usf      # → SongData.lean (subtune 0)
lake build sidgen_thing_on_a_spring
./.lake/build/bin/sidgen_thing_on_a_spring                  # → build/thing_on_a_spring.sid

python3 src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Thing_on_a_Spring.sid \
    pipelines/hubbard/thing_on_a_spring/build/thing_on_a_spring.sid
```

## Remaining gap to Grade A

60 mismatching frames (4.0%) cluster in a handful of short runs:

| Run | Length | Pattern |
|---|---|---|
| F767-F773, F1185-F1191 | 7 frames each | V1 freq-lo flips $7D ↔ $46 |
| F776-F781, F1194-F1199 | 6 frames each | (same pattern) |
| F864-F868, F872-F877 | ~6 frames | V1 freq-lo/hi small drift |

The recurring V1 flo=$7D vs $46 pattern looks like the arpeggio
pitch-selection picking the wrong octave on specific notes. To diagnose
further: trace V1 across one of those runs with py65 and compare
`v_pitch`/`v_inst` against the engine's `$C47F`/`$C47C`.

## Engine reference

The hand-annotated disassembly at
`pipelines/hubbard/thing_on_a_spring/disassembly.s` documents the full
engine: subtune dispatch, main player tempo gate ($C494/$C495), per-voice
SID-write gating via $C4A0, SFX overlay engine at $C326 (currently not
rebuilt — only subtune 0 is supported), instrument table layout
(8 bytes × 15 records at $CD2A), and the self-modifying INC/DEC trick
at $C35F. See it before changing any of the codegen's engine-specific
constants.

## Why a separate pipeline from Monty

Two Hubbard SIDs from the same player era still differ in load-bearing
ways. Cloning the pipeline rather than parameterising it keeps the Monty
byte-perfect invariant safe while this one is being adapted. The two
can be merged once a third Hubbard SID validates the abstraction.

See also: the engine notes in
`pipelines/hubbard/thing_on_a_spring/disassembly.s` and the memories
`reference_hubbard_pwm_bounds.md`,
`project_hubbard_notenum_overlap.md`.
