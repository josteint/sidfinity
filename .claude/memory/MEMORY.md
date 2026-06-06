## Project state

- [USF init.sid block](project_usf_init_sid_block.md) — CURRENT. USF carries SID-chip priming as typed `init.sid { master_vol, filter, voice N { envelope_prime, pw_init } }` block; composer reads it directly; shape-detection deleted. Bowden migrated as the proof case. Built on [[init-trichotomy]] principle.
- [Composer dissolution](project_composer_dissolution.md) — Phase 8 of the composer rewrite is done; `composer_hubbard.py` DELETED. The Hubbard '85 family lives entirely in `pipelines/composer.py` as feature-driven asm composition (18 chunk emitters + typed args, no template substitution). Run `tools/regression.py` for the current verdict.
- [FC principled composer](project_fc_principled_composer.md) — IN PROGRESS. De-verbatim the FC data tail (patterns/sequences/aux). Schema foundation DONE (commit 4f040eb: `Orderlist.transposes`). Transpose stays a sequence command (64-pattern limit); voiceinc bakes into wave_adjust. Next: extract un-bake + composer emit. Verdict = `verify_featuredriven`.

## Per-engine project memories

- [Commando — no drum engine](project_commando_no_drum_engine.md) — "the drum" is inst 4 played off the end of the freq table; the drum sub-engine never runs in subtune 0
- [Chimera pipeline](project_chimera.md) — PSID rebuild (no KERNAL); music frame-exact + digi cycle-strict. Drove the digi pipeline + USF v2 + the no-verbatim-engine-bytes refactor. Includes the C64 banking gotcha that surfaced during the $B093 player_base shrink.
- [Devils Galop pipeline](project_devils_galop.md)
- [Monty on the Run](project_monty.md) — off-table SFX sweep via `sfx_state_ofs=251`
- [Action Biker](project_action_biker.md) — sps_fill extended to LDX #23 for the $D415-$D418 cleanup
- [Human Race](project_human_race.md) — required skydive params, drumarp period, PWmode linear_pw_or, N_MUSIC parameterization, off-table arp layout
- [Human Race effect audit](project_human_race_audit.md) — ALL FIVE HR effects collapse to existing shared-core effects (downslide ≡ freq_slide, drumarp ≡ fx_arp, skydive ≡ fx_incby2, PWmode ≡ fx_pwm, per-note slide ≡ fx_drumslide)
- [Hunter Patrol](project_hunter_patrol.md) — added frame_ctr_init, incby2_late_gate, seed_offsets
- [Thing on a Spring](project_thing_on_a_spring.md) — master_VOL formula `clamp($47 − V3_orderpos, $0F)` with `master_vol_trigger='every_note'`; SFX uses Commando-shape sfx_play
- [One Man and his Droid](project_one_man_and_his_droid.md) — new knob `arp_phase_invert`; songs = `len(subtunes) + len(sfx_list)`
- [Battle of Britain](project_battle_of_britain.md) — surfaced the tie-preserves-slide bug in the shared note codec
- [Confuzion](project_confuzion.md) — stripped runtime (only vibrato + bidirectional PWM); frame counter advanced via self-modifying `INC $085C`; uses the song-end $D418 fade
- [5 Title Tunes (unified)](project_five_title_tunes.md) — UNIFIED single-engine driven by per-subtune params + ovseed + orderlist tables and globally-renumbered instruments
- [Companion engine (Up, up & Away!)](project_companion.md) — pipelines/companion/. First non-Hubbard-'85 engine; Hubbard's 1984 first SID.
- [Bowden-canonical (Vic Berry)](project_bowden_canonical.md) — pipelines/companion/bowden_canonical/. Flat-orderlist engine; surfaced a 6502 carry-leak quirk (PW loop runs 5 iterations, not 4, because `ADC #4` inherits carry from upstream CPX).
- [Clever Music (Fairlight + Gyroscope)](project_clever_music.md) — pipelines/companion/clever_music/. Duration counters, embedded commands ($Bx tempo / $Cx vol / $Dx instrument / $Ex pattern jump), song-position synchronisation counter cycling $E0..$E5.
- [Henrys House](project_henrys_house.md) — pipelines/companion/henrys_house/. Single-voice variant, hardcoded tempo 8, $FF restart-init handler.
- [Yes Tune family](project_yes_tune.md) — pipelines/companion/yes_tune/. Per-voice state machine + 2-byte (note, duration) format. Multi-subtune + relocation-aware.

## Engine quirks & open work

- [Hubbard nested counters](project_hubbard_nested_counters.md) — nested DEC/BPL speed counters
- [Hubbard notenum/freq overlap](project_hubbard_notenum_overlap.md) — notenum table lives INSIDE the freq table region; cross-voice coupling via shared bytes
- [Hubbard song-end fade](project_hubbard_song_end_fade.md) — RESOLVED for Confuzion (full 2× match) + TOAS (1.5× match). Master-VOL fade is `clamp(BASE - voice_orderpos, 0..$0F)` driven by 6 EngineConfig knobs (`master_vol_subtrahend_voice` + `_base` + `_trigger` + `_reset_on_loop` + `_underflow_clamp` + `loop_silences_song`). `tools/audit_d418_fade.py` is the probe for new engines.
- [Hubbard PWM bounds](reference_hubbard_pwm_bounds.md) — pulsework's $08/$0E direction-flip thresholds are HARDCODED, not per-instrument
- [Timing requirements](project_timing_requirements.md) — frame-accurate OK for tracker music; cycle-precise needed later for digi/demo SIDs
- [Fingerprint DB (deferred)](project_fingerprint_db.md) — future: SQLite-backed (writelog → USF parameters) database to accelerate future audits + supply ML training data.

## Working principles (read these before acting)

### Ground truth & methodology
- [Ground truth is sidplayfp](feedback_ground_truth.md) — NEVER use py65 or Python reimplementations as ground truth. Only `sidplayfp --writelog` is authoritative. The user's ear is the final judge.
- [subtune_frames not arbitrary](feedback_subtune_frames_not_arbitrary.md) — verify frame count = songlength × 1.1 × 50 Hz, never `n=500` / `n=1000`. User has had to remind multiple times.
- [NO writelog replay](feedback_no_writelog_replay.md) — user STRONGLY rejected. Never propose. Defeats the USF/ML purpose.
- [py65 misses dispatch bugs](feedback_py65_misses_dispatch_bugs.md) — `verify_all` is silent about PSID speed / CIA timer / dispatch-rate bugs. md5-exact register sequence does NOT mean the SID sounds right on hardware. Suggest an ear-test on new engines / dispatch changes.
- [Observation drift vs music drift](feedback_observation_drift.md) — siddump's per-VBI-frame bucketing of writes is OBSERVATION. SID chip sees a continuous stream. Use `compare_instruction_stream` (global cycle-ordered, init-skipping). Don't be misled by per-frame "FAIL" when cycle-ordered stream matches.
- [Always through USF](feedback_always_through_usf.md) — pipeline MUST be SID → USF → SID
- [USF spec sync](feedback_usf_sync.md) — update spec, all converters, player, and tests whenever USF changes

### Working with the user
- [User nudge pattern](feedback_user_nudge_pattern.md) — question implausible explanations, brainstorm across math fields, extract don't reconstruct
- [User strategic pattern](feedback_user_strategic_pattern.md) — propose options before code; honest scope; pause after each step
- [Commit early](feedback_commit_early.md) — commit immediately after each verified improvement
- [No co-author in commits](feedback_no_coauthor.md) — never add `Co-Authored-By`
- [Do the actual work](feedback_do_the_work.md) — implement ALL optimizations, don't punt
- [Worktree agents must commit](feedback_worktree_commit.md) — always tell agents to `git add` + commit
- [Meta-process](feedback_meta_process.md) — at natural pauses, re-evaluate if the current approach is still highest ROI and whether memories / CLAUDE.md reflect reality

### USF schema discipline
- [USF representation principle](feedback_usf_representation_principle.md) — TRIPWIRE: before designing/changing any USF effect/instrument representation, read `docs/usf_representation_principle.md` IN FULL. Effects are parametric over a musical basis; the engine holds mechanism, never an indexed library.
- [Init trichotomy](feedback_init_trichotomy.md) — TRIPWIRE: before handling init for a new engine migration, read `docs/sid_init_report.md` IN FULL. Init writes split into reset (universal, invisible to USF) + priming (typed musical params in USF init.sid) + environment (top-level USF) + engine bookkeeping (out of USF). NO shape detection, NO engine-name dispatch. Validated empirically across 100% of HVSC.
- [Principle-first analysis](feedback_principle_first_analysis.md) — CHECKLIST. Run the 6 questions BEFORE proposing any effect/instrument design or "engine-specific codegen" suggestion. Don't wait to be caught.
- [Schema addition discipline](feedback_schema_addition_discipline.md) — CHECKLIST. Before adding any USF schema field: re-read the principle doc IN FULL, then exhaust derivation / engine_constants / existing-params alternatives. `bytes`-typed fields are suspicious by default. Lesson from Companion's reverted `VoiceBlock.trailing`.

### Engineering reflexes
- [Use 6502 mindset](feedback_6502_mindset.md) — all bugs are pointer errors; think in exact byte offsets
- [C64 banking when relocating](feedback_c64_banking_relocation.md) — relocating code into $A000-$BFFF? Audit every `sta $01` inside it. A banking flip takes effect on the very next fetch; if that fetch is also in the banked range it reads ROM.
- [Bug investigation methodology](feedback_bug_investigation.md) — pick one bad subtune, trace the first wrong frame, fix root cause
- [Full decompile before Hubbard work](feedback_full_decompile_hubbard.md) — disassemble init+play first for every new Hubbard SID
- [Trust binary not disassembly](feedback_disassembly_data_section.md) — `!by` directives can be wrong about initial data; read the actual bytes
- [Deconstruct, don't reproduce the trick](feedback_deconstruct_not_reproduce.md) — reproduce the exact instruction stream with clean code; the trick to avoid is Hubbard's space-saving MECHANISM, not the output. Investigate odd behaviour (what/audible?) before discarding.
- [Migration as stress test](feedback_migration_as_stress_test.md) — migrating a new engine surfaces hardcoded assumptions in the shared core. Fix parametrically, not by matching the hardcode.
- [Audit discriminator](feedback_audit_discriminator.md) — for per-instrument audits, use fx_flags cache or v_instr,x — NEVER ADSR alone. Multiple insts share AD/SR.
- [Sidxray methodology](feedback_sidxray_methodology.md) — read `src/sidxray/METHODOLOGY.md` before cracking a new player
- [Dataflow over heuristics](feedback_dataflow_over_heuristics.md) — for engine-data extraction from a disassembled 6502 player, default to dataflow tracing (find STA $D4xx, walk A's predecessors back to its source). Reach for content heuristics only when the semantics aren't recoverable.

## References

- [HVSC index DB](reference_hvsc_db.md) — `hvsc84.db` at repo root. SQLite catalogue of every HVSC #84 SID with engine classification + per-SID build status. Query with Python (no `sqlite3` CLI). Refresh via `tools/build_sid_db.py` after migrations / new builds / HVSC updates.
- [Songlength overrides](reference_songlength_overrides.md) — `tools/songlength_overrides.json`. Durable corrections to HVSC's Songlengths.md5 when a duration is clearly anomalous (defaulted ~4s for a 56s natural-loop tune). Survives HVSC re-fetches.
- [USF v2 format](reference_usf_v2_format.md) — the on-disk .usf format + sidecar FLACs. Spec at `docs/usf_format.md`. Custom DSL, Lark grammar, `.usf` + N `.sample{N}.flac`.
- [Digi pipeline](reference_digi_pipeline.md) — USF2 digi support; extract → Sample/FLAC → pack → SID. Cycle-strict via `siddump --writelog`. First engine: Chimera 1-bit wavetoggle.
- [PC trace tool](reference_pc_trace_tool.md) — `tools/siddump --pc-trace FILE START END` dumps libsidplayfp CPU PC. Use when a SID misbehaves in sidplayfp but py65/writelog look fine.
- [Audit tool](reference_audit_tool.md) — `src/usf/audit.py`: PC-traced per-voice SID-write capture. Use for Rule 1 collapse audits when voice attribution matters.
- [Tokenization for ML](reference_tokenization.md) — USF is NOT tokens; tokenization is a downstream conversion when ML training starts. REMI-style is the proven starting point.
- [Hubbard PWM bounds](reference_hubbard_pwm_bounds.md) — pulsework's $08/$0E direction-flip thresholds are HARDCODED, not per-instrument

## Deprecated memories

Older project phases (Lean codegen, Grade A counting on GT2, completed
migration / refactor phases) live under [`_deprecated/`](_deprecated/)
with a README explaining what's there. They no longer load — out of
this index.
