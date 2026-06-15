---
source_url: https://codebase64.com/doku.php?id=base:jch_20.g4_player_file_format
fetched_via: direct
fetch_date: 2026-06-15
author: FTC (documented on Codebase64 wiki)
content_date: unknown (wiki article, not dated)
reliability: secondary
---

# JCH 20.G4 Player File Format

Brief documentation of the JCH Editor file format, by FTC.
Available on Codebase64 wiki at multiple mirror URLs:
- https://codebase64.com/doku.php?id=base:jch_20.g4_player_file_format
- https://codebase64.pokefinder.org/doku.php?id=base:jch_20.g4_player_file_format
- http://www.codebase64.pokefinder.org/doku.php?id=base:jch_20.g4_player_file_format

## Memory Layout (fixed addresses for NP20.G4)

| Component | Address |
|-----------|---------|
| Arpeggio table Col 1 | $18CB |
| Arpeggio table Col 2 | $19CB |
| Filter table | $1ACB |
| Pulse table | $1BCB |
| Instrument table | $1CCB |
| Sequence Pointers (Low byte) | $1DCB |
| Sequence Pointers (High byte) | $1ECB |
| Super Table | $1FCB |
| Voice 0 sequence list | $20CB |
| Voice 1 sequence list | $24CB |
| Voice 2 sequence list | $28CB |
| Sequence 0 data | $2CCB (+3 bytes offset) |
| Sequence 1 data | $2DCB (+3 bytes offset) |

**Note:** These are the NP20.G4 canonical addresses. NP21.G4/G5 (Laxity) uses
the same table structure but with 4-byte (not 2-byte) pulse/filter rows and
48-instrument column-major layout (instead of NP20's 32 instruments).

## Sequence Data Format

Each step in a sequence is represented by a byte pair (AA, BB).

**Byte AA:**
- `$7F` — End of sequence
- `$90` — Tie note (retrigger prevention; gate stays on)
- `$A0–$BF` — Instrument selection: instrument number = (AA - $A0), range $00–$1F (max 32 instruments in NP20; 48 in NP21)
- `$C0–$DF` — Super Table pointer: index = AA - $C0
- `$80` — No operation / hold

**Byte BB:**
- `$00` — Gate off
- `$01+` — Note value (triggers the active instrument at this note)
- `$7E` — Gate hold / sustain (NP gate-on-hold sentinel)

## Example encodings

| AA | BB | Meaning |
|----|-----|---------|
| $A2 | $24 | Instrument 2, note C-3 |
| $80 | $7E | Hold current instrument with gate on |
| $80 | $00 | Empty row |
| $90 | $25 | Change to C#4 without retriggering (tie) |

## Notes for USF extraction

This documentation is for the NP20.G4 packed binary format — the on-disk
layout. The NP21.G4 (Laxity_NewPlayer_V21) and NP21.G5 players use:
- 4-byte pulse rows (vs 2-byte in NP20)
- 4-byte filter rows (vs 2-byte in NP20)
- 48 instruments, column-major layout with stride=48 (vs 32 instruments in NP20)
- Same AA/BB sequence alphabet (with NP21 extending to 48 instruments: $A0–$CF = insts $00–$2F)

The full NP21 format oracle is CheeseCutter's `player_v4.acme` (GPL; documented
in `pipelines/laxity_newplayer/docs/cluster_np21_effect_routines.md`).

The article notes: "this format is not directly visible in the editor interface,
making the specification valuable for conversion tools."
