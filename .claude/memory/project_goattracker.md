---
name: project_goattracker
description: "GoatTracker family migration state — V1 (original 1.x) is the active target; research done, disassembly next"
metadata: 
  node_type: memory
  type: project
  originSessionId: c0742216-af17-42da-9a5c-fa8ae0d40172
---

GoatTracker = 2nd-largest HVSC family after DMC: **8,670 SIDs** (7,311 V2 +
1,359 V1). Family-doc state `OK`. **Active focus: V1** (the *original*
GoatTracker 1.x by Cadaver, NOT GoatTracker 2 — user-directed 2026-06-29).

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
- **V1-defining diffs vs V2** (full table in `docs/v1_README.md`): arpeggio
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
- **Primary 6502 player source** in `docs/src/`: `v1_player1_v153.s` (V1.5 std —
  the disassembly reference), `v1_player1_125.s` (V1.25), `v1_gmusic_v153.s`,
  `v1_readme_125/153.txt` (manuals). Plus GT2's `gsong.c` GTS! importer
  (`deprecated/gt2_pipeline/GoatTracker_2.77/src/gsong.c`).
- Index: `docs/v1_README.md`; provenance: `docs/v1_provenance_log.md`.

## Next steps (extractor phase)
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
   docs/src/v1_player1_v153.s); verify mine's chninstnum/chnfx/chnwaveptr at the
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
