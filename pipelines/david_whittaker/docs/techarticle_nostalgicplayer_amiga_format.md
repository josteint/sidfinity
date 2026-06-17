---
source_url: https://github.com/neumatho/NostalgicPlayer/tree/main/Source/Agents/Players/DavidWhittaker
fetched_via: direct (GitHub raw API)
fetch_date: 2026-06-17
author: neumatho (Thomas Neumann) — NostalgicPlayer project
content_date: active development (NostalgicPlayer v1.9+ as of 2026)
reliability: secondary (C# re-implementation of the Amiga .dw format; not the original player)
---

# NostalgicPlayer — David Whittaker Amiga Format: C# Source Analysis

NostalgicPlayer is an open-source C# music player (GitHub: `neumatho/NostalgicPlayer`)
descended from the Amiga APlayer (1993).  It includes a full re-implementation
of David Whittaker's Amiga `.dw` format.

This document summarises the technical content of the player implementation at:
`Source/Agents/Players/DavidWhittaker/`

Files:
- `DavidWhittaker.cs`       — agent interface (minimal, delegates to Worker)
- `DavidWhittakerWorker.cs` — full format parser + playback engine
- `Tables.cs`               — period/frequency lookup tables
- `Containers/Effect.cs`    — effect code enum
- `Containers/ChannelInfo.cs`   — per-channel state
- `Containers/GlobalPlayingInfo.cs` — global playing state
- `Containers/SongInfo.cs`      — per-sub-song metadata
- `Containers/PositionList.cs`  — per-channel orderlist
- `Containers/Sample.cs`        — sample descriptor
- `Containers/Snapshot.cs`      — state snapshot for rewind

---

## Format Summary

David Whittaker's Amiga `.dw` files are binary Motorola 68000 machine code
modules in which the player code and all music data are embedded together.
There is NO separate editor or standard chunk header (unlike IFF/RIFF).

The player recognises multiple variants by scanning for 68000 opcode
sequences characteristic of Whittaker's init and play routines.

File extensions: `.dw`, `.dwold` (older variant).

---

## Format Identification (from DavidWhittakerWorker.cs)

File must be ≥ 2048 bytes.  Files beginning with "SC68" are rejected.

**Init function markers** (M68K opcodes):
- `0x47FA` + `F0+` nibble: `LEA (pc+offset),A3` — relative address load
- `0x6100`: `BSR` (branch to subroutine)
- Sample init patterns: `0x4A2B`, `0x41EB`, `0x41FA`

**Play function markers**:
- `0x47FA 0x4A2B 0x67??`: play function entry
- Delay counter: `0x103A` pattern
- Square waveform animation: `0x207A 0x303A` sequence
- Channel count extraction: `0x7E` instruction + immediate value

**Pointer type detection**:
- `0x2070`: 32-bit MOVEA.L → `uses32BitPointers = true`
- `0x3070`: 16-bit MOVEA.W → `uses32BitPointers = false`

Once identified, the player extracts absolute offsets for:
`subSongListOffset`, `sampleInfoOffset`, `sampleDataOffset`,
`arpeggioListOffset`, `envelopeListOffset` — all computed from
displacement fields in the 68000 init code.

---

## Old vs New Player Variants

| Feature | Old player (QBall) | New player |
|---------|-------------------|-----------|
| Sample metadata | Count only | Full 12-byte Sample struct |
| Channel volumes | `channelVolumeOffset` table | Per-sample volume field |
| Note encoding | `note / 12` → sample; `note % 12` → pitch | Direct sample cmds |
| Period table | Periods1 (12 values, one octave) | Periods2/Periods3 (48/63 values) |
| File extension | `.dwold` | `.dw` |

---

## Sub-song List Structure

Located at `subSongListOffset`.  Scanned until Speed > 255.

```
[Speed: uint16]                        — playback speed
[DelayCounterSpeed: uint8]             — only if enableDelayCounter flag set
[ChannelPositionListPointers: N×ptr]   — 32- or 16-bit ptr per channel
```

Each sub-song is a `SongInfo`:
- `Speed` (ushort)
- `DelayCounterSpeed` (byte)
- `PositionLists` (array of PositionList)

---

## Position List (Orderlist)

Each channel has one `PositionList`:
- Array of `uint32` or `uint16` offsets into track data
- `RestartPosition`: offset for loop restart
- Terminated by zero / out-of-range offset

---

## Track Data (Pattern Stream)

Byte stream per channel:

```
$00–$7F        Note value:
                 old: sampleNumber = note / 12; noteIndex = note % 12
                 new: direct note with sample set by prior command
$80–(newSampleCmd-1)  Effect bytes (see Effect enum)
>= newSampleCmd       Select instrument/sample (index from byte)
>= newEnvelopeCmd     Select envelope (if enabled)
>= newArpeggioCmd     Select arpeggio (if enabled)
$E0–$FF        Speed multiplier: (byte - $DF) * baseSpeed
```

`newSampleCmd`, `newEnvelopeCmd`, `newArpeggioCmd` are derived from the
player binary by the format recogniser (they vary between driver versions).

**Per-frame logic** (Play() method):
1. Check delay counter if `enableDelayCounter`
2. Decrement `ExtraCounter`
3. Update `GlobalVolumeFade`
4. Animate square waveform (`SquareChangePosition` / `SquareChangeDirection`)
5. For each channel:
   - Decrement speed counter
   - If counter == 0: read next track commands until `WaitUntilNextRow`
   - Else: apply ongoing effects (arpeggio, vibrato, slide)

---

## Effect Codes (Amiga)

From `Effect.cs`:

| Hex | Name | Arg bytes | Description |
|-----|------|-----------|-------------|
| $00 | EndOfTrack | 0 | Advance to next position list entry; loop when exhausted |
| $01 | Slide | 2 | Pitch slide: speed + counter (portamento) |
| $02 | Mute | 0 | Silence channel (key-off, no release) |
| $03 | WaitUntilNextRow | 0 | End command processing for this frame |
| $04 | StopSong | 0 | Halt all playback |
| $05 | GlobalTranspose | 1 | Signed byte: shift all notes globally |
| $06 | StartVibrato | 2 | speed + maxValue |
| $07 | StopVibrato | 0 | Disable vibrato on this channel |
| $08 | Effect8 | 1 | Context-dependent: volume fade, channel transpose, or half-volume toggle |
| $09 | Effect9 | 0 or 2 | Disable half-volume OR restart to new position |
| $0A | SetSpeed | 1 | New playback speed (or delay speed if `enableDelayCounter`) |
| $0B | GlobalVolumeFade | 1 | Master volume fade rate |
| $0C | SetGlobalVolume | 1 | Set master volume (0–64) |
| $0D | StartOrStopSoundFx | ? | Enable/disable SFX channel |
| $0E | StopSoundFx | ? | Terminate sound effects |

---

## Arpeggio Table

Located at `arpeggioListOffset`:
- Array of 16-bit offsets, one per arpeggio pattern
- Each pattern: variable-length byte sequence (semitone offsets)
- Terminated by byte with high bit set ($80+)
- Default (no arpeggio): `[0x80]` (single-element, immediate terminator)
- Applied per-frame: advance arp pointer; add semitone offset to current note

---

## Envelope Table

Located at `envelopeListOffset`:
- Array of 16-bit offsets
- Each envelope:
  - Byte 0: speed (ticks per step)
  - Bytes 1+: volume levels 0–127 (high bit = end marker)
- Applied per-frame via `EnvelopeSpeed` / `EnvelopeCounter` in ChannelInfo

---

## Channel State (ChannelInfo.cs fields)

```csharp
int    ChannelNumber
PositionList PositionList
int    CurrentPosition, RestartPosition   // orderlist cursor
byte[] TrackData; int TrackDataPosition   // pattern stream cursor
Sample CurrentSampleInfo                  // active sample
int    Note, Transpose                    // pitch
bool   EnableHalfVolume
int    Speed, SpeedCounter               // tempo

// Arpeggio
byte[] ArpeggioList; int ArpeggioListPosition

// Envelope
byte[] EnvelopeList; int EnvelopeListPosition
int    EnvelopeSpeed, EnvelopeCounter

// Slide (portamento)
bool   SlideEnabled
int    SlideSpeed, SlideCounter, SlideValue

// Vibrato
int    VibratoDirection   // -1, 0, +1
int    VibratoSpeed, VibratoValue, VibratoMaxValue
```

---

## Global State (GlobalPlayingInfo.cs fields)

```csharp
sbyte  Transpose                          // global pitch shift
ushort VolumeFadeSpeed
ushort GlobalVolume
byte   GlobalVolumeFadeSpeed, GlobalVolumeFadeCounter

// Square-wave PWM animation
ushort SquareChangePosition
bool   SquareChangeDirection

// Timing
byte   ExtraCounter
byte   DelayCounterSpeed
ushort DelayCounter
ushort Speed
```

---

## Period / Frequency Tables (Tables.cs)

### Periods1 — 12 values (QBall old player)

One octave, Amiga hardware periods:
```
256 242 228 215 203 192 181 171 161 152 144 136
```

### Periods2 — 48 values (first new player)

Four octaves:
```
4096 3864 3648 3444 3252 3068 2896 2732 2580 2436 2300 2168
2048 1932 1824 1722 1626 1534 1448 1366 1290 1218 1150 1084
1024  966  912  861  813  767  724  683  645  609  575  542
 512  483  456  430  406  383  362  341  322  304  287  271
 256  241  228
```
(Last 3 values beyond original player range, added by NostalgicPlayer
for out-of-range arp/transpose safety.)

### Periods3 — 63 values (newer player)

Over five octaves:
```
8192 7728 7296 6888 6504 6136 5792 5464 5160 4872 4600 4336
4096 3864 3648 3444 3252 3068 2896 2732 2580 2436 2300 2168
2048 1932 1824 1722 1626 1534 1448 1366 1290 1218 1150 1084
1024  966  912  861  813  767  724  683  645  609  575  542
 512  483  456  430  406  383  362  341  322  304  287  271
 256  241  228  215  203  191  181  170  161  152  143  135
```

### EmptyTrack constant

`byte[] EmptyTrack = { 0x80 }` — fallback for channels with no data.

---

## Known Modules (from NostalgicPlayer website)

20 modules in this format, 18 KB – 194 KB file sizes.  The wide size range
reflects both minimal (early games) and rich sample-based (later Amiga games)
variants.  Q-Ball is confirmed as an "old player" variant.

---

## Leads to follow

1. **Full `DavidWhittakerWorker.cs` source** — the analysis here was from
   the WebFetch AI summary; the raw file has all the exact offset derivation
   logic showing how `subSongListOffset` etc. are computed from the 68000 code.
   Raw: `https://raw.githubusercontent.com/neumatho/NostalgicPlayer/main/Source/Agents/Players/DavidWhittaker/DavidWhittakerWorker.cs`

2. **`Containers/PositionList.cs`** — exact PositionList terminator and restart-
   position logic.

3. **`Containers/Sample.cs`** — exact Sample struct field layout with byte offsets.

4. **UADE `uade/players/DavidWhittaker`** (the original Amiga native player binary
   shipped with UADE 2.13) — this is the ORIGINAL 68000 code, not a re-implementation.
   Much higher reliability for format RE.  Check `https://github.com/dv1/uade`.

5. **Modland.com Whittaker .dw files** — the raw .dw files are publicly downloadable
   and can be used to cross-check the format spec:
   `ftp://modland.com/pub/modules/David%20Whittaker/`
