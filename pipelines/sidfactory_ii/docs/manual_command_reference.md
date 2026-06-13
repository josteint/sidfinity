---
source_url: https://github.com/Chordian/sidfactory2/releases/download/release-20260314/SIDFactoryII-linux.zip
fetched_via: direct
fetch_date: 2026-06-13
author: Jens-Christian Huus (manual); Thomas Egeskov Petersen (editor/driver)
content_date: 2026-03-14
reliability: primary
secondary_sources:
  - http://files.chordian.net/sf2/SIDFactoryII_20260314_User_Manual.pdf (primary PDF manual)
  - https://blog.chordian.net/2022/08/27/composing-in-sid-factory-ii-part-4-instruments/
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/driver/driver_info.cpp
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/datasources/datasource_orderlist.cpp
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/datasources/datasource_sequence.cpp
---

# SID Factory II — Command Reference (Driver 11)

Source: `documentation/notes_driver11.txt` from the official release archive (build 20260314).
This is the **primary technical reference** for driver 11 (the default/standard driver).

## Driver 11 Version History

| Version | Added feature |
|---------|--------------|
| 11.00   | Original default driver |
| 11.01   | Fret slide command (T4) |
| 11.02   | Pulse table index command (Tc), tempo table index command (Td), main volume command (Te) |
| 11.03   | Filter enable flag bit (bit 5 = $20) in instrument byte 2 |
| 11.04   | Note event delay (single-nibble command encoding) |
| 11.05   | Fret slide removed; HR table size decreased from 16 to 8 rows; skip pulse reset flag added (bit 3 = $08 in instrument byte 2) |

## Command Table Format

Commands are 3-byte entries: **opcode byte** (Tx nibble, hi = type, lo = sub), then **XX** and **YY**.

The command column in a sequence stores a 1-byte index into the command table (0x00–0x3F).
In the packed sequence stream, a command value is encoded as `0xC0 + index` (range $C0–$FF).

### Command Encoding Summary

```
T0 XX YY - Slide up/down        XXYY = 16-bit speed (signed — positive = up, negative = down)
T1 XX YY - Vibrato              XX   = frequency (period of oscillation)
                                 YY  = amplitude (SMALLER values = STRONGER vibrato)
T2 XX YY - Portamento           XXYY = 16-bit speed
                                 (use 02 80 00 to disable a runaway portamento)
T3 XX YY - Arpeggio             XX   = arpeggio speed
                                 YY  = arpeggio table index
T4 XX YY - [11.01-11.04 only]
           Fret slide            XX   = 00-7F = speed upward
                                        80-FF = speed downward
                                 YY  = semitones to slide
T8 XX YY - Set local ADSR       XXYY = ADSR (lasts until next note is triggered)
T9 XX YY - Set instrument ADSR  XXYY = ADSR (lasts until a different instrument is used)
Ta -- XX - Filter program        XX   = filter table index
Tb -- XX - Wave program          XX   = wave table index
Tc -- XX - [11.02+] Pulse prg   XX   = pulse table index
Td -- XX - [11.02+] Tempo prg   XX   = tempo table index
Te -- -X - [11.02+] Main volume X    = 0-F main volume ($D418 bits 0-3)
Tf -- XX - Increase demo value  XX   = amount (for timing demo parts / sync)
|
T        - [11.04 only]
           Note delay            T    = 0-F ticks of delay before the note triggers
```

### Note on amplitude/vibrato polarity:
In the vibrato command (T1), **smaller YY = stronger vibrato** (counter-intuitive). YY=01 is
maximum vibrato depth; YY=7F is a very subtle wobble.

### Note on portamento:
Portamento (T2) slides the pitch from the previous note frequency to the new note's frequency
at 16-bit speed XXYY per frame. Use `02 80 00` to cancel a portamento that has gone wild.

### Note on arpeggio (T3) and the arpeggio table:
The arpeggio table is separate from the wave table. Values are semitones added to the note.
The arpeggio table index YY determines which arp pattern plays, and XX controls speed.
**In driver 11, the arpeggio ONLY affects wave table rows where the semitone add value is 00.**
Non-zero wave table semitone offsets bypass the arpeggio entirely.

Arpeggio table format:
```
XX        - arp step if XX < $70   (XX = semitones to add to current note)
7X        - jump to relative index X within the arp table
```

Example arp table:
```
00: 0C          ; +12 semitones (one octave up)
01: 07  *1      ; +7 semitones
02: 04  *2      ; +4 semitones
03: 00          ; +0 (root)
04: 71          ; jump to *1 if called with T3 XX 00, jump to *2 if called with T3 XX 01
```

## Driver 12 ("The Barber") — Commands

Simple driver, no tables. Commands are 2-byte entries.

```
0X XX - Slide up       XXX = 12-bit speed
1X XX - Slide down     XXX = 12-bit speed
2X -Y - Vibrato        X   = frequency    Y = amplitude
```

## Driver 13 ("The Hubbard Experience") — Commands

Emulates Rob Hubbard's player sound. Commands are 2-byte entries.

```
0X XX - Slide up       XXX = 12-bit speed
1X XX - Slide down     XXX = 12-bit speed
2X -Y - Vibrato        X   = frequency    Y = amplitude
```

## Driver 14 ("The Experiment") — Commands

Experimental approach to SID writes; allows very short gate-off durations (instability risk).
Commands are 3-byte entries.

```
00 XX YY - Slide up/down   XXYY = 16-bit speed
01 XX YY - Vibrato         XX   = frequency    YY = amplitude
```

Wave, pulse, filter tables identical to driver 11 (see `manual_table_formats.md`).

## Driver 15 ("Tiny, mark I") — Commands

Small driver; all variables in zero page.

```
0X XX - Slide up       XXX = 12-bit speed
1X XX - Slide down     XXX = 12-bit speed
2X -Y - Vibrato        X   = frequency    Y = amplitude
3X YY - Wave program   YY  = wave table index    [added in 15.02]
```

Has wave table (same semantics as driver 11). Hard restart is always on.

## Driver 16 ("Tiny, mark II") — Commands

Like driver 15 but with NO commands at all. Has wave table. Hard restart always on.

## Leads to follow

- The `notes_driver11.txt` file (copied to `docs/src/`) is the authoritative command reference.
- The F12 overlay PNG (`linux_driver11_05.png` in `tmp/sidfactory_ii_research/sf2_docs/`) shows the
  full help screen including color-coded table explanations — useful for visual cross-reference.
- Effect SID register mapping is in `manual_effect_semantics.md`.
