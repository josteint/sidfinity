---
source_url: https://github.com/Chordian/sidfactory2 (dist/documentation/notes_driver*.txt)
fetched_via: curl
fetch_date: 2026-06-15
author: Jens-Christian Huus (JCH / Chordian)
content_date: 2020-2022
reliability: primary
---

# SID Factory II — Drivers 11–16 Format Documentation

Downloaded from the SID Factory II GitHub repository (Chordian).
Source files extracted to: /home/jtr/sidfinity/tmp/vibrants_laxity_research/sidfactory2/dist/documentation/

These drivers represent the current (2020+) state of the JCH/Laxity lineage. The HVSC #84 database
shows 64 SIDs classified as `SidFactory_II/Laxity`. The default driver is Driver 11.

---

## Driver 11 (Standard)

Source: `notes_driver11.txt`

The main, feature-rich driver. Most SF2 tunes use this.

### Instrument (6 bytes)

| Byte | Purpose |
|------|---------|
| 0 | Attack/Decay |
| 1 | Sustain/Release |
| 2 | Switches: `$80`=Hard restart; `$40`=Filter on; `$10`=Osc reset; `$0x`=HR index |
| 3 | Filter table pointer |
| 4 | Pulse table pointer |
| 5 | Wave table pointer |

### Wave table (2 bytes: waveform, note)

- `waveform xx`, `note 00-7F` = relative semitone offset
- `waveform xx`, `note 80-FF` = absolute semitone value (`- $80`)
- `7F xx` = jump to index `xx`

### Pulse table (3 bytes: pulse_hi, pulse_lo, duration)

- `8x xx yy` = Set pulsewidth to `xxx`, duration `yy`
- `0x xx yy` = Add `xxx` to pulsewidth every frame, duration `yy`
- `7F ?? xx` = Jump to index `xx`

### Filter table (3 bytes: type, cutoff, resonance+voices)

- `xy zz wq` where x>8: Set filter type `x`, cutoff `yzz`, resonance `w`, voice select `q`
- `0x xx yy` = Add cutoff `xxx`, duration `yy`
- `7F -- xx` = Jump to index `xx`

### Arpeggio table (1 byte)

- `00-6F` = relative semitone offset
- `7x` = jump to start index + `x`

### Commands (3 bytes each)

| Opcode | Params | Description |
|--------|--------|-------------|
| `00` | `xx yy` | Slide @ speed `xxyy` |
| `01` | `xx yy` | Vibrato @ frequency `xx`, amplitude `yy` |
| `02` | `xx yy` | Portamento @ speed `xxyy` (`$8000` = disable) |
| `03` | `xx yy` | Arpeggio from Arp index `yy` @ speed `xx` |
| `08` | `ad sr` | ADSR `adsr` until next **note** plays |
| `09` | `ad sr` | ADSR `adsr` until next **instrument** plays |
| `0A` | `-- yy` | Start Filter @ index `yy` |
| `0B` | `-- yy` | Start Wave @ index `yy` |

---

## Driver 12 (Standard, with pulse program changes)

Source: `notes_driver12.txt`

"Driver 12 is a standard music driver with calculated vibrato. It extends on driver 11 by
adding support for a temporal pulse program restart."

### Key differences from Driver 11

- Instrument byte 2: adds `$20`=Pulse reset — when the driver is initiated on a new note,
  the pulse program is restarted
- Added command `0C xx yy` — Pulse program: start Pulse @ index `xx` (3rd byte `yy` unused)

Everything else (wave, filter, arpeggio, other commands) identical to Driver 11.

---

## Driver 13 (Compact, fewer features)

Source: `notes_driver13.txt`

"Driver 13 is a compact music driver with calculated vibrato. It's designed to minimize
memory footprint and focuses on the most commonly used features."

### Instrument (6 bytes — same as Driver 11)

### Key differences from Driver 11

- NO arpeggio table (removed entirely)
- Filter table is 2 bytes (not 3): `aa bb` where `aa`=add to filter cutoff, `bb`=execution time
  - Jump: `7F xx` = jump to index `xx`
- Pulse table is 2 bytes (not 3): same as filter (add to pulse, execution time, jump)
- Commands available: `00`=slide, `01`=vibrato, `02`=portamento (same as D11)

---

## Driver 14 (Compact + gate commands)

Source: `notes_driver14.txt`

"Driver 14 is a compact music driver with gate commands. It's designed to minimize
memory footprint with particular focus on minimizing data size."

### Instrument (6 bytes — same as Driver 11)

### Key differences from Driver 11

- Pulse/filter tables are 2-byte entries (same as Driver 13)
- Arpeggio table: `7x` = jump to index `x` from start of arpeggio (same as D11)
- Added command `0C`: Gate off (--- equivalent as a command)
- Added command `0D`: Gate on (+++ equivalent as a command)
- NO portamento command (command `02` absent)

---

## Driver 15 (Tiny, mark I)

Source: `notes_driver15.txt`

"Driver 15 is a tiny driver... really a variation of driver 12.00 where all of the variables
have been moved to zero page addressing space."

### Instrument (5 bytes — REDUCED)

| Byte | Purpose |
|------|---------|
| 0 | Attack/Decay |
| 1 | Sustain/Release |
| 2 | Pulse width XY: X=middle 4 bits, Y=top 4 bits (12-bit pulse width) |
| 3 | Linear pulse sweep: X=add to mid 4 bits, Y=add to top 4 bits |
| 4 | Wave table index |

**Hard restart is always on** (not configurable per instrument).

### Wave table (2 bytes: waveform, note) — same as Driver 11

### Commands (v15.02+)

| Opcode | Params | Description |
|--------|--------|-------------|
| `0X XX` | 12-bit | Slide up @ speed XXX |
| `1X XX` | 12-bit | Slide down @ speed XXX |
| `2X -Y` | X=freq, Y=amp | Vibrato |
| `3X YY` | YY=index | Wave program pointer |

### Changes in v15.02

- Hard restart settings changed: now sets ADSR to `$0F00` before `$00` (more aggressive)
- Programs continue running during next note phase (v15.00 suspended them, causing artifacts)
- Added command `3x yy` for wave program pointer
- Added stop marker (orderlist) support

---

## Driver 16 (Tiny, mark II)

Source: `notes_driver16.txt`

"Driver 16 is a tiny driver... variation of driver 15.00 where all variables are in zero page.
Hard restart is always on and there are NO commands available."

### Instrument (5 bytes — identical to Driver 15)

| Byte | Purpose |
|------|---------|
| 0 | Attack/Decay |
| 1 | Sustain/Release |
| 2 | Pulse width XY: X=middle 4 bits, Y=top 4 bits |
| 3 | Linear pulse sweep |
| 4 | Wave table index |

### Commands: NONE

### Wave table: same as all other drivers (2 bytes: waveform + note)

---

## SF2 Track / Orderlist System

Source: SF2 User Manual (pages 1-12 read), `notes_driver11.txt`

Track format is identical to the JCH C64 editor (the same inventor):

- Track table entry: 2 bytes `XXYY`
  - `XX` = transpose byte (`$80` = no transpose)
  - `YY` = sequence number
- Special markers:
  - `FF` = loop (go back to start)
  - `00` = end / stop

Sequence format (in-editor, 3 rows per tick):
- Row 1: instrument set (or `*` for tie / keep instrument)
- Row 2: command number (or `..` for no command)
- Row 3: note (`C-3`..`G-7`), `+++` (gate on), `---` (gate off), `...` (rest)

---

## Driver Lineage Summary

| Driver | Type | Instr bytes | Arpeggio | Vibrato | Portamento | Pulse table |
|--------|------|-------------|----------|---------|------------|-------------|
| 11 | Standard | 6 | Yes (1-byte) | Calculated | Yes | 3-byte |
| 12 | Standard+ | 6 | Yes | Calculated | Yes | 3-byte (+ reset cmd) |
| 13 | Compact | 6 | No | Calculated | Yes | 2-byte |
| 14 | Compact | 6 | Yes | Calculated | No | 2-byte |
| 15 | Tiny | 5 | No | Calculated | No | Linear only (in inst) |
| 16 | Tiny | 5 | No | Calculated | No | Linear only (in inst) |

---

## HVSC #84 Usage

From DB query (read-only):
- `SidFactory_II/Laxity`: 64 SIDs
- `SidFactory/Laxity` (SF 0.5): 27 SIDs
- Most SF2 tunes use Driver 11 (the default); SF2 exports with whichever driver the author chose
