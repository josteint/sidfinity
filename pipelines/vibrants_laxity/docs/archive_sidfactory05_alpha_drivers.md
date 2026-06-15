---
source_url: http://csdb.dk/getinternalfile.php/29773/20060901_SID_Factory_0_5.zip
fetched_via: curl
fetch_date: 2026-06-15
author: Thomas Egeskov Petersen (Laxity) of Maniacs of Noise / Vibrants
content_date: 2006-09-01 (SID Factory 0.5 alpha 1 release)
reliability: primary
---

# SID Factory 0.5 (Alpha 1) — Driver 5 and Driver 6 Format Documentation

Downloaded from CSDb release #39519 (https://csdb.dk/release/?id=39519).
Archive saved to: /home/jtr/sidfinity/tmp/vibrants_laxity_research/SID_Factory_0_5.zip

SID Factory 0.5 (alpha) is Laxity's 2006 C64-native editor — the direct predecessor to SID Factory II
(cross-platform, 2020+). It ships with two music drivers: Driver 5 and Driver 6. These are the
earliest documented driver formats in the Laxity lineage that preceded the JCH NewPlayer V21 (2006).

---

## SID Factory Driver 5.00d

Source: `20060901_SID_Factory_0_5/Docs/SidFactory_Driver v5.00d_Documentation.txt`

"Driver 5 is a standard music driver with calculated vibrato and no aim at execution speed."

### Instrument (8 bytes: aa bb cc dd ee ff gg hh)

| Byte | Purpose |
|------|---------|
| aa | Attack/Decay |
| bb | Sustain/Release |
| cc | Instrument properties 1 — bit7: Hard restart enabled; bit6: N/A; bit5: Arpeggio instrument; bit4: Reset oscillators; bits 0-3: Hard restart table pointer |
| dd | Instrument properties 2 — bit7: Filter is only reset on instrument set command; bit6: Pulse is only reset on instrument set command; bits 0-5: Arpeggio delta delay |
| ee | Resonance setting (non-zero = filter enabled for this channel) |
| ff | Filter table pointer |
| gg | Pulse table pointer |
| hh | Wave table pointer |

### Wave table (2 bytes: aa bb)

- `aa` = Note offset; if bit 7 set, note is fixed (absolute)
- `bb` = Waveform
- `aa = $7x`: special commands:
  - `$7f bb` = Jump to position `bb`
  - `$7e bb` = Set wave table delay to `bb`
  - `$7d bb` = Wait `bb` ticks (not implemented in 0.5)

### Arpeggio table (1 byte: aa)

- `aa` = Note offset to add
- `aa = $7x`: "repeat X steps from the top of the current arpeggio" command

### Pulse table (3 bytes: aa bb cc)

- `aa < $10`: Add to pulse — `aa` = add pulse high, `bb` = add pulse low, `cc` = execution time (frames)
- `aa = $7f`: Jump to index — `cc` = new index
- `aa >= $80 & aa < $90`: Set pulse — `aa=$8x` where x = new high pulse value, `bb` = new low pulse value, `cc` = wait time (frames)

### Filter table (3 bytes: aa bb cc)

- `aa < $10`: Add to filter — `aa` = add filter LOW value (REVERSED from pulse: this is the high part of filter freq), `bb` = add filter HIGH, `cc` = execution time (frames)
- `aa = $7f`: Jump to index — `cc` = new index
- `aa >= $80 & aa < $90`: Set filter — `bb` = new high filter value, `cc` = wait time (frames)

NOTE: Filter low/high ordering is OPPOSITE of pulse table (documented as a quirk).

### Commands (sequence commands)

| Opcode | Description |
|--------|-------------|
| `0x aa ?b` | Set slide — `aabb` = 16-bit speed added to current frequency (additive only) |
| `1x aa bb` | Set vibrato — `aa` = frequency, `?b` = amplitude |
| `2x ?? aa` | Set arpeggio pointer — `aa` = arpeggio index |
| `3x aa bb` | Set filter and/or pulse pointer — `x` bits: bit0 = aa is filter ptr, bit1 = bb is pulse ptr |
| `4x aa bb` | Set wave and/or pulse pointer — `x` bits: bit0 = aa is wave ptr, bit1 = bb is pulse ptr |
| `8x AD SR` | ADSR set for scope of current instrument including current note |
| `9x AD SR` | Direct ADSR for current note only, reset to previous ADSR on next note event |
| `f0 xx ??` | Set new tempo — `xx` = pointer into tempo table |

---

## SID Factory Driver 6.02d

Source: `20060901_SID_Factory_0_5/Docs/SidFactory_Driver v6.02d_Documentation.txt`

"Driver 6 is a 'fast' music driver without calculated vibrato and aims at a maximum
execution spike at around $18 scanlines."

### Instrument (6 bytes: aa bb cc dd ee ff)

| Byte | Purpose |
|------|---------|
| aa | Attack/Decay |
| bb | Sustain/Release |
| cc | Instrument properties — bit7: Restart settings; bit6: Filter pointer set enable; bit5: Pulse pointer set DISABLE; bit4: Oscillator reset (changed from $08 in driver 6.02+); bits 3-0: Hard restart release value $00-$0f |
| dd | Filter table pointer (used when bit6 of cc is set) |
| ee | Pulse table pointer (NOT used when bit5 of cc is set) |
| ff | Wave table pointer |

**Key change from Driver 5**: Only 6 bytes (not 8). No separate arpeggio table; no resonance byte.
Oscillator reset bit moved from $08 to $10 in version 6.02.

### Wave table (same format as Driver 5)

- `aa bb` — `aa` = note offset (bit7 = fixed/absolute), `bb` = waveform
- `aa = $7f bb` = jump to index

### Pulse table (2 bytes: aa bb) — REDESIGNED from Driver 5

NOTE: Driver 6 uses **reversed nibbles** for pulse width (see Appendix below).

- `aa < $80`: Execution time + pulse sweep — `aa` = execution time, `bb` = pulse sweep value (reversed nibble)
- `aa >= $80` (Set pulse): `bb` = new pulse value (reversed nibble format → stored as $0yx0)
- `aa = $7f`: Jump to index — `bb` = new index

### Filter table (2 bytes: aa bb) — REDESIGNED from Driver 5

- `aa < $80`: Add to filter — `aa` = time to execute step, `bb` = add to current filter value
- `aa = $80` (Set filter): `bb` = new filter value
- `aa = $7f`: Jump to index — `bb` = new index

### Commands (sequence commands — fewer than Driver 5)

| Opcode | Description |
|--------|-------------|
| `0X XX` | Set slide up — `XXX` = value added to current frequency |
| `1X XX` | Set slide down — `XXX` = value subtracted from current frequency |
| `2X YY` | Set vibrato — `X` = frequency, `YY` = amplitude (absolute add/subtract to frequency) |
| `3X YY` | Set filter parameters — `X` = bandwidth, `YY` = resonance and filter select bits |
| `4x YY` | Set filter program pointer — `YY` = new filter program pointer |
| `5x YY` | Set pulse program pointer — `YY` = new pulse program pointer |
| `6x YY` | Set wave table pointer — `YY` = new wave table pointer |
| `8D SR` | Set ADSR — Attack is always set to 0 (documented as "Bummer!") |

### Init table (3 bytes: aa bb cc)

- `aa` = Tempo table index
- `bb` = Volume / Filter bandpass setting (e.g. $1f = $f volume, $1 bandpass)
- `cc` = Filter Resonance / Filter channel enabled (e.g. $f1 = $f resonance, $01 = enable filter ch1)
  - bit0/$01 = channel 1 filter enabled
  - bit1/$02 = channel 2 filter enabled
  - bit2/$04 = channel 3 filter enabled

---

## Appendix: Reversed Nibble Format (Driver 6 Pulse)

Driver 6 uses reversed nibbles for pulse width. The most significant nibble is the least
significant part of the pulse width and vice versa.

If reversed nibble value is `xy`:
- `x` = least significant part
- `y` = most significant part
- Pulse width stored as: `$0yx0`

Example: Pulse width $0800 is expressed as $08 in reversed format.

Addition is straightforward: $08 + $10 = $18 (pulse moves from $0800 to $0810).

Subtraction requires wrapping: to subtract $10 from reversed nibble, compute `$ff - $10 = $ef` and ADD that.
Rule: `AddVal = $ff - SubVal` (both in reversed nibble format).

---

## SID Factory 0.5 Editor Keys

Source: `20060901_SID_Factory_0_5/Docs/SidFactory_Keys.txt`

- 3 editing groups: tracks/sequences, static tables (instruments+commands), dynamic tables
- Instrument range: $00-$1f (max 32 instruments)
- Command range: $00-$3f (max 64 commands)
- Max sequence length: $40 ticks
- Three rows per sequence tick: instrument set row, command set row, note set/held row
- Notes: C#3 / Db3 notation; standard QWE... ProTracker layout
- `*` = tie note (instrument row)
- `+++ / ---` = gate on/off (Shift+Space / Space)

---

## Known Bugs (both drivers)

- Hard restart override is buggy when tempo is 2 and two note events follow each other
- Driver 6: Initialization sometimes creates artifacts of obscure sound
