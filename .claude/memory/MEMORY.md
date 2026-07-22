## Project state


- [USF init.sid block](project_usf_init_sid_block.md) — CURRENT. USF carries SID-chip priming as typed `init.sid { master_vol, filter, voice N {...} }`; composer reads it directly; shape-detection deleted. Built on the init trichotomy (docs/the_trichotomy.md).
- [Composer dissolution](project_composer_dissolution.md) — Phase 8 done; `composer_hubbard.py` DELETED. Hubbard '85 family lives entirely in `pipelines/composer.py` (feature-driven asm, 18 chunk emitters + typed args). `tools/regression.py` = verdict.
- [FC principled composer](project_fc_principled_composer.md) — §9 closed: the FC build is orig-free at build time; both canaries (Cyb II 2/2 + Hawkeye 12/12) de-verbatim, PSID header synthesized. Verdict = `verify_featuredriven`. **2026-07-22: orig-free ≠ USF-complete — CLOSED.** 3 per-member player-build params (`std_vibrato_stale_tail` 32 carriers / `std_glide_hi_reg` 20 / `std_arp3_init` 1, measured vs the ORIGINAL) lived in the Python cfg, not the `.usf`; ledger C7 class A3. Now carried in `params`, corpus re-synced (FC batch 2530 full, 0 regressed / 0 gained).
- [FC fingerprint DB + standard player](project_fc_fingerprint_and_standard.md) — `tools/engine_fingerprint.py` reloc-invariant fingerprinting; 91% of HVSC FC is ONE vanilla "standard" player (distinct from the Tel composer). **✅ 2530/2672 FULL (94.7%), mass-written in stated-duration form (D6 piece 2).** Residue 140 partial. Per-round detail in topic file — READ IT first.

## Per-engine project memories

- [Basic_Program family](project_basic_program.md) — 486 RSID-BASIC tunes (engine IS the BASIC+KERNAL ROM); trace-lift → USF round-trip. **✅ 458/486 (94.2%) FULL** + 226 NF. Residue ~28 (float/random tail + digi). METHOD: census a bucket for a shared lever.
- [DMC migration](project_dmc.md) — THE FOCUS ENGINE (10,676 SIDs; largest family). V4 f1 **5238/5401 FULL + 163 partial + 0 error**, corpus synced (r85: 0 regressed / 1 gained, audit 18/18; the RELOCATING C31 wrapper — a packed player that exists only in RAM). r83: the COMPILATION path's three defects — dispatch OBSERVED not parsed, record 0 restored to merged slot 0, idle priming per-subtune; r83b: **the C19 wedge probes never reached multi-SID sub-players** (C9 5th occ — check WHICH LAYER params attach at) and a stored `.usf`/`.sid` pair could disagree (C20 5th layer, now an audit invariant); f2/V5 fam-3/5 in progress. Full 2SID/3SID (C27/C28) + compilation support incl. HETEROGENEOUS (DMC players + a distinct `dmc_sfx` SFX sub-player, ledger C31 — see [[project_dmc_compilations]]). Per-SID levers = first-f1-partial-by-path fixes: gated params, positive-minority census, 0-regr-by-construction, ledger-recorded. **72-round history + every lever + methodology live in project_dmc.md — READ IT FIRST** (do NOT expand this line; new rounds → topic file). Re-verify any stale wide batch (dmc_f*.jsonl) before picking.
- [DMC compilations](project_dmc_compilations.md) — a WHOLE residue class: one file packs N independent players + a per-subtune dispatch wrapper (subtune→(base,song)). Ledger C31; ≥15 in Bayliss. Unified-merge built; homogeneous + HETEROGENEOUS (DMC + a `dmc_sfx` sub-player, Canyon 13/13 FULL r72) both land.
- [Music_Assembler](project_music_assembler_target.md) — **MIGRATED, SID→USF→SID** (3rd-largest family, 6,351 SIDs). Wide batch **3,915 FULL (61.6%; 71.2% of members with a locatable player)** + 1,587 partial + 849 unsupported. 16-member portfolio + the Freespace_2075 DMC+MA canary wired as tier 1 in regression.py; `tools/masm_family_batch.py` is tier 2. Residue is half CHIP-GLOBAL: `$D416` filter 323, `$D418` master vol 181 (never written after init), plus 370 length_only. Corpus mass-write deliberately NOT done yet. Surfaced ledger **C34** (decoder position-dependence the write-stream verdict cannot see).
- [GoatTracker family](project_goattracker.md) — 2nd-largest (8,670: 7,311 V2 + 1,359 V1). **Active: V1** (original 1.x, NOT GT2). Extract + composer BUILT (`pipelines/goattracker/v1/`); wide batch **164/1359 FULL**, now re-run THROUGH the stored `.usf` (2026-07-22) with 0 status changes vs the in-memory baseline — V1's USF was previously unreadable (list params / `loop: -1` / its whole row-command vocabulary) and nothing noticed because the composer only ever saw the in-memory object. Now wired into regression.py (4 round-trip canaries). Per-round detail in topic file — READ IT first.
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
- [Fingerprint DB (deferred)](project_fingerprint_db.md) — future: SQLite-backed (writelog → USF params) DB to accelerate audits + supply ML training data.

## Working principles (read these before acting)

- [Knowledge placement](feedback_knowledge_placement.md) — 6 kinds → 6 homes (oracle=code, law=canon doc, technique=ledger, discipline=memory, status=project_<engine>, operation=CLAUDE.md); one home, point don't copy; nothing engines×members-shaped in shared containers; NEVER retroactively distill a ledger entry/canon doc.
- [Deprecate stale docs](feedback_deprecate_stale_docs.md) — USER PREFERENCE: a docs/ file that no longer holds live info gets DEPRECATED (git mv → deprecated/old_docs/ + dated banner + README line + repoint), not left in docs/ with an in-place banner. Test: every live fact already held elsewhere.
- [Re-anchor at decision points](feedback_reanchor_at_decisions.md) — TRIPWIRE. At EVERY representation/correctness decision, re-run CORE TENET + USF principle + uready as adversarial CHECKS that could overturn the easy choice. Tell of drift: citing a precedent to DEFEND an easy choice instead of describing the test I ran to BEAT it.
- [Convergence ledger](feedback_convergence_ledger.md) — TRIPWIRE. The ledger's recognition cards are imported at session start (full entries: docs/ledger/C<n>.md — READ before applying); before ANY non-trivial solution, actively CHECK for a matching entry (don't trust passive recall); RECORD every solution (1st sight); canonicalize on the 2nd. Weak link = checking BEFORE solving.
- [Three filters](feedback_three_filters.md) — every technique passes THREE: CORE TENET (permissive), USF PRINCIPLES (restrict the SCHEMA), MOVE-1 UNIFICATION-READINESS (restrict the COMPOSER — `shared_mechanism(per_engine_config)`, never ad-hoc).

### Ground truth & methodology
- [Ground truth is sidplayfp](feedback_ground_truth.md) — NEVER use py65/Python reimplementations as ground truth. Only `sidplayfp --writelog` is authoritative. The user's ear is final judge.
- [NO snapshot-per-frame verdict](feedback_no_snapshot_verdict.md) — verdict is ALWAYS the write-log, NEVER per-frame register snapshots (Trap A). It had false-passed 25 Hubbard subtunes. py65 capture is for extraction only.
- [Verification modes (full trap discussion)](feedback_verification_modes.md) — the worked Hawkeye examples for Traps A/B/C; the companion the Core Tenet doc points at. (Recovered 2026-07-14 from the orphaned pre-repo memory dir.)
- [Within-frame write ORDER is signal](feedback_sid_hidden_state_write_order.md) — multiset-equal frames are NOT a safe verdict; comparator stays cycle-ordered; per-voice write order is a per-engine parameter. (Recovered 2026-07-14.)
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
- [VOCABULARY: "uready"](feedback_uready_vocabulary.md) — unification-ready: the 6-criteria gate for leaving an engine family (orig-free §9, no escape hatches, factored USF, representative verification, feature accounting, documented residue). Per-family status lives in project_<engine>, not here.

### USF schema discipline
- [Principle-first analysis](feedback_principle_first_analysis.md) — CHECKLIST. Run the 6 questions BEFORE proposing any effect/instrument design or "engine-specific codegen". Don't wait to be caught.
- [Schema addition discipline](feedback_schema_addition_discipline.md) — CHECKLIST. Before adding any USF schema field: re-read the principle doc IN FULL, then exhaust derivation / engine_constants / existing-params. `bytes`-typed fields are suspicious by default.

### Engineering reflexes
- [Use 6502 mindset](feedback_6502_mindset.md) — all bugs are pointer errors; think in exact byte offsets
- [Writelog divergence recipe](feedback_writelog_divergence_recipe.md) — the full step-by-step protocol behind CLAUDE.md's "start with find_first_divergence" convention. (Recovered 2026-07-14.)
- [SMC disasm check](feedback_smc_disasm_check.md) — before trusting a static disasm, scan for STA into instruction operands; SMC makes the static reading lie. (Recovered 2026-07-14.)
- [Check existing engine docs](feedback_check_existing_engine_docs.md) — the three-source order (family docs → disassembly.s → RE_NOTES) behind CLAUDE.md's MANDATORY questions. (Recovered 2026-07-14.)
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
- [HVSC index DB](reference_hvsc_db.md) — `hvsc84.parquet` (+ `engine_docs.csv`): STATIC catalogue, DuckDB via `src/sid_db` (no build-status columns — palimpsest-prone). Coverage/FULL-list = a FRESH family batch, NOT the index/stored `.usf`; batch jsonls carry a `code_hash` so resume auto-invalidates stale verdicts. Regenerate via `tools/build_sid_db.py`.
- [Songlength overrides](reference_songlength_overrides.md) — `tools/songlength_overrides.json`. Durable corrections to HVSC's Songlengths.md5 for anomalous durations. Survives HVSC re-fetches.
- [USF format](reference_usf_format.md) — the on-disk .usf format + sidecar FLACs. Spec at `docs/usf_format.md`. Custom DSL, Lark grammar, `.usf` + N `.sample{N}.flac`.
- [Digi pipeline](reference_digi_pipeline.md) — USF digi support; extract → Sample/FLAC → pack → SID. Cycle-strict via `siddump --writelog`. First engine: Chimera 1-bit wavetoggle.
- [PC trace tool](reference_pc_trace_tool.md) — `tools/siddump --pc-trace FILE START END` dumps libsidplayfp CPU PC. Use when a SID misbehaves in sidplayfp but py65/writelog look fine.
- [Audit tool](reference_audit_tool.md) — `src/usf/audit.py`: PC-traced per-voice SID-write capture. Use for Rule 1 collapse audits when voice attribution matters.
- [Tokenization for ML](reference_tokenization.md) — USF is NOT tokens; tokenization is a downstream conversion when ML training starts. REMI-style is the proven start.
- [Hubbard PWM bounds](reference_hubbard_pwm_bounds.md) — pulsework's $08/$0E direction-flip thresholds are HARDCODED, not per-instrument
- [Divergence census tool](reference_divergence_census.md) — `tools/divergence_census.py`: clusters a family's non-FULL residue into ranked root-cause buckets. Found: detection ≠ FULL; partials are the bottleneck.
- [Canon-diff wedge enumerator](reference_dmc_canon_diff.md) — `tools/dmc_canon_diff.py`: a-priori wedge catalogue — diff every member's player code vs the canon binary, cluster+tag handled/NEW, split partial/full. PROVED DMC f1 wedges ~fully handled (188 partials: 78% no-wedge off-table residue, 17% handled-wedge, only 9=4% genuine unhandled, all singletons).

## Deprecated memories

Older project phases (Lean codegen, GT2 Grade-A counting, completed migration/refactor phases) live under [`_deprecated/`](_deprecated/) with a README. They no longer load — out of this index. `_deprecated/premigration_2026-06/` holds 30 memories recovered 2026-07-14 from the orphaned pre-repo memory dir (per-engine Hubbard-era + USF-design-era, frozen at their 2026-06 state).
