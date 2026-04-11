---
source_url: "https://github.com/Galfodo/SIDdecompiler/blob/master/src/SIDdisasm/STHubbardRipper.cpp"
fetched_via: "direct"
fetch_date: 2026-04-11
author: "Galfodo (original C++ code); local: analysis notes"
content_date: "unknown"
reliability: "primary"
---
# SIDdecompiler Commented-Out Conversion Code

Source: https://github.com/Galfodo/SIDdecompiler/blob/master/src/SIDdisasm/STHubbardRipper.cpp
Lines 130-356 are completely commented out — three methods that were apparently ported from an older
Objective-C/iOS tool (comments reference `NSNumber`, `waveTable`, `waveTableEntry` objects from that era).
The `scanForData()` method (lines 8-128) is the only ACTIVE code in the file.

---

## Method 1: convert() — Track/Sequence Dispatcher

```cpp
bool STHubbardRipper::convert() {
  unsigned char* memory = m_sid.m_Memory.data();
  bool is_converted[256];
  memset(is_converted, 0, sizeof(is_converted));
  m_app.song().init();
  // Asserts: 1 subtune, 3 tracks, >= 0x48 sequences
  for (int voice = 0; voice < 3; ++voice) {
    int trackAdr = m_TrackAddress[voice];
    for (int i = 0; i < 256; ++i) {
      int trackdata = memory[trackAdr + i];
      m_app.song().tracks()[voice].m_RawData[i] = trackdata;
      if (trackdata >= 0xfe)          // 0xfe/0xff = end of track
        break;
      if (trackdata >= 0x48) {        // Max 0x48 sequences
        printf("Sequence out of range: %d\n", trackdata);
        continue;
      }
      if (!is_converted[trackdata]) {
        is_converted[trackdata] = convertSequence(trackdata);
        if (!is_converted[trackdata])
          return false;
      }
    }
  }
  return true;
}
```

**Key findings:**
- Track data is a raw byte array. Values `>= 0xfe` are end-of-track markers.
- Up to 0x48 (72) distinct sequences. Values >= 0x48 are out-of-range (logged, skipped).
- Each sequence is converted once (deduplication via `is_converted[]` bitmask).


---

## Method 2: convertSequence() — Sequence Byte Parser

```cpp
bool STHubbardRipper::convertSequence(int sequence) {
  int seqAddr = memory[m_SeqLoAddress + sequence] | (memory[m_SeqHiAddress + sequence] << 8);
  int write = 0;
  bool tied = false, nextTied = false;
  while (true) {
    int data = memory[seqAddr];
    if (data == 0xff) { seq.terminateAt(write); break; }   // 0xff = end of sequence

    notelength = ((data & 0x1f) + 1) / m_SpeedDivider;    // bits [4:0] = raw length

    if (data & 0x40) {                                      // bit 6: release (rest) event
      seq.setReleaseAt(write, notelength);
      write += notelength;
      ++seqAddr;
      continue;
    }

    nextTied = (data & 0x20) != 0;                         // bit 5: tie to next note

    if (data & 0x80) {                                     // bit 7: modifier byte follows
      ++seqAddr;
      data = memory[seqAddr];
      if (data == 0xff) { seq.terminateAt(write); break; }
      if ((data & 0x80) == 0) {                            // modifier bit 7 clear: instrument change
        new_instrument = data;                             // instrument index (max ~0x20)
      } else {                                             // modifier bit 7 set: portamento
        data = data & 0x7f;
        if (data & 1)
          portaval = -(data >> 1);                         // odd -> porta down
        else
          portaval = data >> 1;                            // even -> porta up
      }
    }

    ++seqAddr;
    data = memory[seqAddr] & 0x7f;                         // note byte, bit 7 ignored
    if (data > RawNote::LastNote)
      seq.setReleaseAt(write, notelength);                 // out-of-range note = rest
    else if (portamento)
      seq.setNoteAt(write, data, portaval, false, true, notelength);
    else
      seq.setNoteAt(write, data, new_instrument, tied, false, notelength);

    write += notelength;
    ++seqAddr;
    tied = nextTied;
  }
}
```

**Sequence byte encoding summary:**

Each event is 1-3 bytes:

```
Byte 0 (always present):
  bits [4:0]  raw length field. actual length = (value + 1) / speedDivider
  bit  5      tie flag (current note is tied to next)
  bit  6      release/rest event (no note, just fill time). If set, consume byte 0 and advance.
  bit  7      modifier byte follows (instrument or portamento)

Byte 1 (only if byte0 bit7 set):
  bit  7 = 0  -> instrument index in bits [6:0]
  bit  7 = 1  -> portamento: remaining 7 bits encode direction+magnitude
                 bit 0 of 7-bit value: 1=down, 0=up
                 bits [6:1] >> 1: magnitude (signed, divided)

Byte 2 (note byte, always present if not a rest/release):
  bits [6:0]  note index (chromatic, 0-based). Values > RawNote::LastNote treated as rest.
  bit  7      ignored (masked off with & 0x7f)

Terminator: 0xff at any position ends the sequence.
```

**Speed divider:** `m_SpeedDivider` scales all note lengths. Not shown in this file — likely set
from the player init or a PAL/NTSC detection. Allows the same sequence data to play at different tempos.


---

## Method 3: convertInstruments() — Instrument Block Parser

```cpp
bool STHubbardRipper::convertInstruments() {
  int instrAddress = m_InstrumentAddress;
  for (int i = 0; i < 32; ++i) {              // up to 32 instruments
    // Each instrument = 8 bytes:
    int pulsewidth = (memory[instrAddress] + memory[instrAddress + 1] * 256) >> 5;
    int waveform   = memory[instrAddress + 2];
    int AD         = memory[instrAddress + 3]; // Attack/Decay
    int SR         = memory[instrAddress + 4]; // Sustain/Release
    int unknown    = memory[instrAddress + 5]; // purpose unknown
    int pulselevel = memory[instrAddress + 6] >> 3;
    int fx         = memory[instrAddress + 7]; // effects flags
    int pulsedepth = 32;                       // hardcoded default
    int delay      = 0;
    int waveoff    = waveform & 0xfe;          // gate-off waveform: same as waveform but gate bit cleared

    instrAddress += 8;
  }
}
```

**Instrument byte layout (8 bytes per instrument):**

| Offset | Field       | Extraction                              | Notes                                      |
|--------|-------------|------------------------------------------|--------------------------------------------|
| +0     | pulse lo    | `memory[+0]`                            | Low byte of 16-bit pulse word              |
| +1     | pulse hi    | `memory[+1]`                            | High byte of 16-bit pulse word             |
|        | pulsewidth  | `(lo + hi*256) >> 5`                    | 11-bit result shifted down 5               |
| +2     | waveform    | `memory[+2]`                            | SID waveform byte (with gate bit)          |
| +3     | AD          | `memory[+3]`                            | Attack/Decay nibbles                       |
| +4     | SR          | `memory[+4]`                            | Sustain/Release nibbles                    |
| +5     | unknown     | `memory[+5]`                            | Purpose not decoded                        |
| +6     | pulselevel  | `memory[+6] >> 3`                       | Pulse modulation level                     |
| +7     | fx          | `memory[+7]`                            | Effects bitfield (see below)               |

**Effects byte (fx = instrAddress+7) bitfield:**

| Bit | Mask  | Effect       | Description                                                          |
|-----|-------|--------------|----------------------------------------------------------------------|
| 0   | `& 1` | Drums        | Enables drum mode. Commando instruments 1,4,5,7 skip porta.        |
|     |       |              | If fx==1 exactly ("Ren puka!" = pure drum): waveform forced to 0xc1 (noise+gate), VibLevel=0x10, VibDepth=0xbf. Wave table: gate-on(waveform), noise(no gate), gate-off(waveform), restart at pos 2. |
| 1   | `& 2` | Sky dive     | Pitch-fall effect. VibLevel=0x10, VibDepth=0xbf. Commando instruments 2,5,6,8 skip porta. |
| 2   | `& 4` | Oct arp      | Octave arpeggio. ChordData[0]=0x0c, [1]=0x00, [2]=0x81. FX=0x40. Wave table: gate-on(waveform), gate-on+12semitones(waveform), restart pos 0. |

**Derived output fields (SteinTronic instrument bank):**

```
ins[GateOnWaveForm]  = waveform & 0xff
ins[AD]              = AD & 0xff
ins[SR]              = SR & 0xff
ins[PulseWidth]      = pulsewidth & 0xff
ins[PulseDepth]      = pulsedepth (32, hardcoded)
ins[PulseLevel]      = pulselevel & 0xff
ins[GateOffDelay]    = 0
ins[GateOffWaveForm] = waveform & 0xfe   (gate bit cleared)
ins[RestartGateOff]  = 0x80
```


---

## Summary: What This Tells Us About the Hubbard Format

### Data section layout
- **Songs table**: 6-byte records. First 3 bytes = lo-bytes of 3 track pointers. Next 3 bytes = hi-bytes. Multi-song files have an array of these; single-song files use a different `currtrklo`/`currtrkhi` variable layout.
- **Sequences**: Pointer table split into lo-byte array (`patptl`) and hi-byte array (`patpth`). The index into both arrays is the sequence number. Max 0x48 (72) sequences.
- **Instruments**: Flat array of 8-byte records. Max 32 instruments.
- **Frequency table**: Located by the byte signature `16 01 27 01` (C-1 in PAL, the lowest note).

### Sequence encoding
- Variable-length events (1-3 bytes each)
- Length field is 5 bits, scaled by a speed divider
- Bit flags in the first byte select: rest/release, tie, instrument change, portamento
- Portamento direction is encoded in the LSB of the modifier byte magnitude

### Instrument encoding
- Pulsewidth uses a 16-bit word shifted right 5 bits (keeps upper 11 bits)
- The unknown byte at offset +5 is not decoded — likely vibrato speed or filter settings
- The fx byte drives three mutually-exclusive effects: drums, skydive, octave arpeggio
- "Sky dive" and "Oct arp" both set VibLevel/VibDepth to the same values (0x10/0xbf), suggesting they share a vibrato/LFO mechanism with different waveform table behaviors

### What is NOT present here
- Filter settings (cutoff, resonance, filter routing)
- Vibrato table / LFO parameters beyond VibLevel/VibDepth
- The `m_SpeedDivider` computation
- Any decoding of the unknown byte at instrument offset +5
- The frequency table format beyond its location signature
