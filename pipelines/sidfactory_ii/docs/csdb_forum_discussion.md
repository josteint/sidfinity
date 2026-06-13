---
source_url: https://csdb.dk/forums/ + https://blog.chordian.net/computer-timeline/ + https://csdb.dk/scener/?id=677 + https://csdb.dk/release/?id=33785 + https://csdb.dk/release/?id=101622
fetched_via: direct
fetch_date: 2026-06-13
author: various (JCH/Chordian, Laxity, scene community)
content_date: 2000-2026
reliability: primary (CSDb direct) + secondary (blog synthesis)
---

# SID Factory II — Scene Discussion, Lineage, and Developer Commentary

## Player Lineage: OldPlayer → NewPlayer → SID Factory II

### JCH's Computer Timeline (from blog.chordian.net/computer-timeline/)

This is JCH's (Jens-Christian Huus / "Chordian") own account of the development lineage:

**April 1987**: JCH starts programming music composition tools on C64 — creates "OldPlayer".

**June 1988**: JCH "reverse engineered Laxity's C64 music player and started composing in it."

**July 1988**: JCH develops "NewPlayer" (the progenitor of all subsequent NP versions).

**1989 (Feb–Jul)**: Rapid iteration:
- NewPlayer v05.02 (Feb 1989)
- NewPlayer v06.01 (Apr 1989)
- NewPlayer v14.G0 and v15.G0 (May 1989)
- NewPlayer v12.G3 and v15.G6 (Jul 1989)
- Editor: ED2.53/D13/09.01 (May 1989) + NP-PACKER V2.5 + RELOCATOR V1.1

**1990–1991**: Further versions:
- NewPlayer v17.G1 (Oct 1990)
- NewPlayer v20.G4 (May 1991) — last standard player on C64
- ED3.04/D15/20.G4 (Aug 16, 1991) — final editor, composed "using Einstein's EASS Amiga utility"

**Note on version naming**: The version string encodes `vMM.Gn` where MM is a major version and Gn is a generation suffix. The "20.G" prefix is what the SF2 JCH converter checks for at address `0x0fee`.

**1991–1994**: JCH moves to PC (AdLib series).

**2019 (July)**: Laxity releases first alpha build of SID Factory II in a private group.

**2020 (May)**: JCH joins SF2 development. Releases SF2Converter. Development public from June 2020.

**2020–2026**: Ongoing collaborative development with Youth (Michel de Bree).

---

## Laxity's Scene Background (from CSDb scener #677)

**Real name**: Thomas (surname not listed; full name Thomas Egeskov Petersen from other sources)  
**Country**: Denmark  
**Active**: August 1987 – present  
**Groups**: Vibrants (since Sep 1990), Maniacs of Noise (since Feb 1990), Bonzai (since Jan 2015), MultiStyle Labs (since Nov 2023)  
**Former**: Starion (1988–1990), The Flexible Arts (1989–1990, founded by Laxity), Wizax

**Music and player development history:**
- Began composing C64 music 1986–1987
- Created personal music players from the start
- JCH reverse-engineered Laxity's player in 1988 (see above)
- Resurgence 2005–2006: developed SID Factory 0.5 (alpha 1) and JCH NewPlayer 21.g5
  - Note: JCH NewPlayer 21.g5 has Laxity as sole code credit (CSDb #33785)
- 2019: Started SID Factory II

**Earlier Laxity editors (C64-era):**
- Laxity Editor v/34-3.35 (1990)
- Laxity Editor v/32-3.34 (1990)
- Laxity Relocator v1.20 and v1.18

---

## JCH NewPlayer CSDb Releases

### JCH NewPlayer 21.G6 — CSDb #101622
- **Date:** 2000
- **Source:** https://csdb.dk/release/?id=101622
- **Credits:** Glover (Samar Productions) — Code; JCH (Vibrants) — Code
- **Downloads:** Jch_Tools.zip (721 dl), 21G6_GLOVER.txt (188 dl), SRC_JCH_Glover.zip (169 dl — source code)
- **Notes:** Source code released. Community note: "Sources added ;)" (Isildur, Feb 2016).

### JCH NewPlayer 21.g4 beta (21.b4) — CSDb #20112
- **Date:** 27 August 2005
- **Credits:** Maniacs of Noise and Vibrants

### JCH NewPlayer 21.g4 Final — CSDb #26563
- **Date:** 16 January 2006
- **Credits:** Maniacs of Noise and Vibrants

### JCH NewPlayer 21.g5 — CSDb #33785
- **Date:** 9 May 2006
- **Source:** https://csdb.dk/release/?id=33785
- **Credits:** Laxity (Maniacs of Noise and Vibrants) — Code only
- **Notes:** Community: "Big improvement over the classic NP players."
  Should be used with JCH Editor V3.04 20G4.
  Also known as "np21.g5".

---

## CSDb Forum: "From JCH NewPlayer file to SID — how?" (roomid=10, topicid=5698)
- **Source:** https://csdb.dk/forums/index.php?roomid=10&topicid=5698
- **Content retrieved:** Yes

Key technical points from discussion:

**Standard JCH load addresses:**
- Init address: `$1000`
- Play address: `$1003`

**Conversion workflow:**
1. Extract PRG from .d64 disk image
2. In SID editor: set init=$1000, play=$1003
3. Save as .sid format

**JCH packer:** Available on the Vibrants page. Can reduce size. Warning: "tunes sounding different after the packing" was reported as possible.

**Alternative tool mentioned:** AcidTrackMusicDevelopmentSystem 3.2 — produces SID files directly with improved packing.

---

## CSDb Forum: SID Factory II (roomid=14, topicid=142903)
- **Source:** https://csdb.dk/forums/?roomid=14&topicid=142903
- **Retrieval status:** Partial (503 on one attempt, partial content on another)

**Key points recovered:**

- JCH and Laxity launched SF2 BETA in June 2020 acknowledging it was "quite stable" but missing sub-tunes support at launch.
- Linux branch merged into master in September 2020.
- Build system: `make dist` for distribution.
- Compiles "with almost zero warnings" on Ubuntu 20.04.1 LTS.
- SDL-based cross-platform application.
- Note about keyboard bindings on Linux (virtual machines may have issues).
- Groepaz recommended: zip artifacts after compilation, let distro maintainers handle packaging.
- Community resources: Facebook group, user manual, YouTube tutorials (latest: November 2024).

---

## Developer Commentary Highlights (from CSDb release comments)

**Youth (build 20211230 comment):**  
"Source code and changelog at https://github.com/Chordian/sidfactory2"  
→ This is the canonical source for the complete changelog.

**Youth (build 20221007 comment — key bugs fixed):**
- "Crash when converting NP20 and GT tunes"
- "Crash when using a loop point beyond position 128"
- "A bug where sometimes you couldn't edit sequences before hitting the play button"

**Youth (build 20231002 — window scale note):**  
"Configuration parameter Window.Scale now has a range from 1.0 to 10.0, so users can blow up the screen even bigger."

**Youth (build 20260314):**  
"ASID support! Thanks to Tubesockor you can now use any hardware SID device that supports ASID directly in SF2!"  
"Fullscreen support for distraction-free editing"  
"Optional C64 ROM font. Half the height of the original 16p font, meaning twice the number of rows."

---

## SID Factory 0.5 (alpha 1) — First Public Release Notes (CSDb #39519)

- **Date:** 2 September 2006
- **Source:** https://csdb.dk/release/?id=39519
- **Author:** Laxity (Maniacs of Noise / Vibrants)

Technical features:
- **Dynamic multispeed switching**: primary design goal
- **Pattern editing**: instrument and slide support
- **Tempo table**: alongside multispeed capability
- **Full-screen pattern editor** ("full screen almost for editing the pattern")
- **Voice pointers**: "set pointers to the various tables from the voice itself"
- **JCH migration path**: designed to make migration from JCH editors easy

Driver versions in 0.5 alpha:
- Driver 5.02: Updated — now has portamento functionality
- Driver 6.03: Corrected severe bug in Driver 6.02
- 4 demo SID files included

**Key implication for decompiler:** The driver numbering in SID Factory II (11–16) represents a continuation of the numbering scheme started in SID Factory 0.5 (which had drivers 5 and 6). Drivers 7–10 presumably existed in intermediate private builds between 2006 and 2019.

---

## Relationship to DMC (Data MusiCom / Dynamic Music Composer)

From research: The SF2 forum discussion mentions converting NP20 and GT tunes as the two primary import paths. No direct DMC (Data MusiCom — the engine in this repo's `pipelines/dmc/`) relationship was recovered. The "DMC" acronym in the C64 scene also refers to other tools; the SID Factory II lineage is: Laxity Editor → JCH NewPlayer (JCH reverse-engineered Laxity) → JCH NewPlayer 21.gX → SID Factory 0.5 → SID Factory II. This is a SEPARATE lineage from the DMC player family used in commercial Commodore game music.

Note from sidid.nfo (https://github.com/cadaver/sidid/blob/master/sidid.nfo): sidid classifies SID Factory II tunes under its own engine tag; this confirms SF2 produces a recognizable engine signature distinct from JCH/DMC.

---

## Leads to Follow

1. **Documentation folder from a release ZIP** — highest priority for exact driver specs. Each `.txt` file in `documentation/` describes one driver's byte layout. Fetch the zip and extract.
2. **User manual PDF** (build 20260314, 106 downloads) — most up-to-date. URL pattern: check csdb.dk #260181 download links.
3. **JCH NewPlayer 21.G6 source code** (`SRC_JCH_Glover.zip`, csdb.dk #101622) — has NP21.G6 6502 source, useful for understanding the player format that SF2 imports.
4. **NP20 source tunes** (`NP20_Source_Tunes_v1.zip`, from build 20210104) — real-world NP20 files for format validation.
5. **Retry CSDb forum 142903** — the main SF2 developer thread; was 503 at scrape time.
6. **ChipMusic.org thread** https://chipmusic.org/forums/topic/24826/ — returned 403; may have extensive format discussion from the broader tracker community.
7. **DeepSID player** (https://deepsid.chordian.net/) — JCH's web player; may document which engines it identifies.
8. **Laxity Editor v3x releases** — find CSDb entries for `Laxity Editor v/34-3.35` and `v/32-3.34` to understand the pre-JCH-collaboration format.
9. **sidid.nfo classification of SF2** — the cadaver/sidid repository has detection signatures for SF2; cross-reference for engine fingerprinting.
