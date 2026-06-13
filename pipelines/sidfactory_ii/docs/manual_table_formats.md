---
source_url: https://github.com/Chordian/sidfactory2/releases/download/release-20260314/SIDFactoryII-linux.zip
fetched_via: direct
fetch_date: 2026-06-13
author: Jens-Christian Huus (documentation); Thomas Egeskov Petersen (driver code)
content_date: 2026-03-14
reliability: primary
secondary_sources:
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/datasources/datasource_orderlist.cpp
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/datasources/datasource_sequence.cpp
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/driver/driver_info.h
  - https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/packer/packer.cpp
  - https://blog.chordian.net/2022/08/27/composing-in-sid-factory-ii-part-4-instruments/
---

# SID Factory II — Table Formats Reference

Primary source: `documentation/notes_driver11.txt` from official build 20260314 archive.
Supplemented by source code analysis of the editor's datasource and driver modules.

---

## Song Structure Overview

Three levels of hierarchy (all three voices are independent):

```
Order List  (voice 1, 2, 3 — each independent length)
    └── Sequence (shared pool, up to 128 entries, packed to ≤256 bytes each)
            └── Row (instrument | command | note/gate)
```

The tempo table controls timing. All three voices share the same sequence pool and table data;
only order lists are per-voice. Multi-song support: each song has its own init table entry
(tempo + main volume), but all songs share sequences and instrument/command/table data.

---

## Order List Format (Binary / Packed)

**Logical view in the editor:** Each entry is shown as `XXYY` where XX = transpose byte,
YY = sequence number.

**Packed binary format** (from `datasource_orderlist.cpp`):

```
byte >= 0x80  →  transpose value
                 actual_transpose = (byte & 0x7F) - 0x20
                 default/no-transpose = 0xA0  →  (0xA0 & 0x7F) - 0x20 = 0x00
                 range: 0x80 (-32 semitones) to 0xBF (+31 semitones)

byte < 0x80   →  sequence index (0x00–0x7F = sequences 0–127)

0xFE          →  end marker (song loops to position 0 in the order list)
0xFF          →  end marker with explicit loop point
                 followed by one byte = packed-data offset of the loop target
```

The transpose byte is optional (omitted if the transpose does not change from the previous entry).
A transpose byte immediately before a sequence number applies to that sequence.

**Transpose examples:**
- `A0 03` — sequence 03, no transpose (A0 = identity)
- `A7 03` — sequence 03, transposed +7 semitones
- `A5 03` — sequence 03, transposed +5 semitones
- `94`    — transpose to -12 semitones (one octave down), applies to next sequence
- `AC`    — transpose to +12 semitones (one octave up), applies to next sequence

---

## Sequence Format (Binary / Packed)

Sequences are packed into at most 256 bytes. Up to 128 sequences exist (0–127). Maximum
1024 rows before packing.

**Packed byte encoding** (from `datasource_sequence.cpp`):

```
0x00          →  note off (gate off, same as --- in the editor)
0x01–0x6F     →  note values (note on at this pitch)
0x7E          →  gate on without new note (+++ in the editor)
0x7F          →  end-of-sequence marker
0x80–0x8F     →  duration = (byte & 0x0F) ticks (no tie)
0x90–0x9F     →  duration = (byte & 0x0F) ticks WITH tie note flag (**) set
0xA0–0xBF     →  instrument select, index = (byte & 0x1F)  →  instruments 0x00–0x1F
0xC0–0xFF     →  command select, index = (byte & 0x3F)     →  commands 0x00–0x3F
```

**Row structure in the sequence:**
Each row in the logical editor has three columns: instrument (optional), command (optional), note.
In the packed stream, these are encoded as consecutive bytes in the order they are set:
  1. Optional command byte (0xC0–0xFF) if a new command is set
  2. Optional instrument byte (0xA0–0xBF) if a new instrument is set
  3. Duration byte (0x80–0x9F) if row has a specific duration
  4. Note/gate byte (0x00–0x7E) or end marker (0x7F)

**Tie note (`**`):** Encoded by using duration range 0x90–0x9F. When a row is tied, the note
does NOT re-trigger — no gate edge, no instrument/effect restart. Used for portamento (glide
from previous note to new one) or sustained notes where gate re-triggering is undesirable.

**Gate semantics:**
- Note byte (0x01–0x6F): gates ON a new note at the specified pitch
- 0x7E (`+++`): gates ON without changing pitch (extend current note)
- 0x00 (`---`): gates OFF (releases the ADSR envelope)
- No note byte (sequence just contains instrument + command + duration): maintains current state

---

## Instrument Table Format (Driver 11)

6 bytes per instrument row. Up to 256 instruments (0x00–0xFF index space, though practical
limit depends on driver). Instruments are referenced from sequences as 0xA0–0xBF → index 0–31
in the packed stream (so the practical limit for the standard packed format is 32 instruments).

```
Byte 0: AD   — Attack (bits 7-4) + Decay (bits 3-0)
               Attack:  0 = ~2ms,  F = ~8s
               Decay:   0 = ~6ms,  F = ~24s
Byte 1: SR   — Sustain (bits 7-4) + Release (bits 3-0)
               Sustain: 0 = silence, F = maximum level
               Release: 0 = ~6ms,  F = ~24s
Byte 2: Flags  (bit field — see below)
Byte 3: Filter table index  — start row in filter table (used when bit 6 set)
Byte 4: Pulse table index   — start row in pulse table
Byte 5: Wave table index    — start row in wave table
```

**Instrument byte 2 flag bits (Driver 11):**

```
Bit 7 ($80) — Enable hard restart
Bit 6 ($40) — Start filter program (use filter table index in byte 3)
Bit 5 ($20) — [11.03+] Enable filter on this channel (combined with bitmask in filter program)
Bit 4 ($10) — Oscillator reset (waveform $09 written in the first frame of a note; unlocks oscillator)
Bit 3 ($08) — [11.05+] Skip resetting the pulse program on note-on, unless the instrument
               is being set EXPLICITLY (not carried over from a previous note)
Bits 2-0 ($07, but encoded as 0X nibble) — Hard restart table index (0–7)
```

Combined example: `$90` = hard restart enabled (bit 7) + oscillator reset (bit 4).
`$C0` = hard restart enabled (bit 7) + filter program start (bit 6).

**Instrument table format for other drivers:**

Driver 12 / 15 / 16 (4 bytes):
```
Byte 0: AD
Byte 1: SR
Byte 2: Waveform (for 12/13) OR Pulse width XY (for 15/16)
          Pulse width byte: X = middle 4 bits, Y = top 4 bits (12-bit PW = Y<<8 | X<<4)
Byte 3: (12) Pulse width XY  OR  (15/16) Linear pulse sweep XY
              Linear sweep: X = add to mid 4 bits per frame, Y = add to top 4 bits
Byte 4: (15/16) Wave table index
```

Driver 13 (7 bytes — Hubbard emulation):
```
Byte 0: AD
Byte 1: SR
Byte 2: Waveform
Byte 3: Pulse width XY  (X = pulsating speed, Y = high nibble start pulse width = Y00)
Byte 4: Pulse sweep range
Byte 5: Flags ($8X=alternate arpeggio+semitones, $40=dive, $20=ignore transpose, $10=add noise)
Byte 6: Arp properties XY  (X = regularity, Y = speed)
```

---

## Wave Table Format (Driver 11 / 14 / 15 / 16)

2 bytes per row. Processed one row per driver tick.

```
Byte 0: Waveform control / loop marker
Byte 1: Note offset / absolute pitch / jump target
```

**Waveform values (byte 0):**

```
$11  — Triangle waveform (SID $D404/$D40B/$D412 bit pattern $11)
$21  — Sawtooth waveform
$41  — Pulse waveform (requires pulse table or PW in instrument)
$81  — Noise waveform (ring mod/oscillator sync bits must be clear)
$31  — Triangle + Sawtooth (combined)
$51  — Triangle + Pulse
$61  — Sawtooth + Pulse
$71  — Triangle + Sawtooth + Pulse
$09  — Oscillator reset waveform (test bit: $04 combined with no waveform; used for HR / osc reset)
       The waveform $09 = test bit $08 + gate $01; it holds the oscillator in reset.
       This is what happens in the FIRST frame of a note when bit 4 ($10) is set in the instrument.
```

The gate bit (bit 0 = $01) is typically always set in waveform bytes while the note is on.
Clearing bit 0 (e.g. $10, $20, $40, $80) gates OFF while maintaining the waveform selection.
Example: $80 instead of $81 = noise waveform with gate OFF.

**Byte 1 — Note offset / absolute pitch:**
```
$00–$7F  — Relative semitone add value added to the note from the sequence
            $00 = play at the sequence note pitch
            $0C = play one octave up
            $FF (i.e. byte value $7F) = ... actually $7F triggers the loop/jump (see below)
$80–$DF  — Absolute semitone value (ignores the sequence note entirely)
            Useful for drums and fixed-pitch sounds that should not follow melody transpositions
```

**Loop / Jump row (byte 0 = $7F):**
```
$7F XX   — Jump to wave table row XX (absolute index)
           Jumping to the current row creates an infinite loop (sustain current waveform)
           Example: $7F $02 means jump back to row 2
```

The $7F jump is the ONLY way to loop in the wave table. A wave table program that doesn't
end with a $7F entry will fall off the end into whatever data follows — always terminate with
a $7F self-loop or a loop-back.

---

## Pulse Table Format (Driver 11 / 14)

3 bytes per row. Controls 12-bit pulse width ($D402/$D403, $D409/$D40A, $D410/$D411).

```
8X XX YY  — Set pulse width:    XXX = 12-bit pulse width value (0–4095)
                                  YY  = number of frames to hold this width before advancing
0X XX YY  — Add to pulse width: XXX = signed 12-bit value added to current pulse width per frame
                                  YY  = number of frames to perform this addition before advancing
7F -- XX  — Jump to index:      XX  = target row index
            (jumping to own index terminates / loops the pulse program)
```

**Pulse width range note:** The effective sound of PW is symmetric around 2048.
PW=0 and PW=4095 sound identical (silent). PW=2048 is widest (50% duty cycle = fullest sound).
Values 0 and 4095 / 10 and 4085 / 1000 and 3095 produce identical audio.

**Typical use:** A pulse program starts by setting a base width (8X), then sweeps it using
add rows (0X), then loops back to produce the characteristic "swooping" sound.

---

## Filter Table Format (Driver 11 / 14)

3 bytes per row. Controls the single global SID filter (cutoff $D415/$D416, resonance+routing $D417,
mode+main-vol $D418).

```
XY YY RB  — Set filter (if X >= 9, i.e. upper nibble of first byte > 8):
              X    = passband (9=HP+BP, A=HP, B=BP, C=HP+LP, D=BP+LP, E=LP, F=LP+HP+BP = all)
              YYY  = 12-bit cutoff frequency (0–2047, 11 bits; stored as 12-bit in table)
              R    = resonance (0=none, F=maximum; upper nibble of byte 2)
              B    = channel bitmask (bit 0=voice1, bit 1=voice2, bit 2=voice3)
                     Examples: 1=V1 only, 3=V1+V2, 7=all voices, 4=V3 only
0X XX YY  — Add to cutoff frequency:
              XXX  = signed 12-bit value added to cutoff per frame
              YY   = number of frames before advancing to the next row
7F -- XX  — Jump to index: XX = target row index
            (jumping to own index loops / sustains the filter program)
```

**Filter mode bit values (X nibble of first byte for set-filter rows):**
These correspond to SID $D418 bits 7-4:
- $9x = High-pass + Band-pass
- $Ax = High-pass
- $Bx = Band-pass
- $Cx = High-pass + Low-pass (notch filter)
- $Dx = Band-pass + Low-pass
- $Ex = Low-pass
- $Fx = All modes (voice 3 off effect when combined with specific routing)

**[11.03] Filter enable per instrument:**
From driver 11.03 onwards, bit 5 ($20) in instrument byte 2 enables filter on the instrument's
channel, combining with the channel bitmask in the filter program. This allows per-instrument
filter routing without changing the global bitmask.

---

## Hard Restart (HR) Table Format (Driver 11)

2 bytes per row. Applied exactly **2 frames before** the next note triggers.

```
Byte 0: AD  — alternative Attack+Decay ADSR values for the hard restart phase
Byte 1: SR  — alternative Sustain+Release values for the hard restart phase
```

**Typical values:** `$0F $00` — very fast release (Attack=0, Decay=0, Sustain=0, Release=F).
This cuts the current note quickly and stabilizes the ADSR hardware before the next note.

**Table size:** 16 rows in driver 11.00–11.04; reduced to **8 rows** in driver 11.05.
The HR table index in instrument byte 2 (bits 2-0 = 0–7) must stay within this range.

**Mechanics:** When hard restart is enabled in the instrument ($80 flag):
- Frame N-2 before new note: gate OFF, apply HR ADSR, apply HR waveform ($09 = test bit)
- Frame N-1: HR continues
- Frame N (new note): gate ON, apply instrument ADSR, begin wave table from instrument's wave index

---

## Init Table Format (Driver 11)

2 bytes per row. One row per song in multi-song files.

```
Byte 0: Tempo table index — which row in the tempo table to start from
Byte 1: Main volume ($D418 low nibble) — typically $0F (maximum)
```

---

## Tempo Table Format (Driver 11)

1 byte per row. Defines the speed of the song.

```
Byte N:   Duration in driver frames for one sequence row.
          PAL = 50 frames/second; NTSC = 60 frames/second.
          Value $02 = 2 frames per row (fastest practical with hard restart).
          Value $06 = 6 frames per row (typical moderate tempo).
$7F:      Loop marker — wrap back to the start of the tempo table.
```

A chain of different values creates swing or tempo changes. Example: `$06 $05 $7F` produces
a 6-frame / 5-frame alternating shuffle rhythm.

---

## Arpeggio Table Format (Driver 11)

1 byte per row.

```
XX ($00–$6F)  — Arp step: XX semitones added to the current note (while XX < $70)
7X ($70–$7F)  — Jump to relative arp index X within the current arp program
```

NOTE: Driver 11's arpeggio ONLY applies when the wave table byte 1 (semitone offset) is $00.
Non-zero wave offsets bypass the arpeggio lookup entirely.

---

## .SF2 File Format (Source Format — PRG-based)

The `.sf2` source file is a standard C64 PRG file (2-byte load address header + data).
It contains:
1. The 6502 driver binary (SID player code) at its load address
2. Auxiliary data block appended after the driver binary, identified by a fixed pointer
   at address `$0FFB` → `ExpectedFileIDNumber = 0x1337`
3. The auxiliary data uses a block-based format with block IDs:
   - `ID_Descriptor` (1): driver metadata (type, version, name)
   - `ID_DriverCommon` (2): runtime addresses (init, stop, update routines; state variables)
   - `ID_DriverTables` (3): table definitions (instruments, commands, wave, pulse, filter, HR, arp, tempo)
   - `ID_DriverInstrumentDescriptor` (4): instrument cell layout descriptions
   - `ID_MusicData` (5): track count, orderlist/sequence pointer tables, sizes, base addresses
   - `ID_TableColorRules` (6): visual highlight rules (editor-only)
   - `ID_TableInsertDeleteRules` (7): row insertion/deletion constraints (editor-only)
   - `ID_TableActionRules` (8): cell interaction rules for e.g. Ctrl+Enter jumps (editor-only)
   - `ID_DriverInstrumentDataDescriptor` (9): pointer/jump-marker mappings for instrument pointers

**Packed output format** (when you save as `.prg` or `.sid` via F6 → Pack):
- Driver code at the chosen destination address
- All table data (instruments, commands, wave, pulse, filter, HR, arp, tempo) immediately after
- Order list pointer tables (low bytes, then high bytes)
- Sequence pointer tables (low bytes, then high bytes)
- Order lists (one per voice per song)
- Sequences (individual packed sequence data)
- Zero page usage is relocated: all ZP references in the driver are patched to the chosen ZP base

## Leads to follow

- The F12 overlay PNG (`tmp/sidfactory_ii_research/sf2_docs/linux_driver11_05.png`) is an image
  of the complete help overlay — read it visually to cross-check table column counts and color codes.
- Driver source assembly would reveal exact SID register write order per frame — not yet obtained.
  The driver .prg files at `docs/src/` (copied from the release) can be disassembled with xa65/dasm.
- The `datasource_sequence.cpp` source (`driver_info.cpp`) confirms the packed sequence byte encoding
  summarized above — see source in the GitHub repo for full detail.
- For the exact SID register semantics of each waveform, filter mode, etc., see `manual_effect_semantics.md`.
