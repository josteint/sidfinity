---
source_url: https://github.com/Chordian/sidfactory2 (packer.cpp, packer.h, psidfile.cpp, psidfile.h, c64file.cpp, driver_info.h, driver_info.cpp)
fetched_via: direct
fetch_date: 2026-06-13
author: Jens-Christian Huus (Chordian)
content_date: unknown (master branch as of 2026-06-13)
reliability: primary
---

# SID Factory II — Packed / Exported Binary Format

Source code: `SIDFactoryII/source/runtime/editor/packer/packer.cpp` + `psidfile.cpp`.
Full source saved at `docs/src/packer_cpp.cpp` and `docs/src/psidfile_cpp.cpp`.

## Overview

The SF2 editor packs a tune via `Packer` (in-editor) → `PSIDFile` (wraps in PSID header) → saved to disk as a `.sid` file. The C64 binary carried inside is a PRG (load-address word prepended), containing the driver code followed by packed music data — **no editor metadata, no 0x1337 descriptor block**.

## Step-by-step: what Packer does

### 1. Setup

```
m_DestinationAddressDelta = inDestinationAddress - m_DriverInfo.GetDescriptor().m_DriverCodeTop
```

The packer operates by building a container initially at the *original* driver source address and then calling `MoveDataToTopAddress(destinationAddress)` at the end to shift it. All internal address fixups during construction use `+ m_DestinationAddressDelta` to account for the relocation.

### 2. Data sections collected

Each logical block is recorded as a `DataSection { SourceAddress, SourceSize, DestinationAddress }`:

| Section | What |
|---------|------|
| Tables (instruments, commands, generic) | Each column of a ColumnMajor table becomes one section; RowMajor tables are one section. Rows beyond highest used are trimmed. |
| Order-list pointer arrays (low, high) | One entry per track. Size = `m_TrackCount` bytes each. |
| Sequence pointer arrays (low, high) | One entry per sequence used. Size = `HighestSequenceIndexUsed + 1`. |
| Order lists | `TrackCount * SongCount` order lists. Each trimmed to its actual length. |
| Sequences | 0..HighestSequenceIndexUsed, each trimmed to actual length. |

All sections are **sorted by source address** before destination addresses are computed. They are then packed **consecutively** immediately after the driver code blob (no gaps, no alignment).

### 3. Output binary layout

```
[driver_code_top]
  driver code bytes       (m_DriverCodeSize bytes, verbatim copy)
  [driver_code_top + m_DriverSize]
  data section 0          (sorted by original source address)
  data section 1
  ...
  data section N
  [if multi-song:]
  order-list pointer table (all songs × tracks × 2 bytes for lo+hi)
  multi-song patch code   (32 bytes, see below)
[destination_address end]
```

Key fields from `Descriptor`:
- `m_DriverCodeTop`: where the driver code starts in C64 memory (also the PRG load address if no relocation). This is where the 0x1337 block chain lives in the in-editor .sid/.c64 file.
- `m_DriverCodeSize`: size of just the executable code (used for the disassembly walk in `ProcessDriverCode`).
- `m_DriverSize`: size of the driver code + any driver-internal data tables (the whole blob copied verbatim before the packer's own data sections).

### 4. Address fixups (`ProcessDriverCode`)

The packer walks the *driver code* region byte-by-byte as a 6502 disassembly:

- **Absolute/indexed/indirect addressing** (`am_ABS`, `am_ABX`, `am_ABY`, `am_IND`): reads the 2-byte operand; if the address is in $D000-$DFFF (SID/IO) it calls `GetRelocatedVector()` (data-section lookup, for data tables that live in that range); otherwise calls `GetRelocatedVector()` + adds `m_DestinationAddressDelta`. Result replaces the operand.
- **Zero-page addressing** (`am_ZP`, `am_ZPX`, `am_ZPY`, `am_IZX`, `am_IZY`): reads the ZP byte, computes `zero_page_base = zp - m_CurrentLowestZP`, then stores `zero_page_base + m_LowestZP` (the user-chosen new lowest ZP). Allows the entire driver ZP frame to be relocated.

`GetRelocatedVector(addr)` checks whether `addr` falls inside any `DataSection.SourceAddress..SourceAddress+SourceSize` range; if so, returns `DataSection.DestinationAddress + (addr - DataSection.SourceAddress)`. Falls through to `addr` unchanged if not found (absolute references to outside the packed block are left as-is).

### 5. Order-list and sequence pointer fixup

After copying all data, the packer patches the in-packed order-list and sequence pointer arrays:

- For each order list: `destination + m_DestinationAddressDelta` is written into the low/high pointer arrays (which are now at their packed positions).
- For each sequence: same pattern.

This is what makes the standalone .sid self-consistent — all internal cross-references are updated to absolute C64 addresses at the chosen relocation target.

### 6. Final step: MoveDataToTopAddress

```cpp
m_OutputData->MoveDataToTopAddress(m_DestinationAddress);
```

`MoveDataToTopAddress` physically shifts the byte buffer so that `m_TopAddress` becomes `m_DestinationAddress`. The actual data content was already prepared for `m_DestinationAddress` throughout construction; this step just ensures the PRG load-address word at bytes [0..1] of the output also reflects the destination. Result: a valid C64 PRG file.

## PSID wrapper

`PSIDFile` wraps the PRG in a standard PSID v2 header (0x7C bytes):

| Field | Value |
|-------|-------|
| Magic | "PSID" |
| Version | 0x0002 (big-endian) |
| DataOffset | 0x007C |
| LoadAddress | 0x0000 → load address embedded in PRG bytes [0..1] |
| InitAddress | `driver_address + inInitOffset` — absolute C64 address of the init routine |
| UpdateAddress | `driver_address + inUpdateOffset` — absolute C64 address of the play routine |
| SongCount | number of songs (multi-song) |
| DefaultSong | 1 (always) |
| SpeedFlags | 0x00000000 → VBlank for ALL subtunes |
| Title/Author/Copyright | 32-char each, from editor metadata |
| Flags | SID model (0x10=6581, 0x20=8580) | clock (0x04=PAL, 0x08=NTSC), big-endian |

`driver_address` is read from bytes [0..1] of the PRG data (little-endian), i.e. the relocated destination address. `inInitOffset` and `inUpdateOffset` are offsets from that load address to the init and play entry points within the driver — these come from `DriverCommon.m_InitAddress` and `.m_UpdateAddress` as known to the driver descriptor.

## CRITICAL VERDICT: Does the 0x1337 descriptor block survive export?

**NO.** The 0x1337 descriptor block chain does NOT appear in the exported HVSC .sid.

Evidence from the code:
1. `CopyDataToOutputContainer()` copies only: (a) driver code (`m_DriverCodeTop` .. `m_DriverCodeTop + m_DriverSize`), and (b) the packed data sections (tables, order lists, sequences). Nothing else from the C64 memory image is copied.
2. The 0x1337 magic number is read by `DriverInfo::Parse()` at `inFile.GetTopAddress()` — i.e., the very first two bytes of the *in-editor* C64 file. In the exported binary the first two bytes of the PRG are the load address; the driver code starts immediately after. The driver code does NOT begin with 0x1337 — that is editor metadata preceding the driver.
3. `ParseAuxilaryData()` reads auxiliary data from `GetWord(0x0FFB)` — a pointer stored at a fixed editor-convention address. The packer never copies anything from address $0FFB or from the aux data region into the output.
4. The `AuxilaryDataCollection` (song names, hardware prefs, play markers, table labels) is accessed by the packer only to read `GetSongs().GetSongCount()` — it is never written to the output container.

**Consequence for HVSC extraction:** An extractor reading an HVSC SF2 .sid file CANNOT use the 0x1337 block chain to locate tables. It must use an alternative strategy — see the "Extractor strategy" section below.

## Extractor strategy for HVSC SF2 .sid files

The exported binary has NO self-describing metadata. The only anchors are:

1. **PSID header fields**: `InitAddress` and `UpdateAddress` give absolute C64 addresses of init and play. These are the primary entry points.

2. **Driver fingerprinting**: The driver code blob is a nearly-verbatim copy of the standard SF2 driver binary (modulo ZP relocation and absolute-address fixup). Fingerprinting against known driver versions (from HVSC's SIDID rules or from the editor's `drivers/` directory) identifies driver version, which in turn provides the fixed-offset positions of all internal tables relative to the driver load address.

3. **Driver-internal table pointers**: The driver code contains `m_TrackOrderListPointersLowAddress`, `m_SequencePointersLowAddress` etc. as addresses operands in known instruction locations. After fingerprinting the driver version, these can be read at known fixed offsets within the driver code.

4. **Sequence/order-list pointer tables**: Once the locations above are known, iterating the pointer tables gives absolute C64 addresses of all order lists and sequences directly.

5. **MusicDataMetaDataEmulationAddresses** (from `driver_info.cpp`): The editor records the emulation addresses of the sequence-pointers and order-list-track-1 fields WITHIN the driver descriptor block, used for live in-editor refresh. In HVSC files these fields don't exist, but the equivalent information is derivable from the driver fingerprint: the sequence pointer low/high tables and order-list table start are at driver-version-specific fixed offsets within the driver code/data.

## Leads to follow
See `packed_auxiliary_data.md` and `packed_multisong.md`.
