---
source_url: multiple
sources:
  - https://archive.org/search?query=SIDin+Ice+Team+Free+Software+Group
  - http://digilander.libero.it/ice00/tsid/sidin/
fetched_via: compiled from multiple sources
fetch_date: 2026-04-11
author: Stefano Tognon (ice00)
content_date: 2002-2015
reliability: secondary
---
# SIDin Magazine — Research Notes

## Overview

SIDin is a fanzine/magazine dedicated to C64 SID music, published by Stefano Tognon (ice00) of
Ice Team Free Software Group. It ran from 2002 to 2015, 15 issues total.

**Archive.org:** https://archive.org/search?query=SIDin+Ice+Team+Free+Software+Group
**CSDb:** search "SIDin" — issues #3–#15 catalogued
**Direct downloads:** http://digilander.libero.it/ice00/tsid/sidin/

---

## Issues and Content Summary

| Issue | Date       | Key Technical Content |
|-------|------------|----------------------|
| #1    | 2002-09-21 | Iseq music tool; Steve Judd Commando arrangement |
| #2    | 2002-11-21 | **David Whittaker's Lazy Jones disassembly** + **Matt Gray's Driller disassembly** |
| #3    | 2003-02-07 | Music Engine pattern searching (SIDID-style fingerprinting), part 1 |
| #4    | 2003-06-21 | **Martin Galway's Arkanoid music routine** (full reverse engineering + source) |
| #5    | 2004-01-11 | Music Engine pattern searching part 2 (Future Composer 1 disassembly example); Chris Huelsbeck interview |
| #6    | 2004-05-08 | Asterion Sid-Tracker analysis; DigiOrganizer internals |
| #7    | 2005-01-09 | Ivan Del Duca's "Modules" engine reverse engineering |
| #8    | 2005-07-30 | Tiny SID Compo entries (256/512 byte): source analysis |
| #9    | 2006-01-14 | Tiny SID Compo 256-byte entries (10 entries with full source) |
| #10   | 2006-07-16 | Tiny SID 2 entries analysis; Richard Bayliss interview |
| #11   | 2007-02-14 | Tiny SID 2 part 2; SID Factory vs Ninjatracker comparison |
| #12   | 2008-05-24 | Tiny SID 2 part 3; Mihaly Horvath (Hermit) interview |
| #13   | 2010-06-28 | (not on archive.org) |
| #14   | 2015-01-25 | (not on archive.org — addendum files on CSDb) |
| #15   | 2015-10-31 | (not on archive.org) |

---

## Rob Hubbard Content in SIDin

**None of the SIDin issues contain a dedicated Rob Hubbard player disassembly.**

Rob Hubbard is mentioned by name in several issues (in interviews and listener preference lists),
but the technical reverse-engineering articles cover other composers:

- Issue #2: David Whittaker (Lazy Jones), Matt Gray (Driller)
- Issue #4: Martin Galway (Arkanoid)
- Issue #5: Future Composer 1 (anonymous/engine example)
- Issue #7: Ivan Del Duca (Modules game engine)

The magazine's general editorial philosophy (from issue #3):
> "if you want to have your preferred music engine reverse engineered by me, please send me an
> email: there's a big probability that I do it (free time permitting)"

It appears Rob Hubbard's engine was never submitted/requested, or was considered too well-documented
elsewhere (the C=Hacking #5 disassembly by Anthony McSweeney was already in wide circulation).

---

## The Rob Hubbard Disassembly (C=Hacking #5, not SIDin)

The primary Rob Hubbard player disassembly is by **Anthony McSweeney**, published in
**C=Hacking issue #5**. It is available at:

- https://www.1xn.org/text/C64/rob_hubbards_music.txt
- Also mirrored on codebase64 and many C64 text archives
- Already archived in this project at: `src/hubbard/docs/chacking_hubbard_disassembly.txt`

---

## SIDin #4 — Martin Galway's Arkanoid Disassembly (Most Relevant Issue)

This is the most technically detailed player disassembly in SIDin, comparable to the Hubbard
C=Hacking article. Full source is included in the PDF (pages 23–98).

**Download:** http://csdb.dk/getinternalfile.php/92941/SIDin4.zip
**Archive.org:** https://archive.org/details/SIDin_04_2003-06-21_Ice_Team_Free_Software_Group

### Architecture Summary (from article)

Songs are structured as: tune pointer + 3 voice track addresses + min duration byte.

```
tune1:
  .byte <tune1_voice1, >tune1_voice1
  .byte <tune1_voice2, >tune1_voice2
  .byte <tune1_voice3, >tune1_voice3
  .byte $09    ; minimum duration
```

No separate tracks/patterns division — instead uses subroutine calls (JSR/RTS pseudo-opcodes
within the music data) to share patterns. Each voice has separate (but identical) player code —
not indexed — a deliberate choice for simplicity.

### Instruction Set (music bytecode)

| Hex      | Mnemonic | Description                                        | Voices |
|----------|----------|----------------------------------------------------|--------|
| 00..5F nn | Note/dur_tab | Play note, duration from table                 | 1,2,3  |
| 60..BF nn | Note/dur | Play note (xx-$60), duration in next byte          | 1,2,3  |
| C0       | RTS      | Return (also terminates track)                     | 1,2,3  |
| C2 lo hi | JSR      | Call subroutine at lo/hi                           | 1,2,3  |
| C4 lo hi | JMP      | Jump to lo/hi                                      | 1,2,3  |
| C6 ht lo hi | JSRT  | Call subroutine, transpose by ht halftones         | 1,3    |
| CA id va | SET      | Set instrument table value at index id to va       | 1,2,3  |
| CC nn    | FOR      | Repeat loop (nn times)                             | 1,2,3  |
| CE       | NEXT     | End of FOR loop                                    | 1,2,3  |
| D2 nn lo hi | SETNI | Set first nn instrument table entries from address | 1,2,3 |
| D4 lo hi | INSTR    | Set 5 instrument params (control/ADSR) from address| 1,2,3  |
| D6 nn va | SETCI    | Set current instrument value at index nn to va     | 1,2,3  |
| D8 lo hi | EXCT     | Execute machine code at address (voice 3 only)     | 3      |
| DC id v1 v2 | SET2I | Set 2 values at instrument table index id         | 2,3    |
| DE id v1 v2 | SET2CI | Set 2 values at current instrument table index id | 1,2,3 |
| E0       | LF3      | Set low filter on voice 3 with max resonance       | 3      |
| E2 lo hi | FILTA    | Set filter table from address                      | 3      |
| F0 lo hi | SETFI    | Set instrument freq effect (13 values)             | 1,2,3  |

### Instrument Table (29 bytes)

| Offset | Description |
|--------|-------------|
| 00h    | Freq.lo to add per cycle in phase 1 |
| 01h    | Freq.hi to add per cycle in phase 1 |
| 02h–03h | Freq delta for phase 2 |
| 04h–05h | Freq delta for phase 3 |
| 06h–07h | Freq delta for phase 4 |
| 08h    | Number of cycles in phase 1 |
| 09h    | Number of cycles in phase 2 |
| 0Ah    | Number of cycles in phase 3 |
| 0Bh    | Number of cycles in phase 4 |
| 0Ch    | Initial delay cycles before phase 1 |
| 0Dh    | Freq effect flag (bit field) |

### Notable Features
- Self-modifying code to mask sample output via volume register ($D418)
- JMP/JSR 6502 opcodes used directly as music pattern flow control
- Sound effects use same engine but bypass track/pattern system entirely
- 6 octaves used (not full 8 SID supports): notes $00..$5E / $60..$BE
- Notes $5F and $BF are rests

---

## SIDin #2 — David Whittaker (Lazy Jones) + Matt Gray (Driller)

**Download:** http://csdb.dk/getinternalfile.php/92940/SIDin3.zip  *(note: SIDin3 zip on CSDb)*
Actually SIDin #2 is at: https://archive.org/details/SIDin_02_2002-11-21_Ice_Team_Free_Software_Group

Both disassemblies include full 6502 source code with comments. These engines are in the same
general lineage as Hubbard's (pattern-based, table-driven) but have distinct data layouts.

---

## SIDin #3 — Music Engine Fingerprinting (Pattern Searching)

Describes the technique behind SIDID (SID player identification tool) — how to identify which
music engine a SID file was made with by scanning for characteristic byte patterns at known
offsets. This became the basis for SIDID and HVMEC.

Key insight from the article: a fingerprint needs at minimum:
- A unique byte pattern at a fixed offset (to avoid false positives from other engines)
- The memory locations of "OrderPos" (current track position) and "SecPos" (current row)
  for real-time visualization and accurate length detection

---

## Comparison: SIDin Engines vs Rob Hubbard

| Feature               | Hubbard (Monty/Commando) | Galway (Arkanoid) | Whittaker (Lazy Jones) |
|-----------------------|--------------------------|-------------------|------------------------|
| Channels              | 3 (shared code)          | 3 (separate code) | 3                      |
| Pattern system        | Yes                      | Subroutine calls  | Yes                    |
| Instrument format     | 8 bytes                  | 29 bytes          | table-based            |
| Arpeggios             | Yes (octarp, skydive)    | Via freq phases   | Yes                    |
| Vibrato               | Yes                      | Via freq phases   | Yes                    |
| Portamento            | Yes                      | No                | No                     |
| Samples/digi          | No                       | Yes (via $D418)   | No                     |
| Engine size           | ~900-1000 bytes          | Larger            | Compact                |

---

## Sources

- CSDb SIDin search: https://csdb.dk/search/?search=SIDin&type=release
- Archive.org collection: https://archive.org/search?query=SIDin+Ice+Team+Free+Software+Group
- Ice Team direct downloads: http://digilander.libero.it/ice00/tsid/sidin/
- Rob Hubbard disassembly (C=Hacking #5): https://www.1xn.org/text/C64/rob_hubbards_music.txt
- CSDb SIDin #4: https://csdb.dk/release/?id=9230
- CSDb SIDin #2: https://csdb.dk/release/?id=8697 (actually #3 page; #2 is at archive.org)
