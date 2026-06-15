---
source_url: binary analysis of RFXT_PLAYER_V1.1.prg + Trance_202.sid + Gubber.sid
fetched_via: direct (files already in tmp/reflextracker_research/)
fetch_date: 2026-06-15
author: RE analysis by this session
content_date: 2026-06-15
reliability: primary (binary evidence)
---

# Reflextracker C64 Player Architecture

## Overview

Reflextracker V1.1 (1995, Reflex + The Obsessed Maniacs) is a **2-channel digital sample
tracker**. It plays 8-bit PCM audio samples through the SID chip's digi technique, NOT a
melodic SID tracker. There are NO SID register writes for voice frequency/gate/envelope in
the normal melodic sense — the audio is produced via $D418 volume (fast PWM digi).

Authors: kb (Tammo Hinrichs), Quiss (Matthias Kramm), Zorc. Music/docs: PVCF.

## Two Player Variants

### Variant A: Standalone RFXT_PLAYER_V1.1.prg
- **Load address**: `$C000`
- **Size**: 2032 bytes (`$C000`–`$C7EF`)
- **Purpose**: Used by the tracker UI running in BASIC at `$0801`
- **SID writes**: Only `$D418` (volume, for digi playback)
- **Note table**: `LDY $1000,X` (module provides data at `$1000`+)
- **Freq table**: `LDX $EE00,Y` (freq lookup at `$EE00`)
- **Identification string embedded**: `RFXT PLAYER V1.1` (ASCII in player binary)

### Variant B: SID-embedded player (in HVSC .sid files)
- **Source location**: `$1F00` in module data
- **Runtime location**: Copied to `$F000` during init (1728 bytes = 6 pages + $C0)
- **Note table**: `LDY $7700,X` (relocated)
- **Freq table**: `LDX $FA00,Y` (relocated)
- **Second init copy**: 1648 bytes from `$B700` → `$E400` (audio sample staging area?)
- **iAN CooG HVSC wrapper** at `$C000`–`$C12D` handles PSID init/play hooks

## Entry Points

### Standalone Player
- `$C000`: JMP → `$C02C` (IRQ/init entry dispatch)
- `$C003`: JMP → `$C016` (play routine entry)
- `$C006`: IRQ handler / CIA-driven play
- `$C02C`: Init: clears SID regs ($D400–$D418), sets CIA, primes voice 1 (PW=$FFFF, ctrl=$41)
- `$C050`: Minimal extra init (SID voice 1 ctrl + CIA CRB = `$41`)
- `$C219`: `JSR $C4E8` — process channel events
- `$C244`: `JSR $C2CC` — channel 2 processing

### SID-embedded player (iAN CooG HVSC wrapper)
- Init address: `$C050` (in HVSC .sid files)
- Play address: `$0000` (RSID, CIA-driven)
- Wrapper `$C000`:
  - CIA1 timer setup: `$DC04`=`$94` (timer lo), `$DC05`=`$00` → ~6657 Hz sample rate
  - ZP init: `$50`=play_state, `$52/$53/$54`=channel vars
  - NMI vector → `$C12D` (RTI stub, blocks NMI)
  - IRQ vector → `$C100` (stub that just acks CIA and returns)
  - JMP `$C047` (→ `$0000`, dummy, init returns)
- Init `$C050`: copies engine from `$1F00`→`$F000`, patches freq tables

## Init Sequence (HVSC SID)

```
C050: SEI
      Save $01, set $01=$38 (all RAM: LORAM=0, HIRAM=0, CHAREN=0)
      Copy table iteration 1 (ZP FF = 1):
        src  = $1F00  (engine code, from $3401/$3403)
        dst  = $F000  (Kernal RAM, mapped in all-RAM mode)
        size = 6 pages + $C0 bytes = 1728 bytes
      Copy table iteration 2 (ZP FF = 0):
        src  = $B700  (audio data / secondary tables, from $3400/$3402)
        dst  = $E400
        size = 6 pages + $70 bytes = 1648 bytes
      Patch F2DE = $11, F2E3 = $18  (SMC: adjust ADC immediates in engine)
      Restore $01
      Enable VIC raster IRQ, disable CIA IRQs
```

The table at `$3400` in Trance_202.sid:
```
B7 1F E4 F0 70 C0 06 06 00 00 ...
^ ^   ^ ^   ^  ^  ^  ^
| |   | |   |  |  |  second copy page count (6)
| |   | |   |  |  first copy page count (6)
| |   | |   |  second copy partial ($C0)
| |   | |   first copy partial ($70)
| |   | dst hi for first copy ($F0 → $F000)
| |   dst hi for second copy ($E4 → $E400)
| src hi for first copy ($1F → $1F00) [at index 1]
src hi for second copy ($B7 → $B700) [at index 0]
```

## Zero-Page State Variables (Standalone Player)

| ZP   | Role |
|------|------|
| `$D0` | Channel 1 data pointer (lo) |
| `$D1` | Channel 1 data pointer (hi) |
| `$D2` | Channel 2 data pointer (lo) |
| `$D3` | Channel 2 data pointer (hi) |
| `$D4` | Channel active/play flag |
| `$D5` | Playback speed counter |
| `$D6` | Sub-speed counter |
| `$D7` | Player state (`$81`=init, `$00`=done) |
| `$D8` | Channel 1 loop/direction flag |
| `$D9` | Channel 2 loop/direction flag |
| `$E7` | End-of-data sentinel |
| `$E8` | Channel active flag ch1 |
| `$F0` | Channel active flag ch2 |
| `$F1` | Channel 1 enabled |

(SID-embedded player uses `$50`=play_state, `$52/$53/$54` for channel vars instead)

## SID Register Writes

Only `STA $D418` observed in standalone player (volume register for digi playback).
Init also writes:
- `$D402/$D403`: Voice 1 PW lo/hi = `$FF/$FF`
- `$D404`: Voice 1 ctrl = `$41` (gate + pulse)
- `$D406`: Voice 2 PW lo = `$FF`

The player uses SID purely as a DAC via `$D418` volume at ~6657 Hz.
No gate, envelope, frequency, or filter registers are written during play.

## Self-Modifying Code (SMC)

The standalone player has ~70+ `STA abs (SMC)` operations. The player patches its own
operand bytes at runtime to:
1. Store the current channel data pointer (split across multiple address operands)
2. Update direction bits for the bounce-back stepping logic
3. Configure the play subroutine JSR target addresses

This is why the sidid signature contains many `??` wildcards — the SMC slots take different
values per module and per player invocation.

## Note-to-Frequency Conversion (in engine)

Subroutine at `$F2CF` (SID-embedded player, after relocation to `$F000`):
```
CMP #$50     ; note < 80?
BCS too_high
LSR A        ; note >> 1
ROR zpx      ; shift into ZP
LSR A        ; >> 2 total
ROR zpx
LSR A        ; >> 3 total (= octave index 0-9)
ROR zpx
TAY
ADC #$D0     ; ← SMC: imm patched to $11 during init (base for freq lo calc)
STA $E2,X   ; store freq component lo
TYA
ADC #$DA     ; ← SMC: imm patched to $18 during init (base for freq hi calc)  
STA $E4,X   ; store freq component hi
TYA
ADC #$E4     ; octave shift
...          ; further note-to-period calculation
```

The ADC immediates at `$F2DE` and `$F2E3` get patched during init to `$11` and `$18`
respectively, adjusting the CIA timer period base for the specific module's sample rate
requirements.

## QuadSID / Multi-SID Support

From the Lemon64 forum thread (Reflextracker Stuff): PVCF confirms Reflextracker
compositions were created using "quadrasid" (four SID chips). The PC-side tracker supported
up to 10 channels; tunes in this multi-SID form "can only be recorded as a midi stream"
and cannot be trivially converted to standard C64 .sid format. The example tune "bladesweet"
involved "crazy conversion of 10 channels to 3 channels" for a standard C64 release.

The HVSC Reflextracker tunes (Gubber, Trance_202, Access_Denied_remix) are 1-SID versions.
Multi-SID Reflextracker tunes would require multiple $D400 base addresses (2-SID: add
`$D420`, 4-SID: add `$D440`, `$D460`, etc.) but no known HVSC-format multi-SID Reflextracker
files have been found.

## Module Load Addresses

| File | Load addr | Notes |
|------|-----------|-------|
| Gubber.sid (RSID) | `$1700` | engine at `$C000` within SID |
| Trance_202.sid (RSID) | `$1000` | engine copy at `$1F00`→`$F000` |
| Access_Denied_remix.sid (RSID) | `$4A1C` | different module layout |
| MOD.TRANCE202.prg (module file) | `$1009` | standalone module format |
| MOD.ENDLOSCHOOR.prg | `$95FC` | different base (quad-SID era?) |
| RFXT_PLAYER_V1.1.prg | `$C000` | standalone player only |
| REFLEXTRACK.V1.1.prg | `$0801` | tracker UI (BASIC area) |
