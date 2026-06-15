---
source_url: https://blog.chordian.net/2022/08/27/composing-in-sid-factory-ii-part-4-instruments/
fetched_via: direct
fetch_date: 2026-06-15
author: Jens-Christian Huus (JCH / Chordian) — tutorial series
content_date: 2022-08-27
reliability: primary
---

# SID Factory II — Instrument Format (Part 4 Tutorial)

## Context

This is the MODERN (SF2) instrument format, NOT the Vibrants/Laxity or NP21 format.
It is included because SID Factory II is the conceptual descendant of the Laxity
editor and the JCH NewPlayer, and comparing its format to the Vibrants/Laxity
SIDId signatures reveals what evolved and what remained.

## Instrument Byte Layout (SID Factory II, Driver 11)

6 bytes per instrument:

| Byte | Field | Description |
|------|-------|-------------|
| 0 | Attack/Decay | High nibble = attack (0-F), low nibble = decay (0-F) |
| 1 | Sustain/Release | High nibble = sustain (0-F), low nibble = release (0-F) |
| 2 | Control byte | Bit 7 ($80) = hard restart enable; bit 3 ($08) = test bit/oscillator reset; bits 3-6 = HR table pointer; combined $90 = HR + test bit |
| 3 | Hard Restart ADSR | Values applied 2 ticks before next note (typically $0F for AD = fastest release, $00 for SR) |
| 4 | Pulse Table pointer | Points into the pulse width table |
| 5 | Wave Table index | Starting row in the wave table |

**Comparison to NP21 (6 bytes per instrument, column-major):**
The NP21 instrument layout per `player_v4.acme` defines 7 fields:
- INS_AD = byte at INSNO×0 + inst_num (stride=48)
- INS_SR = byte at INSNO×1 + inst_num
- INS_HR = byte at INSNO×2 + inst_num (hard restart type + wave delay low nibble)
- INS_7  = byte at INSNO×3 + inst_num (HR sustain/release)
- INS_PULSP = byte at INSNO×4 + inst_num (pulse program pointer, or direct PW if ≥$80)
- INS_WAVEP = byte at INSNO×5 + inst_num (wave program start)
- (byte at INSNO×6 + inst_num — usage depends on player variant)

## Wave Table Format (SID Factory II)

One row per tick, two-byte rows:

| Column | Value range | Meaning |
|--------|-------------|---------|
| Col 1 (waveform) | $11, $21, $41, $81 | Triangle/Saw/Pulse/Noise waveform values |
| Col 1 special | $7F | Loop indicator |
| Col 2 (note offset) | $00-$7F | Semitone offset from playing note (relative mode) |
| Col 2 special | $80-$DF | Static frequency (absolute mode, bit7=1 forces direct freq lookup) |

Waveform codes:
- `$11` = Triangle
- `$21` = Sawtooth
- `$41` = Pulse
- `$81` = Noise
- `$31`, `$51`, `$61`, `$71` = combinations

When `$7F` encountered: loop, adjacent byte = target row.

**Comparison to NP21 wave table** (from `cluster_np21_effect_routines.md`):
NP21 uses two parallel byte arrays `arp1[]` (col A = transpose/loop) and `arp2[]` (col B = waveform/delay).
The relative/absolute mode split is the same conceptually — in NP21, arp1[] values $00-$5F = relative
transpose, $80-$DF = absolute pitch. The SF2 wave table appears to be a row-oriented unification of
NP21's two separate parallel arrays into a single 2-column table, which is the primary structural
difference.

## Hard Restart in SF2

> "Hard Restart: Gates off and applies a different set of ADSR two ticks before the next note
> triggers to prevent ADSR stumbling in rapid sequences."

> "Test Bit: Set the test bit by adding $10 to the third byte to unlock noise waveforms."

The hard restart is the same conceptual feature as NP21's `$8x`/`$Ax` INS_HR modes.
SF2's bit7=$80 (enable HR) + bit3=$10 (test bit) vs NP21's hi-nibble ($8x/$Ax) encoding:
different encoding, same concept. The "2 ticks" timing in SF2 matches NP21's `tsync` 3-frame
sequence (frame 1 = HR gate-off, frame 2 = intermediate, frame 3 = gate-on).

## Static Frequencies

> "Values $80-$DF in the wave table offset byte create a wave table line always stuck at the
> same note, no matter what happens in the sequence."

This is the absolute pitch mode, directly equivalent to NP21 arp1[] $80-$DF values.

---

## Relationship to Vibrants/Laxity format

The SF2 driver is structurally simplified vs both the Laxity editor and NP21:
- Row-oriented instrument table (vs NP21's column-major stride layout)
- Unified 2-column wave table (vs NP21's parallel arp1[]/arp2[] arrays)
- SF2 has `converter_jch.cpp` to import old JCH NP20.gX files — NOT a NP21 converter;
  NP21 tunes need the old NP21 player binary to play

The Vibrants/Laxity format (1987-1990) predates all of these and uses a different
freq model, sequence encoding, and almost certainly a different instrument layout
(the SIDId signatures do not reveal the instrument table structure directly — that
requires disassembly).
