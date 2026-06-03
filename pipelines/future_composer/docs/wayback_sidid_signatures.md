---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: github raw 2026-06-03
fetch_date: 2026-06-03
author: Cadaver et al. (sidid maintainers)
content_date: ongoing (most recent commit)
reliability: primary
---

# sidid signatures for FutureComposer family (cadaver/sidid)

The de facto byte-pattern fingerprints for FC + MoN drivers. Each line
starts at a fixed point inside the player code; `??` accepts any byte.
The "named" sub-variants (`FutureComposer_V1.0`, `FC_V3.x`,
`FC_V4_Packed`) refine the parent `MoN/FutureComposer` match.

## MoN/FutureComposer (generic — matches V2 + V3 + V4 base driver)

```
FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 03 END
8D 17 D4 A0 06 88 88 88 88 88 88 B1 F9 END
```

Decoded (instruction-stream view):

```
INC abs,x      ; FE ?? ??  — bump a per-voice counter
LDY abs,x      ; BC ?? ??
LDA (zp),y     ; B1 ??     — fetch byte from pattern
CMP #$FF       ; C9 FF
BNE *+5        ; D0 ??     — $FF = pattern end
LDA #$00
STA abs,x      ; 9D ?? ??
LDA abs,x      ; BD ?? ??
BEQ *+7        ; F0 05
DEC abs,x      ; DE ?? ??
BPL *+5        ; 10 03
```

Second signature `8D 17 D4 A0 06 88×6 B1 F9` is the **distinctive
resfilt+wait + 6-step countdown** Hubbard wrote — STA $D417 (resfilt
register), LDY #$06, DEY×6 (a 12-cycle hand-rolled delay), then LDA
(zp),Y from a pattern pointer in $F9/$FA.

## FutureComposer_V1.0

```
EE ?? ?? EE ?? ?? AD ?? ?? C9 32 D0 05 A9 01 8D ?? ?? 60 END
```

Decoded:

```
INC abs        ; EE ?? ??
INC abs        ; EE ?? ??
LDA abs        ; AD ?? ??
CMP #$32       ; C9 32      — compare counter against 50 (1 second @ 50 Hz)
BNE *+7        ; D0 05
LDA #$01
STA abs        ; 8D ?? ??   — set "1-second tick" flag
RTS
```

V1 has a simple 50-tick second counter the later versions dropped.

## FC_V3.x

```
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? C9 40 90 0B 29 3F 9D
```

Decoded:

```
JMP abs        ; 4C ?? ??
LDA abs        ; AD ?? ??
CMP #$60       ; C9 60      — pattern-byte ≥ $60? handle one way
BCC *+13       ; 90 0B
AND #$0F       ; 29 0F      — keep low nibble (4-bit param)
STA abs,x      ; 9D ?? ??
INC abs,x      ; FE ?? ??
JMP abs        ; 4C ?? ??
LDA abs        ; AD ?? ??
CMP #$40       ; C9 40      — second discrimination at $40
BCC *+13       ; 90 0B
AND #$3F       ; 29 3F      — keep 6-bit param
STA abs,x      ; 9D ?? ??
```

This is the **V3 pattern-byte dispatcher**: nested
`CMP #$60 / CMP #$40` to split the byte-space into command-vs-note.
The same shape as MoN/Cyb2 (Cybernoid 2). Confirms Hawkeye driver
is essentially the Cybernoid 2 driver with cosmetic edits — both
released by MoN/Deenen in 1988.

## FC_V4_Packed

```
EE 99 ?? EE 9A ?? EE 9B ?? A9
```

Three sequential `INC abs` against $??99/$??9A/$??9B — a 24-bit
counter inside a "packed-data" decompressor. Confirms FC V4
introduces a compressed song format.

## Sibling MoN drivers (same family)

```
MoN/Deenen     C9 60 B0 03 4C ?? ?? C9 FF D0 ?? A9 00 END    ; dispatcher
               B9 ?? ?? F9 ?? ?? 9D ?? ?? BD ?? ?? 4A 4A 4A 4A A8 88 30 ?? END
               BD ?? ?? DD ?? ?? D0 ?? A9 FE 9D ?? ?? DE ?? ?? F0 ?? BD ?? ?? C9 FF F0 END

MoN/Cyb2       4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? 29 3F 9D ?? ?? FE ?? ?? 4C END
MoN/Bjerregaard A9 00 ?? ?? ?? 8D ?? D4 8D ?? D4 8D ?? ?? 60 AND 29 7F 38 E9 40 END
MoN/TTWII      BC ?? ?? BE ?? ?? 8E ?? ?? A5 ?? 29 0F 85 27 A5 ?? 29 70 4A 4A 4A 4A A6 ?? 95 ?? A0 BC ...
MoN/JTS        A9 ?? 9D ?? ?? 9D ?? ?? 9D ?? ?? 4C ?? ?? 8D ?? ?? 29 80 F0 0E AD ?? ?? 29 1F 9D ?? ?? FE ?? ?? 4C ...
MoN/RWE        AD ?? ?? 29 40 F0 0E AD ?? ?? 29 3F 9D ?? ?? FE ?? ?? 4C ...
MoN/Bantam     B0 05 BD ?? ?? D0 05 BD ?? ?? 29 FE 9D ?? ?? BD ?? ?? D0 0A AD ?? ?? C9 ?? D0 03 99 06 D4 BD ...
MoN/Deenen_Digi 0A 0A 0A AA 8E ?? ?? BD ?? ?? A6 FF 9D ?? ?? 99 04 D4 A9 00 99 02 D4 A6 FF 9D ...
               A2 00 F0 ?? 98 0A A8 B9 ?? ?? 8D ?? ?? B9 ?? ?? 8D ...
               4A 4A 4A B8 50 ?? 4A 4A 4A 18 69 ?? 8D 18 D4 END
```

`MoN/Cyb2` and `FC_V3.x` share the **identical** `4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ??` opening, only diverging on the second `CMP` value (`#$40` vs nothing). Strong evidence: Hawkeye / FC V3 driver was forked directly off the Cybernoid 2 driver.

## Takeaway for the rebuild

- Hawkeye should match **FC_V3.x** (or possibly the bare
  `MoN/FutureComposer` if sidid sees just the V1 fragment too).
- The `4C ?? ?? AD ?? ?? C9 60 / C9 40` byte-range dispatcher is the
  pattern-stream interpreter. **Pattern-byte semantics: ranges
  $00-$3F = ?, $40-$5F = command class A, $60-$BF = command class B,
  $C0-$DF = ?, $E0-$EF = ?, $F0-$FF = control / end** (exact ranges
  TBD; see Cybernoid 2 disassembly which uses precisely the same
  dispatcher and is fully annotated — see `wayback_cybernoid2_driver.md`).

## Provenance log entry

`https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg`
— direct fetch from GitHub raw, no Wayback needed. The same signature
block exists in `WilfredC64/player-id` at `config/sidid.cfg` (1:1
identical for the FC block, with `&&` in place of `AND` for the
generic MoN/FutureComposer second signature — same semantic).
