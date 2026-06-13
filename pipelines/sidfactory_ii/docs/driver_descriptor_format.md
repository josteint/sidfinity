---
source_url: https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/driver/driver_info.h
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity) / Jens-Christian Huus (JCH) / Michel de Bree (Youth)
content_date: 2020–2026
reliability: primary
---

# SID Factory II — Driver Descriptor Format

This document describes the binary structure of a SID Factory II driver `.prg` file
as parsed by the editor's C++ class `Editor::DriverInfo`
(`SIDFactoryII/source/runtime/editor/driver/driver_info.{h,cpp}`).

Secondary sources: `driver_utils.{h,cpp}`, `driver_architecture_sidfactory2.{h,cpp}`,
`datasource_orderlist.{h,cpp}`, `datasource_sequence.{h,cpp}`.


---

## 1. PRG File Layout

A `.prg` (Commodore program) file starts with a 2-byte little-endian load address, then
data that should be placed at that address in C64 memory.

```
Offset 0x00 : WORD  load address  (= m_TopAddress; the address placed in memory)
Offset 0x02 : ...   descriptor block chain (see §2)
              ...   driver 6502 code
              ...   music data (order lists, sequences)
              ...   data tables (instruments, commands, wave, pulse, filter, arpeggio, HR, tempo)
Offset 0x0FFB (absolute in file, fixed): WORD  pointer to auxiliary data block
                                                (0x0000 = no aux data)
```

The file is a standard C64 PRG: load address at byte 0, everything else follows immediately.
`GetTopAddress()` on the C64File object returns the load address word; all subsequent
addresses in the descriptor are absolute 6502 addresses (i.e. relative to where the PRG
was loaded).

**File identity magic:** The first 2 bytes *at the load address* (i.e. the first data word
the driver sees in C64 memory) must equal `0x1337`. The parser validates this before
proceeding:

```cpp
static const unsigned short ExpectedFileIDNumber = 0x1337;
if (inFile.GetWord(top_address) == ExpectedFileIDNumber) { ... }
```

---

## 2. Descriptor Block Chain

Starting at `load_address + 2`, the file contains a chain of typed variable-length blocks.
Each block is:

```
[block_id : BYTE]  [block_size : BYTE]  [block_data : block_size bytes]
```

`block_id == 0xFF` terminates the chain. The parser reads IDs sequentially; duplicate IDs
are an error. Block sizes are expressed in bytes and the reader enforces the boundary.

### Block IDs

| ID | Enum name                          | Required | Description                                      |
|----|------------------------------------|----------|--------------------------------------------------|
| 1  | `ID_Descriptor`                    | YES      | Driver type, version, code location              |
| 2  | `ID_DriverCommon`                  | YES      | Addresses of runtime state variables             |
| 3  | `ID_DriverTables`                  | YES      | List of editable data tables (instruments, etc.) |
| 4  | `ID_DriverInstrumentDescriptor`    | YES      | Cell label strings for the instrument editor     |
| 5  | `ID_MusicData`                     | YES      | Track/sequence layout in memory                  |
| 6  | `ID_TableColorRules`               | optional | Per-table row colorization rules                 |
| 7  | `ID_TableInsertDeleteRules`        | optional | Cross-table insert/delete propagation rules      |
| 8  | `ID_TableActionRules`              | optional | Table cell action trigger rules                  |
| 9  | `ID_DriverInstrumentDataDescriptor`| optional | Pointer-following rules for instrument sub-tables|
| FF | `ID_End`                           | —        | Terminates the block chain                       |

Validity: a driver is *fully valid* if all five required blocks are present AND the
`ID_DriverTables` block contains at least one `Instruments`-typed table AND one
`Commands`-typed table. A driver is *partially valid* if at least one block parsed.

---

## 3. Block Payloads

All multi-byte integers are **little-endian** (6502/C64 native), matching
`C64FileReader::ReadWord()` behaviour.

### 3.1 ID_Descriptor (block id 1)

```
driver_type           : BYTE    // 0x00 = DriverArchitectureSidFactory2
driver_size           : WORD    // total size of the driver binary in bytes
driver_name           : ASCIIZ  // null-terminated name string (e.g. "11.00 - The Standard")
driver_code_top       : WORD    // absolute 6502 address where driver code begins
driver_code_size      : WORD    // size of driver code in bytes
driver_version_major  : BYTE
driver_version_minor  : BYTE
driver_version_rev    : BYTE    // optional; if block ends before this, revision = 0
```

`driver_type == 0x00` → instantiates `DriverArchitectureSidFactory2`. Only one architecture
type exists in the current codebase.

`driver_code_top` + `driver_code_size` define the range the packer's `ProcessDriverCode()`
walks for relocation (see §6).

### 3.2 ID_DriverCommon (block id 2)

Sequence of 18 WORDs + 2 BYTEs + 1 WORD (all absolute 6502 addresses of runtime variables
stored in the driver or zero-page):

```
init_address                      : WORD  // JSR here to initialise the driver
stop_address                      : WORD  // JSR here to stop playback
update_address                    : WORD  // JSR here every frame (the "play" routine)
sid_channel_offset_address        : WORD  // ptr to per-voice SID base offset table
driver_state_address              : WORD  // overall driver play state byte
tick_counter_address              : WORD  // per-voice tick countdown (array, TrackCount bytes)
order_list_index_address          : WORD  // per-voice orderlist read index (array)
sequence_index_address            : WORD  // per-voice position within current sequence (array)
sequence_in_use_address           : WORD  // per-voice "sequence active" flag (array)
current_sequence_address          : WORD  // per-voice current sequence number (array)
current_transpose_address         : WORD  // per-voice active transpose value (array)
current_seq_event_duration_address: WORD  // per-voice remaining duration ticks (array)
next_instrument_address           : WORD  // per-voice next instrument to apply (array)
next_command_address              : WORD  // per-voice next command to apply (array)
next_note_address                 : WORD  // per-voice next note value (array)
next_note_is_tied_address         : WORD  // per-voice "tie note" flag (array)
tempo_counter_address             : WORD  // tempo countdown register
trigger_sync_address              : WORD  // sync trigger flag address
note_event_trigger_sync_value     : BYTE  // value written to trigger_sync when a note fires
reserved_byte                     : BYTE
reserved_word                     : WORD
```

These addresses are what `PostInitSetPlaybackIndices()` writes into to reposition playback
mid-song (the "play from cursor" feature).

### 3.3 ID_DriverTables (block id 3)

A list of table definitions terminated by `0xFF`. Each entry:

```
table_type          : BYTE    // 0x00=Generic, 0x80=Instruments, 0x81=Commands
table_id            : BYTE    // unique ID referenced by other rules
text_field_size     : BYTE    // width of the label text column in editor (0=no label col)
name                : ASCIIZ  // display name (e.g. "Instruments", "Wave", "Pulse", "Filter")
data_layout         : BYTE    // 0=RowMajor, 1=ColumnMajor
properties          : BYTE    // bitfield: 0x01=EnableInsertDelete, 0x02=LayoutVertically,
                               //           0x04=IndexAsContinuousMemory
insert_delete_rule_id: BYTE   // rule set ID from block 7 (0xFF = none)
enter_action_rule_id: BYTE    // rule set ID from block 8 (0xFF = none)
color_rule_id       : BYTE    // rule set ID from block 6 (0xFF = none)
address             : WORD    // absolute 6502 address of the table data
column_count        : WORD    // number of columns (bytes per row)
row_count           : WORD    // total number of rows allocated
visible_row_count   : BYTE    // rows shown in the editor at once
```

`table_type` determines the table's role:
- `0x80 (Instruments)`: The instrument table. Must appear exactly once.
- `0x81 (Commands)`: The command table. Must appear exactly once.
- `0x00 (Generic)`: Any auxiliary table (wave, pulse, filter, arpeggio, HR, tempo, etc.).

For Driver 11, the typical tables are (names from `notes_driver11.txt`):

| Name         | Type        | Layout      | Cols | Rows | Notes                         |
|--------------|-------------|-------------|------|------|-------------------------------|
| Instruments  | Instruments | ColumnMajor | 6    | 32   | 6 bytes/row: AD SR Flags F P W|
| Commands     | Commands    | ColumnMajor | 3    | 64   | 3 bytes/row: T XX YY          |
| Wave         | Generic     | ColumnMajor | 2    | 256  | 2 bytes/row: waveform + semit |
| Pulse        | Generic     | ColumnMajor | 3    | 64   | 3 bytes/row                   |
| Filter       | Generic     | ColumnMajor | 4    | 64   | 4 bytes/row                   |
| Arpeggio     | Generic     | ColumnMajor | 1    | 128  | 1 byte/row                    |
| HR (hard rst)| Generic     | ColumnMajor | 2    | 8/16 | 11.05 reduced to 8            |
| Tempo        | Generic     | ColumnMajor | 1    | 16   | optional (11.02+)             |

**ColumnMajor memory layout:** `byte[col * row_count + row]` — i.e. all values for column 0
are stored contiguously, then all values for column 1, etc. This is the dominant layout for
Driver 11 tables and matches the 6502 player's indexed access (`LDA table_col0,X`).

**RowMajor memory layout:** `byte[row * column_count + col]` — conventional row-first order.

### 3.4 ID_DriverInstrumentDescriptor (block id 4)

```
descriptor_count : BYTE
descriptor_count × ASCIIZ  // cell description strings for instrument editor columns
```

For Driver 11 with 6-byte instruments, there are 6 strings:
`["AD", "SR", "Flags", "Filter", "Pulse", "Wave"]` (exact strings vary by build).

### 3.5 ID_MusicData (block id 5)

```
track_count                              : BYTE   // typically 3 (one per SID voice)
track_orderlist_ptrs_low_address         : WORD   // abs addr of lo-byte pointer table
track_orderlist_ptrs_high_address        : WORD   // abs addr of hi-byte pointer table
sequence_count                           : BYTE   // number of sequence slots (max 128)
[emulation_ptr_to:]
sequence_ptrs_low_address                : WORD   // abs addr of sequence lo-byte ptr table
[emulation_ptr_to:]
sequence_ptrs_high_address               : WORD   // abs addr of sequence hi-byte ptr table
order_list_size                          : WORD   // allocated bytes per order list
[emulation_ptr_to:]
order_list_track1_address                : WORD   // abs addr of track 1's order list data
sequence_size                            : WORD   // allocated bytes per sequence slot
[emulation_ptr_to:]
sequence_00_address                      : WORD   // abs addr of sequence slot 0
```

The `[emulation_ptr_to:]` notation means the parser records the *file address* of the
next WORD field before reading it (stored in `MusicDataMetaDataEmulationAddresses`).
This allows `RefreshMusicData()` to re-read these four addresses from C64 memory after
the packer relocates the music data — the descriptors themselves become self-updating
pointers.

**Order list memory layout:**
```
order_list_track1_address + (track_index * order_list_size)
```
Multi-song: `track_count * song_count` order lists laid out consecutively.

**Sequence slot memory layout:**
```
sequence_00_address + (sequence_index * sequence_size)
```

### 3.6 ID_TableColorRules (block id 6)

A list of rule-sets (one per table that has a `color_rule_id`), each terminated by `0xFF`,
and the whole block terminated by `0xFE`. Each rule within a set:

```
evaluation_cell_index         : BYTE   // which column to test
evaluation_cell_mask          : BYTE   // AND mask applied before comparison
evaluation_cell_conditional   : BYTE   // expected value after masking
background_color              : BYTE   // color to apply if condition is met
```

### 3.7 ID_TableInsertDeleteRules (block id 7)

Same nested-list structure (`0xFF` inner, `0xFE` outer). Each rule:

```
target_table_id               : BYTE
target_cell_index             : BYTE
evaluation_cell_index         : BYTE
evaluation_cell_mask          : BYTE
evaluation_cell_conditional   : BYTE
```

### 3.8 ID_TableActionRules (block id 8)

Same nested-list structure. Each rule:

```
applicable_cell               : BYTE
target_table_id               : BYTE
target_index_cell             : BYTE
target_index_mask             : BYTE
evaluation_cell_index         : BYTE
evaluation_cell_mask          : BYTE
evaluation_cell_conditional   : BYTE
```

### 3.9 ID_DriverInstrumentDataDescriptor (block id 9)

Describes how instrument bytes point into sub-tables (e.g. byte 5 = wave table index):

```
instrument_pointer_count : BYTE
instrument_pointer_count × {
    table_id                           : BYTE
    instrument_data_pointer_position   : BYTE  // which instrument byte holds the index
    pointer_and_value                  : BYTE  // AND mask to extract the index
    instrument_data_conditional_pos    : BYTE  // byte to check for conditional activation
    condition_value_and_value          : BYTE  // AND mask for condition
    condition_equality_value           : BYTE  // expected value for condition
    table_data_type                    : BYTE
    table_jump_marker_value_position   : BYTE
    table_jump_marker_value            : BYTE
    table_jump_destination_index_pos   : BYTE
}
```

---

## 4. Auxiliary Data Block

At absolute file address `0x0FFB` is a 2-byte little-endian pointer to the auxiliary data
block. If `0x0000`, there is no auxiliary data.

The aux data block is parsed by `AuxilaryDataCollection::Load()` and stores editor-specific
metadata (song names, play markers, editing preferences, hardware preferences, table text
labels). It is NOT part of the 6502 driver binary and is NOT relocated.

The sub-block `AuxilaryDataSongs` records the song count and per-song names. The song count
drives `GetHighestSequenceIndexUsed()` which iterates
`track_count × song_count` order lists.

---

## 5. Sequence Packed Format

Sequences are stored in a variable-length run-encoded byte stream, max `sequence_size` bytes
each. Byte ranges:

| Range      | Meaning                                                          |
|------------|------------------------------------------------------------------|
| `0x00`     | Note off (gate off)                                              |
| `0x01–0x6F`| Note value (semitone index; layout is Protracker-style key map) |
| `0x7F`     | **End-of-sequence marker** (must be present)                     |
| `0x80–0x8F`| Duration: lower nibble = ticks-1, no tie                         |
| `0x90–0x9F`| Duration with tie-note flag set                                  |
| `0xA0–0xBF`| Instrument select: bits 0–5 = instrument index (0–31 for drv11) |
| `0xC0–0xFF`| Command select: bits 0–5 = command table index (0–63)            |

Instrument and command bytes are written only when they change (delta encoding).
Multiple identical notes at the same instrument/command are folded into a duration+count.

An empty sequence is: `[0x80, 0x00, 0x7F]` (duration=1, note=off, end marker).

---

## 6. Order List Packed Format

Each order list is `order_list_size` bytes. Byte ranges:

| Range      | Meaning                                                               |
|------------|-----------------------------------------------------------------------|
| `0x00–0x7F`| Sequence index                                                        |
| `0x80–0xFF`| Transpose change (value >= 0x80 is a transposition byte, not a seq#) |
| `0xFE`     | **End marker** (no loop); list ends here                              |
| `0xFF`     | **Loop marker**; next byte = packed-stream offset of loop start       |

The default (no transpose) is represented as `0xA0` (= semitone offset 0 in driver 11's
convention: `transpose_byte - 0xA0` gives the semitone shift, range -32 to +31).

An empty order list is: `[0xA0, 0x00, 0xFF, loop_offset]` (transpose=0, seq=0, loop back).
`SetEmptyOrderList()` writes `[0xA0, 0x00, 0xFF]`.

`GetOrderListsLength()` returns `j+2` for `0xFF` entries (+2 because the loop index byte
follows), and `j+1` for `0xFE` entries.

---

## 7. Driver Entry Points

All three entry points are absolute 6502 addresses stored in `ID_DriverCommon`:

| Address field         | Purpose                                                  |
|-----------------------|----------------------------------------------------------|
| `m_InitAddress`       | Call once at song start. Sets up all voice state, loads  |
|                       | initial instruments, primes tables.                      |
| `m_StopAddress`       | Call to silence playback (writes $00 waveforms etc.).    |
| `m_UpdateAddress`     | Call once per frame (IRQ or VBI). Advances all voices.   |

The IRQ wrapper inserted by `InsertIRQ()` calls `m_InitAddress` once on startup, then
calls `m_UpdateAddress` from the raster IRQ handler each frame. The IRQ vector installed
is at `$0314/$0315` (C64 standard IRQ vector). The inserted machine code patch is 58 bytes
assembled at the end of the file by `Utility::C64FileWriter`.

---

## 8. Instrument Layout (Driver 11)

6 bytes per instrument row, ColumnMajor — i.e. all AD values for all 32 rows contiguous,
then all SR values, etc.

```
Byte 0 (col 0): AD      — Attack (hi nibble) / Decay  (lo nibble)
Byte 1 (col 1): SR      — Sustain (hi nibble) / Release (lo nibble)
Byte 2 (col 2): Flags
    bit 7 (0x80): Enable hard restart
    bit 6 (0x40): Start filter program (index from byte 3)
    bit 5 (0x20): [11.03] Enable filter on this channel
    bit 4 (0x10): Oscillator reset (uses waveform $09 on first frame)
    bit 3 (0x08): Skip pulse-program reset on note-on (unless instrument explicitly set)
    bits 0–2 (0x0X): Hard restart table index (0–7; 0–15 before 11.05)
Byte 3 (col 3): Filter table index (used when bit 6 of flags is set)
Byte 4 (col 4): Pulse table index
Byte 5 (col 5): Wave table index
```

---

## 9. Command Layout (Driver 11)

3 bytes per command row, ColumnMajor. Three columns: `T`, `XX`, `YY`.

Full command semantics: see `src/notes_driver11.txt` and `driver11_source.md`.

---

## 10. Validity and Parsing Guards

- `IsValid()` → all 5 required blocks parsed + instruments table + commands table found.
- `IsPartiallyValid()` → at least one block parsed (partial parse mode for broken files).
- `HasParsedRequiredBlocks()` requires blocks 1, 2, 3, 4, 5 all parsed; blocks 6–9 are
  optional (commented out in the guard).
- The driver is "not valid" if the file ID `0x1337` check fails at `top_address`.

---

## Leads to follow

1. **Actual 6502 asm source for driver 11** — the `.prg` files in `SIDFactoryII/drivers/`
   are compiled binaries; the `.asm` source is NOT in the public GitHub repo. See
   `driver11_source.md` for what is recoverable. RE the binary to extract the full
   6502 source: run `siddump --pc-trace` on a driver-11 SID, or disassemble
   `sf2driver11_05.prg` with `tools/seed_disassembly.py`.

2. **Exact table counts per driver variant** — `notes_driver11.txt` documents the semantic
   changes across 11.00–11.05, but the exact row/column/address values for each
   build-variant's `ID_DriverTables` entries require parsing the actual `.prg` binary.
   OPEN: write a Python parser for the block chain to dump all table addresses.

3. **The `m_SIDChannelOffsetAddress` table** — this is a 3-byte table (one offset per
   voice) that tells the driver's SID write routines which voice's registers to address.
   Understanding this is needed for init-priming (which registers need to be zeroed at
   driver init). OPEN: read from a loaded driver binary.

4. **Multi-song order list layout** — the packer's `ApplyMultiSongPatch()` injects code to
   switch the order list pointer based on a song index. The exact patch bytes and the
   injected code's interface need to be reverse-engineered from `packer.cpp` fully.
   The summary captures the mechanism but the exact injected bytes are unknown.

5. **Third-party annotated disassembly** — web search found none. The only RE material
   is the editor source itself. Consider posting a request on CSDb forum thread
   https://csdb.dk/forums/?roomid=14&topicid=142903 or reaching Laxity directly.

6. **Auxiliary data format** — `AuxilaryDataCollection::Load()` and the individual
   `AuxilaryData` subclasses have their own versioned serialization format.
   These are editor-only (not part of 6502 playback) but needed for round-trip USF
   conversion. OPEN: fetch and read `auxilary_data.cpp` + `auxilary_data_collection.cpp`.
