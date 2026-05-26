# Music Assembler

## Overview

- **HVSC count:** ~6,403 tunes
- **Authors:** Marco Swagerman (MC) and Oscar Giesen (OPM), Dutch USA-Team
- **Year:** 1989, published by Markt+Technik
- **Documentation:** Manual PDF at https://csdb.dk/getinternalfile.php/137191/masm_manual_0_01b.pdf
- **CSDb:** #94388

## Key Concept

Not a tracker — it "assembles" complete standalone executables. Saving bundles the player routine + compressed music data into a relocatable binary. Base address user-selectable $0400-$FF00. Play via `SYS <base>`.

## Player Signature

- **Init address:** base + $0048
- **Play address:** base + $0021
- **IRQ setup:** base + $0000

## Data Structures

### Presets (Instruments) — 32 max, 8 bytes each

- ADSR envelope (2 bytes: AD, SR)
- Waveform byte (noise/pulse/saw/tri/disable/ring/sync/gate)
- Pulse rate (2 digits: LSB, MSB)
- Pulse effects (slide or vibrate mode with pulse byte/level/speed)
- Vibrato parameters (delay, speed, level)
- Arpeggio link (index into arpeggio table, or none)

### Arpeggios — 16 max

Each step has:
- Waveform byte
- Note offset (semitones, absolute with `<` or relative)
- Filter frequency value
- $FF = loop, $FE = stop

### Tracks — 3 separate (one per SID voice)

Each entry: sequence number ($00-$FD, $FE=stop, $FF=loop), transpose offset (0-15), repeat count.

### Sequences — Monophonic note lists

Each step:
- Note (C through B, across octaves)
- Duration ($00=16th, $01=8th, $03=quarter, $07=half, $0F=whole, $1F=double whole)
- Optional preset selection (PRE command)
- Optional modifiers: legato (Shift+note), hold, rest, portamento (2 extra columns), low-pass filter (3 params)

### Filter

Only low-pass supported. Shared across voices. Applied to triggering track and all lower-numbered tracks.

## Assembled Output Format

Player code + compressed data. The manual states data is "assembled into intricate, to many people unreadable data which is disassembled by the player routine while playing."

## File Types

- `s.filename` — complete song (player + data, relocatable)
- `p.filename` — presets only (shareable)
