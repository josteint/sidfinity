# CLAUDE.md — Instructions for continuing development

## Project goal

Build the SIDfinity universal SID music player and ML pipeline. Take the
HVSC catalogue of ~60,000 C64 SID files and translate every engine's binary
format into a single Unified SID Format (USF) — engine-neutral
musical data that an ML model can learn from. See `docs/PLAN.md` for the
roadmap.

## CORE TENET — read this FIRST, before every session

**The verification target is the SID write-log stream, not the engine code.**

Every composer / codegen / migration in this repo is judged ONLY by whether
the rebuilt SID emits the same `$D400..$D418` write sequence (frame-by-frame
for tracker music; cycle-strict for digi) as the HVSC original. Nothing
else is the target.

This means the composer is FREE to invent any runtime architecture it wants —
different dispatch path, different instrument layout, different orderlist
scheme, different memory map, completely re-arranged effect-chain emitters,
zero-page reassignment, JSR/RTS where the original had inline code, inline
where the original had subroutines. The original engine's machine code is a
historical artifact, not a blueprint.

When you are stuck on "I need to add N bytes but there's no room" or "the
disassembly forces me to do X" — the answer is almost always to **re-state
the problem in terms of the write-log stream**, then restructure the code
to produce that stream more compactly. Do NOT reach for hacks like
shifting data addresses, reproducing self-modifying code mechanisms, or
emitting verbatim byte regions from HVSC.

Concrete corollaries:
- USF carries only musical content, never engine-positional artifacts
  (sub-jump tables, abs pointers, raw inst-program bytes, SMC slots).
- Per-engine config fields parametrise differences between engines'
  write-log streams (e.g. `nextvoice_write_order`, `fx_drum_d401_offset`,
  `held_note_clears_stod404_gate`) — they never describe HVSC's code layout.
- When a disasm shows SMC, do NOT reproduce it; emit clean code that
  produces the same writes (see [[feedback_smc_disasm_check]]).
- For FC family see [[feedback_deconstruct_not_reproduce]] for the Hawkeye
  sub-0 worked example (match=133 → 1538 after this reframing).

If you find yourself reading a long disasm and asking "how do I mirror this
structure," stop and ask "what writes does this produce in this frame?"
instead.

## Current state

Composer rewrite is complete. The Hubbard '85 family lives entirely in
`pipelines/composer.py` as feature-driven asm composition (no template,
no string substitution — every per-engine knob is a typed argument
threaded through `_compose_hubbard_engine_asm`). The earlier
`composer_hubbard.py` + `universal_codegen.py` + `pipelines/codegen.py`
+ the ENGINE asm template are gone. See
[[project_composer_dissolution]] for the architecture + build-path
call chain.

Two engine families ship through the USF pipeline today:

- **Hubbard '85** (under `pipelines/hubbard/<engine>/`) — feature-driven
  asm composition out of the shared composer.
- **Companion strains** (under `pipelines/companion/<engine>/`) —
  Hubbard's 1984 Up_up_and_Away, Bowden-canonical, Clever_Music
  (Fairlight + Gyroscope), Henrys_House, Yes_Tune family.

`tools/regression.py` is the verdict for both families. It prints the
current ok / known-partial / regressed counts and enumerates the
pre-existing partial subtunes — treat it as the source of truth, not
this file.

**Layout — `pipelines/`:**
```
pipelines/
├── composer.py         ← THE composer (~5k lines: 18 routine chunks,
│                          data emitters, _Inputs adapters, dispatch)
├── build_from_usf.py   ← Public entry; thin wrapper around composer
├── engine_model.py     ← Typed feature dataclasses
├── hubbard/            ← Shared Python core (codec, verify, sfx, digi,
│   │                     instrument modelling) + per-tune extracts
│   ├── verify.py / verify_cycle.py
│   ├── note_codec.py / engine_constants.py / inst_*.py
│   ├── sfx.py / sample.py / flac_io.py / digi_pack.py
│   ├── config.py       ← EngineConfig (extract path only)
│   └── <engine>/       config.py + extract/{engine_model,to_usf}.py
├── companion/          ← Companion-strain engines (Up_up_and_Away,
│                          Bowden-canonical, Clever_Music, Henrys_House,
│                          Yes_Tune family); each subdir has its own
│                          extract path.
└── README.md
```

Older paths live under `deprecated/`:
- `deprecated/lean_codegen/` — the per-engine Lean 4 codegen
- `deprecated/usf1_pipelines/` — engines that never migrated off USF v1

`tools/regression.py` runs the full pipeline regression (Hubbard +
companion). Use it as the verdict after any composer change.

## MANDATORY before any new pipeline work

1. **Check the engine's project memory** — `.claude/memory/project_<engine>.md`. Reads any prior session's root-cause analysis so you don't re-investigate from scratch.
2. **Re-read `docs/usf_representation_principle.md` IN FULL** before designing or changing any USF instrument/effect representation. Load-bearing — see [`feedback_usf_representation_principle`](.claude/memory/feedback_usf_representation_principle.md).
3. **Check `deprecated/` for prior attempts** before rewriting something from scratch.

## Doing a Hubbard '85 engine migration

Use the `migrate-hubbard-engine` skill at `.claude/skills/migrate-hubbard-engine/`. Short form:

1. The HVSC original is read directly from `hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.sid` — no copy needed.
2. Generate a seed disassembly: `tools/seed_disassembly.py …` → `pipelines/hubbard/<engine>/disassembly.s` → hand-annotate the header
3. Create `pipelines/hubbard/<engine>/config.py` (clone a similar existing one — Action Biker is a good template; Chimera if there's digi)
4. Create `pipelines/hubbard/<engine>/extract/engine_model.py` + `extract/to_usf.py`
5. Iterate: build → capture original vs rebuilt → fix first diff → repeat
6. Verify byte-exact via `pipelines.hubbard.verify.verify_all`

When the engine reaches byte-exact, its USF + rebuilt SID go alongside the
HVSC original at `hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.{usf, sidfinity.sid}`.

## Working conventions

- **`pipelines.hubbard.verify.verify_all` is the verdict.** Returns subtune-level OK/FAIL. md5 of per-frame `$D400-$D418` register snapshots from py65 capture; for digi subtunes it uses `siddump --writelog` (cycle-strict).
- **For writelog-partial debugging, start with `tools/find_first_divergence.py ORIG.sid REBUILD.sid --subtune N`.** It localises the first `(reg, val)` mismatch + names the voice/role (e.g. "V2 freq hi") in one command. THEN disassemble orig's effect for that register, THEN diff against the composer emitter. Do NOT start from py65 state traces or prior task descriptions — both go stale. Full protocol in [`feedback_writelog_divergence_recipe`](.claude/memory/feedback_writelog_divergence_recipe.md).
- **py65 misses dispatch bugs** (CIA timer, PSID speed). Ear-test new engines and any dispatch changes in real sidplayfp before declaring done.
- **Commit early.** Each verified delta is one commit. No `Co-Authored-By`.
- **Propose options before code** for non-trivial work. Honest scope. Pause at decision points.
- **Schema additions are suspicious by default** — see [`feedback_schema_addition_discipline`](.claude/memory/feedback_schema_addition_discipline.md). Exhaust derivation / `engine_constants` / existing-params alternatives first. `bytes`-typed fields almost always mean you're papering over a representation gap.
- **The shared core stays parametric.** New engine quirks become config fields on `EngineConfig`, never `if engine == "Foo"` branches.

## Build & test

```bash
source src/env.sh              # adds tools/siddump etc. to PATH
bash tools/build.sh            # builds libsidplayfp + siddump (one-time)

# Full pipeline regression — Hubbard + companion + 5TT
python3 tools/regression.py

# Rebuild one engine through the pipeline
python -c "
from pipelines.hubbard.commando.extract.to_usf import write_commando_usf
from pipelines.hubbard.commando.config import COMMANDO
from pipelines.build_from_usf import build_from_usf
write_commando_usf(COMMANDO, 'hvsc84/MUSICIANS/H/Hubbard_Rob')
build_from_usf('hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.usf', 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')
"

# Verify one engine byte-exact
python -c "
from pipelines.hubbard.verify import verify_all
from pipelines.hubbard.commando.config import COMMANDO
print(verify_all([(COMMANDO, 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')]))
"

# Extract smoke tests
pytest pipelines/
```

## Key files (USF path)

The build path is `build_from_usf` → `composer.emit_sid_from_usf` →
`_emit_hubbard85_bytes` → `_compose_hubbard_engine_asm` → xa65 → PSID.
Everything except extraction lives in `pipelines/composer.py` after
the Phase 8 dissolution (~5,000 lines: 18 routine-chunk emitters +
data-section emitters + `_Inputs` adapters + `_inputs_from_usf` +
`_hubbard_emit_sid`/`_emit_combined_sid`/`_emit_hubbard85_bytes`).

| File | Purpose |
|------|---------|
| `pipelines/composer.py` | The composer. Owns the entire asm composition: 18 Hubbard '85 routine chunks, all data-section emitters, USF→`_Inputs` adapter, and the build dispatch. ~5,000 lines. |
| `pipelines/build_from_usf.py` | Public entry. Thin wrapper calling `composer.emit_sid_from_usf`. |
| `pipelines/engine_model.py` | `EngineModel` + the typed feature dataclasses (`StateLayoutMirror`, `FadeProgressive`, `SubtuneSpec`, ...). |
| `pipelines/hubbard/verify.py` | `verify_all` — md5 of per-frame snapshots (Hubbard verification). |
| `pipelines/hubbard/verify_cycle.py` | `compare_instruction_stream` + `writelog_capture` — cycle-strict verification (companion + digi). |
| `pipelines/hubbard/engine_constants.py` | Freq tables, digi player asm, `EngineConstants`, `CHIMERA_DIGI`. |
| `pipelines/hubbard/note_codec.py` | Bitstream note encoder + decoder asm (`BitPackCodec`). Composer's `_resolve_codec_note_asm` substitutes the four fade/tie sentinels in this codec's `note_asm`. |
| `pipelines/hubbard/inst_generalize.py`, `inst_program.py` | Instrument modelling. |
| `pipelines/hubbard/sfx.py` | SFX record types (`SoundEffect`). |
| `pipelines/hubbard/sample.py`, `flac_io.py`, `digi_pack.py` | Digi sidecar pipeline (used by `composer._build_digi_region`). |
| `pipelines/hubbard/config.py` | `EngineConfig` dataclass — drives the per-engine *extract* path (binary → USF). |
| `pipelines/hubbard/<engine>/config.py` | Per-tune `EngineConfig` instance. |
| `pipelines/hubbard/<engine>/extract/engine_model.py` | Per-tune binary → `(T, I, S)` lifter. |
| `pipelines/hubbard/<engine>/extract/to_usf.py` | Per-tune USF writer. |
| `pipelines/hubbard/to_usf.py` | Shared USF writer helpers. |
| `pipelines/hubbard/song_interp.py` | Runtime interpretation of voice/note state (used by extract). |
| `pipelines/companion/` | Companion-strain engines (Up_up_and_Away, Bowden-canonical, Clever_Music, Henrys_House, Yes_Tune family). Extract path + per-engine USF writers. |
| `src/usf/` | USF grammar + reader/writer (spec: `docs/usf_format.md`). |
| `tools/regression.py` | Full pipeline regression — Hubbard `verify_all` + companion `compare_instruction_stream` + 5TT. Lists pre-existing partials so they're not mistaken for regressions. |
| `tools/siddump.cpp` | C++ register dumper (libsidplayfp). `--writelog` for cycle timing, `--pc-trace` for CPU PC trace. |

## HVSC index database — `hvsc84.db`

A SQLite catalogue of every SID in `hvsc84/` with classification +
build status. The pipeline updates this DB automatically (build → `sidfinity_md5`, USF write → `usf_path`, verify → `verify_*`). Initial population + full rebuild via `tools/build_sid_db.py` (re-runnable, idempotent,
~20 s incremental). Use it for:

- **engine-by-engine iteration** (instead of folder-by-folder)
- **coverage queries** ("how many Rob_Hubbard tunes are migrated?")
- **migration candidate selection** ("show me the longest unmigrated
  tunes by engine X, sorted by songlength")

There's **no `sqlite3` CLI** on this system — query with Python:

```python
import sqlite3
db = sqlite3.connect('hvsc84.db')
for path, title in db.execute(
    "SELECT path, title FROM sids "
    "WHERE engine='Rob_Hubbard' AND pipeline IS NULL "
    "ORDER BY songlength_s DESC LIMIT 10"
): print(path, title)
```

Schema in `tools/build_sid_db.py` (one table `sids`, indexes on
engine / pipeline / md5).

### When to re-run `tools/build_sid_db.py`

| Trigger | Why |
|---|---|
| After migrating a new engine to `pipelines/` | refresh `pipeline` column |
| After running the build for an engine | refresh `usf_path` / `sidfinity_md5` |
| After an HVSC update (#85 lands) | re-walk + re-classify added/removed SIDs |
| After re-running `sidid` | refresh engine column |
| After `verify_all` (future hook) | refresh `verify_status` columns |
| After editing `tools/excluded_sids.json` | refresh `excluded` + `exclusion_reason` columns |

The script is idempotent — when in doubt, re-run with no flags. Use
`--rebuild` to ignore mtime cache and re-hash everything.

## Excluded SIDs — `tools/excluded_sids.json`

Some SIDs / engine families can't fit into the principled USF
representation without dragging engine-mechanism bookkeeping into the
schema. For example: Companion/Jay_Derrett engine (25 SIDs) is
aperiodic by design — voices never simultaneously realign, the song
is conceptually infinite, and storing a finite played-trace requires
either an arbitrary cut-off OR sub-jump-table positional info that
violates the USF principle.

Such SIDs are listed in `tools/excluded_sids.json` with a reason and
an `excluded_date`. The pipeline (`pipelines/build_from_usf.py` +
per-engine `write_usf` paths) calls `src.exclusions.check_or_raise`
early and refuses to process listed paths with a clear error pointing
back to the JSON. The DB picks up `excluded` (INTEGER) + `exclusion_reason`
(TEXT) columns from the JSON on `build_sid_db.py` rebuild.

To add an exclusion: append to `entries[]` in the JSON with `{path,
reason, excluded_date}`, then re-run `tools/build_sid_db.py`.

To query excluded SIDs:
```python
db.execute("SELECT path, exclusion_reason FROM sids WHERE excluded=1")
```

## Build environment

64-core EPYC, 512 GB RAM, dual 3090 GPUs. No sudo — everything from source in-tree.
xa65 assembler at `tools/xa65/xa/xa`. CUDA at `/usr/bin/nvcc`.

## Project structure

```
pipelines/              active engines — hubbard/ (Hubbard '85 family) + companion/
src/                    USF shared source — usf/ (grammar + reader/writer),
                        hubbard_emu.py, effect_detect.py, songlengths.py,
                        gt_parser.py, env.sh. Everything pre-USF-v2 moved
                        to deprecated/<topic>/.
docs/                   specifications and reference docs
tools/                  build tools (xa65, siddump, libsidplayfp)
hvsc84/                 HVSC #84 collection (not in git, gitignored)
deprecated/             earlier project phases — see deprecated/<topic>/README.md
```

## Earlier workstreams (now under `deprecated/`)

Pre-USF-v2 work lives in `deprecated/<topic>/` clusters, each with its
own README. The most relevant ones to know about:

- `deprecated/gt2_pipeline/` — the GT2 / GoatTracker conversion pipeline
  (static binary → USF v1) + bundled GoatTracker source distributions +
  the universal register-trace fallback
- `deprecated/v2_codegen/` — the GT2-era per-song 6502 codegen (V2/V3
  + Z3 + GPU optimisers)
- `deprecated/gt2_grading/` — Grade S/A/B/C/F bucketing tools + the
  HVSC coverage dashboard
- `deprecated/lean_codegen/` — the original per-engine Lean 4 codegen
  + Lean formal-methods tools
- `deprecated/usf1_pipelines/` — engines and helpers that never moved
  off USF v1
- `deprecated/sidxray/` — player reverse-engineering toolkit
- `pipelines/<engine>/docs/` — per-engine research material (format
  specs, disassemblies, version differences). Created via the
  `research-player` skill. ~47 engine subdirs today, covering both
  migrated engines and pre-migration research stash.

Each `deprecated/<topic>/README.md` describes what's there and how to
revive it if needed.
