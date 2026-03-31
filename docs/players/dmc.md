# DMC (Demo Music Creator)

## Overview

- **HVSC count:** 10,738 tunes (largest single player in HVSC)
- **Author:** Balazs Farkas (Brian) of Graffity (Hungary)
- **Year:** 1991+
- **Source:** Never publicly released
- **CSDb:** #2596 (V4.0), #2594 (V5.0), #2629 (V7.0)
- **Type:** Duration-based editor (not tick-based — patterns can be any length, no sync between voices)
- **Predecessor:** GMC (Game Music Creator), also by Brian/Graffity

## Versions

| Version | Year | Notes |
|---------|------|-------|
| GMC V1.0-V2.0 | pre-1991 | Game Music Creator, predecessor |
| V2.0/V2.1 | ~1991 | Early version, multiple speed variants (2x, 4x by Keen Acid/Moog) |
| V4.0 | Sep 1991 | Most popular, ~2000 byte player, CSDb #2596 |
| V4.0 pro | ? | Enhanced by Morbid/Onslaught |
| V4.3++ | ? | Enhanced by Moog/Keen Acid (quadruple speed) |
| V5.0 | 1993 | Improved version, CSDb #2594 |
| V5.0+ | Dec 2002 | Enhanced by CreaMD with audible editing |
| V5.1 | ? | Last official public release |
| V5.1+ | 1994 | Package by Graffity and Motiv 8 |
| V5.4 | ? | By Glover/Samar, improved hard restart, rastertime savings, buggy packer |
| V6.0 | ? | Never publicly released, 7-8 rasterlines CPU, by Brian + Syndrom/TIA |
| V7.0 | 1995 | By Axl+Ray/Unreal, based on V4 code, major editor enhancements, CSDb #2629 |
| V7.0A/V7.0B | ? | Sub-versions of V7 |
| DMC 4 Editor 1.0 | Mar 2025 | Cross-platform Windows editor by Logan/Slackers |
| DMC 4 Editor 1.1 | Mar 2025 | Bug fixes, sector duration display, sound bank import/export |

**Key lineage:** V4 → V7 (same player code, enhanced editor). V5 is a separate branch. V6 was internal only.

## Entry Points

- Init: base + $0000 (typically $1000)
- Play: base + $0003
- Extra entry 1: base + $0006 (multi-player mode)
- Extra entry 2: base + $0009
- Tune select: base + $001D

## Player Specs

| Property | DMC V4 | DMC V5 |
|----------|--------|--------|
| Code size | ~2000 bytes | <1900 bytes |
| CPU time (1x) | ~23-27 rasterlines | ~28-33 rasterlines |
| Zero page | $FB-$FF (5 bytes) | $FB-$FF (5 bytes) |
| Max instruments | 32 | 32 |
| Max sectors | 64 | 96-127 (up to 250 rows each) |
| Max subtunes | 8 | 8-31 |
| Instrument size | 11 bytes | 8 bytes |
| Table entry size | 1 byte | 2 bytes (wave/pulse/filter/command) |

## Binary Memory Layout (V4, default base $1000)

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
| +$0A50 | Filter definition table |
| +$0A72 | Wave table (variable length, typically ~48 bytes) |
| +$0AA2 | Track data (sector order lists, variable length) |
| +$0BF9 | Tune pointer table (8 subtunes x 6 bytes = 48 bytes) |
| +$0C01 | Sector data (variable length) |
| end-N | Sector pointer table lo (N = num_sectors) |
| end | Sector pointer table hi (N bytes) |

**Key relationships:**
- Instrument table is always at freq_hi + $0248
- Sector pointer tables are at the very end of the binary
- Tune pointer table: 8 subtunes x 6 bytes (3 interleaved lo/hi pairs)

**NOTE:** These offsets are for standard V4.0. Other versions (V5, V7, custom) will have different offsets. The reliable anchors are:
1. Frequency table (detectable by pattern matching)
2. Instrument table (freq_hi + $0248)
3. Sector pointer table (end of binary, referenced by player code)
4. Tune pointer table (found via LDA abs,Y pair in player code)

## Instrument Format

### V4: 11 bytes per instrument, 32 max

| Byte | Field | Description |
|------|-------|-------------|
| 0 | AD | Attack (hi nib) / Decay (lo nib) — written to SID $D405 |
| 1 | SR | Sustain (hi nib) / Release (lo nib) — written to SID $D406 |
| 2 | Wave | Wave table start position index (0-based into wave table) |
| 3 | PW1 | Pulse width speed byte 1 |
| 4 | PW2 | Pulse width speed byte 2 |
| 5 | PW3 | Pulse width speed byte 3 |
| 6 | PW-L | Pulse width modulation limit (border limiter) |
| 7 | Vib1 | Vibrato: hi nib = pause/delay frames, lo nib = pitch swing range |
| 8 | Vib2 | Vibrato extended range modulation |
| 9 | Filt | Filter set number (0 = no filter, 1+ = filter definition index) |
| 10 | FX | Effect flags (see below) |

### V5: 8 bytes per instrument, 32 max

The exact mapping of the reduced 8-byte V5 format is **not publicly documented**. Likely the 3 pulse width bytes (PW1-PW3) are consolidated or removed. Needs reverse-engineering from V5 binaries.

### FX Flags (byte 10, V4)

| Bit | Value | Flag | Meaning |
|-----|-------|------|---------|
| 0 | $01 | Drum | Triggers drum-mode synthesis |
| 1 | $02 | No filter reset | Don't reset filter on new note |
| 2 | $04 | No pulse reset | Don't reset pulse width on new note |
| 3 | $08 | No gate | Suppress gate bit (no ADSR retrigger) |
| 4 | $10 | Holding | Instrument holds after wave table completes |
| 5 | $20 | Filter activation | Enable filter for this instrument |
| 6 | $40 | Dual effect | Half-speed processing |
| 7 | $80 | Cymbal | Special noise-based cymbal synthesis |

## Sector Data Format (variable-length note sequences)

| Byte Range | Meaning |
|------------|---------|
| $00-$5F | Note number (C-0 through B-7, 96 notes) |
| $60-$7C | Duration command (AND $1F = ticks; duration 0 = 1 tick) |
| $7D | Continuation/switch: disable ADSR reset on next note (legato/tie) |
| $7E | Gate off: release current note |
| $7F | End of sector (V4 terminator) |
| $80-$9F | Instrument select (AND $1F = instrument number 0-31) |
| $A0-$BF | Glide command ($A0 + semitones, portamento/slide) |
| $C0-$DF | Additional commands (volume, etc.) — not fully documented |
| $E0-$FF | Extended commands; $FF also serves as sector end in some V5 variants |

**Timing:** Actual time in frames = (Tune Speed + 1) × Duration value. Sectors should synchronize across channels using integer multiples.

## Track Data Format (order list per voice)

| Byte Range | Meaning |
|------------|---------|
| $00-$3F | Sector number (play this sector next) |
| $80-$8F | Transpose down: -(value AND $0F) semitones, then next byte is sector |
| $A0-$AF | Transpose up: +(value AND $0F) semitones, applies to following sectors |
| $FE | End of tune (deactivate voice, stop playing) |
| $FF | Loop to beginning of track |

**Note:** Transpose commands set the transposition for all following sectors until changed. $A0 = transpose 0 (reset).

## Tune Pointer Table

8 subtunes × 6 bytes each. Format: 3 interleaved 16-bit addresses (lo0, hi0, lo1, hi1, lo2, hi2) pointing to the track data start for each voice.

Player accesses via:
```
LDA tune_ptr_table,Y    ; lo byte (Y = voice * 2)
LDA tune_ptr_table+1,Y  ; hi byte
```

Subtune selection: subtune number × 8 (via ASL ×3) indexes this table. Only the first 6 bytes of each 8-byte subtune slot are used (last 2 are padding).

## Sector Pointer Table

Two parallel arrays at the end of the binary data:
- Lo-bytes array: N bytes (one per sector)
- Hi-bytes array: N bytes (one per sector)

For V4: up to 64 sectors. For V5: up to 96-127 sectors.
Each entry is the absolute address of a sector's start in memory.

## Wave Table

Sequence of SID waveform/control register values, stepped frame-by-frame (1 entry per frame at 50Hz PAL):

- Bits 4-7: Waveform selection (1=tri, 2=saw, 4=pulse, 8=noise)
- Bits 0-3: Control bits (bit 0=gate, bit 1=sync, bit 2=ring, bit 3=test)
- Combined waveforms: $30=tri+saw, $50=tri+pulse, $60=saw+pulse

**Special values:**
- $FE: Hold (no waveform change this frame)
- $FF: Terminate wave table (hold last value)
- $9x (≥$90): Jump back x steps in wave table (loop). E.g. $91 = jump back 1 step (repeat previous entry)

The gate bit in wave table entries is ANDed with a gate mask by the player before writing to SID $D404. The player controls gate on/off independently of the wave table waveform.

## Filter Definition Table (6-step envelope per filter)

| Parameter | Description |
|-----------|-------------|
| R | Resonance/Rate (0-F) |
| T | Filter Type: bit 0=LP, bit 1=BP, bit 2=HP (combinable) |
| Cutoff | Starting cutoff frequency |
| RT | Repeat step position (loop point, 01-05) |
| ST | Stop at defined frequency step |
| S1-S6 | Step direction: $01-$7F ascending, $80 neutral, $81-$FF descending |
| X1-X6 | Step duration/magnitude pairs |

## Frequency Table

Standard PAL, 96 entries (8 octaves × 12 notes), stored as two 96-byte arrays:
- Hi bytes first (at +$06A8 in V4)
- Lo bytes second (at +$0708 in V4)

Some DMC versions use custom frequency tables (non-standard tuning).

## Hard Restart / Testbit Method

DMC uses the "modern testbit method" (shared with JCH player):

1. 2+ frames before next note: ADSR set to preset ($0000, $0F00, or $F800), gate cleared
2. First note frame: AD and SR values written, then $09 written to waveform register (test bit + gate)
3. Second note frame: actual waveform value loaded from wave table, note is heard

Works reliably on PAL only. Gives sharp, clean attack.

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
6. Look up frequency from freq table, load instrument parameters
7. Step wave table, apply PWM
8. Apply vibrato, filter, effects
9. Write SID registers ($D400 + voice offset)

## Pulse Width Modulation

3 speed bytes (PW1-PW3) control the pulse width cycling pattern:
- PW speed table at +$0644 (96 entries, shared across instruments)
- PW-L (limit byte) defines the boundary for direction reversal
- Pulse width oscillates between limits at the defined speed

## SIDId Signature Patterns

**DMC (base):**
```
18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

**DMC V4.x:**
```
FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0
```

**DMC V5.x:**
```
BC ?? ?? B9 ?? ?? C9 90 D0 AND BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

**DMC V6.x:**
```
A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4 8D 0B D4 8D 12 D4 8D 11 D4 A9 1F 8D 18 D4 A9 F2 8D 17 D4 60 CE ?? ?? 30 69 20
```

## Key Differences Between Versions

| Feature | V4 | V5 | V7 |
|---------|----|----|-----|
| Instrument size | 11 bytes | 8 bytes | 11 bytes (V4 code) |
| Max sectors | 64 | 96-127 | 64 |
| Max subtunes | 8 | 8-31 | 1-5 |
| Player code | ~2000 bytes | <1900 bytes | ~3000 bytes (V4 + editor code) |
| Rastertime | 23-27 lines | 28-33 lines | 23-27 lines |
| Wave table | 1 byte/entry | 2 bytes/entry | 1 byte/entry |
| Packer | Built-in | SYS $2E00 | Built-in + turbotape |

## References

- [CSDb - DMC 4.0](https://csdb.dk/release/?id=2596)
- [CSDb - DMC V5.0](https://csdb.dk/release/?id=2594)
- [CSDb - DMC 7.0 by Unreal](https://csdb.dk/release/?id=2629)
- [CSDb - DMC V5.1+ Package](https://csdb.dk/release/?id=2600)
- [CSDb - DMC V5.4 by Samar](https://csdb.dk/release/?id=36658)
- [CSDb - DMC Relocator](https://csdb.dk/release/?id=10758)
- [CSDb - DMC 4 Editor 1.1](https://csdb.dk/release/?id=251057)
- [Cadaver/SIDId signatures](https://github.com/cadaver/sidid/blob/master/sidid.cfg)
- [WilfredC64/player-id](https://github.com/WilfredC64/player-id)
- [Cadaver - music player technical rant](https://cadaver.github.io/rants/music.html)
- [Chordian C64 editors comparison](http://chordian.net/c64editors.htm)
- [TND64 Music Scene tutorial (DMC 4/7)](http://www.tnd64.unikat.sk/music_scene.html)
- [HVMEC - DMC versions](https://hvmec.altervista.org/blog/?p=700)
- [Restore64.dev - SID disassembler](https://restore64.dev/)
- [Lemon64 DMC threads](https://www.lemon64.com/forum/viewtopic.php?t=86611)
