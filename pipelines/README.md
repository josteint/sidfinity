# Pipelines

Each subdirectory is a per-engine SID rebuild pipeline. Read the engine's
`README.md` for current verification status and run instructions.

## Active path — shared USF2 core

The active codegen lives at [`hubbard/`](./hubbard/) — a parametric
6502 player generator. Per-engine specifics are declared as
`EngineConfig` objects in `pipelines/<engine>/config.py`; the shared
core consumes the config + the engine's USF to emit the rebuild.

Adding a new engine = one `config.py` + one `extract/` package; no
codegen written from scratch.

Engines on this path (byte-exact):

| Engine | Verification |
|---|---|
| `commando/` | byte-exact 19/19 subtunes |
| `monty/` | byte-exact 19/19 (3 music + 16 SFX) |
| `action_biker/` | byte-exact 3/3 ($D400-$D418 snapshot) |
| `battle_of_britain/` | byte-exact 1/1 |
| `chimera/` | byte-exact 4/4 (2 music + 2 digi, cycle-strict) |
| `confuzion/` | byte-exact 1/1 ($D400-$D418 snapshot) |
| `devils_galop/` | byte-exact 1/1 |
| `five_title_tunes/` | byte-exact 5/5 (unified single-engine) |
| `human_race/` | byte-exact 5/5 |
| `hunter_patrol/` | byte-exact 1/1 |
| `one_man_and_his_droid/` | byte-exact 14/14 (1 music + 13 SFX) |
| `thing_on_a_spring/` | byte-exact 17/17 ($D400-$D418 snapshot) |
| `companion/` (Up, up & Away!) | byte-exact 5/5 (1984 Bowden engine) |

Engines that haven't reached byte-exact (extract scaffolded only):
`bump_set_spike`, `crazy_comets`, `gremlins`, `last_v8`, `last_v8_c128`,
`master_of_magic`, `rasputin`, `sample_music_i_karate`,
`dragons_lair_part_ii`.

## Shape of a pipeline

```
<engine>/
  README.md           Engine-specific notes (grade, quirks, run)
  config.py           EngineConfig — the per-engine parameters
  extract/            Python: SID binary -> USF
    decompile.py      Parses PSID header + engine data structures
    engine_model.py   Lifts binary into (Tracks, Insts, Score)
    to_usf_v2.py      Writes the .usf file (USF v2)
    types.py          Dataclasses for the extract API
    cli.py / __main__.py
  build/              Output dir for the rebuilt SID
  tests/              pytest extract smoke tests
```

## Build / run

```bash
# Extract + build for one engine — through the shared core
python -m pipelines.commando.extract       # writes the .usf
python -c "from pipelines.hubbard.build_from_usf import build_from_usf; \
           build_from_usf('demo/hubbard/Commando.usf', 'demo/hubbard/Commando.sid')"

# Verify
python -c "from pipelines.hubbard.verify import verify_all; \
           from pipelines.commando.config import COMMANDO; \
           print(verify_all([(COMMANDO, 'demo/hubbard/Commando.sid')]))"

# Smoke tests
pytest pipelines/
```

## Adding a new engine

See the `migrate-hubbard-engine` skill at
`.claude/skills/migrate-hubbard-engine/` for the full procedure. In
short:

1. `cp data/.../<Engine>.sid demo/hubbard/<Engine>_original.sid`
2. Disassemble: `tools/seed_disassembly.py` → hand-annotate header
3. Write `pipelines/<engine>/config.py` (clone an existing one)
4. Write `pipelines/<engine>/extract/engine_model.py`
5. Iterate: build → capture original vs rebuilt → fix first diff → repeat
6. Verify byte-exact via `pipelines.hubbard.verify.verify_all`

## Historical — the deprecated Lean codegen

Each engine here previously had its own Lean 4 codegen
(`pipelines/<engine>/codegen/<Engine>/*.lean`, ~4000 lines per engine).
This was the original implementation — every engine self-contained,
with compile-time `Properties.lean` proofs. The 11 byte-exact engines
were collapsed onto the shared Python core; the Lean trees were moved
to [`deprecated/lean_codegen/`](../deprecated/lean_codegen/). Reviving
the Lean toolchain is documented there.

`dragons_lair_part_ii/` was Lean-only (verbatim binary image via
`EngineImage.lean`). Its build path is currently broken pending a
Python reimplementation; the original SID is unaffected.
