# Hubbard Commando Feature Inventory

Derived from exact Python reimplementation (`src/hubbard_emu.py`) verified 100% against
py65 6502 emulator for 500 frames (10,500 SID register comparisons, zero mismatches).

See also: `docs/hubbard_commando_disassembly.s` for the fully-commented 6502 listing.

## State Variable Map

| Python attribute | 6502 address | Purpose |
|---|---|---|
| `speed_ctr` | $5513 | Speed counter (decremented once per frame at X=2 loop entry) |
| `resetspd` | $5517 | Speed reset value (tick every resetspd+1 frames) |
| `mode_byte` | $5519 | State machine: $40=first frame, $80=end-of-song, $00=normal |
| `frame_ctr` | $5525 | Global frame counter (0-255, wraps, incremented every play call) |
| `drum_inhibit` | $5526 | Nonzero = skip drum engine (set when voice is playing drum pattern) |
| `drum_state` | $5527 | $FF=ready-for-drum-init, $00-$0F=active drum idx, negative=end-of-song |
| `drum_enable` | $5528 | $FF=drum output DISABLED (SID writes allowed), $00=drum output ENABLED |
| `seq_idx[v]` | $54EC,X | Sequence index: which slot in voice's song sequence |
| `note_idx[v]` | $54EF,X | Note index: byte offset within current pattern |
| `duration[v]` | $54F2,X | Duration countdown (decrements on each tick frame) |
| `note_byte[v]` | $54F5,X | Raw note byte 0 (flags + duration field) |
| `ctrl_byte[v]` | $54F8,X | Instrument ctrl byte (stored for gate control on release) |
| `pitch[v]` | $54FB,X | Current pitch index (0-95, into freq table) |
| `instr_num[v]` | $54FE,X | Current instrument number (0-15) |
| `drum_trig[v]` | $5520,X | Drum trigger byte ($00=none, bit7=drum) |
| `freq_hi[v]` | $551A,X | Current freq_hi (modified by skydive/arpeggio) |
| `freq_lo[v]` | $551D,X | Current freq_lo (modified by portamento/drum slide) |
| `pw_period[v]` | $550D,X | PW oscillation period counter (bidirectional mode) |
| `pw_dir[v]` | $5510,X | PW oscillation direction flag (0=rising, nonzero=falling) |

## Musical Features

### 1. Tempo

**Code**: $5054-$505C (DEC $5513, BMI reload, LDA $5517, STA $5513)
**Mechanism**: The speed counter is decremented ONCE per play frame (only when processing
voice X=2, the first in the loop). All three voices share the same counter and see the same
tick/no-tick decision for that frame. A "tick" occurs when the counter underflows and is
reloaded: `speed_ctr = resetspd`.
**Note advance**: All voices advance notes simultaneously on tick frames.
**Commando song 0**: resetspd=$02 → tick every 3 frames → 50/3 ≈ 16.7 Hz note rate.
**Das Model status**: Implemented (but nested counter case not handled).

### 2. Note Format (Pattern Byte Encoding)

**Code**: $50C2-$50F0 (note reading section)
**Format**:
- Byte 0: `bit7=has_instrument`, `bit6=tie`, `bit5=no_release`, `bits4-0=duration`
- Byte 1 (if bit7 set): `bit7=drum_trigger`, `bits6-0=instrument_number`
- Byte 2: pitch index (0-95, into freq table at $5428)
**Tie** (bit6): gate-enable set to $FE (ANDed with ctrl clears gate) — re-uses running note.
**No-release** (bit5): gate not cleared at end of note (legato/slur).
**Duration**: 1-31 ticks; total frame duration = `duration * (resetspd+1)`.
**Das Model status**: Partially implemented. Tie and no-release need verification.

### 3. Frequency Table

**Code**: $50FA-$5112 (freq lookup on new note)
**Format**: Interleaved lo/hi pairs at $5428. `freq_lo[n]=$5428+n*2`, `freq_hi[n]=$5429+n*2`.
**Entries**: 96 words (192 bytes) at $5428-$54E7. Covers ~8 octaves of C64 PAL freq values.
**Das Model status**: Implemented.

### 4. Instrument Table

**Code**: $5128-$5153 (instrument write on new note)
**Format**: 8 bytes per instrument at $5591+instr*8:
- `+0`: pw_lo, `+1`: pw_hi (pulse width, 12-bit)
- `+2`: ctrl (SID waveform + gate bits)
- `+3`: AD (attack/decay), `+4`: SR (sustain/release)
- `+5`: vib_depth (vibrato depth), `+6`: pwm_speed (PW modulation speed)
- `+7`: fx_flags (feature bits)
**Instrument data written to SID only when `drum_enable=$FF` (drum output disabled)**.
On new-note-read frames, instrument is written but effects are NOT applied (code jumps
directly to $538F after the note read, skipping $519B).
**Das Model status**: Implemented.

### 5. Vibrato

**Code**: $51C1-$5229
**Mechanism**: Triangular vibrato envelope over 8 frames (steps: 0,1,2,3,3,2,1,0).
Computed by taking the frequency difference between current and next semitone, then
right-shifting it `(vib_depth+1)` times to get the per-step delta. The envelope step
count times this delta is added to the base frequency.
**Condition**: Only active when note `duration_field >= 6` (short notes get no vibrato).
**Effect**: Writes to `D400,Y` and `D401,Y` (freq_lo/hi) every frame.
**Commando instruments**: Instr 0 (vib=2), Instr 6 (vib=2), Instr 8 (vib=2) etc.
**Das Model status**: NOT implemented. Critical missing feature for melody voices.

### 6. Pulse Width Modulation (PW) — Unidirectional

**Code**: $5237-$5248 (fx_flags bit3=1)
**Mechanism**: Each frame, add `pwm_speed` to `pw_lo` (in-place in instrument table).
The addition wraps at 8 bits. PW_hi is unchanged. Result written to `D402,Y`.
**Commando instruments**: Instr 2 (pwm=$16), Instr 5 (pwm=$02), Instr 8 (pwm=$03).
**Das Model status**: NOT implemented as continuous per-frame modification.

### 7. Pulse Width Modulation (PW) — Bidirectional Oscillation

**Code**: $524C-$52B2 (fx_flags bit3=0, pwm_speed!=0)
**Mechanism**: Period counter (`pw_period[v]`) counts down; when it expires (reloads from
`pwm_speed & $1F`), the PW is stepped by `pwm_speed & $E0` (upper 3 bits as step size).
Oscillates PW_hi between $08xx and $0Exx, reversing direction at boundaries.
**Direction flag** (`pw_dir[v]`): 0=rising, nonzero=falling.
**Commando instruments**: Instr 0 (pwm=$E0, period=0, step=$E0).
**Das Model status**: NOT implemented.

### 8. Drum Slide (per-note trigger)

**Code**: $52B3-$52F9 (drum_trig[v] != 0)
**Mechanism**: When a note is played with `bit7` set in the instrument byte, the drum trigger
is stored. Each frame: extract delta from bits 6-1, direction from bit 0. Add/subtract from
`freq_lo`/`freq_hi`. Written to `D400,Y` and `D401,Y`.
**Effect**: Per-voice frequency slide effect (pitch sweep on individual notes).
**Das Model status**: NOT implemented (drum trigger bit encoding not decoded).

### 9. Skydive (freq_hi decrement)

**Code**: $52FA-$5335 (fx_flags bit0=1)
**Mechanism**: Each sustain frame: if freq_hi != 0 and duration != 0, decrement freq_hi by 1.
Handles two phases:
- Note-start phase (dur-1 < countdown): write freq_hi and $80 to ctrl (noise+gate).
- Sustain phase (dur-1 >= countdown): decrement freq_hi, write old value to SID.
  If `ctrl & $FE != 0` (waveform active), writes `ctrl & $FE` (gate off) to D404.
  If `ctrl & $FE == 0`, writes new (decremented) freq_hi then $80 to D404.
**Commando instruments**: Instr 1, 3, 7, 9 (fx bit0 set).
**Das Model status**: NOT implemented. Important for drum/percussive effects.

### 10. Arpeggio (octave alternation, fx bit2)

**Code**: $535E-$538E (fx_flags bit2=1)
**Mechanism**: Alternates freq every frame between base pitch and pitch+12.
On odd frames: `arp_pitch = pitch + 12`.
On even frames: `arp_pitch = pitch`.
Freq table lookup at `$5428 + arp_pitch * 2` written to SID each frame.
**The +12 Hubbard trick**: Pitch+12 for high notes (88+12=100) reads beyond the 96-entry
freq table into player state variables ($54F0 = note_idx[1], $54F1 = note_idx[2]).
These hold low values (typically 3-7) producing very low frequencies = percussive buzzing.
**Commando instruments**: Instr 1 (DRUM+ARPEGGIO), Instr 3, 5, 7, 9 (fx bits 0,2).
**Das Model status**: PARTIALLY implemented (ext. freq table for high notes). The key
insight (reading runtime state memory) is captured in the extended freq table approach.

### 11. Arpeggio with Skydive (fx bit1)

**Code**: $5336-$535D (fx_flags bit1=1)
**Mechanism**: On odd frames, if freq_hi != 0 and duration_field >= 3:
increment freq_hi by 2 (in memory), but write the PRE-increment value to D401.
This produces a slight pitch-up on alternating frames.
**Combined with bit0**: When both bit0 and bit1 are set, the skydive section may modify
freq_hi before the bit1 section reads it.
**Commando instruments**: Instr 4 (fx=$03 = bit0+bit1 = DRUM+SKYDIVE combination).
**Das Model status**: NOT implemented.

### 12. Gate Release

**Code**: $518B-$5198 (sustain path, duration=0, no no_release)
**Mechanism**: When duration countdown reaches 0 and no_release (bit5) is not set:
write `ctrl & $FE` (gate cleared) to D404, then write $00 to D405 and D406 (clear AD/SR).
This triggers the SID envelope release phase.
**Das Model status**: Implemented.

### 13. Sequence / Pattern Navigation

**Code**: $5086-$5171 (sequence reading)
**Song sequence**: Per-voice list of pattern indices. $FF = wrap to start. $FE = end of song.
**Pattern end**: When note peek at `note_idx` shows $FF: reset note_idx=0, advance seq_idx.
**Die format**: Sequences stored as byte arrays at song-specific addresses. Per-song init
copies 6 bytes (3 lo + 3 hi pointers) from song table into $56F9-$56FE.
**Das Model status**: Implemented.

### 14. Drum Engine

**Code**: $53A5-$5427, subroutine $5531-$5590
**Mechanism**: Virtual 4th channel using SID V1 and V2 for percussion.
Initialized when `$5527 bit6=1` (first time after drum_state=$FF).
Steps through a freq table sequence (ascending or descending based on drum_flags bits 5-4).
Writes V1/V2 freq based on drum_counter position; V2 offset from V1 by `drum_intv`.
Gate bits toggled each step for rhythmic gating.
16 drum patterns in table at $55F9, each 16 bytes.
**Sub-counter** ($552A): Controls timing within drum pattern (reload from `drum_flags & $0F`).
**Das Model status**: NOT implemented. The drum engine is entirely separate from the voice
effects described in the rh_to_usf converter.

## Critical Implementation Notes for Das Model

### Voice Processing Order
Voices processed X=2→X=1→X=0 (V3→V2→V1). Speed counter decremented ONCE (only at
X=2 entry). All voices share the same tick decision.

### Effects Not Applied on New-Note Frames
After reading a new note ($5086-$5171), code jumps to $538F directly, BYPASSING the
effects section at $519B. Effects (vibrato, PW, skydive, arpeggio) only apply on:
- Non-tick frames (sustain frames where duration > 0)
- Tick sustain frames (duration expired but still counting down)

### Drum Output Enable ($5528)
$5528=$FF (drum DISABLED) allows normal instrument writes to SID.
$5528=$00 (drum ENABLED) prevents instrument writes (drum engine owns SID V1/V2).
The drum_enable flag is updated after EACH voice (at $538F) based on $5526 and $5527.

### Live State Memory Overlay
The Hubbard arpeggio trick reads beyond the freq table into player state memory.
A Python emulator must maintain a "live state" mapping from 6502 addresses to current
Python attribute values, so that `_rb(addr)` for addr > $54E7 returns runtime state.

### Self-Modifying Code
The drum direction is implemented by patching the opcode at $53DE:
- $CE (DEC) = drum counter decrements (freq table scanned downward)
- $EE (INC) = drum counter increments (freq table scanned upward)
This is reflected in `drum_step_op` in the Python emulator.

## What Das Model Needs to Implement

| Feature | Priority | Notes |
|---|---|---|
| Vibrato | HIGH | Per-instrument, triangular, 8-frame period; condition dur_field>=6 |
| Skydive (fx bit0) | HIGH | Per-instrument freq_hi decrement with complex ctrl handling |
| Arpeggio (fx bit2) | MEDIUM | Already partially done via ext. freq table |
| PW modulation | MEDIUM | Both unidirectional and bidirectional modes |
| Drum engine | HIGH | Entirely separate from voice engine; major missing feature |
| Drum slide | MEDIUM | Per-note freq slide encoded in instrument byte |
| Arpeggio+skydive (bit1) | LOW | Only in instrument 4 (Commando) |
