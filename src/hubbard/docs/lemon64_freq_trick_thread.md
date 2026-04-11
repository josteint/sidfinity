---
source_url: "https://www.lemon64.com/forum/viewtopic.php?t=64066"
fetched_via: "direct"
fetch_date: 2026-04-11
author: "various forum contributors (tfg, groepaz)"
content_date: "2017-04"
reliability: "secondary"
---
# Lemon64: Rob Hubbard Frequency Table Trick / Appreciation Thread

Source: https://www.lemon64.com/forum/viewtopic.php?t=64066
Date: April 2017

## Frequency Table Variable Placement (tfg, April 12, 2017)

Hubbard placed player variables directly after the frequency table in memory.
By using out-of-range pitch indices that point past the end of the frequency
table and into these variables, the player would load variable values as
frequency words. This created frequency modulation effects without any extra
calculation code -- the same note-fetch-and-set-frequency code path that
handles normal notes also produces FM when given these special pitch values.

### Commando Staccato Effect

tfg: "At the start of the Commando main theme Rob used the in-pattern-position
variables that way for the iconic 'galloping down the stairs'-staccato effect."

The in-pattern-position variable (the current byte offset within the pattern)
changes every frame as the player advances through note data. When this
variable's address is read as a frequency value (via an out-of-range pitch
index), the frequency tracks the pattern position, creating a descending
staircase pitch effect that sounds like a galloping rhythm.

## Note Encoding Format (tfg)

"It's duration based and all the notelengths have to entered as length-1 plus
various flags on top for pauses, instrument changes etc."

This means:
- Note length is stored as (actual_length - 1)
- Additional flag bits in the length byte control:
  - Pauses (rest notes)
  - Instrument changes (triggers loading new instrument data)
  - Other control features

Manual composition with this format is described as challenging without
dedicated editor tools.

## Update Mechanism (tfg, April 14, 2017)

"Normally just once per frame. Actually even slightly less often as it does
either read in a new note or process the effects for the previously read one,
but never does both at once on the same channel to keep the execution time low."

Key insight: the player alternates between two modes per channel per frame:
1. **Note fetch mode**: Read the next note from pattern data, set up registers
2. **Effect processing mode**: Apply vibrato, pulse modulation, portamento, etc.

Never both in the same frame on the same channel. This halves worst-case CPU
usage per frame, which was critical on the C64.

## Guitar Sampling

Hubbard's guitar sampling used the SID volume register bug ($D418) for 4-bit
PCM playback. This technique sounds correct on the original 6581 SID chip but
muffled on the 8580 revision.

## Historical Note

Hubbard composed directly in assembly -- he never used a music editor utility.
He would edit note data directly in the assembler source code. This was common
practice among early C64 composers.

Red/Judges (Jeroen Kimmel) later converted the driver back into editable
source form and used it for his own compositions. groepaz clarified this was
specifically the Crazy Comets driver, not the Commando driver.
