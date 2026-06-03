# Soundmonitor

## Overview

- **HVSC count:** ~3,663 tunes
- **Author:** Chris Huelsbeck
- **Year:** 1986, published in 64'er magazine issue 10/1986
- **Distribution:** 5-page hex dump (11 KB) that users typed in manually
- **CSDb:** #59929
- **Key ref:** https://namelessalgorithm.com/computer_music/blog/soundmonitor/

## Architecture

- **Editor:** loaded at $1000, occupies to ~$2FFF
- **MusicMaster replayer:** standalone playback routine for games/demos

## Memory Layout

| Range | Purpose |
|-------|---------|
| $1000 | Editor code |
| $3000-$9FFF | Note/bar data region 1 |
| $B000-$BDFF | Note/bar data region 2 |
| $BE00+ | Bar data addresses |
| $C000 | MusicMaster replayer init |
| $C020 | MusicMaster replayer play |

Songs typically >10 KB. Standard signature: init=$C000, play=$C020.

## Data Structures

### Track/Step Table (master sequencing)

Format per row: `SP TRKx TR ST 00`
- **SP:** Step parameters (tempo, length, volume, fade-out speed)
- **TRKx:** 16-bit address pointing to a bar in memory
- **TR:** Transpose (two's complement)
- **ST:** Sound/instrument index offset

### Bar/Pattern Format

Notes laid out in grid of 32nd-note subdivisions. Leftmost column = even 8th notes, each followed by 3 successive 32nd notes.

### Note Format

- Note value (e.g., C-2, G#3)
- Instrument index (hex digit)
- Sound options nybble (4 bits):
  - Bit 0: Portamento enable
  - Bit 1: Transpose disable
  - Bit 2: Arpeggio enable
  - Bit 3: Sound transpose enable

### Sound Patches — 24 parameters each

- Waveform selection
- ADSR envelope
- Vibrato (speed, depth, delay)
- Portamento (speed)
- Pulse width and modulation
- Filter cutoff, resonance, envelope

### Arpeggio

Configured per-bar in "AR/S DATA" view. Rapid pitch changes to simulate chords.

## MusicMaster Replayer

Features: transpose, detune, portamento, vibrato, PWM, filter modulation, arpeggios. Playback via `SYS 49152` ($C000). Not relocatable. High CPU usage.

## Limitations

- Large file sizes (>10 KB)
- Not relocatable
- No sample playback
- Slow compared to hand-optimized drivers

## Related Tools

- **Rockmonitor:** Modified/hacked version of Soundmonitor
- **JC64dis:** Can identify and disassemble Soundmonitor players
- **JITT64:** Can import from PSID files
