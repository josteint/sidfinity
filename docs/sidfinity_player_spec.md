# SIDfinity Player Specification

## Design Principles

1. **Reproduce any SID tune** — the player's table/instrument system must be flexible enough to generate the same register writes as any of the 642 known player engines
2. **Play on real C64** — valid PSID v2, runs within CPU budget (~20k cycles/frame)
3. **Compact** — player code ~1.5-2KB, data fits typical songs in <32KB
4. **ML-friendly** — data format should tokenize naturally for transformer training

## Architecture Overview

Three-level song structure (matching the universal pattern across all analyzed players):

```
Song
 ├── Orderlist (per voice) — which patterns to play, with transpose
 ├── Patterns (shared pool) — sequences of note events
 └── Instruments — define timbre via programmable tables
      ├── Wave Table — waveform + pitch per tick
      ├── Pulse Table — pulse width modulation
      └── Filter Table — cutoff/resonance/mode
```

## Data Structures

### Song Header (16 bytes)

| Offset | Size | Field |
|--------|------|-------|
| 0 | 1 | Number of subtunes (1-32) |
| 1 | 1 | Default speed (ticks per row, 1-63) |
| 2 | 1 | Number of instruments (1-63) |
| 3 | 1 | Number of patterns (1-255) |
| 4 | 1 | Wave table size (rows) |
| 5 | 1 | Pulse table size (rows) |
| 6 | 1 | Filter table size (rows) |
| 7 | 1 | Speed table size (rows) |
| 8 | 1 | SID model (0=unknown, 1=6581, 2=8580, 3=both) |
| 9 | 1 | Clock (0=unknown, 1=PAL, 2=NTSC) |
| 10 | 1 | Speed multiplier (1=normal, 2-8=multispeed) |
| 11 | 1 | Flags (bit 0: use filter, bit 1: use pulse mod) |
| 12-15 | 4 | Reserved |

### Instruments (12 bytes each)

Based on analysis of all 642 players, every instrument engine boils down to:

| Offset | Size | Field | Description |
|--------|------|-------|-------------|
| 0 | 1 | AD | Attack/Decay (SID format) |
| 1 | 1 | SR | Sustain/Release (SID format) |
| 2 | 1 | Wave table ptr | Start index in wave table (0=none) |
| 3 | 1 | Pulse table ptr | Start index in pulse table (0=none) |
| 4 | 1 | Filter table ptr | Start index in filter table (0=none) |
| 5 | 1 | Vibrato speed | Speed table index (0=none) |
| 6 | 1 | Vibrato delay | Frames before vibrato starts |
| 7 | 1 | HR method | Hard restart config (see below) |
| 8 | 1 | HR AD | ADSR Attack/Decay during hard restart |
| 9 | 1 | HR SR | ADSR Sustain/Release during hard restart |
| 10 | 1 | HR waveform | Waveform written during HR ($09=test+gate, $08=test, $FE=gate off) |
| 11 | 1 | First wave | Waveform for first frame ($00=use wave table) |

#### HR Method byte (offset 7)

| Value | Method | Description |
|-------|--------|-------------|
| $00 | None | Direct note change, no preparation (54.5% of tunes) |
| $01-$03 | Gate-off | Gate off N frames before note (31.8% of tunes) |
| $11-$13 | Test-bit | Write test bit N frames before note (11.8%) |
| $21-$23 | ADSR-only | Change ADSR N frames before note (2.0%) |
| $80 | Legato | No gate off/on between notes |

The number in the low nibble is the HR lead time in frames (1-3).

### Wave Table (2 bytes per row, max 255 rows)

Controls waveform and pitch per tick. This is the core of sound design.

| Byte 1 | Byte 2 | Meaning |
|--------|--------|---------|
| $01-$0F | — | Delay N ticks (no waveform change) |
| $10-$DF | relative note | Set waveform, relative pitch offset |
| $10-$DF | $80 | Set waveform, keep current pitch |
| $10-$DF | $81-$DF | Set waveform, absolute note |
| $E0-$EF | value | Command: set AD ($E0), set SR ($E1), set filter ptr ($E2), etc. |
| $FF | target | Jump to row (0=stop) |

Waveform values follow SID convention:
- $10=triangle, $20=saw, $40=pulse, $80=noise
- Add $01 for gate bit
- Combinations: $41=pulse+gate, $21=saw+gate, $11=tri+gate, etc.

### Pulse Table (2 bytes per row, max 255 rows)

| Byte 1 | Byte 2 | Meaning |
|--------|--------|---------|
| $01-$7F | speed | Modulate for N ticks at given speed (signed) |
| $80-$FE | low byte | Set pulse width (byte 1 high nib = bits 8-11) |
| $FF | target | Jump to row (0=stop) |

### Filter Table (3 bytes per row, max 255 rows)

| Byte 1 | Byte 2 | Byte 3 | Meaning |
|--------|--------|--------|---------|
| $00 | cutoff | — | Set cutoff directly |
| $01-$7F | speed | — | Modulate cutoff for N ticks |
| $80-$8F | res+route | mode | Set filter params (res=hi nib, route=lo nib, mode=$10/$20/$40) |
| $FF | target | — | Jump to row (0=stop) |

### Speed Table (2 bytes per row, max 64 rows)

Shared by vibrato, portamento, and funktempo:

| Usage | Byte 1 | Byte 2 |
|-------|--------|--------|
| Vibrato | Speed (direction change interval) | Depth (pitch change per tick) |
| Portamento | Frequency delta MSB | Frequency delta LSB |
| Funktempo | Tempo value 1 | Tempo value 2 (alternating) |

### Orderlists (per voice per subtune)

Sequential byte stream:

| Byte | Meaning |
|------|---------|
| $00-$FE | Pattern number |
| + next byte | Transpose value ($80=no transpose, $81=+1, $7F=-1, etc.) |
| $FF | End marker, followed by restart position byte |

### Patterns (variable length, max 128 rows)

Packed format (same principle as GoatTracker, proven compact):

| Byte range | Meaning |
|------------|---------|
| $00 | End of pattern |
| $01-$3F | Set instrument (1-63) |
| $40-$4F | Command (0-15) + note follows |
| $50-$5F | Command (0-15) + rest (no note) |
| $60-$BC | Note (C-0 through G#-7, 93 notes) |
| $BD | Rest |
| $BE | Key off (gate off) |
| $BF | Key on (gate on without new note) |
| $C0-$FF | Packed rests (2-64 consecutive rests) |

Instrument and command bytes are omitted when unchanged from previous row.

### Commands ($40-$4F with parameter byte)

| Cmd | Name | Param | Description |
|-----|------|-------|-------------|
| 0 | Do nothing | — | (instrument vibrato active) |
| 1 | Portamento up | speed table idx | |
| 2 | Portamento down | speed table idx | |
| 3 | Tone portamento | speed table idx | Slide to target note |
| 4 | Vibrato | speed table idx | Override instrument vibrato |
| 5 | Set AD | AD value | |
| 6 | Set SR | SR value | |
| 7 | Set waveform | waveform value | |
| 8 | Set wave ptr | table index | |
| 9 | Set pulse ptr | table index | |
| A | Set filter ptr | table index | |
| B | Set filter ctrl | res+route | |
| C | Set filter cutoff | cutoff value | |
| D | Set volume | $00-$0F | |
| E | Funktempo | speed table idx | |
| F | Set tempo | speed value | |

## Player Frame Execution (6502)

Called once per frame (50 Hz PAL, 60 Hz NTSC), or N times for multispeed:

```
1. Process filter table (global)
   - Step through filter program if active
   - Write $D415 (cutoff lo), $D416 (cutoff hi), $D417 (res+route), $D418 (mode+vol)

2. For each voice (X = 0, 7, 14):
   a. Decrement tempo counter
   b. If tempo counter == 0: advance sequencer
      - Read next byte(s) from pattern
      - If pattern ended: advance orderlist, load next pattern
      - If orderlist ended: loop to restart position
   c. If new note: execute hard restart sequence (method from instrument)
   d. Step wave table (set waveform, calculate frequency)
   e. Apply continuous effects (vibrato, portamento)
   f. Step pulse table (pulse width modulation)
   g. Write SID registers:
      - $D400+X: freq lo
      - $D401+X: freq hi
      - $D402+X: pulse lo
      - $D403+X: pulse hi
      - $D404+X: waveform (AND with gate mask)
      - $D405+X: AD
      - $D406+X: SR
```

## Memory Layout (C64)

```
$0800 - $08FF  Player code (init + play, ~256 bytes core)
$0900 - $0BFF  Player code continued (~768 bytes effects/tables)
$0C00 - $0C3F  Song header + speed table
$0C40 - $0FFF  Instruments + wave/pulse/filter tables
$1000 - $CFFF  Orderlists + pattern data (~48KB available)
```

With BASIC ROM banked out ($A000-$BFFF = +8KB) and Kernal banked out ($E000-$FFFF = +8KB), total available = ~63KB for music data.

## PSID Header

Standard PSID v2 (124 bytes):
- Init address: $0800
- Play address: $0803
- Load address: $0800 (or 0 with embedded load addr)
- Songs: from song header
- SID model flag: from song header
- Clock flag: from song header
- Speed: 0 for VBI timing, or CIA timer value for multispeed

## Estimated Sizes

| Component | Bytes |
|-----------|------:|
| Player code | ~1,500 |
| Song header | 16 |
| Instruments (32 typical) | 384 |
| Wave table (128 rows) | 256 |
| Pulse table (64 rows) | 128 |
| Filter table (32 rows) | 96 |
| Speed table (16 rows) | 32 |
| Orderlists (3 voices, 1 subtune) | ~100 |
| Pattern data (40 patterns avg) | ~2,000 |
| **Total for typical tune** | **~4,500** |

A 4.5KB SID file is comparable to original GoatTracker/DMC exports. Plenty of room for complex tunes within 64KB.

## Compatibility Target

The SIDfinity player aims to reproduce the register write behavior of:
- All 3 hard restart methods (covering 100% of analyzed note transitions)
- Single speed and multispeed (covering 100% of tunes)
- All waveform/ADSR/pulse/filter combinations used across 642 player engines
- Both 6581 and 8580 SID chip models (set via PSID header flag)

The only tunes NOT coverable are:
- Digi sample tunes (~2%) — need separate sample playback engine
- Self-modifying code tricks — a handful of tunes
- Cycle-exact scanline effects — ~0.1% of tunes
