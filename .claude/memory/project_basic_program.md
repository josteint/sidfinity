---
name: project_basic_program
description: "Basic_Program family (486 RSID-BASIC tunes) — PRODUCTIONIZED round-trip: 224/486 (46.1%) FULL through real USF, mass-written + regression"
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

**RESIDUE (262, not_clean ELIMINATED): arp/dup 96** (variable_template 67 + legato_variable 29 — precedence cycles +
deeper variants) + too_few 68 (after_trim 59 + steps 9) + length_fail 42 (loop-period; +8 ex-not_clean) +
overlap_diverge 36 (+6 ex-not_clean) + build_fail 20 (vibrato too_many_pitches + partial-freq stragglers; +5
ex-not_clean). 1 digi (Black_Box_V8_Demo) → Mode 2.

**NEXT (highest-leverage first):** (1) length_fail loop-period (42 — overlap-EXACT but length off; loop-detect
misses + window boundary). (2) the arp/dup 96 (precedence cycles + split-then-still-variable). (3) overlap_diverge
36 + partial-freq stragglers (Glass_Jaw/Interlace). (4) too_few 68 (degenerate/short). (5) vibrato too_many_pitches
(freq alphabet >96). Iterate via `family_batch.py` (resumes from the OUT jsonl; delete to force clean). Survey raw:
`tmp/basic_program_research/survey.jsonl`.

**CONVERGENCE (ledger C10, 2026-06-27):** the `global_track` is the EXPLICIT-event form of chip-global $D415-$D418
automation; the OTHER engines already represent the same registers PARAMETRICALLY (`MasterVolConfig` fade formula,
`FilterProgConfig`/`default_filter`/`filter_env` programs, `init.sid.filter`) — do NOT convert those to global_track
(that's the C7 opaque-dump direction; Confuzion's fade = 2 knobs, not hundreds of dyn events). Choose by musical
STRUCTURE (parametric = mechanism+knobs the engine generates; explicit = arbitrary authored data, the trace-lift
case), same axis as NoteRow vs VibratoConfig. Move-1 TODOs in C10: make global_track a SHARED primitive; consider a
sweep-detecting lift so basic_program's parametric sweeps (Moog_Swing cutoff = 190 explicit events for a sawtooth)
become filter-programs. Not a rewrite-the-FULLs task.
