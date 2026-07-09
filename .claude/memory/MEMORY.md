## Project state

- [Current host is 8-core](project_current_host_8core.md) — since 2026-06-11: 8 cores (NOT the 64-core EPYC in CLAUDE.md), no pytest. Pool(8); regression as the gate.

- [USF init.sid block](project_usf_init_sid_block.md) — CURRENT. USF carries SID-chip priming as typed `init.sid { master_vol, filter, voice N {...} }`; composer reads it directly; shape-detection deleted. Built on [[init-trichotomy]].
- [Composer dissolution](project_composer_dissolution.md) — Phase 8 done; `composer_hubbard.py` DELETED. Hubbard '85 family lives entirely in `pipelines/composer.py` (feature-driven asm, 18 chunk emitters + typed args). `tools/regression.py` = verdict.
- [Hubbard remaining partials](project_hubbard_remaining_partials.md) — RESOLVED: entire Hubbard family exact (71/71). Fixes: CIA-aware per-play verdict (--writelog-per-irq); Devils_Galop master_vol_every_note knob.
- [FC principled composer](project_fc_principled_composer.md) — IN PROGRESS. De-verbatim the FC data tail. Schema foundation DONE (`Orderlist.transposes`). Next: extract un-bake + composer emit. Verdict = `verify_featuredriven`.
- [FC fingerprint DB + standard player](project_fc_fingerprint_and_standard.md) — `tools/engine_fingerprint.py` reloc-invariant fingerprinting; 91% of HVSC FC is ONE vanilla "standard" player (distinct from the Tel composer). **✅ WIDE BATCH 2419/2672 FULL (90.5%), mass-written.** Full effect chain gated; residue 253. Per-round detail in topic file — READ IT first.
- [Off-table unified transform](project_offtable_unified.md) — recurring "engine reads past the freq/wave/pulse table" across ALL engines; census → `docs/offtable_unified_transform.md`. Observe-don't-reimplement; REALIZE→CLASSIFY→FIT; revive `strip_decompose`.

## Per-engine project memories

- [Basic_Program family](project_basic_program.md) — 486 RSID-BASIC tunes (engine IS the BASIC+KERNAL ROM); trace-lift → USF round-trip. **✅ 458/486 (94.2%) FULL** + 226 NF. Residue ~28 (float/random tail + digi). METHOD: census a bucket for a shared lever.
- [DMC migration](project_dmc.md) — THE FOCUS ENGINE (10,676 SIDs; largest family). V4 family-1 **≈5163/5401 FULL, ≈238 partial, 0 unsupported/error (per-round; wide batch STALE)**; family-2 2507/2889; V5 fam-3/5 1098/1495; fam-4 in progress. Full 2SID/3SID support (each chip = an independent single-chip player; merged log chip-TAGGED reg=chip*$20+reg; verdict compares each chip's stream independently — ledger C27/C28). Per-SID levers land as first-f1-partial-by-path fixes: extract-time derivation knobs or gated composer params, positive-minority census, 0-regr-by-construction, ledger-recorded; latest r65 Groove = $D418 re-asserted every frame via a filter-tail wrapper (`d418_filter_tail`, C19 10th/C10). **Per-round history (rounds 1–65) + every lever + methodology lessons live in project_dmc.md — READ IT FIRST.**
- [GoatTracker family](project_goattracker.md) — 2nd-largest (8,670: 7,311 V2 + 1,359 V1). **Active: V1** (original 1.x, NOT GT2). Research DONE 2026-06-29; no extract code yet. One dominant player → FC-standard-shaped migration. Next: fingerprint→canary→disassembly.s.
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
- [Adrenalin (HeatWave)](project_adrenalin.md) — SUB 0 DONE: 3rd FC canary, exact via PURE-TRICHOTOMY init (`init_style='universal_reset'` + `compare_instruction_stream(mode='trichotomy')`). A COMPILATION (3 engines + 4 independent data pools); full Adrenalin needs multi-independent-song FC support.

## Engine quirks & open work

- [Hubbard nested counters](project_hubbard_nested_counters.md) — nested DEC/BPL speed counters
- [Hubbard notenum/freq overlap](project_hubbard_notenum_overlap.md) — notenum table lives INSIDE the freq table region; cross-voice coupling via shared bytes
- [Hubbard song-end fade](project_hubbard_song_end_fade.md) — RESOLVED (Confuzion 2×, TOAS 1.5×). Master-VOL fade = `clamp(BASE - voice_orderpos, 0..$0F)` via 6 EngineConfig knobs. Audit the fade via the write-log, not snapshots.
- [Hubbard PWM bounds](reference_hubbard_pwm_bounds.md) — pulsework's $08/$0E direction-flip thresholds are HARDCODED, not per-instrument
- [Timing requirements](project_timing_requirements.md) — frame-accurate OK for tracker music; cycle-precise needed later for digi/demo SIDs
- [Fingerprint DB (deferred)](project_fingerprint_db.md) — future: SQLite-backed (writelog → USF params) DB to accelerate audits + supply ML training data.

## Working principles (read these before acting)

- [Re-anchor at decision points](feedback_reanchor_at_decisions.md) — TRIPWIRE. At EVERY representation/correctness decision, re-run CORE TENET + USF principle + uready as adversarial CHECKS that could overturn the easy choice. Tell of drift: citing a precedent to DEFEND an easy choice instead of describing the test I ran to BEAT it.
- [Convergence ledger](feedback_convergence_ledger.md) — TRIPWIRE. Before ANY non-trivial solution, CONSULT `docs/convergence_ledger.md` for the canonical form; RECORD every solution (1st sight); canonicalize on the 2nd. Weak link = consulting BEFORE solving.
- [Three filters](feedback_three_filters.md) — every technique passes THREE: CORE TENET (permissive), USF PRINCIPLES (restrict the SCHEMA), MOVE-1 UNIFICATION-READINESS (restrict the COMPOSER — `shared_mechanism(per_engine_config)`, never ad-hoc).

### Ground truth & methodology
- [Ground truth is sidplayfp](feedback_ground_truth.md) — NEVER use py65/Python reimplementations as ground truth. Only `sidplayfp --writelog` is authoritative. The user's ear is final judge.
- [NO snapshot-per-frame verdict](feedback_no_snapshot_verdict.md) — verdict is ALWAYS the write-log, NEVER per-frame register snapshots (Trap A). It had false-passed 25 Hubbard subtunes. py65 capture is for extraction only.
- [STRICT write-stream match, always](feedback_strict_writestream_always.md) — USER POLICY: never relax the verdict (no audio-equivalence). Reproduce inaudible writes instead.
- [subtune_frames not arbitrary](feedback_subtune_frames_not_arbitrary.md) — verify window = songlength × 1.1 (RATIFIED 2026-07-02), never arbitrary N, never 1.0x.
- [NO writelog replay](feedback_no_writelog_replay.md) — user STRONGLY rejected. Never propose. Defeats the USF/ML purpose.
- [py65 misses dispatch bugs](feedback_py65_misses_dispatch_bugs.md) — `verify_all` is silent about PSID speed / CIA timer / dispatch-rate bugs. Ear-test new engines / dispatch changes.
- [Header flags are audible](feedback_header_flags_audible.md) — NEW-COMPOSER CHECKLIST: derive PSID flags from usf.psid + diff rebuilt header vs orig at bring-up. The write-log verdict is blind to SID-model/clock flags; the hardcode recurred in 3 composers before an ear-test caught it (Taurus_02).
- [Observation drift vs music drift](feedback_observation_drift.md) — siddump's per-VBI-frame bucketing is OBSERVATION; the chip sees a continuous stream. Use `compare_instruction_stream`; don't trust per-frame "FAIL".
- [Always through USF](feedback_always_through_usf.md) — pipeline MUST be SID → USF → SID
- [USF spec sync](feedback_usf_sync.md) — update spec, all converters, player, and tests whenever USF changes

### Working with the user
- [User nudge pattern](feedback_user_nudge_pattern.md) — question implausible explanations, brainstorm across math fields, extract don't reconstruct
- [User strategic pattern](feedback_user_strategic_pattern.md) — propose options before code; honest scope; pause after each step
- [Completeness over dominant-cause](feedback_completeness_over_dominant_cause.md) — user wants ALL DMC SIDs FULL, not ROI triage. Clustering batches fixes; work through EVERY failure mode incl. the long tail. Drop the "is it worth it" hedging.
- [Commit early](feedback_commit_early.md) — commit immediately after each verified improvement
- [Repo tmp/ not /tmp](feedback_repo_tmp_dir.md) — ALL scratch artifacts go in the gitignored repo-local `tmp/`, never system /tmp (it gets wiped)
- [Background jobs via harness](feedback_background_jobs_harness.md) — long batches MUST use Bash `run_in_background: true`, never `nohup&` foreground. Family batches RESUME from the OUT jsonl (now code_hash-gated — [[reference_hvsc_db]]). Sanity-check result mtime vs the fix's mtime.
- [No self-matching waiters](feedback_no_self_matching_waiters.md) — TRIPWIRE. NEVER `while pgrep -f 'PATTERN'; do sleep N; done` (pattern matches the waiter's OWN argv → infinite loop). Wait for `<task-notification>`; identify your procs vs a parallel session's before any kill.
- [No co-author in commits](feedback_no_coauthor.md) — never add `Co-Authored-By`
- [Do the actual work](feedback_do_the_work.md) — implement ALL optimizations, don't punt
- [Worktree agents must commit](feedback_worktree_commit.md) — always tell agents to `git add` + commit
- [Subagents: no git mutations](feedback_subagents_no_git.md) — fan-out/research agents forbidden from `git restore`/`checkout`; one reverted live DB state. Open shared DBs `mode=ro`.
- [research-player leaf agents](feedback_research_player_leaf_agents.md) — TRIPWIRE. Fan-out agents recursively spawn their OWN sub-agents (a "6-agent" sweep became 30+). Every agent prompt MUST open with a LEAF constraint. Report the TRUE live agent count.
- [Meta-process](feedback_meta_process.md) — at natural pauses, re-evaluate highest-ROI approach + whether memories / CLAUDE.md reflect reality
- [VOCABULARY: "uready"](feedback_uready_vocabulary.md) — unification-ready: the 6-criteria gate for leaving an engine family (orig-free §9, no escape hatches, factored USF, representative verification, feature accounting, documented residue). Scoreboard in the memory.

### USF schema discipline
- [USF representation principle](feedback_usf_representation_principle.md) — TRIPWIRE: before designing/changing any USF effect/instrument representation, read `docs/usf_representation_principle.md` IN FULL. Effects are parametric over a musical basis; the engine holds mechanism, never an indexed library.
- [Init trichotomy](feedback_init_trichotomy.md) — TRIPWIRE: before handling init for a new engine, read `docs/sid_init_report.md` IN FULL. Init = reset (universal) + priming (typed USF init.sid) + environment + engine bookkeeping. NO shape detection, NO engine-name dispatch.
- [Principle-first analysis](feedback_principle_first_analysis.md) — CHECKLIST. Run the 6 questions BEFORE proposing any effect/instrument design or "engine-specific codegen". Don't wait to be caught.
- [Schema addition discipline](feedback_schema_addition_discipline.md) — CHECKLIST. Before adding any USF schema field: re-read the principle doc IN FULL, then exhaust derivation / engine_constants / existing-params. `bytes`-typed fields are suspicious by default.

### Engineering reflexes
- [Use 6502 mindset](feedback_6502_mindset.md) — all bugs are pointer errors; think in exact byte offsets
- [C64 banking when relocating](feedback_c64_banking_relocation.md) — relocating code into $A000-$BFFF? Audit every `sta $01` inside it. A banking flip takes effect on the next fetch; if that fetch is in the banked range it reads ROM.
- [Bug investigation methodology](feedback_bug_investigation.md) — pick one bad subtune, trace the first wrong frame, fix root cause
- [Residue-triage order](feedback_residue_triage_order.md) — large wide-family residue: census FIRST, then attack in DEPENDENCY order (measure→fix-verdict→unblock-builds→fix-effects→accept-limit-last), never biggest-bucket-first. A verdict fix can flip ~150 false-partials at zero composer cost.
- [Full decompile before Hubbard work](feedback_full_decompile_hubbard.md) — disassemble init+play first for every new Hubbard SID
- [Trust binary not disassembly](feedback_disassembly_data_section.md) — `!by` directives can be wrong about initial data; read the actual bytes
- [Deconstruct, don't reproduce the trick](feedback_deconstruct_not_reproduce.md) — reproduce the exact instruction stream with clean code; the trick to avoid is the space-saving MECHANISM, not the output. Investigate odd behaviour before discarding.
- [Migration as stress test](feedback_migration_as_stress_test.md) — migrating a new engine surfaces hardcoded assumptions in the shared core. Fix parametrically, not by matching the hardcode.
- [Audit discriminator](feedback_audit_discriminator.md) — for per-instrument audits, use fx_flags cache or v_instr,x — NEVER ADSR alone. Multiple insts share AD/SR.
- [Dataflow over heuristics](feedback_dataflow_over_heuristics.md) — for engine-data extraction, default to dataflow tracing (find STA $D4xx, walk A's predecessors to source). Content heuristics only when semantics aren't recoverable.

## References

- [siddump frame cycles](reference_siddump_frame_cycles.md) — TRIPWIRE: a siddump "frame" ≈ ~18,000 CPU cycles (`cyclesPerFrame=19688` EVENT-SCHEDULER ticks, each <1 CPU cyc), NOT the 19,656-cycle PAL play period. ρ≈0.919. Bites absolute-cycle math (frame×19688 overestimates ×1.088); not the flat Mode-1 verdict. Mis-derived twice.
- [HVSC index DB](reference_hvsc_db.md) — `hvsc84.parquet` (+ `engine_docs.csv`): **STATIC catalogue**, DuckDB-queried via `src/sid_db`. **2026-07-04: dropped ALL build-status columns + `record_*` write-through (palimpsest-prone) and CSV→Parquet.** Coverage/FULL-list = a FRESH family batch, NOT the index or stored `.usf`; batch jsonls carry a `code_hash` (`src/code_fingerprint.py`) so resume auto-invalidates stale-code verdicts. Regenerate via `tools/build_sid_db.py`.
- [Songlength overrides](reference_songlength_overrides.md) — `tools/songlength_overrides.json`. Durable corrections to HVSC's Songlengths.md5 for anomalous durations. Survives HVSC re-fetches.
- [USF format](reference_usf_format.md) — the on-disk .usf format + sidecar FLACs. Spec at `docs/usf_format.md`. Custom DSL, Lark grammar, `.usf` + N `.sample{N}.flac`.
- [Digi pipeline](reference_digi_pipeline.md) — USF digi support; extract → Sample/FLAC → pack → SID. Cycle-strict via `siddump --writelog`. First engine: Chimera 1-bit wavetoggle.
- [PC trace tool](reference_pc_trace_tool.md) — `tools/siddump --pc-trace FILE START END` dumps libsidplayfp CPU PC. Use when a SID misbehaves in sidplayfp but py65/writelog look fine.
- [Audit tool](reference_audit_tool.md) — `src/usf/audit.py`: PC-traced per-voice SID-write capture. Use for Rule 1 collapse audits when voice attribution matters.
- [Tokenization for ML](reference_tokenization.md) — USF is NOT tokens; tokenization is a downstream conversion when ML training starts. REMI-style is the proven start.
- [Hubbard PWM bounds](reference_hubbard_pwm_bounds.md) — pulsework's $08/$0E direction-flip thresholds are HARDCODED, not per-instrument
- [Divergence census tool](reference_divergence_census.md) — `tools/divergence_census.py`: clusters a family's non-FULL residue into ranked root-cause buckets. Found: detection ≠ FULL; partials are the bottleneck.

## Deprecated memories

Older project phases (Lean codegen, GT2 Grade-A counting, completed migration/refactor phases) live under [`_deprecated/`](_deprecated/) with a README. They no longer load — out of this index.
