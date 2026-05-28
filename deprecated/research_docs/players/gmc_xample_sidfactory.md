# GMC, X-Ample, SID Factory II

## GMC / Superiors - Game Music Creator (446 tunes)

- **Author:** Balazs Farkas (Brian) of Graffity (Hungary)
- **Year:** 1990
- **Source:** Not public
- **CSDb:** #7268
- **Predecessor to DMC** (Demo Music Creator)

### Entry Points
- Init: $1000, Play: $1003

### Data Structure
Two-level hierarchy: Tracks -> Sectors.

**Track level:** Up to 8 tunes per file. Tracks reference sectors with transpose controls.

**Sector level (per step):**
- DUR: duration
- SND: sound/instrument number
- APM: amplitude/modulation
- GLD: glide/portamento
- HLD: hold duration
- CONT: continuation/tie flag
- END: terminator

Sound definitions: 16 bytes each (indexed via 4x ASL A = multiply by 16).

### SIDId Variants
GMC/Superiors (V1.0), GMC_V2.0/Superiors.

---

## X-Ample / Compotech (387 tunes)

- **Authors:** Markus Schneider (driver), Helge Kozielek (optimizations), Joachim Fräder (editor UI) — X-Ample Architectures (Germany)
- **Year:** 1989-1995
- **Source:** Not public
- **CSDb:** #122614 (Compotech V2.1)

### Evolution
Schneider's driver -> Parsec Music Editor -> Compotech editor (full tracker).

### Architecture
Player iterates 3 voices via bitmask, calls per-voice subroutine, advances SID register base by 7 per voice ($D400, $D407, $D40E).

### SIDId Variants (6+)
Compotech_V2.x, Sonic/SDS, Thomas_Detert, XTracker_V4.1x, XTracker_V4.2x, X-Ample_Digi.

### Notable Users
Thomas Detert (177 SIDs), Stefan Hartwig (134 SIDs), Markus Schneider (105 SIDs).

---

## SID Factory II / Laxity (380 tunes)

- **Authors:** Thomas Egeskov Petersen (Laxity), Jens-Christian Huus (JCH), Michel de Bree (Youth)
- **Year:** 2006 (C64 editor), 2020+ (cross-platform)
- **License:** GPL v2
- **Source:** https://github.com/Chordian/sidfactory2
- **Actively developed** (latest build 2026)
- **CSDb:** #210571

### Modular Driver System

Ships with interchangeable 6502 drivers:

| Driver | Description |
|--------|-------------|
| 11 | Default, full-featured (pulse, filter, wave tables, arpeggio, commands) |
| 12 | Extremely simple, basic effects only |
| 13 | Emulates Rob Hubbard's player sound |
| 14 | Short gate-off variant of driver 11 |
| 15 | Tiny driver mark I |
| 16 | Tiny driver mark II (no commands) |

CPU: ~24 rasterlines for driver 11.

### Song Structure (Driver 11)

**Three levels:**

1. **Order Lists** (3 voices, independent lengths): 2-byte entries XXYY
   - XX: transpose ($A0=none, range -32 to +31 semitones)
   - YY: sequence number (0-127)

2. **Sequences** (up to 128, shared pool): Rows of note data
   - Note column: 8 octaves, `+++`=gate on, `---`=gate off
   - Instrument column: 2-digit hex ($00-$FF), `**`=tie
   - Command column: 2-digit hex from command table
   - Max 1024 rows, packed to max 256 bytes
   - $FF = end-of-data, $7E = loop marker

3. **Tempo Table**: Countdown values for row timing. $7F = loop. Enables swing/variable tempo.

### Instrument Format (6 bytes per row)

| Byte | Field | Description |
|------|-------|-------------|
| 0 | AD | Attack(hi)/Decay(lo) |
| 1 | SR | Sustain(hi)/Release(lo) |
| 2 | Control | Bit 7=hard restart, bit 4=test bit, bits 0-3=HR table ptr |
| 3 | Pulse Table Index | Start position |
| 4 | Filter Table Index | Start position |
| 5 | Wave Table Index | Start position |

### Wave Table (2 bytes per row)

Byte 1 = waveform ($11=tri, $21=saw, $41=pulse, $81=noise, combos). $7F=loop (byte 2 = target).

Byte 2: $00-$7F = relative semitone offset, $80-$DF = absolute frequency.

Core of sound design: controls waveform changes, arpeggios, oscillator behavior over time.

### Pulse/Filter/HR Tables

- **Pulse Table:** 12-bit PWM control over time
- **Filter Table:** Cutoff, resonance, mode, voice routing over time
- **HR Table:** ADSR values for 2 ticks before note trigger

### Commands (Driver 11)

Pulse program index changes, tempo changes, main volume, note delay (0-F ticks), filter enable toggle.

### File Format

SF2 files are PRG files containing 6502 driver + music data + interrupt driver for VICE playback (SYS 4093). Relocatable to any C64 memory address. Configurable zero-page usage.
