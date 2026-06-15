---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: curl
fetch_date: 2026-06-15
author: Cadaver (with signatures by Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos)
content_date: ongoing
reliability: primary
---

# SIDId player-identification signatures for Ariston / Ian_Crabtree / Wally_Beben

SIDId (cadaver/sidid) is the canonical HVSC playroutine identity scanner.
The following signature blocks identify the Ariston family of players.
Each hex byte is literal; `??` accepts any byte; `END` terminates.

## Ariston (canonical / base player)

```
A2 00 6E ?? ?? 90 07 BD ?? ?? 99 ?? ?? C8 E8 E0 08 D0 EF AE ?? ?? A9 FF END
```

Decoded mnemonics (6502):
- `A2 00`        = LDX #$00
- `6E ?? ??`     = ROR abs  (rotates some byte in memory — likely a counter/seed)
- `90 07`        = BCC +7
- `BD ?? ??`     = LDA abs,X  (load from table)
- `99 ?? ??`     = STA abs,Y  (store into voice state/output)
- `C8`           = INY
- `E8`           = INX
- `E0 08`        = CPX #$08   (loop over 8 bytes — 3 voices × 2 regs + extras?)
- `D0 EF`        = BNE loop
- `AE ?? ??`     = LDX abs
- `A9 FF`        = LDA #$FF
- `END`

The `E0 08` (loop over 8 iterations) and the Y-indexed STA into what is likely
the $D400 region suggests this copies 8 bytes from a source table indexed by X
into voice-register output positions.

## Ian_Crabtree_V1

```
9D ?? ?? 20 ?? ?? CA 10 EF A0 ?? A9 ?? 99 00 D4 END
```

Decoded:
- `9D ?? ??`    = STA abs,X
- `20 ?? ??`    = JSR abs
- `CA`          = DEX
- `10 EF`       = BPL loop (-17)
- `A0 ??`       = LDY #imm
- `A9 ??`       = LDA #imm
- `99 00 D4`    = STA $D400,Y  (direct SID write)
- `END`

Note: `99 00 D4` is STA $D400,Y — confirms direct SID register writes indexed by Y.

## Ian_Crabtree_V2

```
AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 29 0F 48 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 BD END
```

Decoded highlights:
- `AA`           = TAX
- `BD ?? ??`     = LDA abs,X  (from frequency/data table)
- `99 05 D4`     = STA $D405,Y  (voice N attack/decay — Y selects voice, stride $07)
- `BD ?? ??`     = LDA abs,X
- `99 06 D4`     = STA $D406,Y  (sustain/release)
- `29 0F`        = AND #$0F      (mask low nibble)
- `48`           = PHA
- `A9 ??`        = LDA #imm
- `99 04 D4`     = STA $D404,Y  (control register)
- `BD ?? ??`     = LDA abs,X
- `99 04 D4`     = STA $D404,Y  (control register again — gate on/off)
- `BD`           = (start of next sequence)
- `END`

Notes on V2:
- Writes $D404 twice (ADSR set, then gate control) — implies two-phase note trigger
- $D405/$D406 = attack/decay, sustain/release = ADSR envelope write
- Y-indexing by 7 per voice (voices at $D400, $D407, $D40E)

## Wally_Beben variant (two sub-signatures)

Sub-signature 1:
```
48 C9 08 B0 ?? A9 ?? 9D ?? ?? AC ?? ?? 68 99 03 D4 68 99 02 D4 CE ?? ?? 30 END
```

Decoded:
- `48`           = PHA
- `C9 08`        = CMP #$08     (compare with 8 — possibly note range threshold)
- `B0 ??`        = BCS +N       (branch if >= 8)
- `A9 ??`        = LDA #imm
- `9D ?? ??`     = STA abs,X    (store to voice-state table)
- `AC ?? ??`     = LDY abs
- `68`           = PLA
- `99 03 D4`     = STA $D403,Y  (voice freq hi-byte)
- `68`           = PLA
- `99 02 D4`     = STA $D402,Y  (voice freq lo-byte)
- `CE ?? ??`     = DEC abs
- `30`           = BMI (branch minus — counter underflow)
- `END`

Notes: $D402/$D403 = voice frequency lo/hi bytes; Y selects voice (stride 7).
The CMP #$08 / BCS branch is consistent with a note-range check (below 8 =
 in-range, else take special path).

Sub-signature 2:
```
BD ?? ?? AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 END
```

Decoded (similar to V2 but with extra TAX):
- `BD ?? ??`     = LDA abs,X   (load instrument/note index)
- `AA`           = TAX          (use as new index)
- `BD ?? ??`     = LDA abs,X   (load from instrument table)
- `99 05 D4`     = STA $D405,Y
- `BD ?? ??`     = LDA abs,X
- `99 06 D4`     = STA $D406,Y
- `A9 ??`        = LDA #imm
- `99 04 D4`     = STA $D404,Y
- `BD ?? ??`     = LDA abs,X
- `99 04 D4`     = STA $D404,Y
- `END`

Sub-signature 3:
```
BD ?? ?? 99 04 D4 AE ?? ?? EE ?? ?? BD ?? ?? 18 END
```

- `BD ?? ??`     = LDA abs,X
- `99 04 D4`     = STA $D404,Y  (control register write)
- `AE ?? ??`     = LDX abs      (load counter/pointer)
- `EE ?? ??`     = INC abs      (increment counter — pattern/sequence pointer advance)
- `BD ?? ??`     = LDA abs,X
- `18`           = CLC           (likely freq calc: CLC; ADC)
- `END`

## Interpretation

The three distinct signature groups (base Ariston, Ian_Crabtree variants, Wally_Beben)
suggest at least three structurally distinct player code variants in HVSC — consistent
with the documented development history (Crabtree original; Beben modification; Maniacs
of Noise drum enhancement feeding back into Beben's version).

Key SID register usage observed in signatures:
- $D402,Y / $D403,Y — voice frequency lo/hi (Y=0/7/14 for voices 1/2/3)
- $D404,Y           — voice control register (waveform + gate)
- $D405,Y / $D406,Y — attack/decay, sustain/release

The `E0 08` loop count in the base Ariston signature (8 iterations) is notable:
3 voices × 2 frequency bytes = 6, plus pulse-width bytes would reach 8 or 9.
Alternatively: 8 could be 2 SID regs × 4 channels if a percussion channel exists.

Source: https://github.com/cadaver/sidid/blob/master/sidid.cfg
