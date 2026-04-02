# GT2 V2.68 Table Processing Algorithms

**Source:** `src/GoatTracker_2.68/src/player.s`
**Date:** 2026-04-02

This documents the exact per-frame algorithms for wave, pulse, filter, and speed
table processing in the GoatTracker 2 player. Written as pseudocode that can be
directly implemented.

## Terminology

- **Left column / right column**: Each table has two parallel byte arrays. The
  left column controls timing/commands, the right column holds parameters.
- **Pointer**: 1-based index into the table. 0 means "stopped" (no processing).
- **X register**: SID channel offset (0, 7, or 14 for channels 0-2).
- All tables are 1-indexed. `tbl-1,y` with Y=1 reads the first entry.

---

## 1. Wave Table

### Tables

- `mt_wavetbl[]` -- left column (waveform / delay / command / jump)
- `mt_notetbl[]` -- right column (note / parameter)

### Channel State

- `mt_chnwaveptr[ch]` -- current position in wave table (1-based, 0 = stopped)
- `mt_chnwavetime[ch]` -- delay counter (only when NOWAVEDELAY==0)
- `mt_chnwave[ch]` -- current waveform byte for this channel
- `mt_chnnote[ch]` -- current note number
- `mt_chnlastnote[ch]` -- last note set via wave table (for calculated speed)

### Algorithm (called every frame, both tick 0 and tick N)

```
function wave_exec(ch):
    ptr = mt_chnwaveptr[ch]
    if ptr == 0:
        goto wave_done              // wave table stopped

    left = mt_wavetbl[ptr]          // 1-based: read mt_wavetbl-1,y with y=ptr

    // --- DELAY HANDLING (NOWAVEDELAY==0) ---
    if left < $10:                  // $00-$0F: delay value
        if left != mt_chnwavetime[ch]:
            mt_chnwavetime[ch] += 1
            goto wave_done          // still counting, no advance
        // delay expired, fall through to advance pointer
        // (but no waveform change this frame)
        goto advance_pointer

    // --- Remove delay offset ---
    left = left - $10               // undo the +$10 bias from packing
                                    // (when NOWAVEDELAY==0, waveforms $10-$DF
                                    //  were stored as $20-$EF)

    // --- WAVE COMMAND CHECK (NOWAVECMD==0) ---
    if left >= $E0:                 // $E0-$EF after subtraction = command
        goto advance_pointer        // don't write to mt_chnwave
                                    // (command executed AFTER pointer advance)

    // --- NORMAL WAVEFORM ($00-$DF after bias removal) ---
    // Note: if NOWAVEDELAY!=0, the raw value is used directly
    // and $00 means "no wave change" (falls through to advance)
    mt_chnwave[ch] = left

advance_pointer:
    // --- CHECK NEXT BYTE FOR JUMP ---
    next_left = mt_wavetbl[ptr + 1]
    if next_left == $FF:            // LOOPWAVE: jump
        new_ptr = mt_notetbl[ptr + 1]   // jump target from right column
        mt_chnwaveptr[ch] = new_ptr
    else:
        mt_chnwaveptr[ch] = ptr + 1

    // --- RESET DELAY COUNTER ---
    mt_chnwavetime[ch] = 0          // (only when NOWAVEDELAY==0)

    // --- WAVE COMMAND EXECUTION (NOWAVECMD==0) ---
    // Check if the CURRENT step (not next) was a command
    current_left = mt_wavetbl[ptr]
    if NOWAVEDELAY==0:
        current_left = current_left - $10
    if current_left >= $E0:
        cmd = current_left & $0F    // command number 0-F
        param = mt_notetbl[ptr]     // right column = parameter
        exec_wave_command(ch, cmd, param)
        goto after_freq             // skip frequency processing

    // --- RIGHT COLUMN: NOTE/FREQUENCY ---
    right = mt_notetbl[ptr]

    if right == 0:                  // $00 = keep current frequency
        goto wave_done              // (no frequency change)

    // In packed data, right column has been XOR $80:
    //   original bit 7 was 0 = absolute -> after XOR = bit 7 set
    //   original bit 7 was 1 = relative -> after XOR = bit 7 clear
    // So in the player, after the XOR:
    if right >= $80:                // bit 7 set = RELATIVE note
        note = (right + mt_chnnote[ch]) & $7F
    else:                           // bit 7 clear = ABSOLUTE note
        note = right
        mt_chnlastnote[ch] = note   // (only when NOCALCULATEDSPEED==0)

    // Look up frequency from table
    mt_chnfreqlo[ch] = mt_freqtbllo[note - FIRSTNOTE]
    mt_chnfreqhi[ch] = mt_freqtblhi[note - FIRSTNOTE]
    mt_chnvibtime[ch] = 0           // reset vibrato phase on note change

after_freq:

wave_done:
    // --- CONTINUOUS EFFECTS (ticks 1+) ---
    // If no frequency change from wave table, run the current
    // continuous effect (vibrato, portamento, etc.)
    // See section 4 (Speed Table) for details.

    // --- PULSE EXECUTION follows ---
    // --- GATE TIMER CHECK follows ---
```

### Wave Commands ($E0-$EF left column, after bias removal)

The command number is the low nibble (0-F). It indexes into the same tick-0
effect jump table used by pattern effects:

| Cmd | Effect | Parameter (right column) |
|-----|--------|--------------------------|
| $0  | Set instrument vibrato | Speed table index |
| $1  | Portamento up | Speed table index |
| $2  | Portamento down | Speed table index |
| $3  | Tone portamento | Speed table index |
| $4  | Vibrato | Speed table index |
| $5  | Set Attack/Decay | AD value |
| $6  | Set Sustain/Release | SR value |
| $7  | Set waveform | Waveform byte |
| $8  | Set wave pointer | New wave table position |
| $9  | Set pulse pointer | New pulse table position |
| $A  | Set filter pointer | New filter table position |
| $B  | Set filter control | Resonance/routing byte (0 = also stop filter) |
| $C  | Set filter cutoff | Cutoff value |
| $D  | Set master volume | Volume 0-F (or timing mark if >= $10) |
| $E  | Set funktempo | Speed table index (loads both funk values) |
| $F  | Set tempo | Tempo value (bit 7: 0=global, 1=channel) |

Commands $0-$4 are dispatched as continuous effects (they set the effect number
and parameter for ongoing per-frame processing). Commands $5-$F are immediate
(tick-0 only, execute once).

```
function exec_wave_command(ch, cmd, param):
    if cmd < 5:
        // Continuous effect: route through effect jump table
        // Sets mt_chnfx and mt_chnparam, then runs the effect
        // on subsequent frames via mt_setspeedparam -> mt_effectjump
        mt_effectnum = cmd
        effect_fn = mt_effectjumptbl[cmd]
        // Load speed parameters from speed table using param as index
        // then jump to the effect handler
        run_effect(ch, effect_fn, param)
    else:
        // Tick-0 command: dispatch through tick0 jump table
        tick0_fn = mt_tick0jumptbl[cmd]
        tick0_fn(ch, param)
```

### Waveform + Gate Combination

The waveform written to the SID register is always:

```
SID_register_4 = mt_chnwave[ch] AND mt_chngate[ch]
```

- `mt_chngate[ch]` is normally $FF (gate on) or $FE (gate off / hard restart).
- Gate off: AND with $FE clears bit 0, so the gate bit is removed.
- Keyoff ($BE in pattern): sets gate to $FE AND $F0 = $BE | $F0 = $FE (clear gate).
- Keyon ($BF in pattern): sets gate to $BF | $F0 = $FF (set gate).

---

## 2. Pulse Table

### Tables

- `mt_pulsetimetbl[]` -- left column (set/modulate/jump)
- `mt_pulsespdtbl[]` -- right column (pulse width value or speed)

### Channel State

- `mt_chnpulseptr[ch]` -- current position in pulse table (1-based, 0 = stopped)
- `mt_chnpulsetime[ch]` -- modulation step duration counter
- `mt_chnpulselo[ch]` -- pulse width accumulator low byte
- `mt_chnpulsehi[ch]` -- pulse width accumulator high byte

### Algorithm (called every frame after wave processing)

```
function pulse_exec(ch):
    ptr = mt_chnpulseptr[ch]
    if ptr == 0:
        goto pulse_skip             // pulse table stopped

    // PULSEOPTIMIZATION: skip pulse on the frame the sequencer ran
    // (when both counter==0 AND pattptr==0, meaning we just loaded a new pattern)
    if PULSEOPTIMIZATION:
        if mt_chncounter[ch] == 0 AND mt_chnpattptr[ch] == 0:
            goto pulse_skip

    // --- CHECK MODULATION TIMER ---
    if mt_chnpulsetime[ch] != 0:    // (only when NOPULSEMOD==0)
        goto pulse_mod

    // --- NEW STEP ---
    left = mt_pulsetimetbl[ptr]

    if left >= $80:                 // SET PULSE mode
        goto set_pulse
    // (if NOPULSEMOD==0, left $01-$7F = new modulation step)
    if left > 0:
        goto new_pulse_mod

    // left == 0 should not normally occur (0 not used in pulse table)

set_pulse:
    // --- NORMAL MODE (SIMPLEPULSE==0) ---
    mt_chnpulsehi[ch] = left        // high byte = left column value ($80-$FF)
    mt_chnpulselo[ch] = mt_pulsespdtbl[ptr]  // low byte from right column
    goto advance_pulse_pointer

    // --- SIMPLE PULSE MODE (SIMPLEPULSE!=0) ---
    // Left column is always $80 (clamped during packing)
    // Right column has the pulse width byte
    // Both lo and hi are set to the right column value
    mt_chnpulselo[ch] = mt_pulsespdtbl[ptr]
    mt_chnpulsehi[ch] = mt_pulsespdtbl[ptr]
    goto advance_pulse_pointer

new_pulse_mod:
    // --- START NEW MODULATION PERIOD ---
    mt_chnpulsetime[ch] = left      // set duration counter ($01-$7F)

pulse_mod:
    // --- MODULATE PULSE WIDTH ---

    // NORMAL MODE (SIMPLEPULSE==0):
    speed = mt_pulsespdtbl[ptr]     // signed 8-bit speed
    if speed >= 0:                  // positive: pulse up
        pulse16 = (mt_chnpulsehi[ch] << 8) | mt_chnpulselo[ch]
        pulse16 = pulse16 + speed   // unsigned add, wraps at 16 bits
    else:                           // negative: pulse down
        // pre-decrement high byte, then add (speed is negative, so
        // adding a negative byte with carry propagation)
        mt_chnpulsehi[ch] -= 1
        lo = mt_chnpulselo[ch] + speed  // carry from this add
        mt_chnpulselo[ch] = lo
        if carry:
            mt_chnpulsehi[ch] += 1

    // More precisely, the 6502 code does:
    //   CLC / BPL pulseup
    //   DEC mt_chnpulsehi,x        ; pre-decrement hi for negative speed
    // pulseup:
    //   ADC mt_chnpulselo,x        ; add speed to lo
    //   STA mt_chnpulselo,x
    //   BCC pulsenotover
    //   INC mt_chnpulsehi,x        ; carry into hi
    // pulsenotover:

    // SIMPLE PULSE MODE (SIMPLEPULSE!=0):
    // Only 8-bit pulse. Speed is added then +0 with carry (rounding):
    //   lo = mt_chnpulselo[ch] + speed + 0  (CLC; ADC speed; ADC #$00)
    //   mt_chnpulselo[ch] = lo
    //   mt_chnpulsehi[ch] = lo     // mirror lo to hi

    mt_chnpulsetime[ch] -= 1
    if mt_chnpulsetime[ch] != 0:
        goto write_pulse            // still modulating, don't advance pointer

advance_pulse_pointer:
    // --- CHECK NEXT BYTE FOR JUMP ---
    next_left = mt_pulsetimetbl[ptr + 1]
    if next_left == $FF:            // LOOPPULSE: jump
        new_ptr = mt_pulsespdtbl[ptr + 1]  // jump target
        mt_chnpulseptr[ch] = new_ptr
    else:
        mt_chnpulseptr[ch] = ptr + 1

write_pulse:
    // Write to SID (when BUFFEREDWRITES==0):
    SID[$D402 + ch_offset] = mt_chnpulselo[ch]
    if SIMPLEPULSE==0:
        SID[$D403 + ch_offset] = mt_chnpulsehi[ch]
    else:
        SID[$D403 + ch_offset] = mt_chnpulselo[ch]  // mirror

pulse_skip:
```

### Key Details

- The pulse accumulator is 16-bit in normal mode (hi:lo), 8-bit mirrored in
  SIMPLEPULSE mode.
- Set-pulse ($80+ left) loads the accumulator directly. In normal mode, the left
  byte IS the high byte (so $80 = pulse width $80xx). In SIMPLEPULSE mode, the
  left byte is always $80 (placeholder) and the right byte sets both lo and hi.
- Modulation speed is a signed 8-bit value added to the 16-bit accumulator each
  frame for `duration` frames.
- The pulse pointer is reset (with timer cleared) on new note init if the
  instrument has a non-zero pulse pointer.

---

## 3. Filter Table

### Tables

- `mt_filttimetbl[]` -- left column (set params / set cutoff / modulate / jump)
- `mt_filtspdtbl[]` -- right column (resonance+routing / cutoff / speed)

### Global State (filter is shared, not per-channel)

- `mt_filtstep` -- current position in filter table (0 = stopped, self-modified)
- `mt_filttime` -- modulation duration counter (self-modified)
- `mt_filtcutoff` -- current cutoff value (self-modified, written to SID $D416)
- `mt_filtctrl` -- filter control: resonance + channel routing (written to SID $D417)
- `mt_filttype` -- filter type: passband bits + master volume (written to SID $D418)

### Algorithm (called once per frame, before channel processing)

```
function filter_exec():
    ptr = mt_filtstep               // self-modifying code; 0 = stopped
    if ptr == 0:
        goto filter_done

    // --- CHECK MODULATION TIMER ---
    if mt_filttime != 0:            // (only when NOFILTERMOD==0)
        goto filter_mod

    // --- NEW STEP ---
    left = mt_filttimetbl[ptr]

    if left == $00:                 // SET CUTOFF
        goto set_cutoff

    if left >= $80:                 // SET FILTER PARAMS ($80+)
        goto set_filter_params

    // left $01-$7F: new modulation period (only when NOFILTERMOD==0)
    goto new_filter_mod

set_filter_params:
    // Left column was transformed during packing:
    //   stored = ((original & $70) >> 1) | $80
    // To recover passband bits for SID $D418:
    //   ASL shifts out the $80 marker, leaving passband bits in correct position
    //   (original bits 4-6 = passband, now in bits 4-6 of result)
    passband = left << 1            // ASL: removes $80 flag, positions passband
    mt_filttype = passband          // written to upper nibble of SID $D418

    // Right column = resonance (bits 4-7) + channel routing (bits 0-2)
    mt_filtctrl = mt_filtspdtbl[ptr]    // written to SID $D417

    // Check if next entry is a cutoff setting (left == $00)
    if mt_filttimetbl[ptr + 1] == $00:
        // Cutoff immediately follows filter params
        ptr = ptr + 1
        goto set_cutoff_and_advance
    else:
        // Advance past this step, skip the normal advance logic
        goto advance_filter_pointer_from_next

set_cutoff:
set_cutoff_and_advance:
    mt_filtcutoff = mt_filtspdtbl[ptr]  // right column = cutoff value

    // (when NOFILTERMOD==0, fall through to advance)
    goto advance_filter_pointer

new_filter_mod:
    // --- START NEW MODULATION PERIOD ---
    mt_filttime = left              // duration counter ($01-$7F)

filter_mod:
    // --- MODULATE CUTOFF ---
    speed = mt_filtspdtbl[ptr]      // signed 8-bit modulation speed
    mt_filtcutoff = mt_filtcutoff + speed   // 8-bit add, wraps

    mt_filttime -= 1
    if mt_filttime != 0:
        goto write_cutoff           // still modulating, don't advance

advance_filter_pointer:
    next_left = mt_filttimetbl[ptr + 1]

advance_filter_pointer_from_next:
    if next_left == $FF:            // LOOPFILT: jump
        new_ptr = mt_filtspdtbl[ptr + 1]
        mt_filtstep = new_ptr
    else:
        mt_filtstep = ptr + 1

filter_done:
write_cutoff:
    // Write filter registers to SID:
    SID[$D416] = mt_filtcutoff          // filter cutoff high byte
    SID[$D417] = mt_filtctrl            // resonance (4-7) + routing (0-2)
    SID[$D418] = mt_filttype | mt_masterfader  // passband + volume
```

### Key Details

- Filter is **global** -- there is one filter pointer, one set of filter state.
  Any channel can set it (via instrument filtptr or pattern effect $0A/$0B/$0C).
- The cutoff written to $D416 is only the **high byte** of the 11-bit filter
  cutoff. The low 3 bits ($D415) are set to 0 at init and never changed by the
  player (except on full init).
- Set-params ($80+ left) and set-cutoff ($00 left) can appear consecutively.
  When set-params is followed by set-cutoff, both execute in the same frame
  (the player checks `mt_filttimetbl[ptr+1]` and chains them).
- Modulation adds a signed speed to the 8-bit cutoff each frame for `duration`
  frames.
- Setting filter control ($0B effect) to 0 also stops filter step-programming
  (`mt_filtstep = 0`).
- The `mt_filttype` upper nibble holds passband mode (LP/BP/HP/combinations).
  The lower nibble comes from `mt_masterfader` (master volume).

---

## 4. Speed Table

### Tables

- `mt_speedlefttbl[]` -- left column
- `mt_speedrighttbl[]` -- right column

The speed table is **not stepped through** like the other tables. Instead,
individual entries are referenced by index from vibrato parameters, portamento
effects, and funktempo.

### 4a. Vibrato (effect $04, or instrument vibrato effect $00)

A vibrato entry in the speed table has:
- Left column = **speed** (how many frames per half-cycle)
- Right column = **depth** (frequency delta per frame)

There are two speed modes:

**Normal speed** (left column bit 7 = 0):
- `mt_temp2` = left column (speed, used as vibrato half-cycle length)
- `mt_temp1` = right column (depth, 16-bit low byte; high byte = 0)

**Calculated speed** (left column bit 7 = 1):
- Speed value = left & $7F (vibrato half-cycle length)
- Right column = shift count
- Depth is calculated from the difference between the current note's frequency
  and the next semitone's frequency, right-shifted by the shift count:
  ```
  freq_delta = freqtbl[lastnote + 1] - freqtbl[lastnote]  // 16-bit
  depth = freq_delta >> shift_count                         // 16-bit
  mt_temp1 = depth low byte
  mt_temp2 = depth high byte
  ```

**Vibrato algorithm** (runs on ticks 1+):

```
function vibrato(ch, speed_index):
    // Load speed parameters
    left = mt_speedlefttbl[speed_index]
    right = mt_speedrighttbl[speed_index]

    if NOCALCULATEDSPEED == 0:
        if left & $80:                          // calculated speed
            speed = left & $7F
            shift = right
            note = mt_chnlastnote[ch]
            delta16 = freq[note+1] - freq[note]
            for i in range(shift):
                delta16 >>= 1                   // logical shift right
            mt_temp1 = delta16 & $FF            // depth lo
            mt_temp2 = (delta16 >> 8) & $FF     // depth hi
        else:                                   // normal speed
            speed = left
            mt_temp1 = right                    // depth lo
            mt_temp2 = 0                        // depth hi
    else:
        // NOCALCULATEDSPEED: always normal speed
        mt_temp1 = right
        mt_temp2 = 0
        speed = left

    // --- VIBRATO PHASE LOGIC ---
    // mt_chnvibtime is a combined direction + counter byte:
    //   bit 7: direction (0 = going up, 1 = going down)
    //   bits 0-6: counter
    //
    // The counter increments by 2 each frame.
    // When counter reaches speed value, direction flips.

    vt = mt_chnvibtime[ch]

    if vt < 0:                      // bit 7 set: going down
        goto no_direction_change
    if (vt & $7F) < speed:          // haven't reached half-cycle yet
        goto no_direction_change_2
    if (vt & $7F) == speed:         // exactly at boundary
        goto no_direction_change    // one more frame at boundary
    // counter > speed: flip direction
    vt = vt XOR $FF                 // invert all bits (flip direction + negate counter)

no_direction_change:
    // carry is set (from CMP or EOR)
    vt = vt + 2                     // CLC not executed, so actually ADC #$02 with C=1 = +3?
                                    // No: at this label carry state varies. Let me be precise.

    // EXACT 6502 logic:
    //   mt_effect_4_nodir:  CLC          ; carry = 0
    //   mt_effect_4_nodir2: ADC #$02     ; vt = vt + 2 + carry
    //
    // Path 1: vt < 0 (BPL not taken) -> CLC -> ADC #2 -> vt += 2
    // Path 2: vt < speed (BCC taken) -> no CLC -> ADC #2 -> vt += 3
    //         (carry is set from CMP because A < speed means borrow, wait...)
    //
    // Actually: CMP subtracts. BCC means A < operand, which means carry CLEAR.
    // So: BCC taken -> carry = 0 -> ADC #2 -> vt += 2. Correct.
    //
    // Path 3: vt == speed (BEQ taken) -> CLC -> ADC #2 -> vt += 2
    // Path 4: vt > speed (EOR $FF) -> no CLC -> carry = 1 from CMP
    //         -> ADC #2 -> vt += 3

no_direction_change_2:
    vt = vt + 2                     // +2 when carry clear, +3 when carry set

    mt_chnvibtime[ch] = vt

    // --- APPLY VIBRATO TO FREQUENCY ---
    // LSR: shift right, old bit 0 goes to carry
    direction = vt & 1              // 0 = add (freq up), 1 = subtract (freq down)

    if direction == 0:              // carry clear from LSR
        freq16 = (mt_chnfreqhi[ch] << 8) | mt_chnfreqlo[ch]
        freq16 = freq16 + (mt_temp2 << 8 | mt_temp1)
    else:                           // carry set from LSR
        freq16 = (mt_chnfreqhi[ch] << 8) | mt_chnfreqlo[ch]
        freq16 = freq16 - (mt_temp2 << 8 | mt_temp1)

    mt_chnfreqlo[ch] = freq16 & $FF
    mt_chnfreqhi[ch] = (freq16 >> 8) & $FF
```

**Precise vibrato phase machine:**

```
vt starts at 0 on note init.

Each frame:
  if vt >= 0:                       // positive half (going up)
    if vt > speed:                  // exceeded half-cycle
      vt = ~vt                      // EOR $FF: flip to negative
      vt = vt + 3                   // ADC #2 with carry set
    elif vt == speed:               // at boundary, one more frame
      vt = vt + 2                   // CLC; ADC #2
    else:                           // vt < speed
      vt = vt + 2                   // carry clear from CMP; ADC #2
  else:                             // negative half (going down)
    vt = vt + 2                     // CLC; ADC #2

  bit0 = vt & 1
  if bit0 == 0: add depth to freq
  if bit0 == 1: subtract depth from freq

Note: vt oscillates roughly between 0 and speed in the positive range,
then between ~$FF-speed and $FF in the negative range. The LSR check on
bit 0 alternates the direction of frequency modulation.
```

### 4b. Portamento (effects $01 up, $02 down)

A portamento entry in the speed table:
- Left = speed high byte (normal) or calculated flag + shift (calculated)
- Right = speed low byte (normal) or shift count (calculated)

**Normal speed** (left bit 7 = 0):
```
mt_temp2 = left     // speed high byte
mt_temp1 = right    // speed low byte
// 16-bit speed value = (left << 8) | right
```

**Calculated speed** (left bit 7 = 1):
```
Same calculation as vibrato calculated speed:
delta16 = freq[lastnote+1] - freq[lastnote]
delta16 >>= right   // shift by right-column value
mt_temp1 = lo(delta16)
mt_temp2 = hi(delta16)
```

**Portamento algorithm** (runs on ticks 1+):

```
function portamento(ch, direction, speed_index):
    // speed loaded into mt_temp1 (lo) and mt_temp2 (hi)
    // direction: 1 = up, 2 = down

    if direction == 1:              // portamento up
        freq16 += (mt_temp2 << 8) | mt_temp1
    elif direction == 2:            // portamento down
        freq16 -= (mt_temp2 << 8) | mt_temp1

    mt_chnfreqlo[ch] = freq16 & $FF
    mt_chnfreqhi[ch] = (freq16 >> 8) & $FF
```

### 4c. Tone Portamento (effect $03)

Uses the same speed table entry format as regular portamento. Slides the current
frequency toward the target note's frequency, stopping when it arrives.

```
function toneporta(ch, speed_index):
    // speed in mt_temp1/mt_temp2 (loaded same as portamento)
    target_note = mt_chnnote[ch]    // set when the new note was received

    // Calculate signed offset: current freq - target freq
    offset_lo = mt_chnfreqlo[ch] - freqtbllo[target_note]
    offset_hi = mt_chnfreqhi[ch] - freqtblhi[target_note]

    if offset >= 0:                 // current freq > target: need to go down
        offset -= speed16
        if offset < 0:             // overshot: we've arrived
            goto arrived
        freq16 -= speed16          // subtract from actual freq
    else:                           // current freq < target: need to go up
        offset += speed16
        if offset >= 0:            // overshot: we've arrived
            goto arrived
        freq16 += speed16          // add to actual freq

    mt_chnfreqlo[ch] = freq16 & $FF
    mt_chnfreqhi[ch] = (freq16 >> 8) & $FF
    return

arrived:
    // Set frequency directly to target
    // (When NOCALCULATEDSPEED==0, uses mt_wavenoteabs path)
    // (When NOCALCULATEDSPEED!=0, uses mt_wavenote path via Y register)
    mt_chnfreqlo[ch] = freqtbllo[target_note]
    mt_chnfreqhi[ch] = freqtblhi[target_note]
    mt_chnlastnote[ch] = target_note
    mt_chnvibtime[ch] = 0          // reset vibrato
```

### 4d. Funktempo (effect $0E)

Funktempo uses a speed table entry to define two alternating tempo values:

```
function set_funktempo(speed_index):
    mt_funktempotbl[0] = mt_speedlefttbl[speed_index]   // tempo A
    mt_funktempotbl[1] = mt_speedrighttbl[speed_index]   // tempo B
    // Also sets global tempo to 0 (funktempo mode)
    set_global_tempo(0)
```

**Funktempo tick counter algorithm** (in the main tick counter):

```
function tick_counter(ch):
    mt_chncounter[ch] -= 1
    if mt_chncounter[ch] == 0:
        goto tick_0                 // process new row

    if mt_chncounter[ch] < 0:      // counter went negative, reload
        tempo = mt_chntempo[ch]

        if tempo < 2:              // funktempo mode (tempo is 0 or 1)
            // Bounce between index 0 and 1
            new_idx = tempo XOR 1
            mt_chntempo[ch] = new_idx
            reload = mt_funktempotbl[tempo]
            reload -= 1            // SBC #$00 with carry clear = subtract 1
        else:
            reload = tempo

        mt_chncounter[ch] = reload
        goto tick_n                 // run continuous effects
```

Funktempo alternates between two tempo values each row. When tempo is 0, it reads
`funktempotbl[0]` and sets tempo to 1. Next time, it reads `funktempotbl[1]` and
sets tempo to 0. This creates the characteristic "swing" timing.

---

## Edge Cases

### Wave table
- Pointer 0 = stopped. No wave processing at all.
- Delay value $00 in left column: completes immediately (0 == 0 on first check),
  so it acts as a 1-frame step with no waveform change.
- Jump ($FF) target can point to any valid table position including itself
  (infinite loop on one step).
- Wave command $08 (set wave pointer) resets the delay counter to 0.

### Pulse table
- Pointer 0 = stopped.
- The pulse pointer and timer are reset on new note init only if the instrument's
  pulse pointer is non-zero. If zero, the existing pulse state continues.
- SIMPLEPULSE mode: the high byte of pulse width is mirrored from low byte,
  giving only 256 distinct pulse widths instead of 4096.

### Filter table
- Filter step 0 = stopped. The current cutoff/control/type values persist (they
  are in self-modifying instruction operands).
- Setting filter control to 0 (via effect $0B) stops filter step-programming.
- Filter is global: if two channels both trigger instrument filter pointers, the
  second one wins (overwrites the shared state).
- Set-params can chain with set-cutoff in the same frame when they are adjacent
  entries.

### Speed table
- Index 0 for instrument vibrato means "no vibrato" (the player checks for
  speed == 0 and skips entirely).
- The extra $00 byte prefixed before `mt_speedlefttbl` and `mt_speedrighttbl`
  in packed data ensures that index 0 reads as 0 (no-op), but the player
  uses 1-based indexing (`-1,y` addressing) so this prefix byte is at the
  conceptual "index 0" position.
- Portamento effects $01/$02 clear the vibrato phase counter on tick 0
  (`mt_chnvibtime = 0`), preventing vibrato from continuing during portamento.
- Calculated speed uses `mt_chnlastnote` which is set when absolute notes come
  from the wave table. If only relative notes have been used, lastnote may be
  stale from a previous note.
