---
source_url: http://csdb.dk/getinternalfile.php/2252/ariston_illusion.d64
fetched_via: curl
fetch_date: 2026-06-15
reliability: primary
---

# Ariston Editor Binary Analysis

## D64 Disk Images

Two D64 disk images downloaded:
- `ariston_illusion.d64` (release #29914, Illusion crack) — 174848 bytes
- `ariston_cic.d64` (release #119920, CIC crack) — 174848 bytes

Both images have identical directory structure: one PRG file named `ARISTON`.

## Main PRG File

- **D64 directory:** 1 file, name `ARISTON`, type $82 (PRG), 119 blocks
- **Load address:** $0801
- **File size:** 30007 bytes
- **Date string embedded:** "6-24-88" (June 24, 1988)

## Embedded Text Strings (PETSCII-decoded)

### Credit/Copyright
- `PROGRAMMED BY PHILIPP BBIN 1987/88` (C64 addr ~$412B; PETSCII truncation of "PHILLIP BRABBIN")
- `(C) ARISTON DESIGNS '88`

### Editor UI Strings
Found at addresses ~$5F00–$6200 (PETSCII decoded):

**Waveform/oscillator type selector:**
- `ANGLE SAWTOOT` (TRIANGLE + SAWTOOTH — two waveforms combined in display)
- `PULS>QNOISXYNC` (PULSE, NOISE, SYNC — separated by control chars in PETSCII)

Interpreted: The editor offers waveform choices including at minimum: TRIANGLE, SAWTOOTH, PULSE, NOISE, SYNC.

**Instrument/envelope parameters:**
- `=VOLUME` — volume control
- `ENVIBOPES` — likely "ENVELOPES" (ADSR)
- `NVIB. D%WAY` — likely "VIBRATO DECAY" or "VIB. DELAY"
- `CHROMATIC` — chromatic pitch mode
- `GLISSANDO` — glide/portamento effect
- `ENVELOPE` — separate envelope section label
- `SECTION` — section marker
- `RANGE` — pitch range control

**Navigation:**
- `RETURNDF` — likely "RETURN" key instruction
- `CRSR` — cursor references

### Demo/Crack Intro Text (from Illusion crack)
- `ILLUSION`
- `THE NEW MEMBER LIST IS BIG MAN - BLACKBEARD - SATAN - INTRUDER - DOCTOR D - AND ALLEY KAT`
- `IMPORTED ON` [date]
- `INTRO BY SATAN`
- `305-559-6065` (US phone number — contact for Illusion group)
- `PRESS 1-4 FOR MUSIC`

### Embedded Music Demos (crack intro)
The crack intro loads 4 music demos (press 1–4 to select).

## sidid.cfg Fingerprint Signatures

From `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg`:

Three variants identified:

### Main Signature
```
Ariston
A2 00 6E ?? ?? 90 07 BD ?? ?? 99 ?? ?? C8 E8 E0 08 D0 EF AE ?? ?? A9 FF END
```

### Ian_Crabtree_V1
```
(Ian_Crabtree_V1)
9D ?? ?? 20 ?? ?? CA 10 EF A0 ?? A9 ?? 99 00 D4 END
```

### Ian_Crabtree_V2
```
(Ian_Crabtree_V2)
AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 29 0F 48 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 BD END
```

### Wally_Beben (improved version)
```
(Wally_Beben)
48 C9 08 B0 ?? A9 ?? 9D ?? ?? AC ?? ?? 68 99 03 D4 68 99 02 D4 CE ?? ?? 30 END
BD ?? ?? AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 END
BD ?? ?? 99 04 D4 AE ?? ?? EE ?? ?? BD ?? ?? 18 END
```

**Key observations from signatures:**
- `99 ?? ?? C8 E8 E0 08 D0 EF` = STA $????,Y ; INY ; INX ; CPX #8 ; BNE ... — iterating over 8 values (3 voices × something?)
- `99 00 D4` = STA $D400,Y — SID register write using Y as index
- `99 05 D4` / `99 06 D4` = STA $D405,Y / STA $D406,Y — per-voice freq hi / pulse lo
- `99 04 D4` = STA $D404,Y — per-voice control register
- `BD ?? ??` = LDA $????,X — loading from tables indexed by X
- `AE ?? ??` = LDX $???? — load X from memory
- `EE ?? ??` = INC $???? — increment counter
- `CE ?? ?? 30` = DEC $???? ; BMI — decrement and branch if minus (counter)
- Wally_Beben variant has: `48 C9 08 B0 ...` = PHA ; CMP #8 ; BCS — checking voice bounds before writing

## Address Patterns in HVSC Corpus

Analysis of 147 Ariston SIDs (load=$0000 for all = BASIC loader or relocatable):

### Crabtree V1 pattern (14 of 21 Crabtree SIDs)
- `init = play + 3` (e.g., play=$1000, init=$1003)
- The 3-byte gap = 3 bytes at play address before init code (likely JMP init_main or JSR)
- All load addr = $0000 (PSID: music is at whatever address it was saved from)

### Wally Beben variant
- Wide scatter of init/play addresses: no consistent 3-byte pattern
- Addresses range from $0900 to $FF03

### No fixed load address
- All 147 SIDs have load_addr=$0000 — the music player is relocatable or was extracted from game binaries with varied positions
- NOT a fixed-address player like many other engines

## JC64dis Example
- JC64dis (https://iceteam.itch.io/jc64dis) includes an Ariston example: "Dark Side" by Wally Beben (c) 1988 Incentive
- Source: https://github.com/ice00/jc64
