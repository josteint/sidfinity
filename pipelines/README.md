# Pipelines

Each subdirectory here is a fully self-contained per-engine SID rebuild
pipeline. Read the engine's `README.md` for run instructions and current
verification status.

| Engine | Pipeline | Verification |
|---|---|---|
| Rob Hubbard (Commando) | [`commando/`](./commando/) | siddump byte-perfect, md5 locked |
| Rob Hubbard (Monty on the Run) | [`monty/`](./monty/) | siddump Grade A 98.8%; py65 0-divergence |

## Shape of a pipeline

Every pipeline has the same shape:

```
<engine>/
  README.md           Engine-specific notes (grade, quirks, run commands)
  extract/            Python: SID binary → USF Lean source
    decompile.py      Parses the PSID header + Hubbard data structures
    engine_model.py   Lifts the binary into the universal (T, I, S) representation
    emit_usf.py       Writes SongData.lean for the codegen to consume
    types.py          Dataclasses for the public extract API
    __init__.py       Package marker
  codegen/            Lean 4: USF → rebuilt SID
    <Engine>/         Capital subdir so Lake's module names are unique
      USF.lean        USF v3 schema (per-engine — clones may diverge)
      SongData.lean   Auto-generated from extract/
      Codegen.lean    USFSong → 6502 player + PSID wrapping
      Constants.lean  Named SID offsets, HR threshold, etc.
      SID.lean, Asm6502.lean, PSIDFile.lean    Supporting types
      Properties.lean Lean theorems — compile-time codegen invariants
      Main.lean       Lake exe entry point
  tests/              pytest suite for the extract path
```

## Why pipelines are cloned, not shared

Each pipeline was developed by cloning the previous one. This is deliberate.

When Monty was being added, sharing code with Commando would have meant
modifying `CodegenV3.lean` — which carries a byte-perfect-output invariant.
Cloning the entire stack let Monty diverge freely without risking Commando.

Trade-off: code duplication between pipelines that aren't yet diverged.
The plan is to merge once we have a third Hubbard SID running through a
clone, so the abstraction is exercised by three cases instead of two.

## Build / run

From the repo root:

```bash
# Extract — Python; writes codegen/SongData.lean
python -m pipelines.commando.extract.emit_usf
python -m pipelines.monty.extract.emit_usf 0,1,2

# Codegen — Lean; writes pipelines/<engine>/build/<engine>.sid
lake build sidgen_commando sidgen_monty
./.lake/build/bin/sidgen_commando      # → pipelines/commando/build/commando.sid
./.lake/build/bin/sidgen_monty         # → pipelines/monty/build/monty.sid

# Tests
pytest pipelines/                       # extract smoke tests
lake build                              # builds Properties.lean; theorems must check
```

## Adding a new engine

1. Pick a clone source closest to your engine (Commando for clean Hubbard,
   Monty if your engine has skydive / per-voice freq-table aliasing).
2. `cp -r pipelines/<source>/ pipelines/<your-engine>/`, then rename the
   `<Source>/` directory under codegen/, and update imports + namespaces.
3. Add two new `lean_lib` / `lean_exe` entries in the root `lakefile.lean`.
4. Update `extract/engine_model.py` for any decompiler differences.
5. Verify byte-perfect or writelog match against the original.
