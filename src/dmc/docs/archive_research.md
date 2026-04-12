---
source_url: https://csdb.dk/group/?id=193, https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html, https://hvmec.altervista.org/blog/?p=700, https://cadaver.github.io/rants/music.html
fetched_via: direct
fetch_date: 2026-04-11
author: multiple sources (Brian/Graffity as original creator; community contributors across CSDb, Lemon64, HVMEC, Chordian, and Cadaver/Lasse Oorni)
content_date: 1990-2025
reliability: secondary
notes: multiple sources — aggregated from archive.org, CSDb, Lemon64, Codebase64, HVMEC, GitHub, Demozoo, and general web searches. No primary source code or annotated disassembly exists publicly. Technical format details are reconstructed from community analysis.
---

# DMC (Demo Music Creator) - Archive Research

Compiled 2026-04-11 from web searches across archive.org, CSDb, Lemon64, Codebase64, HVMEC, GitHub, Demozoo, and other sources.

---

## 1. Overview and History

**DMC** (Demo Music Creator, originally Game Music Creator / GMC) is a C64 SID music editor/player created by **Brian** (Balazs Farkas) of the Hungarian group **Graffity**. It was one of the most popular SID editors in the early 1990s C64 demoscene.

Note: The user prompt mentioned "Vibrants (members: Greckle, Lansen/Vistral)" but research shows DMC was created by Brian/Graffity, NOT by Vibrants. Vibrants was JCH's group (creator of the JCH Editor, a different music editor). This is a common confusion. The predecessor of DMC was GMC (Game Music Creator), also by Brian/Graffity.

### Version History

| Version | Year | Author/Group | CSDb ID | Notes |
|---------|------|-------------|---------|-------|
| GMC V1.0 | 1990 | Brian/Graffity | 7268 | Game Music Creator - predecessor |
| GMC V1.6 | 1990 | Brian/Graffity | 98639 | With beta music |
| DMC V1.2 | 1991 | Brian/Graffity | 2598 | First "Demo Music Creator System" |
| DMC V2.0 | 1991 | Brian/Graffity | 10757 | |
| DMC V3.0 | 1991 | Brian/Graffity | 98640 | |
| DMC V4.0 | Sep 1991 | Brian/Graffity | 2596 | Most widely used version |
| DMC V4.05 | 1992 | Brian/Graffity | 2597 | |
| DMC V4.0 Six Speed | ? | Brian/Graffity | 2606 | 6x speed variant |
| DMC V4.0 Pro | ~1995 | Morbid/Onslaught | - | Modified V4.0 |
| DMC V4.3++ | ? | Tide | - | Modified V4.0 |
| DMC V5.0 | 1993 | Brian/Graffity | 2594 | New player engine |
| DMC V5.0+ | 2002 | CreaMD/DMAgic | 22938 | Extended sector editing |
| DMC V5.1 Package | 1994 | Brian+Iceball/Motiv8 | 2599 | Bugfixed |
| DMC V5.1+ Package | 1994 | Brian+Iceball/Motiv8 | 2600 | Bugfixed, documented by The Syndrom |
| DMC V5.4 | ? | Glover/Samar | 36658 | Improved hard restart |
| DMC V6.0 | ? | Brian/Graffity | - | NEVER RELEASED publicly. Low rastertime (7-8 lines). Complete editor. |
| DMC V7.0 | 1995 | Axl+Brian+Ray/Unreal | 2629 | Based on V4.0 code + extensions |
| DMC 4 Editor 1.0 | Mar 2025 | Logan/Slackers | 250645 | Cross-platform (Windows) re-implementation |
| DMC 4 Editor 1.1 | Mar 2025 | Logan/Slackers | 251057 | Improvements |

Sources:
- [CSDb - Graffity group releases](https://csdb.dk/group/?id=193)
- [CSDb - DMC 4.0](https://csdb.dk/release/?id=2596)
- [CSDb - DMC 7.0](https://csdb.dk/release/?id=2629)
- [CSDb - DMC V5.0](https://csdb.dk/release/?id=2594)
- [CSDb - DMC V5.0+](https://csdb.dk/release/?id=22938)
- [CSDb - DMC V5.1+ Package](https://csdb.dk/release/?id=2600)
- [CSDb - DMC V5.4](https://csdb.dk/release/?id=36658)
- [Lemon64 - DMC 6 thread](https://www.lemon64.com/forum/viewtopic.php?t=24476)
- [CSDb - DMC 4 Editor 1.0](https://csdb.dk/release/?id=250645)
- [Demozoo - DMC tagged productions](https://demozoo.org/productions/tagged/dmc/)

### Key People

- **Brian** (Balazs Farkas) - Graffity, The Imperium Arts. Creator of GMC and all official DMC versions.
- **Iceball** - Motiv 8, Vision. Bugfixed V5.1.
- **The Syndrom** - Crest, The Imperium Arts. Documentation, charset.
- **Axl** and **Ray** - Area Team, Unreal. V7.0 extensions.
- **CreaMD** - DMAgic/C64.SK. V5.0+ extensions.
- **Logan** - Slackers. 2025 cross-platform editor.
- **Richard Bayliss** - The New Dimension. Extensive DMC tutorials and music.

---

## 2. Player Architecture

### Version Split

The DMC family splits into two main player engines:

1. **V4 line** (V4.0, V4.05, V7.0, V7.1) - original player architecture
2. **V5 line** (V5.0, V5.1, V5.4) - different/improved player engine

V7 is based on V4 code with extensions (multi-song, etc.).

### Speed Variants

DMC supports multiple playback speeds:
- **1x** (normal, ~50 Hz PAL)
- **2x** (double speed, ~100 Hz)
- **4x** (quadruple speed) - V2.1+ by Moog/Keen Acid
- **6x** (six speed) - V4.0 variant

### Init/Play Convention

Standard DMC SID files use:
- **Init**: `$1000` (or wherever player is loaded)
- **Play**: `$1003` (init + 3)

The editor itself loads at `$2000` and overwrites memory there.

### Player Size and Performance

From Chordian's C64 Music Editor Comparison table (DMC V5.0):
- Player size: approximately 2000 bytes
- Zero page usage: at least 2 bytes ($F8-$F9)
- CPU time (1x speed): approximately 23-27 rasterlines
- V6.0 (unreleased): only 7-8 rasterlines

Source: [Chordian C64 Music Editor Comparison](http://chordian.net/c64editors.htm)

### Hard Restart Method

DMC uses the **"modern" / "testbit" method** for hard restart (same as JCH Editor):

1. 2+ frames before the next note: ADSR is set to a preset value (e.g., `$0000`, `$0F00`, or `$F800`) and the gate bit is cleared
2. On the first frame of the new note: Attack/Decay and Sustain/Release values are written first, then `$09` is written to the Waveform register (test bit + gate)
3. On the second frame: the instrument's actual waveform value is loaded and the note is heard

This method works reliably on PAL machines only but gives a nice sharp sound.

Source: [Covert Bitops - Music](https://cadaver.github.io/rants/music.html)

### Register Write Order

Based on the hard restart method, DMC writes SID registers in this order per voice per frame:
1. Frequency (lo/hi)
2. Pulse width (if pulse waveform)
3. Waveform / Gate
4. Attack/Decay
5. Sustain/Release
6. Filter settings (shared)

---

## 3. Data Format

### Editor Components

DMC has these main editing sections:
- **Sound Editor** (instruments) - AD, SR, wave pointer, pulse, vibrato, filter, FX
- **Wave Editor** (wave table) - waveform + note data per step
- **Filter Editor** - filter sweep parameters
- **Track Editor** - arrangement of sectors per channel
- **Sector Editor** (patterns) - note/duration/command sequences

### Sector Encoding (Pattern Data)

Each sector contains up to 256 bytes of sequentially encoded events. Byte ranges:

| Range | Meaning |
|-------|---------|
| `$00-$5F` | Note (C-0 through B-7, 96 notes) |
| `$60-$7C` | Duration (`& $1F` = ticks, so 0-28) |
| `$7D` | Continuation (no ADSR reset on next note, "tie") |
| `$7E` | Gate off |
| `$7F` | End of sector (V4) |
| `$80-$9F` | Instrument select (`& $1F` = instrument 0-31) |
| `$A0-$BF` | Glide/portamento command (`$A0` + semitones) |
| `$C0-$DF` | Additional commands |
| `$FF` | End of sector (V5 variant) |

Notes:
- Duration-based patterns: sectors can be any length, no sync is done
- Notes and durations are interleaved in the byte stream
- Maximum 64 sectors (sector numbers $00-$3F)
- Each sector up to 250 rows

### Instrument Table (Sound Data)

32 instruments, 11 bytes each (352 bytes total):

| Offset | Name | Description |
|--------|------|-------------|
| 0 | AD | Attack/Decay (SID register value) |
| 1 | SR | Sustain/Release (SID register value) |
| 2 | wave_ptr | Pointer/index into wave table |
| 3 | pw1 | Pulse width parameter 1 |
| 4 | pw2 | Pulse width parameter 2 |
| 5 | pw3 | Pulse width parameter 3 |
| 6 | pw_limit | Pulse width limit |
| 7 | vib1 | Vibrato parameter 1 |
| 8 | vib2 | Vibrato parameter 2 |
| 9 | filter | Filter control byte |
| 10 | fx | Effect flags byte |

### FX Byte (Instrument Byte 10)

The FX byte controls several flags:

**Low nibble:**
- Bit 0: DRUM EFFECT
- Bit 1: NO FILT RES (no filter reset)
- Bit 2: NO PULS RES (no pulse reset)
- Bit 3: NO GATE FX (skip gate/hard restart)

**High nibble:**
- Bit 4: HOLDING FX
- Bit 5: FILTER FX
- Bit 6: DUAL EFFECT
- Bit 7: CYMBAL FX

Source: [TND64 Music Scene](http://www.tnd64.unikat.sk/music_scene.html) (via web search excerpt)

### Wave Table

Two parallel columns (left and right), indexed by the instrument's `wave_ptr`:

**Left column** (waveform bytes):
- `$00-$8F`: Raw SID waveform byte (written to voice waveform register)
- `$90+`: Loop command - loops back `(byte - $90)` steps
- `$FE`: End marker / special command

**Right column** (note data):
- Contains note offset or arpeggio data
- Accessed in parallel with left column

The player reads left column first. If value < `$90`, it's a waveform byte and the corresponding right column byte is the note offset. If >= `$90`, it's a loop-back command.

### Track Data

Three channels, each with a track of up to 256 entries.

Track byte encoding:
- `$00-$3F`: Sector number (play this sector)
- `$80-$8F`: Transpose down (`& $0F` = semitones)
- `$A0-$AF`: Transpose up (`& $0F` = semitones)
- `$FE`: Loop/repeat
- `$FF`: End of track

### Tune Pointer Table

DMC supports up to 8 tunes (subtunes) per file. The tune pointer table stores interleaved 16-bit addresses: `lo0 hi0 lo1 hi1 lo2 hi2` for 3 channels, accessed with Y register offsets (Y=0,2,4).

### Sector Pointer Table

A pair of tables (lo/hi) containing addresses of each sector's data. The gap between the lo table address and hi table address equals the number of sectors.

### Frequency Table

96 entries (C-0 through B-7), stored as separate hi and lo byte tables (96 bytes each, 192 bytes total). Standard C64 PAL frequency values.

### Memory Layout (V4 typical)

Relative to the frequency table high byte offset:

| Offset from freq_hi | Content |
|---------------------|---------|
| +$0000 | Frequency table (hi, 96 bytes) |
| +$0060 | Frequency table (lo, 96 bytes) |
| +$00C0 | (varies - per-voice variables, speed table) |
| +$0248 | Instrument table (32 x 11 = 352 bytes) |
| after instruments | Wave table, sector pointers, sector data, track data |

The V5 player has a different layout - instrument table location must be found dynamically via LDA abs,Y references from player code.

### Pulse Width

- Range sweeping only (no arbitrary pulse width tables)
- Parameters pw1, pw2, pw3 control the sweep
- pw_limit sets the sweep boundary

### Filter

- Raw sweeping only (no arbitrary filter tables)
- Filter control byte in instrument sets channel routing and mode
- Cutoff frequency swept via player code

### Arpeggio

- Implemented through the wave table (right column = note offsets)
- Hi-frequency mode available for fast arpeggios

### Vibrato

- Two parameters per instrument (vib1, vib2)
- Speed and depth control

---

## 4. Player Identification Signatures (SIDId)

From [cadaver/sidid](https://github.com/cadaver/sidid) `sidid.cfg`:

### DMC (generic)
```
18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

### DMC_V4.x
```
FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0
```

### DMC_V5.x
```
BC ?? ?? B9 ?? ?? C9 90 D0 AND BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```
(Note: the `AND` is likely a notation artifact; the actual pattern continues with additional bytes)

### DMC_V6.x
```
A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4 8D 0B D4 8D 12 D4 8D 11 D4 A9 1F 8D 18 D4 A9 F2 8D 17 D4 60 CE ?? ?? 30 69 20
```

The V6 signature notably shows the init routine writing to all three voice waveform registers ($D404, $D40B, $D412) and the filter registers ($D411 = filter mode/volume, $D418 = filter cutoff hi, $D417 = filter resonance/routing).

`??` = wildcard byte (differs between builds/relocations).

Sources:
- [sidid.cfg on GitHub](https://github.com/cadaver/sidid/blob/master/sidid.cfg)
- [sidid.nfo on GitHub](https://github.com/cadaver/sidid/blob/master/sidid.nfo)

---

## 5. Available Downloads and Archives

### Editor Binaries

| File | Source | Size |
|------|--------|------|
| `DMC-v4.0.prg` | [Zimmers.net](https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html) | 13,878 bytes |
| `dmc4.0.prg` | Zimmers.net | 12,357 bytes |
| `demo_music_creator_v4.0qu.prg` | Zimmers.net | 14,039 bytes |
| `demo_music_creator_v4.0sx.prg` | Zimmers.net | 13,878 bytes |
| `demo_music_creator_v2.1db.prg` | Zimmers.net | 15,175 bytes |
| `demo_music_creator_v2.1qd.prg` | Zimmers.net | 15,143 bytes |
| `DMC_5.0.t64` | [CSDb](https://csdb.dk/release/?id=2594) | - |
| `DMC_V7.zip` | [CSDb](https://csdb.dk/release/?id=2629) | - |
| `dmc7_0.prg` | unreal64.net / CSDb | - |
| `DMC_V5.1 Packages.zip` | CSDb | - |
| `dmcv5plus.zip` | CSDb | - |
| `DMC_v5.4_SAMAR.zip` | CSDb | - |

### Documentation Files

- `dmc_5_docs.txt.gz` - Referenced on HVMEC V5.0 page
- DMC V5.1+ Package includes documentation by The Syndrom
- C64 Turkiye magazine Issue #4 (Feb 2004) contains a DMC 4.0 tutorial (in Turkish)

Sources:
- [HVMEC - DMC V5.0](https://hvmec.altervista.org/blog/?p=700)
- [HVMEC - DMC V4.0 pro](https://hvmec.altervista.org/blog/?p=570)
- [HVMEC - DMC V2.1+](https://hvmec.altervista.org/blog/?p=504)
- [HVMEC - DMC V4.0 2x](https://hvmec.altervista.org/blog/?p=541)
- [HVMEC - DMC V4.3++](http://hvmec.altervista.org/blog/?p=630)

---

## 6. Technical Details from Community Sources

### Duration-Based Patterns (from Lemon64 DMC V4 thread)

DMC uses "duration based patterns" that "can be any length, no syncing is done at all." This means sectors on different channels are NOT synchronized at sector boundaries - each channel independently follows its own timing. This is different from tracker-style editors where patterns have fixed lengths.

Source: [Lemon64 - DMC V4 is back](https://www.lemon64.com/forum/viewtopic.php?p=1056030)

### DMC V6.0 (Unreleased)

From Brian/Graffity's own statement on Lemon64:
- "DMC 6.0 does exist, though it has not been released to the public"
- Low rastertime player: only 7-8 CPU lines
- Has a complete editor
- Has limitations (unspecified) to conserve processing resources
- Supports pulse and filter effects, limited to specific channels

Source: [Lemon64 - DMC 6 thread](https://www.lemon64.com/forum/viewtopic.php?t=24476)

### DMC V7.0 Features

From Unreal group commentary:
- 1-5 multiple songs (subtunes)
- Multi-channel play
- Bigger editor improvements
- Play from any line or note
- Sector length visible
- Cassette recorder supported

Source: [CSDb - DMC 7.0](https://csdb.dk/release/?id=2629)

### Idle Channel Behavior

A Lemon64 user reported that even when a DMC song only uses 2 channels, "the DMC player is not actually leaving the channel completely free. Maybe it doesn't use it, but it is resetting its state every time the IRQ is called." This means the player touches all 3 voices every frame, even unused ones.

Source: [Lemon64 - DMC 4.0 Player idle channel](https://www.lemon64.com/forum/viewtopic.php?t=48548)

### Comparison to Other Editors

From Chordian's comparison table (DMC V5.0 entry):
- PAL only (no NTSC support)
- No source code included in releases
- Proprietary file format
- 1 SID only (no stereo)
- 6 or 8 visible channels
- 1x speed only (V5.0 base)
- No digi/sample support
- No vibrato support (in V5.0 - note: V4 does have vibrato)
- No hard restart (uncertain, marked "No?" in table)
- No transpose, no repeat, loop only
- No volume control, no tempo specification
- 32 instruments maximum
- No sub-tune support (in V5.0 - V7 adds this)

Source: [Chordian C64 Editors comparison](http://chordian.net/c64editors.htm)

### Packer Issues

DMC V5.4's packer was reported as buggy: "able pack only one of them" and packed music exhibits "false notes". V5.1 was considered more reliable.

Source: [CSDb - DMC V5.4](https://csdb.dk/release/?id=36658)

---

## 7. Related Tools

- **All Round Relocator** / **I-Relocator** - Used to relocate DMC music to different addresses
- **Dutch USA Team Music Assembler** - Can convert DMC to other formats
- **DMC V5 PACKER** - Compresses V5 music data
- **DMC V5.0 SCANNER** - Scans/analyzes V5 music data
- **Restore 64** (https://restore64.dev/) - Browser-based C64 PRG disassembler that detects 787 player signatures including DMC
- **SIDId** (https://github.com/cadaver/sidid) - Player identification scanner with DMC signatures
- **SID Toolbox** (https://www.doussis.com/sidtoolbox/) - Edit/create .sid files

---

## 8. HVSC Statistics

DMC is one of the most represented player engines in HVSC. The project's existing `sidid.py` tool identifies DMC SIDs, and the `dmc_parser.py` already handles the core data extraction. The HVSC collection contains approximately 10,738 DMC SIDs.

---

## 9. What is NOT Documented Online

Despite extensive searching, the following technical details are NOT available in any publicly indexed web resource:

1. **Complete annotated disassembly** of any DMC player version - no public source code exists
2. **Exact pulse width algorithm** - only "range sweeping" mentioned, no byte-level specification of pw1/pw2/pw3 interaction
3. **Exact vibrato algorithm** - vib1/vib2 parameter interaction not documented
4. **Filter sweep algorithm** - raw sweeping mentioned but no formula
5. **V5 vs V4 player differences** at the code level
6. **Exact wave table processing loop** - only general description available
7. **Per-voice variable layout** in player zero page / RAM
8. **Speed table format** for multi-speed variants
9. **DMC V6 internals** - completely undocumented (never released)

These would need to be reverse-engineered from the actual player binaries, which is what `src/dmc_parser.py` and `src/sidxray/` tools are designed to do.

---

## 10. Key URLs for Further Research

- CSDb DMC releases: https://csdb.dk/search/?seinession=all&search=demo+music+creator&type=release
- HVMEC catalog: https://hvmec.altervista.org/blog/?p=570
- TND64 Music Scene: http://tnd64.unikat.sk/music_scene.html (SSL cert issues, may need HTTP)
- Chordian editor comparison: http://chordian.net/c64editors.htm
- SIDId signatures: https://github.com/cadaver/sidid/blob/master/sidid.cfg
- Zimmers.net editors: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html
- Covert Bitops music rant: https://cadaver.github.io/rants/music.html
- Codebase64 SID programming: https://codebase64.org/doku.php?id=base:sid_programming
- Pouet DMC 4.0: https://www.pouet.net/prod.php?which=13452
