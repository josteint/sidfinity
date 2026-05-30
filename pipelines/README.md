# Pipelines

Two top-level pipelines:

- [`hubbard/`](./hubbard/) — the Hubbard '85 engine family. Shared
  Python core (codegen + verify) at the root, with 12 per-tune
  engines living as subdirectories that share that core.
- [`companion/`](./companion/) — the Bowden 1984 / Hubbard-extended
  Companion engine. Different engine family from the 1985 Hubbard
  player; structurally separate.

## hubbard/ — the Hubbard '85 family

The shared core consumes per-engine `EngineConfig` declarations and
emits a 6502 player. Adding a new Hubbard '85 tune = one `config.py`
+ one `extract/` package; no codegen written from scratch.

```
pipelines/hubbard/
  ├── (shared core)
  │   config.py              EngineConfig dataclass
  │   engine_constants.py    freq tables, digi player asm, EngineConstants
  │   codegen.py             6502 player generator (consumed by all engines below)
  │   build_from_usf.py      end-to-end .usf → assembled SID
  │   to_usf.py           shared USF writer
  │   song_interp.py / note_codec.py / inst_*.py / sfx.py
  │   sample.py / flac_io.py / digi_pack.py    (digi)
  │   verify.py / verify_cycle.py              (verify)
  │
  └── (per-tune engines — 12 byte-exact)
      action_biker/
      battle_of_britain/
      chimera/
      commando/
      confuzion/
      devils_galop/
      five_title_tunes/
      human_race/
      hunter_patrol/
      monty/
      one_man_and_his_droid/
      thing_on_a_spring/
```

Each per-tune engine:

```
pipelines/hubbard/<engine>/
  README.md            engine-specific notes
  config.py            EngineConfig — per-tune parameters
  extract/
    decompile.py       parse PSID header + engine data structures
    engine_model.py    lift binary into (Tracks, Insts, Score)
    to_usf.py       write the .usf file
    types.py
  build/               output dir for the rebuilt SID
  tests/               pytest extract smoke tests
```

(`five_title_tunes/` has a slightly different shape — its USF writer is
at `v2/write_unified_usf.py` rather than `extract/to_usf.py`, because
the parent PSID dispatches to 5 sub-engines that get unified into one.)

Status (all byte-exact, 90/90 subtunes):

| Engine | Subtunes verified |
|---|---|
| `commando/` | 19/19 |
| `monty/` | 19/19 (3 music + 16 SFX) |
| `action_biker/` | 3/3 |
| `battle_of_britain/` | 1/1 |
| `chimera/` | 4/4 (2 music + 2 digi) |
| `confuzion/` | 1/1 |
| `devils_galop/` | 1/1 |
| `five_title_tunes/` | 5/5 |
| `human_race/` | 5/5 |
| `hunter_patrol/` | 1/1 |
| `one_man_and_his_droid/` | 14/14 (1 music + 13 SFX) |
| `thing_on_a_spring/` | 17/17 |

## companion/ — the 1984 Bowden engine

Separate engine, separate pipeline. Doesn't share the Hubbard core.

```
pipelines/companion/
  config.py             EngineConfig (own dataclass — not the Hubbard one)
  engine_constants.py
  codegen.py            6502 player generator
  build_from_usf.py     end-to-end build
  to_usf.py          USF writer
  extract/
```

Status: 5/5 subtunes byte-exact (Up, up & Away!, 1984 Hubbard).

## Build / run

```bash
# Extract + build one engine end-to-end (example: Commando)
python -c "
from pipelines.hubbard.commando.extract.to_usf import write_commando_usf
from pipelines.hubbard.commando.config import COMMANDO
from pipelines.hubbard.build_from_usf import build_from_usf
write_commando_usf(COMMANDO, 'demo/hubbard')
build_from_usf('demo/hubbard/Commando.usf', 'demo/hubbard/Commando.sid')
"

# Verify byte-exact via per-frame SID register snapshots
python -c "
from pipelines.hubbard.verify import verify_all
from pipelines.hubbard.commando.config import COMMANDO
print(verify_all([(COMMANDO, 'demo/hubbard/Commando.sid')]))
"

# Extract smoke tests
pytest pipelines/
```

## Adding a new Hubbard '85 engine

See the `migrate-hubbard-engine` skill at
`.claude/skills/migrate-hubbard-engine/` for the full procedure. In
short:

1. `cp hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.sid demo/hubbard/<Engine>_original.sid`
2. Disassemble: `tools/seed_disassembly.py` → hand-annotate header
3. Write `pipelines/hubbard/<engine>/config.py` (clone an existing one)
4. Write `pipelines/hubbard/<engine>/extract/engine_model.py` + `extract/to_usf.py`
5. Iterate: build → capture original vs rebuilt → fix first diff → repeat
6. Verify byte-exact via `pipelines.hubbard.verify.verify_all`

## Deprecated paths

- [`deprecated/usf1_pipelines/`](../deprecated/usf1_pipelines/) —
  9 engines that never migrated off USF v1 (`bump_set_spike`,
  `crazy_comets`, `dragons_lair_part_ii`, `gremlins`, `last_v8`,
  `last_v8_c128`, `master_of_magic`, `rasputin`,
  `sample_music_i_karate`), plus per-engine USF v1 writers from the 12
  active engines.
- [`deprecated/lean_codegen/`](../deprecated/lean_codegen/) — the
  original per-engine Lean 4 codegen. Replaced by the shared Python
  core at `pipelines/hubbard/codegen.py`.
