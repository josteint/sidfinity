---
source_url: https://github.com/Chordian/sidfactory2, https://github.com/cadaver/sidid/blob/master/sidid.cfg, https://github.com/WilfredC64/player-id
fetched_via: direct
fetch_date: 2026-04-11
author: Jens-Christian Huus (Chordian/JCH) — SIDFactory II; Lasse Oorni (Cadaver) — sidid; Wilfred/HVSC — player-id
content_date: 2020-2025 (SIDFactory II active development); 1991-present (sidid signatures)
reliability: primary
notes: multiple sources — SIDFactory II JCH converter source code (primary: actual working parser for the closest relative format), sidid.cfg signatures (primary: byte-pattern identification), and WilfredC64/player-id (primary: same config). No public DMC source code or DMC-specific converter exists; JCH NP20 converter is the closest architectural reference. Other tools examined (ChiptuneSAK, SIDdecompiler, desidulate, libsidplayfp) have no DMC-specific parsing.
---

# DMC Format: External Source Code and Tools Reference

Collected 2026-04-11. Research into open-source implementations that parse, convert, or identify DMC (Demo Music Creator) files for the Commodore 64.

---

## 1. SIDFactory II -- JCH (NP20) Converter

**Repository:** https://github.com/Chordian/sidfactory2
**Files:**
- `SIDFactoryII/source/runtime/editor/converters/jch/converter_jch.h`
- `SIDFactoryII/source/runtime/editor/converters/jch/converter_jch.cpp`

**Context:** SIDFactory II is by Jens-Christian Huus (JCH), who also created the JCH NewPlayer (NP20) format. JCH NewPlayer is the direct successor/evolution of DMC -- same author lineage (Brian/Graffity created DMC, JCH extended it). The NP20 format shares the same fundamental architecture as DMC: sectors/sequences, orderlists with transposition, wave/pulse/filter tables, command tables with instrument references, and duration-based note encoding.

**SIDFactory II does NOT have a DMC converter** -- it has converters for GT (GoatTracker), CC (CheeseCutter), JCH (NP20), and MOD. But the JCH converter is the closest reference to DMC format since both formats share the same design heritage.

### JCH NP20 Format Identification

```cpp
// Load address must be $0F00
// Version signature at $0FEE: "20.G" (ASCII: '2','0','.','G')
bool ConverterJCH::CanConvert(const void* inData, unsigned int inDataSize) const
{
    if (inDataSize < 0x10000)
    {
        const unsigned short destination_address =
            Utility::C64File::ReadTargetAddressFromData(inData, static_cast<unsigned short>(inDataSize));
        if (destination_address == 0x0f00)
        {
            auto file = Utility::C64File::CreateFromPRGData(inData, inDataSize);
            unsigned char version_1 = file->GetByte(0x0fee + 0); // '2'
            unsigned char version_2 = file->GetByte(0x0fee + 1); // '0'
            unsigned char version_3 = file->GetByte(0x0fee + 2); // '.'
            unsigned char version_4 = file->GetByte(0x0fee + 3); // 'G'
            if (version_1 != '2' || version_2 != '0' ||
                version_3 != '.' || version_4 != 'G')
                return false;
            return true;
        }
    }
    return false;
}
```

### JCH NP20 Pointer Table Layout (all relative to $0F00 base)

| Address | Field |
|---------|-------|
| $0FA6 | Init data base address (speed at +6) |
| $0FBA | Fine tune setting |
| $0FBC | Wave table pointer (16-bit) |
| $0FC0 | Filter table pointer (16-bit) |
| $0FC2 | Pulse table pointer (16-bit) |
| $0FC4 | Instrument table pointer (16-bit) |
| $0FC6 | Orderlist V1 pointer (16-bit) |
| $0FC8 | Orderlist V2 pointer (16-bit) |
| $0FCA | Orderlist V3 pointer (16-bit) |
| $0FCC | Sequence vector low pointer (16-bit) |
| $0FCE | Sequence vector high pointer (16-bit) |
| $0FD0 | Command table pointer (16-bit) |
| $0FEE | Version string "20.G" |

```cpp
void ConverterJCH::GatherInputInfo()
{
    m_InputInfo.m_FineTuneAddress = m_InputData->GetWord(0x0fba);
    m_InputInfo.m_WaveTableAddress = m_InputData->GetWord(0x0fbc);
    m_InputInfo.m_FilterTableAddress = m_InputData->GetWord(0x0fc0);
    m_InputInfo.m_PulseTableAddress = m_InputData->GetWord(0x0fc2);
    m_InputInfo.m_InstrumentTableAddress = m_InputData->GetWord(0x0fc4);
    m_InputInfo.m_CommandTableAddress = m_InputData->GetWord(0x0fd0);
    m_InputInfo.m_OrderlistV1Address = m_InputData->GetWord(0x0fc6);
    m_InputInfo.m_OrderlistV2Address = m_InputData->GetWord(0x0fc8);
    m_InputInfo.m_OrderlistV3Address = m_InputData->GetWord(0x0fca);
    m_InputInfo.m_SequenceVectorLowAddress = m_InputData->GetWord(0x0fcc);
    m_InputInfo.m_SequenceVectorHighAddress = m_InputData->GetWord(0x0fce);
    m_InputInfo.m_SpeedSettingAddress = m_InputData->GetWord(0x0fa6) + 6;
}
```

### JCH NP20 Table Import

**Instrument and Command tables** are stored in **row-major** order in JCH and must be transposed to **column-major** for SIDFactory II:

```cpp
bool ConverterJCH::ImportTables()
{
    // Instrument table: row-major -> column-major
    CopyTableRowToColumnMajor(m_InputInfo.m_InstrumentTableAddress,
        table->m_Address, table->m_RowCount, table->m_ColumnCount);

    // Command table: row-major -> column-major (2 columns)
    CopyTableRowToColumnMajor(m_InputInfo.m_CommandTableAddress,
        table->m_Address, table->m_RowCount, table->m_ColumnCount);

    // Wave, Pulse, Filter tables: direct copy (already column-major)
    CopyTable(m_InputInfo.m_WaveTableAddress, table->m_Address, size);
    CopyTable(m_InputInfo.m_PulseTableAddress, table->m_Address, size);
    CopyTable(m_InputInfo.m_FilterTableAddress, table->m_Address, size);
}
```

### JCH NP20 Orderlist Format

Each orderlist entry is 2 bytes: **[transpose, sequence_index]**

- Transpose $FF = end of orderlist
- Transpose is stored as offset: destination = 0x20 + source_transpose
- 3 parallel voices (V1, V2, V3)

```cpp
unsigned int ConverterJCH::ImportOrderLists()
{
    for (int i = 0; i < 3; ++i)
    {
        for (int offset = 0; offset < orderlist_max_length; offset += 2)
        {
            const unsigned char transpose = m_InputData->GetByte(read_address + offset);
            const unsigned char sequence_index = m_InputData->GetByte(read_address + offset + 1);

            if (transpose == 0xff)  // End marker
            {
                entry.m_Transposition = 0xff;
                entry.m_SequenceIndex = 0x00;
                break;
            }

            entry.m_Transposition = 0x20 + transpose;  // Bias by $20
            entry.m_SequenceIndex = sequence_index;
        }
    }
}
```

### JCH NP20 Sequence Format

Sequences are stored as (command, note) byte pairs. Max 128 events (256 bytes) per sequence.

- `command == 0x7F`: end of sequence
- `command >= 0xC0`: command byte (instrument = 0x80 = none)
- `command < 0xC0`: instrument index (command = 0x80 = none)

```cpp
void ConverterJCH::ImportSequence(unsigned short inReadAddress,
    std::shared_ptr<DataSourceSequence>& inWriteDataSource)
{
    for (unsigned short i = 0; i < 0x100; i += 2)
    {
        unsigned char command = m_InputData->GetByte(inReadAddress + i);
        unsigned char note = m_InputData->GetByte(inReadAddress + i + 1);

        if (command == 0x7f) break;  // End marker

        if (command >= 0xc0)
        {
            event.m_Command = command;       // Command byte
            event.m_Instrument = 0x80;       // No instrument
        }
        else
        {
            event.m_Command = 0x80;          // No command
            event.m_Instrument = command;    // Instrument index
        }
        event.m_Note = note;
    }
}
```

### JCH NP20 Tempo Table

Tempo commands ($E0 prefix in command table) reference tempo values. The converter builds a tempo lookup table:

```cpp
bool ConverterJCH::BuildTempoTableAndCorrectTempoCommands(
    const DriverInfo::TableDefinition& inCommandTable)
{
    // Default tempo from speed setting address
    const unsigned char default_tempo =
        std::max<unsigned char>((*m_InputData)[m_InputInfo.m_SpeedSettingAddress], 1);

    // If tempo >= 2: single byte entry
    // If tempo < 2 (multispeed): 2-byte pair from filter table address
    if (default_tempo >= 2)
        tempo_table_values.push_back(default_tempo);
    else
    {
        tempo_table_values.push_back((*m_InputData)[m_InputInfo.m_FilterTableAddress + 1]);
        tempo_table_values.push_back((*m_InputData)[m_InputInfo.m_FilterTableAddress + 0]);
    }
    tempo_table_values.push_back(0x7f);  // Entry terminator

    // Each tempo command references an index into this table
    for (const auto& tempo_command : m_TempoCommandInfoList)
    {
        // Remap to offset into new table
        (*m_OutputData)[column_2_address + tempo_command.command_index] =
            static_cast<unsigned char>(tempo_table_values.size());
        // ... add tempo bytes + 0x7f terminator
    }
}
```

---

## 2. SIDFactory II -- CheeseCutter (CC/CT) Converter

**Files:**
- `SIDFactoryII/source/runtime/editor/converters/cc/converter_cc.cpp`
- `SIDFactoryII/source/runtime/editor/converters/cc/source_ct.cpp`

### CheeseCutter Format Identification

```cpp
// Magic: first 3 bytes == "CC2"
bool ConverterCC::CanConvert(const void* inData, unsigned int inDataSize) const
{
    if (inDataSize >= 3)
    {
        if (memcmp("CC2", inData, 3) == 0)
            return true;
    }
    return false;
}
```

### CheeseCutter CT Format Key Details

- File is MZ-compressed; decompresses to ~0x50000 bytes
- Version byte at offset 0x10000 (valid: 6-127)
- Tempo table address at offset 0x0FDC
- Instrument descriptions at offset 0x101A5 (32 bytes each)
- 0x30 instruments, 0x80 sequences with 0x40-row entries
- 0x40-row command table with vibrato, portamento, ADSR mappings
- Order lists for 3 channels, using address pointer pairs
- Sequence command bytes: 0x40+ = pulse index, 0x60+ = filter index, 0x80+ = chord/arpeggio
- Wave table has delay commands E0-EF that expand into repeated waveforms

---

## 3. SIDFactory II -- GoatTracker (GT) Converter

**Files:**
- `SIDFactoryII/source/runtime/editor/converters/gt/converter_gt.cpp`
- `SIDFactoryII/source/runtime/editor/converters/gt/source_sng.cpp`

GT converter handles GoatTracker SNG format. Not directly relevant to DMC but shows the SIDFactory II converter architecture pattern for reference.

---

## 4. SIDId -- DMC Player Signature Bytes

**Repository:** https://github.com/cadaver/sidid
**Config file:** `sidid.cfg`

SIDId by Cadaver (Lasse Oorni) identifies C64 player routines by byte pattern signatures.

### DMC Signatures

**DMC (generic/early)**
```
18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

**DMC V4.x**
```
FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0
```

**DMC V5.x**
```
BC ?? ?? B9 ?? ?? C9 90 D0 AND BD ?? ?? 3D ?? ?? 99 ?? ?? 60
```

**DMC V6.x** (init routine signature -- SID register initialization)
```
A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4 8D 0B D4 8D 12 D4 8D 11 D4 A9 1F 8D 18 D4 A9 F2 8D 17 D4 60 CE ?? ?? 30 69 20
```

### 6502 Disassembly of Key Signatures

**DMC V4.x signature decoded:**
```asm
; FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0
INC $????,X     ; FE -- increment voice counter
LDA $????,X     ; BD -- load voice state
CLC             ; 18
ADC $????,Y     ; 7D -- add freq/note value
STA $????,X     ; 9D -- store result
LDA $????,X     ; BD -- load high byte
ADC #$00        ; 69 00 -- carry propagation
BIT $????       ; 2C -- test bits
LDA $????,X     ; BD -- load mask
AND #$01        ; 29 01 -- isolate bit 0
BNE ...         ; D0 -- branch if set
```

**DMC V5.x signature decoded:**
```asm
; BC ?? ?? B9 ?? ?? C9 90 D0
LDY $????,X     ; BC -- load wave table index from voice var
LDA $????,Y     ; B9 -- read wave table entry
CMP #$90        ; C9 90 -- compare with $90 (loop marker threshold)
BNE ...         ; D0 -- branch if not loop
```
This confirms the $90 threshold for wave table loop commands in DMC V5.

---

## 5. Player-ID (WilfredC64) -- DMC Identification

**Repository:** https://github.com/WilfredC64/player-id
**Config file:** `config/sidid.cfg`

Player-ID uses the same signature format as cadaver/sidid. Contains the same DMC signatures. Also has metadata:

### DMC Version Metadata (from TCRF/vgmid c64.nfo)

| ID | Name | Author | Year | Reference |
|----|------|--------|------|-----------|
| DMC | Demo Music Creator System | Balazs Farkas (Brian) | 1991 | csdb.dk/release/?id=2598 |
| DMC_V4.x | Demo Music Creator System | Balazs Farkas (Brian) | 1991 | csdb.dk/release/?id=2596 |
| DMC_V5.x | Demo Music Creator System | Balazs Farkas (Brian) | 1993 | csdb.dk/release/?id=2594 |
| DMC_V6.x | Demo Music Creator System | Balazs Farkas (Brian) | -- | -- |

---

## 6. DMC V4 Cross-Platform Editor (2025)

**CSDb:** https://csdb.dk/release/?id=250645
**Author:** Brian (Graffity) and Logan (Slackers)
**Released:** March 2025
**Platform:** Windows only (64-bit, 32-bit, XP builds)

This is a new cross-platform recreation of the DMC V4.0 editor. It can import existing PRG/SID tunes composed with DMC V4.0, V7.0A, or V7.0B. **Source code is NOT available** -- closed-source Windows application.

Key technical observation from forum discussion: DMC uses **duration-based patterns** (not tick-synchronized). Patterns can be any length, no syncing is done. This means notes are encoded as (note + duration) rather than one-event-per-tick.

---

## 7. DMC Format Summary (from all sources)

### Versions

| Version | Year | Author | Notes |
|---------|------|--------|-------|
| V2.1 | ~1990 | Brian/Graffity | Early version, quadruple speed variants exist |
| V4.0 | 1991 | Brian/Graffity | Most widely used version, ~2000 byte player |
| V4.0 Pro | ~1991 | Morbid/Onslaught | Modified V4 |
| V4.3++ | ~1992 | Modified | Enhanced V4 |
| V5.0 | 1993 | Brian/Graffity | Enhanced version, different wave table handling |
| V6.0 | unreleased | Brian/Graffity | "Sync" - low rastertime (7-8 lines), never publicly released |
| V7.0 | ~1993+ | UNREAL? | Based on V4 code with extra features |

### Common Init/Play Addresses

- **Init:** $1000
- **Play:** $1003 (single speed) or $1006 (multi-speed)

### Key Format Details

**Sector Encoding** (our existing dmc_parser.py confirms):
- $00-$5F: Note (C-0 through B-7, 96 notes)
- $60-$7C: Duration (AND $1F = ticks)
- $7D: Continuation (no ADSR reset on next note)
- $7E: Gate off
- $7F: End of sector (V4)
- $80-$9F: Instrument select (AND $1F, up to 32 instruments)
- $A0-$BF: Glide/portamento command
- $C0-$DF: Additional commands
- $FF: End of sector (V5)

**Wave Table:**
- Two columns: left (waveform), right (note data)
- Left column < $90: raw SID waveform byte
- Left column >= $90: loop command ($90 + steps back)
- Left column $FE: special terminator
- Player accesses via LDA abs,Y followed by CMP #$90

**Instrument Definition:** 11 bytes per instrument, 32 instruments max:
- Byte 0: Attack/Decay (AD)
- Byte 1: Sustain/Release (SR)
- Byte 2: Wave table pointer (index)
- Byte 3: Pulse width 1
- Byte 4: Pulse width 2
- Byte 5: Pulse width 3
- Byte 6: Pulse width limit
- Byte 7: Vibrato 1
- Byte 8: Vibrato 2
- Byte 9: Filter
- Byte 10: FX flags (bit 3 = no gate hard restart)

**Track/Orderlist:** (from dmc_to_usf.py analysis)
- Tune pointer table: interleaved lo/hi bytes for 3 voices
- Each track entry: sector index (0-$3F) or control byte
- $FF: end of track
- $FE: loop/repeat
- $80-$8F: transpose down (AND $0F = semitones)
- $A0-$AF: transpose up (AND $0F = semitones)

**Sector Pointer Table:**
- Split into lo/hi byte arrays
- Number of sectors typically 3-64
- Each pointer gives absolute address of sector data

**Frequency Table:**
- 96 entries (8 octaves x 12 notes)
- Hi/lo byte arrays (may be hi_lo or lo_hi order)
- Located before instrument data in player binary

**Memory Layout (V4 typical):**
- Player code: $1000-$1xxx (variable size, ~2000 bytes)
- Frequency table: after player code (192 bytes)
- Instrument table: freq_hi + $0248 (352 bytes = 32 x 11)
- Wave/Pulse/Filter tables: referenced by player code pointers
- Sector data: after tables
- Track data: after sector data

### Key Differences from JCH NP20

| Feature | DMC | JCH NP20 |
|---------|-----|----------|
| Load address | $1000 (typical) | $0F00 (fixed) |
| Version ID | Signature bytes in player code | "20.G" at $0FEE |
| Pointer storage | Via player code references | Fixed offsets from $0FA6-$0FD0 |
| Instrument storage | Row-major (11 bytes contiguous) | Row-major (converted to col-major) |
| Sequence format | Single-byte events (note, duration, instr are separate bytes) | Byte pairs (command, note) |
| Command threshold | $C0 | $C0 (same) |
| Wave table loop | >= $90 | Same concept |
| Orderlist | Variable-length single bytes with control codes | Fixed 2-byte entries (transpose, seq_index) |

---

## 8. Other Tools (No DMC-Specific Parsing Found)

### ChiptuneSAK
- **Repository:** https://github.com/c64cryptoboy/ChiptuneSAK
- Python pipeline for processing C64 music
- Works from SID register dumps (via siddump), NOT from native format parsing
- Does NOT parse DMC format natively

### SIDdecompiler (Galfodo)
- **Repository:** https://github.com/Galfodo/SIDdecompiler
- Generates relocatable 6502 assembly from SID files
- Player-agnostic (runs SID through 6502 emulator)
- Does NOT parse DMC data structures

### desidulate
- **Repository:** https://github.com/anarkiwi/desidulate
- Tools for analyzing C64 SID music from register logs
- Player-agnostic, works from VICE register dumps
- Does NOT parse DMC format natively

### sidtool
- **Repository:** https://github.com/olefriis/sidtool
- Converts SID to other formats
- Player-agnostic (emulation-based)
- Does NOT parse DMC format natively

### libsidplayfp
- **Repository:** https://github.com/libsidplayfp/libsidplayfp
- C64 SID emulation library
- Plays DMC SIDs by emulating the 6502 player code
- Does NOT parse DMC data structures

---

## 9. Key Conclusions for Our DMC Parser

1. **No battle-tested open-source DMC parser exists.** SIDFactory II does NOT have a DMC converter. The JCH NP20 converter is the closest relative but parses a different (evolved) format.

2. **Our existing dmc_parser.py and dmc_to_usf.py are likely the most complete DMC parsers available.** They already handle sector encoding, instrument parsing, wave table extraction, and orderlist recovery.

3. **The JCH NP20 converter provides architectural guidance:**
   - Row-major to column-major table transposition pattern
   - Orderlist 2-byte (transpose, seq_index) format
   - Sequence (command, note) pair format with $7F terminator
   - Tempo table construction from command references
   - $C0 threshold for command vs instrument in sequences

4. **DMC version detection should use sidid signatures** (already partially in dmc_parser.py -- V4 vs V5 detection). The V6 signature covers init routine SID register setup.

5. **The wave table $90 loop threshold is confirmed** by the V5.x sidid signature (`CMP #$90; BNE`) and our existing parser.

6. **DMC's duration-based encoding** (not tick-synced) is a fundamental format characteristic that affects how we map to USF patterns.
