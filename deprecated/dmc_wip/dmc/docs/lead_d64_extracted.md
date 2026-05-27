---
source_url: https://csdb.dk/download.php?id=210838, https://csdb.dk/download.php?id=210837, https://csdb.dk/download.php?id=87688
fetched_via: direct
fetch_date: 2026-04-11
author: unknown
content_date: 1994-01-01
reliability: primary
---

# DMC D64 Extraction Report

## Tool Written

`/tmp/d64extract.py` — Python D64 extractor supporting:
- Standard 1541 35-track D64 images (174,848 bytes)
- Sector chain following, directory reading, file extraction
- PETSCII-to-ASCII conversion for text files
- Heuristic text-file detection

## Disks Attempted

### CSDb ID 210838 (`dmc6-docs.txt` → `/tmp/dmc6-docs.d64`)
**Result: Packed/single-file cracker intro — NOT DMC documentation**

174,848 byte D64. Directory shows 1 file: `"u2 pic"` (PRG, 3,522 bytes).
This is a C64 cracker group intro, not DMC release material.
The CSDb URL for "dmc6-docs.txt" resolved to unrelated content.

### CSDb ID 210837 (`dmc version6.D64` → `/tmp/dmc6-disk.d64`)
**Result: Packed/single-file demo — NOT a standard DMC disk**

174,848 byte D64. Directory shows 1 file: `"sky n0.5 demo ii"` (PRG, 13,791 bytes).
Contains a BASIC program with SYS+machine code. Single-file packed release.
Not a usable DMC tool disk.

### CSDb ID 46836 (`DMC_5.1y_ONS.zip` → `Dmc5_1Y.d64`)
**Result: Valid multi-file DMC 5.1y disk — DOCS are a demo scroller**

Disk label: `"ons toolz"`. Contains 4 files:

| Filename | Size | Type |
|---|---|---|
| `d.m.c. v5.1y [O]` | 8,558 bytes | PRG — DMC player |
| `5.1y packer! [O]` | 6,190 bytes | PRG — DMC packer |
| `dmc 5.1y docs [O]` | 11,859 bytes | PRG — demo scroller (see below) |
| `dmc 5.1y s.re [O]` | 5,550 bytes | PRG — unknown (sound replay?) |

### DMC 5.0+, 5.1x, 4.y Pro
All have identical structure: player + packer + "note" scroller.
None contain plain-text documentation files.

## DMC Docs File Analysis

### Format
The `dmc 5.1y docs [O]` file is a **C64 demo intro with scrolltext**, not a structured
documentation file. Load address `$0801`. BASIC `SYS 2059` jumps to machine code.

### Decompressor
Machine code at `$080B` copies 256 bytes from `$3579` to zero page `$00FB`
(the display engine + ZP initialization), then jumps to `$0100`.

The display engine at `$0100` reads 256 bytes at a time from a pointer in
ZP `$FC/$FD` (initially `$3479`) and writes directly to screen RAM at `$071C+Y`.
The pointer decrements by 1 byte per scroll tick — character-level vertical scrolling.

### Why Plain Text Extraction Fails

The 11,628 bytes of scroll text data (file offsets `$0E`–`$2D79`) are stored as
**C64 screen codes**, not PETSCII or ASCII. C64 screen codes use a completely
different mapping than ASCII:

- Screen code `$00` = `@`
- Screen codes `$01`–`$1A` = `A`–`Z`
- Screen codes `$20`–`$3F` = space through `?` (same as ASCII)
- Screen codes `$40`–`$5F` = C64-specific graphics characters
- Screen codes `$60`–`$7F` = additional graphics
- Screen codes `$80`–`$FF` = reverse-video versions of above

Only ~56% of bytes fall in the printable ASCII range (`$20`–`$7E`).
The remainder are C64 graphics characters used for decorative borders,
color fills, and visual presentation that only render correctly on VIC-II hardware.

### Emulation Attempt

The file was run in py65 (project's 6502 emulator at `tools/py65_lib`):
- Decompressor executed successfully
- Display engine reached correctly (loops at `$01C5`)
- Screen RAM at `$0400`–`$07E7` filled with screen codes including heavy graphics

Simulating 200 scroll pages captured the screen codes, but the content is
visually-formatted C64 art, not parseable ASCII text.

### Readable Text Fragments Recovered

The following ASCII-range strings were found embedded in the scroll data:

| Offset | String | Context |
|---|---|---|
| `$0085` | `"WORLD` | Greeting text: `"world in hm..."` |
| `$0097` | `BYE6PRI'94` | Farewell: `bye spring '94` (release date: spring 1994) |
| `$11D1` | `DUCTION` | Part of `PRODUCTION` |
| `$12DA` | `EDITOR` | DMC editor reference |
| `$148D` | `NEW` | New feature mention |
| `$168E` | `UN,mEDITOR` | EDITOR reference with decoration |
| `$1C9F` | `TABLE` | Data tables reference |
| `$2005` | `mEDITOR` | EDITOR reference |
| `$298C` | `DMCwunq` | Tool name `DMC` |
| `$2996` | `LAYrT` | Likely `PLAY` function |
| `$2A09` | `PACKE` | `PACKER` (DMC packer) |
| `$2B08` | `CATOR` | Likely part of `OSCILLATOR` or `CALCULATOR` |

### Conclusion

The DMC 5.1y docs file is a **spring 1994 release intro** (demo scene presentation)
with greetings to other groups and brief feature mentions, embedded in a fancy
C64 character-art scroller. It is **not a structured technical manual**.

No plain-text DMC documentation was found in any of the D64 images downloaded
from CSDb. The actual DMC format knowledge useful for `dmc_to_usf.py` must come
from reverse-engineering (as already done in `src/dmc_parser.py`).

## D64 Format Knowledge Confirmed

The Python extractor works correctly for standard 1541 D64 images. Key format facts
verified against the disks:

- Track layout: tracks 1–17=21 sectors, 18–24=19, 25–30=18, 31–35=17
- Sector size: 256 bytes; each sector starts with [next_track, next_sector]
- Directory at track 18, sector 1+ (BAM at track 18, sector 0)
- 8 directory entries per sector, 32 bytes each
- File type byte: `$82`=PRG, `$81`=SEQ, `$00`/`$80`=DEL (used for directory art)
- Last sector: first byte=0, second byte=bytes-used (1-indexed from byte 2)
- PETSCII disk names use `$A0` as padding (treated as space)

## What DMC Documentation Exists

From `src/dmc_parser.py` (already reverse-engineered):

**Sector encoding:**
- `$00`–`$5F` = Note (C-0 through B-7, 96 notes)
- `$60`–`$7C` = Duration (value `AND $1F` = ticks)
- `$7D` = Continuation (no ADSR reset on next note)
- `$7E` = Gate off
- `$7F` = End of sector (V4) / `$FF` (V5)
- `$80`–`$9F` = Instrument select (`AND $1F` = instrument number)
- `$A0`–`$BF` = Glide command (`value - $A0` = semitones)
- `$C0`–`$DF` = Additional commands

**Instrument layout (11 bytes):**
byte 0=AD, 1=SR, 2=wave_ptr, 3=pw1, 4=pw2, 5=pw3, 6=pw_limit, 7=vib1, 8=vib2, 9=filter, 10=fx

**Version detection:**
- V4: code pattern `FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D`
- V5: code pattern `BC ?? ?? B9 ?? ?? C9 90`

**Layout:**
- Freq table (192 bytes hi+lo) → instruments (+`$0248` from freq_hi in V4, dynamic in V5)
- Sector pointer table: two arrays of N bytes (lo, hi) pointing to sector data
