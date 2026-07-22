---
name: project_goattracker
description: "GoatTracker family migration — V1 (original 1.x) is the active target; extract + composer in pipelines/goattracker/v1/. Current status = the STATUS section at the head of the body (+ MEMORY.md line). Tail sections are the old research/plan phase — superseded, kept as RE reference."
metadata: 
  node_type: memory
  type: project
  originSessionId: c0742216-af17-42da-9a5c-fa8ae0d40172
  modified: 2026-07-22T14:50:40.332Z
---

## STATUS (head — newest wins; update THIS section, prepend new rounds here)

**2026-07-22 — V1's USF ROUND TRIP WAS BROKEN AND IS NOW FIXED.** The V1
extract emitted three things the GRAMMAR could not read back, so every `.usf`
it wrote was unparseable and the family had no round trip at all:

  * list-valued `params` (`filt_init`, `funk`) — the writer emitted
    `[0, 128, 15, 0, 0]` via `str(val)` with no matching `param_value` rule;
  * `loop: -1`, V1's wave-program STOP sentinel (grammar took only `INT`);
  * the whole per-row command vocabulary (`arp=X,Y,S`, `vibrato=X,Y`,
    `fcutadd=`, `fctrl=`, `keyoff`) — `to_usf.py` even says "grammar extension
    pending", because the V1 composer reads the in-memory model, so nothing
    ever exercised the parse side.

Fixed in the grammar/parser/writer (ledger C14 for the row commands). V1's one
stored `.usf` now parses and is round-trip stable (730 rows, params/loops/flags
preserved). NOTE this means the earlier 164/1359 batch verdict never went
through USF — when V1 work resumes, re-run the batch through the USF path
before trusting it, and wire V1 into `regression.py` (still absent, which is
why this stayed invisible).

**2026-07-16:** V1 extract + composer BUILT (`pipelines/goattracker/v1/`);
authoritative wide batch **164/1359 FULL** incl. the player1 `optimized`
write-order knob (ledger C16, commit 3f20ab5). The optimized variant needs a
dedicated engine BODY (shared USF + variant extract done; variant composer
body TODO). Everything below this section is the historical log.

GoatTracker = 2nd-largest HVSC family after DMC: **8,670 SIDs** (7,311 V2 +
1,359 V1). Family-doc state `OK`. **Active focus: V1** (the *original*
GoatTracker 1.x by Cadaver, NOT GoatTracker 2 — user-directed 2026-06-29).

**⛔ POLICY OVERRIDE (user, 2026-07-01) — supersedes every C15/audio-equivalence
mention below:** every SID always gets the STRICT write-stream match; ledger C15
is REMOVED (design parked in `docs/the_move-1_plan.md`, Move-1-era-only —
never propose it during per-engine work). The V1 idle-freewheel partials must be
solved by REPRODUCING the idle writes (the core tenet permits reproducing the
mechanism; the composer — not USF — may carry/derive the idle state). References
to "re-verify under audio-equivalence" below are void.

**Status: ✅ 2 tunes FULLY CONVERGED (Topaz/Joker + Dexter/Menace47, instruction-
sequence-exact at full songlength). Working V1.5 engine + full SID→USF→SID
pipeline.** Imdunk at 18%. KEY fixes this session (each high-leverage):
- wave-program `$FF`-marker note-target byte 0 = STOP (waveptr→0), NOT loop —
  after stop the continuous fx runs, so a legato toneporta SLIDES
  (speed=param<<2). `parse_wave_program` tgt==0 → loop_to=-1; composer marker
  wnote=0. (This converged the canary fully.)
- porta carry: `clc` before freqadd / `sec` before freqsub (freqsub's sbc needs
  carry set; portadown was off by 1). (→ Menace47 FULL.)
- full filter table emission (engine steps it; was a 4-byte placeholder).
- per-player freq table (extract 128 entries incl. C6 off-table window).

**⚠️ VARIANT LANDSCAPE — the dominant non-V1.5 variant is the OPTIMIZED-LAYOUT
sub-version, NOT just "no delayed-wave".** In a 42-tune load-$1000 sample only
~8 are the V1.5 (delayed-wave, normal-layout) variant my engine handles; ~34 are
the optimized layout (`player_variables.md` "Optimized Variable Layout", used
when NOWAVEDELAY + other flags) — a substantially different player: different
channel-var positions, init sets chntick=TEMPO (not gt+2 → different first-row
write-stream TIMING), and a different gate-check + setfiltersub structure. They
fail MULTIPLE detection anchors (filttbl `A8 B9 ?? ?? F0`, gatetimer
`A9 ?? 9D ?? ?? A9 ?? 9D ?? ?? A9 FF`, some wavetbl). Rep: DEMOS/A-F/Alive.sid. **DECISIVELY a SUB-ENGINE, not a knob** (RE'd its full
play loop — see RE_NOTES §11). Confirmed differences vs V1.5: no-delay wave-exec;
different channel-var layout THROUGHOUT; init chntick=TEMPO (not gt+2); gate via a
`$13f7` HR-countdown (set to gt on new-note: `lsr; lda #gt; sta hrflag,x; bcs`;
NOT chntick==gatetimer); different hard restart (NO `hr_sr` write). Decoded
values for Alive: filttbl=$15c7, gatetimer=2, tempo=5, setfiltersub @ $1315.
DONE this session toward it (all V1.5-safe, committed): dual wavetbl anchor
(`C9 08` OR `F0 03 9D`) + `nowavedelay` prologue; optimized gatetimer anchor
(`4A A9 <gt> 9D ?? ?? B0`) + tempo (double-store init) + `inittick_is_tempo`
composer knob; tolerant hr_ad/hr_sr. CONCLUSION (corrected framing — re-ran CORE TENET): the optimized variant is a
VARIANT EXTRACTION PATH + shared composer + knobs, NOT a separate engine. The
composer reproduces the WRITE STREAM with its own layout-agnostic engine, so the
original's internal differences (channel layout, init, pattern/instr ENCODING)
only affect the EXTRACTOR (reading the binary into the engine-neutral USF). It's
the SAME tracker → one USF model + one composer (USF principle; cf. DMC
family-1/2 = variant extract + knobs). Write-stream knobs: `inittick=tempo`
(added) + `$13f7`/no-`hr_sr` HR (verify). EXTRACTION fixes needed: (1) song/patt
pair assignment — code-order is REVERSED vs V1.5; use the DIFF rule (song hi-lo
== 3*nsubtunes) — IN PROGRESS; (2) re-derive instrument-extent + pattern/instr
decode for the optimized layout. Clean-reject guard kept (`extract` raises 'wave
runaway' when no $FF terminator in 256 steps). V1.5-safe pieces KEPT (Joker +
Menace47 FULL). RE groundwork in RE_NOTES §11.

**✅ EXTRACTION PATH DONE (this turn): the song/patt diff-rule unblocked the
optimized variant** — in the 42-tune sample, extract-OK jumped 8→18, of which
**10 are the optimized variant**, now extracting cleanly into the shared USF
model (proves: extraction-variant + shared composer, not a separate engine).
Remaining detect-errs: filttbl(20)/wavetbl(4) = FURTHER layout sub-variants
(more anchors needed). **COMPOSER KNOBS needed to converge the optimized write
stream (characterized from Alive frames, NOT yet implemented):** (1) filter is
EVENT-DRIVEN — written only via setfiltersub (init + new-note instfilter + cmd5
+ program step), NOT a per-frame exec (V1.5 writes $16/$17/$18 every frame; Alive
writes $15/$17/$18 once at f0, never again); (2) per-voice write ORDER is
loadregs(freq/ctrl 00/01/04) BEFORE pulse(02/03) — V1.5 does pulse before
loadregs; (3) the $13f7/no-hr_sr hard restart; (4) inittick=tempo (done). These
restructure the engine's per-frame write sequence → conditional engine sections,
multi-cycle build+diff.

**COMPOSER KNOBS — progress (commit 8bf0118):** (1) ✅ filter-event-driven LANDED
— `_engine` branches on `t.optimized`: setfilter writes $D416/$D417/$D418
directly (sf_d417/d418/d416), per-frame filter exec skipped, init writes filter
once via setfilter(0). Alive's per-frame filter writes gone; V1.5 unchanged
(Joker+Menace47 FULL). REMAINING (each a build/diff cycle, all on Alive, div now
at pos 0 = init timing): (2) init must PLAY MUSIC on f0 — orig f0 already loads
all 3 voices' freq/pulse/ctrl (no silent deferred-init frame), but mine's f0 is
silent (deferred init `jmp loadregs`), so mine is ~1 frame behind + pulse not yet
running. Needs the optimized init to fetch+load the first note in the first
play() (structural). (3) per-voice order loadregs(00/01/04)-before-pulse(02/03).
(4) $13f7/no-hr_sr hard restart. The optimized COMPOSITION is a multi-cycle
structural phase (≈ a 2nd engine body selected by knobs); 1 of ~4 knobs landed.

**⚠️ REVISED SCOPE (this turn, deeper probe of Alive): the optimized COMPOSITION
is NOT a few knobs — it needs a variant ENGINE BODY (like DMC v5), reading the
shared USF.** The EXTRACTION genuinely shares the USF model (10 tunes extract;
song/patt assignment VERIFIED correct — orderlists at the 3-entry table hold real
pattern numbers, patterns at the 18-entry table). But building Alive with the
shared V1.5 body + knobs produces SILENCE — the note/freq path doesn't work.
THREE layered causes found (each its own RE): (1) **resting-voice idle-wave
freewheel** — orig f0 has all voices freq-set (00=6d) but ctrl=$00 (ungated/
silent); the patterns genuinely START WITH RESTS (`5f 00 00`), so the f0 freqs
are a RESTING voice running its wave program (DMC `idle_wave` analog), not played
notes. Mine leaves resting voices at freq 0. (2) **1-based filttbl init** — GT
filttbl ptr 0 = the OFF entry, so my setfilter(0) reads the off-entry → $D418=$00
(orig $0f from a 1-based entry); the init filter ptr is NOT 0. (3) init plays
music on f0 (no silent deferred-init frame) + per-voice loadregs-before-pulse +
$13f7 HR. CONCLUSION: treat the optimized variant as a DEDICATED future
engine-body migration (shared USF + variant extract DONE; variant composer body
TODO) — not a continuation. KEPT this turn (all V1.5-safe, Joker+Menace47 FULL):
filter-event-driven knob + sf_d418 direct-write (no & volmask). Optimized tunes
currently build as div-0 partials (accurate WIP, not false-FULL).
THEN (V1.5 path): Imdunk's
gate/note tail (voice3 ctrl $20 gate-off vs $21), grammar ext arp/vibrato fx,
relocation factory, wide batch. Quick batch: tmp/v1_sample.txt + `v1/verify.py`.

**📊 80-TUNE COVERAGE TRIAGE (this turn, tmp/v1_batch.py — random sample, capped
durations so noDiv=provisional-FULL not a songlength verdict): partial 41 / extract_err
35 / noDiv 4 / (optimized-in-sample 14).** Two dominant levers:

**LEVER 1 — freqlo partials (23, the dominant partial role) = RESTING/IDLE-VOICE
WAVE FREEWHEEL (confirmed root, this turn).** The GT analog of DMC `idle_wave`
(project_dmc already solved this class). DISCRIMINATOR: Joker/Menace47 (FULL) have
a REAL NOTE in their first pattern row → mine loads it → converges; Memoires/Bomdibom
(partial) start with a KEYOFF ($5e/note94) or rest → orig FREEWHEELS `freqtbl[curnote]`
(Memoires v1 = freqtbl[60]=$22d0, ungated ctrl=$00) while MINE leaves resting freq=0.
Confirmed NOT an orderlist off-by (songtbl/orderlist-start bytes verified correct,
patt6 genuinely first & genuinely a keyoff). TODO: RE what init sets curnote to
(orig v1 idles at note60=C5 — likely a fixed editor default; v3 idles at $2e1e which
is NOT a clean freqtbl entry, so curnote default may be per-voice or note-derived —
needs the wave-program freewheel mechanism nailed) + run the wave program for
gate-off/resting voices. This is the SAME root as the optimized-Alive silence →
fixing it helps BOTH paths. HIGHEST LEVERAGE (also flips the unblocked extract_err
tunes once detection widens).

**✅ RESOLVED via principled re-anchor — idle_chip REVERTED (bb7b097); audio-equivalence
verdict DESIGNED+VALIDATED but DEFERRED → ledger C15.** The idle freewheel writes are
INAUDIBLE (idle voice = ctrl=$00/no-waveform; pre-load is overwritten before it sounds)
= trichotomy §4.4 engine bookkeeping, NOT musical → carrying them (idle_chip: extract
chnfreq/pulse from `chnfreq_base+v` → params → BSS) is C7 anti-pattern + INSUFFICIENT
(a sync/ringmod-source idle voice's freq IS audible & freewheels — a constant pre-load
can't reproduce it). RIGHT answer = **audio-equivalence verdict** (drop freq/pulse
writes while `(ctrl&$F0)==0`, with the sync/ringmod guard: keep a silent source's freq
if consumer `(N+1)%3` syncs/ringmods). Validated: Bomdibom→FULL w/o idle_chip;
Joker/Menace47 no regression; Drrsh real bug still caught; the guard caught Memoires
(uses sync) as a naive-filter FALSE PASS. DEFERRED (user choice B, 2026-06-29): small
immediate coverage (+1 / 60-sample — most strict-partials have REAL audible bugs under
the idle noise) and it changes the sacred verdict; not worth it for +1 now. **Until
adopted: idle-divergent tunes are an "audio-identical / strict-partial" residue class
— re-verify under audio-equivalence before counting as real partials.** Full record +
hardened filter spec + edge cases in ledger C15. DMC `idle_wave`/resting-voice is the
SAME class — re-examine there too. KEY LESSON (kept): residue tunes have MULTIPLE
STACKED divergences (idle-freq → pulse-mod → real-bug) — fixing the idle layer only
exposes the next genuine bug, doesn't flip FULL alone.

**LEVER 2 — extract anchors. ✅ EXTRACT 57.1%→65.0% this session (+108 OK / 1359),
4 commits** (full census `tmp/v1_extract_census.py` over all 1359 drove it):
- wavetbl variant-3 (d5a030c): no-delay build writes $D404 DIRECTLY in wave-exec
  `B9 ?? ?? F0 06 9D ?? ?? 9D 04 D4` (sta $D404,x disambiguates from +3 form).
- filttbl direct-write (d5a030c): `A8 B9 ?? ?? 8D 17 D4` (setfiltersub writes $D417
  every call, no beq) → +73 OK.
- songtbl/patttbl ZP-generalized (3e8fa12): the ptr-load `lda LO,y;sta zp;lda HI,y;
  sta zp+1` uses a build-varying ZP ($FC/$FD canonical; $AA/$AB, $40/$41, $D6/$D7) →
  wildcard ZP, require consecutive stores, keep the 3*nsubtunes diff-rule. 43→1.
- pattern-walk bound (f814452): clean reject instead of IndexError crash.
**REMAINING extract buckets (475 fail): filttbl 413 + gatetimer 30 + pattern-overran
20 + instrument-cluster 10.** The BIG one (filttbl 413) is **IDENTIFIED: it's PLAYER2 = Cadaver's gamemusic-mode
routine** (full source `pipelines/goattracker/docs/src/v1_player2_125.s`; 374/413 match, rest=2SID/other).
NOT byte-RE — documented player. Detector: global SMC filter sweep `A9 ?? 69 ?? 8D ??
?? 8D 16 D4` (+ direct-$D404 wave-exec). SHARED format w/ player1 (8-byte instruments,
wavetbl/notetbl, songtbl/patttbl, pattern format) → reuse extractors. DIFFERS: NO
filttbl (filter is GLOBAL SMC sweep + per-instrument `instfilter` byte = cutoff+type;
global cutoff sweep = ledger C10 chip-global automation); command semantics differ
(2=SETCUTOFFADD not porta-down, 6=SETSUSTAIN not SR); direct $D404; entries init/play/
setvolume/playsfx (SFX+setvolume game-only → IGNORE for PSID). Full RE + migration plan
in RE_NOTES §12. MIGRATION = variant extraction branch (modest — most tables shared) +
a player2 composer body (the lift) selected by a `player='gamemusic'` knob; USF model
SHARED. Single biggest V1 lever (~374 tunes), multi-step sub-project.

**✅ PLAYER2 EXTRACTOR BRANCH LANDED (d7f8800) → EXTRACTION 57.1%→90.0% this session
(+466 OK / 1359).** `Layout.player='tracker'|'gamemusic'`; detect via SMC filter-sweep
anchor; for player2 skip filttbl + gatetimer and resolve song/patt by player2's loads
(PATT=85-zp getnewnotes pair; SONG=init per-channel address store `B9 ?? ?? 9D ?? ?? B9
?? ?? 9D` with diff==3*nsubtunes). +338 player2 tunes read into V1Song. Sample split:
~26% gamemusic / ~74% tracker. Joker+Menace47 still 'tracker'+FULL (no detector
collision — player1 filter uses zp A5/65/85, not SMC immediates). **READ path only.**
REMAINING extract residue (136): filttbl 39 (2SID/other), gatetimer 30 (player1 gt
variant), pattern-overran 30 + IndexError 17 (wrong/edge detection), instrument-cluster
10, songtbl/patttbl 7, wave-runaway 3. **NEXT = player2 COMPOSE (the lift for FULL):**
(1) ✅ to_usf player2 command map DONE (d47d5ef): params['player']='tracker'|
'gamemusic'; player2 cmds 2→fcutadd (global cutoff sweep), 5→fctrl ($D417), 6→srr,
1→signed glide; arp/porta/vibrato/tempo shared. Global filter fully captured by the
per-row cmds + per-inst instfilter (no separate C10 track). Validated 66 p2+206 p1
to_usf, 0 crashes. (2) ✅ player-aware pattern
ENCODER done (c57a402: _fx_to_cmd/_encode_pattern/_Tables.player — player2 cmd1
signed-porta/cmd2 fcutadd/cmd5 fctrl; byte format shared). (3) STILL TODO — the
**`_engine_v2` asm body** selected by `t.player=='gamemusic'`. FULLY SPEC'd in
RE_NOTES §12b (routine-by-routine): REUSE V1.5 sequencer/getnewnotes/arpeggio/
makespeed/freqadd-sub/toneporta/pulseexec (read our shared layout); CHANGE 6 player2
behaviors — note-fetch at tick0 (no gatetimer), simpler filter sweep ($D418=filttype|
vol), cmd2=setcutoffadd/cmd5=setfilter-global, wave-exec writes $D404 direct (split
freq/pulse), immediate HR + instfilter→global filter, init. It's a multi-turn bring-up
(core play-model timing differs) → write the routines + converge a canary (Faderik)
via find_first_divergence. Until done, player2 tunes EXTRACT+to_usf but don't compose
(not FULL). ~374 tunes ride on it.

**✅ _engine_v2 WRITTEN + BUILDS + RUNS (75a9e55)** — clean port of player2's play
routine, dispatched by `t.player=='gamemusic'`. Faderik builds; global filter sweep +
play model correct; player1 unaffected. REMAINING = the strict idle-prefix
reproduction (C15 phase gate: player2 doesn't reset phase → idle freq audible → must
reproduce, NOT audio-equivalence — confirmed via test-bit; see ledger C15). **Idle
state located** (RE_NOTES §12c): chnnote block via notetbl-anchor **+7** operand,
chnwave block via `BD ?? ?? 29 FE 9D 04 D4` +1. The idle freewheel = the engine running
the PRE-LOADED continuous effect (arp/porta) on the pre-loaded note (Faderik v1: arp
cdat=$0c on note $41). Init zeros chnwavetbl/chnpulsedir/chnsongptr, KEEPS chnnote/
chnfreq/chncommand/chncmddata/chnarpcount/chnvibcount/chnpulse. FINISH = emit idle
priming + diff-converge. **✅ CRACKED via pc-trace (RE_NOTES §12d) — NOT an impasse;
the earlier "no pc-trace file" was just siddump off PATH.** Faderik's player2 is a
SUB-VERSION of v1_player2_125.s differing in per-frame EMISSION STRUCTURE (C16). The
pc-trace shows: (1) arpfreq writes freq → nextchn (NO loadpulse after); (2) pulse
written in the pulse-MOD path BEFORE freq, conditional (skipped on the sequencer
frame, carry-set) → per-frame order pulse-THEN-freq, and freq-without-pulse on f1;
(3) per-player freq table (Faderik freqtbl[65]=$2e38≠standard $2e79) — player2's
arpfreq has an EXTRA `9D $d400` so the existing arpfreq anchor misses it. **3 FIXES TO
CONVERGE (all understood): (a) player2 freq-table anchor `B9 ?? ?? 9D ?? ?? 9D ?? ??
B9 ?? ?? 9D`; (b) C16 emission restructure — pulse-in-mod-before-freq, arpfreq/
continuous-fx → nextchn (no loadpulse-always); (c) idle priming (emit chnnote/
chncommand/chncmddata/chnarpcount).** All 3 needed before f1 converges (first div =
idle freq). Tractable convergence, not RE. TOOL LESSON: pc-trace needs env.sh/full
path; it's the unlock for player2 — don't conclude "impasse" from a PATH error.

**✅ FIXES (a)(b)(c) LANDED (commit 1de261a) → Faderik div 3→12 — f1 (idle freewheel)
+ v1 FULLY CONVERGE.** subA emission knob `p2_pulse_in_mod`; idle priming emits per-
voice kept state incl INSTNUM from the 2 block bases (chnnote_base = notetbl-anchor+7;
chnwave_base = `BD ?? ?? 29 FE 9D 04 D4`+1). Player1 still FULL. **LAST BLOCKER
(div@12, v2 pulse, RE_NOTES §12e): subA's pulse MODEL differs — `chnpulsedir` is the
free-running pulse accumulator (+= instpulsespd, wraps; v2 $01→$41→$81→$c1), pre-loaded
& NOT zeroed by init (subB zeroes it + uses chnpulse bounded). To finish: emit
chnpulsedir in idle priming (chnwave+3) + DON'T zero it in pi_loop for subA + a subA
pulse-mod variant (accumulate chnpulsedir += instpulsespd, write chnpulsedir; dir-flip
logic TBD from a wider trace). Then v2/v3 pulse match → f2 converges. The subA pulse-mod
is the final structural piece for the player2 majority.

**✅ UPDATE — subA pulse RESOLVED via chninstnum>>3 (commit ae9dd66) → Faderik div
12→58 (f1-f5 converge).** The pulse value was wrong because player2 stores chninstnum
as inst*8 (interleaved byte offset; pc-trace v2=$10→instpulsespd[$10]=inst-2's field)
while OUR engine stores the inst INDEX (lsr×3 on note-load) → idle chninstnum must be
>>3, else it reads the wrong instrument's pulsespd. (NOT a separate-arrays layout —
instruments ARE interleaved; chninstnum is just the *8 offset.)

**✅✅ FADERIK (player2/gamemusic CANARY) IS FULL (2026-06-30) — instruction-sequence-
exact at full songlength; Joker (player1) still FULL.** div 3 → FULL across the session
via 8 fixes. The tick-theory was a RED HERRING (chntick=5 is correct, DEF-1 overshot —
don't re-chase the init tick). The REAL chain of fixes (mine-vs-orig pc-trace of the
note-load was the cracking tool, `tools/siddump SID --pc-trace FILE A B --frames N`):
1. per-player freq table; 2. subA emission (pulse-in-mod); 3. idle priming; 4.
chninstnum>>3 (index vs inst*8). Then the structural ones (commits f4bc81e + 2b2718b):
5. **tick0-defer**: ALL tick0 cmd handlers `jmp nextchn` (NOT effects2) — orig's tick0
cmds all go cmddonothing→nextchn, so the hard-restart/gate-off frame writes no pulse/freq
and newnoteinit is deferred ONE play(). 6. **ADSR-init instwave POINTER**: ctrl=wctrl
[instwave] (orig X-swap: stx temp1; tax; lda wctrl,x; ldx temp1 — keeps Y=chninstnum for
instad/instsr), and `ef_skipwavetbl: jmp ew_skipwave` (run the wave program for freq, NOT
jmp loadpulse). 7. **ctrl-FIRST order** (orig: ctrl,AD,SR). 8. **packed-rest re-dispatch**:
`gp_cont: ldy chncommand; jmp gn_rest` (orig mt_packedrest→mt_rest) so a held SETSUSTAIN
keeps re-applying SR each rest row. KEY player2 mechanism learned: **the tick0 (note-fetch)
frame does hard-restart (AD=0/SR=0/gate-off) + cmd-tick0-action then nextchn — the note's
pulse (newnoteinit) is +1 frame, gate-on/freq (ADSR-init) is +2 frames.**

**PLAYER2 FAMILY RESIDUE (next work):** GT V1 = 1359 (884 player1 + 339 player2 +136
detect_fail). **⚠️ VERIFY-BUG CORRECTION:** `verify(duration=None)` passed `--duration
None` to siddump → captured ZERO frames → vacuous `is_full=True` FALSE PASS. Earlier
session "Improper FULL", "Lovin_SID FULL", "39/40", "18/45" numbers were ALL bogus
(0-frame). FIXED (commit 6dbdaba): verify(duration=None) now looks up HVSC `songlength_s`
and captures songlength×1.1. **TRUE state (songlength-based, capped 75s): ~3/30 player2
FULL (~10%).** ALWAYS verify with a real duration — NEVER duration=None pre-fix, NEVER
arbitrary 12s (overshoots short songs into post-song divergence; the 12s "10→18" was also
misleading). Faderik + Joker genuinely FULL (confirmed via real captures).
Two REAL fixes this session (progress, NOT full for those tunes):
- **init test-bit ctrl (commit f1ba30f):** deferred init `lda #$08; sta chnwave; sta
  $D404` (test-bit reset) — detect imm via `A9 ?? 9D <chnwave> 9D 04 D4` (`p2_init_ctrl`,
  default 0). Improper div 44 → **151** (NOT full; init `lda #imm; sta $D404` WITHOUT the
  chnwave store also exists — Lovin_SID — currently undetected, but it's fr0/dropped +
  doesn't persist so harmless).
- **deftempo disambiguation (commit 57382c3):** the generic `A9 ?? 9D 9D 9D A9` matched
  the zero-init group (tempo=0) before the real tempo-init; pick the match whose 3rd
  store == chnnewnote (chnnote_base+3). Lovin_SID div 3 → **28144** (~38s, NOT full).
RESIDUE buckets (TRUE first_div, songlength verify): **div=None/len-mismatch (5:** Zonik,
Addiction, Reggae_1, Yummy_Pizza, Rusty_Gate — match over overlap, different total len) /
**div=0 (3:** A_Goat_Day, Truck_Driver, beastie_boys) / div=60 (2) / scattered early
(48/51/56/82/87/151/170/307/12) / DEEP (Lovin 28144, Sanxzodiz 15023, Scenial 19869).
- **div=0 → init filter SMC (commit e955448):** player2 init_filter was hardcoded
  (0,0,0x0F,0,0). The global filter SMC slots filtcut ($D416) + filttype ($D418 hi) are
  NOT zeroed by the deferred init, so a pre-set filter is live from frame 1. Detect
  mt_filtcutoff (`A9 ?? 69 ?? 8D ?? ?? 8D 16 D4`) + mt_filttype (`A9 ?? 09 ?? 8D 18 D4`);
  pi_loop sets filtcut/filttype to those (not 0). A_Goat_Day div 0→58.
- **subB note-load (commits a490b73 + 5b940c4) — A_Goat_Day div 0→58→299:** TWO subB
  fixes. (1) **wavetbl +6-anchor reorder:** the loose `B9 ?? ?? F0 03 9D` wavetbl anchor
  false-positived INSIDE the interleaved instrument table (A_Goat_Day wavetbl landed at
  instbase+2 → runaway 100+ step wave programs → garbage ctrl). Try the SPECIFIC +6
  direct-ctrl form `B9 ?? ?? F0 06 9D ?? ?? 9D 04 D4` first (can't match a +3 loadregs
  tune). HIGH-LEVERAGE correctness (many subB tunes had garbage wave programs). (2)
  **newnoteinit-pulse knob (`p2_nn_writes_pulse`):** some subB players' newnoteinit sets
  chnpulse ONLY (no $D402/$D403 write) and rely on loadpulse every frame; detect via
  `B9 ?? ?? F0 ?? 9D ?? ?? 9D 02 D4`. Composer makes the nn pulse write conditional.

**HONEST FAMILY STATE (songlength verify, sample 30): ~3/30 FULL (~10%).** The many
fixes this session (deftempo, init-ctrl, init-filter, wavetbl, nn-pulse) are REAL — they
move divergences progressively DEEPER + fix correctness (runaway wave programs) — but
DON'T jump the FULL count because each tune has SEVERAL divergences (fixing one reveals
the next). This is the realistic wide-family grind: incrementally harden the engine/
extraction, each variant fix helps audio even before FULL.

**✅ AUTHORITATIVE WIDE BATCH (2026-06-30, `pipelines/goattracker/v1/family_batch.py` +
`pipelines/goattracker/v1/census.py`, FULL-songlength verify over all 1359):** **164/1359 FULL (12%)** —
**player1 (tracker) 84/884 (9.5%)**, **player2 (gamemusic) 80/341 (23.5%)**, detect_fail
134, build_fail 3. KEY INVERSION: player2 (this session's focus) is now BETTER than
player1; **player1 is the bigger problem.** Tools: batch verifies at songlength×1.1
(Pool(8), resume-safe jsonl `tmp/gt_v1_results.jsonl`, records player + div_sig); census
clusters partials by (player, first-div register-role, depth). **RANKED BUCKETS (the
real levers):**
1. **player1 optimized-layout WRITE ORDER (v1_pwlo div<50 ×302 + v1_freqlo div<50 ×133
   = 435 tunes, THE #1 LEVER).** Pure per-frame write-ORDER diff (all values match):
   ORIG writes PER-VOICE [v1 freq,ctrl,pw][v2 freq,ctrl,pw][v3 …]; MINE writes all-voices
   freq+ctrl THEN pulse. These are ALL the optimized-layout variant (nowavedelay=True +
   inittick_is_tempo=True) — a substantially different player my engine emits in V1.5
   order. Fix = parametrize player1's per-frame emission to per-voice freq/ctrl/pulse for
   the optimized variant (C16 write-order parametrization). HALF of player1's partials.
2. **detect_fail 134** (mostly `V1 anchor not found: gatetimer` — the optimized
   gatetimer anchor `4A A9 gt 9D ?? ?? B0` misses a sub-variant; + 17 IndexError).
3. **deep partials div>=10k** (~150 across both: v2/v3_freqlo, v_ctrl — match long then
   one effect; per-cause). 4. **len bucket** (~46, both players — near-converged
   song-end tails). 5. player2 v1_pwlo div<50 ×27 + v_ctrl scattered.
NEXT: the player1 optimized-layout write-order fix is the single highest-leverage item
(435 tunes). Then detect_fail (gatetimer anchor), then deep partials per-cause.

**✅ C16 EMISSION-ORDER KNOB LANDED (commit 3f20ab5) — but NECESSARY-NOT-SUFFICIENT.**
After a re-anchor (user) + ledger consult: I'd MIS-SCOPED the #1 lever as a "flow
restructure" (the exact anti-pattern C16 warns against — trace first, it's a bounded
knob; FC `nextvoice_write_order` precedent). The real fix is an `optimized`-gated knob:
pulseexec modulates chnpulse/chnpulsedir but doesn't emit $D402/$D403; loadregs emits
them every frame after $D404 (player2 loadpulse-after-freq order). Gated → V1.5 (Joker)
+ player2 (Faderik) byte-identical, ZERO regression. **MEASURED on a 25-tune optimized
sample: moved the whole bucket div 3 → 15/30, but 0 → FULL.** So the order cause is
fixed; the 435 bucket has MORE causes — the new wall is **div≈15 = pulse-mod-START
timing** (the sweep lags one frame: orig $20→$40→$60 from f2, reb $20→$20→$40; a new-
note/pulse-mod-start timing issue analogous to player2's tick0-defer). A few stay at
div=3 (Dungeon_Horror/dynamit/Murphys_Law/Redlight — a different early cause). So the
435 bucket needs the C16 knob (done) + the pulse-mod-start timing (NEXT) + per-residue.
**2nd knob LANDED — optimized FETCH-TICK (commit 44d3af3):** the pulse-mod lag traces to
the note-fetch tick condition: optimized fetches at chntick==0 (RE_NOTES §11 tick0; "NO
cmp #gatetimer in the pulse path"), MINE fetched at chntick==GATETIMER(=2) so the
modulation-SKIP frame was misaligned by 2 ticks (GATETIMER is the HR-flag preset, NOT the
fetch offset). Gated `tick_fetch_cmp=''` for optimized → fetch at 0. Blueseczka div 33→63,
MM7-Bass 30→60; Joker+Faderik FULL. STILL necessary-not-sufficient.
**⚠️ OPTIMIZED BUCKET = ALL-OR-NOTHING MULTI-CAUSE + MULTI-SUB-VARIANT (re-batch
2026-06-30, 164/1359 UNCHANGED after both knobs).** The C16-order + fetch-tick knobs are
CORRECT (no regression, writelog moves deeper: Blueseczka 3→63, the v1_pwlo div<50 ×302
bucket collapsed) but converted ZERO to FULL — every optimized tune is uniformly multi-
cause, so nothing converts until ALL its causes are fixed. Causes mapped so far: (1) C16
pulse order ✓ (2) fetch-tick ✓ (3) HR/fetch decoupling ($13f7 look-ahead, RE_NOTES §11a)
(4) **per-frame FILTER/VOLUME — a SUB-VARIANT split:** Kyokumei + Dont_You_Want_Me
(optimized) write $D418/$D416 every frame, Blueseczka (also optimized, same detection)
does NOT — so my `filter_exec=''` is right for Blueseczka, wrong for Kyokumei; needs a
per-tune filter-write detection, NOT a universal knob. So the optimized variant is a ZOO
of sub-variants (filter-writing vs not, + likely HR variants), each a detect+knob. This
is a MAJOR multi-session RE effort (essentially fully RE-ing "a substantially different
player" w/ sub-variants), NOT a quick grind — the FULL count won't move until a whole
tune's causes ALL land. STRATEGIC: the foundation (2 knobs) is laid + the causes mapped;
the realistic path is a sub-variant census (cluster the optimized partials by their write-
stream sub-variant) THEN per-sub-variant knobs, OR interleave with the deep-partial
one-fix-from-FULL tunes for visible count gains. **HONEST STATE of the optimized grind:** the divergences are LARGELY inaudible idle
freewheel (RESTING voices' pulse/freq sweep — confirmed via pc-trace, Blueseczka v1 is all
rests; player1.5 resets phase via $09 → C15 audibly equivalent). Strict (user choice)
requires reproducing them = a LONG grind of intricate tick/HR knobs (C16 order ✓, fetch-
tick ✓, more remain), each moving the bucket deeper but NOT converting (3→33→63). Next
causes: Hawk_Intro div@0 + Cactus_Inc div@15 (different early causes), Blueseczka div@63
(likely the optimized HR mechanism via $13f7, RE_NOTES §11). Under the deferred C15 audio-
equivalence verdict most of the 435 pass with NO knobs — the standing tension.

**⚠️ SAMPLE-CAP UNDERCOUNTS (historical, now superseded by the batch above):** the ~3/30
used a 75s duration CAP for speed, which
undercounts (masks FULL on long tunes + boundary-truncates). Re-checked the div=None
"cluster" at FULL songlength: **Yummy_Pizza = actually FULL** (179s, cap masked it);
Reggae_1/Rusty_Gate = div=None w/ TINY tail diff (7/17 writes — song-end capture
boundary, effectively converged); Zonik = reb ~3000 short (real loop/end); Addiction =
real div@83. So div=None is NOT one cause, and the TRUE FULL rate is >3/30. NEXT
SESSION: build `pipelines/goattracker/v1/family_batch.py` (FC-standard-shaped) that verifies at FULL
songlength (NEVER a duration cap / arbitrary 12s — both undercount) + a divergence census
to get the accurate rate and rank real buckets. Then attack: deep partials (Lovin 28144,
Sanxzodiz/Scenial ~15-20k), Zonik-style short (loop/end), the genuine early divergences.

**✅ BATCH+CENSUS BUILT + RUN (2026-06-30). C6 offtable_freq MIGRATION DONE (commit
8a743d1, correctness-neutral).** GT V1's freq capture migrated from the superseded
contiguous 128-entry window to per-inst `offtable_freq` records (`extract/to_usf.
_offtable_freq` + composer rebuild). USF carries the 96-entry tuning + `(idx,0,lo,hi)`
records for reachable off-table reads (wave/arp/**bare-note** idx≥96, cross-pattern
instrument-carry walk). **CORRECTION — the deep partials are NOT C6.** I hypothesized
the reb=$ba(186) deep partials (Tarantula/Dojo/Last_Ninja, div≥3000) were off-table, but
VERIFIED: $ba is IN-table (idx 8/76), so reb reads a WRONG NOTE INDEX (a freq-COMPUTATION
divergence — glide/toneporta/vibrato/arp), not off-table. GT notes ≤93 + offset ≤15 →
idx ≤~110 < the 128-window, so off-table-past-window reads don't exist in GT V1; the
migration is ML-cleanliness only, **0 FULL-count change (164→164, 0 status changes vs
baseline)**. LESSON (ledger C6): the contiguous-window→records change SHIFTS the composer
freqlo/freqhi BSS size per-tune → page-crossing cycle drift → song-end-boundary `sig=len`
flips (8 tunes, all `sig=len`, NO value divergence — Trap B); FIXED by padding the
internal array to a stable ≥128. Diffing a pre-migration baseline jsonl was what isolated
the `sig=len` noise from a real regression.
**SESSION-END MAP — remaining GT V1 buckets (no quick wins, the count is genuinely hard):**
(1) optimized variant (435, biggest) = all-or-nothing multi-cause + multi-sub-variant ZOO
(C16 ✓, fetch-tick ✓; remaining HR-$13f7 look-ahead, per-frame filter/volume sub-variant
split, freq-timing) — major multi-session RE. (2) **deep-partial freq (39+ V1.5) = WRONG-
NOTE freq computation (NOT C6)** — reb's glide/toneporta/vibrato/arp lands on a different
note index deep in the song; per-tune-ish, the real convergence work for these. (3)
detect_fail (134) = gatetimer-anchor miss → fixing makes them BUILD but join the optimized
partial pool (not direct FULL). (4) len bucket (46) = song-end-boundary tails, near-
converged (a small-tail tolerance in verify would recover these + is principled — the
music matches, only the capture-cutoff partial frame differs). 164/1359 (12%) FULL.
Batch+census now live at `pipelines/goattracker/v1/{family_batch,census}.py` (FULL-
songlength verify, per-player rate, divergence buckets). **KEY correctness result earlier: PCM
audio comparison CANNOT be a verdict (rebuilds are per-frame-exact not cycle-exact,
Trap B); the audio-equivalence soundness is decided by the TEST BIT (phase reset),
not by rendering — proven, recorded in ledger C15.** gatetimer 30 = optimized-init tunes whose HR-flag
gatetimer anchor `4A A9 gt 9D ?? ?? B0` misses (medium). pattern-overran 20 = my
generalized song/patt picks a false-positive when no diff-3 table exists (orderlist
refs an out-of-range pattern) — needs a self-consistency validator or better detect.

Secondary: Drrsh-style DEEP partials (converge ~57% then a per-effect freq diverge —
rarer, per-cause). pwlo partials (11) are mostly the parked optimized variant.
**V1 ROADMAP (revised after choice B — extract anchors are the bigger lever; only
31/60 sample even BUILT):** (1) **widen extract anchors — wavetbl 20 + filttbl 8 +
songtbl/patttbl 3 + gatetimer 2** (each is a layout sub-variant where the byte-pattern
anchor misses; unblocks detection → those tunes then join the verify residue); (2) real
audible per-effect partial bugs (now cleanly exposed once idle noise is set aside —
Drrsh@5007, Memoires audible tail); (3) audio-equivalence verdict (ledger C15) when
worth the verdict change; (4) optimized engine body. Batch runner: `tmp/v1_batch.py N`
(sid_db.query, capped-dur triage); `tmp/audioeq_*.py` = the C15 filter prototype.

(history below — superseded by the CONVERGED status above)
`pipelines/goattracker/v1/` has `disassembly.s` (annotated, canary Joker) +
`RE_NOTES.md` (full engine semantics + data layout + extraction plan). No
extractor/composer/config yet. **Layout VALIDATED against Joker**: instruments
@ $1553 (8-byte stride), wavetbl $157a / notetbl $158a, patttbl lo/hi $159b/$159e
— matches v1_player1_v153.s exactly. **Representation DECIDED** (ledger C14):
per-row commands → `NoteRow.fx_flags` strings (FC precedent), NO schema change;
arp is a per-row musical fx, not a new kind.

## V1 at a glance (the migration target)
- 1,359 SIDs; **1,347 single-SID** + 12 dual-SID/2SID (exclude). **95.6%
  single-subtune.** **78% load $1000**, rest relocated ($0ff6/$0ffa/$3000/
  $c000…) → needs a relocation factory (FC/DMC pattern).
- **ONE dominant player body** (the 639 "distinct" 48-byte prefixes are mostly
  the per-tune freq table; the player-code stub is near-universal) → single
  composer covers most, like FC standard.
- GoatTracker player **lineage**: stride-7 channel state, global filter written
  at frame start ($D416/$D417/$D418), 1-based table pointers, multispeed via
  self-modified `LDY` operand, **deferred first-play init** (init stashes
  subtune×2 into the play routine; real setup runs on first play()). The V2 docs
  (`player_algorithm.md` etc.) are a **Rosetta stone**, not authoritative.
- **V1-defining diffs vs V2** (full table in `pipelines/goattracker/docs/v1_README.md`): arpeggio
  pattern command `0XY` (root→+X→+Y semis, every tick, X≥8=half-speed, shares
  vibrato counter; REMOVED in V2); per-instrument **inline** wave table;
  **4-scalar per-instrument pulse** (no step table); **filter table from V1.4+**
  (64×4 bytes; V1.25 none); **no speed table**; 3-byte variable pattern rows,
  8 commands packed in 3 bits; max 31 instruments; testbit hard restart from V1.5.
- Song file ID is **`GTS!`** — the old research.md "GTS3/GTS4" claim was WRONG
  (GTS3/4 are early GT2); corrected 2026-06-29.
- **Audio sub-versions inside one sidid class** (binary-detect, not sidid):
  pre-V1.3 / V1.3-1.4 / V1.5+; cmd meanings shifted V1.25↔V1.53.

## Key assets (all under pipelines/goattracker/docs/)
- **Primary 6502 player source** in `pipelines/goattracker/docs/src/`: `v1_player1_v153.s` (V1.5 std —
  the disassembly reference), `v1_player1_125.s` (V1.25), `v1_gmusic_v153.s`,
  `v1_readme_125/153.txt` (manuals). Plus GT2's `gsong.c` GTS! importer
  (`deprecated/gt2_pipeline/GoatTracker_2.77/src/gsong.c`).
- Index: `pipelines/goattracker/docs/v1_README.md`; provenance: `pipelines/goattracker/docs/v1_provenance_log.md`.

## Next steps (extractor phase) — ⚠️ SUPERSEDED (kept as RE reference)

> The sections from here down are the old research/plan phase. Current state
> = the wide-batch sections ABOVE (extract + composer built, 164/1359 FULL
> authoritative batch, C16 knob landed). Do not resume plans from here.

1. **Extractor binary→model DONE + validated** (`v1/extract/engine_model.py`):
   `parse_sid` + `detect_layout` (anchor/cluster table-base + globals detection,
   variant-tolerant) + `extract` → `V1Song` (orderlists, patterns, instruments
   + wave programs, filter table). Validated on Joker/Imdunk/Menace47. KEY decode
   fixes already in: instbase via B9-operand clustering (PHA/PLA variants break
   single anchors); note-without-cmd = `b-$60` (carry-clear sbc, NOT b-$5f);
   filttbl anchor `A8 B9 ?? ?? F0`; song(diff-3)/patt pair by code-order. Run
   `python3 pipelines/goattracker/v1/extract/engine_model.py` for the smoke dump.
   NOTE: Xetris-class (load $4000, older/gamemusic variant) fails the $fc/$fd
   pair anchor → factory concern for later.
   **NEXT: `to_usf.py`** (model→UsfFile): per-row cmds→fx_flags (C14), inst→
   PwmConfig/waveform/wave_freq/loop + FilterProgConfig, note $5E=keyoff/$5F=rest,
   duration from tempo. Then `config.py`.
2. **Composer** (`v1/composer.py`): data-emission + xa65 + PSID harness DONE
   (assembles, builds a 2592-byte SID for Joker; `build_v1_sid`/`compose_v1_asm`).
   Data layout chosen: separate per-field instrument arrays (instad/instsr/...
   indexed by 1-based id, NO *8), wave arrays in GT shape (wctrl/wnote + $FF
   marker + relative loop tgt=loop+2 so waveexec is a faithful v153 transcription),
   freq table = baked constant, song/pattern pointer tables (per-voice slot base).
   `_encode_pattern`/`_fx_to_cmd` invert to_usf. **ENGINE IS STUBBED** (`_ENGINE`
   = init/play rts) — the clean v153 transcription is the NEXT focused task:
   filter exec (always writes $D416/17/18), 3-voice loop (X=0/7/14), deferred
   first-play init via RAM flag, tick/funktempo, tick0 seq+newnote, waveexec,
   continuous fx (arp/porta/toneporta/vibrato), pulse bounce, gatetimer+HR,
   loadregs. RAM globals (no SMC), rts-trick cmd dispatch, constants
   GATETIMER/HR_AD/HR_SR/DEFTEMPO. Reproduce write OUTPUTS incl. $D404=$09 testbit.
3. **Verify** (`v1/verify.py`): build+flat-compare. **Canary converges to
   flat-position 887/2776 (~32%)** at full songlength — init + filter + voices
   1/2 + row0 + fast toneporta all match. Fixes landed (each advanced the div):
   (a) freq table is PER-PLAYER (extract 128 entries incl. the C6 off-table
   window — wave relative notes mask &$7F → read past the 96-entry table);
   (b) wave-loop emitted as ABSOLUTE target (own clean scheme, no carry math);
   (c) TONEPORTA/note-only INHERITANCE — note-only rows (Row.cmd None) inherit
   prev cmd+instr; emit cmd-flag for ALL cmd-rows (incl. arp0 = CLEARS effect),
   set instr only on real change (Row.new_instr);
   (d) TONEPORTA LEGATO applies NEXT play — t0_toneport jmps pulseexec (skip this
   frame's waveexec); Joker's build differs from v153 (which runs waveexec at
   toneporta tick0). 11%→32%. **chntick countdown PROVEN byte-identical orig vs
   reb (direct memwatch compare) — row timing is correct; divergences are
   per-effect, NOT timing.** Diagnosis method: `siddump --writelog-per-irq`
   (Trap-C-free) + `--memwatch-on-write d418 <ram>` (RAM labels via
   `assemble(...,return_labels=True)`).
   **OPEN (next, ~div 887): TONEPORTA SLIDE — the `jmp pulseexec` fix (d) is a
   JUMP approximation; orig actually SLIDES.** Confirmed: orig slides note60→62
   as $22a0 → $269c (+$3fc = param $ff<<2) → snaps $26dd. So toneporta is a
   genuine continuous slide (speed = param<<2, snap on arrival); fast params
   ($ff) reach in ~1 step (look like a jump → why the hack got 32%), slow
   ($53/$af) take several. THE PUZZLE: in v153 the continuous-fx path (incl.
   toneporta slide, mt_tickntoneport) runs ONLY when chnwaveptr==0, but ALL
   Joker insts have LOOPING wave programs (waveptr!=0) that set freq=freqtbl
   [chnnote] every frame — which would OVERRIDE the slide. Yet orig slides. So
   either (i) the slid inst's wave program STOPS (waveptr→0; check if a wave
   cmd $E0-$EF stops it, or the loop-target/end differs from my forced-loop
   extraction), or (ii) Joker's build runs the slide despite the wave (variant),
   or (iii) my instrument/command STATE diverged at that point (memwatch was
   inconclusive — used stale labels). NEXT: RE the V1 toneporta↔wave interaction
   (read mt_waveexec + mt_tickntoneport + the wave-cmd dispatch in
   pipelines/goattracker/docs/src/v1_player1_v153.s); verify mine's chninstnum/chnfx/chnwaveptr at the
   div with CORRECT labels (recompute after each code change). Likely revert the
   `jmp pulseexec` hack once the real slide is implemented. Then grammar ext for
   arp/vibrato fx (text round-trip), relocation factory, wide batch.
Then reloc factory + stratified-subset iteration; full batch at closeout (the
[[project_fc_fingerprint_and_standard]] playbook). Mirror DMC infra:
composer_asm.py + v4/factory.py + extract/. Harness refs: `src.composer_runtime.
xa65.assemble`, `.psid.build_header`, `pipelines.hubbard.verify_cycle`.

See [[feedback_check_existing_engine_docs]], [[feedback_residue_triage_order]],
[[project_fc_fingerprint_and_standard]] (the closest analog: one vanilla player +
reloc factory + wide batch).
