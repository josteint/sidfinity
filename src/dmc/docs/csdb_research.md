---
source_url: https://csdb.dk/release/?id=2596, https://csdb.dk/release/?id=2594, https://csdb.dk/release/?id=2629, https://csdb.dk/group/?id=193
fetched_via: direct
fetch_date: 2026-04-11
author: multiple sources (Brian/Graffity as original creator; CSDb community contributors)
content_date: 1991-2025
reliability: secondary
notes: multiple sources — aggregated from CSDb release pages, HVMEC, Lemon64, DeepSID, and sidid.cfg. Most authoritative source is CSDb (primary scene database). Technical format details are secondary analysis with no single canonical spec.
---

# DMC (Demo Music Creator) - CSDb Research

Comprehensive technical research on the Demo Music Creator (DMC) family of C64 music
editors/players, compiled from CSDb, HVMEC, Lemon64, DeepSID, sidid, and other sources.

---

## Table of Contents

1. [History and Lineage](#history-and-lineage)
2. [Complete Version List](#complete-version-list)
3. [Version Family Tree](#version-family-tree)
4. [Data Format (Sector Encoding)](#data-format-sector-encoding)
5. [Instrument Table Format](#instrument-table-format)
6. [Wave Table](#wave-table)
7. [Track/Order List Structure](#trackorder-list-structure)
8. [Player Architecture](#player-architecture)
9. [SIDId Signatures](#sidid-signatures)
10. [DMC V4 vs V5 Differences](#dmc-v4-vs-v5-differences)
11. [DMC V6 Details](#dmc-v6-details)
12. [DMC V7 Details](#dmc-v7-details)
13. [DMC Pro Variants](#dmc-pro-variants)
14. [DMC 4 Editor (2025)](#dmc-4-editor-2025)
15. [Editor Features and Commands](#editor-features-and-commands)
16. [Player Specifications](#player-specifications)
17. [Key People](#key-people)
18. [Source URLs](#source-urls)

---

## History and Lineage

DMC (Demo Music Creator System) was created by **Balazs Farkas (Brian)** of **Graffity**
(Hungary). It evolved from the earlier GMC (Game Music Creator).

### Predecessor: GMC (Game Music Creator)
- **GMC V1.0** (8 Dec 1990) by Brian + Jay of Graffity
  - CSDb: https://csdb.dk/release/?id=7268
  - Included 28 built-in SID tunes
  - Known for "really twisted filtering" capabilities
  - A humorous comment on CSDb suggests it should have been called "DMC V1.0"
- **GMC V1.6** (1990) - "Superiors Game Music Creator System V1.6"
  - CSDb: https://csdb.dk/release/?id=98639
  - Also: https://csdb.dk/release/?id=46470

### DMC Development Timeline
- **DMC V1.2** (4 Feb 1991) - First official DMC release
- **DMC V2.0** (4 Feb 1991) - Same day as V1.2
- **DMC V3.0** (Jul 1991) - Intermediate version
- **DMC V4.0** (Sep 1991) - Major release, became the most widely used version
- **DMC V4.05** (1992) - Minor update to V4
- **DMC V5.0** (1993) - Complete rewrite, much more complex
- **DMC V5.1** (1994) - Final official V5 release by Brian
- **DMC V6.0** (private, ~1994; CSDb release 2018) - Ultra-low rastertime player
- **DMC V7.0** (1995) - By Unreal, based on V4 code, NOT an official Brian release

The development is "mainly split into two programs: DMC 4 and 5" - these are fundamentally
different editors with different data formats and player routines.

---

## Complete Version List

All known DMC releases from CSDb and other sources:

### Official Brian/Graffity Releases

| CSDb ID | Name | Year | Group | Notes |
|---------|------|------|-------|-------|
| 7268 | GMC V1.0 | 1990 | Graffity | Predecessor |
| 98639 | GMC V1.6 Editor | 1990 | Graffity | Predecessor |
| 46470 | Superiors GMC V1.6 | 1990 | Graffity | Predecessor |
| 2598 | DMC V1.2 | 1991 | Graffity | First DMC |
| 10757 | DMC V2.0 | 1991 | Graffity | |
| 79233 | Superiors DMC V2.0 | 1992 | Chromance | Repack |
| 200842 | Superiors DMC V2.1+ | 1991 | Graffity | |
| 98640 | DMC V3.0 | 1991 | Graffity | |
| 2596 | DMC V4.0 | 1991 | Graffity | **Major version** |
| 2597 | DMC V4.05 | 1992 | Graffity | |
| 2594 | DMC V5.0 | 1993 | Graffity | **Major version, complete rewrite** |
| 2599 | DMC V5.1 Package | 1994 | Graffity + Motiv 8 | Bugfix by Iceball |
| 2600 | DMC V5.1+ Package | 1994 | Graffity + Motiv 8 | Bugfixed V5.1 |
| 170999 | DMC V6.0 | 2018 | The Imperium Arts | Private since ~1994 |

### DMC Pro Variants (Morbid/Onslaught)

| CSDb ID | Name | Year | Group | Notes |
|---------|------|------|-------|-------|
| 2603 | DMC 4.0 Professional | 1995 | Graffity + Onslaught | Brian + Morbid |
| 46811 | DMC 4.X Pro | 1996 | Onslaught | Brian + Morbid |
| 46813 | DMC 4.y Pro | 1996 | Onslaught | Brian + Morbid |
| 236891 | DMC V4.0 Pro Tool Kit | - | Onslaught | Morbid only |
| 35088 | DMC V4.2 | - | Sonic Screams | Brian + Morbid |

### Third-Party Modifications

| CSDb ID | Name | Year | Group | Notes |
|---------|------|------|-------|-------|
| 190760 | DMC V1.2 | - | The Ancient Temple | Repack |
| 216165 | DMC V4.1A | - | The Ancient Temple | Modified V4 |
| 121358 | DMC 4.G | 1997 | Samar Productions | Brian + Glover |
| 36658 | DMC V5.4 | - | Samar Productions | Glover; "better hard restart" |
| 28439 | DMC 5.Z. | 1995 | Samar Productions | Zeor |
| 22938 | DMC V5.0+ | 2002 | CreaMD/DMAgic | Audible sector editing |
| 46814 | DMC 5.0+ | 1997 | Onslaught | Morbid variant |
| 46835 | DMC 5.1x | 1997 | Onslaught | Morbid variant |
| 46836 | DMC 5.1y | 1999 | Onslaught | Morbid variant |
| 236892 | DMC V5.01B | - | Chaos | |
| 2629 | DMC V7.0 | 1995 | Unreal | Based on V4 code |

### Speed Variants

| CSDb ID | Name | Year | Group | Notes |
|---------|------|------|-------|-------|
| 504 (HVMEC) | DMC V2.1+ [4x] | 199? | Keen Acid | Quadruple speed by Moog |
| 541 (HVMEC) | DMC V4.0 [2x] | 199? | Keen Acid | Double speed by Moog |

### Relocators

| CSDb ID | Name | Year | Group | Notes |
|---------|------|------|-------|-------|
| 10758 | DMC Relocator | 1991 | Graffity | V2 + V4 relocators |
| 236894 | DMC Relocator V2 | - | Graffity | |
| 4386 | DMC V4.0 Relocator V2.0 | 1993 | Warriors of the Wasteland | By Stormlord + The Syndrom |

### Modern Cross-Platform Editor

| CSDb ID | Name | Year | Group | Notes |
|---------|------|------|-------|-------|
| 250645 | DMC 4 Editor 1.0 | 2025 | Logan/Slackers | Windows cross-platform |
| 251057 | DMC 4 Editor 1.1 | 2025 | Logan/Slackers | PRG export, relocation |

---

## Version Family Tree

```
GMC V1.0 (1990)
  |
  v
GMC V1.6 (1990)
  |
  v
DMC V1.2 (Feb 1991)
  |
  v
DMC V2.0 (Feb 1991) ------> DMC V2.1+ [4x] (Keen Acid, quadruple speed)
  |
  v
DMC V3.0 (Jul 1991)
  |
  +---> DMC V4 family                    +---> DMC V5 family
  |     |                                |
  |     DMC V4.0 (Sep 1991)              DMC V5.0 (1993)
  |     |                                |
  |     DMC V4.05 (1992)                 DMC V5.1 (1994, bugfix by Iceball)
  |     |                                |
  |     DMC V4.0 [2x] (Keen Acid)        DMC V5.1+ (1994, bugfixed)
  |     |                                |
  |     DMC V4.1A (Ancient Temple)        DMC V5.0+ (2002, CreaMD)
  |     |                                |
  |     DMC V4.2 (Brian+Morbid)          DMC V5.01B (Chaos)
  |     |                                |
  |     DMC V4.3++ (Tide)                DMC V5.4 (Samar, Glover)
  |     |                                |
  |     DMC V4.G (1997, Samar)           DMC V5.Z. (1995, Samar)
  |     |                                |
  |     DMC 4.0 Professional (1995)      DMC 5.0+ (1997, Onslaught)
  |     |                                |
  |     DMC 4.X Pro (1996, Onslaught)    DMC 5.1x (1997, Onslaught)
  |     |                                |
  |     DMC 4.y Pro (1996, Onslaught)    DMC 5.1y (1999, Onslaught)
  |     |
  |     DMC V7.0 (1995, Unreal)  <-- adopted V4 code, NOT official
  |     |
  |     DMC V7.1 beta (mentioned in comments)
  |
  +---> DMC V6.0 (private ~1994, released 2018)
        Ultra-low rastertime, separate development branch
```

---

## Data Format (Sector Encoding)

DMC uses a **duration-based** pattern format, NOT a tick-based tracker format. Each sector
(pattern) is a variable-length stream of bytes. Unlike trackers where row N in channel 1
corresponds to row N in channel 2, DMC channels run independently -- each channel processes
its sector data at its own pace based on duration commands.

### V4 Sector Byte Encoding

From our existing parser (`dmc_parser.py`) and cross-referenced with player analysis:

| Byte Range | Meaning | Details |
|------------|---------|---------|
| `$00-$5F` | **Note** (96 notes) | C-0 through B-7. Value = octave*12 + semitone |
| `$60-$7C` | **Duration** | Ticks = byte AND $1F (range 0-28) |
| `$7D` | **Continuation** | No ADSR reset on next note (tie/legato) |
| `$7E` | **Gate off** | Release current note |
| `$7F` | **End of sector** (V4) | Marks end of pattern data |
| `$80-$9F` | **Instrument select** | Instrument = byte AND $1F (0-31) |
| `$A0-$BF` | **Glide** (portamento) | Semitones = byte - $A0 |
| `$C0-$DF` | **Additional commands** | V5+ extended commands |
| `$FF` | **End of sector** (V5) | Some V5 variants use $FF instead of $7F |

### Key Design Properties

- **Duration-explicit**: Every note needs a DUR command; no implicit "one row = one tick"
- **Independent channels**: Step N in channel 1 is NOT synchronized with step N in channel 2
- **Variable-length sectors**: A sector can contain any number of bytes
- **Polyrhythm-friendly**: Independent channel timing makes polyrhythms natural
- **Up to 64 sectors** (00-3F) in V4
- **Up to 96 sectors** in V5 (per Chordian comparison)
- **Up to 250 rows per sector** in V5

### V5 Extended Commands ($C0-$DF range)

V5 adds commands in the sector data for:
- Filter frequency (high byte)
- Filter type and resonance
- ADSR register direct setting (Attack-Decay, Sustain-Release)
- Volume control
- Gate bit reset
- Hard restart disable (tie note)
- Fade in/out

These are set via the sector editor using key combinations like SHIFT+A (AD register),
SHIFT+S (SR register), SHIFT+Q (filter freq), SHIFT+F (filter type), SHIFT+V (volume).

---

## Instrument Table Format

DMC instruments are stored as **11 bytes each**, with **32 instruments** (numbered 0-31).
Total instrument table size: **352 bytes** (32 x 11).

From our parser (`dmc_parser.py`):

| Offset | Name | Description |
|--------|------|-------------|
| +0 | AD | Attack/Decay register value (SID $D405/0C/13) |
| +1 | SR | Sustain/Release register value (SID $D406/0D/14) |
| +2 | wave_ptr | Index into wave table (starting row) |
| +3 | pw1 | Pulse width parameter 1 |
| +4 | pw2 | Pulse width parameter 2 |
| +5 | pw3 | Pulse width parameter 3 |
| +6 | pw_limit | Pulse width limit |
| +7 | vib1 | Vibrato parameter 1 (speed/depth) |
| +8 | vib2 | Vibrato parameter 2 |
| +9 | filter | Filter configuration |
| +10 | fx | Effect/flag byte |

### FX Byte Flags

| Bit | Meaning |
|-----|---------|
| bit 3 ($08) | No-gate flag (skip gate-off during hard restart) |

### Instrument Table Location

- **V4**: Located at freq_hi_table + $0248 bytes offset
- **V5**: Located dynamically; found by searching for Y-indexed LDA (opcode $B9)
  references from player code pointing past the frequency table

The instrument table always follows the frequency table in memory.

### Instrument Features (from Chordian comparison)

- 32 instruments/sounds available (V4 and V5)
- Some V5 variants report 63 instruments
- Configurable ADSR envelope
- Programmable pulse width modulation (3 parameters + limit)
- Vibrato (hi-fi + "feeling" modes)
- Filter assignment
- Wave table pointer for arpeggio/waveform sequences
- Gate timer (hard restart)

---

## Wave Table

The wave table is a dual-column table used for waveform sequences and arpeggios.

### Structure

- **Left column**: Waveform bytes (SID control register values)
- **Right column**: Note data (relative pitch / absolute note values)

### Wave Table Byte Encoding (Left Column)

| Value | Meaning |
|-------|---------|
| `$00-$8F` | Raw SID waveform byte written to control register |
| `$90-$FD` | Loop command: jump back (value - $90) steps |
| `$FE` | End/stop marker |

### Player Access Pattern

From `dmc_to_usf.py` code analysis, the wave table columns are found by:
1. Looking for `LDA abs,Y` (opcode $B9) followed by `CMP #$90` (opcode $C9 $90)
   -- this identifies the left (waveform) column
2. The right (note data) column is the next `LDA abs,Y` within ~40 bytes

The player processes one wave table step per frame, cycling through waveform and note
values. The `$90+N` loop command creates repeating sequences.

### Arpeggio via Wave Table

Arpeggios are implemented through the wave table's right column: each step specifies
a note offset that is added to the base note frequency. Combined with rapid waveform
changes in the left column, this creates classic C64 arpeggio effects.

---

## Track/Order List Structure

### V4 Track System

- **8 independent tunes** per file (selectable via tune switching)
- **3 channels** per tune
- **256 rows** per track (00-FF) for sequencing sector references
- Each track row contains a sector number (00-3F)
- Special track commands: transpose up/down, end marker, stop command

### Sector Pointer Table

The sector pointer table is a split lo/hi byte table:
- **Sector pointer lo**: N bytes of low address bytes
- **Sector pointer hi**: N bytes of high address bytes
- N = number of sectors (typically 3 to 64)

The gap between lo and hi tables equals the sector count. Each pair of bytes
forms a 16-bit address pointing to the sector data in memory.

### Track Editor Commands

- S: Insert sector reference
- +/-: Insert transpose up/down
- SHIFT+E: End marker (loop back to start)
- C=+E: Stop command (halt playback)

---

## Player Architecture

### Memory Layout (V4 typical)

```
$1000  Player code (init at $1000, play at $1003)
       ~2000-2400 bytes player routine
       Frequency table (96 notes x 2 = 192 bytes, hi/lo or lo/hi)
       Instrument table (32 x 11 = 352 bytes)
       Wave table (left + right columns)
       Sector pointer tables (lo + hi)
       Sector data
       Track data
$xxxx  End of data
```

The player is relocatable -- the DMC Relocator tool can move the entire player + data
to any base address. Standard PSID init address is typically $1000 with play at $1003.

### Player Routine Flow

1. **Init** ($1000): Set up initial state, select tune number
2. **Play** ($1003): Called once per frame (50Hz PAL VBI)
   - For each of 3 voices:
     - Process duration countdown
     - When duration expires, read next sector byte
     - Handle note/command/instrument/glide bytes
     - Process wave table (one step per frame)
     - Process pulse width modulation
     - Process vibrato
     - Process filter
     - Write SID registers

### Zero Page Usage

- At least 5 locations: $FB-$FF (per Chordian comparison)
- Used for temporary pointers during sector data access

### CPU Time

- **V4**: "Most of the screen" (~23-27 raster lines at 1x speed)
- **V5**: Similar or higher
- **V6**: Only 7-8 raster lines (optimized for demos)

### Speed

- **1x speed** only (standard versions)
- Special variants exist for 2x speed (Keen Acid) and 4x speed (Keen Acid)
- Speed is set per-tune; "speed always depends on the setting of speed of tune 7"
  (per CreaMD's V5.0+ notes)

---

## SIDId Signatures

From cadaver's sidid.cfg (https://github.com/cadaver/sidid/blob/master/sidid.cfg):

### DMC (generic/early)
```
18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

### DMC_V4.x
```
FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0
```

### DMC_V5.x
```
BC ?? ?? B9 ?? ?? C9 90 D0 AND BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```
Note: `AND` appears to be a placeholder/wildcard in the signature format.

### DMC_V6.x
```
A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4 8D 0B D4 8D 12 D4 8D 11 D4 A9 1F 8D 18 D4 A9 F2 8D 17 D4 60 CE ?? ?? 30 69 20
```

### Signature Analysis

- **V4.x signature**: `FE ?? ??` = INC abs (frame counter), `BD ?? ??` = LDA abs,X
  (per-voice indexed), `18 7D ?? ??` = CLC; ADC abs,X. This is the main voice
  processing loop.
- **V5.x signature**: `BC ?? ??` = LDY abs,X, `B9 ?? ??` = LDA abs,Y,
  `C9 90` = CMP #$90. The CMP #$90 check is the wave table loop detection.
- **V6.x signature**: Distinctive init routine writing $08 to all three waveform
  registers ($D404, $D40B, $D412) and setting filter ($D417=$F2, $D418=$1F).

### sidid.nfo Metadata

| Identifier | Full Name | Author | Year | CSDb |
|-----------|-----------|--------|------|------|
| DMC | Demo Music Creator System (DMC) | Balazs Farkas (Brian) | 1991 | id=2598 |
| DMC_V4.x | Demo Music Creator System (DMC) | Balazs Farkas (Brian) | 1991 | id=2596 |
| DMC_V5.x | Demo Music Creator System (DMC) | Balazs Farkas (Brian) | 1993 | id=2594 |
| DMC_V6.x | Demo Music Creator System (DMC) | Balazs Farkas (Brian) | - | - |

---

## DMC V4 vs V5 Differences

V4 and V5 are **fundamentally different programs**, not incremental updates.

| Feature | V4 | V5 |
|---------|----|----|
| Complexity | Simpler, "easy to use" | "Very powerful but hard to use" |
| Sectors | 64 (00-3F) | 96 (up to 250 rows each) |
| Instruments | 32 | 32 (some variants: 63) |
| End marker | $7F | $FF (some variants) |
| Speed options | 1x | 1x |
| Player size | ~2000 bytes | ~2000-2400 bytes |
| Wave table | Basic | Extended with CMP #$90 loop check |
| Sector commands | Notes, duration, instrument, glide, gate | + filter, ADSR, volume, fade |
| Pattern system | Contiguous stacking | Duration-based, variable length |
| Tunes per file | 8 | 8 |
| Editor interface | 3 channels shown | 3 order lists + 1 sector |
| User assessment | "Like ProTracker is to Amiga" | "Complete other music editor, much more difficult" |
| Hard restart | Standard | "Better hard restart" (V5.4) |
| Follow-play | No (V4.0) | Yes (V5.0) |

### Code Detection

The V4 player uses X-indexed absolute addressing for per-voice data:
```
FE ?? ??     ; INC voice_counter,X
BD ?? ??     ; LDA voice_data,X
18 7D ?? ??  ; CLC; ADC voice_data,X
9D ?? ??     ; STA voice_data,X
```

The V5 player uses Y-indexed absolute addressing for wave/instrument table access:
```
BC ?? ??     ; LDY voice_wave_ptr,X
B9 ?? ??     ; LDA wave_table,Y
C9 90        ; CMP #$90  (loop check)
D0 ??        ; BNE not_loop
```

### Frequency Table

Both V4 and V5 use the same 96-note frequency table (C-0 through B-7).
The table is 192 bytes: 96 bytes freq_hi followed by 96 bytes freq_lo
(or lo/hi depending on version). The table is used for PAL tuning.

---

## DMC V6 Details

DMC V6.0 is a **separate development branch** -- not based on V4 or V5 code.

### Key Characteristics
- **Ultra-low rastertime**: Only 7-8 raster lines (compared to 23-27 for V4/V5)
- **Trade-off**: "Pulse or filter only on some channel(s)" to save CPU
- **Complete editor**: No source code editing needed
- **Private release**: Used by scene members since ~1994, officially released Nov 2018
- **Developers**: Brian (player code) + The Syndrom/Matthias (editor)
- **CSDb**: https://csdb.dk/release/?id=170999

### Documentation
A `dmc6-docs.txt` file exists on CSDb but it is a D64 disk image, not a text file.

### Init Routine (from SIDId signature)
```asm
LDA #$02
STA voice_state,X      ; Initialize 3 voices
LDA #$00
STA voice_data,X
DEX
BPL loop               ; Loop for all 3 voices
STA some_var
LDA #$08
STA $D404              ; Test bit waveform (voice 1)
STA $D40B              ; Test bit waveform (voice 2)
STA $D412              ; Test bit waveform (voice 3)
STA $D411              ; Also written here
LDA #$1F
STA $D418              ; Volume = max + filter
LDA #$F2
STA $D417              ; Filter resonance + voice routing
RTS
```

### Known Musicians Using V6
- PRI (Oxyron, The Imperium Arts) - e.g., "Coma_Chase.sid"
- The Syndrom (Crest, The Imperium Arts)

---

## DMC V7 Details

### Important Context
DMC V7.0 is **NOT an official Brian release**. Per The Syndrom's comment on CSDb:
"This is an adopted v4.0, which someone released as v7.0 without permission."

### V7.0 (1995, by Unreal)
- CSDb: https://csdb.dk/release/?id=2629
- Coded by: Axl + Brian + Ray (Area Team, Unreal)
- Based on DMC V4 code with modifications
- Features added:
  - 1-5 multiple songs
  - Multi-channel play
  - Play from any line or note
  - Sector length display
  - Cassette recorder support (turbotape)
  - "50% code growth of original Brian's size"
- V5/V6 existed as separate branches; team "decided to improve old V4 and used V7"

### V7.1 (mentioned)
- Has "player improvements" and new filter/AD/SR commands
- Never released as a formal CSDb entry

---

## DMC Pro Variants

The "Pro" variants were created by **Morbid** (Dwayne James Bakewell) of **Onslaught**,
modifying Brian's original V4 code.

### DMC 4.0 Professional (1995)
- CSDb: https://csdb.dk/release/?id=2603
- By Brian (Graffity) + Morbid (Onslaught)
- First Pro variant

### DMC 4.X Pro (Apr 1996)
- CSDb: https://csdb.dk/release/?id=46811
- Includes tunes by Link and Fred Gray

### DMC 4.y Pro (1996)
- CSDb: https://csdb.dk/release/?id=46813
- Another variant by the same team

### DMC V4.0 Pro Tool Kit
- CSDb: https://csdb.dk/release/?id=236891
- By Morbid only (no Brian credit)
- D64 disk image with toolkit utilities

### DMC V4.2 (Sonic Screams release)
- CSDb: https://csdb.dk/release/?id=35088
- Brian + Morbid credited

### Other Morbid/Onslaught V5 Variants
- **DMC 5.0+** (1997): https://csdb.dk/release/?id=46814
- **DMC 5.1x** (1997): https://csdb.dk/release/?id=46835
- **DMC 5.1y** (1999): https://csdb.dk/release/?id=46836

All of these are V4 or V5 modifications with Morbid's enhancements.

---

## DMC 4 Editor (2025)

A modern cross-platform editor for DMC V4 format music.

### DMC 4 Editor 1.0 (3 Mar 2025)
- CSDb: https://csdb.dk/release/?id=250645
- By Logan (Slackers)
- Windows builds (64-bit, 32-bit, XP)
- Based on Brian's original code
- Features: 6x speed, revives DMC V4.0

### DMC 4 Editor 1.1 (15 Mar 2025)
- CSDb: https://csdb.dk/release/?id=251057
- Added features:
  - Music import with word message/credit display
  - PRG export with music relocation
  - Sector editor enhancements (octave controls, voice toggles)
  - Sound editor naming
  - Sound bank import/export
  - Track playback from any position with timing display
  - Font scaling
  - Many bug fixes

### Compatibility
Imports PRG/SID files composed with DMC V4.0, V7.0A, and V7.0B editors.

### Lemon64 Thread
https://www.lemon64.com/forum/viewtopic.php?p=1055941

---

## Editor Features and Commands

### DMC V4 Keyboard Commands

**Playback Controls:**
| Key | Function |
|-----|----------|
| F1 | Start current music |
| F3 | Stop music |
| F5 | Continue playing |
| F6 | Record playing |
| F7 | Fast play |
| F8 | Enter synthesizer (real-time keyboard) |

**Track Editor:**
| Key | Function |
|-----|----------|
| S | Insert sector reference |
| + | Insert transpose up |
| - | Insert transpose down |
| SHIFT+E | Insert end marker (loop) |
| C=+E | Insert stop command |
| SHIFT+RETURN | Enter screen (switch to sector editor) |
| ^ | Buffer track |
| SHIFT+C | Copy track |
| SHIFT+X | Exchange tracks |
| SHIFT+HOME | Clear tracks |
| SHIFT+T | Choose music (select tune 1-8) |
| SHIFT+I | Clear all |
| LEFT ARROW | Return to main menu |

**Sector Editor:**
| Key | Function |
|-----|----------|
| [ ] | Choose sector |
| < > | Transport notes (transpose) |
| + | Toggle voice/music; insert gate |
| - | Insert continuation (legato) |
| C=+D | Insert duration |
| C=+S | Insert sound/instrument |
| C=+G | Insert glide |
| ^ | Buffer sector |
| RETURN | Paste buffer |
| SHIFT+RETURN | Return to track editor |
| LEFT ARROW | Return to main menu |

### DMC V5 Additional Sector Commands

| Key | Function |
|-----|----------|
| SHIFT+D | Set note duration |
| SHIFT+S | Set sound number ($00-$1F) |
| SHIFT+G | Glide effect |
| SHIFT+H | Slide note |
| SHIFT+A | AD register (Attack/Decay) |
| SHIFT+S | SR register (Sustain/Release) |
| SHIFT+Q | Filter frequency (high byte) |
| SHIFT+F | Filter type and resonance |
| SHIFT+V | Volume |
| SHIFT+X | Disable hard restart (tie note) |
| SHIFT++/- | Fade in/out |
| Pound key | Reset gate bit |
| = | End sector |

---

## Player Specifications

### Summary Table (from Chordian comparison + analysis)

| Property | V4 | V5 | V6 |
|----------|----|----|-----|
| Player size | ~2000 bytes | ~2000-2400 bytes | ~1500 bytes (est.) |
| Zero page | >= 5 ($FB-$FF) | >= 5 ($FB-$FF) | Unknown |
| Rastertime | ~23-27 lines | ~23-27 lines | 7-8 lines |
| Speed | 1x (50Hz) | 1x (50Hz) | 1x (50Hz) |
| SID chips | 1 | 1 | 1 |
| Channels | 3 | 3 | 3 |
| Format | PAL only | PAL only | PAL only |
| Digi/samples | No | No | No |
| Arpeggio | Via wave table (hi-freq) | Via wave table (hi-freq) | Via wave table |
| Pulse width | Programmable | Programmable | Limited channels |
| Filter | Yes | Programmable | Limited channels |
| Vibrato | Hi-fi + feeling | Hi-fi + feeling | Unknown |
| Gate off timer | Yes | Yes | Yes |
| Hard restart | Standard | Better (V5.4) | Unknown |

### HVSC Identification

In HVSC, DMC SIDs are identified by the `sidid` tool using the signatures above.
The player is categorized as:
- `DMC` (generic early versions)
- `DMC_V4.x` (V4 family)
- `DMC_V5.x` (V5 family)
- `DMC_V6.x` (V6 family)

DMC is one of the most common player engines in HVSC, with thousands of SID files.

---

## Key People

### Brian (Balazs Farkas)
- **Groups**: Graffity, The Imperium Arts
- **Country**: Hungary
- **CSDb**: https://csdb.dk/scener/?id=367
- **Role**: Original author of GMC and all official DMC versions (V1-V6)
- Created GMC V1.0 in 1990, then DMC V1.2-V6.0 through the 1990s

### The Syndrom (Matthias)
- **Groups**: Crest, The Imperium Arts
- **Role**: DMC V6 editor co-developer, documentation, DMC V4 Relocator V2.0 concept
- Also created charsets for DMC packages

### Morbid (Dwayne James Bakewell)
- **Groups**: Bass, Onslaught, Rebels, Warriors of the Wasteland
- **Role**: Created DMC Pro variants (V4.0 Professional, 4.X Pro, 4.y Pro, V4.2)
- Also modified V5 variants (5.0+, 5.1x, 5.1y)

### Iceball
- **Groups**: Motiv 8, Vision
- **Role**: Bug-fix for DMC V5.1/V5.1+ packages

### Glover
- **Group**: Samar Productions
- **Role**: Created DMC V5.4 and DMC 4.G modifications

### Moog
- **Group**: Keen Acid
- **Role**: Created speed variants (2x, 4x) of DMC V2.1+ and V4.0

### Logan
- **Group**: Slackers
- **Role**: Created DMC 4 Editor (2025 cross-platform Windows editor)

### Richard Bayliss
- **Group**: The New Dimension (TND)
- **Role**: Prolific DMC V4 user; wrote tutorial documentation for DMC V4

---

## Source URLs

### CSDb Release Pages

| URL | Description |
|-----|-------------|
| https://csdb.dk/release/?id=7268 | GMC V1.0 (1990) |
| https://csdb.dk/release/?id=2598 | DMC V1.2 (1991) |
| https://csdb.dk/release/?id=10757 | DMC V2.0 (1991) |
| https://csdb.dk/release/?id=98640 | DMC V3.0 (1991) |
| https://csdb.dk/release/?id=2596 | DMC V4.0 (1991) |
| https://csdb.dk/release/?id=2597 | DMC V4.05 (1992) |
| https://csdb.dk/release/?id=2594 | DMC V5.0 (1993) |
| https://csdb.dk/release/?id=2599 | DMC V5.1 Package (1994) |
| https://csdb.dk/release/?id=2600 | DMC V5.1+ Package (1994) |
| https://csdb.dk/release/?id=170999 | DMC V6.0 (2018/~1994) |
| https://csdb.dk/release/?id=2629 | DMC V7.0 (1995) |
| https://csdb.dk/release/?id=2603 | DMC 4.0 Professional (1995) |
| https://csdb.dk/release/?id=46811 | DMC 4.X Pro (1996) |
| https://csdb.dk/release/?id=46813 | DMC 4.y Pro (1996) |
| https://csdb.dk/release/?id=236891 | DMC V4.0 Pro Tool Kit |
| https://csdb.dk/release/?id=35088 | DMC V4.2 |
| https://csdb.dk/release/?id=216165 | DMC V4.1A |
| https://csdb.dk/release/?id=121358 | DMC 4.G (1997) |
| https://csdb.dk/release/?id=36658 | DMC V5.4 |
| https://csdb.dk/release/?id=28439 | DMC 5.Z. (1995) |
| https://csdb.dk/release/?id=22938 | DMC V5.0+ (2002, CreaMD) |
| https://csdb.dk/release/?id=46814 | DMC 5.0+ (1997, Onslaught) |
| https://csdb.dk/release/?id=46835 | DMC 5.1x (1997) |
| https://csdb.dk/release/?id=46836 | DMC 5.1y (1999) |
| https://csdb.dk/release/?id=236892 | DMC V5.01B |
| https://csdb.dk/release/?id=250645 | DMC 4 Editor 1.0 (2025) |
| https://csdb.dk/release/?id=251057 | DMC 4 Editor 1.1 (2025) |
| https://csdb.dk/release/?id=10758 | DMC Relocator (1991) |
| https://csdb.dk/release/?id=4386 | DMC V4.0 Relocator V2.0 (1993) |
| https://csdb.dk/release/?id=236894 | DMC Relocator V2 |

### Other Sources

| URL | Description |
|-----|-------------|
| https://csdb.dk/scener/?id=367 | Brian/Graffity/The Imperium Arts profile |
| https://csdb.dk/group/?id=193 | Graffity group page |
| https://github.com/cadaver/sidid/blob/master/sidid.cfg | SIDId signatures |
| https://github.com/cadaver/sidid/blob/master/sidid.nfo | SIDId player metadata |
| https://github.com/WilfredC64/player-id | Player-ID utility |
| http://chordian.net/c64editors.htm | C64 Music Editors comparison table |
| https://deepsid.chordian.net/ | DeepSID online SID player |
| https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/ | Editor comparison blog |
| https://chipflip.wordpress.com/2009/08/17/note-duration-in-chipmusic-software/ | Duration-based format analysis |
| https://hvmec.altervista.org/blog/?p=504 | HVMEC: DMC V2.1+ |
| https://hvmec.altervista.org/blog/?p=541 | HVMEC: DMC V4.0 [2x] |
| https://hvmec.altervista.org/blog/?p=570 | HVMEC: DMC V4.0 Pro |
| https://hvmec.altervista.org/blog/?p=630 | HVMEC: DMC V4.3++ |
| https://hvmec.altervista.org/blog/?p=700 | HVMEC: DMC V5.0 |
| https://hvmec.altervista.org/blog/?p=757 | HVMEC: DMC V5.0+ |
| https://hvmec.altervista.org/blog/?p=973 | HVMEC: DMC V5.4 |
| https://silo.tips/download/demo-music-creator-40 | DMC V4.0 documentation PDF |
| https://www.lemon64.com/forum/viewtopic.php?t=24476 | Lemon64: DMC 6 discussion |
| https://www.lemon64.com/forum/viewtopic.php?p=1055941 | Lemon64: DMC V4 is back (2025) |
| https://www.lemon64.com/forum/viewtopic.php?t=80234 | Lemon64: DMC 4 Instructions |
| https://www.pouet.net/prod.php?which=13452 | Pouet: DMC 4.0 |
| https://demozoo.org/productions/tagged/dmc/ | Demozoo: DMC-tagged productions |
| http://www.tnd64.unikat.sk/music_scene.html | TND: Richard Bayliss DMC tutorial (SSL broken) |

---

## Notes for Parser/Player Development

### What We Already Have
- `src/dmc_parser.py` - Working parser with sector encoding, instrument table, layout detection
- `src/dmc_to_usf.py` - Partial DMC-to-USF converter with wave table extraction

### Key Technical Gaps to Fill
1. **V5 extended commands** ($C0-$DF): Need to decode filter, ADSR, volume, fade commands
   from sector data. These are NOT present in V4.
2. **Pulse table format**: pw1/pw2/pw3/pw_limit in instrument table need exact interpretation
   (modulation speed, direction, limits)
3. **Vibrato parameters**: vib1/vib2 exact encoding (speed vs depth vs mode)
4. **Filter byte**: Exact encoding in instrument table (filter type, resonance, routing)
5. **Track data format**: How tune selection (1-8) maps to track data in memory
6. **V6 data format**: Completely different from V4/V5; needs separate parser
7. **V7 compatibility**: V7 is "adopted V4" -- may need minor adjustments to V4 parser
8. **Speed variants**: 2x/4x speed variants change the tempo interpretation
9. **Pro variant differences**: What Morbid changed in the Pro versions

### Recommended Approach
1. Start with V4 (most common in HVSC, simplest format)
2. Use `sidid` signatures to identify exact version
3. Build V5 support as a separate code path (different player, different commands)
4. V6 requires its own parser (very different architecture)
5. V7 can likely reuse V4 parser with minor adjustments

### Player Source Code Status
No official source code for any DMC version has been publicly released. All format
knowledge comes from:
- Disassembly of existing SID files
- The existing `dmc_parser.py` address analysis technique
- SIDId signature patterns
- Editor documentation (keyboard commands, not data format)
- Community knowledge from CSDb/Lemon64 comments
