---
source_url: https://csdb.dk/getinternalfile.php/573/FutureComposerV4%20+%20Note%20+%20TestTunes.zip
fetched_via: direct (downloaded D64, extracted via python-d64, disassembled with py65)
fetch_date: 2026-06-03
author: The Syndicate (Dynamix) — original code
content_date: 1989 (release date), bytes preserved exactly
reliability: primary
---

# FC V4 standalone player — full 6502 disassembly

`PLAYER $4000 [D]` file from the official Dynamix FC V4 release.
80 bytes. Loads at `$4000`. This is the **complete public-facing
template** for embedding an FC V4 (and by extension V3.x — same
init/play interface) song in a standalone program. Use:

> `LOAD "PLAYER $4000 [D]",8,1` → `LOAD "<tune>",8,1` → `SYS 16384`

(Per the disk's "PLAYER NOTE..." instructions, recovered verbatim
from the same D64.)

## Disassembly (verbatim, from py65 against the file bytes)

```
$4000  SEI                  ; disable IRQ
$4001  LDX #$01
$4003  STX $D01A            ; enable raster IRQ
$4006  DEX                  ; X=0
$4007  STX $D020            ; border = black
$400A  STX $D021            ; background = black
$400D  STX $DC0E            ; stop CIA1 timer A (kill KERNAL IRQ)
$4010  LDA #$1B
$4012  STA $D011            ; screen on, 25-row, default
$4015  LDA #$33
$4017  STA $D012            ; raster line $33 = top of screen
$401A  LDA #$34
$401C  STA $0314            ; new IRQ vector lo
$401F  LDA #$40
$4021  STA $0315            ; new IRQ vector hi → $4034
$4024  NOP
$4025  LDA #$35
$4027  STA $01              ; bank out KERNAL ROM (I/O still in)
$4029  LDA #$00
$402B  JSR $1800            ; *** init song 0 ***
$402E  LDA #$37
$4030  STA $01              ; bank KERNAL back in
$4032  CLI
$4033  RTS                  ; return to BASIC, song now playing under IRQ

; --- IRQ handler at $4034 ---
$4034  INC $D020            ; flash border (raster-time visible)
$4037  LDA #$35
$4039  STA $01              ; bank out KERNAL
$403B  JSR $1806            ; *** play frame ***
$403E  LDA #$37
$4040  STA $01              ; bank KERNAL back
$4042  DEC $D020            ; restore border
$4045  LDA #$01
$4047  STA $D019            ; ack raster IRQ
$404A  JMP $EA31            ; chain to KERNAL IRQ
```

## Hard facts this disassembly nails down

1. **Init entry = `$1800` (load_addr + 0).**
2. **Play entry = `$1806` (load_addr + 6).** This is the
   `+6` offset for **FC V4 standalone-player output**.
   (NB: FC V3.x output — including Hawkeye.sid — uses +3 instead.
   See `csdb_hawkeye_provenance.md` for the disassembled trampoline
   table at $7AE0/$7AE3 in the real Hawkeye SID. V3.x has
   3-byte JMP trampolines at +0/+3, while V4 inlines the entry
   bytes from +0 to +5 and starts play at +6.)
3. **Init takes the subtune number in `A`.** `LDA #$00; JSR $1800`
   plays the first subtune; pass other values for multi-subtune
   SIDs.
4. **Driver expects KERNAL banked out during both init and play**
   (`$35` on `$01`). This means the driver itself can use
   `$E000-$FFFF` RAM if it wants — important for relocators.
   It does *not* mean PSID files have to disable KERNAL — PSID's
   built-in dispatcher already does, so the FC V3/V4 PSIDs in
   HVSC do not include any `STA $01` writes.
5. **Required IRQ rate = 50 Hz (raster IRQ on a single line at
   $33)**, i.e. the standard PAL VBI rate. No tempo-based
   re-arming — the song's tempo is internal.
6. **No init parameter beyond subtune number.** The driver
   doesn't take a load address argument; it uses absolute
   addressing baked in at relocation time (hence the existence
   of "Future Composer Re-Locator v1.3+").

## Implication for our PSID rebuild

A V3.x PSID's header should declare:

```
load    = $1800   (or wherever the song was relocated to)
init    = load + 0
play    = load + 6
songs   = N
speed   = $00000000   (vertical-blank-synced)
```

For Hawkeye specifically (HVSC: load $7AE0, init $7AE0, play $7AE3),
the +3 offset reflects the V3.x **two-JMP trampoline layout**
(`JMP init_code` at +0, `JMP play_code` at +3). Disassembled
confirmation in `csdb_hawkeye_provenance.md`. The byte-exact
rebuild path needs to emit these two trampoline JMPs as the
first 6 bytes, then the real init/play code can live anywhere.
