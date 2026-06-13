---
source_url: https://github.com/Chordian/sidfactory2 (auxilary_data.cpp, auxilary_data_collection.cpp, auxilary_data_songs.cpp, driver_info.h, driver_info.cpp)
fetched_via: direct
fetch_date: 2026-06-13
author: Jens-Christian Huus (Chordian)
content_date: unknown (master branch as of 2026-06-13)
reliability: primary
---

# SID Factory II — Auxiliary Data Format

Full source saved at `docs/src/auxilary_data_collection_cpp.cpp` and `docs/src/auxilary_data_songs_cpp.cpp`.

## What is auxiliary data?

Auxiliary data is **editor-only metadata** attached to an SF2 in-editor `.c64`/`.sid` file. It is NOT carried into the exported/packed HVSC .sid. It contains:

- `AuxilaryDataPlayMarkers` — editor play-position markers
- `AuxilaryDataHardwarePreferences` — SID model, clock, second/third SID addresses
- `AuxilaryDataEditingPreferences` — editor-specific display/edit preferences
- `AuxilaryDataTableText` — per-table row/column label text (table names, instrument names etc.)
- `AuxilaryDataSongs` — multi-song count and per-song names

## Location in the in-editor file

From `driver_info.h`:

```cpp
static const unsigned short AuxilaryDataPointerAddress = 0x0ffb;
```

And from `DriverInfo::ParseAuxilaryData()`:

```cpp
unsigned short auxilary_data_address = inFile.GetWord(AuxilaryDataPointerAddress);
if (auxilary_data_address == 0)
    return false;
Utility::C64FileReader reader = Utility::C64FileReader(inFile, auxilary_data_address);
m_AuxilaryDataCollection->Load(reader);
```

So the in-editor file has a **16-bit little-endian pointer at absolute C64 address $0FFB** that points to the start of the auxiliary data block. If the word at $0FFB is 0x0000, no aux data exists.

## Auxiliary data block wire format

The aux data is a sequence of typed chunks, terminated by an Undefined/end-mark chunk. Each chunk:

```
[1 byte]  Type (enum AuxilaryData::Type)
[2 bytes] Version (unsigned short, little-endian)
[2 bytes] DataSize (unsigned short, little-endian)
[DataSize bytes] Payload
```

Type enum values (from `auxilary_data.h`):
```
Undefined = 0        <- also used as the end-mark sentinel
EditingPreferences = 1
HardwarePreferences = 2
PlayMarkers = 3
TableText = 4
Songs = 5
```

The collection is written in this order:
1. PlayMarkers (type 3)
2. HardwarePreferences (type 2)
3. EditingPreferences (type 1)
4. TableText (type 4)
5. Songs (type 5)
6. End mark (type 0, version 0, size 0)

Each reader iterates until it hits type 0 (end mark). Chunks it doesn't recognise are skipped using the DataSize field.

## AuxilaryDataSongs payload (type 5, current version 2)

```
[1 byte]  SongCount     — number of songs (1 for single-song tunes)
[1 byte]  SelectedSong  — currently selected song index (0-based)
[for each song 0..SongCount-1:]
  [N+1 bytes]  Song name as SaveDataPushStdString256:
               1 byte length (max 255), then N bytes of string chars
```

Version 1 (older files): payload is just `SongCount` + `SelectedSong`, no names.

## Impact on HVSC extraction

Auxiliary data is editor-only and is never present in HVSC .sid files. An extractor reading HVSC files:
- Cannot read aux data (it lives outside the packed binary)
- Cannot read table labels (instrument names, command names, row labels) — these are in `AuxilaryDataTableText` which is also editor-only
- Can read song count ONLY from the PSID header's `SongCount` field (see `packed_export_format.md`)
- The `SelectedSong` / default song is always 1 in the PSID header (hardcoded in `PSIDFile` constructor)

## Leads to follow

- `auxilary_data_hardware_preferences.cpp` — what fields? PAL/NTSC, 6581/8580, 2nd/3rd SID address. Needed to understand what HVSC files' Flags field encodes vs what the editor stored.
- `auxilary_data_table_text.cpp` — how instrument/command names are stored. If HVSC files ever carry a sidecar, these would be the source.
- Are there any SF2 releases in HVSC that DO include a sidecar .c64 file (with full aux data)?  Check HVSC's `/DEMOS/` and `/MUSICIANS/L/Laxity/` directories.
