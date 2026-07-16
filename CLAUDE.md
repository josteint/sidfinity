# CLAUDE.md — Instructions for continuing development

## Project goal

Build the SIDfinity universal SID music player and ML pipeline. Take the
HVSC catalogue of ~60,000 C64 SID files and translate every engine's binary
format into a single Unified SID Format (USF) — engine-neutral
musical data that an ML model can learn from. See `docs/PLAN.md` for the
roadmap.

## The canon — the four load-bearing documents

All four canon docs are imported verbatim below, every session (their full
text is already in context — do not re-read the files, and do not act on a
summary of them):

@docs/the_core_tenet.md

@docs/the_principle.md

@docs/the_trichotomy.md

@docs/the_convergence_ledger.md

The Convergence Ledger is fully in context so that a known problem-class is
RECOGNIZED, not just looked up — before choosing how to solve ANY non-trivial
problem, check it for a matching entry (the documented failure mode is solving
first and skipping the check). The verdict CODE
(`pipelines/hubbard/verify_cycle.py`) is the oracle all four route to.

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
- `deprecated/usf1_pipelines/` — engines that predate the current USF representation

`tools/regression.py` runs the full pipeline regression (Hubbard +
companion). Use it as the verdict after any composer change.

## MANDATORY before any new pipeline work

**Before any engine investigation, ask yourself three questions OUT LOUD (in your first text turn of the session). They form a hierarchy from family-wide foundation to per-SID specifics:**

1. **Do we have engine-family docs?** — `pipelines/<family>/docs/` is where family-wide research lives: format specs, player manuals, CSDB release notes, lineage, prior reverse-engineering. This is the FIRST thing acquired when work begins on a new player family (via the `research-player` skill at `.claude/skills/research-player/`). ~47 family-doc dirs exist today (`pipelines/future_composer/docs/`, `pipelines/goattracker/docs/`, ...). If a family-doc dir exists, READ IT BEFORE any per-SID work — it tells you the player's instruction semantics, instrument format, effect catalogue, byte encodings. Skipping this means re-deriving the format from raw bytes.

2. **Did I do full decompilation?** — does the SID have a hand-annotated `pipelines/<family>/<engine>/disassembly.s` already in the repo? Most migrated FC + Hubbard engines do (1000+ lines, hand-labelled with routine names + state-byte assignments). If yes, READ IT before any py65 fragment-disasm work — the structural labels (`L_7DCA`, `sub_7DBD`) are knowledge py65 cannot reconstruct. If no, generate one with `tools/seed_disassembly.py` and annotate the header BEFORE coding.

3. **Do we have per-engine RE notes?** — check `pipelines/<family>/<engine>/RE_NOTES.md` (often 500+ lines of state-byte assignments + flow narration + prior-session findings + known partial-cause analysis). If it exists, read FIRST.

Skipping these three questions cost a multi-hour wrong-guessing session on Hawkeye sub 6 (2026-06-06) — the answer was in `disassembly.s` + `RE_NOTES.md` (+ the FC v4.1 manual in `pipelines/future_composer/docs/`) and would have taken 5 minutes. See [[feedback_check_existing_engine_docs]].

Then:

1. **Check the engine's project memory** — `.claude/memory/project_<engine>.md`. Reads any prior session's root-cause analysis so you don't re-investigate from scratch.
2. **Re-anchor in The Principle** (imported above — don't Read the file again) before designing or changing any USF instrument/effect representation: run its tests against your proposal as adversarial checks, per its own §Provenance challenge. Load-bearing.
3. **Check `deprecated/` for prior attempts** before rewriting something from scratch.
4. **Convergence ledger reflex** — the full ledger is imported above; before choosing how to solve ANY non-trivial problem, CHECK it for a matching entry (a known class should be recognized from the in-context text — actively check, don't trust passive recall). Then follow its "How to use it": RECORD every solution on first sight (with the placement rule — technique in the entry, occurrences in `project_<engine>`), CANONICALIZE on the 2nd occurrence. `/uready-review` is the periodic maintainer.

## Doing a Hubbard '85 engine migration

Use the `migrate-hubbard-engine` skill at `.claude/skills/migrate-hubbard-engine/`. Short form:

1. The HVSC original is read directly from `hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.sid` — no copy needed.
2. Generate a seed disassembly: `tools/seed_disassembly.py …` → `pipelines/hubbard/<engine>/disassembly.s` → hand-annotate the header
3. Create `pipelines/hubbard/<engine>/config.py` (clone a similar existing one — Action Biker is a good template; Chimera if there's digi)
4. Create `pipelines/hubbard/<engine>/extract/engine_model.py` + `extract/to_usf.py`
5. Iterate: build → capture original vs rebuilt → fix first diff → repeat
6. Verify the per-frame instruction sequence via `pipelines.hubbard.verify.verify_all`

When the engine's instruction sequence matches, its USF + rebuilt SID go alongside the
HVSC original at `hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.{usf, sidfinity.sid}`.

## Working conventions

- **`pipelines.hubbard.verify.verify_all` is the verdict.** Returns subtune-level OK/FAIL via the SID WRITE-LOG (`siddump --writelog`, libsidplayfp ground truth): a subtune passes iff the rebuild's `(reg,val)` write sequence matches the original's over their overlap (same as `find_first_divergence`). It does NOT snapshot per-frame register state — that's Trap A (loses within-frame order, can't model multispeed, false-passes real bugs); the py65-snapshot verdict was removed 2026-06-07, having silently false-passed 25 Hubbard subtunes incl. all of Monty's multispeed. Digi subtunes use the `--writelog` flattened-`(reg,val)` check.
- **Regression scope by touched files** — don't run full regression on every edit, but don't skip it when shared code changed either:
  - `pipelines/<engine>/` only → that engine's verify only (e.g., `verify_featuredriven(CFG)` for FC, `verify_all([(cfg, sid)])` for Hubbard). Other families are physically untouched and can't regress.
  - `src/composer_runtime/`, `src/usf/types.py`, `pipelines/hubbard/verify_cycle.py`, or any shared plumbing → full `tools/regression.py` (one diff hits all engines).
  - Before commit → full `tools/regression.py` regardless of what was touched.
- **Regression portfolio — the standard family-closeout step.** When a feature-driven family's wide batch is mass-written (the family reaches its FULL coverage), derive its regression portfolio and wire it as **tier 1** in `tools/regression.py`; the full family batch (`tools/<engine>_family_batch.py`) is the **tier 2** milestone verdict. The portfolio is the EXACT minimum set of FULL members covering every feature dimension the corpus exercises ≥2× (factory knobs + instrument effects + pattern/track structure) — so one cheap regression run guards the whole feature space, not just one canary. Tool: `tools/select_regression_portfolio.py --engine <name>` (engine-parametric registry; `exact_multicover` is engine-blind — adding a family = a registry entry + a `<engine>_features` function). **Re-derive whenever a new fix lands a big new clump of FULLs** — the portfolio is only as current as its last derivation (it is NOT auto-triggered). Wired today: `fc_standard` (11 members) + `dmc_v4` (5 members, covering relocation / loop-target / dual-phase / per-tune-tuning / multi-subtune).
- **Wide-family iteration — DON'T full-batch every experiment.** A full family batch (`tools/<engine>_family_batch.py` over ~1.5k members) is ~1 hr; running it to test each composer/extract fix is the slow trap. Instead: **iterate on a fixed STRATIFIED SUBSET** (~100-150 members, stratified across the current first-divergence buckets — V1sr / V1flo / FCLO / pulse / ... — PLUS a slice of currently-FULL members for regression coverage), ~5 min (~12× faster). It tells you the fix's direction + obvious regressions before committing. Run the **full batch ONLY at round closeout** (the authoritative count + the mass-write, which must build every FULL member), or when a fix touches a hot path with broad regression risk. NB code-Jaccard clustering does NOT help pick the subset — within a family the player is ~identical; pass/fail varies by DATA (which orderlist loops to a transpose, which filter table is tiny). Stratify by first-diff bucket / feature-cover (the `select_regression_portfolio.py` basis), not code similarity. The closeout can also be INCREMENTAL: re-verify only partials + unsupported (where gains come from) + a FULL-regression sample, and reason about the fix's regression scope (e.g. a loop-target fix can't regress a FULL — a FULL never hit that path).
- **For writelog-partial debugging, start with `tools/find_first_divergence.py ORIG.sid REBUILD.sid --subtune N`.** It localises the first `(reg, val)` mismatch + names the voice/role (e.g. "V2 freq hi") in one command. THEN disassemble orig's effect for that register, THEN diff against the composer emitter. Do NOT start from py65 state traces or prior task descriptions — both go stale. Full protocol in [`feedback_writelog_divergence_recipe`](.claude/memory/feedback_writelog_divergence_recipe.md).
- **For engine-state divergence, use `tools/state_diff.py` + auto-generated map.**
  - Build the map: `python3 tools/state_map_gen.py --engine ENGINE --voice {1,2,3,all} --output MAP.py` — joins per-engine `pipelines/future_composer/<engine>/state_map.py` annotation with composer's xa65 labels. **DO NOT hand-craft state maps** (wrong addresses bit hard last session).
  - Run: `python3 tools/state_diff.py ORIG REBUILD --map MAP.py --subtune N`. Reports first diverging frame + an automatic Trap C check (IRQ count delta — see [`feedback_verification_modes`](.claude/memory/feedback_verification_modes.md)).
  - **EVENT-ALIGNED mode (Trap-C-free, prefer when available):** `--on-write TRIG --align-value VV` snapshots at every write to TRIG and compares by global event index. Works when the engine writes a fixed register exactly once per play() — the standard FC player: `--on-write D418 --align-value 1F`. `state_map_gen --sid SID.sid` derives per-member maps for the standard family (rebuild layout + orig reloc shift). Diagnostic theorem: **"writelog diverges + event-aligned state matches" = a missing/extra effect EMISSION**, not an engine-state bug (this is how Entrail's +$04 arp was found in minutes after an hour of frame-bucket chasing).
  - **When state_diff reports a divergence, always cross-check with `find_first_divergence.py` (writelog flat-prefix verdict).** If writelog matches, the state hint is noise. (The --on-write mode is exempt — it has no bucketing.)
- **Specialised diagnostic tools** (full inventory + when-to-use in [`tools/INVESTIGATION_BACKLOG.md`](tools/INVESTIGATION_BACKLOG.md)):
  - `tools/voice_writelog.py --voice {1,2,3}` — filter writelog to one voice; auto-tag each write with the likely engine routine (nolengset / pulse_prog / glide / etc.). Use when "which effect produced this write?" is the question.
  - `tools/pattern_stream_decode.py --addr HEX [--seq]` — decode FC pattern/seq stream bytes as readable commands ($Cx wave/inst, $Fx markers, glide triples, etc.). Use when the bug is "what byte does the pattern stream actually have at this offset?"
  - `siddump --memwatch-on-write TRIG ADDRS` — event-driven RAM snapshot. Captures the listed RAM addresses every time the CPU writes to TRIG. Use for SMC behavior + "show me the engine state at every $D404 write" investigations.
  - `tools/disasm_diff.py --orig SID --orig-range HEX-HEX --composer FILE --composer-label LABEL` — side-by-side orig disasm vs composer emitter (extracts the asm string from `_emit_*` functions). Use during step 3 of the recipe ("diff orig's effect code against the composer emitter line by line") to spot structural differences.
  - `tools/taint_source.py <sid> <LO-HI> [--all]` — GREY-BOX CLASSIFY an OFF-TABLE read: is its source RAM region STATIC (never written during play → REPRESENTABLE, capture the value/program) or DYNAMIC (written → hard residue)? Uses `--memtrace` (per-ACCESS, within-frame-complete — a per-frame `--memwatch` snapshot misses a write-then-restore inside one play()). Use when an off-table read is the first flat-stream divergence and you must decide fix-the-capture (static) vs accept-residue (dynamic). Landed the first family-4 FULL (Jupiter41). See ledger C2.
  - `siddump --writelog-per-irq` — emits the writelog stream bucketed PER PSID `play()` invocation (one `\|I` chunk per IRQ) instead of per siddump frame. Kills Trap C at the source — IRQ-bucketed streams align across mine/orig regardless of siddump's frame boundaries. Splits by play-entry cycle (origin-corrected: play entries are absolute PHI1 clocks, write-log cycles are relative to a per-frame base, so the splitter subtracts the base) and DROPS the init prefix (the writes before the first play-entry, frame-0 only — later-frame pre-entry writes are straddle tails and are kept). This is the capture behind `verify_all`'s CIA-tune verdict (see below). Add `--per-irq-debug` to print base / entry / write cycles to stderr for one frame. Implies `--writelog`.
  - `tools/effect_chain_profiler.py SID --subtune N --frames F1-F2 [--register HEX]` — attribute each SID write to its CPU PC by reading the store instruction's PC DIRECTLY off the pc-trace (every line carries PC + A/X/Y + the resolved effective `[d4xx]` address). Answers "which routine wrote this $D408 = $47?" in one command, grouped by play() invocation. NOTE: an earlier version reconstructed each write's cycle as `frame*19688+rel` and cycle-matched the pc-trace — that's the Trap-C pitfall (a siddump frame advances ~18,000 cyc, NOT 19688), so it drifted and mis-attributed writes to the PSID driver's idle spin loop ($04A5). Rewritten 2026-06-28 to avoid cycles entirely. Lesson: NEVER trust write→PC attribution that relies on reconstructing absolute cycles from siddump frames.
  - `tools/pattern_stream_verify.py --engine ENGINE` (or `--all`) — USF roundtrip check for the pattern-stream region. Verifies that orig and rebuild bytes match (accounting for `featuredriven_addr_shift` and the verbatim-pointer fixup). Catches data-emission regressions at extract/compose time.
  - `tools/divergence_census.py --engine ENGINE --results BATCH.jsonl [--partials]` — RESIDUE TRIAGE for a wide family: census a batch-results jsonl by status+reason, then CLUSTER either the detect-rejects (live first-divergence site, default) or the verify PARTIALS (`--partials`, by first writelog `(reg,role)` divergence). Turns N opaque failures into ranked root-cause buckets with representatives. Automates "stratify by first-diff bucket". Wired: dmc_v5 (one `ENGINES` entry per family). See [`reference_divergence_census`](.claude/memory/reference_divergence_census.md). Key lesson it proved: **detection ≠ FULL** — the partials, not the detect-rejects, are the FULL bottleneck.
  - `tools/dmc_canon_diff.py [--members family1|FILE] [--status JSONL] [--csv]` — A-PRIORI WEDGE ENUMERATOR (canon-player families): linear-align every member's reachable player code to the canonical player binary (`pipelines/dmc/docs/dmc4_player_embedded_1000.bin`), diff OPCODES + in-player OPERAND-REPOINTS (packer operands point below $1000, so wedge repoints into $1000-$17FF separate cleanly), Δ-mode-filter bulk state/table relocations, cluster by canon site, tag handled-vs-NEW, and split each cluster into partial/full carriers (`--status BATCH.jsonl`). The PROACTIVE complement to the reactive `_*_probe` detectors — enumerates the whole code-patch wedge space in ONE pass + audits the probes' true carrier counts. Proved DMC family-1's wedges are essentially fully handled: of 188 partials, 78% carry NO code wedge (= off-table/CIA hard residue), 17% a handled wedge, only **9 (4%) a genuine unhandled patch — all singletons** (no multi-carrier lever). LIMIT: misses immediate-value tweaks (hr_preset/cymbal) + re-assembled members (linear-align only). See [`reference_dmc_canon_diff`](.claude/memory/reference_dmc_canon_diff.md).
- **py65 misses dispatch bugs** (CIA timer, PSID speed). Ear-test new engines and any dispatch changes in real sidplayfp before declaring done. Prefer `siddump --memwatch` for state inspection — it uses libsidplayfp = ground truth.
- **Tooling reflex.** After each non-trivial debugging session (>30 min), ask: "what tool would have collapsed this to <5 min?" Add to [`tools/INVESTIGATION_BACKLOG.md`](tools/INVESTIGATION_BACKLOG.md) (or build immediately if <1 hour). If a tool starts producing misleading output or rotting, MODIFY or REMOVE it rather than working around it — bad tools cost more than no tool. Maintain context: when adding/modifying a diagnostic tool, update CLAUDE.md + the relevant memory so future sessions know it exists.
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

# Verify one engine's per-frame instruction sequence
python -c "
from pipelines.hubbard.verify import verify_all
from pipelines.hubbard.commando.config import COMMANDO
print(verify_all([(COMMANDO, 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')]))
"

# Build + verify ONE DMC family-1 / 2SID member (build helper — the family
# batch only runs in bulk; wraps dmc_v4_config -> write_dmc_usf -> build_dmc_sid)
python3 tools/dmc_build_one.py MUSICIANS/S/SilverFox/Seaside_99.sid --verify --localize

# Locate the NEXT DMC family-1 partial (first by hvsc path) + its first
# divergence, maintaining the hint queue tmp/dmc_f1_partials.jsonl. Re-confirms
# leading hints against current code (self-heals cluster flips + stale rows),
# stops at the first still-partial. Auto-seeds from the batch if the queue is
# missing. Use at session start instead of re-verifying from index 0.
python3 tools/dmc_next_partial.py

# Crash smoke-test BEFORE the ~10-min regression: builds a diverse DMC set
# (canonical / family-2 / page-3 reloc / out-of-image / 2SID-config) through
# config->USF->compose in ~40s. Catches a probe/composer change that crashes on
# a variant (e.g. gatemask_addr=None) so the full regression never dies mid-run.
python3 tools/dmc_smoke.py

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
| `pipelines/hubbard/verify.py` | `verify_all` — write-log overlap verdict (Hubbard verification; siddump ground truth, no register snapshots). |
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

## HVSC index — `hvsc84.parquet` (+ `engine_docs.csv`), via DuckDB

A **static catalogue** of every SID in `hvsc84/` (path, PSID header, engine
classification, songlength, exclusion), stored as a compact **git-tracked
Parquet** file (`hvsc84.parquet`, zstd, ~3 MB) and queried via **DuckDB**.
(History: SQLite blob → CSV 2026-06-15 → Parquet 2026-07-04.)

**Catalogue only — NO per-build verdicts.** The old build-status columns
(`verify_status`/`usf_path`/`sidfinity_md5`/`pipeline`) and the `src/sid_db.record_*`
write-through were removed 2026-07-04: zero readers, ~empty, palimpsest-prone
(a persisted verdict rots the moment extract/composer code changes), and the
full-file-rewrite write path was a concurrency hazard for parallel sessions. So
in normal dev **nothing writes the index** — it's read-mostly and parallel-safe.
Derive coverage on demand from a fresh family batch, never from a cached column.
Regenerate the catalogue with `tools/build_sid_db.py` (idempotent, ~13 s with
the mtime cache — only after an HVSC update / `sidid` re-run). Use for:

- **engine-by-engine iteration** (instead of folder-by-folder)
- **catalogue queries** (engine counts, longest tunes by engine, exclusions)

Query via the `src/sid_db` helper — it **shells out to the `duckdb` CLI binary**
(`~/.local/bin/duckdb`, on PATH), so it needs only `duckdb` on PATH, **no
env.sh / PYTHONPATH** (it just needs `src` importable for `import sid_db`,
which the tools add to `sys.path` themselves). sqlite3-style:

```python
from src import sid_db
for path, title in sid_db.query(
    "SELECT path, title FROM sids "
    "WHERE engine='Rob_Hubbard' ORDER BY songlength_s DESC LIMIT 10"):
    print(path, title)
# or: db = sid_db.connect(); db.execute(sql, params).fetchall()/.fetchone()
```

Each `query()` spawns one `duckdb` process reading the parquet — fine for
occasional queries; for a per-row loop use `sid_db.read_all()` (one duckdb -json
process) and filter in Python. DuckDB SQL: no `SUM(bool)` (use `SUM(CASE WHEN …
THEN 1 ELSE 0 END)`); `?` params, LIKE, `random()` all work. Schema
(columns/types) + read/write helpers live in `src/sid_db.py`; the
walk/hash/classify that builds the catalogue is in `tools/build_sid_db.py`.
Tables: `sids` (parquet) + `engine_docs` (csv). Ad-hoc CLI:
`duckdb -c "SELECT … FROM read_parquet('hvsc84.parquet')"`.

**Coverage / FULL-list source of truth** = a fresh family batch, NOT stored
`.usf`/`.sid` files or the index. Batch results (`tmp/<engine>_*_results.jsonl`)
are stamped with a `code_hash` (`src/code_fingerprint.py`): on resume a row is
reused ONLY if its hash matches the current engine dependency set, so a code
change auto-re-verifies exactly the members it could have affected — no more
"remember to delete the jsonl", and no stale-verdict palimpsests. The
`*_mass_write.py` tools likewise skip (and warn about) any FULL row whose
code_hash is stale, so they never write an unverified build to disk.

### Per-family documentation state — `engine_docs` table

A second table records, per engine family, **how far we've researched its
player** — so a future session can see at a glance which families are
ready to disassemble vs which still need a research sweep. It's a
research-PROGRESS ladder, NOT a content-volume measure:

| `doc_state` | meaning |
|---|---|
| `NONE` | no `pipelines/<family>/` dir; never researched (family absent from the table) |
| `LITTLE` | single stub `research.md`; no real sweep yet |
| `SOME` | research-engine run / substantial corpus, but with known gaps to chase |
| `OK` | research-engine sweep **complete** → cleared to start disassembling |

A family reaches `OK` by *completing* a `research-player` sweep, regardless
of how much was found. Source of truth is the version-controlled
`tools/engine_docs.json` (`{family: {state, notes, updated}}`);
`build_sid_db.py` materialises it into `engine_docs.csv` (one row per family,
annotated with the `sids.engine` strings that map to it + total SID count).
The engine→family map lives in `build_sid_db.engine_to_family`.

```python
# families cleared to start RE:
sid_db.query("SELECT family, sid_count FROM engine_docs WHERE doc_state='OK'")
```

After editing `engine_docs.json`, refresh just `engine_docs.csv` in seconds
with `python3 tools/apply_engine_docs.py` (reads the parquet for counts, no
re-walk). Nothing write-throughs the catalogue anymore — it's regenerated
wholesale by `build_sid_db.py`, so parallel sessions never race on it.

### When to re-run `tools/build_sid_db.py`

| Trigger | Why |
|---|---|
| After an HVSC update (#85 lands) | re-walk + re-classify added/removed SIDs |
| After re-running `sidid` | refresh engine column |
| After editing `tools/excluded_sids.json` | refresh `excluded` + `exclusion_reason` columns |
| After editing `tools/engine_docs.json` | refresh `engine_docs` (or just `tools/apply_engine_docs.py`) |
| After a `research-player` sweep completes for a family | bump its `engine_docs.json` state (→ `OK`) |

(No per-build triggers anymore — the catalogue is static; build status is not
tracked here. Coverage comes from a fresh family batch.)

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
sid_db.query("SELECT path, exclusion_reason FROM sids WHERE excluded=1")
```

## Build environment

**Current host (until ~Sept 2026): Lenovo X230, 8 cores** — size worker
pools to 8 (`Pool(8)`), expect long wall times for corpus-wide batches, and
note **pytest is not installed** here (use `tools/regression.py` as the
gate; the `pytest pipelines/` smoke tests only run on the big box). From
September the primary machine is again the 64-core EPYC, 512 GB RAM, dual
3090 GPUs — update this paragraph when that happens.

No sudo — everything from source in-tree.
xa65 assembler at `tools/xa65/xa/xa`. CUDA at `/usr/bin/nvcc`. Python packages
install into `.pylocal/` (on `env.sh`'s PYTHONPATH; gitignored) via
`pip install --no-cache-dir --target .pylocal/lib/python3.12/site-packages <pkg>`
(PEP 668 blocks a plain `pip install`). Source `src/env.sh` before running
tools — it puts `.pylocal` + `src` on PYTHONPATH.

**DuckDB = the CLI binary at `~/.local/bin/duckdb`** (v1.5.3, on PATH,
per-user — NOT in the repo, NOT the python module). `src/sid_db` shells out to
it for index reads, so **DB queries need only `duckdb` on PATH — no env.sh /
PYTHONPATH / .pylocal** (deliberate: the python-module path was brittle). The
python `duckdb` module is NOT installed/used. Ad-hoc:
`duckdb -c "SELECT … FROM read_parquet('hvsc84.parquet')"`.
(The snap `duckdb` at `/snap/bin/duckdb` is broken — `snap-confine` error — don't use it.)

## Project structure

```
pipelines/              active engines — hubbard/ (Hubbard '85 family) + companion/
src/                    USF shared source — usf/ (grammar + reader/writer),
                        composer_runtime/ (xa65 + PSID header, engine-blind),
                        hubbard_emu.py, songlengths.py, sid_db.py,
                        code_fingerprint.py, code_flow.py, exclusions.py,
                        env.sh. Everything pre-USF moved to deprecated/<topic>/.
docs/                   specifications and reference docs
tools/                  build tools (xa65, siddump, libsidplayfp)
hvsc84/                 HVSC #84 collection (not in git, gitignored)
deprecated/             earlier project phases — see deprecated/<topic>/README.md
```

## Earlier workstreams (now under `deprecated/`)

Pre-USF work lives in `deprecated/<topic>/` clusters, each with its
own README. The most relevant ones to know about:

- `deprecated/gt2_pipeline/` — the GT2 / GoatTracker conversion pipeline
  (static binary → the original pre-refactor USF) + bundled GoatTracker source distributions +
  the universal register-trace fallback
- `deprecated/v2_codegen/` — the GT2-era per-song 6502 codegen (V2/V3
  + Z3 + GPU optimisers)
- `deprecated/gt2_grading/` — Grade S/A/B/C/F bucketing tools + the
  HVSC coverage dashboard
- `deprecated/lean_codegen/` — the original per-engine Lean 4 codegen
  + Lean formal-methods tools
- `deprecated/usf1_pipelines/` — engines and helpers that never moved
  off the original pre-refactor USF
- `deprecated/sidxray/` — player reverse-engineering toolkit
- `pipelines/<engine>/docs/` — per-engine research material (format
  specs, disassemblies, version differences). Created via the
  `research-player` skill. ~47 engine subdirs today, covering both
  migrated engines and pre-migration research stash.

Each `deprecated/<topic>/README.md` describes what's there and how to
revive it if needed.
