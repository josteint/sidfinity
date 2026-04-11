---
source_url: https://github.com/anarkiwi/desidulate
fetched_via: local read
fetch_date: 2026-04-11
author: Josh Bailey (anarkiwi)
content_date: unknown
reliability: secondary
---
# desidulate SSF Analysis — Technical Details

**Repo:** https://github.com/anarkiwi/desidulate
**Author:** Josh Bailey
**License:** MIT

## Architecture

Pandas-based pipeline for SID register analysis:

```
VICE emulator (-sounddev dump)
    -> vicesnd.sid (CSV register log)
    -> reg2state() [sidlib.py] -> DataFrame of decoded SID state
    -> state2ssfs() [sidwrap.py] -> SSF log + SSF summary DataFrames
    -> ssf2midi.py / ssf2wav.py / ssf2swi.py (export)
```

## Key Module: sidlib.py

### reg2state(snd_log_name, nrows)

Reads VICE `-sounddev dump` output (CSV format with clock offsets + register writes).

Processing steps:
1. `compress_writes()` — reads CSV, cumulates clock offsets, removes duplicate consecutive
   register writes to same address
2. Pivot register data from long to wide format (one column per register)
3. `decode_regs()` — orchestrates per-voice and global decoding

### Voice Decoding (set_voice)

For each of 3 voices (register offsets 0-6, 7-13, 14-20):
- **Frequency:** 16-bit from lo + (hi << 8)
- **Pulse width:** 12-bit from lo + (hi & 0x0F) << 8
- **Control bits:** Individually extracted — gate, sync, ring, test, tri, saw, pulse, noise
- **ADSR:** High/low nibble split for attack, decay, sustain, release

### Global Decoding (set_common)

Registers 21-24:
- Filter cutoff (11-bit)
- Filter resonance + voice routing
- Volume + filter type + voice 3 mute

### Register Constants

```python
CONTROL_BITS = ["gate", "sync", "ring", "test", "tri", "saw", "pulse", "noise"]

CANON_REG_ORDER = (
    "gate1", "freq1", "pwduty1", "pulse1", "noise1", "tri1", "saw1", "test1",
    "sync1", "ring1", "freq3", "test3", "flt1", "fltcoff", "fltres", "fltlo",
    "fltband", "flthi", "fltext", "atk1", "dec1", "sus1", "rel1", "vol"
)
```

## Key Module: ssf.py (SID Sound Fragments)

### SidSoundFragment class

Represents an atomic musical unit bounded by gate transitions (GATE 0->1).
Each SSF captures all register changes for one voice between consecutive gate-on events.

Key methods:
- `control_labels()` — segments waveform sequences, distinguishing noise ("n") and
  pulse ("p") phases
- `add_freq_notes_df()` — extracts unique freq1 values, applies SID frequency scaler,
  maps to closest MIDI notes via `closest_midi()` lookup
- `samples_loudestf()` — determines loudest frequency for percussion classification

### Percussion Detection

Fragments classified as percussion when:
1. Duration <= one half-note
2. Noise waveform present
3. Initial pitch drop > 2 semitones
4. Loudest frequency matches `MEMBRANE_DRUM_MAP` cutoff frequencies

Maps to MIDI drum types: kicks (low freq), snares (mid freq), hi-hats (high freq).

### Instrument Boundaries

Boundaries emerge from:
- Control label parsing (waveform sequence segmentation)
- Volume state filtering (excluding NA, normalizing to 15)
- Clock-based indexing with forward-fill interpolation

## Key Module: sidwrap.py (SID Emulation Wrapper)

Wraps pyresidfp for SID chip emulation. Contains:
- PAL/NTSC clock frequency configuration
- Timing conversion (musical time <-> clock cycles)
- ADSR envelope timing tables (`ATTACK_MS`, `DECAY_RELEASE_MS`)
- `state2ssfs()` function — converts decoded register state to SSF boundaries

## Value for Hubbard Decompiler

### SSF concept maps to Hubbard notes:
- Hubbard's notes are gate-bounded (gate-on at note start, gate-off at release)
- SSFs capture exactly this structure
- Exception: Hubbard's legato/append flag (bit 6) skips gate-off between tied notes,
  so an SSF may span multiple logical notes. Our decompiler must handle this.

### Percussion detection is relevant:
- Hubbard's drum instruments (FX bit 0) use noise waveform + rapid pitch fall
- desidulate's percussion classifier should correctly identify these
- The pitch-drop criterion (>2 semitones) matches Hubbard's drum behavior

### Register-level validation:
- Generate VICE register dump from original Hubbard SID
- Generate VICE register dump from our rebuilt SID
- Run both through desidulate's reg2state
- Compare SSF characteristics (waveforms, ADSR, frequencies, durations)
- Any systematic differences indicate player bugs

### Limitation:
- Requires VICE emulator for register dumps (we use siddump/libsidplayfp instead)
- Converting our siddump output to VICE dump format would be needed, or we could
  adapt desidulate's reg2state to read our format
