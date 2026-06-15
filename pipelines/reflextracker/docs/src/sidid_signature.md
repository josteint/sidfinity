---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: curl 2026-06-15
fetch_date: 2026-06-15
author: Cadaver / iAN CooG / various
content_date: ongoing
reliability: primary
---

# Reflextracker SIDId Identification Signature

From `cadaver/sidid` (github.com/cadaver/sidid), the `sidid.cfg` contains exactly one
Reflextracker entry:

```
Reflextracker
69 ?? 8D ?? ?? ?? 0A AD ?? ?? C9 ?? 49 01 8D ?? ?? A5 D0 69 ?? 85 D0 AA A5 D1 90 07 69 00 85 D1 8D ?? ?? C9 ?? 90 06 D0 0D E0 ?? B0 09 BC ?? ?? BE ?? ?? 4C ?? ?? AD ?? ?? AE ?? ?? 4C ?? ?? A9 END
```

## Signature Analysis

This signature matches the **frequency-stepping / channel-advance loop** in the Reflextracker
play engine. Annotated:

```
69 ??           ADC #imm        ; add step to channel position (lo)
8D ?? ??        STA abs         ; store updated lo (SMC patch slot)
0A              ASL A           ; carry for hi byte
AD ?? ??        LDA abs         ; load hi byte of position
C9 ??           CMP #imm        ; compare against wrap threshold
49 01           EOR #$01        ; toggle direction bit
8D ?? ??        STA abs         ; store updated hi byte (SMC)
A5 D0           LDA $D0         ; load channel 1 lo ptr
69 ??           ADC #imm        ; add step
85 D0           STA $D0         ; store lo
AA              TAX
A5 D1           LDA $D1         ; load channel 1 hi ptr
90 07           BCC ...
69 00           ADC #$00        ; carry propagation
85 D1           STA $D1
8D ?? ??        STA abs         ; SMC update
C9 ??           CMP #imm        ; compare hi against page limit
90 06           BCC ...
D0 0D           BNE ...
E0 ??           CPX #imm        ; compare lo
B0 09           BCS ...
BC ?? ??        LDY abs,X       ; LDY note_table,X (note lookup)
BE ?? ??        LDX abs,Y       ; LDX freq_table,Y (freq lookup)
4C ?? ??        JMP abs         ; continue
AD ?? ??        LDA abs         ; load counter
AE ?? ??        LDX abs
4C ?? ??        JMP abs
A9              LDA #...        ; load channel param
```

## Matched Locations

- **Standalone RFXT_PLAYER.prg** (at `$C000`): signature at `$C05D`
  - `LDY $1000,X` (note_table), `LDX $EE00,Y` (freq_table)
  - Context: `69 00 8D 5C C0 90 0A AD 8F C0 C9 C7 49 01 8D 8F C0 ...`

- **Trance_202.sid** embedded engine (at `$1F00`, copied to `$F000`):
  signature at `$1F1C` (= `$F01C` after copy)
  - `LDY $7700,X` (note_table), `LDX $FA00,Y` (freq_table)
  - Context: `69 80 8D 1B F0 90 0A AD 4E F0 C9 FB 49 01 8D 4E F0 ...`

The ?? bytes encode player-specific constants:
- The step increment (speed byte) varies per module
- The wrap threshold varies with relocation
- The note/freq table addresses vary with player base address
