# CLAUDE.md — Instructions for continuing development

## Project goal

Build the SIDfinity universal SID music player and ML pipeline. Take the
HVSC catalogue of ~60,000 C64 SID files and translate every engine's binary
format into a single Unified SID Format (USF) — engine-neutral
musical data that an ML model can learn from. Strategy: grind ENGINE BY
ENGINE to full family coverage (no canary sampling — pass/fail varies by
per-member data/patches, not player code; superseded plan archived at
`deprecated/old_docs/canary_picker.md`). Next family = the largest
un-migrated family whose `engine_docs` state is OK (research done), via
the `hvsc85.parquet` catalogue; within a family, work the next-partial-
by-path loop and let each fix propagate through the batch. Move 1 (the
composer unification, `docs/the_move-1_plan.md`) waits until the
grind is done or demonstrably saturated — the user decides; NO automatic
trigger. Original 2026-04 vision doc:
`deprecated/old_docs/PLAN_2026_04.md`.

## The canon — the four load-bearing documents

All four canon docs are imported verbatim below, every session (their full
text is already in context — do not re-read the files, and do not act on a
summary of them):

@docs/the_core_tenet.md

@docs/the_principle.md

@docs/the_trichotomy.md

@docs/the_convergence_ledger.md

The Convergence Ledger's RECOGNITION layer (index + per-entry signature
cards) is fully in context so that a known problem-class is RECOGNIZED, not
just looked up — before choosing how to solve ANY non-trivial problem, check
it for a matching entry (the documented failure mode is solving first and
skipping the check). On a match, READ the full entry at `docs/ledger/C<n>.md`
BEFORE applying — a card is never enough to act on. The verdict CODE
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

Families shipping through the USF pipeline today (per-family status/counts
live in each family's `project_<engine>` memory + MEMORY.md, not here):

- **Hubbard '85** (`pipelines/hubbard/<engine>/`) — feature-driven asm
  composition out of the shared composer; whole family exact.
- **Companion strains** (`pipelines/companion/<engine>/`) — Up_up_and_Away,
  Bowden-canonical, Clever_Music, Henrys_House, Yes_Tune,
  C64_Music_Examples, Jay_Derrett.
- **Future Composer** (`pipelines/future_composer/`) — Tel-variant canaries
  + the dominant "standard" player (wide batch mass-written).
- **DMC** (`pipelines/dmc/`) — THE FOCUS ENGINE (largest HVSC family);
  v4/v5 + 2SID/3SID + compilations. See [[project_dmc]].
- **GoatTracker V1** (`pipelines/goattracker/v1/`) — extract + composer
  built, wide batch run. NOT yet wired into regression.py.
- **basic_program** (`pipelines/basic_program/`) — RSID-BASIC trace-lift →
  USF round-trip.
- **Music Assembler** (`pipelines/music_assembler/`) — 3rd-largest family
  (6,351 SIDs); SID → USF → SID, wide batch 61.6% FULL. Tier-1 portfolio +
  the Freespace_2075 DMC+MA heterogeneous canary. See
  [[project_music_assembler_target]].

`tools/regression.py` is the verdict across the migrated families
(Hubbard + companion + C64ME + Jay_Derrett + FC + DMC + basic_program +
Music_Assembler; tier-1 portfolios for FC/DMC/basic/MA). It prints the current ok /
known-partial / regressed counts and enumerates the pre-existing partial
subtunes — treat it as the source of truth, not this file.

**Layout — `pipelines/`** (~50 family dirs; most are research-doc stubs
from `research-player` sweeps — the active migration trees are marked):
```
pipelines/
├── composer.py         ← THE composer for Hubbard '85 + companion
│                          (~5k lines: 18 routine chunks, data emitters,
│                          _Inputs adapters, dispatch)
├── build_from_usf.py   ← Public entry; thin wrapper around composer
├── engine_model.py     ← Typed feature dataclasses
├── hubbard/            ← ACTIVE. Shared Python core (codec, verify, sfx,
│   │                     digi, instrument modelling) + per-tune extracts
│   ├── verify.py / verify_cycle.py
│   ├── note_codec.py / engine_constants.py / inst_*.py
│   ├── sfx.py / sample.py / flac_io.py / digi_pack.py
│   ├── config.py       ← EngineConfig (extract path only)
│   └── <engine>/       config.py + extract/{engine_model,to_usf}.py
├── companion/          ← ACTIVE. Companion-strain engines (Up_up_and_Away,
│                          Bowden-canonical, Clever_Music, Henrys_House,
│                          Yes_Tune, C64_Music_Examples, Jay_Derrett)
├── future_composer/    ← ACTIVE. FC family: Tel canaries + standard/
│                          (own composer_asm.py, verify.py)
├── dmc/                ← ACTIVE. THE FOCUS ENGINE: v4/ + v5/ (factory,
│                          dataflow extract, composer_asm, compilation)
├── goattracker/        ← ACTIVE. v1/ extract + composer
├── music_assembler/    ← ACTIVE. 3rd-largest family: locate + packed-format
│                          decode + composer_asm + to_usf/from_usf +
│                          heterogeneous (the DMC+MA member)
├── basic_program/      ← ACTIVE. RSID-BASIC trace-lift (semantic_lift,
│                          usf_roundtrip)
├── <family>/docs/      ← ~50 research-doc dirs (soundmonitor, jch_*, …)
└── README.md
```

Older paths live under `deprecated/`:
- `deprecated/lean_codegen/` — the per-engine Lean 4 codegen
- `deprecated/usf1_pipelines/` — engines that predate the current USF representation

`tools/regression.py` runs the full pipeline regression (all migrated
families). Use it as the verdict after any composer change.

## MANDATORY before any new pipeline work

**Before any engine investigation, ask yourself three questions OUT LOUD (in your first text turn of the session). They form a hierarchy from family-wide foundation to per-SID specifics:**

1. **Do we have engine-family docs?** — `pipelines/<family>/docs/` is where family-wide research lives: format specs, player manuals, CSDB release notes, lineage, prior reverse-engineering. This is the FIRST thing acquired when work begins on a new player family (via the `research-player` skill at `.claude/skills/research-player/`). ~50 family-doc dirs exist today (`pipelines/future_composer/docs/`, `pipelines/goattracker/docs/`, ...). If a family-doc dir exists, READ IT BEFORE any per-SID work — it tells you the player's instruction semantics, instrument format, effect catalogue, byte encodings. Skipping this means re-deriving the format from raw bytes.

2. **Did I do full decompilation?** — does the SID have a hand-annotated `pipelines/<family>/<engine>/disassembly.s` already in the repo? Most migrated FC + Hubbard engines do (1000+ lines, hand-labelled with routine names + state-byte assignments). If yes, READ IT before any py65 fragment-disasm work — the structural labels (`L_7DCA`, `sub_7DBD`) are knowledge py65 cannot reconstruct. If no, generate one with `tools/seed_disassembly.py` and annotate the header BEFORE coding.

3. **Do we have per-engine RE notes?** — check `pipelines/<family>/<engine>/RE_NOTES.md` (often 500+ lines of state-byte assignments + flow narration + prior-session findings + known partial-cause analysis). If it exists, read FIRST.

Skipping these three questions cost a multi-hour wrong-guessing session on Hawkeye sub 6 (2026-06-06) — the answer was in `disassembly.s` + `RE_NOTES.md` (+ the FC v4.1 manual in `pipelines/future_composer/docs/`) and would have taken 5 minutes. See [[feedback_check_existing_engine_docs]].

Then:

1. **Check the engine's project memory** — `.claude/memory/project_<engine>.md`. Reads any prior session's root-cause analysis so you don't re-investigate from scratch.
2. **Re-anchor in The Principle** (imported above — don't Read the file again) before designing or changing any USF instrument/effect representation: run its tests against your proposal as adversarial checks, per its own §Provenance challenge. Load-bearing.
3. **Check `deprecated/` for prior attempts** before rewriting something from scratch.
4. **Convergence ledger reflex** — the ledger's recognition layer (index + cards) is imported above; before choosing how to solve ANY non-trivial problem, CHECK it for a matching entry (a known class should be recognized from the in-context cards — actively check, don't trust passive recall); on a match READ the full entry at `docs/ledger/C<n>.md` before applying. Then follow its "How to use it": RECORD every solution on first sight (entry file + index row + recognition card; technique in the entry, occurrences in `project_<engine>`), CANONICALIZE on the 2nd occurrence. `/uready-review` is the periodic maintainer.

## Doing a Hubbard '85 engine migration

Use the `migrate-hubbard-engine` skill at `.claude/skills/migrate-hubbard-engine/`. Short form:

1. The HVSC original is read directly from `hvsc85/MUSICIANS/H/Hubbard_Rob/<Engine>.sid` — no copy needed.
2. Generate a seed disassembly: `tools/seed_disassembly.py …` → `pipelines/hubbard/<engine>/disassembly.s` → hand-annotate the header
3. Create `pipelines/hubbard/<engine>/config.py` (clone a similar existing one — Action Biker is a good template; Chimera if there's digi)
4. Create `pipelines/hubbard/<engine>/extract/engine_model.py` + `extract/to_usf.py`
5. Iterate: build → capture original vs rebuilt → fix first diff → repeat
6. Verify the per-frame instruction sequence via `pipelines.hubbard.verify.verify_all`

When the engine's instruction sequence matches, its USF + rebuilt SID go alongside the
HVSC original at `hvsc85/MUSICIANS/H/Hubbard_Rob/<Engine>.{usf, sidfinity.sid}`.

## Working conventions

- **`pipelines.hubbard.verify.verify_all` is the verdict.** Returns subtune-level OK/FAIL via the SID WRITE-LOG (`siddump --writelog`, libsidplayfp ground truth): a subtune passes iff the rebuild's `(reg,val)` write sequence matches the original's over their overlap (same as `find_first_divergence`). It does NOT snapshot per-frame register state — that's Trap A (loses within-frame order, can't model multispeed, false-passes real bugs); the py65-snapshot verdict was removed 2026-06-07, having silently false-passed 25 Hubbard subtunes incl. all of Monty's multispeed. Digi subtunes use the `--writelog` flattened-`(reg,val)` check.
- **Regression scope by touched files** — don't run full regression on every edit, but don't skip it when shared code changed either:
  - `pipelines/<engine>/` only → that engine's verify only (e.g., `verify_featuredriven(CFG)` for FC, `verify_all([(cfg, sid)])` for Hubbard). Other families are physically untouched and can't regress.
  - `src/composer_runtime/`, `src/usf/types.py`, `pipelines/hubbard/verify_cycle.py`, or any shared plumbing → full `tools/regression.py` (one diff hits all engines).
  - Before commit → full `tools/regression.py` regardless of what was touched.
- **Regression portfolio — the standard family-closeout step.** When a feature-driven family's wide batch is mass-written (the family reaches its FULL coverage), derive its regression portfolio and wire it as **tier 1** in `tools/regression.py`; the full family batch (`tools/<engine>_family_batch.py`) is the **tier 2** milestone verdict. The portfolio is the EXACT minimum set of FULL members covering every feature dimension the corpus exercises ≥2× (factory knobs + instrument effects + pattern/track structure) — so one cheap regression run guards the whole feature space, not just one canary. Tool: `tools/select_regression_portfolio.py --engine <name>` (engine-parametric registry; `exact_multicover` is engine-blind — adding a family = a registry entry + a `<engine>_features` function). **Re-derive whenever a new fix lands a big new clump of FULLs** — the portfolio is only as current as its last derivation (it is NOT auto-triggered). Wired today: `fc_standard` (11 members) + `dmc_v4` (5 members, covering relocation / loop-target / dual-phase / per-tune-tuning / multi-subtune) + `basic_program` (tools/basic_program_regression_portfolio.json) + `music_assembler` (16 members + the Freespace_2075 DMC+MA cross-family canary). NOTE the portfolio is only half the wiring: `regression.py`'s per-family summary AND its **exit-code check** are a hardcoded family list, so a new family must be added to both or its failures print without failing the gate.
- **Wide-family iteration — DON'T full-batch every experiment.** A full family batch (`tools/<engine>_family_batch.py` over ~1.5k members) is ~1 hr; running it to test each composer/extract fix is the slow trap. Instead: **iterate on a fixed STRATIFIED SUBSET** (~100-150 members, stratified across the current first-divergence buckets — V1sr / V1flo / FCLO / pulse / ... — PLUS a slice of currently-FULL members for regression coverage), ~5 min (~12× faster). It tells you the fix's direction + obvious regressions before committing. Run the **full batch ONLY at round closeout** (the authoritative count + the mass-write, which must build every FULL member), or when a fix touches a hot path with broad regression risk. NB code-Jaccard clustering does NOT help pick the subset — within a family the player is ~identical; pass/fail varies by DATA (which orderlist loops to a transpose, which filter table is tiny). Stratify by first-diff bucket / feature-cover (the `select_regression_portfolio.py` basis), not code similarity. The closeout can also be INCREMENTAL: re-verify only partials + unsupported (where gains come from) + a FULL-regression sample, and reason about the fix's regression scope (e.g. a loop-target fix can't regress a FULL — a FULL never hit that path).
- **Carrier refactors are gated by BYTE-IDENTITY, not re-verification.** A
  carrier refactor moves WHERE information lives (params→typed field,
  composer→extract, renames, writer-only output) without changing WHAT the
  composer emits. Gate: `tools/golden_sid_diff.py` — capture a pre-change
  baseline over a golden set (regression portfolio + every member exercising
  the touched feature), apply the change, require every rebuilt `.sid`
  byte-identical (MD5). Byte-identity ⇒ identical write stream ⇒ identical
  verdict — stronger and ~100× cheaper than re-verifying. Precedent: DMC
  Phases A+D (offtable_redirect elimination, the USF keyword renames).
  Move-1's D-moves are all carrier refactors; this is their gate too. (A
  fix that DOES change emission is not a carrier refactor — normal
  verify/regression applies.)
- **For writelog-partial debugging, start with `tools/find_first_divergence.py ORIG.sid REBUILD.sid --subtune N`.** It localises the first `(reg, val)` mismatch + names the voice/role (e.g. "V2 freq hi") in one command. THEN disassemble orig's effect for that register, THEN diff against the composer emitter. Do NOT start from py65 state traces or prior task descriptions — both go stale. Full protocol in [`feedback_writelog_divergence_recipe`](.claude/memory/feedback_writelog_divergence_recipe.md).
- **For engine-state divergence, use `tools/state_diff.py` + auto-generated map.**
  - Build the map: `python3 tools/state_map_gen.py --engine ENGINE --voice {1,2,3,all} --output MAP.py` — joins per-engine `pipelines/future_composer/<engine>/state_map.py` annotation with composer's xa65 labels. **DO NOT hand-craft state maps** (wrong addresses bit hard last session).
  - Run: `python3 tools/state_diff.py ORIG REBUILD --map MAP.py --subtune N`. Reports first diverging frame + an automatic Trap C check (IRQ count delta — see [`feedback_verification_modes`](.claude/memory/feedback_verification_modes.md)).
  - **EVENT-ALIGNED mode (Trap-C-free, prefer when available):** `--on-write TRIG --align-value VV` snapshots at every write to TRIG and compares by global event index. Works when the engine writes a fixed register exactly once per play() — the standard FC player: `--on-write D418 --align-value 1F`. `state_map_gen --sid SID.sid` derives per-member maps for the standard family (rebuild layout + orig reloc shift). Diagnostic theorem: **"writelog diverges + event-aligned state matches" = a missing/extra effect EMISSION**, not an engine-state bug (this is how Entrail's +$04 arp was found in minutes after an hour of frame-bucket chasing).
  - **When state_diff reports a divergence, always cross-check with `find_first_divergence.py` (writelog flat-prefix verdict).** If writelog matches, the state hint is noise. (The --on-write mode is exempt — it has no bucketing.)
- **Specialised diagnostic tools** (full inventory + when-to-use in [`tools/INVESTIGATION_BACKLOG.md`](tools/INVESTIGATION_BACKLOG.md)):
  - `tools/voice_writelog.py --voice {1,2,3}` — filter writelog to one voice; auto-tag each write with the likely engine routine (nolengset / pulse_prog / glide / etc.). Use when "which effect produced this write?" is the question.
  - `tools/pattern_stream_decode.py --addr HEX [--seq]` — decode FC pattern/seq stream bytes as readable commands ($Cx wave/inst, $Fx markers, glide triples, etc.). Use when the bug is "what byte does the pattern stream actually have at this offset?"
  - `siddump --memwatch-on-write TRIG ADDR[,ADDR...]` — event-driven RAM snapshot. Captures the listed RAM addresses every time the CPU writes to TRIG. Use for SMC behavior + "show me the engine state at every $D404 write" investigations. The address list is ONE **comma-separated** argument; siddump now hard-errors on any unrecognised argument (it used to swallow stray numbers as `--subtune`/`--duration` and emit a plausible WRONG dump). NB **`--subtune` is 1-BASED** (0 = the tune's start song) while the rest of the project counts from 0 — a verdict's "sub k" is `--subtune k+1`.
  - `siddump --peek-post-init HEX-HEX[,HEX-HEX...]` — CPU-EYE post-init bytes
    THROUGH the MMU: banked-in ROM (incl. psiddrv's PATCHED KERNAL vectors —
    invisible to a RAM-only `--memwatch`, absent from ROM files), the 6510
    port, and libsidplayfp's power-on RAM pattern, in one `PEEK:` line. Use
    when an engine sonifies ENVIRONMENT bytes (ledger C29 — Super_Seven's
    truncated-copy KERNAL-tail sector window). Consumed by the DMC extract's
    `_cpu_peek`.
  - `siddump --reinit-snapshot PC LO-HI` — GROUND-TRUTH PC-triggered RAM-window
    capture (native-capture Phase 1): COLD = RAM[LO..HI] at the first
    play-vector entry (post-init), WARM = at the first play-vector entry after
    PC EXECUTES (= end of that play()); one `SNAP:COLD=…|WARM=…` line.
    Execution is discriminated from a DATA read of PC by the ≥3-consecutive-
    ascending-reads bus signature (ledger C36 — a bare `addr==PC` check
    false-fires and returns a plausible WRONG snapshot). Serves the DMC C19
    shape-B ghost capture (`_reinit_windows_via_siddump`; the py65 path is
    deleted). Prefer extending THIS mechanism over py65 for new observations —
    architecture decided in `docs/siddump_native_capture_decision.md`.
  - `siddump --pc-watch LIST BEFORE-AFTER [--pc-watch-first] [--pc-watch-abs
    LO-HI]` — GROUND-TRUTH executed-PC event stream (native-capture Phase 2):
    one `|PW:<pc>:<a>:<x>:<y>:<playidx>:<relwin>:<abswin>` event per EXECUTION
    of a watched PC (exact hex or `*XX` low-byte pattern; data reads rejected
    per C36), carrying A/X/Y, the play-invocation index (0 = during init) and
    RAM windows captured AT the hit. Serves "run init(A=sub), where does it
    land" (DMC `_observe_dispatch`, C31 compilation dispatch — py65 loop
    deleted) and is built to serve the C18 play-phase observers (exact PCs +
    X + playIdx). NB register values sample at the PC+2 read: pre-instruction
    for ≥3-byte sites (JMP / `LDA abs,X`), post for 2-byte ones.
  - `tools/divergence_triage.py ORIG REBUILD [--engine E]` — ENGINE-BLIND
    divergence classifier (prototype): localizes the first writelog divergence
    with a Trap-C-free PER-IRQ capture (robust to the CIA "diverge at position
    0" artifact that `find_first_divergence`'s naive per-frame compare hits),
    then runs writelog-SIGNATURE detectors suggesting the likely ledger class +
    evidence — collapsing the manual "which C-entry is this?" step. Blind
    detectors work on ANY family (length-tail→C24/C9/C25/C12, cross-chip→C28,
    wrong-value-freq→C6/C22, reorder/missing→C16, global-reg→C10); engine-
    specific probes plug in via the `ENGINE_DETECTORS` registry (blind core +
    one entry per family, the `divergence_census` pattern; `dmc` routes freq
    divergences to `dmc_offtable_probe`). The engine-agnostic diagnostic seam
    for the whole migration, not just DMC.
  - `tools/disasm_diff.py --orig SID --orig-range HEX-HEX --composer FILE --composer-label LABEL` — side-by-side orig disasm vs composer emitter (extracts the asm string from `_emit_*` functions). Use during step 3 of the recipe ("diff orig's effect code against the composer emitter line by line") to spot structural differences.
  - `tools/dmc_state_addr.py <member> [--idx N|--var NAME|--all] [--reg D40F]` — **the DMC answer to "DO NOT hand-craft state maps"** (the FC rule above, which had no DMC equivalent). Resolves any engine state variable to BOTH the orig address for THIS member (relocation-aware — the DMC player is usually NOT at $1000) and our composer's label address, and prints the paired `siddump --memwatch-on-write` commands for the ledger-C11 tracking measurement. `--idx N` answers "what does off-table window index N sonify?". REFUSES to name an address on a NON-CANON-geometry member (page-3 builds moved the state block) instead of returning a confident wrong one, and on a MULTI-PLAYER member (compilation / 2SID) reports every player's base + the subtune→player map and resolves each address ONCE PER PLAYER — a canon offset is a different address in each packed player. Built 2026-07-22 after probing canon `$1720` on a member based at `$9000` returned a coherent-looking lie (fxf=$FF, route=$00) that read as a genuine engine difference; extended 2026-07-23 after it reported `base $1000 / CANON` for a 2-player compilation whose divergent read was at `$2707`.
  - `tools/dmc_offtable_probe.py <member> [--subtune N]` — **the whole DMC off-table freq diagnosis in ONE command** (build → trichotomy verdict → localize the FAILING subtune → pc-trace the ORIGINAL over a ±3-frame window AROUND THE DIVERGENCE for the indexed freq-table load whose result is the diverging value with an off-table index ≥96 → classify the source addr STATIC/LIVE → for a COMPILATION, sample the SAME idx in EVERY packed player in its selecting file subtune, surfacing the C31 per-player window fact). Reports every proximate candidate (index, effective address, table byte). Cleanly bows out when the divergence is NOT a voice freq lo/hi (points you at `dmc_build_one --localize` + `effect_chain_profiler`), and when the value is found only FAR from the divergence it reports "NOT an off-table read at the divergence" with the far matches labeled as by-value coincidences — the PROXIMITY GATE (r116) that killed the tool's 6 historical mis-fires (whole-song by-value scans matching coincident loads: wavepos 3×, Real_Hardcore, Psycho_One). Built 2026-07-23 (round 91) after Rogue_Ninja's off-table idx-97 diagnosis took ~15 manual pc-trace/memwatch/writelog steps.
  - `tools/taint_source.py <sid> <LO-HI> [--all]` — GREY-BOX CLASSIFY an OFF-TABLE read: is its source RAM region STATIC (never written during play → REPRESENTABLE, capture the value/program) or DYNAMIC (written → hard residue)? Uses `--memtrace` (per-ACCESS, within-frame-complete — a per-frame `--memwatch` snapshot misses a write-then-restore inside one play()). Use when an off-table read is the first flat-stream divergence and you must decide fix-the-capture (static) vs accept-residue (dynamic). Landed the first family-4 FULL (Jupiter41). See ledger C2.
  - `siddump --writelog-per-irq` — emits the writelog stream bucketed PER PSID `play()` invocation (one `\|I` chunk per IRQ) instead of per siddump frame. Kills Trap C at the source — IRQ-bucketed streams align across mine/orig regardless of siddump's frame boundaries. Splits by play-entry cycle (origin-corrected: play entries are absolute PHI1 clocks, write-log cycles are relative to a per-frame base, so the splitter subtracts the base) and DROPS the init prefix (the writes before the first play-entry, frame-0 only — later-frame pre-entry writes are straddle tails and are kept). This is the capture behind `verify_all`'s CIA-tune verdict (see below). Add `--per-irq-debug` to print base / entry / write cycles to stderr for one frame. Implies `--writelog`.
  - `tools/effect_chain_profiler.py SID --subtune N --frames F1-F2 [--register HEX]` — attribute each SID write to its CPU PC by reading the store instruction's PC DIRECTLY off the pc-trace (every line carries PC + A/X/Y + the resolved effective `[d4xx]` address). Answers "which routine wrote this $D408 = $47?" in one command, grouped by play() invocation. **`--find-write REG=VAL`** (e.g. `--find-write D408=B7`, `--frames` optional → full-song scan) locates every write of a specific value BY VALUE — the fix for "find_first_divergence gave me a value but not the frame" (siddump frame ≠ play() index; never grep a guessed frame range again, 2026-07-23). NOTE: an earlier version reconstructed each write's cycle as `frame*19688+rel` and cycle-matched the pc-trace — that's the Trap-C pitfall (a siddump frame advances ~18,000 cyc, NOT 19688), so it drifted and mis-attributed writes to the PSID driver's idle spin loop ($04A5). Rewritten 2026-06-28 to avoid cycles entirely. Lesson: NEVER trust write→PC attribution that relies on reconstructing absolute cycles from siddump frames.
  - `tools/pattern_stream_verify.py --engine ENGINE` (or `--all`) — USF roundtrip check for the pattern-stream region. Verifies that orig and rebuild bytes match (accounting for `featuredriven_addr_shift` and the verbatim-pointer fixup). Catches data-emission regressions at extract/compose time.
  - `tools/usf_corpus_check.py` — **can the CURRENT grammar still read every stored `.usf`?** Parses all 11,943 in ~9 s, groups failures by cause + DMC family, exits 1 on any. **Run after ANY change to `src/usf/grammar.lark` / `parser.py` / `writer.py` / `types.py` — a schema change is not finished until it passes.**
  - `tools/usf_spec_lint.py` — **does the CURRENT writer honor the format
    spec's own invariants?** Four checks over a stratified corpus sample:
    round-trip object equality `parse(write(x)) == x` (the guarantee that
    makes writer changes .sid-byte-safe), the spec's canonical-fixpoint
    invariant, a DEFAULT-NOISE census (flags any key whose value is constant
    across ≥99% of occurrences = a suspected elidability violation — the
    check that would have caught `dur_field: $00` × 12k files; warnings +
    reviewed ALLOWLIST), and the §7 forbidden-shape field scan of
    `types.py` (errors). **Run alongside `usf_corpus_check` after any
    grammar/parser/writer/types change** (corpus_check = the stored corpus
    still parses; spec_lint = the current writer behaves). Born 2026-08-03
    after the init.voice_state default-emission sat unenforced for months —
    a declared principle without a mechanical check eventually drifts. Closes a blind spot `regression.py` structurally cannot see: regression builds from a ~116-member portfolio, so a typed-field move orphaned 1,182 stored `.usf` (9.9%) while it stayed fully green (2026-07-21). Breaks `verify_usf` + every downstream ML consumer. Cure = map failures to families FIRST, then per-family batch + mass-write (ledger C20, third layer).
  - `tools/batch_diff.py OLD.jsonl NEW.jsonl [--fail-on-regression]` — diff two
    family-batch results: surfaces **full→partial REGRESSIONS loudly** (plus
    gains / error transitions / membership changes). Closeouts report NET
    aggregate counts, which MASK regressions (+57 net hid −4 between the DMC
    Jul-22/Jul-26 batches — 4 members a mid-week fix broke sat unnoticed a week
    because the alphabetical work queue had already passed their letters). Run
    it against the PREVIOUS batch as part of EVERY family-batch closeout; a
    regression is a SIGNAL (an exposure set some fix's census missed), never
    fold it into the partial queue undifferentiated.
  - `tools/divergence_census.py --engine ENGINE --results BATCH.jsonl [--partials]` — RESIDUE TRIAGE for a wide family: census a batch-results jsonl by status+reason, then CLUSTER either the detect-rejects (live first-divergence site, default) or the verify PARTIALS (`--partials`, by first writelog `(reg,role)` divergence). Turns N opaque failures into ranked root-cause buckets with representatives. Automates "stratify by first-diff bucket". Wired: dmc_v5 (one `ENGINES` entry per family). See [`reference_divergence_census`](.claude/memory/reference_divergence_census.md). Key lesson it proved: **detection ≠ FULL** — the partials, not the detect-rejects, are the FULL bottleneck.
  - `tools/dmc_canon_diff.py [--members family1|FILE] [--status JSONL] [--csv]` — A-PRIORI WEDGE ENUMERATOR (canon-player families): linear-align every member's reachable player code to the canonical player binary (`pipelines/dmc/docs/dmc4_player_embedded_1000.bin`), diff OPCODES + in-player OPERAND-REPOINTS (packer operands point below $1000, so wedge repoints into $1000-$17FF separate cleanly), Δ-mode-filter bulk state/table relocations, cluster by canon site, tag handled-vs-NEW, and split each cluster into partial/full carriers (`--status BATCH.jsonl`). The PROACTIVE complement to the reactive `_*_probe` detectors — enumerates the whole code-patch wedge space in ONE pass + audits the probes' true carrier counts. Proved DMC family-1's wedges are essentially fully handled: of 188 partials, 78% carry NO code wedge (= off-table/CIA hard residue), 17% a handled wedge, only **9 (4%) a genuine unhandled patch — all singletons** (no multi-carrier lever). LIMIT: misses immediate-value tweaks (hr_preset/cymbal) + re-assembled members (linear-align only). See [`reference_dmc_canon_diff`](.claude/memory/reference_dmc_canon_diff.md).
- **py65 misses dispatch bugs** (CIA timer, PSID speed). Ear-test new engines and any dispatch changes in real sidplayfp before declaring done. Prefer `siddump --memwatch` for state inspection — it uses libsidplayfp = ground truth.
- **py65 is NOT ground truth for EXTRACTED VALUES that depend on divergent memory** (the third failure mode in [`feedback_ground_truth`](.claude/memory/feedback_ground_truth.md), DMC Roots 2026-07-24). Running a member's code under py65 to READ a value (loop target, off-table byte, post-init leftover) is only trustworthy when the byte was LOADED by the file image or provably WRITTEN by the code that just ran. A value read from UNINITIALIZED RAM, or from DEEP PLAYBACK of a C29-class player (null/stale pointers, off-image or `$00xx`/power-on-RAM reads), is emulator-dependent — py65's fill differs from libsidplayfp's and their whole playback state diverges (Roots: py65 read `$00` / played noise where libsidplayfp read `$87` / played silent). **VERIFY any py65-derived value that reaches the write stream against the same quantity from siddump (`--memwatch-on-write` / `--writelog`) before shipping it.** Tripwire: `_TaintMemory` (DMC extract) flags py65 reads of never-written memory.
- **Tooling reflex.** After each non-trivial debugging session (>30 min), ask: "what tool would have collapsed this to <5 min?" Add to [`tools/INVESTIGATION_BACKLOG.md`](tools/INVESTIGATION_BACKLOG.md) (or build immediately if <1 hour). If a tool starts producing misleading output or rotting, MODIFY or REMOVE it rather than working around it — bad tools cost more than no tool. Maintain context: when adding/modifying a diagnostic tool, update CLAUDE.md + the relevant memory so future sessions know it exists.
- **Commit early.** Each verified delta is one commit. No `Co-Authored-By`.
- **Propose options before code** for non-trivial work. Honest scope. Pause at decision points.
- **Schema additions are suspicious by default** — see [`feedback_schema_addition_discipline`](.claude/memory/feedback_schema_addition_discipline.md). Exhaust derivation / `engine_constants` / existing-params alternatives first. `bytes`-typed fields almost always mean you're papering over a representation gap.
- **The shared core stays parametric.** New engine quirks become config fields on `EngineConfig`, never `if engine == "Foo"` branches.

## Memory hygiene

The 2026-07-16 memory audit found the dominant rot mode is **status frozen at
write-time** (frontmatter descriptions, index one-liners, "Next steps"
sections written once while the work moved on). Rules that prevent it:

- **Timeless descriptions.** A memory's frontmatter `description:` says what
  the file IS, never where the work STANDS. Live status goes in exactly two
  places: the file's MEMORY.md index line and the head of its body.
- **Newest-first bodies for `project_<engine>` files.** Prepend rounds; the
  head IS the current status (the `project_dmc.md` convention — it was the
  only large file that survived the audit clean). Files with an older
  oldest-first body instead maintain a `## STATUS (head)` section at the top.
- **No forward-looking sections without a date.** "Next steps" / "What's
  left" / "RUNNING" blocks must carry their date; a later head entry
  supersedes them. When work they describe ships, mark them superseded —
  don't leave them contradicting the head.
- **Archive on resolve.** A memory that is fully RESOLVED with nothing open
  moves to `.claude/memory/_deprecated/` (note in its README) the same
  session it's declared resolved. If it still carries load-bearing engine
  knowledge (quirks, formulas, config semantics), it stays — resolved-but-
  load-bearing is a KEEP.
- **Lint before committing memory changes:** `python3 tools/memory_lint.py`
  (<1 s) — checks index↔file consistency, dead `[[links]]`, dead cited repo
  paths, and stale live-status markers. Errors block; warnings are prompts
  to verify.
- The **semantic** review (contradicts canon? wrong home? superseded?) is
  part of `/uready-review` — run it periodically; grep can't catch those.

## Build & test

```bash
source src/env.sh              # adds tools/siddump etc. to PATH
bash tools/build.sh            # builds libsidplayfp + siddump (one-time)

# Full pipeline regression — all migrated families
python3 tools/regression.py

# Rebuild one engine through the pipeline
python -c "
from pipelines.hubbard.commando.extract.to_usf import write_commando_usf
from pipelines.hubbard.commando.config import COMMANDO
from pipelines.build_from_usf import build_from_usf
write_commando_usf(COMMANDO, 'hvsc85/MUSICIANS/H/Hubbard_Rob')
build_from_usf('hvsc85/MUSICIANS/H/Hubbard_Rob/Commando.usf', 'hvsc85/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')
"

# Verify one engine's per-frame instruction sequence
python -c "
from pipelines.hubbard.verify import verify_all
from pipelines.hubbard.commando.config import COMMANDO
print(verify_all([(COMMANDO, 'hvsc85/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')]))
"

# Build + verify ONE DMC family-1 / 2SID member (build helper — the family
# batch only runs in bulk; wraps dmc_v4_config -> write_dmc_usf -> build_dmc_sid)
# Prints the BUILD PATH (single / compilation / multisid / hetero_masm) with
# each packed player's base + the subtune->player map — check it FIRST on any
# investigation, since a canon $17xx offset resolves once per player.
# --localize (implies --verify) auto-localizes the first divergence of EVERY
# FAILING subtune, inline from the verify capture (no second siddump run); a
# compilation's sub 0 is often FULL, so it targets the subtune that diverges.
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
| `tools/regression.py` | Full pipeline regression across all migrated families (Hubbard `verify_all`, companion/C64ME/Jay_Derrett `compare_instruction_stream`, FC canaries + portfolio, DMC portfolio, basic_program portfolio). Lists pre-existing partials so they're not mistaken for regressions. |
| `tools/siddump.cpp` | C++ register dumper (libsidplayfp). `--writelog` for cycle timing, `--pc-trace` for CPU PC trace. |

## HVSC index — `hvsc85.parquet` (+ `engine_docs.csv`), via DuckDB

A **static catalogue** of every SID in `hvsc85/` (path, PSID header, engine
classification, songlength, exclusion), stored as a compact **git-tracked
Parquet** file (`hvsc85.parquet`, zstd, ~3 MB) and queried via **DuckDB**.
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

**The `engine` column comes from `tools/sidid_full.txt`**, regenerated by the
vendored SIDId at `tools/sidid/` (cloned + patched + built by `tools/build.sh`):
`./tools/sidid/sidid hvsc85 -ctools/sidid/sidid.cfg` (~3 min). Two things that
bite, both handled by the generator and re-checkable in the file's header:
⚠ it scans EVERY `.sid`, so our own `.sidfinity.sid` rebuilds inside the tree
get classified too and must be filtered out; and ⚠ **upstream truncates paths
to 56 chars for display** — fatal for a dump consumed as a `{path: engine}` map
(it silently dropped 1,384 members, 2.3% of HVSC, which was 43% of everything
reading as "unclassified"). `tools/sidid_no_truncate.patch` removes it; a
re-clone without the patch reintroduces the loss. Also drop sidid's trailing
per-player summary — those lines parse as bogus paths.

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
`duckdb -c "SELECT … FROM read_parquet('hvsc85.parquet')"`.

**Coverage / FULL-list source of truth** = a fresh family batch, NOT stored
`.usf`/`.sid` files or the index. Batch results (`tmp/<engine>_*_results.jsonl`)
are stamped with a `code_hash` (`src/code_fingerprint.py`): on resume a row is
reused ONLY if its hash matches the current engine dependency set, so a code
change auto-re-verifies exactly the members it could have affected — no more
"remember to delete the jsonl", and no stale-verdict palimpsests. The
`*_mass_write.py` tools likewise skip (and warn about) any FULL row whose
code_hash is stale, so they never write an unverified build to disk.

**Reading a batch results jsonl — always via `src/batch_results.load_latest`.**
The file is APPEND-ONLY (a resume, or a `code_hash` invalidation, appends fresh
rows beside the old), so one member routinely has several rows with different
verdicts. Dedupe by path, LAST ROW WINS — the `code_hash` gate is NOT a
substitute (a plain resume adds no new hash, so duplicates can all carry the
current one). The module's docstring is the one home for the rule and the
incidents behind it. Safe without it: a resume gate that builds a `set()` of
done paths.

**A mass-write is a SYNC, not a write** (`src/corpus_sync.py`, shared by every
family's `*_mass_write.py`). "What is stored" must equal "what was verified",
which needs three things beyond the code_hash gate — each one a C20 layer that
has already bitten us:

- **Replay the recorded build path, never re-derive the dispatch.** When a
  batch dispatches over several build paths (multi-SID / compilation / single),
  a writer that re-derives can pick a different one and store a well-formed,
  code_hash-blessed, WRONG artifact no other gate can see (DMC stored every
  multi-SID member as a single-chip extraction of a multi-chip tune). It also
  *cannot* match a fallback fired by a verify-time exception. So the batch
  records `build_path` in its row and the writer replays it; a row missing it
  is refused, never guessed. A one-path family may pass
  `require_build_path=False` — until it grows a second path.
- **Remove orphans.** A member that is NOT full must have no stored artifact.
  Nothing else deletes one: mass-writes only ever revisit FULL members, and
  `usf_corpus_check` can't see it because the file parses fine (56 such files
  had accumulated in DMC f1).
- **Audit from disk.** After writing, re-verify a sample **from the stored
  artifacts**, stratified over the build paths — the only check that exercises
  writer and verifier against each other. `dmc_mass_write.py --audit N`
  (default 12) does this and exits 1 on failure.

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

Some SIDs / engine families may not fit the principled USF representation
without dragging engine-mechanism bookkeeping into the schema. **The list
is currently EMPTY** — its one historical entry class (Companion/Jay_Derrett,
excluded 2026 for being aperiodic-by-design) was later solved and migrated
(`pipelines/companion/jay_derrett/`, wired into regression). Treat exclusion
as a last resort that can be revisited; the mechanism stays in place:

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

**The repo hops between two hosts** — the 64-core EPYC (128 threads, 512 GB
RAM, dual 3090s) and the Lenovo X230 laptop (8 cores). **Current host (since
2026-07-24, for ~a month): the X230.** No per-host config exists or is
needed: **never hardcode a worker count** — every parallel site calls
`src.jobs.default_jobs()`, which reads the CPU count (affinity-aware) and is
capped by the work available, so pools auto-size to 8 here and 128 on the
EPYC. Override with `SIDFINITY_JOBS=N` for everything at once, or a per-tool
var (`REGRESSION_JOBS=1` forces sequential for debugging). NB wall-clock
guidance elsewhere (full DMC batch ~1 hr, regression ~10 min) was calibrated
on the EPYC — multiply by ~16 on the X230; lean even harder on stratified
subsets and incremental closeouts, and treat a full family batch as an
overnight background job.

**pytest** runs here, but only via the vendored lib — `PYTHONPATH=tools/py_test_lib`
(`env.sh` does NOT add it). `tools/regression.py` is still the gate; note
`pytest pipelines/` currently has 16 stale-expectation failures that predate
the move (they were unrunnable on the X230, so they rotted unnoticed).

**Treat `~/.local` as untrustworthy on this host** — `~/.local/share` was
wiped twice on 2026-07-21 (19:41, 21:31). Anything the pipeline needs lives
in the repo:

- **C64 ROMs**: `tools/c64roms/{kernal,basic,chargen}` (gitignored —
  copyrighted Commodore binaries). `env.sh` exports `SIDFINITY_ROMS_DIR`, and
  siddump resolves `--roms-dir` → `$SIDFINITY_ROMS_DIR` →
  `~/.local/share/sidplayfp`, so the repo copy is used and nothing outside
  the tree is load-bearing. Without ROMs siddump cannot execute RSID/BASIC
  tunes: the BASIC interpreter never runs and every `Basic_Program` member
  reports `unsupported:too_few_steps` — a silent wrong verdict, not a crash.
- **Python packages**: the in-repo `.pylocal/` (`lark`, `py65`, `numpy`,
  `soundfile`).

**The one remaining external prerequisite** is the **`duckdb` CLI** at
`~/.local/bin/duckdb` (v1.5.3) — all catalogue queries. It survived both
wipes (only `share/` was hit), but it is not in the repo: re-install it if
catalogue queries start failing.

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
`duckdb -c "SELECT … FROM read_parquet('hvsc85.parquet')"`.
(The snap `duckdb` at `/snap/bin/duckdb` is broken — `snap-confine` error — don't use it.)

## Project structure

```
pipelines/              engine families (~50 dirs) — active migration trees:
                        hubbard/, companion/, future_composer/, dmc/,
                        goattracker/, basic_program/; the rest are
                        research-doc stubs
src/                    USF shared source — usf/ (grammar + reader/writer),
                        composer_runtime/ (xa65 + PSID header, engine-blind),
                        hubbard_emu.py, songlengths.py, sid_db.py,
                        code_fingerprint.py, code_flow.py, exclusions.py,
                        env.sh. Everything pre-USF moved to deprecated/<topic>/.
docs/                   specifications and reference docs
tools/                  build tools (xa65, siddump, libsidplayfp)
hvsc85/                 HVSC #84 collection (not in git, gitignored)
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
  `research-player` skill. ~50 engine subdirs today, covering both
  migrated engines and pre-migration research stash.

Each `deprecated/<topic>/README.md` describes what's there and how to
revive it if needed.
