---
source_url: https://csdb.dk/scener/?id=677 (Laxity); https://csdb.dk/scener/?id=626 (JCH); https://csdb.dk/release/?id=26563 (NP21); https://github.com/cadaver/sidid/blob/master/sidid.nfo; https://sidpreservation.6581.org/sid-trackers/
fetched_via: direct
fetch_date: 2026-06-15
author: various
content_date: 1989-2026
reliability: primary
---

# Vibrants/Laxity Player — Version History & Lineage

## Author Profile

**Thomas Egeskov Petersen (Laxity)**
- Handle aliases: Laxity, The Sad Sausage
- Groups: Starion → The Flexible Arts → (joined Vibrants 1990-09-09) → Maniacs of Noise → Bonzai → MultiStyle Labs
- Country: Denmark
- CSDb: https://csdb.dk/scener/?id=677
- Started C64 composition: 1986-87
- Made own player/editor for first composition era (c.1987–1990)

## Version Timeline

### Pre-TFA period (~1987–1988)
- Laxity wrote initial music routine(s) before any public release
- Composition was hex-based: typing music data directly in a monitor
- JCH later described studying Laxity's player via disassembly to learn from it
- "The early TFA / Laxity Editors are more-or-less convenient frontends for HEX and assembler editing"
  (source: VGMPF + sidpreservation.6581.org)

### TFA Editor V3.24 / "v/26-3.24" (CSDb #215790, 1989)
- Sequencer version 26 (v/26), driver version 3.24
- Released while Laxity was in Starion / The Flexible Arts
- Load/save NOT yet implemented — save manually from $0F00 to $2000 + $80/pattern
- Instrument data at $1700, SYS 2304 ($0900) to restart

### Laxity Editor v/32-3.34 (CSDb #122333, 1990)
- Sequencer version 32, driver version 3.34
- Key property: **does NOT patch loaded music with the current routine** → allows editing older
  tunes with their original driver (backward compatibility preserved)
- Tunes made in this version: Fast Stuff, Wow Reggae, Squamp, Ghosts, Funk Off, + Scortia/Zonix attempts
- Likely released late 1989

### Laxity Editor v/33-3.35 (no separate CSDb entry found; intermediate version)
- Mentioned in production notes for v/32-3.34 and v/34-3.35

### Laxity Editor v/34-3.35 (CSDb #142168, 1990-10-17)
- Sequencer version 34, driver version 3.35
- **Later versions (v/33, v/34) PATCH loaded music with the current musicroutine** (unlike v/32)
- "Likely the last incarnation of both sequencer (v/34) and driver (3.35)"
- Tunes: Zimxusaf I, Well Baby, Syncopated, Sax Nuddle, Pige Bluse, Oh That, On One,
  A Trace of Space, + Drax's Laxity editor attempts

### 3x-player variant (Laxity, c.1990)
- A simple player routine written by Laxity to call the music routine 3 times per frame
- Available at zimmers.net: `audio/Vibrants/3x-player/3xplayer.prg` (97 bytes)
- Music for this format loads at $4000 (different from standard format)
- 8 example tunes included (mcoolkaf, meastend, msyncopa, mwasteii, myieldpo, mzimxusa, soap1440, sweet144)

### Post-editor era (~1990 onwards)
- Laxity joined Vibrants (1990-09-09) and continued using the v/34-3.35 driver
- The editor was "never intended to go public" and never received full documentation
- Laxity told JCH to stop using his editor → JCH created his own (JCH Editor, 1988+)

---

## Relationship to JCH Editor

From JCH's own account (blog.chordian.net):
1. JCH disassembled Laxity's player and studied the code structure
2. JCH used "generic labels" from the disassembly
3. JCH composed music by typing hexadecimal numbers into a monitor, similar to Laxity
4. First JCH editor (Nov 1988): no sequences, no instrument editor — pure notes
5. Second JCH editor (Dec 1988): added flexible sequences (the core innovation)
6. JCH added packer (concatenates notes into fewer bytes with duration indicators) and relocator
7. Klaus (Link of Cheyens) was first external JCH editor user

The JCH editor evolved into a completely separate engine from the Laxity editor. The HVSC
classifies them as different player families (Vibrants/Laxity vs JCH_NewPlayer).

---

## Player Evolution (Laxity → SID Factory)

| Era | Player/Tool | CSDb | Notes |
|-----|------------|------|-------|
| 1989-1990 | TFA/Laxity Editor v3.24-3.35 | #215790, #122333, #142168 | Original editor era |
| 1990s | Vibrants/Laxity player (embedded in tunes) | — | 179 HVSC SIDs |
| 2005 | SID Factory 0.5 alpha 1 | #39519 | New cross-platform editor |
| 2006 | JCH NewPlayer V21.G4 Final | #26563 | Player for JCH Music Editor, coded by Laxity |
| 2020+ | SID Factory II | #210571+ | Current cross-platform editor, still uses C64-native drivers |

---

## Relocators

| Tool | Source | Notes |
|------|--------|-------|
| Laxity Relocator V1.18 | CSDb #128192 | Older; message "All code was done by Thomas Egeskov Petersen" at $8000 |
| Laxity Relocator V1.20 | CSDb #126841 | Newer; by Laxity himself |
| Relocate Laxity.prg | zimmers.net utils/ | 3921 bytes, part of Vibrants collection |

---

## SID Factory II Driver Versions (modern Laxity players)

The SID Factory II repository contains .prg driver files that are direct C64-native descendants
of the Laxity player tradition:
- Version 11.xx series (sf2driver11_00 through 11_05): main modern driver
- Version 12.xx, 13.xx, 14.xx, 15.xx, 16.xx series
- np20 variant (sf2driver_np20_00.prg): based on JCH NP20

These are binary C64 PRG files. Source code is NOT in the sidfactory2 repo.
The HVSC classifies 377 SIDs under `SidFactory_II/Laxity`.
