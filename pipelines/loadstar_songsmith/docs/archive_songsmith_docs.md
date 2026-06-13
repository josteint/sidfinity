---
source_url: multiple — Songsmith-Loadstar.d64 (CSDb id=122855), HVSC SID binaries, GitHub MUS format spec
fetched_via: curl download + binary analysis + WebFetch
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: primary (direct binary analysis of reference disk)
---

# Loadstar SongSmith — Format Documentation Extracted from D64 and SID Binaries

## Overview

SongSmith is Loadstar/Softdisk's proprietary C64 music composition editor.
It stores songs in a **multi-file native format** (M./W./C./S./L. prefixes) and
includes a converter to produce **COMPUTE!'s SidPlayer MUS format** for
distribution and sharing.

The SIDs in HVSC tagged as `Loadstar_SongSmith` contain the SidPlayer player
routine (Craig Chamberlain) with the MUS data embedded. This is the EXPORTED
format, not the SongSmith native format.

---

## SongSmith Native File Format

### File Naming Convention

Per embedded documentation text on `Songsmith-Loadstar.d64`:

> "SongSmith songs always have at least two files, one beginning with 'M.' and
> the other beginning with 'W.'. Veteran music makers have found that it's [useful
> using] the more sophisticated features."

| Prefix | Content | Example |
|--------|---------|---------|
| `M.SONGNAME` | Melody / note data | `M.FUNICULI` |
| `W.SONGNAME` | Waveform / instrument data | `W.FUNICULI` |
| `C.SONGNAME` | Credits (title, composer) | `C.FUNICULI` |
| `S.SONGNAME` | SID export (converted format) | `S.FUNICULI` |
| `L.SONGNAME` | Lyrics | `L.FUNICULI` |

All 5 file types observed on the CSDb reference disk for each song.

### Native Format — OPEN (RE Required)

The **native SongSmith format** (M.*/W.* files) is different from the SidPlayer
MUS format. The converter program (`SSSPCONV.O` or similar — seen in disk strings
as `"SSSPCONV.O",DN`) translates M.*/W.* into the standard SID/MUS format.

From the embedded documentation:
> "Here are step-by-step instructions on how to turn your SongSmith songs into
> SID songs."

The conversion process was a **deliberate two-stage workflow**:
1. Compose in SongSmith (M.*/W.* files, native format)
2. Convert to SID format using the converter for distribution/playback

The converter handles key conversion details:
- Step 2: Play (or SID) format — "A program that will play SongSmith or SID format songs on any disk"
- Step 3: Prompt for "APPEND CREDITS TO FILE? (Y/N)"
- Step 4: Key signature selection (list of all key signatures and their sharps/flats)
- Step 5: Drive 9 support
- Step 6: "SONGSMITH FILENAME?" prompt
- Step 7: Choose between Tempo 1 and Tempo 2 (documented as "SongSmith's inexplicable way of saving the tempo (speed) of a song")

> "This strange prompt is due to [SongSmith]'s inexplicable way of saving the tempo
> (speed) of a song. Either one [works]."

**OPEN:** What does Tempo 1 vs Tempo 2 mean in the native format? Two separate
tempo fields? A "slow/fast" binary flag?

---

## Instrument Definitions

From raw string extraction of the editor code on the d64, SongSmith ships with
**at minimum 16–19 preset instrument names** (abbreviated 5-char codes used internally,
full names used in the editor UI):

| Short Code | Full Name |
|------------|-----------|
| `PIANO` | Piano |
| `BANJO` | Banjo |
| `ECGTR` | Elec Guitar |
| `TRMPT` | Trumpet |
| `VIOLN` | Violin |
| `FLUTE` | Flute |
| `PCLTR` | Percolator |
| `CLRNT` | Clarinet |
| `CNGTR` | Country Guitar |
| `CLIPE` | Calliope |
| `BASSV` or `BSGTR` | Bassviol / Bass Guitar |
| `CELLO` | Cello |
| `HPSCD` | Harpsichord |
| `FRHRN` | French Horn |
| `CYMBL` | Cymbal |
| `XLPHN` | Xylophone |
| `TUBA ` | Tuba |
| `RNGMD` | Ring Mod |
| `FRQMD` | Freq Mod |
| `OBOE ` | Oboe |
| `PIPES` | Bagpipes |

Two versions of the instrument list appear in the d64 binary (short form at one
location, full-name form at another), confirming these are the built-in presets.
The "Instrument Toolhouse" (string found at disk offset 0x0109eb) is the editor
screen for modifying instruments.

---

## Tempo System

From disk strings:
- Editor prompt: `ENTER NEW TEMPO (30-260): ` → tempo range **30–260 BPM**
- Editor label: `BEATS/MINUTE`
- The conversion to CIA timer value is done by the SidPlayer player (see SID binary analysis below)

The editor UI shows "SPEED (+..)" and "\ TO CANCEL" controls, suggesting
tempo is adjusted incrementally.

---

## Editor Hot Keys (from disk strings)

```
SPACE  — Next song
Q      — Menu
A      — Add to music
E      — Edit a [voice/instrument]
C      — Copy
M      — Move
D      — Delete [voice/measure]
N      — New (erase)
S      — Save (special/change)
P      — Play music
F      — File [operations]
I      — Instrument
F5     — Center staff
F7     — Reformat notes
F8     — Delete voice
<      — Move 1 measure left
>      — [Move 1 measure right?]
```

From the main menu region (offset 0x0111a6+):
```
MAIN MENU:
1  — Save/Change
3  — New Instrument
N  — [New?]
F5 — Center Staff
F7 — Reformat Notes
F8 — Delete Voice
<  — Move 1 Measure
>  — [Right]
```

File sub-menu (offset 0x011aca+):
```
S  — Save Music File
$  — Directory
F  — Format [disk]
C  — Change a Load Address
```

---

## Voice/Note Editor

From disk strings:
- `VOICE   .1 .^.` → voice 1 being edited (navigation keys)
- `EDITED: .. 1 .. 2 . 3 .]` → voice count display
- `DOT THE NOTE` → dotted note entry
- `+  SHARP` → sharp entry
- `DON'T OVERLAP NOTES` → overlap detection/warning
- `NOT [FIT]TING THAT VOICE` → space warning
- `CONFIRM TO DELETE VOICE` → deletion confirmation
- `MEASURE #` → measure navigation
- `LEFT/RIGHT — ADSR (attack, decay, sustain, release)`
- `A — Attack`, `D — Decay`, `S — Sustain`, `R — Release`
- `W — Change Waveform`, `M — Measure # to hear`, `N — Name`

The instrument editor screen shows:
- Attack/Decay/Sustain/Release per instrument
- Waveform selection (`H — ?`)
- Named instruments
- Key of [V?], Flats selector

---

## Measure and Song Structure

From disk strings:
- `MEASURE #` displayed prominently (editor shows measure number)
- `MEASURE # TO HEAR:` (play from a specific measure)
- `LAST MEASURE` (file/song info)
- `MUSIC MEMORY USED: [X] BYTES` (memory monitor)
- `ADD TO MUSIC`, `COPY`, `MOVE`, `DELETE [MEASURE]`
- `SIGNATURE [E SBCT?]` — key signature display (possibly showing sharps/flats)

Songs are organized as measures within 3 voices.

---

## SID Export Format (SIDSMITH/SidPlayer MUS)

### Player Identification

All HVSC SongSmith SIDs share:
- **init address:** $CC00
- **play address:** $CC48
- **load address:** varies ($B800–$C900, relocation per song)

The jump table at $CC00:
```
CC00: JMP CC09  (init entry)
CC03: JMP CE63  (?)
CC06: JMP CE83  (?)
```

Init code ($CC09–$CC47):
```
CC09: SEI
CC0A: PHA
CC0B–CC1F: NOP × 21  (padding)
CC20: LDX #00
CC22: LDY #<hi_byte>    ← varies per SID! = hi byte of music data address
CC24: STX $8E           (lo byte of music data ptr to ZP $8E)
CC26: STY $8F           (hi byte of music data ptr to ZP $8F)
CC28: LDA $01           (C64 memory map / PLA)
CC2A: AND #FE
CC2C: STA $01           (clear bit 0 to enable KERNAL ROM?)
CC2E: LDY #2
CC30: LDA ($8E),Y       (read music_data[2] = tempo/CIA timer hi)
CC32: STA $DC05         (CIA1 Timer A Hi)
CC35: STA $CF60         (player internal tempo variable)
CC38: LDY #0
CC3A: STY $02           (zero out ZP $02)
CC3C: JSR $CD6E         (player init subroutine)
CC3F: LDA $01
CC41: ORA #01
CC43: STA $01
CC45: PLA
CC46: NOP
CC47: RTS
```

Play entry ($CC48):
```
CC48: NOP
CC49: LDA $CF5C
CC4C: BNE → $CD4D  (branch if timer not elapsed)
CC4F: NOP × 5
CC54: LDA $01
CC56: AND #FE
CC58: STA $01
CC5A: LDA $CF58
CC5D: BNE [cond]
... (playback loop)
```

### Music Data Layout

Music data starts at the SID load address (the $CC22 LDY #hi instruction sets
the high byte; lo byte is always $00, so music address = $XX00 where XX is the byte
at init code offset $CC23).

**Byte layout of music data (from binary analysis of multiple SIDs):**
```
Offset 0: $00 (always zero — first byte of voice 1 stream, or format marker)
Offset 1: varies (second byte of voice 1 stream)
Offset 2: CIA timer hi byte (= tempo, also part of voice 2 size in MUS header?)
Offset 3+: voice data continues
```

The music data is **MUS-format voice streams** (2-byte command/option pairs).
The player reads `music[2]` during init for the CIA timer hi byte. This overlaps
with the MUS format's "voice 2 data size lo byte" field position if a 6-byte size
header were present — suggesting SIDSMITH may embed tempo differently from standard
MUS or may omit the size header entirely.

**No HLT marker ($01 $4F) was found in sampled voice data.** This suggests either:
- The voice data uses a different terminator, OR
- The player uses the size fields to know when to stop (and the size field is
  present but was misidentified in this binary analysis session), OR
- Voice boundaries are implicit (fixed size per voice based on some other field)

**OPEN — needs RE:** Locate voice 1/2/3 boundaries and terminator format.

### SIDSMITH Reference (from disk strings)

The conversion program and player are called:
- `SIDSMITH` — the exported player/format name
- `SIDSMITH.SHPL` — a shell/startup file for the SidPlayer

The documentation text on disk states:

> "[SIDSMITH/SidPlayer] is the player program for Craig Chamberlain's music system
> that was first published by Compute's Gazette. It has become the standard of the
> Commodore music industry and is supported by thousands of [musicians]."

> "Veteran music makers have found that it's [handy] to do the first draft of their
> songs with [SongSmith], then add things like triplets, tied measures and filtering
> — which SongSmith cannot do — with [SIDSMITH/Sidplayer]. Then they use
> [the converter] to convert their SongSmith music over to the SID format."

This confirms:
1. SongSmith lacks triplets, tied measures, and filtering
2. The exported format IS Craig Chamberlain's Sidplayer MUS format
3. Both tools coexisted as complementary tools in the Loadstar ecosystem

---

## SidPlayer MUS Format (COMPUTE's Gazette, Craig Chamberlain)

Full spec documented in a companion file: `github_sidplayer_mus_format.md`.  
Source: https://github.com/MyDeveloperThoughts/ComputeSidPlayerC64Source/blob/main/notes/musFileFormat.md

Key parameters relevant to SongSmith export:

**File structure:**
- Bytes 0-1: Voice 1 data size (lo/hi, LE)
- Bytes 2-3: Voice 2 data size (lo/hi, LE)
- Bytes 4-5: Voice 3 data size (lo/hi, LE)
- Voice 1 data (ends with HLT = $01 $4F)
- Voice 2 data (ends with HLT)
- Voice 3 data (ends with HLT)
- NULL-terminated song description text

**Note encoding (2 bytes per note):**
```
Command byte (duration byte):
  bits 0-1: 00 = note command identifier
  bits 2-4: duration (010=whole, 011=half, 100=quarter, 101=8th, 110=16th, 111=32nd, 000=64th)
  bit 5:    dotted (0=no, 1=yes)
  bit 6:    tie (0=no, 1=yes)
  bit 7:    double-dotted (0=no, 1=yes)

Option byte (note byte):
  bits 0-2: note (000=rest, 001=C, 010=D, 011=E, 100=F, 101=G, 110=A, 111=B)
  bits 3-5: octave (stored EOR $FF → actual octave = stored_bits XOR 0b111)
  bits 6-7: accidental (10=normal, 01=sharp, 11=flat)
```

**Tempo command:** TEM (cmd=$06, opt=tempo_value)  
Tempo table maps $08 (1800 BPM) through $00 (56 BPM) in steps of $08.

**SongSmith limitations vs full SidPlayer:**
- No triplets (MUS format supports them; SongSmith editor can't enter them)
- No tied measures (MUS TIE bit exists; SongSmith can't create them)
- No filter commands (MUS has F-M, F-C, F-S, FLT, RES, AUT, F-X; SongSmith has none)

---

## Instrument Toolhouse

From disk strings near offset 0x0109eb:

```
INSTRUMENT TOOLHOUSE
K.D / K.X / K.l / K.% / K..
ATTACK / DECAY / SUSTAIN / RELEASE
CHANGE WAVEFORM
KEY OF V
FLATS
```

The Instrument Toolhouse is the SongSmith instrument design screen.
ADSR parameters are adjustable per-instrument.
Waveform selection is available.
Key/flats relate to transposition in the instrument context (or key signature display).

---

## Program Package Contents

From the embedded disk documentation:

```
THE PACKAGE CONTAINS:
- THE MUSIC MAKING PROGRAM [= SongSmith editor]
- A PROGRAM FOR SHOWING OFF YOUR SONGS [= Jukebox player]
- A PROGRAM FOR CONVERTING SONGSMITH SONGS INTO THE MORE STANDARD SID FORMAT [= converter]
```

The Jukebox program has two data files: `JUKEBOX ML` and `JUKEBOX FONT`.
Copying the Jukebox requires copying these files alongside the `JUKEBOX` main program.

The documentation text also mentions:
```
- SIDSMITH / SID player (Craig Chamberlain's format player)
- MUSIC STAR.BAS (a BASIC file)
```

---

## Loadstar 237 Version — Discmaster Archive

Loadstar 237 (2004 disk, Jan 2004 issue date) contains the definitive documented
version of SongSmith, available on discmaster.textfiles.com (item 5218):

**Files on Loadstar 237 D81:**
- `t.songsmith` — text documentation article by Dave Moorman (79 lines, 2.1 KB)
  URL: https://discmaster.textfiles.com/view/5218/237.d81/t.songsmith
- `b.songsmith` — BASIC boot loader (41 lines, 1.2 KB)
  URL: https://discmaster.textfiles.com/view/5218/237.d81/b.songsmith
  Contains: `by Joe Garrett` credit; `(c) 2005 by mid$ & asc Publishing, Inc.`
  (the Loadstar successor publisher www.eloadstar.com)
- `songsmith/songsmith.080d/songsmith.1b39` — the program binary (62.0 KB)
  URL: https://discmaster.textfiles.com/browse/5218/237.d81/songsmith/songsmith.080d
  The `.1b39` suffix = load address **$1B39**. This is a RE primary target.

From b.songsmith boot screen: "this program does not return to LOADSTAR"
(must power down to exit). Credits confirm "by Joe Garrett".

**Loadstar 237 context:**
- SongSmith "never appeared on a regular issue of LOADSTAR" — it was a standalone
  product sold separately. Loadstar 237 is the first time it appeared as an in-issue
  feature (Dave Moorman brought it to the magazine format).
- Documentation in t.songsmith is BY Dave Moorman, program BY Joe Garrett.

See also `src/loadstar237_t_songsmith_extracted.md` and
`src/loadstar237_converter_docs_extracted.md` for fully extracted content from
prior research session.

---

## Leads to Follow (Format-Specific)

1. **Download songsmith.1b39 (62 KB, load=$1B39)** from discmaster and run
   seed_disassembly. The load address $1B39 is unusual (mid-RAM, below $4000).
   URL: https://discmaster.textfiles.com/file/5218/237.d81/songsmith/songsmith.080d/songsmith.1b39
   (This is binary RE — flagged as OPEN per research-only constraint.)

2. **Mount CSDb d64 in VICE/c1541** and read the M.*/W.* files as binary to understand
   the NATIVE SongSmith note/instrument format before conversion.
   c1541 command: `c1541 Songsmith-Loadstar.d64 -list` then `-read M.ALOUETTE`.

3. **Compare M.FUNICULI with W.FUNICULI bytes** — the two files should clarify
   the split between note data (M.) and instrument/waveform data (W.).
   The W. file is exactly 1 disk block (254 usable bytes) per SmithSID docs.

4. **SSSPCONV.O program** — the converter from SongSmith to SID/MUS format.
   Disassembling this would reveal EXACTLY how the native format maps to MUS.
   It was referenced in the CSDb d64 strings as `"SSSPCONV.O",DN`.

5. **Verify MUS header presence:** Do SongSmith-exported SIDs actually have the
   6-byte voice-size MUS header at their load address? Binary analysis was
   inconclusive (size values read as implausibly large in raw LE interpretation).
   Check with the disassembly of the player's init/play routines vs the MUS spec.

6. **Voice boundary RE:** Run `find_first_divergence.py` or a write-log capture
   on one of the Beggerow SIDs to observe the exact write pattern for all 3 voices.
   This reveals whether voices are written simultaneously or sequentially, and the
   timing/loop structure.

7. **Tempo 1 vs Tempo 2 in native format:** What is the byte encoding difference
   between the two tempo choices offered at conversion time?

8. **Download Loadstar 237 full D81** from discmaster item 5218:
   https://discmaster.textfiles.com/browse/5218/237.d81
   The issue also has `t.sidsmith` (SongSmith→SID converter docs) and
   `t.smithsid` (SID→SongSmith converter docs) — already extracted in prior session
   into `src/loadstar237_converter_docs_extracted.md`.
