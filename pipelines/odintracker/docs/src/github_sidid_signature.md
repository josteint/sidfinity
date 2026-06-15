---
source_url: https://github.com/cadaver/sidid (raw: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg)
fetched_via: curl (raw GitHub)
fetch_date: 2026-06-15
author: Lasse Öörni (Cadaver) / Covert Bitops
content_date: ~2006 (ongoing)
reliability: primary
---

# OdinTracker — SIDId Signature

## From sidid.cfg (cadaver/sidid on GitHub)

```
OdinTracker
29 0F C0 80 F0 ?? C0 90 F0 ?? C0 A0 F0 ?? C0 B0 F0 ?? C0 C0 F0 END
```

## From sidid.nfo (cadaver/sidid)

```
OdinTracker
   AUTHOR: Zoltán Konyha (Zed)
 RELEASED: 2000
REFERENCE: https://csdb.dk/release/?id=12577
```

Note: the CSDb reference in sidid.nfo points to id=12577 (possibly v1.00 or v1.10), 
whereas the latest release (1.13) is at id=2628.

## Signature analysis

The signature `29 0F C0 80 F0 ?? C0 90 F0 ?? C0 A0 F0 ?? C0 B0 F0 ?? C0 C0 F0`
corresponds to 6502 opcodes:

```
AND #$0F         ; 29 0F  — mask effect parameter to low nybble (= bits 3..0)
CMP #$80         ; C0 80  — NOTE: this is actually CPY #$80 (opcode $C0 = CPY imm)
BEQ ??           ; F0 ??  — branch to effect0f80 (set global volume)
CPY #$90         ; C0 90
BEQ ??           ; F0 ??  — branch to effect0f90 (set filter mode)
CPY #$A0         ; C0 A0
BEQ ??           ; F0 ??  — branch to effect0fa0 (fine slide down)
CPY #$B0         ; C0 B0
BEQ ??           ; F0 ??  — branch to effect0fb0 (fine slide up)
CPY #$C0         ; C0 C0
BEQ ??           ; F0     — branch to effect0fc0 (note cut)
```

This is the effect0f dispatch chain in `vplayer.s` / `eplayer.s` lines ~892-912.
The `AND #$0F` (29 0F) masks the low nybble of the effect parameter AFTER the high 
nybble is saved into Y. The sequence is uniquely identifiable across all relocations.

Our local copy of the signature had `C0 0F` as the first two bytes — that was an error.
The correct canonical signature starts `29 0F`.

## Context in vplayer.s (effect0f handler, ~line 892)

```asm
effect0f:
    lda chn_effectpar,x
    bpl effect0fspeed       ; param < $80: set speed
    and #$f0
    tay                     ; Y = high nybble * $10
    lda chn_effectpar,x
    and #$0f                ; A = low nybble   ← 29 0F  ← SIGNATURE STARTS HERE
    cpy #$80                ; C0 80
    beq effect0f80          ; F0 ??
    cpy #$90                ; C0 90
    beq effect0f90          ; F0 ??
    cpy #$a0                ; C0 A0
    beq effect0fa0          ; F0 ??
    cpy #$b0                ; C0 B0
    beq effect0fb0          ; F0 ??
    cpy #$c0                ; C0 C0
    beq effect0fc0          ; F0 ??  ← SIGNATURE ENDS HERE
```

The signature is in the PLAYER code (not data) so it relocates with the player.
sidid must search a range of addresses for this pattern; the player can be placed 
at any page boundary by the packer.
