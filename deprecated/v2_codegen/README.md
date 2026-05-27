# V2 player codegen (deprecated)

The GT2-era V2 per-song 6502 code generator and supporting tooling.
Moved here from `src/player/` during the USF v2 cleanup.

This was the codegen for the GT2/GoatTracker pipeline — takes a USF
song (USF v1 / `src/usf.py` schema), emits 6502 bytes via Python.
Includes peephole optimizer, cycle modelling, Z3-based instruction
synthesis, and a CUDA brute-force 6502 optimizer (dual-3090 era).

Superseded by the USF v2 / Hubbard byte-exact pipeline at
`pipelines/hubbard/codegen.py`, which is parametric over `EngineConfig`
and consumes USF v2 directly. The V2 codegen was per-song; the new
core is per-engine + parameterised.

## What's here

```
player/
  codegen.py            feature detection for codegen
  codegen_v2.py         the per-song 6502 generator
  codegen_v3.py         a later experimental rewrite
  cycle_model.py        static cycle counting + path tracing
  emu_test.py           py65 6502 emulator test harness
  layout_opt.py         JMP/branch distance analysis
  peephole.py           post-generation branch-over-JMP optimizer
  z3_6502.py            Z3 SMT 6502 model for formal verification
  z3_synth.py           Z3 instruction-sequence synthesiser
  gpu_6502.cu           CUDA brute-force 6502 optimizer
  gpu_optimize.py       Python interface for the GPU optimizer
  regression_registry.json  registry of GT2 regression baselines
  gcommon.h / gplay.c / greloc.c   GoatTracker C bindings
  archive/              earlier iterations
```

## Reviving

If the GT2/V2 codegen workflow becomes useful again: move `player/`
back to `src/player/` and update any imports that still reference
`from src.player`. None of the active USF v2 path uses any of this.
