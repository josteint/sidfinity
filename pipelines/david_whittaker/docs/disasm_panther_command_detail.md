---
source_url: https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Whittaker_David/Whittaker_David_Panther.asm
fetched_via: direct (file already in repo at pipelines/david_whittaker/docs/src/Whittaker_David_Panther.asm)
fetch_date: 2026-06-17
author: dmx87 (realdmx) — reverse-engineer
content_date: 1986 (original); disassembly ~2020s
reliability: primary
---

# Panther Disassembly — Detailed Command Analysis

This document complements `csdb_player_technical.md` with a closer read of
`Whittaker_David_Panther.asm` (the sole published dmx87 C64 Whittaker
disassembly as of 2026-06-17).  Focus: command byte semantics, SoundUpdate
frequency arithmetic, PWM sweep, and pattern data cross-check.

---

## 1.  Command Table (18 entries, $80–$93)

The `pspecial` code at ~$9744 first checks `CMP #$B8`.  If `< $B8` (i.e.
$80–$B7), the lower 4 bits minus $80 are used as a 2-byte index into
`CommandTable`.  So $80 = entry 0, $81 = entry 1 … $93 = entry 19 (18
entries actually used).

Complete dispatch table as read from the source:

| Cmd | Target label | Decoded behaviour |
|-----|-------------|-------------------|
| $80 | L_93FB | JMP L_9431 — re-enter note trigger at the "duration reload" step; effectively a "re-gate" with current note |
| $81 | L_93CF | LDA #0; STA VD_B1D — clear B1D (disables PWM, slide-UP, any active effect bits in B1D) |
| $82 | L_93D7 | LDA #$40; STA VD_B1D — set B1D bit7 = enable PWM-style effect (upward) |
| $83 | L_93DF | Read 1 byte from pattern → STA ModeVol — override global $D418 volume |
| $84 | L_9363 | ORA FLAGS with $04 (bit3) → enable pitch-bend/portamento down mode |
| $85 | L_935B | ORA FLAGS with $20 (bit6) → enable pitch slide UP; clear B07/B08 (slide accumulators) |
| $86 | L_93C5 | ORA FLAGS with $08 (bit4) → enable vibrato step (one-shot?) |
| $87 | L_93BD | ORA FLAGS with $80 (bit8) then fall into $86: sets both bit8 AND bit4 → slide DOWN with vibrato step |
| $88 | L_9304 | Track advance: adds 2 to B05/B06 (track byte-offset), loads next pattern ptr; wraps at track end |
| $89 | L_939A | Set B1A (PWM half-range) + B1C (PWM initial value) from 2 pattern bytes; 3rd byte → B1A and B1C |
| $8A | cmd_Noise | WAVE = $80 (Noise waveform) |
| $8B | cmd_Pulse | WAVE = $40 (Pulse/Square waveform) |
| $8C | cmd_Saw | WAVE = $20 (Sawtooth waveform) |
| $8D | cmd_Tri | WAVE = $10 (Triangle waveform) |
| $8E | L_93EF | ORA FLAGS with $02 + $01 → set bits 1+2 = enable vibrato (both direction bits) |
| $8F | cmd_PulseHi | PWL=0; read 1 byte → PWH; B21=0 (fixed pulse width, disables PWM sweep) |
| $90 | L_9297 | Read 3 bytes → B1E, B1F, B20 (PWM sweep: lo-bound, hi-bound, step-per-frame); set B21=1 |
| $91 | cmd_StopMusic | PLA×2 (unwind JSR call chain); JMP StopMusic |
| $92 | cmd_RingTri | WAVE = $14 (Triangle + Ring-Mod) |
| $93 | cmd_SyncSquare | WAVE = $42 (Pulse + Sync) |

**Key observations:**
- $88 is BOTH the pattern end sentinel AND a valid command byte (track advance).
  Context: $88 at the start of a pattern byte stream means "end of this
  pattern, advance to next"; as a raw command it is also the track-advance
  command.  In practice the arp table $88 terminator is handled by the
  SoundUpdate arp-reset code, not by pspecial.
- Waveforms: Noise($80), Pulse($40), Saw($20), Tri($10), Ring+Tri($14),
  Sync+Pulse($42).  Gate bit is NOT stored in WAVE; it is added at output
  time by the `INX; STX` idiom.
- Commands $94–$B7 are valid command-table indices (entries 20–55) but the
  table only has 18 entries; $94–$B7 would be out-of-table and thus
  undefined (not used in Panther data).

---

## 2.  High-byte dispatch ($B8–$FF)

After confirming `< $B8` routes to CommandTable, the cascade uses ADC+BCS:

```asm
pspecial:
    cmp #$b8         ; A < $B8 → commands (handled above)
    bcc pcommand
    adc #$1f         ; $B8+$1F = $D7; carry set if A >= $B8+$20 = $D8
    bcs pdur         ; → $C0–$CF range (after offset): note duration
    adc #$10         ; $C8+$10 = $D8 range check for ADSR
    bcs padsr        ; → $C8–$CF: ADSR
    adc #$10         ; next test
    bcc ptempo       ; → $D8–$DF: tempo
    ; fall through to arp select ($E0–$FF)
```

Reconstructed decode table:

| Range | Category | Handler |
|-------|----------|---------|
| $80–$B7 | Commands (see table above) | pcommand |
| $B8–$BF | (8 unused/unmapped values) | undefined in Panther |
| $C0–$C7 | Note duration (short) | pdur — `(A + $1F)` after carry; NOTD = result |
| $C8–$CF | ADSR override | padsr — read 2 bytes (AD, SR) |
| $D0–$D7 | Note duration (medium) | pdur via different path |
| $D8–$DF | Tempo | ptempo — SongTempo = `(A + $09)` |
| $E0–$FF | Arpeggio select | arp path — index = `(A & $1F) * 2` |

**Duration values ($C0–$D7):** After the `adc #$1f` the carry was set ($B8+
$1F = carry when A>$B7 = always in this range).  The carry-folded result
ends up as the NOTD value.  Short durations ($C0–$C7) map to NOTD = 2–9
(approximate); longer durations ($D0–$D7) map to larger values.

**ADSR ($C8–$CF):** Next 2 pattern bytes are loaded directly into VD_AD
and VD_SR (Attack/Decay and Sustain/Release).

**Tempo ($D8–$DF):** `SongTempo = A + $09`.  For $D8 that gives $E1 = 225
(very slow), for $DF gives $E8 = 232.  Tempo in this engine is a countdown
reload: SongTempo is loaded into TempoCnt each tempo cycle, so LARGER value
= SLOWER tempo.

**Arpeggio ($E0–$FF):** `(A & $1F) * 2` = 0–62 (even index), into ArpTable
(13 entries in Panther, indices 0–12 = $E0–$EC).  $ED–$FF would be out-of-
table for Panther's 13-entry ArpTable (likely valid in other songs that have
more arpeggios).

---

## 3.  SoundUpdate — Frequency Arithmetic

The `SoundUpdate` routine (~$9835) computes the final SID frequency word
in $f8/$f9 (16-bit), then returns X=$f8, Y=$f9.

### 3a.  Arpeggio path (FLAGS bit5 set)

```
Get ARP pointer → load arp byte
If arp byte >= $54 → reset ARP to ARP2 (loop)
transpose_val = arp_byte
NOTE = NOTE + transpose_val (semitone offset)
→ proceed to freq lookup
```

The $54 threshold (84 decimal) is the full range of the note table
(84 semitones).  Any arp offset above 83 would fall off the table, so
$54–$87 are all "reset" triggers; $88 is the arp-end sentinel.

### 3b.  Frequency lookup

```
X = NOTE × 2
NoteFreqsL[X] → $f8 (freq lo)
NoteFreqsH[X] → $f9 (freq hi)   ; NoteFreqsH = NoteFreqsL + 1 (same table, offset by 1)
```

### 3c.  PWM path (B1D bit7 set)

If B1D & $40 (bit7):
- Uses the PWM accumulator logic in B1A/B1B/B1C to compute a ±freq offset
- The offset is scaled and added/subtracted from $f8/$f9

This is Whittaker's pitch-wobble / vibrato-like PWM effect applied to
frequency rather than pulse width.

### 3d.  Slide path (FLAGS bits 2 or 5 via $24 mask)

Flip FLAGS bit1 (alternating every frame).
Check FLAGS & $24:
- If FLAGS bit3 ($04) set → Slide down path (L_9608):
  subtract B07/B08 accumulator from $f8/$f9 each frame
- If FLAGS bit6 ($20) set → Slide up path (L_9??):
  add B07/B08 accumulator

B07/B08 are loaded from B0D/B0E (which were set by the $89 command).

### 3e.  PWM sweep output (SoundUpdate exit, B21 check)

After frequency arithmetic, the PWM sweep is evaluated:
- B21 = 0: PWM off
- B21 = 1 (sweep up): PWL/PWH += B20 per frame; at PWH == B1F → reverse direction (B21 = $81)
- B21 = $81 (sweep down): PWL/PWH -= B20 per frame; at PWH <= B1E → reverse direction (B21 = 1)

This is the pulse-width modulation effect activated by command $90.

### 3f.  Noise special case

```asm
LDA FLAGS
AND #3
CMP #3
BNE L_9691     ; not 3: normal exit

; if FLAGS & 3 == 3 → noise: add $30 to freq hi
LDA $f9
ADC #$30
STA $f9
CTRL = $80     ; force noise waveform
```

Noise is enabled by setting FLAGS bits 0 AND 1 simultaneously.
The freq-hi offset (+$30) is the standard C64 noise frequency trick to
ensure noise sounds correct across octaves.

---

## 4.  Gate-On / Gate-Off Mechanism

From the `play` output stage for voice 1 (similar for v2/v3):

```asm
LDX  VD_CTRL      ; = WAVE without gate bit
LDA  VD_B19
BEQ  _v2          ; B19==0: skip gate-off, just write gate-on
DEC  VD_B19       ; B19>0: write gate-off then gate-on
STX  SIDV1CTRL    ; write without gate (gate-off)
_v2:
INX               ; +1 = set gate bit
STX  SIDV1CTRL    ; write with gate (gate-on)
```

`B19` is set to 1 when a new note is triggered.  On the next frame,
B19=1: gate-off is written first (STX with WAVE), then gate-on (INX;STX).
On subsequent frames B19=0: only gate-on is written (the previous value
with gate already set).

This means Whittaker's engine does a one-frame gate reset on every new
note — generating a crisp note attack even without an explicit ADSR change.

---

## 5.  ArpTable — Full Data (Panther)

13 arpeggio patterns, semitone offsets from root, terminated by $88:

| Index | Cmd byte | Semitones | Character |
|-------|----------|-----------|-----------|
| 0 | $E0 | 0 3 7 | Minor triad |
| 1 | $E1 | 0 4 7 | Major triad |
| 2 | $E2 | 0 3 7 12 | Minor + octave |
| 3 | $E3 | 0 4 7 12 | Major + octave |
| 4 | $E4 | 7 12 15 | Power + ext (5th, 8va, m9) |
| 5 | $E5 | 7 12 16 | Power + maj9 (5th, 8va, M9) |
| 6 | $E6 | 3 7 12 | Minor triad inverted (m3, 5th, 8va) |
| 7 | $E7 | 4 7 12 | Major triad inverted (M3, 5th, 8va) |
| 8 | $E8 | 0 12 | Octave jump |
| 9 | $E9 | 0 4 | Root + major 3rd only |
| 10 | $EA | 0 3 | Root + minor 3rd only |
| 11 | $EB | 0 5 | Root + perfect 4th |
| 12 | $EC | 0 7 | Root + perfect 5th (power chord) |

Raw bytes in source:
```
L_976F  $00 $03 $07 $88
L_9773  $00 $04 $07 $88
L_9777  $00 $03 $07 $0C $88
L_977C  $00 $04 $07 $0C $88
L_9781  $07 $0C $0F $88
L_9785  $07 $0C $10 $88
L_9789  $03 $07 $0C $88
L_978D  $04 $07 $0C $88
L_9791  $00 $0C $88
L_9794  $00 $04 $88
L_9797  $00 $03 $88
L_979A  $00 $05 $88
L_979D  $00 $07 $88
```

Semitone values up to $53 (83) are valid note offsets; $54 and above
trigger arp-pointer reset back to ARP2 (which = ARP at start, since
ARP2L/ARP2H is set to the same address as ARP/ARPH when an arp command
is first loaded).

---

## 6.  NoteFreqsL/H Table (Panther, full 84 entries)

PAL tuning, 424 Hz reference.  Stored as interleaved LoHi word table.
Note 0 = lowest note (approximately C1, ~16 Hz at SID PAL).

```
SID freq word:  (lo byte at NoteFreqsL[N*2], hi byte at NoteFreqsH[N*2])

Note  0-11 (C1–B1):
  0116 0126 0138 014B 0160 0172 0189 01A1 01BB 01D6 01F1 020E

Note 12-23 (C2–B2):
  022C 024C 0270 0296 02C0 02E4 0312 0342 0376 03AC 03E2 041C

Note 24-35 (C3–B3):
  0458 0498 04E0 052C 0580 05C8 0624 0684 06EC 0758 07C4 0838

Note 36-47 (C4–B4):
  08B0 0930 09C0 0A58 0B00 0B90 0C48 0D08 0DD8 0EB0 0F88 1070

Note 48-59 (C5–B5):
  1160 1260 1380 14B0 1600 1720 1890 1A10 1BB0 1D60 1F10 20E0

Note 60-71 (C6–B6):
  22C0 24C0 2700 2960 2C00 2E40 3120 3420 3760 3AC0 3E20 41C0

Note 72-83 (C7–B7):
  4580 4980 4E00 52C0 5800 5C80 6240 6840 6EC0 7580 7C40 8380

... plus 2 more (would be $8B00 $9300 but table is 84 entries):
  8B00 9300 9C00 A580 B000 B900 C480 D080 DD80 EB00 F880
```

(Source has 88 entries when counting the tail bytes, but the standard 84
semitone range is notes 0–83.)

Note on tuning: A4 (standard 440 Hz) would have SID freq word ≈ $1ABA at
PAL.  A4 in Panther table (note 57 in MIDI counting from C-1=0, or roughly
note 45 in Whittaker's scheme) — the 424 Hz tuning produces values
consistently ~4% below standard A=440 values.

---

## 7.  Track / Sequence Data (Panther)

Three voices, each with an independent sequence (orderlist):

**Voice 1 (Track1Seq):** 60 pattern pointers + terminator $0000
- Intro: L_9902 (1 entry)
- Main loop: L_9909 (noise/percussion), L_9934, L_996E (alternating melodic)
- Total: 60 entries

**Voice 2 (Track2Seq):** 68 pattern pointers + terminator $0000
- Intro: L_99A8 (1 entry)
- Main: L_99CD, L_99EB (two melodic variants), L_9A09, L_9A27, L_9A45, L_9A63 (bridge patterns)
- Total: 68 entries

**Voice 3 (Track3Seq):** 52 pattern pointers + terminator $0000
- Intro: L_9A81
- Bass/chord: L_9AAB (main bass riff), L_9AC9, L_9AEB, L_9B0C, L_9B2D, L_9B4F, L_9B71, L_9B93, L_9BB5
- Bridge: L_9BD0, L_9C03, L_9C36, L_9C69, L_9C9C, L_9CBD, L_9CD2
- Total: 52 entries

---

## 8.  Pattern Data Examples

**L_9902** (Voice 1 intro):
```
$BE $D0 $00 $00 $FF $80 $88
```
- $BE = note 0x3E (62 decimal) — F#5 approximately
- $D0 = note duration (medium duration)
- $00 $00 = two note 0 (C1 or rest-like)
- $FF = note 0x7F (127? — past end of 84-note table; likely silence or overflow)
- $80 = command $80 (re-gate)
- $88 = pattern end / track advance

**L_9909** (Voice 1 main noise riff):
```
$8A   ; cmd_Noise → WAVE=$80
$D0   ; duration
$40   ; note 64 = E5 approx
$00   ; note 0
$81   ; cmd $81 → clear B1D
$E0   ; arp $E0 (minor triad)
...
$88   ; pattern end
```

**L_9934** (Voice 1 pulse melodic):
```
$8B         ; cmd_Pulse → WAVE=$40
$90         ; cmd $90 → PWM sweep: read 3 bytes
$02 $08 $28 ; PWM: lo=$02, hi=$08, step=$28
$D0         ; duration
$0A         ; note 10 = A#1 approx
$40         ; note 64
...
```

**L_99CD** (Voice 2 main melody):
```
$8B         ; cmd_Pulse
$D0         ; duration
$08         ; note 8
$10         ; note 16
$89         ; cmd $89 → set B1A+B1C: 3 bytes follow
$03 $06 $82 ; B1A=3, B1C=6, (3rd byte)=$82
$90         ; cmd $90 → PWM sweep
$02 $08 $28 ; lo=$02, hi=$08, step=$28
$E0         ; arp $E0 (minor triad)
$18 $18 ... ; notes 24, 24
$88         ; pattern end
```

---

## 9.  Notes on dmx87 Partial Annotations

Several labels remain un-decoded in the disassembly (B05, B07, B08,
B0D–B0F, B19–B21).  From tracing the code:

- **B05 / B06** (initialised to 2): byte-offset into the track sequence table
  (since each entry is a 2-byte pointer, step=2 on each advance).  $88
  command (L_9304) does: load TRACK base → add B05 → load pattern ptr;
  then B05 += 2.  If the loaded pattern ptr == 0,0: reset B05 = 2.

- **B07/B08**: slide accumulator (lo/hi), written by $89 command, used
  by the SoundUpdate slide add/subtract path.

- **B0D/B0E/B0F**: sub-step counter and slide step operands.  B0F is the
  countdown; B0D and B0E are loaded from the slide parameter bytes.

- **B1A**: PWM half-range (half of max sweep).  Used to compute the
  frequency wobble in the B1D bit7 path.

- **B1B**: PWM step delta (used in PWM sweep direction control).

- **B1C**: PWM current value (accumulates B20 each frame).

- **B1D**: Bit-field for active effects:
  - bit7 ($40): PWM/freq-wobble active
  - bit6 ($20): PWM sweep direction (up/down)
  - bit3 ($04): set by $84 command (pitch-bend)

- **B21**: PWM direction state: 0=off, 1=sweep-up, $81=sweep-down.

---

## Leads to follow

1. **Full read of pspecial adc chain** (source lines ~$9744–$9782) — the
   exact cascade decode of $B8–$FF ranges.  Current analysis is based on
   code trace; the exact boundary values for duration ranges need a careful
   carry-flag simulation.

2. **B0D vs B0E ordering** — the slide path uses B0D and B0E as operands;
   the exact lo/hi assignment in $89 handler (L_939A) needs confirmation.

3. **$80 command semantics** — `L_93FB: JMP L_9431` re-enters the note-trigger
   "duration reload" path.  Verify whether this resets only the duration counter
   or also re-triggers the gate.

4. **Second dmx87 disassembly (non-Panther)** — differences between Panther
   and e.g. Red Max / Storm would reveal what changed across driver versions.
   Check the GitHub repo for additional .asm files.

5. **NoteFreqsH interleave detail** — `NoteFreqsH = NoteFreqsL + 1` suggests
   the table is stored as interleaved lo/hi words (not separate arrays).
   Confirm by checking the actual `!wo` declarations in the asm source.
