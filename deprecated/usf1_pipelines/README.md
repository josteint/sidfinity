# USF v1 pipelines (deprecated)

USF v1 was the original pipeline format, paired with the per-engine Lean
codegen ([`deprecated/lean_codegen/`](../lean_codegen/)). It emitted
`SongData.lean` files that the Lean codegen consumed. USF v2 replaced
it: a single on-disk `.usf` text format consumed by the shared Python
codegen at `pipelines/hubbard/`.

This directory holds two populations:

## 1. Fully-deprecated pipelines (9 engines)

Engines that never moved off USF v1 — never grew a `config.py` /
`EngineConfig` for the shared core. Some reached partial grades via
the Lean codegen (crazy_comets Grade C, last_v8 Grade D); most are
scaffold-only.

```
bump_set_spike/          (1986 Hubbard; scaffold only)
crazy_comets/            (1985; Grade C 87.6%; effect-dispatch gap)
dragons_lair_part_ii/    (1986; was BYTE-EXACT under Lean's verbatim-
                          image path, md5 884019e0...; revivable as
                          ~30 lines of Python wrap)
gremlins/                (1985; Grade F 5.8%)
last_v8/                 (1985; Grade F→D 46.3%)
last_v8_c128/            (1985 C128 variant)
master_of_magic/         (1985; scaffold only)
rasputin/                (1985; scaffold only)
sample_music_i_karate/   (1985; build_byte_perfect.py outside standard shape)
```

Each contains a full `extract/` + `build/` + `tests/` + `README.md`.

## 2. USF v1 leftovers from now-USF-v2 engines (12 engines)

Per-engine USF v1 files (`emit_usf.py`, `cli.py`, `__main__.py`) from
engines that DID migrate to the shared USF v2 core. The v2 path
(`pipelines/<engine>/extract/to_usf_v2.py` → `pipelines/hubbard/...`)
is the active build. The v1 files here are the historical writers
that wrote `SongData.lean` for the Lean codegen — superseded but
preserved.

```
action_biker/extract/{emit_usf,cli,__main__}.py
battle_of_britain/extract/{emit_usf,cli,__main__}.py
chimera/extract/{emit_usf,cli,__main__}.py
commando/extract/{emit_usf,cli,__main__}.py
confuzion/extract/{emit_usf,cli,__main__}.py
devils_galop/extract/{emit_usf,cli,__main__}.py
human_race/extract/{emit_usf,cli,__main__}.py
hunter_patrol/extract/{emit_usf,cli,__main__}.py
monty/extract/{emit_usf,cli,__main__}.py
one_man_and_his_droid/extract/{emit_usf,cli,__main__}.py
thing_on_a_spring/extract/{emit_usf,cli,__main__}.py
```

For five_title_tunes the v1 path was structurally different (a separate
extract/ + merge.py to fuse 5 sub-engines), so the whole old extract/
moved here along with the old compound-build artifacts:

```
five_title_tunes/extract/           (decompile, engine_model, emit_usf,
                                     merge, types — entire v1 dir)
five_title_tunes/combine.py         (old "lake build each sub + glue"
                                     script — replaced by v2 unified
                                     path at pipelines/five_title_tunes/v2/)
five_title_tunes/build_compound.py  (was at pipelines/five_title_tunes/v2/;
                                     compound build before the unified
                                     collapse)
```

## Migrating one back

For the 9 fully-deprecated engines, see the `migrate-hubbard-engine`
skill at `.claude/skills/migrate-hubbard-engine/`. The existing
`extract/decompile.py` + `extract/engine_model.py` are usually a head
start — they're the binary-layout decoders. The USF v1 emitter
(`emit_usf.py`) and the Lean target are no longer relevant; ignore
them.

For the 12 leftovers, nothing to do — the engines are already on the
shared core. These files are just here for historical reference and
can stay or be `git rm`'d at any time.
