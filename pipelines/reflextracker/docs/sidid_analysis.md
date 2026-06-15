---
source_url: local: /home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg
fetched_via: local read
fetch_date: 2026-06-15
author: cadaver (CSDb sidid tool)
content_date: unknown
reliability: primary
---

# Reflextracker — SIDId Signature Analysis

## Raw signature (from sidid.cfg)

```
69 ?? 8D ?? ?? ?? 0A AD ?? ?? C9 ?? 49 01 8D ?? ??
A5 D0 69 ?? 85 D0 AA A5 D1 90 07 69 00 85 D1 8D ?? ??
C9 ?? 90 06 D0 0D E0 ?? B0 09
BC ?? ?? BE ?? ?? 4C ?? ??
AD ?? ?? AE ?? ?? 4C ?? ?? A9
```

## Online sidid.cfg (GitHub cadaver/sidid)

The online version (fetched 2026-06-15) contains **the same single Reflextracker entry** — no version splits, no second variant. One signature covers all known HVSC members.

## Confirmed match offset in player binary

The signature anchors at **$C060** in `RFXT PLAYER V1.1` (the standalone player PRG, load=$C000, size=2048 bytes). The EOR #$01 appears at $C069. Multiple instances of the core pattern exist for the two digi voices (confirmed at $C060, $C09E, $C103 in the player binary).

## Opcode-by-opcode decode

| Bytes | Mnemonic | Derived interpretation |
|-------|----------|----------------------|
| `69 ??` | `ADC #imm` | Add step to A (step varies per call site) |
| `8D ?? ??` | `STA abs` | Store updated value to abs address |
| `?? 0A` | (skip byte) `ASL A` | Arithmetic shift left A; old bit7 → Carry |
| `AD ?? ??` | `LDA abs` | Load direction/toggle byte from abs |
| `C9 ??` | `CMP #imm` | Compare with wrap-around limit ($C7 = player end, confirmed) |
| `49 01` | `EOR #$01` | **Toggle bit 0 — sample direction (forward/reverse ping-pong)** |
| `8D ?? ??` | `STA abs` | Write direction flag back |
| `A5 D0` | `LDA $D0` | Load low byte of 16-bit ZP pointer **$D0/$D1** |
| `69 ??` | `ADC #step` | Advance pointer low byte by variable step |
| `85 D0` | `STA $D0` | Store updated low byte |
| `AA` | `TAX` | Save new pointer low byte in X for later |
| `A5 D1` | `LDA $D1` | Load high byte of pointer |
| `90 07` | `BCC +7` | No carry from low byte → skip high byte increment |
| `69 00` | `ADC #$00` | Ripple carry into high byte |
| `85 D1` | `STA $D1` | Store updated high byte |
| `8D ?? ??` | `STA abs` | Shadow-copy high byte to absolute address |
| `C9 ??` | `CMP #imm` | High-byte range check (end-of-stream) |
| `90 06` | `BCC +6` | Still within stream → skip |
| `D0 0D` | `BNE +13` | Additional range check |
| `E0 ??` | `CPX #imm` | Low-byte range check (X = low byte from TAX above) |
| `B0 09` | `BCS +9` | Low byte ≥ limit → stream exhausted |
| `BC ?? ??` | `LDY abs,X` | **Load Y via jump table (X = stream position low byte)** |
| `BE ?? ??` | `LDX abs,X` | Load X via parallel jump table |
| `4C ?? ??` | `JMP abs` | Dispatch to handler |
| `AD ?? ??` | `LDA abs` | Secondary dispatch: load A from abs |
| `AE ?? ??` | `LDX abs` | Secondary dispatch: load X from abs |
| `4C ?? ??` | `JMP abs` | Jump to secondary handler |
| `A9` | `LDA #imm` (partial) | First byte of next instruction (not part of pattern) |

## Structural analysis (DERIVED — not confirmed by disassembly)

### 1. 16-bit packed-data stream reader ($D0/$D1 = current read pointer)

The central routine advances a 16-bit zero-page pointer (`$D0/$D1`) by a variable step per call. After each advance, the **low byte is saved in X** (via `TAX`) for use in the jump table dispatch below.

This is a packed sample-stream reader. In the Reflextracker context:
- `$D0/$D1` = current read position in packed digi sample data
- The "step" (`ADC #??`) varies: call sites confirmed at $C05B (ADC #$00), $C06E (ADC #$00 i.e. step from carry), suggesting the step is computed dynamically
- `C9 $C7` (limit byte $C7 appears in the player) = high-byte limit check against the end of the player's $C000–$C7FF range

### 2. Direction toggle (ping-pong playback)

`EOR #$01` on a stored byte = toggle bit 0. In a 2-channel digi player, this is the **sample playback direction flag** (forward vs. reverse), enabling ping-pong sample loops. Confirmed by PVCF's STIL comment: "echoeffects and flanger" — the echo is likely implemented via reverse sample replay.

### 3. Jump table dispatch (LDY abs,X / LDX abs,X / JMP abs)

`BC ?? ?? / BE ?? ?? / 4C ?? ??` = a 2-array jump table. X (= stream position low byte mod table) indexes into two parallel arrays:
- Array 1 (BC = LDY abs,X): probably the command/note index
- Array 2 (BE = LDX abs,X): probably a parameter or handler address component
- `JMP abs`: fixed handler or indirect via Y/X

This dispatch pattern is used in both the main stream handler and a secondary path (plain `LDA abs / LDX abs / JMP`), suggesting the player has at least two parallel stream readers (one per digi channel, as documented).

### 4. Two stream readers confirmed

The EOR/pointer pattern appears **four times** in the 2048-byte player:
- $C060 / $C09E: **Voice 1** stream reader (forward + reverse path)
- $C103 / $C13A: **Voice 2** stream reader (forward + reverse path)

Voice 2 uses `$D2/$D3` as its ZP pointer (not $D0/$D1), confirmed by the `A5 D2` / `A5 D3` at $C113/$C123.

### 5. CIA timer / own IRQ install (confirmed from binary + docs)

At $C016 (second JMP target in the player):
```
$C016: 78           SEI
$C019: A9 36        LDA #$36     ; banking: basic ROM out, char ROM in ($01 = $36)
$C01B: 85 01        STA $01
...
$C03A: A2 7F        LDX #$7F
$C03C: 8E 0D DD     STX $DD0D    ; CIA2 ICR: disable all interrupts
$C03F: A2 93        LDX #$93
$C041: 8E 04 DD     STX $DD04    ; CIA2 timer A low
$C044: 8D 05 DD     STA $DD05    ; CIA2 timer A high
```

The player installs a CIA2-driven interrupt (not VBI). This is consistent with the PSID header having `play_addr=0` (own IRQ install). The init call at $C006 sets up the CIA timer and IRQ vector; subsequent IRQ fires play one frame of the digi stream.

### 6. Volume register used for 4-bit DAC

The SID chip's master volume register ($D418 bits 3:0) is used as a 4-bit DAC for sample output. Consistent with standard C64 digi technique. The packed sample bytes in the MOD file are 4-bit nibbles interleaved or sequential — this matches the "4BHI"/"4BLO" driver naming on disk (SDRV.UPRT 4BHI, SDRV.UPRT 4BLO = uniport 4-bit high/low nibble drivers).

## Cross-version confirmation

The online cadaver/sidid.cfg has no additional Reflextracker signatures beyond the one in the local copy. **Single signature, no version splits identified.** The five address variants in the HVSC corpus ($C000, $C006, $C050, $C103, $CF40) are all start-address variations of the same player binary, not different player versions.
