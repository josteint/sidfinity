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

2. **DIFFERENT SECTOR ENCODING — the blocker.** Family 2's sector-end
   check (canon sub_11E6 @ $11E6) is **`CMP #$FF`**, NOT `CMP #$7F`.
   So the sector TERMINATOR is **$FF**, and the whole sector-command
   byte map is shifted (the canon $7F terminator / $F0-$FF VOL range no
   longer hold). Sample sector @$1A2F:
   `61 90 1D 29 1D 29 1D 29 1D 29 FF 60 90 02 FE FE FE FE FE FE FE FF ...`
   — decodes plausibly as note/instr/duration with $FF as the end, but
   the $7E/$7D/$7C/$F0 command semantics must be RE'd (the family-2
   dispatch tests $60/$90/$C0/$FE/$FF, missing canon's $7x set in the
   trace). This needs a family-2 sector decoder (extract) + the
   composer's family-2 pattern encoding.

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
