---
source_url: https://github.com/Chordian/sidfactory2
fetched_via: git clone
fetch_date: 2026-06-15
author: Thomas Egeskov Petersen (Laxity) and Jens-Christian Huus (JCH / Chordian)
content_date: 2026-06-15 (latest commit)
reliability: primary
---

# SID Factory II — Driver Format Documentation

SID Factory II is the DIRECT descendant of the Laxity Editor → JCH NewPlayer lineage.
Main programming by Thomas Egeskov Petersen (Laxity), with assistance from
Jens-Christian Huus (JCH). It is the authoritative reference for the data format.

Repository cloned to: /home/jtr/sidfinity/tmp/vibrants_laxity_research/sidfactory2/

## Driver naming and versioning

The SF2 `.prg` drivers are in `SIDFactoryII/drivers/`. Naming convention:
- `sf2driver11_00.prg` through `sf2driver11_05.prg` — "The Standard" (6 variants)
- `sf2driver12_00.prg` — "The Barber" (minimal)
- `sf2driver13_00.prg` — "The Hubbard Experience" (emulates Rob Hubbard's sound)
- `sf2driver14_00.prg` — "The Experiment" (short gate-off times)
- `sf2driver15_00.prg`, `sf2driver15_01.prg`, `sf2driver15_02.prg` — "Tiny, mark I"
- `sf2driver16_00.prg`, `sf2driver16_01.prg`, `sf2driver16_01_01.prg` — "Tiny, mark II"
- `sf2driver_np20_00.prg` — **JCH NewPlayer 20.G0 converter target** (see github_jch_source.md)

The `.prg` files are BINARY (compiled 6502 code). No assembly source is in the repo.
The driver contains an embedded metadata header (magic bytes `0x1337` at load address)
that the editor parses to discover table addresses, row/column counts, init/update/stop
addresses, etc. See `docs/src/sf2_driver_info.h` for the full header block layout.

---

## DRIVER 11.xx — "The Standard" (primary / most-used driver)

Documentation sources:
- `dist/documentation/notes_driver11.txt` (saved to `docs/src/sf2_notes_driver11.txt`)
- `macos/player11.md`

### Instrument table (6 bytes per instrument, ColumnMajor layout in memory)

```
Byte 0 — AD          (Attack/Decay nibbles)
Byte 1 — SR          (Sustain/Release nibbles)
Byte 2 — Flags
          $80  Enable hard restart
          $40  Start filter program (byte 3 is then used)
          $20  [11.03+] Enable filter on channel (combined with bitmask in filter prg)
          $10  Oscillator reset (waveform $09 used in first frame of note)
          $08  Skip resetting pulse program on note-on, unless instrument set explicitly
          $0X  Hard restart table index (0-7; selects from HR sub-table)
Byte 3 — Filter table index
Byte 4 — Pulse table index
Byte 5 — Wave table index
```

### Command table (3 bytes per command: T, XX, YY; ColumnMajor layout)

```
T0 XX YY  Slide up/down       XXYY = 16-bit speed (signed)
T1 XX YY  Vibrato             XX = frequency, YY = amplitude (smaller = stronger)
T2 XX YY  Portamento          XXYY = 16-bit speed; use 02 80 00 to disable
T3 XX YY  Arpeggio            XX = speed, YY = arp table index
T4 XX YY  [11.01–11.04] Fret slide  XX = 00-7F speed up / 80-FF speed down, YY = semitones
T8 XX YY  Set local ADSR      XX=AD, YY=SR (until next note)
T9 XX YY  Set instrument ADSR XX=AD, YY=SR (until next instrument)
Ta -- XX  Filter program      XX = table index
Tb -- XX  Wave program        XX = table index
Tc -- XX  [11.02+] Pulse program     XX = table index
Td -- XX  [11.02+] Tempo program     XX = table index
Te -- 0X  [11.02+] Main volume       X = 0-F
Tf -- XX  Increase demo value XX = amount (for timing demo parts)
|T        [11.04] Note event delay   T = 0-F ticks before next note fires
```

### Wave table (2 bytes per row, RowMajor)

```
XX YY     Waveform + semitone
          XX = waveform byte (written to $D404/$D40B/$D412)
          YY = 00-7F → semitones added to note pitch (relative)
               80-DF → absolute semitone (useful for drums: value - $80)
7F XX     Jump to index XX
```

### Pulse table (3 bytes per row, RowMajor)

```
8X XX YY  Set pulse width     XXX = pulse width (12-bit), YY = frame count
0X XX YY  Add to pulse width  XXX = delta added per frame, YY = frame count
7F -- XX  Jump to index       XX (jump to self = end program)
```

### Filter table (3 bytes per row, RowMajor)

```
XY YY RB  Set filter (if X > 8)
          X = passband type (9-F)
          YYY = 12-bit cutoff frequency
          R = resonance nibble
          B = channel bitmask (which voices to filter)
0X XX YY  Add to cutoff       XXX = delta, YY = frame count
7F -- XX  Jump to index       XX
```

### Arpeggio table (1 byte per row, RowMajor)

```
00-6F     Semitones to add (relative arpeggio step)
7X        Jump to start_index + X  (relative jump; used to select arpeggio sub-pattern)
```

Example: `00: 0C / 01: 07 *1 / 02: 04 *2 / 03: 00 / 04: 71`
- Called with command T3 XX 00 → arp at index 0
- Called with command T3 XX 01 → arp starts at *1 (relative jump 1)
- Called with command T3 XX 02 → arp starts at *2 (relative jump 2)

### Hard Restart (HR) sub-table

Up to 8 entries (16 rows in driver ≤11.04, reduced to 8 rows in 11.05).
Entries selected by low nibble of instrument flag byte.

---

## DRIVER 12.00 — "The Barber" (minimal, no programs)

```
Instrument (4 bytes):
  Byte 0 — AD
  Byte 1 — SR
  Byte 2 — Waveform
  Byte 3 — Pulse width XY (X=mid 4 bits, Y=top 4 bits of 12-bit PW)

Commands:
  0X XX   Slide up    XXX = 12-bit speed
  1X XX   Slide down  XXX = 12-bit speed
  2X -Y   Vibrato     X = frequency, Y = amplitude
```

---

## DRIVER 13.00 — "The Hubbard Experience"

Emulates Rob Hubbard's driver sound.

```
Instrument (7 bytes):
  Byte 0 — AD
  Byte 1 — SR
  Byte 2 — Waveform
  Byte 3 — Pulse width XY: X=pulsating speed, Y=high nibble of start PW (Y00)
  Byte 4 — Pulse sweep range
  Byte 5 — Flags:
            $8X  Alternate arpeggio, X=semitones added (also set byte 6)
            $40  Dive effect
            $20  Ignore orderlist transposition
            $10  Add noise in beginning of note
  Byte 6 — Arp properties XY: X=regularity, Y=speed

Commands: same as driver 12 (slide/vibrato only)
```

---

## DRIVER 14.00 — "The Experiment"

Same instrument/table layout as driver 11.00 but WITHOUT flags $20, $10, $08.
Allows very short gate-off durations. Greater risk of instability.

```
Instrument (6 bytes): same layout as driver 11.00
Commands (2 only):
  00 XX YY  Slide up/down   XXYY = 16-bit speed
  01 XX YY  Vibrato         XX = freq, YY = amp
Wave/Pulse/Filter tables: same format as driver 11
```

---

## DRIVER 15.02 — "Tiny, mark I"

Small driver; all player variables in zero page. Hard restart always on.

```
Instrument (5 bytes):
  Byte 0 — AD
  Byte 1 — SR
  Byte 2 — Pulse width XY: X=mid 4 bits, Y=top 4 bits of 12-bit PW
  Byte 3 — Linear pulse sweep XY: X=add to mid 4 bits, Y=add to top 4 bits (per frame)
  Byte 4 — Wave table index

Commands:
  0X XX   Slide up    XXX = 12-bit speed
  1X XX   Slide down  XXX = 12-bit speed
  2X -Y   Vibrato     X = freq, Y = amp
  3X YY   [15.02+] Wave program  YY = table index

Wave table: same format as driver 11
```

---

## DRIVER 16.00 — "Tiny, mark II"

Like driver 15.xx but NO commands at all. Same 5-byte instrument layout.
Zero-page variable scheme. Hard restart always on.

---

## On-disk SF2 format (`.sf2` files)

The `.sf2` format is a PRG (C64 program) with an embedded metadata header at the
load address. Header identification: first 2 bytes = `0x1337`.

Header blocks (TLV structure: block_id byte, size byte, data):
```
ID=1  Descriptor:     driver type (1 byte), driver size (word), driver name (C string),
                      code top (word), code size (word), version major/minor/revision
ID=2  DriverCommon:   addresses of init/stop/update routines; per-voice state addresses
                      (tick counter, orderlist index, sequence index, current sequence,
                       current transpose, event duration, next instrument/command/note,
                       tempo counter, trigger sync)
ID=3  DriverTables:   per-table: type, id, name, data layout (RowMajor/ColumnMajor),
                      properties, rules IDs, address, column count, row count, visible rows
ID=4  InstrumentDescriptor: column description strings
ID=5  MusicData:      track count, orderlist pointer tables (lo/hi), sequence count,
                      sequence pointer tables (lo/hi), orderlist size, track 1 address,
                      sequence size, sequence 0 address
ID=6  TableColorRules
ID=7  TableInsertDeleteRules
ID=8  TableActionRules
ID=9  InstrumentDataDescriptor: links instrument bytes to their target table entries
ID=$FF  End
```

After the header: player 6502 code, then instrument/command/wave/pulse/filter/arp tables,
then orderlist data, then sequence data.

---

## Orderlist on-disk format (packed)

Decoded by `DataSourceOrderList::Unpack()` in `datasource_orderlist.cpp`:

```
Bytes $80-$FD:  Transposition byte; value encodes semitone shift as: (byte & $7F) - $20
                i.e. $A0 = transpose 0, $81 = transpose -31, $BF = transpose +31
Bytes $00-$7F:  Sequence index (the sequence to play next)
$FF LL:         Loop marker — LL = byte offset INTO packed data of the loop point
$FE:            Stop marker (play once, no loop)
```

Run-length compression: a transposition byte applies to all subsequent sequence-index
bytes until the next transposition byte. Transposition is only re-emitted if it changes
OR if it's a loop boundary.

When the SF2 editor unpacks to its internal representation, it stores `(transposition, sequence_index)` pairs. The transposition value internally is the stored byte ($80-$FD range). For the NP20 (JCH) format the transposition was stored differently: NP20 uses raw 7-bit signed offset; SF2 converts via `entry.m_Transposition = 0x20 + np20_transpose`.

---

## Sequence on-disk format (packed)

Decoded by `DataSourceSequence::Unpack()` in `datasource_sequence.cpp`:

```
Byte ranges (read left-to-right per event):
  $C0-$FF   Command byte (sets command; low 6 bits = command index 0-63)
              Always followed immediately by next byte in stream
  $A0-$BF   Instrument byte (low 5 bits = instrument index 0-31)
              Always followed immediately by next byte in stream
  $80-$8F   Duration byte (bits 3-0 = extra ticks; bit 4 = tie note flag)
              Value $80 = duration 0 (1 tick). $8F = duration 15 (16 ticks).
  $90-$9F   Duration with tie flag set (note continues without re-triggering)
  $00-$7F   Note byte — MUST follow; terminates the event:
              $00         Rest (gate off)
              $01-$6F     Notes (semitone 1-111)
              $7E         Gate on / hold (continue previous note)
              $7F         End-of-sequence marker
```

Parsing order within one event packet: optional command ($C0-$FF), optional instrument
($A0-$BF), optional duration ($80-$9F, with tie flag in bit 4), mandatory note ($00-$7F).

Duration encodes extra ticks: the note lasts (duration_value + 1) ticks. The FIRST
note does NOT need a duration byte; if absent, the previous duration is inherited.

---

## Key architectural facts

1. **Three voices**: orderlist pointers for V1/V2/V3 are stored separately (split lo/hi byte
   tables; same scheme as other C64 players).
2. **Sequences** are shared across voices. Same sequence can appear in all three tracks.
3. **Orderlist transposition** is per-entry (not per-sequence). A transpose byte in the orderlist
   shifts ALL notes in sequences played under it.
4. **Tables are shared** across voices (wave, pulse, filter, arp indexed from sequence or command).
5. **Hard restart** is an optional per-instrument feature (flag $80); when active the player
   forces waveform $09 for one frame before triggering the new note.
6. **Tempo table** (driver 11.02+): controls timing in a loop. Default = VBI (50Hz PAL).

---

## Files saved

- `docs/src/sf2_notes_driver11.txt` — driver 11 full format spec (from SF2 dist/)
- `docs/src/sf2_notes_driver12.txt` — driver 12 spec
- `docs/src/sf2_notes_driver13.txt` — driver 13 spec
- `docs/src/sf2_notes_driver14.txt` — driver 14 spec
- `docs/src/sf2_notes_driver15.txt` — driver 15 spec
- `docs/src/sf2_notes_driver16.txt` — driver 16 spec
- `docs/src/sf2_converter.txt` — converter notes (GT2/CT/MOD)
- `docs/src/sf2_converter_jch.cpp` — JCH NP20 → SF2 converter C++ source
- `docs/src/sf2_datasource_orderlist.cpp` — orderlist pack/unpack implementation
- `docs/src/sf2_datasource_sequence.cpp` — sequence pack/unpack implementation
- `docs/src/sf2_driver_info.h` — driver info header struct definitions
