<!--
source_url: https://carol6502.neocities.org/c6_ccutter_guide
fetched_via: WebFetch (small-model summarization of fetched page)
fetch_date: 2026-06-13
author/handle: carol6502 (community CheeseCutter guide author)
content_date: unknown (CheeseCutter 2.x era; post-2011)
reliability: secondary
note: CheeseCutter is the cross-platform port of JCH Editor; its player is based
      on NP21.G4 (Laxity / Vibrants / MoN). This therefore documents the NP21+
      *4-byte-table* family, NOT the older NP20.G4 *2-byte-table* family already
      in research.md. Treat this as the authoritative NP21/CheeseCutter spec.
      Numbers below are as reported by the page summarizer; cross-check the
      4-byte row layouts and the sequence command-column map against a real
      CheeseCutter .sng / NP21 rip before trusting them for the codec.
-->

# CheeseCutter / NP21 music format (4-byte-table family)

This is the format used by **CheeseCutter** and the **NP21.G4+** player line
(Laxity / Vibrants / MoN). It differs from the older NP20.G4 documented in
`research.md` chiefly in that **pulse and filter table rows are 4 bytes wide**
(NP20.G4 used 2-byte rows) and the **sequence row is a full 3-byte
note/instrument/command triple** with a rich command column.

## Instrument Table (8 bytes per instrument)

| Byte | Field | Details |
|------|-------|---------|
| A-B  | ADSR  | Attack/Decay (A), Sustain/Release (B) |
| C    | Hardrestart & Wave Delay | Low nibble (0-F): wave delay; high nibble: restart type |
| D    | Hardrestart Waveform | Value written to waveform reg during HR (typically `00` or `08`) |
| E    | Filter Program | `00` = no filter |
| F    | Pulse Program | `00` = no pulse |
| G    | Unused | — |
| H    | Wave Table Pointer | start row in wave table |

### Hard-restart types (byte C, high nibble) — verbatim
- `0x`: "Gate off 3 frames before next note; waveform cleared 1 frame before"
- `4x`: "Soft restart; gate off 2 frames before"
- `8x`: "Regular hard restart; gate off & write hardrestart ADSR value 2 frames before"
- `Ax`: "Laxity restart; like 8x but preserves AD envelope"

> **Hardrestart ADSR default:** "The hardrestart ADSR value is read from the
> first row in the Command Table in bytes B and C. The default value is 0F 00."

(This is the row-0-of-command-table convention already noted for NP20 — the
"super table row 0 stores hard restart ADSR." Confirms it carries into NP21.)

## Wave Table (2 bytes per row) — unchanged from NP20

**Byte A (transpose):**
- `00-5F`: regular (note-relative) transpose
- `80-DF`: absolute transpose (unaffected by note transpose)
- `7E`: stop — wave program stays in previous row
- `7F`: wrap — byte B defines the wrap (loop) point

**Byte B (waveform):**
- `00`: keep previously set waveform
- `01-0F`: overrides the instrument's wave delay for the previous row
- `10-DF`: SID waveform (control-reg) values
- `E0-EF`: SID waveform values `00-0F` (i.e. low control values reachable via the E-prefix)

## Pulse Table (4 bytes per row) — NP21/CheeseCutter

| Byte | Field | Details |
|------|-------|---------|
| A | Duration | `00-7F` = positive sweep; `80-FF` = negative sweep |
| B | Add Value | sweep rate per frame |
| C | Init Value | initial sweep value; `FF` = use previous value (retain) |
| D | Jump Value | `00` = next row; `7F` = stop (jumps to row 0) |

## Filter Table (4 bytes per row) — NP21/CheeseCutter

**Filter INIT rows (byte A >= $80):**
- Byte A: filter type
- Byte B: resonance (high nibble) + voice routing bitmask (low nibble)
- Byte C: initial cutoff frequency
- Byte D: jump value

**Filter SWEEP rows (byte A < $80):**
- Byte A: duration (`00-7F` positive; `80-FF` negative)
- Byte B: add value (always additive; `FF` = subtract 1)
- Byte C: initial cutoff (`FF` = keep previous)
- Byte D: jump value (`00` = next row; `7F` = stop)

## Command Table (3 bytes per entry)

Row 0 holds the hard-restart ADSR (see above). Other rows are commands:

| Code | Command | Parameters (bytes B,C) |
|------|---------|------------------------|
| 0 | Slide up | rate/target |
| 1 | Slide down | rate/target |
| 2 | Vibrato | B: delay; C: speed/depth |
| 3 | Detune | B,C: 16-bit frequency offset |
| 4 | Set ADSR | B,C: Attack/Decay values |
| 5 | Lowfi vibrato | B: speed; C: depth |
| 6 | Set waveform | B: new waveform value |
| 7 | Portamento | "Activate before target notes; tied notes only" |
| 8 | Stop slide/portamento | none |

## Sequence Row (3 bytes) — NP21/CheeseCutter

| Byte | Field | Values |
|------|-------|--------|
| 1 | Note | note value |
| 2 | Instrument | instrument index |
| 3 | Command | see command-column map below |

### Command column ($byte 3) map — verbatim
- `01-3F`: execute command from the Command Table (i.e. command-table row index)
- `40-5F`: change pulse table pointer
- `60-7F`: change filter table pointer
- `80-9F`: activate chord; (`40-7F` = negative transpose) *[as reported — verify]*
- `A0-AF`: set Attack envelope
- `B0-BF`: set Decay envelope
- `C0-CF`: set Sustain envelope
- `D0-DF`: set Release envelope
- `E0-EF`: set global volume
- `F0-FF`: set song speed (`0-1` enable swing)

> NOTE on the `80-9F` line: the summarizer's "(40-7F = negative transpose)"
> aside is ambiguous and likely conflates the chord/transpose sub-encoding.
> Flag for verification against a real CheeseCutter source/rip — this is a
> codec-critical row.

## Tracklist / Order list (per-sequence entry)

- Byte 1 (transpose): `00-5F` regular; `80-DF` absolute; `80` = skip / use previous
- Byte 2: sequence length
- Byte 3+: overall (cumulative) song position

## SID waveform bit reference (for the codec)

Triangle `01` + Sawtooth `02` + Pulse `04` + Noise `08`; e.g. `03` =
triangle+sawtooth; `0F` = all four (locks the oscillator).

## Why this matters for SIDfinity

- **Version discriminator:** 4-byte pulse/filter rows + 3-byte sequence triples
  ⇒ NP21+/CheeseCutter family; 2-byte rows + byte-pair sequence ⇒ NP20.G4.
  This is the single cleanest binary discriminator between the two major eras.
- **Write-model:** hard-restart timing (gate-off N frames before, HR-ADSR write,
  HR-waveform write) is per-instrument via byte C/D and must be reproduced
  frame-accurately. The four HR types differ in (a) how many frames before the
  note the gate drops and (b) whether AD is rewritten (`Ax` preserves AD).
- **Command 7 (portamento)** only acts on tied notes — tie/gate semantics couple
  to the command column.
