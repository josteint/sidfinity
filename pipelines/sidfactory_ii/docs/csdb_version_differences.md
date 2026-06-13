---
source_url: https://github.com/Chordian/sidfactory2 + https://csdb.dk + https://blog.chordian.net/sf2/
fetched_via: direct
fetch_date: 2026-06-13
author: JCH (Jens-Christian Huus), Laxity (Thomas Egeskov Petersen), Youth (Michel de Bree)
content_date: 2020-2026
reliability: primary (source code) + secondary (CSDb pages)
---

# SID Factory II — Version Differences and Technical Format Analysis

## .sf2 File Format: Overview

An `.sf2` file is a **C64 PRG-format binary** containing:
1. The 6502 driver code (one of the drivers listed below)
2. Music data (instruments, patterns/sequences, order lists, tables) interleaved with driver
3. An embedded metadata header block at a driver-defined address (validated by magic `0x1337`)
4. Auxiliary data (editor preferences, play markers, hardware settings, song names)

The file is **not** packed on disk — it is the raw C64 memory image. Saved via F11 / Ctrl+S. Cannot load packed tunes or .sid files (unpack first). Can be relocated to different C64 memory addresses using the built-in relocator.

### PRG Layout

- Loads into a 64 KB C64 memory space (up to 0x10000 bytes)
- Load address stored in PRG header (2 bytes, little-endian)
- Music data ends are computed via `DriverUtils::GetEndOfMusicDataAddress()`
- IRQ vectors inserted at save time for VICE direct-play (SYS 4093)
- Auxiliary data pointer at address `0x0ffb` (a fixed location used as an AUX data anchor)

### Embedded Driver Metadata Block (magic `0x1337`)

Every driver PRG ships with an embedded metadata block that the editor reads to know the layout of all tables. This is NOT the music data — it is a descriptor for the editor.

Block format (sequential, terminated by `0xFF`):

```
[BlockID: 1 byte] [BlockSize: 1 byte] [Data: BlockSize bytes]
...repeat...
[0xFF]  ← end marker
```

Block IDs:
| ID | Name | Key Fields |
|---|---|---|
| 1 | Descriptor | type, size, name string, code address/size, version (major.minor.revision) |
| 2 | DriverCommon | init/stop/update routine addresses, SID channel offset, tick counter addr, order list index addr, sequence index addr, note/instrument/command buffer addrs, tempo/sync addrs |
| 3 | DriverTables | array of TableDefinition (type, ID, name, address, columns, rows, layout orientation, insert/delete support, color rules) |
| 4 | DriverInstrumentDescriptor | vector of cell descriptions for instrument rows |
| 5 | MusicData | track count, sequence count, orderlist pointer addrs, sequence pointer addrs, sizes |
| 6 | TableColorRules | evaluation criteria + color values per cell |
| 7 | TableInsertDeleteRules | what to modify in other tables on insert/delete |
| 8 | TableActionRules | actions triggered by cell evaluation |
| 9 | DriverInstrumentDataDescriptor | pointer mapping for instrument data retrieval |

Required blocks for a valid driver: 1 (Descriptor), 2 (DriverCommon), 3 (DriverTables), 4 (DriverInstrumentDescriptor), 5 (MusicData). A driver is "partially valid" if some optional blocks are missing.

### Auxiliary Data Block

Stored appended to the PRG (at address pointed to by `0x0ffb`). Six categories:

| Type | Contents |
|---|---|
| EditingPreferences | UI/editor settings |
| HardwarePreferences | SID model (6581/8580), PAL/NTSC, filter curves |
| PlayMarkers | Bookmarks for playback positions |
| TableText | Per-row labels for instruments/commands |
| Songs | Multi-song metadata (as of build 20220914) |

Each aux block has a `FileHeader`: DataType (enum), DataVersion, DataSize.

---

## Driver Differences

### Driver 11 (Primary/Standard) — Full-featured

The editor's DEFAULT driver. Highest feature count. Used by most SF2 compositions.

**Instrument row** (6 bytes):
| Byte | Field |
|---|---|
| 0 | AD: Attack(hi nibble) / Decay(lo nibble) |
| 1 | SR: Sustain(hi nibble) / Release(lo nibble) |
| 2 | Control: bit7=hard restart enable, bit4=test bit; lo nibble → HR table ptr |
| 3 | Pulse Table Index (start position) |
| 4 | Filter Table Index (start position; bit added in 11.03 for filter enable flag) |
| 5 | Wave Table Index (start position) |

**Hard Restart (HR) Table:** ADSR values applied for 2 ticks before note trigger. Prevents ADSR sticking from previous notes.

**Wave Table** (2 bytes per row):
- Byte 1: Waveform value ($11=triangle, $21=sawtooth, $41=pulse, $81=noise, combos).  
  $7F = loop marker (byte 2 = target line).
- Byte 2: $00–$7F = semitone offset from played note.  
  $80–$DF = static/absolute frequency (bypasses note transposition).

**Pulse Table** (2 bytes per row): 12-bit PWM control over time.

**Filter Table** (2 bytes per row): Cutoff, resonance, filter mode, voice routing mask — all variable over time.

**Arpeggio Table:** Separate table for chords only (distinct from wave table arpeggios). 12-bit pulse and filter.

**Order List** (3 independent voices): 2-byte entries:
- Byte 1: transpose ($A0 = no transpose; range -32 to +31 semitones around $A0)
- Byte 2: sequence number (0–127)

**Sequences** (shared pool, up to 128):
- Rows contain: note, instrument, command
- Note: 8 octaves; `+++` = gate on; `---` = gate off
- Instrument: $00–$FF (hex); `**` = tie (hold previous)
- Command: single byte from command table
- Terminator: $FF (end of sequence), $7E (loop marker)
- Max 1024 rows (packed to ≤256 bytes in memory)

**Tempo Table:** Countdown values per row. $7F = loop. Enables swing/variable tempo.

**Commands available (driver 11.02+):**
- Pulse program index change
- Tempo change
- Main volume ($D418) control
- Note delay 0–F ticks (added 11.04)
- Filter enable toggle (added 11.03 as instrument flag, separately as command)
- Pulse reset flag (added 11.05)

### Driver 12 — Minimal

"Extremely simple, basic effects only." Based on build 20200718 test SID ("The Barber").
Fewer table types, reduced instrument format.

### Driver 13 — Rob Hubbard Emulation

Emulates the sound characteristics of Rob Hubbard's classic C64 driver (see test SID: "Driver 13 Test" in early builds). This is an emulation within the SF2 framework, not a binary-compatible replication of Hubbard's engine.

### Driver 14 — Short Gate-Off

Variant of driver 11 with shorter gate-off timing. Used for percussion-heavy styles.

### Driver 15 — Tiny Mark I

Minimal footprint driver. Reduced feature set, small code size.

### Driver 16 — Tiny Mark II

Even smaller than driver 15. No commands column. Minimal tables.

### Driver NP20 — JCH NewPlayer 20 Compatibility

`sf2driver_np20_00.prg` — Special driver for importing/playing tunes originally made in JCH NewPlayer version 20.Gx format. See JCH lineage section below.

---

## JCH NewPlayer Format — Conversion Details

The JCH converter (`source/runtime/editor/converters/jch/converter_jch.cpp`) reveals the NP20 binary format:

**Identification:** String "20.G" at address `0x0fee`  
**Load address:** `0x0f00`  
**Max size:** under 64 KB

**Fixed-address pointer table (NP20 format):**
| Address | Points to |
|---|---|
| `0x0fa6` | Speed/tempo setting |
| `0x0fb8`/`0x0fba` | (additional pointer, per JCH20g4Info struct) |
| `0x0fbc` | Wave table |
| `0x0fbe`/`0x0fc0` | Filter table |
| `0x0fc2` | Pulse table |
| `0x0fc4` | Instruments table |
| `0x0fc6` | Order list V1 |
| `0x0fc8` | Order list V2 |
| `0x0fca` | Order list V3 |
| `0x0fcc` | Sequence vector low bytes |
| `0x0fce` | Sequence vector high bytes |
| `0x0fd0` | Commands table |

**Data layout:** Row-major in NP20; converter transposes to column-major for SF2.  
**Order list entries:** Pairs of (transposition offset, sequence index).  
**Sequences:** Alternating command and note bytes, terminated by `0x7f`.  
  Commands: values ≥ `0xC0` for special functions; lower values = instrument index.

**Crash fix note:** Build 20221007 fixed a crash specifically when converting NP20 tunes  
(CSDb #224223, Youth comment). Loop point beyond position 128 was also fixed in same build.

---

## GoatTracker (.sng) Conversion

The GT converter (`converters/gt/converter_gt.cpp`) identifies files by magic strings:
- `"GTS3"`, `"GTS4"`, or `"GTS5"` at file header

On import, it loads `sf2driver11_05.prg` as the target driver and converts via `SourceSng`.

---

## Multi-Song Support (build 20220914+)

Before build 20220914: one song per .sf2 file.  
After: multiple songs can share sequences within a single .sf2. The AuxilaryData `Songs` block carries per-song metadata. The order list and sequence pool are shared.

---

## File Save Protocol

From `editor_facility.cpp`:
1. Retrieve music data end address via `DriverUtils::GetEndOfMusicDataAddress()`
2. Extract memory range → `C64File` object
3. Insert IRQ vectors for VICE direct-play
4. Insert auxiliary data pointer at `0x0ffb`
5. Write PRG to disk

Loading:
1. Read file (max 65,536 bytes)
2. Parse into `C64File`
3. Parse `DriverInfo` (validate `0x1337` magic)
4. `IsFileSF2()`: true if `IsValid()` or `IsPartiallyValid()`
5. Copy to 64 KB `CPUMemory`
6. Set init/stop/update execution vectors

---

## Platform/Build Infrastructure Notes

- C/C++ project; C 68.2%, C++ 31.1%, Objective-C 0.3%
- Depends on: reSID-FP, SDL2 (2.32.10 for Win/macOS)
- Branches: master = stable; features in separate branches before merge
- Merge requirements: changelog update in README.md, config.ini documentation, key mapping notes
- Nightly builds from master (untested); official releases announced manually with updated user manuals
- Build 20260314 added tubesockor as new code contributor (ASID hardware support)
- GitHub Actions CI/CD for all three platforms

## Leads to follow

- **Documentation folder in release ZIP**: Each driver has a `.txt` file. Highest priority — extract all from any downloaded release and save to `docs/src/`.
- **Latest user manual PDF**: Download `SIDFactoryII_20260314_User_Manual.pdf` (csdb.dk #260181 download) and extract to `docs/src/`.
- **driver_info.h full dump**: The `~310 line` header has exact struct field types/sizes — get raw file for byte-offset calculations.
- **auxilary_data_songs.h**: Multi-song format details — fetch this source file.
- **Laxity's Editor v3.x (1990–1991)**: These are the earliest Laxity editors that precede JCH NewPlayer collaboration. CSDb scener page #677 lists `Laxity Editor v/34-3.35` and `Laxity Editor v/32-3.34` — find those releases.
- **JCH Editor V3.04 20G4**: The companion editor to NP21.G5 — fetch its CSDb entry.
- **ChipMusic.org SF2 forum thread** https://chipmusic.org/forums/topic/24826/ (returned 403 at scrape time — retry).
