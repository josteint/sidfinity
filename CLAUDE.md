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

## The two verification modes — read alongside the CORE TENET

The project has EXACTLY TWO modes for declaring a rebuild correct — i.e.
**per-frame instruction-sequence exact** (the rebuilt SID is NOT byte-for-byte
identical to HVSC's binary; we compose our own engine — only the `$D400-$D418`
write stream matches). Anything else is wrong. Three traps eat hours of
session time; each is explicitly documented.

**Mode 1 — frame-by-frame instruction sequence (tracker music).**
Each PSID `play()` invocation emits a finite, ordered sequence of writes
to `$D400-$D418`. The rebuild matches iff that per-`play()` sequence
matches the original, frame by frame, for the whole song. WITHIN a frame
the ORDER of writes matters (gate edges, test bit, ADSR delay, $D418
clicks). The CYCLE TIMESTAMPS within a frame do NOT. This is what 99% of
HVSC needs.

- Tool: `tools/siddump --writelog` (capture).
- Comparator: `pipelines.hubbard.verify_cycle.compare_instruction_stream`
  (flat-prefix over `(reg, val)`, cycle dropped). Robust against siddump
  frame-bucket drift (Trap C).
- Localizer: `tools/find_first_divergence.py`.
- **Engines that emit their OWN init (pure trichotomy):** when the composer
  emits a universal reset + typed priming instead of reproducing the original
  engine's init write SEQUENCE (e.g. FC `init_style='universal_reset'`), the
  two streams share an identical play stream but differ by a short init prefix
  of different length — so a flat prefix match diverges at frame 0. Use
  `compare_instruction_stream(mode='trichotomy')`: it recovers the play-stream
  shift, then checks (A) the end-of-init chip STATE matches (the priming) and
  (B) the aligned play stream matches (+ close length tolerance). It reduces to
  a full prefix match when inits coincide, so verbatim-init engines are
  unaffected. This is the answer to "how do we compare when we have our own
  init" — see [[feedback_init_trichotomy]] + [[project_adrenalin]].
- **CIA-timed tunes (PSID `speed != 0`):** the flat per-50Hz-frame capture
  buckets init + first play() out of phase between orig and a rebuild with a
  different init length (Trap C specialised to CIA), so `verify_all` captures
  these subtunes PER `play()` via `tools/siddump --writelog-per-irq`
  (`writelog_per_irq_capture`, init prefix dropped) and flat-compares the
  flattened play stream. Detected by the PSID `speed` bit; vblank subtunes
  use the flat path unchanged. Validated against the `--pc-trace` oracle.

**Mode 2 — cycle-exact (digi only).**
For digi (sample playback timing IS the signal), every `(cycle, reg, val)`
must match. Used for Chimera and similar.

- Tool: same `--writelog`.
- Comparator: `pipelines.hubbard.verify_cycle.compare_strict`.

**Trap A — snapshotting registers instead of capturing the write
sequence.** Half the early project did this. Loses within-frame writes
and order. Never use register snapshots for Mode 1 verdict.

**Trap B — chasing cycle-exactness for music.** Within-frame cycle
position is observation, not signal. Don't try to make cycles match for
tracker music; same writes in the same order at different cycles within
a frame are equivalent.

**Trap C — siddump frame buckets ≠ PSID `play()` invocations.** siddump
runs 19688 cycles per loop iteration; PAL VBI is 19656. So per siddump
"frame" the PSID `play()` vector fires usually 1, sometimes 0, sometimes
2 times. Consequences:

- `compare_instruction_stream` is ROBUST (flat concatenation across
  frames; sequence is identical regardless of bucket boundary).
- `tools/state_diff.py` (memwatch snapshots) is NOT robust — state is
  sampled at siddump frame boundaries, not at IRQ boundaries. A state
  "divergence" at siddump-frame N may be IRQ misalignment, not a real
  engine bug. Cross-check against `find_first_divergence.py` (writelog
  ground truth) before treating state_diff localization as a verdict.

Full discussion (with worked Hawkeye examples for each trap) in
[`feedback_verification_modes`](.claude/memory/feedback_verification_modes.md).

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

**Before any engine investigation, ask yourself three questions OUT LOUD (in your first text turn of the session). They form a hierarchy from family-wide foundation to per-SID specifics:**

1. **Do we have engine-family docs?** — `pipelines/<family>/docs/` is where family-wide research lives: format specs, player manuals, CSDB release notes, lineage, prior reverse-engineering. This is the FIRST thing acquired when work begins on a new player family (via the `research-player` skill at `.claude/skills/research-player/`). ~47 family-doc dirs exist today (`pipelines/future_composer/docs/`, `pipelines/goattracker/docs/`, ...). If a family-doc dir exists, READ IT BEFORE any per-SID work — it tells you the player's instruction semantics, instrument format, effect catalogue, byte encodings. Skipping this means re-deriving the format from raw bytes.

2. **Did I do full decompilation?** — does the SID have a hand-annotated `pipelines/<family>/<engine>/disassembly.s` already in the repo? Most migrated FC + Hubbard engines do (1000+ lines, hand-labelled with routine names + state-byte assignments). If yes, READ IT before any py65 fragment-disasm work — the structural labels (`L_7DCA`, `sub_7DBD`) are knowledge py65 cannot reconstruct. If no, generate one with `tools/seed_disassembly.py` and annotate the header BEFORE coding.

3. **Do we have per-engine RE notes?** — check `pipelines/<family>/<engine>/RE_NOTES.md` (often 500+ lines of state-byte assignments + flow narration + prior-session findings + known partial-cause analysis). If it exists, read FIRST.

Skipping these three questions cost a multi-hour wrong-guessing session on Hawkeye sub 6 (2026-06-06) — the answer was in `disassembly.s` + `RE_NOTES.md` (+ the FC v4.1 manual in `pipelines/future_composer/docs/`) and would have taken 5 minutes. See [[feedback_check_existing_engine_docs]].

Then:

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
  - `siddump --writelog-per-irq` — emits the writelog stream bucketed PER PSID `play()` invocation (one `\|I` chunk per IRQ) instead of per siddump frame. Kills Trap C at the source — IRQ-bucketed streams align across mine/orig regardless of siddump's frame boundaries. Splits by play-entry cycle (origin-corrected: play entries are absolute PHI1 clocks, write-log cycles are relative to a per-frame base, so the splitter subtracts the base) and DROPS the init prefix (the writes before the first play-entry, frame-0 only — later-frame pre-entry writes are straddle tails and are kept). This is the capture behind `verify_all`'s CIA-tune verdict (see below). Add `--per-irq-debug` to print base / entry / write cycles to stderr for one frame. Implies `--writelog`.
  - `tools/effect_chain_profiler.py SID --subtune N --frames F1-F2 [--register HEX]` — attribute each SID write to its CPU PC by cross-referencing writelog + pc-trace. Answers "which routine wrote this $D408 = $47?" in one command.
  - `tools/pattern_stream_verify.py --engine ENGINE` (or `--all`) — USF roundtrip check for the pattern-stream region. Verifies that orig and rebuild bytes match (accounting for `featuredriven_addr_shift` and the verbatim-pointer fixup). Catches data-emission regressions at extract/compose time.
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

Schema in `tools/build_sid_db.py` (tables `sids` + `engine_docs`,
indexes on engine / pipeline / md5).

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
`build_sid_db.py` materialises it into `engine_docs` (one row per family,
annotated with the `sids.engine` strings that map to it + total SID count).
The engine→family map lives in `build_sid_db.engine_to_family`.

```python
# families cleared to start RE:
db.execute("SELECT family, sid_count FROM engine_docs WHERE doc_state='OK'")
```

After editing `engine_docs.json`, refresh just this table in seconds with
`python3 tools/apply_engine_docs.py` (no full re-hash). **Single-writer DB
in `delete` journal mode — don't run it while a build/pipeline write is mid
-transaction** (it waits on a 30 s busy_timeout, but a concurrent writer
without one could see "database is locked").

### When to re-run `tools/build_sid_db.py`

| Trigger | Why |
|---|---|
| After migrating a new engine to `pipelines/` | refresh `pipeline` column |
| After running the build for an engine | refresh `usf_path` / `sidfinity_md5` |
| After an HVSC update (#85 lands) | re-walk + re-classify added/removed SIDs |
| After re-running `sidid` | refresh engine column |
| After `verify_all` (future hook) | refresh `verify_status` columns |
| After editing `tools/excluded_sids.json` | refresh `excluded` + `exclusion_reason` columns |
| After editing `tools/engine_docs.json` | refresh `engine_docs` (or just `tools/apply_engine_docs.py`) |
| After a `research-player` sweep completes for a family | bump its `engine_docs.json` state (→ `OK`) |

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
