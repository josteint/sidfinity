# JCH NewPlayer

## Overview

- **HVSC count:** 3,678 tunes
- **Author:** Jens-Christian Huus (JCH) of Vibrants
- **Year:** 1988+ (editor), many player versions
- **Key versions:** NP 17.G0, 20.G4 (standard), 20.Q0 (multispeed), 21.G4-G6, 22-25
- **Source:** JCH released player source code; many derivatives exist
- **Key ref:** https://codebase64.com/doku.php?id=base:jch_20.g4_player_file_format
- **Related:** CheeseCutter (cross-platform port), SID Factory II (modern successor)

## Entry Points

- Init: $1000 (A = subtune)
- Play: $1003 (50 Hz)

## Memory Layout (NP 20.G4 at $1000)

| Address | Content |
|---------|---------|
| $1000 | Player code (~1000 bytes) |
| $18CB | Wave table column A (256 bytes) |
| $19CB | Wave table column B (256 bytes) |
| $1ACB | Filter table (256 bytes) |
| $1BCB | Pulse table (256 bytes) |
| $1CCB | Instrument table (32 x 8 = 256 bytes) |
| $1DCB | Sequence pointers low (256 bytes) |
| $1ECB | Sequence pointers high (256 bytes) |
| $1FCB | Super table / command table (256 bytes) |
| $20CB | Order list voice 0 (~1024 bytes) |
| $24CB | Order list voice 1 |
| $28CB | Order list voice 2 |
| $2CCB+ | Sequence data |

## Instrument Format (8 bytes, 32 max)

| Byte | Field | Description |
|------|-------|-------------|
| A | AD | Attack/Decay |
| B | SR | Sustain/Release |
| C | HR+Delay | Hi nib: HR type ($0x/$4x/$8x/$Ax), lo nib: wave delay |
| D | HR Waveform | Waveform during hard restart |
| E | Filter Ptr | $00=none |
| F | Pulse Ptr | $00=none |
| G | (unused) | |
| H | Wave Ptr | Wave table start position |

### Hard Restart Types (byte C high nibble)
- $0x: Gate off 3 frames before, waveform clear 1 frame before
- $4x: Soft restart (gate off 2 frames before)
- $8x: Hard restart (gate off + HR ADSR)
- $Ax: Laxity restart (like $8x but AD untouched)

## Sequence Data (byte pairs)

Byte AA (control):
- $7F: end of sequence
- $90: tie note
- $A0-$BF: instrument $00-$1F
- $C0-$DF: super table pointer
- $80: no action / empty row

Byte BB (note/gate):
- $00: gate off
- $01+: note value
- $7E: gate hold

## Order List

Per voice: transpose value ($A0=none, $A1=+1, $9F=-1), sequence number, $FF=end.

## Wave Table (2 x 256 bytes)

Byte A (transpose): $00-$5F relative up, $80-$DF absolute pitch, $7E=stop, $7F=loop (B=target)

Byte B (waveform): $00=no change, $01-$0F=delay override, $10-$DF=SID control reg, $E0-$EF=alt values

## Pulse Table (NP 20.G4: 2 bytes/row, NP 21+/CheeseCutter: 4 bytes/row)

CheeseCutter 4-byte: A=duration/direction, B=add value, C=initial PW ($FF=retain), D=jump ($7F=stop)

## Filter Table (NP 20.G4: 2 bytes/row, NP 21+/CheeseCutter: 4 bytes/row)

A >= $80: init row (filter type, resonance+routing, cutoff)
A < $80: sweep row (duration, add value, cutoff)

## Super Table (Command Table)

Row 0 stores hard restart ADSR values. Other rows:

| Cmd | Type |
|-----|------|
| 0 | Slide up |
| 1 | Slide down |
| 2 | Vibrato |
| 3 | Detune |
| 4 | Set ADSR |
| 5 | Lo-fi vibrato |
| 6 | Set waveform |
| 7 | Portamento |
| 8 | Stop slide/porta |

## Player Specs

- Code size: ~1000 bytes (NP 20.G4), ~1900 bytes (CheeseCutter v4)
- Zero page: 2 bytes
- CPU: ~12-13 rasterlines (NP 20.G4)
- Max instruments: 32 (NP 20.G4), 48 (CheeseCutter)
- Max sequences: 127, max rows/sequence: 180
- Speed: 1x only (NP 20.G4); multispeed in Q-series and NP 21+

## SIDId

21 distinct signature variants (V1-V20, V0x, Dane_NewPlayer).
