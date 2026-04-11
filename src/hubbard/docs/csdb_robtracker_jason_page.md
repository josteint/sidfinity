---
source_url: multiple
# https://csdb.dk/release/?id=43956
# https://c64.xentax.com/index.php/16-sid-digi-play-routines
fetched_via: compiled from multiple sources
fetch_date: 2026-04-11
author: unknown (compiled from sidid.nfo, CSDb, and XeNTaX analysis)
content_date: 1988-2020
reliability: secondary
---
# Jason Page / RobTracker — Technical Details

## What Is RobTracker?

RobTracker is a C64 music player created by Jason Page (handle: "Jay") that is based on
Rob Hubbard's digital sample playback (digi) routine. It is identified as a distinct player
by the SIDID/player-id tools under the name `Jason_Page/RobTracker`.

## SIDID Identification

### sidid.nfo entry:
```
Jason_Page/RobTracker
   AUTHOR: Jason Page
  COMMENT: Based on Rob Hubbard's Digi routine.
```

### sidid.cfg signature:
```
85 ?? BC ?? ?? B1 ?? C9 FF F0 13 C9 FD D0 1D C8 B1 ?? 9D ?? ?? FE ?? ?? FE ?? ?? 4C ?? ?? A9 00 END
```

This signature shows:
- `85 ??` — STA to zero page (store accumulator)
- `BC ?? ?? B1 ??` — LDY abs,X then LDA (zp),Y (indirect indexed load from data pointer)
- `C9 FF F0 13` — CMP #$FF; BEQ +$13 (check for end-of-data marker)
- `C9 FD D0 1D` — CMP #$FD; BNE +$1D (check for special command $FD)
- `C8 B1 ??` — INY; LDA (zp),Y (read next data byte)
- `9D ?? ?? FE ?? ?? FE ?? ??` — STA abs,X; INC abs,X; INC abs,X (store and advance pointers)
- `4C ?? ??` — JMP (jump to continue processing)
- `A9 00` — LDA #$00 (clear accumulator)

## How It Differs from the Standard Hubbard Player

1. **Digi playback focus:** RobTracker is specifically built around Hubbard's 4-bit unsigned
   PCM sample playback technique (writing to $D418 volume register).

2. **Different sequencer:** The signature shows a different pattern fetch/sequencing approach
   compared to the standard Hubbard player. Uses $FF for end-of-data and $FD as a special
   command byte, whereas the standard Hubbard player uses $FF for end-of-pattern and $FE for
   end-of-track.

3. **Not a direct fork:** While "based on" the Hubbard digi routine, it appears to be Jason
   Page's own reimplementation with a different sequencer architecture. The SIDID system
   identifies it as a separate player type.

## Jason Page's Other Player: "Jay's Music Routine"

### sidid.nfo entry:
```
Jason_Page/Jay
     NAME: Jays Music Routine
   AUTHOR: Jason Page (Jay)
 RELEASED: 1988
REFERENCE: https://csdb.dk/release/?id=43956
```

### sidid.cfg signature:
```
9D 62 C0 BD 68 C0 0A 0A 0A 0A 8D 73 C2 A9 00 69 00 END
```

This is a completely separate player — Jay's own music routine from 1988. It uses hardcoded
addresses ($C062, $C068, $C273) and the `0A 0A 0A 0A` (ASL A x4, i.e., multiply by 16)
suggests 16-byte instrument records.

### CSDb release:
- **URL:** https://csdb.dk/release/?id=43956
- **Name:** Jay's Music Routine V1
- **Type:** C64 Tool (music editor)
- **Year:** 1988

## Detection in HVSC

From local HVSC scan of the Hubbard_Rob/ directory:
- 82/96 songs detect as `Rob_Hubbard` (standard player)
- 5/96 detect as `Jason_Page/RobTracker`
- 4/96 detect as `SidTracker64` (modern recreations)
- 2/96 detect as `Companion` (early non-Hubbard-driver works)
- 3/96 detect as other engines

The 5 songs detected as `Jason_Page/RobTracker` in the Hubbard_Rob/ HVSC directory are
likely songs that use Hubbard's later digi-capable driver variant, which has enough code
similarity with Page's RobTracker to trigger the Page signature instead. This is a
signature overlap issue, not proof that Page wrote those songs.

## Jason Page's Background

- UK-based, started as trainee programmer at Graftgold at age 16
- C64 game credits: Orion (1988), Bushido (1989)
- Used Sound Monitor, Rock Monitor, a Maniacs of Noise rip-off, Steve Turner's routine
  (at Graftgold), and his own custom routines — NOT Hubbard's standard player
- Cited Hubbard as primary musical inspiration but developed independent player technology
- Created an unreleased GoatTracker-to-Hubbard converter as a personal project
- Later active in the MultiStyle Labs group (2020+), creating GoatTracker tools and SID remakes

## Relevance to Decompiler

For building a Hubbard decompiler, the key insight is that `Jason_Page/RobTracker` detection
on a Hubbard_Rob SID file means the file uses the **digi variant** of Hubbard's player,
not that it uses a completely different format. The core data structures (instruments, patterns,
tracks) should be similar to the standard Hubbard format with added digi sample playback
tables.

The `Rob_Hubbard_Digi` sub-signature in sidid.cfg specifically covers this:
```
4C ?? ?? 28 F0 AND 4A 4A 4A 4A 4C ?? ?? 29 0F EE ?? ?? D0 03 EE AND 8D 18 D4 AD 0D DD END
```
This detects the actual digi IRQ handler: PLP, BEQ, LSR x4 (high nybble), AND #$0F (low nybble),
write to $D418 (volume), acknowledge CIA IRQ at $DD0D.

## Digi Routine Cycle Timing (from XeNTaX analysis)

Source: https://c64.xentax.com/index.php/16-sid-digi-play-routines

The 4-bit $D418 routine (BMX Kidz 1987 variant, 55 bytes) has variable cycle counts:
- Maximum: 67 cycles (low nibble path + high byte address increment)
- Low nibble path: 63 cycles
- High nibble path: 52 cycles
- Average: ~57.5 cycles

On PAL (1 cycle = ~1.015 microseconds), maximum theoretical sample rate is ~14,705 Hz.

Implementation details:
- Toggle flag (e.g., at $FC) tracks high vs. low nibble: `AND #$01` extracts the bit
- Low nibble path shifts left 4 times before writing to $D418 (to place in high nibble
  for the volume register)
- End-of-sample detected by checking if loaded byte equals $1F
- Timer A stopped by writing 0 to $DD0E when sample ends
