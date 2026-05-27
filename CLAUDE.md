# CLAUDE.md — Instructions for continuing development

## Project goal

Build the SIDfinity universal SID music player and ML pipeline. Take the
HVSC catalogue of ~60,000 C64 SID files and translate every engine's binary
format into a single uniform symbolic representation (USF) — engine-neutral
musical data that an ML model can learn from. See `docs/PLAN.md` for the
roadmap.

## Current state (2026-05-27)

**13 Hubbard '85 engines byte-exact through the USF v2 pipeline.**
95/95 subtunes verify via `pipelines.hubbard.verify.verify_all` (md5 of
per-frame SID-register snapshots). Members: Commando, Monty, Action Biker,
Battle of Britain, Chimera (2 music + 2 digi), Confuzion, Devils Galop,
5 Title Tunes (unified), Human Race, Hunter Patrol, One Man and his Droid,
Thing on a Spring, plus the separate 1984 Companion engine (Up, up & Away!).

**Layout — `pipelines/`:**
```
pipelines/
├── hubbard/            shared Python core + 12 per-tune engines as subdirs
│   ├── codegen.py      ← THE 6502 player generator (consumed by every engine)
│   ├── build_from_usf.py
│   ├── verify.py
│   ├── engine_constants.py
│   ├── (digi, sfx, instrument, song, sample, flac modules)
│   └── <engine>/       config.py + extract/{decompile,engine_model,to_usf_v2,types}.py
├── companion/          separate 1984 Bowden engine (own codegen)
└── README.md
```

Older paths live under `deprecated/`:
- `deprecated/lean_codegen/` — the per-engine Lean 4 codegen (replaced by `pipelines/hubbard/codegen.py`)
- `deprecated/usf1_pipelines/` — engines that never migrated off USF v1 + per-engine USF v1 writers

## MANDATORY before any new pipeline work

1. **Check the engine's project memory** — `~/.claude/projects/-home-jtr-sidfinity/memory/project_<engine>.md`. Reads any prior session's root-cause analysis so you don't re-investigate from scratch.
2. **Re-read `docs/usf_representation_principle.md` IN FULL** before designing or changing any USF instrument/effect representation. Load-bearing — see [`feedback_usf_representation_principle`](~/.claude/projects/-home-jtr-sidfinity/memory/feedback_usf_representation_principle.md).
3. **Check `deprecated/` for prior attempts** before rewriting something from scratch.

## Doing a Hubbard '85 engine migration

Use the `migrate-hubbard-engine` skill at `.claude/skills/migrate-hubbard-engine/`. Short form:

1. The HVSC original is read directly from `hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.sid` — no copy needed.
2. Generate a seed disassembly: `tools/seed_disassembly.py …` → `docs/hubbard_<engine>_disassembly.s` → hand-annotate the header
3. Create `pipelines/hubbard/<engine>/config.py` (clone a similar existing one — Action Biker is a good template; Chimera if there's digi)
4. Create `pipelines/hubbard/<engine>/extract/engine_model.py` + `extract/to_usf_v2.py`
5. Iterate: build → capture original vs rebuilt → fix first diff → repeat
6. Verify byte-exact via `pipelines.hubbard.verify.verify_all`

When the engine reaches byte-exact, its USF + rebuilt SID go alongside the
HVSC original at `hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.{usf, sidfinity.sid}`.

## Working conventions

- **`pipelines.hubbard.verify.verify_all` is the verdict.** Returns subtune-level OK/FAIL. md5 of per-frame `$D400-$D418` register snapshots from py65 capture; for digi subtunes it uses `siddump --writelog` (cycle-strict).
- **py65 misses dispatch bugs** (CIA timer, PSID speed). Ear-test new engines and any dispatch changes in real sidplayfp before declaring done.
- **Commit early.** Each verified delta is one commit. No `Co-Authored-By`.
- **Propose options before code** for non-trivial work. Honest scope. Pause at decision points.
- **Schema additions are suspicious by default** — see [`feedback_schema_addition_discipline`](~/.claude/projects/-home-jtr-sidfinity/memory/feedback_schema_addition_discipline.md). Exhaust derivation / `engine_constants` / existing-params alternatives first. `bytes`-typed fields almost always mean you're papering over a representation gap.
- **The shared core stays parametric.** New engine quirks become config fields on `EngineConfig`, never `if engine == "Foo"` branches.

## Build & test

```bash
source src/env.sh              # adds tools/siddump etc. to PATH
bash tools/build.sh            # builds libsidplayfp + siddump (one-time)

# Rebuild one engine through the pipeline
python -c "
from pipelines.hubbard.commando.extract.to_usf_v2 import write_commando_usf
from pipelines.hubbard.commando.config import COMMANDO
from pipelines.hubbard.build_from_usf import build_from_usf
write_commando_usf(COMMANDO, 'hvsc84/MUSICIANS/H/Hubbard_Rob')
build_from_usf('hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.usf', 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')
"

# Verify byte-exact
python -c "
from pipelines.hubbard.verify import verify_all
from pipelines.hubbard.commando.config import COMMANDO
print(verify_all([(COMMANDO, 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')]))
"

# Extract smoke tests
pytest pipelines/
```

## Key files (USF v2 path)

| File | Purpose |
|------|---------|
| `pipelines/hubbard/codegen.py` | The 6502 player generator. Parameterised by `EngineConfig`. |
| `pipelines/hubbard/build_from_usf.py` | End-to-end: `.usf` → assembled SID |
| `pipelines/hubbard/verify.py` | `verify_all` — md5 of per-frame snapshots |
| `pipelines/hubbard/engine_constants.py` | freq tables, digi player asm, `EngineConstants` |
| `pipelines/hubbard/config.py` | `EngineConfig` dataclass (the parameter surface) |
| `pipelines/hubbard/to_usf_v2.py` | Shared USF v2 writer |
| `pipelines/hubbard/song_interp.py` | runtime interpretation of voice/note state |
| `pipelines/hubbard/note_codec.py` | bitstream note encoding |
| `pipelines/hubbard/inst_*.py` | instrument modelling |
| `pipelines/hubbard/sfx.py` | sound-effect engine (shared) |
| `pipelines/hubbard/sample.py`, `flac_io.py`, `digi_pack.py` | digi sidecar pipeline |
| `pipelines/hubbard/<engine>/config.py` | per-tune `EngineConfig` instance |
| `pipelines/hubbard/<engine>/extract/engine_model.py` | per-tune binary → `(T, I, S)` lifter |
| `pipelines/hubbard/<engine>/extract/to_usf_v2.py` | per-tune USF v2 writer |
| `src/usf2/` | USF v2 grammar + reader/writer (spec: `docs/usf_v2_format.md`) |
| `tools/siddump.cpp` | C++ register dumper (libsidplayfp). `--writelog` for cycle timing, `--pc-trace` for CPU PC trace. |

## Build environment

64-core EPYC, 512 GB RAM, dual 3090 GPUs. No sudo — everything from source in-tree.
xa65 assembler at `tools/xa65/xa/xa`. CUDA at `/usr/bin/nvcc`.

## Project structure

```
pipelines/              13 active engines (12 Hubbard under hubbard/, plus companion)
src/                    shared source — USF v2 reader/writer at src/usf2/
                        plus broader-scope tools (sidxray, GT2 pipeline, etc.)
docs/                   specifications and reference docs
tools/                  build tools (xa65, siddump, libsidplayfp)
hvsc84/                 HVSC #84 collection (not in git, gitignored)
deprecated/             earlier project phases — see deprecated/<topic>/README.md
```

## Other workstreams (not the USF v2 focus)

- **GT2 / GoatTracker pipeline** lives at `src/gt2_*.py` and ships its own
  USF format (USF v1 / `src/usf.py`). It's a separate active pipeline that
  reached partial coverage of HVSC GT2 SIDs. Documented separately; not part
  of the USF v2 byte-exact methodology described above.
- **Register-trace pipeline** (`src/regtrace_to_usf.py`) — universal fallback
  via siddump CSV. Useful for engines we haven't reverse-engineered.
- **sidxray** (`src/sidxray/`) — player reverse-engineering toolkit.

These workstreams are intentionally not detailed here. If they become
relevant to a given task, search `src/` and the relevant `_deprecated/`
memory archive.
