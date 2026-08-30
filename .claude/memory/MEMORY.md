## Project state


- [USF init.sid block](project_usf_init_sid_block.md) — USF carries SID-chip priming as typed `init.sid { master_vol, filter, voice N }`; composer reads it directly; shape-detection deleted. Built on the init trichotomy.
- [Composer dissolution](project_composer_dissolution.md) — Phase 8 done; Hubbard '85 lives entirely in `pipelines/composer.py` (feature-driven asm, 18 chunk emitters + typed args).
- [FC principled composer](project_fc_principled_composer.md) — §9 closed: the FC build is orig-free at build time; **orig-free ≠ USF-complete** also closed (ledger C7 class A3). Verdict = `verify_featuredriven`.
- [FC fingerprint DB + standard player](project_fc_fingerprint_and_standard.md) — reloc-invariant fingerprinting (`pipelines/future_composer/engine_fingerprint.py`); 91% of HVSC FC is ONE "standard" player. **✅ 2,604/2,748 FULL (94.8%)** ⚠STALE-VERDICTS Per-round detail in topic file — READ IT first.

## Per-engine project memories

⚠STALE-VERDICTS = the count predates a shared-code change and no batch has
re-run; `tools/migrate_verdict_rows.py` refuses to carry those rows. Re-batch
before quoting the number (measured 2026-08-22).

- [Basic_Program family](project_basic_program.md) — 524 RSID-BASIC tunes on #85 (engine IS the BASIC+KERNAL ROM); trace-lift → USF round-trip. **489/524 FULL (93.3%)** — verdicts CURRENT (full re-batch 2026-08-29, 0 regressions; the +1 is Cascading, the pw-sweep portfolio carrier, recovered at its honest 288s window — three stale caps, not a representation gap). Legion/Pepper: real divergences now, leads in backlog 14. Residue + round history: topic file.
- [DMC migration](project_dmc.md) — THE FOCUS ENGINE (10,758 SIDs on #85; largest family). **v4 f1 5,449/5,474 (99.5%) + f2 2,929/2,944 (99.5%)** — NOT closed; the old "100%" was a denominator artifact (50 claimed members had no verdict row → 37 partial + 3 error, and that IS the whole f1/f2 residue). Verdicts CURRENT (full re-batch 2026-08-28, 0 regressions). **v5 GRIND OPEN: 1,211/2,031 FULL (59.6%)**, 820 partial, **0 unsupported / 0 error** — both `data_tables_off_image` refusals resolved (a real C26 unpacker + a misidentified player that got its own site map). Verdicts CURRENT (same 2026-08-28 re-batch). DMC-wide: 9,589/10,449 claimed = 91.8%, or 89.0% of the 10,774 corpus (309 unrouted + 16 v6 still uncovered). Table-overflow bucket CLOSED (C8 6th widening paged cursor + the owner-approved C11 live-position form `pulse_position`/`filter_position`); backlog 19 deleted. 2SID/3SID + compilations incl. heterogeneous ([[project_dmc_compilations]]). **READ project_dmc.md FIRST** (newest-first); do NOT expand this line.
- [DMC compilations](project_dmc_compilations.md) — a residue CLASS: one file packs N players + a per-subtune dispatch wrapper. Ledger C31. Unified-merge built; homogeneous + HETEROGENEOUS both land.
- [Digi-Organizer](project_digi_organizer.md) — first parametric-digi family (`digi{}` schema, volume_4bit): **36/39 standalone FULL cycle-strict, 0 unsupported** (verdicts CURRENT 2026-08-30, 0 regressions); residue = 3 sub-frame cycle-phase partials, then the 92 music-paired members. READ IT first.
- [Music_Assembler](project_music_assembler_target.md) — **MIGRATED, SID→USF→SID** (3rd-largest, 6,489 SIDs on #85). **4,021 FULL (62.0%)** ⚠STALE-VERDICTS 16-member portfolio + the Freespace_2075 DMC+MA canary are tier 1; residue half CHIP-GLOBAL; mass-write deliberately NOT done. Surfaced ledger **C34**.
- [GoatTracker family](project_goattracker.md) — 2nd-largest (8,670). **Active: V1** (original 1.x, NOT GT2). Extract + composer built; wide batch **168/1387 FULL** ⚠STALE-VERDICTS re-run THROUGH the stored `.usf`; wired into regression.py. Detail in topic file — READ IT first.
- [Commando — no drum engine](project_commando_no_drum_engine.md) — "the drum" is inst 4 played off the end of the freq table; the drum sub-engine never runs in subtune 0
- [Chimera pipeline](project_chimera.md) — PSID rebuild (no KERNAL); music frame-exact + digi cycle-strict. Drove the digi pipeline + no-verbatim-engine-bytes refactor. Includes the C64 banking gotcha.
- [Human Race effect audit](project_human_race_audit.md) — ALL FIVE HR effects collapse to existing shared-core effects (downslide≡freq_slide, drumarp≡fx_arp, skydive≡fx_incby2, PWmode≡fx_pwm, per-note slide≡fx_drumslide)
- [Confuzion](project_confuzion.md) — stripped runtime (only vibrato + bidirectional PWM); frame counter via self-modifying `INC $085C`; song-end $D418 fade
- [5 Title Tunes (unified)](project_five_title_tunes.md) — UNIFIED single-engine driven by per-subtune params + ovseed + orderlist tables and globally-renumbered instruments
- [Companion engine (Up, up & Away!)](project_companion.md) — pipelines/companion/. First non-Hubbard-'85 engine; Hubbard's 1984 first SID.
- [Bowden-canonical (Vic Berry)](project_bowden_canonical.md) — pipelines/companion/bowden_canonical/. Flat-orderlist engine; surfaced a 6502 carry-leak quirk (PW loop runs 5 iterations because `ADC #4` inherits carry from upstream CPX).
- [Clever Music (Fairlight + Gyroscope)](project_clever_music.md) — pipelines/companion/clever_music/. Duration counters, embedded commands ($Bx tempo/$Cx vol/$Dx inst/$Ex jump), song-position sync counter $E0..$E5.
- [Henrys House](project_henrys_house.md) — pipelines/companion/henrys_house/. Single-voice variant, hardcoded tempo 8, $FF restart-init handler.
- [Yes Tune family](project_yes_tune.md) — pipelines/companion/yes_tune/. Per-voice state machine + 2-byte (note, duration) format. Multi-subtune + relocation-aware.
- [Adrenalin (HeatWave)](project_adrenalin.md) — SUB 0 DONE: 3rd FC canary, exact via PURE-TRICHOTOMY init. A COMPILATION (3 engines + 4 data pools); full Adrenalin needs multi-independent-song FC support.

## Engine quirks & open work

- [Hubbard nested counters](project_hubbard_nested_counters.md) — nested DEC/BPL speed counters
- [Hubbard notenum/freq overlap](project_hubbard_notenum_overlap.md) — notenum table lives INSIDE the freq table region; cross-voice coupling via shared bytes
- [Hubbard song-end fade](project_hubbard_song_end_fade.md) — RESOLVED (Confuzion 2×, TOAS 1.5×). Master-VOL fade = `clamp(BASE - voice_orderpos, 0..$0F)` via 6 EngineConfig knobs. Audit the fade via the write-log, not snapshots.
- [Fingerprint DB (deferred)](project_fingerprint_db.md) — future: SQLite-backed (writelog → USF params) DB to accelerate audits + supply ML training data.

## Working principles (read these before acting)

- [Knowledge placement](feedback_knowledge_placement.md) — 6 kinds → 6 homes (oracle=code, law=canon, technique=ledger, discipline=memory, status=project_<engine>, operation=CLAUDE.md); one home, point don't copy.
- [Deprecate stale docs](feedback_deprecate_stale_docs.md) — USER PREFERENCE: a stale docs/ file gets DEPRECATED (git mv → deprecated/old_docs/ + dated banner + README line + repoint), not banner-in-place.
- [Re-anchor at decision points](feedback_reanchor_at_decisions.md) — TRIPWIRE. At EVERY representation/correctness decision re-run CORE TENET + USF principle + uready as adversarial checks. Drift tell: citing a precedent to DEFEND an easy choice.
- [Convergence ledger](feedback_convergence_ledger.md) — TRIPWIRE. Cards import at session start (full entries `docs/ledger/C<n>.md` — READ before applying); CHECK before any non-trivial solution, RECORD on 1st sight, canonicalize on the 2nd. Weak link = checking BEFORE solving.
- [Three filters](feedback_three_filters.md) — every technique passes THREE: CORE TENET (permissive), USF PRINCIPLES (restrict the SCHEMA), MOVE-1 READINESS (restrict the COMPOSER).

### Ground truth & methodology
- [Ground truth is sidplayfp](feedback_ground_truth.md) — NEVER use py65/Python reimplementations as ground truth. Only `sidplayfp --writelog` is authoritative. The user's ear is final judge.
- [NO snapshot-per-frame verdict](feedback_no_snapshot_verdict.md) — verdict is ALWAYS the write-log, NEVER per-frame register snapshots (Trap A). It had false-passed 25 Hubbard subtunes. py65 capture is for extraction only.
- [Verification modes (full trap discussion)](feedback_verification_modes.md) — the worked Hawkeye examples for Traps A/B/C; the companion the Core Tenet doc points at. (Recovered 2026-07-14 from the orphaned pre-repo memory dir.)
- [Within-frame write ORDER is signal](feedback_sid_hidden_state_write_order.md) — multiset-equal frames are NOT a safe verdict; comparator stays cycle-ordered; per-voice write order is a per-engine parameter. (Recovered 2026-07-14.)
- [STRICT write-stream match, always](feedback_strict_writestream_always.md) — USER POLICY: never relax the verdict (no audio-equivalence). Reproduce inaudible writes instead.
- [subtune_frames not arbitrary](feedback_subtune_frames_not_arbitrary.md) — verify window = songlength × 1.1 (RATIFIED 2026-07-02), never arbitrary N, never 1.0x.
- [NO writelog replay](feedback_no_writelog_replay.md) — user STRONGLY rejected. Never propose. Defeats the USF/ML purpose.
- [py65 misses dispatch bugs](feedback_py65_misses_dispatch_bugs.md) — `verify_all` is silent about PSID speed / CIA timer / dispatch-rate bugs. Ear-test new engines / dispatch changes.
- [Header flags are audible](feedback_header_flags_audible.md) — NEW-COMPOSER CHECKLIST: derive PSID flags from usf.psid + diff rebuilt header vs orig at bring-up. The write-log verdict is blind to SID-model/clock flags.
- [Observation drift vs music drift](feedback_observation_drift.md) — siddump's per-VBI-frame bucketing is OBSERVATION; the chip sees a continuous stream. Use `compare_instruction_stream`; don't trust per-frame "FAIL".
- [Always through USF](feedback_always_through_usf.md) — pipeline MUST be SID → USF → SID
- [USF spec sync](feedback_usf_sync.md) — update spec, all converters, player, and tests whenever USF changes

### Working with the user
- [User nudge pattern](feedback_user_nudge_pattern.md) — question implausible explanations, brainstorm across math fields, extract don't reconstruct
- [User strategic pattern](feedback_user_strategic_pattern.md) — propose options before code; honest scope; pause after each step
- [Completeness over dominant-cause](feedback_completeness_over_dominant_cause.md) — user wants ALL DMC SIDs FULL, not ROI triage. Clustering batches fixes; work through EVERY failure mode incl. the long tail. Drop the "is it worth it" hedging.
- [Commit early](feedback_commit_early.md) — commit immediately after each verified improvement
- [Repo tmp/ not /tmp](feedback_repo_tmp_dir.md) — ALL scratch artifacts go in the gitignored repo-local `tmp/`, never system /tmp (it gets wiped)
- [Timestamped tool logging](feedback_timestamped_tool_logging.md) — OWNER DIRECTIVE: dev tools print timestamped flushed phase lines (`src.tslog`); silent long phases read as hangs. Wire into any tool you touch.
- [Background jobs via harness](feedback_background_jobs_harness.md) — long batches MUST use Bash `run_in_background: true`, never `nohup&`; never pipe a backgrounded command through `tail` (empty output reads as stalled). Sanity-check result mtime.
- [Old-vs-new code compare = worktree](feedback_old_code_compare_worktree.md) — compare current vs pre-change behavior in a git WORKTREE, never `git stash` in the main tree (a stash/pop across a timed-out command stranded edits at old code).
- [Relaxing an error kills its guards](feedback_relaxing_an_error_kills_its_guards.md) — before making code stop raising, grep for who CATCHES it: `except`-shaped guards go dead silently, no test fails. One took a FULL member down.
- [No self-matching waiters](feedback_no_self_matching_waiters.md) — TRIPWIRE. NEVER `while pgrep -f 'PATTERN'` (matches the waiter's OWN argv). Wait for `<task-notification>`; identify your procs before any kill.
- [No co-author in commits](feedback_no_coauthor.md) — never add `Co-Authored-By`
- [Do the actual work](feedback_do_the_work.md) — implement ALL optimizations, don't punt
- [Worktree agents must commit](feedback_worktree_commit.md) — always tell agents to `git add` + commit
- [Subagents: no git mutations](feedback_subagents_no_git.md) — fan-out/research agents forbidden from `git restore`/`checkout`; one reverted live DB state. Open shared DBs `mode=ro`.
- [research-player leaf agents](feedback_research_player_leaf_agents.md) — TRIPWIRE. Fan-out agents spawn their OWN sub-agents (a "6-agent" sweep became 30+). Every agent prompt MUST open with a LEAF constraint.
- [Meta-process](feedback_meta_process.md) — at natural pauses, re-evaluate highest-ROI approach + whether memories / CLAUDE.md reflect reality
- [VOCABULARY: "uready"](feedback_uready_vocabulary.md) — unification-ready: the 6-criteria gate for leaving an engine family. Per-family status lives in project_<engine>.

### USF schema discipline
- [Principle-first analysis](feedback_principle_first_analysis.md) — CHECKLIST. Run the 6 questions BEFORE proposing any effect/instrument design or "engine-specific codegen". Don't wait to be caught.
- [Schema addition discipline](feedback_schema_addition_discipline.md) — CHECKLIST + the OWNER-APPROVAL GATE: grammar/typed-field/new-representation changes NEVER land without owner approval (passing the tests is the argument to BRING, not a permission slip); C19-licensed params wedge knobs stay autonomous. Exhaust derivation first; check for a typed sibling before the params-bag shortcut.

### Engineering reflexes
- [Use 6502 mindset](feedback_6502_mindset.md) — all bugs are pointer errors; think in exact byte offsets
- [Writelog divergence recipe](feedback_writelog_divergence_recipe.md) — the full step-by-step protocol behind CLAUDE.md's "start with find_first_divergence" convention. (Recovered 2026-07-14.)
- [Measure mechanism before precedent](feedback_measure_mechanism_before_precedent.md) — diagnostic ordering: pc-trace the ACTUAL read before matching it to a prior round's index; read the WHOLE multi-stage pipeline before instrumenting one stage. Round-91 retrospective; spawned `pipelines/dmc/offtable_probe.py`, `--find-write`, `dmc_build_one --localize` auto-target.
- [Residue claim is a measurement](feedback_residue_claim_is_measured.md) — a "hard boundary / can't-reproduce" verdict must be MEASURED (siddump, never py65 for divergent memory), never inferred. DMC Verdict_01 mis-claimed it 3× → each fell to one measurement → FULL.
- [SMC disasm check](feedback_smc_disasm_check.md) — before trusting a static disasm, scan for STA into instruction operands; SMC makes the static reading lie. (Recovered 2026-07-14.)
- [Check existing engine docs](feedback_check_existing_engine_docs.md) — the three-source order (family docs → disassembly.s → RE_NOTES) behind CLAUDE.md's MANDATORY questions. (Recovered 2026-07-14.)
- [C64 banking when relocating](feedback_c64_banking_relocation.md) — relocating code into $A000-$BFFF? Audit every `sta $01` inside it. A banking flip takes effect on the next fetch; if that fetch is in the banked range it reads ROM.
- [Bug investigation methodology](feedback_bug_investigation.md) — pick one bad subtune, trace the first wrong frame, fix root cause
- [Residue-triage order](feedback_residue_triage_order.md) — wide-family residue: census FIRST, then attack in DEPENDENCY order (measure→fix-verdict→unblock-builds→fix-effects→accept-last), never biggest-bucket-first.
- [Full decompile before Hubbard work](feedback_full_decompile_hubbard.md) — disassemble init+play first for every new Hubbard SID
- [Trust binary not disassembly](feedback_disassembly_data_section.md) — `!by` directives can be wrong about initial data; read the actual bytes
- [Deconstruct, don't reproduce the trick](feedback_deconstruct_not_reproduce.md) — reproduce the exact instruction stream with clean code; the trick to avoid is the space-saving MECHANISM, not the output. Investigate odd behaviour before discarding.
- [Migration as stress test](feedback_migration_as_stress_test.md) — migrating a new engine surfaces hardcoded assumptions in the shared core. Fix parametrically, not by matching the hardcode.
- [Audit discriminator](feedback_audit_discriminator.md) — for per-instrument audits, use fx_flags cache or v_instr,x — NEVER ADSR alone. Multiple insts share AD/SR.
- [Dataflow over heuristics](feedback_dataflow_over_heuristics.md) — for engine-data extraction, default to dataflow tracing (find STA $D4xx, walk A's predecessors to source). Content heuristics only when semantics aren't recoverable.

## References

- [siddump frame cycles](reference_siddump_frame_cycles.md) — TRIPWIRE: a siddump "frame" ≈ ~18,000 CPU cycles, NOT the 19,656-cycle PAL play period (ρ≈0.919). Bites absolute-cycle math; not the flat Mode-1 verdict. Mis-derived twice.
- [HVSC index DB](reference_hvsc_db.md) — `hvsc85.parquet` + `engine_docs.csv`: STATIC catalogue via `src/sid_db`. Coverage = a FRESH family batch, never the index. Regenerate with `tools/build_sid_db.py`.
- [Songlength overrides](reference_songlength_overrides.md) — `tools/songlength_overrides.json`. Durable corrections to HVSC's Songlengths.md5 for anomalous durations. Survives HVSC re-fetches.
- [USF format](reference_usf_format.md) — the on-disk .usf format + sidecar FLACs. Spec at `docs/usf_format.md`. Custom DSL, Lark grammar, `.usf` + N `.sample{N}.flac`.
- [Digi pipeline](reference_digi_pipeline.md) — USF digi support; extract → Sample/FLAC → pack → SID. Cycle-strict via `siddump --writelog`. First engine: Chimera 1-bit wavetoggle.
- [PC trace tool](reference_pc_trace_tool.md) — `tools/siddump --pc-trace FILE START END` dumps libsidplayfp CPU PC. Use when a SID misbehaves in sidplayfp but py65/writelog look fine.
- [Audit tool](reference_audit_tool.md) — `src/usf/audit.py`: PC-traced per-voice SID-write capture. Use for Rule 1 collapse audits when voice attribution matters.
- [Tokenization for ML](reference_tokenization.md) — USF is NOT tokens; tokenization is a downstream conversion when ML training starts. REMI-style is the proven start.
- [Hubbard PWM bounds](reference_hubbard_pwm_bounds.md) — pulsework's $08/$0E direction-flip thresholds are HARDCODED, not per-instrument
- [Divergence census tool](reference_divergence_census.md) — `tools/divergence_census.py`: clusters non-FULL residue into ranked root-cause buckets. Found: detection ≠ FULL.
- [Canon-diff wedge enumerator](reference_dmc_canon_diff.md) — `pipelines/dmc/canon_diff.py`: diff every member vs the canon player, cluster + tag handled/NEW. PROVED DMC f1 wedges ~fully handled.
- [Post-project research ideas](reference_post_project_research.md) — pointer to `docs/post_project_research_ideas.md`: what the finished corpus enables beyond ML. A parking lot, not work.

## Deprecated memories

Older project phases live under [`_deprecated/`](_deprecated/) with a README; they no longer load. Includes `premigration_2026-06/` (30 memories recovered 2026-07-14, frozen at their 2026-06 state).
