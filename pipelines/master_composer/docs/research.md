## Master Composer (1,075 tunes)

- **Author:** Paul Kleimeyer
- **Publisher:** Access Software, Inc.
- **Year:** 1983-1984
- **Price:** $39.95
- **Source:** Not public
- **CSDb:** #128699
- **Historical significance:** First popular C64 music editor

### Entry Points (typical load $7580)
- $7580: Init (7 bytes)
- $7587: Play (init + 7)
- VBlank-timed, interrupt-driven
- Relocatable (absolute addresses adjusted at load time)

### Three-Tier Hierarchy

**1. Pages (up to 23):** Played sequentially, each specifies start/end block.

**2. Blocks (up to 64):** Each defines ALL SID register values for 3 voices:
- Waveform, ADSR, pulse width, filter cutoff, resonance/routing, volume/mode
- When a new block starts, all SID parameters change (like switching instruments)

**3. Bars (up to 127):** Each bar = up to 16 notes (16th-note resolution):
- $00 = rest
- $01-$63 = note frequency index
- Bar durations stored in separate table

### Memory Layout

| Offset | Purpose |
|--------|---------|
| +$000 | Init routine |
| +$007 | Play routine entry |
| +$0AA | Block register write routine |
| +$300 | Frequency table lo (96 entries) |
| +$360 | Frequency table hi (96 entries) |
| +$3C0 | Player variables (page/block/bar indices, flags) |
| +$3D0 | Bar duration table (127 entries) |
| +$450 | Block parameter tables (64 entries each, 16 tables for all SID regs) |
| +$A68 | Page table (23 entries) |
| +$A80 | Note/music data |

Player code: ~768 bytes. Total: 3600-7800 bytes.

### Characteristics
- No built-in effects (no vibrato, arpeggio, PWM)
- Direct SID register manipulation per block
- Default tuning: 450 Hz (NTSC) / 433.5 Hz (PAL)
- Identical player code across all files (only addresses differ for relocation)
- Known bug: decaying hum after final page completes
- Page duplication allows songs up to ~20 minutes
