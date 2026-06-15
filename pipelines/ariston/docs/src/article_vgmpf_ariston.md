---
source_url: https://www.vgmpf.com/Wiki/index.php?title=Ariston
fetched_via: direct
fetch_date: 2026-06-15
author: VGMPF community
content_date: unknown (wiki, retrieved 2026-06-15)
reliability: secondary
---

# VGMPF — Ariston driver page

## Core Facts

- Platform: Commodore 64 (primary); ported to Atari ST and Amiga in 1988
- Language: 6502 Assembly
- Release: 1987
- Region: United Kingdom
- CSDb entry: #29914 (cracked/imported disk image, 24 June 1988)

## Creator & Development History

- **Ian Crabtree** created the driver in 1987.
- **Wally Beben** helped write the driver (co-author).
- **Charles Deenen** (Maniacs of Noise): In late 1987, Maniacs of Noise asked
  Beben how he produced the "phasing" effect. Beben sent them the source code;
  they added better drums and returned it. This means the drum-enhanced variant
  post-dates the original circa late 1987.
- **Philip Brabbin** programmed the official GUI editor. Most composers bypassed
  it and composed directly in 6502 assembler.
- **ST/Amiga port (1988)**: Beben ported the driver with assistance from a
  programmer named "Chris" (surname unknown).

## Frequency Tuning Variants

Multiple modified versions exist, tuned at **424 Hz** or **434 Hz**. The
difference maps to different frequency table constants in the player code.

From VGMPF Ian_Crabtree page: Ian Crabtree's own tunes are tuned at
**433.5 Hz on PAL, 450 Hz on NTSC** — which is closer to 434 Hz than 424 Hz.

Note: Barry Leitch's drivers are documented at **424 Hz** (briefly 434 Hz
in 1988), so the 424 Hz variant is likely the original/base frequency table
and 434 Hz is a later revision.

## Composers Known to Use Ariston

Eight composers plus demo-scene users:

**Commercial game composers:**
1. Allister Brimble — first driver before Michael Delaney wrote him a custom one
2. Barry Leitch — used on Marauder (C64, ~June 1988); how he obtained it is unknown
3. Ian Crabtree — driver creator; composed in assembler
4. Jonathan Dunn — first two games (Subterranea, Matchday II); later switched to Galway's driver
5. Matt Gray — initial use with Soundmonitor; Codemasters convinced him to write his own
6. Paul Meredith
7. Steve Barrett — multiple Codemasters titles
8. Wally Beben — co-author; most prolific user

**Demo-scene / other:**
- Neil Baldwin ("Demon") — mentioned in Recollection as an Ariston scener user
  (also used Electrosound)
- Denis Harris ("Mole/Moley") / Ariston Design — UK group using the player
- Neil Scales / Ariston Design / N.W.C.U.G. — UK group
- Perdita (Sandra Park) — UK
- Mark Wilson — UK
- Kendal — UK
- Deadman — (Colossus Chess Atari ST)
- Denis Harris — A Short One, Final Red
- Lyndon Sharp — Fruit Machine Simulator 2, Skyhigh Stuntman, Wizard Willy

"Ariston Design" is a named C64 music group (Denis Harris + Neil Scales at least),
separate from the commercial driver. The group name appears to derive from the driver.

## Composition Method

"Almost all composers arranged in a 6502 assembler" — this means the driver's
data format was hand-written assembly, not a GUI-generated binary format
(unlike GoatTracker, Future Composer etc.). This implies the "format" is
essentially a convention agreed-upon by assembler-coded data tables.

## Amiga Workflow (Wally Beben's account)

"I wrote it initially using soundtracker for which I had a little program
I'd written to convert the data into blocks that I could use within my own
player that I'd migrated/converted from my C64 player."

Implication: the Amiga format is a converted/packed form of the C64 data
format, not a completely independent design. The C64 data layout is likely
tables of notes/instruments, and the Amiga version reorganises these into
"blocks" compatible with his Amiga player (which reused the C64 player logic
ported to 68000).

## ST Source Code Status

Wally Beben lost all of his ST and Amiga music driver source code due to
hard drive crashes. The Atari ST player was reverse-engineered by "Mug UK"
in 2004 (see atari-forum.com thread t=21588) — original RE is in attached
files, not available in the public thread text. The "R-Type" ST player
(Wally Beben) is the primary known reverse-engineered example.

## Sources Used

- https://www.vgmpf.com/Wiki/index.php?title=Ariston
- https://www.vgmpf.com/Wiki/index.php?title=Ian_Crabtree
- https://www.vgmpf.com/Wiki/index.php/Wally%20Beben
- https://www.vgmpf.com/Wiki/index.php/Barry%20Leitch
- https://www.vgmpf.com/Wiki/index.php/Jonathan_Dunn
- https://www.vgmpf.com/Wiki/index.php/Allister%20Brimble
- https://www.vgmpf.com/Wiki/index.php/Matt_Gray
- https://www.vgmpf.com/Wiki/index.php?title=Tetris_(C64)
