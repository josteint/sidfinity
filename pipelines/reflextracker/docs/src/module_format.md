---
source_url: binary analysis of MOD.TRANCE202.prg + MOD.ENDLOSCHOOR.prg + MOD_ACCESS2B_extracted.prg
fetched_via: direct (files already in tmp/reflextracker_research/)
fetch_date: 2026-06-15
author: RE analysis by this session
content_date: 2026-06-15
reliability: primary (binary evidence; no public format spec found)
---

# Reflextracker Module Format (RFX1)

**Status**: Partially reverse-engineered from binary evidence. No public format
specification found. The manual (described as "multi-page, written in German by PVCF")
has not been located online.

## Magic / Header

All Reflextracker module files start with the 4-byte magic string:

```
52 46 58 31   = "RFX1"
```

Immediately following the magic the data appears to be **8-bit PCM audio sample data**
(values cluster around 0x77–0x88 indicating signed audio centered at 0x80). The module
is primarily a large sample bank.

## Module File Layout (Observed)

### In standalone tracker context (MOD.TRANCE202.prg, loads at `$1009`)

```
$1009: RFX1 magic
$100D+: Sample data (8-bit PCM, ~26 KB)
  - Channel 1 samples
  - Channel 2 samples (may be interleaved or sequential)
$3D80: Pattern / sequence data (small: ~8 bytes observed: 23 33 43 34 44 43 35 77)
$3400: Init pointer table (8 bytes): [src_hi, dst_hi, partial, pages] × 2
  B7 1F E4 F0 70 C0 06 06
$B700+: Secondary sample data / silence/padding (all 0x88 = silence)
$1F00: Play engine code (1728 bytes) — gets copied to $F000 at PSID init
```

### In SID-embedded format (Trance_202.sid)

Entire SID body from `$1000` to `$C12E`:
- `$1000`–`$10FF`: Zeros (padding / unused low page)
- `$1100`+: Module sample data (non-zero starts here)
- `$1F00`–`$25BF`: Play engine (1728 bytes, copied to `$F000`)
- `$3400`: Init pointer table
- `$3D80`: Pattern/sequence data blob
- `$B700`+: Secondary tables / sample data (copied to `$E400`)
- `$C000`–`$C12D`: iAN CooG HVSC wrapper (init/play stubs)

## Pattern/Sequence Data

At `$3D80` in Trance_202.sid, 8 bytes were found before a zero run:
```
23 33 43 34 44 43 35 77
```

These look like note/step values in the range 0x23–0x77. Given the player's
`CMP #$50` / `BCS too_high` check, valid note range appears to be 0x00–0x4F (0–79).
Values above $50 may be control/effect bytes or silence markers.

**Hypothesis**: The pattern data is a sequence of note bytes (0x00–0x4F) with sentinel
values (>= $50) for control (loop, end, silence, speed change). This is typical for
compact C64 digi tracker formats.

## Sample Storage

The audio sample data is 8-bit PCM. Audio appears centered around 0x77–0x88 (signed or
unsigned depending on convention). The digi playback uses SID $D418 (volume register) as
a DAC, writing 4-bit amplitude values.

**Encoding**: The player reads sample bytes and writes the upper nibble to $D418. So
sample bytes are effectively 4-bit PCM, or the player extracts upper/lower nibbles
alternately (as is common in C64 digi players — 2 samples per byte → doubles effective
sample rate).

## Note-to-Period Mapping

From the subroutine at `$F2CF` (play engine):
```
Note 0x00–0x4F (0–79) → CIA timer period
- Note >> 3 = octave (0–9)
- Within-octave fraction → CIA fine-tuning
- ADC immediate #$D0 / #$DA (patched to #$11 / #$18 by init)
```

The CIA timer at `$DC04/$DC05` controls sample playback rate (~6657 Hz at value `$94`).
Note variation adjusts this timer to create pitch effects on the samples.

## Module Files Found

| File | Load | Size | Content |
|------|------|------|---------|
| MOD.TRANCE202.prg | `$1009` | 28472 bytes | Full module (Trance 202 tune) |
| MOD.ENDLOSCHOOR.prg | `$95FC`? | 9910 bytes | Shorter module ("Endloschoor") |
| MOD_ACCESS2B_extracted.prg | `$4A1C` | 29412 bytes | "Access Denied" module |

Note that ENDLOSCHOOR loads at `$95FC` — this is unusual (> `$8000`). This may indicate
a multi-SID configuration where module data lands in upper RAM while SID 1 is at
`$D400` and SID 2 might be at a different address.

## Unknown / Unresolved

1. **Instrument/patch format**: What parameters (loop points, loop type, length, base
   pitch) define each sample instrument? Not yet located.
2. **Sequence/orderlist format**: How channels reference patterns? Only 8 bytes found.
3. **Effect commands**: Are there volume, arpeggio, or other effects beyond pitch?
4. **Multi-SID channel mapping**: How 4–10 channels map to multiple SID addresses.
5. **Module version byte**: Is there a version byte after "RFX1"? First byte varies
   between modules (0x87, 0xBB) — could be version or first sample byte.
6. **ENDLOSCHOOR high load address** ($95FC): significance unclear.
