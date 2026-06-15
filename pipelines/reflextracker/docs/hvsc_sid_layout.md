---
source_url: hvsc84/MUSICIANS/**/*/*.sid + binary analysis
fetched_via: python analysis of local HVSC collection
fetch_date: 2026-06-15
author: reverse-engineered
content_date: 1995-2000 (SID creation dates)
reliability: primary (direct binary analysis)
---

# Reflextracker HVSC SID Layout

## Count

137 Reflextracker SIDs in HVSC #84 (engine='Reflextracker' in hvsc84.db).

## Standard memory layout (confirmed across 10 SIDs)

```
$XXXX - $BFFF: RFX1 + sample data (variable start address)
$C000 - $C7FF: RFXT PLAYER V1.1 (ALWAYS at $C000, exactly 2032 bytes)
--- end of file ---
$C800:         End of loaded data
```

All 10 sampled SIDs end exactly at `$C800`. The player is ALWAYS at `$C000-$C7FF`.

## RSID header format

All Reflextracker HVSC SIDs are RSID v2:

| Field | Value | Notes |
|-------|-------|-------|
| Magic | `RSID` | Real SID (not PSID) |
| Version | 2 | RSID v2 |
| Load addr (header) | `$0000` | Means: take load addr from first 2 bytes of data |
| Init addr | `$C006` | 6 bytes into player = real init entry (SEI; LDA #$36; STA $01; JSR init) |
| Play addr | `$0000` | Self-driven via CIA2 timer (no external play call) |
| Songs | 1 | Always 1 subtune |

## Load address variation

The sample data (RFX1 header + 4-bit audio) starts at different addresses per song,
depending on the total sample data size:

| SID | Sample data start | Total sample size |
|-----|------------------|-------------------|
| Huba_Buba.sid | $3EFC | ~35KB |
| No_Future.sid | $6C64 | ~22KB |
| Hardrave.sid | $5FB3 | ~25KB |
| Mix.sid | $601D | ~25KB |
| Modek_by_Ja.sid | $8E8E | ~14KB |
| Never_More_Depression.sid | $798D | ~18KB |

All end at `$C800`. Smaller songs = higher start address.

## Player entry points

```
$C000: JMP $C02C   ; Entry 1: PLAY (unused in RSID - CIA driven)
$C003: JMP $C016   ; Entry 2: toggle/state check
$C006: SEI         ; INIT (called once by libsidplayfp/PSID driver)
       LDA #$36
       STA $01      ; bank out BASIC ROM ($A000-$BFFF → RAM)
       JSR $C02C    ; call play entry (sets up CIA timer, clears SID)
       ...
```

## Data structure within the SID

```
[load_lo] [load_hi]        ← PRG-style 2-byte load address (little-endian)
$XXXX: 52 46 58 31         ← "RFX1" magic = start of sample/module data
$XXXX+4: [4-bit sample data] ← packed audio (2 samples per byte: hi nibble, lo nibble)
...
$BA00: [32 bytes]           ← sample page table (only if load addr low enough)
$BA20: [32 bytes]           ← sample end-limit table
$BA58: "REFLEXTRACKER 0 MODULE (UNPKD)CODE BY ZORC/REFLEX AND KB/T.O.M"
$BAB0+: [sample names in PETSCII]
$BA60+: [track table and pattern data]
$C000: [RFXT PLAYER V1.1 code] ← 2032 bytes of player code + tables
$C800: end of file
```

Note: The $BA00 region (sample/pattern tables) is only present in songs where
the sample data extends to $BA00. Small songs (e.g. Modek at $8E8E) DO have
their track/pattern data embedded between the sample data and $C000.

## CIA2 Timer A timing

The player sets CIA2 Timer A to value `$0093` (147 cycles). With PAL clock ~985kHz:
- Timer A fires every 147 cycles
- Sample output rate = 985,248 / 147 ≈ **6,702 Hz** sample rate

This is a low-quality digi output by modern standards, but typical for 1995 C64 digi music.

## SID output register

Samples are output to **$D418** (SID master volume register). This is the standard
C64 "digidigi" technique: writing 4-bit values to the volume register at ~6.7kHz
produces audible digi audio. The SID chip's built-in DAC on the master volume register
acts as a crude D/A converter.

## RFX1 magic bytes

Every Reflextracker SID starts with "RFX1" immediately after the 2-byte PRG load address.
The load address itself = the song's first data byte address.

Note: One SID (Never_More_Depression) has load=$798D with RFX1 at $798E (1 byte offset) —
this may indicate a slight variation or alignment artifact.
