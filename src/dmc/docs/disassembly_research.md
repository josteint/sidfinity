---
source_url: https://github.com/cadaver/sidid/blob/master/sidid.cfg, https://github.com/TCRF/vgmid/blob/master/c64.nfo, https://chordian.net/c64editors.htm
fetched_via: direct
fetch_date: 2026-04-11
author: multiple sources (Lasse Oorni/Cadaver for sidid signatures; Jens-Christian Huus/Chordian for editor comparison; Brian/Graffity as original creator in forum posts; Logan/Slackers for 2025 editor)
content_date: 1991-2025
reliability: primary
notes: multiple sources — sidid.cfg byte-pattern signatures are primary source material (6502 disassembly of actual player code). TCRF/vgmid metadata, Chordian comparison table, CSDb releases, HVMEC, Lemon64 forums, and Zimmers.net binaries are secondary. No annotated public disassembly of any DMC version exists. The 6502 signature decoding sections constitute original primary analysis from the player binary bytes.
---

# DMC (Demo Music Creator) Disassembly & Analysis Research

Compiled 2026-04-11 from web searches across DeepSID, CSDb, HVSC tooling,
GitHub projects, Lemon64 forums, and demoscene archives.

---

## 1. Background

DMC (Demo Music Creator) was created by Balazs Farkas (Brian/Graffity) for
the Commodore 64. Development spanned roughly 1989-1995 across several
versions: V2.1, V4.0, V4.3++, V5.0, V5.1, V5.4, V6.0, and V7.0.

The version lineage is not strictly sequential:
- **V4.x** is the original widely-used branch (1991). V7.0 (Unreal, 1995)
  is actually a heavily modified V4.0 -- not a successor to V5/V6.
- **V5.x** (1993) is a separate branch with lower raster time, different
  player architecture. V5.1+ (Graffity + Motiv 8, 1994) is a bugfix.
  V5.4 (Samar/Glover) is a community variant.
- **V6.0** exists but was never publicly released. Brian confirmed it in a
  2013 Lemon64 post. It uses 7-8 raster lines (very low CPU). It has a
  complete editor but limited pulse/filter to specific channels.

**Key insight**: DMC V4.x and V5.x have **different player code and
different binary layouts**. V4.x and V7.x share the same player core.

## 2. SIDId / Player-ID Signatures

### From cadaver/sidid (sidid.cfg)
https://github.com/cadaver/sidid

```
DMC
18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60 END

(DMC_V4.x)
FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0 END

(DMC_V5.x)
BC ?? ?? B9 ?? ?? C9 90 D0 AND BD ?? ?? 3D ?? ?? 99 ?? ?? 60 END

DMC_V6.x
A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4 8D 0B D4 8D 12 D4 8D 11 D4 A9 1F 8D 18 D4 A9 F2 8D 17 D4 60 CE ?? ?? 30 69 20 END
```

### From WilfredC64/player-id (sidid.cfg)
https://github.com/WilfredC64/player-id

Same signatures as cadaver/sidid (shared config format). The player-id tool
extends sidid with V2 config format support but uses the same DMC entries.

### From TCRF/vgmid (c64.nfo)
https://github.com/TCRF/vgmid/blob/master/c64.nfo

```
DMC           - Demo Music Creator System (DMC), Balazs Farkas (Brian), 1991
                http://csdb.dk/release/?id=2598
DMC_V4.x      - Demo Music Creator System (DMC), Balazs Farkas (Brian), 1991
                http://csdb.dk/release/?id=2596
DMC_V5.x      - Demo Music Creator System (DMC), Balazs Farkas (Brian), 1993
                http://csdb.dk/release/?id=2594
DMC_V6.x      - Demo Music Creator System (DMC), Balazs Farkas (Brian)
```

### Signature analysis (6502 interpretation)

**DMC (base signature, likely V2.x/early V4):**
```
18        CLC
7D ?? ??  ADC $????,X     ; add frequency component
99 ?? ??  STA $????,Y     ; store result
BD ?? ??  LDA $????,X     ; load next component
7D ?? ??  ADC $????,X     ; add carry
?? ?? ??  ...
BD ?? ??  LDA $????,X     ; load wave/mask data
99 ?? ??  STA $????,Y     ; store
BD ?? ??  LDA $????,X     ; load more data
99 ?? ??  STA $????,Y     ; store
BD ?? ??  LDA $????,X     ; load
3D ?? ??  AND $????,X     ; mask with voice enable
99 ?? ??  STA $????,Y     ; store
60        RTS
```

**DMC V4.x:**
```
FE ?? ??  INC $????,X     ; increment counter/pointer
BD ?? ??  LDA $????,X     ; load voice data
18        CLC
7D ?? ??  ADC $????,X     ; add offset
9D ?? ??  STA $????,X     ; store result
BD ?? ??  LDA $????,X     ; load high byte
69 00     ADC #$00        ; add carry
2C ?? ??  BIT $????       ; test flags (skip next?)
BD ?? ??  LDA $????,X     ; load
29 01     AND #$01        ; mask bit 0
D0        BNE ...         ; branch if set
```

**DMC V5.x:**
```
BC ?? ??  LDY $????,X     ; load Y-index from voice table
B9 ?? ??  LDA $????,Y     ; load data via Y (instrument table)
C9 90     CMP #$90        ; compare with $90 threshold
D0        BNE ...         ; branch if not command
...AND...                 ; (multi-pattern signature)
BD ?? ??  LDA $????,X     ; load
3D ?? ??  AND $????,X     ; mask
99 ?? ??  STA $????,Y     ; store to SID
60        RTS
```

**DMC V6.x (init routine signature):**
```
A9 02     LDA #$02        ; voice count (2, loops to 0)
9D ?? ??  STA $????,X
A9 00     LDA #$00
9D ?? ??  STA $????,X
CA        DEX
10 F3     BPL loop        ; loop 3 voices
8D ?? ??  STA $????       ; store zero
A9 08     LDA #$08        ; test bit waveform
8D 04 D4  STA $D404       ; voice 1 control
8D 0B D4  STA $D40B       ; voice 2 control
8D 12 D4  STA $D412       ; voice 3 control
8D 11 D4  STA $D411       ; voice 3 freq hi (?)
A9 1F     LDA #$1F        ; filter cutoff/mode
8D 18 D4  STA $D418       ; volume/filter mode
A9 F2     LDA #$F2
8D 17 D4  STA $D417       ; filter cutoff hi
60        RTS
```

## 3. Player Addresses and Structure

### Standard addresses
- **Init**: `$1000` (JSR $1000 with A = subtune number)
- **Play**: `$1003` (JSR $1003 from IRQ, 1x speed)
- **Play (multi)**: `$1006` (for multi-speed, some versions)

The packed/relocated DMC SID always loads at $1000 with init at $1000 and
play at $1003. The editor workspace uses different addresses but the packer
relocates everything.

### Player timing
- **V4.x/V7.x**: ~23-27 raster lines (measured by Chordian comparison table)
- **V5.x**: Lower raster time than V4 (exact measurement not found)
- **V6.x**: 7-8 raster lines (confirmed by Brian)
- **Speed**: V4/V5 support 1x speed only. V2.1 variants exist for 2x and 4x.

### Subtunes
Up to 8 subtunes per file. Init routine uses accumulator value to select tune.

## 4. Data Layout (from dmc_parser.py + web research)

### Frequency table
- 96 entries (C-0 through B-7), split hi/lo
- Located in player code area, standard SID frequency values
- Can be hi_lo or lo_hi order depending on version

### Instrument table
- 32 instruments, 11 bytes each (352 bytes total)
- Located after frequency table
- V4.x: at freq_hi + $0248 (fixed offset)
- V5.x: dynamic location, found via LDA $XXXX,Y references in player code

### Instrument byte layout (11 bytes per instrument)
```
Offset  Field       Description
0       AD          Attack/Decay ($D405/$D40C/$D413)
1       SR          Sustain/Release ($D406/$D40D/$D414)
2       wave_ptr    Index into wave table
3       pw1         Pulse width byte 1 (initial/low)
4       pw2         Pulse width byte 2 (speed/direction)
5       pw3         Pulse width byte 3 (limit/range)
6       pw_limit    Pulse width limit
7       vib1        Vibrato parameter 1 (depth/speed)
8       vib2        Vibrato parameter 2 (delay/range)
9       filter      Filter parameter
10      fx          Effects flags
```

### Sector encoding (music data)
```
$00-$5F   Note (C-0 through B-7, 96 notes)
$60-$7C   Duration (value AND $1F = ticks)
$7D       Continuation (no ADSR reset on next note, legato)
$7E       Gate off (release current note)
$7F       End of sector (V4.x) / also end marker
$80-$9F   Instrument select (value AND $1F = instrument 0-31)
$A0-$BF   Glide command ($A0 + semitones target)
$C0-$DF   Additional commands (version-dependent)
$FF       End of sector (V5.x)
```

### Sector pointer table
- Split lo/hi byte arrays
- Up to 64 sectors ($00-$3F)
- Each pointer references the start of sector data in memory

### Track table
- 3 tracks (one per SID voice)
- Each track has up to 256 entries ($00-$FF)
- Each entry references a sector number or special command
- Track commands include:
  - Sector number (play this sector)
  - Transpose (+/- semitones for following sectors)
  - End marker (loop or stop)

## 5. DeepSID

### Source
https://github.com/Chordian/deepsid

DeepSID (by Jens-Christian Huus / Chordian) is a PHP/MySQL web application
that uses the HVSC collection. It displays player type information per SID
file. Player identification is done via sidid/player-id integration, not
through custom DMC analysis. DeepSID does not contain DMC-specific parsing
or format documentation beyond what sidid provides.

### C64 Editors Comparison Table
https://chordian.net/c64editors.htm

DMC 5.0 specifications from the comparison table:
- **Instruments/Sounds**: 32
- **Channels**: 3
- **Speed**: 1x only
- **Sub-tunes**: 8
- **Player size**: ~2000 bytes
- **Zero page usage**: 2 bytes ($F8-$F9)
- **CPU time (1x)**: ~23-27 raster lines
- **Platform**: PAL only
- **Arpeggio**: Wave table with Hi-freq mode
- **Pulsating**: Range sweeping only
- **Filtering**: Raw sweeping only
- **Vibrato**: No
- **Hard restart**: No
- **Pattern system**: Single-channel patterns, 63 blocks, up to 32 rows each

## 6. DMC 4 Editor (2025, by Logan/Slackers)

### CSDb entries
- v1.0: https://csdb.dk/release/?id=250645 (released 2025-03-03)
- v1.1: https://csdb.dk/release/?id=251057 (released 2025-03-15)

### Description
A cross-platform (Windows) GUI editor for DMC V4.0 format music. Written
by Logan (Slackers), with original code credit to Brian (Graffity).

### Features (v1.1)
- Traditional DMC V4.0 editor: sound (instruments), wave, filter, track, sequence
- Import PRG/SID files from DMC V4.0, V7.0A, V7.0B
- Export PRG with music relocator
- Sector duration display for synchronization
- Audible sector editing
- Octave adjustment controls
- Configurable font sizes
- Sound name assignment
- Track playback from any position

### Source code
**Not found on GitHub.** Windows-only binaries (64-bit and 32-bit) are
distributed via CSDb. No public source repository was identified.

### Technical significance
The import capability (reads DMC V4.0/V7.x SIDs) implies Logan reverse-
engineered the complete format. However, this knowledge is embedded in the
closed-source Windows binary, not in public documentation.

## 7. HVMEC (High Voltage Music Engine Collection)

https://hvmec.altervista.org/blog/

HVMEC catalogs C64 music editors with screenshots and download links but
contains NO technical documentation about player internals. Pages exist for:
- DMC v2.1+ [4x]: https://hvmec.altervista.org/blog/?p=504
- DMC v4.0 [2x]: https://hvmec.altervista.org/blog/?p=541
- DMC v4.0 pro: https://hvmec.altervista.org/blog/?p=570
- DMC v4.3++: https://hvmec.altervista.org/blog/?p=630
- DMC v5.0: https://hvmec.altervista.org/blog/?p=700

Each page provides: title, version, year, group, keyboard shortcuts, and
a download link for the C64 PRG. Source code is listed as "Not Available"
for all versions.

## 8. CSDb Releases (Key DMC Entries)

| Release | CSDb ID | Year | Notes |
|---------|---------|------|-------|
| DMC V4.0 | [2596](https://csdb.dk/release/?id=2596) | 1991 | Original by Graffity |
| DMC V5.0 | [2594](https://csdb.dk/release/?id=2594) | 1993 | By Graffity |
| DMC V5.1+ | [2600](https://csdb.dk/release/?id=2600) | 1994 | Bugfix by Graffity + Motiv 8 |
| DMC V5.0+ | [22938](https://csdb.dk/release/?id=22938) | 2002 | Enhanced by CreaMD/DMAgic |
| DMC V5.4 | [36658](https://csdb.dk/release/?id=36658) | ~2003 | By Glover/Samar; packer issues reported |
| DMC Relocator | [10758](https://csdb.dk/release/?id=10758) | 1991 | By Graffity |
| DMC V4.0 Relocator V2.0 | [4386](https://csdb.dk/release/?id=4386) | 1993 | By Warriors of the Wasteland |
| DMC V7.0 | [2629](https://csdb.dk/release/?id=2629) | 1995 | By Unreal (Axl, Brian, Ray); enhanced V4.0 |
| DMC 4 Editor 1.0 | [250645](https://csdb.dk/release/?id=250645) | 2025 | Cross-platform by Logan |
| DMC 4 Editor 1.1 | [251057](https://csdb.dk/release/?id=251057) | 2025 | Updated version |

## 9. Zimmers.net Archive

https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/

Binary PRG files available (no source):
- `demo_music_creator_v2.1db.prg` (15,175 bytes)
- `demo_music_creator_v2.1qd.prg` (15,143 bytes)
- `demo_music_creator_v4.0qu.prg` (14,039 bytes)
- `demo_music_creator_v4.0sx.prg` (13,878 bytes)
- `DMC-v4.0.prg` (13,878 bytes)
- `dmc4.0.prg` (12,357 bytes)

## 10. SID-Wizard Relationship

SID-Wizard (by Hermit) was influenced by DMC's design:
- Uses DMC/GMC piano-keyboard layout option
- "Merged lots of style from both DMC and JCH" (SID Preservation)
- Does NOT import/export DMC format directly
- SWMconvert and sng2swm handle SWM/SNG formats, not DMC

Source: https://sourceforge.net/projects/sid-wizard/

## 11. Other GitHub Projects Examined

### realdmx/c64_6581_sid_players
https://github.com/realdmx/c64_6581_sid_players

Contains reverse-engineered player source code for various composers (Rob
Hubbard, Martin Galway, Fred Gray, etc.) but does NOT include DMC player
disassembly.

### anarkiwi/desidulate
https://github.com/anarkiwi/desidulate

Analyzes SID register dumps from VICE. No DMC-specific support.

### M64GitHub/zig64
https://github.com/M64GitHub/zig64

Cycle-accurate 6510 emulator in Zig with SID register tracing. Useful for
analyzing DMC player behavior but contains no DMC-specific code.

### Compyx/hvsclib
https://github.com/Compyx/hvsclib

Library for HVSC file handling. No player-specific analysis.

## 12. DMC V4.0 Manual (Partial)

Source: https://silo.tips/download/demo-music-creator-40 (C64 Turkiye magazine)

### Sectors
- 64 sectors available ($00-$3F)
- Each sector has 256 rows for notes and commands
- Sectors are the fundamental unit of composition (not patterns/rows)
- Duration-based: each note plays for its set duration, no fixed row tick

### Tracks
- 3 tracks (one per voice)
- 256 entries per track ($00-$FF)
- Track entries reference sector numbers plus special commands

### Sound editor
- ADSR envelope
- Filter assignments
- Waveform selection
- Vibrato/modulation

### Special commands in sectors
- Duration (C=+D): sets note length for subsequent entries
- Sound (C=+S): selects instrument ($00-$1F)
- Glide (C=+G): pitch slide between notes
- Gate off: terminates sustained notes

### Keyboard note mapping
QWERTY layout maps to chromatic scale across multiple octaves.

## 13. Key Gaps (What We DON'T Have)

1. **No annotated disassembly exists publicly** for any DMC version. The
   player binary has been distributed since 1991 but no one has published
   a complete commented disassembly.

2. **No binary format specification** exists beyond what can be inferred from
   the SIDId signatures and our own dmc_parser.py reverse engineering.

3. **Wave table format** is not documented. We know instruments reference a
   wave_ptr (byte 2 of the 11-byte instrument), but the wave table structure
   (location, entry size, effect encoding) is undocumented publicly.

4. **Filter table format** is similarly undocumented.

5. **Track command encoding** (beyond sector references) is not documented.
   Track entries include transpose and end/loop markers but the exact byte
   encoding is not published.

6. **V4 vs V5 differences** at the binary level beyond what SIDId signatures
   show are not documented.

7. **Logan's DMC 4 Editor** likely contains the most complete modern
   understanding of the format, but is closed-source Windows-only.

## 14. Recommended Next Steps for SIDfinity

1. **Disassemble a DMC V4 SID directly.** Pick a simple DMC SID from HVSC
   (short, single subtune), load into a 6502 disassembler, annotate the
   player routine starting at $1000/$1003. This will reveal:
   - Exact wave table location and entry format
   - Filter table location and format
   - Track command encoding
   - Per-voice state variable layout

2. **Use sidxray tools.** The existing sidxray methodology (trace.py,
   analyze.py, xray.py) can trace DMC player execution to discover:
   - Data table access patterns
   - Tempo/frame rate
   - SID register write sequences

3. **Compare V4 and V5 binaries.** Disassemble one of each to document the
   structural differences.

4. **Contact Logan (DMC 4 Editor author).** His import code for DMC V4/V7
   SIDs implies he has the complete format documented. He may be willing
   to share format documentation even if not the editor source.

5. **Check the DMC V5.1+ package.** The CSDb entry (id=2600) includes
   documentation by The Syndrom. This might contain more technical detail
   than the V4.0 manual.

## Sources

- [DeepSID](https://deepsid.chordian.net/)
- [DeepSID GitHub](https://github.com/Chordian/deepsid)
- [Chordian C64 Editors Comparison](https://chordian.net/c64editors.htm)
- [Chordian Blog: Comparison of C64 Music Editors](https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/)
- [cadaver/sidid GitHub](https://github.com/cadaver/sidid)
- [cadaver/sidid config](https://github.com/cadaver/sidid/blob/master/sidid.cfg)
- [WilfredC64/player-id GitHub](https://github.com/WilfredC64/player-id)
- [TCRF/vgmid c64.nfo](https://github.com/TCRF/vgmid/blob/master/c64.nfo)
- [CSDb: DMC 4.0 by Graffity](https://csdb.dk/release/?id=2596)
- [CSDb: DMC V5.0](https://csdb.dk/release/?id=2594)
- [CSDb: DMC V5.1+ Package](https://csdb.dk/release/?id=2600)
- [CSDb: DMC V5.0+ by CreaMD](https://csdb.dk/release/?id=22938)
- [CSDb: DMC V5.4 by Samar](https://csdb.dk/release/?id=36658)
- [CSDb: DMC Relocator](https://csdb.dk/release/?id=10758)
- [CSDb: DMC V4.0 Relocator V2.0](https://csdb.dk/release/?id=4386)
- [CSDb: DMC 7.0 by Unreal](https://csdb.dk/release/?id=2629)
- [CSDb: DMC 4 Editor 1.0 by Logan](https://csdb.dk/release/?id=250645)
- [CSDb: DMC 4 Editor 1.1 by Logan](https://csdb.dk/release/?id=251057)
- [HVMEC: DMC v2.1+](https://hvmec.altervista.org/blog/?p=504)
- [HVMEC: DMC v4.0 2x](https://hvmec.altervista.org/blog/?p=541)
- [HVMEC: DMC v4.0 pro](https://hvmec.altervista.org/blog/?p=570)
- [HVMEC: DMC v4.3++](https://hvmec.altervista.org/blog/?p=630)
- [HVMEC: DMC v5.0](https://hvmec.altervista.org/blog/?p=700)
- [SID Preservation: Editors](https://sidpreservation.6581.org/sid-editors/)
- [Lemon64: DMC 6 thread](https://www.lemon64.com/forum/viewtopic.php?t=24476)
- [Lemon64: DMC V4 is back in 2025](https://www.lemon64.com/forum/viewtopic.php?p=1055941)
- [Lemon64: DMC 4.0 Player info](https://www.lemon64.com/forum/viewtopic.php?t=48548)
- [DMC 4.0 Manual (C64 Turkiye)](https://silo.tips/download/demo-music-creator-40)
- [Zimmers.net editors archive](https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html)
- [realdmx/c64_6581_sid_players GitHub](https://github.com/realdmx/c64_6581_sid_players)
- [anarkiwi/desidulate GitHub](https://github.com/anarkiwi/desidulate)
- [anarkiwi/sid-wizard GitHub](https://github.com/anarkiwi/sid-wizard)
- [SID-Wizard SourceForge](https://sourceforge.net/projects/sid-wizard/)
