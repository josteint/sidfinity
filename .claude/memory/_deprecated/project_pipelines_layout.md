---
name: pipelines-layout-2026-05-27
description: "Current pipelines/ layout after the USF reorg. Hubbard '85 engines under pipelines/hubbard/<engine>/; companion separate; deprecated paths sequestered."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`pipelines/` layout after the 2026-05-27 reorg:

```
pipelines/
├── hubbard/
│   ├── (shared core — codegen.py + build_from_usf.py + verify.py +
│   │    engine_constants.py + ... — consumed by every engine below)
│   ├── action_biker/
│   ├── battle_of_britain/
│   ├── chimera/             ← has digi sidecar (FLAC)
│   ├── commando/
│   ├── confuzion/
│   ├── devils_galop/
│   ├── five_title_tunes/    ← unified single-engine; USF writer at v2/write_unified_usf.py
│   ├── human_race/
│   ├── hunter_patrol/
│   ├── monty/
│   ├── one_man_and_his_droid/
│   └── thing_on_a_spring/
├── companion/               ← separate 1984 Bowden engine; own codegen + USF writer
├── __init__.py
└── README.md
```

Per shared-core engine:

```
pipelines/hubbard/<engine>/
  README.md
  config.py             ← EngineConfig instance with the per-tune parameters
  extract/
    decompile.py
    engine_model.py     ← lift binary to (Tracks, Insts, Score)
    to_usf_v2.py        ← write the .usf file
    types.py
  build/                ← output dir (mostly historical; new artifacts go to HVSC tree)
  tests/
```

Imports follow `pipelines.hubbard.<engine>.config.<ENGINE_NAME>`. Example:

```python
from pipelines.hubbard.commando.config import COMMANDO
from pipelines.hubbard.build_from_usf import build_from_usf
from pipelines.hubbard.verify import verify_all
```

## Where outputs go

Active convention: per-engine USF + rebuilt SID live alongside the HVSC
original in the HVSC tree:

```
hvsc84/MUSICIANS/H/Hubbard_Rob/
    Commando.sid               ← HVSC original, untouched
    Commando.usf               ← our USF export
    Commando.sidfinity.sid     ← our rebuild
    Chimera.sample2.flac       ← digi sidecars (chimera-style engines)
```

`demo/hubbard/<EngineName>.sid` is still kept as a dev-iteration scratch
location; it's where the verify cache currently expects them. Both
locations stay byte-identical.

## What lives where (related deprecated/)

- `deprecated/lean_codegen/` — the original per-engine Lean 4 codegen (~21 trees + lakefile)
- `deprecated/usf1_pipelines/` — two populations:
  1. 9 engines that never migrated off USF v1 (bump_set_spike, crazy_comets, dragons_lair_part_ii, gremlins, last_v8, last_v8_c128, master_of_magic, rasputin, sample_music_i_karate)
  2. per-engine USF v1 leftovers (emit_usf.py / cli.py / __main__.py) from the 12 active engines, plus 5tt's old extract/ + combine.py + v2/build_compound.py
