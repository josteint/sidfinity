# SID Player Documentation

Research on all major C64 SID music players identified in HVSC #84 via sidid.
Players identified using [cadaver/sidid](https://github.com/cadaver/sidid) signature database.

## Coverage Summary

| Tunes | Player | Doc File | Source Available |
|------:|--------|----------|:---:|
| 10,738 | DMC (Demo Music Creator) | [dmc.md](dmc.md) | No |
| 7,550 | GoatTracker V2 | [goattracker.md](goattracker.md) | Yes |
| 6,403 | Music Assembler | [music_assembler.md](music_assembler.md) | No |
| 4,085 | Future Composer | [future_composer.md](future_composer.md) | No |
| 3,678 | JCH NewPlayer | [jch_newplayer.md](jch_newplayer.md) | Yes (player) |
| 3,663 | Soundmonitor | [soundmonitor.md](soundmonitor.md) | No |
| 1,384 | GoatTracker V1 | [goattracker.md](goattracker.md) | Yes |
| 1,170 | HardTrack Composer | [hardtrack_master_composer.md](hardtrack_master_composer.md) | Yes |
| 1,075 | Master Composer | [hardtrack_master_composer.md](hardtrack_master_composer.md) | No |
| 1,074 | SidWizard | [sidwizard.md](sidwizard.md) | Yes |
| 994 | SIDDuzz'It | [sidduzzit.md](sidduzzit.md) | Yes (player) |
| 950 | SoedeSoft | [soedesoft_digitalizer_romuzak.md](soedesoft_digitalizer_romuzak.md) | No |
| 680 | Digitalizer | [soedesoft_digitalizer_romuzak.md](soedesoft_digitalizer_romuzak.md) | No |
| 593 | RoMuzak | [soedesoft_digitalizer_romuzak.md](soedesoft_digitalizer_romuzak.md) | No |
| 446 | GMC/Superiors | [gmc_xample_sidfactory.md](gmc_xample_sidfactory.md) | No |
| 387 | X-Ample | [gmc_xample_sidfactory.md](gmc_xample_sidfactory.md) | No |
| 380 | SidFactory II | [gmc_xample_sidfactory.md](gmc_xample_sidfactory.md) | Yes |
| 289 | Rob Hubbard | [rob_hubbard.md](rob_hubbard.md) | No (disassembly exists) |
| ~2,325 | 8 smaller players | [smaller_players_1.md](smaller_players_1.md) | Mixed |
| ~2,146 | 10 smaller players | [smaller_players_2.md](smaller_players_2.md) | Mixed |
| ~1,577 | 12 smaller players | [smaller_players_3.md](smaller_players_3.md) | Mixed |

**Total identified:** 59,267 / 60,572 (97.8%)
**Unidentified:** 1,305 (2.2%)

## Best-Documented Formats (for ML training data extraction)

These players have the most complete format documentation, making them the best candidates for extracting music data:

1. **GoatTracker V2** (7,550) — full .sng format spec, packed SID format documented, open source player
2. **SID-Wizard** (1,074) — SWM format spec in source, open source player
3. **SIDDuzz'It** (994) — 65KB documentation file, player source available
4. **JCH NewPlayer** (3,678) — Codebase64 format doc, CheeseCutter open source port
5. **CheeseCutter** (306) — open source (GitHub), ACME assembler player
6. **SID Factory II** (380) — open source (GitHub), modular driver system
7. **NinjaTracker** (97) — open source player (nt2play.s)
8. **HardTrack Composer** (1,170) — source available at elysium.filety.pl

## Players by Architecture Type

### Tracker-style (pattern/sequence based)
GoatTracker, JCH NewPlayer, SidWizard, SIDDuzz'It, CheeseCutter, SidFactory II, NinjaTracker, HardTrack, DMC, CyberTracker, DefMon, OdinTracker, John Player

### Assembler/compiler (code + compressed data)
Music Assembler, Rob Hubbard (hand-coded), David Whittaker (hand-coded MML)

### Bar/block/page editors
Master Composer, Soundmonitor, Electrosound, MusicShop

### Game music drivers (no GUI, compose in source)
Ariston, MoN/Deenen, LordsOfSonics/MS, Vibrants/JO
