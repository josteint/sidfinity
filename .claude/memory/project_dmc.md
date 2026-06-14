---
name: project_dmc
description: "DMC (Demo Music Creator) migration — the new focus engine (10,676 HVSC SIDs, largest family). Census DONE: V4 canonical = 5401 (50.6%), target. Research docs + fully annotated V4 disassembly DONE (pipelines/dmc/v4/disassembly.s, rep Geometrical_Zaks). KEY: data-table addresses are PACKER-PATCHED operands — extract by dataflow, never fixed offsets. NEXT: config + extract + composer emitters, write-log-first on Zaks."
metadata: 
  node_type: memory
  type: project
  originSessionId: c83d6f65-8c2c-42bb-8f55-d46a1994efb2
---

## DMC — the focus engine after FC standard went uready (2026-06-12)

Largest HVSC family: 10,676 SIDs (`engine LIKE 'DMC%'` in hvsc84.db).
Player by Brian/Graffity, never source-released. All research in
`pipelines/dmc/docs/` (README.md is the index; provenance_log.md per wave).

## Census (tools/engine_fingerprint.py — renamed/generalized from fc_fingerprint)
`pipelines/dmc/docs/fingerprint_census.md`. 688 exact skeletons → 134
families. **Family 1 = V4 canonical, 5401 (50.6%)** — 0.973 vs the V4
player binary carved from DMC 4 Editor 2025
(`docs/dmc4_player_embedded_1000.bin`). Family 2 = V4-derived variant,
2889 (0.732 to V4, identity TBD — diff later; much may carry over).
Families 3+4+5 = V5 line (2181). V6 = 15 (different player, skip).
Raw data: `tmp/dmc_fingerprint.jsonl` + `tmp/dmc_families.json`
(regen: `tmp/dmc_census.py`). NB the canary-picker DMC candidates are
all V5-line/tail — NOT family 1 (same trap as FC's custom-outliers).

## V4 disassembly — DONE, fully annotated
`pipelines/dmc/v4/disassembly.s` — representative
`MUSICIANS/A/Amadeus_Slash_Design/Geometrical_Zaks.sid` (family-1
dominant exact hash = 3002 members, 3 subtunes, load/init $1000 play $1003).
Header carries: memory map, full variable map, sector/track byte dispatch,
instrument record, filter def, wave table semantics, play flow + write order.

**KEY EXTRACTION FINDING: the editor's packer PATCHES the player's absolute
operands per song.** Fixed: code skeleton, freq tables ($1647/$16A7),
instruments ($18F0), per-note vib depth table ($1888, OVERLAPS code bytes
$1888-$188D for notes 0-5). Patched (read by dataflow at operand sites
$1227/$159C/$15B9/$1296/$180E/$1103/$1108): wavectrl, wavefreq, filterdef,
tunetab, sector ptr lo/hi. Region sizes = address deltas. Some family-1
members have wrapper inits/shifted code (On_My_Way_to_X, Retro_Tech) →
factory must probe, FC-style.

## Engine model essentials (write-log-relevant)
- Duration-based (NOT tick-synced voices); tick = speed-counter reload;
  time = (speed+1) × duration frames.
- Note lifecycle: fetch frame writes ONLY $08→ctrl + $0F→AD+SR (hard
  restart); frame 2 = real AD/SR + pulse/filter/vib init + wave step +
  freq/PW/ctrl; gate on 3 frames min ($1786 guard), then non-holding
  ($10 clear) instruments get gate-mask $FE → tail rides SID release.
  Holding: gate off at duration ctr == 1 (+ AD/SR=$00, sub_17EC).
- Steady-state writes per voice per frame: freq lo,hi, PW lo,hi, ctrl;
  then global $D416 (cutoff), $D417 (res|route). $D418 ONLY at init and
  at filter note-init (mode|vol) — sparse!
- Sector dispatch: $F0-$FF VOL (sustain override), $7C soft-start toggle,
  $7E rest, $7D SWITCH (gate-mask bit0 toggle), $C0-$DF glide/slide
  (bit4=mode), $80-$BF duration (&$3F), $60-$7B instrument (&$1F),
  $00-$5F note, $7F sector end (peeked post-event). Track: $00-$7F
  sector#, $80-$9F/-$A0-$BF transpose ∓0-31 (then next byte = sector),
  $FE voice end (state freewheels!), $FF loop.
- Instrument 11B: AD, SR, PWbounds/init, PW speed nibbles ×3 (6 phases,
  saturate at 5), PWstep-base|filterdef#, vibdelay|width, vibramp/slide
  speed, wave start, FX flags ($01 drum abs-freq, $02/$04 no filt/pulse
  reset, $08 no gate-off, $10 holding, $20 filter, $40 half-rate
  per-note slide w/ GLOBAL parity $1019, $80 cymbal $FFFF+$81).
- Vibrato: triangle, per-note depth ($1888 table), width DOUBLES per
  half-cycle until ramp ctr == byte8; dead-code ADC/BIT quirk at $1589.
- Wave: 2 parallel arrays (ctrl, freq-offset); ctrl >= $90 jumps back
  (val-$90); melodic freq byte REBASES the note (arp); drum = abs hi.
- Filter: single owner per frame ($1720 claim, first voice in X order);
  16B defs: res|mode, cutoff, repeat, stop, 6×(size), 6×(duration).
- Init does NOT clear $1018 ($D417 route shadow) — file-image leftover
  leaks into $D417 until instruments set it (init.sid priming candidate).
- Entries: init/play/+$06 all-off/+$09 sfx (A=note Y=instr X=voice,
  no transpose)/+$1D tune-select.
- ZP $F8/$F9 only.

## ✅ ZAKS FULL (2026-06-12) — pipeline COMPLETE end-to-end
Geometrical_Zaks: ALL 3 subtunes instruction-sequence exact at full
songlength (303565/266449/73661 play writes, trichotomy state ✓).
Pipeline: pipelines/dmc/v4/extract (dataflow operands, path-resolved
patterns w/ loop-unroll cycle detection, exact 5-stage dispatch incl.
ghost $7F=instr31) → USF (schema growth: wave_freq, gate_mode, pwm
speed_steps/keep_running, vibrato ramp, slide 'run'+half_rate,
filter keep_running, noise_attack, signed ol transposes, duration
filter_programs, gate_toggle + glide_to flags, InitVoice.note) →
pipelines/dmc/composer_asm.py (OUR engine; own event encoding) →
xa65 → PSID. Wired into tools/regression.py (DMC section).
Artifacts at hvsc84/.../Geometrical_Zaks.{usf,sidfinity.sid}.

THE THREE FIXES (full detail in pipelines/dmc/v4/RE_NOTES.md):
(1) idle-note voice_state priming — rest-opening voices run effects
on the WORK-FILE LEFTOVER $1012-14 note (init { voice N { note } });
idle effects use instrument RECORD 0 (cleared cache) → extract
force-includes record 0 as slot 0. (2) pulse base split — step =
nibble + CACHED base; idle base=0; composer derives base = step&$0F.
(3) xa65: ':' is a statement separator EVEN IN COMMENTS (sanitizer).

## ✅✅ FAMILY-1: 3135/5401 FULL (58.0%) as of 2026-06-14
Progression: 2257 (first sweep) -> 2656 (relocation: +399) -> 2921
(2-entry layout + base=load: +265) -> 2945 (CIA) -> **3135 (round 1
sub-build recovery: +190, 2026-06-14)**. Mass-written + db-refreshed
(0 err; DMC total 5019 sidfinity builds = 3135 fam1 + 1884 fam2).
**ROUND 1 (commit a8d59ae):** recovered player_code_mismatch + a few
no_jumptable members — the family-1 sub-builds use the SAME variant
axes as family 2: (a) IMAGE-WIDE jump-table scan for relocated-within-
file players (+7; 364 have no jump table, 35 CIA-timer-unreadable);
(b) $1181 = rest_effects='skip' (130 members, the family-2 rest knob in
fam-1 — probe $1180); (c) $1631+$163E = all-off/sfx routines vary but
NEVER run during play() -> masked $162F-$1647 (136); (d) $12A8 = filter
$D418 via JSR helper (STA $D418 + dead store) -> mask+validate (80).
player_code_mismatch re-run: 183 FULL + 73 partial. Residue: remaining
sub-build sites ($1231 SR-variant + helper, $1008-resolved, $18B4,
$1493, smaller), 364 no-jump-table, the off-table architectural limit
(~600). Full regression green (0 regressed).

**2-ENTRY LAYOUT (commit 9212423):** the biggest code-mismatch bucket
(688 @ $1001) is a re-assembled build with a 2-entry jumptable
(JMP base+$807/base+$50) but a play body BYTE-IDENTICAL to canon. The
factory detects layout from the jumptable signature; for 2-entry it
masks the restructured init/dispatch/all-off regions + uses the $180E
tunetab site (also valid for canon). ~290 of the 688 recovered (rest
are 2-entry members with CIA/offtable). player_code_mismatch 1182->495.

RELOCATION FACTORY (commit ab4b4c9): the same player at ANY base passes
(Face2face $9000 FULL, verified $2000-$C000). Relocation is EXTRACT-ONLY
(composer always emits at $1000; writelog base-independent incl. the
original's wrapper-init writes via Check A). base = play-3 (robust to
custom init wrappers — init may point elsewhere). Identity compare vs a
RELOCATED canonical reference: self-ref operands ([$1000,$1900)) shifted
by delta, computed once by tracing canon. Masked the 5 dead-code gap
fragments (unreachable padding w/ relocated operands). vibdepth compared
[6:96] (0-5 overlap code, relocate). config.base threads through extract.

Factory `dmc_v4_config(sid)` (pipelines/dmc/v4/factory.py): masked
identity compare vs the carved canonical player + multi-site operand
consistency + typed DMCV4Unsupported reasons. Wide runner:
tools/dmc_family_batch.py (Pool(8), crash-safe JSONL resume).
Results: tmp/dmc_wide_results.jsonl (first_diff per partial member).

5 triage classes solved this batch (all in RE_NOTES.md):
gate-mask leftovers ($100F-11 → InitVoice.gate_mask); filter-def
slot-vs-slot*8 indexing; 16-bit running pattern pointer (my event
encoding inflates patterns >255B); the OFF-TABLE WINDOW (orig reads
past freq tables into state — composer mirrors the stable prefix
sidoff/fbit/fmask/spd/mvol, extract certifies reachable reads);
TRACK LOOP-TO-TARGET variant (JSR-$1042 hook reads byte-after-$FF as
loop pos; factory-probed); PER-TUNE FREQ TABLES (members ship edited
temperaments → USF freq_table); IDLE WAVE PROGRAM (cleared-cache walks
table from idx 0 → wave_programs[0] + jump-back marker pool semantics);
DUAL-CLOCK PHASE ($1019 leftover → params.slide_phase).

## NEXT (ranked residue, all in RE_NOTES.md "Wide-batch residue buckets")
1. **CIA-MULTISPEED — FEATURE BUILT (eafc895), partial rollout.** +24 of
   the 135 cia_multispeed bucket FULL. Residue within it: ~32 py65-init
   programs no readable timer (init hangs / timer set in an IRQ handler /
   different timer — could measure rate from writelog, risks drift);
   ~29 non-canonical-under-CIA (2-entry or other build at base);
   offtable-live limit. BIGGER: the 459 no_jumptable members are CIA
   wrappers whose player is at NEITHER play-3 NOR load (relocated WITHIN
   the file) — need a jumptable-SIGNATURE SCAN of the image to find the
   base, then the CIA path applies. That scan is the next CIA unlock.
2. 2nd loop-hook variant: EVAPORATED (relocation absorbed it; ~13
   ambiguous `7e18ea` members remain — not worth a dedicated fix).
3. Remaining code-mismatch sub-builds (player_code_mismatch 495, down
   from 1182 after the 2-entry layout: $1181/$1631/$12A8/... — each a
   distinct re-assembly, diminishing returns).
4. offtable_live + zero-wave-table edge errors (636, mostly correctly
   refused — genuinely live per-voice runtime state; architectural limit).
5. Partial long tail (275: bucket by first_diff in the jsonl).
6. **Family 2 (2889, 0.732 V4-derived) — CHARACTERIZED + SCOPED
   2026-06-13** (`pipelines/dmc/family2/RE_NOTES.md`, rep Kajun_Klog).
   SAME V4 engine core (play body \$1085 + all-off \$162F byte-identical;
   ~85% effect chain matches; freq \$1647/\$16A7; operand SITES at canon
   addresses) with: (a) RELOCATED tables — instr \$17B0 (canon \$18F0,
   same 11-byte format), \$D417 shadow \$1034, data tables at family-2
   addrs; (b) THE BLOCKER — DIFFERENT SECTOR ENCODING: terminator is
   \$FF not \$7F (sub_11E6 CMP #\$FF), whole command map shifted. Needs:
   RE the family-2 sector byte map -> family-2 sector decoder (extract
   only; composer/effects unchanged) + factory variant (init JMP
   base+\$37, instr base from operand, d417=base+\$34) + carved
   reference. Tractable, focused sub-migration. Jump-table init offset
   \$37 is the family-2 detect signature.
   **✅ KAJUN_KLOG FULL (commit d9a0cda, 2026-06-14):** write-log loop
   complete — instruction-sequence exact at full songlength (verify_dmc
   66674/66674, trichotomy state ok; writelog 100%). The prior "vibrato
   blocker" was FOUR family-2 effect-chain diffs, ALL rooted in family 2
   relocating its instr table over \$17B0-\$17FF (clobbering canon's
   sub_17EC + sub_17FB ADSR helpers + re-laying the note-init tail/rest
   dispatch). Each = a typed canon-defaulting param (full regression
   green, no family regressed):
   (1) `vib_ramp=step` — family 2 RAMPS the 16-bit vstep by freq_hi(note)>>1
   each half-cycle (\$157F-8E) with fixed width; canon doubles WIDTH with
   a fixed \$1888-table step. Increment DERIVED from the freq table ->
   the prior vib_depth_curve USF field REMOVED (derivable; schema
   hygiene). New vsteph/vdep regs; triangle add/sub now 16-bit.
   (2) `hold_gateoff=mask_only` — holding gate-off = mask only, no AD/SR=0.
   (3) `hard_restart=none` — hard restart = TEST bit only, no AD/SR=0F0F.
   (4) `rest_effects=skip` — rest/switch/slide-tail JMP \$1591 (wavestep),
   NOT the effect chain (canon JMP \$1322) -> vibrato+pulse HOLD one frame
   at each tie boundary (the subtle periodic stall; found via flat
   write-log + sector-dispatch disasm, NOT snapshots).
   (METHOD NOTE: per-frame siddump snapshots = Trap C; stay on the flat
   write-log + --writelog-per-irq + event-aligned --on-write for
   diagnosis — see [[feedback_verification_modes]].)
   **✅✅ FAMILY-2 WIDE BATCH: 1884/2889 FULL (65.2%, commits b0349d3 /
   4e0161d, 2026-06-14)** — exceeds family-1's 54.5%. Mass-written
   (.usf+.sidfinity.sid, 0 err) + db-refreshed (7416 total sidfinity
   builds). `dmc_v4_config` family-2 path: detect jump table init+$37/
   play+$85 (4-entry OR 2-entry), masked identity-compare vs carved
   reference `pipelines/dmc/docs/dmc4_family2_player_1000.bin`
   (reloc-aware), table addrs from canon-compatible sites (tunetab $1051,
   d417 base+$34, instr $17B0 from $1227). The 5 knobs → factory-PROBED
   `cfg.extra_params` (hold_gateoff VARIES: mask_only vs adsr_clear-via-
   helper-at-$1018). Runner tools/dmc_family_batch.py (--members/--out).
   Triage round 1 (+43): $129F filter-mode (STA $9E dead store ≡ AND #$0F,
   probe+mask) + 2-entry jump table (init+play only). 4 family-2 canaries
   wired into regress_dmc (Kajun/Lameness/Fury/Bells = variant cover).
   RESIDUE (tmp/dmc_f2_merged.json): architectural off-table ~580 (20%,
   offtable_live 512+zero_wave 62; correctly refused, same ceiling as
   family 1); partial 279 (diverse freq/NOTE divergences — e.g. Short_Dream
   V3 note 69-vs-66 +3-semitone wave-program/arp diff, Crush_01 V2 freq
   sweep; per-member-diverse long tail, code matches Kajun so it's DATA);
   player_code_mismatch 53 + no_jumptable 52 + sector_decode ~20 (more
   sub-builds / relocated-in-file / corrupt). KNOWN BUG (low ROI):
   dual_phase read from $1019 not family-2's $1035 (harmless w/o dual
   instruments). NEXT (diminishing returns): partial freq/note tail,
   dual_phase, remaining sub-build sites; then family 2's own sub-builds
   are largely done — move to V5 line (2181, separate engine) or family-1
   residue.
"7. **V5 line (2181) — ENGINE PROVEN (2026-06-14): Katusha FULL.** A
   DISTINCT engine (Jaccard 0.136 to V4); full pipeline in pipelines/dmc/v5/
   (disassembly.s Phase A + SCOPE.md + RE_NOTES.md). Phase A: annotated
   disasm + the SECTOR COMMAND BYTE MAP cracked (notes<$80; cmds $F1-$FE:
   SRR/ADR/VOL/gate/FD-/FD+/FRQ/FLT/SLD/GLD/SND/DUR/GATE; $FF END). 8-byte
   instruments (AD,SR,WV,PU,FL,vibD,vibS,vibW); 3 programmable 2-byte
   tables (wave/pulse/filter, $90 loop); full 11-bit cutoff $D415+$D416;
   filter voice-3-only; vib step=freq<<width. Phase B: extract
   (config.py + extract/engine_model.py -> V5Model, validated). Phase C:
   composer_v5.py (clean re-authored engine driven by extracted song
   data) -> Katusha FULL (trichotomy is_full, 97955/97955; 100%
   write-log). **✅ USF LAYER DONE (2026-06-14, commit 8e4c685): Katusha
   FULL THROUGH USF** — extract -> to_usf -> .usf -> parse -> from_usf ->
   V5Model -> composer (composer unchanged). New schema `pulse_sweep`
   (PulseSweepConfig, spec-synced); wave decoded into Instrument.waveform/
   wave_freq/loop; sectors -> Pattern with set_dur/set_instr ORDERED PREFIX
   FLAGS (gate_logic reads the raw lookahead byte, so command byte position
   is write-stream-significant — can't reshuffle snd/dur).
   **✅ FACTORY + FULL SECTOR COMMANDS + PARAMETERIZED PULSE/FILTER (commit
   a8776c2, 2026-06-14):** `dmc_v5_config` (factory.py: 2-entry jump-table
   detect init+$40/play+$A1, family-4 play+$95 REJECTED, relocation-aware
   masked compare vs Katusha ref — operand classes code+state relocate /
   freq+data masked / SID+CIA absolute; typed DMCV5Unsupported). Full
   sector set (vol/frq/fade/adr/srr/flt/gate_toggle/gate_tie/glide/slide).
   PULSE/FILTER are SHARED/FUSED tables (packer overlaps programs; ~30%
   lack $90, bleed) — carried NOT as a table but as per-instrument
   `pulse_env`/`filter_env` = start + (rate,frames) phases + repeat (the
   PWM/cutoff envelope, cross-engine w/ Hubbard/V4 PWM). Fusion dissolved
   by CAPTURE-BY-SIMULATION (`_capture_env` follows $90 jumps, cycle-detects
   on revisit, reach-bounded); from_usf SYNTHESIZES a de-fused table. All
   5 sample-FULL members verify FULL through it. Batch:
   tools/dmc_v5_family_batch.py. **WIDE-BATCH COVERAGE = COMPOSER-GATED
   (6% on an 80-sample, NOT a representation issue — partials reproduce in
   the DIRECT model path).** composer_v5 was proven only on Katusha;
   bug-lever order from the batch: $D416/$D415 FILTER cutoff (22),
   end-of-init state-only Check-A (16), freq/PW (7); + residue
   (player_code_mismatch sub-builds, no_jumptable reloc/CIA, ~36%). NEXT:
   composer rounds — FILTER FIRST, then state-only, then freq (V4-style
   coverage climb). Census: family-3 1461 + family-5 34 = 1495; family-4
   686 (play +$95, separate branch).

## REGRESSION PORTFOLIO (2026-06-13): generalized + DMC wired
`tools/select_regression_portfolio.py` made engine-parametric (registry:
engine -> jsonl/out/feature_fn/witnesses/sid_key; exact_multicover stays
engine-blind). DMC feature extractor + `tools/dmc_regression_portfolio.json`
wired as tier-1 in regress_dmc(). The closeout step is now standard
(documented in CLAUDE.md + migrate skill): family reaches FULL coverage
-> derive portfolio -> wire tier-1 (full family batch = tier-2).

## Related
[[project_fc_fingerprint_and_standard]] (the playbook this follows),
[[feedback_dataflow_over_heuristics]] (the operand-patching finding is
exactly this), [[feedback_disassembly_data_section]] (research.md's wrong
tables), [[feedback_init_trichotomy]] (the $1018 leftover).
