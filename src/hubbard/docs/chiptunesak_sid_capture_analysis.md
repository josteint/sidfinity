---
source_url: https://github.com/c64cryptoboy/ChiptuneSAK
fetched_via: local read
fetch_date: 2026-04-11
author: unknown (ChiptuneSAK project / c64cryptoboy)
content_date: unknown
reliability: secondary
---
# ChiptuneSAK SID Register Capture — Technical Analysis

**Repo:** https://github.com/c64cryptoboy/ChiptuneSAK
**Key file:** `chiptunesak/sid.py`
**Architecture:** LLVM-inspired pipeline: Import -> Chirp IR -> Transform -> Export

## How It Works

ChiptuneSAK runs SID files through a built-in 6502 emulator (`thin_c64_emulator.py`),
captures every write to $D000-$DFFF during play routine execution, and converts the
register snapshots into structured note events.

## Register Capture (sid.py)

The `track_io_settings()` method records every write to I/O addresses during each play
call. After each call completes, a full SID register snapshot is taken.

### Per-voice registers captured (3 channels x 7 bytes each):
```
Offset 0+7*ch: Frequency low byte
Offset 1+7*ch: Frequency high byte
Offset 2+7*ch: Pulse width low byte
Offset 3+7*ch: Pulse width high byte (4 bits)
Offset 4+7*ch: Control register (gate, sync, ring, test, waveform)
Offset 5+7*ch: Attack/Decay
Offset 6+7*ch: Sustain/Release
```

### Global registers:
```
$D415-$D416: Filter cutoff (11-bit)
$D417: Filter resonance (bits 4-7) + voice routing (bits 0-2)
$D418: Volume (bits 0-3) + filter type (bits 4-6) + voice 3 mute (bit 7)
```

## Note Event Detection

A new note is created when ANY of these conditions hold:

1. **First play call** (`play_call_num == 0`)
2. **Silent-to-active transition** — no previous active note, current has gate ON + waveforms enabled
3. **Frequency change** on an already-active note
4. **Intra-frame gate toggle** — gate briefly toggled within the play routine while frequency unchanged
5. **Gate-off during release** — optional, tracks release envelope duration using ADSR tables

### Release envelope tracking:
Uses lookup tables indexed by the ADSR release nibble to calculate when the release
phase has completed. This avoids false note-on events from lingering envelope output.

## Frequency-to-Note Conversion

```python
midi_note = log2(freq_arch / base_freq) * 12 + offset
```

- Architecture-aware: uses PAL or NTSC clock from SID header or parameter
- Base frequency derived from tuning parameter (default 440 Hz concert pitch)
- **Vibrato margin:** Frequencies within N cents of the previous note snap to that note,
  reducing false note changes from vibrato oscillation. Critical for Hubbard SIDs which
  use aggressive vibrato.
- Rejects frequencies below ~8 Hz (MIDI note -1 floor)

## Delta Row Optimization

Instead of storing complete state per frame, generates "delta rows" showing only changes
from the previous snapshot. First row with notes includes full filter/volume state as baseline.

## Multispeed Detection

Compares CIA 1 timer A latch value set during init against standard values:
- PAL standard: 17045 cycles
- NTSC standard: 17095 cycles
- >30% deviation triggers multispeed mode, scaling play call interval

## Instrument Detection: NOT Implemented

All notes receive `instr_num = 1`. Code comments: "FUTURE: Do something with instruments?"
Waveform composition (tri/saw/pulse/noise) is captured in 4-bit flags but NOT mapped to
instrument identities.

## Value for Hubbard Decompiler

### Directly useful:
- **Note detection logic** — the 5-condition trigger system is well-designed and handles
  Hubbard's gate patterns (legato/append via bit 6, drum gate toggles)
- **Vibrato margin** — essential for Hubbard's logarithmic vibrato, which sweeps frequency
  continuously. Without this, every vibrato cycle generates false note events.
- **Release tracking** — Hubbard's "no release" flag (bit 5) means some notes never gate
  off. ChiptuneSAK handles this via ADSR duration tracking.

### Not useful:
- **Instrument detection** — placeholder only, no help here
- **Pattern/sequence structure** — register-level approach cannot recover this
- **Effect classification** — vibrato, portamento, arpeggio are all just frequency changes
  from this perspective

### As validation oracle:
Run Hubbard SID through ChiptuneSAK, extract note list (pitch + timing + duration).
Compare against our decompiler's parsed pattern data (after expanding sequences/tracks
to a flat note list). Discrepancies indicate either:
- Our decompiler is parsing data wrong
- ChiptuneSAK's heuristics are wrong (less likely for simple cases)
- Timing difference in playback speed interpretation
