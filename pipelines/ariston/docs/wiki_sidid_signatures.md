---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-15
author: Cadaver (Lasse Öörni) + contributors
content_date: ongoing (cadaver/sidid master branch)
reliability: primary (canonical SID player fingerprint database)
---

# Ariston / Ian_Crabtree Player Signatures — sidid.cfg

These are the byte-pattern signatures used by the sidid tool (and the
WilfredC64/player-id tool) to identify Ariston-family SIDs. `??` means
any byte is accepted at that position.

## Ariston (the full Brabbin/Beben editor output)

```
A2 00 6E ?? ?? 90 07 BD ?? ?? 99 ?? ?? C8 E8 E0 08 D0 EF AE ?? ?? A9 FF
```

Interpretation (6502 mnemonics):
```
LDX #$00
ROR <addr>        ; 6E ?? ?? — rotate right absolute (address varies)
BCC +7            ; 90 07
LDA <table>,X    ; BD ?? ?? — load from freq/note table
STA <dest>,Y     ; 99 ?? ?? — store to SID register area
INY
INX
CPX #$08         ; E0 08 — 8 voices or 8 registers in inner loop
BNE -17          ; D0 EF
LDX <addr>       ; AE ?? ?? — load x from zero-page/absolute
LDA #$FF         ; A9 FF — mask or channel-off value
```

The `E0 08` (CPX #8) and `A9 FF` pattern, combined with the `6E` ROR instruction,
are the key discriminating bytes. This inner loop pattern suggests a voice loop
iterating over 8 channels/registers.

## Ian_Crabtree_V1 (early/simple Crabtree player)

```
9D ?? ?? 20 ?? ?? CA 10 EF A0 ?? A9 ?? 99 00 D4
```

Interpretation:
```
STA <table>,X    ; 9D ?? ?? — store A to indexed address
JSR <addr>       ; 20 ?? ?? — call subroutine
DEX
BPL -17          ; 10 EF — loop while X >= 0
LDY #??          ; A0 ??
LDA #??          ; A9 ??
STA $D400,Y      ; 99 00 D4 — write to SID register $D400+Y
```

The `99 00 D4` (STA $D400,Y) is a direct SID write pattern.
`JSR` + `DEX` + `BPL` suggests a counted subroutine loop over voices.

## Ian_Crabtree_V2 (more developed Crabtree player)

```
AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 29 0F 48 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4 BD
```

Interpretation:
```
TAX
LDA <table>,X   ; BD ?? ??
STA $D405,Y     ; 99 05 D4 — write Attack/Decay (AD)
LDA <table>,X   ; BD ?? ??
STA $D406,Y     ; 99 06 D4 — write Sustain/Release (SR)
AND #$0F        ; 29 0F — mask to low nibble
PHA             ; 48
LDA #??         ; A9 ??
STA $D404,Y     ; 99 04 D4 — write Control Register (gate/waveform)
LDA <table>,X   ; BD ?? ??
STA $D404,Y     ; 99 04 D4 — write Control Register again
LDA <table>,X   ; BD ?? ??
```

This reveals:
- Writes to $D405 (AD) and $D406 (SR) in sequence = ADSR loading
- Double write to $D404 (Control Register) = hard restart pattern
  (gate-off then gate-on, or waveform change then gate-on)
- `AND #$0F` masking the ADSR value = per-instrument ADSR with nibble masking

## Wally_Beben variant (from sidid.cfg — additional signature)

```
48 C9 08 B0 ?? A9 ?? 9D ?? ?? AC ?? ?? 68 99 03 D4 68 99 02 D4 CE ?? ?? 30
BD ?? ?? AA BD ?? ?? 99 05 D4 BD ?? ?? 99 06 D4 A9 ?? 99 04 D4 BD ?? ?? 99 04 D4
BD ?? ?? 99 04 D4 AE ?? ?? EE ?? ?? BD ?? ?? 18
```

This multi-line signature covers Beben's personal variant of the Ariston player.
Key observations:
- `C9 08 B0` = CMP #8, BCS — 8-voice/channel boundary check
- `68 99 03 D4` = PLA + STA $D403,Y — pull and write to PW high
- `68 99 02 D4` = PLA + STA $D402,Y — pull and write to PW low
  (stack-based PW register writes — unusual, suggests computed PW)
- `CE ?? ?? 30` = DEC <addr>, BMI — countdown reaching zero, branch if minus
- `EE ?? ??` = INC <addr> — counter increment
- `18` = CLC — clear carry (before ADC presumably)

The PW writes via stack pull are distinctive — suggests Beben pushed PW values
earlier, then pulls them for write during voice update.

## Version lineage summary

Based on sidid.cfg naming:
1. **Ian_Crabtree_V1** — earliest Crabtree player (simple JSR-loop structure)
2. **Ian_Crabtree_V2** — more developed (explicit AD/SR writes, double $D404)
3. **Ariston** — the full Brabbin-edited version (8-voice ROR-based loop)
4. **Wally_Beben** — Beben's personal variant (stack PW writes, enhanced drums
   from Maniacs of Noise collaboration)

## Notes on sidid tool

- Tool: github.com/cadaver/sidid (Cadaver/Lasse Öörni)
- Format: hex patterns with `??` wildcards + `END` terminator
- Used by: sidid CLI + WilfredC64/player-id (cross-platform rewrite)
- The sidid.nfo additionally confirms the three-name lineage:
  Ian_Crabtree_V1, Ian_Crabtree_V2, and Ariston (the published editor output)
