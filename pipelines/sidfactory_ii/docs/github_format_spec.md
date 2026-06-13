---
source_url: https://github.com/Chordian/sidfactory2 (multiple C++ source files)
fetched_via: direct
fetch_date: 2026-06-13
author: Laxity / JCH / Michel de Bree
content_date: 2026-03-14
reliability: primary
---

# SID Factory II — Complete On-Disk Format Specification

Derived from reading the C++ source:
- `source/runtime/editor/driver/driver_info.h` + `driver_info.cpp`
- `source/runtime/editor/datasources/datasource_orderlist.h` + `.cpp`
- `source/runtime/editor/datasources/datasource_sequence.h` + `.cpp`
- `source/runtime/editor/driver/driver_utils.cpp`
- `source/runtime/editor/converters/utils/sf2_interface.h` + `.cpp`
- `dist/documentation/notes_driver11.txt` (and 12-16)

All information is primary source (GPL v2 code). No guessing.

---

## 1. .sf2 File Layout (PRG format)

An .sf2 file is a C64 PRG binary (first 2 bytes = load address, little-endian), loaded
into emulated C64 memory. The layout is:

```
[load_address: 2 bytes]
[Driver binary: from load_address to end of driver code]
  - Starts with magic word 0x1337 at load_address
  - Followed by the self-describing header blocks (see section 2)
  - Followed by driver 6502 machine code
[Song data: order lists + sequences + tables]
  - All addresses are stored in the driver header blocks
[IRQ routine: appended after song data]
  - ~58 bytes (see InsertIRQ in driver_utils.cpp)
[Auxiliary data: appended after IRQ]
  - Song names, hardware preferences, table text labels, etc.
```

Key fixed addresses (not part of the header — hardcoded in the C++ host):
- `$0FFB`: 16-bit LE pointer to auxiliary data start
- `driver_init_address - 2`: 16-bit LE pointer to IRQ routine
- `driver_init_address - 5`: 16-bit LE pointer to auxiliary data (same as $0FFB)

The end-of-file address is computed as:
```
Sequence00Address + SequenceSize * (highest_sequence_index_used + 1)
```
(then IRQ routine + auxiliary data appended after that)

---

## 2. Driver Self-Description Header

The driver header starts at the load address. Format:
```
[load_address]     : WORD = 0x1337  (magic number, ExpectedFileIDNumber)
[load_address + 2] : sequence of blocks until block_id = 0xFF
```

Each block:
```
BYTE  block_id      (1..9, or 0xFF = end)
BYTE  block_size    (size of block data following)
BYTE* block_data    (block_size bytes)
```

Block IDs (HeaderBlockID enum):

| ID | Name                         | Required |
|----|------------------------------|----------|
| 1  | Descriptor                   | YES      |
| 2  | DriverCommon                 | YES      |
| 3  | DriverTables                 | YES      |
| 4  | DriverInstrumentDescriptor   | YES      |
| 5  | MusicData                    | YES      |
| 6  | TableColorRules              | no       |
| 7  | TableInsertDeleteRules       | no       |
| 8  | TableActionRules             | no       |
| 9  | DriverInstrumentDataDescriptor | no     |
| FF | End                          | —        |

---

## 3. Block 1: Descriptor

```
BYTE   driver_type          (0 = SidFactory2 architecture)
WORD   driver_size          (total size in bytes)
STRING driver_name          (null-terminated ASCII, e.g. "Standard 11.00")
WORD   driver_code_top      (absolute C64 address where 6502 code starts)
WORD   driver_code_size     (size of 6502 code region)
BYTE   version_major        (e.g. 11)
BYTE   version_minor        (e.g. 0)
BYTE   version_revision     (optional, 0 if absent)
```

The `driver_type` must equal `DriverArchitectureSidFactory2::GetDescriptorType()`.

---

## 4. Block 2: DriverCommon

20 WORD fields (40 bytes), all absolute C64 addresses pointing into driver RAM/ZP:

```
WORD  init_address                        ; JSR here to initialize
WORD  stop_address                        ; JSR here to stop playback
WORD  update_address                      ; JSR here each frame (called by IRQ)
WORD  sid_channel_offset_address          ; address of per-voice SID reg offset table
WORD  driver_state_address                ; driver state byte
WORD  tick_counter_address                ; current tick counter (per-voice)
WORD  orderlist_index_address             ; current position in order list (per-voice)
WORD  sequence_index_address              ; cursor into current sequence (per-voice)
WORD  sequence_in_use_address             ; sequence-in-use flag (per-voice)
WORD  current_sequence_address            ; current sequence index being played (per-voice)
WORD  current_transpose_address           ; current transpose value (per-voice)
WORD  current_sequence_event_duration_address ; remaining ticks for current event
WORD  next_instrument_address             ; instrument to be set on next note (per-voice)
WORD  next_command_address                ; command to be set on next note (per-voice)
WORD  next_note_address                   ; note to play on next tick (per-voice)
WORD  next_note_is_tied_address           ; tie-note flag (per-voice)
WORD  tempo_counter_address               ; tempo counter
WORD  trigger_sync_address                ; note event trigger sync register
BYTE  note_event_trigger_sync_value       ; the "event happened" sync value
BYTE  reserved_byte
WORD  reserved_word
```

---

## 5. Block 3: DriverTables

A list of table definitions followed by 0xFF terminator. Each table definition:

```
BYTE   table_type          (0x00=Generic, 0x80=Instruments, 0x81=Commands)
BYTE   table_id            (unique ID for rule targeting)
BYTE   text_field_size     (size of text label field, 0 if no labels)
STRING table_name          (null-terminated; canonical names: "Wave","Pulse","Filter",
                             "HR","Arp","Tempo","Init","Instruments","Commands")
BYTE   data_layout         (0=RowMajor, 1=ColumnMajor)
BYTE   properties          (bit 0=EnableInsertDelete, bit 1=LayoutVertically, bit 2=IndexAsContinuousMemory)
BYTE   insert_delete_rule_id
BYTE   enter_action_rule_id
BYTE   color_rule_id
WORD   address             (absolute C64 address of table data)
WORD   column_count        (number of columns)
WORD   row_count           (total rows available)
BYTE   visible_row_count   (rows visible on screen)
```

**Data layout:**
- RowMajor: data[row * col_count + col] at address + (row * col_count + col)
- ColumnMajor: data[row][col] at address + (col * row_count + row)
  - Instruments and Commands tables use ColumnMajor in driver 11

**Canonical table names** (matched by sf2_interface.cpp):
- `"Wave"` — wave program table (2 columns per row: waveform byte, note byte)
- `"Pulse"` — pulse program table (3 columns: type/hi, mid, duration)
- `"Filter"` — filter program table (3 columns: type/hi, mid, resonance/bitmask)
- `"HR"` — hard restart table (driver 11: 16 rows in v11.00-11.04, 8 rows in v11.05)
- `"Arp"` — arpeggio table (1 column: value byte)
- `"Tempo"` — tempo table (driver 11.02+)
- `"Init"` — init table (driver-specific)
- Type=0x80: Instruments table
- Type=0x81: Commands table

---

## 6. Block 4: DriverInstrumentDescriptor

```
BYTE   descriptor_count   (N = number of column descriptions)
STRING descriptor[0]      (null-terminated label for column 0, e.g. "AD")
STRING descriptor[1]
...
STRING descriptor[N-1]
```

For driver 11: 6 entries = ["AD", "SR", "Flags", "Filter", "Pulse", "Wave"]

---

## 7. Block 5: MusicData

```
BYTE   track_count                           (number of voices, e.g. 3)
WORD   track_orderlist_pointers_lo_address   (abs addr of lo-byte table for OL pointers)
WORD   track_orderlist_pointers_hi_address   (abs addr of hi-byte table for OL pointers)
BYTE   sequence_count                        (total sequences, e.g. 128 or 256)
WORD   sequence_pointers_lo_address          (abs addr of lo-byte table for seq pointers)
WORD   sequence_pointers_hi_address          (abs addr of hi-byte table for seq pointers)
WORD   orderlist_size                        (size in bytes of each track's OL block)
WORD   orderlist_track1_address              (abs addr of track 1's order list data)
WORD   sequence_size                         (size in bytes of each sequence block)
WORD   sequence00_address                    (abs addr of sequence 0's data block)
```

The C++ host stores the addresses of the WORD fields above (not the values) separately
for runtime refresh (`MusicDataMetaDataEmulationAddresses`), because they can change when
the driver is relocated.

**Track N order list address:** `orderlist_track1_address + N * orderlist_size`
(0-indexed; track 1 = index 0)

**Sequence N address:** `sequence00_address + N * sequence_size`

Multi-song: total order list blocks = track_count * song_count. Songs are interleaved:
song 0 tracks 1-3, then song 1 tracks 1-3, etc.

---

## 8. Order List Packed Format (on-disk/in-RAM)

The order list is a packed byte stream. Max 256 bytes per block (one full order list).

```
Packed encoding:
  byte < 0x80 : sequence index to play (0x00..0x7F)
  byte >= 0x80: transposition byte. Value = (byte & 0x7F) - 0x20
                Range: $80 = transpose -32, $A0 = transpose 0 (identity), $BF = transpose +31
  byte == 0xFF: end-of-orderlist marker (loop). Next byte = packed loop index (byte offset into packed data)
  byte == 0xFE: end-of-orderlist marker (no loop / stop)
```

**Transposition encoding detail:**
In the unpacked model, each entry has a `m_Transposition` byte and `m_SequenceIndex`.
A new transposition byte is only emitted in the packed stream when it changes (run-length
suppressed). The identity (no transpose) is `0xA0`.

Initial virgin state of a track: `A0 00 FF 00` (transpose 0, seq 0, loop to start).

---

## 9. Sequence Packed Format (on-disk/in-RAM)

The sequence is a packed byte stream. Max 255 bytes per block ($FF = end of sequence).
MaxEventCount in the C++ model = 1024 (the unpacked model).

```
Packed byte roles:
  $00         : note off (gate off)
  $01..$6F    : note (MIDI-like note number, C4 would be some specific value)
  $70..$7D    : reserved (not used)
  $7E         : note on (gate on, hold previous note — "tie continuation")
  $7F         : end of sequence
  $80..$8F    : duration (0..15 extra ticks). Value = byte & 0x0F.
                Next tick will be note on (or note off for $00).
                This means the NOTE has (duration+1) ticks total.
  $90..$9F    : duration + tie note flag. Value & 0x0F = duration, tie=true.
                A tied note triggers gate on again but doesn't re-trigger the instrument.
  $A0..$BF    : set instrument. Instrument index = byte & 0x1F. (32 instruments max)
  $C0..$FF    : set command. Command index = byte & 0x3F. (64 commands max)
```

**Unpack algorithm (from datasource_sequence.cpp):**

Reading a sequence:
1. Read next byte.
2. If >= 0xC0: set command for this event. m_Command = byte. Read next byte.
3. If >= 0xA0: set instrument. m_Instrument = byte. Read next byte.
4. If >= 0x80: duration byte. duration = byte & 0x0F. tie = (byte & 0x10) != 0. Read next byte.
5. Now we have the note byte (< 0x80 or 0x7E/0x7F/$00).
6. If note == 0x7F: end of sequence.
7. Otherwise: emit event (instrument, command, note). Then emit `duration` more events
   as "continuation" events (no new instrument/command, note = 0x7E for held note or 0x00
   for note off continuation).

**Pack algorithm:**
Events with no instrument change ($80) and no command change ($80) collapse into
continuations. A duration byte is emitted only when it changes from the previous event's
duration. Instrument/command bytes are emitted only when they differ from the last value set.

---

## 10. Driver 11 — Instrument Format (6 bytes, column-major)

```
Byte 0 (col 0, "AD"):    Attack/Decay   (standard SID ADSR format)
Byte 1 (col 1, "SR"):    Sustain/Release
Byte 2 (col 2, "Flags"): Control flags:
    bit 7 (0x80): Hard restart enable
    bit 6 (0x40): Start filter program (uses filter table index in byte 3)
    bit 5 (0x20): [v11.03+] Enable filter on channel (combined with filter bitmask)
    bit 4 (0x10): Oscillator reset (waveform $09 used in first frame of note)
    bit 3 (0x08): [v11.05] Skip pulse reset on note-on (unless explicit instrument set)
    bits 0-2 (0x0X): Hard restart table index (0..7)
Byte 3 (col 3, "Filter"): Filter table index
Byte 4 (col 4, "Pulse"):  Pulse table index
Byte 5 (col 5, "Wave"):   Wave table index
```

The instrument table is ColumnMajor with row_count rows. So in memory:
- All AD values for all instruments are stored contiguously at `address`
- All SR values at `address + row_count`
- All Flags at `address + 2*row_count`
- etc.

---

## 11. Driver 11 — Command Table Format (2 columns, column-major)

The command table has 2 columns (col 0 = command type byte, col 1 = params byte).
ColumnMajor layout: all col-0 bytes at `address`, all col-1 bytes at `address + row_count`.

Command type byte encoding (from sf2_interface.h Command enum):

| Type byte | Name            | Params          | Notes |
|-----------|-----------------|-----------------|-------|
| 0x00      | Slide up/down   | XX YY = speed   | 16-bit; sign in XX |
| 0x01      | Vibrato         | XX=freq, YY=amp |       |
| 0x02      | Portamento      | XX YY = speed   | use 02 80 00 to disable |
| 0x03      | Arpeggio        | XX=speed, YY=arp_index |  |
| 0x04      | Fret slide      | XX=speed, YY=semitones | v11.01-11.04 only |
| 0x08      | ADSR local      | AD, SR          | lasts until next note |
| 0x09      | ADSR instrument | AD, SR          | lasts until instrument change |
| 0x0A      | Filter index    | --, XX          | start filter program |
| 0x0B      | Wave index      | --, XX          | start wave program |
| 0x0C      | Pulse index     | --, XX          | v11.02+ only |
| 0x0D      | Tempo           | --, XX          | v11.02+ only |
| 0x0E      | Main volume     | --, 0X          | v11.02+, X=0..F |
| 0x0F      | Demo flag       | --, XX          | timing for demo effects |

**Note on T (nibble) vs T (full byte):** In the sequence editor, commands are stored as
indices 0x00..0x3F into the command table. The command table row's type byte tells what
kind of effect this command slot performs. The sequence stores $C0 + index, which gives
0xC0..0xFF in the packed sequence stream.

**Note delay (v11.04):** Special case — encoded differently. A `T`-nibble value (0..15) is
the delay in ticks. NOT a standard command table entry.

---

## 12. Driver 11 — Wave Table Format (2 columns, row-major)

```
Row encoding:
  col 0 = waveform byte (any SID waveform + control flags)
  col 1 = note offset byte:
    0x00..0x7F: relative semitone offset (added to sequence note)
    0x80..0xDF: absolute semitone value ($80 = note 0, use for drums etc.)

Special row: col0 = 0x7F = jump to index. col1 = target row index.
  (Jumping to own index = end the program)
```

---

## 13. Driver 11 — Pulse Table Format (3 columns, row-major)

```
Row byte 0 (high nibble X, low nibble bits):
  X >= 8: set pulse width to XXX (12-bit absolute value)
    byte0 = 0x8X (upper bit set), byte1 = YY (middle 8 bits), byte2 = ZZ (duration)
    Actually: high byte = byte0 & 0x0F, middle byte = byte1, forming 12-bit pulse width
  X < 8: add to pulse width (signed 12-bit delta)
    byte0 = 0x0X, byte1 = YY = "add XXX to current pulse"
  byte0 = 0x7F: jump. byte2 = target index.
```

**Exact encoding (3 bytes per row):**
```
8X XX YY  : set pulse width to XXX (12-bit), YY = duration frames
0X XX YY  : add XXX (12-bit signed delta) to pulse, YY = duration frames
7f -- XX  : jump to row index XX
```
(jump to own index = end program)

---

## 14. Driver 11 — Filter Table Format (3 columns, row-major)

```
XY YY RB  : set filter
  X = passband type (must be > 8, i.e. 9..F for a filter command)
  YYY = 12-bit cutoff frequency (X nibble + 2 bytes)
  R = resonance (4-bit, $0..$F)
  B = channel select bitmask (voice enable flags)
0X XX YY  : add to cutoff
  XXX = 12-bit signed delta
  YY = duration frames
7f -- XX  : jump to row index XX (jump to self = end program)
```

---

## 15. Driver 11 — Arpeggio Table Format (1 column, row-major)

```
0x00..0x6F : add this value in semitones to current note
0x70..0x7F : jump to (start_index + X) where X = low nibble
             (relative jump — enables arpeggio pattern entry point selection)
```

The command `T3 XX YY` specifies speed (XX) and starting index (YY) into the arp table.
A `7X` jump adds X to the starting index — so index 0 catches `70`, index 1 catches `71`, etc.

---

## 16. Driver 12 — Instrument Format (4 bytes)

```
Byte 0: AD
Byte 1: SR
Byte 2: Waveform
Byte 3: Pulse width XY (X=middle 4 bits, Y=top 4 bits of 12-bit pulse width)
```

Commands: slide up/down (0X XX, 12-bit speed), slide down (1X XX), vibrato (2X -Y).

---

## 17. Driver 13 — Instrument Format (7 bytes, Hubbard emulation)

```
Byte 0: AD
Byte 1: SR
Byte 2: Waveform
Byte 3: Pulse width XY (X=pulsating speed, Y=high nibble start PW)
Byte 4: Pulse sweep range
Byte 5: Flags
    8X: alternate arpeggio (X = semitones, also set byte 6)
    40: dive effect
    20: ignore order list transposition
    10: add noise at start of note
Byte 6: Arp properties XY (X=regularity, Y=speed)
```

---

## 18. Driver 14 — Instrument Format (6 bytes, like driver 11 but different flags)

```
Byte 0: AD
Byte 1: SR
Byte 2: Flags
    80: "immediate response" hard restart
    40: start filter program
Byte 3: Filter table index
Byte 4: Pulse table index
Byte 5: Wave table index
```

Driver 14 differences from driver 11: enables very short gate-off durations at cost of
potential instability. Different hard-restart mechanism.

---

## 19. Driver 15 / 16 — Instrument Format (5 bytes, tiny driver)

```
Byte 0: AD
Byte 1: SR
Byte 2: Pulse width XY (X=middle 4 bits, Y=top 4 bits)
Byte 3: Linear pulse sweep XY (X=add to mid 4, Y=add to top 4)
Byte 4: Wave table index
```

Driver 15 has commands: slide up/down, vibrato, and (v15.02) wave program pointer.
Driver 16 has NO commands. Hard restart always on in both.
Zero-page variables (vs driver 11/12 which use regular RAM variables).

---

## 20. IRQ Routine (appended after song data)

The editor appends a fixed ~58-byte IRQ stub when saving. From `InsertIRQ()` in
`driver_utils.cpp`. It:
1. Calls driver init with `JSR init_address` (with A=song_index?)
2. Sets up CIA timer interrupt
3. The IRQ itself calls `JSR update_address` each frame
4. Increments $D020 (border color) as a visual activity indicator

The stub also needs the driver's addresses patched in at fixed byte offsets.

---

## 21. Auxiliary Data Format

Appended after the IRQ routine. Pointed to by $0FFB (and init_address - 5).

This is a serialized collection of typed blocks. Each `AuxilaryData` subclass has a type
enum and serializes itself. Types include:
- Songs: song count, selected song, per-song name strings
- HardwarePreferences: SID model (6581/8580), PAL/NTSC
- EditingPreferences
- PlayMarkers
- TableText: per-row label strings for each table (by table ID)

The exact binary format of the auxiliary data is NOT directly documented in the header
files reviewed. It uses AuxilaryDataCollection::Save/Load. OPEN: parse auxilary_data_collection.cpp.

---

## 22. Note Number Convention

From the sequence unpack code:
```
$00      = note off (gate off, silence)
$01..$6F = note values 1..111
$7E      = note on / gate on (hold/tie continuation)
$7F      = end of sequence
```

OPEN: The exact MIDI-to-note-number mapping (what note number = C4?) requires checking
the driver's note table or the frequency lookup logic. The wave table relative offset
(0x00..0x7F) and absolute offset (0x80..0xDF, where $80 = lowest) also imply a range.

---

## 23. Known HVSC distribution

SF2 music in HVSC is stored as PSID/RSID files. The SF2 driver is the 6502 player code.
SIDID likely identifies these tunes by byte patterns in the driver binary.
OPEN: Confirm the SIDID pattern for SF2 driver 11 family.
