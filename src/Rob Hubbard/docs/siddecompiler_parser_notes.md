---
source_url: https://github.com/Galfodo/SIDdecompiler/blob/master/src/SIDdisasm/STHubbardRipper.cpp
fetched_via: direct (GitHub raw)
fetch_date: 2026-04-21
author: Stein Pedersen (Galfodo)
content_date: unknown (repo active 2015+)
reliability: primary
---

# SIDdecompiler — STHubbardRipper.cpp Analysis

**Repo:** https://github.com/Galfodo/SIDdecompiler
**File:** `src/SIDdisasm/STHubbardRipper.cpp` (12,816 bytes)
**Purpose:** C++ Rob Hubbard SID ripper/converter, started as a Prosonix plugin

The SIDdecompiler project originated specifically to produce a Rob Hubbard plugin for
the Prosonix SID tracker. Rob Hubbard tunes get "non-generic label names for data of
known purpose" — better documentation than other drivers.

---

## Data Structure Detection Patterns

The ripper uses byte-pattern matching on the SID binary to find data structures.

### Multi-song format detection
```
Pattern: "bd****99****e8c8c006"
```
This matches: `LDA songs_lo,X` / `STA (ptr),Y` / `INX` / `INY` / `CPY #$06`
Used when the song has a table of 3-channel track pointers indexed by song number.

### Single-song format (fallback)
```
Pattern: "bd****85**bd****85**de"
```
Matches: `LDA table,X` / `STA zp` / `LDA table,X` / `STA zp` / `DEC`
Used when track pointers are hardcoded (one song only).

### Instrument data detection
```
Pattern: "bd****9902d4bd****9903d4"     (without push)
Pattern: "bd****9902d448bd****9903d4"   (with PHA push, alternate variant)
```
Matches SID register write pattern for voice frequency (D402/D403 = voice 1 freq lo/hi).

### Sequence pointer detection
```
Pattern: "a8b9****85**b9****85**"
```
Matches: `TAY` / `LDA seq_hi,Y` / `STA zp` / `LDA seq_lo,Y` / `STA zp`
This is the standard pattern for loading a pattern address from lo/hi tables.

### Frequency table detection
```
Pattern: "16012701"
```
The bytes $16 $01 $27 $01 = the C-1 and C#-1 frequencies in the PAL freq table.
(Same as our `find_freq_table` approach.)

---

## Note Duration Formula (from commented-out convertSequence)

```cpp
notelength = ((data & 0x1f) + 1) / m_SpeedDivider;
```

- `data & 0x1f` = lower 5 bits of first note byte (0-31)
- `+1` converts to 1-based count
- `/ m_SpeedDivider` = divide by the speed divider

**Critical:** `m_SpeedDivider` is initialized externally but NOT shown in the active code.
It's a member variable of PlayerInstance. This suggests it's detected from the binary
separately and stored in the struct before conversion.

The formula divides out the speed, converting from "driver ticks" to some normalized unit.
For our purposes: **frames = (note_len_bits + 1) * (resetspd + 1)**

---

## Instrument Format (from commented-out convertInstruments)

```cpp
int pulsewidth = (memory[instrAddress] + memory[instrAddress + 1] * 256) >> 5;
int waveform   = memory[instrAddress + 2];
int AD         = memory[instrAddress + 3];
int SR         = memory[instrAddress + 4];
int unknown    = memory[instrAddress + 5];   // vibrato depth
int pulselevel = memory[instrAddress + 6] >> 3;  // PWM speed, right-shifted
int fx         = memory[instrAddress + 7];
```

Note: `pulsewidth >> 5` converts the 16-bit PW value to a reduced-precision format.
`pulselevel >> 3` similarly reduces the PWM speed byte.

### Effects from fx byte
```cpp
if (fx & 0x01) { /* drum */ }
if (fx & 0x02) { VibLevel=0x10; VibDepth=0xbf; }  // skydive
if (fx & 0x04) { /* octave arpeggio, chord data */ FX=0x40; }
```

The skydive sets specific vibrato level/depth constants (VibLevel=$10, VibDepth=$BF)
in the output format — these are fixed values in the Prosonix/SIDdecompiler output format,
not the actual driver parameters.

---

## PlayerInstance Structure

```cpp
struct PlayerInstance {
    std::vector<SongData> m_Songs;
    int m_InstrumentAddress;
    int m_SeqLoAddress;
    int m_SeqHiAddress;
    int m_SequencesUsedGuesstimate;
    int m_FrqAddress;
    // implied: int m_SpeedDivider;
};

struct SongData {
    int m_SongAddress;
    int m_TrackAddress[3];
};
```

---

## What the SIDdecompiler Does NOT Handle

1. **Speed counter detection** — m_SpeedDivider is used but its initialization is not visible
   in STHubbardRipper.cpp. It's likely set elsewhere (possibly hardcoded or from binary scan).
2. **Nested speed counters** — no evidence in the code.
3. **Fourth channel** — only 3 track addresses per song (m_TrackAddress[3]).
4. **Driver variants** — only 2 variants detected (multi-song vs single-song by pointer table pattern).
5. **Per-song speed tables** — not detected.

---

## Key Takeaway for Our Implementation

The SIDdecompiler confirms our approach is correct:
- 8-byte instruments at a fixed base address
- Sequence tables: separate lo/hi arrays
- Track pointers: lo/hi from song table
- Note format: first byte has 5-bit length + 3 flag bits

The `m_SpeedDivider` mystery suggests they either hardcoded it or scanned for it in a
separate pass not shown in this file. Our `find_speed()` in `rh_decompile.py` is likely
more sophisticated than what SIDdecompiler does.
