---
source_url: http://chordian.net/files/programs/c64/JCH_C64_Editor_v3.04.zip
fetched_via: curl
fetch_date: 2026-06-15
author: Jens-Christian Huus (JCH / Chordian) of Vibrants
content_date: 1995 (docs) / 1998 (archive release) / 2007 (README tweak)
reliability: primary
---

# JCH NewPlayer Editor v3.04 — Complete Technical Documentation

Downloaded from CSDb release #14037 (https://csdb.dk/release/?id=14037).
Archive saved to: /home/jtr/sidfinity/tmp/vibrants_laxity_research/JCH_C64_Editor_v3.04.zip
Also: D64 images and ED37_SRC.TXT (96KB assembler source for editor v3.03) extracted.

This documents the FULL JCH editor + NewPlayer format — direct descendant of the Laxity Editor
(Laxity told JCH to stop using his editor, so JCH wrote his own, starting ~1988).

---

## Memory Map (JCH Editor v3.03 source header)

From ED37_SRC.TXT (6502 assembler source, comments in Danish):

```
BUFFER  $0900-$093F   — TrackCopy buffer
DISK1   $0A00-$0E3F   — Diskmenu print-frame
MUSIC   $0F00-$45D3   — Music data block (example: Drax's 'FUNKY')
DISK2   $C800-$CFE0   — Diskmenu code
JMPS    $CF00-$CFFF   — Sys$CF00 and jmp($CFFE)
TABLES  $E000-$E2BD   — Player version tables
NEWFR   $E2D0-$E437   — '/' table-window plots
EASS    $8000-$84FF   — Einstein EASS code (Amiga→C64 dev tool)
EDITOR  $A000-????    — Editor machine code
PLOTBUF $E440-$E5A7   — Table-window plot store
COLBUF  $E5B0-$E6EF   — Table-window color store
```

Key zero-page variable assignments (from ED37_SRC.TXT):
- `$a0` voicon, `$a2` vol, `$a4` credits, `$a6` tpoin, `$a8` sinit
- `$aa` ain, `$ac` getinit, `$ae` getcom, `$b0` get2, `$b2` getins
- `$b4` real, `$b6` setsid, `$b8` notes, `$ba` fintun
- `$bc` arp1, `$be` arp2, `$c0` filttab, `$c2` pulstab
- `$c4` instr, `$c6` v1, `$c8` v2, `$ca` v3
- `$cc` lobyt, `$ce` hibyt, `$d0` slidtab
- `$d2` s0, `$d4` s1, `$d6` s2, `$d8` s3
- `$da` gat, `$dc` nog, `$de` trans1, `$e0` sflag
- `$e2` not, `$e4` vhzl, `$e6` vhzh, `$e8` next
- `$ea` insnr, `$ec` ge02

---

## Track/Sequence System (ED6_EPIL.TXT — JCH manual, written 1990)

### Music data starts at $0F00

### Track entry format (2 bytes: XXYY)

- `XX` = transpose byte ($80 = no transpose, $8C = one octave up, etc.)
  - Range: $80..FD (values below $80 are ILLEGAL — causes two sequences to play at once)
  - $8C = +12 semitones, $80 = base
- `YY` = sequence number ($00–$70 valid, $71-$FF reserved for editor code)
- Special markers:
  - `FF xx` = wrap marker (loop voice back to start — sequence number ignored)
  - `FE xx` = end marker (stop voice — only in players v14+)

### Sequence byte encoding (pre-pack / in-editor)

Each sequence step occupies 2 bytes in memory (uncompressed editor format):
- Left byte: duration ($80 = duration-length 00, i.e. one gamespeed-frame)
- Right byte: note/command value:
  - `$30` = C-4 (standard note encoding)
  - `$7E` = continue (+++ / gate-on hold)
  - `$00` = rest (--- / gate-off)

Example from ED manual:
```
C-4  +++ +++ +++ +++ --- --- ---
→ in memory: 80 30  80 7E  80 7E  80 7E  80 7E  80 00  80 00  80 00
→ packed:    84 30  82 00    (C-4 dur=4, rest dur=2)
```

### Packed sequence byte format (NP-Packer v5.3 output)

After packing, a note entry is `dd nn` where:
- `dd` = duration count (number of gamespeed frames for this step)
  - High nibble bits control step type; low bits are duration count
- `nn` = note value or command

### Sequence commands (in-sequence, left column)

| Command | Description |
|---------|-------------|
| `I00`–`I1F` | Set instrument number (0–31) |
| `S00`–`S3F` | Invoke super-table entry (slide/vibrato/hard-restart/arpeggio-change) |
| `***` | Tie note (note sustains without retriggering — affects packer behavior) |

---

## JCH NewPlayer Format — Player Version History

(From ED6_EPIL.TXT and README.TXT)

| Version | Key Feature | Notes |
|---------|-------------|-------|
| v00–v04 | Pre-editor players | Cannot be used in the editor |
| v05–v09 | Demo-only players | No multiple-tune support |
| v10 | First multi-tune player | `G` suffix means game-capable |
| v11 | First hard restart (buggy) | |
| v12 | First successful compromise player | ~$12 scanlines, no hard restart |
| v13 | Corrected hard restart | |
| v14 | Hard restart + FE00 end-mark + arpeggio direct pointers | Best "standard" player |
| v15.G6 | Super-table; vibrato moved to sequence commands | Ultra-precise vibrato (Jesper Olsen algorithm shared w/ Laxity, Rob Hubbard, Charles Deenen) |
| v17.G1 | Compromise: hard restart + $14 scanlines | No `FE00` end-mark |
| v18 | Complex, high rastertime | Not recommended |
| v19.G1 | Extreme cut-down: $0D scanlines, no vibrato | Very hard restart |
| v20.G4 | Best player: $1F scanlines, all features | DEFAULT in ED v3.04 |

Version naming: `vNN.Gx` where `NN` = version, `G` = game-capable, `x` = bug-fix revision.

---

## 8-Byte Instrument Table (Players v14, v15)

### v14 instrument (8 bytes: A B C D E F G H)

| Byte | Content | Details |
|------|---------|---------|
| A | Attack/Decay | |
| B | Sustain/Release | |
| C | Vibrato width (hi-nibble) + vibrato trigger/delay (lo-nibble) | |
| D | Vibrato speed (hi-nibble) + hard restart timer (lo-nibble, 0=off, min=2, max=gamespeed) | |
| E | Hi-freq mode (hi-nibble: 0=off, 1=on) + filter on/off+passband (lo-nibble: 0=off, 1-F=on+passband, 8=modulate-only) | |
| F | Filter table pointer | |
| G | Pulse table pointer | |
| H | Arpeggio table pointer | |

### v15 instrument (8 bytes: A B C D E F G H) — changes from v14

| Byte | Content | Changes |
|------|---------|---------|
| A | Attack/Decay | unchanged |
| B | Sustain/Release | unchanged |
| C | Hi-freq mode (whole byte, 0=off, any other=on) | Was vibrato — vibrato MOVED to super-table |
| D | Filter resonance (hi-nibble) + filter on/off+passband (lo-nibble) | Resonance moved INTO instrument |
| E | Filter table pointer | Was hi-freq+filter |
| F | Pulse table pointer | unchanged (was G) |
| G | Arpeggio pointer for GATE-ON (+++ steps) | Now TWO arpeggio pointers! |
| H | Arpeggio pointer for GATE-OFF (--- steps) | New in v15 |

### v20 instrument (8 bytes: A B C D E F G H) — changes from v18

| Byte | Content | Changes |
|------|---------|---------|
| A | Attack/Decay | unchanged |
| B | Sustain/Release | unchanged |
| C | SPLIT: hi-nibble = hi-freq (4=on, 8=hard-restart-on, C=both) + lo-nibble = arpeggio SPEED (0=fastest, F=slowest) | Expanded from v18 |
| D–H | Same as v18/v15 | |

v20 byte C examples:
- `$40` = hi-freq on, hard restart off, arp speed 0 (fastest)
- `$83` = hi-freq off, hard restart on, arp speed 3
- `$CF` = both hi-freq and hard restart on, arp speed F (slowest)

---

## Arpeggio Table (v14 format — two-column, 256 bytes each)

The arpeggio table is physically TWO 256-byte tables interleaved in the editor display:

Left column (note values):
- `$00–$5F` = note add (added to sequence note)
- `$80–$DF` = absolute note from hertz table (ignores note, transpose, slide)
- `$7F` = end/loop marker — right column byte is the WRAP POINTER (direct index, changed from v13 indirect)

Right column (waveforms):
- Normal waveform values while playing
- When left column = `$7F`: this byte is the loop-back index

Example:
```
3C: DF-81   ← fixed note DF, waveform $81
3D: 00-41   ← add 0 semitones, waveform $41
3E: 03-41   ← add 3 semitones
3F: 07-41   ← add 7 semitones
40: 7F-3D   ← end, loop back to $3D
```

v20 adds the `$7E` endmark: repeats last step forever (like $7F but no explicit loop pointer).
WARNING: The NP-packer hunts for `$7F` to find table end — using `$7E` as the LAST arpeggio
entry will cause the packer to erase everything from that point until it finds a `$7F`.
Safe usage: ensure the very last arpeggio in the table uses `$7F`.

---

## Pulse Table (v14 format — 4 bytes per set)

```
Byte 1: Width boundaries (hi-nibble=lo-boundary, lo-nibble=hi-boundary, SWAPPED)
Byte 2: Pulsation speed ($00–$FF)
Byte 3: Step-control byte (bit 7 = read startpuls from byte 4; bit 6 = stay forever; bits 0-5 = frame count $00-$3F)
Byte 4: Start pulse (hi-nibble=lo-byte-hi-part, lo-nibble=hi-byte — stored SWAPPED; only used when byte3 bit7 set)
```

Pulse width $0xxx encoding: stored as nibble-swapped in byte4 (lo-nibble is hi-part of freq, hi-nibble is lo-part).
To store pulse $4A0: byte4 = $A4 (lo $A, hi $4 → stored as $A4).

Sets are indexed as $00, $04, $08, $0C... (every 4 bytes). Byte 3 pointer field points to next set index.

Example (MoN-style bass pulse):
```
00: 3D A0 82 03   ← start at $300, range $300-$D00, speed $A0, 2 frames, then next
04: 3D 80 02 00   ← continue range $300-$D00, speed $80, 2 frames, next
08: 3D 60 02 00   ← speed $60, 2 frames, next
0C: 3D 40 4F 00   ← speed $40, $0F frames forever (bit6 set in $4F → stay)
```

---

## Filter Table (v14 format — 4 bytes per set, starting at offset $04)

IMPORTANT: First 4 bytes ($00-$03) are RESERVED — always start filter programs at offset $04.

Reserved bytes usage varies by player version:
- v14: `$0F 00 09 01` — hard restart fine-tuning + first-frame skip control
  - Bytes 1-2: Hard restart ADSR overrides (normally `0F 00`)
  - Byte 3: First-frame waveform ($09 = test-bit reset)
  - Byte 4: First-frame skip enable ($01=skip, $00=don't skip)
- v15: Bytes 1-3 are ctrl-bytes (00=max rastertime/01=skip when vibrato on/02=always skip per voice)
  - Byte 4: Voice selector for filter-sweep calculations (00=voice1, 01=voice2, 02=voice3)
- v20: Bytes 1-2 = half-speed selectors (filter-table speeds for pseudo-speed 0/1 mode)

Filter set format (4 bytes: A B C D):
- A: Start filter frequency (hi-byte of freq, e.g. $80 = freq starts at $80xx)
  - `$FF` in v14 = "use current filter freq, don't reset"
- B: Filter sweep speed ($00–$FF)
- C: Step-control byte (same as pulse: bit7=read start, bit6=stay, bits0-5=frame count)
  - DIFFERENCE from pulse: direction is determined by byte C bit 7 in v20
    (0=add, 1=subtract; achieves subtraction via byte wrap)
- D: Start resonance+filter in v14 (hi-nibble=freq-hi, lo-nibble=resonance);
     In v15/v20: only filter frequency start (resonance moved to instrument byte D)
     In v20: `$FF` = don't reset filter, continue with current value

---

## Super-Table / Slide-Table (v15 format)

The super-table replaces the separate slide-table from v14. A 2-byte command entry,
accessed via `Sxx` sequence command.

Recognize bits determine command type:

### Slide command (nibble A = 0, 1, 2, or 3):
```
AA BB CC DD (4 nibbles = 2 bytes)
A: direction+ignore (0=up@note, 1=up@+++/---, 2=down@note, 3=down@+++/---)
BCD: 12-bit speed value
```
Examples: `00 80`=slide up speed $80 at note; `20 80`=slide down speed $80 at note.

### Vibrato command (nibble A = 4 or 6):
```
AB CD
A: 4=at note, 6=at +++/---
B: "feeling" (add value to width per frame, 0=no feeling, turns off if 0)
C: vibrato speed (1=fast, F=police-siren slow; normally 3)
D: vibrato width (0=max, 7=barely noticeable; 8-F unused)
```
Vibrato uses the same calculated vibrato routine as Laxity, Charles Deenen, Rob Hubbard (by Jesper Olsen) — octave-independent precision.

### Hard restart / echo / reverb command (nibble A = 8):
```
8B CD
8: recognize nibble (always 8)
B: duration timer (0=off, 2=typical, max=gamespeed)
CD: new SUSTAIN value ($00 for hard restart, other values for echo/reverb)
```
Position 0 in super-table is reserved for hard restart default (normally `82 00`).

### Arpeggio-change command (v15 only, nibble AB = C0..DF):
```
AB CD
AB: $C0-$DF — instrument number (C0=inst0, DF=inst31)
CD: new arpeggio pointer value
```

---

## Player v20 — Pulse/Filter Step Programming (redesigned from v15)

### v20 Pulse table (4 bytes: A B C D)

- A: Start pulse (reversed nibble — `$FF` = use current pulse, don't reset)
- B: Pulsation speed ($00–$FF)
- C: Frame duration + direction (bit7=direction: 0=add, 1=subtract; bits0-6=frame count $00-$7F)
- D: Pointer to next set

### v20 Filter table (4 bytes: A B C D)

- A: Start filter frequency ($00-$FE; $FF = use current)
- B: Add value (wrapping addition — to subtract X, use $FF-X as addition)
- C: Frame duration ($00-$7F)
- D: Pointer to next set

---

## Multi-tune Support (v10+)

Tunes are split by FF00 wrap-markers. Maximum 31 tunes in one music block. The NP-packer:
1. Detects tune boundaries by finding FF00/FE00 sequences
2. Sets an info-byte in the player header indicating tune count
3. The Deluxe Driver reads this count and allows numeric access (keys 1-N)
4. Each tune can have an INDEPENDENT speed defined at pack time

---

## Files in JCH_C64_Editor_v3.04.zip

```
README.TXT         — Main readme (JCH 1998, tweaked 2004+2007)
ED37_SRC.TXT       — Full assembler source for editor v3.03 (96KB, Danish comments)
D64.ZIP            — D64 disk images:
  ED3_04.D64       — Editor v3.04 object files
  JCH_SRC.D64      — Player source: v17.G1, v19.G1, v20.G4, NP-Packer v5.3, digi
  JCH_UTIL.D64     — Latest editor+packer+utilities
  WORK.D64         — Worktunes by DRAX and JCH
  D_DRV_51.D64     — Deluxe Driver v5.1 source+objects
ED_TEXTS.ZIP       — Documentation texts (TXT + SEQ for C64):
  14_G0_V2.TXT     — Full instructions for player v14 (29KB)
  15_G6_IN.TXT     — Full instructions for player v15 (30KB)
  17_G1_IN.TXT     — Instructions for player v17
  19_G1_V2.TXT     — Instructions for player v19
  20_G4_IN.TXT     — Instructions for player v20 (16KB)
  ED2_53_K.TXT     — Editor v2.53 key guide
  ED3_02_K.TXT     — Editor v3.02 key guide
  ED6_EPIL.TXT     — Epilogue: full v2.53 manual + track/sequence system (30KB)
  MEMO-V*.TXT      — One-page memo cards for each player version
  PACK_5_3.TXT     — NP-Packer v5.3 instructions
  SLD_V14.TXT      — Slide table addendum for v14
```

---

## Relationship to Laxity Editor

From JCH's 20_G4_IN.TXT (May 1991):

> "the same system as used in LAXITY's player" (referring to v20's pulse step-programming)
> "$7E endmark, which simply repeats the very last step all the time. Very small addition
> really, as you could achieve the same thing easily with $7F, but what the heck. However,
> using the $7E endmark COULD cause misunderstandings in the PACKER!"
> "some players (like LAXITY's and JOZZ's to mention a few) also offers the $7E endmark"

From 15_G6_IN.TXT (July 1990):
> "[vibrato uses] the same calculated vibrato routine [as] JESPER OLSEN, LAXITY and
> CHARLES DEENEN (amongst many others)... it was originally done by ROB HUBBARD"
> "kinda like LAXITY's raster-time if I may say so...!"

These confirm that:
1. The Laxity Editor's pulse programming was the MODEL for JCH v20's redesign
2. Laxity used a `$7E` arpeggio endmark (repeat-last-step-forever) — distinct from $7F (jump to index)
3. Laxity's player used the Jesper Olsen calculated vibrato routine (octave-independent)
4. Laxity's rastertime was considered very well-controlled (~$21 scanlines reference)

---

## Zimmers.net Vibrants Collection Notes

Source: `ftp://ftp.zimmers.net/pub/cbm/c64/audio/Vibrants/`

The Vibrants music collection at Zimmers.net organizes tunes by composer with player version numbers:
- **3x-player/**: Laxity's 3x-speed player — tunes start at $4000 (NOT standard $1000)
- **Laxity/**: Player versions: (from README) not explicitly listed but covered by Vibrants/Laxity sidid sig
- **utils/Relocate Laxity.prg**: Official relocator for Laxity tunes

The 3x-player subdirectory contains:
- `3xplayer.prg` (97 bytes!) — "A simple 3x-player routine written by Laxity"
- Several music files (mcoolkaf, meastend, msyncopa, mwasteii, myieldpo, mzimxusa, soap1440, sweet144)

The 97-byte player is extremely minimal — almost certainly just a dispatch stub that calls into the
main music data block. The music data is likely at $4003 (standard JCH/Laxity init/play offsets).
