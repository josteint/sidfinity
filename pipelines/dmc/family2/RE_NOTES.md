# DMC family 2 — RE notes (V4-derived variant, 2889 SIDs)

Census family 2: 2889 members, 0.732 Jaccard to V4 canonical (vs
family 1's 0.973). Representative: `DEMOS/G-L/Kajun_Klog.sid`
(load/init $1000, play $1003). Characterized 2026-06-13; NOT yet
migrated.

## What family 2 IS

The **same V4 engine core** as canonical, RE-LAID-OUT and with a
DIFFERENT SECTOR ENCODING. Hard evidence:

- **Jump table** `4C 37 10 4C 85 10 4C 2F 16 4C 3E 16` = init JMP
  $1037 / play JMP **$1085** / all-off **$162F** / sfx **$163E**.
  3 of 4 entries are the CANON addresses; only init differs ($1037 vs
  canon $101D). The distinguishing signature for the factory is the
  init-entry offset $37 (the canon-shared play/all-off/sfx offsets
  $85/$62F/$63E confirm the lineage).
- **Play body @ $1085 and all-off @ $162F are BYTE-IDENTICAL to canon.**
- **~85% of the effect chain matches canon** (large contiguous runs:
  $135A-$13E6, $13EF-$14B1, $14BB-$1508, $1511-$157F = pulse / filter /
  glide / vibrato; $15FD-$1706 = wave step + freq tables). 1368 bytes
  match canon in runs ≥ 16b; the rest differ (operands + relocated
  regions). Overall byte-match at delta=0 is only 9% (operands differ
  per song + the relocated-table regions).
- **Freq tables at $1647/$16A7** (canon addresses).
- **Operand SITES are at canon addresses** (the code reads tables at
  the same code positions): instr $1227, wavectrl $159C, wavefreq
  $15B9, filtdef $1296, tunetab $1051, secp_lo $1103, secp_hi $1108.
  They just read FAMILY-2 table addresses.

## The two real differences (what makes it a sub-migration)

1. **RELOCATED TABLES.** Same 11-byte instrument format + same effect
   semantics, but the tables moved:
   - instrument table at **$17B0** (canon $18F0). Read via the canon
     $1227 site (operand → $17B0). 11-byte records; the note-init reads
     instr+6 at $1257 (LDA $17B6,Y), instr+10 at $1269 (LDA $17BA,Y) —
     same byte layout as canon.
   - **routing shadow ($D417 shadow) at $1034** (canon $1018). Read/
     written at $1270/$1276 (LDA/STA $1034).
   - data tables (per-song) at family-2 addresses (Kajun: wavectrl
     $18AD, wavefreq $1922, filtdef $1997, tunetab $1A27, secp_lo
     $1B75, secp_hi $1B8A). Sector data begins right AFTER the tune
     record (secp[0] = tunetab + 8 = first sector).
   - vibdepth: TBD (canon $1888; family-2 instr table at $17B0 frees
     $18xx — confirm where family-2 reads the per-note vib depth).

2. **DIFFERENT SECTOR ENCODING — RE'd + DONE (commit 09176d4).** The
   full family-2 command map (from the $110C dispatch + sub_11E6
   CMP #$FF end-peek):
     note $00-$5F · instr $60-$7F · duration $80-$BF · glide $C0-$DF
     · switch $FD · rest $FE · END $FF · (no VOL, no soft-start)
   vs canon (instr $60-$7B, soft $7C, switch $7D, rest $7E, end $7F,
   VOL $F0+). `_simulate_sector` is now parametric over `_SecFmt`
   (config.sector_format 'family2'). Family 2 BUILDS + decodes
   correctly with this + canon sites + instr $17B0 + d417 $1034.

## Remaining: effect-semantic differences (the write-log loop)

Family 2's note-init TAIL ($12C9-$1300) differs from canon (the
~119-byte chunk). Found so far (Kajun_Klog first divergence at the
note-init):
- **No note-init cymbal.** Canon falls into the $1300 cymbal check
  after note-init; family 2's note-init ends `$12FD JMP $1591` (straight
  to wave step), SKIPPING it. The $1300 cymbal check still exists (bit7
  + $1786==2 guard, DEC guard) but is reached per-frame, not at
  note-init — so the EXTRACT must NOT emit `noise_attack` from FX bit 7
  for family 2 (inst 1 has byte10=$B0 bit7 set yet plays a normal pulse
  note). The composer cymbal currently fires -> first divergence.
- **Freq-based vibrato depth.** Canon $12F1 `LDA $1888,Y` (per-note
  vibdepth table) -> $1792. Family 2 $12F1 `LDA $16A7,Y` (freq HI of the
  current note) `LSR A` -> $178C. Different source + register. A
  family-2 vibrato-depth mechanism to model.
- vibdepth_addr ($1888) is IRRELEVANT for family 2 (the extract reads it
  but never carries it — composer uses the VIBDEPTH constant; and family
  2 doesn't use the $1888 table anyway).

## ✅ KAJUN_KLOG FULL — write-log loop complete (4 effect-chain diffs)

Kajun_Klog now verifies instruction-sequence exact at full songlength
(`verify_dmc`: 1 subtune, 66674/66674 play writes, trichotomy state ✓;
`find_first_divergence` 67414/67414 = 100%). The write-log loop pushed
the first divergence sector → frame 7 → 15 → 16 → 100% by RE'ing FOUR
genuine family-2 effect-chain differences from canon. ALL four come from
ONE root: **family 2 relocated its instrument table over $17B0-$17FF**,
which clobbered canon's two ADSR-helper subroutines (`sub_17EC`,
`sub_17FB`) and forced inline mask-only / skip variants; plus the
note-init tail + rest dispatch were re-laid-out. All gated behind typed
build-level `params`, defaulting to canon — family 1 + others untouched
(full regression green).

1. **Cymbal timing — `cymbal_onset: 1`.** Burst fires on FRAME 2 (note-init
   `$12FD JMP $1591` skips it; the `$1300` guard==2 check fires it one
   frame later), not frame 1 like canon.
2. **Vibrato swell — `vib_ramp: step`.** Canon loads a FIXED per-note step
   from the `$1888` VIBDEPTH table → `$1792` and DOUBLES the half-cycle
   width as it swells (`$1583 ADC $1774`). Family 2 instead holds a fixed
   width and RAMPS the 16-bit step: note-init `$12F1 LDA $16A7,y (freq HI)
   / LSR / STA $178C`, then each half-cycle boundary `$157F-$158E` does
   `vstep ($1792/$1795) += $178C` (i.e. `+= freq_hi(note)>>1`). The
   per-note increment is DERIVED from the freq table the composer already
   carries — no data field needed. Composer: new `vsteph`/`vdep` regs;
   the triangle add/sub is now 16-bit (`adc vsteph` ≡ `adc #$00` for canon
   since vsteph stays 0).
3. **Holding gate-off — `hold_gateoff: mask_only`.** Canon `$133D JSR $17ec`
   (gate mask `$FE` + AD/SR=$00). Family 2 inlines `$133D STA $100f,x`
   (mask only) — no `$D405/$D406=$00` write (sub_17EC is under the
   relocated instr table).
4. **Hard restart — `hard_restart: none`.** Canon `$11DB JSR $17fb`
   (TEST `$08`→ctrl + AD/SR=$0F0F). Family 2 inlines `$11DB STA $d404,y`
   (TEST bit only) — no `$D405/$D406=$0F` (sub_17FB clobbered).
5. **Rest/switch/slide skip effects — `rest_effects: skip`.** Canon's
   rest($FE)/switch($FD)/slide-tail dispatch ends `$1180 JMP $1322`
   (full effect chain). Family 2 ends `$1180 JMP $1591` (wavestep) — so
   on a tie boundary the vibrato + pulse program HOLD for that one frame
   (re-emit cached freq/pw). This was the subtle one: a periodic 1-frame
   modulator stall, found via the flat per-voice write-log + the
   family-2 sector-dispatch disasm (NOT snapshots).

The `vib_depth_curve` USF field added in the prior session was REMOVED
(derivable from the freq table; schema hygiene).

The `vib_depth_curve` USF field added in the prior session was REMOVED
(derivable from the freq table; schema hygiene).

## ✅✅ FACTORY + WIDE BATCH — 1884/2889 FULL (65.2%)

`dmc_v4_config` gained a family-2 path (pipelines/dmc/v4/factory.py):
detects the family-2 jump table (init JMP base+$37 / play +$85), masked
identity-compares the player region against a carved family-2 reference
(`pipelines/dmc/docs/dmc4_family2_player_1000.bin`, from Kajun, $1000-
$17B0), relocation-aware, then derives the table addresses from the
canon-compatible operand sites (tunetab via $1051, d417 base+$34, instr
base $17B0 from the $1227 operand). The 5 family-2 write-stream knobs go
into `cfg.extra_params` (factory-PROBED, not hardcoded — `hold_gateoff`
varies across sub-builds: STA $100f,x mask-only vs JSR a helper that
also clears AD/SR=$00). Runner: `tools/dmc_family_batch.py --members
tmp/dmc_family2_members.json` (Pool(8), crash-safe).

**Batch (2889 members): 1884 FULL (65.2%)** — exceeds family-1's 54.5%.
Two triage rounds:
- Round 0 = the 4 Kajun effect-chain diffs (above).
- Round 1 (+43): `$129F` filter-mode variant (STA $9E dead store ≡ AND
  #$0F — probe+mask) collapsed player_code_mismatch 74→53; 2-entry
  family-2 jump table (init+play only, all-off/sfx zeroed) collapsed
  no_jumptable 120→52. Sector-decode dead-ends now refuse cleanly
  (unsupported:sector_decode).

RESIDUE (data: tmp/dmc_f2_merged.json):
- **Architectural limit ~580 (20%):** offtable_live 512 + zero_wave 62 +
  wave_marker_chain 5 — the off-table reads land on genuinely live
  per-voice runtime state (same ceiling family-1 hit; correctly refused).
- **partial 279 (9.7%):** diverse FREQ/NOTE divergences — dominated by
  freq-lo diffs ($D40E 57 / $D400 27 / $D407 26) + state=False/no-align
  85. Investigated: NOT off-table per se — e.g. Short_Dream V3 plays
  note 69 (orig) vs 66 (rebuild), a +3-semitone wave-program/arp
  difference; Crush_01 V2 freq SWEEP to $F0 (glide). Per-member-diverse
  long tail (note/wave-program/glide/edited-table edges); the code
  matches Kajun (FULL), so it's DATA exercising paths Kajun doesn't.
- **player_code_mismatch_f2 53 / no_jumptable 52 / sector_decode ~20:**
  remaining sub-builds + relocated-within-file / corrupt-data members.
- KNOWN BUG (not yet fixed, low ROI — needs a member WITH dual instrs):
  the extract reads `dual_phase` (the $40 half-rate slide parity) from
  $1019 (canon); family 2's parity is at $1035. Harmless for the many
  family-2 members with no dual instruments; would need `cfg.dual_phase`
  off=$35 for family 2.

NEXT (further coverage, diminishing returns): the partial freq/note tail
(per-member wave-program/glide RE), the dual_phase fix, the remaining
sub-build sites (player_code_mismatch_f2 by $detail address).

## Migration plan (when picked up)

1. RE the family-2 sector-command byte map (disassemble its dispatch
   chain fully — the $11xx region that differs from canon). Determine
   the terminator ($FF), note/instr/duration/glide/VOL ranges.
2. Carve a family-2 reference player (from Kajun_Klog, mask per-song
   operands) for the factory identity compare (canon won't match — 91%
   differs, though the play body / effect chain do match in runs).
3. Factory: detect the family-2 jump table (init JMP base+$37), use
   canon operand SITES (they align) + read the instr base from the
   operand (relax the `== base+$8F0` assert), d417_shadow = base+$34.
4. Extract: parametrize the sector decoder over the terminator +
   command map (config flag); confirm vibdepth address.
5. The effect chain + instrument format are canon → the composer
   likely needs NO changes (our engine already emits this); only the
   extract's sector decode + the factory site map are family-2-specific.
6. Verdict: verify_dmc (same trichotomy / per-IRQ as family 1).

Tractability: HIGH (same engine + format, only the sector encoding +
table addresses differ) but it's a real focused sub-migration, not a
layout add. Likely one of the documented V4 variants (V4.0 pro /
V4.3 / a re-assembly) — cross-check `pipelines/dmc/docs/` version notes.
