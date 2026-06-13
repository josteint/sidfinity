# SID Duzz'It 2.1.7 — Manual Summary (Psylicium PDF)

<!-- PROVENANCE
source_url: http://csdb.dk/getinternalfile.php/155415/sdi_217_manual.pdf
mirror_url: https://files.psylicium.dk/sdi_217_manual.pdf
fetched_via: curl + pdftotext (41-page PDF, image pages but has text layer)
fetch_date: 2026-06-13
author: Henrik Mortensen (Psylicium), based on official SDI 2.1.6 docs + 2.1.7 corrections
content_date: February 2017 (SDI 2.1.7 revision 1; 19 Feb 2017)
reliability: HIGH — official-quality community manual; author is a power-user not a developer, but
             corrections are based on real usage + the official bundled docs from 2.1.6.
             Player source (sdi_zip/player_n50.asm) cross-checked for accuracy.
-->

## Background

SDI is a music tracker for the C64/C128, built on ideas from:
- JCH/Vibrants editor
- Olav Morkrid/Panoramic "Digitalizer" editor
- Geir Tjelta/Shape/Moz(ic)art SID Systems

The player is ~$0900 bytes + enabled effects. All parameters are hexadecimal.
Two player variants: `SDI21-N50` (singlespeed, fires once per VBI) and
`SDI21-SPD50` (multispeed, CIA-timed; PAL raster = 312/speed, NTSC = 262/speed).

---

## Player API (entry points at load address $1000)

```
ldx #00-$1f
jmp $1000       ; INIT — init subtune X

jmp $1003       ; PLAY — main play call (updates tracks, sequences, sounds)

lda #$00-$7f
jmp $1006       ; FADEOUT — start fadeout (negative = fade down)

jmp $1009       ; SPEEDPLAY — sound-only update (for multispeed extra calls)
```

Zero-page usage: `MZERO = $FE / $FF` (configurable via `mzero` flag).
SID base: `sid = $D400` (configurable; $D5C0 also works, C128 only $D400-$D500).

---

## Instrument (Sound) Parameters

Each instrument has 11 fields in the Sound Setup table:

| Field | Offset | Description |
|-------|--------|-------------|
| WAVEFORM | 0 | Pointer into waveform program table (see below) |
| ATTACK/DECAY | 1 | AD nibbles ($D405-style) |
| SUSTA/RELEASE | 2 | SR nibbles |
| GATE TIMEOUT | 3 | Hard/soft restart + gate delay |
| VIBRATO | 4 | Pointer into vibrato program table (00 = none, $01-$55) |
| PULSE | 5 | Pointer into pulse program table |
| FILTER | 6 | Pointer into filter program table |
| BAND/RESONANCE | 7 | Filter band+resonance ($D417-style); $00 = no filter |
| DETUNE HI | 8 | High-freq detune ($00=off, $01-$7F up, $80-$FF down) |
| DETUNE LO | 9 | Low-freq detune ($00=off, $01-$7F up, $80-$FF down) |

**Instrument count:** $00-$1F (32 "normal" instruments).
Instruments $20-$2F (16 more) exist but are accessible **only through the arpeggio program**, not
directly in the sequencer. Total 48 instruments.

### Gate Timeout (GATE TIMEOUT field)

Controls hard/soft restart behaviour:

| Value range | Behaviour |
|-------------|-----------|
| $00,$20,$40,$60,$80,$A0,$C0,$E0 | No timeout (gate-off never auto-sets) |
| $01-$1F | Normal hard restart + gate timeout |
| $21-$3F | Hard restart 2 + gate timeout |
| $41-$5F | Hard restart 3 + gate timeout |
| $61-$7F | Hard restart 4 + gate timeout |
| $81-$9F | Soft restart 1 + gate timeout |
| $A1-$BF | Soft restart 2 + gate timeout |
| $C1-$DF | Soft restart 3 + gate timeout |
| $E1-$FF | Soft restart 4 + gate timeout |

### Pulse program pointer (instrument field)

| Value | Meaning |
|-------|---------|
| $00 | No pulse |
| $01-$40 | Pulse program line (finite sweep) |
| $41-$80 | Pulse program with infinite sweep |
| $8x (x=1-F) | Value stored directly in SID Pulse High register |

### Filter program pointer (instrument field)

| Value | Meaning |
|-------|---------|
| $00 | No filter |
| $01-$40 | Filter program (finite sweep) |
| $41-$80 | Filter sweep mode 1 |
| $81-$C0 | Filter sweep infinite mode 2 |
| $C1-$FF | Filter sweep mode 3 |

---

## Program Tables

### Waveform Program Table (SHIFT+W in editor, addr $E000-$E100 in editor)

Each line has 3 columns:
- **C1**: program line position (index)
- **C2**: waveform byte OR command byte
- **C3**: note value OR command parameter

**Note values (C3):**
- `$00-$5E` — soft note, added to note+track transpose
- `$60-$7F` — soft note, subtracted from note+track transpose
- `$80-$DE` — fixed note, overrides note+track transpose

**Standard SID waveforms:**
| Value | Waveform |
|-------|----------|
| $10 | Triangle |
| $20 | Sawtooth |
| $40 | Pulse (requires pulse value) |
| $80 | Noise |
| $30 | Triangle+Sawtooth |
| $50 | Pulse+Triangle |
| $60 | Pulse+Sawtooth |
| $70 | Pulse+Sawtooth+Triangle |

Gate bit: add $01 for gate-on, $00 for gate-off. Sync bit = $02/$03.
Ring modulation = $04/$05.

**Arpeggio waveforms:** add $80 to above (e.g. sawtooth+arp = $A1, pulse+arp = $C1).

**Waveform commands (C2 = command, C3 = parameter):**

| Command | Name | Parameter | Description |
|---------|------|-----------|-------------|
| `$FF` | Jump | `xx` ($00-$FE) | Jump to program line xx |
| `$FE` | Delay | `xx` ($00-$FF) | Delay following waveform xx frames |
| `$FD` | ADSR | `AD SR` | Set ADSR ($FD sets gate-off after xx frames; $00/$80=no delay; $81-$FF same as $01-$7F but gate can't re-open) |
| `$FB` | Multipulse | `P2` | Switch between two pulse programs (P2=second pointer; `$0x yy`: x=0 start with P2, x=1 start with setup pointer; yy=switch speed) |
| `$FA` | Repeat | `xx` ($01-$FF) | Repeat the following `$FF` jump xx times; auto-falls-through after |
| `$F0-$F7` | Filter cutoff | — | Write lower 3 bits of $D415 (lowpass cutoff); yy unused |
| `$EE` | Pulse init | `lh` | Write low|high pulse to $D402/$D403 + player regs |
| `$ED` | Pulse subtract | `xx` | Subtract xx from current pulse |
| `$EC` | Pulse addition | `xx` | Add xx to current pulse |
| `$EB` | Pulse write | `lh` | Write low|high pulse to SID registers only |
| `$E2-$E7` | Noise trick | — | Write Ex to waveform register (metallic noise; x=2-7) |

---

### Vibrato Program Table (SHIFT+V, addr $E500-$E600 in editor)

4 columns per line:
- **C1**: table position
- **C2**: delay value / detune command / loop command
  - `$00` = detuning and continue
  - `$01-$FD` = delay value (wait N frames)
  - `$FE` = detuning and hold
  - `$FF` = infinite loop on vibrato
- **C3**: vibrato width
  - `$00-$7F` = going up first, then down
  - `$80-$FF` = going down first, then up
- **C4**: vibrato speed OR detune high byte
  - Values >$80 in C4 produce "Crazy Comet" loop effect

**Detuning syntax:** `$FE dl dh` (hold with detune) or `$00 dl dh` (detuning + continue).
`dl`/`dh` = low/high detune bytes. `$00-$7F dh` = finetune upwards; `$FF-$80 dh` = downwards.

Vibrato programs can be called from the FX column in the sequencer with `$21-$3F`.

---

### Pulse Program Table (SHIFT+P, addr $E200-$E300 in editor)

5 columns per line:

**Pulse sweep mode:**
- **C2**: PulseLow / PulseHigh starting value
- **C3**: PulseHigh sweeping (end) value
- **C4**: sweep speed
- **C5**: sweep mode/jump:
  - `$00,$40,$80,$C0` — sweep to end value, stop
  - `$0x-$3F` — sweep to end, cut back to C2 value (x = program line to cut to)
  - `$4x-$7F` — if x points to same line: continuous between C3 values; if different: sweep to C3 then to new line
  - `$8x-$BF` — reversed sweep, cut to C2
  - `$Cx-$FF` — reversed continuous sweep

**Pulse hold mode:** When C3=0, C4 is used as a delay counter decremented to zero, then jumps per C5.

---

### Filter Program Table (SHIFT+F, addr $E600-$E700 in editor)

Same structure as pulse program with two differences:
1. C2 columns have high/low byte **swapped** (filter starts with cutoff-high).
2. No pulse-hold routine; instead has a **filter frame routine**:
   - When C3=0: C2=filter cutoff high ($D416), C4=band+resonance, C5=delay+jump
   - `$8x` C5 = 1-frame delay before jump; `$0x` C5 = 2-frame delay

---

### Arpeggio Program Table (SHIFT+A, addr $E300-$E500 in editor)

4 columns: C1=position, C2=unused, C3=data location (jump table pointer), C4=speed+instrument.

**Jump table structure (recommended):** First entries are "shortcuts":
- `C3` = address of actual chord data
- `C4` upper nibble = speed (`$0,$4,$8,$C` valid), lower nibble = instrument

**Chord data lines:**
- `$00` = root note (no transpose)
- `$03` = transpose up 3 semitones
- `$87` = transpose up 7 semitones + loop flag (add $80)

All waveforms used in arpeggio must have $80 added (e.g. sawtooth+arp = $A1).
Arpeggio programs $40-$6F are referenced from sequencer FX column.

---

### Tempo Program Table (SHIFT+T, addr $ED40-$ED70 in editor)

3 columns:
- **C1**: program line & number
- **C2**: tempo value (`$01-$7F` = tempo; `$81-$FF` = loop at value&$7F)
- **C3**: program lookup pointer

Press RETURN on lookup pointer to set as default tempo.
Tempo programs $40-$60 are called from channel 4's FX column.

---

### Initial Volume Table (SHIFT+I, addr $EDC0-$EE00 in editor)

Per-subtune settings. 3 columns:
- **C1**: song number
- **C2**: `[fadein nibble][initial volume nibble]`
  - High nibble ($1-$F) = fade-in speed (1=fastest; 0=no fadein)
  - Low nibble ($0-$F) = starting volume (0=silent, F=max)
- **C3**: `[filter force nibble][filter speed nibble]`
  - High nibble: force filter on channels (bitmask: 1=ch1, 2=ch2, 4=ch3; 3=ch1+2, etc.)
  - Low nibble: filter speed delay ($0=fastest, $F=slowest)

---

## Sequencer Model

### Structure

- **4 channels**: ch1-3 = audio, ch4 = master transpose/tempo/filter control
- **Up to 128 sequences** ($00-$7F), each sequence up to $FF bytes
- **32 subtunes** (songs), each with independent order lists per channel
- Each channel has an independent **order list** (track) with entries of form:
  `[transpose byte] [sequence number]`
- **Order list transpose values:**
  - `$80-$9F` = transpose down
  - `$A0` = no transpose
  - `$A1-$BF` = transpose up
- Order list terminates with `J000` (jump = 2-byte loop target) or `STOP`

### Sequencer FX — Channels 1-3

Each sequence line has 2 fields: FX and NOTE.

| FX value | Note | Meaning |
|----------|------|---------|
| `$00-$1F` | --- | Set instrument N, no note |
| `$00-$1F` | C-0..A#7 | Set instrument N + note |
| `$00-$1F` | tie | Add instrument to waveform + tie note |
| `$21-$3F` | C-0..A#7 | Glide: value $2E = glide speed $0E |
| `$21-$3F` | --- | Vibrato program ($21=$01, $22=$02…$3F=$1F) |
| `$40-$6F` | --- | Set arpeggio ($40-$6F = arpeggio 0-$2F), no note |
| `$40-$6F` | C-0..A#7 | Set arpeggio + note |
| `$70-$7F` | --- | Set release (value = $7x → release = $x) |
| `$70-$7F` | C-0..A#7 | Set sustain ($7x → sustain=$x) + note |
| `$70` | C-0..A#7 | Restore original ADSR + note |
| `$7A` | tie | Set attack $A + tie note |
| `--` | C-0..A#7 | Note (with current sustain if set) |
| `--` | tie | Tie note |
| `--` | GAT | Gate on (restarts attack+decay+sustain) |
| `--` | (gate sym) | Gate off (release cycle) |

**Tie notes** don't restart programs; they inherit running state.
**Attack notes** (SHIFT+note) restart all programs without resetting waveform.

### Sequencer FX — Channel 4 (transpose/tempo/filter)

| FX value | Note | Meaning |
|----------|------|---------|
| `$00-$1F` | --- | Set tempo to N |
| `$00-$1F` | C-0..A#7 | Set tempo to N + transpose |
| `--` | note | Set transpose only |
| `$40-$60` | --- | Look up tempo program N-$40 |
| `$40-$60` | GAT | Tempo program + transpose 0 |
| `$21-$3F` | --- | Force filter program $01-$1F |
| `$61-$67` | --- | Force filter band $01-$07 |
| `$70` | --- | Filter control back to main channel |
| `$71-$7F` | --- | Force filter output on specific channel |

Notes: `00` as tempo stops music. Keep channel 4 transpose between GAT and C-2 to avoid crashes.
Channel 4 filter works as a layer over ch1-3; ch1-3 must have an active filter instrument first.

---

## Player Flags (Compile-Time Feature Switches)

All flags in the Turbo Assembler player source. `1 = disable feature`, `0 = enable`.
Enabling features costs raster time and memory.

| Flag | Default | Description |
|------|---------|-------------|
| `rem_4ch` | 1 | Ignore 4th channel (set 0 if using ch4) |
| `rem_det` | 0 | Ignore detuning |
| `rem_gout` | 0 | Ignore gate timeout |
| `rem_1wf` | 0 | Ignore 1st byte of waveform program (saves raster; may change sound) |
| `rem_wfd` | 1 | Ignore waveform delay ($FE command) |
| `rem_adsr` | 1 | Ignore ADSR command ($FD) |
| `rem_mp` | 1 | Ignore multipulse ($FB) |
| `rem_wfr` | 1 | Ignore waveform repeat ($FA) |
| `rem_wf0` | 1 | Ignore $F0-$F7 $D415 filter command |
| `rem_puw` | 1 | Ignore waveform pulse commands ($EB-$EE) |
| `rem_pu` | 1 | Ignore pulse routine |
| `rem_we2` | 1 | Ignore $E2-$E7 noise trick |
| `rem_arp` | 0 | Ignore arpeggio routine |
| `rek_fi` | 0 | Ignore filter routine |
| `rem_fspd` | 0 | Ignore filter speed |
| `rem_glid` | 0 | Ignore glide routine |
| `rem_vib` | 0 | Ignore vibrato routine |
| `rem_cc` | 1 | Ignore Crazy Comet vibrato |
| `rem_fad` | 1 | Ignore fadeout routine |
| `rem_gat` | 1 | Ignore GAT/FLG command |
| `rem_f20` | 1 | Ignore sequencer command `$20 xx` (filter toggle command) |
| `rem_wfo` | 1 | Ignore waveform ORA command in sequencer |
| `rem_voff` | 1 | Ignore voice on/off toggle |
| `rem_trkl` | 1 | Max $FF bytes per track (set 0 for $07FF tracks) |
| `rem_tp` | 0 | Ignore tempo programs (insert single tempo in offset `s`) |
| `rem_opt` | 0 | Optional speed channels (for multispeed with fewer than 3 active channels) |

**Multispeed flags:**
- `spdchan` = `%00000111` — bitmask of active speed channels (1=ch1, 2=ch2, 4=ch3)
- `speed` = 4 — number of speeds (2-15); used by music displayer, not the player
- `system` = 1 — 1=PAL, 0=NTSC

---

## Memory Overview (Editor RAM Layout)

| Address range | Content |
|---------------|---------|
| $0100-$017F | Stack |
| $0180-$0200 | Sequence lengths |
| $02A7-$0300 | Data tables |
| $0340-$0400 | Sprites |
| $0400-$07E8 | Screen |
| $0800-$2EE0 | Editor part 1 |
| $2F00-$3000 | Data buffer |
| $3000-$3800 | Track 1 |
| $3800-$4000 | Track 2 |
| $4000-$4800 | Track 3 |
| $4800-$5000 | Track 4 |
| $5000-$D000 | Sequences ($8000 bytes = 128 sequences × 256 bytes max) |
| $D000-$D810 | Directory memory (max 128 SDI files) |
| $D810-$E000 | Editor part 2 |
| $E000-$E100 | Waveform program table |
| $E100-$E200 | Waveform program note table |
| $E200-$E300 | Pulse program table |
| $E300-$E400 | Arpeggio data |
| $E400-$E500 | Arpeggio program table |
| $E500-$E600 | Vibrato program table |
| $E600-$E700 | Filter program table |
| $E700-$E8E0 | Sound setup (instruments): |
| $E700-$E730 | — Waveform program pointer (48 entries) |
| $E730-$E760 | — Attack/Decay |
| $E760-$E790 | — Sustain/Release |
| $E790-$E7C0 | — Gate timeout |
| $E7C0-$E7F0 | — Vibrato program pointer |
| $E7F0-$E820 | — Pulse program pointer |
| $E820-$E850 | — Filter program pointer |
| $E850-$E880 | — Filter band/resonance |
| $E880-$E8B0 | — Detune high |
| $E8B0-$E8E0 | — Detune low |
| $E8E0-$E970 | Future expansion |
| $E970-$E980 | File info (speed calls / speed channels) |
| $E980-$EA00 | Tempo data |
| $EA00-$ED00 | Sound names |
| $ED00-$ED20 | Default tempo lookup per subtune |
| $ED20-$ED40 | Channels ON lookup per subtune |
| $ED40-$ED70 | Tempo program table |
| $ED80-$EDC0 | Marked channel positions |
| $EDC0-$EDE0 | INVOL volume setup |
| $EDE0-$EE00 | INVOL filter setup |
| $EE00-$EEC0 | Note frequency table (PAL) |
| $EEC0-$FFE6 | Player/Editor part 3 |

---

## Capacity Summary

From SourceForge project description:
- **32 subtunes**, 128 sequences
- **32 instruments** ($00-$1F) directly usable in sequencer; **48 total** (extra 16 via arpeggio only)
- **85 vibrato programs**, 64 filter programs, 64 pulse programs, 48 tempo programs
- **11-bit filter** possible through the waveform table ($F0-$F7 command)
- Sequence max size: 256 bytes (hard limit; larger = dump stall)

---

## Note Encoding (Fixed Note Table, from manual)

Two representations for note bytes:
- **Fixed note table** (C3 values $80-$DE): C-0=$80 … A#7=$DE (8 octaves × 12 = 95 notes + $DF=B-7)
- **Soft note table up** (relative, C-0 as base): C-0=$00 … B-7=$5F
- **Soft note table down** (relative, C-3 as base): E-0=$60, F-0=$61 … B-2=$7F

These map linearly into FREQHI/FREQLO (96 entries, PAL-tuned), indexed 0-95.

---

## Dumped File Format (Music Data)

When a tune is "dumped" via the editor, the output is a Turbo Assembler sequential file.
The player source is then loaded, the dumped data appended after the `RTS`, and assembled.

From the player source (`player_n50.asm`), the runtime data structures per-channel are:

**Per-channel voice state (7 bytes each, 3 channels = 21 bytes stride):**
```
CHANON     voice enable bitmask
CHANOFF    inverse
TRKLO      track pointer low byte
TRKHI      track pointer high byte
TDELAY     track delay counter
TRACKY     track position byte (or 16-bit TRACKY/TRACKHI)
TRACKHI    (only for rem_trkl=0 mode)
```

**Per-channel runtime state (another 7-byte stride × channels):**
```
TRANSP     current track transpose
DUR        note duration
DURATION   duration counter
SEQP       sequence byte pointer
SOUND2     current instrument number
NOTE2      current note value
```

Additional per-channel state arrays (7×channels each):
`RELEASE, SEQSUST, SEQBYTE, FILTRE, GLIDADD2, WF.ORA, WF.ORA2`
`ARPNUM2, ARPLE, SRCO, SOUND, NOTE, GATE, GATEDEC`
`ARPNUM, ATTACK, SUSTAIN, GLIDADD, GLIDTO, ADDLO, ADDHI`
`ARPDE, VIBLE, VIBWID, VIBDIR, VIBDEC`
`PULSCO, PULSEOR, PULSDEL, PULSLE, PULSLE2, PULSDEC, PULSDEC2`
`PULSLO, PULSLO2, PULSHI, PULSHI2, PULSHLD`
`WF, WFP, WF.DEL, WF.REPET, DETUNLO, DETUNHI`

**Per-subtune tables (1 byte each, indexed by subtune 0-31):**
`S` = default tempo for subtune
`C` = CHANON bitmask (voices enabled)
`FV` = volume+fadein byte ([fadein nibble][vol nibble])
`FS` = filter channels+speed byte
`TP` = track pointer base index for subtune
`TL/TH` = track low/high pointer pairs (for each channel of each subtune)

**Sequence data** follows after all headers.
**Instrument data tables** (`W`=waveform, `AD`=attack/decay, `SR`=sustain/release, `GT`=gate-timeout,
`VB`=vibrato, `PU`=pulse, `FI`=filter, `DB`=band/resonance, `DT.H`/`DT.L`=detune) indexed by instrument.

**Z-page data** labels in player source:
`Z3` = gate-timeout table; `Z5` = arpeggio data; `Z7` = filter band; `Z8/Z9` = detune tables.

---

## Known Bugs (from manual)

1. Filling a `$7F`-length sequence completely with tie notes can produce a dump >256 bytes → dump stalls. Solution: split the sequence.

---

## File Format Notes

- SDI save files: filename starts with `↑` (C64 up-arrow); packed with bytepacker covering $3000-$D000 + $E000-$EE00. Empty file ≈ 5 blocks; full tune ≈ 60 blocks.
- Dumped files: filename starts with ` ` (space); Turbo Assembler SEQ files; range 5-120 blocks.
- Load menu only shows SDI files (tagged with `↑`). Max 128 files per directory displayed.
- Format difference between V1.x and V2.x: V1.8 and V2.17 are reported incompatible in VICE.

---

## OPEN items from this manual (RE needs)

- Exact binary byte layout of the dumped music data (label → offset mapping) requires assembling the player source against a known tune.
- The `$20 xx` sequencer command (channel 4 filter toggle, `rem_f20` flag) is not fully documented in the manual.
- The `rem_wfo` (waveform ORA) sequencer command is mentioned but not explained in the manual.
- Arpeggio `C4` speed encoding: values `$0,$4,$8,$C` valid — exact speed meaning not in manual.
- Gate-timeout "hard restart" variants 1-4 and "soft restart" variants 1-4 — exact behaviour differences not documented.
- NTSC frequency table separate from PAL (noted in player source but not in manual).
