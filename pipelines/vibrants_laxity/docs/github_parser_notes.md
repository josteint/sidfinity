---
source_url: https://github.com/Chordian/sidfactory2 (C++ source + docs)
fetched_via: git clone
fetch_date: 2026-06-15
author: Thomas Egeskov Petersen (Laxity) + JCH + SID Factory II team
content_date: 2026-06-15
reliability: primary
---

# Parser / Decompiler Notes — Vibrants/Laxity/JCH Player Family

This file synthesises byte-level findings from SID Factory II C++ source code
and the JCH editor assembly source. Use for building the USF extractor.

---

## Player family tree

```
Laxity Editor (1987-88)       — original; Turbo Assembler source; 6 surviving tunes
  └── JCH NewPlayer (1988+)   — NP_00 through NP_20 (v20.G0 is the last major)
        └── SID Factory II (2019+)  — driver 11 is the main descendant
              — Thomas Egeskov Petersen (Laxity) is lead developer
```

HVSC identifies SIDID player signature as "Vibrants" for tunes using the Laxity/JCH player.
The SF2 family is the direct living descendant. The SID files in HVSC for Laxity and JCH
use the NP player binary (loaded at $0F00) with music data starting after it.

---

## CRITICAL: SF2 driver vs NP20 binary in HVSC SIDs

The `.sf2` files (SID Factory II native) use the EMBEDDED SF2 driver (`.prg` from the
drivers/ folder) and share no binary format with the HVSC `.sid` files.

The HVSC `.sid` files for Laxity/JCH tunes use the **NP binary directly** — a C64 PRG
loaded at $0F00 containing the player code + tables + music data as one blob. To parse
HVSC SIDs you need the NP player layout, NOT the SF2 file format.

The **SF2 NP20 converter** (`converter_jch.cpp`) is the only publicly available parser
for the NP20 binary format. It detects NP20 by: load address = $0F00 AND bytes at
$0FEE = '2', '0', '.', 'G'. It then reads pointer table at fixed offsets (see github_jch_source.md).

---

## How to identify a Laxity/JCH/Vibrants SID in HVSC

Heuristic checks (in order):
1. PSID/RSID load address == $0F00 (almost certain for NP player)
2. Read bytes at $0FEE: if "20.G" → NP20.G0
3. Read bytes at $0FEE: for other versions the pattern may differ (v17.G0 = "17.G" etc.)
4. SIDID database covers these; "Vibrants" fingerprint should fire

For earlier Laxity tunes (LAXITY.ZIP, pre-NP): these use a different, simpler player.
The .DAT files are raw data; .SID files are 153-180 byte wrappers that embed a compact
player. The player structure for these is NOT documented in the SF2 source.

---

## NP20 memory layout at $0F00

```
$0F00+   Player binary (6502 code; length variable by version)
         At end of code, before music data:
$0FA6    Word → pointer to init table
$0FBA    Word → pointer to fine-tune table  (3 bytes: V1/V2/V3 fine-tune offsets)
$0FBC    Word → pointer to wave table
$0FC0    Word → pointer to filter table
$0FC2    Word → pointer to pulse table
$0FC4    Word → pointer to instrument table
$0FC6    Word → pointer to orderlist V1
$0FC8    Word → pointer to orderlist V2
$0FCA    Word → pointer to orderlist V3
$0FCC    Word → pointer to sequence vector low bytes  (sequence N low byte = this+N)
$0FCE    Word → pointer to sequence vector high bytes (sequence N high byte = this+N)
$0FD0    Word → pointer to command table
$0FEE    4 bytes: version string ("20.G" for v20.G0)
$0FF4    Byte: quantize value / speed (editor stores here)
$0FFF    Byte: various flags

Player entry points:
$1000    Init (JSR $1000; A=subtune number)
$1003    Update/play (JSR $1003; called once per frame by interrupt)
```

---

## SF2 driver 11 (the modern equivalent) — key playback semantics

These are confirmed from documentation and C++ source code:

### Per-frame playback loop (per voice)

1. Decrement tick counter. If not zero, just update running programs (vibrato/slide/pulse/filter).
2. When tick counter reaches 0: advance orderlist if sequence exhausted.
3. Fetch next event from sequence (command + instrument + duration + note).
4. If new note (not rest, not gate-on): apply hard restart if enabled.
5. Write waveform from wave table (and frequency from note + transpose + fine-tune).
6. Trigger gate: write to $D404/$D40B/$D412.
7. Run wave program if active (may modify waveform on subsequent ticks).

### Orderlist advancement

When the sequence index hits $7F (end-of-sequence): increment orderlist pointer.
If orderlist byte is $FF → loop to saved loop position. If $FE → stop.
If byte >= $80 → new transposition; fetch next byte as sequence index.
If byte < $80 → sequence index; keep current transposition.

### Transposition

Each orderlist entry carries a transposition value. Notes in the sequence are
semitone values (relative 1-111 or absolute $80-$DF). Transpose shifts the
relative semitones but NOT absolute ones.

### Hard restart

When `flag & $80`: on new note-trigger, the player first writes waveform `$09`
(triangle+gate, or oscillator sync?) for 1 frame to force oscillator reset,
then writes the real waveform. The HR table index (flag & $0F) selects which
HR sub-table row to use for timing.

### Oscillator reset

When `flag & $10`: waveform $09 is used in the FIRST frame of the note (similar
to hard restart but controlled by the oscillator-reset flag, not the HR table).

### Filter enable

When `flag & $40`: the filter program (indexed by byte 3) is started on note-on.
When `flag & $20` [11.03+]: additionally enables the filter for this voice's
SID channel (combined with the channel bitmask in the filter program entry).

---

## Sequence parsing (SF2 driver 11 / NP20 converted)

Full byte-level format from `datasource_sequence.cpp`:

```
Token priority (highest byte value wins):
  $C0-$FF → command token (sets which command runs; index = value & $3F)
  $A0-$BF → instrument token (sets instrument; index = value & $1F)
  $80-$8F → duration token (extra ticks = value & $0F; bit4=0 → normal)
  $90-$9F → duration + TIE flag (extra ticks = value & $0F; bit4=1 → tie note)
  $00-$7F → note token (REQUIRED last token of event):
             $00      = rest
             $01-$6F  = semitone (1-111)
             $7E      = gate-on / hold (tie continuation)
             $7F      = END OF SEQUENCE
```

Each event in the packed stream: optional $C0+ command, optional $A0+ instrument,
optional $80+ duration, THEN mandatory $00-$7F note. The note terminates the event.

Duration encodes ticks-1: byte $8N → note plays N+1 ticks. Without a duration token,
previous duration is reused. Starting duration is 0 (1 tick).

The tie note flag ($90-$9F): the note byte that follows should use $7E (gate-on),
meaning the instrument is replaced by the "tie" marker ($90 overrides $A0+ instrument).

---

## Orderlist parsing (SF2 driver 11)

From `datasource_orderlist.cpp`:

```
Bytes < $80:  sequence index (0-127). Current transposition still applies.
Bytes $80-$FD: new transposition value; (byte & $7F) - $20 = semitone shift.
               i.e. $A0 → shift 0, $81 → shift -31, $9F → shift -1, $A1 → shift +1
Byte $FF:     loop marker. Next byte = BYTE OFFSET INTO PACKED DATA for loop target.
Byte $FE:     stop (play once, don't loop).
```

Compression: the transposition byte is OMITTED when it equals the previous value.
Only emitted on first occurrence or when it changes (or at loop boundary).

---

## SF2 driver header — binary format in .prg file

The `.prg` file starts with a 2-byte load address then immediately:
```
Offset 0 from load:  Word $1337  (magic ID)
Then a sequence of TLV blocks:
  1 byte:  block ID (see driver_info.h HeaderBlockID enum; $FF = end)
  1 byte:  block size (bytes that follow)
  N bytes: block payload
```

Block IDs that are REQUIRED for a valid driver:
- ID=1 (Descriptor): name, version, code location/size
- ID=2 (DriverCommon): init/stop/update addresses + per-voice state machine addresses
- ID=3 (DriverTables): one entry per data table (instruments/commands/wave/pulse/filter/arp)
- ID=4 (InstrumentDescriptor): human-readable column names
- ID=5 (MusicData): track count, orderlist and sequence pointer tables

---

## libsidplayfp / VICE handling

No specific Laxity/JCH/Vibrants player handling code was found in GitHub searches.
These engines play back fine as generic PSID (libsidplayfp just runs the 6502 as-is).
The SIDID fingerprint database identifies them as "Vibrants" for HVSC cataloging.

---

## What is NOT documented (gaps for future research)

1. **Early Laxity player format** (pre-NP, 1987-88): the 6 .DAT files in LAXITY.ZIP
   are in Laxity's original format. The .SID wrapper files (153-180 bytes) embed a
   compact player but its format is not documented anywhere in the SF2 repo.
   The editor source (ED37_SRC.TXT) documents accessing these via the same $0F00
   pointer table, suggesting the pointer layout may be shared.

2. **NP player versions before v20**: NP_00 through NP_19 may have different pointer
   layouts or data formats. The SF2 NP20 converter only handles v20.G0 specifically.
   Earlier versions may need separate fingerprinting.

3. **Multi-speed / CIA-timed variants**: NP v20.Q0 ("quattro") is a multi-speed player.
   Speed is encoded at init_data_ptr+6; if < 2, filter_table[0]/[1] encode alternating
   CIA timer values. Full CIA timing semantics not yet researched.

4. **SF2 driver assembly source**: the .prg driver files are binary-only in the SF2 repo.
   The 6502 source for the SF2 drivers (driver 11.xx etc.) is not publicly released.
   The drivers must be disassembled from the .prg files to understand the exact 6502
   write sequence.

5. **Instrument grow / addressing**: SF2 mentions "instrument growth (ids 0-31)". Whether
   the NP player supports >32 instruments in some versions is unclear.
