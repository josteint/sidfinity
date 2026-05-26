# Das Model — Formal Specification

## 1. Overview

Every SID performance is determined by four components:

```
SID = (T, I, S, Ω)

T : Frequency Table
I : Instrument[]
S : Score
Ω : Timing Schedule
```

A universal engine evaluates these to produce SID register writes.
The engine is fixed — it never changes. All musical variation comes
from T, I, S, and Ω.

**Core principle:** Instruments are behavioral PROGRAMS extracted from the
binary, not detected from register output. The decompiler is engine-specific;
the engine that executes the programs is universal.

## 2. Frequency Table

```
T : [0..N] → uint16
```

A lookup array mapping note indices to 16-bit SID frequency values.
The engine indexes into T to get frequency register values.
The table contents are song-specific (extracted from the binary).

### 2.1 Static vs Dynamic Entries

Entries T[0..95] are typically static (extracted from the binary at load
time). Entries T[96+] may be dynamic: their values are computed from engine
state at runtime and written into the table at the start of each frame before
voice evaluation begins.

The specific meaning of each dynamic entry is engine-specific. The engine
reads T[i] uniformly — it does not know or care whether T[i] is static or
dynamic.

**Example (Hubbard engine):** T[100] encodes the accumulated pattern-byte
offset for voices 2 and 3. T[100].lo = V2 hub_off, T[100].hi = V3 hub_off.
These are updated each frame from live engine state before voice evaluation.

### 2.2 Freq Write Skip

On eval frames (not note-load frames), the engine may skip writing the
frequency registers for instruments that have no arpeggio program active.
This is not an optimisation — it replicates the original engine's exact
register-write pattern. The frequency remains whatever was loaded at
note-start.

Formally: `write_freq_on_eval = (F.arp_offset != 0)`.

When `write_freq_on_eval` is false, the freq registers for that voice are not
touched during the eval path. They retain the value written during note-load.

## 3. Instruments

An instrument is a collection of PROGRAMS that the engine executes per frame.
The engine does not interpret these programs — it evaluates them mechanically.

```
Instrument = {
    W : WaveProgram
    F : FreqProgram
    P : PulseProgram
    E : EnvelopeSpec
    V : VibratoProgram      -- may be null (no vibrato)
}
```

### 3.1 Wave Program (W)

A finite sequence of waveform bytes with a loop point.

```
W = {
    steps : uint8[]       -- one SID control byte ($D404 value) per frame
    loop  : uint          -- index to loop back to after last step
}
```

The engine writes `W.steps[step]` to the SID control register each frame,
advancing `step` by one. When `step` reaches `len(steps)`, it resets to
`loop`.

The engine does not interpret the waveform byte. It does not know about gate
bits, noise bursts, or waveform types. It writes the byte as-is.

**Gate-off override:** The engine checks the remaining frame count against
`E.gate_off_delta`. If the check triggers, the gate bit (bit 0) is cleared in
the value before writing, regardless of what W.steps contains. See §3.4.

### 3.2 Freq Program (F)

Defines per-frame frequency modulation. In the simplest case this is a static
arpeggio offset. In general it is a program with a loop point.

```
F = {
    arp_offset : uint8     -- semitone offset added to base_note on every
                           -- eval frame when frame_counter bit 0 is set
                           -- (0 = no arpeggio)
}
```

Each frame where arpeggio is active:
```
if frame_counter & 1:
    idx = base_note + F.arp_offset
else:
    idx = base_note
freq = T[idx]
write freq_lo to $D400+voice_offset, freq_hi to $D401+voice_offset
```

The engine does not know about the musical meaning of arp_offset. It adds the
value and does the table lookup.

**Freq write on note-load:** When a new note is loaded, the engine always
writes freq from T[base_note] regardless of arp_offset (even for non-arp
instruments). This establishes the base frequency for the note. Subsequent
eval frames then apply the arp alternation (or skip the write if arp_offset
is 0).

### 3.3 Vibrato Program (V)

A triangle LFO that modulates frequency. The LFO runs on a global frame
counter, independent of per-note timing.

```
V = {
    scale  : uint8     -- right-shift count applied to the frequency delta
                       -- (0 = no vibrato; higher = shallower modulation)
    delay  : uint8     -- frames into the note before vibrato activates
                       -- (vibrato is silent for the first `delay` frames)
}
```

LFO shape: triangle wave derived from the global frame counter.
The LFO index runs 0–7 repeating. The triangle shape maps index → depth:

```
lfo_depth[i] = [0, 1, 2, 3, 3, 2, 1, 0][i]   -- period 8 frames
```

The frequency delta per frame:

```
lfo_i = frame_counter & 7
depth = lfo_depth[lfo_i]
delta = (T[base_note + 1] - T[base_note]) >> V.scale
modulation = delta * depth
write T[base_note] + modulation to freq registers
```

Activation condition:

```
frames_into_note = note_len - tick_ctr
if frames_into_note >= V.delay:
    apply vibrato
else:
    write T[base_note] (no modulation)
```

When `V` is null (no vibrato), the engine does not modulate frequency and
writes freq only as described in §3.2.

The engine does not know about LFO shapes, musical vibrato, or modulation
depth. It evaluates the program parameters mechanically.

### 3.4 Pulse Program (P)

Defines how pulse width evolves per frame. The engine maintains a per-voice
PW accumulator that carries across notes.

```
P = {
    speed    : uint8       -- per-frame PW delta magnitude (0 = no modulation)
    mode     : enum        -- 'none' | 'linear' | 'bidirectional'
    min_hi   : uint8       -- lower boundary on pw_hi (bidirectional only)
    max_hi   : uint8       -- upper boundary on pw_hi (bidirectional only)
    init_pw  : uint16      -- initial PW value for this instrument
}
```

Engine execution per frame (accumulate-then-write order):

```
-- Accumulation phase (skip on note-load frame):
if mode == 'none' or tick_ctr == note_len:
    (no accumulation)
elif mode == 'linear':
    pw_lo = (pw_lo + speed) & $FF     -- 8-bit wrap, pw_hi unchanged
elif mode == 'bidirectional':
    if pw_dir == UP:
        (pw_hi, pw_lo) += speed       -- 16-bit add
        if pw_hi == max_hi: pw_dir = DOWN
    else:
        (pw_hi, pw_lo) -= speed       -- 16-bit subtract
        if pw_hi == min_hi: pw_dir = UP

-- Write phase (always):
write pw_lo to $D402+voice_offset
write pw_hi to $D403+voice_offset
```

**PW state persistence:** pw_lo, pw_hi, and pw_dir persist across notes on
the same voice. On instrument change: init_pw is loaded into pw_lo/pw_hi only
if the instrument actually changes (a new instrument ID is seen). Changing to
the same instrument keeps the accumulator running.

**Shared mutable PW state:** After writing PW to the SID, the engine writes
the current pw_lo and pw_hi values BACK into the instrument table. This means
the instrument table is MUTABLE at runtime: `i_pwlo[inst_id] = pw_lo` and
`i_pwhi[inst_id] = pw_hi`. When any voice later loads this instrument (or
when the same voice re-loads it), it reads the accumulated value, not the
original init_pw. This is not a side effect to be avoided — it is the
specified behavior.

Cross-voice sharing: if voice A and voice B use the same instrument ID,
whichever voice ran last has written its accumulated PW back to the shared
table. The next voice to load that instrument inherits the accumulated value.
The order in which voices are evaluated within a frame determines which
accumulated value survives to the next frame.

### 3.5 Envelope Spec (E)

```
E = {
    ad             : uint8    -- attack/decay register value
    sr             : uint8    -- sustain/release register value
    gate_off_delta : uint8    -- when tick_ctr reaches this value (counting
                              -- down), clear gate bit before writing ctrl
                              -- (0 = never clear gate early)
    adsr_zero_delta : uint8   -- when tick_ctr reaches this value, write
                              -- $00 to both AD and SR registers
                              -- (0 = never zero ADSR early)
}
```

Engine execution per frame:

```
if tick_ctr == E.adsr_zero_delta:
    write $00 to $D405+voice_offset
    write $00 to $D406+voice_offset
else:
    write E.ad to $D405+voice_offset
    write E.sr to $D406+voice_offset

if tick_ctr <= E.gate_off_delta:
    clear bit 0 of the ctrl register value before writing it (gate off)
```

ADSR writes happen AFTER the ctrl register write within each frame (the
engine's register write order is freq → ctrl → pw → adsr). See §5 (Ω).

The engine does not know about "hard restart." It zeroes ADSR and clears gate
at the frame offsets specified by the instrument.

## 4. Score

```
Score = {
    tempo  : uint8          -- frames per tick
    voices : Voice[3]
}

Voice = {
    orderlist : pattern_idx[]   -- sequence of pattern indices to play
    patterns  : Pattern[]       -- pattern data (shared across voices)
    loop      : int             -- orderlist index to loop back to (-1 = no loop)
}

Pattern = {
    notes : NoteEvent[]
}

NoteEvent = {
    note       : uint8     -- frequency table index (base pitch)
    duration   : uint8     -- length in ticks
    instrument : uint8     -- instrument index
}
```

The engine converts ticks to frames: `note_frames = duration * tempo`

Pattern end is marked by a sentinel byte ($FE). When the engine reads a
sentinel, it advances to the next pattern in the orderlist. If the orderlist
is exhausted, the engine loops back to `Voice.loop`.

At pattern boundaries, the engine resets the pattern-byte-offset counter
(hub_off) to 0, and forces an instrument reload on the next note (by setting
prev_inst = $FF). This ensures T[100] dynamic entries are computed correctly
at pattern boundaries.

## 5. Timing Schedule (Ω)

The engine is a timed performer, not merely a register writer. Within each
frame, the precise sequence and timing of SID register writes affects the
SID's internal oscillator phase. This matters for:

- **Ring modulation:** voice 1 uses voice 3's oscillator phase. Writing voice
  3 earlier in the frame means its oscillator advances before voice 1 reads it.
- **Sync:** similarly phase-sensitive.
- **Hard restart:** the SID envelope generator reacts immediately to ADSR
  register changes; the frame position of the write determines how many
  envelope generator cycles run before the gate comes on.

```
Ω = {
    voice_order         : uint[3]     -- evaluation order of voices within a frame
                                      -- e.g. [2, 1, 0] = V3 first, V1 last
    register_write_order : enum       -- order of register writes within a voice
                                      -- 'freq_ctrl_pw_adsr' or engine-specific
    eval_delay_cycles   : uint[3]     -- additional idle cycles (NOPs) inserted in
                                      -- the eval path per voice, to match the
                                      -- original engine's cycle budget
    note_load_delay_cycles : uint[3]  -- additional idle cycles in the note-load path
}
```

**Voice evaluation order:** The engine processes voices in the order given by
`Ω.voice_order`. For the Hubbard engine this is [2, 1, 0] (V3 → V2 → V1),
matching Hubbard's original ISR execution order.

**Register write order within a voice:** For each voice, the engine writes
registers in this order:
1. Frequency (freq_lo, freq_hi)
2. Control (ctrl, with gate-off applied)
3. Pulse width (pw_lo, pw_hi)
4. Envelope (AD, SR)

This order is fixed by Ω and must match the original engine's write order.
Changing the order changes when the SID chip sees each value within the frame,
affecting oscillator phase.

**Cycle delays:** The original engine spends a specific number of CPU cycles
processing each voice. The rebuilt engine inserts NOP instructions to match
the original cycle budget. These are not arbitrary padding — they determine
the exact wall-clock time at which each SID register is written within the
frame, which affects the SID chip's oscillator phase.

Formally, Ω defines a partial order on register writes across all three voices
within a single frame. A correct implementation must produce writes in an
order consistent with Ω.

## 6. Universal Engine

The engine evaluates SID = (T, I, S, Ω) per frame. Before voice evaluation:

```
-- Pre-frame: update dynamic T entries from engine state
for each dynamic_entry in T[96+]:
    T[dynamic_entry.index] = dynamic_entry.compute(engine_state)
```

Then, for each voice in Ω.voice_order:

```
1. tick_counter--
   if tick_counter == 0:
       load next NoteEvent from Score (via orderlist → pattern)
       set tick_counter = duration * tempo
       set note_len = tick_counter       (saved for gate-off comparison)
       set base_note = event.note
       if event.instrument != prev_inst:
           load I[event.instrument]
           load P.init_pw into pw_lo, pw_hi
           reset pw_dir = UP
           prev_inst = event.instrument
           hub_off += 3   (3-byte note: note + duration + instrument)
       else:
           hub_off += 2   (2-byte note: note + duration)
       write freq from T[base_note] to freq registers  (note-load always writes)
       write E.ad, E.sr to ADSR registers
       [optionally insert Ω.note_load_delay_cycles NOPs]

2. [optionally insert Ω.eval_delay_cycles NOPs]

3. FREQ: if F.arp_offset != 0:
       apply arpeggio alternation (§3.2)
       write freq registers
   else if V is not null and frames_into_note >= V.delay:
       apply vibrato (§3.3)
       write freq registers
   -- else: freq registers are not written on this eval frame

4. CTRL (W): val = W.steps[w_step]
       if tick_counter <= E.gate_off_delta: val &= $FE   (clear gate)
       write val to ctrl register
       advance w_step (loop if past end)

5. PW (P): accumulate pw, then write pw_lo, pw_hi to SID
       write pw_lo, pw_hi back to I[prev_inst].init_pw   (shared mutable state)

6. ADSR (E): if tick_counter == E.adsr_zero_delta:
                 write $00, $00 to AD, SR registers
             else:
                 write E.ad, E.sr to AD, SR registers
```

That is the complete engine. It has no knowledge of any specific SID player
engine, effect type, or musical concept. It reads programs and data, evaluates
them mechanically, and writes SID registers.

## 7. Invariants

The following invariants must hold for any correct implementation:

**I1 (Freq write on note-load):** The engine always writes freq on the
note-load frame from T[base_note], regardless of F.arp_offset.

**I2 (Freq write skip on eval):** The engine does NOT write freq on eval
frames when F.arp_offset == 0 AND V is null. The freq registers retain the
note-load value.

**I3 (Shared mutable PW):** After each frame's PW write, the engine updates
the instrument table: `I[prev_inst].pw_lo = pw_lo; I[prev_inst].pw_hi = pw_hi`.
This happens even when mode == 'none'.

**I4 (PW skip on note-load):** The PW accumulation step is skipped on the
note-load frame (tick_counter == note_len after loading). The PW is written
(not accumulated) on the note-load frame, so the init value plays on frame 1.

**I5 (Gate-off before ADSR-zero):** gate_off_delta >= adsr_zero_delta. The
gate is cleared before (or simultaneously with) ADSR zeroing. Reversing this
order causes the SID envelope to retrigger incorrectly.

**I6 (Voice order consistent with Ω):** Voices are evaluated in Ω.voice_order
within every frame. Changing the order changes oscillator phase relationships.

**I7 (Register write order):** Within each voice, writes happen in the order:
freq → ctrl → pw → adsr. This order is fixed by Ω and must not be changed.

**I8 (Dynamic T updated before voice eval):** T[96+] dynamic entries are
updated at the start of each frame, before any voice is evaluated. Voice
evaluation reads the freshly updated values.

**I9 (Hub_off at pattern boundary):** hub_off resets to 0 at every pattern
boundary. prev_inst is set to $FF at pattern boundaries to force a 3-byte
note load (instrument change) on the first note of the new pattern.

## 8. Instrument Extraction

Instruments are created by per-engine DECOMPILERS that read the original SID
binary and translate engine-specific parameters into (W, F, P, E, V) programs.

The decompiler is engine-specific. The instrument format is universal.
The engine evaluates any instrument the same way, regardless of which
decompiler created it.

**Hubbard engine example:**
- W program: noise burst ($80) frames if has_drum flag set; gate byte with loop
- F program: arp_offset = 12 if has_arpeggio flag set, else 0
- V program: scale from byte+5 of instrument table; delay = 6 frames
- P program: speed and mode from pwm_speed and fx_flags bit 3
- E spec: AD/SR from instrument table; gate_off_delta = adsr_zero_delta = 3

**GT2 engine example:**
- W program: extracted from GT2 wave table (multi-step, with loop point)
- F program: extracted from GT2 arp table (variable offsets, not just +12)
- V program: null (GT2 uses its own arpeggio table for vibrato-like effects)
- P program: extracted from GT2 pulse table
- E spec: extracted from GT2 instrument ADSR fields

The decompiler maps each engine's representation to the formal model. The
formal model is the interface contract between decompiler and engine.

## 9. Formal Summary

```
Engine(T, I, S, Ω) → SID_register_stream

Per frame f:
    update_dynamic_T(T, engine_state)
    for v in Ω.voice_order:
        tick[v]--
        if tick[v] == 0:
            (note, dur, inst) = next_note(S, v)
            tick[v] = dur * S.tempo
            note_len[v] = tick[v]
            base[v] = note
            if inst != prev_inst[v]:
                load_instrument(I[inst], v)
                prev_inst[v] = inst
            write T[base[v]] → freq_regs[v]
            write I[inst].E.ad, .sr → adsr_regs[v]
        [Ω.eval_delay_cycles[v] idle cycles]
        if I[prev_inst[v]].F.arp_offset != 0:
            write arp_freq(T, base[v], frame_ctr) → freq_regs[v]
        elif I[prev_inst[v]].V is not null:
            write vibrato_freq(T, base[v], frame_ctr, tick[v], note_len[v],
                               I[prev_inst[v]].V) → freq_regs[v]
        ctrl = W_step(I[prev_inst[v]].W, v)
        if tick[v] <= I[prev_inst[v]].E.gate_off_delta: ctrl &= $FE
        write ctrl → ctrl_reg[v]
        pw_accum(I[prev_inst[v]].P, v, tick[v] == note_len[v])
        write pw[v] → pw_regs[v]
        I[prev_inst[v]].P.init_pw = (pw_hi[v] << 8) | pw_lo[v]  -- writeback
        if tick[v] == I[prev_inst[v]].E.adsr_zero_delta:
            write $00, $00 → adsr_regs[v]
        else:
            write I[prev_inst[v]].E.ad, .sr → adsr_regs[v]
```

Any implementation that produces the same SID register stream as this
specification is a correct Das Model engine.
