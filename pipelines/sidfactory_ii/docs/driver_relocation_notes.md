---
source_url: https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/packer/packer.cpp
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity) / Jens-Christian Huus (JCH) / Michel de Bree (Youth)
content_date: 2020–2026
reliability: primary
---

# SID Factory II — Driver Relocation Notes

This document describes how the SF2 editor (via `Editor::Packer`) relocates a driver
binary from its "compiled-in" base address to an arbitrary destination address when
exporting a SID file.

Source: `SIDFactoryII/source/runtime/editor/packer/packer.{h,cpp}` and
`packing_utils.{h,cpp}`.

---

## 1. Overview

The SF2 driver `.prg` files are compiled to a fixed base address (the `driver_code_top`
address stored in `ID_Descriptor`). When a song is exported, the driver + music data
is relocated to whatever destination address the user specifies. The `Packer` class
performs all required fixups in a single pass.

The relocation produces a new `C64File` at the destination address containing:
- Driver 6502 code (with all internal absolute address references updated)
- Data tables (instrument, command, wave, pulse, filter, etc.)
- Order lists
- Sequences
- (Optionally) IRQ wrapper appended at the end

---

## 2. Address Delta

```
m_DestinationAddressDelta = m_DestinationAddress - m_DriverInfo.GetDescriptor().m_DriverCodeTop
```

All absolute addresses in the driver that reference code or data within the driver
are adjusted by this delta. Addresses in the I/O range `$D000–$DFFF` (SID registers,
CIA, VIC) are **not** adjusted — they go through `GetRelocatedVector()` which applies
custom mapping for those hardware addresses instead.

---

## 3. ProcessDriverCode() — The Relocation Engine

Walks the driver code byte-by-byte from `driver_code_top` to
`driver_code_top + driver_code_size`, decoding each opcode:

### 3a. Absolute Address Relocation

Opcodes using **absolute addressing modes** (ABS, ABX, ABY, IND):
- Read the embedded 2-byte little-endian address.
- If the address is in `$D000–$DFFF`: apply `GetRelocatedVector()` (hardware mapping).
- Otherwise: add `m_DestinationAddressDelta` to the address and write it back.

These opcodes are 3 bytes each (opcode + 2-byte address).

### 3b. Zero Page Relocation

Opcodes using **zero-page addressing modes** (ZP, ZPX, ZPY, IZX, IZY):
- Read the embedded 1-byte zero-page address.
- Compute `zero_page_base = zp_address - m_CurrentLowestZP`.
- Write back `target_zero_page_base + zero_page_base`.

This remaps the driver's ZP usage from whatever zero-page range it was compiled for
to a new range at the destination. `m_CurrentLowestZP` is found by
`GetZeroPageRangeFromDriver()` (scans the driver for the lowest ZP address used).

### 3c. Non-Relocating Opcodes

All other addressing modes (immediate, relative, implied, accumulator) are left
untouched.

---

## 4. Data Section Management

The packer maintains a `m_DataSectionList` of sections, each with:
- Source address in C64 memory (where the editor currently has the data)
- Data size in bytes
- Destination address in the output file (computed after sorting)

Sections are sorted by source address, then `ComputeDestinationAddresses()` assigns
consecutive output addresses starting from `destination_address + driver_code_size`,
preserving relative order.

Data copied includes:
- **Tables** (fetched by `FetchTables()`): each `TableDefinition`'s data block
  at `table_definition.m_Address`, size = `row_count × column_count`
- **Order list pointer tables** (lo-byte and hi-byte arrays): `FetchOrderListPointers()`
- **Sequence pointer tables** (lo-byte and hi-byte arrays): `FetchSequencePointers()`
- **Order lists**: each `order_list_size`-byte block: `FetchOrderLists()`
- **Sequences**: each `sequence_size`-byte block: `FetchSequences()`

After the destination addresses are computed, `AdjustOrderListPointers()` and
`AdjustSequencePointers()` rewrite the pointer tables in the output to point to the
new relocated addresses.

---

## 5. Table Data Layout in Output

For ColumnMajor tables (dominant in Driver 11), the packed output is:

```
col_0_row_0, col_0_row_1, ..., col_0_row_{N-1},
col_1_row_0, col_1_row_1, ..., col_1_row_{N-1},
...
col_{M-1}_row_0, ...
```

Where N = `row_count`, M = `column_count`. Total size = `N × M` bytes.

For RowMajor tables:

```
row_0_col_0, row_0_col_1, ..., row_0_col_{M-1},
row_1_col_0, ...
```

---

## 6. Order List and Sequence Pointer Tables

The driver locates order lists and sequences via two split lo/hi pointer tables
(C64 indirect-indexed addressing pattern):

```
LDA orderlist_ptrs_lo,X   ; X = track index
STA ptr+0
LDA orderlist_ptrs_hi,X
STA ptr+1
; ... then use (ptr),Y to read orderlist bytes
```

Similarly for sequences. After relocation, both pointer tables are rewritten to
contain the new absolute addresses of the relocated order list / sequence blocks.

The `m_TrackOrderListPointersLowAddress` and `m_TrackOrderListPointersHighAddress`
from `ID_MusicData` are the source addresses; the packer writes updated values
into the output at the corresponding relocated positions.

---

## 7. Multi-Song Patch

When `AuxilaryDataSongs.GetSongCount() > 1`, the packer calls `ApplyMultiSongPatch()`.

This injects a small 6502 stub into the output file that:
1. Reads a song-index variable (in ZP or a fixed location).
2. Uses it to load the correct set of order list pointers for the selected song.
3. Patches the player's order list pointer table fetch vector to go through
   the injected stub instead.

The injected machine code's pointer references are patched by the multi-song logic
before writing, so that it points to the correct song's set of order lists in the
relocated output.

---

## 8. GetRelocatedVector() — Hardware Address Mapping

For absolute addresses in `$D000–$DFFF` encountered in the driver code:
- SID registers (`$D400–$D418`) are left as-is (they are hardware-fixed on C64).
- Other I/O addresses (CIA `$DC00/$DD00`, VIC `$D000`) may similarly be preserved.
- The function applies a "custom mapping" — the exact mapping logic needs RE from
  the compiled `packer.cpp`. Behavior observed: hardware addresses are preserved
  unchanged, since `$D000–$DFFF` is always the I/O space on C64 regardless of
  where the driver code lives.

---

## 9. Zero Page Allocation Strategy

`GetZeroPageRangeFromDriver()` (in `packing_utils.cpp`) scans the driver binary for
all ZP-mode accesses and returns the `[lowest_zp, highest_zp]` range used.

The user (or the editor's export dialog) specifies a `target_zero_page_base`, and the
packer relocates all ZP references to start at that base:

```
new_zp_address = target_zero_page_base + (old_zp_address - lowest_zp_in_driver)
```

This means the driver's ZP footprint is a contiguous block whose size is
`highest_zp - lowest_zp + 1`. Choosing an overlapping ZP range for two drivers
would cause conflict. For Driver 11 the ZP usage is moderate (voice state arrays
and work registers); the exact range requires reading from the binary.

---

## 10. IRQ Wrapper

`DriverUtils::InsertIRQ()` appends 58 bytes of machine code to the output, patching
in `m_InitAddress` and `m_UpdateAddress` (already relocated):

```asm
; Pseudo-disassembly of the 58-byte IRQ wrapper (irq_assembly[]):
; Offset 00:
  LDA #<driver_init_lo        ; irq_assembly[01] = lo(init_address)
  JSR driver_init             ; irq_assembly[03/04] = relocated init_address
  SEI
  LDX #$00
  STX $DC0E                   ; CIA1 timer A stop
  INX
  STX $D01A                   ; VIC raster IRQ enable
  LDA #<irq_handler           ; irq_assembly[10] = lo(irq_address)
  STA $0314                   ; IRQ vector lo
  LDA #>irq_handler           ; irq_assembly[15] = hi(irq_address)
  STA $0315                   ; IRQ vector hi
  LDA #$32                    ; raster line 50
  STA $D012                   ; VIC raster line trigger
  CLI
  RTS

; irq_handler (at irq_vector + $20):
  LDA #$1B
  STA $D011                   ; ensure $D011 bit 7 clear
  NOP × 6
  INC $D020                   ; border flash (debug?)
  JSR driver_update           ; irq_assembly[0x2F/0x30] = relocated update_address
  DEC $D020
  ROR $D019                   ; ACK raster IRQ
  JMP $EA31                   ; standard C64 IRQ exit
```

The `irq_address` is set to `irq_vector + 0x0020` (32 bytes into the injected block),
where `irq_vector` is the write address at the time `InsertIRQ()` is called (i.e. the
end of the packed data).

---

## 11. Implications for USF Decompiler

When writing a USF decompiler/converter for SF2 files:

1. **Parse the descriptor block chain** (see `driver_descriptor_format.md`) to locate
   all data tables, order lists, and sequences.

2. **The driver code itself is not needed** for USF extraction — only the music data
   tables (instruments, wave, pulse, filter, arpeggio, HR) and song structure
   (order lists, sequences) are needed.

3. **Relocation is transparent**: the packer has already applied all fixups; reading
   the exported SID file gives you relocated absolute addresses. But the descriptor
   block chain was written at load time using the *pre-relocation* addresses stored
   in `ID_MusicData`. After loading into memory, `RefreshMusicData()` is called to
   re-read the four self-updating pointer fields from the running emulation memory —
   this gives the *post-relocation* actual addresses.

4. **For static analysis of an SF2 SID file** (without running the emulator), the
   approach is:
   a. Find the `0x1337` magic at the PRG load address.
   b. Parse the block chain to get pre-relocation `ID_MusicData` addresses.
   c. Compute `delta = actual_load_address - m_DriverCodeTop` from `ID_Descriptor`.
   d. Add delta to all addresses from the block chain to get the actual in-SID addresses.
   e. Read tables and music data from those addresses.

5. **Zero-page layout**: the driver uses ZP for voice state; the specific bytes are
   not needed for data extraction (only for runtime RE or init-write reproduction).

---

## Leads to Follow

1. **Python parser for the block chain** — write a small parser that:
   - Finds the `0x1337` magic in a `.sid` or `.prg`
   - Walks blocks 1–9 and dumps all addresses and sizes
   - Computes the relocation delta
   - Dumps table contents
   This is the foundation for the SF2 USF extractor.

2. **GetRelocatedVector() exact logic** — the behavior for `$D000–$DFFF` addresses
   inside the driver code. Fetch `packer.cpp` in full (the summarized version didn't
   show the actual function body). OPEN: fetch raw `packer.cpp` and search for
   `GetRelocatedVector`.

3. **Multi-song patch injected bytes** — the `ApplyMultiSongPatch()` exact machine
   code and how the song-index variable is identified. Important if we need to support
   multi-song SF2 files (where multiple songs share one driver). OPEN: fetch full
   `packer.cpp`.

4. **ZP range for Driver 11** — determined by disassembling `sf2driver11_05.prg`
   and scanning ZP accesses, or by running `GetZeroPageRangeFromDriver()` on the binary.
   Needed to know which ZP bytes the driver's init writes.

5. **Auxiliary data round-trip** — the aux data at `0x0FFB` contains song names, play
   markers, and editor preferences. For USF extraction, only `AuxilaryDataSongs` matters
   (song count). Fetch and read `auxilary_data_collection.cpp` and `auxilary_data_songs.cpp`
   to understand the serialization format.
