---
source_url: hvsc84.db (local read-only query) + HVSC Musicians.txt
fetched_via: direct (local DB)
fetch_date: 2026-06-15
author: HVSC team
content_date: HVSC #84
reliability: primary
---

# HVSC #84 Ariston corpus — statistics and file inventory

## Corpus size

Total SID files identified as engine='Ariston' by sidid: **147**

(research.md previously said 148 — off by 1, likely a counting artifact.)

## Composer breakdown

| Composer dir        | Count (approx) | Notes                                     |
|---------------------|----------------|-------------------------------------------|
| Beben_Wally         | 28             | Co-author; most prolific user             |
| Crabtree_Ian        | 21             | Creator                                   |
| Barrett_Steve       | 21             | Codemasters composer                      |
| Wilson_Mark         | 19             | UK demo scene + commercial                |
| Scales_Neil         | 10             | Ariston Design group member               |
| Sharp_Lyndon        | 3              |                                           |
| Brimble_Allister    | 4              | Early work before Delaney custom driver   |
| Perdita             | 10             | Sandra Park, UK                           |
| Dunn_Jonathan       | 2              | Matchday_II, Subterranea                  |
| Gray_Matt           | 4              | Early Codemasters tunes                   |
| Leitch_Barry        | 2              | Captain_Courageous, Marauder              |
| Harris_Denis        | 2              | Ariston Design                            |
| Kendal              | 2              |                                           |
| Deadman             | 1              | Colossus_Chess_Atari_ST                   |
| DEMOS/GAMES (misc)  | ~13            | Energy Warrior, Street Fighter, etc.      |

## SID header survey (selected tunes)

| File                        | Real load | Init   | Play   | Songs | Size  |
|-----------------------------|-----------|--------|--------|-------|-------|
| Crabtree/Outrun.sid         | $2000     | $2003  | $2000  | 1     | 2841  |
| Crabtree/Technicolour_1.sid | $6000     | $6003  | $6000  | 1     | 4317  |
| Crabtree/Going_Home.sid     | $6000     | $6003  | $6000  | 1     | —     |
| Beben/Tetris.sid            | $4000     | $7440  | $0000  | 1     | 13539 |
| Beben/Dark_Side.sid         | $0900     | $1628  | $0901  | 1     | 3374  |
| Beben/Inside_Outing.sid     | —         | $CBA5  | $C101  | 1     | —     |
| Leitch/Marauder.sid         | $1000     | $1000  | $10C2  | 6     | 6464  |
| Dunn/Matchday_II.sid        | $C000     | $CF00  | $C001  | 2     | 3847  |
| Gray/Quedex.sid             | $4000     | $4B79  | $4BB3  | 9     | 14292 |
| Wilson/Galdregons_Domain.sid| $4000     | $6A70  | $0000  | 1     | 10909 |
| Barrett/Super_Hang-On.sid   | —         | $F100  | $E002  | 4     | —     |

Notes:
- All tunes use PAL clock, speed=0 (VBI-driven), 6581 chip
- No NTSC-specific variants found in corpus
- play=$0000 in some Beben tunes means no separate play address (init does everything,
  or play is embedded differently — needs investigation)
- Crabtree tunes: init = load+3, play = load — suggests 3-byte header at start of player
  (e.g. JMP player_loop at load; init starts at load+3)
- Marauder has 6 subtunes (multi-song with single engine instance)
- Quedex has 9 subtunes

## Load address variation

Player does NOT have a fixed load address — it is fully relocatable or
each composer placed it at a different origin:
- $0900 (Dark Side — very low memory, below screen)
- $1000 (Marauder)
- $2000 (Outrun)
- $4000 (Tetris, Quedex, Galdregons_Domain)
- $6000 (Technicolour_1, Going_Home)
- $C000 (Matchday_II)
- $CBA5 (Inside_Outing)
- $F100 (Super_Hang-On — unusually high, possibly relocated/compressed)

This wide scatter confirms composers assembled the driver at arbitrary origins.

## Corpus anomalies

- Beben/Tetris: play=$0000, data size=13539 bytes (very large — 26-minute song)
- Wilson/Galdregons_Domain: play=$0000, data size=10909 bytes (long tune, 1 subtune)
- Some Beben tunes use other drivers (David_Whittaker, Adam_Gilmore, Colleen,
  Antony_Crowther_V2, Soundmonitor, Electrosound) — not all Beben == Ariston

## HVSC Musicians.txt references

Ariston Design is listed as a C64 music group.
Members identified:
- Denis Harris (Mole {Moley}) / Ariston Design — UNITED KINGDOM
- Neil Scales (Neil) / Ariston Design / N.W.C.U.G — UNITED KINGDOM

Other composers have no group affiliation listed but use the same engine.

Neil Baldwin ("Demon") is mentioned in Recollection article as a scener
who used Ariston (also used Electrosound), though HVSC does not classify
his SIDs as Ariston (he used his own driver).
