---
source_url: "http://www.1xn.org/text/C64/rob_hubbards_music.txt"
fetched_via: "direct"
fetch_date: 2026-04-11
author: "Anthony McSweeney"
content_date: "1993-03-07"
reliability: "primary"
---
# Rob Hubbard Music Driver - Monty on the Run Disassembly

**Source:** http://www.1xn.org/text/C64/rob_hubbards_music.txt
**Original:** C=Hacking Issue #5, March 7, 1993
**Author:** Anthony McSweeney (documenter)
**Player location:** $8000-$9554 in Monty on the Run

## Games Using This Same Driver (with slight modifications)

Confuzion, Thing on a Spring, Monty on the Run, Action Biker, Crazy Comets,
Commando, Hunter Patrol, Chrimera, The Last V8, Battle of Britain, Human Race,
Zoids, Rasputin, Master of Magic, and others.

## Player Interface

Three entry points:
- `music+0` ($8000): Initialize - A register contains music number
- `music+3` ($8003): Play - call at 50Hz (every VBI)
- `music+6` ($8006): Stop - silence SID chip

## Data Hierarchy

```
Song (6 bytes: 3 lo + 3 hi track pointers)
  -> Track (sequence of pattern numbers, $FF=loop, $FE=play-once)
    -> Pattern (sequence of notes, $FF=end-of-pattern)
      -> Note (2-4 bytes, variable encoding)
```

## Note Encoding (2-4 bytes, variable length)

### Byte 1: Length + Flags
```
Bits 0-4: Duration (0-31 frames)
Bit 5:    No release required (gate stays high)
Bit 6:    Append to previous note (tie/legato)
Bit 7:    Instrument or portamento byte follows
```

### Byte 2 (optional, when bit 7 set): Instrument or Portamento
```
If positive (bit 7 clear): Instrument number
If negative (bit 7 set):   Portamento speed + direction bit
```

### Byte 3: Pitch
```
0-72+: Note value (C-1 to C-6+, index into frequency table)
```

### Byte 4: End marker
```
$FF = End of pattern
```

### Encoding Examples

```
$84, $04, $24  = length 4, instrument 4, pitch $24 (C-3)
$44, $24       = length 4 with append (tie), pitch $24
$04, $24       = length 4, no instrument change, pitch $24
$84, $80, $24  = length 4, portamento (speed $80), pitch $24
```

## Instrument Structure (8 bytes per instrument)

```
Offset 0: Pulse width low byte
Offset 1: Pulse width high byte
Offset 2: Control register (waveform: $11=tri+gate, $21=saw+gate, $41=pulse+gate, $81=noise+gate)
Offset 3: Attack/Decay
Offset 4: Sustain/Release
Offset 5: Vibrato depth
Offset 6: Pulse width speed
Offset 7: Effects byte (bit field):
  Bit 0: Drum (noise + fast frequency sweep down)
  Bit 1: Skydive (slow frequency descent)
  Bit 2: Octave arpeggio
```

## Key Player Variables

| Variable | Purpose |
|---|---|
| `mstatus` | Music state: $C0=off, $80=silent, $40=init, other=playing |
| `counter` | Frame counter (0-255) |
| `speed` / `resetspd` | Note fetch rate (tempo) |
| `lengthleft[3]` | Remaining duration per channel |
| `posoffset[3]` | Track position (which pattern in sequence) |
| `patoffset[3]` | Pattern position (which note in pattern) |
| `currtrklo[3]` / `currtrkhi[3]` | Current track pointer per voice |

## Playback Flow (per frame, per channel)

1. **Check length counter**: If > 0, decrement and go to SoundWork
2. **Fetch pattern data**: Read next byte from pattern
3. **Check for end-of-pattern** ($FF): Load next pattern from track
4. **Decode note byte**: Extract length, flags, optional instrument/portamento, pitch
5. **Set frequency**: Look up pitch in frequency table, write to SID
6. **Initialize instrument**: Copy 8-byte instrument params to SID + variables

### SoundWork (when no new note):
- Release envelope triggering (gate bit clear after duration)
- Vibrato (pitch oscillation using depth from instrument byte 5)
- Pulse-width modulation (sweeping using speed from instrument byte 6)
- Portamento (frequency sliding toward target)
- Effects: drums (noise sweep), skydive (slow freq descent), octave arpeggio

## Frequency Table

Standard SID frequency table, ~6+ octaves, stored as low/high byte pairs.
The table starts with known values that can be used for detection:
`$16 $01 $27 $01` (C#1 and D-1 low bytes from the SIDdecompiler pattern search).

## Effect Details

### Drums (effects byte bit 0)
- First frame: square wave at note frequency
- Rapid switch to noise waveform
- Frequency sweeps down quickly

### Skydive (effects byte bit 1)
- Slow continuous frequency descent
- Creates characteristic "falling" sound effect
- Named in C=Hacking Issue #5

### Octave Arpeggio (effects byte bit 2)
- Alternates between base note and one octave up
- Per-frame alternation creates "chord" effect

### Vibrato (instrument byte 5)
- Logarithmic vibrato - compensated across octaves
- Uses difference between note frequency and neighbor frequency
- Speed is relative to current pitch

### Pulse Width Modulation (instrument byte 6)
- Sweeps from ~50% to ~88% duty cycle
- Speed controlled by instrument parameter

## Hard Restart Technique

Hubbard's approach:
1. Clear gate bit several frames before note end
2. Zero ADSR registers
3. On new note: set Waveform, then Attack/Decay, then Sustain/Release
4. Works on both PAL and NTSC without timing sensitivity

## Driver Variants

Hubbard modified his driver frequently between games:
- **Early (1985):** Basic version (Thing on a Spring, Monty)
- **Mid (1986):** Added features like better drums
- **Late (1987):** Added table-based drums, table-based PWM, 4-bit PCM sample playback
- **Digi version:** Unsigned 4-bit PCM with loop-in-middle capability

Up to 16 simultaneous sound effects supported in later versions.
Each effect uses two voices, can play over music by muting voices 1-2.

## Notes for Decompiler Implementation

1. The same core format is shared across ~30+ games with minor variations
2. Song data is always 6 bytes (3 lo + 3 hi) per song entry
3. Tracks are pattern-number sequences terminated by $FF or $FE
4. Patterns are variable-length note sequences terminated by $FF
5. Instruments are always 8 bytes
6. The player code varies but the data format is consistent
7. Key detection: find the SID register write patterns (see SIDdecompiler patterns)
