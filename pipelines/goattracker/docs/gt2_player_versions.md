# GoatTracker V2 Player Version Differences

**Date:** 2026-04-02

## Overview

GoatTracker V2 shipped 11 player.s versions (2.65-2.77), but only 3 transitions contain actual code changes. This means there are **4 behavioral groups** that produce different audio output from identical song data.

The player isn't just a renderer — it's part of the composition. Two songs with identical .sng data but different player versions sound audibly different because the player encodes musical choices: wave table stepping, ADSR write order, new-note register behavior, vibrato implementation.

## Identical Versions

These version pairs have byte-identical player.s files:

- 2.65 = 2.67
- 2.68 = 2.69 = 2.70 = 2.71 = 2.72
- 2.73 = 2.74
- 2.76 = 2.77

## The 4 Behavior Groups

| Group | Versions | Shorthand |
|-------|----------|-----------|
| **A** | 2.65-2.67 | "classic" |
| **B** | 2.68-2.72 | "sr-first" |
| **C** | 2.73-2.74 | "ghostregs" |
| **D** | 2.76-2.77 | "vibfix" |

## Transition 1: v2.67 → v2.68 (Group A → B)

The largest change. Five audio-affecting modifications:

### 1a. ADSR write order reversed everywhere

**Before (A):** AD ($D405) written first, then SR ($D406).
**After (B+):** SR ($D406) written first, then AD ($D405).

Applies to: hard restart, new-note init, buffered loadregs, sound FX hard restart.

**Why it matters:** The SID latches AD on gate transitions. Writing AD last (just before the gate bit changes) ensures the SID picks up the correct attack/decay values. The v2.65 order (AD then SR) meant the SID could briefly see stale AD values during gate-on.

Detection: In the player binary, find `STA $D405,X` / `STA $D406,X` near the hard restart code. If AD ($D405) comes first → Group A. If SR ($D406) comes first → Group B+.

### 1b. New-note frame: wave-only instead of all registers

**Before (A):** New-note init ends with `jmp mt_loadregs` → writes freq, pulse, wave, AD, SR to SID.
**After (B+):** New-note init ends with `jmp mt_loadregswaveonly` → writes ONLY waveform ($D404) to SID.

**Why it matters:** In Group A, the frequency register is re-written on the new-note frame even though it was just set. In Group B+, only the waveform changes on that frame — the frequency appears on the next frame's loadregs. This creates a 1-frame difference in when the frequency becomes audible after a new note.

Detection: Find the JMP instruction at the end of new-note init (after wave_ptr load). If target is `mt_loadregs` (writes freq+wave) → Group A. If target is `mt_loadregswaveonly` (writes wave only) → Group B+.

### 1c. New-note init ordering

**Before (A):** AD → SR → pulse_ptr → filter_ptr → first_wave → wave_ptr → effects → loadregs.
**After (B+):** first_wave → pulse_ptr → filter_ptr → wave_ptr → SR → AD → effects → loadregswaveonly.

**Why it matters:** The wave register value is available to tick-0 effect processing in B+ but not in A. Effects that check waveform state behave differently.

### 1d. Global tempo write bounds check

**Before (A):** Global tempo write always targets all 3 channel slots unconditionally.
**After (B+):** Wrapped in `NUMCHANNELS > 1` / `> 2` guards.

Only matters for 1-channel or 2-channel songs (rare). In A, this could corrupt memory.

## Transition 2: v2.72 → v2.73 (Group B → C)

### 2a. Ghost register mode (GHOSTREGS flag)

New feature: when `GHOSTREGS != 0` and `ZPGHOSTREGS == 0`, a "full ghost" mode activates. At the start of each `mt_play`:

```asm
ldx #24
mt_copyregs:
    lda ghostregs,x
    sta SIDBASE,x
    dex
    bpl mt_copyregs
```

All 25 SID registers are written in a single burst from a shadow buffer. Individual channel processing writes to the buffer, not SID.

**Why it matters:** Introduces exactly 1 frame of latency for all register changes. All three channels update simultaneously at frame start. Eliminates timing artifacts from sequential channel processing.

Most HVSC files don't use this (GHOSTREGS=0), so this only matters for files explicitly compiled with ghost registers.

### 2b. Buffered-writes ADSR order partial revert

In the `GHOSTREGS==0` buffered-writes loadregs path, the AD/SR write order was reverted to AD-first (matching Group A). But the hard restart path kept SR-first (Group B behavior).

This inconsistency only applies to the specific `BUFFEREDWRITES != 0, GHOSTREGS == 0` configuration.

## Transition 3: v2.74 → v2.76 (Group C → D)

### 3a. Vibrato parameter zeroing fix

When instrument vibrato is disabled (`NOINSTRVIB != 0`) but regular vibrato is enabled (`NOVIB == 0`), effect 0 (instrument vibrato) jumps to `mt_tick0_34` which stores A into the vibrato parameter.

**Before (C):** A register contains stale value → garbage vibrato parameter.
**After (D):** `lda #$00` added → vibrato parameter explicitly zeroed.

**Why it matters:** Bug fix. In Group C, instruments without vibrato could accidentally get vibrato from a stale accumulator value. Only triggers when both `NOINSTRVIB == 1` and `NOVIB == 0` — i.e., songs that use pattern-command vibrato but not instrument vibrato.

## USF Representation

USF should capture the player behavior group as a song-level field:

```
gt2_player_group: A | B | C | D
```

Or, for more granular control, individual behavioral parameters:

| USF Field | Values | Default |
|-----------|--------|---------|
| `adsr_write_order` | `ad_first` / `sr_first` | `sr_first` (B+) |
| `newnote_reg_writes` | `all_regs` / `wave_only` | `wave_only` (B+) |
| `newnote_init_order` | `adsr_first` / `wave_first` | `wave_first` (B+) |
| `ghost_regs` | `none` / `zp` / `full` | `none` |
| `vibrato_param_fix` | `true` / `false` | `true` (D) |

## Detection from Binary

To identify which group a packed SID belongs to, examine the player code:

1. **Find hard restart code**: `LDA #ADPARAM` near `STA $D405,X` / `STA $D406,X`.
2. **Check ADSR order**: If `STA $D405,X` appears before `STA $D406,X` → Group A. Otherwise → B/C/D.
3. **Find new-note JMP target**: After wave_ptr load, the JMP target determines: `loadregs` (Group A) vs `loadregswaveonly` (Group B+).
4. **Check for ghost reg copy loop**: `LDX #24 / LDA ghostregs,X / STA SIDBASE,X` → GHOSTREGS active (Group C+ with ghost flag).
5. **Check vibrato fix**: In effect 0 handler, look for `LDA #$00` before `JMP mt_tick0_34` → Group D.

## File Distribution in HVSC

Estimated from SIDId signatures and GT2 version release dates:
- Group A (2.65-2.67): Early GT2 files, ~2003-2005
- Group B (2.68-2.72): Most common, ~2005-2008
- Group C (2.73-2.74): ~2008-2012
- Group D (2.76-2.77): Latest files, ~2012-2017+

The majority of HVSC GT2 files are likely Group B or C.
