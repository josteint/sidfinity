---
source_url: binary: RFXT_PLAYER_V1.1.prg (from Reflextracker V1.1 disk image)
fetched_via: direct analysis 2026-06-15
fetch_date: 2026-06-15
author: RE analysis by this session (automated 6502 disassembly)
content_date: 2026-06-15
reliability: primary (binary evidence)
---

# Reflextracker Player Disassembly — Standalone RFXT_PLAYER V1.1

## Binary Properties

- **File**: `RFXT_PLAYER_V1.1.prg`
- **Load address**: `$C000`
- **Size**: 2032 bytes
- **String found**: `RFXT PLAYER V1.1` (at offset ~0x4A0 in player)

## Entry Points

| Address | Role |
|---------|------|
| `$C000` | JMP `$C02C` — init/reset entry |
| `$C003` | JMP `$C016` — play entry |
| `$C006` | Play routine continuation (state check) |
| `$C016` | Main play dispatch (checks `$D7` state) |
| `$C02C` | Full init routine |
| `$C050` | Minimal init (voice 1 ctrl + CIA CRB) |
| `$C219` | Channel event processor call |
| `$C244` | Channel 2 processor |
| `$C4E8` | Event tick routine |

## Init Routine (`$C02C`)

```
$C02C  A9 81        LDA #$81
$C02E  85 D7        STA $D7          ; state flag = init
$C030  A9 00        LDA #$00
$C032  A2 18        LDX #$18
$C034  9D 00 D4     STA $D400,X      ; clear all 25 SID regs ($D400-$D418)
$C037  CA           DEX
$C038  10 FA        BPL $C034        ; loop
$C03A  A2 7F        LDX #$7F
$C03C  8E 0D DD     STX $DD0D        ; CIA2 ICR: disable all IRQs
$C03F  A2 93        LDX #$93
$C041  8E 04 DD     STX $DD04        ; CIA2 timer A lo = $93 (147)
$C044  8D 05 DD     STA $DD05        ; CIA2 timer A hi = $00
                                     ; → timer period = 147 cycles, ~6700 Hz
$C047  A2 FF        LDX #$FF
$C049  8E 02 D4     STX $D402        ; V1 PW lo = $FF
$C04C  8E 03 D4     STX $D403        ; V1 PW hi = $FF (full pulse width)
$C04F  8E 06 D4     STX $D406        ; V2 PW lo = $FF
$C052  A2 41        LDX #$41
$C054  8E 04 D4     STX $D404        ; V1 ctrl = $41 (gate + pulse wave)
$C057  8E 0E DD     STX $DD0E        ; CIA2 CRB = $41 (start timer B in pulse mode?)
$C05A  60           RTS
```

## Play Loop (`$C016`)

```
$C016  A5 D7        LDA $D7
$C018  10 0A        BPL $C03D        ; if D7 >= 0: jump to full init area? No, to $C03D
                                     ; Actually BPL branches if N=0 (positive/zero)
                                     ; D7=$81 (10000001) has N=1 → DOES NOT branch
                                     ; D7=$00 → branches
$C01A  20 19 C2     JSR $C219        ; process channel events
$C01D  A5 D7        LDA $D7
$C01F  F0 F5        BEQ $C016        ; if D7=0, loop
$C021  4C B2 C1     JMP $C1B2        ; else: advance playback position

[secondary entry]
$C024  F0 F0        BEQ $C03B        ; branch if done
$C026  20 44 C2     JSR $C244        ; process channel 2 events
$C029  4C B2 C1     JMP $C1B2
```

## SID Writes Observed

Only `$D418` is written during play (one write at `$C1A9`):
```
$C1A9  8D 18 D4     STA $D418        ; volume = digi sample byte (upper nibble → DAC)
```

Init writes: `$D400–$D418` (clear), `$D402`, `$D403`, `$D404`, `$D406`.

## Data Tables Within Player

| Address | Content |
|---------|---------|
| `$C560` | Freq lo table (starts: 72 78 00 00 00 00 80 87 8F 98 A1 AA B5 BF CB D7 E4 F1 ...) |
| `$C5A0` | Octave table / note step table (starts: 0A 0B 0C 0D 0E 0F 03 03 04 05 05 06 ...) |
| `$C5E0` | ADSR/envelope table or hi-byte freq (81 41 01 C1 81 41 04 04 04 03 03 03 ...) |
| `$C5F0` | Secondary table (02 01 01 01 00 00 00 ...) |

## Key ZP Usage

```
$D0  ch1 data pointer lo     (also: $D8 = ch1 loop flag)
$D1  ch1 data pointer hi     (also: $D9 = ch2 loop flag)
$D2  ch2 data pointer lo
$D3  ch2 data pointer hi
$D4  channel flags
$D5  speed counter
$D6  sub-speed counter
$D7  player state ($81=uninit, $00=done, $01+=playing)
$DC  indirect ptr lo (ch1 waveform base)
$DD  indirect ptr hi
$DE  indirect ptr lo (ch2 waveform base)
$DF  indirect ptr hi
$E0/$E9  counter vars
$E7  end-of-data sentinel
$E8  ch1 active
$F0  ch2 active
$F1  ch1 enabled
$CF  note result (from note-to-freq subroutine)
```

## Self-Modifying Code (SMC) Pattern

The player has ~70+ SMC writes. Pattern is:

1. Compute channel position step
2. `ADC #imm` — step value is SMC (changes per module speed)
3. `STA $CXXX` — patches the imm byte for next call
4. Compare against wrap threshold (also SMC)
5. `EOR #$01` — toggle direction for bounce-back
6. Store via `LDY $1000,X / LDX $EE00,Y` — note/freq table lookup

This means effectively every per-module configuration variable is patched
into the player code at runtime by the tracker or by the init section.

## JSR Call Graph

```
C00B → C02C (init)
C01A → C219 (process ch1 events)
C026 → C244 (process ch2 events)
C21B → C4E8 (event tick)
C24F → C26E (note decode, ch1)
C260 → C26E (note decode, ch2)
C318 → C4B1 (helper)
C3F1 → C4B1 (helper)
C499 → C4D6 (sample step)
C4B5 → C0890 (external? tracker callback)
C54A → C4C50 (external? tracker callback)
C551 → C3156 (external? tracker callback)
```

External JSRs (to addresses outside player range `$C000–$C7EF`) likely call
back into the tracker UI running in BASIC at `$0801`.

## Automated Full Disassembly

The complete raw disassembly (1114 lines) is saved to:
`tmp/reflextracker_research/rfxt_player_disasm_raw.txt`

Generated 2026-06-15 by automated 6502 disassembler (Python, opcode table).
Many bytes may be data misidentified as opcodes due to SMC and indirect jumps.
Manual review required for full understanding.
