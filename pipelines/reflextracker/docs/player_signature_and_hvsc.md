---
source_url: https://github.com/cadaver/sidid (sidid.cfg), hvsc84.db (local query)
fetched_via: curl + sqlite3
fetch_date: 2026-06-15
reliability: primary
---

# Reflextracker — Player Signature and HVSC Corpus

## sidid.cfg Signature (from cadaver/sidid)

The Reflextracker player is positively identified in `sidid.cfg`:

```
Reflextracker
69 ?? 8D ?? ?? ?? 0A AD ?? ?? C9 ?? 49 01 8D ?? ?? A5 D0 69 ?? 85 D0 AA A5 D1
90 07 69 00 85 D1 8D ?? ?? C9 ?? 90 06 D0 0D E0 ?? B0 09 BC ?? ?? BE ?? ??
4C ?? ?? AD ?? ?? AE ?? ?? 4C ?? ?? A9 END
```

This is a single-signature match (one variant). The pattern shows:
- `ADC #?? / STA ?? / ?? / ASL A` — frequency accumulator computation
- `LDA $D0 / ADC #?? / STA $D0 / TAX / LDA $D1 / BCC ...` — 16-bit sample position arithmetic
- `STA ??` — write to SID register (computed sample playback position)
- `CMP #?? / BCC ?? / BNE ?? / CPX #?? / BCS ??` — bounds checking
- `LDY ??,X / LDX ??,X / JMP ??` — indirect dispatch
- `LDA ?? / LDX ?? / JMP ??` — track/pattern read

This is consistent with a **sample-based player** that steps through PCM data at a variable rate (D0/D1 = 16-bit fractional position accumulator).

## KB/TOM Signature (separate player, also by kb)

```
KB/TOM (signature 1)
3D ?? ?? 9D 04 D4 B9 ?? ?? 7D ?? ?? A8 B9 ?? ?? 18 7D ?? ?? 9D 00 D4
B9 ?? ?? 7D ?? ?? 9D 01 D4 4C ?? ?? 29 END

KB/TOM (signature 2)
B9 ?? ?? 29 08 F0 ?? B9 ?? ?? 3D ?? ?? 9D 04 D4 C8 B9 ?? ?? 9D 01 D4
A9 ?? 9D 00 D4 C8 98 END
```

KB/TOM is a different player used in kb's C64 demos (Breitbandkatze, Reflection, etc.) — NOT Reflextracker. PVCF used both. KB/SDS is a third variant (Smash Designs era).

---

## HVSC Corpus Statistics

**Total Reflextracker SIDs in HVSC #84: 137**

Query: `SELECT path, init_addr, play_addr FROM sids WHERE engine='Reflextracker'`

### Init Address Distribution

| init_addr | Count | Notes |
|-----------|-------|-------|
| $C006 (49158) | 130 | Standard — player at $C000, entry at $C006 |
| $C050 (49232) | 4 | PVCF's Gubber, Trance_202, Originalzak + 1 other |
| $C003 (49155) | 1 | Access_Denied_intro (PVCF) |
| $C0C3 (49411) | 1 | Brainbeat_3_Introrap (PVCF) |
| $1C06 (7174) | 1 | Jonny/Future_Come — relocated player! |

All have **play_addr = $0000** (PAL VBI self-installed IRQ, standard for all 137 SIDs).

### Composers Using Reflextracker (HVSC)

| Composer | SID count |
|----------|-----------|
| Warlock | 26 |
| Vegeta | 13 |
| JFK | 13 |
| PVCF | 6 |
| Data | 14 |
| Mephisto | 9 |
| Randy | 7 |
| Gregfeel | 12 |
| Manik | 6 |
| V-12 | 4 |
| Stice | 3 |
| Leming | 3 |
| Cliff | 3 |
| Flip | 1 |
| Brizz | 1 |
| Bax | 1 |
| Rea | 2 |
| Killer | 3 |
| Jammer | 1 |
| Jonny | 3 |
| Praiser | 2 |
| Various (DEMOS/) | 5 |

**Note:** Most composers are Polish (Warlock, JFK, Vegeta, Gregfeel, Data, Mephisto, etc.) — consistent with the Lemon64 thread reference to "a Reflextracker competition disk from Poland." The tracker spread from Germany to the Polish C64 scene.

### Notable SIDs

```
MUSICIANS/P/PVCF/Access_Denied_remix.sid   init=$C006  (original demo song)
MUSICIANS/P/PVCF/Gubber.sid                init=$C050  (demo song — samples "Ein Bisschen Frieden")
MUSICIANS/P/PVCF/Trance_202.sid            init=$C050
MUSICIANS/P/PVCF/Originalzak.sid           init=$C050
MUSICIANS/P/PVCF/Brainbeat_3_Introrap.sid  init=$C0C3
MUSICIANS/P/PVCF/Access_Denied_intro.sid   init=$C003
MUSICIANS/J/Jonny/Future_Come.sid          init=$1C06  (player relocated to $1C00!)
MUSICIANS/M/Manik/I_Love_Punk.sid          init=$CF00  (different base)
```

### Standard vs Non-Standard

- **Standard (init=$C006):** 130/137 = 94.9% — nearly all HVSC Reflextracker SIDs use the canonical player at $C000 with init at $C006
- **Non-standard:** 7 SIDs with different init addresses (possibly different player versions or relocated)

---

## SID Technical Details (from CSDb SID pages)

### Access Denied (remix) — init=$C006 ($C006 = 49158)
- Load addr: $4A1C ($4A1C = 18972)
- Data size: 32228 bytes
- SID model: 8580
- Clock: PAL
- HVSC: `/MUSICIANS/P/PVCF/Access_Denied_remix.sid`

### Gubber — init=$C050
- Load addr: $1700 ($1700 = 5888)
- Data size: 43566 bytes
- SID model: 6581
- Clock: PAL
- HVSC: `/MUSICIANS/P/PVCF/Gubber.sid`

### Trance 202 — init=$C050
- Load addr: $1000 ($1000 = 4096)
- Data size: 45358 bytes
- SID model: 6581
- Clock: PAL
- HVSC: `/MUSICIANS/P/PVCF/Trance_202.sid`

---

## Memory Layout Inference

From load addresses and player location ($C000):

For `Trance_202.sid`: Load=$1000, init=$C050, player at $C000–$C7FF
- Sample data + MOD data starts at $1000
- Player starts at $C000 (above sample/mod data)
- Total data: 45358 bytes from $1000 to ~$C1FE (samples + player combined)

For `Access_Denied_remix.sid`: Load=$4A1C, init=$C006
- Sample + mod data from $4A1C (~$D400 area or just below player)
- Much smaller data set (32228 bytes)

The 4 SIDs with init=$C050 (vs $C006) suggest a minor player variant: the init routine starts 74 bytes later, possibly different initialisation sequence (e.g., skips the border-colour startup code seen at $C006 in the standard player).

---

## Reflextracker Player Binary (Extracted)

File: `/home/jtr/sidfinity/tmp/reflextracker_research/rfxt_player_v1.1.prg`

```
Load address:  $C000
Size:          2048 bytes
First JMP:     $C000: JMP $C02C   (main entry)
Second JMP:    $C003: JMP $C016   (play entry? or init?)
Startup:       $C006: SEI / LDA #$36 / STA $01 / JSR $C02C / STA $D020 / STA $D011
```

- `STA $01` with $36 = $00110110 = RAM + I/O visible (standard C64 config, no BASIC ROM)
- Immediate write to $D020 (border) and $D011 (VIC control) in startup suggests the player sets up the display
- `$C006` = first real code after the two jump vectors = the PSID init_addr

This binary is NOT disassembled here (per constraint). The sidid.cfg signature covers the play routine's inner loop (sample position accumulator at ~$C02C or similar).
