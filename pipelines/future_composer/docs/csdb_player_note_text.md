---
source_url: https://csdb.dk/getinternalfile.php/573/FutureComposerV4%20+%20Note%20+%20TestTunes.zip → PLAYER NOTE...
fetched_via: direct (D64 extraction + BASIC detokenize)
fetch_date: 2026-06-03
author: The Syndicate (Dynamix)
content_date: 1989
reliability: primary
---

# FC V4 PLAYER NOTE — recovered verbatim text

The `PLAYER NOTE...` PRG on the V4.0 disk is a 336-byte BASIC v2
program. Detokenized verbatim:

```
0 REM note
1 POKE 53280,0:POKE 53281,0:PRINT"{wht}":PRINT"{clr}"
2 LIST 10-
10 TO use the tunes, firstly LOAD the
11 file called 'player $4000 [d]'. THEN
12 LOAD the tune that you would like TO
13 hear. NEXT, enter a machine code
14 monitor (e.g. one like the one on
15 action replay cartridge) AND type:
16 g4000
17 the tune should now play. TO STOP
18 it, hit RUNSTOP/RESTORE.
```

(Capitalisation reflects PETSCII case-conversion. The 'TO',
'LOAD' etc. tokens detokenize as uppercase keywords.)

## What this proves about the V3/V4 player interface

1. **Player and tune are loaded as separate files.** The 80-byte
   player at `$4000` is reusable across tunes; tunes load to their
   own address (V4 tunes load to `$1800` per the player's `JSR $1800`
   call).
2. **No tune metadata in the player — all metadata is in the tune
   file.** Number of subtunes, song lengths, instrument bank: all
   in the tune-side data block. The init routine at load+0 reads
   `A` to pick a subtune.
3. **The user invokes via SYS/monitor `G4000`.** This is the
   reference for what `SYS 16384` does — it runs the init at
   `$4000`, which sets up the IRQ vector at `$0314/0315 = $4034`,
   banks out KERNAL, calls `JSR $1800` (init), and returns to
   BASIC with music playing. Then the IRQ at $4034 fires 50 Hz
   and calls `JSR $1806` (play).
4. **Subtune 0 is hardwired in the standalone player** — the
   wrapper does `LDA #$00; JSR $1800`. Editor-resident playback
   handles multi-subtune; for embedded standalone playback the
   game/demo code provides its own wrapper that picks the
   subtune.

## Note on the V3 disk's "(M)/F.COMP. NOTE"

The Mnemonic Designs V3.0 release ships an equivalent NOTE file
but it's a compiled M/C executable (not BASIC), so its text isn't
extractable without 6502 emulation. The disassembly head looks
like a screen-print + wait-for-key routine — likely just an
on-screen credits/instructions splash.

## Note on "FC INSTRUCTIONS!" (V1/V2/V3/V4 disk)

This is a 20 KB file that is a compiled-BASIC/MC viewer with
encrypted or packed text body (no plaintext PETSCII or screen-code
runs of length > 10 detected in the body). Likely needs a custom
unpacker — the screen routine inside the binary decompresses
text into screen RAM on-the-fly. This is a **lead**: if we can
extract the text, it would be the most comprehensive period
documentation of the FC editor + driver. See `provenance_log.md`.
