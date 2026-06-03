# Future Composer (MoN/FutureComposer)

## Overview

- **HVSC count:** 4,085 tunes
- **Origin:** Finnish Gold (1988), based on ripped Maniacs of Noise driver
- **Versions:** V1.0 (1988), V2.0-2.1 (Beastie Boys, 1988), V3.1 (Union, 1990), V4.0-4.1 (Dynamix, 1989-1990)
- **Note:** Unrelated to Amiga Future Composer (Jochen Hippel) — completely different format
- **Architecture:** Descended from MoN driver, which was influenced by Rob Hubbard's driver

## Entry Points

- Init: load address (commonly $1000 or $1800)
- Play: init + 6 (**distinctive +6 offset**, not +3)
- Example: init=$1800, play=$1806

## Data Hierarchy

1. **Song/Sequence Table** — per-voice ordered list of pattern numbers
2. **Pattern Data** — note events
3. **Sound/Instrument Definitions** — waveform/envelope/effect programs
4. **Frequency Table** — 96 entries of 16-bit SID frequencies (C-0 to B-7)

## Sequence Table

Per voice: entries specify pattern number, transposition (semitones), speed. Terminated by $FF (loop) or end marker. Three voices advance in parallel.

## Pattern Data (2-4 bytes per note, Hubbard lineage)

- Byte 1: duration + flags (legato/tie, instrument change, portamento)
- Byte 2 (conditional): instrument number or portamento speed
- Byte 3: pitch (0-95, index into frequency table)
- Byte 4 (conditional): effect parameter
- $FF: pattern end
- Standard length: 32 steps per pattern

## Instrument Format

| Parameter | Purpose |
|-----------|---------|
| Pulse Width lo/hi | Initial pulse width |
| Waveform/Control | Wave selection + gate/sync/ring/test |
| Attack/Decay | ADSR |
| Sustain/Release | ADSR |
| Vibrato depth | Pitch modulation |
| Pulse speed | PWM rate |
| Effect flags | Drum, skydive, arpeggio |

Later versions (V3+) added:
- Wave table (per-frame waveform control)
- Pulse table (automated PWM sequences)
- Filter table (per-frame filter cutoff/resonance/mode)

Tables use command-based language: 2-3 bytes per entry (command + param), with loops, jumps, delays.

## Memory Layout (typical)

```
$1000-$10FF  Player code
$1100-$11FF  Variables, shadow registers
$1200-$12xx  Frequency table (192 bytes)
$1300+       Instruments, sequences, patterns, tables
```

Total: 2-8 KB. Relocatable within PSID.

## Player Frame Execution (50 Hz)

Per voice:
1. Decrement duration, fetch next note if zero
2. Parse note bytes, load instrument if new
3. Apply pitch from freq table + transposition
4. Execute wave table program
5. Execute pulse table
6. Apply vibrato, portamento, arpeggio
7. Write SID registers

Global: execute filter table, write $D415-$D418.

## Version Differences

| Version | Changes |
|---------|---------|
| V1.0 | Basic MoN driver rip |
| V2.0-2.1 | Bug fixes, improved editor |
| V3.x | Enhanced driver (Hawkeye), wave/pulse/filter tables |
| V4.0-4.1 | Sequence editor, filter/drum editors, packed format |

## Related MoN Drivers

Same family: MoN/Deenen, MoN/Bjerregaard, MoN/Cyb2, MoN/JTS, MoN/TTWII, MoN/RWE, MoN/Bantam, MoN/Deenen_Digi. Same architecture, different customizations.

## SIDId Signatures

Multiple variants: MoN/FutureComposer (generic), FutureComposer_V1.0, FC_V4_Packed, FC_V3.x.
