---
source_url: https://codebase64.com/doku.php?id=base:jch_20.g4_player_file_format
fetched_via: direct 2026-06-15
fetch_date: 2026-06-15
author: FTC/HT
content_date: unknown (Codebase64 wiki)
reliability: secondary
---

# JCH 20.G4 Player File Format (Codebase64 wiki)

Author: FTC/HT ("Brief documentation of the JCH Editor file format, by FTC")

## Memory Layout (fixed addresses in NP20.G4)

| Component              | Address  |
|------------------------|----------|
| Arpeggio Table col 1   | $18CB    |
| Arpeggio Table col 2   | $19CB    |
| Filter Table           | $1ACB    |
| Pulse Table            | $1BCB    |
| Instrument Table       | $1CCB    |
| Sequence Ptrs (lo)     | $1DCB    |
| Sequence Ptrs (hi)     | $1ECB    |
| Super Table            | $1FCB    |
| Voice 0 Orderlist      | $20CB    |
| Voice 1 Orderlist      | $24CB    |
| Voice 2 Orderlist      | $28CB    |
| Sequence Data          | $2CCB+   |

NOTE: These are fixed layout addresses for NP20.G4. Different player versions
(NP15, NP17, NP18, NP21) use different base addresses. The CheeseCutter
player (based on NP21.G4) uses a different base at $1000.

## Sequence Data Format

Each step in the sequence is represented by byte pairs (AA and BB).

### Byte AA values:
- `$7F`      = End of sequence
- `$90`      = Tie note (no retrigger, continue current note)
- `$A0-$BF`  = Instrument selection ($A0 = inst 0, $BF = inst 31)
- `$C0-$DF`  = Super table pointer ($C0 = pointer 0, $DF = pointer 31)
- `$80`      = No command / empty step (hold)

### Byte BB values:
- `$00`      = Gate off
- `$01+`     = Note value (semitone index into frequency table)
- `$7E`      = Gate hold (continuation)

Note: "the description is not 100% complete" per the author. The full
sequence command set is documented in jch_np15g6_full_instructions.txt
and jch_np20g4_full_instructions.txt (primary sources, by JCH).
