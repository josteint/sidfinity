---
name: project_basic_program
description: "Basic_Program family (486 RSID-BASIC tunes) — research done, capture unblocked, Twinkle proof FULL"
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
triangle instrument, init) → write+reparse a real `.usf` (USF v2) → build a MINIMAL DEDICATED
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
MUSICAL (maps to USF v2 instruments/master_vol/etc.) -> the principled fix is a SEMANTIC richer lift
into existing USF v2 (NOT generic per-step register-deltas = the [[feedback_no_writelog_replay]] trap,
NOT a bytes escape-hatch). Reuse deprecated `gt2_pipeline/converters/regtrace_to_usf.py` (~80% of the
lift algorithm: freq_to_note_pal, gate-transition note boundaries, tempo). **PORT CAVEAT (user, do not
forget): the old regtrace_to_usf consumes per-frame SNAPSHOTS (Trap A — loses within-frame order +
can't model the things we need); the port MUST consume the `--writelog` ordered (reg,val) stream
instead.** Probe failure buckets: overlap_diverge 42 / lift_crash 16 / build_fail 6 (branch-out-of-range
= the +-127 trampoline bug) / lift_no_gate 4 (legato gate-once + GET) / too_many_steps 4 (N>255, 8-bit
stepidx) / length_fail 1. Cheap wins in progress: branch trampolines + 16-bit step indexing.

**NEXT (build the family, not yet done):** the 1 digi tune (Black_Box_V8_Demo, Mode 2 cycle-exact);
fold the proof scripts into proper `pipelines/basic_program/{extract,build,verify}` + wire the
`verdict_basic` duration_tol comparator + a regression portfolio; then a stratified-subset batch over
the 486 (the lift handles single + multi-voice chord-per-step; remaining variants: Ahoy-style legato
where gate stays on + freq-only changes, independent per-voice timing, SYS-to-ML hybrids). Survey raw:
`tmp/basic_program_research/survey.jsonl`.
