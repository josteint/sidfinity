# HardTrack Composer & Master Composer

## HardTrack Composer (1,170 tunes)

- **Authors:** Brush (code) and Longhair/Milosz Ignatowski (player routine), Elysium/Parados (Poland)
- **Year:** 1992
- **Source:** Available at elysium.filety.pl (depacker, editor, assembly source)
- **CSDb:** #74928 (V1.0), #36647 (V1.0+)
- **Scene:** Primarily Polish C64 scene

### Entry Points (typical load $1000)
- $1000: JMP init
- $1003: JMP play
- CIA timer-based (multispeed up to 6x)

### Memory Layout

| Offset | Purpose |
|--------|---------|
| +$000 | JMP init, JMP play |
| +$006 | Speed counter, subtune config |
| +$00A-$01B | Voice ADSR shadows, pattern pointers, track positions |
| +$01F | Metadata (song name, author, date) |
| +$060 | Init routine (~120 bytes) |
| +$0D8 | Play routine (~1200 bytes) |
| +$651 | Instrument macro data tables |
| +$880 | Frequency table hi (96 entries) |
| +$8E0 | Frequency table lo (96 entries) |
| +$919 | Track data |
| ~+$1020 | Pattern data |

Player code: ~1536 bytes. Total: 3000-6000 bytes.

### Track Data (per voice)
- $00-$7F: Pattern number
- $80-$FC: Change transposition (signed)
- $FD xx: Jump to position xx
- $FE: End (stop)
- $FF: Loop to beginning

### Pattern Data
- $00-$5F: Note (index into 96-entry freq table)
- $60: Rest/tie
- $61: DEL (gate off)
- $62: CUT (hard cut)
- $63 yy: Glissando up by yy
- $64 yy: Glissando down by yy
- $80-$FF: Set instrument (value AND $7F)
- $FF: End of pattern

### Instrument Macro Format
Pairs of xx yy bytes:
- xx = waveform register value
- yy = transposition ($00-$5C relative, $80-$DF absolute for drums)
- FX byte: hi nib = type (0=normal, 8=drum), lo nib = hard restart frames
- Additional: pulse start, filter start, vibrato width/add/end

### Features
Multispeed (up to 6x), hard restart, glissando up/down, instrument macros with waveform sequences, drum instruments (absolute pitch), pulse width and filter automation.

### Top Users
Bzyk (262), Klax (197), Randy (92), Remarque (87), Shapie (81).

---

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
