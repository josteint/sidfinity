---
source_url: local: /home/jtr/sidfinity/tmp/odintracker_research/OdinTracker113src/
fetched_via: local read (downloaded from http://csdb.dk/getinternalfile.php/154684/OdinTracker113src.zip)
fetch_date: 2026-06-15
author: Zoltan Konyha (Zed), zed@inf.bme.hu
content_date: 2001-04-17 (v1.13)
reliability: primary (official source code)
---

# OdinTracker Player Format — Complete Technical Reference

Source: OdinTracker 1.13 source code (DASM assembler, `vplayer.s` + `defines.s` + `help/help.in`)

## Version history

- **1.00** — released 15 Feb 2000 (CSDb release id=12577)
- **1.13** — released 17 Apr 2001 (CSDb release id=2628)
- Help text: "The fileformat has changed in version 1.1x. If a song sounds like
  garbage, it may be the old format and needs to be loaded using 'Import 1.0x song'.
  WARNING: the filter settings will not be imported."

**Summary:** Two known versions with incompatible file formats. Version 1.1x
introduced the filter table into the instrument structure (fields 13–15). The
player engine (vplayer.s) is the same binary for all 1.1x+ songs.

## Memory layout (editor / packed song)

All addresses are for the editor's unpacked format. Packed songs are relocated
to a user-specified page boundary.

| Symbol            | Address | Size     | Contents |
|-------------------|---------|----------|----------|
| `ORDERLIST`       | $4000   | 256 B    | Order list (pattern indices, $FF = end) |
| `SONGTITLE`       | $4100   | 32 B     | Song title (null-terminated) |
| `PATTERNS`        | $4200   | $600 B   | 256 patterns × (3 track numbers + 3 transposes) = 6 bytes/pattern |
| `INSTRUMENTS`     | $4800   | 512 B    | 32 instruments × 16 bytes, stored transposed (see below) |
| `INSTRUMENTNAMES` | $4A00   | 512 B    | 32 instrument names × 16 bytes |
| `WAVETABLE`       | $4C00   | 256 B    | Wave table (one flat array, shared by all instruments) |
| `ARPEGGIOTABLE`   | $4D00   | 256 B    | Arpeggio table (one flat array, shared) |
| `FILTERTABLE`     | $4E00   | 256 B    | Filter table (one flat array, shared) — v1.1x+ |
| `SONGSTARTTABLE`  | $4F00   | 256 B    | Subsong start positions (orderlist indices) |
| `TRACKS_BASE`     | $5000   | $6000 B  | 128 tracks × 64 rows × 3 bytes = 192 B/track |

### Packed song layout (vplayer.s at VPLAYER=$B000, or relocated)

The packer produces a "decompiled" format with separate per-voice tables:

| Symbol               | Size  | Contents |
|----------------------|-------|----------|
| `TRACKTRANSPOSES0/1/2` | 256 B each | Per-order transpose for voices 0/1/2 |
| `TRACKPOINTERSLO0/1/2` | 256 B each | Low byte of track pointer for voices 0/1/2 |
| `TRACKPOINTERSHI0/1/2` | 256 B each | High byte of track pointer for voices 0/1/2 |

These 9 tables (9 × 256 = 2304 bytes) replace the PATTERNS + orderlist mechanism
in packed songs. The player reads transpose and pointer directly by order number
(X register = ordernumber).

## Instrument structure (16 bytes, transposed storage)

The 32 instruments are stored transposed: field N of all 32 instruments occupies
addresses `INSTRUMENTS + N*32 .. INSTRUMENTS + N*32 + 31`.

| Field | Offset | Name | Description |
|-------|--------|------|-------------|
| 0     | $00 | `INST_AD`               | Attack (hi nybble) / Decay (lo nybble) → SID $D405 |
| 1     | $01 | `INST_SR`               | Sustain (hi) / Release (lo) → SID $D406 |
| 2     | $02 | `INST_WAVETABLESTART`   | Wave table start index |
| 3     | $03 | `INST_WAVETABLEEND`     | Wave table end index (inclusive) |
| 4     | $04 | `INST_WAVETABLELOOP`    | Wave table loop index |
| 5     | $05 | `INST_ARPTABLESTART`    | Arpeggio table start index |
| 6     | $06 | `INST_ARPTABLEEND`      | Arpeggio table end index (inclusive) |
| 7     | $07 | `INST_ARPTABLELOOP`     | Arpeggio table loop index |
| 8     | $08 | `INST_VIBDELAY`         | Ticks before instrument vibrato starts |
| 9     | $09 | `INST_VIBDEPTH_SPEED`   | Vibrato: hi nybble = depth, lo nybble = speed |
| 10    | $0A | `INST_PULSEWIDTH`       | Initial pulse width bits [11:4] (8 MSBs) |
| 11    | $0B | `INST_PULSESPEED`       | Pulse sweep speed (added to 8 LSBs per tick) |
| 12    | $0C | `INST_PULSELIMITS`      | lo nybble = lower limit bits [11:8]; hi nybble = upper limit bits [11:8] |
| 13    | $0D | `INST_FILTERTABLESTART` | Filter table start index (v1.1x+) |
| 14    | $0E | `INST_FILTERTABLEEND`   | Filter table end index (v1.1x+) |
| 15    | $0F | `INST_FILTERTABLELOOP`  | Filter table loop index (v1.1x+) |

**Instrument 0 is reserved** (means "no instrument" in track).

## Track row format (3 bytes per row)

Each row in a track is 3 bytes:

```
Byte 0: [bit7=effect_msb] [bits6:0 = note]
Byte 1: [bits7:5 = effect_low3] [bits4:0 = instrument]
Byte 2: effect parameter
```

**Note encoding:**
- 0 = no note (hold previous)
- 1–96 = C-0 through B-7 (semitone index, C-0=1, C#-0=2, … B-7=96)
- 97 = note off (gate release)

**Effect number** = (byte0_bit7 << 3) | (byte1_bits7:5 >> 5)
This gives a 4-bit effect number (0–15 = effects 0–F).

**Instrument number** = byte1 & $1F (0–31; 0 = no new instrument)

**Fetchrow decoding (from vplayer.s):**
```asm
lda (player_trackptr),y     ; byte 0
cmp #$80                    ; move bit7 into C
and #$7f
sta fr_nextnote+1           ; note (bits 6:0)
iny
lda (player_trackptr),y     ; byte 1
ror                         ; C (=bit7 of byte0) → bit7 of A
lsr / lsr / lsr / lsr       ; >> 4 → effect = (C << 3) | (byte1 >> 5)
sta chn_effect,x            ; effect = bits[3:0] after >>4 with C rolled in
```

## Effect table

| Effect | Name | Parameter | Description |
|--------|------|-----------|-------------|
| 0      | None         | —     | No effect |
| 1      | Slide        | $00–$7F = slide down; $80–$FF = slide up (by param-$80) | Multiplied ×16 per tick |
| 2      | Set Pulse Width | $00–$FF | Sets pulse width bits [11:4] (8 MSBs) |
| 3      | Slide to Note | $00–$FF | ProTracker-style portamento; speed ×16 per tick; disables hard restart |
| 4      | Vibrato      | hi=depth, lo=speed | Overrides instrument vibrato |
| 5      | Set Pulse Speed | $00–$FF | Speed of pulse width sweep |
| 6      | Set Pulse Limits | hi=lower bits[11:8], lo=upper bits[11:8] | Pulse swing limits |
| 7      | Set AD       | $AD   | Override Attack/Decay from track |
| 8      | Set SR       | $SR   | Override Sustain/Release from track |
| 9      | Set Waveform | $WF   | Override wave table waveform (SID $D404 value) |
| A      | Arpeggio     | hi=note1_delta, lo=note2_delta | ProTracker-style; overrides arp table |
| B      | Order Jump   | $xx   | Jump to order $xx |
| C      | Set Filter Cutoff | $xx | 8 MSBs of filter cutoff (overrides filter table) |
| D      | Pattern Break | $xx  | Break to row $xx (hex) of next pattern |
| E      | Filter Resonance/Input | hi=resonance, bits[2:0]=voice enables | Controls SID $D417 |
| F      | Multi-function | — | See sub-effects below |

### Effect F sub-effects

| Parameter | Sub-effect |
|-----------|------------|
| $00–$7F   | Set speed (0 = freeze pattern, effects still run) |
| $80–$8F   | Set global volume (lo nybble = $0–$F → SID $D418 bits[3:0]) |
| $90–$9F   | Set filter mode (lo: bit0=LP, bit1=BP, bit2=HP, bit3=cut V3) → SID $D418 bits[7:4] |
| $A0–$AF   | Fine slide down (lo nybble × 4, once per note-row only) |
| $B0–$BF   | Fine slide up (lo nybble × 4, once per note-row only) |
| $C0–$CF   | Note cut at tick = lo nybble (releases gate) |
| $D0–$DF   | Note delay (TODO in source — not implemented in v1.13) |
| $E0–$EF   | Select filter controller instrument (lo nybble = instrument number, 0 = off) |
| $F0–$FF   | Set hard restart ticks (lo nybble; default = 2) |

## Player engine — key behaviours

### Speed / timing
- Default speed = 6 (6 VBI ticks per row)
- Speed counter increments each tick; new row at `speedcounter == speed`
- CIA timing: only 1 SID in corpus (`CiaTno.sid`); VBI is the norm

### Hard restart
- N ticks before new note, clears waveform and AD/SR to 0
- Default = 2 ticks; configurable per-voice with FFx
- Disabled for slide-to-note (effect 3)
- Comment in source: "TODO: shit happens if we have to look ahead into the next pattern"

### Wave table
- $FF in wave table → clear waveform+AD/SR to 0 (sharp attack)
- Gate bit = waveform bit 0 (SID gate is on iff waveform & 1 ≠ 0)
- Note-off = `chn_gateon,x = $FE` (bit 0 clear, bits 7:1 = 1)

### Arpeggio table
- Values < $80: relative (add to note)
- Values >= $80: absolute note = (value & $7F) + 1
  - Track transpose is NOT added to absolute arp values

### Vibrato
- Table-driven (256 bytes, 16 depth levels × 16 positions = quarter-sine)
- Position cycles through 64 states (bits[4:0] = position, bit[5] = add/sub)

### Pulse width modulation
- Initial PW from instrument field $0A (bits [11:4])
- Speed from field $0B (added to PW each tick)
- Limits from field $0C: lower limit = hi nybble (bits [11:8]), upper = lo nybble
- Direction reverses at limits (bidirectional sweep)

### SID write order per frame

```
For each channel (2 → 1 → 0):
    $D402+base = pulse width lo
    $D403+base = pulse width hi
    $D400+base = freq lo
    $D401+base = freq hi
    $D404+base = waveform & gateon  (or 0 if waveform==$FF)
    $D405+base = AD
    $D406+base = SR
$D416 = filter cutoff (8 MSBs)
$D417 = filter input/resonance
$D418 = global volume | filter mode
```

Channel base register offsets: voice 0 = 0, voice 1 = 7, voice 2 = 14.

### Zero-page usage (player)

- `$FB` / `$FC` — `player_trackptr` (16-bit pointer to track)
- `$FD` / `$FE` — `player_patternptr` (16-bit pointer to pattern; alias `player_vibratotemp` when not used)

## Packed song structure (PSID file)

The packer relocates the player to a user-chosen page boundary. Song data
follows immediately after the player code. The player code ends at
`VPLAYER_CODE_END = $B610` (relative to $B000 = $610 = 1552 bytes of code).

PSID entry points (at chosen relocation page `$xx`):
- `$xx00`: Init (A = song number)
- `$xx03`: Play frame
- `$xx06`: Stop / silence SID
- `$xx09`: Quick driver hack (plays until keypress)

The 32-byte song title is embedded at `$xx0D` in the packed file (after the
quick driver hack).

## Filter notes (v1.0x vs v1.1x)

Version 1.0x had simpler filter control. Version 1.1x added:
- Per-instrument filter table indices (fields 13–15 of instrument)
- Effect FEx selects which instrument controls the filter cutoff table
- The filter table advances each tick through the start/end/loop range
- Effect Cxx can override the table at any time

## Source files

| File | Purpose |
|------|---------|
| `vplayer.s` | Relocatable player (packed songs). ~1550 bytes of 6502 code. |
| `eplayer.s` | Editor's player (same logic, not relocatable). |
| `defines.s` | All memory layout constants and instrument field offsets. |
| `tracker.s` | Editor main module (not needed for player RE). |
| `help/help.in` | User documentation (plain text with C64 petscii markers). |
| `freqtab/freqtab.cpp` | Frequency table generator (C++). |
| `vibrato/vibrato.s` | Vibrato table (256 bytes, 16 × 16 quarter-sine). |
| `c64pack/c64pack.cpp` | Packer/relocator (C++ host tool). |
| `c64pack/depacker.s` | Inline depacker (RLE, embedded in packed SID). |
