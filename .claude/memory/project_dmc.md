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

## ✅✅ FAMILY-1 WIDE BATCH (2026-06-13): 2257/5401 FULL (41.8%)
Full sweep on the fixed pipeline: **2257 full / 178 partial / 453
error / 2513 unsupported.** Of the 2888 FACTORY-PASSING members, 78%
instruction-sequence exact at full songlength. 2257 .usf +
.sidfinity.sid mass-written (0 errors, tools/dmc_mass_write.py);
hvsc84.db refreshed (2257 DMC sidfinity_md5 + usf_path).
Ear test PASSED on Zaks (user).

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
1. **RELOCATION CLASSES (~1800, highest value):** nonstandard_vectors
   (1184, same skeleton at a different base — FC-reloc-factory analogue,
   load-relative operand probe) + the relocated 2-entry layout (~621,
   `player_code_mismatch` @ $1001: 2-entry jumptable, body shifted —
   needs a 2nd canonical ref binary).
2. Other code-mismatch sub-builds (~430: $1181/$1631/$12A8/...).
3. Second loop-hook variant (~277: `c8 20 4d` site = different hook addr).
4. offtable_live + zero-wave-table edge errors (453, mostly correctly
   refused — genuinely live state).
5. Partial long tail (178: bucket by first_diff in the jsonl).
6. Then family 2 (0.732 V4-derived, 2889); V5 line needs sector-encoding RE.

## Related
[[project_fc_fingerprint_and_standard]] (the playbook this follows),
[[feedback_dataflow_over_heuristics]] (the operand-patching finding is
exactly this), [[feedback_disassembly_data_section]] (research.md's wrong
tables), [[feedback_init_trichotomy]] (the $1018 leftover).
