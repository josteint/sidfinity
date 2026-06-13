# SID-Wizard by Hermit

> **⚠ 2026-06-13 — see [`README.md`](README.md) + `spec_extraction_plan.md` / `spec_write_model.md` for the source-grounded specs** (from the open-source `player.asm`/`exporter.asm` + the 1.4 manual + decoded HVSC binaries). Refinements to this overview: timing is **mostly vblank** in HVSC (PSID speed=0 for 992/1048; only 56 CIA — NOT the "CIA-based" default), so the in-scope target uses the **flat Mode-1** verdict; exported data sits **behind self-modified pointer tables** (not a tight concatenation — the per-(version,drivertype) offset map is the key OPEN); init clears $D400-$D417 + sets $D418=$0F (the **$D418 was dropped from the init clear in V1.5**); the lean 1-SID build writes `$D4xx` incrementally (`SIDG=SID`) with a **driver-variant-dependent** note-start order, while ghost/multi-SID builds use the fixed COMMONREGS loop. **Scope: 1010 1SID tunes (v2); exclude the 38 multi-SID (v3/v4, `_2SID`/`_3SID`) — they write $D420+/$D440+.**

## Overview

- **HVSC count:** 1,074 tunes
- **Author:** Mihaly Horvath (Hermit)
- **Year:** 2012-2022 (V1.0 RC through V1.92)
- **License:** WTF (open source)
- **Source:** https://sourceforge.net/p/sid-wizard/code/HEAD/tree/ and https://github.com/anarkiwi/sid-wizard
- **Key source files:** `sources/include/player.asm`, `sources/exporter.asm`, `sources/SWM-spec.src`
- **Supports:** 1SID, 2SID (stereo), 3SID, 4SID

## SWM File Format (Native)

### Header (64 bytes)

| Offset | Field | Description |
|--------|-------|-------------|
| 0x00-0x03 | ID | `"SWM1"` (mono) or `"SWMS"` (stereo) |
| 0x04 | Frame speed | 1-8 |
| 0x0B | Default pattern length | |
| 0x0C | Sequence amount | |
| 0x0D | Pattern amount | |
| 0x0E | Instrument count | |
| 0x0F | Chord table length | |
| 0x10 | Tempo table length | |
| 0x13 | Driver type | bare/light/medium/extra |
| 0x14 | Tuning | 0=440Hz, 1=432Hz Verdi, 2=Just intonation |
| 0x18-0x3F | Author | 40 bytes ASCII |

Data follows: sequences, patterns, instruments, chord table, tempo table, subtune tempos.

### Limits

- Max subtunes: 31, patterns: 100, instruments: 37
- Max sequence length: 126 bytes, pattern length: 249 bytes
- Max instrument size: 128 bytes, chords: 64, tempo programs: 64

## Instrument Structure (16-byte base + variable tables)

| Offset | Field | Description |
|--------|-------|-------------|
| 0 | Control | HR timer(0-1), gate-off HR(2), test-bit HR(3), vibrato type(4-5), PW reset OFF(6), filter reset OFF(7) |
| 1-2 | HR-ADSR | Hard-restart ADSR |
| 3 | AD | Attack/Decay |
| 4 | SR | Sustain/Release |
| 5 | Vibrato | Hi nib: amplitude, lo nib: frequency |
| 6 | Vibrato delay | Or amplitude-increment speed |
| 7 | Arp/chord speed | Bit 6: multispeed PW, bit 7: multispeed filter |
| 8 | Default chord | |
| 9 | Octave shift | 2's complement transpose |
| 0A | PW table ptr | |
| 0B | Filter table ptr | |
| 0C | Gate-off WF ptr | |
| 0D | Gate-off PW ptr | |
| 0E | Gate-off filter ptr | |
| 0F | First frame waveform | |
| 10+ | WF-ARP table | $FF terminated |
| var | PW table | $FF terminated |
| var | Filter table | $FF terminated |

## Pattern Format

Each row has up to 4 columns: Note/FX, Instrument/SmallFX, BigFX, FX value.

- $00-$5F: notes
- $60: vibrato FX
- $70-$77: packed NOPs (2-9 empty rows)
- $78: portamento, $79/$7A: sync on/off, $7B/$7C: ring on/off, $7D/$7E: gate on/off
- Instrument: $01-$3E, $3F=legato
- Pattern ends with $FF

## Sequence Format

- $01-$7F: pattern numbers
- $80-$8F/$90-$9F: transpose down/up ($90=none)
- $A0-$AF: volume
- $B0-$EF: track tempo
- $FE: end, $FF: jump

## Player Architecture

- Ghost/shadow registers buffered in RAM before SID writes
- Zero-page: bunches of 7 bytes per channel
- Multispeed support (MULPLY processes tables between main frames)
- SID write order: SR, AD, Freq, PW, Waveform
- Player variants: bare, light, medium, normal, extra (feature/size tradeoff)

## SID Export

PSID v2 header. Player at PLAYERADDR (typically $1000). Init = base (subtune in A). CIA-based timing for multispeed.
