---
source_url: https://github.com/Chordian/sidfactory2 (dist/documentation/ + blog.chordian.net/sf2/)
fetched_via: direct
fetch_date: 2026-06-13
author: Laxity / JCH
content_date: 2026-03-14 (latest build)
reliability: primary
---

# SID Factory II — Driver Version Differences

## Driver 11 — "The Standard" (Laxity)

Primary driver for SF2. Progressive feature additions across sub-versions.

| Version | Changes |
|---------|---------|
| 11.00 | Original default driver |
| 11.01 | Added fret slide command (T4 XX YY) |
| 11.02 | Added pulse table index (Tc), tempo table index (Td), main volume (Te) commands |
| 11.03 | Added filter channel enable flag (bit 5 = 0x20 in instrument byte 2) |
| 11.04 | Added note event delay (T = 0..F ticks before note fires) |
| 11.04_01 | Minor variant of 11.04 |
| 11.05 | Fret slide removed; HR table reduced from 16 to 8 rows; "skip pulse reset" flag (0x08) added |

**Feature matrix:**
- Fret slide: 11.01, 11.02, 11.03, 11.04 ONLY (not 11.00 or 11.05)
- Pulse/Tempo/Volume commands: 11.02+ only
- Filter channel enable: 11.03+ only
- Note delay: 11.04 ONLY (removed in 11.05)
- Skip pulse reset: 11.05 only
- HR table size: 16 rows in 11.00-11.04; 8 rows in 11.05

**Command set by version:**
```
11.00: T0 T1 T2 T3 T8 T9 Ta Tb Tf
11.01: + T4 (fret)
11.02: + Tc Td Te
11.03: (same commands as 11.02, only instrument flag change)
11.04: + T4 note delay encoding (parallel, different slot)
11.05: - T4, + skip-pulse-reset flag (not a new command)
```

The C++ sf2_interface.cpp ParseDriverDetails() currently only implements driver 11 (major=11)
and maps all minor versions to the same 11.02 command set (without fret or note delay).

---

## Driver 12 — "The Barber" (Laxity)

Minimal driver. Only 1 version (12.00).

**Differences from driver 11:**
- Only 4-byte instruments (AD, SR, Waveform, PW)
- No wave/pulse/filter/arpeggio TABLES — effects are per-instrument
- Commands are nibble-encoded (0X XX style), not byte-indexed into a command table
- No hard restart configuration
- No filter support
- No oscillator reset

**Commands:** 3 only: slide up (0X XX), slide down (1X XX), vibrato (2X -Y)

---

## Driver 13 — "The Hubbard Experience" (Laxity)

Rob Hubbard emulation driver. Only 1 version (13.00).

**Differences from driver 11:**
- 7-byte instruments (AD, SR, Waveform, PW, PW-sweep, Flags, Arp-props)
- Built-in pulsating PW effect per instrument (no separate pulse table)
- Built-in arpeggio per instrument (alternate arpeggio flag)
- Dive effect (per-instrument flag)
- Noise at note start (per-instrument flag)
- Same simple 3-command set as driver 12

**Key design difference:** Effects are baked into the instrument rather than programmed via
separate tables. This reflects Hubbard's original design where each instrument carries its
own effect parameters.

---

## Driver 14 — "The Experiment" (Laxity)

Experimental hard restart timing. Only 1 version (14.00).

**Differences from driver 11:**
- Same 6-byte instrument format as driver 11 (AD/SR/Flags/Filter/Pulse/Wave)
- Different hard restart mechanism: "immediate response" type (bit 7 = 0x80)
  vs. driver 11's standard hard restart
- Same table set as driver 11 (wave, pulse, filter)
- Only 2 commands: slide and vibrato (vs 12+ in driver 11)
- Allows shorter gate-off durations than driver 11 (at cost of instability)

**Use case:** Punchy, tight bass lines where gate timing is critical.

---

## Driver 15 — "Tiny, mark I" (Laxity)

Zero-page variable driver. 3 versions: 15.00, 15.01, 15.02.

**Differences from driver 12:**
- Same waveform + pulse approach as driver 12 (no separate tables initially)
- All driver variables in zero-page ($00-$FF) instead of regular RAM
- Optimized for small code size
- Hard restart always on (not configurable)
- Linear pulse sweep per instrument (byte 3)
- Wave table support (byte 4 = wave table index)

**15.00 vs 15.02 differences:**
- 15.02: ADSR hard restart also clears AD (sets to $0F00 instead of just SR=$00)
- 15.02: Programs (wave table) now run during "next note" phase
- 15.02: Added command 3X YY for setting wave program pointer
- 15.02: Added stop marker support in order list

---

## Driver 16 — "Tiny, mark II" (Laxity)

Variation of driver 15. 3 versions: 16.00, 16.01, 16.01_01.

**Differences from driver 15:**
- NO COMMANDS at all (not even slide/vibrato/wave)
- Otherwise same instrument format (5 bytes)
- Smallest possible driver code footprint
- Hard restart always on

---

## Driver NP20 — JCH's NewPlayer 2.0 (JCH)

JCH's own player engine, completely different architecture from Laxity's drivers.

**Key differences:**
- Loaded at $0F00 (fixed address, not relocatable)
- Version identifier "20.G" at $0FEE
- Row-major table layout (instrument/command tables)
- Wave table columns SWAPPED relative to SF2 convention
- Order lists stored as flat (transpose, index) pairs, NOT packed like SF2
- Sequences stored as flat (cmd_or_inst, note) pairs (only 2 bytes per event)
- No concept of duration byte — each row = 1 tick
- Command byte >= 0xC0: is a command; < 0xC0: is an instrument index
- Filter table doubles as tempo data storage (filter bytes 0 and 1 used for tempo)
- No end-of-sequence marker in orderlist except 0xFF for end

The NP20 format is unique enough that a dedicated `converter_jch.cpp` handles it,
and it only imports to `sf2driver_np20_00.prg` (NOT a standard driver 11 file).

---

## Summary: Which drivers share the most features

| Feature | d11 | d12 | d13 | d14 | d15 | d16 | NP20 |
|---------|-----|-----|-----|-----|-----|-----|------|
| Wave table | YES | no | no | YES | YES | YES | YES |
| Pulse table | YES | no | no | YES | no | no | YES |
| Filter table | YES | no | no | YES | no | no | YES |
| Arp table | YES | no | no | no | no | no | ? |
| HR table | YES | no | no | no | no | no | ? |
| Tempo table | YES(02+) | no | no | no | no | no | ? |
| Column-major inst | YES | YES | YES | YES | YES | YES | no |
| Hard restart cfg | YES | no | no | YES | always | always | ? |
| Filter support | YES | no | no | YES | no | no | YES |
| Portamento | YES | no | no | no | no | no | ? |
| Arpeggio cmd | YES | no | no | no | no | no | ? |
| Multi-song | YES | YES | YES | YES | YES | YES | ? |

---

## Build history (from blog.chordian.net/sf2/)

| Build | Key additions |
|-------|--------------|
| 20200604 | First major public release |
| 20200911 | Driver 11.02 (pulse, tempo, main volume commands) |
| 20210104 | Driver 11.03 (filter channel enable) |
| 20211230 | Driver 11.04 (note event delay) |
| 20231002 | Driver 11.05 (fret removed, HR size 16→8, skip pulse reset) |
| 20260314 | MIDI output via ASID protocol |
