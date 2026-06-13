<!--
local: tmp/dmc_hunt/sidfactory2/  (read-only checkout of Chordian/laxity SID Factory II)
  - JCH NP20.gX converter:  SIDFactoryII/source/runtime/editor/converters/jch/converter_jch.{cpp,h}
  - driver-info model:      SIDFactoryII/source/runtime/editor/driver/driver_info.h
  - native driver notes:    SIDFactoryII/dist/documentation/notes_driver11.txt (+ converter.txt, notes.txt)
  - NP20 reimplementation:  SIDFactoryII/drivers/sf2driver_np20_00.prg  (binary)
  - JCH example tunes:      SIDFactoryII/music/JCH/*.sf2 (9 tunes)
source_url (upstream): https://github.com/Chordian/sidfactory2
fetched_via: local read-only checkout (Read/Bash tools)
fetch_date: 2026-06-13
author: SID Factory II by Thomas Egeskov Petersen (Chordian) & Jens-Christian Huus (JCH/laxity); JCH NP20 driver/format by JCH
content_date: SF2 source (driver default 11.05); .sf2 files dated "11.04.00"
reliability: PRIMARY (maintained C++ parser of the exact NP20.gX binary; defines the successor driver model)
-->

# SID Factory II — the JCH successor, and its NP20.gX importer

SID Factory II (SF2) is the modern cross-platform successor to JCH's NewPlayer
editor, co-authored by JCH himself. Two parts of the local checkout are directly
load-bearing for SIDfinity's JCH work:

1. **`converter_jch.cpp`** — a maintained C++ parser that reads a raw **JCH NP20.gX
   `.prg`** and pulls out every table. This is an authoritative, up-to-date statement
   of the NP20.gX on-disk layout (the extraction target for the bulk of HVSC JCH).
2. **`driver_info.h` + the SF2 native driver model** — shows how the JCH design
   (contiguous sequence stacking, order lists, per-instrument table pointers) was
   re-expressed as a typed driver, useful as a clean reference for the same musical
   concepts.

SF2's own `.sf2` files and `sf2driver*.prg` are a *different* container from JCH
NP — they are SF2-native (driver binary + data + metadata header). They are NOT the
HVSC JCH binary format; treat them as the successor model, per the task framing.

---

## 1. JCH NP20.gX file layout — from `converter_jch.cpp` (PRIMARY)

### Detection (`CanConvert`, lines 51-86)
```cpp
const unsigned short address_version = 0x0fee;
// load/top address must be 0x0f00:
if (destination_address == 0x0f00) {
    version_1 = file->GetByte(0x0fee+0);   // '2'
    version_2 = file->GetByte(0x0fee+1);   // '0'
    version_3 = file->GetByte(0x0fee+2);   // '.'
    version_4 = file->GetByte(0x0fee+3);   // 'G'
    // accepts iff bytes spell "20.G"
}
```
So a JCH NP20.gX module's **file top address = `$0f00`** and a 6-char version
string lives at **`$0fee`** (`"20.Gx"`). (CheeseCutter uses the identical `$0fee`
slot for `"cc4.07"` — same lineage.) The runtime `init`/`play` are at `$1000`/`$1003`
but the *file* begins at `$0f00` with the editor pointer block at `$0fa0`.

### Pointer block at `$0fa0` (`GatherInputInfo`, lines 231-261)
The converter reads these absolute pointer words out of the input image — this is
the canonical NP20.gX header (identical layout to CheeseCutter's `ofa0..ofee`):

```cpp
address_fine_tune                = 0x0fba;   // -> fine-tune table
address_pointer_wave_table       = 0x0fbc;   // -> wave table (arp col A; col B at +256)
address_pointer_filter_table     = 0x0fc0;   // -> filter table
address_pointer_pulse_table      = 0x0fc2;   // -> pulse table
address_pointer_instrument_table = 0x0fc4;   // -> instrument table
address_pointer_orderlist_v1     = 0x0fc6;   // -> voice-1 order list
address_pointer_orderlist_v2     = 0x0fc8;   // -> voice-2 order list
address_pointer_orderlist_v3     = 0x0fca;   // -> voice-3 order list
address_pointer_sequence_vector_low  = 0x0fcc;  // -> seq pointer LOW table
address_pointer_sequence_vector_high = 0x0fce;  // -> seq pointer HIGH table
address_pointer_command_table    = 0x0fd0;   // -> super/command table
address_init_data                = 0x0fa6;   // songsets; SPEED at +6
m_SpeedSettingAddress = GetWord(0x0fa6) + 6; // default song speed byte
```

These pointers are **absolute addresses** stored in the module; the tables can sit
anywhere (relocatable). For the fixed-layout NP20.G4 build they resolve to the
codebase64 map (`$18CB` wave colA … `$1CCB` inst … `$1DCB`/`$1ECB` seq ptrs …
`$1FCB` super … `$20CB/$24CB/$28CB` orderlists … `$2CCB` seq data).

### Instrument table — ROW-major in JCH, stride = column count
`ImportTables` (lines 264-306) copies the instrument table with
`CopyTableRowToColumnMajor(src, dst, RowCount, ColumnCount)` (lines 521-532):
```cpp
src_address  = inSourceAddress + c + r * inColumnCount;   // JCH: row-major
dest_address = inDestinationAddress + c * inRowCount + r;  // SF2: column-major
```
i.e. in the **JCH source the 8 instrument bytes of one instrument are contiguous**
(`r * 8 + c`), whereas SF2 stores them column-major. The wave/pulse/filter tables
are copied straight (`CopyTable`, byte-for-byte) — they are already the right
layout in JCH and SF2.

### Order lists (`ImportOrderLists`, lines 379-435)
```cpp
orderlist_max_length = orderlist_v2_addr - orderlist_v1_addr;   // stride between voices
for offset in 0..max step 2:
    transpose      = GetByte(read_address + offset);
    sequence_index = GetByte(read_address + offset + 1);
    if (transpose == 0xff) { entry = END; break; }              // 0xff = end-of-orderlist
    entry.m_Transposition = 0x20 + transpose;                    // decode transpose
    entry.m_SequenceIndex = sequence_index;
```
So a JCH NP20 order list is **fixed 2-byte entries `[transpose, sequence_index]`**,
terminated by a `$ff` transpose byte. (Note: this NP20 form is *uniform* 2-byte
pairs — simpler than CheeseCutter's run-length-on-change packed orderlist. The
decode `transpose+0x20` matches CC's `sbc #$a0`/`+0x20` convention.)

### Sequences (`ImportSequences` / `ImportSequence`, lines 438-493)
```cpp
read_address = (GetByte(SeqVectorHigh + i) << 8) | GetByte(SeqVectorLow + i);
ImportSequence(read_address + 2, ...);   // NB: +2 — skip a 2-byte per-sequence header
...
for i in 0..0x100 step 2:
    command = GetByte(addr + i);
    note    = GetByte(addr + i + 1);
    if (command == 0x7f) break;             // 0x7f = end of sequence
    if (command >= 0xc0) { event.m_Command = command; event.m_Instrument = 0x80; }
    else                 { event.m_Command = 0x80;     event.m_Instrument = command; }
    event.m_Note = note;
```
Confirms the **2-byte (command, note) sequence pair** encoding:
- `command == 0x7f` ⇒ end of sequence.
- `command >= 0xc0` ⇒ it is a super/command-table pointer (CC: `$c0..$df`).
- `command <  0xc0` ⇒ it is an instrument number (CC: `$a0..$bf`, `$80`=none, `$90`=tie).
- second byte = note value.
- Sequences are addressed via split **low/high pointer tables**, and each sequence
  is preceded by a **2-byte header** (the converter reads from `read_address + 2`).
  This matches the codebase64 "+3 byte offset" remark and explains why the player's
  `getseq` starts at `seqcnt`, not 0.

### Tempo / "breakspeed" rebuild (`BuildTempoTableAndCorrectTempoCommands`, 309-363)
NP20.gX encodes tempo via super-table command `$Ex` and a default speed byte; when
speed `< 2` the player reads a tempo list out of the **filter-table head**
(`FilterTableAddress + 0/1` — analogous to CheeseCutter reading tempo from the
chord table). SF2 reconstructs this into a separate Tempo table; `$Ex` command rows
are rewritten to indices into it (lines 327-360, `GatherCommandInfoFromRowMajorDestinationTable`
collects `command == 0xe0` rows). This is the one NP20 quirk that is *not* a simple
table copy — worth replicating carefully in extraction.

---

## 2. The SF2 native driver model — `driver_info.h` (successor reference)

SF2 finalized tunes / drivers begin with a typed header that the editor parses
(`DriverInfo::Parse`). Top of file is `$0d7e` for the bundled drivers (the
`sf2driver*.prg` and `.sf2` files all start with bytes `7e 0d`). The header model:

- `ExpectedFileIDNumber = 0x1337`, `AuxilaryDataPointerAddress = 0x0ffb`.
- **Header blocks** (`HeaderBlockID`): Descriptor(1), DriverCommon(2), DriverTables(3),
  DriverInstrumentDescriptor(4), MusicData(5), TableColorRules(6),
  TableInsertDeleteRules(7), TableActionRules(8), DriverInstrumentDataDescriptor(9),
  End(0xff).
- `Descriptor`: driver type, size, name, code top/size, version major/minor/revision.
- `DriverCommon`: `m_InitAddress`, `m_StopAddress`, `m_UpdateAddress` (= init/stop/play),
  `m_SIDChannelOffsetAddress`, plus a long list of per-voice **state-variable
  addresses** (TickCounter, OrderListIndex, SequenceIndex, CurrentSequence,
  CurrentTranspose, EventDuration, NextInstrument, NextCommand, NextNote,
  NextNoteIsTied, TempoCounter, TriggerSync + `m_NoteEventTriggerSyncValue`). These
  name exactly the same runtime state the JCH/CC player keeps (`curseq`, `shtrans`,
  `duration`, `shinst`, `shsuper`, `shnote`, `tienote`, `speedcnt`, `tsync`).
- `MusicData`: `m_TrackCount`, order-list pointer low/high addresses, `m_SequenceCount`,
  sequence pointer low/high addresses, `m_OrderListSize`, `m_OrderListTrack1Address`,
  `m_SequenceSize`, `m_Sequence00Address`. (Same shape as the JCH header above.)
- `TableDefinition`: `m_Name`, `m_DataLayout` (RowMajor=0 / ColumnMajor=1),
  `m_Address`, `m_ColumnCount`, `m_RowCount`, plus editor rule IDs. The converter
  finds tables by name: **"Instruments", "Commands", "Wave", "Pulse", "Filter",
  "Tempo", "Init"** — the canonical JCH-lineage table set.

### SF2 native driver 11 table layout (notes_driver11.txt) — the "successor schema"
This is SF2's own driver (NOT JCH NP binary), but it shows the same musical model
with cleaner fields:

Instrument (6 bytes): `0:AD  1:SR  2:Flags  3:FilterIdx  4:PulseIdx  5:WaveIdx`.
Flags: `80` HR enable, `40` start filter program, `20` filter-channel enable
[11.03], `10` oscillator reset (waveform `09` first frame), `08` skip pulse reset,
low nibble = HR table index 0-7.

Commands (`T` = command nibble): `T0` slide up/down (16-bit), `T1` vibrato (freq,amp),
`T2` portamento (16-bit; `02 80 00` disables), `T3` arpeggio (speed, arp-table idx),
`T8` set local ADSR, `T9` set instrument ADSR, `Ta` filter program, `Tb` wave program,
`Tc` pulse program [11.02], `Td` tempo program [11.02], `Te` main volume [11.02],
`Tf` increase demo value; leading nibble alone `T` = note delay [11.04].

Wave (2 bytes): `XX YY` = waveform / (`00-7f` semitones added, `80-df` absolute);
`7f XX` = jump to index. **Pulse** (3 visible cols + frames): `8X XX YY` set PW,
`0X XX YY` add to PW, `7f -- XX` jump. **Filter** similar with passband nibble.
Arpeggio table: `XX`(<`70`) semitones, `7X` jump relative.

These map 1:1 onto the JCH NP fields (the differences are mostly cosmetic /
column ordering and a couple of extra flag bits SF2 added).

---

## 3. The bundled NP20 reimplementation driver

`SIDFactoryII/drivers/sf2driver_np20_00.prg` (5345 bytes) is SF2's reimplementation
of the JCH NP20 player as an SF2 driver. Its file header (bytes after the `$0d7e`
load address) carries the SF2 driver descriptor and the ASCII name **"NP20.<ver>"**.
`converter_jch.cpp` loads this driver as the *destination* when importing a JCH
tune (line 202: `"sf2driver_np20_00.prg"`), then copies the JCH tables into it.
This `.prg` is the cleanest reference player for the NP20 register write model in
the SF2 family, parallel to CheeseCutter's `player_v4.acme` for NP21.

---

## 4. Example JCH tunes & file header

`SIDFactoryII/music/JCH/` has 9 JCH-authored `.sf2` tunes (All Around The World,
Awry, Crazy, Down, Gentofte, Haploid, Rising_Planet, Slow_Cool, Synchords). They
are SF2-native containers (not JCH NP binary): a hexdump of `JCH - Crazy.sf2` begins
```
7e 0d 37 13 01 29 00 22 08 44 12 09 16 05 12 20   ~.7..).".D.....
31 31 2e 30 34 2e 30 30 20 2d 20 54 ...            "11.04.00 - T..."
```
i.e. load address `$0d7e`, the `$1337` file-ID, then the driver descriptor and the
version string `"11.04.00 - T..."` (driver 11.04). Useful as worked examples of the
JCH musical idiom (sequence stacking, table programs) but parse them with the SF2
container model above, not the NP binary layout.

---

## Leads to follow
- `converter_jch.cpp` is the single most authoritative NP20.gX parser; mirror its
  `GatherInputInfo` pointer offsets (`$0fba..$0fd0`) and decode rules
  (`transpose+0x20`, `0xff` end, `0x7f` seq-end, `command>=0xc0` ⇒ super) in the
  SIDfinity extractor.
- The **per-sequence 2-byte header** (converter reads `read_address + 2`) and the
  **uniform 2-byte order-list entries** are NP20-specific; do not assume CC's packed
  forms for NP20 HVSC tunes.
- NP20 tempo lives at `FilterTable + 0/1` when speed `< 2` (breakspeed); SF2 rebuilds
  a Tempo table from it. Replicate this when modelling tempo.
- The bundled `sf2driver_np20_00.prg` can be disassembled (it is plain 6502) for a
  second, independent NP20 write-model reference distinct from CheeseCutter's NP21.
- SF2's `driver_info.h` `DriverCommon` field names are a ready-made glossary for the
  player's runtime state bytes — handy when annotating an NP disassembly.
