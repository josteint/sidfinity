---
name: Reverse engineering tools
description: New universal tools for cracking any SID player engine — regtrace_to_usf, code_flow, memdiff, freq_reconstruct
type: reference
---

**Universal SID reverse-engineering tools (added 2026-04-10):**

| Tool | Purpose | When to use |
|------|---------|-------------|
| `src/regtrace_to_usf.py` | Register trace → USF Song | Any SID where binary parsing fails, or non-GT2 engines |
| `src/code_flow.py` | Find code_end via 6502 control flow | When find_freq_table returns None |
| `src/freq_reconstruct.py` | Reconstruct freq table from played freqs | Diagnosing tuning (PAL/NTSC/custom) |
| `src/memdiff.py` | Static vs dynamic memory classification | Understanding unknown player data layout |
| `siddump --memdump <file>` | Dump 64KB C64 memory after emulation | Feed to memdiff or freq_reconstruct |

**Key architectural insight:** Some SIDs have NO freq table anywhere (not in binary, not in memory). The player computes frequencies mathematically. Only the regtrace path handles these.

**regtrace_to_usf quality (2026-04-10):**
- On 100 random Grade A GT2 songs: 3A + 5B + 6C, avg score 60.2, 20 songs score 80+
- On 311 unparseable GT2 SIDs: 2A + 11B + 12C, 42 songs score 80+
- CRITICAL BUG FIXED: usf_to_sid was ignoring NoteEvent.duration field — notes with duration > 1 were played as 1-tick notes. Fixed by expanding duration into note_row + rest_rows in the GT2 pattern encoder.
- Wave table reconstruction: detects non-noise first-wave waveform changes and octave-up transients from per-frame register data
- Tempo detection: frame-based gate-on interval analysis + event-based refinement + doubling preference (3→6)
- Arpeggio collapse: detects repeating short-note patterns, merges into single note with wave table offsets
- Noise first-wave disabled: V2 player timing doesn't match original noise click well enough

**Still not captured:**
- Full wave table cycling (the biggest remaining quality gap — ~40% of frames differ)
- Vibrato/portamento effects
- Pulse modulation
- Filter effects

**See also:** `docs/reverse_engineering.md` for full investigation results.
