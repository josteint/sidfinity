---
source_url: local: /home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg
fetched_via: local read
fetch_date: 2026-06-15
author: Unknown (sidid project)
content_date: Unknown
reliability: primary
---

# OdinTracker SIDId Signature Analysis

## Raw signature (local sidid.cfg, line 1477)

```
29 0F C0 80 F0 ?? C0 90 F0 ?? C0 A0 F0 ?? C0 B0 F0 ?? C0 C0 F0 END
```

## Opcode decoding

| Offset | Bytes     | Mnemonic         | Meaning |
|--------|-----------|------------------|---------|
| 0      | 29 0F     | AND #$0F         | Mask low nybble of A (already extracted via `and #$0f` in effect0f) |
| 2      | C0 80     | CPY #$80         | Compare Y against $80 |
| 4      | F0 ??     | BEQ <effect0f80> | Branch if == $80 → set global volume |
| 6      | C0 90     | CPY #$90         | Compare against $90 |
| 8      | F0 ??     | BEQ <effect0f90> | Branch if == $90 → set filter mode |
| 10     | C0 A0     | CPY #$A0         | Compare against $A0 |
| 12     | F0 ??     | BEQ <effect0fa0> | Branch if == $A0 → fine slide down |
| 14     | C0 B0     | CPY #$B0         | Compare against $B0 |
| 16     | F0 ??     | BEQ <effect0fb0> | Branch if == $B0 → fine slide up |
| 18     | C0 C0     | CPY #$C0         | Compare against $C0 |
| 20     | F0 ??     | (BEQ <effect0fc0>) | Branch if == $C0 → note cut |

This is the dispatch chain inside **effect0f** (effect number $0F / "F") of the
relocatable player (vplayer.s). The full dispatch covers $80/$90/$A0/$B0/$C0/$E0/$F0
sub-ranges; the signature only captures the first five comparisons.

## Exact match in source

From `vplayer.s` lines 892–912:

```asm
; Now A is parameter bits 0..3, Y is bits 4..7
        cpy #$80
        beq effect0f80
        cpy #$90
        beq effect0f90
        cpy #$a0
        beq effect0fa0
        cpy #$b0
        beq effect0fb0
        cpy #$c0
        beq effect0fc0
        cpy #$e0
        beq effect0fe0
        cpy #$f0
        beq effect0ff0
```

Preceded by:
```asm
        and #$f0      ; extract high nybble into Y
        tay
        lda chn_effectpar,x
        and #$0f      ; A = low nybble  ← this is the 29 0F in the signature
```

The `29 0F` in the signature is `AND #$0F` (the second `and #$0f` above).

## Version split

**No version split** in either our local sidid.cfg or the GitHub cadaver/sidid repo.
One signature covers all known OdinTracker versions (1.00 and 1.13 both use the
same player structure; file format changed at 1.1x but the player core is the same).

## Implication for detection

The signature uniquely identifies the `effect0f` dispatch section inside the
OdinTracker player. Since the player is relocatable (can be placed at any page
boundary), the absolute address is not part of the signature — only the opcode
sequence. This makes it robust across all relocation targets.
