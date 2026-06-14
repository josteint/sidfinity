# John Player — Byte-Level Version Discriminators

Source: direct READ-ONLY inspection of HVSC #84 SID binaries (2026-06-14).
All offsets are from the PSID data region start (after 126-byte header + 2-byte embedded load address).

---

## Canonical Specimens Used

| Version | Path (relative to hvsc84/) | Total bytes | Code bytes |
|---------|---------------------------|-------------|------------|
| V1.4 | MUSICIANS/E/Eeben_Aleksi/John_Player_note.sid | 2274 | 2148 |
| V1.6 | MUSICIANS/E/Eeben_Aleksi/Rock_n_Roll_Butterfly.sid | 4029 | 3903 |
| V2.0b | MUSICIANS/E/Eeben_Aleksi/Radio_Challenge.sid | 4039 | 3913 |

---

## $1000 Entry Point (first 16 bytes from load)

**V1.4** (`John_Player_note`):
```
$1000: 4C 27 13  A4 42 F0 54  A2 FF 8E 72 10  E8 86 42  B9
       JMP $1327  LDY $42 BEQ+  LDX #FF STX $1072 INX STX$42  LDA $1420,Y
```
- `$1000`: JMP to init at $1327 (init offset +$327 = +807 decimal)
- `$1003`: Play inline; first instr = `LDY $42`

**V1.6** (`Rock_n_Roll_Butterfly`):
```
$1000: 4C 34 13  A4 42 F0 56  A2 FF 8E 74 10  E8 86 42  8E
       JMP $1334  LDY $42 BEQ+  LDX #FF STX $1074 INX STX$42  STX $D404
```
- `$1000`: JMP to init at $1334 (init offset +$334 = +820 decimal)
- `$1003`: Play inline; first instr = `LDY $42` (same as V1.4)
- V1.6 writes `STX $D404` directly (gate off) before instrument reads; V1.4 also does this but via a different path

**V2.0b** (`Radio_Challenge`):
```
$1000: 4C 7C 10  4C BA 10  86 41 60  86 46 CA 86 45 60  A9
       JMP $107C  JMP $10BA  STX $41 RTS  STX$46 DEX STX$45 RTS  LDA #...
```
- `$1000`: JMP to init at $107C (init offset +$07C = +124 decimal)
- `$1003`: JMP to play at $10BA (second JMP)
- `$1006–$107B`: Helper subroutines (modulator, sequence, zero helpers)

---

## Key Discriminating Byte Sequences in Play Routine

### $D406 context (Sustain/Release write)

**V1.4** — at $1018:
```
$1012: B9 20 14  8D 05 D4   ; LDA $1420,Y -> STA $D405 (AD)
$1018: B9 21 14  8D 06 D4   ; LDA $1421,Y -> STA $D406 (SR) — per-instrument
$101D: A9 09     8D 04 D4   ; LDA #$09    -> STA $D404 (CTRL) — hardcoded!
```
sidid discriminator: `8D 06 D4 **A9**` (A9 = LDA #imm follows the SR write)

**V1.6** — at $1018:
```
$1012: B9 20 14  8D 05 D4   ; LDA $1420,Y -> STA $D405 (AD)
$1018: B9 21 14  8D 06 D4   ; LDA $1421,Y -> STA $D406 (SR) — per-instrument
$101E: B9 22 14  8D 5E 10   ; LDA $1422,Y -> STA $105E (local scratch, pulse lo)
$1030: A9 09     8D 04 D4   ; LDA #$09    -> STA $D404 (CTRL) — still hardcoded, just later
```
sidid discriminator: `8D 06 D4 **B9**` (B9 = LDA abs,Y follows the SR write — loads next instrument field)

Note: BOTH V1.4 and V1.6 eventually write $D404 = #$09, just at different points in the voice block. The single binary difference between V1.4 and V1.6 is the byte immediately following `8D 06 D4`.

### After init loop

**V1.4/V1.6** (init loop + 15 bytes):
```
CA 10 F5  ; DEX / BPL (end of loop)
A8        ; TAY  (Y=0 after LDA #00 at top of init)
A9 0F     ; LDA #$0F
8D 18 D4  ; STA $D418 (master vol = $0F)
A9 0C     ; LDA #$0C
85 46     ; STA $46 (tempo = $0C)
```
sidid sees: `CA 10 F5 A8 A9` (loop end + TAY + LDA #imm)

**V2.0b** (init loop + 15 bytes):
```
CA 10 F5  ; DEX / BPL (end of loop)
A8        ; TAY
AD 80 16  ; LDA $1680 (wave table entry 0)
8D 17 D4  ; STA $D417 (filter ctrl from song data)
AD 00 17  ; LDA $1700 (arp table entry 0)
8D 18 D4  ; STA $D418 (master vol from song data)
AD 00 16  ; LDA $1600 (song param table)
85 46     ; STA $46 (tempo from song param table)
```
sidid sees: `CA 10 F5 A8 AD` (loop end + TAY + LDA abs)

---

## Init Loop Location

| Version | Code offset | Absolute address | ZP base (byte at loop+5) |
|---------|-------------|------------------|--------------------------|
| V1.4 | +807 = $327 | $1327 | $40 |
| V1.6 | +820 = $334 | $1334 | $40 |
| V2.0b | +124 = $07C | $107C | $40 |

All three use ZP base $40 (byte XX in `95 XX`).

---

## Frequency Table Base Addresses

| Version | Table base | Note 0 (C~2) | Note 12 (C~3) | Note 24 (C~4) |
|---------|-----------|--------------|---------------|---------------|
| V1.4 | $135A | $0224 | $0449 | $0892 |
| V1.6 | $1360 | $0224 | $0449 | $0892 |
| V2.0b | $1460 | $0224 | $0449 | $0892 |

Content identical; address differs. All use erroneous 1 MHz clock assumption (sharp on PAL by ~1.5%).

---

## End-of-Binary Signature String

All confirmed binaries end with an embedded ASCII player ID string:
```
"NGE      JOHN PLAYER BY A. EEBEN"
```
(hex: `4E 47 45 20 20 20 20 20 20 4A 4F 48 4E 20 50 4C 41 59 45 52 20 42 59 20 41 2E 20 45 45 42 45 4E`)

Present in V2.0b (Radio_Challenge, last 31 bytes). The leading "NGE" prefix is not explained; possibly page-alignment padding or part of a longer internal string.
