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

## ✅✅ FAMILY-1: 3739/5401 FULL (69.2%) as of 2026-06-22 — STEP 2: CIA verdict + multispeed rate
**CIA MULTISPEED (2026-06-22, +367 over the 3372 jsonl base; authoritative
re-batch of all 2029 non-FULL).** Step 2 of the residue dependency order
(measure->fix-verdict->...; see [[feedback_residue_triage_order]]). The "length/CIA"
partials were NOT a pure verdict artifact — the per-IRQ verdict fix alone flipped
0/30. It RE-BUCKETED the residue (exactly as the methodology predicts) and exposed
the real cause: the rebuild ran SINGLE-SPEED while the orig multispeeds off the
CIA1 timer. TWO fixes, commit 46cd1ae:
1. **Verdict (per-IRQ capture):** `dmc_family_batch.py` now routes speed-bit
   subtunes through `writelog_per_irq_capture` (Trap C for CIA — flat per-50Hz
   capture phases init+play differently for orig vs a rebuild with different init
   length). Init dropped both sides -> trichotomy recovers d=0, reduces to
   overlap+close. Same machinery FC/Hubbard use.
2. **Rate recovery (the real lever):** the factory only read the CIA timer latch
   when `play != base+3` (a wrapper dispatcher). But the CANONICAL DMC init
   programs $DC04/$DC05 ITSELF with play==base+3 (latch $1331=>4x, $2663=>2x).
   Gate the latch read on the speed bit alone (canon path) + mirror on the
   dataflow path (was hardcoded cia_period=0). Flows cfg.cia_period -> USF params
   -> composer (installs CIA timer + sets speed bits).

Sample 30 CIA partials: 0 -> 11 FULL. Also dropped unsupported 688->380 +
error 199->62 (the re-batch recovered formerly-unbuildable members).

**PARTIAL RESIDUE NOW (1220, rich-record bucketed):** effect_div 680 (genuine
play-stream divergences, lengths now align — the biggest ACTIONABLE bucket =
STEP 3) | state_div 512 (end-of-init priming mismatch; includes the off-table
DYNAMIC freq floor = the architectural-limit bucket, LAST) | rate_or_loop_mult 13
| close_tail<=256 9 | len_gap_nonmult 6.

**TWO NEW FINDINGS (both small, both recorded for later):**
- **close-tail = ALL 9 are CIA** (|la-lb| 85-170). Genuine FULLs (full overlap
  match + state match, only tail length differs) failed by the flat close_tol=80,
  which is calibrated for 1x tunes; at 4x multispeed one play() at the duration
  cutoff = ~40 writes, so the boundary band is ~2-4x larger. SAME class as FC
  World_Record_1 (close_tol 64->80), scaled for multispeed. A flat bump to ~176
  recovers all 9 — but it's a CROSS-FAMILY verdict constant (FC+Hubbard), so
  DECISION DEFERRED to the user, not bumped unilaterally.
- **INTERNAL-MULTISPEED (13+, speed bit CLEAR):** High_Speed / Speed_It_Up /
  X-Static / Melodic_Trance etc. run 2x/4x with NO PSID speed bit — the player's
  single vblank play() loops the engine N times INTERNALLY. Distinct from the CIA
  mechanism: needs a composer play-repeat count (detect the wrapper loop, emit
  repeat=N, composer calls inner play N x). NEW composer feature, step-3+. Likely
  MORE such members hide in effect_div (internal repeat that diverges mid-stream
  rather than as a clean length-multiple).

## (historical) FAMILY-1: 3558/5401 FULL (65.9%) as of 2026-06-22 — + JT-less locator
**JT-LESS BASE LOCATOR (2026-06-22, +90):** the `no_jumptable` residue (364)
aren't jump-table-less — they HAVE a JMP table at load with NON-canonical targets
(e.g. Yardies init->+\$807/play->+\$85; Master_and_Servant init->+\$7D/play->+\$E5)
that the factory's `_jt_layout` (fixed e0/e1 patterns) rejected. The dataflow trace
FOLLOWS the JMPs to the handlers regardless of target offset, so the dataflow
extractor handles them with base=load (work RAM at load+\$0F.., canonical). Wired
(commit a263477): 'no_jumptable' added to `_DATAFLOW_RETRY`; `_build_via_dataflow`
accepts base=load when any JMP table sits at load. Re-batch of 364: **90 FULL
(25%)** + 172 build (partial) + 71 still no_jumptable (genuinely NO JMP table at
load — headerless/different entry; need another locator) + 31 err/other.
Mass-written + db-refreshed.

**RESIDUE CENSUS (2026-06-22, after re-localizing the no-first-diff partials).**
The 1843 non-FULL fully categorized; the 7 actionable buckets in dependency order
(measure -> fix-verdict -> unblock-builds -> fix-effects -> accept-limit):
- **freq ~726** (509 state-match = off-table-DYNAMIC residue, the StateLayoutMirror
  limit; +217 other freq) — the architectural floor, tackle LAST.
- **length/CIA ~154** (the "no_fpd" partials: play stream matches over the overlap,
  only LENGTHS differ -> orig vblank-stub vs rebuild full play = the CIA/multispeed
  artifact). FIX VIA THE CIA-AWARE PER-IRQ VERDICT (exists for FC/Hubbard), not the
  composer. STEP 2 — the biggest single lever, a verdict fix.
- **error 206** ("sector ... never ends" runaway + "wave shape n=0") — extract
  robustness; unblock-builds.
- **vol fade ~145** (master-vol ramp not reproduced) — one coherent modelable effect.
- **unsupported ~410**: offtable_live 78, no_jumptable 71 (truly headerless),
  loop_hook 68, cia_multispeed 67, player_code_mismatch 40 (unlocatable), loop_site
  27, sector_decode 24, zero_wave 22.
- **small effects ~99** (adsr/ctrl/filter/pulse).
Re-localizing the 249 no-first-diff partials (re-run verify_dmc, extract
first_play_diff): 154 length/CIA + 67 freq + 24 small effects + 4 now-FULL (stale
records recovered). Lesson: batch first_diff truncates to [sub,state_match] when
first_play_diff is None (length/init mismatch) -> looks "uncategorized"; re-verify
to localize. NEXT = step 2 (CIA verdict).

**SESSION FAMILY-1 TOTAL: 3135 -> 3562 (+427, 58.0% -> 66.0%):** off-table
offtable_freq port +149, vibdepth follow-on +44, post-init capture +70, dataflow
extractor (player_code_mismatch) +70, JT-less locator (no_jumptable) +90. Two
Core-Tenet breakthroughs: post-init capture (the "dynamic residue" was a file-image
mis-capture) + the dataflow extractor (opcode-skeleton operand location for moved
layouts). Remaining: 71 truly-headerless no_jumptable, 22 unlocatable
player_code_mismatch, the partials (off-table dynamic + newly-buildable).

## (historical) FAMILY-1: 3468/5401 FULL (64.2%) as of 2026-06-22 — + dataflow extractor
**DATAFLOW EXTRACTOR (2026-06-22, +70):** the `player_code_mismatch` residue (203)
is RE-ASSEMBLED DMC v4 players — the routines AND their operand sites moved (e.g.
the `$1231` family, 24 members: SR helper relocated to base+$25A, wave/filter/
sector tables moved), so the factory's fixed-offset extraction + byte-compare gate
fail. New `pipelines/dmc/v4/dataflow.py` locates every table by its canonical
OPCODE-SKELETON signature (relocation-invariant — the opcodes around each read
don't change when a routine moves; match them in the variant's traced code, the
operand there is the table address) + the track-loop hook -> loop_target. Wired as
a factory FALLBACK (commit 10ca8bd): `dmc_v4_config` tries the canon path, then
`_build_via_dataflow` on a moved-layout rejection (player_code_mismatch /
loop_site_unknown / operand_inconsistent / layout_disorder / nonstandard_instr_base).
Canon path first -> normal members unchanged (regression green, 0 regressed);
verify-gated (mislocation -> partial, never false FULL). Re-batch of the 185
player_code_mismatch: **70 FULL (38%)** + 84 build (now partial/diagnosable) + 22
still unlocatable (harder variants) + 9 other. Mass-written + db-refreshed.
NB: handles re-assembled players that HAVE a jump table; `no_jumptable` (364, no
locatable JT) needs a separate JT-less base locator (future). The opcode-skeleton
locator + factory-fallback pattern is reusable for any moved-layout engine.

## (historical) FAMILY-1: 3398/5401 FULL (62.9%) as of 2026-06-22 — off-table port + post-init
**POST-INIT CAPTURE (2026-06-22, +70 more):** the "374 dynamic-residue freq
partials" were a CAPTURE BUG, not an architectural limit (Core-Tenet meditation).
The off-table source bytes live in the engine's work RAM AFTER the freq tables;
the engine's INIT writes them, so the value the original READS at runtime != the
file-image byte I captured. siddump --memwatch on the original shows those bytes
are CONSTANT for the whole song (e.g. Have_a_Drink \$170A: file-image \$68 ->
runtime \$1A). Fix (commit 354fc73): `_correct_offtable_postinit` reads the
off-table source bytes' post-init values via siddump --memwatch (ground truth)
and replaces the file-image values; only CONSTANT-across-sample bytes used
(init-written-then-stable). Re-batch of the 452 partials: +70 FULL. The TRUE
residue is now (a) genuinely-dynamic reads — bytes that increment per frame, e.g.
Small_Introzak k31/k32 cycle 0..15 (the StateLayoutMirror case, REJECTED) — and
(b) co-location edges (off-table reads landing on k15/k16 = the rebuild's own
spd/mvol, e.g. Silent_Tears). Lesson: capture what the engine READS (post-init),
not the file image; don't mirror the state machine. **Off-table partial sub-census
(by first-divergence): 83% freq, then vol/master 29, filter 7, ctrl 5.**

## (historical) FAMILY-1: 3328/5401 FULL (61.6%) as of 2026-06-22 — off-table port
**OFF-TABLE RECOVERY (2026-06-22, +193):** ported v5's `offtable_freq` to v4 —
the biggest family-1 residue bucket was `offtable_live` (665 members: off-table
freq reads past the 96-entry table, previously REJECTED as k<=5 track-ptr / k>=17
live state). The extract now CAPTURES each read's explicit (offset,note,lo,hi) by
VALUE (stable-when-read = the read-before-evolution result), and the composer
places them in the freq overrun window (dual lo/hi landing via freqlo/freqhi/
window adjacency; positions 6..16 stay co-located live spd/mvol -> existing FULLs
byte-identical, 0 regressed). Commits: 83d7c7c (freq port, +149) + 89fa81f
(vibdepth follow-on, +44). The vibdepth follow-on handles note>95 (TWO reads: the
note's own freq via an offset-0 offtable_freq record + the vibdepth table via a
new note-keyed `UsfFile.offtable_vibdepth` field + composer overrun window). NB
the offset-0 base read does the bulk of the vibdepth recovery (vibwid=0 members);
the `offtable_vibdepth` window itself is load-bearing for only ~2 of 45 vibdepth
FULLs (vibwid!=0) — principled (note-keyed musical, same class as offtable_freq)
but marginal. Re-batch (665 off-table-affected): **193 FULL / 452 partial / 20
unsup+err**. Mass-written (193, 0 err) + db-refreshed. Residue: the 452 partials
(now BUILDABLE = diagnosable; many have separate non-off-table divergences) +
genuinely-per-frame-dynamic track-ptr reads. Off-table arc now spans all 3 DMC
consumers (v5, FC, v4). Next family-1 buckets: no_jumptable (364) +
player_code_mismatch (203) + the 452 partials.

## (historical) FAMILY-1: 3135/5401 FULL (58.0%) as of 2026-06-14
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
   **✅ FILTER ROUND 1 (2026-06-14, commits 8bea641 + f598c2a + 0057347):**
   The "$D416/$D415 cutoff (22)" bucket was TWO causes (the first-divergence
   reg just NAMES the filter — it's the first play-frame write). CAUSE A
   (the ~10-member lead-in cluster "orig $D416=$00 / new $D418=$0F at pos 0")
   = THREE uncleared STARTUP LEFTOVERS in the $1006-$103F gap the init clear
   loop ($17D5-$1845) misses: $1013 spdctr (speed COUNTER -> startup phase:
   when !=0 the first non-skip play runs effects-on-leftover N frames before
   the first fetch; Katusha's=$00 so the cleared composer matched it),
   $100F,x current NOTE (lead-in wave_step freq lookup), $101C fade-frac
   accumulator (first FD ramps master vol off-by-one; init clears the fade
   SPEEDS not this phase). FIX: extract lo_spdctr/lo_notes/lo_mvolfrac; prime
   in init; carry through USF via existing `speed_ctr_init` params + V4
   `InitVoice.note` + new `fade_frac_init` params key — NO shared-schema
   additions. X-Files + Believe newly FULL (80-sample 5->7); Katusha FULL;
   USF round-trip faithful. CAUSE B (round 2, the BIGGER filter lever, still
   gates Grid/Minoam/Conanious): FILTER ENVELOPE KEEP-RUNNING continuation.
   Post-A the cutoff DRIFTS mid-song — FCLO ($D415) drifts (orig RAMPS,
   rebuild HOLDS at Minoam FCLO index 764) while FCHI ($D416) NEVER differs.
   Per-instrument _capture_env envelopes match in ISOLATION, but the
   de-fused per-inst synthesis (each inst its own copy + $90 terminal) does
   NOT reproduce the orig SHARED/FUSED-table running position when a note
   with FL=0 (no filter restart; Minoam insts 3-6,8-13 are FL=0) keeps the
   global filterpos running PAST one program into the next region. Also
   _capture_env treats frames>=$9000 as terminal (inst-2 count $9008 =
   entry-9 $90 marker read as a count).
   **✅ ROUND 2 (commit 24875f3): keep-running filter_run — a run-GATING
   bug, NOT the synthesis-flow I'd hypothesised.** The orig filter_run_v3
   ($1496) gates ONLY on CPX #$02 (V3) -> runs EVERY V3 frame (FL=0 = no
   RESTART, not no RUN -- same PU=0 semantics as pulse). The composer gated
   filter_run on the PER-NOTE filtflag (the inst FL), which an FL=0 note
   resets to 0 -> skipped filter_run on keep-running frames -> cutoff HELD
   while orig RAMPED (FCLO drifts, FCHI matches; Minoam FCLO idx 764).
   Katusha passed (pre-filter null no-op). FIX: sticky filt_run_on flag
   (set once on first FL!=0 note, never cleared); filter_run gates on it,
   filter_init keeps the per-note gate (FL=0 still no restart). Only ADDS
   filter_run on keep-running frames -> FULL members can't regress. The
   per-instrument filter_env representation is UNCHANGED (user-chosen
   parameterisation stands; no synthesis change). **80-SAMPLE: FULL 5->15
   over the session (+10 new, 0 regressions; 7 of 10 were original
   $D416/$D415 partials: Grid/Reggae_2/Save_the_Kwiatki/Fire_Exit/
   A_Load_of_Cowbell/Lands/Bach_VC-220).** RESIDUE: Minoam 98.3% /
   Conanious 96.2% small end-of-song tail (V1/V2 SR + V3 freq late diffs,
   the diverse partial long tail -- NOT filter).
   **✅✅ FAMILY-3/5 CLOSEOUT (commit d46146f): 354/1495 FULL (23.7%; 42.4%
   of the 835 supported full+partial).** Full batch (tmp/dmc_v5_full_results
   .jsonl) -> mass-wrote all 354 .usf + .sidfinity.sid (0 err,
   tools/dmc_v5_mass_write.py) + hvsc84.db refreshed. RESIDUE: 481 partial
   (diverse long tail: Minoam/Conanious end-of-song V1/V2-SR + V3-freq tail,
   + state-only Check-A + freq/PW buckets); 593 unsupported (no_jumptable
   261 reloc/CIA + player_code_mismatch 266 sub-builds + note_out_of_range
   27 + cia 13 + wave/pulse-overflow + trailing-cmds); 67 error
   (_capture_env ptr-overflow 45 + unknown-sector-cmd 12 in relocated/corrupt
   + timeout 8).
   **✅✅ RELOCATED/WRAPPER-INIT UNLOCK (commits 0e3c319 + 023c1b6 + 5f3a0de):
   354 -> 461/1495 FULL (+107; 30.8% of 1495, 41.9% of supported).** The
   no_jumptable (261) + player_code_mismatch (266) buckets were 477/527 the
   SAME family-3/5 player with a RELOCATED or WRAPPED init: play body still
   at base+$A1, but the init MOVED elsewhere and/or its A-reg prefix differs
   (LDA #0 single vs ASL*3 song-indexed). Old factory keyed base off the
   jumptable LOCATION (+$40/+$A1) and compared the WHOLE player -> any
   moved/re-prefixed init rejected. FIX (family-1/2 sub-build playbook, V5
   form): base = play_target - $A1 (play is the reliable anchor); validate
   the PLAY-reachable body only (_v5_play_ref $10A1-$170E); validate the
   init by its orderlist-copy SKELETON at the jumptable's init target +
   read op_orderlist from THAT init's actual load operand (init_target+7) ->
   relocated/wrapped init handled. base-plausibility margin = base+$848
   (only code+state $1006-$1845 relocate; data tables are packer-patched;
   the $1900 margin wrongly rejected high-load base=$F000 builds -> 2
   regressions, fixed). multi_subtune (36, ASL*3 song-indexed orderlist,
   songs>1) typed-deferred (needs multi-song PSID emit). ~300 members moved
   unsupported->supported; all 461 FULL mass-written + db refreshed.
   RESIDUE NOW (286 unsupported + 640 partial + 108 error): player_code_
   mismatch 152 (deeper code variants — bucket by play-body first-diff PC),
   multi_subtune 36 (multi-song emit feature), note_out_of_range 36,
   no_jumptable 22, error 108 (extract robustness: _capture_env ptr-overflow
   + unknown-sector-cmd in relocated/corrupt).
   **✅✅ MULTI-SUBTUNE SUPPORT (commits b4994d0 + 21e767d): 461 -> 466/1495
   FULL (31.2%; 41.4% of supported), 0 regressions.** Song-indexed orderlist
   record (init reads song# from A: ASL*3; PHA across state clear; PLA; TAY;
   index ordrec by song#*8); data tables (sectors/instr/freq/wave/pulse/
   filter) SHARED across subtunes; one MusicSubtune per record (per-sub
   tempo/master_vol/voices; global leftovers on subtune 0). UNIFIED with
   single-subtune (song#=0 -> Y=0, identical). 5-file change (engine_model
   V5Subtune + extract N records; composer ordrec N + song-indexed init +
   PSID songs=N; to_usf N MusicSubtunes; from_usf pool sectors across all
   subtunes; factory rejection removed). +5 fully FULL (members need ALL
   subtunes FULL; 138 subtune-songs all build correctly); 34 moved
   unsupported->supported. All 466 mass-written + db refreshed.
   RESIDUE NOW (252 unsupported + 660 partial + 117 error): player_code_
   mismatch 160 (deeper code variants), note_out_of_range 38, trailing/wave/
   pulse/cia/no_jumptable misc; error 117 (extract robustness).
   **✅✅ PARTIAL LONG TAIL round 1 — FILTER OFF-TABLE (commit ba63846):
   466 -> 543/1495 FULL (+77; 36.3% of 1495, 47.1% of supported), 0
   regressions.** Biggest partial cluster (FCLO/FCHI bucket ~70+) = the
   filter table is the LAST data region so a_fh-a_fl does NOT bound it; tiny
   tables (2 entries, all insts FL=1) run filter_run PAST the array into the
   overlapping lo/hi arrays + following bytes (ramp lives OFF-TABLE). FIX
   (extract+capture, no composer change): read filter table generously
   (n_filter=min(256,memtop) — filterpos is a byte; off-table bytes = what
   orig reads, 0 past payload = siddump zero-fill); _capture_env count==0 =
   counter wraps 65536 = TERMINAL HOLD (off-table zero-region was spinning to
   sweep_too_long). Also fixed ~28 _capture_env ptr-overflow errors
   (117->89). Direct path already worked (emits table verbatim); only USF
   capture needed it. partial 660->610, all 543 mass-written + db refreshed.
   **✅✅ PARTIAL LONG TAIL round 2 — LOOP-TARGET TRANSPOSE (commit ddaed0c):
   543 -> 683/1495 FULL (+140 — biggest single win; 45.7% of 1495, 59.2% of
   supported), 0 regressions.** The end-of-song cluster (292 partials @>=95%,
   just after the orderlist $FF loop) was ONE root cause despite the diverse
   symptom: the composer's $FF handler treated the loop-target byte as a
   sector#, but MANY orderlists loop back to a LEADING $FC/$FD transpose
   (Minoam: all 3 voices loop to pos 0 = $FC). The orig's $FF -> $111F
   re-dispatches the loop target through the $FD/$FC checks. FIX (1 line):
   $FF handler `jmp tf_chk_fd` (sector# targets fall through unchanged; a
   FULL can't regress — never hit the path). Minoam FULL (its "pulse
   off-by-one" was downstream of this loop). partial 610->470, all 683
   mass-written + db refreshed. **METHODOLOGY (CLAUDE.md): from here, iterate
   on a STRATIFIED SUBSET (~120, by first-diff bucket + FULL slice, ~5min),
   full-batch ONLY at closeout.**
   **✅✅ ROUND 3 — LOOP-POSITION + TRANSPOSE RE-ESTABLISHMENT (commit e882c10):
   683 -> 842/1495 FULL (+159), 0 regressions** (the USF round-trip loop-target
   bugs: to_usf loop_to via group-start bytes + loop_transpose re-establishment,
   negative loop@N-T grammar). **✅ ROUND 4 — this session (commits 575492b +
   40f496d): 842 -> 848/1495 FULL (56.7%), 0 regressions.** Two parts: (a) a
   carry-target loop fix — round-3 only handled loops targeting the transpose
   PREFIX (re-establish); a loop can also target the entry byte PAST the prefix
   (CARRY, transpose persists over the wrap), which fell to loop_to=0 and
   REGRESSED 5 ex-FULL members (Metropolitan/Fast_and_Slow/Trance/Techno_2/
   Deep_Inside). _orderlist now maps each byte to (entry, is_prefix); monotonic.
   (b) wrapper/trampoline detection (follow a 1-hop `JMP base+$A1`; resolve init
   skeleton among [jt-target, JMP-follow, base+$40]) — +Background_Pleasure.
   **TOOL: `tools/divergence_census.py`** (see [[reference_divergence_census]]) —
   clusters the residue. KEY FINDING: **detection ≠ FULL** — the 153
   player_code_mismatch are NOT the FULL bottleneck (detecting them just exposes
   downstream bugs); the verify-PARTIALS are.
   **✅ ROUND 5 — STATIC PULSE/FILTER HOLD (commit 266a5b5): 848 -> 875/1495
   FULL (+27, 58.5%), 0 regressions.** The "67 check_A_state_only" cluster was a
   RED HERRING — 0 were init-priming; all were `shift_d=None` trichotomy
   alignment failures (early play divergences desync the midpoint landmark;
   init prefixes match, d=0). TRUE first-divergence histogram: ~34 pulse-width
   (clean 2x-ramp signature), ~18 filter, ~13 frequency. Root cause of the
   pulse cluster: `from_usf.add_env` emitted `[start][$90->start]` for a STATIC
   env (phases=[]); the engine re-reads the START pair as an ADD step → ramps
   +start.hi/frame instead of holding (Hardcore_DMC $D403: orig holds 8; rebuild
   8,16,24,32...). Fix: static env loops on a ZERO-ADD with count==0
   (65536-frame hold). Shared by pulse+filter. Also `verify_cycle` fallback now
   reports first_play_diff (16c4053, diagnostic).
   **✅ ROUND 6 — DEFAULT (IDLE) V3 FILTER SWEEP (commit 86d3259): 875 -> 889/1495
   FULL (+14, 59.5%), 0 regressions.** The engine runs filter_run_v3 for V3
   EVERY frame from filterpos=0, where filter-table position 0 is a DEFAULT
   (idle) cutoff sweep no instrument points at — applied to the leftover cutoff
   from song start (for tunes whose V3 never plays a filtered note, this is the
   whole filter motion, e.g. Glory_Kingdom). The composer nulled entry 0 + gated
   filter_run on a sticky filt_run_on flag → never ran the idle. FIX (principled
   per the rep-principle + init trichotomy): new top-level USF `default_filter`
   (a SweepEnvelope — same form as Instrument.filter_env, Rule 1) carrying the
   PLAY-TIME sweep; init.sid.filter keeps only the priming STATE (initial
   cutoff). Composer runs filter_run for V3 from frame 0 (gate removed; pos 0 =
   the idle sweep, or a (0,0) hold). Shared USF plumbing (types/grammar/parser/
   writer/docs) — full tools/regression.py GREEN (0 cross-engine regressions).
   **✅ ROUND 7 — SONG-DERIVED SWEEP CAPTURE HORIZON + walk-cap (commit 5b32e79):
   889 -> 891/1495, 0 regressions.** `_capture_env`'s fixed `_REACH_FRAMES=30000`
   capture budget (a magic number, safe only because 30000 > every 1x song's
   window) replaced by the actual per-song horizon `reach = min(songlen*1.1,
   1500)*50` play-frames (verified V5 = all vblank; CIA rejected, so 50Hz exact),
   computed in write_v5_usf from cached Songlengths.md5, threaded to _capture_env.
   Needed (not "capture whole program") because from_usf DE-FUSES the packer's
   byte-overlapped programs, so a full capture can exceed the 256-entry table;
   bounding at the window keeps it fitting. Helps both ways: SMALLER for short
   songs (fixed filter_table_overflow: Hot_Island, Progress = the +2) / LARGER
   for >545s (closes the old under-capture hole). Plus `_WALK_CAP=5000` iteration
   seatbelt (reads, not frames): a malformed $90->$90 chain spun _capture_env
   forever (900s batch timeouts / infinite hang in tools) — now an instant
   `unsupported:capture_loop` (timeout 10->0, +9 capture_loop). Idle-filter
   capture best-effort. (Came out of the owner's "why 30000, not songlen*1.1?"
   question — their instinct was right; "capture complete program" over-corrected
   into 2 overflow regressions before landing on the per-song window.)
   **✅ ROUND 8 — DEFAULT (IDLE) PER-VOICE PULSE SWEEP (commit a4c70c8): 891 ->
   913/1495 FULL (+22, 61.1%), 0 regressions.** Pulse twin of default_filter: the
   `rebuild=0` cluster is a real idle pulse program at pulse pos 0 (Doomed V2
   $D409 = 0,49,98,147,196 = pulse[0]=(0,49) loop) the composer nulled. Carry as
   `default_pulse` (PW SweepEnvelope), emit at pulse pos 0; pulse_run runs it from
   pulsepos=0 (UNCONDITIONAL — `run_effects` JMPs to pulse_run; NO per-voice gate;
   $1841 only gates the note-time LOAD). **CORRECTION to a wrong earlier note: I
   hypothesized a "per-voice pulse-active gate" — there is NONE.** The first cut
   regressed 891->786 (-135) NOT from the idle ramp (all 135 regressed have
   pulse[0]=(0,0), no idle) but from changing the NO-IDLE case from single (0,0)
   to a 3-entry hold (shifted the de-fused table). Fix: keep single (0,0) for
   no-idle (byte-identical → can't regress); emit idle only when pulse[0] is a
   real ADD. Lesson: a no-idle "layout cleanup" is NOT free (de-fused table is
   position-sensitive). NEXT V5 (ranked): (1) FREQUENCY clusters (~143 across
   V1/V2/V3 freq regs — BIGGEST, likely vibrato/glide); (2) remaining pulse
   partials w/ a SECONDARY divergence (idle now fixed: Doomed/Amiga-Zak); (3)
   NON-idle filter bugs (Emulating_Vinkuna/Cooksey/Art_of_Noise); (4)
   player_code_mismatch; family-4 (+$95). Full detail in RE_NOTES.
   **DONE: DB migrated SQLite -> git-tracked CSV (hvsc84.csv) + DuckDB CLI
   (see [[reference_hvsc_db.md]] / CLAUDE.md).**

## REGRESSION PORTFOLIO (2026-06-13): generalized + DMC wired
`tools/select_regression_portfolio.py` made engine-parametric (registry:
engine -> jsonl/out/feature_fn/witnesses/sid_key; exact_multicover stays
engine-blind). DMC feature extractor + `tools/dmc_regression_portfolio.json`
wired as tier-1 in regress_dmc(). The closeout step is now standard
(documented in CLAUDE.md + migrate skill): family reaches FULL coverage
-> derive portfolio -> wire tier-1 (full family batch = tier-2).

## Off-table-freq de-verbatim (v5) — DONE 2026-06-21, LOSSLESS

The v5 `freq_overrun` blob (verbatim post-freq-table bytes, the C7 anti-pattern) is
ELIMINATED. Replaced by per-instrument `Instrument.offtable_freq` = list of
`(offset, note, freq_lo, freq_hi)`, `idx=(offset+note)&$FF` (USF schema in
src/usf/{types,grammar,parser,writer}; extract `_assign_offtable_freq`; composer
`composer_v5` builds in-bounds extended freqlo/freqhi from it — no OOB read).
**1041 FULL = the freq_overrun baseline, 0 regressed.** Full design + evidence:
`docs/offtable_freq_plan.md` + `pipelines/dmc/v5/RE_NOTES.md` rounds 11-18.

WHAT THE OFF-TABLE IS (verified, rounds 12-18): the player's wave-program freq
lookup `freqlo/hi[wave_offset+note]` has NO bounds check; for notes that overshoot
past the 96-entry table it sonifies the engine's own work-RAM (orderlist POINTERS
= addresses, counters, track-sequence bytes) in the fixed `$17CF-$1877` gap.
UNDOCUMENTED (full online sweep) but the v5 expression of the documented DMC4/7
"DRUM EFFECT = pitch steps in higher range" idiom; player binary is sole authority
(kept under `pipelines/dmc/docs/src/`). ~1/3 of load-bearing reads are audible
(noise drums / tri tones), ~2/3 inaudible. Capture SITES (all needed): wave-program
steps + offset-0 BASE read (vib_setup `base-note freq<<width`, note freq, glide
arrival) + the lead-in IDLE program (wave index 0) x lo_notes.

LESSON: the "load-bearing residue" bugs (Redemption_6_4, Planet_Love) were CAPTURE
GAPS (missing off-table read sites), NOT glide/vibrato/wave-position effect bugs —
my diagnosis was wrong twice until I TRACED (state via composer xa65 return_labels
vs orig memwatch) instead of assuming. **Phase 6 DONE 2026-06-21:** FC migrated to
the SAME `offtable_freq` mechanism (cross-family unification — 2528 FULL lossless;
see [[project_fc_fingerprint_and_standard]]), surfacing the dual lo/hi-read window
bug + the close_tol 64→80 boundary fix. Phase 7 (remove the `freq_overrun` field
from the shared schema, now both consumers are off it) is the remaining cleanup.

## Related
[[project_fc_fingerprint_and_standard]] (the playbook this follows),
[[feedback_dataflow_over_heuristics]] (the operand-patching finding is
exactly this), [[feedback_disassembly_data_section]] (research.md's wrong
tables), [[feedback_init_trichotomy]] (the $1018 leftover).
