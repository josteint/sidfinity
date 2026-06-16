---
source_url: https://csdb.dk/scener/?id=6003
fetched_via: direct
fetch_date: 2026-06-16
author: unknown
content_date: unknown
reliability: primary
---

# Markus Schneider — CSDb Scener Page

**CSDb Scener ID:** 6003
**URL:** https://csdb.dk/scener/?id=6003

## Identity

- **Real Name:** Markus Schneider
- **Country:** Germany
- **Functions:** Coder, Musician

## Handles / Aliases

| Handle | Period |
|--------|--------|
| Markus Schneider / MS | Primary |
| Diflex | 1988–?? |
| Synth-Man | 1987–1988 |

## Group Memberships

| Group | Role | Period | Status |
|-------|------|--------|--------|
| X-Ample Architectures | Coder/Musician | 3-1989+ | Current |
| Lords of Sonics | Musician/Founder | 1988+ | Former (ex-member) |
| Elite | — | — | Former |

## Biographical Trivia

Markus Schneider is quoted as saying: **"I hate Disco Tunes! But I do what people want."**

## Role in the LordsOfSonics/MS Engine

Markus Schneider created the music player/editor that became known as:
1. **Lords of Sonics Music Editor** (original, 1988–1989 era)
2. **The Parsec Music Editor V5.1** (1989, distributed via Mnemonic Designs / Ruthless)
3. **Compotech** (1992, X-Ample Architectures release)
4. **Compotech V2.1** (1995, X-Ample Architectures release)

The HVSC SIDID engine tag "LordsOfSonics/MS" credits Markus Schneider as the engine author.

## Selected Game Credits

| Game | Year | Publisher |
|------|------|-----------|
| Rolling Ronny | 1991 | Virgin Games / Starbyte Software |
| No Mercy | 1990 | Fairlight |
| Lethal Zone | 1991 | (Golden Disk 64/CP Verlag) |
| Xiphoids | 1992 | Magic Disk 64/CP Verlag |
| Think Cross | ~1990–1992 | — |

## HVSC Music Directory

All of Markus Schneider's HVSC contributions are under:
`/MUSICIANS/S/Schneider_Markus/`

Known SIDs (from CSDb listing of 109+ results):
- Markus_Schneider_01.sid (1988, load $1000, init $100D, play $1013, data 2414 bytes)
  - Note: different init/play addressing than standard LOS format
- Beyond_the_Zero.sid (1988, load $1C00/init $1C03/play $1C00, 3158 bytes)
- Double_Density_Commercial.sid (1989, load $A000/init $A003/play $A000, 2816 bytes)
- No_Mercy.sid (1989, load $0F52/init $8C4A/play $0000, 13 songs, 32060 bytes)
- Rolling_Ronny.sid (1991, load $2000/init $2003/play $2000, 4 songs, 4864 bytes)
- Lethal_Zone.sid (1991, load $1000/init $1003/play $1000, 10 songs, 7873 bytes)
- Xiphoids.sid (1992, load $AA80/init $AA83/play $AA80, 5 songs, 4721 bytes)

## Address Pattern Observations

Most standard LOS engine SIDs follow the pattern:
- Init address = Load address + 3
- Play address = Load address
This matches a simple engine layout where the init subroutine begins at the 4th byte (the first 3 bytes are typically a JMP instruction to the main play loop or initialization code).

The early 1988 SID (Markus_Schneider_01) uses a different layout (init $100D, play $1013), suggesting the engine format evolved early on.

The No_Mercy.sid has an unusual init at $8C4A (far from load at $0F52), suggesting a music disk with player at the high address and data elsewhere.

## Discography Note

The "Thomas Detert & Markus Schneider Music Collection (160 Tracks)" (1995, The Party) is a major compilation of both composers' work from ~1990–1994, released at the demoscene party The Party 1995. It contains tracks titled: Another World, Apoxoly, Circuit, multiple Magic Disk 64 and Game On entries, Lost Ninja, Parsec, and Zillion.

## Active Since Retirement

Despite the group being inactive, Markus Schneider has continued contributing to recent releases (2025–2026):
- 41 Neurons (2026)
- Happy New Year 2025 (2025)
- RecrackInc25 (2025, Hokuto Force)
