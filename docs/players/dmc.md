# DMC (Demo Music Creator)

## Overview

- **HVSC count:** 10,738 tunes (largest single player in HVSC)
- **Author:** Balazs Farkas (Brian) of Graffity
- **Year:** 1991+
- **Source:** Not public
- **CSDb:** #2596 (V4.0), #2594 (V5.0)
- **Type:** Duration-based editor (not tick-based — patterns can be any length, no sync between voices)

## Versions

- **V2.1** (1991) — early version
- **V4.0** (1991) — most popular, ~2000 byte player
- **V5.0** (1993) — improved version
- **V5.0+** (2002) — enhanced by CreaMD with audible editing
- **V6.0** — unreleased, low rastertime (7-8 rasterlines)
- **V7.0** — by Graffity + Unreal, based on V4 code
- **DMC 4 Editor 1.1** (2025) — modern cross-platform Windows editor by Logan

## Entry Points

- Init: base + $0000
- Play: base + $0003
- Default load: $1000

## Player Specs

- Code size: ~2000 bytes
- CPU: ~23-27 rasterlines/frame
- Zero page: $FB-$FF (5 bytes)
- Max instruments: 32, max sectors: 64, max subtunes: 8

## Binary Memory Layout

| Offset | Content |
|--------|---------|
| +$0000 | JMP init |
| +$0003 | JMP play |
| +$0006 | JMP extra_entry_1 |
| +$0009 | JMP extra_entry_2 |
| +$000C | Player variables |
| +$001D | JMP tune_select |
| +$0020 | Copyright string |
| +$0085 | Play routine code (~1475 bytes) |
| +$0600 | SID register write subroutines |
| +$0644 | Pulse width speed table (96 entries) |
| +$06A8 | Frequency table hi (96 entries) |
| +$0708 | Frequency table lo (96 entries) |
| +$0807 | Tune select/init subroutine |
| +$0888 | Filter processing code |
| +$08F0 | Instrument table (32 x 11 = 352 bytes) |
| +$0A14 | Filter definition table |
| +$0A72 | Wave table |
| +$0AA2 | Track data (sector order lists) |
| +$0BF9 | Tune pointer table (8 subtunes x 6 bytes) |
| +$0C01 | Sector data (variable length) |
| end-40 | Sector pointer table lo |
| end-14 | Sector pointer table hi |

## Instrument Format (11 bytes per instrument, 32 max)

| Byte | Field | Description |
|------|-------|-------------|
| 0 | AD | Attack/Decay |
| 1 | SR | Sustain/Release |
| 2 | Wave | Wave table start position |
| 3 | PW1 | Pulse width speed byte 1 |
| 4 | PW2 | Pulse width speed byte 2 |
| 5 | PW3 | Pulse width speed byte 3 |
| 6 | PW-L | Pulse width modulation limit |
| 7 | Vib1 | Vibrato (hi nib=delay, lo nib=range) |
| 8 | Vib2 | Vibrato extended range |
| 9 | Filt | Filter set number |
| 10 | FX | Effect flags (see below) |

### FX Flags (byte 10)
- Bit 0: Drum effect
- Bit 1: No filter reset
- Bit 2: No pulse reset
- Bit 3: No gate
- Bit 4: Holding
- Bit 5: Filter activation
- Bit 6: Dual effect (half-speed)
- Bit 7: Cymbal effect

## Sector Data Format (variable-length note sequences)

| Byte Range | Meaning |
|------------|---------|
| $00-$5F | Note (C-0 through B-7, 96 notes) |
| $60-$7C | Duration command (AND $1F = ticks) |
| $7D | Switch/continuation (no ADSR reset) |
| $7E | Gate off |
| $7F | End of sector |
| $80-$9F | Instrument select (AND $1F) |
| $A0-$BF | Glide command ($A0 + semitones) |
| $C0-$DF | Additional commands (volume, etc.) |
| $E0-$FF | Extended commands |

## Track Data Format (order list per voice)

| Byte Range | Meaning |
|------------|---------|
| $00-$3F | Sector number |
| $80-$BF | Sector with flag (AND $3F) |
| $A0+val | Transposition (val-$A0 semitones) |
| $FE | End of tune (deactivate voice) |
| $FF | Loop to beginning |

## Tune Pointer Table

8 subtunes x 6 bytes each: 3 pairs of (lo, hi) addresses pointing to track data start for each voice. Subtune number x 8 (via ASL x3) indexes this table.

## Sector Pointer Table

Two parallel arrays at end of data: lo-bytes and hi-bytes for up to 64 sector start addresses. Sectors are variable-length, terminated by $7F.

## Wave Table

Sequence of SID control register values stepped through frame-by-frame. Bits 4-7 = waveform (tri/saw/pulse/noise), bits 0-3 = gate/sync/ring/test. $FF = terminate, $FE = loop/hold.

## Filter Definition (6-step envelope per filter)

- R: Resonance/Rate (0-F)
- T: Type (bit 0=LP, 1=BP, 2=HP)
- Cutoff: Starting frequency
- RT: Repeat step (loop point)
- ST: Stop step
- S1-S6, X1-X6: Step direction/magnitude and duration pairs

## Frequency Table

Standard PAL, 96 entries (8 octaves x 12 notes).

## Play Routine Flow

1. Decrement speed counter; reload on zero
2. For each voice (X=0,1,2): call voice processing
3. Write filter cutoff hi to $D416
4. Write volume/mode to $D417

### Voice Processing
1. Check voice active
2. Decrement duration counter
3. If expired: read next byte(s) from sector
4. If sector ended ($7F): advance track to next sector
5. If track ended ($FF=loop, $FE=stop)
6. Look up frequency, load instrument
7. Step wave table, apply PWM
8. Apply vibrato, filter, effects
9. Write SID registers

## SIDId Variants

DMC (base), DMC_V4.x, DMC_V5.x, DMC_V6.x — each with distinct byte signatures.
