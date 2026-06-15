---
source_url: D64 disk image extracted from Reflextracker_V1.1.zip (c64.rulez.org)
fetched_via: curl + Python D64 parser
fetch_date: 2026-06-15
author: reverse-engineered from binary
content_date: 1995-1996 (disk dated 1996-03-29)
reliability: primary (direct binary analysis)
---

# Reflextracker V1.1 — Format Analysis

## Source material

Downloaded: `Reflextracker_V1.1.zip` (200KB)
Contains two D64 disk images:
- `Reflextracker V1.1 [Reflex + The Obsessed Maniacs] (side 1).d64`
- `Reflextracker V1.1 [Reflex + The Obsessed Maniacs] (side 2).d64`

## Disk contents

### Side 1 (REFLEXTRACKER)
| Filename | Type | Size | Load addr | Purpose |
|----------|------|------|-----------|---------|
| REFLEXTRACK.V1.1 | PRG | 43 blk | $0801 | Main tracker executable (BASIC loader) |
| RFXT PLAYER V1.1 | PRG | 9 blk / 2034 bytes | $C000 | Standalone SID player |
| BESCHREIBUNG | PRG | 112 blk / 28077 bytes | $0801 | German documentation (BASIC program with embedded text) |
| SDRV.UPRT 4BHI | PRG | 1 blk | ? | Sample driver: userport 4-bit hi-nibble sampler |
| SDRV.UPRT 4BLO | PRG | 1 blk | ? | Sample driver: userport 4-bit lo-nibble sampler |
| SDRV.UPRT 8BIT | PRG | 1 blk | ? | Sample driver: userport 8-bit sampler |
| SDRV.UPRT AMIGA | PRG | 1 blk | ? | Sample driver: Amiga parallel cable sampler |
| SDRV.I/O1 4BHI | PRG | 1 blk | ? | Sample driver: I/O port 1, 4-bit hi |
| SDRV.I/O1 4BLO | PRG | 1 blk | ? | Sample driver: I/O port 1, 4-bit lo |
| SDRV.I/O1 8BIT | PRG | 1 blk | ? | Sample driver: I/O port 1, 8-bit |
| SDRV.I/O2 4BHI | PRG | 1 blk | ? | Sample driver: I/O port 2, 4-bit hi |
| SDRV.I/O2 4BLO | PRG | 1 blk | ? | Sample driver: I/O port 2, 4-bit lo |
| SDRV.I/O2 8BIT | PRG | 1 blk | ? | Sample driver: I/O port 2, 8-bit |
| SDRV.JOY1 2BHI | PRG | 1 blk | ? | Sample driver: joystick port 1, 2-bit hi |
| SDRV.JOY1 2BLO | PRG | 1 blk | ? | Sample driver: joystick port 1, 2-bit lo |
| SDRV.JOY1 4BIT | PRG | 1 blk | ? | Sample driver: joystick port 1, 4-bit |
| SDRV.JOY2 2BHI | PRG | 1 blk | ? | Same for joystick port 2 |
| SDRV.JOY2 2BLO | PRG | 1 blk | ? | Same |
| SDRV.JOY2 4BIT | PRG | 1 blk | ? | Same |
| SDRV.SIDWAVE | PRG | 1 blk | ? | SID chip waveform capture driver |
| MOD.ACCESS2/B | PRG | 116 blk | $4A1C | Module: Access Denied 2 (side B) |
| MOD.ENDLOSCHOOR | PRG | 40 blk / 9910 bytes | $95FC | Module: Endless Choir example song |
| MOD.TRANCE202 | PRG | 175 blk / 28474 bytes | $1009 | Module: Trance 202 example song |

### Side 2 (SAMPLES)
54 sample files, all PRG. Names: ORGANIC BASS, SCHERBENKLIRREN, ONE !!, TWO !!, THREE!!, C-2 BASS, C-3 BASS, SUMBA-EH!, DRUM1, SCRATCH, STRING OCT.HIGH, ACD.BASSWAVE, ACD.BASS, RFX.PR.T.Y., C64 DRUMM, ROCK, PVCF/SAM/H, DRUMM MUELLTONNE, BOOTWAVE1, OL C3 VOICE, BASS1 C2, PANFLOETE1 C2, CHOOR 2 C3, ODYSSE CHOOR/H, BOOTWAVE2, RAVE-BASS1, RAVE-DRUMM1, NICHT NORMAL!, RAVE 3 LANG, RAVE4 LANG, SUPERDRUMMM, AU!-SCHREI, AUUUUHHHH!!!, ALARM/SCHIFF, E-GITARRE, SCRATCH, SCRATCHHH!, FLESCH KORKEN, WUM.!!!, EFFECT/OUTRUN, HUST SCOTCH, WAAUUU!, SUPER HE.!!, HE.!!!, HAE.!!!, HEH!!!, OKAY!!, WELCOME!MIESS, ONE TWO, HIT IT!!!, PUMPKINS WAVE, PUMPKINS GITARRE, PUMPKINS SCHREI, GOATHE!!!

---

## The RFXT PLAYER V1.1 binary

File: `RFXT_PLAYER_V1.1.prg` (2034 bytes, extracted from D64)
Load address: `$C000`

### Entry points

The player is a standard PSID-style 2-entry design:

```asm
$C000: JMP $C02C    ; Entry point 1: PLAY (IRQ handler)
$C003: JMP $C016    ; Entry point 2: INIT / START / STOP
```

### INIT routine ($C016)

Checks state flag $D7: if positive, calls sample processing ($C219); if $D7=0, falls through.

Main INIT at $C02C:
```asm
A9 81     LDA #$81   ; set state = active
85 D7     STA $D7
A9 00     LDA #$00
A2 18     LDX #$18   ; 25 SID registers
9D 00 D4  STA $D400,X ; clear all SID ($D400-$D418)
CA 10 FA  DEX; BPL loop
A2 7F     LDX #$7F
8E 0D DD  STX $DD0D   ; disable CIA2 NMI
A2 93     LDX #$93
8E 04 DD  STX $DD04   ; CIA2 Timer A lo = $93
8D 05 DD  STA $DD05   ; CIA2 Timer A hi = $00
A2 FF     LDX #$FF
8E 02 D4  STX $D402   ; Voice 1 PW lo = $FF
8E 03 D4  STX $D403   ; Voice 1 PW hi = $FF
8E 06 D4  STX $D406   ; Voice 2 PW lo = $FF (!)
A2 41     LDX #$41    ; pulse + gate
8E 04 D4  STX $D404   ; Voice 1 control = pulse+gate
8E 0E DD  STX $DD0E   ; CIA2 Timer A: start
RTS
```

**Dispatch mechanism:** CIA2 Timer A fires at rate ~$0093 cycles (147 cycles), triggering the playback IRQ. This is a **very fast CIA timer** — much faster than the standard 50Hz VBI. This drives 4-bit sample playback through the SID pulse width.

### Sample playback engine ($C05D)

The core loop plays back 4-bit digi samples using SID pulse width modulation:

```asm
; Voice 1 sample playback:
$C05D: 69 ??   ADC #step     ; step = SMC operand (playback speed)
$C05F: 8D 5C C0 STA $C05C   ; SMC: write back (step accumulator)
$C062: 90 0A   BCC no_carry
; Page carry: flip direction bit
$C064: AD 8F C0 LDA $C08F   ; load direction byte
$C067: C9 C7   CMP #$C7     ; page boundary check
$C069: 49 01   EOR #$01     ; toggle forward/backward
$C06B: 8D 8F C0 STA $C08F
; Update 16-bit sample pointer $D0/$D1
$C06E: A5 D0   LDA $D0      ; lo byte
$C070: 69 ??   ADC #step_lo  ; SMC
$C072: 85 D0   STA $D0
$C074: AA      TAX
$C075: A5 D1   LDA $D1      ; hi byte
$C077: 90 07   BCC no_carry2
$C079: 69 ??   ADC #0       ; SMC (propagate carry)
$C07B: 85 D1   STA $D1
$C07D: 8D 8C C0 STA $C08C  ; SMC: update page in LDY instruction
; Check if pointer reached end of sample
$C080: C9 ??   CMP #end_page ; SMC: end page
$C082: 90 06   BCC continue
$C084: D0 0D   BNE next_pattern
$C086: E0 ??   CPX #end_lo  ; SMC: end lo byte
$C088: B0 09   BCS next_pattern
; Fetch sample byte and step size
$C08A: BC 00 10 LDY $1000,X  ; load sample BYTE from $1000+X
$C08D: BE 00 EE LDX $EE00,X  ; load step from step table at $EE00
$C090: JMP $C109             ; output to SID
```

Voice 2 has a parallel path at $C0A0+ using $D2/$D3 pointers.

### SID output ($C1A0+)

The sample byte (in Y register) and pitch table lookup produce a CIA-timed pulse to the SID:

```asm
$C1A0: 18       CLC
$C1A1: BD A0 C5 LDA $C5A0,X  ; step table lookup
$C1A4: BE 00 10 LDX $1000,??  ; (?)
$C1A7: BC 00 EE LDY $EE00,??  ; (?)
$C1A9: 18       CLC
$C1AA: 79 A0 C5 ADC $C5A0,Y  ; add step
$C1AD: 4A       LSR           ; /2
$C1AE: AE 0D DD LDX $DD0D    ; read CIA2 ICR (acknowledge)
$C1B1: F0 FB   BEQ $C1AE     ; wait for timer flag
$C1B3: 8D 18 D4 STA $D418    ; write to SID $D418 (master vol / digi output)
```

**Key finding:** Sample bytes are output to **$D418 (master volume register)**. This is the standard C64 "digidigi" technique — 4-bit samples written to the volume register at high frequency produce audio. NOT pulse width modulation as initially assumed.

### Player tables ($C560-$C7FF)

```
$C560-$C56B: 12 freq lo values (one octave, C64 SID note table)
$C570-$C57B: 12 freq hi values
$C580-$C58B: 12 freq extension values (for higher octaves)
$C590-$C59F: 0x00-0x0F (16-entry index table)
$C5A0-$C5EF: Playback speed/step tables (48 bytes — 3 sub-tables of 16)
              Sub-table 1: $C5A6-$C5AF (octave-like groups)
              Sub-table 2: $C5B6-$C5BF
              Sub-table 3: $C5C6-$C5CF
$C5D0-$C5DF: 08 08 08 09 09 09 01 C1 81 41 01 C1 81 41 01 C1 (direction/phase)
$C5E0-$C5EF: 04 04 04 03 03 03 03 02 02 02 02 01 01 01 00 00 (volume envelope?)
$C5F0-$C7FF: 512-byte table: ramp 0x00→0x0F repeated (linear nibble table)
             Pattern: each nibble value 0x0-0xF repeated 16 times
             (Used for 4-bit → volume mapping? Or pitch stepping?)
```

### Zero-page usage

| ZP addr | Usage |
|---------|-------|
| $D0/$D1 | Voice 1: current 16-bit sample byte pointer |
| $D2/$D3 | Voice 2: current 16-bit sample byte pointer |
| $D4 | Pattern/track position counter |
| $D5 | Play rate hi |
| $D6 | Volume |
| $D7 | State flags: $81 = active, $00 = stopped |
| $D8 | Voice 1: current pattern number |
| $D9 | Voice 1: current note/row |
| $DB | Pattern command byte |
| $DC/$DD | Sample table pointer (indirect) |
| $DE/$DF | Sample table pointer 2 |
| $E0 | Loop counter |
| $E7 | Effect flags |
| $E8 | Voice 1 active flag |
| $E9 | Voice 2 loop counter |
| $EA/$EB | Voice 2: pattern data pointer (indirect-Y) |
| $EC/$ED | Voice 1: pattern data pointer (indirect-Y) |
| $E5 | Another indirect pointer base |
| $F0 | Voice 2 active flag |
| $F1 | Voice 1 note trigger flag |

---

## MOD File Format ("RFX1 Module")

### Module file layout in C64 memory

A Reflextracker module occupies a contiguous region of C64 RAM:

```
$1009 or variable load addr:
  [4 bytes] Magic "RFX1"
  [N bytes] 4-bit packed audio sample data
             (2 samples per byte, hi nibble first)

$BA00:
  [32 bytes] Sample page table: hi-byte of page for each of 32 samples
             (0x00 = sample slot empty)

$BA20:
  [32 bytes] Sample end-limit table: per-sample boundary byte

$BA38-$BA57:
  [32 bytes] Dashes "---..." separator

$BA58:
  "REFLEXTRACKER 0 MODULE (UNPKD)CODE BY ZORC/REFLEX AND KB/T.O.M"
  This is the module identification header (ASCII).
  "UNPKD" indicates this is the UNPACKED format (packed = compressed variant exists).

$BAB0+:
  Sample name strings in PETSCII (0x01=A, 0x02=B, ... 0x1A=Z, 0x20=space)
  Example: CHOOR 1, ACCORD1, ACCORD2, etc.

$Bxxx:
  Track table (pattern ordering for both voices)
  Pattern data (rows with note + sample + direction + speed + volume)
```

**Important:** The load address of the module varies per song. TRANCE202 loads at $1009 (sample data fills $1009-$7F43). ENDLOSCHOOR loads at $95FC-$BCB2. ACCESS2/B loads at $4A1C-$BC1A. The track/pattern data at $BA00+ is ALWAYS at those fixed addresses regardless of where sample data loads.

### Pattern entry format (inferred from player code)

Each pattern entry (one "row") for one voice contains at minimum:
- Note / pitch value
- Sample number (instrument index 0-31)
- Direction (D: forward=P, backward=Q from docs)
- Speed (S: P=slowest to F=fastest, recommended W=normal)
- Volume (V: P=max to S=min, 4 levels)

From the docs:
```
NR  SND IS DSV   <- column headers
PP  ..M MM ..P   <- example row: pattern PP, sample M, inst M, dir .., vol P
```

Special values:
- `MM` (0x4D4D?) = mute/silence this voice
- `RP` = repeat/loop: jump back to start of track table
- `ED` (end) = stop player
- `K` = kill: sample stops playing
- Shift+pattern_num = open pattern for editing

### Track table format

Two parallel voice columns (Voice 1, Voice 2). Each row has pattern numbers for both voices. `MM` = voice muted for that row. When player reaches end of track, `RP` marker causes loop back to row 0.

Max patterns: hex $1F = 31 patterns per song (from docs: "maximal bis HEX TF").

Actually from docs: "ES KOENNEN MAXIMAL BIS HEX TF H.WYI PATTERN EDITIERT WERDEN" — appears garbled PETSCII. Standard trackers support ~128 patterns, so likely 16 or 32.

Each pattern is **16 rows long** (from docs: "EIN PATTERN IST HEX QF LANG" = hex $0F + 1 = 16 rows).

---

## Tracker features (from BESCHREIBUNG documentation)

### Editor modes

1. **Track editor**: Enter pattern numbers for Voice 1 and Voice 2, row by row
2. **Pattern editor**: Edit 16-row patterns with note/sample/dir/speed/volume per row
3. **Sample editor**: Manage sample table, set start/end addresses, preview

### Edit modes (F5 key cycles through)

- **Mode 1 (blue border)**: Notes typed go into pattern AND play immediately; song pauses at note entry
- **Mode 2 (light blue border)**: Notes go into pattern but sample doesn't play; can edit live
- **Mode 3 (black border = "keyboard mode")**: Notes play but are NOT entered into pattern (test/preview only)

### Sample editor operations

- **Set Name**: rename sample
- **Set Start/Set End**: change sample boundaries (trim)
- **Delete**: erase sample
- **Copy**: duplicate sample data to another slot
- **Load**: load sample from disk (D key = directory listing)
- **Save**: save sample to disk
- **Upsample**: halve sample length (one octave higher, some quality loss)
- **Downsample**: double sample length (one octave lower; sample plays from C-1)
- **Change NBS** (nibble swap): swaps hi/lo nibbles in sample data (fixes scratchy samples)
- **Mix**: mix two samples together (each at 50% level; mixed at C-3 sample rate)
- **Echo**: add hall/reverb effect

### Sample drivers (SDRV.* files)

The tracker supports external sampling hardware via loadable drivers:
- Userport (UPRT): 4-bit hi-nibble, 4-bit lo-nibble, 8-bit
- Module port (I/O1, I/O2): 4-bit hi, 4-bit lo, 8-bit
- Joystick ports (JOY1, JOY2): 2-bit hi, 2-bit lo, 4-bit
- **SDRV.SIDWAVE**: converts SID waveforms to samples (using $D4xx registers)

The SIDWAVE driver parameters:
- WFORM/PULSE: waveform type (1-7 = triangle/sawtooth/pulse/noise) + 12-bit pulse width
- FREQUENCY: SID frequency register value for the target pitch

### Keyboard mapping (note input)

```
Q W E R T Y U I O P  (main row)
A S D F G H J K L Z  (home row)
```
Musical mapping: A=C, W=C#, S=D, E=D#, D=E, F=F, T=F#, G=G, Y=G#, H=A, U=A#, J=B, K=C (next octave)
Numbers 1-4 select octave.

### Playback commands

- **F1**: Play from cursor position
- **F2**: Optimal play (...)
- **F3**: Stop
- **F4**: Continue play
- **F5**: Cycle edit mode
- **F7/F8**: (track editor) Load/Save track table
- **J/L keys**: Load/Save from RAM buffer
- **R key**: Insert repeat (RP) byte
- **M key**: Insert mute (MM) for voice
- **. key**: Insert END marker

### Disk menu

- Load Song / Save Song
- Directory
- Clear All (erase all RAM data)
- Load Driver (load sampler driver)

---

## QuadSID / multi-chip support

The tracker supports composing for up to **10 channels** using multiple SID chips ("QuadSID"). However:
- Songs with >3 channels cannot be directly exported as standard .SID
- They "can only be recorded as a MIDI stream" (PVCF, Lemon64 forum)
- Converting to 3-channel: requires manual remixing using "DMC and the changed Polonus digieditor"

This explains why HVSC Reflextracker entries (137 tunes) all appear as standard 2-voice digi SIDs.

---

## Player dispatch timing

The player uses **CIA2 Timer A** for sample output timing:
- Timer A loaded with $0093 (147 cycles)
- Timer A controls sample byte output rate
- VERY high sample rate — this is how digi quality is achieved
- The raster interrupt syncs with SID register writes

The standalone player's INIT starts the CIA timer. The PSID wrapper must implement the same timing. HVSC SIDs using Reflextracker will have the player embedded at $C000 with their music data.

---

## Module identification string

All module files contain the string at $BA58:
```
REFLEXTRACKER 0 MODULE (UNPKD)CODE BY ZORC/REFLEX AND KB/T.O.M
```

The "0" after "REFLEXTRACKER" may be a version number. "UNPKD" = unpacked format. A packed format likely exists (Quiss wrote the sample pack code per the documentation).
