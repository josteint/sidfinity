---
source_url: http://chordian.net/c64editors.htm, https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/
fetched_via: direct
fetch_date: 2026-04-11
author: Chordian (Thomas Egeskov Petersen)
content_date: 2020-08-15 (last modified); DMC 5.0 row added 2018-02-25
reliability: secondary
---

# Chordian C64 Music Editor Comparison — DMC 5.0 Data

Source: http://chordian.net/c64editors.htm (last modified 2020-08-15)
Also referenced at: https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/ (DMC 5.0 added 2018-02-25)

The table compares 14 editors: GoatTracker 2.73/2.74s, CheeseCutter 2.9, SID-Wizard 1.7,
SID Duzz' It 2.1.7, Blackbird 1.2, Virtuoso 1.01, defMON 20171026, NinjaTracker 2.04,
JCH Editor 3.04/NP 20.G4, Polyanna 1.00, **DMC 5.0**, SidTracker 64 1.0.3, DefleMask 0.12.0.

Note: Table covers DMC 5.0 only, not V4 or earlier versions. No V4 column exists.

---

## Package

| Field | DMC 5.0 |
|-------|---------|
| Platform | Native / C64 emulator |
| PAL / NTSC | PAL only |
| Source Code | No (only player source available — see docs) |
| Documentation | See [DMC_V5_DOCS.txt on arnold.c64.org](ftp://arnold.c64.org/pub/utils/music/dmc/DMC_V5_DOCS.txt) and [tnd64.unikat.sk/music_scene.html](http://tnd64.unikat.sk/music_scene.html) |
| Example tunes | No (none bundled) |
| Proprietary file format | (not named in table) |
| Download | [CSDb release #2594](http://csdb.dk/release/?id=2594) |
| Creator | Brian of Graffity, 1993 |

---

## Features

| Field | DMC 5.0 |
|-------|---------|
| Number of SID chips | 1SID |
| Channels visible | 3 order lists + 1 sector |
| Speeds | 1x only |
| Digi / Samples | No |
| Auxiliary support | None (no MIDI, HardSID, etc.) |
| Import from | None |
| Save/Export to | None (editor-native only) |
| Packer | Must use SYS 11776 ($2E00) |
| Relocator | No |
| Load/Save sounds | Instruments (can save/load instrument files) |
| Instruments / Sounds | 32 |
| Sub tunes | 8 |

---

## Player Characteristics

| Field | DMC 5.0 |
|-------|---------|
| Noteworthy | Filter in channel 3 only |
| Size of player | Approx 2000 bytes |
| Zero page usage | At least 2 ($F8-$F9) |
| CPU time (1x) | Approx 23-27 rasterlines (measured with SIDDump) |
| Arpeggio | Wave table with Hi-freq mode |
| Arpeggio: Set in instrument | Pointer to table |
| Arpeggio: Set with command | No |
| Pulsating | Programmable |
| Pulsating: Program table | Yes |
| Pulsating: Set in instrument | Pointer to table |
| Pulsating: Set with command | No |
| Filtering | Programmable (only filter in Ch3) |
| Filtering: Program table | Yes |
| Filtering: Set in instrument | Pointer to table |
| Filtering: Set with command | Set Type/Reso/Cut |
| Vibrato | Yes |
| Vibrato: Set in instrument | 3 bytes |
| Vibrato: Set with command | No |
| Hard restart | Hard-coded |
| First frame waveform | Unknown (?) |
| Gate off timer | Unknown (?) |
| ADSR | Unknown (?) |

---

## Editor Features

| Field | DMC 5.0 |
|-------|---------|
| Track system | Order list with one sector shown |
| Patterns / Sequences | 96 sectors; each up to 250 rows |
| Follow-play | No |
| Copy and Paste | Yes |
| Undo | No |
| Track commands | Bytes in a vertical order list |
| Transpose | 127 half-tones up or down |
| Repeat | No |
| Loop / Stop | Both |
| Volume | No |
| Tempo | No |

---

## Column Structure

### Note Column
| Field | DMC 5.0 |
|-------|---------|
| Example row | Note C#2 |
| Note input layout | Two middle keyboard rows |
| Gating | On or Off (GATE command) |
| Legato / Tie note | Uses a SWITCH command |
| Additional effects | — |

### Instrument / FX / SP Column
| Field | DMC 5.0 |
|-------|---------|
| Example row | Instr SND.01 |
| Instrument / Sound | Instrument (00-1F) |
| Additional effects | — |

### Command Column
| Field | DMC 5.0 |
|-------|---------|
| Example row | Cmd GLD.08 |
| Pointer to wave table | No |
| Pointer to pulse table | No |
| Pointer to filter table | No |
| Pointer to chord/arp table | No |
| Specify slide | Glide to destination note |
| Specify portamento | Glide start to destination note |
| Specify vibrato | Set in instrument |
| Specify ADSR | AD/SR |
| Specify waveform | No |
| Specify pulse width | No |
| Specify filter type | Together with resonance |
| Specify filter resonance | Together with type |
| Specify filter bitmask | Filter in channel 3 only |
| Specify filter cutoff | Yes; 8-bit (MSB) |
| Specify volume | Fade in/out + Affect sustain |
| Specify tempo | No |
| Specify arpeggio speed | No |
| Specify transpose | No |
| Specify finetune | No |
| Specify delay | Uses a DUR command |
| Specify hard restart | No |
| Additional effects | — |

---

## Tables

### Instrument Table
| Field | DMC 5.0 |
|-------|---------|
| Size | **8 bytes per instrument** |
| Names / Descriptions | No |
| View multiple at once | No |
| Pointer to wave table | Yes |
| Pointer to pulse table | Yes |
| Pointer to filter table | Yes |
| Pointer to chord/arp/freq | No |
| Pointer to slide/gliss table | No |
| Pointer to ADSR/tremolo | Uses one ADSR (in instrument) |
| Pointer to vibrato table | Set here in instrument |
| Specify ADSR | Yes |
| Specify vibrato | 3 bytes |
| Specify pulse width/sweep | Set in pulse table |
| Specify filter type/reson. | Set with a command |
| Specify filter cutoff/sweep | Set in filter table |
| Specify arpeggio speed | No |
| Specify hard restart | No; hard-coded |
| Specify octave | No |
| Specify finetune | No |

### Wave Table
| Field | DMC 5.0 |
|-------|---------|
| Row size | **2 bytes per row** |
| Waveform + Gating | All (waveform and gate in table) |
| Relative + Absolute notes | Relative + Hi-frequency (00-FF) |
| Delay/Repeat | No |
| Loop/Stop | Loop only |
| Additional effects | **Hi-freq mode bit replaces test-bit** |

### Pulse Table
| Field | DMC 5.0 |
|-------|---------|
| Row size | **2 bytes per row** |
| Specify pulse width | **12-bit** |
| Duration + Speed | Yes; **16-bit speed** |
| Loop/Stop | Loop only |
| Additional effects | — |

### Filter Table
| Field | DMC 5.0 |
|-------|---------|
| Row size | **2 bytes per row** |
| Specify filter type | Set with a command (not in table) |
| Specify filter resonance | Set with a command (not in table) |
| Specify filter bitmask | Filter in channel 3 only |
| Specify filter cutoff | **11-bit** |
| Duration + Speed | Yes; **16-bit speed** |
| Loop/Stop | Loop only |
| Additional effects | — |

### Chord/Arp/Freq Table
| Field | DMC 5.0 |
|-------|---------|
| Note | Just the wave table only (no separate chord/arp table) |
| Intervals / Notes | — |
| Loop/Stop | — |

### Slide/Glissando Table
| Field | DMC 5.0 |
|-------|---------|
| Note | Set with a command |
| Amplitude | — |
| Delay/Repeat | — |
| Loop/Stop | — |

### ADSR/Tremolo Table
| Field | DMC 5.0 |
|-------|---------|
| Note | Uses one ADSR in instrument |
| Delay/Repeat | — |
| Loop/Stop | — |

### Vibrato Table
| Field | DMC 5.0 |
|-------|---------|
| Note | Set in instrument |
| Delay | — |
| Loop/Stop | — |
| Finetune | — |

### Tempo/Swing Table
| Field | DMC 5.0 |
|-------|---------|
| Note | Set globally |
| Loop | — |

### Volume Table
| Field | DMC 5.0 |
|-------|---------|
| Note | Set globally |
| Fading | Set with a command instead |
| Additional effects | — |

### Command Table (Pattern/Sequence level)
| Field | DMC 5.0 |
|-------|---------|
| Note | **No** (no command table) |

### Unified Table
| Field | DMC 5.0 |
|-------|---------|
| Note | **No** |

---

## Key Technical Notes

- **Hi-freq mode**: The wave table uses a hi-frequency mode bit that **replaces the test-bit**. This means arpeggio notes use hi-freq (00-FF range), not the standard SID test-bit trick.
- **Filter restriction**: Filter only works on **channel 3** (voice 3). Channels 1 and 2 cannot be filtered.
- **Vibrato**: Stored as **3 bytes** in the instrument definition.
- **Pulse width**: 12-bit precision, with 16-bit speed in pulse table.
- **Filter cutoff**: 11-bit precision (MSB available via command), with 16-bit speed in filter table.
- **Instrument size**: Each instrument is **8 bytes**.
- **Wave table**: 2 bytes per row, loop only (no stop marker for patterns — loop is mandatory).
- **Hard restart**: Hard-coded (cannot be adjusted or disabled per-instrument).
- **Glide commands**: Two distinct types — GLD (glide to destination note) and portamento (glide from current to destination).
- **Volume**: No volume column; fade in/out done via command (affects sustain level).
- **Tempo**: Set globally only, no per-pattern or per-row tempo changes.
- **Packer**: Uses SYS 11776 ($2E00) — a BASIC SYS call to a fixed address, not a standalone tool.
- **Only player source available**: The editor source is not public; only the player code is distributed.
- **Documentation**: Officially at arnold.c64.org FTP (DMC_V5_DOCS.txt) and tnd64.unikat.sk.

---

## Version Coverage Note

This comparison table covers **DMC 5.0 only** (1993, by Brian of Graffity). No earlier versions
(V1, V2, V3, V4) are represented in the Chordian table. For V4 vs V5 differences, see:
- `lead_v5_v6_docs.md` — documentation differences
- `lead_variants_and_people.md` — version history and authors
- DMC_V5_DOCS.txt at arnold.c64.org

The comparison was frozen as of 2018-02-25 (when DMC 5.0 was added) and will not be updated
with additional editors or newer versions per the author's note.
