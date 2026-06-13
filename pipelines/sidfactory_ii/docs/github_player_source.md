---
source_url: https://github.com/Chordian/sidfactory2
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity) + Jens-Christian Huus (JCH) + Michel de Bree
content_date: 2026-03-14 (latest release)
reliability: primary
---

# SID Factory II — GitHub Player Source Notes

## Repository

- URL: https://github.com/Chordian/sidfactory2
- License: GPL v2
- Latest release tag: release-20260314

## Key finding: No 6502 assembly source in the repo

The driver .asm source files are NOT in the repository. Only compiled `.prg` binaries are
shipped in `SIDFactoryII/drivers/`. The 6502 player code must be obtained by disassembly
of those .prg files (see `github_format_spec.md` for the driver descriptor format, which
tells you where every table lives).

The drivers ARE self-describing: each .prg contains a binary header at its load address
that the editor parses to discover all table addresses, sizes, and semantics. The C++
`driver_info.cpp` parser is the authoritative decoder of this header.

## Driver file inventory

Located at `SIDFactoryII/drivers/`:

| Filename              | Driver | Variant |
|-----------------------|--------|---------|
| sf2driver11_00.prg    | 11     | 00      |
| sf2driver11_01.prg    | 11     | 01 (+fret slide) |
| sf2driver11_02.prg    | 11     | 02 (+pulse/tempo/main volume cmds) |
| sf2driver11_03.prg    | 11     | 03 (+filter channel enable) |
| sf2driver11_04.prg    | 11     | 04 (+note delay) |
| sf2driver11_04_01.prg | 11     | 04_01 (minor variant) |
| sf2driver11_05.prg    | 11     | 05 (fret removed, HR table 16->8, skip pulse reset flag) |
| sf2driver12_00.prg    | 12     | 00 (simple) |
| sf2driver12_00_01.prg | 12     | 00_01 |
| sf2driver13_00.prg    | 13     | 00 (Hubbard emulation) |
| sf2driver13_00_01.prg | 13     | 00_01 |
| sf2driver14_00.prg    | 14     | 00 (experimental short gate-off) |
| sf2driver14_00_01.prg | 14     | 00_01 |
| sf2driver15_00.prg    | 15     | 00 (tiny, zero-page vars) |
| sf2driver15_01.prg    | 15     | 01 |
| sf2driver15_02.prg    | 15     | 02 (updated HR, wave prog cmd 3x) |
| sf2driver16_00.prg    | 16     | 00 (tiny, no commands) |
| sf2driver16_01.prg    | 16     | 01 |
| sf2driver16_01_01.prg | 16     | 01_01 |
| sf2driver_np20_00.prg | NP20   | 00 (JCH's NewPlayer 2.0) |

## Music example files in the repo

`SIDFactoryII/music/JCH/` contains 9 .sf2 files (JCH compositions using the NP20 driver):
- JCH - All Around The World.sf2
- JCH - Awry.sf2
- JCH - Crazy.sf2
- JCH - Down.sf2
- JCH - Gentofte.sf2
- JCH - Haploid.sf2
- JCH - Rising_Planet.sf2
- JCH - Slow_Cool.sf2
- JCH - Synchords.sf2

These are real SF2 format files and can be parsed once the driver format is understood.
The .sf2 format is simply: driver .prg image + packed song data appended after the driver
code, with auxiliary data (song names, descriptions, etc.) appended further at the end.

## Driver architecture overview (from C++ source)

The `driver_info.cpp` parser reads a self-describing binary header embedded at the start
of each driver .prg. The header starts with magic word `0x1337` at the load address, then
has sequential blocks until a `0xFF` terminator. Each block has:
- 1 byte: block type ID
- 1 byte: block size
- N bytes: block data

Required blocks: Descriptor, DriverCommon, DriverTables, InstrumentDescriptor, MusicData.
Optional: TableColorRules, TableInsertDeleteRules, TableActionRules, InstrumentDataDescriptor.

The `DriverCommon` block contains ~20 absolute addresses into the driver's zero-page and
RAM state: init/stop/update routine addresses, tick counter, order list index, sequence
index, current note/instrument/command registers, etc. — all driver-version-specific.

The `MusicData` block contains the addresses and sizes of the variable data region:
- Track count + order-list pointer table addresses (split lo/hi, like FC)
- Sequence count + sequence pointer table addresses (split lo/hi)
- Order list size (fixed per driver version, each track's block is this many bytes)
- Address of track 1's order list (Track N = track1 + N*orderlist_size)
- Sequence size (fixed per driver version)
- Address of sequence 0 (Sequence N = seq0 + N*sequence_size)

The `DriverTables` block describes each editable table (wave, pulse, filter, arp, HR,
tempo, instruments, commands) with: name string, data layout (row-major vs column-major),
absolute address, column count, row count, visible row count, and rule IDs.

## Converters in the repo

- `converters/gt/` — GoatTracker 2 .sng → SF2
- `converters/cc/` — CheeseCutter .ct → SF2
- `converters/mod/` — Amiga MOD → SF2
- `converters/jch/` — JCH NP20.gX (old JCH player format) → SF2 (driver_np20)
- `converters/null/` — null converter

The `converters/utils/sf2_interface.cpp` (~890 lines) is the most important file: it's a
full programmatic interface to the SF2 memory model used by ALL converters. It reads/writes
order lists, sequences, and tables, and handles pack/unpack. See `github_parser_notes.md`.

## Auxiliary data

After the driver + song data, each .sf2 file has auxiliary data at the address stored at
`$0FFB` (a known fixed address). The auxiliary data stores:
- Song names / song count / selected song (AuxilaryDataSongs)
- Hardware preferences (SID model 6581/8580)
- Editing preferences
- Play markers
- Table text labels (per-row descriptions for instruments/commands/etc.)

The init routine address is at DriverCommon.m_InitAddress. The IRQ/auxiliary vectors
are stored at known fixed offsets relative to it:
- `[init_address - 2]` = IRQ vector lo/hi
- `[init_address - 5]` = auxiliary data vector lo/hi
- `$0FFB` = auxiliary data address (also)

## Song (multi-subtune) support

The AuxilaryDataSongs struct supports multiple songs (subtunes). Song count starts at 1.
Each song selects a different starting point in the order lists. The driver's order-list
structure interleaves songs: for track_count=3 and song_count=N, order lists are laid out
as tracks 1-3 for song 0, then tracks 1-3 for song 1, etc. (total = track_count * song_count
order-list blocks in sequential memory).

## NP20 driver (JCH's player)

The NP20 format is NOT the SF2 driver format — it's JCH's older "NewPlayer 2.0" engine
loaded at $0F00. The converter_jch.cpp reads it and imports into the sf2driver_np20 format.

JCH NP20 binary layout (absolute addresses in the .prg):
- $0F00: load address (destination)
- $0FA6: pointer to init data (speed setting at init_data_address + 6)
- $0FBA: pointer to fine tune table
- $0FBC: pointer to wave table
- $0FC0: pointer to filter table
- $0FC2: pointer to pulse table
- $0FC4: pointer to instrument table
- $0FC6: pointer to orderlist voice 1
- $0FC8: pointer to orderlist voice 2
- $0FCA: pointer to orderlist voice 3
- $0FCC: pointer to sequence vector low bytes
- $0FCE: pointer to sequence vector high bytes
- $0FD0: pointer to command table
- $0FEE: version string "20.G" (2.0 GoatTracker-compatible format identifier)

NP20 orderlist format: pairs of (transpose, sequence_index), transpose 0xFF = end marker.
NP20 sequence format: pairs of (command_or_instrument, note), command=0x7F = end.
  - command >= 0xC0: this is a command byte ($C0 = command 0)
  - command < 0xC0: this is an instrument index byte
  - note: note value
Tables are row-major in NP20, converted to column-major for SF2.
