---
name: project_basic_program
description: "Basic_Program family (486 RSID-BASIC tunes) — PRODUCTIONIZED round-trip: 455/486 (93.6%) FULL; NO-SILENCE + NORMAL FORM stage 1 (260 NF / 195 legacy); mass-written + regression"
metadata: 
  node_type: memory
  type: project
  originSessionId: 31df618e-1d05-4346-8dfa-a60476d0a5cc
---

**Basic_Program = 486 HVSC SIDs, all RSID v2, load=init=play=0, C64-BASIC flag set.**
Each is a tokenized Commodore BASIC V2 program at `$0801` that POKEs the SID — NO
machine-code player; the "engine" IS the C64 BASIC+KERNAL ROM. Each tune is its own
hand-written micro-program (tempo = FOR/NEXT busy-waits; loops via GOTO or ENDs).
Adjacent labels are NOT this: `Basic/Jim_Butterfield` (47, a player), `Basically_Music`
(12, machine-code, pun name). Full dossier: `pipelines/basic_program/docs/` (README +
6 research clusters + recon + survey + Twinkle proof). engine_docs `basic_program` = OK.

**Ground-truth capture was BLOCKED, now SOLVED (commit 495c877).** `siddump` never called
libsidplayfp `setRoms()`, so RSID-BASIC ran with stub ROMs and emitted ~nothing (one
$D418 then silence). Added `--roms-dir` (default `~/.local/share/sidplayfp`, where canonical
MD5-verified C64 ROMs already live); loads kernal/basic/chargen + calls setRoms() before
config(). Now ALL siddump invocations load ROMs by default, so `writelog_capture` works on
BASIC tunes with no change. libsidplayfp auto-handles BASIC warm-start ($BF53/55) + $030C
subtune select. ROMs are Commodore copyright — use locally, never commit.

**Capture survey (486×2, commit 8605e4a): 486/486 DETERMINISTIC, 486/486 musical, 0 exclusions.**
libsidplayfp is deterministic from cold reset (m_rand only used for random powerOnDelay,
which we set 0), so even RND(0)/TI/PEEK-timer tunes reproduce — under Path B we freeze ONE
canonical realization. 5 late-start tunes (long DATA/array build) confirmed musical at 120s.
1 digi tune (`Black_Box_V8_Demo`, $D418 ~107x/frame) → Mode 2 (cycle-exact); other 485 → Mode 1.

**Strategy = Path B (trace-lift), NOT source-decompile.** Capture the deterministic writelog,
lift to USF note events (engine-agnostic; covers SYS-hybrid + algorithmic + RND that decompile
can't). CORE-TENET fit. NO new USF schema fields. See [[feedback_no_writelog_replay]] — this
is NOT replay: we extract musical note events (pitch+duration+instrument), the player re-derives
writes from musical content.

**Twinkle proof FULL (commits 3d58742 + 14c0158): SID→USF→SID, writelog 60/60 is_full=True + rhythm faithful.**
`pipelines/basic_program/proof_twinkle.py`. Loop: capture → lift to (notes, per-tune freq_table,
triangle instrument, init) → write+reparse a real `.usf` (USF) → build a MINIMAL DEDICATED
PSID player from the parsed USF → flat (reg,val) match + rhythm (inter-onset frame-gap) check.
`docs/example_Twinkle.usf` is pure musical content (note names + durations + tuning), zero
artifacts. Key generalizable findings:
- **Driver prefix**: empty-init PSID emits a leading $D418=$0F; the RSID capture starts with the
  same driver write — STRIP it from the emitted init or it duplicates. Init otherwise rebuilt from
  USF semantics (instrument ADSR + init.sid.master_vol), not raw-byte replay.
- **Rhythm-blindness**: each note = exactly 4 writes regardless of hold (the FOR-NEXT hold is pure
  delay), so the flat (reg,val) stream can't see rhythm — duration lives in frame GAPS. USF carries
  durations; faithful verdict = flat match + frame-gap check. `writelog_capture` DROPS empty frames,
  so durations need a raw-frame capture (`capture_real` in the proof).
- BASIC's free-running FOR/NEXT can't align frame-exactly to a 50Hz player (+Trap C), so rhythm has
  inherent ±few-frame slack = the `duration_tol` C6 specified.
- Hubbard composer NOT reused (it adds per-frame writes BASIC tunes lack) — per CORE TENET the family
  gets its own runtime.

**Multi-voice generalization DONE (commit 12e6b68): Baby_Elephant_Walk FULL + Twinkle regression.**
`pipelines/basic_program/proof_multivoice.py`. Step model `[attack]·hold·[release]·gap`; Baby =
3-voice chord-per-step (gate-then-freq, waves saw/pulse/saw), Twinkle = 1-voice (freq-then-gate) —
same code. Overlap EXACT for both (Baby 1677/1677, Twinkle 60/60) = every (reg,val) reproduced in
order across all voices. Key pieces: the cross-voice WRITE ORDER is a per-tune structural template
derived from the capture (gate-vs-freq order + voice sequence) — NOT in USF; per-voice waveforms →
instruments; freq 0 = silent-but-gated voice (verbatim); loop detection (`_find_loop`: Baby intro=9
period=134, loops back; Twinkle ENDs); 16-bit initial-delay reproduces the ~9s DATA-read setup.
**Family verdict = `verdict_basic` = overlap-exact + proportional `duration_tol` (0.15)**: free-running
BASIC can't frame-exactly match a 50Hz player (per-step sub-frame rounding + Trap-C accumulate over a
multi-min loop), so Hubbard's strict |len|<=64 doesn't apply — the duration_tol C6 anticipated. Baby's
~12% wall-clock length drift is tempo quantization; the write STREAM is exact. REFINEMENT (noted, not
built): absolute-frame step scheduling (fire step k at its captured absolute frame) would stop the
per-step rounding accumulating and tighten the length.

**Absolute-frame scheduling + rho unit-conversion DONE (commits dbc567f -> dd4d5bf): CYCLE-EXACT, diff 0.**
The player fires step k at its captured frame (16-bit frame counter vs per-step atk[k]/rel[k]; loopbase
+= loop period each wrap) — no per-step accumulation. **KEY siddump-timing finding (corrects an earlier
WRONG call): there is NO emulation-vs-hardware difference.** The rebuild's play() fires at the TRUE VIC
frame rate (PAL 19656 CPU cyc = 50Hz; consecutive play-entry PHI1 cycles are exactly 19656 apart). BUT
`siddump` steps via `engine.play(cyclesPerFrame=19688)` where cyclesPerFrame counts EVENT-SCHEDULER ticks
(`c64::clock()=eventScheduler.clock()`, <1 CPU cycle each), so one siddump "frame" advances only ~18000
CPU cycles, NOT one 19656-cycle play period. So an onset in siddump-FRAME units is the wrong clock for a
player that advances per PLAY-PERIOD. FIX = scale targets by **rho = plays-per-siddump-frame** (~0.919 PAL;
`measure_rho` self-calibrates per-clock from a trivial PSID's |P: rate, so NTSC works too). Result: gate-on
absolute-cycle ratio reb/orig 1.088 -> **1.000**, verdict length diff 225 -> **0** (Baby 1902/1902, Twinkle
60/60). Verdict tightened to strict |len|<=64. (The earlier dbc567f framing — "measurement bias, don't
scale because it'd be 8.7% fast on hardware" — was WRONG; the play IS 50Hz, the 1.088 was the
siddump-frame-vs-play-period unit mismatch, and scaling by rho is the correct hardware-faithful fix. User
caught it: "i doubt there is a 9% difference between emulated and real hardware.") Hubbard etc. never hit
this — both sides PSID, so the flat (reg,val) compare is bucketing-agnostic and the mismatch cancels.

**COVERAGE PROBE (commit b38da6a): 8/81 (10%) FULL** with the freq+gate lift. Dominant gap (~52%
overlap_diverge, 23 on ctl regs) = the per-step writes are RICHER than freq+gate (per-note vol/accent
e.g. Deutschlandlied vol=0F->08->06, per-note ADSR, gate-value/order variants, legato). All of it is
MUSICAL (maps to USF instruments/master_vol/etc.) -> the principled fix is a SEMANTIC richer lift
into existing USF (NOT generic per-step register-deltas = the [[feedback_no_writelog_replay]] trap,
NOT a bytes escape-hatch). Reuse deprecated `gt2_pipeline/converters/regtrace_to_usf.py` (~80% of the
lift algorithm: freq_to_note_pal, gate-transition note boundaries, tempo). **PORT CAVEAT (user, do not
forget): the old regtrace_to_usf consumes per-frame SNAPSHOTS (Trap A — loses within-frame order +
can't model the things we need); the port MUST consume the `--writelog` ordered (reg,val) stream
instead.** Probe failure buckets: overlap_diverge 42 / lift_crash 16 / build_fail 6 (branch-out-of-range
= the +-127 trampoline bug) / lift_no_gate 4 (legato gate-once + GET) / too_many_steps 4 (N>255, 8-bit
stepidx) / length_fail 1. Cheap wins in progress: branch trampolines + 16-bit step indexing.

**SEMANTIC LIFT DONE (10%->22%): `pipelines/basic_program/semantic_lift.py` + `semantic_probe.py`.**
Ported the regtrace_to_usf IDEA onto the --writelog stream (NOT per-frame snapshots). Model: segment
writelog (real frames) into active-runs separated by silent FOR/NEXT holds; a STEP = attack run (note
start: freq/gate-on + per-note timbre) + optional release run (gate-off group). Per-step TEMPLATE: each
reg is CONST (same every step = instrument/waveform, emitted inline) or PERSTEP (varies = note freq /
$D418 dynamics / per-note timbre, packed in the step record, emitted via (sp),y). Principled (const=
instrument, perstep-freq=notes, $D418=dynamics), reuses the absolute-frame+rho+16bit-ptr+loop player.
Trims trailing capture-cut steps before the consistency check. **Stratified probe 18/81 FULL (22%, up
from 8/81=10%).** The opaque overlap_diverge 52 bucket RESOLVED into clean named levers: **#1
unsup_variable_template 31 (RESTS — voices conditionally silent so the per-step reg set varies; needs a
per-step voice-active MASK = the note pattern, emit only active slots) + #2 unsup_legato 19 (gate set
once + freq-only; 1-phase attack-only steps, note boundary = freq change)** + too_few 8 + overlap_diverge
3 (near-misses) + length_fail 2 (loop-detect miss). Rests+legato = ~62% of the sample -> handling both
pushes coverage well past 50%. STILL proof-grade (no USF-file round-trip yet; productionize = map
const->instrument / perstep-freq->notes / $D418->dynamics into USF + regression).

**RESTS via per-register mask DONE (commit ad3b783): 22% -> 27% (Deutschlandlied FULL).**
`_superset_templates`: superset register order (max-reg step), every step must = superset filtered to
its present regs (order-preserving subset), per-step PER-REGISTER mask (bit i = superset entry i present);
`build_player_masked` emits each superset entry iff its mask bit set. Handles silent-voice rests +
freq-inherited steps (Deutschlandlied step0 = gate-only). Gain modest (+4 FULL). Remaining
variable_template (26) PRECISELY diagnosed: **dup_reg_in_step 15** (a reg written 2x/step -> the reg-keyed
superset can't represent repeats; needs POSITIONAL masking) + **off_superset_reg 9** (no single step has
all voices -> superset must be the ordered UNION of all steps, not a max step) + 2 now-pass. Probe buckets
now: FULL 22 / variable_template 26 / legato 19 / too_few 8 / overlap_diverge 4 / length_fail 2 (incl.
American_Flag: overlap EXACT 403/403 but len diff 68, just over the +-64 -> loop/window boundary).

**LEGATO DONE (commit ce7337f): 27% -> 35%.** segment() routes legato (small gate-off count): one-time
gate-on + setup -> INIT, steps = pure freq active-runs (boundary = freq group after a hold), no release.
`build_player_legato` = 1-phase (each fire emits attack at its abs frame, advances, targets next step;
no gate-off), reuses per-register mask + abs-frame + rho + loop. Cancion_de_cuna + Golden_Brown FULL.
Probe 28/81 FULL (35%). **The remaining big buckets CONVERGE on TWO shared `_superset_templates`
limitations across variable_template (26) + legato_variable (11) = 37 tunes: (1) dup_reg — a reg written
2x/step (reg-keyed superset can't represent repeats; needs POSITIONAL matching); (2) off_superset — no
single step has all regs (superset must be the ordered UNION of all steps, not a max-reg step). Fixing
both is ONE unified generalization paying off across gated AND legato.** Coverage trajectory this session:
10% -> 22% (templates) -> 27% (rests) -> 35% (legato).

**ORDERED-UNION SUPERSET DONE (commit 50e5c90): 35% -> 40%.** `_union_order` builds the superset as the
ordered UNION of all step reg-seqs (precedence DAG over adjacent regs + Kahn topo-sort + subsequence
verify), replacing the max-reg-step pick. Captures off_superset (one-voice-per-step alternating V1/V2/V3).
Swapped into `_superset_templates.derive` (attack+release; benefits gated AND legato). Probe 32/81 (40%).
**KEY: the two root causes turned out to be DIFFERENT problems, not one — off_superset was the tractable
half (union order); dup_reg is mostly ARPEGGIO (`04 00 01 00 01 00 01...` = freq written a VARIABLE number
of times per step; example_05, Head_Coach), a variable-length intra-step sequence (like Ahoy multi-rate)
= genuinely hard, DEFERRED (_union_order returns None on intra-step dup).** Remaining: variable_template 22
+ legato_variable 9 (mostly arpeggio) + length_fail 5 (overlap-EXACT but length off — timing/loop, e.g.
Toonypoo reb 2980 vs orig 4132) + too_few 9 + overlap_diverge 4. Session arc: 10%->22%->27%->35%->40%.

**CATCH-UP LOOP DONE (commit fdab2c7): 40% -> 41%.** Players fired ONE step/play(); FAST tunes (multiple
note-steps per siddump frame, e.g. Toonypoo one-voice-per-step ~9 writes/frame) fell behind -> rebuild
overlap-exact but truncated. Fix: catch-up loop (load sp once; `while frame>=curtgt: fire; recheck` via
jmp pl_chk after each fire), all 3 players. Toonypoo FULL. CORRECTNESS fix (fast tunes were broken); only
+1 on this sample (few fast tunes here). length_fail 5->4 — remaining are DISTINCT causes (missed-loop
e.g. Techno-Rock_Fugue, degenerate e.g. Bowling 6-step), not one clean fix. Session arc:
10%->22%->27%->35%->40%->41%.

**✅ PRODUCTIONIZE DONE — REAL USF ROUND-TRIP: 137/486 (28.2%) FULL at full songlength, mass-written + regression.**
`pipelines/basic_program/usf_roundtrip.py` (`model_to_usf` / `usf_to_model` / `roundtrip` / `verify_usf`)
+ `family_batch.py` (full-songlength through-USF coverage + `--write` mass-write, resumable). The semantic
model splits cleanly: pitch/rhythm/timbre/tuning are MUSICAL → real USF (per-voice NoteRows pitch+duration,
rests = silent voices, instruments = const waveform, freq_table = tuning); the non-musical per-tune WRITE
MODEL (template slots + kind, init, loop, rho, start_frame) packs into USF scalar `params {}` as ints
(bp_atk{i}=reg<<16|kind<<8|val, bp_init{i}, bp_loop_*, bp_rho_milli, bp_start_frame, bp_legato). build_psid
reconstructs from the parsed .usf and reproduces the exact writelog. 137 `.usf` + `.sidfinity.sid` written
next to HVSC originals; DB registers usf_path/sidfinity_md5 + pipeline=`pipelines/basic_program` (137);
6-member feature-cover portfolio wired into `tools/regression.py` (tier: full SID→USF→SID round-trip FULL).

THREE round-trip bugs fixed this session (the gap from 16%→28%):
1. **Stale `s['next']`** — durations must come from the NEXT step's ρ-scaled `on_frame`, not the pre-ρ
   `s['next']` (build_model ρ-scales on_frame but leaves 'next' stale) → span was ~2.8× too long.
2. **Dropped `start_frame` offset** — the first step's absolute on_frame (e.g. Baby's 406-frame intro
   silence) is a scalar param (`bp_start_frame`); without it the rebuild starts early and loops extra times.
3. **Lossless per-tune freq ALPHABET** (`_assign_slots`) — distinct POKEd freqs that quantize to the same
   equal-tempered note name collided in the 256-byte freq_table (it holds one freq per (octave,semitone)).
   The freq_table is per-tune CONTENT (USF principle Rule 2), so each distinct freq gets its OWN slot at its
   nearest name, linear-probing on collision (≤96 usable slots; >96 = glide/vibrato → too_many_pitches,
   deferred). Measured: 25 no-collision / 11 collision-fit96 / 0 over96 on the stride-6 sample → fixes ALL.
4. **Voiceless-const per-step activity** (`bp_has_masks`+`bp_mask{k}`) — usf_to_model derived per-step masks
   from voice-rests, which can't see a voiceless const's activity (e.g. a per-note $D418=15 re-poke on SOME
   steps). Detect when rest-derivation is insufficient (Ahoy-class) → store explicit masks; common path
   (voices all-or-nothing) unchanged. Ahoy_Magazine 581/581 FULL. (+41 FULL: 96→137.)

**✅ NTSC CLOCK-FLAG FIX (2026-06-25): 137→163 FULL (28.2%→33.5%).** `build_psid` hardcoded `FLAGS_PAL_6581`,
so NTSC tunes' rebuilds were captured by siddump at 50Hz not 60Hz → the rebuild got through LESS music per
wall-second → an overlap-exact but SHORT (truncated-prefix) flat stream = length_fail. The flat (reg,val)
verdict drops timing, so a clock mismatch shows as length, NOT divergence. Diagnosis: `capture_real` gave the
orig 2520 frames vs the rebuild 2100 for the same 42s (60 vs 50 fps) with per-bin writes identical where both
exist (NOT tempo-stretch — a frame-count mismatch). 34/46 length_fail were NTSC; the SHORT ones already passed
(deficit < the |len|≤64 tol; deficit grows with songlength). Fix: derive clock bits from `model['clock']`
(NTSC→2, PAL→1, flags=`(bits<<2)|(1<<4)`). +26 length_fail→FULL; 40 already-FULL NTSC stay FULL; PAL untouched.
American_Flag added as the NTSC regression canary. length_fail 46→19.

**✅ ARPEGGIO/VIBRATO SPLIT (2026-06-26): 163→187 FULL (33.5%→38.5%).** An arpeggio/vibrato note is a held
note whose freq is re-POKEd per tick (arp cycling a chord, or vibrato wobble) — `segment` lumped it into ONE
step with the freq register written N times → `_union_order` None (intra-step dup) → unsupported. `_split_attack`
splits a step's attack into sub-steps at each register repeat → each freq update is a fast freq sub-step (fired
by the abs-frame player's catch-up loop); gate-off rides only the last sub. THREE correctness subtleties: (1)
the split is CONDITIONAL — a CONSISTENT intra-step dup (same shape every note, e.g. ctrl re-poked) is handled
positionally by `derive_template`, so `build_model` tries the UNSPLIT segmentation FIRST (== the pre-arp path,
provably can't regress any prior FULL — Xmas-Card class) and only falls back to `segment(split_dups=True)` on a
template/too_few build-failure; (2) a `force_split` override + `best_attempt()` VERIFY-LEVEL retry recovers
tunes whose unsplit model BUILDS but VERIFIES wrong where splitting wins (Pearl_Diver — the build-level fallback
can't see verify-failures); (3) `family_batch.process()` refactored onto `best_attempt` (shared orig-writelog
capture, returns the verified usf+sid bytes for byte-exact mass-write). Vibrato with >96 distinct freqs hits
`too_many_pitches`→build_fail (the freq alphabet caps at 96 slots) — deferred. Head_Coach (arp) + Xmas-Card
(consistent-dup) added as portfolio canaries (now 9). 187 mass-written, 0 orphans, DB refreshed.

**RESIDUE (299, by dependency order — all are LIFT limits or richer-musical, NOT round-trip-encoding):**
unsup_variable_template 67 + unsup_legato_variable 29 = 96 (the arp/intra-dup cases the split did NOT resolve —
deeper variants: precedence cycles, or split-then-still-variable) + too_few_after_trim 59 + too_few_steps 9
(degenerate/short; the split grew too_few_after_trim by re-bucketing former variable_template) + not_clean 53
(NOT FULL — perstep non-freq; the split EXPOSED per-tick non-freq writes, e.g. per-tick ctrl/PW → needs a
dynamics/instrument-param representation) + overlap_diverge 45 + length_fail 26 (loop-period) + build_fail 9
(mostly vibrato too_many_pitches). 1 digi (Black_Box_V8_Demo) → Mode 2.

**✅ PER-NOTE INSTRUMENTS (Phase 1) + SONG-END LOOP FIX (2026-06-26): 187→192 FULL, not_clean 53→27, 0 regr.**
PRINCIPLED + SCHEMA-FREE: per-note per-voice TIMBRE (waveform/ad/sr/pulse-width) = a per-note INSTRUMENT change,
represented by a finite set of USF `Instrument`s selected by `NoteRow.instr` (Rule 2: instrument = const musical
content; the engine holds mechanism). The note's instrument = its RUNNING/effective timbre (engine re-writes a
reg only when it changes — the stateful case, captured by the existing per-step mask). ctrl→waveform[0],
ad/sr→adsr, pw→pwm.init. is_clean now rejects only perstep GLOBAL regs (filter $D415-17 / master-vol $D418 = NOT
per-voice instrument props → Phase 2). Three integration fixes were the actual unblock (the player/lift, not the
representation): (a) **SONG-END detection** in build_model — if the WRITELOG goes silent well before the capture
window (last_write < 0.85*window), the song plays ONCE → DON'T apply a spurious internal-phrase loop (`_find_loop`
false positive) or the rebuild over-emits ~2× by replaying (Musette direct build 728 vs orig 339 → fixed). Use
the last WRITE frame, NOT the last step (a tune that loops with a trailing gap still fills the window — Musichetta
ratio 1.00). (b) the player only knows const/perstep, so usf_to_model RESOLVES inst slots into each step's writes
then presents them as plain perstep. (c) **KIND-AWARE voice**: inst slots are voice-tied (REG_VOICE); const/
perstep-freq keep the freq-only voice (VOICE_OF) so a non-freq CONST (e.g. V2 ctrl written every step) stays
VOICELESS = always-present — fixes a Musichetta-class regression where const V2 ctrl got wrongly voice-gated and
skipped on V2 rests. Musette/Frogs/Musichetta FULL. Canary: Musette (portfolio, 10 members).

**✅ TIMBRE-ONLY rest-step (2026-06-26): 192→197 FULL, 0 regr.** The "rest-step timbre" build_fail was a voice
writing a perstep-timbre reg on a step with NO note (instrument SETUP for an upcoming note); inst_val crashed on
the rest row's missing instrument. Fix: a TIMBRE-ONLY step (writes a perstep-timbre reg but NEITHER freq byte)
carries the instrument on its rest NoteRow, so the stored mask emits only the timbre regs (no freq). 14/20 were
Bond_Alan tunes (a common authoring style). Chain-Reaction/Tybbernyde FULL. The OTHER rest-step sub-case is
PARTIAL-FREQ (a note writing ONE freq byte + timbre, the other byte CARRIED = stateful freq; Lead_De-tuned) —
still build_fail, needs the running-freq generalization (vfreq must return the effective (running hi, running lo)
and treat a freq-byte/gate-on write as active).

**✅ RUNNING-FREQ / partial-freq (2026-06-26): 197→216 FULL (+19!), 0 regr.** A voice may write only the CHANGED
freq byte (the other CARRIED) — `vfreq` required both, misreading partial-freq notes as rests (build_fail) or
diverging on glides. Replaced `vfreq` with an `eff` running-freq table: track running (hi,lo) per voice (seeded
from init); a note's pitch = effective (running hi, running lo); active = wrote a freq byte. Full-freq tunes
UNCHANGED (both bytes every note → identical). Also fixed `_kind`: a CONST timbre slot (e.g. a fixed gate-off
RELEASE ctrl) stays const even when that (voice, reg) is a perstep inst slot in the ATTACK — was wrongly tagged
inst → crash. HIGH-VALUE: +19 (helped build_fail partial-freq AND overlap_diverge GLIDES 48→30). Lead_De-tuned
FULL. Some Bond_Alan (Glass_Jaw build_fail, Interlace diverge) still need more.

**✅ GLOBAL AUTOMATION TRACK (Phase 2, 2026-06-27): 216→224 FULL (44.4%→46.1%), not_clean 27→0, 0 regr.**
The chip-GLOBAL state (master volume $D418 + filter $D415-18) is NOT a per-voice instrument prop, so it can't ride
`NoteRow.instr` — it belongs to the whole subtune. Represented as a **single shared per-subtune global automation
track**: a list of `GlobalEvent(step, dyn?, cutoff?, res?, mode?, route?)` on `MusicSubtune.global_track`, where each
field is a NAMED musical control decomposed from the registers ($D418 = mode<<4 | dyn; $D417 = res<<4 | route; $D416
= cutoff hi). PRINCIPLED per the representation TRIPWIRE — the forbidden shape is OPAQUE register dumps / library
indices, NOT multiple-named-fields-per-row (a `GlobalEvent` is exactly like a `NoteRow`'s pitch+dur+instr+flags: many
named fields, one row). One shared track (not separate vol/filter streams): SID's only global controls ARE these few
regs, and the engine writes them interleaved in a fixed per-tune order — splitting them loses nothing and the
composer re-packs the exact register bytes; write ORDER comes from the per-tune template (unchanged). User settled
the design ("i dont really see the problem of a shared track... why couldnt we just do multiple commands"). Shared-USF
plumbing: grammar `global_block?` (backward-compat, 40/40 existing .usf still parse), `GlobalEvent` type + parser/
writer/`__init__` export. basic_program: `is_clean` accepts perstep GLOBAL_TRACK regs ($D416-18; perstep $D415-lo
still rejected); `model_to_usf` decomposes a running-global-state diff into GlobalEvents (only emit a field when it
CHANGES); `usf_to_model` re-packs via `gpack` + applies each step's GlobalEvent before emitting, kind='global' slots
emit the packed reg, `_to_ps` maps global→perstep for the player. Moog_Swing (filter-sweep: cutoff ramp + mode/res/
route cycling LP/BP/HP) + Xmas + 6 more FULL; Moog_Swing added as canary (now 12). The 19 other former-not_clean
tunes now flow through and reveal their REAL next blocker (length/loop, overlap, vibrato build) — correctly, they
were masked by the not_clean rejection. Text round-trip proven end-to-end (best_attempt does write_file→parse_file).

**✅ LOOPING EXTEND-AND-VERIFY (length_fail Fix A, 2026-06-27): 224→231 FULL (46.1%→47.5%), 0 regr.** length_fail
census (42, 41 short): a LOOPING rebuild's play() runs ~1/rho SLOWER than the orig's free-running BASIC, so the
fixed songlength×1.1 capture window cuts the rebuild mid-loop → it's a correct PREFIX but short past the |len|≤64
tol. Fix (`_compare_with_extend` in usf_roundtrip, used by BOTH `_attempt_model` and `verify_usf`): when the rebuild
is a short exact-prefix AND the tune loops (`loop_to` set) AND short by >64, RE-CAPTURE the rebuild for more frames
(`dur*(a/b)*1.2`, cap 240s) and accept iff the orig's ENTIRE writelog is reproduced as an exact prefix (orig ⊑
extended-rebuild, match_all==len_a). NO tolerance widened — this is literally "the rebuild emits the same writelog
as the original," just given enough frames to finish (CORE TENET clean; the user's FULL definition preserved). A
play-once rebuild has HALTED (done=1) so it never grows → genuine short tails (trailing-trim) stay failed; a loop
that truly DIVERGES when extended fails the exact-prefix check and stays failed (Computer_Shake/Legion_of_One/
Shake_n_Vaccine — real loop-body divergence, correctly NOT passed). Recovered 7 (Love_Me_Tender, Fog, Galaga_Chords,
Yellow_Submarine, Arkansas_Traveller, Kandenslit, House_of_Cards). Canary: Love_Me_Tender (portfolio now 13). The
DEEP length_fail residue (Fix B, NOT done) = ~31 noloop tunes that play once when the orig keeps going (short up to
3846): `_find_loop` needs ≥8 IDENTICAL backward-run chords; these have all-distinct tail chords (transposing melody /
per-frame vibrato/filter modulation) → no exact-chord loop to detect. Needs a smarter loop detector (rhythm-periodic
but pitch-transposed) or a richer evolving-content model — investigate which before fixing.

**✅ MIN-TRIM FALLBACK (length_fail Fix B part 1, 2026-06-27): 231→235 FULL (47.5%→48.4%), 0 regr.** length_fail
census (34) sub-causes: onsets_ok_short_tail 21 (model has every note; short only at the tail) + perframe_PWM/filter
6 (continuous per-frame $03/$0A/$11 pulse-width + $16 filter sweep the onset model doesn't lift — Pepper_Spray 62
onsets but 11480 writes) + under_segment 4 (segment merged onsets not gap-separated) + loop-real-diverge 3 (the
extend-verify correctly rejected). The trailing-trim was OVER-aggressive: it dropped EVERY trailing step differing
from the modal template (Polimus lost 93 real-note steps), when its only job is removing capture-cutoff partials.
Fix: `min_trim` variant drops ONLY trailing steps with no release (gate-off never captured = real cutoff), keeping
complete differing final sections for the masked path. Made it a best_attempt VERIFY-FALLBACK (try aggressive trim
first; min_trim only on length_fail + must verify FULL) → structurally 0-regression (some tunes NEED the aggressive
trim: their tail breaks the template — Singalong/Let_it_Be regressed under unconditional min_trim, fine under
fallback). +4 (El-Shaddai, English_Tune, A_Musical_Round, Spy_Music). build_model gained `min_trim`; best_attempt
adds the 3rd retry after force_split.

**✅ FREQ-HI SEED (overlap_diverge round 1, 2026-06-27): 235→248 FULL (48.4%→51.0%), 0 regr.** overlap_diverge (36)
clustered by first-divergence site (od census, `tmp/`): DOMINANT = `V1fhi reb=$00` ~13 (rebuild emits freq-HI=$00
where orig has nonzero) + song-end `mvol=$00` fade mis-looped 3 + ordering/ctl misc. Root cause of the dominant
cluster: in `model_to_usf` the running-freq `eff` table seeded `run_hi/run_lo` ONLY from init writes, then gated
`row[vc] = (hi<<8|lo) if (wh or wl) and vc in run_hi and vc in run_lo else None`. A voice writing freq-HI-ONLY (a
coarse pitch sweep/glide, lo never written) failed `vc in run_lo` → row=None → the note became a REST → the perstep
mask still emitted V1fhi with `_pitch_freq(rest)=0` → `V1fhi=$00`. The SID freq regs RESET to 0, so a hi-only write
genuinely means freq `(hi, 0)`. Fix: seed `run_hi/run_lo = {vc:0 for vc in voices}` (chip reset state). 0-regression
(a FULL tune writing hi-only would already have diverged). +13 (Earthworms, Moonlight, Two_Lines_of_Code 1+2,
Alien_Attack, Angry_Ninja, Infinitesimal, M7_Shot, Dog_Fight, Spaceshuttle, Drum_Controller, Little_Brain,
Wail_of_the_Banshee). A few glide-heavy sweeps moved buckets (M8_Sound/Tron → length_fail correct-but-short;
Interlace → too_many_pitches >96 freqs). Canary: Earthworms (portfolio 15).

**✅ SONG-END SILENCE (overlap_diverge round 2, 2026-06-27): 248→252 FULL (51.0%→51.9%), 0 regr.** 9/23
overlap_diverge tunes end with master-vol=$00 (the engine silences itself). Two shapes: (a) bare `mvol=00` after the
notes (a fade to silence; the orig plays ONCE but the model found a FALSE internal loop → rebuild loops instead of
ending) — the CLEAN cluster, diverges only at i=a−1; (b) a full zero-everything silence-all sequence + mvol=0 (these
also diverge EARLY for other reasons — not this fix). Fix = a `song_end` write sequence: the engine's stop-routine
output, captured as the SYMMETRIC BOOKEND of `init` (same packed `bp_songend{i}` round-trip as `bp_init{i}`).
`_song_end_writes` grabs every write after the last note step's gate-off frame when the writelog ends in mvol=$00;
its presence forces `ends=True` (play-once, no loop); the 3 players emit it once at the halt before `sta done`. Wired
as a best_attempt VERIFY-FALLBACK (`detect_song_end=True`, tried only on overlap_diverge/length_fail) → structurally
0-regression; non-song-end tunes get `song_end=[]` = byte-identical asm + `bp_songend_n=0` (old .usf unaffected,
`.get` default). +4 (Silver_Bells, Let_it_Snow, Oh_Suzannah, Bach_Minuet — last two EXACT). Canary: Silver_Bells.
The zero-all sub-cluster (Hymna_CCCP/Johnny_Reb/Prospector/Sounds_of_Dixie) needs the silence-all captured
mid-stream — deferred.

**RESIDUE (208, after too_few fallback): arp/dup 96** (variable_template 67 + legato_variable 29 — heterogeneous
templates, same root as the remaining too_few) + too_few 56 (after_trim 47 + steps 9 — give variable_template under
min_trim) + overlap_diverge 19 (zero-all silence-all ~4 + early ctl/order/freq misc) + length_fail 20 (filter/PW
modulation 5 + bigger shortfalls Tron/Knightrider/Legion = loop/section + Glass_Jaw/Scrilling/Victory small-short) +
build_fail 15 (vibrato/glide too_many_pitches 13) + no_note_voices 2 (pitchless SFX). 1 digi (Black_Box_V8_Demo) → Mode 2.

**✅ PER-FRAME PWM SWEEP-PROGRAM ENGINE (commit f2eaabf, 2026-06-28): 252→253 FULL, Cascading FULL, 0 regr.** The
per-frame PWM cluster is a free-running MODULATION engine (`detect_modulation` best_attempt fallback). The key
correction vs the WIP single-`SweepEnvelope` form: the real signal is a per-voice multi-section sweep PROGRAM (~40
sections/voice, voices INDEPENDENT) — `_capture_pw_program` lifts each voice's PW-hi ($03/$0A/$11) write seq into a
value-table of distinct period bytes + RLE sections `(offset, period_len, repeats)` (a PWM automation orderlist,
ledger C1; dedup via `_find_sub` reuses identical period runs so all 3 voices fit the ≤255 table guard). Player
(masked+legato) = 6502 sweep walker (`_emit_pw_mod_asm`, trampoline `pwm_skip: jmp pwm_done` for the ±127 branch
limit), FRACTIONAL rate (`mod_inc`/256 ticks per play() = BASIC-loop rate not 50Hz, `mod_inc=round(256*pw_writes/
active)`), notes re-timed onto the sweep-tick clock (`on_tick` = cumulative tick count, NOT rho-scaled frames), sweep
emitted BEFORE the note check (orig order [PW][note] — legato calls emit_pw_mod after pl_load), PW stripped from
frames pre-segmentation (parametric, so not re-split into raw sub-steps). USF: `bp_pwprog{vc}_*` params (value-table
4-bytes/int + sections). Cascading FULL (match 10382/10418, all 3 voices, full program matched). Canary added
(portfolio now 17). Methodology that cracked it: divide-and-conquer on the FIRST DIVERGENCE, one cause at a time
(gating→rate→interleaving→write-order→section-varying), each fix a new divergence index. The deleted single-sweep
helpers (`_minimal_period`/`_sweep_from_values`/`_expand_sweep`) were insufficient — a program, not one envelope.
REMAINING modulation tunes (5): per-voice gating + arp (Pong_Strikes_Back, Doom_Comer) or filter-$D416 modulation
(Sullen, Pepper_Spray, Brickout — $16 sweep not yet handled, only PW $03/$0A/$11).

**✅ FILTER-$D416 SWEEP CHANNEL (commit d03434a, 2026-06-29): FOUNDATION, 0 new FULL, 0 regr.** Extended the sweep-program
engine to the filter cutoff $D416 as register-keyed channel 4 (`MODREG={1:$03,2:$0A,3:$11,4:$16}`; the `default_filter`
analog, ledger C1/C10 — a swept $D416 lifts to the sweep-program, NOT hundreds of explicit global_track events = the C7
opaque-dump direction). 3 pieces: (a) INIT-BOUNDARY (`_first_note_frame`) — the init is MULTI-FRAME and interleaves the
sweep's first value(s) with one-time envelope setup, so capture/strip the sweep from the LOOP region only (frames ≥
first-note); the init region keeps its filter writes VERBATIM (flat-matches). (b) MODULATION TAIL (`modtick` counter +
`notesdone`) — a free-running sweep (filter still sweeping after the melody ends) continues past the last note until the
program is fully played (modtick ≥ mod_total), THEN halts. (c) all 3 players unified to emit the sweep at pl_load BEFORE
notes via `_emit_mod_sweep_and_tail` (build_player gained the hooks too — Brickout is masked=False). ADVANCES every filter
tune (Brickout first-div i=3 → i=160, init now matches) but lands NONE alone — each has a distinct orthogonal blocker:
Brickout = short note model (length_fail) + variable-template final section; Sullen = MULTI-RATE channels (filter ticks 4×
faster than V3 PW — single mod_inc clock can't represent it); Pepper/Doom_Comer = release-less-step crash (masked player
record needs off_frame); Pong = too_few. These are the loop/length residue, not filter-specific.

**✅ GAP-EXACTNESS / DRIFT-FREE TIMING (commit 33c12de, 2026-06-29): 253→266 FULL (+13!), 0 regr.** length_fail census
showed a cluster of LONG tunes short by a small amount (exact-prefix). ROOT CAUSE: the USF stored the inter-note gap as
`max(1, nxt-off)` (model_to_usf + usf_to_model both floored). For BACK-TO-BACK notes (gate-off frame == next gate-on,
real gap 0) it forced +1 frame EVERY such step → a PROGRESSIVE timing drift accumulating ~0.6 frame/step → 500+-step
tunes drift past the |len|≤64 tolerance (Bachs: last step 6565→6886, +321 frames), reconstructing on_frames LATE and
dropping the tail. The model was exact; the loss was purely the gap floor. FIX: a `gap_exact` encoding (gmin=0,
lossless on_frame reconstruction), wired as a length_fail-only VERIFY-FALLBACK — best_attempt now runs the whole
fallback chain TWICE (`_try(gap_exact)`: default gap, then gap_exact). FALLBACK not default because a rho-rounding-
COLLAPSED nxt-off=0 is sometimes SPURIOUS (two distinct frames merged) → gap=0 would REORDER same-frame writes; the 3
tunes where that happens (Chromatic_Boogie/Mull_of_Kentyre/Riffraff went FULL→overlap_diverge under unconditional gap=0)
stay FULL via the default and never trigger pass 2. gap_exact COMPOSES with every variant (Barn_Razing needs min_trim +
gap_exact), hence the full second pass. +13 (Bachs/Piano/Minuet/Polonaise/Traitor/Old_Amps/Taking_Steps/Where_I_Want/
Momo_Color/Videobreak_11/Barn_Razing/Dance_of_the_Damned/Allt_Som_Jag). LESSON: a musical-duration round-trip that
sums rounded per-step durations accumulates drift on long tunes — keep the deltas EXACT (allow 0).

**✅ TOO_FEW → min_trim/force_split FALLBACK (commit 9687321, 2026-06-29): 266→278 FULL (+12!), 0 regr.** too_few census
(68): 49 SEGMENT FINE (raw segment 60-600+ steps!) but the AGGRESSIVE trailing-trim drops the HETEROGENEOUS step
sequence below 2 → unsup:too_few_after_trim. min_trim (keep complete differing final steps) often rebuilds them. BUG:
best_attempt only fired its fallbacks on overlap_diverge/length_fail, NEVER on `unsupported:too_few_*` — so min_trim/
force_split were skipped for exactly the tunes needing them. Fix: treat too_few as a built-but-over-trimmed retry
candidate (force_split + min_trim + the gap_exact 2nd pass). ADDITIVE, 0-regression BY CONSTRUCTION (the new branches
fire only on too_few/unsupported results + only return on FULL, so no existing FULL is touched). +12 (Musicale_Demo/
Bright_Eyes/Melodie/Streets_of_Lond/Infinite_Inferno/Missioncode_CX-13/Trail_West/Good_Mourning/Rivers/Robot_Rock/
Tiptoes/Hill_Street_Blues). The remaining too_few (47) give variable_template under min_trim (same root as the
variable_template bucket). NB the batch is now slower (too_few tunes run the full chain ×2 before falling back).

**🔍 RELEASE-LESS-STEP CRASH = PHANTOM (verified 2026-06-29).** The masked-player `off_frame & 0xFF`-on-None crash only
fires in a DIRECT build_model→build_psid shortcut. The real pipeline (best_attempt) ALWAYS round-trips through USF, and
usf_to_model reconstructs gated off_frame as an int (onf+hold) — so build_psid never sees None. No pipeline tune's
status depends on it; do NOT chase it. (The 4 build_fail-no-detail tunes were 2 genuine min()-on-empty = pitchless SFX,
now guarded as `no_note_voices` (commit 52f8c13), + 2 not_clean.) Victory's real blocker is structural: a mixed
gated/held-note tune (196 gate-ons / 54 gate-offs) with a V1-solo final section — forcing legato gives legato_variable.

**✅✅ MULTI-TEMPLATE (ledger C17, commit ecc87ce, 2026-07-02): 278→385 FULL (+107!! 57.2%→79.2%), 0 regr.** The
heterogeneous-template cluster CRACKED by one lever, census-first: of 143 censused residue members, 112 failed on
register-ORDER conflicts (one superset order can't embed all steps) + the rest on release-side dups; K≤16 distinct step
shapes for 137/143. Fix: cluster steps by their EXACT (attack reg-seq, release reg-seq) SHAPE → K POSITIONAL templates
(const/perstep per slot — an intra-step dup is just two slots, so arps/gate-off-groups are free) + per-step template id;
the single template and the masked superset are the K=1 special cases. `build_player_multi` = per-template straight-line
emit blocks + tid dispatch (cmp-chain w/ jmp trampolines); records [on,off,tid,vals] uniform stride. USF: `bp_multi`/
`bp_ntmpl`/`bp_t{t}_atk{i}`/`bp_tid{j}` params (write model only, same precedent as bp_mask); musical content unchanged.
TWO exactness sub-fixes found via Barbs_Boat: (1) HOLD kept exact in multi (a zero-length hold — gate-off in the gate-on
frame — floored to 1 accumulates +1/step drift, the C12 lesson a 3rd time); (2) a per-note RELEASE ctrl ≠ attack_ctrl&$FE
is instrument content (the gate-off WAVEFORM) → carried as `Instrument.waveform[1]`, inst_val(release) reads it. Wired as
a best_attempt verify-fallback (fires only on failure, accepts only FULL → 0-regression by construction; composes with
gap_exact 2nd pass). New FULLs by prior bucket: variable_template 41 / too_few_after_trim 33 / length_fail 12 /
legato_variable 12 / overlap_diverge 9 — ONE lever cut across FIVE buckets. Full regression green.

**✅ MULTI+SPLIT round 2 (2026-07-02): 385→420 FULL (+35, 86.4%), 0 regr.** Residue census (43 multi-failures) showed
28 diverging EARLY on freq regs = intra-step dup FREQ (arp within a step): builds positionally but round-trips WRONG
(one NoteRow pitch per step can't carry two freqs — both dup slots reconstruct the same value). The unsplit multi MODEL
succeeds, so the auto split-fallback never fired → explicit `build_model(multi_template=True, force_split=True)` retry
(res7 in best_attempt; each freq = own sub-step = own NoteRow) + holds exact in ALL multi branches (same-frame split
sub-steps otherwise drift +1). LESSON: a model can be write-stream-complete yet USF-lossy — census the ROUND-TRIP.

**✅ LINEAR-GLIDE LIFT (2026-07-02): 420→431 FULL (+11, 88.7%), 0 regr.** Constant-delta freq runs (>=4 releaseless
same-shape single-voice steps) lift to the head NoteRow + `glide_up/glide_down=$RATE` (REUSED FC vocabulary, C14) +
NEW musical param `glide_ticks=N` (grammar+parser); intermediates = engine mechanism, regenerated at read time
(head_freq + k*delta via the head's C17 template, frames spread over `bp_glide{k}` span) — never enter the 96-slot
alphabet. Chain: res8 = multi+split+glide, res9 = +min_trim (the multi trim ate trailing capture-cut runs).
EXTEND-VERIFY relaxed: (a) fires for play-once rebuilds too (a slow rebuild gets window-cut without looping; a halted
one never grows = can't false-pass); (b) extended verdict gets the same |len|<=64 tail tolerance as the base verdict
(segmentation drops the orig's final capture-cut partial note). NOT handled: interleaved simultaneous multi-voice
glides (Sleepy — steps alternate voices, run rule breaks), exponential/float slides (C_Prog_07), >128 distinct glide
START pitches (In_Your_Head, 144 kept heads).

**✅ GLIDE REST-ROW REFACTOR + interleave (2026-07-02): 431→436 FULL (+5, 89.7%), 0 regr.** Unified scheme replaces
the drop-scheme: members stay ORDINARY steps (own tid/frames/durations) whose gliding-voice row is a REST; the reader
arms per-voice glide state from the head fx and derives member freqs (head + k*delta) at rest-rows whose template
writes that voice's freq. Exact order/frames by construction; INTERLEAVED simultaneous multi-voice glides work
(per-voice run scan skips other voices; Tron FULL 3936/3936 exact); deleted kept-filter/span-params/loop-remap. Plus
segment() now KEEPS the trailing capture-cut partial group (gate-off past window; only min_trim retains downstream) —
was silently dropping final sections (Tron 173 writes). The 11 old drop-scheme .usf regenerated. STRUCTURE CENSUS
(tmp/bp_census_wobble.py, runs/cycles/interleaved coverage per voice): cycle-covered tunes fail for OTHER reasons
(cycles-as-rows do not reduce distinct pitches — no cycle representation needed); the hard tail = float/random freq
tunes (~12: C_Prog examples, Star_Ship, Snaker, Alpine_Escape, Bunny_Hop, Cliffhanger, Dragonwick, Gobblers,
Organ_Torture, Close_Encounters(float vibrato), Dunes(random ramp), Guy_Next_Door) — BASIC float arithmetic not
parametrically reproducible.

**✅ GLIDE ROUND 3: per-voice chains + staircase + kmax (2026-07-02): 436→443 FULL (+7, 91.2%), 0 regr.**
(a) PER-VOICE CHAINS: a step writing several voices' freqs ([V1hi,V2hi] tick) contributes to EACH voice's chain
(candidate for V iff among V's regs it writes only freq; other voices/globals in the step fine) — simultaneous
bundled glides lift (Wood_Steve/Music 2345/2345). (b) STAIRCASE `u_t = u0 + (t//R)*delta` + NEW param `glide_hold=R`.
(c) multi kmax 48→128 (Christmas_Album K>48 → FULL). (d) res9 (min_trim glide retry) fires on ANY non-FULL res8
(alphabet-driven min_trim need, not just length). (e) CAPTURE-RETRY hardening (verify_cycle.writelog_capture +
capture_real retry 3x on rc!=0/empty — parallel-load siddump death read as empty capture, caused phantom verdicts
+ the portfolio flake; ALSO siddump silently returns empty on a WRONG PATH — check paths before debugging "0 writes").
In_Your_Head + Deutschlandlied + Hackers_Rap + Strawberry_Fields + Nightwalker landed too.

**RESIDUE (43): PENDING USER DECISION — 8 no-music-in-window tunes** (Baroque_Music_64, C_Prog_09, God_Save,
Mexican_Hat, Pong, Small_World, Casino_Poker, Hacksville_Hoedown, Sonata): HVSC songlength < the BASIC program's
DATA/setup phase, so the ratified songlength*1.1 window holds only ~9-33 setup writes, no notes. Options: init-only
degenerate FULL (games the metric, encodes silence) / exclude via excluded_sids.json / lift+verify at a longer
window (needs user to amend the ratified window policy). Recommended: exclude or amend.

**✅ PER-TEMPLATE RECORD STRIDE + $D000 IMAGE GUARD (2026-07-02): 443→444 (+1 Arcade_Alley 6996/6996), 0 regr.**
Arcade's 4935 records x padded max-stride crossed $D000 — the player read SID IO as record bytes and SILENTLY stopped
(looked like an early halt at write 6415). Fix: per-template stride (strtab indexed by tid, no pad — glide members
shrink to 6 bytes) + build_psid guard `LOAD+len(body) > $CF00 -> ValueError('image_too_big')` (honest build_fail
instead of silent corruption). Sibling of [[feedback_c64_banking_relocation]]: data tables crossing into IO read
garbage — ALWAYS guard generated-image size. ALSO 2x wrong-path lesson this session: siddump prints 'could not open
file' but the capture layer returns EMPTY (reads as 'SID emits nothing') — VERIFY THE PATH before debugging 0-write
captures (Music_BASIC + Beisikki both under different MUSICIANS dirs than assumed).

**Near-miss diagnoses (recorded, not fixed):** Beisikki (diverge at write 1565/1566: doubled gate-off at the loop
seam — orig's release group differs between loop iterations); Crac_Mur (orig fully reproduced but rebuild loops ~11%
FAST — loop_period too short, timing infidelity, needs loop-seam gap work); both per-tune loop-seam issues.

**✅✅ NO-SILENCE START POLICY (user-ratified 2026-07-02): 444→452 FULL (93.0%), full-family re-lift.** THE POLICY:
every basic_program USF starts its music at frame 0 — NO leading silence, NO `bp_start_frame` field (REMOVED; reader
defaults 0) — structurally uniform with the other engine families for ML training (user: "no silence is best"; evolved
from cap=5 in-session). The BASIC setup dead-air ("PLEASE WAIT" DATA-decode, up to 105s among prior FULLs) is engine
bookkeeping per the init trichotomy, NOT musical content. Mechanism: `semantic_lift.cap_start_frames(model, cap=0)`
applied at MODEL level in `_attempt_model` — pure time translation (all relative timing intact → identical write
stream), `m['start_shift']` records the removed (rho-scaled) frames. VERIFICATION = equal MUSIC-TIME windows: the
rebuild's capture window shrinks by the removed dead-air; CRITICAL rho subtlety (cost 1 false regression,
Curly_Calypso): start_shift is in rho-SCALED model frames — divide by rho to get orig frames BEFORE converting to
seconds, else the window under-shrinks by (1-rho)≈8% of the delay and dense loops overshoot the |len|<=64 tolerance.
`verify_usf` (regression path) estimates the shift from the ORIG capture (first gate-on frame backed over freq-only
frames, in unscaled orig frames) since the USF deliberately carries no delay. AMENDED WINDOW (same round): when the
canonical songlength*1.1 window has ZERO gate-ons (HVSC songlength SHORTER than the BASIC setup phase — the 9
"PLEASE WAIT" tunes; lengths presumably measured by a silence-detector), best_attempt probes a 240s capture for the
real music start and lifts/verifies over [0, music_start + window]. 7 of the 9 landed (Baroque_Music_64,
God_Save_the_King, Mexican_Hat_Dance, Pong, Small_World, Casino_Poker, Sonata; the ear-test mystery SOLVED: the
programs print "PLEASE WAIT 1 2/3 MINUTES" etc. and pre-decode DATA for 1-3 min — SIDs fine, sidplayfp fine, HVSC
songlengths wrong). All 486 re-lifted from scratch (USF content changed family-wide).

**✅ METADATA + INSTR-ON-CHANGE (2026-07-02): user-reported fixes, family re-lifted (452 held).** (a) The original
PSID header title/author/released now transfer into BOTH the USF psid block and the built .sidfinity.sid header
(read_sid_meta; was "probe/x/x"). (b) Instrument refs emit ONLY on change (tracker convention; reader tracks a
running instrument per voice; timbre-only rest rows still resolve via running). Musette (per-note-instr canary) FULL.

**✅ NORMAL FORM STAGE 1 SHIPPED (2026-07-02): 452→455 FULL (93.6%), 260 NF / 195 legacy.** The write model
dissolves into NAMED per-event-type ORDER DECLARATIONS: `bp_order_<sig>: "v1_flo v1_fhi v1_ctrl / v1_ctrl"`
(attack / release) — sig = row-derivable event types per voice (n=note+changed-byte flags hl / n0 re-poke / t=tie /
z=no_release / i=instr-change / g=glide tick / x=timbre-setup / G<regs> globals). WHAT a step writes derives from
rows; every VALUE is musical (pitch/instrument/global track); templates+tids+masks are gone from NF files — the
player's K templates are RE-DERIVED internally (reader: steps → S._multi_templates). Params grammar gained STRING
values (shared schema; packing into ints was the §3 failure). Writer computes sigs alongside rows and raises
nf_conflict on any non-derivable case (same-sig different order, re-poked unchanged global, release timbre beyond
gate-off, rel-only voices) → chain falls back to legacy forms (coverage cannot regress; NF attempts run FIRST:
_try_nf(False) → legacy chain → _try_nf(True)). KEY SYMMETRY LESSONS: (1) timbre-setup rest rows must ALWAYS carry
their instrument ref (an unchanged-instr re-poke is otherwise row-invisible) and 'x' sigs carry no i-flag; (2) NF
instruments absorb ALL written timbre (const+perstep incl. gate values + release ctrl as waveform[1]); (3) sig keys
join with __ (CNAME-safe). tie/no_release fx mark gateless/releaseless notes (existing vocabulary).
STAGE 2-4 REMAIN: init→typed init.sid priming (trichotomy verdict), merged rest rows + union-onset step grid (user
point B), loop seam-gap extension (kill bp_loop_period), rho→composer, sweeps→typed C1 form, legacy-tune census.

**(superseded plan note)** The user flagged the params block as
anti-ML (packed ints) — review confirmed it is representation-principle §3 FAILURE MODE B (the USF carrying a
per-tune engine program; "complete but unlearnable"). DERIVABILITY CENSUS (tmp/bp_census_derivable.py, 277 FULLs):
Q1 79% of tunes have a perfect unordered-writes→order function (templates+tids fully derivable from rows; the 50
conflicted tunes are glide/legato where the crude signature conflates event types — row-aware signatures will raise
this). Q2 ordering vocabulary small per tune → residue = NAMED per-event-type order declarations (C16 knob shape).
Q3 82% of inits decompose into reset (composer universal) + EXISTING typed init.sid priming (master_vol/
envelope_prime/filter/pw_init); remainder = ctrl_prime + freq_seed → typed priming siblings. Q4 loop_period ≈
row-span + seam gap → extend the final rest to cover the seam, then Orderlist.loop_to alone carries the loop.
ROW-AWARE CENSUS (tmp/bp_census_rowaware.py, all 452): 82% (371) fully order-derivable; median 3 order
declarations/tune (max 60); 81 tunes have same-event-type order conflicts (likely per-SECTION poke-loop changes —
candidate scopes: per-pattern order declarations, or keep C17 templates for just those). With a corpus-default
order, typical tunes need ~0-3 named declarations = FC-knob scale.
PLAN: rows become true tracker rows (note+duration, ONE merged rest between events — the user-approved B); step
grid derived from union of event onsets + row-aware event types; init→init.sid via trichotomy verification; sweeps
→ typed C1 forms; rho/reset → composer. End state: basic USFs structurally identical to FC/DMC (psid + small named
params + init.sid + instruments + patterns).

**RESIDUE (rest):** variable_template 16 + build_fail 15 (mostly too_many_pitches = vibrato >96 freq slots) +
too_few_steps 9 + legato_variable 8 (incl. Chicken_Song/Argument_Emulator/Dunes = Bond_Alan vibrato-heavy) +
overlap_diverge 8 (Deutschlandlied close m=1672/1678; Crazy_Conveyors/Dark_Tower/Escape_from_Death early) +
too_few_after_trim 5 + length_fail 3 + no_note_voices 2 + 1 digi (Black_Box_V8_Demo → Mode 2).

**NEXT:** (1) too_many_pitches ~19 incl. build_fail + several *_variable (vibrato >96 distinct freqs — needs a
glide/vibrato effect representation, the largest remaining coherent bucket); (2) too_few_steps 9 (degenerate/short
segmentation); (3) the early-diverge misc tail. Iterate via `family_batch.py` (resumes from OUT jsonl).
METHOD THAT WORKS: census a bucket for a SHARED lever (multi-template +107, multi+split +35, gap-exactness +13).

**CONVERGENCE (ledger C10, 2026-06-27):** the `global_track` is the EXPLICIT-event form of chip-global $D415-$D418
automation; the OTHER engines already represent the same registers PARAMETRICALLY (`MasterVolConfig` fade formula,
`FilterProgConfig`/`default_filter`/`filter_env` programs, `init.sid.filter`) — do NOT convert those to global_track
(that's the C7 opaque-dump direction; Confuzion's fade = 2 knobs, not hundreds of dyn events). Choose by musical
STRUCTURE (parametric = mechanism+knobs the engine generates; explicit = arbitrary authored data, the trace-lift
case), same axis as NoteRow vs VibratoConfig. Move-1 TODOs in C10: make global_track a SHARED primitive; consider a
sweep-detecting lift so basic_program's parametric sweeps (Moog_Swing cutoff = 190 explicit events for a sawtooth)
become filter-programs. Not a rewrite-the-FULLs task.
