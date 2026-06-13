# GT2 V2.68 Player Algorithm (Group B)

**Source:** `src/GoatTracker_2.68/src/player.s` (1808 lines)
**Date:** 2026-04-02
**Purpose:** Exact frame-by-frame behavioral spec for the most common GT2 player version (75% of HVSC GT2 files). This document is the spec for building the SIDfinity player.

## Overview

The player is called once per frame (50Hz PAL, 60Hz NTSC). Each call to `mt_play` processes the global filter, then iterates through channels 0, 1, 2 in order. Each channel goes through either the tick-0 path (sequencer advance + new note) or the tick-N path (effects only), followed by wave table execution, pulse table execution, gate timer check, and register writes.

## Variable Layout

Channel variables are stored in arrays with a stride of 7 bytes (for 3 channels, X register = 0, 7, or 14). There are multiple variable groups, each with their own base arrays. The first variable in each group defines the base; subsequent variables follow at offset +1, +2, etc. The channel index X selects which channel.

### Variable Groups (normal layout, when features are enabled)

**Group 1** (stride 7, 7 vars):
| Offset | Variable | Init |
|--------|----------|------|
| +0 | mt_chnsongptr | 0 |
| +1 | mt_chntrans | 0 |
| +2 | mt_chnrepeat | 0 |
| +3 | mt_chnpattptr | 0 |
| +4 | mt_chnpackedrest | 0 |
| +5 | mt_chnnewfx | 0 |
| +6 | mt_chnnewparam | 0 |

**Group 2** (stride 7, 7 vars):
| Offset | Variable | Init |
|--------|----------|------|
| +0 | mt_chnfx | 0 |
| +1 | mt_chnparam | 0 |
| +2 | mt_chnnewnote | 0 |
| +3 | mt_chnwaveptr | 0 |
| +4 | mt_chnwave | 0 |
| +5 | mt_chnpulseptr | 0 |
| +6 | mt_chnpulsetime | 0 |

**Group 3** (stride 7, 7 vars):
| Offset | Variable | Init |
|--------|----------|------|
| +0 | mt_chnsongnum | 0 (ch0), 1 (ch1), 2 (ch2) |
| +1 | mt_chnpattnum | 0 |
| +2 | mt_chntempo | DEFAULTTEMPO |
| +3 | mt_chncounter | 1 |
| +4 | mt_chnnote | 0 |
| +5 | mt_chninstr | 1 |
| +6 | mt_chngate | $FE |

**Group 4** (stride 7, 7 vars):
| Offset | Variable | Init |
|--------|----------|------|
| +0 | mt_chnvibtime | 0 |
| +1 | mt_chnvibdelay | 0 |
| +2 | mt_chnwavetime | 0 |
| +3 | mt_chnfreqlo | 0 |
| +4 | mt_chnfreqhi | 0 |
| +5 | mt_chnpulselo | 0 |
| +6 | mt_chnpulsehi | 0 |

**Group 5** (stride 7, 7 vars, conditional on BUFFEREDWRITES/FIXEDPARAMS/CALCULATEDSPEED):
| Offset | Variable | Init |
|--------|----------|------|
| +0 | mt_chnad | 0 |
| +1 | mt_chnsr | 0 |
| +2 | mt_chnsfx | 0 |
| +3 | mt_chnsfxlo | 0 |
| +4 | mt_chnsfxhi | 0 |
| +5 | mt_chngatetimer | 0 |
| +6 | mt_chnlastnote | 0 |

### Global Variables (self-modifying code immediates)

These are stored as the immediate byte of instructions, modified in-place:
- `mt_initsongnum+1` -- song init flag (negative = no init pending)
- `mt_filtstep+1` -- current filter table position (0 = stopped)
- `mt_filttime+1` -- filter modulation time counter
- `mt_filtcutoff+1` -- current filter cutoff value
- `mt_filtctrl+1` -- filter control (resonance + channel routing)
- `mt_filttype+1` -- filter type (passband bits, shifted left by 1)
- `mt_masterfader+1` -- master volume (0-15)
- `mt_funktempotbl` -- 2-byte funktempo table (toggling tempos)

## 1. Song Initialization

On the very first call (or when a new song is selected), `mt_initsongnum+1` is non-negative:

```
if init_song_num >= 0:
    # Clear ALL channel variables to 0
    for i in range(NUMCHANNELS * 14 - 1, -1, -1):
        chnsongptr_array[i] = 0    # covers groups 1+2

    # Reset SID filter cutoff low byte
    SID[$15] = 0                   # (or ghostfiltcutlow if ZPGHOSTREGS)

    # Reset filter state
    filtctrl = 0
    filtstep = 0                   # stop filter table

    # Mark init complete (set to $FF = negative)
    init_song_num = $FF

    # Initialize each channel
    for ch in [0, 7, 14]:          # (for 3 channels)
        if NUMSONGS > 1:
            chnsongnum[ch] = song_index++    # 0, 1, 2 for song 0
        chntempo[ch] = DEFAULTTEMPO
        chncounter[ch] = 1
        chninstr[ch] = 1
        # Falls through to mt_loadregswaveonly:
        #   wave = chnwave[ch] AND chngate[ch]
        #   write wave to SID[$04 + ch]
```

**Note:** The init clears `NUMCHANNELS * 14` bytes starting at `mt_chnsongptr`. This covers groups 1 and 2 (14 variables). Groups 3-5 are initialized individually per channel. The counter starts at 1, so the first call after init will decrement to 0 and enter tick-0 (sequencer advance).

## 2. Frame Start: Filter Processing

After init check, filter processing runs FIRST, before any channel:

```
# --- Filter table execution ---
if filtstep == 0:
    goto filtdone               # filter stopped

if filttime != 0:
    goto filtmod                # modulation in progress

# New filter step
left = filttimetbl[filtstep - 1]

if left == 0:                   # $00 = set cutoff
    goto setcutoff

if left >= $80:                 # $80+ = set filter parameters
    goto setfilt

# $01-$7F = new modulation step
filttime = left
goto filtmod

setfilt:
    filttype = left << 1        # shift passband bits (becomes the $D418 hi nibble)
    filtctrl = filtspdtbl[filtstep - 1]  # resonance + channel routing
    # Check if cutoff setting follows immediately
    if filttimetbl[filtstep] != 0:
        goto nextfiltstep2      # advance and check for jump
    # else fall through to setcutoff with incremented index
    filtstep++

setcutoff:
    filtcutoff = filtspdtbl[filtstep - 1]
    goto nextfiltstep

filtmod:
    # Modulate cutoff
    filtcutoff = filtcutoff + filtspdtbl[filtstep - 1]   # signed add (wraps)
    filttime--
    if filttime != 0:
        goto storecutoff        # don't advance step yet

nextfiltstep:
    next = filttimetbl[filtstep]    # peek at next entry
nextfiltstep2:
    if next == $FF:             # LOOPFILT = jump
        filtstep = filtspdtbl[filtstep]   # jump target from right column
    else:
        filtstep = filtstep + 1

filtdone:
storecutoff:
    SID[$16] = filtcutoff       # filter cutoff high byte

# Always write filter control and volume
SID[$17] = filtctrl             # resonance + routing
SID[$18] = filttype | mastervol # filter mode + master volume
```

**Key detail:** Filter is GLOBAL, not per-channel. The filter step pointer, cutoff, control, and type are all single global values. Any channel can set the filter pointer via instrument init or pattern commands, but only one filter program runs at a time.

**Table indexing:** All table accesses use 1-based indexing (the code does `lda table-1,y` with Y being the 1-based pointer). A step value of 0 means "stopped."

## 3. Per-Channel Processing Order

After filter, channels are processed sequentially:

```
for ch_offset in [0, 7, 14]:   # channel 0, 1, 2
    X = ch_offset              # X register = SID offset (0, 7, 14)
    execute_channel(X)
```

Channels 0 and 1 are called via `jsr mt_execchn`, channel 2 falls through into `mt_execchn`. The X register serves double duty: it indexes both the channel variable arrays (stride 7) and the SID registers (SID voice registers are at offsets 0, 7, 14 from $D400).

## 4. Channel Execution: Tick Counter

```
mt_execchn:
    chncounter[X]--

    if chncounter[X] == 0:
        goto tick0              # TICK 0: sequencer advance

    if chncounter[X] < 0:      # underflowed (was 0 before dec)
        # Reload tempo
        tempo = chntempo[X]

        if FUNKTEMPO enabled AND tempo < 2:
            # Funktempo: toggle between two speed values
            other = tempo XOR 1
            chntempo[X] = other
            tempo = funktempotbl[tempo] - 1   # (SBC #$00 with carry clear)

        chncounter[X] = tempo

    # TICK N: skip to wave table execution (effects run from there)
    goto waveexec
```

**Funktempo detail:** When tempo is 0 or 1, it acts as an index into the 2-byte funktempotbl. Each frame, the index toggles (0->1->0->1...), and the actual tick count is loaded from the table. The `sbc #$00` with carry clear subtracts 1 from the table value. Default funktempotbl = [8, 5], so tempos alternate between 7 and 4 ticks.

## 5. Tick 0 Path: Sequencer + New Note

### 5a. Setup tick-0 effect jump targets

```
tick0:
    fx_num = chnnewfx[X]       # current effect number for this channel
    jump_addr = tick0jumptbl[fx_num]   # low byte of handler
    # Store in BOTH tick0jump1 and tick0jump2 (self-modifying JSR targets)
    tick0jump1 = jump_addr
    tick0jump2 = jump_addr
```

### 5b. Check if new pattern needed

```
mt_checknewpatt:
    if chnpattptr[X] != 0:
        goto nonewpatt          # still have data in current pattern

    # --- SEQUENCER: advance to next pattern ---
    song_idx = chnsongnum[X]
    song_addr = songtbl[song_idx]      # address of this channel's orderlist
    pos = chnsongptr[X]
    entry = song_addr[pos]

    # Check for loop marker
    if entry == $FF (LOOPSONG):
        pos = song_addr[pos + 1]       # restart position
        entry = song_addr[pos]

    # Check for transpose command ($E0-$EF = trans down, $F0-$FE = trans up)
    if entry >= $E0 (TRANSDOWN):
        chntrans[X] = entry - $F0      # signed: $E0=-16..$EF=-1, $F0=0..$FE=+14
        pos++
        entry = song_addr[pos]

    # Check for repeat command ($D0-$DF)
    if entry >= $D0 (REPEAT):
        repeat_count = entry - $D0
        chnrepeat[X]++
        if chnrepeat[X] != repeat_count:
            goto nonewpatt      # repeat: don't advance, reuse current pattern
        chnrepeat[X] = 0       # repeat done, fall through to store pattern

    chnpattnum[X] = entry       # store pattern number
    pos++
    chnsongptr[X] = pos         # advance song position
```

### 5c. Load gate timer and check new note

```
nonewpatt:
    instr = chninstr[X]
    if FIXEDPARAMS == 0:
        chngatetimer[X] = insgatetimer[instr - 1]

    if chnnewnote[X] == 0:
        goto nonewnoteinit      # no new note pending
```

### 5d. New note initialization

```
newnoteinit:
    note = chnnewnote[X] - NOTE     # NOTE = $60, so subtract to get raw note number
    chnnote[X] = note
    chnfx[X] = 0                    # reset continuous effect
    chnnewnote[X] = 0               # clear new note flag

    # Load instrument vibrato
    chnvibdelay[X] = insvibdelay[instr - 1]
    chnparam[X] = insvibparam[instr - 1]

    # Toneportamento check: if current effect is toneporta, skip most of init
    if chnnewfx[X] == TONEPORTA (3):
        goto nonewnoteinit

    # Load first-frame waveform
    if FIXEDPARAMS == 0:
        firstwave = insfirstwave[instr - 1]
        if firstwave == 0:
            goto skipwave           # 0 = don't change waveform
        if firstwave >= $FE:
            goto skipwave2          # $FE/$FF = skip waveform but set gate
    else:
        firstwave = FIRSTWAVEPARAM  # fixed parameter

    chnwave[X] = firstwave

    if NUMLEGATOINSTR > 0 or NOFIRSTWAVECMD == 0:
        chngate[X] = $FF           # gate on (no bits masked)
    else:
        chngate[X]++               # increment from $FE to $FF

skipwave:
    # Load pulse pointer (if nonzero)
    pulse_ptr = inspulseptr[instr - 1]
    if pulse_ptr != 0:
        chnpulseptr[X] = pulse_ptr
        chnpulsetime[X] = 0        # reset pulse step duration

    # Load filter pointer (if nonzero)
    filt_ptr = insfiltptr[instr - 1]
    if filt_ptr != 0:
        filtstep = filt_ptr         # GLOBAL filter step
        filttime = 0                # reset filter modulation

    # Load wave pointer (always)
    chnwaveptr[X] = inswaveptr[instr - 1]

    # Load ADSR (SR first, then AD -- this is the Group B change)
    if BUFFEREDWRITES == 0:
        SID[$06 + X] = inssr[instr - 1]    # sustain/release
        SID[$05 + X] = insad[instr - 1]    # attack/decay
    else:
        chnsr[X] = inssr[instr - 1]
        chnad[X] = insad[instr - 1]

    # Execute tick-0 effect (using the jump target set in 5a)
    param = chnnewparam[X]
    call tick0_handler(param)       # JSR to tick0jump1 target

    # Write registers -- GROUP B: wave only (not all regs)
    if BUFFEREDWRITES == 0:
        goto loadregswaveonly       # writes ONLY waveform to SID
    else:
        goto loadregs               # buffered mode writes all regs
```

**Critical Group B behavior:** After new-note init, only the waveform register is written to SID (via `mt_loadregswaveonly`). Frequency is NOT written on the new-note frame. It appears on the next frame when `mt_loadregs` runs.

Exception: With BUFFEREDWRITES enabled, all registers are written (loadregs includes freq, pulse, ADSR, and wave).

### 5e. No new note: execute tick-0 effect only

```
nonewnoteinit:
    param = chnnewparam[X]
    call tick0_handler(param)       # JSR to tick0jump2 target
    # Fall through to wave table execution
```

## 6. Tick-0 Effects

These run on tick 0 only, dispatched via `mt_tick0jumptbl`. The accumulator A holds the effect parameter value (`chnnewparam`).

### Effect 0: Instrument Vibrato
```
if NOINSTRVIB == 0:
    param = insvibparam[instr - 1]    # load from instrument, not from A
    goto tick0_34                      # store as vibrato param
else:
    # Group B (without vibfix): A contains stale value!
    goto tick0_34
```

### Effects 1, 2: Portamento Up/Down
```
    chnvibtime[X] = 0              # reset vibrato phase
    # Fall through to tick0_34
```

### Effects 3, 4: Toneportamento, Vibrato
```
tick0_34:
    chnparam[X] = A                # store effect parameter (speed index)
    chnfx[X] = chnnewfx[X]        # activate continuous effect
    return
```

### Effect 5: Set AD
```
    SID[$05 + X] = A               # (or chnad[X] if buffered)
    return
```

### Effect 6: Set SR
```
    SID[$06 + X] = A               # (or chnsr[X] if buffered)
    return
```

### Effect 7: Set Waveform
```
    chnwave[X] = A
    return
```

### Effect 8: Set Wave Pointer
```
    chnwaveptr[X] = A
    chnwavetime[X] = 0             # reset wave delay counter
    return
```

### Effect 9: Set Pulse Pointer
```
    chnpulseptr[X] = A
    chnpulsetime[X] = 0             # reset pulse step duration
    return
```

### Effect A: Set Filter Pointer
```
    filttime = 0                    # reset filter modulation
    filtstep = A                    # set global filter step
    return
```

### Effect B: Set Filter Control
```
    filtctrl = A                    # resonance + channel routing
    if A == 0:
        filtstep = 0               # also stop filter step-programming
    return
```

### Effect C: Set Filter Cutoff
```
    filtcutoff = A
    return
```

### Effect D: Set Master Volume / Timing Mark
```
    if NOAUTHORINFO == 0 AND A >= $10:
        # Timing mark: store in author info area
        mt_author[31] = A
        return
    mastervol = A                   # values 0-15
    return
```

### Effect E: Set Funktempo
```
    # A = speed table index
    funktempotbl[0] = speedlefttbl[A - 1]
    funktempotbl[1] = speedrighttbl[A - 1]
    A = 0
    # Fall through to set global tempo = 0 (which activates funktempo)
    goto tick0_f_setglobaltempo
```

### Effect F: Set Tempo
```
    if A >= $80:                    # bit 7 set = channel tempo
        chntempo[X] = A AND $7F
    else:                           # global tempo
        chntempo[0] = A
        chntempo[7] = A             # (if NUMCHANNELS > 1)
        chntempo[14] = A            # (if NUMCHANNELS > 2)
    return
```

## 7. Wave Table Execution

This runs every frame (both tick 0 and tick N), after the tick-0 sequencer/effect processing OR directly after the tick counter on non-zero ticks.

```
mt_waveexec:
    Y = chnwaveptr[X]
    if Y == 0:
        goto wavedone               # wave table stopped

    left = wavetbl[Y - 1]          # left column (waveform / delay / command)

    # --- Delay handling (NOWAVEDELAY == 0) ---
    if left < $10:                  # values $00-$0F = delay
        if left != chnwavetime[X]:  # delay not yet reached
            chnwavetime[X]++
            goto wavedone           # don't advance, don't change wave
        # delay reached, fall through
        left = left - $10          # undo the +$10 offset... but wait:
                                   # actually: sbc #$10 on the original value
                                   # If left was 0-F (delay), we skip wave change
                                   # and go to nowavechange
```

Let me re-read the wave delay logic more carefully:

```
mt_waveexec:
    Y = chnwaveptr[X]
    if Y == 0:
        goto wavedone

    left = wavetbl[Y - 1]

    if NOWAVEDELAY == 0:
        if left < $10:                     # $00-$0F: delay count
            if left == chnwavetime[X]:     # delay expired?
                chnwavetime[X]++           # (increments past match, won't match again)
                # fall through to nowavechange (no wave set)
            else:
                chnwavetime[X]++
                goto wavedone              # still waiting
            # Actually, re-reading the assembly:
            # cmp mt_chnwavetime,x / beq mt_nowavechange
            # So: if delay == wavetime, skip to nowavechange
            # inc mt_chnwavetime,x / bne mt_wavedone
            # If delay != wavetime, increment and exit
```

Let me re-read the exact assembly one more time to get this right.

```asm
                cmp #$10                        ;0-15 used as delay
                bcs mt_nowavedelay              ;>= $10: not a delay
                cmp mt_chnwavetime,x
                beq mt_nowavechange             ;delay expired -> don't set wave, advance step
                inc mt_chnwavetime,x
                bne mt_wavedone                 ;still waiting (always branches)
mt_nowavedelay:
                sbc #$10                        ;remove delay offset
```

So the actual logic is:

```
    left = wavetbl[Y - 1]

    if left < $10:                              # delay entry ($00-$0F)
        if left == chnwavetime[X]:
            goto nowavechange                   # delay done: advance step but don't set waveform
        chnwavetime[X]++
        goto wavedone                           # still in delay, exit

    left = left - $10                           # remove +$10 offset applied during packing
                                                # (carry is set from the cmp #$10 / bcs)

    # --- Command check ---
    if left >= $E0:                             # $F0-$FE after -$10 = commands $E0-$EE
        goto nowavechange                       # don't set waveform, handle as command below

    chnwave[X] = left                           # set waveform ($00-$DF after adjustment)

nowavechange:
    # Check for jump / advance
    next = wavetbl[Y]                           # peek at NEXT left column entry
    if next == $FF (LOOPWAVE):                  # jump marker
        Y++
        chnwaveptr[X] = notetbl[Y - 1]         # jump target from right column
    else:
        chnwaveptr[X] = Y + 1                   # advance to next step

    chnwavetime[X] = 0                          # reset delay counter

    # --- Command execution ---
    prev_left = wavetbl[Y - 2]                  # the entry we just processed
    if prev_left >= $E0:                        # was it a command? ($E0-$EF after -$10)
        goto wavecmd                            # execute wave command

    # --- Note/frequency from right column ---
    right = notetbl[Y - 2]                      # right column of current step

    if right == 0:
        goto wavedone                           # no frequency change -> go to effects

    if right < $80:                             # bit 7 clear = absolute note
        goto wavenoteabs
    else:                                       # bit 7 set = relative note
        note = right + chnnote[X]               # add to base note
        note = note AND $7F                     # mask to 7 bits

wavenoteabs:
    chnlastnote[X] = note                       # (for calculated speed)
    chnvibtime[X] = 0                           # reset vibrato phase
    freq = freqtbl[note - FIRSTNOTE]
    chnfreqlo[X] = freq low byte
    chnfreqhi[X] = freq high byte
```

**Right column encoding (after packing transformation):** The packer XORs the right byte with $80. So in the packed data: bit 7 SET = absolute note, bit 7 CLEAR = relative offset. The player checks `bpl mt_wavenoteabs` (bit 7 clear = positive = absolute). Wait, let me re-read:

```asm
mt_wavefreq:
                bpl mt_wavenoteabs      ; if positive (bit 7 clear) -> absolute
                adc mt_chnnote,x        ; bit 7 set -> relative: add to base note
                and #$7f
mt_wavenoteabs:
```

So after the XOR $80 transformation: bit 7 CLEAR (positive) = absolute, bit 7 SET (negative) = relative. This is the OPPOSITE of the original .sng format where bit 7 set meant absolute.

**Wave command detail:** When `left >= $E0` (values $E0-$EF after the -$10 adjustment, which means original packed values $F0-$FE):

```
wavecmd:
    cmd = (left - $E0) AND $0F                  # effectively: original & $0F
    param = notetbl[Y - 2]                      # right column = parameter

    if cmd < 5:
        # Commands 0-4: continuous effects (portamento, vibrato, etc.)
        # Dispatch through effectjumptbl (same as tick-N effects)
        # Uses param as a speed table index
        goto setspeedparam -> effectjump

    # Commands 5-15: tick-0 effects
    # Dispatch through tick0jumptbl
    call tick0_handler[cmd](param)
    goto done
```

So wave table commands $F0-$F4 trigger continuous effects (portamento up/down, toneporta, vibrato), and $F5-$FE trigger the same tick-0 effects as pattern commands (set AD, set SR, set wave, set pointers, etc.).

## 8. Continuous Effects (Tick N)

After wave table execution, if there's no frequency change from the wave table (right column = 0 or wave table stopped), the player runs continuous effects:

```
wavedone:
    if REALTIMEOPTIMIZATION AND chncounter[X] == 0:
        goto gatetimer              # skip effects on tick 0 (already handled)

    fx = chnfx[X]
    Y = chnparam[X]                 # speed table index

    # Calculate speed from speed table
    speed_left = speedlefttbl[Y - 1]

    if speed_left >= $80:           # calculated speed (bit 7 set)
        goto calculatedspeed
    else:                           # normal speed
        temp2 = speed_left          # speed high byte
        temp1 = speedrighttbl[Y - 1]  # speed low byte
        goto effectjump

calculatedspeed:
    # Speed is relative to note's frequency interval
    divisor = speedrighttbl[Y - 1]  # right shift count
    lastnote = chnlastnote[X]
    # Calculate freq difference between lastnote and lastnote+1
    diff = freqtbl[lastnote + 1 - FIRSTNOTE] - freqtbl[lastnote - FIRSTNOTE]
    # Right-shift diff by divisor
    for i in range(divisor):
        diff >>= 1
    temp1 = diff low byte
    temp2 = diff high byte

effectjump:
    dispatch to effect handler based on fx
```

### Effect 0: Instrument Vibrato (continuous)

```
    if Y == 0:                      # speed 0 = no vibrato
        goto done
    if chnvibdelay[X] != 0:
        chnvibdelay[X]--
        goto done                   # still in delay period
    # (falls through to vibrato code -- same as effect 4)
```

### Effect 4: Vibrato (continuous)

```
    speed_half = speedlefttbl[Y - 1] AND $7F    # vibrato speed (half-cycle width)
    # temp2 set to 0 for normal speed, or calculated

    time = chnvibtime[X]
    if time >= 0:                   # positive half
        if time > speed_half:       # reached peak
            time = time EOR $FF     # negate (flip to negative half)
        elif time == speed_half:
            time = time EOR $FF     # negate at exact peak
            # (no add, skip next)

    if time was negated (carry clear):
        time = time + 2             # advance phase
    else:
        time = time + 2

    chnvibtime[X] = time

    if time is even (bit 0 clear after LSR):
        goto freqadd                # add speed to frequency
    else:
        goto freqsub                # subtract speed from frequency
```

The vibrato oscillates the frequency up and down. `chnvibtime` cycles: 0, 2, 4, ..., speed*2, then flips negative and counts back. The LSR checks the low bit of the vibrato timer to alternate between adding and subtracting.

### Effects 1, 2: Portamento Up/Down (continuous)

```
    # temp1/temp2 = speed (from speed table, 16-bit)

    if fx == 1 (PORTAUP):
        goto freqadd
    if fx == 2 (PORTADOWN):
        goto freqsub

freqadd:
    chnfreqlo[X] = chnfreqlo[X] + temp1
    chnfreqhi[X] = chnfreqhi[X] + temp2 + carry

freqsub:
    chnfreqlo[X] = chnfreqlo[X] - temp1
    chnfreqhi[X] = chnfreqhi[X] - temp2 - borrow
```

### Effect 3: Toneportamento (continuous)

```
    if Y == 0:                      # speed 0 = tie note (instant)
        goto effect_3_found

    # Calculate distance to target
    target_note = chnnote[X]
    target_freq = freqtbl[target_note - FIRSTNOTE]
    offset = current_freq - target_freq     # 16-bit signed

    if offset >= 0:                 # current > target: need to go down
        offset = offset - speed     # subtract speed
        if sign changed (became negative):
            goto effect_3_found     # overshot -> snap to target
        goto freqsub

    if offset < 0:                  # current < target: need to go up
        offset = offset + speed     # add speed
        if sign changed (became positive):
            goto effect_3_found     # overshot -> snap to target
        goto freqadd

effect_3_found:
    # Snap frequency to target note
    note = chnnote[X]
    chnlastnote[X] = note
    freq = freqtbl[note - FIRSTNOTE]
    chnfreqlo[X] = freq lo
    chnfreqhi[X] = freq hi
    chnvibtime[X] = 0
```

## 9. Pulse Table Execution

After effects (or after wave table if no effects), pulse processing runs:

```
mt_pulseexec:
    Y = chnpulseptr[X]
    if Y == 0:
        goto pulseskip              # pulse stopped

    if PULSEOPTIMIZATION:
        if chncounter[X] == 0 AND chnpattptr[X] == 0:
            goto pulseskip          # skip when sequencer just ran and pattptr is 0

    if chnpulsetime[X] != 0:
        goto pulsemod               # modulation step in progress

# New pulse step
    left = pulsetimetbl[Y - 1]

    if left >= $80:                 # SETPULSE: set absolute pulse width
        if SIMPLEPULSE == 0:
            chnpulsehi[X] = left    # high byte (includes $80 flag... see note)
        chnpulselo[X] = pulsespdtbl[Y - 1]  # low byte
        goto nextpulsestep

    # $01-$7F: modulation step
    chnpulsetime[X] = left          # set modulation duration

pulsemod:
    if SIMPLEPULSE == 0:
        speed = pulsespdtbl[Y - 1]  # signed speed byte
        if speed >= 0:
            # positive: pulse up
            chnpulselo[X] = chnpulselo[X] + speed
            if carry: chnpulsehi[X]++
        else:
            # negative: pulse down
            chnpulsehi[X]--
            chnpulselo[X] = chnpulselo[X] + speed  # (speed is negative, so wraps)
            if carry: chnpulsehi[X]++
    else:
        # SIMPLEPULSE: 8-bit only
        chnpulselo[X] = chnpulselo[X] + pulsespdtbl[Y - 1] + carry_bit
        # (adc #$00 adds carry from the clc+adc sequence)

    chnpulsetime[X]--
    if chnpulsetime[X] != 0:
        goto pulsedone2             # still modulating

nextpulsestep:
    next = pulsetimetbl[Y]          # peek at next entry
    if next == $FF (LOOPPULSE):
        chnpulseptr[X] = pulsespdtbl[Y]  # jump target
    else:
        chnpulseptr[X] = Y + 1      # advance

pulsedone:
    if BUFFEREDWRITES == 0:
        SID[$02 + X] = chnpulselo[X]     # pulse width low
        if SIMPLEPULSE == 0:
            SID[$03 + X] = chnpulsehi[X] # pulse width high
        else:
            SID[$03 + X] = chnpulselo[X] # (same value for both)

pulseskip:
```

**Note on SIMPLEPULSE:** When the packer enables SIMPLEPULSE, set-pulse entries have the high nibble moved to the right column and the left column clamped to $80. The modulation is 8-bit only (the low and high pulse bytes get the same value).

## 10. Gate Timer and New Note Fetch

After pulse execution, the player checks whether it's time to fetch a new note:

```
    if chncounter[X] == chngatetimer[X]:
        goto getnewnote
    else:
        goto loadregs               # write registers and return
```

**Gate timer meaning:** The gate timer determines how many ticks BEFORE the new note the gate goes off (hard restart begins). When the counter counts down to this value, it's time to read the next row from the pattern.

For example, if tempo = 6 and gatetimer = 2:
- Tick 6 (counter=6): note plays, gate on
- Tick 5 (counter=5): normal tick
- Tick 4 (counter=4): normal tick
- Tick 3 (counter=3): normal tick
- Tick 2 (counter=2): gate timer match -> fetch new note, possibly hard restart
- Tick 1 (counter=1): hard restart ADSR active
- Tick 0 (counter=0): tick 0, new note init

### New Note Fetch (Pattern Reader)

```
getnewnote:
    patt_num = chnpattnum[X]
    patt_addr = patttbl[patt_num]
    pos = chnpattptr[X]
    byte = patt_addr[pos]

    # Decode pattern byte
    if byte < $40 (FX):            # $01-$3F: instrument change
        goto instr_change

    if byte < $60 (NOTE):          # $40-$5F: effect (with or without note)
        goto fx_change

    if byte < $C0 (FIRSTPACKEDREST):  # $60-$BF: note/rest/gate
        goto note_handling

    # $C0-$FF: packed rest
    goto packedrest
```

### Packed Rest

```
packedrest:
    if chnpackedrest[X] != 0:
        # Already in a packed rest sequence
        chnpackedrest[X] = chnpackedrest[X] + carry  # (ADC #$00, carry may vary)
        if chnpackedrest[X] == 0:
            goto rest                # rest count expired
        goto loadregs               # still resting

    # First encounter of packed rest byte
    chnpackedrest[X] = byte + carry  # store initial count
    if chnpackedrest[X] == 0:
        goto rest
    goto loadregs
```

Packed rests encode multiple rest frames in a single byte. On each entry to `getnewnote`, carry is SET (from the `cmp #FIRSTPACKEDREST` that routed here). First time (`chnpackedrest == 0`), the pattern byte is loaded. Then `adc #$00` adds 1 (carry). The result is stored in `chnpackedrest`. If it wrapped to 0, rest is done; otherwise, `loadregs` runs and the pattern pointer is NOT advanced. On subsequent frames, `chnpackedrest` is loaded (nonzero) and incremented again. The rest ends when the counter wraps to $00.

Duration: $C0 = 64 frames, $FE = 2 frames, $FF = 1 frame. Formula: 256 - byte_value frames.

### Instrument Change

```
instr_change:
    chninstr[X] = byte              # store new instrument number
    pos++
    byte = patt_addr[pos]           # next byte is either FX or note
    if byte >= $60 (NOTE):
        goto note_handling
    # else: it's an FX byte, fall through to fx_change
```

### Effect Change

```
fx_change:
    has_note = (byte >= $50)        # FXONLY=$50: if >= $50, note does NOT follow
    fx_num = byte AND $0F
    chnnewfx[X] = fx_num

    if fx_num == 0:
        goto fx_noparam             # effect 0 has no parameter byte

    pos++
    chnnewparam[X] = patt_addr[pos]

fx_noparam:
    if has_note:                    # $50-$5F: FX only, no note follows
        goto rest                   # advance pointer, done
    # $40-$4F: FX followed by note
    pos++
    byte = patt_addr[pos]
    # fall through to note_handling
```

### Note Handling

```
note_handling:
    if byte == $BD (REST):
        goto rest                   # rest: no note change
    if byte == $BE (KEYOFF):
        goto gate_keyoff
    if byte == $BF (KEYON):
        goto gate_keyon

    # $60-$BC: normal note
    note = byte + chntrans[X]       # add transpose (signed, wraps)
    chnnewnote[X] = note            # flag for new note init on tick 0

    # Toneportamento check
    if chnnewfx[X] == TONEPORTA (3):
        goto rest                   # toneporta: no gate off, no hard restart

    # Instrument type check for hard restart
    if chninstr[X] >= FIRSTNOHRINSTR:
        if NUMLEGATOINSTR > 0 AND chninstr[X] >= FIRSTLEGATOINSTR:
            goto rest               # legato: no gate off at all
        goto skiphr                 # no-HR instrument: gate off but no HR ADSR

    # --- HARD RESTART ---
    # Write hard restart ADSR (SR first, then AD -- Group B order)
    SID[$06 + X] = SRPARAM          # (or chnsr if buffered) typically $00
    SID[$05 + X] = ADPARAM          # (or chnad if buffered) typically $00

skiphr:
    chngate[X] = $FE               # gate OFF (bit 0 cleared by AND with wave)

gate_keyoff:                        # KEYOFF ($BE)
    byte = byte OR $F0             # $BE -> $FE
    chngate[X] = byte              # $FE = gate off

gate_keyon:                         # KEYON ($BF)
    byte = byte OR $F0             # $BF -> $FF
    chngate[X] = byte              # $FF = gate on
```

### End of Pattern / Advance Pointer

```
rest:
    pos++
    next = patt_addr[pos]
    if next == $00 (ENDPATT):
        chnpattptr[X] = 0          # signal "need new pattern" for next tick 0
    else:
        chnpattptr[X] = pos        # save position within pattern
```

## 11. Register Writes

At the end of channel processing, registers are written to SID.

### Non-buffered writes (BUFFEREDWRITES == 0)

```
mt_loadregs:
    SID[$00 + X] = chnfreqlo[X]    # frequency low
    SID[$01 + X] = chnfreqhi[X]    # frequency high

mt_loadregswaveonly:
    wave = chnwave[X] AND chngate[X]   # apply gate mask
    SID[$04 + X] = wave             # waveform + gate bit
    return
```

**Register write order:** Freq lo, freq hi, wave+gate. Pulse and ADSR are written inline during their respective processing (pulse during pulse exec, ADSR during new-note init or hard restart).

### Buffered writes (BUFFEREDWRITES != 0, ZPGHOSTREGS == 0)

```
mt_loadregs:
    # Check for sound FX override
    if chnsfx[X] != 0:
        goto sfxexec

    SID[$02 + X] = chnpulselo[X]    # pulse low
    SID[$03 + X] = chnpulsehi[X]    # pulse high (or same as low for SIMPLEPULSE)
    SID[$06 + X] = chnsr[X]         # sustain/release
    SID[$05 + X] = chnad[X]         # attack/decay

mt_loadregswavefreq:
    SID[$00 + X] = chnfreqlo[X]     # frequency low
    SID[$01 + X] = chnfreqhi[X]     # frequency high

mt_loadregswaveonly:
    wave = chnwave[X] AND chngate[X]
    SID[$04 + X] = wave
    return
```

**Buffered register write order:** Pulse lo, pulse hi, SR, AD, freq lo, freq hi, wave+gate.

**ADSR order in buffered writes (Group B):** SR is written BEFORE AD. This ensures the SID latches the correct attack/decay on the gate transition.

## 12. Hard Restart Sequence (Frame by Frame)

Hard restart is the mechanism that ensures clean note starts on the SID chip. Here's the exact frame-by-frame sequence for a note with gatetimer = 2 and tempo = 6:

```
Frame N+0 (counter=6, tick 0):
    Previous note plays. Sequencer advances.
    New note init: loads instrument ADSR, waveform, wave/pulse/filter pointers.
    Gate = $FF (on). Wave register written with gate bit set.

Frame N+1 (counter=5):
    Normal tick. Wave table advances. Effects run.
    Gate still $FF.

Frame N+2 (counter=4):
    Normal tick. Wave table advances. Effects run.

Frame N+3 (counter=3):
    Normal tick. Wave table advances. Effects run.

Frame N+4 (counter=2 == gatetimer):
    *** Gate timer fires ***
    Pattern reader runs. Reads next note.
    Hard restart: SID[$06+X] = SRPARAM (usually $00)
                  SID[$05+X] = ADPARAM (usually $00)
    Gate: chngate = $FE (gate off, bit 0 clear)
    loadregs: freq written, wave AND $FE written (gate bit = 0)
    -> SID sees: ADSR = $00/$00, gate OFF. Release begins with rate 0 = instant.

Frame N+5 (counter=1):
    Normal tick (counter > 0, not tick 0, not gatetimer).
    Wave table continues, effects continue.
    Gate still $FE. ADSR still $00/$00.
    -> SID output quickly drops to 0 (hard restart ADSR zeroes the envelope).

Frame N+6 (counter=0, tick 0):
    *** New note init ***
    chnnewnote is set -> newnoteinit runs.
    Loads instrument's real ADSR (SR first, then AD).
    Loads first-frame waveform into chnwave.
    Gate = $FF (on).
    loadregswaveonly: writes wave AND $FF = waveform with gate ON.
    -> SID sees: new ADSR, gate ON. Attack begins from zero envelope.
    -> Frequency is NOT written this frame (Group B: waveonly).

Frame N+7 (counter=tempo-1):
    First normal tick of new note.
    loadregs: frequency finally written to SID.
    -> SID now has correct frequency + waveform + ADSR + gate on.
```

**No-HR instruments:** Skip the ADSR zeroing. Gate still goes off ($FE) but ADSR retains the previous instrument's values. The envelope continues its current phase.

**Legato instruments:** Skip gate-off entirely. Go straight to rest. On tick 0, new note init loads the new note number, wave pointer, ADSR, etc., but the gate never turns off. This produces a smooth pitch change without retriggering the envelope.

## 13. Complete Frame Execution Order (Summary)

```
mt_play():
    1. Check for song init (first call only)
    2. Filter table execution
       -> Writes SID $16 (cutoff), $17 (filter ctrl), $18 (filter type + volume)

    3. For each channel (X = 0, 7, 14):
       a. Decrement tick counter
       b. If tick 0:
          - Setup tick-0 effect jump targets
          - If pattern pointer == 0: run sequencer (advance orderlist, load pattern)
          - Load gate timer from instrument
          - If new note pending: full new note init
            * Store note, reset effects
            * Load vibrato params
            * Check toneporta (skip gate/HR if active)
            * Load first wave, pulse ptr, filter ptr, wave ptr
            * Load ADSR (SR first, then AD)
            * Execute tick-0 effect
            * Write wave register only (Group B)
            * RETURN from channel
          - If no new note: execute tick-0 effect only
       c. If tick N (not zero):
          - Reload tempo if counter underflowed (handle funktempo)

       d. Wave table execution (every frame)
          - Handle delay ($00-$0F)
          - Set waveform ($10-$DF after offset removal)
          - Handle commands ($F0-$FE via $E0-$EE)
          - Set frequency from right column (absolute or relative)
          - Advance step pointer (or jump on $FF)

       e. If no freq change from wave table:
          - Continuous effects (portamento, vibrato, toneporta)
          - Uses speed table for velocity calculation

       f. Pulse table execution
          - Set absolute pulse ($80+)
          - Modulate pulse (signed speed add)
          - Advance step pointer (or jump on $FF)
          - Write pulse to SID (non-buffered mode)

       g. Gate timer check
          - If counter == gatetimer: fetch new note from pattern
            * Parse instrument changes, effects, notes
            * Handle packed rests
            * Hard restart (zero ADSR, gate off)

       h. Write registers to SID
          - Non-buffered: freq lo, freq hi, wave+gate
          - Buffered: pulse lo, pulse hi, SR, AD, freq lo, freq hi, wave+gate

       i. RETURN from channel
```

## 14. Key Behavioral Notes for SIDfinity Implementation

1. **SR before AD everywhere (Group B).** This is the defining characteristic. All ADSR writes -- hard restart, new-note init, buffered loadregs -- write SR ($D406) before AD ($D405).

2. **Wave-only on new note frame.** After new-note init, only the waveform register is written. Frequency appears on the NEXT frame. This creates a 1-frame delay between gate-on and the correct frequency being set.

3. **Filter is global.** One filter program shared by all channels. Any channel's instrument or pattern command can redirect the filter pointer.

4. **Tables are 1-indexed.** All table pointers are 1-based. A pointer value of 0 means "stopped." Access is `table[ptr - 1]`.

5. **Self-modifying code for globals.** Filter cutoff, filter control, filter type, master volume, filtstep, filttime, funktempotbl, and effect jump targets are all stored as immediate operands of instructions and modified in place.

6. **Wave table delay.** Values $00-$0F in the packed wave table left column are delay counts. The delay counter (`chnwavetime`) increments each frame. When it matches the delay value, the step advances but no waveform is set. The delay counter resets to 0 when the step advances.

7. **Packed wave table offset.** Non-delay, non-command waveforms have +$10 added during packing. The player subtracts $10 before use. So packed $11 = actual waveform $01, packed $51 = actual $41, etc.

8. **Right column XOR $80.** The note table (wave table right column) has bit 7 flipped during packing. In the player: bit 7 clear (positive) = absolute note number, bit 7 set (negative) = relative to current note.

9. **Funktempo.** When tempo is 0 or 1, it indexes into a 2-byte table. The index toggles each frame. The actual tick count loaded from the table has 1 subtracted (due to the SBC with carry clear).

10. **Pulse optimization.** When PULSEOPTIMIZATION is enabled, pulse execution is skipped on the frame when the sequencer just fetched a new pattern (counter == 0 AND pattptr == 0). The gate timer check also moves before pulse execution.

11. **Calculated speed.** When the speed table left column has bit 7 set, the speed is calculated relative to the frequency interval between the current note and the next semitone. The right column specifies how many times to right-shift this interval.

12. **Pattern byte encoding ranges:**
    - $00: end of pattern
    - $01-$3F: instrument number (followed by FX or note)
    - $40-$4F: effect + note follows
    - $50-$5F: effect only (no note follows)
    - $60-$BC: note values (note = byte, before transpose)
    - $BD: rest
    - $BE: key off
    - $BF: key on
    - $C0-$FF: packed rest (duration encoded in value)

13. **Orderlist encoding:**
    - $00-$CF: pattern number
    - $D0-$DF: repeat command (count = value - $D0)
    - $E0-$EF: transpose down ($E0 = -16 semitones ... $EF = -1)
    - $F0-$FE: transpose up ($F0 = 0 ... $FE = +14)
    - $FF: end/loop marker (followed by restart position byte)
