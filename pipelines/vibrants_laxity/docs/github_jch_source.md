---
source_url: https://archive.org/details/jch_c64_zip
fetched_via: curl (jch_c64.zip downloaded to /home/jtr/sidfinity/tmp/vibrants_laxity_research/jch_c64.zip)
fetch_date: 2026-06-15
author: Jens-Christian Huus (JCH / Chordian) of Vibrants
content_date: 1995-09-16 (archive release date)
reliability: primary
---

# JCH Complete C64 Music Collection — NewPlayer Source / Editor

The `jch_c64.zip` archive on archive.org is JCH's complete release of his C64 music
and tools circa 1995. It contains source code for his editor (v3.03) and the original
Laxity-format tunes.

## Archive contents (top-level)

```
OLD_PLAY.ZIP   — Older player versions
LAXITY.ZIP     — Tunes made in Laxity's original player (1988, pre-NewPlayer era)
NP_00-05.ZIP   — NewPlayer v00-v05 tunes + READMEs
NP_06-09.ZIP   — NewPlayer v06-v09 tunes
NP_10-14.ZIP   — NewPlayer v10-v14 tunes
NP_15-20.ZIP   — NewPlayer v15-v20 tunes + README (saved to docs/src/)
DIGI.ZIP       — Digi/sample tunes
DOUBLE.ZIP     — Double-speed tunes
GAMES.ZIP      — Game music
SOURCE.ZIP     — *** EDITOR SOURCE CODE: ED37_SRC.TXT (96KB) ***
ED_TEXTS.ZIP   — Editor documentation texts
D64.ZIP        — D64 disk images (editor + players as C64 binaries)
-README-.TXT   — Top-level description
```

## Source file: ED37_SRC.TXT

This is the 6502 assembly source for "JCH's NewPlayer EDITOR v3.03" (~5697 lines).
Saved to `docs/src/jch_editor37_source.txt`.

### Memory map (from source header comments)

```
$0900-$093F   BUFFER   — TrackCopy buffer
$0A00-$0E3F   DISK1    — Diskmenu print-frame
$0F00-$45D3   MUSIC    — Player + music data ("Drax's FUNKY" example tune)
$C800-$CFE0   DISK2    — Diskmenu code
$CF00-$CFFF   JMPS     — sys $CF00 and jmp($CFFE)
$E000-$E2BD   TABLES   — Player version tables
$A000-$????   EDITOR   — The editor assembly listing itself
```

The MUSIC region ($0F00 onwards) is the player binary + music data blob.

### Key player addresses (extracted from editor source code)

The editor accesses the NP player data at fixed offsets from $0F00:

```
$0FA6         init data pointer (pointer to init table — word)
$0FB4         not used
$0FBA         fine tune table pointer (word)
$0FBC         wave table pointer (word)
$0FC0         filter table pointer (word)
$0FC2         pulse table pointer (word)
$0FC4         instrument table pointer (word)
$0FC6         orderlist V1 pointer (word)
$0FC8         orderlist V2 pointer (word)
$0FCA         orderlist V3 pointer (word)
$0FCC         sequence vector low-byte table pointer (word)
$0FCE         sequence vector high-byte table pointer (word)
$0FD0         command table pointer (word)
$0FEE         player version string (e.g. "20.G")
$0FF4         quantize value for SHIFT-RETURN in editor
$0FFF         various flags byte (wave counter init, etc.)
$1000         player init entry point (JSR $1000)
$1003         player update entry point (JSR $1003) — called each frame
$1006         "quick-speed" player 2nd update entry point
$1021-$1022   "PL" signature bytes (used to detect player type)
$103F         "-" signature byte
```

The **version string at $0FEE** is "20.G" for JCH NewPlayer v20.G0 (the SF2 NP20 converter
checks for bytes: '2', '0', '.', 'G' at $0FEE+0 through +3).

### Zero-page variables used by the player (from editor source label assignments)

```
$A0  voicon    — voice icon (octave tracking)
$A2  vol       — volume
$A4  credits
$A6  tpoin     — track pointer
$A8  sinit     — song init
$AA  ain       — ?
$AC  getinit
$AE  getcom
$B0  get2
$B2  getins
$B4  real
$B6  setsid    — set SID
$B8  notes     — note table pointer
$BA  fintun    — fine tuning pointer
$BC  arp1      — arpeggio table pointer 1
$BE  arp2      — arpeggio table pointer 2
$C0  filttab   — filter table pointer
$C2  pulstab   — pulse table pointer
$C4  instr     — instrument table pointer
$C6  v1        — voice 1 state pointer
$C8  v2        — voice 2 state pointer
$CA  v3        — voice 3 state pointer
$CC  lobyt     — low byte temp
$CE  hibyt     — high byte temp
$D0  slidtab   — slide table pointer
$D2  s0        — state 0
$D4  s1        — state 1
$D6  s2        — state 2
$D8  s3        — state 3
$DA  gat       — gate register
$DC  nog       — no gate
$DE  trans1    — transposition 1
$E0  sflag     — sound flag
$E2  not       — note
$E4  vhzl      — vibrato HZ low
$E6  vhzh      — vibrato HZ high
$E8  next      — next step
$EA  insnr     — instrument number
$EC  ge02
```

### Historical lineage (from LAXITY.ZIP README)

1988: Laxity created his own player. JCH got a copy and composed tunes in it.
1988: Laxity told JCH to stop using his player → JCH created "NewPlayer".
Later: Laxity joined Vibrants (JCH's group); both became founding contributors to SF2.

The NP player versions are NP_00 through NP_20:
- v17.G0, v20.G4 = standard NP versions used by many composers
- v20.Q0 = "quattro" (multi-speed variant)
- The NP_15-20 README confirms v19 = "compromise player" (no vibrato, very small)

### NP20 data layout (from SF2 converter_jch.cpp analysis)

The JCH NP20 format is a PRG file loaded at $0F00. Table locations are NOT fixed;
they are stored as words (pointers) in the player header region:

| Pointer address | Points to        |
|-----------------|------------------|
| $0FBA           | Fine tune table  |
| $0FBC           | Wave table       |
| $0FC0           | Filter table     |
| $0FC2           | Pulse table      |
| $0FC4           | Instrument table |
| $0FC6           | Orderlist V1     |
| $0FC8           | Orderlist V2     |
| $0FCA           | Orderlist V3     |
| $0FCC           | Seq vector lo    |
| $0FCE           | Seq vector hi    |
| $0FD0           | Command table    |
| $0FA6           | Init data ptr    |

**Instrument table format (row-major in NP20, converted to column-major in SF2)**:
The SF2 converter uses `CopyTableRowToColumnMajor()` for instruments and commands,
meaning NP20 stores them row-major (all bytes of instrument 0, then instrument 1, etc.)
while SF2 uses column-major (all AD bytes, then all SR bytes, etc.).

**Orderlist format (NP20 raw)**:
Pairs of (transpose, sequence_index). Terminate with transpose=$FF.
- transpose $FF → loop back (followed by loop target index)
- transpose = signed byte; SF2 adds $20 to convert: `sf2_transpose = 0x20 + np20_raw_transpose`

**Sequence format (NP20 raw)**:
Each event = 2 bytes: (command_or_instrument, note).
- command_or_instrument < $C0 → instrument byte; note = note value
- command_or_instrument >= $C0 → command byte; note = note value
- $7F in command position → end of sequence
The SF2 converter skips the first 2 bytes of each sequence (likely length/header bytes).

**Speed / tempo**:
The speed setting is at `init_data_ptr + 6` (i.e., `$0FA6` dereferenced + 6).
Special case: if speed < 2, the filter table encodes alternating fast/slow tempo bytes
at filter_table+0 and filter_table+1 (multispeed via CIA timer swap).

## Files saved

- `docs/src/jch_editor37_source.txt` — full 96KB editor assembly source
- `docs/src/laxity_orig_readme.txt` — README from LAXITY.ZIP (history)
- `docs/src/jch_np15_20_readme.txt` — README from NP_15-20.ZIP (tune list + history)
