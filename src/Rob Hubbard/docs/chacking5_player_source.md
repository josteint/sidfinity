---
source_url: http://csbruce.com/cbm/hacking/hacking05.txt
fetched_via: direct
fetch_date: 2026-04-21
author: Anthony McSweeney
content_date: 1993-03
reliability: primary
---

# C=Hacking Issue 5 — Rob Hubbard's Music: Disassembled, Commented and Explained

**Article:** "Rob Hubbard's Music: Disassembled, Commented and Explained"
**Author:** Anthony McSweeney
**Publication:** C=Hacking #5, March 7, 1993
**Source:** http://csbruce.com/cbm/hacking/hacking05.txt
**Mirror:** https://www.1xn.org/text/C64/rob_hubbards_music.txt

This is the primary technical reference for the Rob Hubbard driver. The routine was ripped from
Monty on the Run (loads at $8000-$9554 approx), with soundfx code removed for clarity.
The same driver was used in Confuzion, Thing on a Spring, Action Biker, and Crazy Comets.

---

## Speed Counter

### Variables
```assembly
speed      .byt $00
resetspd   .byt $01    ; Monty uses speed=1
```

### Counter decrement/reset loop
```assembly
dec speed        ;check the speed
bpl mainloop     ;still positive — skip note work

lda resetspd     ;reload default speed
sta speed
; ... proceed to note work
```

**Key formula from the article:**
> "The speed for Monty on the Run is 1, which means that a note of length $1f will last for
> 64 calls to the routine (ie just over a second)."

**Unpacking this formula:**
- `speed` starts at 1 (resetspd = 1)
- Each frame: `dec speed` → speed goes 1, 0, -1 (BPL fails) → reset to 1
- So note work fires every 2 frames (speed+1 = 2 frames per tick)
- Note length bits 0-4 give value 0-31
- A note with length $1f = 31 means `dec lengthleft` fires 31+1=32 times before bmi triggers
  Wait: 32 ticks × 2 frames/tick = 64 frames ≈ 1.28 seconds at 50Hz. ✓

**Frame count formula:**
```
frames_per_tick = resetspd + 1
note_frames = (note_length_bits + 1) * frames_per_tick
           = (note_length_bits + 1) * (resetspd + 1)
```

Where `note_length_bits` = byte1 & 0x1F (0-31).

### No nested speed counters in this driver
The article confirms: "no nested speed counters or tempo changes" in the core Monty driver.
The speed is a single global value, uniform for all 3 channels.

---

## Note Format (variable-length, 2-4 bytes)

### First byte always present: length + control flags
```
Bits 0-4: Note duration (0-31)
Bit 5:    No-release flag (gate not cleared at note end)
Bit 6:    Tie/append flag (no re-trigger, no new attack)
Bit 7:    New instrument or portamento byte follows (if set, byte 2 present)
```

### Parsing code
```assembly
lda ($04),y      ;get length of note
sta savelnthcc,x
sta templnthcc
and #$1f         ;mask to 5-bit length
sta lengthleft,x

bit templnthcc   ;test bit 6 (append/tie)
bvs appendnote   ;skip new instrument if tied

lda templnthcc   ;test bit 7
bpl getpitch     ;skip 2nd byte if clear

iny              ;byte 2 present
lda ($04),y
bpl isinstr      ;positive = instrument number
sta portaval,x   ;negative = portamento value
jmp getpitch
isinstr:
sta instrnr,x

getpitch:
iny              ;get pitch byte
lda ($04),y
sta notenum,x
```

### Second byte (only if byte1 bit7 set)
- Bit 7 clear (positive): New instrument number (0-N)
- Bit 7 set (negative): Portamento command
  - Bits 1-6: Speed
  - Bit 0: Direction (0=up, 1=down)

### Third byte: Pitch value
- 0-95: Pitch index into frequency table
- 96+: Out-of-range — indexes into player variables (frequency table trick)

---

## Note Duration Decrement

```assembly
dec lengthleft,x  ;decrement remaining frames
bmi getnewnote    ;fetch new note when expired (<0)
jmp soundwork     ;still sounding — just do per-frame effects
```

The counter decrements each frame tick only (after speed counter fires).
Wait: actually looking at the code flow — lengthleft decrements once per driver call
when the speed counter has expired. The outer loop:

```assembly
mainloop:
  dec speed
  bpl mainloop_end  ; (skip note work if speed not expired)
  lda resetspd
  sta speed
  ; --- note work for all 3 channels ---
  ldx #2
noteloop:
  dec lengthleft,x
  bmi getnewnote
  jmp soundwork
```

So `lengthleft` decrements once per `resetspd+1` frames.

---

## Track / Pattern Parsing

### Song structure (6 bytes per song)
Songs are indexed by a lookup table. Each song has:
- 3 lo bytes for channel 1/2/3 track pointers
- 3 hi bytes for channel 1/2/3 track pointers

### Track: sequence of pattern numbers terminated by $FF or $FE
```assembly
lda ($02),y      ;get current track entry
cmp #$ff         ;$FF = restart track from beginning (loop)
beq restart
cmp #$fe         ;$FE = stop music on all channels
bne getnotedata
jmp musicend
```

### Pattern: sequence of note data terminated by $FF
```assembly
lda ($04),y      ;get note data
cmp #$ff         ;$FF = end of pattern
beq nextpattern  ;advance to next pattern in track
```

### Zero page indirect pointers
```
$02/$03: Current track pointer (channel-indexed)
$04/$05: Current pattern pointer (channel-indexed)
```

---

## Vibrato Implementation

```assembly
lda counter      ; global frame counter
and #7           ; 3-bit mask → values 0-7
cmp #4
bcc +
eor #7           ; invert upper half → triangle wave 01233210
+:
sta oscilatval
```

**Commentary from article:** "This is clever!! counter turns into oscillating value (01233210)"
This creates a triangle wave LFO without a sine table.

Vibrato delta is computed as the difference between the current note frequency and the
next-lower semitone in the frequency table (logarithmic vibrato scaling).

---

## Instrument Format (8 bytes each)

```
Offset 0: PW low byte
Offset 1: PW high byte
Offset 2: SID control register (waveform + gate/sync/ring/test bits)
Offset 3: Attack/Decay (ADSR)
Offset 4: Sustain/Release (ADSR)
Offset 5: Vibrato depth
Offset 6: Pulse width modulation speed
Offset 7: Effects flags (bit field)
```

### Effects flags (byte 7)
- Bit 0 (0x01): Drum — rapid freq slide down, fast decay
- Bit 1 (0x02): Skydive — decrements freq_hi every other frame (pitch dive)
- Bit 2 (0x04): Octave arpeggio — alternates base note and base+12 each frame

---

## Pulse Width Modulation

PWM oscillates the pulse width continuously using the `pwm_speed` byte from the instrument:
```assembly
lda pulsedir,x
beq pwidthup      ; direction 0 = going up
lda pulsehi,x
cmp #$0e
beq pwidthup      ; wrap at $0E00
inc pulsehi,x     ; wait — actually DEC going down?
bne donewidth
; ...
```
PWM sweeps between approximately $0800 (50%) and $0E00 (88%).

---

## Hard Restart Sequence

When a note's duration expires, the driver:
1. Clears the gate bit from the control register
2. Sets ADSR to $00/$00 (silent, fast release)
3. On new note: writes control, then AD, then SR (in that order)

This is the "hard restart" technique to ensure sharp attack.

---

## Variable Declarations

```assembly
tempstore  .byt $00
posoffset  .byt $00,$00,$00  ; pattern position per channel
patoffset  .byt $00,$00,$00  ; track position per channel
lengthleft .byt $00,$00,$00  ; remaining note frames per channel
savelnthcc .byt $00,$00,$00  ; saved note length per channel
voicectrl  .byt $00,$00,$00  ; SID control shadow per channel
notenum    .byt $00,$00,$00  ; current pitch per channel
instrnr    .byt $00,$00,$00  ; current instrument per channel
pulsedelay .byt $00,$00,$00  ; PWM phase per channel
pulsedir   .byt $00,$00,$00  ; PWM direction per channel
savefreqhi .byt $00,$00,$00  ; current freq hi per channel
savefreqlo .byt $00,$00,$00  ; current freq lo per channel
portaval   .byt $00,$00,$00  ; portamento speed+dir per channel
counter    .byt $00           ; global frame counter (for vibrato)
mstatus    .byt $c0           ; music status byte
speed      .byt $00           ; speed counter (counts down)
resetspd   .byt $01           ; speed reset value (default=1)
```

---

## Notes on Driver Scope

The article notes:
- The routine is ~900-1000 bytes of code
- The same routine (with slight modifications) was used in Confuzion, Thing on a Spring,
  Monty on the Run, Action Biker, Crazy Comets, Commando
- Later songs differ in additional features, especially International Karate (pattern transposition)
- The article does NOT cover later driver features (arpeggio tables, PCM, filter control, 4th channel)
