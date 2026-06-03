---
source_url: "multiple"
  - https://www.lemon64.com/forum/viewtopic.php?t=88030
  - https://www.lemon64.com/forum/viewtopic.php?t=35717
  - https://www.lemon64.com/forum/viewtopic.php?t=24542
  - https://www.lemon64.com/forum/viewtopic.php?t=7920
  - https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)
fetched_via: "direct"
fetch_date: 2026-04-11
author: "various forum contributors (groepaz, Tigro, 4mat, Lasse, nata, johncl, Luxocrates, smf, tfg)"
content_date: "2007-2017"
reliability: "secondary"
---
# Additional Lemon64 Thread Findings

## Commando Arcade Porting Thread

Source: https://www.lemon64.com/forum/viewtopic.php?t=88030

Luxocrates is porting Hubbard's Commando tune to the original arcade cabinet
hardware (hybrid sound chips: 3 AY voices + 3 FM voices).

smf mentioned having "ported a version of rob's player to C and ran that on
an arcade PCB and translated the SID registers to the sound hardware available."
No implementation details were shared.

Key observation: "early tunes work great with straight 1:1 translators" for
arcade hardware, but later tunes with complex pulse modulation and SID-specific
effects require creative reinterpretation.

## Deconstructing SID Files Thread

Source: https://www.lemon64.com/forum/viewtopic.php?t=35717

groepaz (Nov 3, 2010): "one or two [player routines] are available as (more or
less) commented disassemblies, for example some rob hubbard driver."

Tigro (Nov 5, 2010): recommended the SIDin magazine/fanzine containing "nice
disassemblies of the player routines."

4mat (Mar 25, 2015) cautioned that "the order sid registers are triggered (and
how many cycles apart) can be different in various players" -- important for
accurate emulation/comparison.

Lasse (Mar 25, 2015) documented siddump output format per channel:
- Frequency (16-bit)
- Note (interpreted from frequency, C-0 to H-7)
- Waveform (8-bit)
- ADSR (16-bit)
- Pulse width (12-bit)
- Plus global: filter cutoff (11-bit), resonance + filter mask, passband, volume

## Trackers Thread

Source: https://www.lemon64.com/forum/viewtopic.php?t=24542

nata (Sep 17, 2007) identified Hubbard's pre-programmed effects: "drums,
skydive and octave arpeggio." Noted these cannot be replicated in GoatTracker.

johncl (Sep 17, 2007) referenced the C=Hacking article as the source he used
to understand the player, describing the code as "very well explained in that
article."

johncl's integration strategy: "I'd easily be able to program the sound effects
as pattern data and trigger effect playback by forcing that pattern into the
playback by setting current track and resetting position."

## WAR Hidden SID Thread

Source: https://www.lemon64.com/forum/viewtopic.php?t=7920

No driver technical details. The hidden tune in WAR is accessed by entering
"GO 159256" at the high-score name prompt (referring to Stoat&Tim's Compunet
page). The hidden track is a Crazy Comets remix.

## VGMPF Wiki Entry

Source: https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)

Provides version timeline showing the driver evolved from late 1984 through
1987, with features added progressively (see chacking_hubbard_driver_disassembly.md
for full timeline).

## Key External References Identified

1. **C=Hacking #5** (March 1993) - Anthony McSweeney's full disassembly article
   - Available at: https://www.1xn.org/text/C64/rob_hubbards_music.txt
   - Also at: http://www.ffd2.com/fridge/chacking/ (C=Hacking archive)
   - Based on "Monty on the Run" driver

2. **CSDB Release #75124** - Ace 2 player editor
   - https://csdb.dk/release/?id=75124

3. **SIDin magazine** - Contains player routine disassemblies

4. **ChipMusic.org thread** (blocked, could not fetch):
   - https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/
   - Two pages of discussion about the driver
