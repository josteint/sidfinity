---
source_url: multiple — OpenMPT/openmpt (Load_fc.cpp), vgmpf.com FC wiki, NostalgicPlayer docs, CSDb
fetched_via: direct (WebFetch/WebSearch)
fetch_date: 2026-06-13
author: various
content_date: various
reliability: secondary (Future Composer format from OpenMPT source; RoMuzak relationship inferred)
---

# RoMuzak — relationship to Future Composer V1.x

## Confirmed relationship

From multiple sources (VGMPF wiki, CSDb, existing research.md):

> **RoMuzak can convert Future Composer V1.0 songs.**

Many HVSC entries are annotated "RoMuzak conversion of [FC tune]." RoMuzak was a popular tool
in the German C64 scene for repurposing existing FC V1.0 songs — importing them into RoMuzak's
own engine and replaying them with RoMuzak's player code.

This means RoMuzak's data format is likely derived from or heavily inspired by FC V1.x concepts,
but the player code is RoMuzak's own (not the original FC player).

---

## Future Composer V1.x format — what we know from open sources

### Source: OpenMPT/openmpt `soundlib/Load_fc.cpp`
URL: https://github.com/OpenMPT/openmpt/blob/master/soundlib/Load_fc.cpp
(Note: This is the **Amiga** FC format, not the C64 version — see caveat below)

#### File header (100 bytes)
```cpp
struct FCFileHeader {
    char     magic[4];           // "SMOD" (FC 1.0-1.3) or "FC14" (FC 1.4)
    uint32be sequenceSize;
    uint32be patternsOffset;
    uint32be patternsSize;
    uint32be freqSequenceOffset;
    uint32be freqSequenceSize;
    uint32be volSequenceOffset;
    uint32be volSequenceSize;
    uint32be sampleDataOffset;
    uint32be waveTableOffset;
    FCSampleInfo sampleInfo[10]; // 6 bytes each = 60 bytes
};
// Total: 100 bytes (MPT_BINARY_STRUCT verified)
```

#### Sample info (6 bytes each, 10 entries)
```cpp
struct FCSampleInfo {
    uint16be length;      // in words
    uint16be loopStart;   // in bytes
    uint16be loopLength;  // in words
};
```

#### Playlist entry (13 bytes)
```cpp
struct FCPlaylistEntry {
    struct Entry {
        uint8 pattern;        // pattern index
        int8  noteTranspose;  // transposition
        int8  instrTranspose; // instrument transposition
    } channels[4];           // 4 channels (Amiga)
    uint8 speed;
};
```

#### Pattern structure
- 64 bytes per pattern entry
- 32 rows per pattern
- Pattern data: `p[0]` = note byte, `p[1]` = effect byte
  - `p[0] == 0x49`: pattern break
  - `p[1] & 0xC0`: auto-portamento flag
  - `p[1] & 0x80`: pitch bend/slide

#### Sequence script commands (frequency and volume envelopes)
```
0xE0  Loop/jump to target
0xE1  End of sequence
0xE2  Waveform control
0xE3  Vibrato parameters
0xE4  Waveform control (variant)
0xE7  Jump to frequency sequence
0xE8  Sustain/delay timing
0xE9  Waveform with subsample (FC 1.4 only)
0xEA  Volume/pitch slides (FC 1.4 only)
0x00-0x7F  Raw pitch/volume values
```

#### Built-in waveforms
FC 1.0-1.3: waveform table embedded in binary at sample index 11.
FC 1.4: own wave tables (80 bytes after header) — this is the key V1.4 change.

---

## CRITICAL CAVEAT: Amiga FC vs C64 FC are different formats

The `Load_fc.cpp` above handles the **Amiga** Future Composer format by Jochen Hippel.

The **C64** Future Composer is a different program:
- Created by Finnish Gold (1988) as an unofficial editor for the Maniacs of Noise C64 driver
- The scene expanded it to add 3-track support, drum/filter editors
- It uses SID chip registers ($D400–$D418), not Amiga Paula DMA
- Format is inherently different: no `SMOD`/`FC14` magic, no big-endian offsets

NostalgicPlayer supports both: `Future Composer 1.0-1.3` (.fc / .fc13 / .smod) = Amiga;
C64 FC tunes play via SidPlayFp (generic 6502 emulation), not a dedicated FC C64 parser.

**Therefore: the struct details above do NOT directly apply to C64 FC V1.0 or RoMuzak.**

---

## What C64 Future Composer V1.x is known to contain

From VGMPF wiki and CSDb (https://csdb.dk/release/?id=10604):

- FC V1.0 released by Finnish Gold, 20 June 1988
- Based on Maniacs of Noise driver (ripped/adapted)
- Later versions (by other groups) added: 3 tracks, drum editor, filter editor, credits editor
- "Better driver from Hawkeye" in later versions
- FC 1.4: own wave tables (vs static tables in 1.0-1.3) — mirrors the Amiga version split

C64 FC V1.0 data is a PRG file laid out for C64 address space. No public format spec found.

---

## Inference: what RoMuzak likely inherited from C64 FC V1.0

RoMuzak "converts" FC V1.0 songs. Possible conversion modes:
1. **Full import/re-encode:** RoMuzak reads FC V1.0 data and translates it into RoMuzak's
   native format, stored in the output SID. The SID then contains RoMuzak format data,
   not FC data. (Most likely — the player code is definitely RoMuzak's own.)
2. **Hybrid player:** RoMuzak player reads FC data structures directly. (Less likely given
   the distinct player code and the V7 note-byte encoding change shown by sidid.)

If mode 1 (most likely): RoMuzak's instrument/sequence model will be an *approximation* of
FC V1.0's model. We'd expect to find:
- An instrument block with: ADSR, waveform selection, PW, vibrato params (parallel to FC's
  freq/vol envelope scripts, but pre-computed / flattened into a simpler struct)
- A pattern format with: note byte + effect/instrument byte per row (similar to FC)
- A sequence/orderlist: per-voice position pointer into a pattern list
- Possibly a drum channel (FC had drum editor additions)
- Filter and volume control per the SID chip

The existing `research.md` confirms: `+$0018` holds a "per-instrument ADSR, waveform, pulse
width, filter, vibrato/portamento" block (~136 bytes) — this is structurally consistent with
a simplified/flattened version of FC's envelope scripts.

---

## FC V1.x "SMOD" magic — relevance to C64 version

The Amiga FC uses "SMOD" as a file magic. C64 FC V1.0 PRG files have no such magic (they are
raw C64 programs loaded at a fixed address). The `ROMUZAK89` string at +$09 serves as RoMuzak's
own format magic.

---

## Leads to follow

- **OPEN (RE needed):** Confirm whether a RoMuzak SID actually contains re-encoded RoMuzak-format
  data after FC import (mode 1), or whether it contains FC structs (mode 2). Disassembling the
  init routine on a known FC-converted SID would reveal which data the player reads.
- **OPEN:** Fetch and study a known "RoMuzak conversion of FC tune" SID from HVSC. The instrument
  block at +$0018 should be cross-referenceable against the original FC tune's instrument data if
  the original FC PRG can be found.
- **OPEN:** C64 FC V1.0 format has no public spec. The HVSC `DOCUMENTS/` directory may contain a
  FC format doc — check `C64Music/DOCUMENTS/` on the HVSC mirror (hvsc.etv.cx).
- **OPEN:** NostalgicPlayer's GitHub (https://github.com/neumatho/NostalgicPlayer) has a
  `/Format_Descriptions/` directory that may contain C64 FC format docs — fetch the directory
  listing and any relevant files.
- **OPEN:** OpenMPT source `soundlib/` directory — search for any C64-specific FC loader
  (separate from `Load_fc.cpp` which is Amiga). A `Load_fc_c64.cpp` or similar may exist.
- **LEAD:** The FC effect commands `0xE0`–`0xEA` in the Amiga version are analogous to what
  RoMuzak might store in its sequence data. The SID-specific equivalents would be:
  - Waveform select → SID $D404 control register write
  - Volume envelope → SID $D405/$D406 ADSR
  - Vibrato → frequency modulation on $D400/$D401
  - Filter → $D415/$D416/$D417
  Worth mapping these FC script commands to expected RoMuzak instrument-block fields as a
  hypothesis to test during RE.
