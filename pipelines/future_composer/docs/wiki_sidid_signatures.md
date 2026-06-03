---
source_url: https://github.com/cadaver/sidid/blob/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-03
author: Lasse Öörni (Cadaver)
content_date: 2024 (file last updated)
reliability: primary
---

# sidid signatures for Future Composer (cadaver/sidid)

These are the live byte-pattern signatures `sidid` uses to classify
HVSC SIDs. **Critical for byte-exact rebuild work**: any rebuilt SID
must match one of these patterns to be classified the same as the
HVSC original.

## MoN/FutureComposer (generic — V1/V2 era)

```
FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 03
8D 17 D4 A0 06 88 88 88 88 88 88 B1 F9
```

Decoded:
- `INC abs ; INC abs` — global counter increment
- `LDY abs,X / LDA (zp),Y` — pattern data fetch
- `CMP #$FF` — end-of-pattern test
- `BNE ...` — branch
- `LDA #$00 / STA abs,X` — clear voice state
- `LDA abs,X / BEQ +5 / DEC abs,X / BPL +3` — duration countdown
- `STA $D417` — filter resonance/voice routing register write
- `LDY #$06 / DEY×6 / LDA (zp),Y` — backwards table walk (the +6 offset
  literal!)

## FC_V1.0 specific

```
EE ?? ?? EE ?? ?? AD ?? ?? C9 32 D0 05 A9 01 8D ?? ?? 60
```

`INC abs ; INC abs ; LDA abs ; CMP #$32 ; BNE +5 ; LDA #$01 ; STA abs ; RTS`
— a counter pair incremented every frame, compared to $32 (50), and a
flag stored at threshold. **50 = PAL frames per second**, so this is
likely a 1-second tick generator.

## FC_V3.x (Hawkeye-era)

```
4C ?? ?? AD ?? ?? C9 60 90 0B 29 0F 9D ?? ?? FE ?? ?? 4C ?? ?? AD ?? ?? C9 40 90
0B 29 3F 9D
```

Decoded:
- `JMP abs` — early dispatch
- `LDA abs / CMP #$60 / BCC +11 / AND #$0F / STA abs,X / INC abs,X / JMP abs`
  — High-nibble test for `$60-$7F` command range; mask low nibble;
  store; increment; jump. This is the **pattern command decoder**:
  values < $60 are notes, ≥ $60 are commands.
- Second branch: `CMP #$40 / BCC +11 / AND #$3F / STA abs,X` — another
  command range with 6-bit parameter mask. Likely the duration band
  (`$40-$5F` range with 32 distinct durations).

## FC_V4_Packed

```
EE 99 ?? EE 9A ?? EE 9B ?? A9
```

Very short signature — three sequential `INC abs` (at offsets $99-$9B
within the player) followed by `LDA #imm`. The triple-INC suggests
per-voice frame counters at consecutive zp/absolute addresses.

## Implications for Hawkeye rebuild

The published research doc says Hawkeye is FC V3 with init=$1800 /
play=$1806. **CSDb metadata for Hawkeye.sid disagrees:**
- Load: $7AE0
- Init: $7AE0
- Play: $7AE3 (+**3**, not +6)
- Songs: 12
- Size: 8768 bytes ($2240)

This means **Hawkeye.sid is NOT FC-formatted**. It's a Tel-internal
MoN/Tel-Jeroen tune, with the same architectural lineage as FC but a
different player binary. The +3 offset and high load address suggest
a relocated standalone driver, not the $1800-anchored FC editor
output.

**Action**: when starting the migration, run sidid against the
sidfinity-rebuilt Hawkeye.sid and confirm it matches MoN/Deenen or
MoN/Tel (none currently exists in sidid.nfo!), NOT MoN/FutureComposer.

This may also explain why FC is the engine grouping in our HVSC index
but Hawkeye is the chosen target: Hawkeye is the architectural elder
of FC, and a successful rebuild proves the MoN family ground truth
before tackling FC's editor-added complications.
