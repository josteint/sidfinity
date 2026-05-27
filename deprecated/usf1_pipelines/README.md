# USF v1 / unmigrated pipelines (deprecated)

Nine engine-pipeline scaffolds that never reached byte-exact on the
active shared core. All shipped only USF v1 emitters (`extract/emit_usf.py`),
not USF v2 (`extract/to_usf_v2.py`), and never grew a `config.py` with
an `EngineConfig` object pointing at `pipelines/hubbard/`.

When the project's per-engine Lean codegen was deprecated
([`deprecated/lean_codegen/`](../lean_codegen/)), these pipelines lost
their build path entirely — the Lean codegen was the only thing that
consumed their `SongData.lean` output.

## What's here

```
deprecated/usf1_pipelines/
  bump_set_spike/         (1986 Hubbard; scaffold only)
  crazy_comets/           (1985 Hubbard; reached Grade C 87.6% via siddump,
                           V1 residual is an effect-dispatch interaction)
  dragons_lair_part_ii/   (1986 Hubbard, different from the 1985 family —
                           dual 8-byte instr tables, $C505 state byte,
                           $FE/$FF orderlist markers; was byte-exact via
                           the Lean verbatim-image path, md5 884019e0...,
                           non-functional since Lean deprecation)
  gremlins/               (1985 Hubbard; Grade F 5.8%; needs $16EB
                           tempo-gate + dirty-BSS port)
  last_v8/                (1985 Hubbard; Grade F→D 46.3%; remaining gap
                           is V2 vibrato/slide phase drift)
  last_v8_c128/           (1985 Hubbard, C128 variant of Last V8)
  master_of_magic/        (1985 Hubbard; scaffold only)
  rasputin/               (1985 Hubbard; scaffold only)
  sample_music_i_karate/  (1985 Hubbard; has a build_byte_perfect.py
                           outside the standard extract shape)
```

Each contains `extract/` (decompile + engine_model + emit_usf — Python),
`build/` (output dir, mostly empty), `tests/` (pytest smoke tests on
extract), and a `README.md` (with a top-of-file deprecation banner from
the earlier Lean-codegen migration).

## Migrating one back

If you want to bring an engine here onto the active shared core, the
process is the standard one from the `migrate-hubbard-engine` skill:

1. Move the directory back to `pipelines/<engine>/`.
2. Write a `config.py` with an `EngineConfig` parameterising the
   shared `pipelines/hubbard/` core for this engine's quirks.
3. Write an `extract/to_usf_v2.py` (replaces `emit_usf.py`).
4. Iterate on `verify_all` until the subtunes verify byte-exact.

The existing `extract/decompile.py` and `extract/engine_model.py` are
usually a head start — they decode the engine's binary layout. The
USF v1 emitter (`extract/emit_usf.py`) and the Lean-era Songtree are
no longer the target format; ignore those.

## Special case — Dragon's Lair Part II

DL2 was byte-exact under the Lean verbatim-image path:
`lake build sidgen_dragons_lair_part_ii` produced md5
`884019e0120b30dfb43aed6c8befd324`, byte-identical to the original.
The verbatim wrapper is what got deprecated, not the engine. Reviving
this one is ~30 lines of Python: read the original 7936 binary bytes,
prepend a fresh PSID header. The structural codegen
(extract/`engine_model.py` → engine semantics) is separate work.
