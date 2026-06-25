---
name: project_basic_program
description: "Basic_Program family (486 RSID-BASIC tunes) — PRODUCTIONIZED round-trip: 163/486 (33.5%) FULL through real USF, mass-written + regression"
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

**RESIDUE (323, by dependency order — all are LIFT limits or richer-musical, NOT round-trip-encoding):**
build_model DECLINES for ~half: unsup_variable_template 134 + unsup_legato_variable 52 = 186, of which
**172 are true ARPEGGIO** (intra-step register repeat: a reg POKEd ≥2× per step = a fast freq run inside one
note; `_union_order` is register-keyed so can't represent repeats — needs POSITIONAL template matching) +
**14 precedence cycles** + too_few_after_trim 32 + too_few_steps 20 (degenerate/short). Round-trip-clean but
failing: length_fail **19** (the SECOND loop sub-problem — loop NOT detected or loop_period slightly off; ~17
short, 2 overshoot e.g. Crac_Mur/Cave_of_the_Ice_Ape) + overlap_diverge 36 (23 diverge in first 10% =
structural; 6 are >90% near-misses) + not_clean 27 (RICHER FULL — perstep non-freq like per-note vol/ADSR;
USF NoteRow can't carry → needs a dynamics/instrument-param representation) + build_fail 3. 1 digi
(Black_Box_V8_Demo) → Mode 2.

**NEXT (highest-leverage first):** (1) length_fail loop-period/detection (19, the residual loop sub-problem
after the clock fix — mostly `_find_loop` missing the period or computing it slightly wrong; some genuinely
degenerate). (2) ARPEGGIO/dup_reg (172) — the variable-length intra-step freq sequence; biggest single lever,
needs positional (not register-keyed) template matching = a real design step. (3) not_clean richer-FULL (27 —
map perstep $D418→dynamics / per-note ADSR→instrument). Iterate via `family_batch.py` (resumable, `--write` to
mass-write); per-cause probes live in `tmp/` (lf_probe / lf_timeline / lf_clockfix). Survey raw:
`tmp/basic_program_research/survey.jsonl`.
