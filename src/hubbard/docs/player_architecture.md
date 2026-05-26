---
source_url: "multiple"
  - http://www.1xn.org/text/C64/rob_hubbards_music.txt
  - https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)
  - https://www.c64-wiki.com/wiki/Rob_Hubbard
  - https://www.lemon64.com/forum/viewtopic.php?t=64066
fetched_via: "compiled from multiple sources"
fetch_date: 2026-04-11
author: "local: compiled from McSweeney disassembly + forum research"
content_date: "2026-04-11"
reliability: "secondary"
---
# Rob Hubbard Player Engine — Technical Architecture

## Overview

Rob Hubbard wrote his C64 music driver in 6502 assembly using Mikro Assembler,
starting late 1984 / early 1985. The driver is approximately 900-1000 bytes of
code and controls all SID synthesis. He modified the driver frequently between
games, adding/removing features and optimizing for either space or speed.

The original source code was lost in spring 1997. All current knowledge comes
from disassemblies, primarily Anthony McSweeney's annotated disassembly of the
Monty on the Run driver (available at https://www.1xn.org/text/C64/rob_hubbards_music.txt).

## Data Hierarchy

```
Module
  +-- Song (selected by init accumulator value)
       +-- Track 0 (voice 1) -- sequence of pattern numbers
       +-- Track 1 (voice 2)
       +-- Track 2 (voice 3)
            +-- Pattern -- sequence of encoded notes
                 +-- Note (1-4 bytes)
```

Track termination bytes:
- `$FF` = loop back to beginning of track
- `$FE` = play once only, then stop

## Note Encoding (1-4 bytes)

### Byte 1: Length + Control Flags

| Bits  | Meaning                                           |
|-------|---------------------------------------------------|
| 0-4   | Note duration (0-31 frames at current speed)      |
| 5     | No-release flag (skip gate-off at end)            |
| 6     | Append flag (no new attack, tie to previous note) |
| 7     | New-instrument / portamento flag (byte 2 follows) |

### Byte 2: Instrument or Portamento (only if bit 7 of byte 1 set)

- Positive value (bit 7 clear): instrument number
- Negative value (bit 7 set): portamento speed
  - Bit 0 = 0: portamento UP
  - Bit 0 = 1: portamento DOWN
  - Bits 1-6: speed value

### Byte 3: Pitch

Value 0 = lowest C. Each increment = one semitone.
Value 12 = next octave C. Supports up to pitch 72+ ($48+).

### Byte 4: Pattern Terminator

`$FF` marks end of pattern. If not $FF, next note starts at byte 1.

### Examples

```
$84, $04, $24
  Byte 1: $84 = 1000_0100 -> length=4, bit7=1 (new instrument follows)
  Byte 2: $04 = instrument 4
  Byte 3: $24 = pitch 36 = C-3

$D6, $98, $25, $FF
  Byte 1: $D6 = 1101_0110 -> length=22, bit5=0, bit6=1 (append), bit7=1
  Byte 2: $98 = negative -> portamento, bit0=0 (up), speed=$18=24
  Byte 3: $25 = C#3
  Byte 4: $FF = end of pattern
```

## Instrument Definition (8 bytes per instrument)

| Offset | Register/Purpose           | Notes                          |
|--------|----------------------------|--------------------------------|
| 0      | Pulse width low            |                                |
| 1      | Pulse width high           |                                |
| 2      | Control register           | Waveform select + gate bits    |
| 3      | Attack/Decay               |                                |
| 4      | Sustain/Release            |                                |
| 5      | Vibrato depth              | 0 = no vibrato                 |
| 6      | Pulse speed                | PWM animation rate             |
| 7      | Effects byte               | Bit flags (see below)          |

### Effects Byte (instrument offset 7)

| Bit | Effect           | Description                                    |
|-----|------------------|------------------------------------------------|
| 0   | Drum             | Noise + rapid freq downslide                   |
| 1   | Skydive          | Slow frequency descent (every other frame)     |
| 2   | Octave arpeggio  | Alternates note and note+12 each frame         |

## Frequency Table

96 entries covering 8 octaves. Low bytes stored consecutively, then high bytes.
Standard C64 PAL frequency values.

## Driver Entry Points

| Offset | Function                                          |
|--------|---------------------------------------------------|
| +0     | Init: load song number in accumulator, JSR        |
| +3     | Play: call at 50Hz (PAL VBI), processes one frame |
| +6     | Stop: silence SID, reset driver state             |

Note: Actual offsets vary between songs. Some songs use +0/+$12 (Commando,
Monty, Warhawk, Thing on a Spring), others use different spacing.

## Per-Frame Processing (called at 50Hz)

The play routine executes a loop 3 times, once per SID voice:

### 1. Speed Check
- Decrement speed counter
- If not zero, skip to SoundWork (effects-only frame)
- If zero, reset counter and proceed to NoteWork

### 2. NoteWork (note fetch)
- Check if current note duration has expired
- If expired, fetch next note from current pattern
- Decode the 1-4 byte note encoding
- If new instrument: load 8-byte instrument definition into workspace
- Write initial SID registers: pulse width, control, AD, SR
- If pattern ended ($FF): advance track pointer to next pattern number
- If track ended ($FF/$FE): loop or stop

**KEY DESIGN CONSTRAINT:** The player either reads a new note OR processes effects
on a given channel, never both in the same frame. This keeps execution time low and
predictable. (Source: tfg on Lemon64, confirmed by disassembly.)

### 3. SoundWork (effects and modulation)
Applied every frame regardless of whether a new note was fetched:
- **Gate release**: if note duration expired and no-release flag not set, clear gate bit
- **Vibrato**: 3-bit counter oscillates (0,1,2,3,3,2,1,0), modulates frequency
  based on depth parameter (frequency difference to next semitone / 2^depth)
- **Pulse width modulation**: animate pulse width register at configured speed
- **Portamento**: slide frequency toward target pitch at configured speed
- **Drum effect**: first frame noise waveform, then pitched square with rapid
  frequency decay
- **Skydive**: decrement freq_hi every other frame
- **Arpeggio**: alternate between base pitch and base+12 (octave) each frame
- **Frequency write**: final freq_lo/freq_hi written to SID

## Key Variables (zero page / workspace)

| Variable     | Purpose                                             |
|--------------|-----------------------------------------------------|
| mstatus      | $C0=off, $80=off-no-kill, $40=init, else=playing    |
| counter      | Global frame counter                                |
| speed/resetspd | Note fetch divider (tempo control)                |
| currtrkhi/lo | Track pointers (3 channels)                         |
| posoffset    | Current position in track (per channel)             |
| patoffset    | Current position in pattern (per channel)           |
| lengthleft   | Remaining note frames (per channel)                 |

## Raster Time

Hubbard's routines were known for very low raster time consumption, leaving
maximum CPU for game code. The driver was frequently optimized for speed.

## Version Differences Across Games

The driver was NOT a static codebase. Hubbard modified it per-game:

- **Thing on a Spring** (early 1985): First driver. Added octave arpeggios.
  Known bug: first frame voice 3 note skipped.
- **Action Biker** (1985): Characteristic drum synthesis added (square frame +
  noise + frequency slide).
- **Monty on the Run** (1985): Pitch bend code added. Canonical reference version.
- **Commando** (1985): 19 subtunes. Tight optimization.
- **International Karate** (1986): Pattern transposition added to save memory.
- **Crazy Comets** (1986): 17 subtunes with Simon Nicol samples.
- **Delta** (1987): Custom code extensions for minimalist composition technique.
  Required special debugging. Loader allowed instrument selection.
- **Mega Apocalypse** (1987): First game with 3-channel music AND samples
  simultaneously during gameplay.
- **BMX Kidz** (1987): 4-bit PCM sample playback (digi variant). First to
  loop samples in the middle. Added in 1.5 hours of development.
- **Skate or Die** (1987): First EA title. Verified correct speed (many cracks
  played at wrong speed).
- **Kings of the Beach** (1988): James Brown voice samples.
- **Last V8**: Had a 7-byte bug causing music to fall out of sync at ~1 minute.
  Corrected in HVSC version.

## Sample Playback (Digi variant)

Later versions exploited the SID volume register ($D418) trick: writing 4-bit
values rapidly produces crude PCM output. Hubbard's final driver iteration
could handle 2 samples + SID music simultaneously (never shipped in a game).

The digi playback runs from a separate CIA timer IRQ, independent of the
main 50Hz VBI music driver.

## Songs Using Non-Hubbard Engines

Some songs in the Hubbard_Rob/ HVSC directory use different engines:
- **RobTracker** (Jason Page): Modern recreations — Go_Go_Dash, Lion_Heart,
  Lakers_vs_Celtics, Pacific_Coast, Radio_ACE, Sun_Never_Shines
- **SidTracker64**: Casio_Extended, Dont_Step_on_My_Wire, Era_of_Eidolon,
  Robs_Life, Task_Force
- **Companion**: Commodore_64_Music_Examples, Up_up_and_Away

## Known SID Addresses

| Song                   | Load   | Init   | Play   | Songs |
|------------------------|--------|--------|--------|-------|
| Commando               | $5000  | $5FB2  | $5012  | 19    |
| Monty on the Run       | $8000  | $8000  | $8012  | 19    |
| Delta                  | $BC00  | $C357  | $BDE4  | 13    |
| Sanxion                | $B000  | $BE00  | $BE20  | 2     |
| International Karate   | $AE00  | $AE00  | $AE0C  | 1     |
| Crazy Comets           | $5000  | $6100  | $500C  | 17    |
| Lightforce             | $F000  | $F0B9  | $F0BF  | 1     |
| Warhawk                | $1000  | $1F53  | $1012  | 18    |
| Thing on a Spring      | $C000  | $CECB  | $C012  | 17    |

## References

- Anthony McSweeney's disassembly: https://www.1xn.org/text/C64/rob_hubbards_music.txt
- VGMPF Wiki: https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)
- C64-Wiki: https://www.c64-wiki.com/wiki/Rob_Hubbard
- STIL.txt in HVSC: data/C64Music/DOCUMENTS/STIL.txt
