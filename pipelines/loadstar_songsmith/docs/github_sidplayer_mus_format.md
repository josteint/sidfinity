---
source_url: https://raw.githubusercontent.com/MyDeveloperThoughts/ComputeSidPlayerC64Source/main/notes/musFileFormat.md
fetched_via: direct (raw.githubusercontent.com)
fetch_date: 2026-06-14
author: MyDeveloperThoughts (reverse-engineered from COMPUTE!'s Enhanced Sidplayer SID.OBJ.64)
content_date: unknown (repo last active ~2023)
reliability: primary (byte-for-byte disassembly claim: "assembles 100% byte for byte to the original SID.OBJ.64")
---

# COMPUTE!'s Sidplayer / Enhanced Sidplayer — MUS File Format

**CRITICAL CONTEXT: This is the Chamberlain/Bratt MUS format, NOT Loadstar SongSmith.**
See `github_lineage.md` for the lineage analysis and why these are distinct engines.

---

## Repository

**GitHub:** https://github.com/MyDeveloperThoughts/ComputeSidPlayerC64Source  
**Stars:** 14 | **Forks:** 2 | **Language:** 99.9% Assembly (Kick Assembler)  
**Purpose:** Disassembled player routine from COMPUTE!'s Enhanced Sidplayer (1986).
Byte-for-byte match to `SID.OBJ.64`, the standalone player binary.

**Files:**
- `src/sidobj64.asm` — complete Kick Assembler source
- `notes/musFileFormat.md` — MUS format specification (fetched verbatim below)
- `notes/howItWorks.md` — IRQ dispatch and command decode documentation
- `music/` — .MUS file storage

---

## .MUS File Format Specification

(Source: `notes/musFileFormat.md`, verbatim as fetched)

### Binary Layout

.MUS files are PRG files. All 2-byte values are in Lo/Hi order.

| Bytes | Description | Notes |
|---|---|---|
| 0-1 | Load Address | Ignored by SID Editors and Players; they load/save at their own address |
| 2-3 | Voice 1 Data Size | Count of bytes |
| 4-5 | Voice 2 Data Size | Count of bytes |
| 6-7 | Voice 3 Data Size | Count of bytes |
| ... | Voice 1 Data | Always ends in HLT ($01 $4F) |
| ... | Voice 2 Data | Always ends in HLT ($01 $4F) |
| ... | Voice 3 Data | Always ends in HLT ($01 $4F) |
| ... | Song Description | NULL-terminated text describing the song and misc data |

### Voice Data Format

Voice data is a stream of command/option pairs (2 bytes per command). Always ends
with HLT. The bits for command and data are intermixed across both bytes. For example,
POR (Portamento) uses only 2 bits for the command type and 14 bits of data spanning
both bytes.

### Note Command

The command byte has bits 0-1 = 00 (identifies a note vs. a non-note command).

**Note Duration Byte (Command Byte):**

| Bits | Description | Values |
|---|---|---|
| 0-1 | | Always 00 |
| 2-4 | Duration | 010=Whole, 011=Half, 100=Quarter, 101=Eighth, 110=16th, 111=32nd, 000=64th |
| 5 | Dotted | 0=No, 1=Yes |
| 6 | Tie | 0=No, 1=Yes |
| 7 | Double Dotted | 0=No, 1=Yes |

**Note Byte (Option Byte):**

| Bits | Description | Values |
|---|---|---|
| 0-2 | Note to Play | Rest=000, C=001, d=010, e=011, f=100, g=101, a=110, b=111 |
| 3-5 | Octave | Values 0-7, stored EORed with 11111111 |
| 6-7 | Accidental | 10=Normal, 01=Sharp, 11=Flat |

### Command Reference

Non-note commands have bits 0-1 of the command byte = 01, 10, or 11.

| Group | CMD | Name | Command | Option | Voices | Info |
|---|---|---|---|---|---|---|
| **Tempo** | UTL | Utility Jiffy | 00010110 | bbbbbbbb | All | Utility Jiffy All voices (0-255) |
| | TEM | Tempo | 00000110 | bbbbbbbb | All | Set Tempo |
| **Volume** | VOL | Volume | 01 | aaaa1110 | All | Volume 0-15 |
| | BMP | Bump Up/Dn | 01 | nnnnc011 | All | Quick Volume Adjust; c=0 +1, c=1 -1 |
| **Repeat** | HED | Head | 00110110 | bbbbbbbb | V | Start of repeat section; count (0=Infinite) |
| | TAL | Tail | 01 | 00001111 | V | Return to last HED, decrement count |
| **Phrase** | CALL | Call Phrase | 01 | aaaa0010 | V | Play phrase 0-23 |
| | DEF | Define Phrase | 01 | aaaa0110 | V | Start phrase definition 0-23 |
| | END | End Definition | 01 | 00101111 | V | |
| **Envelope** | ATK | Attack | 01 | 0aaaa100 | V | 0-15 |
| | DCY | Decay | 01 | aaan0000 | V | 0-15 |
| | SUS | Sustain | 01 | 1aaaa100 | V | 0-15 |
| | REL | Release | 01 | aaa11000 | V | 0-15 |
| | PNT | Point Release | 00100110 | bbbbbbbb | V | 0-255 |
| | HLD | Hold Time | 01001110 | bbbbbbbb | V | 0-255 |
| **Waveform** | P-W | Pulse Wave | aaaa0010 | bbbbbbbb | V | Pulse-Width 0-4095 (aaaa=Hi4, bb=Lo8) |
| | P-S | Pulse Sweep | 01010110 | bbbbbbbb | V | -128 to 127 |
| | PVD | Pulse Vib Dp | 11000110 | bbbbbbbb | V | Pulse Vibrato Depth 0-127 |
| | PVR | Pulse Vibrato | 11010110 | nbbbbbbb | V | Pulse Vibrato BitRate 0-127 |
| | SNC | Waveform Sync | 01 | 0011c011 | V | c: 0=off, 1=on |
| | RNG | Ring Modulation | 01 | 0101c011 | V | c: 0=off, 1=on |
| | WAV | Waveform | 01 | aaa00111 | V | 000=Noise, 001=Tri, 010=Saw, 100=Pulse, combos |
| **Freq** | VDP | Vibrato Depth | 01110110 | bbbbbbbb | V | 0-127 |
| | VRT | Vibrato Rate | 10000110 | bbbbbbbb | V | 0-127 |
| | POR | Portamento | aaaaaa11 | bbbbbbbb | V | 14-bit value 0-16383 |
| | P&V | Prt and Vibr | 01 | 0111c011 | All | c=0 On, c=1 Off |
| | DTN | Detune | aaaa1010 | bbbbbbbb | V | 12-bit, -2048 to 2047 |
| | TPS | Transpose | 10100110 | bbbbbbbb | V | -95 to 95 half steps |
| | RTP | Relative Transp | 00101110 | bbbbbbbb | V | -47 to 47 from prev note |
| **Filter** | F-M | Filter Mode | 01 | aaa10111 | All | 0=None, 1=LP, 2=BP, 4=HP |
| | AUT | Auto Filter | 10010110 | bbbbbbbb | V | -128 to 127 |
| | RES | Resonance Filter | 01 | aaaa1010 | All | 0-15 |
| | FLT | Filter Through | 01 | 0001c011 | All | c: 0=No, 1=Yes |
| | F-C | Filter Cutoff | 00001110 | bbbbbbbb | V | 0-255 |
| | F-S | Filter Sweep | 01100110 | bbbbbbbb | V | -128 to 127 |
| | F-X | Filter External | 01 | 0100c011 | All | c: 0=No, 1=Yes |
| **Modulation** | LFO | Low Freq Osc | 01 | 0110c011 | All | c: 0=triangle, 1=pulse |
| | RUP | | 01 | aaaaa001 | All | LFO Rate Up 0-31 |
| | RDN | | 01 | aaaaa101 | All | LFO Rate Down 0-31 |
| | SRC | Source | 01 | aaa11111 | V | 0=SW wave, 1=OSC3, 2=ENV3 |
| | DST | Destination | 01 | 1aa01111 | V | 0=Off, 1=Freq, 2=PW, 3=Filter Cutoff |
| | SCA | Mod Scale | 01101110 | bbbbbbbb | V | -7 to 7 |
| | MAX | Mod Max | 11100110 | bbbbbbbb | All | 0-255 |
| **Misc** | MS# | Measure # | aa011110 | bbbbbbbb | V | Combined 10-bit, max 999 |
| | UTV | Util Jif Voice | 11110110 | bbbbbbbb | V | 0-255 |
| | JIF | Jiffy Clock | aa111110 | bbbbbbbb | All | CIA Timer A lo/hi bytes |
| | FLG | Flag | 01000110 | bbbbbbbb | All | Sets FLAG_STATUS |
| | AUX | Auxiliary | 10110110 | bbbbbbbb | All | Future expansion |
| | 3-O | Voice 3 Off | 01 | c011 | V3 | c: 0=no, 1=yes |
| | HLT | HALT | 01 | 01001111 | V | Stop playing voice |

### Tempo Table

| Value | M.M. | Whole | Half | Quarter | 8th | 16th | 32nd | 64th |
|---|---|---|---|---|---|---|---|---|
| $08 | 1800 | 8 | 4 | 2 | 1 | — | — | — |
| $20 | 450 | 32 | 16 | 8 | 4 | 2 | 1 | — |
| $40 | 225 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
| $80 | 112 | 128 | 64 | 32 | 16 | 8 | 4 | 2 |
| $C0 | 75 | 192 | 96 | 48 | 24 | 12 | 6 | 3 |
| $F0 | 60 | 240 | 120 | 60 | 30 | 15 | — | — |
| $00 | 56 | 256 | 128 | 64 | 32 | 15 | 8 | 4 |

(Full table: $08 to $F8 in steps of $08, plus $00 = 256-jiffy whole note.)

---

## IRQ Dispatch Architecture (from howItWorks.md)

- Player installed as user-defined IRQ at $0314 (replaces Kernal EA31 handler).
- Fires 60 times/second from CIA 1 Timer A. Same speed on PAL and NTSC.
- Per-jiffy: for each active voice, decrement jiffy counter; if counter > 0,
  apply effects only; if counter == 0, process all non-note commands until
  next note command, then start note (look up duration in jiffys, program SID).
- Three voices processed sequentially. HLT command silences voice and stops processing it.

**Command routing:** Command byte ANDed with $03. If bits 0-1 == 00, it's a note.
Otherwise bits are LSR'd one at a time to route to the correct handler routine.
Example: POR (Portamento, value 12000): command=$BB (10111011), option=$E0 (11100000).
After two LSRs: acc=00101110 (46), carry-flag sequence routes to POR handler.
Portamento hi byte = 46 (in A), lo byte = $E0=224 from stack: 224 + 256*46 = 12,000.

---

## CGSC Collection

The Compute's Gazette Sid Collection (c64music.co.uk) archives 16,601 .MUS files,
4,383 .STR files (voices 4-6 for stereo), 5,593 .WDS files (lyrics). Available on
Archive.org at https://archive.org/details/ComputesGazetteSidCollection_1_35 (v1.35,
516 files). The `00_Documents/` subdirectory contains `MUS_format_A.txt` and
`MUS_format_B.txt` — two independent format write-ups. Not directly fetched (CGSC
website returned 403), but referenced by multiple sources.

Additional format references:
- `https://ist.uwaterloo.ca/~schepers/formats/SIDPLAY.TXT` — confirms file layout
  (load addr, 3× voice-size words, 3× voice-data streams, text description).
- `https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/SID_file_format.txt` — PSID
  spec Bit 0 indicates "Compute!'s Sidplayer MUS format" (no embedded player; requires
  external SID.OBJ.64 merged for replay).

---

## Leads to Follow

1. **CGSC 00_Documents/** — Fetch MUS_format_A.txt and MUS_format_B.txt by downloading
   the CGSC ZIP from c64music.co.uk (requires browser session, not direct wget).
   Both files have been identified by the Lemon64 thread at
   https://www.lemon64.com/forum/viewtopic.php?t=82359 as the canonical format docs.
2. **Archive.org book scan** (Craig Chamberlain, 1986) — "COMPUTE!'s Music System for
   the Commodore 128 & 64" at https://archive.org/details/Computes_Music_System_for_the_Commodore_128_and_64
   contains full format spec + manual. PDF and full-text versions available. OPEN.
3. **STR format** — 4,383 .STR files exist but no STR format spec was found. Likely
   adds voices 4-6 (stereo second SID chip). OPEN.
4. **WDS format** — lyrics file. Format unknown from this research pass. OPEN.
