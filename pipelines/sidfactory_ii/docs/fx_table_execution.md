---
source_url: https://github.com/Chordian/sidfactory2 (driver notes + C++ source)
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity), Jens-Christian Huus (JCH)
content_date: 2026-03-14
reliability: primary
secondary_sources:
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/notes_driver11.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/src/user_manual_20260314.txt
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/github_format_spec.md
  - /home/jtr/sidfinity/pipelines/sidfactory_ii/docs/driver11_source.md
---

# SID Factory II — Table Execution Models (Driver 11)

Detailed per-row/per-tick execution models for every table type in driver 11.
Cross-reference with `fx_register_semantics.md` for the register-level output.

---

## 1. Wave Table Execution Model

### Format: 2 bytes per row (row-major layout in memory)

```
Byte 0: waveform byte (written to Voice+4, SID ctrl register)
Byte 1: note/pitch byte
```

### Per-frame algorithm:
1. Read current wave table row (byte 0, byte 1).
2. If byte 0 = $7F: jump — set wave pointer to byte 1, go to step 1 with new row.
3. Else (normal row):
   a. Write byte 0 to Voice+4 (SID ctrl = waveform + gate bit).
   b. Compute frequency from byte 1:
      - If byte 1 in $00–$7F: pitch = sequence_note + orderlist_transpose + byte1_semitones
        (if arp active AND byte 1 = $00: pitch += arp_table[arp_step])
        freq = note_table[pitch]; write to Voice+0 (lo), Voice+1 (hi)
      - If byte 1 in $80–$DF: pitch = byte1 - $80 (absolute, range 0–95)
        freq = note_table[pitch]; write to Voice+0, Voice+1
        (sequence note and orderlist transpose IGNORED)
   c. Advance wave pointer by 1 row.

### Jump row semantics:
- $7F XX: jump to row XX. Jump to own row index = self-loop (hold current state forever).
- The wave table MUST end with a $7F self-loop or a loop-back; falling off the end
  reads adjacent table data as waveform bytes (undefined behavior).

### Note-on reset:
On each new note trigger (non-tie), the wave pointer resets to the instrument's wave
table index (instrument byte 5). The pulse pointer also resets (unless $08 flag set).

### Waveform byte values (write to Voice+4, gate bit = $01 normally set):
```
$11 = triangle  + gate
$21 = sawtooth  + gate
$41 = pulse     + gate  (requires pulse table or instrument PW for sound)
$81 = noise     + gate
$31 = tri+saw   + gate
$51 = tri+pulse + gate
$61 = saw+pulse + gate
$71 = tri+saw+pulse + gate
$09 = test bit ($08) + gate ($01): oscillator reset / HR hold
$10 = triangle  (no gate, gate off)
$20 = sawtooth  (no gate)
$40 = pulse     (no gate)
$80 = noise     (no gate)
```
Gate bit = $01. Test bit = $08. Sync bit = $02. Ring bit = $04.

---

## 2. Pulse Table Execution Model (Driver 11 / 14)

### Format: 3 bytes per row (row-major)

```
Row type A: 8X XX YY  (byte 0 high nibble >= $8)  → Set pulse width
Row type B: 0X XX YY  (byte 0 high nibble = $0)    → Add to pulse width
Row type C: 7F -- XX  (byte 0 = $7F)               → Jump to index
```

### Set pulse width row ($8X XX YY):
- 12-bit pulse width = (byte0_lo_nibble << 8) | byte1
  i.e., pw12 = ($X << 8) | XX  where X = byte 0 & $0F
- Write pw12 to Voice+2/3: pw_lo = pw12 & $FF, pw_hi = (pw12 >> 8) & $0F
- Hold for YY frames (duration counter). Each frame: no further PW write until YY expires.
- When YY count exhausted: advance to next row.

### Add to pulse width row ($0X XX YY):
- 12-bit signed delta = (byte0_lo_nibble << 8) | byte1
  i.e., delta12 = ($X << 8) | XX
  Sign: if delta12 >= $800, treat as negative (12-bit two's complement)
- EVERY FRAME during YY frames: current_pw += delta12 (mod 12-bit wrap)
- Write updated current_pw to Voice+2/3 each frame
- When YY count exhausted: advance to next row.

### Jump row ($7F -- XX):
- Jump to row XX in pulse table. Self-jump (own index) = end program (no further PW changes).
- The '--' (ignored byte) is not written anywhere.

### Pulse table pointer reset:
- On new note trigger: reset to instrument byte 4 (pulse table index), UNLESS
  instrument byte 2 bit 3 ($08, driver 11.05+) is set AND the instrument was NOT explicitly
  changed in this sequence row (i.e., the instrument is carried over, not re-declared).

### Note on pulse register layout:
Voice+2 = PW low byte (bits 7-0 of 12-bit value).
Voice+3 = PW high byte (bits 11-8 of 12-bit value, in bits 3-0 of $D403/$D40A/$D411).
PW range 0–4095 ($000–$FFF). Effective sound is symmetric: PW=0 ≡ PW=4095 (both silent),
PW=2048 = widest (50% duty cycle). Values 0 and 4095, or 10 and 4085, sound identical.

---

## 3. Filter Table Execution Model (Driver 11 / 14)

### Format: 3 bytes per row (row-major)

```
Row type A: XY YY RB  (byte 0 high nibble > $8, i.e. $9–$F)  → Set filter
Row type B: 0X XX YY  (byte 0 high nibble = $0)               → Add to cutoff
Row type C: 7F -- XX                                           → Jump to index
```

### Set filter row ($XY YY RB, with X in $9–$F):
The 3 bytes encode:
- byte 0 = $XY: X = filter passband nibble ($9–$F), Y = top nibble of 12-bit cutoff
- byte 1 = YY: lower 8 bits of cutoff value
- byte 2 = $RB: R = resonance nibble, B = voice bitmask (3-bit)

12-bit cutoff value = (Y << 8) | YY  (only 11 bits are used by SID: range 0–2047)

SID writes:
- $D415 (filter cutoff lo): bits 2-0 of the 11-bit cutoff value (3 bits)
- $D416 (filter cutoff hi): bits 10-3 of the 11-bit cutoff value (8 bits)
- $D417 (resonance + routing): (R << 4) | B
  B bit 0 = voice 1 enable, bit 1 = voice 2 enable, bit 2 = voice 3 enable
- $D418 (mode + main vol): filter mode bits 7-5 from X nibble (see below) | current main vol

Filter mode → $D418 bits 7-5 mapping:
```
X=$9 → HP+BP  → $D418: bit7=1, bit6=1, bit5=0  → mask $C0
X=$A → HP     → $D418: bit7=1, bit6=0, bit5=0  → mask $80
X=$B → BP     → $D418: bit7=0, bit6=1, bit5=0  → mask $40
X=$C → HP+LP  → $D418: bit7=1, bit6=0, bit5=1  → mask $A0  (notch)
X=$D → BP+LP  → $D418: bit7=0, bit6=1, bit5=1  → mask $60
X=$E → LP     → $D418: bit7=0, bit6=0, bit5=1  → mask $20
X=$F → all    → $D418: bit7=1, bit6=1, bit5=1  → mask $E0
```
OPEN: Confirm these exact bit assignments vs SID datasheet ($D418: bit7=HP, bit6=BP, bit5=LP).
The bits 3-0 of $D418 (main volume) are preserved / combined with existing value.

The set-filter row is held for its own frame (one frame write, then advance? Or the set
persists until the next row?) OPEN: does the filter program hold the set-filter row's
values for multiple frames or just one? The driver notes say add-to-cutoff has a "YY =
number of frames" counter, but the set-filter row ($XY YY RB) encodes the resonance+bitmask
in what would be "YY" and "RB." There is NO separate frame-count for the set-filter row —
it appears to write once and immediately advance to the next row. Needs disasm to confirm.

### Add to cutoff row ($0X XX YY):
- 12-bit signed delta = ($X << 8) | XX
- EVERY FRAME during YY frames: current_cutoff += delta, then write $D415/$D416
- $D417 and $D418 NOT written (only cutoff is updated)
- Advance to next row when YY exhausted.

### Jump row ($7F -- XX):
Jump to row XX (self = end program, no further filter writes).

### Per-instrument filter enable [driver 11.03+]:
Instrument byte 2 bit 5 ($20): when set, the voice's channel bit is OR'd into the
B bitmask in $D417. This allows a voice to always be filtered regardless of the filter
program's B setting.

---

## 4. HR (Hard Restart) Table Execution Model

### Format: 2 bytes per row

```
Byte 0: AD  (applied to Voice+5 during hard restart phase)
Byte 1: SR  (applied to Voice+6 during hard restart phase)
```

Indexed by instrument byte 2 bits 2-0 (0–7 in driver 11.05, 0–15 in 11.00–11.04).

### Timing:
- Frame N-2 before the next note: write HR AD and SR to Voice+5/6; write $09 to Voice+4
- Frame N-1: no further writes (hardware stabilizes)
- Frame N: new note fires normally

Typical values:
- HR row 0: $0F $00 = AD(fast attack, fast decay) + SR(sustain 0, fast release)
  This quickly cuts the previous note and stabilizes the ADSR for a clean next note.

### Minimum safe tempo with HR:
With HR firing 2 frames before, the minimum sequence row duration is 2 frames. Below 2,
HR and the new note collide. The manual explicitly states: "Usually [the minimum] is 02."

---

## 5. Arpeggio Table Execution Model

### Format: 1 byte per row

```
$00–$6F  Semitone offset (added to base note for frequency lookup)
$70–$7F  Relative jump: new_index = start_index + (byte & $0F)
```

### Activation: T3 XX YY command
- XX = arpeggio speed (frames per arp step; 0 = advance every frame)
- YY = starting index in arp table

### Per-frame algorithm:
1. Speed counter counts down XX frames.
2. When counter expires: read arp table at current_step.
   - If $00–$6F: use as semitone offset; advance current_step by 1.
   - If $70–$7F: set current_step = start_index + (byte & $0F), loop.
3. Semitone offset added to base_note for frequency computation.
4. Only applied when wave table byte 1 = $00 (see §1 above).

### Relative jump semantics:
The jump target is relative to YY (the start_index from T3). This allows multiple arp
shapes to share rows, differentiated by which starting index T3 specifies:

```
Example from notes_driver11.txt:
00: 0C   (add 12 semitones)
01: 07   (add 7) *start_1
02: 04   (add 4) *start_2
03: 00   (add 0)
04: 71   (relative jump +1)
         → if called with YY=00: $71 → 00+1=01 → loops *start_1 = [07, 04, 00, loop]
         → if called with YY=01: $71 → 01+1=02 → loops *start_2 = [04, 00, loop]
```

---

## 6. Tempo Table Execution Model

### Format: 1 byte per row

```
$01–$7E  Duration: this many frames per sequence row
$7F      Loop back to start of tempo table (or configured loop point)
```

### Per-sequence-row algorithm:
1. Read current tempo table byte.
2. If $7F: wrap back to row 0 (or loop_index), re-read.
3. Otherwise: row_duration = this_byte. Decrement for (row_duration) frames.
4. When count exhausted: advance both sequence row and tempo table pointer.

Multiple tempo values create shuffle/swing rhythms. A chain of $06 $05 $7F produces
alternating 6/5 frame rows. A single $06 $7F produces steady 6 frames/row (PAL
50 Hz: 6 frames = ~120 ms = tempo ~8.3 rows/sec ≈ 100 BPM with 2 rows/beat).

---

## 7. Init Table Execution Model

### Format: 2 bytes per row

```
Byte 0: Tempo table index (which tempo program to start from)
Byte 1: Main volume ($D418 bits 3-0); written to $D418 on song init
```

One row per song in multi-song files. On song start:
1. Set tempo pointer to tempo_table[byte 0].
2. Write byte 1 to $D418 low nibble (main volume; filter mode bits preserved or reset).

Typically byte 1 = $0F (maximum volume).

---

## 8. Sequence Byte Encoding (packed binary)

For completeness — how the sequence stream feeds the table consumers above.

```
$00        Gate off (clears Voice+4 gate bit)
$01–$6F    Note on (sequence note value → freq table lookup, gate on)
$7E        Gate on hold (re-gates without new note)
$7F        End of sequence (terminates sequence stream)
$80–$8F    Duration (byte & $0F) ticks, no tie
$90–$9F    Duration (byte & $0F) ticks, WITH tie (no gate re-trigger)
$A0–$BF    Set instrument: index = byte & $1F (up to 32 instruments)
$C0–$FF    Set command: index = byte & $3F (up to 64 commands)
```

Instrument and command bytes are delta-compressed (only emitted on change).

---

## 9. Order List Byte Encoding (packed binary)

```
$00–$7F    Sequence index 0–127
$80–$FF    Transpose byte: semitone_shift = (byte & $7F) - $20
           $A0 = no transpose (identity), $94 = -12 (octave down), $AC = +12 (octave up)
           Range: $80 = -32 semitones, $BF = +31 semitones
$FE        End marker (stop, no loop)
$FF        Loop marker; next byte = packed-stream byte offset of loop target
```

Transpose bytes are stateful (persist until next transpose byte in the stream).

---

## Leads to follow

- **OPEN: Set-filter row frame count** — does the $XY YY RB row produce a single-frame write
  (then advance) or is there an implicit hold? The RB byte's B is a bitmask, not a frame
  count; the add-to-cutoff row HAS a frame count (YY). A disasm of the filter program runner
  loop will show whether set-filter rows advance immediately or hold one frame.
- **OPEN: Add-to-pulse / add-to-cutoff — is the write per-frame or once?** The notes say
  "add to pulse width" for YY frames. Confirm whether the delta is applied ONCE then held,
  or applied every single frame during the YY count. Most likely every frame.
- **OPEN: Pulse table first-byte structure** — is the 12-bit value stored as:
  (byte0 & $0F) << 8 | byte1, or (byte0 & $0F) << 4 | (byte1 >> 4), etc.?
  Need to verify exact bit packing from the driver binary.
- **OPEN: wave table column-major vs row-major** — the driver_info source shows
  data_layout = RowMajor for wave, Pulse, Filter (ColumnMajor only for Instruments/Commands).
  Confirm from the prg binary that wave table data is stored col0[0], col1[0], col0[1],
  col1[1], ... (interleaved), vs separate column arrays.
