# GoatTracker V1.xx — Source Code Research

```
source_url:   https://cadaver.github.io/tools/goattrk.zip   (V1.53 current)
              https://cadaver.github.io/tools/goatold.zip   (V1.25 archive)
              local: deprecated/gt2_pipeline/GoatTracker_2.77/src/gsong.c (GT2 V1 importer)
              local: deprecated/gt2_pipeline/GoatTracker_2.65/src/betaconv.c (GT2 early-beta conv.)
fetched_via:  curl + local file read
fetch_date:   2026-06-29
author:       Lasse Öörni (Cadaver / Covert Bitops)
content_date: 2006-05-16 (V1.53, final release); 2004-03-30 (V1.25)
reliability:  primary — original author sources
```

## TL;DR

GoatTracker V1 ("GTS!" format) is a COMPLETELY different architecture from GT2.
The key structural differences:

| Dimension | GT V1 | GT V2 |
|---|---|---|
| File magic | `GTS!` / `GTI!` | `GTS5` / `GTI5` (latest) |
| Arpeggio | Per-pattern command (cmd 0, 3-note) | Removed; use wavetable instead |
| Wavetable | Per-instrument inline (embedded in .sng) | Global shared table (WTBL index) |
| Pulse table | Per-instrument params (start/speed/lo/hi) | Global shared table (PTBL index) |
| Filter table | Global, 64 entries × 4 bytes | Global shared table (FTBL) |
| Speed table | None (vibrato/porta speed = direct param) | 4th table (STBL) added in GT2 |
| Instruments | 31 max, per-instr wavetable | 63 max, table-pointer style |
| Patterns | 3 bytes/row (note+cmd+data packed) | 4 bytes/row (note+instr+cmd+data) |
| Max patterns | 208 | 208 (same) |
| Max orderlist | 254 entries | 254 entries (same) |
| Subtunes | Up to 32 | Up to 32 (same) |

---

## Sources Found Locally

### 1. GT2 importer of V1 format — `deprecated/gt2_pipeline/GoatTracker_2.77/src/gsong.c`

**Highest-value source.** This is a PRIMARY authoritative source: the code that
GT2 uses to load GTS! files and convert them to GT2 internal representation.
The conversion section begins at line 329 (`if (!memcmp(ident, "GTS!", 4))`).
Reading this code gives the exact byte layout of every V1 format section.

### 2. V1.53 player sources (downloaded from cadaver.github.io)

Saved to `pipelines/goattracker/docs/src/`:

- `v1_player1_v153.s` — Standard V1.5 playroutine (768 lines, full 6502 source)
- `v1_player2_v153.s` — Relocation info stub for game-music mode (14 lines)
- `v1_gmusic_v153.s` — Game-music playroutine with sound-FX and relocatemusic (868 lines)

Also in `tmp/goattracker_v1_research/`:
- `v1_player1_125.s` — V1.25 player (earlier, pre-filter-step version)
- `v1_player2_125.s` — V1.25 game player
- `v1_readme_153.txt` — V1.53 README (full format spec in section 6)
- `v1_readme_125.txt` — V1.25 README

---

## V1 Song File Format — GTS! (from readme + gsong.c importer)

### Header

```
Offset  Size    Description
+0      4       Identification string "GTS!"
+4      32      Song name (zero-padded)
+36     32      Author name (zero-padded)
+68     32      Copyright string (zero-padded)
+100    byte    Number of subtunes
```

### Orderlists

The orderlist structure repeats for channels 1,2,3 of each subtune.

```
Offset  Size    Description
+0      byte    Length n-1 of this channel's orderlist (one LESS than in GT2!)
+1      n       Orderlist data bytes:
                  $00-$CF ($00-207): pattern numbers
                  $D0-$DF ($D0-$DF): repeat commands (value - $CF = repeat count 1-16)
                  $E0-$EF: transpose down (value - $DF = 1..16 semitones down)
                  $F0-$FE: transpose up (value - $EF = 1..15 semitones up)
                  $FF: RST endmark, followed by restart-position byte
```

**NB**: GT2 uses the same orderlist byte values ($D0/$E0/$F0/$FF) — this part
is unchanged across versions.

### Instruments (31 instruments, instrument 0 not stored)

Fixed layout — 31 instruments always present, no count byte.

```
Offset  Size    Description
+0      byte    Attack/Decay (nibble-packed: hi=attack, lo=decay)
+1      byte    Sustain/Release (nibble-packed: hi=sustain, lo=release)
+2      byte    Initial pulse width (bits 7:1 = pulse_hi nibble×16; bit 0 = hard-restart flag)
+3      byte    Pulse speed (even values $00-$FE; added each tick to pulse low byte)
+4      byte    Pulse limit low  (low limit for pulse, low nybble always 0)
+5      byte    Pulse limit high (high limit for pulse, low nybble always 0)
+6      byte    Filter table pointer (1-based, 0 = no filter)
+7      byte    Wavetable size in bytes n (always even; n/2 = number of entry pairs)
+8      16      Instrument name (zero-padded)
+24     n       Wavetable: n/2 pairs of (waveform_byte, note_byte)
```

**Key point**: The V1 instrument carries its OWN wavetable inline in the .sng file.
There is no global wave table in V1; each instrument's wavetable is private.

**Pulse initial value encoding** (byte +2):
- Bits 7:4 = high nybble of pulse (×16 = bits 11:8 of 12-bit pulse)
- Bits 3:1 = low nybble of pulse (= bits 7:4 of byte written to $D402; bits 3:0 hardwired 0)
- Bit 0 = no-hard-restart flag (1 = skip hard restart on note trigger)
- Value $00 = pulse unchanged (don't reset pulse width or direction on new note)

**Pulse speed encoding** (byte +3):
- Bit 0 = also the no-hard-restart flag (ORed with byte +2's bit 0 in gt2 importer)
- Bits 7:1 = speed (must mask to &$FE before use)
- Even values $02-$FE are valid speeds; $00 = no pulse modulation

### Patterns Header

```
Offset  Size    Description
+0      byte    Number of patterns n
```

### Patterns

Repeats n times (pattern 0 first):

```
Offset  Size    Description
+0      byte    Size of pattern in bytes m (m is a MULTIPLE OF 3 — 3 bytes/row)
+1      m       Groups of 3 bytes per row:
                  Byte 0: Note number (see table below)
                  Byte 1: (instrument << 3) | command  — both packed into one byte
                  Byte 2: Command data byte
```

**Note byte encoding (V1)**:

```
$00-$5D   Notes C-0 to A-7 (94 notes) + command+data bytes PRESENT (full 3-byte row)
$5E       Keyoff (gate clear) — command+data bytes present
$5F       Rest — command+data bytes present
$60-$BC   Notes (offset by $60 from V2 encoding) — NO command bytes (1-byte row compressed)
           Wait: actually from player1.s: NOCMD=$60, so $60-$BD = notes without cmd bytes
$C0-$FE   Packed rests (value - $C0 = rest count-1; no cmd bytes)
$FF       End of pattern
```

Actually the exact mapping (from player1.s defines):
- `KEYOFF = $5E` — keyoff WITH cmd bytes
- `REST = $5F` — rest WITH cmd bytes
- `NOCMD = $60` — first note value that has NO cmd bytes (1-byte row)
- `FIRSTPACKEDREST = $C0` — start of multi-rest range (no cmd bytes)
- `ENDPATT = $FF`

For the pattern decoder logic (from `mt_getnewnotes` in player1.s):
```
if (note < $60) → note + command + data follow (3 bytes)
  if (note >= $60 && note < $C0) → note only (1 byte), no cmd/data
  if (note >= $C0) → packed rest (multiple rests), count = note - $C0 + 1
```

**The 2nd byte format** (instrument+command, when present):
```
Bits 7:3 = instrument number (0-31; 0 = no change)
Bits 2:0 = command number (0-7)
```

This is the crucial V1-vs-V2 difference: V1 packs instrument+command into ONE byte
(max 31 instruments, 8 commands). V2 uses two separate bytes (max 63 instruments, 16 commands).

### Filter Table (always 256 bytes — 64 entries × 4 bytes)

The filter table is ALWAYS 256 bytes regardless of how many filters are used.
Stored at the END of the file (after all patterns).

```
For each filter entry n (n = 0..63):
  Byte 0 (n*4+0): Filter control / channels bitmask
                    Non-zero = "static set" mode
                    Zero     = "modulation" mode
  Byte 1 (n*4+1): Filter type+volume (static mode) OR modulation duration (mod mode)
                    Static:  nibble 7:4 = filter type bitmask (LP/BP/HP/ch3mute)
                             nibble 3:0 = master volume (0-F, default F)
                    Mod:     duration in frames
  Byte 2 (n*4+2): Filter cutoff frequency (static: new cutoff; mod: cutoff add/frame)
  Byte 3 (n*4+3): Next filter step pointer (0 = stop; non-zero = next step index)
                    NOTE: in filter 0, "next step" is DISABLED (funktempo hack uses bytes 2-3)
```

**Static mode** (byte 0 ≠ 0): Set filter type+volume+cutoff in one frame, then jump to next.
**Modulation mode** (byte 0 = 0): Sweep cutoff by byte2 each frame for byte1 frames, then jump.

The filter byte 0 (channels) bitmask:
```
Bit 0 = filter channel 1
Bit 1 = filter channel 2
Bit 2 = filter channel 3
Bit 3 = filter external input
Bits 7:4 = resonance (0-F)
```

### Funktempo Hack

Filter entry 0 is special: bytes 2-3 encode the two alternating tempos for
`CMD_SETTEMPO` with data=$00 (funktempo command). Tempo 1 = `filttbl[2]`,
Tempo 2 = `filttbl[3]`. The "next step" field at byte 3 is repurposed.

---

## V1 Wavetable Semantics (player1.s: `mt_waveexec`)

The wavetable is a sequence of (waveform_byte, note_byte) pairs. Execution
starts at the instrument's wave pointer (1-based into the table).

### Waveform byte

| Value | Meaning |
|---|---|
| $00 | No waveform change (just change note) |
| $01-$07 | Delay N frames (do NOT change waveform; skip to pulse exec) |
| $08-$FF | Write this byte to $D404 (SID voice control register) |
| $FF | Jump/end marker (see below) |

SID control register bits: $01=gate, $02=sync, $04=ring, $08=test,
$10=triangle, $20=sawtooth, $40=pulse, $80=noise.

**First frame default**: On note trigger, $09 (test+gate = testbit hard restart)
is written to the voice. This is the "hardrestart" — the instrument's own
wavetable takes over from the next frame.

**Delay rows ($01-$07)**: The `mt_chnarpcount` register counts up each frame;
once it matches the waveform delay value, the delay completes. While delaying,
arpeggio/vibrato is NOT executed (wavetable has precedence).

### Note byte

| Value | Meaning |
|---|---|
| $00-$7F | Relative note: add to channel's current note (0 = same note) |
| $80-$FF | Absolute note: use directly (masked with $7F = note index $00-$7F) |

Note bytes $00-$5F are relative semitone offsets (0 = root, 12 = +1 octave, etc.)
Absolute notes $80-$DF correspond to C-0 through B-7.

### Jump/end (waveform byte = $FF)

```
if note_byte == $00: end wavetable execution (loop to instrument start? No — stops)
if note_byte != $00: jump to table position note_byte (1-based); can loop
    Special: if note_byte > 0 and the target lands past all entries, loop to instrument's
             wavetable start (waveptr + note_byte - 2 + instrument_start, from player1.s line 349)
```

From player1.s lines 344-354:
```asm
cmp #$ff
bcc mt_nowaveend        ; if not $FF, advance to next row
lda mt_notetbl+1,y
beq mt_nowaveloop       ; if note is 0: pointer = 0 (stop)
ldy mt_chninstnum,x
adc mt_instwave,y       ; carry cleared; adc + #$fe = jump relative to instrument start
adc #$fe
bne mt_nowaveloop       ; result is new table position
```
So: `new_ptr = note_byte + instwave - 2` (1-based). If note_byte=0, stop (ptr=0).

---

## V1 Arpeggio Command (Command 0) — The Key V1-only Feature

**This is the most important V1-specific feature removed in GT2.**

### Encoding

Pattern row 2nd byte: `(instrument << 3) | 0`, data byte encodes the arpeggio:

```
Data byte bits 6:4 = semitone offset for "step 1" (0-7 halftones; bit 7 = half-speed flag)
Data byte bits 3:0 = semitone offset for "step 2" (0-15 halftones)
Data byte bit 7    = half-speed flag (if set, arpeggio runs at half speed)
```

### Execution (player1.s: `mt_arpeggio`, lines 663-690)

The arpeggio cycles through 3 positions using `mt_chnarpcount` (0..5, wrapping):

```
arpcount 0,1 → play root note (no offset)
arpcount 2,3 → play root + bits[6:4] semitones (step 1)
arpcount 4,5 → play root + bits[3:0] semitones (step 2)
```

One counter tick per frame (no half-speed in V1.5 player — the bit 7 flag is
in the data byte but NOT implemented in player1.s v1.53; only the GT2 importer
references it when constructing arpeggio wavetable entries).

Actually from the arpeggio code in player1.s:
```asm
mt_arpeggio:    asl         ; A = data byte shifted left 1
                lda mt_chnarpcount,x
                pha
                adc #$01
                cmp #$06    ; wrap at 6
                bcc mt_arpnotover
                lda #$00
mt_arpnotover:  sta mt_chnarpcount,x
                pla
                lsr
                cmp #$01
                bcc mt_arp1      ; count/2 < 1 → arp1 (step 1: bits[6:4])
                bne mt_arp0      ; count/2 > 1 → arp0 (root)
mt_arp2:        lda mt_chnfxparam,x
                and #$0f         ; step 2: bits[3:0]
                bpl mt_arpfreq2
mt_arp0:        lda #$00         ; root: offset = 0
                bpl mt_arpfreq2
mt_arp1:        lda mt_chnfxparam,x
                and #$70         ; step 1: bits[6:4]
                lsr, lsr, lsr, lsr  ; shift down to get semitone count
mt_arpfreq2:    clc
                adc mt_chnnote,x ; add to current note
                tay              ; use as freq table index
                jmp mt_arpfreq
```

**Summary**: 3-position arpeggio cycling root→step1→step2→root (2 frames each,
so 6-frame period). Step 1 = bits 6:4 of data (0-7 semitones), step 2 = bits 3:0 (0-15).

### Arpeggio + Wavetable interaction

From `mt_tick0arp` and `mt_ticknarp`:
- Tick 0: arpeggio NOT executed if there's an active wavetable (waveptr ≠ 0)
- Tick N: arpeggio executed if waveptr = 0; skipped if waveptr ≠ 0
- This means: wavetable takes precedence over arpeggio command. The wavetable
  must complete (or use $FF/$00 end) before arpeggio resumes.

### GT2 import of arpeggio (gsong.c lines 700-804)

When GT2 imports a V1 song, it converts each unique (instrument, arpeggio_param)
combination to a V2 wavetable program. The conversion:

1. Copies instrument's wavetable up to the `$FF` jump/end
2. Appends 4 new entries:
   ```
   (ctrl=bit7_of_param>>7, note=bits[6:4]>>4)   ; step 1
   (ctrl=bit7_of_param>>7, note=bits[3:0])       ; step 2
   (ctrl=bit7_of_param>>7, note=0)               ; root
   (ctrl=$FF, note=arploop_position)             ; loop back
   ```
3. Creates either a new instrument (if <64 instruments) or a CMD_SETWAVEPTR command

The `bit 7` (`param & 0x80`) maps to `ltable[WTBL]` = 0 or 1 (delay 1 frame each step
= half-speed). A half-speed V1 arpeggio becomes a V2 arpeggio where each position
lasts 2 frames (delay=1 row in the wavetable).

---

## V1 Pattern Commands (all 8)

All 8 commands (bits 2:0 of the combined instrument+command byte):

| Cmd | Name | tick0 handler | tickN handler | Description |
|---|---|---|---|---|
| 0 | Arpeggio | mt_tick0arp | mt_ticknarp | data=0 → nothing; data≠0 → 3-note arp |
| 1 | Porta up | mt_tick0idle | mt_ticknportaup | Raise freq by (data×4) per tick |
| 2 | Porta down | mt_tick0idle | mt_ticknportadown | Lower freq by (data×4) per tick |
| 3 | Tone portamento | mt_tick0toneport | mt_tickntoneport | Slide to target note; data=speed (0=tie) |
| 4 | Vibrato | mt_tick0idle | mt_ticknvibrato | data: hi=speed, lo=depth; period = (hi×2) frames |
| 5 | Set filter | mt_tick0filter | mt_ticknidle | data = filter number (0-63) |
| 6 | Set SR | mt_tick0sr | mt_ticknidle | data written to $D406 (sustain/release) |
| 7 | Set tempo/special | mt_tick0tempo | mt_ticknidle | See below |

**Command 7 special values**:
- data $00-$7F with bit 7 clear: set ALL channels' tempo to data
- data $80-$EE with bit 7 set: set CURRENT channel's tempo to (data & $7F)
- data $EF: increment timing mark byte (at playerbase+$445)
- data $F0-$FF: set master volume fader (V1.5+; AND mask for $D418 = data & $0F<<4)
- data $00 (funktempo): use filter entry 0 bytes 2-3 as alternating tempos

**Speed/portamento formula**:
```
mt_makespeed:   asl       ; A = data byte
                rol temp2 ; shift into high byte
                asl
                rol temp2
                sta temp1 ; temp1 = (data << 2) & $FF = low byte of speed
                           ; temp2 = (data >> 6) = high byte of speed
```
So speed = data × 4 (as a 16-bit value split across temp1/temp2).

---

## V1 Vibrato (Command 4)

Data byte: high nybble = speed (how many frames per direction change), low nybble = depth.

From the player:
```asm
mt_ticknvibrato:tay
                and #$f0        ; clear low bits → speed part (×16)
                sta mt_temp1
                tya
                and #$0f        ; depth part
                sta mt_vibratocmp+1
```

The `mt_chnarpcount` register doubles as the vibrato direction/count register.
Direction flip when arpcount reaches `depth`. Vibrato pitch offset = arpcount/2 × speed.

Note from readme: "V1.3 onwards arpeggio & vibrato share the same internal register.
Mixing arpeggio and vibrato in the same note may cause unexpected results."

---

## V1 Pulse Modulation

Unlike GT2's shared pulse TABLE (PTBL), V1 stores pulse parameters per-instrument
and executes them per-channel. Executed every tick (both tick0 and tickN).

**Per-instrument params** (from instrument struct):
- `instpulse` (byte +2): initial pulse init (high nybble × 16 = $D402 value; low nybble → $D403 nib)
- `instpulsespd` (byte +3): modulation speed (bits 7:1; bit 0 = no-hard-restart)
- `instpulselow` (byte +4): lower limit for direction flip
- `instpulsehigh` (byte +5): upper limit for direction flip

**Per-channel runtime state**:
- `mt_chnpulse`: current pulse high byte (written to $D403)
- `mt_chnpulsedir`: current pulse direction + low bits (written to $D402; carry bit = direction)

**Pulse execution** (player1.s `mt_normalpulse` lines 371-400):
```
if direction bit (carry from pulsedir >> 1) == 0: ADD speed
  pulsedir += speed (carry = new direction flag)
  pulse_hi += carry (carry-in from lo byte add)
  if pulse_hi >= instpulsehigh: flip direction to subtract
else: SUBTRACT speed
  pulsedir -= speed
  pulse_hi -= borrow
  if pulse_hi <= instpulselow: flip direction to add
$D403 = pulse_hi
$D402 = pulsedir (the lo byte)
```

**No pulse table** — GT2's PTBL step-programming with arbitrary waveforms and jump
commands does NOT exist in V1. The GT2 importer synthesizes a PTBL program from
V1's 4 scalar parameters (see gsong.c lines 419-539).

---

## V1 Filter Execution

**Filter is a global shared resource** (same as GT2). Set via:
1. Instrument's filter field (non-zero = activate filter on note trigger)
2. Pattern command 5 (set filter pointer)

**Frame loop**: Filter executed ONCE at the start of every play() frame
(before per-channel processing). Handled by the `mt_filttime` / `mt_filtstep`
self-modifying code block at the very start of the play routine.

**Filter step execution** (`mt_setfiltersub`):
```
if filttbl[step*4+0] != 0:   static mode
  $D417 = filttbl[step*4+0]  (resonance + channel enable)
  $D418 = filttbl[step*4+1]  (filter type + master vol)
  if filttbl[step*4+2] != 0: $D416 = filttbl[step*4+2] (cutoff)
  mt_filttime = 0 (no countdown, execute next step immediately next frame)
  mt_filtstep = filttbl[step*4+3] (next step)
else:                          modulation mode
  mt_filtcutoffadd = filttbl[step*4+2]  (cutoff delta per frame)
  mt_filttime = filttbl[step*4+1]       (duration in frames)
  mt_filtstep = filttbl[step*4+3]       (next step after duration)
```

Each frame with active modulation: countdown decrements, cutoff += add.
When countdown reaches 0: jump to next step.

---

## V1 Player Frame Loop Structure

From `play` in player1.s (contrast with GT2's `mt_play`):

```
play():
1. Save zeropage (mt_temp1, mt_temp2)
2. FILTER: execute filter step or decrement modulation timer + apply cutoff add
3. Write $D416 (cutoff lo), $D417 (filter ctrl), $D418 (filter type+vol & master vol)
4. CHANNEL INIT CHECK: if channel needs init (chnsongnum >= 0), initialize it
   - Reset all per-channel state variables
   - Set tempo=5, tick=gatetimer+2
   - Force pattern fetch
5. For channel 0 (X=0), 1 (X=7), 2 (X=14):
   a. Decrement tick counter
   b. If tick != 0 (tickN):
      - Reload tempo if needed (funktempo)
      - Execute wavetable (if waveptr != 0) OR effect command (porta/vibrato/arp)
   c. If tick == 0 (tick0):
      - Read instrument + command from chnnewfx
      - Execute tick0 command (arpeggio/toneport/filter/sr/tempo)
      - If new note: init note (pulse reset, wavetable ptr, AD/SR, hard restart)
   d. Execute pulse modulation
   e. Check for note fetch (tick == gatetimer): fetch next pattern row
   f. Write $D400-$D404 (freq lo/hi, gate & wave)
6. Restore zeropage
7. RTS
```

**Key V1 vs GT2 loop differences**:
- V1 filter goes before channels; GT2 same
- V1 writes $D402/$D403 (pulse) from channel struct every frame in mt_loadregs (no buffering)
- GT2 has optional buffered SID writes; V1 always unbuffered
- V1 hardcodes X register offsets (0, 7, 14 for 3 channels, 7 bytes apart) for SID addressing
- GT2 same (SID registers $D400-$D418 are 7 bytes per voice: $D400, $D401, ... $D406, $D407 = next voice start)
- V1 uses self-modifying code for the jump dispatch table (low-byte SMC at mt_tick0jump+1, mt_ticknjump+1)
- V1 and GT2 both use this same low-byte SMC trick for the effect jump table

---

## V1 Instrument Format (.INS file)

```
Offset  Size    Description
+0      4       Identification string "GTI!"
+4      byte    Attack/Decay
+5      byte    Sustain/Release
+6      byte    Initial pulse width (bit 0 = no-hard-restart flag)
+7      byte    Pulse speed (bits 7:1; bit 0 = no-hard-restart, same as byte +6 bit 0)
+8      byte    Pulse limit low
+9      byte    Pulse limit high
+10     byte    Filter number (0 = no filter; 1-63 = filter table entry)
+11     byte    Wavetable size in bytes n (always even)
+12     16      Instrument name (zero-padded)
+28     n       Wavetable (n/2 pairs of (waveform_byte, note_byte))
+28+n   4       If filter number nonzero: 4-byte filter entry for this instrument
```

The 4-byte filter entry is a single filter step in the same format as the main filter table.

---

## V1 vs GT2 Feature Comparison (V1.53 → GT2 import logic)

From gsong.c lines 329-806 (the "GoatTracker 1.xx import" block):

| V1 feature | GT2 equivalent | GT2 import conversion |
|---|---|---|
| Per-instrument wavetable | WTBL global table, instrument has WTBL pointer | Appended to global WTBL; pointer adjusted |
| Wavetable $FF jump rel. | WTBL $FF jump (absolute 1-based) | rtable[WTBL][fw] += ptr - 1 to make absolute |
| Wavetable ctrl $08-$0F | WTBL left values $E0-$EF (silent+ctrl range) | `lval |= $E0` applied in importer |
| Per-instr pulse 4 params | PTBL step sequence (set+modulate+jump) | Synthesized 3-phase PTBL program |
| Filter table (64 × 4B) | FTBL global table | 4-byte entries decoded + mapped into FTBL rows |
| Arpeggio command (cmd 0) | None (use WTBL) | Converted to WTBL program + new instrument |
| Vibrato (cmd 4 direct) | STBL (speedtable) pointer in instrument | makespeedtable() call: maps old param to STBL |
| Portamento (cmd 1/2/3) | Same commands but STBL-speed | makespeedtable() call |
| Funktempo (tempo=0) | CMD_FUNKTEMPO with STBL pointer | filttbl[2/3] → makespeedtable() → STBL |
| 31 instruments max | 63 instruments max | Same; arpeggio may add synthetic instruments |
| 3-byte pattern rows | 4-byte pattern rows | instr byte = (cmd_byte >> 3), cmd = (cmd_byte & 7) |
| Filter table in file | FTBL global (same) | Entries individually decoded + remapped |
| $5E/$5F note values | $BE/$BD ($BE=keyoff, $BD=rest) | OLDKEYOFF + OLDREST constants in gcommon.h |

---

## V1 Identification in HVSC

The HVSC engine string for GoatTracker V1 tunes is `GoatTracker_V1.x`. The file
format magic is `GTS!` (4 bytes). GT2 format is `GTS2`-`GTS5` depending on version.

sngspli2.c (GT2 pattern splitter) at lines 281-284 confirms the table count:
- `GTS2` → 3 tables (wave, pulse, filter; no speedtable yet)
- `GTS3`/`GTS4`/`GTS5` → 4 tables (wave, pulse, filter, speed)
- `GTS!` (V1) → not handled by sngspli2 (GTS! songs must be imported to GT2 first)

betaconv.c (GT2 early-beta converter, 2.65): converts early GT2 beta (GTS2, 47 instruments)
to current GT2. Not related to V1 but confirms the intermediate GTS2 layout (3 tables).

---

## Key Takeaways for SIDfinity

1. **Arpeggio is the V1-defining feature**: entirely absent in GT2. It's a per-frame
   3-note cycling command (period = 6 frames for full cycle). Encoded as a single data
   byte where `bits[6:4]` = step1 offset and `bits[3:0]` = step2 offset. Half-speed
   flag (bit 7) runs the arpeggio at 1/2 speed (12-frame period).

2. **Wavetable is per-instrument, not global**: each V1 instrument embeds its own
   wavetable inline. There is no HVSC "GTS!" file with a global wave table. This is
   the single biggest structural difference from GT2.

3. **Pulse is parametric, not table-driven**: V1 has a simple bounce oscillator
   (start, speed, lo-limit, hi-limit) per instrument. GT2's PTBL is a much more
   expressive step sequencer.

4. **Filter is already step-programmable in V1.4+**: 64 entries, 4 bytes each.
   Same basic model as GT2's FTBL.

5. **The V1 player wavetable delay ($01-$07) is the "held note" mechanism**: during
   delay, no arpeggio or vibrato executes. This matches the "waveptr takes precedence
   over effects" semantics.

6. **Pattern row density**: V1 uses 3 bytes/row (packed cmd+instr) with optional
   1-byte rows (note only, no cmd). GT2 uses fixed 4 bytes/row. V1 is more compact.

7. **No speed table in V1**: vibrato and portamento use direct-byte parameters
   (not STBL pointers). The conversion to GT2 calls makespeedtable() to synthesize
   STBL entries from V1 params.

---

---

## Packed Binary Layout (PSID/HVSC files — NOT the .sng format)

**Important for SIDfinity RE**: HVSC GoatTracker V1 tunes are PSID containers,
not GTS! files. The GTS! format is the editor's save format. The packed binary
(produced by the editor's F9 packer/relocator) has a DIFFERENT layout.

### PSID header followed by packed player + music data

The player uses pre-multiplied-by-8 instrument indices (INST1=$08, INST2=$10, ...
INST31=$F8). The binary music data layout is:

```
Instrument block (31 × 8 bytes = 248 bytes at base address):
  For instrument n (n=1..31, index = n*8):
    base + n*8 + 0 = Attack/Decay
    base + n*8 + 1 = Sustain/Release
    base + n*8 + 2 = Initial pulse (hi nybble; bit 0 = no-hardrestart)
    base + n*8 + 3 = Pulse speed (bits 7:1; bit 0 = no-hardrestart)
    base + n*8 + 4 = Pulse limit low
    base + n*8 + 5 = Pulse limit high
    base + n*8 + 6 = Filter table pointer (0 = none)
    base + n*8 + 7 = Wavetable pointer (1-based index into wavetbl)

Wavetable (two parallel arrays, each up to 256 bytes):
  mt_wavetbl[0..N-1] = wave control bytes
  mt_notetbl[0..N-1] = note bytes
  (wavetbl and notetbl are at fixed offsets determined by packer relocation)

Song pointer tables (two parallel arrays):
  mt_songtbllo[0..S-1] = lo bytes of per-subtune-channel orderlist addresses
  mt_songtblhi[0..S-1] = hi bytes

Pattern pointer tables (two parallel arrays):
  mt_patttbllo[0..P-1] = lo bytes of per-pattern addresses
  mt_patttblhi[0..P-1] = hi bytes

Filter table (always 256 bytes = 64 entries × 4 bytes):
  mt_filttbl[0..255]
```

The relocation sizes (from player2.s stub bytes at the start of the packed block):
```
byte 0: Instrument data size in bytes (= 31 × 8 + optional per-inst-filter extensions)
byte 1: Wavetable length in bytes / 2 (= N pairs, so N wave + N note bytes)
byte 2: Songtable size in bytes / 2 (= S lo + S hi bytes)
byte 3: Patterntable size in bytes / 2 (= P lo + P hi bytes)
```

These 4 bytes precede the actual music data in gamemusic-mode packed songs and
let the RELOCATEMUSIC routine adjust all internal pointers when music is loaded
to a different address.

**For RE of a PSID**: find the player entry point, locate the data access
instructions (LDA abs,Y for instrument fields), and follow the data section
starting at offset 0 from the instrument block base.

---

## Leads to follow

- The `src/goattrk.c` in V1.53 (156 KB, the main editor source) contains the full
  C-side serialization code for GTS! save/load, pattern editing, and instrument editing.
  Not read yet — worth extracting the loadsong/savesong functions to verify filter table
  binary layout and confirm the 31-instrument structure.
- The V1.25 player sources (`v1_player1_125.s`, `v1_player2_125.s`) predate the filter
  step table (V1.3 added it) and show the earlier per-step single-filter design. Read
  if understanding the pre-filter-step V1 variant matters.
- Archive.org may have even earlier V1 betas (0.9-1.2) with different arpeggio behaviour
  — the V1.3 changelog notes "arpeggio & vibrato now share internal register".
- CSDb GoatTracker V1 entries (search `engine:GoatTracker_V1.x`) may show how composers
  used the arpeggio command in practice.
- `src/sngsplit.c` in V1.53 (pattern splitter for V1 format) — may confirm the binary
  format from a different angle, specifically the orderlist length encoding.
- SIDFactory II (`github.com/Chordian/sidfactory2`) has a GoatTracker importer that
  may parse GTS! format — check `Tools/src/library/FileIO/` or similar.
