---
source_url: https://github.com/Chordian/sidfactory2/tree/master/SIDFactoryII/source
fetched_via: direct
fetch_date: 2026-06-13
author: Michel de Bree / Jens-Christian Huus / Thomas Egeskov Petersen
content_date: 2026-03-14
reliability: primary
---

# SID Factory II — C++ Parser / Converter Notes

## Primary Source Files Read

All files fetched from raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/

| File | Lines | Role |
|------|-------|------|
| runtime/editor/driver/driver_info.h | 310 | DriverInfo data structures + parsing API |
| runtime/editor/driver/driver_info.cpp | 555 | Binary header parser implementation |
| runtime/editor/driver/driver_utils.h | 46 | Utility function declarations |
| runtime/editor/driver/driver_utils.cpp | 464 | Address calculations, IRQ insertion, SID write analysis |
| runtime/editor/datasources/datasource_orderlist.h | 87 | Order list data model |
| runtime/editor/datasources/datasource_orderlist.cpp | 371 | Pack/unpack for order list format |
| runtime/editor/datasources/datasource_sequence.h | 123 | Sequence data model + Event struct |
| runtime/editor/datasources/datasource_sequence.cpp | 412 | Pack/unpack for sequence format |
| runtime/editor/converters/utils/sf2_interface.h | 221 | High-level SF2 API (table/orderlist/sequence access) |
| runtime/editor/converters/utils/sf2_interface.cpp | 890 | SF2 converter interface implementation |
| runtime/editor/converters/jch/converter_jch.cpp | 582 | JCH NP20 → SF2 converter |
| runtime/editor/instrument/instrumentdata.h | 35 | |
| runtime/editor/instrument/instrumentdata.cpp | 128 | |
| runtime/editor/auxilarydata/auxilary_data_songs.h | 77 | Song/subtune data |
| runtime/editor/auxilarydata/auxilary_data_songs.cpp | ~100 | |
| dist/documentation/notes_driver11.txt | 96 | Official driver 11 format doc |
| dist/documentation/notes_driver12.txt | 29 | |
| dist/documentation/notes_driver13.txt | 39 | |
| dist/documentation/notes_driver14.txt | 60 | |
| dist/documentation/notes_driver15.txt | 50 | |
| dist/documentation/notes_driver16.txt | 40 | |

---

## SF2 Interface API (sf2_interface.cpp)

The `SF2::Interface` class in `sf2_interface.cpp` (~890 lines) is the complete
programmatic interface used by all converters. Key observations for our decompiler:

### Loading a driver

```cpp
Interface sf2(platform, console);
sf2.LoadFile("path/to/sf2driver11_05.prg");
```

This:
1. Reads the PRG binary
2. Calls `DriverInfo::Parse()` to parse the self-describing header blocks
3. Loads the data into emulated C64 memory (CPUMemory)
4. Calls `InitData()` which prepares datasources for all order lists and sequences

### Reading order list data

```cpp
std::vector<unsigned char> GetContainerOrderList(int inTrack);
// Returns: [track_index, transpose_0, seq_0, transpose_1, seq_1, ..., 0xFF, loop_idx]
// Wait, actually: [track_index, transpose_0, seq_0, ...]
// The container is built from DataSourceOrderList entries.
```

Actually from the source: the container is built by iterating `orderlist->GetLength()` entries,
each having `{m_Transposition, m_SequenceIndex}`.

### Table column count for driver 11 (from ParseDriverDetails)

The `ParseDriverDetails()` function probes each table by name and caches column counts.
Driver 11.xx sets command format to byte position 0, mask 0xFF.

For driver 11, supported commands are:
```
Cmd_Slide, Cmd_Vibrato, Cmd_Portamento, Cmd_Arpeggio,
Cmd_ADSR_Note, Cmd_ADSR_Persist, Cmd_Index_Filter, Cmd_Index_Wave,
Cmd_Index_Pulse, Cmd_Tempo, Cmd_Volume, Cmd_Demo_Flag
```
Note: `Cmd_Fret` (0x04) is NOT in the v11.02 supported list even though it exists in
v11.01-v11.04. This is a bug in the converter code or intentional (only v11.02+ supported).

### Wrap format for driver 11 tables

```
Wave:    ByteIDPosition=0, ByteIDMask=0xFF, ByteID={0x7F}, WrapPosition=1, WrapMask=0xFF
Pulse:   ByteIDPosition=0, ByteIDMask=0xFF, ByteID={0x7F}, WrapPosition=2, WrapMask=0xFF
Filter:  same as Pulse
Tempo:   ByteIDPosition=0, ByteIDMask=0xFF, ByteID={0x7F}, WrapPosition=-1 (no wrap value)
Arpeggio: no wrap ID (ByteIDPosition=-1) — relative jumps always
```

This means: in the converter, wave/pulse/filter jump indices start relative (0 = first row of
this cluster) and get converted to absolute when `PushAllDataToMemory(true)` is called.

---

## DataSourceOrderList Key Points

### Unpack algorithm (from datasource_orderlist.cpp)

The packed orderlist byte stream is parsed as:
```
bytes >= 0x80 → transpose byte: current_transpose = byte
               (the actual transpose = (byte & 0x7F) - 0x20 = signed -32..+31)
bytes < 0x80 → sequence index: emit entry (current_transpose, byte)
byte == 0xFF → end marker (loop). Loop point byte follows.
byte == 0xFE → end marker (no loop/stop).
```

The unpacked model stores entries as `{m_Transposition, m_SequenceIndex}` where
`m_Transposition` is the raw byte ($A0 = identity = no transpose).

A virgin (empty) order list starts with `{0xA0, 0x00}` = default transpose + sequence 0.
The converter initializes all tracks to `{0xFF, 0x00}` temporarily to detect "untouched".

### Computing loop point

After the 0xFF end marker, the NEXT byte is the loop point — a byte offset into the PACKED
data, pointing to the transposition byte (or sequence byte) to restart from. This is NOT a
simple sequence index; it's a byte position in the packed stream.

Example orderlist (packed):
```
A0    ; transpose 0 (identity)
00    ; sequence 0
01    ; sequence 1  <- loop starts here (offset 2 in packed stream)
A4    ; transpose +4 (= 0xA4 & 0x7F - 0x20 = 0x24 - 0x20 = 4)
02    ; sequence 2
FF    ; end (loop)
02    ; loop offset = 2 (back to "01" = sequence 1)
```

### GetIndexInPackedData

Used to find byte offset for playback positioning:
```cpp
for each byte in packed data:
  if byte < 0x80: increment event count; if count == target+1, return current position
  else: update transpose (byte & 0x7F - 0x20)
```

---

## DataSourceSequence Key Points

### Exact byte encoding (from the comment in datasource_sequence.cpp)

```
00         = Note off
01 - 6f    = Notes (1..111)
70 - 7d    = Reserved
7e         = Note on (gate-on continuation / tie)
7f         = End of sequence
80 - 8f    = Duration, note follows. Duration = byte & 0x0F extra ticks.
90 - 9f    = Duration + tie note. Duration = byte & 0x0F; tie=true.
a0 - bf    = Set instrument ($00 - $1F). Inst = byte & 0x1F.
c0 - ff    = Set command ($00 - $3F). Cmd = byte & 0x3F.
```

### AppendToSequence API

```cpp
// instrument: 0x00..0x1F (31 instruments) or 0x80 (no change) or 0x90 (tie)
// command: 0x00..0x3F or 0x80 (no change)
// note: 0x00..0x6F or 0x7E (note on)
// stored as:
Event.m_Instrument = (instrument < 0x20) ? instrument + 0xA0 : instrument;
Event.m_Command    = (command < 0x40)    ? command + 0xC0    : command;
Event.m_Note       = note;
```

### Pack details

Duration compression: the packer looks ahead for continuation events. An event is a
"continuation" if it has no instrument change (m_Instrument == 0x80) and no command change
(m_Command == 0x80), AND the note is 0x7E (held) or 0x00 (off = same as previous 0x00).

Max duration = 15 extra ticks ($8F = 0 extra = 1 tick total; $8F = 15 extra = 16 ticks).

The duration byte is NOT emitted if it hasn't changed since the last event.

---

## DriverUtils Key Functions

### GetEndOfMusicDataAddress

```cpp
unsigned short GetEndOfMusicDataAddress(DriverInfo, Memory):
  highest_seq = GetHighestSequenceIndexUsed()  // scan all orderlists
  return sequence00_address + sequence_size * (highest_seq + 1)
```

### GetSequenceUsageCount

Scans all order lists for each song, counts how many times each sequence index is referenced.
Order list bytes < SequenceCount are sequence indices; bytes >= 0xFE are end markers.

### GetHighestInstrumentIndexUsed

Scans all sequences for $A0..$BF bytes, extracts instrument index = byte & 0x1F.

### GetHighestCommandIndexUsed

Scans all sequences for $C0..$FF bytes, extracts command index = byte & 0x3F.

---

## JCH NP20 Converter (converter_jch.cpp)

Converts JCH's older "NewPlayer 2.0" format (.prg loaded at $0F00) to SF2 NP20 driver.

### NP20 fingerprint
- Load address: $0F00
- Bytes at $0FEE: "20.G" = version identifier "2.0 GoatTracker"

### NP20 data pointers (absolute addresses in the file)
```
$0FA6: pointer to init data (speed setting 6 bytes in from there)
$0FBA: fine tune table pointer
$0FBC: wave table pointer
$0FC0: filter table pointer
$0FC2: pulse table pointer
$0FC4: instrument table pointer
$0FC6: orderlist voice 1 pointer
$0FC8: orderlist voice 2 pointer
$0FCA: orderlist voice 3 pointer
$0FCC: sequence vector low bytes pointer
$0FCE: sequence vector high bytes pointer
$0FD0: command table pointer
```

### NP20 table layout
- Instrument + command tables: row-major in NP20, converted to column-major for SF2
- Wave table: bytes are SWAPPED during copy (col0 and col1 of wave table exchange)
- Pulse, filter tables: direct copy

### NP20 orderlist format
Pairs of (transpose_byte, sequence_index_byte):
- transpose_byte = 0xFF → end marker (no loop support in NP20?)
- transpose converted: SF2_transpose = NP20_transpose + 0x20 (i.e. NP20 uses 0=identity,
  SF2 uses 0xA0=identity; the shift is 0x20)

### NP20 sequence format
Pairs of (command_or_instrument, note_byte):
- 0x7F in command position = end of sequence
- command_or_instrument >= 0xC0 → SF2 command byte (stored directly)
- command_or_instrument < 0xC0 → SF2 instrument byte (stored directly)

---

## Auxiliary Data Files Not Yet Read

The following files contain auxiliary data serialization that was NOT fully parsed:
- `auxilary_data_collection.h/cpp` — main serializer (type→block format)
- `auxilary_data.h/cpp` — base class
- `auxilary_data_hardware_preferences.h/cpp` — SID model, PAL/NTSC
- `auxilary_data_editing_preferences.h/cpp`
- `auxilary_data_play_markers.h/cpp`
- `auxilary_data_table_text.h/cpp`

OPEN: Fetch these to understand exact binary serialization of auxiliary data blocks.

---

## Instrument Data Table Mapping (instrumentdata_tablemapping.cpp)

This file provides additional instrument-to-table mapping (which wave/pulse/filter program
does this instrument use?). The `InstrumentDataPointerDescription` struct in `driver_info.h`
describes this:

```cpp
struct InstrumentDataPointerDescription {
    unsigned char m_TableID;                        // Which table
    unsigned char m_InstrumentDataPointerPosition;  // Byte in instrument row = index into table
    unsigned char m_PointerAndValue;                // AND-mask for the pointer value
    unsigned char m_InstrumentDataConditionalValuePosition; // Condition byte in instrument row
    unsigned char m_ConditionValueAndValue;         // AND-mask for condition
    unsigned char m_ConditionEqualityValue;         // Condition == this value → pointer is active
    unsigned char m_TableDataType;                  // 0=single entry, 1=looping with jump markers
    unsigned char m_TableJumpMarkerValuePosition;   // Position of jump marker in table row
    unsigned char m_TableJumpMarkerValue;           // The jump marker value
    unsigned char m_TableJumpDestinationIndexPosition; // Position of jump target in table row
};
```

For driver 11, this is populated via Block 9 (InstrumentDataDescriptor) in the driver header,
enabling the editor to know: "instrument byte 3 (filter table index) points into the Filter
table, but only if byte 2 bit 6 (0x40) is set."
