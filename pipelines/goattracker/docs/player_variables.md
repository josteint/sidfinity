# GT2 V2.68 Player Variables Reference

**Source:** `src/GoatTracker_2.68/src/player.s`
**Date:** 2026-04-02

## Overview

The GT2 player stores per-channel variables in memory blocks with stride 7 (one byte per slot, 7 bytes apart for each of the 3 channels). Channel index X = 0, 7, or 14 ($00, $07, $0E). All per-channel variables are accessed as `variable,x`.

Variables are organized into blocks. Depending on which optimization flags are active, the player uses either a "normal" layout or an "optimized" layout. There is also an "extended" block that appears only when certain features are enabled.

Global variables use self-modifying code (STA into immediate operands) rather than fixed memory locations.

## Conditional Compilation Flags

The following flags are injected by greloc.c before assembly. When a `NOxxx` flag is 1, that feature is excluded (code and variables eliminated).

| Flag | Meaning |
|------|---------|
| ZPGHOSTREGS | Use zero-page ghost registers instead of SID direct writes |
| BUFFEREDWRITES | Buffer all SID writes (implies ghost regs in non-ZP memory) |
| FIXEDPARAMS | Gate timer and first-wave are compile-time constants |
| SIMPLEPULSE | Simplified pulse modulation (no hi-byte tracking) |
| PULSEOPTIMIZATION | Reorder pulse exec to skip on tick 0 |
| REALTIMEOPTIMIZATION | Skip continuous effects on tick 0 |
| NOEFFECTS | No pattern effects at all |
| NOGATE | No KEYON/KEYOFF commands |
| NOFILTER | No filter table |
| NOFILTERMOD | No filter modulation steps |
| NOPULSE | No pulse table |
| NOPULSEMOD | No pulse modulation steps |
| NOWAVEDELAY | No wave delay values (0-15) in wave table |
| NOWAVECMD | No wave table commands ($E0-$FE) |
| NOREPEAT | No orderlist repeat command |
| NOTRANS | No orderlist transpose command |
| NOPORTAMENTO | No portamento up/down effects |
| NOTONEPORTA | No tone portamento effect |
| NOVIB | No vibrato effect |
| NOINSTRVIB | No instrument vibrato |
| NOSETAD | No set-AD effect |
| NOSETSR | No set-SR effect |
| NOSETWAVE | No set-waveform effect |
| NOSETWAVEPTR | No set-wave-pointer effect |
| NOSETPULSEPTR | No set-pulse-pointer effect |
| NOSETFILTPTR | No set-filter-pointer effect |
| NOSETFILTCTRL | No set-filter-control effect |
| NOSETFILTCUTOFF | No set-filter-cutoff effect |
| NOSETMASTERVOL | No set-master-volume effect |
| NOFUNKTEMPO | No funktempo |
| NOGLOBALTEMPO | No global tempo setting |
| NOCHANNELTEMPO | No per-channel tempo |
| NOFIRSTWAVECMD | No first-wave special commands ($00, $FE, $FF) |
| NOCALCULATEDSPEED | No calculated (relative-to-note) speed values |
| NONORMALSPEED | No normal (absolute) speed values |
| NOZEROSPEED | No zero-speed entries |
| SOUNDSUPPORT | Sound effect playback support |
| VOLSUPPORT | External master volume control |
| NOAUTHORINFO | Omit author info block at base+$20 |

## Variable Layout Condition

The "normal" variable layout is used when ANY of these conditions hold:
- NOEFFECTS == 0
- NOWAVEDELAY == 0
- NOTRANS == 0
- NOREPEAT == 0
- FIXEDPARAMS == 0
- ZPGHOSTREGS != 0
- BUFFEREDWRITES != 0
- NOCALCULATEDSPEED == 0

Otherwise the "optimized" (minimal) layout is used.

---

## Normal Variable Layout

### Block 1: Sequencer/Effect Variables (stride 7)

Labels are defined on the channel-0 byte. Channel 1 is at +7, channel 2 at +14.

| Offset | Name | Size | Init | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnsongptr` | 1/ch | 0 | Current position index into the orderlist for this channel |
| +1 | `mt_chntrans` | 1/ch | 0 | Current transpose offset from orderlist (signed, applied to notes) |
| +2 | `mt_chnrepeat` | 1/ch | 0 | Current repeat counter (counts up; reset to 0 when repeat done) |
| +3 | `mt_chnpattptr` | 1/ch | 0 | Current byte offset into the current pattern (0 = fetch new pattern) |
| +4 | `mt_chnpackedrest` | 1/ch | 0 | Packed rest counter (counts down from encoded value to 0) |
| +5 | `mt_chnnewfx` | 1/ch | 0 | Effect number queued by pattern reader for tick-0 execution |
| +6 | `mt_chnnewparam` | 1/ch | 0 | Effect parameter queued by pattern reader for tick-0 execution |

### Block 2: Note/Wave/Pulse Variables (stride 7)

| Offset | Name | Size | Init | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnfx` | 1/ch | 0 | Currently active continuous effect number (0-4) |
| +1 | `mt_chnparam` | 1/ch | 0 | Currently active continuous effect parameter (speed table index) |
| +2 | `mt_chnnewnote` | 1/ch | 0 | New note pending init (NOTE+n value); 0 = no new note |
| +3 | `mt_chnwaveptr` | 1/ch | 0 | Current position in wave table (1-based; 0 = stopped) |
| +4 | `mt_chnwave` | 1/ch | 0 | Current waveform byte to write to SID register $04 |
| +5 | `mt_chnpulseptr` | 1/ch | 0 | Current position in pulse table (1-based; 0 = stopped) |
| +6 | `mt_chnpulsetime` | 1/ch | 0 | Pulse modulation step duration counter (counts down) |

### Block 3: Song/Tempo/Note Variables (stride 7)

| Offset | Name | Size | Init (ch0/ch1/ch2) | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnsongnum` | 1/ch | 0 / 1 / 2 | Index into song table (which orderlist set to use) |
| +1 | `mt_chnpattnum` | 1/ch | 0 | Current pattern number from orderlist |
| +2 | `mt_chntempo` | 1/ch | DEFAULTTEMPO | Tempo value (ticks per row; reloaded into counter) |
| +3 | `mt_chncounter` | 1/ch | 1 (from init) | Tick counter (counts down from tempo to 0; 0 = tick 0) |
| +4 | `mt_chnnote` | 1/ch | 0 | Current note number (after transpose, used for freq lookup) |
| +5 | `mt_chninstr` | 1/ch | 1 | Current instrument number (1-based; packed index) |
| +6 | `mt_chngate` | 1/ch | $FE | Gate mask ANDed with waveform: $FF=gate on, $FE=gate off |

### Block 4: Extended Variables (stride 7)

**Condition:** Present when `(ZPGHOSTREGS == 0) || (NOCALCULATEDSPEED == 0)`

| Offset | Name | Size | Init | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnvibtime` | 1/ch | 0 | Vibrato phase/direction counter (bit 7 = direction) |
| +1 | `mt_chnvibdelay` | 1/ch | 0 | Vibrato delay counter (counts down; vibrato starts at 0) |
| +2 | `mt_chnwavetime` | 1/ch | 0 | Wave delay counter (counts up to match delay value) |
| +3 | `mt_chnfreqlo` | 1/ch | 0 | Frequency register low byte (shadow) |
| +4 | `mt_chnfreqhi` | 1/ch | 0 | Frequency register high byte (shadow) |
| +5 | `mt_chnpulselo` | 1/ch | 0 | Pulse width register low byte (shadow) |
| +6 | `mt_chnpulsehi` | 1/ch | 0 | Pulse width register high byte (shadow) |

### Block 5: Further Extended Variables (stride 7)

**Condition:** Present when `(BUFFEREDWRITES != 0) || (FIXEDPARAMS == 0) || (NOCALCULATEDSPEED == 0)`

| Offset | Name | Size | Init | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnad` | 1/ch | 0 | Buffered Attack/Decay value |
| +1 | `mt_chnsr` | 1/ch | 0 | Buffered Sustain/Release value |
| +2 | `mt_chnsfx` | 1/ch | 0 | Sound effect state (0=none, 1=init, 2+=frame count) |
| +3 | `mt_chnsfxlo` | 1/ch | 0 | Sound effect data pointer low byte |
| +4 | `mt_chnsfxhi` | 1/ch | 0 | Sound effect data pointer high byte |
| +5 | `mt_chngatetimer` | 1/ch | 0 | Gate-off timer threshold (note triggers hard restart this many ticks before next note) |
| +6 | `mt_chnlastnote` | 1/ch | 0 | Last note set by wave table (for calculated speed) |

**Alternate Block 4** (when Block 4 condition is false but Block 5 vars are still needed via `SOUNDSUPPORT` or `FIXEDPARAMS == 0`):

| Offset | Name | Size | Init | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnvibtime` | 1/ch | 0 | (same as above) |
| +1 | `mt_chnvibdelay` | 1/ch | 0 | (same as above) |
| +2 | `mt_chnwavetime` | 1/ch | 0 | (same as above) |
| +3 | `mt_chnsfx` | 1/ch | 0 | (same as above) |
| +4 | `mt_chnsfxlo` | 1/ch | 0 | (same as above) |
| +5 | `mt_chnsfxhi` | 1/ch | 0 | (same as above) |
| +6 | `mt_chngatetimer` | 1/ch | 0 | (same as above) |

---

## Optimized Variable Layout

Used when all features that need extra variables are disabled. Fewer blocks, different ordering.

### Block 1: Sequencer Core (stride 7)

| Offset | Name | Size | Init | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnsongptr` | 1/ch | 0 | Orderlist position |
| +1 | `mt_chnpattptr` | 1/ch | 0 | Pattern byte offset |
| +2 | `mt_chnpackedrest` | 1/ch | 0 | Packed rest counter |
| +3 | `mt_chnnewnote` | 1/ch | 0 | Pending new note |
| +4 | `mt_chnwaveptr` | 1/ch | 0 | Wave table position |
| +5 | `mt_chnwave` | 1/ch | 0 | Current waveform |
| +6 | `mt_chnpulseptr` | 1/ch | 0 | Pulse table position |

### Block 2: Pulse/Vibrato/Freq (stride 7)

| Offset | Name | Size | Init | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnpulsetime` | 1/ch | 0 | Pulse step duration counter |
| +1 | `mt_chnpulselo` | 1/ch | 0 | Pulse width low byte |
| +2 | `mt_chnpulsehi` | 1/ch | 0 | Pulse width high byte |
| +3 | `mt_chnvibtime` | 1/ch | 0 | Vibrato phase counter |
| +4 | `mt_chnvibdelay` | 1/ch | 0 | Vibrato delay counter |
| +5 | `mt_chnfreqlo` | 1/ch | 0 | Frequency low byte |
| +6 | `mt_chnfreqhi` | 1/ch | 0 | Frequency high byte |

### Block 3: Song/Tempo/Note (stride 7)

Same layout as normal Block 3:

| Offset | Name | Size | Init (ch0/ch1/ch2) | Meaning |
|--------|------|------|------|---------|
| +0 | `mt_chnsongnum` | 1/ch | 0 / 1 / 2 | Song table index |
| +1 | `mt_chnpattnum` | 1/ch | 0 | Current pattern number |
| +2 | `mt_chntempo` | 1/ch | DEFAULTTEMPO | Tempo |
| +3 | `mt_chncounter` | 1/ch | 1 | Tick counter |
| +4 | `mt_chnnote` | 1/ch | 0 | Current note |
| +5 | `mt_chninstr` | 1/ch | 1 | Current instrument |
| +6 | `mt_chngate` | 1/ch | $FE | Gate mask |

Note: In the optimized layout, `mt_chntrans`, `mt_chnrepeat`, `mt_chnfx`, `mt_chnparam`, `mt_chnnewfx`, `mt_chnnewparam`, `mt_chnwavetime`, `mt_chnad`, `mt_chnsr`, `mt_chnsfx*`, `mt_chngatetimer`, and `mt_chnlastnote` do not exist.

---

## Global Variables (Self-Modifying Code)

These are stored as immediate operands within instructions. They are NOT in the channel variable blocks.

| Name | Location | Init | Meaning |
|------|----------|------|---------|
| `mt_initsongnum+1` | Operand of `ldy #$00` in mt_play | $00, then $FF after init | Song init flag. Non-negative triggers init; set to $FF (negative) after init completes |
| `mt_filtctrl+1` | Operand of `lda #$00` | 0 | Filter control register: resonance (hi nibble) + channel routing (lo 3 bits) |
| `mt_filtstep+1` | Operand of `ldy #$00` in mt_filtstep | 0 | Current filter table position (1-based; 0 = stopped) |
| `mt_filttime+1` | Operand of `lda #$00` in mt_filttime | 0 | Filter modulation duration counter. Only when NOFILTERMOD==0 |
| `mt_filtcutoff+1` | Operand of `lda #$00` in mt_filtcutoff | 0 | Current filter cutoff high byte |
| `mt_filttype+1` | Operand of `lda #$00` in mt_filttype | 0 | Filter type/passband bits (hi nibble of $D418) |
| `mt_masterfader+1` | Operand of `ora #$0f` in mt_masterfader | $0F | Master volume (low nibble of $D418) |
| `mt_funktempotbl` | 2 bytes | 8, 5 | Funktempo toggle values (two alternating tempo values) |
| `mt_effectnum+1` | Operand of `lda #$00` | 0 | Current effect number for wave command dispatch. Only when NOWAVECMD==0 && NOPORTAMENTO==0 |

### Zero-Page Temporaries

| Name | Location | Meaning |
|------|----------|---------|
| `mt_temp1` | zpbase+0 (or +25 with ghost regs) | General temporary / pointer lo byte |
| `mt_temp2` | zpbase+1 (or +26 with ghost regs) | General temporary / pointer hi byte |

### Zero-Page Ghost Registers (when ZPGHOSTREGS != 0)

| Name | Location | Per-channel | Meaning |
|------|----------|-------------|---------|
| `ghostfreqlo` | zpbase+0 | Yes (stride 7) | Frequency lo byte shadow |
| `ghostfreqhi` | zpbase+1 | Yes (stride 7) | Frequency hi byte shadow |
| `ghostpulselo` | zpbase+2 | Yes (stride 7) | Pulse width lo byte shadow |
| `ghostpulsehi` | zpbase+3 | Yes (stride 7) | Pulse width hi byte shadow |
| `ghostwave` | zpbase+4 | Yes (stride 7) | Waveform shadow |
| `ghostad` | zpbase+5 | Yes (stride 7) | Attack/Decay shadow |
| `ghostsr` | zpbase+6 | Yes (stride 7) | Sustain/Release shadow |
| `ghostfiltcutlow` | zpbase+21 | Global | Filter cutoff low byte shadow |
| `ghostfiltcutoff` | zpbase+22 | Global | Filter cutoff high byte shadow |
| `ghostfiltctrl` | zpbase+23 | Global | Filter control shadow |
| `ghostfilttype` | zpbase+24 | Global | Filter type + volume shadow |

When ZPGHOSTREGS is active, `mt_chnfreqlo/hi`, `mt_chnpulselo/hi`, `mt_chnad`, `mt_chnsr` are replaced by the zero-page ghost equivalents. The non-ZP channel variables for those fields do not exist.

---

## Variables Grouped by Function

### Sequencer Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chnsongptr` | Per-channel | Index into the current orderlist. Incremented after each pattern number is read. On LOOPSONG, reloaded from the restart byte |
| `mt_chnsongnum` | Per-channel | Index into mt_songtbllo/hi to get the orderlist base address. Set during init (0, 1, 2 for channels 0-2). Changed for multi-song support |
| `mt_chnpattnum` | Per-channel | Pattern number fetched from orderlist. Used to index mt_patttbllo/hi |
| `mt_chnpattptr` | Per-channel | Byte offset into current pattern data. 0 means "need new pattern from orderlist". Set to 0 at end of pattern (ENDPATT) |
| `mt_chnpackedrest` | Per-channel | Packed rest countdown. Values $C0-$FF in pattern encode multi-frame rests. Counter decrements each tick-0; new notes fetched when it reaches 0 |
| `mt_chntrans` | Per-channel | Transpose value from orderlist. $F0 = no transpose, $E0-$EF = down, $F1-$FF = up. Stored as signed offset (after `sbc #TRANS`) and added to note values |
| `mt_chnrepeat` | Per-channel | Repeat counter. Orderlist REPEAT command specifies count; this increments until match, then resets to 0 |

### Note and Instrument Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chnnote` | Per-channel | Current note number (0-95 range). Set from `mt_chnnewnote - NOTE`. Used for frequency table lookup and tone portamento target |
| `mt_chnnewnote` | Per-channel | Pending note (raw value from pattern + transpose). Non-zero triggers new-note init on next tick 0. Cleared to 0 after processing |
| `mt_chninstr` | Per-channel | Current instrument number (1-based, packed index). Set by INS command in pattern data. Used to index all mt_ins* tables |
| `mt_chngate` | Per-channel | Gate bit mask. $FF = gate on (bit 0 set after AND with wave), $FE = gate off (bit 0 clear). $BF/$BE from KEYON/KEYOFF set specific bits |
| `mt_chnwave` | Per-channel | Waveform value to write to SID $D404. Set by wave table, set-wave effect, or first-wave from instrument. ANDed with mt_chngate before SID write |

### Effect Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chnnewfx` | Per-channel | Effect number (0-$F) queued during pattern read for next tick-0 execution |
| `mt_chnnewparam` | Per-channel | Effect parameter queued during pattern read |
| `mt_chnfx` | Per-channel | Currently active continuous effect (0=instrvib, 1=porta up, 2=porta down, 3=toneporta, 4=vibrato). Set from mt_chnnewfx on tick 0 for effects 0-4 |
| `mt_chnparam` | Per-channel | Active continuous effect speed parameter (speed table index). Set from mt_chnnewparam on tick 0 |
| `mt_chnvibtime` | Per-channel | Vibrato phase accumulator. Bit 7 = direction. Toggled when magnitude reaches speed threshold. Reset to 0 on new note |
| `mt_chnvibdelay` | Per-channel | Vibrato startup delay. Loaded from instrument's vibdelay on new note. Decremented each frame; vibrato begins when 0 |
| `mt_chnlastnote` | Per-channel | Last note used for frequency (for calculated speed mode). Set by mt_wavenoteabs. Used to compute note-relative speed scaling |

### Table Pointer Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chnwaveptr` | Per-channel | Current index into wave table (1-based). 0 = wave table stopped. Loaded from instrument's waveptr on new note. Advanced each frame as wave table steps execute. On LOOPWAVE ($FF), reloaded from the jump target |
| `mt_chnpulseptr` | Per-channel | Current index into pulse table (1-based). 0 = pulse stopped. Loaded from instrument's pulseptr on new note (if non-zero). Advanced as pulse steps execute |
| `mt_filtstep+1` | Global (SMC) | Current index into filter table (1-based). 0 = filter stopped. Set from instrument's filtptr on new note, or by set-filter-pointer effect |

### Frequency and Pulse Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chnfreqlo` | Per-channel | Frequency register low byte. Set from mt_freqtbllo on note, modified by portamento/vibrato. Written to SID $D400,x |
| `mt_chnfreqhi` | Per-channel | Frequency register high byte. Set from mt_freqtblhi on note, modified by portamento/vibrato. Written to SID $D401,x |
| `mt_chnpulselo` | Per-channel | Pulse width low byte. Set by pulse table SETPULSE or modulation. Written to SID $D402,x |
| `mt_chnpulsehi` | Per-channel | Pulse width high byte. Set by pulse table SETPULSE. Written to SID $D403,x. Not present in SIMPLEPULSE mode (lo byte used for both) |

### Timer and Duration Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chntempo` | Per-channel | Tempo value: number of ticks per row. Loaded into mt_chncounter when counter goes negative. Set by SETTEMPO effect (global or per-channel) or FUNKTEMPO |
| `mt_chncounter` | Per-channel | Tick countdown. Decremented each frame. When 0: tick-0 (new note fetch, tick-0 effects). When negative: reload from tempo. Initialized to 1 |
| `mt_chngatetimer` | Per-channel | Gate-off threshold. When mt_chncounter equals this value, gate-off starts (hard restart begins) and new note is fetched. Loaded from instrument's gatetimer column. Not present when FIXEDPARAMS==1 (uses compile-time GATETIMERPARAM instead) |
| `mt_chnwavetime` | Per-channel | Wave delay counter. Counts up from 0. When wave table entry is $00-$0F (delay value), the waveform change is deferred until counter reaches that value. Reset to 0 on wave ptr advance. Only present when NOWAVEDELAY==0 |
| `mt_chnpulsetime` | Per-channel | Pulse modulation step duration. Loaded from pulse table left column when $00-$7F. Decremented each frame; when 0, next pulse step is fetched. Only meaningful when NOPULSEMOD==0 |
| `mt_filttime+1` | Global (SMC) | Filter modulation step duration. Same concept as pulse time but for filter table. Only present when NOFILTERMOD==0 |

### Buffered Write Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chnad` | Per-channel | Buffered Attack/Decay. Written to SID $D405,x during mt_loadregs. Only when BUFFEREDWRITES!=0 and ZPGHOSTREGS==0 |
| `mt_chnsr` | Per-channel | Buffered Sustain/Release. Written to SID $D406,x during mt_loadregs. Only when BUFFEREDWRITES!=0 and ZPGHOSTREGS==0 |

### Sound Effect Variables

| Variable | Type | Description |
|----------|------|-------------|
| `mt_chnsfx` | Per-channel | Sound effect state: 0=no SFX, 1=just started (hardrestart frame), 2=first data frame, 3+=subsequent frames. Only when SOUNDSUPPORT!=0 |
| `mt_chnsfxlo` | Per-channel | Sound effect data pointer low byte |
| `mt_chnsfxhi` | Per-channel | Sound effect data pointer high byte. Also used for SFX priority comparison |

---

## Detailed Read/Write Analysis

### mt_chnsongptr

- **Writes:** (1) Zeroed during `mt_resetloop` (init clears all 14*NUMCHANNELS bytes starting from mt_chnsongptr). (2) Stored from Y (incremented orderlist index) at `mt_nonewpatt`/after sequencer reads pattern number. (3) Reloaded from orderlist restart byte on LOOPSONG.
- **Reads:** `mt_sequencer` loads Y from `mt_chnsongptr,y` to index into the orderlist.

### mt_chntrans

- **Writes:** (1) Zeroed during init. (2) Set in `mt_notrans` block when orderlist byte >= TRANSDOWN: value = byte - TRANS (signed offset).
- **Reads:** `mt_normalnote` adds it to the raw note value (`adc mt_chntrans,x`).
- **Condition:** Only exists when NOTRANS==0.

### mt_chnrepeat

- **Writes:** (1) Zeroed during init. (2) Incremented in `mt_repeat`. (3) Reset to 0 in `mt_repeatdone`.
- **Reads:** `mt_repeat` compares repeat count against it.
- **Condition:** Only exists when NOREPEAT==0.

### mt_chnpattptr

- **Writes:** (1) Zeroed during init. (2) Set from Y (next byte position) at `mt_endpatt`/`mt_rest`. Set to 0 when ENDPATT ($00) encountered (triggers new pattern fetch next tick 0).
- **Reads:** (1) `mt_checknewpatt` tests if zero (need new pattern). (2) `mt_getnewnote` loads Y from it to read pattern data. (3) PULSEOPTIMIZATION reads it to skip pulse on tick 0.

### mt_chnpackedrest

- **Writes:** (1) Zeroed during init. (2) Set/incremented in `mt_packedrest` handler (loaded from pattern byte, then ADC #0 each tick 0 until wraps to 0).
- **Reads:** `mt_packedrest` checks if non-zero (continuing rest) or zero (new packed rest).

### mt_chnnewfx

- **Writes:** (1) Zeroed during init. (2) Set in `mt_fx` from pattern data (low nibble of FX byte).
- **Reads:** (1) `mt_tick0` loads Y from it for jump table dispatch. (2) `mt_tick0_34` copies it to mt_chnfx. (3) `mt_normalnote` checks for TONEPORTA to skip hard restart.
- **Condition:** Only exists when NOEFFECTS==0.

### mt_chnnewparam

- **Writes:** (1) Zeroed during init. (2) Set in `mt_fx` from the byte following the FX command.
- **Reads:** `mt_nonewnoteinit` and `mt_newnoteinit` load it for tick-0 effect dispatch.
- **Condition:** Only exists when NOEFFECTS==0.

### mt_chnfx

- **Writes:** (1) Zeroed during init. (2) Set from mt_chnnewfx in `mt_tick0_34` (effects 0-4). (3) Reset to 0 in `mt_newnoteinit`.
- **Reads:** `mt_effects`/`mt_wavedone` loads Y from it for continuous effect jump table. Also read by `mt_effectnum` for portamento direction check.
- **Condition:** Only exists when NOEFFECTS==0 and at least one of porta/vibrato is enabled.

### mt_chnparam

- **Writes:** (1) Zeroed during init. (2) Set from A in `mt_tick0_34` (from effect parameter). (3) Set from instrument vibrato param in `mt_newnoteinit`.
- **Reads:** `mt_wavedone` effect dispatch loads Y from it as speed table index.
- **Condition:** Only exists when at least one of porta/toneporta/vibrato is enabled.

### mt_chnnewnote

- **Writes:** (1) Zeroed during init. (2) Set in `mt_normalnote` (note value + transpose). (3) Cleared to 0 in `mt_newnoteinit` after processing.
- **Reads:** `mt_nonewnoteinit` check: if non-zero, branches to `mt_newnoteinit`.

### mt_chnwaveptr

- **Writes:** (1) Zeroed during init. (2) Set from instrument's waveptr in `mt_newnoteinit`. (3) Updated by wave table stepping (incremented or loaded from jump target). (4) Set by SETWAVEPTR effect. (5) Cleared to 0 by SFX exec.
- **Reads:** `mt_waveexec` loads Y from it (0 = skip wave execution).

### mt_chnwave

- **Writes:** (1) Zeroed during init, then set from instrument first-wave or loaded during `mt_loadregswaveonly`. (2) Set by wave table non-command entries. (3) Set by SETWAVE effect. (4) Set by SFX exec.
- **Reads:** `mt_loadregswaveonly` ANDs with mt_chngate and writes to SID $D404,x.

### mt_chnpulseptr

- **Writes:** (1) Zeroed during init. (2) Set from instrument's pulseptr on new note (if non-zero). (3) Updated by pulse table stepping. (4) Set by SETPULSEPTR effect.
- **Reads:** `mt_pulseexec` loads Y from it (0 = skip pulse execution).

### mt_chnpulsetime

- **Writes:** (1) Zeroed during init. (2) Set from pulse table left column ($01-$7F = modulation duration). (3) Decremented each frame during modulation. (4) Reset to 0 by SETPULSEPTR effect and on new note.
- **Reads:** `mt_pulseexec` checks if non-zero (continue modulation) or zero (fetch new step).

### mt_chnsongnum

- **Writes:** (1) Set during `mt_initchn` from Y (0, 1, 2 for the three channels). Only changes with NUMSONGS > 1.
- **Reads:** `mt_sequencer` loads Y from it to get orderlist base address from song table.

### mt_chnpattnum

- **Writes:** (1) Zeroed during init. (2) Set in sequencer from orderlist byte.
- **Reads:** `mt_getnewnote` loads Y from it to index pattern table.

### mt_chntempo

- **Writes:** (1) Set to DEFAULTTEMPO during `mt_initchn`. (2) Set by SETTEMPO effect (global: all channels; per-channel: just one). (3) Modified by funktempo toggle.
- **Reads:** `mt_notick0` reloads counter from it when counter goes negative. Funktempo reads/writes it to toggle between two values.

### mt_chncounter

- **Writes:** (1) Set to 1 during `mt_initchn`. (2) Reloaded from tempo in `mt_nofunktempo`. (3) Decremented at start of `mt_execchn`.
- **Reads:** (1) `mt_execchn` decrements and checks for zero (tick 0). (2) Gate timer comparison. (3) REALTIMEOPTIMIZATION/PULSEOPTIMIZATION checks.

### mt_chnnote

- **Writes:** (1) Zeroed during init. (2) Set in `mt_newnoteinit` from (newnote - NOTE). (3) Set by tone portamento when target reached.
- **Reads:** (1) Tone portamento uses it as target note for frequency comparison. (2) `mt_effect_3_found` uses it for final frequency set.

### mt_chninstr

- **Writes:** (1) Set to 1 during init. (2) Set in `mt_instr` from pattern data.
- **Reads:** (1) `mt_nonewpatt` loads Y from it to access instrument tables (ADSR, waveptr, etc). (2) Effect dispatch when NOEFFECTS==1 reads it for vibrato param. (3) Hard restart checks compare it against FIRSTNOHRINSTR/FIRSTLEGATOINSTR.

### mt_chngate

- **Writes:** (1) Set to $FE during init. (2) Set to $FF (or $FE/$BF/$BE) in `mt_newnoteinit` and `mt_setgate`. (3) Set to $FE during hard restart. (4) Set to $FE by SFX exec.
- **Reads:** `mt_loadregswaveonly` ANDs it with mt_chnwave before SID write.

### mt_chnvibtime

- **Writes:** (1) Zeroed during init. (2) Reset to 0 on new note (`mt_wavenote`). (3) Cleared to 0 on portamento effects 1/2 (`mt_tick0_12`). (4) Updated by vibrato algorithm in `mt_effect_4` (accumulator with direction flip).
- **Reads:** `mt_effect_4` reads it, checks direction bit, updates it. LSR produces frequency offset.

### mt_chnvibdelay

- **Writes:** (1) Zeroed during init. (2) Loaded from instrument's vibdelay on new note init.
- **Reads:** `mt_effect_0` checks it; if non-zero, decrements and skips vibrato.

### mt_chnwavetime

- **Writes:** (1) Zeroed during init. (2) Incremented during wave delay check. (3) Reset to 0 on wave ptr advance. (4) Reset to 0 by SETWAVEPTR effect.
- **Reads:** `mt_waveexec` compares it against wave table delay value.
- **Condition:** Only when NOWAVEDELAY==0.

### mt_chnfreqlo / mt_chnfreqhi

- **Writes:** (1) Zeroed during init. (2) Set from frequency table on note. (3) Modified by portamento add/subtract. (4) Modified by vibrato add/subtract.
- **Reads:** (1) `mt_loadregs` writes them to SID $D400/D401,x. (2) Tone portamento reads them to compute distance to target.

### mt_chnpulselo / mt_chnpulsehi

- **Writes:** (1) Zeroed during init. (2) Set by pulse table SETPULSE command. (3) Modified by pulse modulation (add/subtract speed). (4) Set by SFX exec.
- **Reads:** (1) `mt_loadregs`/`mt_pulsedone` writes them to SID $D402/D403,x. (2) Pulse modulation reads lo for add/sub.

### mt_chnad / mt_chnsr

- **Writes:** (1) Zeroed during init. (2) Set from instrument's AD/SR on new note init. (3) Set by SETAD/SETSR effects. (4) Set during hard restart (ADPARAM/SRPARAM). (5) Set by SFX exec.
- **Reads:** `mt_loadregs` writes them to SID $D405/D406,x.
- **Condition:** Only when BUFFEREDWRITES!=0 (and ZPGHOSTREGS==0).

### mt_chngatetimer

- **Writes:** (1) Zeroed during init. (2) Loaded from instrument's gatetimer column on tick 0 (`mt_nonewpatt`).
- **Reads:** `mt_gatetimer` compares mt_chncounter against it.
- **Condition:** Only when FIXEDPARAMS==0.

### mt_chnlastnote

- **Writes:** Set in `mt_wavenoteabs` whenever a note frequency is looked up.
- **Reads:** `mt_calculatedspeed` uses it to compute frequency delta between adjacent notes for note-relative speed scaling.
- **Condition:** Only when NOCALCULATEDSPEED==0.

### mt_chnsfx / mt_chnsfxlo / mt_chnsfxhi

- **Writes:** (1) Zeroed during init. (2) mt_chnsfx set to 1 in `mt_playsfxok`, incremented each SFX frame, cleared to 0 on SFX end. (3) lo/hi set from `mt_playsfx` arguments.
- **Reads:** (1) `mt_loadregs` checks mt_chnsfx (non-zero = redirect to SFX exec). (2) `mt_playsfx` checks for priority. (3) SFX exec uses lo/hi as data pointer.
- **Condition:** Only when SOUNDSUPPORT!=0.

---

## Channel State Machine

A channel progresses through these states each frame:

```
mt_execchn entry
    |
    v
Decrement mt_chncounter
    |
    +-- counter != 0 (ticks 1-N) --> mt_notick0
    |       |
    |       +-- counter < 0 --> reload from mt_chntempo (funktempo toggle if enabled)
    |       |                    store to mt_chncounter
    |       |
    |       v
    |   mt_effects --> mt_waveexec (wave table stepping)
    |       |
    |       +-- wave table produces note? --> set frequency
    |       |
    |       +-- no note from wave table --> continuous effect execution
    |       |       (instrvib / porta up / porta down / toneporta / vibrato)
    |       |       modifies mt_chnfreqlo/hi
    |       |
    |       v
    |   mt_done --> gate timer check
    |       |
    |       +-- counter == gatetimer --> mt_getnewnote (fetch pattern data)
    |       |
    |       +-- counter != gatetimer --> pulse execution --> mt_loadregs
    |
    +-- counter == 0 (tick 0) --> mt_tick0
            |
            +-- setup tick-0 FX jump from mt_chnnewfx
            |
            v
        mt_checknewpatt
            |
            +-- mt_chnpattptr == 0 --> mt_sequencer
            |       |
            |       +-- read orderlist: handle LOOPSONG, TRANS, REPEAT
            |       +-- store pattern number, advance song pointer
            |
            +-- mt_chnpattptr != 0 --> mt_nonewpatt (continue current pattern)
            |
            v
        Load instrument params (gatetimer, first-wave if applicable)
            |
            +-- mt_chnnewnote != 0 --> mt_newnoteinit
            |       |
            |       +-- set mt_chnnote
            |       +-- reset effect, vibrato delay
            |       +-- check toneporta (skip gate/HR if active)
            |       +-- set first-wave, gate
            |       +-- load pulse/filter/wave pointers from instrument
            |       +-- load AD/SR
            |       +-- execute tick-0 effect
            |       +-- jump to mt_loadregs
            |
            +-- mt_chnnewnote == 0 --> mt_nonewnoteinit
            |       |
            |       +-- execute tick-0 effect only
            |       |
            |       v
            |   mt_waveexec --> (same as ticks 1-N wave/effect chain)
            |
            v
        mt_getnewnote (fetch next note/FX from pattern)
            |
            +-- read pattern byte:
            |     $00-$3F: instrument change (followed by FX or note)
            |     $40-$4F: FX + note follows
            |     $50-$5F: FX only (no note)
            |     $60-$BC: note
            |     $BD: rest
            |     $BE: key off
            |     $BF: key on
            |     $C0-$FF: packed rest
            |
            +-- instrument change: store to mt_chninstr, read next byte
            +-- FX: store effect + param to mt_chnnewfx/mt_chnnewparam
            +-- note: add transpose, store to mt_chnnewnote, trigger hard restart
            +-- rest: just advance pattern pointer
            +-- key off/on: set mt_chngate
            +-- packed rest: set/decrement mt_chnpackedrest counter
            |
            v
        mt_rest --> advance mt_chnpattptr (or set to 0 on ENDPATT)
            |
            v
        mt_loadregs --> write freq, pulse, wave*gate, AD/SR to SID
            |
            +-- if SOUNDSUPPORT and mt_chnsfx != 0 --> mt_sfxexec (overrides normal output)
```

### Hard Restart Sequence

When a new note arrives (not toneporta, not legato, not no-HR instrument):

1. **Gate-off tick** (counter == gatetimer): Note is fetched from pattern, `mt_chnnewnote` set, `mt_chngate` set to $FE (gate off). For HR instruments, AD/SR set to ADPARAM/SRPARAM (typically $0000 for fast release).
2. **Ticks between gate-off and tick 0**: Wave table and effects continue executing with gate off. SID outputs silence (release phase with HR params).
3. **Tick 0 (new note init)**: Full instrument reload: waveptr, pulseptr, filtptr, AD/SR from instrument tables. Gate set to $FF. First waveform written. Frequency set from note.

### Filter Execution

Filter runs once per frame BEFORE channel execution (global, not per-channel):

```
mt_filtstep (mt_filtstep+1 = current filter table index)
    |
    +-- index == 0 --> filter stopped, just output current values
    |
    +-- read mt_filttimetbl[index]:
    |     $80+ --> set filter params (passband, resonance/routing)
    |     $01-$7F --> modulation duration (add speed to cutoff each frame)
    |     $00 --> set cutoff from mt_filtspdtbl
    |
    +-- check for jump ($FF) or advance index
    |
    v
    Output: cutoff -> $D416, control -> $D417, type|volume -> $D418
```

---

## Compile-Time Constants

These are not variables but fixed values injected by greloc.c:

| Name | Meaning |
|------|---------|
| `base` | Player load address |
| `zpbase` | Zero-page base address |
| `SIDBASE` | SID chip base ($D400 normally) |
| `NUMCHANNELS` | 1, 2, or 3 |
| `NUMSONGS` | Number of songs |
| `FIRSTNOTE` | Lowest note number in frequency table |
| `FIRSTNOHRINSTR` | First instrument index that skips hard restart |
| `FIRSTLEGATOINSTR` | First instrument index that is legato |
| `NUMHRINSTR` | Count of hard-restart instruments |
| `NUMNOHRINSTR` | Count of no-HR instruments |
| `NUMLEGATOINSTR` | Count of legato instruments |
| `ADPARAM` | Hard restart Attack/Decay value |
| `SRPARAM` | Hard restart Sustain/Release value |
| `DEFAULTTEMPO` | Default tempo loaded during init |
| `FIRSTWAVEPARAM` | First-wave value when FIXEDPARAMS==1 |
| `GATETIMERPARAM` | Gate timer value when FIXEDPARAMS==1 |
