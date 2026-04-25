# Das Model — Formal Specification

## Overview

Every SID performance is determined by three components:

```
SID = (T, I, S)

T : FreqTable     — maps note indices to SID frequency values
I : Instrument[]   — behavioral rules that produce register values
S : Score          — what instrument plays what note at what time
```

The universal engine evaluates these to produce SID register writes.

## 1. Frequency Table

```
T : [0..N] → uint16

T[n] = (freq_hi[n] << 8) | freq_lo[n]
```

Standard PAL table has N=95 (96 entries). Some engines extend beyond
(Hubbard reads runtime state at indices 96+).

## 2. Instruments

An instrument defines RULES (programs) for how each SID register
behaves relative to δ (frames since note-on):

```
Instrument I = {
    W : WaveProgram       — waveform per frame
    F : FreqProgram       — frequency behavior per frame
    P : PulseProgram      — pulse width modulation rule
    E : EnvelopeSpec      — ADSR + hard restart
}
```

### 2.1 Wave Program W

W depends on BOTH δ (frame within note) and L (total note length):

```
W(δ, L) determines the SID control register ($D404) value.
```

Two components:
1. **Waveform sequence** — the upper bits (waveform select, ring, sync)
2. **Gate bit** — bit 0, depends on envelope timing

**Waveform sequence** (a finite program with loop):
```
waveform_steps = [(wave_byte, duration), ...]
```

**Case 1: Drum + arpeggio** (has_drum AND has_arpeggio):
```
δ=0: ctrl | 0x01 (gate on, native waveform)
δ=1: $80 (noise burst, gate off)
δ=2: $80 (noise burst, gate off)
δ≥3: ctrl & $FE (sustain, gate off) — LOOPS HERE
```
The noise burst occurs regardless of the instrument's native waveform.
This applies to both noise instruments (ctrl=$81) and non-noise (ctrl=$41, $15, $21).

**Case 2: Drum without arpeggio** (has_drum AND NOT has_arpeggio):
```
δ=0: ctrl | 0x01 (gate on, native waveform)
δ≥1: ctrl & $FE (gate off, KEEP native waveform — NO noise burst)
```
The drum effect slides freq_hi down but does NOT produce a noise burst.
The native waveform (pulse+sync, etc.) is maintained throughout.

**Case 3: Non-drum instruments** (has_drum=False):
```
δ=0..L-hr-1: ctrl | 0x01 (gate ON for most of note)
δ=L-hr..L-1: ctrl & $FE (gate OFF, hard restart)
```
where hr = hard_restart frames (typically 3).

**Key insight**: the gate bit is ON for most of the note in non-drum
instruments. The waveform byte doesn't change — only the gate bit
toggles at hard restart. The noise burst in drum instruments only
occurs when the instrument's native waveform IS noise ($80/$81).

### 2.2 Freq Program F

Determines the frequency written to SID each frame. Two modes:

**Mode 'table'**: frequency from table lookup with offset
```
F_table = (offsets[], loop_target)

freq(δ, base_note) = T[base_note + offsets[δ_wrapped]]
```

Example: octave arpeggio → offsets = [0, 12], loop_target = 0

**Mode 'slide'**: frequency modified directly each frame
```
F_slide = (initial_offset, delta_per_frame)

freq_hi(δ, base_note) = T[base_note].hi + delta_per_frame * δ
freq_lo(δ, base_note) = T[base_note].lo
```

Example: drum slide → delta_per_frame = -1

### 2.3 Pulse Program P

The pulse width rule. The engine maintains per-voice PW STATE;
the instrument defines the RULE applied to that state each frame.

```
PulseProgram = {
    speed     : int16      — per-frame PW delta (0 = no modulation)
    mode      : enum       — 'none' | 'linear' | 'bidirectional'
    min_hi    : uint8      — lower boundary for pw_hi (bidirectional mode)
    max_hi    : uint8      — upper boundary for pw_hi (bidirectional mode)
    init      : uint16     — initial PW value on first note with this instrument
}
```

Engine execution per frame:
```
if mode == 'none':
    pw unchanged
elif mode == 'linear':
    pw_lo += speed_lo        (8-bit wrap, pw_hi unchanged)
elif mode == 'bidirectional':
    if direction == UP:
        pw += speed          (16-bit add)
        if pw_hi >= max_hi:
            pw_hi = max_hi
            direction = DOWN
    else:
        pw -= speed          (16-bit subtract)
        if pw_hi <= min_hi:
            pw_hi = min_hi
            direction = UP
    write pw_lo to $D402+voice_offset
    write pw_hi to $D403+voice_offset
```

PW STATE carries across notes on the same voice.
On instrument change:
- Same PW mode: state continues
- To noise instrument: save pw state, load instrument init
- From noise instrument: restore saved pw state
- To different PW mode: load instrument init

### 2.4 Envelope Spec E

```
EnvelopeSpec = {
    ad              : uint8    — attack/decay register value
    sr              : uint8    — sustain/release register value
    hard_restart    : uint8    — frames before note end to zero AD/SR (typically 3)
}
```

Engine execution:
```
E(δ, note_length) =
    if δ < note_length - hard_restart:
        write ad to $D405, sr to $D406
    else:
        write $00 to $D405, $00 to $D406
```

## 3. Score

```
Score = {
    voices : Voice[3]
    tempo  : uint8              — frames per tick
}

Voice = {
    events : NoteEvent[]
    loop   : uint               — event index to loop back to
}

NoteEvent = {
    note       : uint8          — frequency table index (base pitch)
    duration   : uint8          — length in ticks
    instrument : uint8          — instrument index
}
```

The engine converts ticks to frames: `frames = duration * tempo`

## 4. Universal Engine

Per frame, for each voice v:

```
1. Advance tick counter; if expired, load next NoteEvent
2. Let δ = current frame - note_start_frame
3. Let I = instruments[current_event.instrument]
4. Let n = current_event.note

5. ctrl = I.W(δ)                                    → write $D404+v*7
6. freq = I.F(δ, n, T)                              → write $D400+v*7, $D401+v*7
7. pw   = engine.apply_pulse(I.P, voice_state[v])   → write $D402+v*7, $D403+v*7
8. (ad, sr) = I.E(δ, note_frames)                   → write $D405+v*7, $D406+v*7
```

## 5. Commando Instruments (Hubbard Engine)

Source: binary at $5000, decompiled by rh_decompile.py

### fx_flags interpretation:
```
Bit 0: drum      — noise burst on frame 0, freq_hi slides down
Bit 1: skydive   — freq_hi decreases by 1 every 2 frames (after gate off)
Bit 2: arpeggio  — octave arpeggio: alternate note+0 and note+12 every frame
Bit 3: table_arp — wave program uses arpeggio table stepping (post-1986 feature)
```

### Commando's 13 instruments:

```
 #  AD   SR   ctrl  PW     speed  fx   W(δ)                           F(δ)
 0  $29  $5F  $41   $0900  $E0    $00  gate→sustain                   table[+0] (vibrato depth 2)
 1  $06  $4B  $41   $0180  $00    $05  gate→noise→noise→sustain       table[+0,+12] arp
 2  $09  $9F  $41   $0180  $16    $08  gate→sustain                   table[+0]
 3  $0A  $09  $81   $0200  $00    $05  gate→noise→noise→sustain       table[+0,+12] arp (noise waveform)
 4  $0F  $C4  $43   $0200  $00    $03  gate→noise→noise→sustain       slide(-1) + skydive
 5  $05  $A9  $41   $0880  $02    $0D  gate→noise→noise→sustain       table[+0,+12] arp + table_arp
 6  $38  $7A  $41   $0800  $E0    $00  gate→sustain                   table[+0] (vibrato depth 2)
 7  $0D  $FB  $15   $0180  $00    $05  gate→noise→noise→sustain       table[+0,+12] arp (tri+pulse)
 8  $49  $5B  $41   $0800  $03    $08  gate→sustain                   table[+0] (vibrato depth 2)
 9  $04  $6F  $21   $0800  $00    $05  gate→noise→noise→sustain       table[+0,+12] arp (sawtooth)
10  $09  $6B  $41   $0300  $01    $0D  gate→noise→noise→sustain       table[+0,+12] arp + table_arp
11  $07  $09  $43   $0200  $00    $01  gate→noise→noise→sustain       slide(-1) drum
12  $09  $0A  $41   $0800  $00    $01  gate→noise→noise→sustain       slide(-1) drum
```

### Pulse modulation parameters (Commando player constants):
```
Bidirectional mode boundaries: min_phi=$08, max_phi=$0E
Speed is per-instrument: $E0 (insts 0,6), $16 (inst 2), $02 (inst 5), $03 (inst 8), $01 (inst 10)
```

### Frequency table:
```
T[0..95]  = standard PAL C64 frequency table
T[96..107] = Hubbard runtime state (read via py65 after init+play)
             T[100] = $0303 (used by octave arpeggio from note 88)
```
