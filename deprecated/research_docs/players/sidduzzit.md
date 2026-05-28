# SID Duzz'It (SDI)

## Overview

- **HVSC count:** 994 tunes
- **Authors:** Geir Tjelta and Glenn Rune Gallefoss of SHAPE
- **Year:** 1992-2014 (V2.1.7)
- **Source:** https://sourceforge.net/projects/sidduzzit/ (player source in Turbo Assembler format)
- **Docs:** SDI.2.1.6-docs.txt (65KB), PDF manual by Psylicium at CSDb #153760

## Entry Points (assembled at $1000)

| Address | Function |
|---------|----------|
| $1000 | Init (X = subtune 0-$1F) |
| $1003 | Main play (reads tracks, sequences, sounds) |
| $1006 | Fadeout (A = $00-$7F) |
| $1009 | Speed play (sound update only, for multispeed) |

Player size ~$0900 bytes + data. Zero-page: $FE, $FF.

## Data Capacities

32 tunes, 128 sequences, 32 instruments (+16 via arpeggio = 48), 48 arpeggios, 85 vibrato programs, 64 filter programs, 64 pulse programs, 48 tempo programs.

## Memory Map (Editor Mode)

Key regions:
- $3000-$5000: Track data (4 tracks, 2KB each)
- $5000-$D000: Sequences (32KB for 128 sequences)
- $E000-$E100: Waveform program table
- $E100-$E200: Waveform note table
- $E200-$E300: Pulse program table
- $E300-$E500: Arpeggio data + program table
- $E500-$E600: Vibrato program table
- $E600-$E700: Filter program table
- $E700-$E8E0: Instrument setup (column-major: all WF ptrs, all AD, all SR, etc.)

## Instrument (10 bytes per instrument, column-major storage)

| Field | Description |
|-------|-------------|
| Waveform PRG | Pointer into waveform program table |
| AD | Attack/Decay |
| SR | Sustain/Release |
| Gate Timeout | Complex encoding: $00-$1F=normal HR, $21-$3F=HR2, etc. |
| Vibrato PRG | $00=none, $01-$55=program pointer |
| Pulse PRG | $00=none, $01-$40=program, $41-$80=infinite sweep, $8X=direct PW |
| Filter PRG | $00=none, $01-$40=program, $41-$80/$81-$C0/$C1-$FF=sweep modes |
| Band/Resonance | Hi nib=resonance, lo nib varies |
| Detune Hi/Lo | Fine pitch offset |

## Waveform Program Table (2 columns, $E000/$E100)

Column 1 (waveform): $10=tri, $20=saw, $40=pulse, $80=noise (+$01 for gate). Arpeggio waveforms: $91/$A1/$B1/$C1/$D1/$E1. Commands: $FF=jump, $FE=delay, $FD=ADSR, $FB=multipulse, $FA=repeat, $EE=pulse init, etc.

Column 2 (note): $00-$5E soft notes (relative), $60-$7F soft subtract, $80-$DE fixed notes.

## Pulse Program Table (4 bytes per entry)

c2: start value, c3: sweep target, c4: speed, c5: mode ($00-$3F=sweep then cut, $40-$7F=continuous, $80-$BF=reverse cut, $C0-$FF=reverse continuous).

## Filter Program Table (4 bytes per entry)

Same structure as pulse, reversed byte order for c2. "Filter frame" mode when c3=0.

## Vibrato Program Table (3 bytes per entry)

c2: $01-$FD=delay, $00=detune+continue, $FE=detune+hold, $FF=infinite loop. c3: width or detune lo. c4: speed or detune hi.

## Sequencer Format

FX + Note per row. FX: $00-$1F=instrument, $21-$3F=glide, $40-$6F=arpeggio, $70-$7F=ADSR control, $20=filter toggle.

## Track Structure

4 tracks (3 voices + 1 for tempo/transpose/filter). Each entry: transpose ($80-$BF), sequence number ($00-$7F), jump pointer.

## Assembly Flags

Optional features controlled by flags: `rem_pu`, `rem_arp`, `rem_fi`, `rem_vib`, `rem_glid` (set to 1 to exclude unused features).
