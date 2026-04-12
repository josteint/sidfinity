---
source_url: https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/converters/jch/converter_jch.cpp, https://csdb.dk/release/?id=7268, https://csdb.dk/release/?id=98639, https://csdb.dk/release/?id=98640, https://raw.githubusercontent.com/TCRF/vgmid/master/c64.nfo
fetched_via: direct
fetch_date: 2026-04-11
author: Chordian (Thomas Egeskov Petersen) for SIDFactory II converter; Brian (Balazs Farkas) for GMC/DMC originals; TCRF community for c64.nfo
content_date: 2018 (SIDFactory II converter, approximate); 1990-1991 (GMC/DMC releases)
reliability: primary
---

# Lead: Predecessors (GMC) and JCH NP20 Converter Analysis

Research date: 2026-04-11

## 1. GMC V1.0 (CSDb #7268) — The Predecessor

**URL:** https://csdb.dk/release/?id=7268
**AKA:** Superiors Game Music Creator System V1
**Released by:** Graffity, 8 December 1990
**Code by:** Brian (Balazs Farkas) and Jay (both of Graffity)
**Type:** C64 Tool

### Key findings

- GMC was the original name before it became DMC. Same author (Brian/Balazs Farkas).
- User comment by Richard (2009): "They should have called this tool DMC V1.0 :)" — confirming community awareness that GMC IS DMC's direct precursor.
- User comment by NecroPolo (2009): "That was my weapon of choice, uhh, 18 years ago. It feels very solid to work with and it is really good at producing some really twisted filtering."
- User comment by wacek (2012): "Uploaded a proper version (including a great intro from Graffity and all the original demotunes)."
- Contains 29 SIDs in HVSC, all under `/MUSICIANS/B/Brian/` and `/MUSICIANS/A/Andy/`.

### Downloads available
- `GMC v1.t64` (1,005 downloads)
- `gmcv1.zip` (230 downloads)
- `GMC - Graffity - with intro and demotunes.d64` (164 downloads)

### Relevance to DMC parsing
GMC V1.0 is the earliest ancestor. The data format is likely simpler than DMC V4+. If we can parse GMC SIDs, it provides a baseline to understand how DMC structures evolved. The HVSC SIDs listed above can serve as test cases for the GMC player variant.

### vgmid/c64.nfo entries
From https://github.com/TCRF/vgmid/blob/master/c64.nfo:
```
GMC/Superiors
     NAME: Game Music Creator System
   AUTHOR: Balazs Farkas (Brian)
 RELEASED: 1990
REFERENCE: http://csdb.dk/release/?id=7268

GMC_V2.0/Superiors
     NAME: Game Music Creator System
   AUTHOR: Balazs Farkas (Brian)
```
Note: GMC V2.0 is listed as a separate SIDID signature but has no release reference. This is the intermediate step between GMC V1.0 and DMC V3.0.

---

## 2. GMC V1.6 (CSDb #98639)

**URL:** https://csdb.dk/release/?id=98639
**AKA:** GMC V1.6
**Full title:** GMC V1.6 Editor + Beta Music
**Released by:** Graffity, December 1990
**Code by:** Brian (of Graffity)
**Type:** C64 Tool

### Key findings

- Released same month as GMC V1.0 (December 1990), suggesting rapid iteration.
- "Beta Music" in the title suggests it shipped with demo tunes.
- No user comments, no SIDs listed — minimal community engagement recorded.
- Single download: `superiors gmc 1.6.zip` (476 downloads).

### Relevance
V1.6 is a refinement of V1.0, still pre-DMC. The fact that it exists confirms there were multiple GMC revisions before the name changed to DMC. Version lineage appears to be: GMC V1.0 -> V1.6 -> V2.0 -> DMC V3.0.

---

## 3. DMC V3.0 (CSDb #98640)

**URL:** https://csdb.dk/release/?id=98640
**AKA:** Demo Music Creator System V3.0
**Released by:** Graffity, July 1991
**Code by:** Brian (of Graffity)
**Type:** C64 Tool

### Key findings

- This is the FIRST release using the "DMC" name (Demo Music Creator).
- Released July 1991 — about 7 months after GMC V1.6.
- No user comments, no SIDs listed.
- Single download: `dmc3.zip` (361 downloads).
- The jump from "GMC V2.0" to "DMC V3.0" suggests the version numbering was continuous across the rename. The lineage is: GMC V1.0 -> V1.6 -> V2.0 -> DMC V3.0.

### Relevance
V3.0 is the missing link between GMC and DMC V4.0 (which is the earliest version with significant HVSC presence). If the binary can be obtained from the download, disassembling its player routine would show what changed when the format transitioned from GMC to DMC. The V3 player likely has a simpler structure than V4/V5.

---

## 4. Version Lineage (confirmed)

From all sources combined:

| Version | Name | Date | CSDb |
|---------|------|------|------|
| V1.0 | GMC (Game Music Creator) | Dec 1990 | #7268 |
| V1.6 | GMC | Dec 1990 | #98639 |
| V2.0 | GMC | ~1991 | (SIDID entry, no CSDb release) |
| V3.0 | DMC (Demo Music Creator) | Jul 1991 | #98640 |
| V4.0 | DMC | 1991 | #2596 |
| V5.0 | DMC | 1993 | #2594 |
| V6.x | DMC | ? | (no CSDb release page) |

From vgmid/c64.nfo, the SIDID signatures are:
- `GMC/Superiors` (V1.x)
- `GMC_V2.0/Superiors` (V2.0)
- `DMC` (generic, references #2598 which is DMC V4.0 editor)
- `DMC_V4.x` (references #2596)
- `DMC_V5.x` (references #2594)
- `DMC_V6.x` (no reference)

---

## 5. SIDFactory II JCH NP20 Converter — Deep Analysis

**Source files:**
- Header: https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/converters/jch/converter_jch.h
- Implementation: https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/converters/jch/converter_jch.cpp

### Architecture Overview

The converter reads JCH NewPlayer 20.g4 format files and converts them to SIDFactory II's internal format. JCH NP20 is the direct descendant of DMC (same architecture, extended by Jens-Christian Huus).

### NP20 File Detection

Files must:
- Load at address `$0F00`
- Have version string "20.G" at address `$0FEE`

### NP20 Pointer Table Layout (at fixed addresses from $0F00 base)

| Address | Field | JCH20g4Info member |
|---------|-------|--------------------|
| `$0FBA` | Fine tune table address | `m_FineTuneAddress` |
| `$0FBC` | Wave table address | `m_WaveTableAddress` |
| `$0FC0` | Filter table address | `m_FilterTableAddress` |
| `$0FC2` | Pulse table address | `m_PulseTableAddress` |
| `$0FC4` | Instrument table address | `m_InstrumentTableAddress` |
| `$0FC6` | Orderlist V1 (voice 1) address | `m_OrderlistV1Address` |
| `$0FC8` | Orderlist V2 (voice 2) address | `m_OrderlistV2Address` |
| `$0FCA` | Orderlist V3 (voice 3) address | `m_OrderlistV3Address` |
| `$0FCC` | Sequence vector low address | `m_SequenceVectorLowAddress` |
| `$0FCE` | Sequence vector high address | `m_SequenceVectorHighAddress` |
| `$0FD0` | Command table address | `m_CommandTableAddress` |
| `$0FA6` | Init data address (speed at +6) | `m_SpeedSettingAddress` = word($0FA6) + 6 |

### Data Structures

#### Instruments (row-major, converted to column-major)
- Stored as rows of N columns in the source
- The converter transposes: `CopyTableRowToColumnMajor()` reads `src + col + row * colcount` and writes `dest + col * rowcount + row`
- This confirms instruments are stored in row-major order in NP20

#### Commands (row-major, 2 columns)
- Column 1: command byte (high nibble = command type, low nibble = value high)
- Column 2: parameter byte
- Command `$E0` = tempo change command. The parameter byte is the tempo value.
- Tempo commands are gathered during import and used to build a tempo table

#### Wave Table
- The `CopyWaveTable()` function shows wave tables have a special structure:
  - Two halves (left/right), each `size` bytes
  - If value is `$7F` or `$7E`: keep in same position (left=left, right=right)
  - Otherwise: SWAP left and right columns
  - This means NP20 stores wave data in opposite column order from SF2 for non-terminator entries

#### Pulse Table and Filter Table
- Simple linear copies (`CopyTable()`) — no transformation needed
- These are flat arrays, not row-major

#### Orderlists
- 3 orderlists (one per voice), each at its own address
- Each entry is 2 bytes: `transpose, sequence_index`
- `$FF` in transpose = end-of-orderlist marker
- Transpose is stored raw; converter adds `$20` bias: `entry.m_Transposition = 0x20 + transpose`
- Max orderlist length is inferred from address spacing: `orderlist_vectors[1] - orderlist_vectors[0]`

#### Sequences
- Addressed via split lo/hi vector tables at `m_SequenceVectorLowAddress` and `m_SequenceVectorHighAddress`
- Each sequence entry is 2 bytes: `command, note`
  - `$7F` in command = end-of-sequence
  - Command >= `$C0`: it's a command (instrument = $80, meaning "no instrument change")
  - Command < `$C0`: it's an instrument number (command = $80, meaning "no command")
- Read starts at vector address + 2 (skipping a 2-byte header)

#### Tempo
- Default speed stored at init_data_address + 6
- If speed >= 2: simple single-value tempo
- If speed < 2 (meaning multispeed/CIA timing): tempo is 2 bytes from filter table address (bytes [1] and [0], in that order)
- Tempo table entries are terminated by `$7F`

### NP20 -> DMC Structure Mapping

Based on the architectural similarity (same author lineage, same general design):

| NP20 Structure | Likely DMC Equivalent | Notes |
|---|---|---|
| Pointer table at $0Fxx | Pointer table at $10xx or embedded | DMC likely has similar pointer block but at different addresses |
| Instruments (row-major) | Instruments (likely row-major) | Same storage convention expected |
| Wave table (2-column, swapped) | Wave table | DMC may or may not swap columns |
| Pulse table (flat) | Pulse table (flat) | Likely identical format |
| Filter table (flat) | Filter table (flat) | Likely identical format |
| Orderlists (2-byte entries) | Orderlists (2-byte entries) | transpose + sequence_index pattern |
| Sequences (2-byte: cmd/instr, note) | Sequences (2-byte entries) | Same encoding likely |
| Sequence vectors (lo/hi split) | Sequence vectors (lo/hi split) | Standard 6502 pattern |
| Command $E0 = tempo | Command = tempo? | Need to verify DMC command set |
| Speed at init+6 | Speed location varies | Need to find in DMC player |

### Key Architectural Insights for DMC Parsing

1. **Row-major to column-major transposition** is needed for instruments and commands. This tells us DMC/NP20 instruments are stored as `[instr0_col0, instr0_col1, ..., instr0_colN, instr1_col0, ...]` NOT as `[all_col0_values, all_col1_values, ...]`.

2. **Orderlists use 2-byte entries** with a `$FF` terminator in the transpose byte. This is simpler than GT2's variable-length orderlist encoding.

3. **Sequences use 2-byte entries** with a `$7F` terminator. The command/instrument byte doubles as both — values >= $C0 are commands, values < $C0 are instruments. This is a clean encoding.

4. **Sequence vectors are split lo/hi** — standard 6502 indirect addressing pattern. The first 2 bytes of each sequence are a header (skipped by the converter).

5. **Wave table column swapping** is specific to the NP20->SF2 conversion and may not apply to DMC->USF. Need to check DMC's wave table column order independently.

6. **Multispeed detection**: speed < 2 triggers a different tempo encoding using filter table bytes. This CIA-timing mode likely exists in DMC too.

---

## 6. TCRF/vgmid c64.nfo — DMC-Adjacent Entries

**URL:** https://github.com/TCRF/vgmid/blob/master/c64.nfo
(Note: the GitHub blob URL returns 404 for raw access; the raw URL works: https://raw.githubusercontent.com/TCRF/vgmid/master/c64.nfo)

### DMC Family Entries

```
DMC
     NAME: Demo Music Creator System (DMC)
   AUTHOR: Balazs Farkas (Brian)
 RELEASED: 1991
REFERENCE: http://csdb.dk/release/?id=2598

(DMC_V4.x)
     NAME: Demo Music Creator System (DMC)
   AUTHOR: Balazs Farkas (Brian)
 RELEASED: 1991
REFERENCE: http://csdb.dk/release/?id=2596

(DMC_V5.x)
     NAME: Demo Music Creator System (DMC)
   AUTHOR: Balazs Farkas (Brian)
 RELEASED: 1993
REFERENCE: http://csdb.dk/release/?id=2594

DMC_V6.x
     NAME: Demo Music Creator System (DMC)
   AUTHOR: Balazs Farkas (Brian)
```

### GMC Family Entries

```
GMC/Superiors
     NAME: Game Music Creator System
   AUTHOR: Balazs Farkas (Brian)
 RELEASED: 1990
REFERENCE: http://csdb.dk/release/?id=7268

GMC_V2.0/Superiors
     NAME: Game Music Creator System
   AUTHOR: Balazs Farkas (Brian)
```

### JCH Family Entries

```
JCH_NewPlayer
   AUTHOR: Jens-Christian Huus (JCH)
REFERENCE: http://csdb.dk/release/?id=14037

JCH_OldPlayer
   AUTHOR: Jens-Christian Huus (JCH)

JCH_Protracker
   AUTHOR: Jens-Christian Huus (JCH)
```

### MiniMusic (Brian's other tool)

```
MiniMusic
     NAME: Mini Music Editor
   AUTHOR: Balazs Farkas (Brian)
 RELEASED: 1990 Tomcat
REFERENCE: http://csdb.dk/release/?id=55790
```

This is another Brian/Balazs Farkas tool from 1990, contemporaneous with GMC. May share code/concepts with GMC/DMC.

### TFX (mentioned in original leads)

```
TFX
   AUTHOR: Ray
 RELEASED: 1995 Unreal
REFERENCE: http://csdb.dk/release/?id=110111
```

TFX is by a different author (Ray of Unreal), released 1995. Not directly in the DMC lineage. Low relevance.

### Dane (JCH-editor extension)

```
Dane
     NAME: JCH-editor 3.1 + NP22-25
   AUTHOR: Stellan Andersson (Dane)
 RELEASED: 2011
REFERENCE: http://csdb.dk/release/?id=100406
```

Dane extended JCH's editor to NP22-25. This confirms the NP20+ lineage continued being actively developed.

---

## 7. Summary and Next Steps

### What we now know
1. **Complete version lineage**: GMC V1.0 (Dec 1990) -> V1.6 (Dec 1990) -> V2.0 (~1991) -> DMC V3.0 (Jul 1991) -> V4.0 (1991) -> V5.0 (1993) -> V6.x
2. **NP20 data structures are fully documented** from the SIDFactory II converter source code. These provide the template for DMC parsing.
3. **Six SIDID signatures** exist for the GMC/DMC family, so we can identify which version a given SID uses.
4. **Downloadable binaries exist** for GMC V1.0, V1.6, and DMC V3.0 on CSDb.

### Recommended next steps
1. **Download GMC V1.0 and DMC V3.0 binaries** from CSDb and disassemble their player routines. Compare pointer table locations with NP20's documented layout.
2. **Map DMC V4/V5 pointer tables** using the NP20 layout as a template — look for the same pattern of pointers at fixed offsets from the load address.
3. **Verify the instrument/sequence encoding** in DMC matches NP20's (row-major instruments, 2-byte sequence entries, $7F terminators).
4. **Check wave table column order** in DMC — the NP20 converter swaps columns, so DMC might store them in a different order than NP20.
5. **Implement DMC detection** using SIDID signatures to determine which version (V4/V5/V6) a SID file uses, then apply version-specific parsing.
