---
source_url: https://github.com/realdmx/c64_6581_sid_players/blob/main/Whittaker_David/Whittaker_David_Panther.asm
fetched_via: direct
fetch_date: 2026-06-17
author: dmx87 (GitHub handle: realdmx)
content_date: 2023-04-23 (single commit "Create Whittaker_David_Panther.asm", hash 0f538e1e4f6920f0a4feeb718fc6b347cca004bd)
reliability: primary
---

# realdmx/c64_6581_sid_players — Whittaker_David_Panther.asm

## Repository

- Repo: https://github.com/realdmx/c64_6581_sid_players
- File: https://github.com/realdmx/c64_6581_sid_players/blob/main/Whittaker_David/Whittaker_David_Panther.asm
- Raw:  https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Whittaker_David/Whittaker_David_Panther.asm

The repository covers ~14 composers: Audial Arts, Bjerregaard (MON), Bulka Adam
(FAME), Deenen Charles (MON), Dunn Jonathan, Galway Martin, Gray Fred, Gray
Matt, Hubbard Rob, Kimmel Jeroen, Ouwehand Reyn (MON), Tel Jeroen (MON), and
Whittaker David. All sources target ACME assembler and assemble to playable .sid
files.

## State of Whittaker coverage

**Only one file exists**: `Whittaker_David/Whittaker_David_Panther.asm`.
One commit only (2023-04-23). No further Whittaker tunes have been added as of
2026-06-17. There is no README in the Whittaker_David folder.

Note: the existing repo file `/home/jtr/sidfinity/pipelines/david_whittaker/docs/src/Whittaker_David_Panther.asm`
appears to have been salvaged from this same source. Confirm byte-for-byte
identity before trusting the copy.

## PSID header (as encoded in the .asm)

| Field | Value |
|---|---|
| Format | PSID v2 |
| Title | "Panther" |
| Composer | "David Whittaker" |
| Copyright | "1986 Mastertronic" |
| Load address | $9000 |
| Init address | $9000 |
| Play address | $9151 (from CSDb) |
| SID model | 6581 |
| Clock | PAL |
| Data size | 3328 bytes ($D00) |
| Songs | 1 |

## Player structure — Panther

### Memory map (load at $9000)

```
$9000        init        — initialization: sets up v1/v2/v3 state, loads
                           first pattern pointers from track sequences,
                           resets SID chip, sets tempo
$9151        play        — main IRQ: decrements tempo counter, calls GetNote
                           for each voice, then SoundUpdate
?            GetNote     — pattern parser: reads pattern bytes, processes
                           command/effect codes, manages note duration counters
?            SoundUpdate — frequency calculation, arpeggio, portamento/glide,
                           PWM sweep, writes to $D400-$D418
```

### Voice data blocks

Three 36-byte state blocks: `v1data`, `v2data`, `v3data`

Named offset constants (prefix `VD_`):
- `VD_FLAGS` — waveform / gate flags
- `VD_PAT`   — current pattern pointer (low/high)
- `VD_TRACK` — current track sequence pointer
- `VD_...`   — additional fields (see disassembly.s when annotated)

### Pattern command encoding

Commands are bytes $80–$93 dispatched via `CommandTable`:

| Byte | Effect |
|---|---|
| $80 | `L_93FB` (unknown — likely tempo or loop) |
| $81–$83 | Envelope/ADSR variants |
| $84–$85 | Flag set operations |
| $86–$87 | More flag operations |
| $88 | Pattern jump |
| $89 | Modulation setup |
| $8A | Noise waveform |
| $8B | Pulse waveform |
| $8C | Sawtooth waveform |
| $8D | Triangle waveform |
| $8E | Master volume |
| $8F | Pulse width high byte |
| $90 | 3-byte pattern data load |
| $91 | Stop music |
| $92 | Ring modulation + Triangle |
| $93 | Sync + Square |

### Data tables

| Table | Description |
|---|---|
| `NoteFreqsL` / `NoteFreqsH` | 96-entry (8 octaves × 12) note frequency lo/hi |
| `ArpTable` | 13 arpeggio patterns, each terminated by a sentinel value |
| `CommandTable` | 20-entry jump table ($80–$93, 2 bytes each) |
| `Track1Seq` / `Track2Seq` / `Track3Seq` | Per-voice track sequences (56 entries each), holding pattern pointers |
| Pattern data | Multiple inline patterns in compact bytecode |

### Effects implemented in Panther

From `SoundUpdate`:
- Arpeggio (via `ArpTable`)
- Frequency modulation / vibrato
- Pulse width sweep (PWM)
- Portamento (likely — `VD_PAT` range has a slide-speed field)

## Significance for this project

This disassembly is the **primary RE artifact** for the Whittaker C64 player.
It is the only known hand-annotated ACME reconstruction in the public domain.
It covers a representative 1986 tune but does NOT cover:
- Early engine variants (1984–1985: Lazy Jones, Red Max)
- Potential later engine variants
- Multi-subtune support (Panther has 1 song)

## Leads to follow

- Raw ASM file: https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Whittaker_David/Whittaker_David_Panther.asm
- All realdmx repo files: https://github.com/realdmx/c64_6581_sid_players/tree/main
- dmx87's GitHub profile: https://github.com/realdmx
  — check for other repos that might contain additional Whittaker tunes
- CSDb Panther SID page: https://csdb.dk/sid/?id=30421
  — Panther is load=$9000 init=$9000 play=$9151 size=$D00 bytes
- CSDb Lazy Jones SID page: https://csdb.dk/sid/?id=30405
  — a 1984 tune; likely an earlier engine variant
- Pull-request the realdmx repo to add further Whittaker tunes (Lazy Jones,
  Glider Rider, Red Max) — the existing Panther file proves dmx87 intends to
  grow the Whittaker set
