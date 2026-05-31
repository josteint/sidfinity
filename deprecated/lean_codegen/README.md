# Lean 4 per-engine codegen (deprecated)

Each engine in this directory used to have its own self-contained Lean 4
codegen — `Codegen.lean` (USF → 6502 player), `Properties.lean` (compile-
time invariants), plus support modules (`SID.lean`, `Asm6502.lean`,
`PSIDFile.lean`, `USF.lean`, `Constants.lean`, `SongData.lean`, `Main.lean`).
Per engine ~4000 lines, ~250 KB; 21 engines total here.

## Why deprecated

The active codegen for byte-exact rebuilds is now the shared Python core at
`pipelines/hubbard/`. Engines are described declaratively in
`pipelines/<engine>/config.py` as `EngineConfig` objects; the shared
`pipelines/hubbard/codegen.py` does the per-engine 6502 emission, parameterised
on the config. Adding a new engine = one config + one extractor; no new
Lean code.

For the 11 USF2 engines that reached byte-exact (Commando, Monty, Action Biker,
Battle of Britain, Chimera, Confuzion, Devils Galop, Human Race, Hunter Patrol,
One Man and his Droid, Thing on a Spring), the Lean codegen here is a
duplicated, older implementation of the same output. The Python path is
authoritative.

For engines that never reached byte-exact (Crazy Comets, Gremlins, Last V8,
Master of Magic, Rasputin, Sample Music I Karate, Bump Set Spike), the Lean
code represents partial reverse-engineering work that didn't get collapsed
into the shared core.

## Dragon's Lair Part II — the one Lean-only active path that broke

`pipelines/dragons_lair_part_ii/codegen/DragonsLairPartIi/EngineImage.lean`
carried the original 7936-byte binary verbatim, and `lake build
sidgen_dragons_lair_part_ii` emitted a byte-identical rebuild (md5
`884019e0120b30dfb43aed6c8befd324`). With the Lean toolchain deprecated, that
rebuild path is no longer reachable. The original SID is unaffected (it lives
in HVSC); only our regenerated-from-pipeline copy is gone for now. Trivially
revivable as ~30 lines of Python if needed (read original bytes, prepend a
fresh PSID header, write).

## What's here

```
deprecated/lean_codegen/
  README.md               (this file)
  lakefile.lean           moved from project root
  lean-toolchain          moved from project root
  lake-manifest.json      moved from project root
  pipelines/<engine>/codegen/<EngineName>/...  per-engine Lean trees
```

## Regenerable artifacts (removed from tree to save space)

- `formal/.lake/` — Lean build outputs. Run `lake build` from `formal/`
  to regenerate (requires the toolchain pinned in `lean-toolchain`).
- `tools/z3_lib/` — vendored z3 4.16.0 Python distribution. Was used
  by `formal/inverse_solver.py` via a `sys.path` injection. Re-vendor
  with `pip install z3-solver==4.16.0 --target tools/z3_lib`, or
  install z3-solver into the active venv and drop the sys.path hack.

## Reviving

If a future engine ever needs the Lean infrastructure back:

1. Move `lakefile.lean`, `lean-toolchain`, `lake-manifest.json` back to
   project root.
2. Move the relevant `pipelines/<engine>/codegen/<EngineName>/` directory
   back to `pipelines/<engine>/codegen/`.
3. `lake build sidgen_<engine>` should work.

The Lake module names (e.g. `Commando`, `ActionBiker`) and the `lean_lib`
/ `lean_exe` declarations in `lakefile.lean` already point at the original
paths.
