---
source_url: https://github.com/cadaver/sidid/blob/master/sidid.cfg
fetched_via: curl https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetch_date: 2026-06-15
author: cadaver / Covert Bitops
content_date: unknown (repo maintained through ~2020)
reliability: primary
---

# SIDId Reflextracker Detection Signature

## Canonical signature from sidid.cfg

```
Reflextracker
69 ?? 8D ?? ?? ?? 0A AD ?? ?? C9 ?? 49 01 8D ?? ?? A5 D0 69 ?? 85 D0 AA A5 D1 90 07 69 00 85 D1 8D ?? ?? C9 ?? 90 06 D0 0D E0 ?? B0 09 BC ?? ?? BE ?? ?? 4C ?? ?? AD ?? ?? AE ?? ?? 4C ?? ?? A9 END
```

## Verified match location in RFXT PLAYER V1.1

The signature matches at `$C05D` in the standalone player binary (RFXT PLAYER V1.1, 2034 bytes, loads at $C000).

Actual bytes at $C05D:
```
69 00 8D 5C C0 90 0A AD 8F C0 C9 C7 49 01 8D 8F C0
A5 D0 69 00 85 D0 AA A5 D1 90 07 69 00 85 D1 8D 8C C0
C9 00 90 06 D0 0D E0 00 B0 09 BC 00 10 BE 00 EE 4C 09 C1
AD 87 C0 AE 81 C0 4C DA C0
```

## Annotation of the signature

```asm
$C05D: 69 00      ADC #$00     ; add step (SMC: byte $C05E holds actual step amount)
$C05F: 8D 5C C0   STA $C05C    ; write back to SMC target (self-modifying!)
$C062: 90 0A      BCC +10      ; branch if no page carry
$C064: AD 8F C0   LDA $C08F    ; load page-flip byte
$C067: C9 C7      CMP #$C7     ; compare with $C7 (boundary)
$C069: 49 01      EOR #$01     ; toggle bit 0 (direction flip)
$C06B: 8D 8F C0   STA $C08F    ; store back (SMC!)
$C06E: A5 D0      LDA $D0      ; ZP $D0 = lo byte of sample pointer
$C070: 69 00      ADC #$00     ; add step lo (SMC)
$C072: 85 D0      STA $D0      ; update lo pointer
$C074: AA         TAX          ; X = lo byte
$C075: A5 D1      LDA $D1      ; ZP $D1 = hi byte of sample pointer
$C077: 90 07      BCC +7       ; no carry from lo
$C079: 69 00      ADC #$00     ; add carry to hi (SMC)
$C07B: 85 D1      STA $D1      ; update hi pointer
$C07D: 8D 8C C0   STA $C08C    ; SMC (immediate in next LDY instruction)
$C080: C9 00      CMP #$00     ; compare hi byte with boundary page
$C082: 90 06      BCC +6       ; branch if below boundary
$C084: D0 0D      BNE +13      ; branch if not equal
$C086: E0 00      CPX #$00     ; check lo byte
$C088: B0 09      BCS +9       ; if at/past end address
$C08A: BC 00 10   LDY $1000,X  ; *** READ SAMPLE BYTE from $1000+X ***
$C08D: BE 00 EE   LDX $EE00,X  ; lookup step size from $EE00 table
$C090: 4C 09 C1   JMP $C109    ; continue audio output
```

## Key architectural observations

1. **Self-modifying code (SMC)**: The player extensively uses SMC. The `ADC #$00` instructions at $C05D, $C070, $C079 all have their immediate operand overwritten at runtime to hold the actual playback step size.

2. **ZP $D0/$D1 = voice 1 sample stream pointer** (16-bit). The pattern `A5 D0 / ADC / 85 D0 / TAX / A5 D1 / ... / 85 D1` is the 16-bit pointer increment pattern. ZP $D2/$D3 is the equivalent for voice 2.

3. **Sample data at $1000+**: `LDY $1000,X` — the sample audio bytes are in memory starting near $1000. The MOD file loads at $1009 with a 4-byte "RFX1" magic prefix.

4. **Step table at $EE00**: `LDX $EE00,X` — this lookup table maps the current sample byte value to a playback step size (determines pitch/speed). Content unknown — may be initialized by the tracker or be part of the module.

5. **Direction flip**: Byte at $C08F toggles between $00 and $01 (via EOR #$01) when the sample pointer crosses a page boundary. This implements **bidirectional sample playback** (forward/reverse for pitch shifting).

## Notes on HVSC SIDID classification

The sidid signature identifies the player BINARY code, not the music format. In HVSC, SID files using this player will have this code embedded in them.
