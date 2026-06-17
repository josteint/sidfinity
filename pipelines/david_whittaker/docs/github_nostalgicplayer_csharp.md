---
source_url: https://github.com/neumatho/NostalgicPlayer/tree/master/Source/Agents/Players/DavidWhittaker
fetched_via: direct
fetch_date: 2026-06-17
author: neumatho (Polycode / NostalgicPlayer project)
content_date: 2023+ (active project)
reliability: primary (Amiga .dw format; NOT the C64 SID version, same caveats as c-flod)
---

# NostalgicPlayer — DavidWhittaker C# Player Agent

## Repository

- Repo: https://github.com/neumatho/NostalgicPlayer
- Player dir: https://github.com/neumatho/NostalgicPlayer/tree/master/Source/Agents/Players/DavidWhittaker
- License: NostalgicPlayer license (see repo)
- Module catalog page: https://nostalgicplayer.dk/modules/format/davidwhittaker/4

## IMPORTANT CAVEAT

This implements the **Amiga** David Whittaker `.dw` format. Highly relevant for
variant detection and data structure layout but does NOT drive C64 SID registers.
The format description on the catalog page states:
> "This format is not a standard file format like other modules. The music data
> are embedded into an assembler player, so the whole module file contains both
> the player and music."

## Files

```
DavidWhittaker.cs         — agent entry point (factory, IAgent interface)
DavidWhittakerWorker.cs   — ALL parsing logic: format detection, structure
                             extraction, playback engine
Tables.cs                 — static period tables + EmptyTrack fallback
Resources.Designer.cs     — localised strings (IDS_DW_NAME, IDS_DW_DESCRIPTION)
Containers/
  ChannelInfo.cs          — per-channel (voice) runtime state
  Effect.cs               — effect record
  GlobalPlayingInfo.cs    — cross-channel global state
  PositionList.cs         — sequence position list (TrackOffsets[], RestartPosition)
  Sample.cs               — instrument/sample record
  Snapshot.cs             — state snapshot (for seeking/position)
  SongInfo.cs             — per-sub-song: Speed, DelayCounterSpeed, PositionLists[]
```

## Format detection (from DavidWhittakerWorker.cs)

Two-stage probe on raw file bytes:

**Stage 1 — reject SC68 modules:**
```csharp
if ((buffer[0] == 0x53) && (buffer[1] == 0x43)) return false; // "SC"
```

**Stage 2 — find init function via 68000 pattern scan:**
- Search for opcode `0x47FA` (LEA pc-relative) followed by mask `0xF0`
  → locates the main code segment base address (`startOffset`)
- Find init code: scan for `0x6100` (BSR) instruction sequences
- Find play function: `0x47FA` + `0x4A2B` + `0x67xx` pattern

**startOffset calculation:**
```csharp
startOffset = (((sbyte)searchBuffer[index + 2] << 8) |
              searchBuffer[index + 3]) + index + 2;
```

## Player variants distinguished

### Old Player (QBall-era)
- Uses 32-bit absolute pointers throughout
- `Periods1` (12-entry, very limited range, "only used by QBall")
- Sample init in separate sub-function
- Note = `trackByte` (direct index, simpler)
- Effect byte order differs at cases 0–2

### New Player (standard)
- Pointer width detected dynamically:
  - `0x2070` pattern → 32-bit pointers
  - `0x3070` pattern → 16-bit pointers
- `Periods2` (48-entry) or `Periods3` (60-entry, extended for arpeggio overflow)
- `sampleInfoOffset` via `0x4BFA` pattern scan (new format only)
- Extended effect commands with `newSampleCmd` threshold
- Per-sample transpose support

## Data structure offsets (extracted at runtime from binary patterns)

| Field | Detection opcode | Notes |
|---|---|---|
| `startOffset` | `0x47FA` + `0xF0` mask | base address of module |
| `sampleInfoOffset` | `0x4BFA` scan | new player only |
| `sampleDataOffset` | `0x41EB` or `0x41FA` + secondary addition | |
| `subSongListOffset` | `0x41EB`/`0x41FA` scan for song list pointer | |
| `arpeggioListOffset` | jump table command parse | |
| `envelopeListOffset` | jump table command parse | |

## SongInfo structure (per sub-song)

```csharp
class SongInfo {
    ushort Speed;               // tempo
    byte   DelayCounterSpeed;   // timing delay
    PositionList[] PositionLists; // one per sub-song
}

class PositionList {
    uint[]  TrackOffsets;       // offsets to track data for each voice
    ushort  RestartPosition;    // loop restart point in position list
}
```

## ChannelInfo fields (per-voice runtime)

| Field | Type | Purpose |
|---|---|---|
| `PositionList` | ref | current sub-song's position list |
| `CurrentPosition`, `RestartPosition` | int | sequence position |
| `TrackData`, `TrackDataPosition` | byte[], int | current track bytes |
| `CurrentSampleInfo` | Sample | active instrument |
| `Note` | byte | current pitch |
| `Transpose` | sbyte | pitch offset |
| `EnableHalfVolume` | bool | volume flag |
| `Speed`, `SpeedCounter` | int, int | tempo / frame counter |
| `ArpeggioList`, `ArpeggioListPosition` | byte[], int | arpeggio sequence |
| `EnvelopeList`, `EnvelopeListPosition` | byte[], int | volume envelope |
| `EnvelopeSpeed`, `EnvelopeCounter` | int, int | envelope timing |
| `SlideEnabled`, `SlideSpeed`, `SlideCounter`, `SlideValue` | bool, int*3 | portamento |
| `VibratoDirection`, `VibratoSpeed`, `VibratoValue`, `VibratoMaxValue` | int*4 | vibrato |

## Sample record fields

```csharp
class Sample {
    short   SampleNumber;
    sbyte[] SampleData;      // PCM audio
    uint    Length;
    int     LoopStart;
    ushort  Volume;
    ushort  FineTunePeriod;  // pitch fine-tune
    sbyte   Transpose;       // semitone offset
}
```

## Pattern command encoding (new player)

| Byte range | Meaning |
|---|---|
| 0x00–0x7F | Note value |
| 0x80 | End-of-track / loop |
| 0x81 | Portamento |
| 0x82 | Note-end (mute) |
| 0x83 | Note-restart |
| 0x84 | Song-end |
| 0x85 | Global transpose (1 byte follows) |
| 0x86 | Vibrato on (2 bytes: speed, depth) |
| 0x87 | Vibrato off |
| 0x88–0x8C | Variant-specific (fade, volume, delay) |
| >= newSampleCmd | Sample selection |
| >= newEnvelopeCmd | Envelope reference |
| >= newArpeggioCmd | Arpeggio reference |
| 0xE0–0xFF | Speed multiplier: rows to wait = byte − 0xDF |

## Period tables (from Tables.cs)

```
Periods1 (12 entries — QBall-only old player):
  256, 242, 228, 216, 203, 192, 181, 171, 161, 152, 144, 136

Periods2 (48 entries — first/standard player):
  4096, 3867, 3649, ... down to 228
  (comment: "additional periods were added beyond original to handle arpeggio
   or transpose exceeding normal ranges")

Periods3 (60 entries — newer player, extended range):
  8192, 7735, 7298, ... down to 135

EmptyTrack: [0x80]  — fallback when a track slot is unused
```

## Mapping to C64 player

The Amiga player's `PositionList.TrackOffsets[]` per voice maps to C64's
`Track1Seq`/`Track2Seq`/`Track3Seq` tables. Sub-songs are handled by iterating
`SongInfo.PositionLists[]`.  The C64 Panther has only 1 song; Amiga versions
can be multi-sub-song. The arpeggio/envelope list architecture matches the
C64 `ArpTable` at the concept level.

## Raw file URLs

- DavidWhittakerWorker.cs: https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/DavidWhittakerWorker.cs
- Tables.cs: https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Tables.cs
- Containers/ChannelInfo.cs: https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Containers/ChannelInfo.cs
- Containers/SongInfo.cs: https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Containers/SongInfo.cs
- Containers/Sample.cs: https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Containers/Sample.cs
- Containers/PositionList.cs: https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Containers/PositionList.cs

## Leads to follow

- Full DavidWhittakerWorker.cs for the complete detection + playback logic:
  https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/DavidWhittakerWorker.cs
- NostalgicPlayer module catalog (lists all playable .dw tunes):
  https://nostalgicplayer.dk/modules/format/davidwhittaker/4
- Effect.cs container (effect record fields not yet fetched):
  https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Containers/Effect.cs
- GlobalPlayingInfo.cs (cross-voice global state):
  https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Containers/GlobalPlayingInfo.cs
