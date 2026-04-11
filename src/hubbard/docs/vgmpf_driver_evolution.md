---
source_url: https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)
fetched_via: direct
fetch_date: 2026-04-11
author: unknown
content_date: unknown
reliability: secondary
---
# Rob Hubbard C64 Driver Evolution
Source: https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)

## Timeline

### Late 1984 / Early 1985 — Initial Driver
- Written in 6502 Assembly using Mikro Assembler
- Supported logarithmic vibrato and simple PWM (sweeping from ~50% to ~88%)
- First game: Confuzion

### Action Biker (~early 1985) — Drum Synthesis
- Introduced characteristic drum effect: selected wave (usually square) plays for 1 frame (20ms), then white noise for 1/32nd, then same wave falling by 15 Hz
- Two-week development period

### Thing on a Spring (1985) — Arpeggios + SFX
- Added octave arpeggios
- Added support for up to 16 sound effects
- Each SFX uses two voices; music voices 1 and 2 suppressed during SFX playback
- BUG: First time driver runs, note on voice 3 is skipped (persisted until early 1986)

### Throughout 1986 — Noise/Triangle Drums, Filter
- Improved drum method: cycling rapidly between noise and a triangle wave
- In mid-1986, started using SID's built-in filter
  - PROBLEM: "the filter varies with every machine and several of Hubbard's melodies sounded muffled to many gamers"
- Limitation introduced: music and SFX could no longer play simultaneously

### March 1987 — Table-Based Drums
- Added table-driven drum method (previously only Mark Cooksey and Martin Galway had done this)

### July 1987 — Table-Based PWM
- Added table-driven PWM method

### Post-July 1987 — PCM Playback
- Added unsigned 4-bit PCM playback, "the first to loop in the middle"
- Developed in approximately 1.5 hours
- Final driver could "play 2 samples plus a SID tune" (never used in released games)

## Games Using Each Driver Variant

### "First 30" — Early driver (Monty on the Run variant)
Confuzion, Thing on a Spring, Monty on the Run, Action Biker, Crazy Comets,
Commando, Hunter Patrol, Chimera, The Last V8, Battle of Britain, Human Race,
Zoids, Rasputin, Master of Magic, One Man & His Droid, Game Killer,
Gerry the Germ, Geoff Capes Strongman Challenge, Phantoms of the Asteroids,
Kentilla, Thrust, International Karate, Spellbound, Bump Set and Spike,
Formula 1 Simulator, Video Poker, Warhawk/Proteus, and more

### Later driver (with table-based features, filter support)
Sanxion, Delta, ACE II, Skate or Die, and others from 1986-1988

## Source Code Status
Source code lost since spring 1997; reportedly discarded by housecleaner while Hubbard traveled.

## Identification Signatures (from sidid/player-id)

### Rob_Hubbard (standard player)
```
BD ?? ?? 99 ?? ?? 48 BD ?? ?? 99 ?? ?? 48 BD ?? ?? 48 BD ?? ?? 99 ?? ?? BD ?? ?? 99
2C ?? ?? 30 ?? 70 ?? B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 98 38
AE ?? ?? AD ?? ?? 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 ?? 9D ?? ?? FE
99 04 D4 BD ?? ?? 99 02 D4 48 BD ?? ?? 99 03 D4 48 BD ?? ?? 99 05 D4
2C ?? ?? 70 ?? FE ?? ?? AD ?? ?? 10 ?? C8 B1 ?? 10 ?? 9D ?? ?? 4C
0A 0A 0A AA BD ?? ?? 8D ?? ?? BD ?? ?? 2D ?? ?? 99 04 D4
```

### Rob_Hubbard_Digi (digital sample playback variant)
```
4C ?? ?? 28 F0 && 4A 4A 4A 4A 4C ?? ?? 29 0F EE ?? ?? D0 03 EE && 8D 18 D4 AD 0D DD
```

## Other Composers Who Used The Hubbard Driver

The driver was sufficiently influential that multiple other composers adopted it:
- **Giulio Zicchi** — used Hubbard's driver directly (sidid detects as variant)
- **Johannes Bjerregaard** — modified variant (sidid detects as variant)
- **John De Margheriti** — with Hubbard's assistance
- **Pablo Toledo**
- **Jeroen Kimmel** (Red/Judges) — converted Commando driver back to source,
  used it for his own productions. This prompted Hubbard to scramble his code
  throughout 1987 to prevent further unauthorized use.
- **Jeroen Tel**
- **Neil Baldwin**
- **Thomas Petersen**

## Known Editors Built on Hubbard's Driver

- **Rob Hubbard Editor** by Predator/Moz(IC)art (1989, CSDb #75124)
  - Targets the ACE II player variant
  - Many Moz(IC)art tunes from 1989 were composed with this tool
  - Available as .d64 disk images with documentation
- **Rob Hubbard Sound Editor V2.0** (CSDb #129184)
  - Contains Monty on the Run and Human Race in memory
  - Functionality appears limited/incomplete
- **SID Sequencer** (1988, by Vic H. Berry) — based on the driver
  - https://hvmec.altervista.org/blog/?p=1689
- **Aleatory Composer** (1989, by Vic H. Berry) — also based on the driver
  - https://hvmec.altervista.org/blog/?p=1695

## Cadaver's Analysis (covertbitops.com)

Lasse Oorni (Cadaver, author of GoatTracker and sidid) notes that Hubbard's
player exemplifies the "old method" of hard restart -- clearing the gate bit and
setting ADSR to zero frames before a note ends. This works well on both PAL and
NTSC machines and isn't timing-sensitive.

Hubbard's vibrato implementation compensates for how vibrato/slides appear slower
in higher octaves by computing the frequency difference between the current note
and its neighbor (one halfstep lower), using this as the basis for vibrato and
slide speed. This produces logarithmic-feeling vibrato rather than linear.

## Other Platform Drivers (from VGMPF)

- **Atari ST**: Hubbard modified David Whittaker's driver for the YM2149F chip.
- **NES**: Pure 6502 assembly with custom implementation of triangle wave instrumentation
  via DPCM channel. No existing driver was adapted.
- **SNES**: Custom version of Nintendo's Kankichi-kun sound driver.
- **Amiga/PC/Mega Drive**: Platform expansions during EA period (1988+).

## Additional References

- Cadaver's music rants: https://cadaver.github.io/rants/music.html
- SID Media Lab analysis: https://akaobi.wordpress.com/2013/09/03/introducing-rob-hubbard/
- GAME journal article: https://www.gamejournal.it/driving-the-sid-chip-assembly-language-composition-and-sound-design-for-the-c64/
- ChiptuneSAK (handles Hubbard SIDs): https://github.com/c64cryptoboy/ChiptuneSAK
- realdmx ACME sources: https://github.com/realdmx/c64_6581_sid_players/tree/main/Hubbard_Rob
