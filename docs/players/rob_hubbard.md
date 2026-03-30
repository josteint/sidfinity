# Rob Hubbard Player

## Overview

- **HVSC count:** 289 tunes
- **Author:** Rob Hubbard (1984-1987)
- **Player size:** ~900-1000 bytes of code
- **Notable games:** Commando, Monty on the Run, Delta, Crazy Comets, Lightforce, Sanxion, International Karate
- **Key reference:** C=Hacking Issue #5 by Anthony McSweeney (full commented disassembly)
  - https://www.1xn.org/text/C64/rob_hubbards_music.txt

## Entry Points

Three entry points at fixed offsets from base address:

| Offset | Function | Usage |
|--------|----------|-------|
| +0 | Init | Load A with song number, JSR |
| +3 | Play | Call once per frame (50 Hz PAL) |
| +6 | Stop | Silence all channels |

## Data Organization (4-level hierarchy)

1. **Module** - contains songs + shared instrument definitions
2. **Song** - 6 bytes: 3 low + 3 high pointers to channel tracks
3. **Track** - sequence of pattern numbers, terminated by $FF (loop) or $FE (stop)
4. **Pattern** - sequence of notes, terminated by $FF

## Note Format (variable-length, 2-4 bytes)

### Byte 1 - Length + Flags (always present)
- Bits 0-4: Note duration (0-31 frames)
- Bit 5: No-release flag (gate not cleared at note end)
- Bit 6: Tie flag (note tied to previous, no re-trigger)
- Bit 7: New instrument/portamento flag (if set, byte 2 follows)

### Byte 2 - Instrument/Portamento (conditional, only if byte 1 bit 7 set)
- Positive (bit 7 clear): New instrument number
- Negative (bit 7 set): Portamento command
  - Bits 1-6: speed
  - Bit 0: direction (0=up, 1=down)

### Byte 3 - Pitch (always present for non-rest notes)
- 0-127: pitch index (0=lowest C, increments of 12 per octave)
- Out-of-range values index into player variables (frequency table trick)

## Instrument Format (8 bytes)

| Offset | Field | Description |
|--------|-------|-------------|
| 0 | PW low | Initial pulse width low byte |
| 1 | PW high | Initial pulse width high byte |
| 2 | Control | Waveform + gate/sync/ring/test |
| 3 | AD | Attack/Decay |
| 4 | SR | Sustain/Release |
| 5 | Vibrato depth | Frequency modulation depth |
| 6 | PW mod speed | Pulse width oscillation rate |
| 7 | Effects flags | Bit field (see below) |

### Effects flags (byte 7)
- Bit 0: **Drum** - rapid freq slide down, fast decay. Noise=$80 for pure noise drum, square wave does square->noise->wave fall
- Bit 1: **Skydive** - decrements freq hi byte every other frame (descending pitch dive)
- Bit 2: **Octave arpeggio** - alternates base note and base+12 each frame

## Memory Layout (Monty on the Run variant)

- **$8000-$9554**: Full player + data
- **Zero page $02-$05**: Indirect addressing pointers
- **Per-voice state**: ~40 bytes per voice (note duration, instrument, portamento, vibrato phase, pulse width state, effect flags)

## Player Loop Architecture

Called at 50 Hz, processes all 3 channels sequentially. Two phases per channel:

### Phase 1 - NoteWork (note fetching)
1. Decrement speed counter; skip to SoundWork if not zero
2. Check remaining note duration
3. If expired, fetch next note from pattern
4. If pattern exhausted ($FF), advance to next pattern in track
5. If track exhausted ($FF=loop, $FE=stop), handle accordingly
6. Parse variable-length note bytes, set up instrument if new
7. Reset speed counter

### Phase 2 - SoundWork (per-frame effects)
1. **Release handling**: When duration reaches threshold (counter=2), clear gate, set ADSR=$00 for hard restart prep
2. **Vibrato**: Add/subtract frequency delta based on oscillating counter. Delta computed logarithmically (difference between current note freq and next-lower semitone)
3. **Pulse width modulation**: Oscillate between ~$0800 (50%) and ~$0E00 (88%) at instrument-defined speed
4. **Portamento**: Add/subtract portamento speed from current frequency each frame
5. **Effects**: Drums, skydive, arpeggio per instrument flags

### Hard restart sequence
Register write order: Waveform, then AD, then SR (ensures sharpest attack).

## The Frequency Table Trick

Player variables stored immediately after frequency lookup table. Out-of-range pitch values index into these variables instead of actual frequencies. The "looked up" values produce pseudo-random frequency modulation with zero CPU overhead. Used for the iconic Commando opening staccato effect.

## Driver Evolution

| Period | Feature Added |
|--------|--------------|
| Late 1984 | Core routine: logarithmic vibrato, PWM sweep |
| Early 1985 | Simmons-style drum synthesis |
| Mid 1985 | Octave arpeggios, sound effects (up to 16) |
| Mid 1985 | Portamento / skydive effect |
| Late 1985 | Frequency table trick (Commando) |
| Mid 1986 | Pattern transposition, SID filter support |
| Late 1986 | Arpeggio tables (data-driven) |
| March 1987 | Table-driven drums |
| July 1987 | Table-driven PWM |
| Late 1987 | Unsigned 4-bit PCM sample playback |
| 1987+ | Code scrambling/obfuscation to prevent unauthorized reuse |

## Other Composers Using This Player

Jeroen Kimmel, Jeroen Tel, Neil Baldwin, Thomas Petersen, and many others adopted Hubbard's driver (sometimes without permission, leading to the code scrambling).

## Composition Workflow

Hubbard composed by writing music notation on paper, annotating with hex values, then typing hex directly into Mikro Assembler. No tracker or GUI — all hand-authored assembly data.
