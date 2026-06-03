---
source_url: multiple
# C=Hacking Issue 5: https://codebase64.org/doku.php?id=magazines:chacking5
# ACME disassemblies: https://github.com/realdmx/c64_6581_sid_players/tree/main/Hubbard_Rob
# desidulate: https://github.com/anarkiwi/desidulate
fetched_via: compiled from multiple sources
fetch_date: 2026-04-11
author: unknown (compiled from Anthony McSweeney and realdmx disassemblies)
content_date: 1993
reliability: secondary
---
# Rob Hubbard Player — Data Format Reference
Compiled from C=Hacking #5 (Anthony McSweeney) and the Commando/Monty on the Run disassemblies.

## Architecture Overview

```
Song Module
  ├── Song Table (6 bytes per song: 3x hi ptr + 3x lo ptr to tracks)
  ├── Tempo Table (1 byte per song)
  ├── Pattern Pointer Table (lo + hi arrays, indexed by pattern number)
  ├── Track 1: sequence of pattern numbers, terminated by $FF (loop) or $FE (stop)
  ├── Track 2: same
  ├── Track 3: same
  ├── Patterns: variable-length note data, each terminated by $FF
  ├── Instruments: 8 bytes each
  └── Frequency Table: 96 words (lo/hi interleaved), 8 octaves x 12 notes
```

## Entry Points

- `jmp initmusic` — Init: A = song number
- `jmp playmusic` — Play: call at 50Hz (PAL VBI)  
- `jmp musicoff`  — Stop: silence SID

## Song Table

6 bytes per song: `lo1, lo2, lo3, hi1, hi2, hi3` — pointers to 3 tracks.

## Track Format

Each track is a sequence of pattern numbers (indices into pattern pointer table).
- `$FF` = restart from beginning (loop)
- `$FE` = stop music

## Pattern Format

Variable-length note data. Each note is 1-3 bytes + optional $FF terminator:

### Byte 1: Duration + Flags
```
Bits 0-4: Note duration (0-31)
Bit 5:    No release (sustain until next note)
Bit 6:    Append/legato (no attack, tied to previous note)
Bit 7:    Instrument/portamento byte follows
```

### Byte 2 (optional, present when bit 7 set):
```
If positive (bit 7 clear): Instrument number
If negative (bit 7 set):   Portamento value
  Bits 1-6: Portamento speed
  Bit 0:    Direction (0 = up, 1 = down)
```

### Byte 3: Note pitch
```
0 = C-0, 12 = C-1, 24 = C-2, ..., 72+ = C-6+
Pitch indexes into frequency table (pitch * 2 for lo/hi word)
```

### Pattern Terminator
`$FF` after the last note's pitch byte signals end of pattern.

## Examples

```
$84, $04, $24       — Duration=4, Instrument=4, Pitch=C-3
$D6, $98, $25, $FF  — Duration=22, Legato, Portamento up speed=24, Pitch=C#-3, End of pattern
$03, $39             — Duration=3, Pitch=$39 (same instrument as before)
$07, $39             — Duration=7, Pitch=$39
$41, ...             — Duration=1, Legato (append to previous)
```

## Instrument Format (8 bytes each)

```
Byte 0: Pulse width low
Byte 1: Pulse width high
Byte 2: Control register (waveform select: $11=tri, $21=saw, $41=pulse, $81=noise)
Byte 3: Attack/Decay
Byte 4: Sustain/Release
Byte 5: Vibrato depth (0 = no vibrato)
Byte 6: Pulse speed/delay byte
         Bits 0-4: delay between pulse width changes
         Bits 5-7: pulse speed (rate of PWM change)
Byte 7: FX flags
         Bit 0: Drum (noise+freq fall, square on first frame then noise)
         Bit 1: Skydive (slow frequency down)
         Bit 2: Octave arpeggio (alternates note and note+12 each frame)
         Bit 3: Pulse width LO modulation (direct add instead of up/down sweep)
         Bits 4-7: Used in later driver versions for additional FX
```

## Vibrato Implementation

Vibrato oscillates the pitch using a triangular LFO derived from the frame counter:
```
oscillator = counter & 7
if oscillator >= 4: oscillator = oscillator ^ 7
// Gives pattern: 0,1,2,3,3,2,1,0,0,1,2,3,...
```

The vibrato amount is the frequency difference between the note and note+1, 
right-shifted by `vibrato_depth` times. This difference is added `oscillator` times 
to the base frequency.

Only applies when note duration >= 6 (Monty) or >= 8 (some versions).

## Pulse Width Modulation

Two modes controlled by FX byte bit 3:

### Mode 0 (sweep): When bit 3 = 0
- Pulse width sweeps up from $08xx to $0Exx, then back down
- Speed controlled by bits 5-7 of pulse speed byte
- Delay between changes controlled by bits 0-4 of pulse speed byte
- Current pulse width stored IN the instrument data (self-modifying)

### Mode 1 (modulate): When bit 3 = 1
- Pulse speed added directly to pulse width low byte each frame
- Creates faster warble effect

## Drum Implementation

When FX bit 0 is set:
- First frame: Noise waveform ($80) written to control register
- Subsequent frames: freq_hi decremented each frame (rapid pitch fall)
- If instrument control register is 0: always noise
- If instrument control register is non-zero: square wave + noise on first frame only

## Speed/Tempo

- `resetspd` byte: 0 = fastest (notes at full 50Hz rate), 1 = half speed, etc.
- Note duration is in "speed ticks", so actual frames = (duration + 1) * (resetspd + 1)
- Commando uses tempo 2, Monty on the Run uses tempo 1

## Frequency Table

Standard SID frequency values for 8 octaves (C-0 through B-7), 96 notes total.
Stored as interleaved lo/hi bytes: `lo0, hi0, lo1, hi1, ...`

Values match the standard PAL C64 SID frequency table:
```
C-0: $0116, C#-0: $0127, D-0: $0138, ...
C-1: $022D, ...
...
C-7: $8B40, ...
```

## Status/Control

`mstatus` byte controls driver state:
- `$C0` = music off, need to silence SID
- `$80` = music off, SID already silenced
- `$40` = initialization pending
- `$00` = music playing

## Variables (per-channel, 3 bytes each)

```
posoffset[3]   — Current position in track (pattern sequence index)
patoffset[3]   — Current offset within current pattern
lengthleft[3]  — Remaining duration of current note
savelnthcc[3]  — Saved first byte of current note (for flags)
voicectrl[3]   — Current control register value
notenum[3]     — Current note number (pitch index)
instrnr[3]     — Current instrument number
portaval[3]    — Portamento speed+direction (0 = none)
pulsedelay[3]  — Pulse width change countdown
pulsedir[3]    — Pulse width direction (0=up, 1=down)
savefreqhi[3]  — Current frequency high byte
savefreqlo[3]  — Current frequency low byte
```

## Known Bugs in Original Driver

**Voice 3 skip on first run:** VGMPF documents that "the first time the driver runs,
the note on voice 3 is skipped." This is a known bug in early Hubbard driver versions.
Our decompiler must reproduce this behavior for register-accurate playback.

## Characteristic Drum Technique (Action Biker onward)

A selected wave (usually square) plays for one frame (20ms), then white noise for a
1/32nd note, then the same wave falling by 15 Hz. This creates Hubbard's signature
"punchy" drum sound and is distinct from the simpler noise-only drum in the early driver.

## Sound Effects Architecture

- Up to 16 concurrent sound effects, each using two voices
- Effects play over music by muting music voices 1-2 while voice 3 plays effects
- Sound effect code was stripped from the Monty on the Run disassembly for clarity

## Differences in Later Drivers (1986-1987)

The early driver described above was used for ~30 songs. Later versions added:

1. **International Karate variant**: Pattern transposition to save memory
2. **ACE II variant**: Arpeggio tables (multiple arpeggio values, not just octave)
3. **1986 additions**: Filter control, noise/triangle drum cycling
4. **March 1987**: Table-based drum synthesis
5. **July 1987**: Table-based PWM
6. **Post-July 1987**: 4-bit PCM sample playback via $D418 volume register
   (first to loop in the middle of a sample, implemented in ~1.5 hours)

The exact byte-level format of the later driver table extensions is not publicly documented
in the same detail as the early driver. Reverse engineering from SID files is needed.

## Concrete Instrument Examples

### Commando Instruments (from realdmx ACME disassembly)

```
Instr  PWL  PWH  CTRL  AD   SR   VIB  PLS  FX   Description
  0    $C0  $0A  $41   $29  $5F  $02  $E0  $00  Lead (pulse, vib, fast PWM)
  1    $80  $01  $41   $06  $4B  $00  $00  $05  Arp drum (IDRUM|IARP)
  2    $52  $01  $41   $09  $9F  $00  $16  $08  Bass (pulse, IPWL)
  3    $00  $02  $81   $0A  $09  $00  $00  $05  Snare (noise, IDRUM|IARP)
```
FX flags: IDRUM=$01, ISKY=$02, IARP=$04, IPWL=$08

### Monty on the Run Instruments (from realdmx ACME disassembly)

```
Instr  PWL  PWH  CTRL  AD   SR   VIB  PLS  FX   Description
  0    $80  $09  $41   $48  $60  $03  $81  $00  Lead (pulse, vibrato=3)
 12    $00  $09  $41   $3F  $C0  $02  $00  $00  Skydive candidate
 13    $00  $08  $41   $90  $F0  $01  $E8  $02  Skydive (FX bit 1)
```

## Commando Variable Addresses (from realdmx disassembly)

```
$14A2  posoff[3]     Track position offset per voice
$14A5  patoff[3]     Pattern offset per voice
$14A8  notec[3]      Note counter
$14AB  notelen[3]    Note length
$14AE  ctrl[3]       Control register state
$14B1  note[3]       Current note value
$14B4  instr[3]      Current instrument index
$14B7  pbend[3]      Pitch bend value
$14BA  pdelay[3]     Pulse delay counter
$14BD  pdir[3]       Pulse direction
$14C0  nfqh[3]       Note frequency high
$14C3  nfql[3]       Note frequency low
$14C6  trackph[3]    Track pointer high
$14C9  trackpl[3]    Track pointer low
```

## Frequency Table Format Variants

Two known layouts:
1. **Interleaved** (Monty on the Run): `lo0, hi0, lo1, hi1, ...`
   - Pitch index multiplied by 2 to get offset
2. **Separate tables** (Commando): `freqsl[N]` + `freqsh[N]` as separate arrays
   - Commando also has secondary freq tables (freqsl_2/freqsh_2) for vibrato half-steps

Both start at C-0: $0116, C#-0: $0127, etc.

## Additional Tools and Resources

### desidulate (https://github.com/anarkiwi/desidulate)
SID register log analyzer — reads VICE emulator dumps, produces Pandas dataframes
of instrument definitions, filter/PWM curves. Not Hubbard-specific but useful for
validating decompiler output against actual SID register writes.

### ACME Disassemblies (https://github.com/realdmx/c64_6581_sid_players/tree/main/Hubbard_Rob)
Full ACME-format disassemblies of Commando and Monty on the Run with complete
labeling of all data structures, variables, and code routines. Primary reference
for exact addresses and data values.
