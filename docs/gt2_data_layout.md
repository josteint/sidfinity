# GT2 Packed SID Data Layout

**Date:** 2026-04-02
**Source:** Analysis of greloc.c from GoatTracker V2.77

## Overview

greloc.c builds an assembly source (defines + player.s + data as .BYTE directives),
then assembles it with the Magnus Lind assembler. The data layout after the player
code is fixed and must be reproduced exactly for the player to work.

## Assembly Source Order

1. **Defines** — flag values, parameters, constants
2. **player.s** — the player source code (inserted verbatim)
3. **Frequency tables** — `mt_freqtbllo`, `mt_freqtblhi`
4. **Song table** — `mt_songtbllo`, `mt_songtblhi` (address expressions, not raw bytes)
5. **Pattern table** — `mt_patttbllo`, `mt_patttblhi` (address expressions)
6. **Instrument columns** — column-major, conditional on flags
7. **Tables** — wave, pulse, filter, speed (each left+right, conditional)
8. **Orderlists** — per song per channel
9. **Patterns** — packed pattern data

## Exact Data Section Layout

After player code ends, data is emitted in this EXACT order:

### Frequency Tables
```
mt_freqtbllo:  (lastnote - firstnote + 1) bytes
mt_freqtblhi:  (lastnote - firstnote + 1) bytes
```

### Song Table (address lo/hi for each orderlist)
```
mt_songtbllo:  songs * 3 bytes (lo bytes of mt_songN labels)
mt_songtblhi:  songs * 3 bytes (hi bytes of mt_songN labels)
```
Uses `.BYTE (mt_song0 % 256)` etc. — the assembler resolves addresses.

### Pattern Table (address lo/hi for each pattern)
```
mt_patttbllo:  num_patterns bytes
mt_patttblhi:  num_patterns bytes
```

### Instrument Columns (column-major, ni bytes each)

Always present:
```
mt_insad:         ni bytes
mt_inssr:         ni bytes
mt_inswaveptr:    ni bytes (values already remapped via tablemap)
```

Conditional (flag must be 0 to include):
```
mt_inspulseptr:   ni bytes    [if NOPULSE == 0]
mt_insfiltptr:    ni bytes    [if NOFILTER == 0]
mt_insvibparam:   ni bytes    [if NOINSTRVIB == 0]
mt_insvibdelay:   ni bytes    [if NOINSTRVIB == 0]
mt_insgatetimer:  ni bytes    [if FIXEDPARAMS == 0]
mt_insfirstwave:  ni bytes    [if FIXEDPARAMS == 0]
```

**CRITICAL:** When a flag is 0, the column label + data MUST be present even if
all values are zero. When a flag is 1, the label must NOT exist (the player code
won't reference it). Getting this wrong shifts all subsequent data.

### Tables

Tables are emitted in order: WAVE, PULSE, FILTER, SPEED.
PULSE is skipped entirely if `NOPULSE == 1`.
FILTER is skipped entirely if `NOFILTER == 1`.

Each table has left + right columns. The number of entries = number of USED
table entries (determined by `tableused[]` during packing). **A table can have
0 used entries** — in that case, the label exists but has 0 bytes of data.

#### Wave Table
```
mt_wavetbl:      N bytes (left column, transformed — see below)
mt_notetbl:      N bytes (right column, transformed — see below)
```

#### Pulse Table (only if NOPULSE == 0)
```
mt_pulsetimetbl: N bytes (left column, may be transformed for SIMPLEPULSE)
mt_pulsespdtbl:  N bytes (right column, may be transformed for SIMPLEPULSE)
```

#### Filter Table (only if NOFILTER == 0)
```
mt_filttimetbl:  N bytes (left column, passband bits shifted)
mt_filtspdtbl:   N bytes (right column)
```

#### Speed Table
If any speed feature is used (`!NOVIB || !NOFUNKTEMPO || !NOPORTAMENTO || !NOTONEPORTA`):
```
$00              1 byte  (extra zero prefix)
mt_speedlefttbl: N bytes (left column, raw)
$00              1 byte  (extra zero prefix)
mt_speedrighttbl:N bytes (right column, raw)
```

If NO speed features are used, speed table labels still exist but with 0 bytes.
The extra $00 prefixes are ONLY emitted when speed features are used AND the
table has entries.

### Orderlists
```
mt_song0:  orderlist bytes for song 0, channel 0
mt_song1:  orderlist bytes for song 0, channel 1
mt_song2:  orderlist bytes for song 0, channel 2
```
Each ends with $FF (end marker) + restart position byte.

### Patterns
```
mt_patt0:  packed pattern bytes ending with $00 (ENDPATT)
mt_patt1:  ...
```
Patterns may share trailing bytes (cross-pattern byte sharing optimization).

## Table Data Transformations

greloc.c transforms table data during packing. When reading from a PACKED binary
(already-transformed data), these transformations have ALREADY been applied.
Do NOT re-transform when re-packing.

### Wave Table Left (mt_wavetbl)
- Silent waves ($E0-$EF in .sng): masked to low nibble ($00-$0F)
- If NOWAVEDELAY==0: waveforms in $10-$DF get +$10 added
- Commands ($F0-$FE) and jumps ($FF) pass through unchanged

### Wave Table Right (mt_notetbl)
- For commands ($F0-$FE left): right byte remapped via tablemap for speed/pulse/filter references
- For jumps ($FF left): right byte remapped via tablemap[WTBL]
- For everything else: **right byte XOR $80** (flips relative/absolute bit)

### Pulse Table Left (SIMPLEPULSE only)
- Set-pulse entries ($80+): clamped to $80 (high nibble moved to right byte)

### Filter Table Left
- Set-filter entries ($80+): passband bits shifted: `((left & 0x70) >> 1) | 0x80`

### Speed Table
- No transformation. Raw bytes.

## Index Remapping (tablemap)

greloc.c uses compact sequential indices for all table references:
- Original .sng indices: 1-255 (sparse, many unused)
- Packed indices: 1, 2, 3, ... (dense, only used entries)

`tablemap[table][original_index] = packed_index`

Applied to:
- Instrument columns: wave_ptr, pulse_ptr, filter_ptr, vib_param (speed idx)
- Pattern command databytes: portamento speed, set-ptr targets
- Wave table command right bytes: speed/pulse/filter references
- All table jump targets ($FF left byte)

**When re-packing from a parsed binary:** The data already has packed indices.
The indices match the packed table data we extracted. Do NOT re-remap.

## Instrument Reordering

Instruments are sorted: normal HR first, then no-HR, then legato.
```
Packed index 1..numnormal:                    normal instruments
Packed index numnormal+1..numnormal+numnohr:  no-HR instruments
Packed index numnormal+numnohr+1..end:        legato instruments
```

Pattern data uses the packed instrument indices. When reading from a packed
binary, the indices are already in packed order. Do NOT re-reorder.

## Critical Rules for Our Packer

1. **Emit data we read.** Since we parse from packed binaries, all transformations
   and remappings are already applied. Emit raw bytes, don't transform again.

2. **Match flag-dependent layout exactly.** If the original has NOPULSE=0 (pulse
   column present), our build must also have NOPULSE=0 — even if all pulse values
   are zero. The column's PRESENCE determines the data layout.

3. **Empty tables = 0 bytes between labels.** A table with 0 used entries has the
   label but no .BYTE data. Don't emit placeholder bytes.

4. **Speed table $00 prefix is conditional.** Only emit the extra $00 when speed
   features are used AND the speed table has actual entries.

5. **Use address expressions for song/pattern tables.** Don't pre-compute addresses.
   Use `.BYTE (mt_song0 % 256)` etc. and let the assembler resolve them.

6. **Track byte counts, not abstractions.** Every label, every .BYTE, every
   conditional inclusion changes the absolute address of everything after it.
   Verify with exact byte arithmetic, not "the wave table comes after instruments."
