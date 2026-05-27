# Commando pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild of Rob Hubbard's *Commando* (1985) SID. The original is
parsed, lifted into a structured USF representation, then re-emitted as a
fresh PSID that uses our own V3 player driving the same musical data.

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 3 (in-game, title, intro) |
| Verification | siddump --writelog byte-perfect against original |
| Rebuild md5 | `1964b77e8b542a5187fdd0a6db2d0186` |
| Grade | A |

This md5 is a load-bearing invariant. Any change anywhere in this pipeline
should preserve it; if it doesn't, either the change is wrong or a new
invariant is being established deliberately.

## Layout

```
commando/
  extract/          Python — reads original SID, emits codegen/SongData.lean
    decompile.py        SID binary → Python objects (instruments, patterns, songs)
    engine_model.py     Hubbard semantics → universal (T, I, S) tuple
    emit_usf.py         (T, I, S) → Lean USF data file
  codegen/          Lean 4 — reads SongData.lean, writes commando.sid
    Commando/
      USF.lean          USF v3 schema (instruments, notes, patterns, subtunes)
      SongData.lean     Auto-generated from extract; the song's USF data
      Codegen.lean      USFSong → 6502 player + PSID wrapping
      SID.lean / Asm6502.lean / PSIDFile.lean   Supporting types
      Properties.lean   Property tests for the codegen
      Main.lean         Lake exe entry — calls generateSID and writes the file
```

## How to run

Regenerate `SongData.lean` from the original (re-runs extraction):

```bash
python -m pipelines.hubbard.commando.extract.emit_usf
```

Build the Lean exe and produce the rebuild:

```bash
lake build sidgen_commando
./.lake/build/bin/sidgen_commando
# → pipelines/hubbard/commando/build/commando.sid
```

Verify byte-perfect:

```bash
md5sum pipelines/hubbard/commando/build/commando.sid  # expect 1964b77e8b542a5187fdd0a6db2d0186
python src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sid \
    pipelines/hubbard/commando/build/commando.sid
```

## What "byte-perfect" means

The *file* md5s of original and rebuild differ — they ship different player
code. What's byte-perfect is the **siddump writelog**: when both SIDs are
emulated for the same number of frames, every write to `$D400-$D418`
matches in (cycle, register, value).
