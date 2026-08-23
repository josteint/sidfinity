# SID Duzz'It (SDI) — Source Code and Format Summary

**provenance:**
- source_url: https://sourceforge.net/projects/sidduzzit/
- fetched_via: curl from master.dl.sourceforge.net (SourceForge CDN mirror)
- fetch_date: 2026-06-13
- author: Geir Tjelta (GT) + Glenn Rune Gallefoss (GRG) of SHAPE, Norway
- content_date: docs v2.1.6 dated 18.05.2013; player source N50/SPD50 dated 16/05/2014; v2.1.7 release 12.10.2014
- reliability: primary source (open-source release from the authors)

Preserved in: `pipelines/sidduzzit/docs/src/`
- `SDI.2.1.6-docs.txt` — 1914-line official format documentation (65 KB)
- `sdi_217_manual.txt` — community-written PDF manual (Henrik Mortensen), more readable
- `SDI.2.1.6-note_tables.txt` — waveform-program note-value tables
- `sdi217_releasenotes.txt` — v2.1.7 bugfix notes
- `SRC_SDI21-N50.asm` — **normal player source** (PETSCII→ASCII decoded, 1999 lines)
- `SRC_SDI21-SPD50.asm` — **multispeed/frame player source** (2006 lines)
- `SRC.SDI21-N50.raw` / `SRC.SDI21-N50.txt` — raw PETSCII from D64
- `SRC.SDI21-SPD50.raw` / `SRC.SDI21-SPD50.txt` — raw PETSCII from D64

---

## 1. Overview

SID Duzz'It (SDI) v2.1 is a 3/4-channel C64 music tracker + player system written in
Turbo Assembler. The editor runs entirely on the C64. The dump workflow converts the
in-editor binary to a Turbo Assembler SEQ (sequential text) file; the composer then
appends it to the player source and assembles the result with TASS.

**History (source: SDI.2.1.6-docs.txt line 1–10):**
Built on ideas from JCH/Vibrants editor, Olav Morkrid/Panoramic "Digitalizer" editor,
and Geir Tjelta/Shape/Moz(ic)art "SID Systems". "SID Duzz' It" named while watching
a TV commercial for a screwdriver.

**HVSC footprint:** ~934 tunes (as of HVSC #84).

---

## 2. Player Entry Points and Load Address

**Source: `SRC_SDI21-N50.asm` line 409–414; docs.txt line 1750–1755; manual p.35.**

The assembled player always loads at `$1000` (hardcoded `*= $1000`).

```
$1000  JMP INIT     ; ldx #subtune (0-based, 0–31), jmp $1000
$1003  JMP PLAY     ; main play call — updates tracks, sequences, sounds
$1006  JMP FADEOUT  ; lda #fadevalue ($00–$7F = down, $00–$7F), jmp $1006
$1009  JMP PLAY     ; speed-play call (multispeed frame player only)
```

ZP usage: `$FE` and `$FF` (configurable as `mzero = $FE`).
SID base: `$D400` (configurable as `sid = $d400`; mirror banks $D5C0 also work).

**Player size:** ~$0900 bytes without optional routines (docs.txt line 1337).

---

## 3. Editor Memory Map (in-editor binary layout)

**Source: docs.txt lines 1832–1880; sdi_217_manual.txt memory overview section.**

This is the C64 memory map WHILE RUNNING THE EDITOR, not the dump format:

```
$0100–$017F   Stack
$0180–$0200   Sequence lengths (128 bytes, one per sequence)
$02A7–$0300   Data tables
$0340–$0400   Sprites
$0400–$07E8   Screen
$0800–$2EE0   Editor part 1
$2F00–$3000   Data buffer
$3000–$3800   Track 1 (4 channels × $800 bytes = $1000 total)
$3800–$4000   Track 2
$4000–$4800   Track 3
$4800–$5000   Track 4
$5000–$D000   Sequences ($8000 bytes / 128 sequences = max ~$100/seq)
$D000–$D810   Directory memory (max 128 SDI files)
$D810–$E000   Editor part 2
$E000–$E100   Waveform program table (256 bytes)
$E100–$E200   Waveform program note table (256 bytes)
$E200–$E300   Pulse program table (256 bytes)
$E300–$E400   Arpeggio data (256 bytes)
$E400–$E500   Arpeggio program table (256 bytes)
$E500–$E600   Vibrato program table (256 bytes)
$E600–$E700   Filter program table (256 bytes)
$E700–$E8E0   Sound setup (10 bytes × 48 instruments, column-major — see §5)
  $E700–$E730   Waveform program pointer  (48 bytes)
  $E730–$E760   Attack/Decay              (48 bytes)
  $E760–$E790   Sustain/Release           (48 bytes)
  $E790–$E7C0   Gate timeout              (48 bytes)
  $E7C0–$E7F0   Vibrato program pointer   (48 bytes)
  $E7F0–$E820   Pulse program pointer     (48 bytes)
  $E820–$E850   Filter program pointer    (48 bytes)
  $E850–$E880   Filter band/resonance     (48 bytes)
  $E880–$E8B0   Detune high               (48 bytes)
  $E8B0–$E8E0   Detune low                (48 bytes)
$E8E0–$E970   Future expansion
$E970–$E980   File info (speed calls, speed channels)
$E980–$EA00   Tempo data
$EA00–$ED00   Sound names (48 × 16 bytes = 768 bytes)
$ED00–$ED20   Default tempo lookup table per tune (32 entries)
$ED20–$ED40   Channels ON lookup table per tune (32 entries)
$ED40–$ED70   Tempo program table
$ED80–$EDC0   Marked channel positions
$EDC0–$EDE0   InVol volume setup (32 songs × 1 byte)
$EDE0–$EE00   InVol filter setup (32 songs × 1 byte)
$EE00–$EEC0   Note frequency table (PAL, 192 entries = 96 lo + 96 hi)
$EEC0–$FFE6   Player + Editor part 3
```

**Key layout insight:** The sound-setup table is COLUMN-MAJOR — each field for all
48 instruments is stored as a contiguous 48-byte array, not as 48 × 10-byte records.
The player accesses `Z0,Y` through `Z9,Y` where Y = instrument number.

---

## 4. Dumped File (Player Data) Layout

**Source: `SRC_SDI21-N50.asm` lines 409–530; docs.txt lines 1381–1495; manual lines 1958–1966.**

The dump is a Turbo Assembler SEQ file appended after the player's `RTS`. The dump
creates assembly labels that the player references. Key labels (in order within the
dump, as referenced by the player source):

### 4.1 Per-Channel State Block (7 bytes × 4 channels)

Defined inline in the player at `$1000+` as zero-initialised arrays:

```
CHANON   ; channel-on bitmask: $01,$02,$04,$80 for ch1–ch4
CHANOFF  ; complement: $FE,$FD,$FB,$7F
TRKLO    ; track data pointer lo byte
TRKHI    ; track data pointer hi byte
TDELAY   ; track delay counter
TRACKY   ; track position (8-bit or 16-bit depending on rem_trkl)
TRACKHI  ; track position hi (16-bit mode only)
```

All per-channel arrays are laid out as 4×7-byte rows (one row per channel).
Channel 4 (the conductor/tempo/filter channel) is row index 3 (offset 21).

### 4.2 Music Data Labels (from the dump)

These are the labels in the DUMPED file that the player refers to:

```
W    Waveform program table     (waveform byte column)
F    Waveform program note col  (note/command byte column)
V    Vibrato program table      (3 bytes per entry: delay, width, speed)
P    Pulse program table        (4 bytes per entry: lo/hi, hi-sweep, speed, mode)
FI   Filter program table       (4 bytes per entry: hi/lo, sweep, speed, mode)
A    Arpeggio data table        (note offsets; $80+ = loop marker)
AD   Arpeggio program table     (pairs: data-pointer-byte, speed+sound-byte)
TEM_P Tempo program pointer table
TEM_D Tempo program data table
Z0   Sound setup col 0: waveform program pointer (per-instrument, 48 entries)
Z1   Sound setup col 1: Attack/Decay
Z2   Sound setup col 2: Sustain/Release
Z3   Sound setup col 3: Gate timeout
Z4   Sound setup col 4: Vibrato program pointer
Z5   Sound setup col 5: Pulse program pointer
Z6   Sound setup col 6: Filter program pointer
Z7   Sound setup col 7: Band/Resonance
Z8   Sound setup col 8: Detune high  (rem_det=1 → omitted)
Z9   Sound setup col 9: Detune low   (rem_det=1 → omitted)
TL   Track lo-byte pointers  (one per song × 4 channels)
TH   Track hi-byte pointers
TP   Tempo program pointer per song
S    Default tempo value per song
C    Channel-on bitmask per song
FV   FadeIn+Volume per song (hi nibble=fadein, lo nibble=vol)
FS   Filter channel force + filter speed per song
SB   Sequence byte/track data (the actual track+sequence payload)
```

**Source verify:** `SRC_SDI21-N50.asm` lines 697–830 (Z0–Z9, W, F reads in
the instrument-set routine `SET_SND`); lines 1843–1874 (FREQHI/FREQLO tables).

### 4.3 Sequence / Track Encoding (Dumped Format)

**Source: docs.txt lines 1381–1495; manual pp.31–32.**

The dump encodes each sequence as a compact byte stream. Decoded examples
(docs.txt line 1386):

```
Editor:           Dumped:
01 C-4 (note)  → 81 61 30 0
  [sound_byte, duration_byte, note_byte, $00 terminator]
```

Byte meanings in the sequence stream:
- `$00` — end-of-sequence terminator
- `$01–$5E` — duration value (raw, frames per line × count)
- `$5F` — "empty / tie continues" (no new note)
- `$60–$7F` — duration values (extended range)
- `$80–$FF` — various command + sound/arp/glide bytes (see §7 below)
- An empty `$1F`-length sequence dumps as `7F 5F 0` (docs.txt line 1484)
- An empty `$3F` sequence: `5F FF 5F 0` (line 1488)
- An empty `$7F` sequence: `5F E0 7F 5F 0` (line 1492)

Track data format (the tracker orderlist per channel):
- Each track line: `[transpose_byte] [seq_number_byte]`
- `$80–$9F` = transpose down; `$A0` = no transpose; `$A1–$BF` = transpose up
- Valid sequence numbers: `$00–$7F`
- Track terminators:
  - Jump: `$F8–$FF [lo] [hi]` (2-byte absolute pointer to track position)
  - Delay: `$C0–$F7 [delay_value]` before `[transpose] [seq]`
  - Stop (voice off): `$F8` (with rem_voff=0)
- Track length: max $FF bytes normally; $07FF with `rem_trkl = 0`

---

## 5. Instrument (Sound Setup) — 10 Fields, Column-Major

**Source: docs.txt lines 422–488; `SRC_SDI21-N50.asm` lines 697–830 (Z0–Z9 reads).**

Each instrument occupies one slot in 10 parallel 48-entry arrays (Z0–Z9):

| Field | Array | Description |
|-------|-------|-------------|
| Z0    | waveform ptr | Index into W/F tables (1-based; player does `TAY; INY; TYA` for 1WF skip) |
| Z1    | attack/decay | SID $D405 format (hi=attack, lo=decay) |
| Z2    | sustain/release | SID $D406 format |
| Z3    | gate timeout | see §5.1 below |
| Z4    | vibrato ptr | 0=no vibrato; 1–$55=vibrato program |
| Z5    | pulse ptr | 0=no pulse; 1–$40=pulse prg; $41–$80=infinite sweep; $8X=direct hi-pulse |
| Z6    | filter ptr | 0=no filter; 1–$40=filter prg; $41–$80=sweep mode 1; $81–$C0=sweep inf; $C1–$FF=mode 3 |
| Z7    | band/resonance | SID $D417 format (hi nibble=band bits 3–1, lo nibble=resonance) |
| Z8    | detune hi | 0=off; $01–$7F=up; $80–$FF=down |
| Z9    | detune lo | 0=off; $01–$FF=fine adjustment |

48 instruments total: instruments $00–$1F are "normal"; $20–$2F are
"arpeggio-only" instruments (accessible only via the arpeggio program, not directly
from the sequencer). (docs.txt line 269, 1887)

### 5.1 Gate Timeout (Z3 / GATE TIMEOUT field)

**Source: docs.txt lines 443–455.**

Controls hard/soft restart behaviour. Bits [6:5] select restart mode; bits [4:0]
select timeout length (in frames × 2):

```
$00,$20,$40,$60,$80,$A0,$C0,$E0  → no timeout (immediate release)
$01–$1F   gate timeout + normal hard restart
$21–$3F   gate timeout + hard restart 2
$41–$5F   gate timeout + hard restart 3
$61–$7F   gate timeout + hard restart 4
$81–$9F   gate timeout + soft restart 1
$A1–$BF   gate timeout + soft restart 2
$C1–$DF   gate timeout + soft restart 3
$E1–$FF   gate timeout + soft restart 4  (like tie note)
```

Note: v2.1.7 bugfix (releasenotes.txt): "If you started your song with a gate
timeout of Ax, Cx or Ex, the first note strike would sometimes not happen."

In the player: `LDA Z3,Y; AND #$1F; ASL A; STA GATEDEC,X` — so the timeout
duration is `(Z3 AND $1F) * 2` frames. (`SRC_SDI21-N50.asm` line 719–721)

---

## 6. Waveform Program Table (W + F)

**Source: docs.txt lines 553–795; note_tables.txt; `SRC_SDI21-N50.asm` lines 831–850, 1451–1640.**

Two parallel tables, accessed as pairs: `W[y]` (waveform/command byte) and `F[y]`
(note/parameter byte). The pointer into these tables is `WFP` (per-voice, 8-bit index).

### 6.1 Standard waveform bytes (W column, c2)

```
$00  Gate off
$01  Gate on
$02  Sync off
$03  Sync on
$04  Ring mod off
$05  Ring mod on
$10  Triangle (gate off)    $11  Triangle (gate on)
$20  Sawtooth (gate off)    $21  Sawtooth (gate on)
$40  Pulse (gate off)       $41  Pulse (gate on)
$80  Noise (gate off)       $81  Noise (gate on)
$30  Tri+Saw  $50  Pulse+Tri  $60  Pulse+Saw  $70  Pulse+Saw+Tri
```

Arpeggio waveforms (set bit 7 → use arpeggio data):
```
$91  Triangle+arp  $A1  Sawtooth+arp  $B1  Tri+Saw+arp
$C1  Pulse+arp     $D1  Pulse+Tri+arp  $E1  Pulse+Saw+arp
```
(Player: `CMP #$90; BCC *+4; AND #$7F` strips the arp-flag before writing to SID.)

### 6.2 Note column (F column, c3) values

```
$00–$5E   Soft note: added to note + track transpose
$60–$7F   Soft note: subtracted from note + track transpose
$80–$DE   Fixed note: overrides note + track transpose (index into freq table)
$DF–$FF   Unused (reserved)
```
Note: `$7F` (H-7 downward-table) is the limit. Values `$E0–$FF` are not used
(note_tables.txt line 72).

### 6.3 Waveform commands (W column $E2–$FF, c2)

These occupy the upper byte; the following byte is F[y]:

| Cmd | Param | Effect |
|-----|-------|--------|
| `$FF` | `XX` | Jump to waveform program line XX |
| `$FE` | `XX` | Delay next waveform XX frames |
| `$FD` | ... | ADSR command (2-byte): `[XX=gate-off delay] [AD] [SR]` — see §6.4 |
| `$FC` | ... | Drum command — UNSUPPORTED in v2.x (only in 1997–1999 versions) |
| `$FB` | ... | Multipulse command — switches between two pulse programs |
| `$FA` | `XX` | Repeat: following FF-jump executes XX times |
| `$F0–$F7` | `YY` | Write `$F0`–`$F7` directly to $D415 (lower 3 bits of filter cutoff) |
| `$EE` | `LH` | Pulse init: write lo+hi to $D402/$D403 and player pulse registers |
| `$ED` | `XX` | Pulse subtract: subtract XX from current pulse |
| `$EC` | `XX` | Pulse add: add XX to current pulse |
| `$EB` | `LH` | Pulse write: write lo+hi to SID pulse registers only |
| `$E2–$E7` | `yy` | Noise trick: write `$E2`–`$E7` directly to waveform register |

### 6.4 FD (ADSR) command detail

**Source: docs.txt lines 651–673.**

```
:FD XX    ; XX = gate-off delay
:AD SR    ; next two bytes = Attack/Decay, Sustain/Release

XX = $01–$7F   gate off after XX frames; can be re-gated
XX = $00/$80   no frame delay; no gate off
XX = $81–$FF   same as $01–$7F but gate cannot be re-enabled
```

Player code: `SRC_SDI21-N50.asm` lines 1480–1500.

### 6.5 FB (Multipulse) command

**Source: docs.txt lines 685–705.**

```
:FB P2    ; P2 = second pulse program pointer
:0X YY    ; X=0 start with P2, X=1 start with sound-setup pulse; YY=switch speed
```

---

## 7. Sequencer FX + Note Combinations

**Source: docs.txt lines 1167–1238; `SRC_SDI21-N50.asm` lines 857–1100.**

Each sequence line has two fields: FX byte (the command/sound selector) and NOTE byte.
Channels 1–3 and channel 4 (tempo/filter conductor) have different semantics.

### 7.1 Channels 1–3

| FX Range | Effect |
|----------|--------|
| `$00–$1F` | Set sound (instrument) number |
| `$21–$3F` | Set glide value (AND note is glide target; lower-case = tie-glide) |
| `$22–$3F` (no note) | Set vibrato program (FX low byte = vib program) |
| `$40–$6F` | Set arpeggio number ($40=arp0, $6F=arp47) |
| `$70` | Restore current sound's original ADSR with note |
| `$71–$7F` | Sustain/Attack effects: `$7x` with note sets attack or sustain |
| `$20 ON/OFF` | Set/remove channel filter mode |

Notes: uppercase = new note (gate on with hard restart); lowercase = tie note
(no restart). Gate commands (`GAT`/`gat`) = explicit gate on/off.

### 7.2 Channel 4 (Conductor / Tempo / Filter)

| FX Range | Effect |
|----------|--------|
| `$01–$1F` | Set tempo (direct value) |
| `$40–$60` | Look up tempo program |
| `$70` | Filter control back to main filter channel |
| `$71–$7F` | Force filter output |
| `$21–$3F` | Force filter program |
| `$61–$67` | Force filter band |
| `$68–$6F` | Future expansion |

The note column in channel 4 carries the main TRANSPOSE for all channels.
Transpose range: GAT (=$00 = C-0 = 0) to about C-2 (docs.txt line 1224).

---

## 8. Vibrato Program (V table)

**Source: docs.txt lines 798–848; `SRC_SDI21-N50.asm` lines 1340–1415.**

3-byte entries: `[delay, width, speed]`

| c2 (delay) | Meaning |
|-----------|---------|
| `$00` | Detuning and continue immediately |
| `$01–$FD` | Delay N frames before next entry |
| `$FE` | Detuning and hold (detuning only, no vibrato) |
| `$FF` | Infinite loop (crazy comet if c4 > $80) |

c3 (width): `$00–$7F` = up then down; `$80–$FF` = down then up.
c4 (speed): vibrato speed. If c4 > $80 → "Crazy Comet" loop effect.

**Detuning mode** (c2 = `$00` or `$FE`): c3=DL, c4=DH form a 16-bit frequency
offset: `DH=$00–$7F` = finetune up; `DH=$FF–$80` = finetune down.

85 vibrato programs available (capacity). (docs.txt line 1889)

---

## 9. Pulse Program (P table)

**Source: docs.txt lines 854–898; `SRC_SDI21-N50.asm` lines 1168–1275.**

4-byte entries (c2 c3 c4 c5): `[pulse_lo_hi, sweep_target_hi/lo, sweep_speed, mode]`

**5th column (c5) mode byte:**
```
$00,$40,$80,$C0  Stop at end value (no jump)
$01–$3F          Sweep to end, cut to c2 value (then jump to line c5&$F)
$41–$7F          Continuous sweep between two c3 values (or jump to new prg line)
$81–$BF          Reverse sweep, cut to c2
$C1–$FF          Reverse continuous sweep
```

**Pulse hold** variant: if c3=0, c4 is used as a delay counter before the jump in c5.

64 pulse programs available. (docs.txt line 1890)

---

## 10. Filter Program (FI table)

**Source: docs.txt lines 902–938; `SRC_SDI21-N50.asm` lines 1700–1795.**

Same structure as pulse program with two differences:
1. Column 2 byte order is reversed: hi/lo instead of lo/hi.
2. No pulse-hold routine; instead has a **filter frame** routine.

**Filter frame** (when c3=0):
```
01:4F 00 2F 82
    \   \  \  \
     \   \  \  8x = 1 frame delay; jump to next line
      \   \  band=$20, resonance=$0F (c4 as $D417 format)
       \   zero → filter frame mode
        $4F → filter cutoff high ($D416)
```

v2.1.7 bugfix (releasenotes.txt): "The filter cutoff routine was missing a small
compare routine for fast downwards subtraction. This could result in difference in
the sound output when compared to the editor."

64 filter programs. (docs.txt line 1891)

---

## 11. Arpeggio Program (AD + A tables)

**Source: docs.txt lines 944–993; `SRC_SDI21-N50.asm` lines 1606–1640.**

Two tables: `A` (arpeggio data, note offsets) and `AD` (arpeggio program, pairs).

`AD` table: 2 bytes per arpeggio:
- byte 0 (`AD[y]`): data pointer into `A` table; values ≥ `$80` set loop flag
- byte 1 (`AD[y+1]`): hi-nibble = speed; lo-nibble = instrument number

`A` table: sequence of semitone offsets. Values ≥ `$80` → loop back to the start
pointer stored in `AD`. Zero in arpeggio data = silence.

48 arpeggios total. Called from sequencer with `$40–$6F`.
Instruments $20–$2F are "arp-only" — only usable inside arpeggio programs.

Player accesses via arpeggio waveforms ($91/$A1/$B1/$C1/$D1/$E1) — if the
waveform byte has bit 7 set, the arpeggio subroutine runs.

---

## 12. Tempo Program (TEM_P + TEM_D tables)

**Source: docs.txt lines 997–1018; `SRC_SDI21-N50.asm` lines 1817–1836.**

Same structure as arpeggio: `TEM_P` (program pointers) + `TEM_D` (tempo data).

Tempo values:
- `$01–$7F` = normal tempo value
- `$81–$FF` = loop marker (wraps back to program start)
- `$00` or `$80` = invalid (stops music)

48 tempo programs. Default tempo per tune stored in `S` table (one byte per subtune).

---

## 13. Initial Volume and Filter (FV + FS tables)

**Source: docs.txt lines 1021–1070.**

`FV` table (one byte per subtune, 32 subtunes):
- hi nibble: fade-in speed (`0` = no fadein; `1` = fastest; `F` = slowest)
- lo nibble: starting volume (`0`–`$F`)

`FS` table (one byte per subtune):
- hi nibble: filter channel force flags (`0`=off; `1`=ch1; `2`=ch2; `4`=ch3; bitmask combinations)
- lo nibble: filter speed delay (`0`=fastest)

---

## 14. Per-Frame Write Model

**Source: `SRC_SDI21-N50.asm` full play loop (~lines 607–1840); docs.txt lines 1166–1238.**

### 14.1 Normal Player (N50) — VBI-driven

The normal player (`PLAY`) is called once per PAL VBI (50Hz). The full per-frame
sequence (each call to `$1003`):

1. **Conductor/tempo (channel 4):** If this channel's duration has expired, advance
   its sequence pointer. Process FX byte: set global tempo, tempo program index,
   transpose, or filter band.
2. **Per-voice loop** (channels 1–3, X iterates 21/14/7/0 offsets):
   a. **Gate timeout decrement:** `DEC GATEDEC,X` — if reaches 0, clear gate bit in
      per-voice WF register (`GATE,X`).
   b. **Duration counter:** `DEC DURATION,X` — if expired, fetch next sequence entry.
   c. **Sequence decode:** Read FX+NOTE bytes. Decode FX:
      - `$5F` = silence/tie → release sequence handling
      - `$F0–$FF` = release update
      - `$C0–$CF` = arpeggio number
      - `$A0–$BF` = glide value
      - `$80–$9F` = waveform ORA / sound update
      - `$40–$7F` = sustain/attack FX
      - `$00–$3F` = sound number or vibrato/glide
      Decode NOTE: `$00` = end-of-seq terminator; `$5F` = tie-note/empty;
      `$60–$DF` = duration; `$E0` = track step; `$F0–$FF` = release.
   d. **Instrument set** (on new note): load Z0–Z9 fields, write SID AD/SR,
      set gate bit, init WFP, PULSLE, FILTRE, GATEDEC, ARPLE.
   e. **Pulse program** (if PULSLE not $FF): run pulse sweep state machine.
   f. **Glide** (if GLIDADD not 0): add ADDVAL to ADDLO/ADDHI; check arrival at GLIDTO.
   g. **Vibrato** (if VIBLE not 0): update ADDLO/ADDHI via ADDVAL; handle crazy-comet.
   h. **Frequency write:** `FREQLO/FREQHI[note]` ± detune ± vibrato/glide addend →
      `SID+0,X` / `SID+1,X`.
   i. **Waveform program:** advance WFP; interpret W[WFP] / F[WFP] pair:
      - `$FF` → jump; `$FE` → delay; `$FD` → ADSR; `$FB` → multipulse;
        `$FA` → repeat; `$F0–$F7` → $D415; `$EE–$EB` → pulse cmds;
        `$E2–$E7` → noise waveform; `<$90` → normal waveform write.
      Write waveform byte AND GATE,X → `SID+4,X`.
   j. **Arpeggio** (if waveform has bit 7 set): advance ARPLE; read `A[ARPLE]`
      as note offset; add to NOTE,X → frequency lookup.
   k. **Frequency final write** (SID+0,X / SID+1,X with all offsets applied).
3. **Fadeout** (if FADE active): decrement/increment VOL, write SID+$18.
4. **Filter program:** run filter sweep state machine → SID+$16, $D417.
5. **Volume write:** `VOL OR BAND` → SID+$18.
6. **Tempo decrement:** `DEC TEMPO+1` — when expired, `DEC DURATION` on all channels.

**Per-frame SID write order (approximate, inner voice loop):**
```
SID+5,X  (AD — attack/decay, on new note)
SID+6,X  (SR — sustain/release, on new note)
SID+4,X  (control register — waveform + gate, always)
SID+2,X  (pulse lo, if pulse active)
SID+3,X  (pulse hi, if pulse active)
SID+0,X  (freq lo)
SID+1,X  (freq hi)
... [after voice loop:]
SID+$16  (filter cutoff hi)
SID+$15  (filter cutoff lo — only from waveform cmd $F0–$F7)
SID+$17  (filter resonance + route)
SID+$18  (volume + band)
```

OPEN: exact cycle-level ordering within a frame is not documented; requires
siddump `--writelog` to verify. The player processes voices in order ch3, ch2, ch1
(X iterates from 21→14→7, i.e. voice 3 first, voice 1 last).

### 14.2 Multispeed / Frame Player (SPD50)

**Source: `SRC_SDI21-SPD50.asm`; docs.txt lines 1757–1790; sdi_217_manual.txt p.35.**

The speed player separates "track/sequence update" from "sound update":
- `$1003` (main play call) = full update including track/sequence advancement
- `$1009` (speed-play call) = sound-only update (waveform prg, vibrato, glide,
  pulse, freq write) without advancing the sequencer

For a 4× speed tune on PAL (312 scanlines):
```
raster = 312/speed = 78 scanlines per IRQ
IRQ:  jsr $1003  (at raster 0)
      jsr $1009  (at raster 78)
      jsr $1009  (at raster 156)
      jsr $1009  (at raster 234)
      rti
```

Speed values: 2–15 (configurable `speed = N` parameter in the source).
`rem_opt = 0` → all channels get the extra speed calls.
`rem_opt = 1` → selectable via `spdchan = %00000111` bitmask which channels
receive speed calls.

---

## 15. Assembly Flags (rem_* / conditional compilation)

**Source: docs.txt lines 1603–1700; `SRC_SDI21-N50.asm` lines 6–34.**

Turbo Assembler conditional assembly; `1` = remove/ignore the feature:

| Flag | Default | Controls |
|------|---------|----------|
| `rem_4ch` | 1 | 4th channel (conductor). Set 0 if tune uses ch4. |
| `rem_det` | 0 | Detune (Z8/Z9). If 1, Z8+Z9 arrays may be omitted from dump. |
| `rem_gout` | 0 | Gate timeout (GATEDEC). |
| `rem_1wf` | 0 | Skip 1st waveform byte (saves cycles; may alter sound). |
| `rem_wfd` | 1 | Waveform delay ($FE command). |
| `rem_adsr` | 1 | ADSR waveform command ($FD). |
| `rem_mp` | 1 | Multipulse command ($FB). |
| `rem_wfr` | 1 | Waveform repeat command ($FA). |
| `rem_wf0` | 1 | $D415 write from waveform table ($F0–$F7). |
| `rem_puw` | 1 | Waveform-embedded pulse commands ($EB–$EE). |
| `rem_pu` | 1 | Pulse program routine (full P-table sweep engine). |
| `rem_we2` | 1 | $E2–$E7 noise waveform trick. |
| `rem_arp` | 0 | Arpeggio routine. |
| `rek_fi` | 0 | Filter routine (note: typo in original; should be `rem_fi`). |
| `rem_fspd` | 0 | Filter speed delay. |
| `rem_glid` | 0 | Glide routine. |
| `rem_vib` | 0 | Vibrato routine. |
| `rem_cc` | 1 | Crazy Comet vibrato effect (requires rem_vib=0). |
| `rem_fad` | 1 | Fadeout routine. |
| `rem_gat` | 1 | GAT/FLG command in sequencer. |
| `rem_f20` | 1 | Sequence command `20 XX` (filter channel force). |
| `rem_wfo` | 1 | Waveform ORA command in sequencer. |
| `rem_voff` | 1 | Voice on/off toggle during playback. |
| `rem_trkl` | 1 | Max $FF track size (0 = $07FF max track size). |
| `rem_tp` | 0 | Tempo programs. If 1, single tempo; enter value at offset `S`. |

**Frame-player only:**
| Flag | Default | Controls |
|------|---------|----------|
| `rem_opt` | 0 | Optional speed channels (use with `spdchan` bitmask). |
| `spdchan` | `%00000111` | Which channels get speed calls (%001=ch1, %010=ch2, %100=ch3). |
| `speed` | 4 | Number of speeds (for music displayer; 2–15). |
| `system` | 1 | 1=PAL, 0=NTSC (affects music displayer raster timing display only). |

**Effect on data layout:** When `rem_det = 1`, Z8 and Z9 arrays may be removed from
the dump entirely (docs.txt line 2011: "data at Z8 and Z9 can be removed"). Similarly
`rem_pu = 1` means the pulse program table `P` is not needed. This means the dumped
file size and table layout varies by the rem_* flags used.

---

## 16. Subtune System

**Source: `SRC_SDI21-N50.asm` INIT routine lines 1877–1999; docs.txt line 1884.**

- 32 subtunes supported (X = 0–31 at init call).
- Per-subtune data stored in: `S` (tempo), `C` (channel-on mask), `FV` (volume),
  `FS` (filter force+speed), `TP` (tempo program), `TL`/`TH` (track pointers per channel).
- Init resets all per-voice state (DURATION, SEQP, TRANSP, PULSLE2, SRCO, FILTRE,
  GATE, NOTE2, SOUND) and writes SID $D400–$D414 to 0.

---

## 17. Frequency Table

**Source: `SRC_SDI21-N50.asm` lines 1843–1874; `SDI.2.1.6-note_tables.txt`.**

96 entries (8 octaves × 12 notes = 96), split into `FREQHI[96]` and `FREQLO[96]`.
PAL-tuned (NTSC table available separately as `freq-ntsc` SEQ file on release disk).
Index 0 = C-0, index 95 = B-7 (using H for B in Nordic notation).

Waveform note table encoding (from note_tables.txt):
```
Soft notes upward:   $00=C-0 (rel. to base), $5E=H-4 (relative, added to seq note)
Soft notes downward: $60=E-0 (relative, subtracted from C-3 base), $7F=H-2
Fixed notes:         $80=C-0 (absolute), $DF=H-7 (absolute)
Values $E0-$FF: unused/reserved.
```

---

## 18. Sequence Size Constraints

**Source: docs.txt lines 1241–1261; known bug §1800.**

Valid sequence sizes: `$00` (min) to `$7F` (max = 128 lines).
Standard double-lengths: `$00 $01 $03 $07 $0F $1F $3F $7F`.
Non-standard sizes yield different polyrhythms.

Known bug: a `$7F`-length sequence filled ENTIRELY with tie notes (every line has
a note AND instrument change or glide) can produce a dumped sequence >256 bytes
(seen at 258 bytes). The dump has a $100 byte limit per sequence. Solution: split
the sequence. (docs.txt lines 1800–1804)

---

## 19. Capacities Summary

**Source: docs.txt lines 1882–1892.**

| Resource | Count |
|----------|-------|
| Subtunes | 32 |
| Sequences | 128 |
| Instruments (direct) | 32 ($00–$1F) |
| Instruments (arp-only) | 16 ($20–$2F) |
| Arpeggios | 48 ($00–$2F) |
| Vibrato programs | 85 |
| Filter programs | 64 |
| Pulse programs | 64 |
| Tempo programs | 48 |
| Track length (default) | 255 bytes |
| Track length (rem_trkl=0) | $07FF bytes |
| Sequence length max | 128 lines |
| Dump sequence byte limit | 256 bytes |
| Waveform/note table entries | 256 each (W and F parallel arrays) |

---

## 20. CSDb PDF Manual

**Source: https://csdb.dk/release/?id=153760**

A PDF user manual (SDI 2.1.7) was released on CSDb 2017-02-19 by Psylicium.
The `sdi_217_manual.txt` in docs/src/ is derived from that manual (by Henrik
Mortensen). It clarifies some points that the original docs.txt is ambiguous on.

---

## Leads to Follow

1. **OPEN: Exact dump byte-stream format.** The docs show high-level examples of dumped sequences but do not give a complete byte-stream grammar. The actual grammar is embedded in the editor's dump routine (on `sdi217_editor.d64` or `sdi217_seqsrc.d64` — likely in the editor binary `SDI V2.1 [SHAPE]`). Extracting + reading the dump routine from `sdi217_editor.d64` would give the authoritative byte grammar. Alternative: dump a known SDI file from HVSC and reverse the byte stream using the player's decode logic in `SRC_SDI21-N50.asm` lines 857–1100.

2. **OPEN: rem_* flag fingerprinting for HVSC tunes.** HVSC SDI tunes are PSID files assembled from the player + dump. The rem_* flags are baked in at assembly time. To extract a tune, we need to probe which optional routines are present by fingerprinting the assembled player binary (similar to `pipelines/future_composer/engine_fingerprint.py` for Future Composer). This is the key prerequisite for a factory-style extraction pipeline.

3. **OPEN: Column 4 (conductor channel) filter interactions.** The filter "layer" system (ch4 `$21–$3F` force filter program, `$71–$7F` force output, `$20 ON/OFF` in ch1–3) interacts with the filter state machine in a way not fully described by the docs. The `FILTENA` / `FILTCH` / `SETFI` state in the player source needs tracing.

4. **OPEN: Exact per-frame write ORDER (cycle-level).** The source shows the logical order but the assembler's conditional inclusion of rem_* blocks changes which code is actually present. Need siddump `--writelog` on a real HVSC SDI tune to observe the actual write sequence.

5. **OPEN: D64 editor source — dump routine.** The `sdi217_editor.d64` and `sdi217_seqsrc.d64` disks contain the editor binary and PETSCII source respectively. The dump routine (which generates the .SEQ output) is in the editor. Extracting + decoding the PETSCII source files beyond the two player sources (N50 and SPD50) would give the dump byte-grammar and potentially other player variants.

6. **OPEN: Version variants in HVSC.** HVSC contains SDI tunes from multiple eras (1992–2014). Earlier versions may have different player structure. The `$FC` drum command was supported in 1997–1999 versions but removed in v2.x. Need to check whether HVSC has older-engine SDI files.

7. **OPEN: `$20 ON/OFF` filter command** (rem_f20). The COMFX handler at `SRC_SDI21-N50.asm` ~line 986 toggles `FILTENA` per-channel. Interaction with the init-time `FS` filter-force mechanism needs clarification.

8. **Multispeed detection:** The speed player (`S.SDI21-SPD50`) has `$1009` as a third entry point. HVSC PSID `speed` field (non-zero = multispeed) would identify multispeed SDI tunes. The `spdchan` bitmask and `speed` value are baked into the assembled binary — recoverable by reading bytes at known offsets relative to the player base.
