---
source_url: various (Usenet/web)
fetched_via: direct
fetch_date: 2026-06-17
author: various
content_date: various
reliability: secondary
---

# SidWinder (Taki/Natural Beat) — Forum, Usenet, and Web Findings

**Scope note:** This document covers Taki's 1999/2000 C64 native music editor
(SIDwinder V01.22 / V01.23 / V01.23 Enhanced). Two UNRELATED modern tools
share the name:
- "SIDwinder" (sidwinder.netlify.app / sidquake.c64demo.com) — 2025
  Genesis Project tool for packaging SIDs into PRGs with EQ visualisers.
  Authors: Raistlin/Genesis Project. Totally different project; do not
  conflate.
- "SIDwinder V1.24 sub030 Enhanced" by Draxish (YouTube demo found,
  relationship to PCH's V1.23 Enhanced unclear — possibly a further fork).

---

## 1. Releases confirmed in CSDb

| CSDb ID | Title | Author | Date |
|---------|-------|--------|------|
| 66494 | SIDwinder V01.22 | Natural Beat (Taki) | 1999 |
| 101758 | SIDwinder V01.23 | Natural Beat (Taki) | 15 Mar 2000 |
| 99574 | SIDwinder V1.23 Enhanced!! | PCH (KGB'92, Unreal) | 17 Apr 2011 |

### V01.22 (CSDb #66494)
- Code and music: Taki (Natural Beat)
- 391 downloads recorded
- No user comments visible in CSDb page

### V01.23 (CSDb #101758)
- Code: Taki (Natural Beat)
- Music: Taki (Natural Beat) + Luca (Fantastic Italian Research Enterprise)
- Testing: Luca (FIRE)
- 534 downloads recorded
- Bundled tunes: Classical, Draxish, Drummer, Glorious, Lost Love, Memories,
  Precisely, Radiation, Realbeat, Southern, Speed Up!, Status Quo,
  Sweet Lullaby, Uncertain (15 compositions)
- 1 production note entry on CSDb; forum discussion available

### V1.23 Enhanced!! (CSDb #99574, PCH 2011)
- Code: PCH (KGB'92, Unreal) + Taki (Natural Beat) [original]
- Released 17 April 2011
- PCH found original code on his hard drive from 2001 and enhanced it
- New feature added: **live piano function** accessible via the "M" key menu
- User comments from CSDb (18 Apr 2011):
  - **Luca:** raised GPL licence questions ("the original GPL licence coming
    from TLC and allowed by Taki" appeared discontinued). Warned of a
    previously-discovered packer bug in longer compositions (endpoints and
    glide/slide functions). Noted TLC had created a fixed packer for Plus/4.
  - **PCH:** confirmed many compositions made in this version without packer
    errors, except one file with an END MUSIC mark issue.
  - **Yogibear:** praised the editor; found "JT Rubicon effects" entertaining.
  - **Reject, FATFrost:** positive reception.
- **Licensing note from Luca:** the tool base is TLC/CNS's SIDwinder V01.23
  under GPL license.

---

## 2. Plus/4 port — SIDwinder V01.23 (Plus/4 World entry)

Source: https://plus4world.powweb.com/software/SIDwinder_V01_23

- Original V01.22 by Taki/Natural Beat (C64)
- Plus/4 conversion & packer rewrite: Levente Hársfalvi (TLC/Coroners)
- Release date: 15 March 2000
- Distribution: Freeware
- Language: English/Hungarian
- PAL only ("may also work on NTSC machines for single speed tunes")
- 64K disk, machine code

### Feature list (from Plus/4 World documentation)

**Music capacity:**
- Up to **32 subtunes** in one music file
- Up to **96 sectors** (256 instructions per sector)
- Up to **64 different instruments**
- Up to **16× music speed** (multispeed)
- Independent volume register control ($1673 and $165D in Plus/4 mapping)
- Three independent SID channels with toggle capability

**Editor components (7 sub-parts, keyboard-accessible):**
1. Track editor
2. Sector editor
3. Glide/slide table edit
4. Disk menu
5. Music options
6. Sound editor — main parameters
7. Wave/arpeggio tables

**Track commands (one byte each, except Jmpxx):**
- Sector playback selection ($00–$5F)
- Transposition (up/down by semitones)
- Volume control
- Volume slides (incremental/decremental)
- Halt functions
- Jump commands (Jmpxx, multi-byte)

**Sector commands:**
- Select instrument ($00–$3F — confirming max 64 instruments)
- Set note duration (1–64 frames)
- Play note (C-1 through A#8)
- Apply glide/slide effects
- Designate sector endpoints

**Sound editor — 7-digit parameter set per instrument:**
- Attack/Decay
- Sustain/Release
- Gate-off counter
- Position pointers for: wave/arpeggio table, filter table, pulse-width
  table, slide table

**Packer (rewritten by TLC for Plus/4 port):**
- Parses and examines all data
- Relocates music to specified memory address
- Configurable zero-page pointer allocation
- Accepts custom identity field text (32 characters)
- Known bug: packer issue with long compositions (END MUSIC mark edge case)
  — fixed version exists for Plus/4 (TLC fix, per Luca's 2011 CSDb comment)

**ASCII Viewer:**
- Standard ASCII display with character conversion
- 80-column display (4×8 charset)
- Print support for PETSCII printers

### Plus/4 clock compensation note
C64 clock: PHI2 = 985,248 Hz (PAL, /18). Plus/4: 17,734,472 Hz /20 ≈
886,723 Hz — approximately one semitone lower. **When porting C64
compositions to Plus/4 SID card: multiply glide speeds and slide table
values by 10/9. Reverse (×9/10) for Plus/4 → C64.** ADSR values also
require manual adjustment.

---

## 3. Source code — confirmed available at zimmers.net

URL: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip
(333.5 KB ZIP — fetched 2026-06-17, binary confirmed accessible)

**File tree visible in the archive:**

Documentation files:
- `COPYING` — licence text
- `GENERAL` — general information
- `HISTORY` — version history
- `README` — readme
- `SUMMARY` — feature summary
- `PLUS4` — Plus/4 specific docs
- `PROGRAM` — program documentation
- `PROGRAMMER` — programmer/format reference (KEY FILE for RE)
- `SIDW0122` — V01.22 reference / changelog

Assembly source files (6502):
- `SRC/ED.ASM` — editor main
- `SRC/PACKER.ASM` — music packer
- `SRC/PLAYER.ASM` — the music player (KEY FILE for RE)
- `SRC/SIDR.ASM` — SID routines
- `SRC/VIEWER.ASM` — ASCII viewer
- `SRC/PLAY0122.ASM` — V01.22 player
- `SRC/PLAY0122.SEQ` — V01.22 sequence data

Binary data files:
- `CHARS`, `MASKS`, `SECTORS`, `TRACKS`, `VCHARS` — editor data

Subdirectories: `SRC/`, `PRE_0123/`, `TOOLS/`

**The `PROGRAMMER` and `PLAYER.ASM` files are the primary RE targets.**
The source is GPL-licensed (per Luca's CSDb comment, originally per TLC).

D64 disk image also available:
https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_C64.d64.gz
(73,918 bytes)

---

## 4. Usenet — comp.sys.cbm mentions

Searches of Google Groups' comp.sys.cbm archive found 4 threads mentioning
SidWinder. None contain format-technical content but they establish community
context:

### "Making / Tracking music on c64" (Jan 2001)
- Author: Fitnak + others including Hukka
- Key quote: "It might not be much more user-friendly than any of the other,
  but it comes with a **very well written documentation** that is non-E133T"
  — confirming the bundled docs were considered comprehensive and accessible.
- Implication: the PROGRAM/PROGRAMMER/SUMMARY docs in the source ZIP are the
  same comprehensive documentation users referenced.

### "Which music editor do you prefer?" (Dec 2000)
- Author: Carlsson, Anders + others
- References "Taki's SidWinder" as a known community option alongside
  other editors of the era.

### "SID — an easy way to compose?" (Jun 2003)
- Author: Flavio "Senesino" FBG + David Holz/White Flame
- Mentions "~10 pages of printable documentation" bundled with SidWinder.
- This matches the `PROGRAM`/`PROGRAMMER`/`SUMMARY`/`GENERAL` files in the
  source ZIP.

### "Commodore Free Magazine, Issue 91" (Mar 2016)
- Author: Stephen Walsh
- Context: Hermit (TEDzakker author) mentions SidWinder as one of the few
  prior Plus/4 music tools: "There's a port of SIDwinder (C64 by Taki,
  ported by TLC), a new PC editor Knaecketraecker, that's all."
- Confirms SidWinder was the dominant native Plus/4 SID tracker before
  TEDzakker.

---

## 5. Author identity confirmed

From HVSC Musicians.txt:
> "Taki (Tak´cs, Bal´zs) / Natural Beat - HUNGARY"

Handle: Taki | Real name: Takács, Balázs | Group: Natural Beat | Country: Hungary

CSDb search for "Taki" confirms his discography includes Agricola (1996),
Black Art (1996), Classical (1996), Craft (1993, Craftmen Company),
Damnation (1993, Craftmen Company), Danko's Remix (1996), plus
"Taki's Music Analyzer V1.0" — a separate C64 tool.

---

## 6. What is NOT found

- No Usenet posts with format-technical details (byte layout, table
  structures, player state machine) found in any accessible archive.
- No published reverse-engineering notes or format specifications found
  beyond what the Plus/4 World documentation describes.
- No HVSC-specific documentation for the SidWinder format found in public
  HVSC DOCUMENTS/ directory.
- The raw source code (PLAYER.ASM, PROGRAMMER doc) was not fetched as text;
  the ZIP is confirmed accessible and is the primary source for RE.

---

## 7. Key derived inferences (from documentation)

Based on the Plus/4 World feature list and track/sector command encoding:

**Song structure:**
- Song = ordered list of **tracks**
- Track = list of **sectors** (pointers into sector pool)
- Track commands include: sector selection, transpose, volume, volume-slide,
  halt, jump (Jmpxx — the only multi-byte command)
- Sector = up to 256 instructions (notes + effects)
- 96 sectors max total in the pool

**Sector command encoding:**
- Instrument select: $00–$3F (6-bit instrument index → max 64 instruments)
- Duration: 1–64 frames
- Notes: C-1 through A#8 (standard chromatic range)
- Glide/slide reference (points into glide/slide table)
- Sector endpoint marker

**Instrument structure (7 parameters):**
- AD (Attack/Decay byte)
- SR (Sustain/Release byte)
- Gate-off counter (duration before gate is released)
- Wave/arpeggio table pointer
- Filter table pointer
- Pulse-width table pointer
- Slide table pointer

**Tables per instrument:**
- Wave/arpeggio table — waveform sequencing + arpeggio
- Filter table — filter cutoff/resonance/mode sequence
- Pulse-width table — pulse width sequence
- Slide/glide table — pitch slide data (shared pool, ref'd from sectors too)

**Speed:**
- Up to 16× multispeed (CIA/VBI divisor)

**Volume:**
- Track-level volume commands + volume slides via $D418

---

## Leads to follow

1. **Primary RE target — source ZIP:**
   https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip
   Specifically: `SRC/PLAYER.ASM` (runtime player), `PROGRAMMER` (format
   reference doc), `PROGRAM` (user manual), `HISTORY` (version log).
   Download and extract to `pipelines/sidwinder/docs/`.

2. **D64 disk image:**
   https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_C64.d64.gz
   Mount and inspect with cbmconvert / c1541 to read PETSCII docs on-disk.

3. **CSDb V01.23 production notes:**
   https://csdb.dk/release/?id=101758
   "1 production note" entry visible — fetch the actual note text (may
   require direct CSDb browse with JS enabled).

4. **PCH's enhanced version (#99574) download:**
   https://csdb.dk/release/?id=99574
   Download D64, mount, examine what the "live piano" function changes +
   any in-disk docs about new features.

5. **FTP path (commodore.ca mirror, zimmers FTP):**
   `ftp.funet.fi:/pub/cbm/c64/audio/editors/` — check for any plain-text
   documentation files separate from the ZIP.

6. **Plus/4 World download mirrors** carry the full package with source:
   https://plus4world.powweb.com/software/SIDwinder_V01_23
   Multiple mirrors listed: Rulez.org, Zimmers, ko2000.nu, commodore.ca.

7. **TLC/Coroners (Levente Hársfalvi)** — the Plus/4 porter who rewrote the
   packer and added GPL licence. May have additional format documentation
   or know of packer bug details. Search CSDb for TLC scener profile.

8. **Luca (FIRE)** — tested V01.23, active commenter in 2011, warned of
   packer bug. May have additional technical insights. CSDb scener: Luca /
   Fantastic Italian Research Enterprise.

9. **comp.sys.cbm archive (Google Groups) threads to read in full:**
   - "Making / Tracking music on c64" Jan 2001 (Fitnak thread)
   - "Which music editor do you prefer?" Dec 2000 (Carlsson thread)
   URLs: search https://groups.google.com/g/comp.sys.cbm with
   `sidwinder` — the 4 threads found are indexed but JS-gated.

10. **SIDwinder V1.24 sub030 Enhanced - Draxish (YouTube):**
    https://www.youtube.com/watch?v=6ZsX3D_vUuY
    A further fork/enhancement; watch video for any UI/format reveals.

11. **"Taki's Music Analyzer V1.0"** — a separate Taki tool found in CSDb
    search results. May shed light on internal format (an analyzer
    presupposes a known binary layout). Find CSDb release ID and fetch.
