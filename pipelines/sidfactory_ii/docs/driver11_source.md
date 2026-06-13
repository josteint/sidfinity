---
source_url: https://github.com/Chordian/sidfactory2/tree/master/SIDFactoryII/drivers
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity)
content_date: 2020–2026
reliability: primary (C++ parser) / secondary (behavioral reconstruction)
---

# SID Factory II — Driver 11 Source Reference

The 6502 assembly source for Driver 11 is **not in the public GitHub repository**.
Only compiled `.prg` binaries exist under `SIDFactoryII/drivers/`:

```
sf2driver11_00.prg   (v11.00 — original)
sf2driver11_01.prg   (v11.01 — adds fret slide)
sf2driver11_02.prg   (v11.02 — adds pulse/tempo/main-vol commands)
sf2driver11_03.prg   (v11.03 — adds filter-enable flag)
sf2driver11_04.prg   (v11.04 — adds note delay)
sf2driver11_04_01.prg
sf2driver11_05.prg   (v11.05 — removes fret slide, HR=8 rows, pulse-reset skip flag)
```

Also present (non-driver-11 variants):
```
sf2driver12_00.prg / _00_01.prg   (Driver 12 — simple)
sf2driver13_00.prg / _00_01.prg   (Driver 13 — Hubbard-style)
sf2driver14_00.prg / _00_01.prg   (Driver 14 — short gate-off)
sf2driver15_00.prg / _01.prg / _02.prg   (Driver 15 — tiny mark I)
sf2driver16_00.prg / _01.prg / _01_01.prg  (Driver 16 — tiny mark II)
sf2driver_np20_00.prg   (Driver NP20)
```

---

## What Is Reconstructible from the Editor Source

The C++ editor code gives a complete behavioral description of what the driver produces
and how the editor interfaces with it. The following sections reconstruct the 6502
semantics from `driver_info.cpp`, `driver_utils.cpp`, `driver_architecture_sidfactory2.cpp`,
`datasource_sequence.cpp`, and `datasource_orderlist.cpp`.

---

## Driver 11 — Version History

From `dist/documentation/notes_driver11.txt` (also at `docs/src/notes_driver11.txt`):

```
11.00  Original default driver
11.01  Added: fret slide command (T4)
11.02  Added: pulse table index command (Tc), tempo table index command (Td),
              main volume command (Te)
11.03  Added: enable-filter-on-channel flag (instrument byte 2 bit 5 = 0x20)
11.04  Added: note delay (high nibble of note byte = 0-F tick delay)
11.05  Removed: fret slide (T4); HR table shrank from 16 to 8 rows;
              Added: skip-pulse-reset flag (instrument byte 2 bit 3 = 0x08)
```

---

## Instrument Format (6 bytes, ColumnMajor table)

From `notes_driver11.txt`:

```
Byte 0 : AD     — hi nibble = Attack (0–F), lo nibble = Decay (0–F)
Byte 1 : SR     — hi nibble = Sustain (0–F), lo nibble = Release (0–F)
Byte 2 : Flags
           0x80  Enable hard restart
           0x40  Start filter program (byte 3 = filter table index)
           0x20  [11.03] Enable filter on this channel (+ bitmask in filter program)
           0x10  Oscillator reset (waveform $09 for first frame of note)
           0x08  [11.05] Skip pulse-program reset on note-on unless instrument explicitly set
           0x0X  Hard restart table index (0–7 in 11.05, 0–15 in 11.00–11.04)
Byte 3 : Filter table index  (used only if bit 6 of byte 2 is set)
Byte 4 : Pulse table index
Byte 5 : Wave table index
```

---

## Command Table (3 bytes per row, ColumnMajor)

Column layout: `T` (type/hi), `XX` (param 1), `YY` (param 2).

```
T0 XX YY  Slide up/down       XXYY = 16-bit slide speed (signed: hi byte T0 means either up or down)
T1 XX YY  Vibrato             XX = frequency, YY = amplitude (smaller = stronger)
T2 XX YY  Portamento          XXYY = 16-bit speed; "02 80 00" kills a runaway portamento
T3 XX YY  Arpeggio            XX = arpeggio speed, YY = arpeggio table index
T4 XX YY  [11.01–11.04 only]
           Fret slide          XX = 00-7F = speed up; 80-FF = speed down
                               YY = semitones to slide
T8 XX YY  Set local ADSR      XX=AD YY=SR; temporary until next note trigger
T9 XX YY  Set instrument ADSR XX=AD YY=SR; persists until instrument changes
Ta -- XX  Filter program      XX = filter table index (-- = ignored byte)
Tb -- XX  Wave program        XX = wave table index
Tc -- XX  [11.02+] Pulse program   XX = pulse table index
Td -- XX  [11.02+] Tempo program   XX = tempo table index
Te -- -X  [11.02+] Main volume     X = 0-F ($D418 hi nibble volume)
Tf -- XX  Demo counter tick   XX = amount to add to demo timing counter
|
T  (high nibble of note byte) [11.04+] Note delay: T = 0-F ticks before note fires
```

---

## Wave Table (2 bytes per row, ColumnMajor)

```
Byte 0 (col 0): Waveform register value ($D404/$D40B/$D412 hi bits)
                  $00  = keep current waveform
                  $11  = triangle
                  $21  = sawtooth
                  $41  = pulse
                  $81  = noise
                  $09  = oscillator reset (test bit + triangle)
                  combos: $61 = pulse+saw, etc.
Byte 1 (col 1): Semitone
                  $00–$7F = relative semitone offset to add to note (signed; $00 = no change)
                  $80–$DF = absolute semitone value (ignores note in sequence; used for drums)

Special row:
  Byte 0 = $7F  → Jump; Byte 1 = table index to jump to
                   (jump to own index = freeze/hold current state)
```

---

## Pulse Table (3 bytes per row, ColumnMajor)

```
Set pulse:  $8X XX YY  → pulse width = 12-bit value ($X << 8 | second byte masked);
                           YY = frame count for this row
Add pulse:  $0X XX YY  → add 12-bit signed delta to pulse width; YY = frame count
Jump:       $7F -- XX  → jump to table index XX (self-jump = end program)
```

The first byte's high nibble selects set ($8) vs add ($0); the remaining 12 bits are
the pulse/delta value across bytes 0 and 1; byte 2 is the duration.

---

## Filter Table (4 bytes per row, ColumnMajor)

```
Set filter: first byte hi-nibble > $8 (i.e. $9–$F)
              Byte 0 hi-nibble: passband select ($9–$F = hi/lo/band-pass combinations)
              Bytes 0+1 low 12 bits: cutoff frequency (0–$FFF)
              Byte 2 hi-nibble: resonance (0–$F)
              Byte 2 lo-nibble: } channel bitmask (bit 0=voice1, bit 1=voice2, bit 2=voice3)
              Byte 3: channel bitmask (combined with byte 2 lo)

Add to cutoff: first byte hi-nibble = $0
              Bytes 0+1: 12-bit signed delta to cutoff
              Byte 2: frame count

Jump:       $7F -- XX  → jump to table index XX
```

Note: `[11.03]` instrument flag bit 5 enables filter routing on the instrument's channel,
combined with the bitmask in the filter program row.

---

## Arpeggio Table (1 byte per row)

```
$00–$6F  Add this semitone value to current note
$70–$7F  Relative jump: X = lower nibble = relative index offset
           (e.g. $71 at position 3 jumps to position 4; used for multi-shape arpeggios)
```

Command T3 specifies: `XX` = arpeggio speed (how many frames per table step),
`YY` = starting table index.

Arpeggio jump example from notes:
```
00: 0C         ; add 12 semitones
01: 07         ; add 7 semitones   *1
02: 04         ; add 4 semitones   *2
03: 00         ; add 0 semitones
04: 71         ; relative jump +1: if called with YY=00 → back to index 1 (*1)
               ;                    if called with YY=01 → back to index 2 (*2)
```

---

## HR (Hard Restart) Table

Provides alternative ADSR values for the last 2 ticks of a note, to prevent the
"ADSR bug" on old SID chips. Size: 2 bytes × 8 rows (11.05) or 2 bytes × 16 rows (11.00–11.04).
Index selected by instrument byte 2 bits 0–2 (bits 0–3 before 11.05).

Each row is 2 bytes: `AD` and `SR` applied during the hard restart phase.

---

## Tempo Table (Driver 11.02+, Generic table)

Countdown values per row controlling note duration. `$7F` = loop back to index 0 (or
configured loop point). Enables swing and variable-tempo patterns.

---

## Sequence Byte Encoding

From `datasource_sequence.cpp` (the `Pack()`/`Unpack()` methods):

```
$00        Gate off (note off, clears gate bit)
$01–$6F    Note value (semitone in editor's key map)
$7F        End-of-sequence marker (required; terminates the sequence)
$80–$8F    Duration: (byte & $0F) + 1 ticks, no tie
$90–$9F    Duration: (byte & $0F) + 1 ticks, with tie-note (no retrigger)
$A0–$BF    Instrument select: (byte & $3F) = instrument index
$C0–$FF    Command select: (byte & $3F) = command table index
```

Encoding is delta-compressed: instrument and command bytes are emitted only on change.
Repeated notes at same inst/command are folded into duration counts.

**Empty sequence:** `[$80, $00, $7F]`  
(= 1-tick duration, note-off, end-of-sequence)

**Example sequence ("A2 for 4 ticks with instrument 3, command 5"):**
```
A3           ; set instrument 3
C5           ; set command 5
83           ; duration = 4 ticks (0x83 & 0x0F = 3 → 3+1=4)
22           ; note A2 (key-map dependent)
7F           ; end of sequence
```

---

## Order List Byte Encoding

From `datasource_orderlist.cpp` (the `Pack()`/`Unpack()` methods):

```
$00–$7F    Sequence index (plays this sequence next)
$80–$FF    Transpose byte: semitone shift = (byte - 0xA0), range -32..+31
            $A0 = no transpose (offset 0)
$FE        End-of-list (no loop); list stops here
$FF        Loop marker; next byte = packed-stream byte offset of loop start
```

Transpose bytes persist until changed (stateful; carried across entries).

**Empty order list:** `[$A0, $00, $FF, $00]`  
(= transpose 0, sequence 0, loop back to byte 0)

---

## Driver Entry Points (Runtime)

Three JSR targets stored in `ID_DriverCommon`:

```
m_InitAddress    Called once: sets up driver state, loads initial instruments, resets SID.
m_StopAddress    Called to silence all voices immediately.
m_UpdateAddress  Called every frame (50 Hz PAL). Advances all 3 voices' state machines.
```

The editor calls `PostInitSetPlaybackIndices()` after `m_InitAddress` to seek to a
mid-song position, writing directly into the per-voice state arrays (order list index,
sequence index, tick counters, transpose, etc.) at the addresses from `ID_DriverCommon`.

---

## IRQ Wrapper

`DriverUtils::InsertIRQ()` generates a 58-byte 6502 IRQ wrapper appended at the end of
the exported SID file. It:
1. Calls `m_InitAddress` once on startup (`LDA #lo; JSR init_lo_address`).
2. Sets up a raster IRQ at `$D012=$32` (line 50).
3. From the IRQ: calls `m_UpdateAddress` every frame.
4. Uses C64 IRQ vector `$0314/$0315` (`$1403`/`$1503` in the machine code).

The IRQ entry point is written at `irq_vector + $0020` (32 bytes after the start of
the injected block).

---

## Known Bugs in Driver 11

From `notes_driver11.txt`: **None**.

---

## Open RE Tasks

1. **Disassemble sf2driver11_05.prg** to recover the full 6502 source.
   Command: `python3 tools/seed_disassembly.py <load_addr> sf2driver11_05.prg > driver11_disasm.s`
   The descriptor block chain starts at `load_address + 2` and can be parsed to find
   `driver_code_top` and `driver_code_size`, then disassemble that range.

2. **Map zero-page usage** in driver 11 — run `tools/packing_utils.cpp`'s
   `GetZeroPageRangeFromDriver()` equivalent on the binary to find which ZP bytes
   the driver touches. This determines the relocation target ZP range.

3. **Identify the per-voice SID channel offset table** at `m_SIDChannelOffsetAddress` —
   this is how the driver switches between voice 1 ($D400/$D407/$D40E), voice 2
   ($D407/$D40E via the offset), and voice 3. Each voice block is 7 bytes.

4. **Instrument count per driver build** — `notes_driver11.txt` doesn't state it but
   instruments are typically 32 rows (5-bit index from $A0–$BF sequence byte range).
   Verify by checking `ID_DriverTables` block in the binary.
