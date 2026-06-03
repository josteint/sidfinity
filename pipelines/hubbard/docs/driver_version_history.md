---
source_url: "multiple"
  - https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)
  - https://www.lemon64.com/forum/viewtopic.php?t=64066
  - C=Hacking #5 (McSweeney, 1993) — print magazine
  - C64Audio.com "Master of Magic" blog series
  - chipmusic.org thread (URL not recorded)
  - sidid.cfg (local tool file)
fetched_via: "compiled from multiple sources"
fetch_date: 2026-04-11
author: "compiled locally (no single author)"
content_date: "1984-2026"
reliability: secondary
---
# Rob Hubbard C64 Driver — Version History and Technical Evolution

Sources: VGMPF wiki, C64Audio.com "Master of Magic" blog series, Lemon64 forums,
C=Hacking #5, chipmusic.org thread, sidid.cfg

## Phase 1: "Razzmatazz" Driver (Late 1984)

- First driver, very limited
- Used for: Up Up and Away (before Nov 1984)
- Not much is known about this version
- Thing on a Spring "couldn't have been done properly in the Razzmatazz driver"

## Phase 2: "Classic" Driver (Early 1985 — March 1986)

The main driver used for approximately 30 songs. This is the version documented in
C=Hacking #5 (McSweeney disassembly of Monty on the Run).

### Core Architecture
- ~900-1000 bytes of code
- Three entry points: init ($+0), play ($+3), stop ($+6)
- Main loop runs 3 times per frame (once per SID channel)
- Two processing layers: NoteWork (note sequencing) + SoundWork (synthesis effects)
- Written in Mikro Assembler

### Features Present from the Start
- Logarithmic vibrato (compensated across octaves)
- Simple PWM sweeping (~50% to ~88% duty cycle)
- Multi-song support (song number in accumulator on init)
- Variable-length note encoding (1-4 bytes)
- 8-byte instrument definitions

### Additions During Phase 2

**Action Biker (early 1985):** Characteristic drum synthesis
- Square wave for 1 frame (20ms)
- White noise for 1/32nd of a second
- Same wave falling by 15 Hz
- Inspired by Simmons electronic drums

**Thing on a Spring (mid 1985):** Arpeggios and SFX
- Octave arpeggios (alternating note and note+12 each frame)
- Up to 16 sound effects, each using two voices
- Music voices 1-2 suppressed during SFX playback

**Monty on the Run (Sept 1985):** Pitch bending
- Portamento effect added to the note encoding
- "Skydive" effect (slow frequency descent) — named in C=Hacking #5
- Guitar solo section served as pitch bend test

### Known Bug
Until early 1986: "The first time the driver runs, the note on voice 3 is skipped."
This affects the first ~30 songs.

### Games Using Phase 2 Driver
Confuzion, Thing on a Spring, Monty on the Run, Action Biker, Crazy Comets,
Commando, Hunter Patrol, Chimera, The Last V8, Battle of Britain, Human Race,
Zoids, Rasputin, Master of Magic, One Man & His Droid, Game Killer,
Gerry the Germ, Geoff Capes Strongman Challenge, Phantoms of the Asteroids,
Kentilla, Thrust, International Karate, Spellbound, Bump Set and Spike,
Formula 1 Simulator, Video Poker, Warhawk, Proteus, and others

## Phase 3: Transitional Period (April — September 1986)

### Cross-Platform Innovation
Hubbard started composing for Atari 8-bit (POKEY chip) around this time. The Atari driver
work introduced new programming concepts: "vectors, wavetables, and function pointers."
These innovations were brought back to the C64 driver.

### Hollywood or Bust
An experimental driver incorporating Atari-derived concepts appeared in this game. This
represents a bridge between the classic and new drivers.

### Noise/Triangle Drums
Improved drum method: cycling rapidly between noise and triangle wave (called the
"We M.U.S.I.C." method). This replaced the earlier square-then-noise approach.

### Filter Support (mid-1986)
Started using SID's built-in analog filter for the first time.
PROBLEM: "the filter varies with every machine and several of Hubbard's melodies
sounded muffled to many gamers."
Recommended VICE settings: 6581 (ReSID) with bias >= 540.

### Music/SFX Change
Music and sound effects could no longer play simultaneously (earlier versions allowed it).

## Phase 4: "New" Driver (September 1986 — 1987)

### W.A.R. (Programmed April 1986, Released September 1987)
"A much more serious-sounding driver for a new, more serious creative outlook."
This represents the major driver rewrite.

### March 1987: Table-Based Drums
Added table-driven drum synthesis. Previously only Mark Cooksey and Martin Galway
had used this approach. Allows more complex multi-step drum sounds.

### July 1987: Table-Based PWM
Added table-driven pulse width modulation. Instead of simple up/down sweeping,
PWM patterns can now follow arbitrary sequences.

### Post-July 1987: PCM Sample Playback
- Unsigned 4-bit PCM via $D418 volume register
- "The first to loop in the middle" (sample loop points)
- Developed in approximately 1.5 hours
- Final capability: "play 2 samples plus a SID tune" (never used in released games)
- This is the "Rob_Hubbard_Digi" variant in SIDID

### Games Using Phase 4 Driver
Sanxion, Lightforce, W.A.R., Delta, ACE II, Thundercats, Auf Wiedersehen Monty,
Chain Reaction, Mega Apocalypse, Nemesis the Warlock, Bangkok Knights, IK+,
Star Paws, Hydrofool, Shockway Rider, Skate or Die, and others

## Phase 5: Electronic Arts Period (1988)

Different drivers for EA games. These are post-"classic" and may have different
data format structures. Games: Jordan vs. Bird, Kings of the Beach, Power Play Hockey.

## Technical Trick: Frequency Table Variable Abuse

Source: Lemon64 (https://www.lemon64.com/forum/viewtopic.php?t=64066)

"One of the coolest technical tricks was to place player variables right behind the
frequency table: by using out-of-range pitches, those variables could then be used for
frequency modulation effects. At the start of the Commando main theme, Rob used the
in-pattern-position variables to create the iconic 'galloping down the stairs' staccato
effect."

This means decompiled note data may contain pitch values beyond the normal musical range
that are actually addressing player workspace variables as frequency sources.

## Composition Method

Hubbard composed on paper in standard musical notation, writing hexadecimal numbers
alongside the notes, then typing them directly into the assembler. He never used a GUI
editor. The format is "duration based with notelengths entered as length-1 plus various
flags for pauses and instrument changes."

## Composers Who Used/Modified the Driver

### With Permission or Assistance
- **Giulio Zicchi** — Modified variant (separate SIDID signature)
- **Johannes Bjerregaard** — Modified variant (separate SIDID signature)  
- **John De Margheriti** — With Hubbard's direct assistance
- **Pablo Toledo** — Used the driver

### Without Permission (ripped the code)
- **Jeroen Kimmel** (Red / The Judges) — Used the Crazy Comets driver for demos
  (Hubbard responded by scrambling his code/data throughout 1987)
- **Jeroen Tel** — Studied and used Hubbard's code
- **Neil Baldwin** — Studied Hubbard's code
- **Thomas Petersen** — Studied Hubbard's code
- **Jochen Hippel** — Used Hubbard's code for Atari ST conversions

## Source Code Status

- Hubbard lost all pre-EA source code in spring 1997
- Rumored cause: housecleaner threw away his floppy disks while he was at a hotel
- Up to mid-1986, some source code was accidentally leaked when Hubbard compiled and
  released soundtracks himself
- The "Master of Magic" book by Chris Abbott (C64Audio.com) contains 6502 assembly
  driver excerpts from the research period

## SIDID Detection Summary

| Signature | Description |
|---|---|
| `Rob_Hubbard` | Main player (6 patterns, any match identifies) |
| `Rob_Hubbard_Digi` | Sub-signature: 4-bit PCM digi playback variant |
| `Rob_Hubbard (Giulio_Zicchi)` | Sub-signature: Zicchi's modifications |
| `Rob_Hubbard (Bjerregaard)` | Sub-signature: Bjerregaard's modifications |
| `Paradroid/HubbardEd` | Scene editor built on the Hubbard architecture |
| `Paradroid/Lameplayer` | Simplified Paradroid variant |
| `Jason_Page/RobTracker` | Based on Hubbard's digi routine (separate player) |
