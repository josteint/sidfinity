# GoatTracker V1/V2

## Overview

- **HVSC count:** V2: 7,550 tunes, V1: 1,384 tunes (total 8,934)
- **Author:** Lasse Oorni (Cadaver) of Covert Bitops
- **Source:** https://github.com/leafo/goattracker2 (V2 mirror), https://sourceforge.net/projects/goattracker2/
- **Player license:** Free for any purpose including commercial (non-GPL)
- **Key refs:** GoatTracker guide, ChiptuneSAK docs, cadaver's miniplayer repos

## Entry Points (exported SID)

| Offset | Function |
|--------|----------|
| base+0 | JMP init (A = subtune number, 0-based) |
| base+3 | JMP play (call once per frame) |
| base+6 | JMP playsfx (optional) |
| base+9 | JMP setmastervol (optional) |

## Song File Format (.SNG) - "GTS5"

### Header (101 bytes)

| Offset | Size | Description |
|--------|------|-------------|
| +0 | 4 | ID: `GTS5` (V2.59+), older: `GTS3`, `GTS4` |
| +4 | 32 | Song name |
| +36 | 32 | Author name |
| +68 | 32 | Copyright |
| +100 | 1 | Number of subtunes |

### Orderlists (per channel per subtune)

Each orderlist: 1 byte length (n), then n+1 bytes (data + restart position).

- `$00-$CF`: Pattern numbers (max 208)
- `$D0-$DF`: Repeat 1-16 times
- `$E0-$EF`: Transpose down 0-15 halftones
- `$F0-$FE`: Transpose up 0-14 halftones ($F0=none)
- `$FF`: End mark, next byte = restart position

### Instruments (max 63)

| Offset | Field |
|--------|-------|
| 0 | Attack/Decay |
| 1 | Sustain/Release |
| 2 | Wave table pointer (1-based, 0=unused) |
| 3 | Pulse table pointer |
| 4 | Filter table pointer |
| 5 | Vibrato param (speed table ptr) |
| 6 | Vibrato delay |
| 7 | Gate-off timer (bits 0-5), bit 6=legato, bit 7=no hard restart |
| 8 | 1st frame waveform ($00=skip, $01-$FD=waveform, $FE-$FF=skip+gate) |
| 9-24 | Instrument name (16 bytes) |

### Tables (4 sections: Wave, Pulse, Filter, Speed)

Each: 1 byte row count (n), n bytes left column, n bytes right column. Max 255 rows.

#### Wave Table
- Left $00: no change; $01-$0F: delay; $10-$DF: waveform; $E0-$EF: inaudible wave; $F0-$FE: wave commands; $FF: jump
- Right: $00-$5F relative note up, $60-$7F relative down, $80 keep freq, $81-$DF absolute note

#### Pulse Table
- Left $01-$7F: modulation duration; $80-$FF: set pulse width; $FF: jump
- Right: signed speed (modulation) or low 8 bits (set)

#### Filter Table
- Left $00: set cutoff; $01-$7F: modulation duration; $80-$FF: set filter params; $FF: jump
- Right: cutoff/speed/resonance+routing depending on left byte

#### Speed Table (vibrato/portamento/funktempo)
- Vibrato: left=speed (bit 7=note-independent), right=depth
- Portamento: 16-bit value (left=MSB, right=LSB)
- Funktempo: left=tempo1, right=tempo2

### Patterns (max 208, max 128 rows)

Each row in .sng = 4 bytes:
- Byte 0: Note ($60-$BC = C-0 to G#7, $BD=rest, $BE=keyoff, $BF=keyon, $FF=end)
- Byte 1: Instrument ($00-$3F)
- Byte 2: Command ($00-$0F)
- Byte 3: Command data

### Pattern Commands

| Cmd | Name | Description |
|-----|------|-------------|
| 0 | Do nothing | Instrument vibrato |
| 1 | Porta up | Speed table index |
| 2 | Porta down | Speed table index |
| 3 | Tone porta | Speed table index ($00=tie) |
| 4 | Vibrato | Speed table index |
| 5 | Set AD | Value |
| 6 | Set SR | Value |
| 7 | Set wave | Waveform value |
| 8 | Set wave ptr | Wave table index |
| 9 | Set pulse ptr | Pulse table index |
| A | Set filter ptr | Filter table index |
| B | Set filter ctrl | Resonance(hi) + routing(lo) |
| C | Set filter cutoff | Value |
| D | Set master vol | $00-$0F=volume |
| E | Funktempo | Speed table index |
| F | Set tempo | $03-$7F=global, $83-$FF=channel-only |

## Packed/Exported SID Format

The `greloc.c` packer/relocator heavily optimizes the .sng into a completely different binary format.

### Packed Pattern Encoding

Variable-length byte stream per pattern:
- `$00`: End of pattern
- `$01-$3F`: Instrument change
- `$40-$4F`: Effect + note follows (next byte = param if cmd!=0)
- `$50-$5F`: Effect + rest (next byte = param if cmd!=0)
- `$60-$BC`: Note values
- `$BD`: Rest, `$BE`: Keyoff, `$BF`: Keyon
- `$C0-$FF`: Packed rests (count = 256-value, max 64)

Instrument/effect bytes omitted if unchanged from previous row.

### Conditional Compilation

The relocator analyzes the song and strips unused features (NOFILTER, NOPULSE, NOVIB, etc.). Player size varies from ~200 to ~800+ bytes.

### Memory Layout

Instrument data stored column-major (all AD values, then all SR values, etc.) for indexed access. Frequency table trimmed to used note range. Channel state: arrays with stride 7 (X = 0, 7, 14 for channels 0-2).

## V1 vs V2 Differences

- V1 IDs: `GTS3`, `GTS4`; V2: `GTS5`
- V1 had arpeggio command; V2 replaced with wave tables
- V2 added 63 instruments, uniform step-programming tables, more commands
- V2 can load V1 songs
