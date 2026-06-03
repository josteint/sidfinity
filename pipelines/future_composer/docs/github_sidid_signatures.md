---
source_url: https://github.com/cadaver/sidid (mirror at https://github.com/WilfredC64/player-id)
fetched_via: git clone
fetch_date: 2026-06-03
author: Cadaver / WilfredC64
content_date: actively maintained signature database
reliability: primary
---

# sidid / player-id — FC and MoN-family detection signatures

Both `cadaver/sidid` and `WilfredC64/player-id` (the modern Rust rewrite)
ship a `sidid.cfg` with byte-level signatures used to identify which
player drives a given SID. The FC and MoN-family entries are the exact
6502 byte sequences that detect FC1.0 / FC3.x / FC4_Packed / Cybernoid II
/ The Last V8 II / James Bond / RWE / Bantam / Deenen_Digi variants.

These signatures are the **anchor we can use to locate the player
runtime inside any candidate PSID** — the byte pattern tells us where
to start disassembling.

## FC and MoN-family signatures (verbatim from sidid.cfg)

```
MoN/FutureComposer
FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 03
8D 17 D4 A0 06 88 88 88 88 88 88 B1 F9 END

(FutureComposer_V1.0)
EE ?? ?? EE ?? ?? AD ?? ?? C9 32 D0 05 A9 01 8D ?? ?? 60 END

(FC_V4_Packed)
EE 99 ?? EE 9A ?? EE 9B ?? A9 END

(FC_V3.x)
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? C9 40 90 0B 29 3F 9D END

(MoN/Cyb2)
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? 29 3F 9D ?? ?? FE ?? ?? 4C END

(MoN/TTWII)        ; The Last V8 II
BC ?? ?? BE ?? ?? 8E ?? ?? A5 ?? 29 0F 85 27 A5 ?? 29 70 4A 4A 4A 4A A6 ?? 95 ?? A0 BC A5 ?? 10 02 A0 7D 8C ?? ?? BC ?? ?? B9 ?? ?? 38 F9 END

(MoN/JTS)
A9 ?? 9D ?? ?? 9D ?? ?? 9D ?? ?? 4C ?? ?? 8D ?? ?? 29 80 F0 0E AD ?? ?? 29 1F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? 29 40 F0 0E AD ?? ?? 29 3F 9D END

(MoN/RWE)
B0 05 BD ?? ?? D0 05 BD ?? ?? 29 FE 9D ?? ?? BD ?? ?? D0 0A AD ?? ?? C9 ?? D0 03 99 06 D4 BD END

(MoN/Bantam)
0A 0A 0A AA 8E ?? ?? BD ?? ?? A6 FF 9D ?? ?? 99 04 D4 A9 00 99 02 D4 A6 FF 9D END

(MoN/Deenen_Digi)
A2 00 F0 ?? 98 0A A8 B9 ?? ?? 8D ?? ?? B9 ?? ?? 8D END
4A 4A 4A B8 50 ?? 4A 4A 4A 18 69 ?? 8D 18 D4 END
```

## What the FC_V3.x signature actually decodes to

`EE 99 ?? EE 9A ?? EE 9B ?? A9` =

```asm
INC $99xx    ; ee 99 xx  — three consecutive INC absolute on $xx99 / $xx9A / $xx9B
INC $9Axx    ; ee 9A xx  — these are the THREE PER-VOICE PATTERN POINTER COUNTERS
INC $9Bxx    ; ee 9B xx  — incremented at frame start (advancing all voices)
LDA #...     ; a9 ..
```

This confirms FC V3.x keeps **three single-byte counters at consecutive
addresses** for per-voice sequence stepping (matching the
`tabcount,x` array we see in the Cybernoid II disassembly:
`tabcount !by $00,$00,$00`).

## What the (default top-level) FC signature decodes to

`FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 03` =

```asm
INC $xxxx,X       ; FE ?? ??     — increment per-voice byte
LDY $xxxx,X       ; BC ?? ??     — load pattern offset
LDA ($xx),Y       ; B1 ??        — fetch pattern byte (indirect indexed)
CMP #$FF          ; C9 FF        — end-of-pattern check
BNE +             ; D0 ??        — branch on end
LDA #$00          ; A9 00
STA $xxxx,X       ; 9D ?? ??     — reset per-voice byte
LDA $xxxx,X       ; BD ?? ??     — load repeat counter
BEQ +5            ; F0 05
DEC $xxxx,X       ; DE ?? ??     — repeat counter--
BPL +3            ; 10 03
```

This matches the **pattern advance / `$FF`-end / repeat-counter logic**
verbatim from the Cybernoid II disassembly's `nextjmp:` block:
```asm
nextjmp:  lda #0
          sta begcount,x
          lda repeatsto,x
          beq nj1
          dec repeatsto,x
          bpl h10b
nj1:      inc tabcount,x
```

## What the FC1.0 signature decodes to

`EE ?? ?? EE ?? ?? AD ?? ?? C9 32 D0 05 A9 01 8D ?? ?? 60` =

```asm
INC $xxxx
INC $xxxx
LDA $xxxx
CMP #$32       ; CMP #50  -- frame counter wraps at 50 (PAL Hz boundary)
BNE +5
LDA #$01
STA $xxxx
RTS
```

A 50-Hz frame divisor — FC1.0 has a separate 1-Hz tick (probably for
fade/master-vol timing). Useful detail: **#$32 = 50** is the magic.

## Practical use

For Hawkeye.sid (or any FC V3.x candidate):

1. Load the PSID, locate the `EE 99 ?? EE 9A ?? EE 9B ?? A9` byte
   pattern inside the player-code region (offset between init and play
   entry points + relocation).
2. The three operand bytes (the `??` between EE 99/9A/9B and the following
   instructions) are pointers to the **per-voice tabcount array**.
3. From there, walk back to find the sequence-table base (the `LDA
   (zp3),Y` pattern fetch) and forward to find the instrument bank
   (the `LDA $XXXX,Y` reads of pulsehi/waveform/attdec/susrel/filcount/
   fx1/fx2/fx3, 8-byte stride).

Both repos are MIT/BSD-licensed (cadaver) / Apache (player-id), so the
signature data is freely reusable.
