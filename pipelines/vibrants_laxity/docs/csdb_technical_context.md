---
source_url: https://blog.chordian.net/2017/01/11/my-computer-chronicles-part-2/; https://sidpreservation.6581.org/sid-trackers/; https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/; https://www.vgmpf.com/Wiki/index.php/Thomas_Petersen; https://blog.chordian.net/sf2/; https://github.com/Chordian/sidfactory2
fetched_via: direct
fetch_date: 2026-06-15
author: JCH (Chordian), VGMPF, sidpreservation.6581.org
content_date: 2017-2026
reliability: secondary
---

# Vibrants/Laxity — Technical Context and Format Knowledge

## What the Laxity Editor Is

"The early TFA / Laxity Editors are more-or-less convenient frontends for HEX and assembler editing."
(sidpreservation.6581.org + VGMPF)

This means the editing interface is essentially a hex monitor with a music-routine-aware display —
not a full tracker. Composition involved entering music data as raw hex values, with the editor
providing structured views rather than step-time note entry via keyboard.

"From SID Factory and onwards, his music was composed using tracker-style editing."
(VGMPF — confirming the Laxity editor pre-dates the tracker paradigm)

---

## JCH's First-Hand Account of the Laxity Player (from chordian.net)

JCH (Jens-Christian Huus) reverse-engineered Laxity's player and this is his description:

> "When the author reverse-engineered Laxity's player using a disassembly tool, they discovered
> 'generic labels' requiring detective work to understand the code structure."

> "The author then attempted creating music using 'hexadecimal numbers in the assembler source,'
> leveraging fast compilation cycles for iterative testing."

JCH's own player evolution after studying Laxity:
- Used "almost no CPU time" (Laxity's player was efficient)
- JCH Version 1 (Nov 1988): no sequences, no instruments — pure sequential notes
- JCH Version 2 (Dec 1988): "flexible sequences" where three voices follow each other but
  have completely individual sequences of flexible size → repeatable fragments
- JCH added a packer: "concatenated note steps into fewer bytes with duration indicators"
- JCH added a relocator for runtime memory management

JCH notes about Laxity's music files (from "From JCH's Special Collection" 2018):
> "some compositions had voice playback problems stemming from variable loading in the player code.
> The author resolved this by 'putting NOP bytes' at specific memory locations to prevent
> incorrect data loading."
> "I could enter a different address close to the music data to keep it as one contiguous block,"
> indicating the player and music existed as **separate memory-resident components** rather than
> combined SID files.

---

## Key Format Properties (Synthesised from Multiple Sources)

### Memory Layout (TFA Editor v3.24 era, earliest documented)
- Music data region: **$0F00 – $2000** (+ $80 bytes per additional pattern)
- Instrument table: **$1700** (within the music data region)
- Init / restart entry: **SYS 2304 = $0900**
- Pattern size: implied ~$80 bytes each

### 3x-player variant layout
- Music loads at **$4000** (different base — player called 3× per frame)
- Player itself: 97 bytes (extremely compact)

### Data Structure (from sidid.cfg signature analysis)
- Note/frequency data: table-based lookup (B9 ?? ?? = LDA abs,Y)
- Frequency written as hi+lo pair to $D400/$D401 (and voice offsets +7, +14)
- Instrument indexing: a byte field, masked (AND #imm) and shifted ×4 (ASL;ASL) →
  suggests instrument table entries are 4 bytes wide (or instrument IDs are 2-bit packed)
- Duration counting: DEC abs,X / BNE pattern (count-down timer per note)
- End-of-sequence sentinel: **$FF** (CMP #$FF pattern in NP V21 signature, also common)
- Multiple nested DEC/BPL tempo counters (line 3 of Vibrants/Laxity sig)

### Effect chain (known from register writes in signatures)
- Frequency: $D400-$D401 per voice
- Control/gate: $D404 per voice (waveform + gate in one byte)
- Filter cutoff: $D416 (updated per-frame via sweep logic)
- Likely filter control ($D418) given filter cutoff is driven — but not confirmed from signatures

---

## Format Features: What Composers Did With It

From SID Factory II comparison and chordian notes (about JCH editor, which evolved from Laxity):
- Pattern/sequence system: 3-voice independent sequences of variable length
- Orderlist: sequences ordered into a song (per-voice)
- Instrument editor
- S-command: pointer to effect sub-table (allows 3 simultaneous effects on one channel)
- Players support: vibrato, pulse width modulation, filter, arpeggio, portamento/glide

The Laxity editor predates full tracker features but the driver supports these effects
(confirmed by quality of output in tunes like "Fast Stuff", "Funk Off", etc.)

---

## Zimmers.net Vibrants Collection Structure

URL: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/

```
Vibrants/
├── READ-ME            (941 bytes — collection index)
├── README             (566 bytes)
├── 3x-player/
│   ├── 3xplayer.prg  (97 bytes — Laxity's 3x-speed player routine)
│   └── [8 music .prg files at $4000]
├── Accept/            (JCH editor tunes)
├── Deek/              (JCH editor tunes)
├── Drax/              (JCH editor tunes)
├── JCH+HJ/            (JCH editor tunes)
├── Jens Christian Huus/ (JCH editor tunes)
├── Link/
├── Metal/
├── Scortia/
├── utils/
│   ├── Deluxe Driver-2.0.prg  (7587 bytes)
│   ├── Deluxe Driver-3.0.prg  (11207 bytes)
│   ├── Deluxe Driver-4.0.prg  (19506 bytes)
│   ├── Deluxe Driver-5.0.prg  (9734 bytes)
│   ├── JCH Coder v1.prg       (1663 bytes)
│   ├── JCH Split v1.1.prg     (5071 bytes)
│   ├── Relocate JCH.prg       (2570 bytes)
│   ├── Relocate Laxity.prg    (3921 bytes) ← KEY FILE
│   ├── VibRip50.00.prg        (3074 bytes) ← KEY FILE (music ripper)
│   └── editor/
│       ├── Example Tune.prg   (11761 bytes)
│       ├── JCH Editor-1.4G.prg (15537 bytes)
│       └── JCH Editor-docs.prg (14269 bytes)
```

**Key files for reverse engineering the Laxity format:**
- `Relocate Laxity.prg` (3921 bytes): relocator for Laxity tunes — will contain format-specific
  knowledge about which bytes are addresses to be patched
- `VibRip50.00.prg` (3074 bytes): music ripper — knows how to identify and extract Laxity
  music data from demos/games

---

## SID Factory II — Modern Laxity Player Architecture

From GitHub (Chordian/sidfactory2) and documentation:

The SF2 editor uses numbered driver .prg files (binary C64 code):
- Default driver: **11.05**
- Drivers 11.xx: main modern Laxity-family drivers
- np20 variant: based on JCH NP20 (different engine)

Driver feature timeline (from README):
- 11.02+: pulse program index, tempo change, main volume commands, note delay (0-F ticks)
- 11.03+: filter enable flag bit in instruments
- 11.04+: (further enhancements)
- 11.05: current default

Data organisation in SF2 (modern, may differ from classic Vibrants/Laxity):
- Multiple order lists (songs) sharing sequences and sounds
- Sequences with configurable highlights
- Instrument tables with descriptions
- Command tables with descriptions
- Zero-page address relocation capability

Imported formats: GoatTracker SNG, CheeseCutter CT, 4-ch MOD files.

---

## Scene Context

- Laxity never wrote public documentation for his editor
- Editor was not intended for public release
- Spread through the scene informally; Drax, Scortia, Zonix all used it
- JCH was initially using Laxity's editor; Laxity told him to stop and JCH created his own
- Vibrants formed 1989 by JCH + Link; Laxity joined 1990-09-09
- Both Laxity and JCH players circulated within Vibrants/scene circles
- "VibRip50.00" music ripper suggests the format was well-enough understood to rip from demos

---

## HVSC Corpus by Engine

| sidid engine | SID count | Notes |
|---|---|---|
| `Vibrants/Laxity` | 179 | Classic Laxity Editor era tunes |
| `Laxity_NewPlayer_V21` | 313 | 2006 player (Laxity-coded, for JCH editor tunes) |
| `SidFactory/Laxity` | 39 | 2005 SID Factory era |
| `SidFactory_II/Laxity` | 377 | Current SID Factory II (2020+) |
| `256bytes/Laxity` | 2 | Compact 256-byte player variant |
| **Total Laxity-family** | **910** | |
| `Vibrants/JO` | 130 | Different engine, same group |

The 179 `Vibrants/Laxity` SIDs are the primary target for a decompiler/USF converter.
Primary concentration in: MUSICIANS/L/Laxity/, MUSICIANS/D/DRAX/, MUSICIANS/F/Future_Freak/,
MUSICIANS/H/HeatWave/, MUSICIANS/S/Scortia/, MUSICIANS/Z/Zenox/, MUSICIANS/Z/Zonix/
