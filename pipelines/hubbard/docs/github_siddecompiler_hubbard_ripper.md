---
source_url: https://github.com/Galfodo/SIDdecompiler
fetched_via: direct
fetch_date: 2026-04-11
author: Stein Pedersen (Galfodo / Prosonix)
content_date: "unknown (repository accessed 2026-04-11; 0 open issues, 24 stars)"
reliability: primary
---
# SIDdecompiler - Rob Hubbard Ripper

**Repo:** https://github.com/Galfodo/SIDdecompiler
**Author:** Stein Pedersen (Galfodo) / Prosonix
**Language:** C++
**Key files:** `src/SIDdisasm/STHubbardRipper.cpp`, `src/SIDdisasm/STHubbardRipper.h`

## Background

Originally started as a Rob Hubbard plugin for the Prosonix SID tracker. The underlying
tracing 6502 emulator proved effective across many music drivers, leading to the broader
SIDdecompiler release. Rob Hubbard tunes get "slightly better documented" output with
non-generic label names for data of known purpose.

## Architecture

Runs a SID file through a 6502 emulator, traces code paths, then generates relocatable
6502 assembly source. The Hubbard ripper specifically identifies player data structures
by searching for known 6502 instruction patterns in the traced memory.

## STHubbardRipper.h

```cpp
#ifndef STHUBBARDRIPPER_H_INCLUDED
#define STHUBBARDRIPPER_H_INCLUDED

#include "STSIDRipper.h"
#include <vector>

class STHubbardRipper {
public:
  struct SongData {
    int                 m_SongAddress;
    int                 m_TrackAddress[3];
  };

  struct PlayerInstance {
    std::vector<SongData> m_Songs;
    int                   m_InstrumentAddress;
    int                   m_SeqLoAddress;
    int                   m_SeqHiAddress;
    int                   m_SequencesUsedGuesstimate;
    int                   m_FrqAddress;
  };

                        STHubbardRipper(STSIDRipper& sid);
  bool                  scanForData();

  std::vector<PlayerInstance>
                        m_Instances;
  STSIDRipper&          m_sid;
};

#endif
```

## STHubbardRipper.cpp - Complete Source

```cpp
#include "STHubbardRipper.h"
#include <assert.h>

STHubbardRipper::STHubbardRipper(STSIDRipper& m_sid) : m_sid(m_sid) {
}

bool STHubbardRipper::scanForData() {
  int foundAddress = 0;
  unsigned char* memory = m_sid.m_Memory.data();
  int search_songs  = 0;
  int search_instr  = 0;
  int search_seq    = 0;
  int search_frq    = 0;
  do {
    PlayerInstance instance;

    // === SONG DATA DETECTION ===
    // Find pointer to "songs" data section.
    //   lda songs,x       $bd SONGS_LOW SONGS_HIGH
    //   sta currtrkhi,y   $99 * *
    //   inx               $e8
    //   iny               $c8
    //   cpy #$06          $c0 $06
    int songsAddress;
    foundAddress = m_sid.findString("bd****99****e8c8c006", search_songs);
    if (foundAddress > 0)
    {
      search_songs = foundAddress + 1;
      songsAddress = memory[foundAddress + 1] | (memory[foundAddress + 2] << 8);
      // songsAddress points to a 6-byte structure:
      //   songs:
      //     .dat <montymaintr1, <montymaintr2, <montymaintr3
      //     .dat >montymaintr1, >montymaintr2, >montymaintr3
      while (songsAddress < 65536) {
        SongData song;
        song.m_SongAddress     = songsAddress;
        song.m_TrackAddress[0] = memory[songsAddress]     | (memory[songsAddress + 3] << 8);
        song.m_TrackAddress[1] = memory[songsAddress + 1] | (memory[songsAddress + 4] << 8);
        song.m_TrackAddress[2] = memory[songsAddress + 2] | (memory[songsAddress + 5] << 8);
        if (m_sid.isAddressInSIDRange(song.m_TrackAddress[0]) &&
            m_sid.isAddressInSIDRange(song.m_TrackAddress[1]) &&
            m_sid.isAddressInSIDRange(song.m_TrackAddress[2])) {
          instance.m_Songs.push_back(song);
          songsAddress += 6;
        } else {
          if (instance.m_Songs.empty()) {
            goto not_found;
          }
          break;
        }
      }
    } else {
      // === SINGLE-SONG FALLBACK ===
      // Only one song in SID. Has no "songs" data, but hard coded pointers instead.
      //   lda currtrklo,x    $bd CURRTRKLO_LOW CURRTRKLO_HIGH
      //   sta $02            $85 *
      //   lda currtrkhi,x    $bd CURRTRKHI_LOW CURRTRKHI_HIGH
      //   sta $03            $85 *
      //   dec lengthleft,x   $de * *
      foundAddress = m_sid.findString("bd****85**bd****85**de", search_songs);
      if (foundAddress > 0) {
        search_songs = foundAddress + 1;
        int currtrklo = memory[foundAddress + 1] | (memory[foundAddress + 2] << 8);
        int currtrkhi = memory[foundAddress + 6] | (memory[foundAddress + 7] << 8);
        SongData song;
        song.m_SongAddress      = currtrklo;
        if (currtrkhi - currtrklo != 3) {
          goto not_found;
        }
        song.m_TrackAddress[0]  = memory[currtrklo]     | (memory[currtrkhi] << 8);
        song.m_TrackAddress[1]  = memory[currtrklo + 1] | (memory[currtrkhi + 1] << 8);
        song.m_TrackAddress[2]  = memory[currtrklo + 2] | (memory[currtrkhi + 2] << 8);
        if (m_sid.isAddressInSIDRange(song.m_TrackAddress[0]) &&
            m_sid.isAddressInSIDRange(song.m_TrackAddress[1]) &&
            m_sid.isAddressInSIDRange(song.m_TrackAddress[2])) {
          instance.m_Songs.push_back(song);
        } else {
          goto not_found;
        }
      } else {
        goto not_found;
      }
    }

    // === INSTRUMENT DATA DETECTION ===
    //   lda instr,x       $bd INSTR_LOW INSTR_HIGH
    //   sta $d402,y       $99 $02 $d4
    //   lda instr + 1,x   $bd * *
    //   sta $d403,y       $99 $03 $d4
    foundAddress = m_sid.findString("bd****9902d4bd****9903d4", search_instr);
    if (foundAddress <= 0) {
      // 2nd chance (with PHA between):
      //   lda instr,x       $bd INSTR_LOW INSTR_HIGH
      //   sta $d402,y       $99 $02 $d4
      //   pha               $48
      //   lda instr + 1,x   $bd * *
      //   sta $d403,y       $99 $03 $d4
      foundAddress = m_sid.findString("bd****9902d448bd****9903d4", search_instr);
    }
    if (foundAddress > 0) {
      search_instr = foundAddress + 1;
      instance.m_InstrumentAddress = memory[foundAddress + 1] | (memory[foundAddress + 2] << 8);
    } else {
      goto not_found;
    }

    // === SEQUENCE/PATTERN POINTER DETECTION ===
    //   tay               $a8
    //   lda patptl,y      $b9 PATPTL_LOW PATPTL_HIGH
    //   sta $04           $85 *
    //   lda patpth,y      $b9 PATPTH_LOW PATPTH_HIGH
    //   sta $05           $85 *
    foundAddress = m_sid.findString("a8b9****85**b9****85**", search_seq);
    if (foundAddress > 0)
    {
      search_seq = foundAddress + 1;
      instance.m_SeqLoAddress = memory[foundAddress + 2] | (memory[foundAddress + 3] << 8);
      instance.m_SeqHiAddress = memory[foundAddress + 7] | (memory[foundAddress + 8] << 8);
      instance.m_SequencesUsedGuesstimate = instance.m_SeqHiAddress - instance.m_SeqLoAddress;
    }

    // === FREQUENCY TABLE DETECTION ===
    // Searches for known frequency table bytes: $16 $01 $27 $01
    int frqAddr = m_sid.findString("16012701", search_frq);
    if (frqAddr > 0) {
      search_frq = frqAddr + 1;
      instance.m_FrqAddress = frqAddr;
    } else {
      instance.m_FrqAddress = 0;
    }
    m_Instances.push_back(instance);
  } while (true);
not_found:
  return m_Instances.size() > 0;
}
```

## Key Insights for Our Decompiler

### Data Structure Discovery via 6502 Pattern Matching

The ripper finds data by searching for specific instruction sequences that access the data.
This is the same approach as our GT2 decompiler (`gt2_parse_direct.py`).

### Pattern Summary

| Data Section | 6502 Pattern | Purpose |
|---|---|---|
| Songs (multi) | `BD ** ** 99 ** ** E8 C8 C0 06` | LDA songs,X / STA currtrkhi,Y / INX / INY / CPY #6 |
| Songs (single) | `BD ** ** 85 ** BD ** ** 85 ** DE` | LDA currtrklo,X / STA zp / LDA currtrkhi,X / STA zp / DEC |
| Instruments | `BD ** ** 99 02 D4 BD ** ** 99 03 D4` | LDA instr,X / STA $D402,Y (pulse lo/hi) |
| Instruments (alt) | `BD ** ** 99 02 D4 48 BD ** ** 99 03 D4` | Same with PHA between |
| Sequences | `A8 B9 ** ** 85 ** B9 ** ** 85 **` | TAY / LDA patptl,Y / STA zp / LDA patpth,Y / STA zp |
| Freq table | `16 01 27 01` | Known frequency table bytes (C#1, D-1 low bytes) |

### Song Data Layout

- Multi-song: 6 bytes per song = 3 low bytes + 3 high bytes for track pointers
- Single-song: currtrklo and currtrkhi are 3 bytes apart (verified: `currtrkhi - currtrklo == 3`)
- Each track pointer -> pattern sequence for one SID voice

### Label Generation in siddisasm.cpp

When Hubbard data is found, the main disassembler generates meaningful labels using
instance-prefixed naming (e.g., `i0_frqlo`, `i1_instr` for multi-instance SIDs):

| Label | Data Structure |
|---|---|
| `frqlo` / `frqhi` | Frequency table low/high bytes (with offset aliases) |
| `instr` | Instrument definitions base (with 7-byte offset aliases) |
| `seqlo` / `seqhi` | Sequence/pattern pointer tables |
| `s` | Main sequence address table |
| `s00` through `sNN` | Individual sequence/pattern addresses |
| `song00` through `songNN` | Song base addresses |
| `song00trk` through `songNNtrk` | Track pointer tables within songs |
| `song00trk00-02` | Individual track addresses per song |

### Repository Status (April 2026)

- **Issues:** 0 open, 0 closed — no bug reports or feature requests
- **Stars:** 24, **Forks:** 2
- **No other ripper modules** besides STHubbardRipper — the repo only has the generic
  STSIDRipper base class and the Hubbard-specific ripper. No GT2, JCH, DMC, or other
  engine-specific rippers exist.
- **Commented-out code:** ~210 lines of disabled `convert()`, `convertSequence()`, and
  `convertInstruments()` methods exist in the .cpp file. These contain parsing logic for
  sequences, instruments (with special handling for drums, skydive vibrato, and octave
  arpeggios), and ADSR envelope extraction — but they are not active.

### Noted Limitations

- Conservative about unexecuted code (remains as data)
- No timer-based sample playback support
- Struggles with multiple driver instances
- No IRQ-based init support
- Partial undocumented opcode support
