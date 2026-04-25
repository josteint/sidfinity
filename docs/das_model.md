# Das Model — Formal Specification

## 1. Overview

Every SID performance is determined by three components:

```
SID = (T, I, S)

T : Frequency Table
I : Instrument[]
S : Score
```

A universal engine evaluates these to produce SID register writes.
The engine is fixed — it never changes. All musical variation comes
from T, I, and S.

## 2. Frequency Table

```
T : [0..N] → uint16
```

A lookup array mapping note indices to 16-bit SID frequency values.
The engine indexes into T to get frequency register values.
The table contents are song-specific (extracted from the binary).

## 3. Instruments

An instrument is a collection of PROGRAMS that the engine executes
per frame. The engine does not interpret these programs — it
evaluates them mechanically.

```
Instrument = {
    W : WaveProgram
    F : FreqProgram
    P : PulseProgram
    E : EnvelopeSpec
}
```

### 3.1 Wave Program (W)

A finite sequence of waveform bytes with a loop point.

```
W = {
    steps : uint8[]       — one SID control byte ($D404 value) per frame
    loop  : uint          — index to loop back to after last step
}
```

The engine writes `W.steps[step]` to the SID control register each frame,
advancing `step` by one. When `step` reaches `len(steps)`, it resets to
`loop`.

The engine does not interpret the waveform byte. It does not know about
gate bits, noise bursts, or waveform types. It writes the byte as-is.

### 3.2 Freq Program (F)

A finite sequence of note offsets with a loop point.

```
F = {
    offsets : int8[]      — note offset per frame (added to base note)
    loop   : uint         — index to loop back to after last offset
}
```

Each frame, the engine computes: `freq = T[base_note + F.offsets[step]]`
and writes freq_lo and freq_hi to SID registers $D400/$D401.

The engine does not know about arpeggio, vibrato, or portamento.
It adds the offset and does the table lookup.

### 3.3 Pulse Program (P)

Defines how pulse width evolves per frame. The engine maintains a
per-voice PW accumulator that carries across notes.

```
P = {
    speed    : int16      — per-frame PW delta (0 = no modulation)
    mode     : enum       — 'none' | 'linear' | 'bidirectional'
    min_hi   : uint8      — lower boundary (bidirectional only)
    max_hi   : uint8      — upper boundary (bidirectional only)
    init_pw  : uint16     — initial PW value for this instrument
}
```

Engine execution per frame:
```
if mode == 'none':
    (no change)
elif mode == 'linear':
    pw_lo = (pw_lo + speed_lo) & $FF     — 8-bit wrap, pw_hi unchanged
elif mode == 'bidirectional':
    if direction == UP:
        pw += speed                       — 16-bit add
        if pw_hi >= max_hi: direction = DOWN
    else:
        pw -= speed                       — 16-bit subtract
        if pw_hi <= min_hi: direction = UP
write pw_lo, pw_hi to SID $D402/$D403
```

PW state (accumulator, direction) persists across notes on the same voice.
On instrument change: init_pw is loaded only if the PW mode changes.

### 3.4 Envelope Spec (E)

```
E = {
    ad            : uint8    — attack/decay register value
    sr            : uint8    — sustain/release register value
    gate_off_delta : uint8   — frames before note end to turn gate off (0 = never)
    adsr_zero_delta : uint8  — frames before note end to zero AD/SR (0 = never)
}
```

Engine execution:
```
let remaining = note_end_frame - current_frame

if remaining == adsr_zero_delta:
    write $00 to AD register, $00 to SR register
elif note is active:
    write E.ad to AD register, E.sr to SR register

if remaining == gate_off_delta:
    clear bit 0 of the ctrl register (gate off)
```

The engine does not know about "hard restart." It zeroes ADSR and clears
gate at the frame offsets specified by the instrument.

## 4. Score

```
Score = {
    tempo  : uint8          — frames per tick
    voices : Voice[3]
}

Voice = {
    events : NoteEvent[]
    loop   : uint           — event index to loop back to (-1 = no loop)
}

NoteEvent = {
    note       : uint8     — frequency table index (base pitch)
    duration   : uint8     — length in ticks
    instrument : uint8     — instrument index
}
```

The engine converts ticks to frames: `note_frames = duration * tempo`

## 5. Universal Engine

The engine evaluates SID = (T, I, S) per frame. For each voice:

```
1. tick_counter--
   if tick_counter == 0:
       load next NoteEvent from Score
       set tick_counter = duration * tempo
       set base_note = event.note
       load instrument I[event.instrument]
       reset W.step and F.step to 0

2. W: write W.steps[step] to $D404+voice_offset
      advance step (loop if past end)
      
      if remaining frames == E.gate_off_delta:
          clear bit 0 of $D404+voice_offset

3. F: freq = T[base_note + F.offsets[step]]
      write freq_lo to $D400, freq_hi to $D401
      advance step (loop if past end)

4. P: apply pulse program to accumulator
      write pw_lo to $D402, pw_hi to $D403

5. E: if remaining frames == E.adsr_zero_delta:
          write $00 to $D405, $00 to $D406
      else:
          write E.ad to $D405, E.sr to $D406
```

That is the complete engine. It has no knowledge of any specific
SID player engine, effect type, or musical concept. It reads programs
and data, evaluates them mechanically, and writes SID registers.

## 6. Instrument Extraction

Instruments are created by per-engine DECOMPILERS that read the
original SID binary and translate engine-specific parameters into
(W, F, P, E) programs.

For example, a Hubbard decompiler reads fx_flags and builds:
- W program with noise burst frames if the flags indicate drum+arp
- F program with +12 offsets if the flags indicate octave arpeggio
- P program with the instrument's PW speed and boundaries
- E spec with the instrument's AD/SR and the engine's HR timing

A GT2 decompiler would read wave/pulse/filter tables and build
different W/F/P/E programs from those.

The decompiler is engine-specific. The instrument format is universal.
The engine evaluates any instrument the same way, regardless of which
decompiler created it.
