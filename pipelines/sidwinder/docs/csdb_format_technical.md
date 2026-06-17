---
source_url: https://plus4world.powweb.com/software/SIDwinder_V01_23
fetched_via: direct
fetch_date: 2026-06-17
author: Levente Hársfalvi (TLC/Coroners); original documentation by Taki/Natural Beat
content_date: 2000-03-15
reliability: primary
---

# SIDwinder V01.23 — Technical Format Documentation

This is the most complete technical specification available from the bundled ASCII documentation
(extracted from Plus/4 World, which mirrors the in-disk documentation).

## Overview / Capabilities

- Up to **32 subtunes** per music file
- Up to **96 sectors** (each holding up to 256 instructions)
- Up to **64 different instruments**
- Up to **16× music speed** (multi-speed, supported in editor)
- Independent volume control via two registers:
  - `$1673` (volume register)
  - `$165D` (volume control register)
- **PAL only**
- **Zero-page word:** default `$FB–$FC` (changed to `$FC` on Plus/4 to avoid Kernal conflict)

## Data Hierarchy

The format has three levels:
1. **Tracks** — the top-level sequence table for each voice; contains sector references + transpose/volume commands
2. **Sectors** — melodic phrases; contain instrument select + note events + effect commands
3. **Instruments/Sounds** — ADSR + table pointers

## Track Commands

Tracks contain sequences of commands. The allowed command order within one track position is:
```
one JmpXX,  one of IncXX / DecXX / HltVS / VolXX,  one of Tr-XX or Tr+XX
```

| Command | Range | Meaning |
|---------|-------|---------|
| `...XX` | $00–$5F | Play sector number XX |
| `Tr+XX` | $00–$3F | Transpose up XX semitones |
| `Tr-XX` | $00–$3F | Transpose down XX semitones |
| `VolXX` | $00–$0F | Set global volume to XX |
| `DecXX` | $01–$07 | Decremental volume slide at speed XX |
| `IncXX` | $01–$07 | Incremental volume slide at speed XX |
| `HltVS` | — | Halt volume slide; retain current volume |
| `JmpXX` | — | Jump to position XX in track table |

**Rules:**
- Every track MUST contain a `JmpXX` (preferably at the end) or the track won't be saved by the packer
- Track tables must NOT overlap for multi-subtune songs or the packer will crash

## Sector Commands

Each sector follows this strict command sequence:
```
one Snd.XX,  one Dur.XX,  one of { glide, slide, ---, +++ } or a single note,  one Finish
```

| Command | Range | Meaning |
|---------|-------|---------|
| `Snd.XX` | $00–$3F | Select instrument (sound) number XX |
| `Dur.XX` | $01–$40 | Note duration in frames |
| `C-1`…`A#8` | — | Play note (standard chromatic notation) |
| `Gld.XX` | $01–$0F | Glide to next note |
| `Gld.XX` | $11–$1F | Slide to next note (range $11–$1F) |
| `-------` | — | Delay unit; release current note |
| `+++++++` | — | Hold current note; stay in sustain stage |
| `Finish` | — | End of sector marker |

**Important:** Fill sectors **sequentially**. The first empty sector terminates saving — sectors after it are discarded.

## Sound Editor — Seven Parameters

Each instrument is defined by 7 numeric fields:

| Field | Name | Description |
|-------|------|-------------|
| 1 | Attack/Decay | ADSR envelope Attack (hi nibble) and Decay (lo nibble) |
| 2 | Sustain/Release | ADSR Sustain (hi) and Release (lo) |
| 3 | Gateoff counter | How long to wait before gate-off |
| 4 | Wave/Arp table pos | Starting index into the wave/arpeggio table |
| 5 | Filter table pos | Starting index into the filter table |
| 6 | Pulse width table pos | Starting index into the pulse width table |
| 7 | Slide table pos | Starting index into the slide/vibrato table |

## Wave/Arpeggio Table

Entries are 2 bytes: `(WF, AR)` — waveform and arpeggio offset.

| WF value | Meaning |
|----------|---------|
| $00–$8F | Current waveform = WF bits, arpeggio offset = AR |
| $90–$FE | Repeat with new arpeggio offset |
| $FF | Jump to position specified by AR |

## Filter Table

Operates on cutoff frequency (lo+hi bytes) and resonance/filter type.

| RP value | Meaning |
|----------|---------|
| $00–$FD | Repeated addition to frequency and resonance |
| `FH` field | Addition to cutoff frequency high byte or filtertype selection |

Note: "When a filtered instrument is initialized, all the filter parameters (frequency low, high, resonance and filtertype registers) are set to zero."

## Pulse Width Table

| RP value | Meaning |
|----------|---------|
| $00–$FE | Repeated pulse width addition |
| $FF | Jump to position specified by PH |

## Slide/Vibrato Table

| RP value | Meaning |
|----------|---------|
| $00–$FD | Repeated frequency addition (vibrato) |
| $FE | Set absolute frequency (drum mode) |
| $FF | Jump to position specified by FH |

Note on vibrato sync with glides: the table supports "vibrato synchronization during glides."

## Packing Process

The packer is a separate program included on the disk. Configuration options when packing:

1. **Filename** — Song data file (enter `$` for directory listing)
2. **Subsongs** — Number of subtunes (typically '1')
3. **Start Address** — Hex load address (e.g., `1000`)
4. **Zeropage Word** — Default `fb` (change to `fc` on Plus/4 to avoid Kernal conflict)
5. **SID Base Address** — `d400` (C64) or `fd40` (Plus/4 with SID card)
6. **Frequency Table** — Platform selection (C64 or Plus/4 clock-corrected)
7. **Identity Field** — 32 ASCII characters for composer/song info embedded in packed output

### Known Packer Bug (V01.23 original)
Luca/FIRE reported a confirmed bug: "the longer the tune, the higher the probability to collect bugs in endpoints and/or glide/slide."
- TLC released a **fixed packer** separately (for Plus/4; applies to C64 as well)
- The fixed packer is available from Plus/4 World, Rulez.org, Othersi.de

## Player Runtime

### Zero-Page Usage
The default zero-page word is `$FB–$FC`. On Plus/4, change to `$FC` because `$FB` stores actual ROM configuration.

### Clock / Frequency Differences (C64 vs Plus/4)
- C64 SID clock: 17.734472 MHz / 18 ≈ 985,248 Hz
- Plus/4 SID card clock: 17.734472 MHz / 20 ≈ 886,723 Hz
- Ratio: Plus/4 clock = 9/10 of C64 clock
- Effect: "frequency values are about one note lower" on Plus/4
- Effect: "Attack / Decay / Release times (ADSR) are extended"

### C64-to-Plus/4 Conversion Guidelines
- Multiply glide speeds by 10/9
- Multiply absolute slide/vibrato values by 10/9
- ADSR: verify by ear (near-impossible to make "everything sound perfect" due to resolution limits)

### Keyboard Controls (Plus/4 version)

| Key | Action |
|-----|--------|
| F1 | Play / restart music |
| F2 | Stop playing |
| F3 | Continue stopped playback |
| HELP | Fast forward |
| F4 | Play single sector |
| F5 | Enter liveplay mode |
| F6 | Next subtune |
| F7 | Previous subtune |
| ESC | Toggle screens |
| `,` | Toggle SID channel 1 |
| `.` | Toggle SID channel 2 |
| `/` | Toggle SID channel 3 |
| SHIFT+1,2,3 | Track editors (voice 1/2/3) |
| SHIFT+4 | Sector editor |
| SHIFT+5 | Glide/slide table |
| SHIFT+6 | Disk menu |
| SHIFT+7 | Music options |

## Player Fingerprint (sidid.cfg)

The SidWinder player is fingerprinted in cadaver's sidid tool as:
```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```
Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg

Decoded: `LDA abs` `BEQ` `DEC abs` `DEY` `JMP abs` `LDA abs,Y` `CMP #imm` `BCC` `BEQ` `LDA abs,Y` `STA abs` `TAY`
This is characteristic of the track/sector dispatch loop in the player.

## Software Components on Disk

1. **SIDwinder Editor** — main composition environment (tracks, sectors, instruments, all effect tables)
2. **SIDPacker** — compresses/packages the song data into a self-contained PSID-style binary
3. **ASCII Viewer** — text documentation reader (works on C64 and Plus/4; supports 80-col display, TAB conversion, PETSCII printer)

## HVSC Count

117 SID files in HVSC #84 identified as SIDwinder engine.
