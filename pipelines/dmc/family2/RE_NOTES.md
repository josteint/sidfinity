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

## Write-log loop progress (Kajun_Klog, divergence pushed forward)

Sector layer → frame 2 → frame 3 → **frame 7** so far (each fix reveals
the next effect difference). DONE:

- **Cymbal timing (commit pending).** Family 2's noise burst fires on
  FRAME 2 (frame 1 = normal note, frame 2 = $FFFF+$81, frame 3+ =
  normal), NOT frame 1 like canon — the note-init `JMP $1591` skips the
  cymbal, which fires per-frame via the $1300 guard==2 check. Modeled as
  `params.cymbal_onset` (0 canon / 1 family2); the composer emits the
  burst at note-init (0) or in run_effects at guard==2 (1). Frame 2 now
  matches exactly. A musical timing parameter (§ principled).
- **vib_depth_curve USF field** (96 bytes, family-wide engine content
  by reference; empty = canon VIBDEPTH). Serialized (writer/parser).

OPEN — **family-2 vibrato is a DIFFERENT MECHANISM (current blocker @
frame 7).** Canon: note-init loads the per-note step from the $1888
VIBDEPTH table → $1792 (vstep), delayed by byte7-hi. Family 2:
note-init does `LDA $16A7,y (freq HI) / LSR / STA $178C` — a SEPARATE
register, and $1792 (vstep) is left 0. Evidence: with vib_depth_curve
= [0] (current placeholder, vibrato disabled) frames 3-6 match, then at
**frame 7 the original drops V1 freq by $02 = freq_hi($05)>>1** — so
family 2 DOES vibrato via freq_hi>>1, but with a longer delay (~6
frames) than byte7-hi gives. Needs: disassemble family 2's $178C usage
+ its delay/application (the $13xx effect path, which DIFFERS from canon
in the note-init tail) → a family-2 vibrato model in the composer
(step = freq_hi>>1, family-2 delay). The current [0] placeholder is a
partial (early frames exact, the delayed vibrato missing).

NEXT: (1) RE family 2's vibrato ($178C step + delay) → composer model;
(2) iterate find_first_divergence (more effect differences may follow —
the ~119-byte note-init-tail divergence isn't fully decoded); (3) once
Kajun is FULL, factory variant (detect init JMP base+$37 ->
sector_format='family2' + cymbal_onset=1, op sites = canon, instr base
from operand, d417=base+$34, vib curve) + carved reference + wide batch.

Tractability note: family 2 is the same engine but its EFFECT CHAIN has
several genuine differences (cymbal timing, vibrato mechanism, + the
undecoded note-init tail). Each is a focused RE step — more than the
2-entry/relocation variants, less than a new engine.

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
