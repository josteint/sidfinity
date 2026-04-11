---
source_url: https://www.1xn.org/text/C64/rob_hubbards_music.txt
fetched_via: direct
fetch_date: 2026-04-11
author: Anthony McSweeney (original disassembly); local structured extraction
content_date: 1993-03-07 (C=Hacking Issue 5, March 7, 1993)
reliability: primary
---
# C=Hacking #5: Rob Hubbard's Music Driver Disassembly

Source: C=Hacking Issue 5, March 1993
Author: Anthony McSweeney
Retrieved from: https://www.1xn.org/text/C64/rob_hubbards_music.txt
Based on: "Monty on the Run" driver (used in ~30 games)

This is the most detailed technical reference for the Hubbard driver format.

## Player Entry Points

- `music+0`: Initialize. Accumulator = song number.
- `music+3`: Play music. Call 50 times per second (PAL VBI).
- `music+6`: Stop music and silence SID chip.

## Status Flag (mstatus variable)

| Value | Meaning |
|-------|---------|
| $C0   | Music off, SID needs quieting |
| $80   | Music off, SID already quiet |
| $40   | Initialization phase |
| other | Music playing normally |

## Data Hierarchy

```
Module
  +-- Song 0, Song 1, ... Song N
        +-- Track 0 (voice 1), Track 1 (voice 2), Track 2 (voice 3)
              +-- Pattern number sequence [p0, p1, p2, ... $FF or $FE]
                    +-- Note data bytes
```

- `$FF` at end of track = loop back to beginning
- `$FE` at end of track = play once only, then stop

Track pointers: 6 bytes per song (3 tracks x 2 bytes = lo/hi for each track).
Pattern pointers: Separate low-byte and high-byte tables indexed by pattern number.

## Note Encoding (2-4 bytes per note)

### Byte 1: Length + Flags

```
Bits 0-4: Note duration (0-31), stored as duration value
Bit 5:    No-release flag (1 = don't release at end of note)
Bit 6:    Append flag (1 = tie to previous note, no new attack/decay)
Bit 7:    Extended flag (1 = next byte is instrument or portamento)
```

### Byte 2 (conditional, only if bit 7 of byte 1 is set)

- **Positive value (bit 7 clear)**: Instrument number
- **Negative value (bit 7 set)**: Portamento speed
  - Bit 0 of this byte: direction (0 = slide up, 1 = slide down)
  - Upper bits: slide speed

### Byte 3: Note Pitch

- Value 0-127+, where 12 semitones = 1 octave
- Used as index into frequency table
- Out-of-range values index past the freq table into player variables (FM trick)

### Byte 4: Pattern End Marker

- `$FF` marks end of pattern

### Example

`$84, $04, $24` = 4-unit duration note, instrument 4, pitch $24 (C-3)

## Instrument Data Structure (8 bytes per instrument)

| Offset | Purpose |
|--------|---------|
| 0      | Pulse width low byte |
| 1      | Pulse width high byte |
| 2      | Control register (waveform select: noise=$80, pulse=$40, saw=$20, tri=$10, + gate, sync, ring) |
| 3      | Attack/Decay ($D405/$D40C/$D413) |
| 4      | Sustain/Release ($D406/$D40D/$D414) |
| 5      | Vibrato depth |
| 6      | Pulse speed (pulse width modulation rate) |
| 7      | Effects flags byte |

### Effects Flags (byte 7, bit flags)

| Bit | Effect |
|-----|--------|
| 0   | Drum: noise waveform + fast frequency sweep downward + fast decay |
| 1   | Skydive: slow continuous frequency descent |
| 2   | Octave arpeggio: alternate between note and note+12 semitones each frame |
| 3-7 | Reserved/unused |

## Frequency Table

- Stores 16-bit SID frequency values
- Organized as two separate tables: low bytes and high bytes
- Indexed by note number (pitch value from note encoding)
- 12 entries per octave (chromatic scale)
- Supports notes up to and beyond C-6 (pitch 72 = $48)

### The Variable Placement Trick

Player variables are placed in memory immediately after the frequency table.
When a pitch index exceeds the table size, the lookup reads variable values
instead of frequency values. Since these variables change during playback
(e.g., pattern position counter), this produces frequency modulation effects
with zero additional code.

## Per-Frame Processing Pipeline

Called 50 times/second. For each of 3 channels:

### 1. Speed Control

Check speed counter against configurable speed parameter.
Speed=1 means 50 notes/sec at duration 1. Speed>1 slows playback.

### 2. Note Fetch (getnewnote)

When speed counter triggers a new note:
1. Load current pattern number from track sequence
2. If pattern = $FF: restart track from beginning
3. If pattern = $FE: stop music
4. Read note bytes from pattern at current offset
5. Decode length, flags, instrument/portamento, pitch
6. Set SID frequency from frequency table lookup
7. Set SID control register, ADSR from instrument data
8. Initialize pulse width from instrument data
9. Advance pattern position

### 3. Sound Processing (soundwork)

When no new note (or after note setup), apply ongoing effects:

1. **Release**: When note duration expires and no-release flag is clear,
   clear gate bit in control register (triggers ADSR release phase)

2. **Vibrato**: If instrument vibrato depth > 0, oscillate pitch up/down
   using a counter. Adds/subtracts from SID frequency register.

3. **Pulse Width Modulation**: If instrument pulse speed > 0, modulate
   pulse width register. Speed value from instrument byte 6.
   Note: the instrument structure itself is modified (pulse width bytes
   0-1 are updated in place).

4. **Portamento**: If portamento active, add/subtract speed from current
   frequency toward target frequency. 16-bit addition/subtraction.

5. **Drum Effect**: First frame uses noise waveform ($81) at high frequency.
   Subsequent frames use the instrument's control register value.
   Frequency sweeps downward rapidly. Fast decay envelope.

6. **Skydive Effect**: Subtract a value from frequency each frame,
   producing continuous downward pitch slide.

7. **Octave Arpeggio**: Toggle between current note frequency and
   frequency of note+12 (one octave up) on alternating frames.

## Memory Map (Per-Channel State)

Each channel maintains:
- Current note length / remaining duration
- Current pattern number
- Pattern byte offset (position within pattern)
- Current frequency (16-bit)
- Current instrument number
- Portamento speed and direction
- Vibrato counter and phase
- Effect state flags

Global state:
- Speed counter
- mstatus flag
- Current song number

## Version Evolution (from VGMPF wiki)

| Period | Feature Added |
|--------|---------------|
| Late 1984 | Initial driver (basic notes, pulse, vibrato) |
| During Thing on a Spring | Octave arpeggios |
| 1986 (inspired by We M.U.S.I.C.) | Drum arrangements via rapid noise/triangle cycling |
| 1986 | Simultaneous music+SFX support dropped |
| March 1987 | Table-based drum methods |
| July 1987 | Table-based PWM methods |
| 1987 | Unsigned 4-bit PCM playback with mid-stream looping |

### Sound Effects System (pre-1986)

- Up to 16 sound effects supported
- Each effect uses two SID voices
- During SFX playback, music voices 1-2 are suppressed
- Voice 3 continues playing music during SFX
- Early bug: voice 3 note skipped on first driver run (fixed early 1986)

### Drum Synthesis

Characteristic Hubbard drum sound:
1. First frame: square wave ($41) for attack transient (1 frame = 20ms)
2. Remaining frames: white noise ($81) with pitch decay ~15 Hz
3. Duration approximately 1/32nd of a note

Later versions (1986+) used rapid noise/triangle wave cycling for more
complex drum timbres.

## Key Technical Notes

- Speed parameter of 1 = 50 calls per note duration unit
- Portamento is 16-bit frequency addition/subtraction per frame
- Pulse width is modified in the instrument data itself (mutable state)
- Vibrato uses a counter that oscillates, not a sine lookup
- Arpeggio is limited to octave transposition only (no arbitrary intervals)
- Player runs at 50Hz via PAL raster interrupt
- Developed using Mikro Assembler
