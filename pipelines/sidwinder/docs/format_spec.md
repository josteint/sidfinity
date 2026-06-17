---
source_url: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip
fetched_via: direct
fetch_date: 2026-06-17
author: Balázs Takács (Taki / Natural Beat); Levente Hérsfalvi (TLC / Coroners)
content_date: 1994-2000
reliability: primary
---

# SIDwinder V01.22/V01.23 — Format Specification

Derived from the V01.23 source package (SIDW0122.txt, SUMMARY, HISTORY, PLAYER.ASM).
Primary author: Balázs Takács (Taki / Natural Beat). V01.23 port: TLC / Coroners.

---

## 1. Overview

SIDwinder is a C64 native SID music editor and player. Original code written in
C64 Turbo Assembler circa 1994; first public release (V01.22) in 1999. V01.23
released March 2000 as GPL source by TLC, who ported to Plus/4 simultaneously.

Key capacity limits:
- Up to **32 subtunes** in one music file
- Up to **96 sectors** (instruction sequences), 256 instructions per sector
- Up to **64 instruments** ($00..$3F)
- Up to **16× music speed** (V01.23; V01.22 supported up to 10×)
- **3 SID voices**; filter runs on voice 1 only (filter is global, controlled from voice 1)
- **PAL only** (frequency tables are PAL-clock based)

---

## 2. Player memory layout (after packing, default load address $1000)

| Address | Contents |
|---|---|
| $1000 | `JMP m_init` — init entry point |
| $1003 | `JMP irqplr` — first play() call per frame |
| $1006 | `JMP mltspd` — subsequent play() calls (multi-speed) |
| $1007+ | ID field: " - SIDwinder V01.23  - Music by (your handle / group)-" |
| $1020..$103F | 32-byte user identity field (editable) |
| $1594 | Number of subtunes (byte) |
| $1673 | Volume register (for external volume control, V01.23) |
| $165D | Volume control register (V01.23) |
| $168E | Volume register (V01.22; write target $00 here to suppress internal slide) |
| $1678 | Volume slide control (V01.22; write $00 to freeze internal slide during fade) |
| $1692 | Speed table — one byte per subtune (V01.22 layout) |

Zero page: one pointer used ($FB/$FC by default, selectable at pack time).

Init: load subtune number ($00..$1F) into accumulator, JSR $1000.

---

## 3. Track format

Each of 3 voices has its own track table. 8 track tables share the 32 subtunes
(4 subtunes per track table, separated by start pointers).

**Track instructions** (1 byte each, executed in strict order):

| Opcode range | Instruction | Description |
|---|---|---|
| $00..$3F | Tr+XX | Transpose up by $00..$3F semitones |
| $40..$7F | Tr-XX | Transpose down (2's complement encoding) |
| $80..$9F | ...XX | Play sector $00..$1F |
| $A0..$BF | ...XX | Play sector $20..$3F |
| $C0..$DF | ...XX | Play sector $40..$5F |
| $E0..$E7 | VolXX | Set volume $00..$07 (masked to low nybble, $00..$0F) |
| $E8..$EF | DecXX | Volume slide down at speed $01..$08 |
| $F0..$F7 | HltVS | Halt volume slide (opcode $F0 specifically, others may differ) |
| $F8..$FF | IncXX | Volume slide up at speed $01..$08 |
| $FF + byte | JmpXX | 2-byte: jump to track position XX |

Ordering rule: one JmpXX, then one vol/slide command, then one transpose, then sector-play.
Missing items are allowed; out-of-order is undefined behaviour (no editor guard).

---

## 4. Sector format

Each sector holds up to 256 bytes of instructions. Instructions must appear in
this strict order (each optional except a terminal note/rest/hold):

```
[Snd.XX]   — $C0..$FF: instrument select ($00..$3F = instr & $3F)
[Dur.XX]   — $80..$BF: note duration 1..$40 frames (= val & $3F, 0 = $40)
[Gld.XX]   — $60..$6F: glide; $70..$7F: slide (index into glide table)
<note>     — one of:
  $00..$4F   note value (semitone index, transposed)
  $5F        --- (delay + release gate)
  $6F        +++ (hold, freeze gate-off counter)
  $7F        Finish (end of sector)
```

Note range: $00 = C-1 lowest, $4F = upper range (96 notes in freq table, but
practical range limited by freq table size).

Glide ($60..$6F): two-note glide — plays first note, sweeps to second note.
Slide ($70..$7F): one-note slide — keeps current note, slides to new note.
Both use index into a separate 16-entry glide table for speed.

---

## 5. Instrument structure (7 bytes)

| Byte | Field | Description |
|---|---|---|
| 0 | AD | Attack (hi nybble) / Decay (lo nybble) |
| 1 | SR | Sustain (hi nybble) / Release (lo nybble) |
| 2 | Gate-off counter | Frames until gate bit cleared (0 = no auto gate-off) |
| 3 | Arpeggio pointer | Index into arpeggio table ($00 = start, any = that row) |
| 4 | Filter pointer | $00 = off, $FF = don't touch (keep running) |
| 5 | Pulse width pointer | $00 = off, $FF = don't touch |
| 6 | Vibrato/slide pointer | $00 = off, $FF = don't touch |

Up to 64 instruments ($00..$3F). Instrument with ADSR = 0000 is treated as
unused by the packer (discarded).

Hard restart: automatic at every sector boundary and on every new note.
Player issues hard restart with test-bit mechanism; first frame is skipped.
Gate-off: player counts down gate-off counter each frame, then does AND #$FE
on waveform register. Minimum safe note duration: 4 frames.

---

## 6. Effect tables

All effect tables share the same structural pattern: (repeat-count, data...)
with $FF = jump. Tables are indexed by byte position.

### 6.1 Arpeggio / Waveform table (2 bytes per row: WF, AR)

| WF | AR | Meaning |
|---|---|---|
| $00..$8F | signed offset | Set waveform=WF, play note+AR semitones |
| $90..$FE | signed offset | Repeat last waveform (WF-$8F) more times with new AR |
| $FF | jump target | Jump to row AR |

Rows $00..$02 reserved in V01.22 for channel-off mute loop:
```
00: WF=$08 AR=$00   (silence waveform)
01: WF=$FE AR=$00   (long repeat)
02: WF=$FF AR=$01   (jump to row $01)
```
(V01.23 moved channel-off to gate-bit masking — rows $00..$02 are free.)

### 6.2 Filter table (3 bytes per row: RP, FH, RL)

| RP | Meaning |
|---|---|
| $00..$FD | Repeat count for additive sweep |
| $FE | Set filter type (FH = type bits 6-4; low bits must be 0) |
| $FF | Jump to FH |

FH = addition to cutoff frequency high byte (or filter type or jump target).
RL = addition to resonance (bits 7-4) and cutoff frequency low byte (bits 2-0).

On instrument init: filter cutoff, resonance, and type all reset to 0.
Player writes: `$D418 = volume OR filtertype`.
Filter only runs for voice 1 (X=0); voices 2/3 skip filter update.

### 6.3 Pulse width table (3 bytes per row: RP, PH, PL)

| RP | Meaning |
|---|---|
| $00..$FE | Repeat count for additive sweep |
| $FF | Jump to PH |

PH/PL = 16-bit addition to pulse width (PH = high byte, PL = low byte).
On instrument init: pulse width registers ($D402/$D403) reset to 0.
SID uses only lower 12 bits. Example program builds from zero using additions.

### 6.4 Vibrato / Slide table (3 bytes per row: RP, FH, FL)

| RP | Meaning |
|---|---|
| $00..$FD | Repeat count for additive frequency sweep |
| $FE | Set absolute frequency (drum mode): write FH→$D4xx+1, FL→$D4xx |
| $FF | Jump to FH |

FH/FL = 16-bit addition to voice frequency (or absolute freq, or jump target).
This offset is added to the note's base frequency (from freq table + arpeggio step).
While glide/slide sector command is active: vibrato is suspended but stays in sync.

---

## 7. Glide table

16 entries, 2 bytes each (high byte, low byte of 16-bit absolute glide speed).
Used by Gld.0X (glide) and Gld.1X (slide) sector commands. Speed is absolute
(not adaptive to note frequency). One of the known limitations Taki planned to fix.

---

## 8. Multi-speed / timing

- `$1003` (`p_play`): first player call per frame — processes track+sector+effects for all 3 voices
- `$1006` (`p_mult`): subsequent calls (for multi-speed) — runs only effect tables (sounds)
- Speed value: number of `$1006` calls per frame (0 = 1× speed, 7 = 8× speed, etc.)
- V01.22: up to 10×; V01.23: up to 16×
- In V01.23, multi-speed calls are spread equally across the raster frame (CIA timer 1)
- Speed per subtune stored at $1692 (one byte per subtune, length at $1594)
- IRQ runs with ROMs mapped out ($01 = $35) except for I/O in the editor

---

## 9. Volume control

- Internal volume slide: Inc/Dec track instructions modify a running counter
- External control (V01.22): write desired volume to $168E, write $00 to $1678 each frame
- External control (V01.23): use $1673 (volume) and $165D (volume control register)
- $D418 = volume (bits 3-0) OR filter-type (bits 6-4)

---

## 10. Packed file format

The packer (V01.23, new implementation by TLC) takes the editor's "compact data"
save format and produces a relocatable player+data binary. Key options:
- Start address (hex, e.g. $1000)
- SID base address (e.g. $D400 for C64, $FD40 for Plus/4 SID card)
- Frequency table variant (C64 = 985248 Hz based; Plus/4 = 885 kHz based)
- Zero-page pointer address (default $FB/$FC)
- Identity field (32 chars, stored at player_start + $20 in screen codes)

Packing process: parse used tracks → used sectors → used instruments → used
effect-table entries; relink all indices; eliminate all dead data.

---

## 11. Version history summary

| Version | Date | Notes |
|---|---|---|
| V00.xx | pre-1994 | Development versions, none functional |
| V01.0x | early 1994 | First working players, too slow |
| V01.14 | 1994 | First used for actual tunes; test bit hard restart; 2 known bugs |
| V01.20 | 1994 | Reduced sector instruction set; optimized; absolute freq for glide/vibrato |
| V01.21 | 1994 | Modified V01.20 slide; "nobody ever used this one" |
| V01.22 | 1994 (code); 1999 (release) | Further optimized; 10-15% less rastertime than V01.20; source lost except player |
| V01.23 | 2000-03-12 (TLC) | GPL release; code runs on C64+Plus/4; up to 16×; new packer; bugs fixed |
| V01.24 sub030 | unknown | Unofficial "Enhanced" version (YouTube evidence only; not in source tree) |

---

## 12. Rastertime

Low rastertime was a primary design goal:
- First call ($1003): maximum ~$14 scanlines
- Subsequent calls ($1006): maximum ~$10 scanlines

Tips from author: avoid glide/slide where possible (worst routine); stagger
effect table jump/repeat points (use primes, avoid round numbers); never use
the same instrument on two voices simultaneously.

---

## 13. Leads to follow

- Obtain and disassemble the V01.22 d64 from CSDB ($1494 download) for the binary layout
- Check whether a V1.24 "sub030 Enhanced" binary is available (YouTube video exists;
  may be on some Hungarian scene FTP or C64 forum)
- Inspect PLAYER.ASM more carefully for exact ZP variable assignments (pt=$FB/$FC,
  plus per-voice state: dur_dc, finish, gt_dec, gt_msk, acnote, etc. — all need mapping)
- Check ftp://c64.rulez.org/pub/c64/Tools/Music/Editor/ for additional SIDwinder releases
- Verify how many HVSC SIDs use this player (sidid signature:
  `AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8`)
- The HVSC has 117 SIDwinder SIDs according to the existing research.md stub
