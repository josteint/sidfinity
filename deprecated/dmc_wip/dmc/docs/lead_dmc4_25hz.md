---
source_url: https://csdb.dk/release/?id=193910, https://demozoo.org/productions/281491/
fetched_via: direct
fetch_date: 2026-04-11
author: Jason Page (patch author); CSDb/Demozoo release metadata; disassembly of DMC_JP1.d64 and Computerized SID by researcher
content_date: 2020-07-26
reliability: primary
---

# DMC 4 25Hz Variant — Research Notes

## Overview

**DMC 4 25Hz** is a patched version of Demo Music Creator 4.0 (by Brian/Graffity, 1991),
modified by **Jason Page / MultiStyle Labs** and released on 26 July 2020.

- **CSDb release:** https://csdb.dk/release/?id=193910
- **Demozoo release:** https://demozoo.org/productions/281491/
- **Downloads:** `DMC_JP1.d64` (C64 disk image), `SID25Hz.exe` (PC companion tool)
- **Event:** 25Hz Music Compo 2020 (1 July – 2 August 2020, MultiStyle Labs)
- **Jason Page credit:** "Crack" (CSDb) / "Code (patch)" (Demozoo)
- **CSDb rating:** 10/10 from 8 votes — received with immediate enthusiasm

---

## The 25Hz Music Compo 2020

Organised by **booker** and **Jammer** of MultiStyle Labs. Alternate title: "Half-Speed Music Compo."

The tagline was *"25Hz Should Be Enough for Everyone!"*

Constraint: All entries had to use **25Hz playback rate** — the SID registers are updated
only 25 times per second instead of the standard 50Hz PAL. This frees up CPU time
(the player runs half as often) and forces composers to work with slower timing resolution.

The competition had **25 entries**. MultiStyle Labs dominated with ~11 submissions.
Notable placing: *Computerized* by psych858o/MultiStyle Labs placed **2nd** and
explicitly credits Jason Page's DMC 4 25Hz patch code.

Forum discussion at: https://csdb.dk/forums/?roomid=12&topicid=143469

---

## How 25Hz Was Achieved: Two Separate Mechanisms

The modification works differently in the **editor** versus the **exported player SID**.

### 1. In the DMC 4 25Hz Editor (DMC_JP1.d64)

The editor is a full C64 program (PRG format, loads at `$0801`, 23698 bytes binary,
end address `$6492`). During composition preview, it uses **CIA1 Timer A** to drive
the music interrupt.

**CIA timer init sequence** (at `$0D50`, called from startup at `$08C7`):

```asm
; Wait for VBI sync
BIT $D011   ; VIC_CTRL1
BPL $0D53   ; spin until raster in lower half

; Load timer values from zero-page and write to CIA registers
; CIA2 Timer A (RS-232, used for something else here)
LDX #$00
LDY #$01
LDA $33     ; ZP$33 = CIA2 TA lo
STA $DD04   ; CIA2_TA_LO
STY $DD0E   ; CIA2_CRA = $01 (start timer, continuous mode)
LDA $34     ; ZP$34 = CIA2 TA hi
STA $DD05   ; CIA2_TA_HI
STX $DD0E   ; CIA2_CRA = $00 (stop/latch)

; CIA2 Timer B
LDA $35     ; ZP$35 = CIA2 TB lo
STA $DD06
LDA $36     ; ZP$36 = CIA2 TB hi
STY $DD0F   ; CIA2_CRB = $01
STA $DD07
STX $DD0F

; CIA1 Timer A (keyboard/IRQ)
LDA $37     ; ZP$37 = CIA1 TA lo
STA $DC04   ; CIA1_TA_LO
STY $DC0E   ; CIA1_CRA = $01 (start, continuous)
LDA $38     ; ZP$38 = CIA1 TA hi
STA $DC05   ; CIA1_TA_HI
STX $DC0E   ; CIA1_CRA = $00

; CIA1 Timer B
LDA $39     ; ZP$39 = CIA1 TB lo
STA $DC06
LDA $3A     ; ZP$3A = CIA1 TB hi
STY $DC0F
STA $DC07
STX $DC0F

; Enable CIA1 IRQ for timer A
LDA $DC0D   ; clear ICR
LDA $DD0D
LDA $30     ; ICR mask value ($81 = enable Timer A)
STA $DD0D
LDA $2D
STA $DC0D
RTS
```

The critical values come from zero-page `$37/$38` (CIA1 Timer A Lo/Hi):

| Mode       | Clock       | Timer value | Actual Hz |
|------------|-------------|-------------|-----------|
| PAL 50Hz   | 985,248 Hz  | `$4CF8` (19704 cycles) | 50.002 Hz |
| PAL 25Hz   | 985,248 Hz  | `$99F0` (39408 cycles) | 25.001 Hz |
| NTSC 50Hz  | 1,022,727 Hz| `$4FE6` (20454 cycles) | 50.003 Hz |
| NTSC 25Hz  | 1,022,727 Hz| `$9FCC` (40908 cycles) | 25.001 Hz |

**The 25Hz modification is exactly: double the CIA timer period (half the frequency).**
`$4CF8 × 2 = $99F0` — a clean binary relationship.

The zero-page timer values come from a config block at `$0241–$0279` in low RAM
(copied from there to ZP `$02–$3A` at startup via `LDX #$38; LDA $0241,X; STA $02,X`).
This block is pre-initialised by the disk image content before the main code runs.

### 2. In the Exported SID Player

The competition entries are exported as `.sid` files. Examined: *Computerized* by
psych858o (CSDb release 193912, download id 239671), PSID v2, 4629 bytes.

**Key fact: the exported SID does NOT use CIA timer.**

```
Speed flag = $00000000  →  VBI interrupt (50Hz)
Init addr  = $1000
Play addr  = $1003
```

There are **no CIA register writes** in the SID binary. Instead, the exported player
implements 25Hz using a **frame-skip wrapper**:

```asm
; PLAY routine @ $2206  (called by SID player harness every VBI = 50Hz)
$2206:  LDA $2214       ; load frame counter (1 byte, initialized to 0)
$2209:  AND #$01        ; test bit 0 (even or odd frame)
$220B:  BNE $2213       ; if odd: skip this frame (do nothing)
$220D:  JSR $194A       ; if even: call music update
$2210:  INC $2214       ; increment frame counter
$2213:  RTS
$2214:  .byte $00       ; frame counter
```

**This is the heart of the DMC 4 25Hz mechanism in the player:**

- The outer harness calls `PLAY` every VBI (50 times/second, PAL)
- The `AND #$01 / BNE skip` pattern skips every other call
- Result: music update rate = 50Hz ÷ 2 = **25Hz**
- Duration ticks now span 2 VBI frames (40ms each) instead of 1 (20ms each)
- This is why the 25Hz format gives a "slower" feel and lower timing resolution

---

## Core DMC 4 Player Architecture

The music player itself (below the 25Hz wrapper) is standard DMC 4:

```
Entry points (jump table at $1000):
  $1000: JMP $1947   (INIT)
  $1003: JMP $2206   (PLAY → 25Hz wrapper → $194A → $1086)
  $1006: JMP $1937   (unknown, second entry)

Core player loop ($1086):
  DEC $1719          ; decrement duration tick counter
  BPL $1091+         ; if still positive, skip to output section
  LDA $1717          ; reload tempo (default value = 1)
  STA $1719          ; reset tick counter
  LDX #$00
  STX $1721          ; clear something
  JSR $10B1          ; process channel 0
  INX
  JSR $10B1          ; process channel 1
  INX
  JSR $10B1          ; process channel 2
  ; write filter registers
  LDA $171D
  STA $D416
  LDA $1019
  ...
  STA $D417
  RTS
```

**Per-channel processing ($10B1):**
- Reads sector pointer from `$1708+X` (lo) / `$170B+X` (hi) per channel (X=0,1,2)
- Reads bytes sequentially from sector data
- Handles: notes (`$00–$5F`), durations (`$60–$7C`), gate-off (`$7E`), end (`$FE`)
- Duration value = byte AND `$1F` = 1..29 ticks (now 1 tick = 2 frames = 40ms at 25Hz)
- Instruments change via `$80–$9F` bytes
- Glide via `$A0–$BF`
- Loop via `$FF` (end sector, jump back via `$21AC/21D9` pointer tables)

**Memory map (Computerized SID at $1000):**
```
$1000–$1005  Jump table (init/play/play2)
$100D–$100F  Per-channel active/gate flags (3 bytes)
$1086        Core player loop
$10B1        Per-channel sector reader
$1708–$170D  Channel 0/1/2 sector pointer lo/hi (6 bytes)
$1717        Tempo reload value (default 1 = update every tick)
$1719        Duration tick counter
$171D–$171E  Filter cutoff/resonance staging
$173C–$173E  Per-channel loop/wrap flags
$1947        INIT entry (→ $1808)
$194A        Music update entry (→ $1086)
$2206–$2214  25Hz frame-skip wrapper + counter byte
$21AC        Sector hi-byte pointer table (32 entries)
$21D9        Sector lo-byte pointer table (32 entries)
```

---

## What the 25Hz Modification Reveals About DMC Internals

### Timing chain

```
[C64 hardware VBI, 50Hz PAL]
        ↓
[SID player harness calls PLAY addr every VBI]
        ↓
[25Hz wrapper: skip every 2nd frame]
        ↓  (every 2nd VBI = 25Hz)
[Core player: DEC tick counter]
        ↓  (when counter = 0)
[Advance sector pointer, read next event]
```

The "tempo" value in DMC is the initial tick count — how many player calls pass
between music events. At 25Hz:
- Tempo 1 = 1 tick × 40ms = 40ms per event
- Tempo 2 = 2 ticks × 40ms = 80ms per event

At standard 50Hz:
- Tempo 1 = 1 tick × 20ms = 20ms per event
- Tempo 2 = 2 ticks × 20ms = 40ms per event

So composing at 25Hz with tempo 1 sounds identical to composing at 50Hz with tempo 2 —
but gives the composer single-tick resolution at the slower rate, which was the artistic
constraint of the competition.

### The 25Hz frame-skip is in the EXPORTED player, not just the editor

This is the critical insight: the exported SID player ALSO skips every other frame.
The DMC 4 25Hz export function generates the 7-byte frame-skip wrapper around the
standard DMC player and embeds it at the tail of the binary. This wrapper is transparent
to the SID file format (speed flag stays 0 = VBI) but halves the effective update rate.

### PAL/NTSC handling in the editor

The editor binary at `$0D50` waits for the raster counter to be in a specific position
before writing CIA timer values, ensuring synchronisation. The timer values themselves
are stored in a config block copied to zero-page. The editor appears to auto-detect
PAL vs NTSC (the startup code does raster timing measurements, as is standard for
C64 PAL/NTSC detection) and would use the appropriate 25Hz CIA value for each.

---

## Implications for DMC Parser / Converter

When parsing DMC 25Hz SID files (from HVSC or competition downloads):

1. **Detection:** Look for the 7-byte frame-skip wrapper at the start of the play
   routine: `AD xx xx 29 01 D0 03 20 xx xx EE xx xx 60`

2. **Speed flag:** DMC 25Hz SIDs have speed flag = 0 (VBI), NOT CIA timer.
   The 25Hz behaviour is entirely self-contained in the player code.

3. **Duration interpretation:** If a 25Hz player is detected, all duration ticks
   represent 40ms (2 × 20ms VBI frames) instead of the standard 20ms.
   Internally in DMC the durations are the same bytes (`$60–$7C`, AND `$1F`);
   the 25Hz modifier doubles the wall-clock time per tick.

4. **Compatibility:** The sector data format is identical to standard DMC 4.
   Only the play wrapper changes. The `dmc_parser.py` sector decoder works
   unchanged; just adjust timing interpretation.

5. **Frame-skip counter:** Located immediately after the `RTS` of the wrapper,
   initialised to 0 by INIT. It wraps: 0→1→0→1... (bit 0 toggles).

---

## Source Files

- Editor disk image: `/home/jtr/sidfinity/src/dmc/downloads/DMC_JP1.d64` (or downloaded to `/tmp/dmc_25hz.prg`)
- Example competition SID: `Computerized` by psych858o — downloaded to `/tmp/computerized2.prg`
- CSDb event page: https://csdb.dk/event/?id=2967
- CSDb forum thread: https://csdb.dk/forums/?roomid=12&topicid=143469
- DMC 4 25Hz release: https://csdb.dk/release/?id=193910
- Computerized release: https://csdb.dk/release/?id=193912
- Demozoo 25Hz compo: https://demozoo.org/parties/4089/
- Jason Page profile: https://csdb.dk/scener/?id=4121

---

## Related HVSC Files

The HVSC collection contains GoatTracker-based 25Hz songs (NOT DMC):
```
MUSICIANS/H/Hairdog/Ducks_25Hz.sid          GoatTracker_V2.x, speed=$1, CIA $998F=25.06Hz
MUSICIANS/T/Tognon_Stefano/Infernal_25Hz.sid JITT64_1.x
MUSICIANS/C/Crowley_Owen/End_Theme_25Hz.sid  GoatTracker_V2.x
MUSICIANS/C/Crowley_Owen/Worktunes/25Hz.sid  GoatTracker_V2.x
MUSICIANS/C/Crowley_Owen/Worktunes/25Hz_II.sid GoatTracker_V2.x
```

These use **CIA timer** (speed flag bit 0 = 1), not the frame-skip technique.
The GoatTracker 25Hz (Multispeed 0) exports with CIA timer value `$998F` = 39311 cycles
= 25.063 Hz (slightly off from exact 25Hz). These are a different player family
from DMC 4 25Hz and are irrelevant to the DMC pipeline.

The DMC 4 25Hz competition SIDs (Computerized, Les Cathedrales, etc.) are NOT yet
in HVSC and would need to be sourced from CSDb directly.
