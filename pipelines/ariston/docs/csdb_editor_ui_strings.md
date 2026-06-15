---
source_url: http://csdb.dk/getinternalfile.php/2252/ariston_illusion.d64
fetched_via: curl (local file: /home/jtr/sidfinity/tmp/ariston_research/ariston_illusion.d64)
fetch_date: 2026-06-15
reliability: primary
---

# Ariston Editor — UI Strings Extracted from Binary

Method: `strings` tool + Python PETSCII decode of ariston_main_prg.prg (extracted from D64).

**PRG details:**
- Extracted from D64 as: `ariston_main_prg.prg`
- Load address: $0801
- Size: 30007 bytes
- Date string: "6-24-88" (June 24, 1988)

## Credit Strings
```
PROGRAMMED BY PHILIPP BBIN 1987/88
(C) ARISTON DESIGNS '88
```
(PETSCII truncation — "PHILIPP BBIN" = "PHILIP BRABBIN")

## Waveform Type Selector Strings (at ~$26E3 in C64 address space)
The editor offers multiple waveform types, found as PETSCII strings:
```
ANGLE SAWTOOT   → TRIANGLE + SAWTOOTH (likely: "TRIANGLE" / "SAWTOOTH")
PULS>QNOISXYNC  → PULSE / NOISE / SYNC (separated by control characters)
```

Interpreted waveform options available in editor:
1. TRIANGLE (ANGLE → trIANGLE suffix)
2. SAWTOOTH
3. PULSE
4. NOISE
5. SYNC

## Instrument/Effect Parameter Strings (at ~$5F00–$6200)
Found via PETSCII decoding of editor menu area:
```
=VOLUME         → Master volume control
ENVELOPE        → ADSR envelope section
ENVIBOPES       → "ENVELOPES" (PETSCII control chars in middle)
NVIB. D%WAY     → "VIBRATO DECAY" or "VIB. DELAY" — vibrato parameter
CHROMATIC       → Chromatic pitch mode (arpeggio?)
GLISSANDO       → Glide/portamento effect
SECTION         → Song section marker
RANGE           → Pitch range control
123456          → Voice/channel numbering (up to 6 entries? or step 1–6?)
```

## Navigation/UI Strings
```
RETURNDF        → "RETURN" key instruction
CRSR            → Cursor key references
PRESS 1-4 FOR MUSIC   → Crack intro demo selection
```

## Structural Inference from UI
From the editor strings, the Ariston format likely includes:
- Per-voice ADSR envelopes
- Per-voice vibrato with delay parameter
- Waveform selection: triangle, sawtooth, pulse, noise, sync
- Portamento/glide (GLISSANDO)
- Chromatic pitch / arpeggio (CHROMATIC)
- Master volume control
- Song sections
- At least 3 voices (standard SID), possibly up to 6 channels (unlikely but "123456" found)
- Volume for main body

## sidid.cfg Signature Interpretation

The three signatures show:
- `E0 08 D0 EF` — CPX #8 ; BNE — loop over 8 values (possibly 8 bytes per voice × 3 voices = some table)
- `99 00 D4` — STA $D400,Y — writes to SID register via Y offset
- `99 05 D4`, `99 06 D4` — writes to $D405,Y (freq hi) + $D406,Y (pulse lo)
- `99 04 D4` — writes to $D404,Y (control register)
- Per-voice stride in Y (Y=0,7,14 for voice 1,2,3 base registers)
- Wally_Beben variant adds: boundary check `C9 08 B0` = CMP #8 ; BCS (different voice routing)

The `E0 08` in the main signature (CPX #8 loop) suggests the player iterates over 8 items — possibly: 8 effect slots per voice, or 8 registers written per voice iteration.
