---
source_url: https://csdb.dk/group/?id=245
fetched_via: direct
fetch_date: 2026-06-16
author: unknown
content_date: unknown
reliability: primary
---

# X-Ample Architectures (XAP) — CSDb Group Page

**CSDb Group ID:** 245
**URL:** https://csdb.dk/group/?id=245
**Website:** http://www.xap64.de
**Aliases:** Xample, X-Ample

## Basic Information

- **Tagline:** "Bit For Bit A Hit"
- **Founded:** July 1988
- **Country:** Germany
- **Group Types:** Demo Group, Game Development Group
- **User Rating:** 8.8/10 (22 votes), 9/10 (10 public votes)
- **Total Documented Releases:** 92

## Name Etymology

The name stands for "Example," as stated in the release "Blade Runner."

**Note:** "Double Density" was NOT an official publishing label for X-Ample but rather a label created by Walter Konrad from CP Verlag for software acquisition.

## Founders

- Stephen Taylor (Musician)
- Takashi (Graphician/Musician)
- General X (Graphician)
- Chap Bizarre (Coder)

## Full Membership

### Active/Current Members
| Handle | Role | Since |
|--------|------|-------|
| Joachim Multermann | Coder | 1989+ |
| Markus Schneider | Coder/Musician | 3-1989+ |
| Michael Detert | Graphician | 7-1988+ |
| Thomas Detert | Musician | 7-1988+ |
| Thomas Heinrich | Graphician | 7-1988+ |

### Inactive Members
| Handle | Role | Since |
|--------|------|-------|
| Helge Kozielek | Coder | 7-1988+ |
| Mr. Cursor | Coder | 3-1989+ |

### Ex-Members
- Cameron (1988)
- Chap Bizarre (Coder, 7-1988+)
- General X (Graphician, 7-1988+)
- Joachim Fräder (Coder, 1989–2005)
- ME (1988)
- Plasticman (Coder/Swapper, 1988)
- Stephen Taylor (Musician, 7-1988+)
- Takashi (Graphician/Musician, 7-1988+)
- The Viking (Coder, 1988–1989)
- Tomcat (1988)
- TPA (Graphician)

## Relevance to LordsOfSonics/MS Engine

Markus Schneider joined X-Ample in March 1989 (from Lords of Sonics). X-Ample subsequently developed and maintained the music tools:

### Tools/Utilities Released by X-Ample
| Release | ID | Year | Type |
|---------|----|------|------|
| Compotech | 130599 | 7-1992 | C64 Tool |
| Compotech V2.1 | 122614 | 8-1995 | C64 Tool |
| X-Ample Intro Architect | 17823 | 1989 | C64 Tool |

### Compotech Credits
Both Compotech (1992) and Compotech V2.1 (1995) were coded by:
- Chap Bizarre
- Joachim Fräder
- Markus Schneider

### Compotech Technical Notes (from user comments)

From user comment on the 1992 crack release (ID 82103):
> "I had to use Compotech V2.1 to load the demo tune, save as turboass format and merge to the provided '.PLAYER-ROUTINE' to be able to generate a working executable, because this version does only save the packed data."

This confirms the Compotech workflow:
1. Compotech composes and saves **packed data** (not a standalone SID)
2. The packed data is combined with a separate **'.PLAYER-ROUTINE'** to form a playable executable
3. V2.1 adds the ability to save in turboass format

## Game Work by X-Ample

Games with music by Markus Schneider (LOS/XAP engine):
- Rolling Ronny (1991/1992) — Music: Markus Schneider; Code: Mario Knezovic; Graphics: Veto/Oliver Lindau; Publisher: Virgin Games/Starbyte
- No Mercy (1990) — Music: Markus Schneider; Code: Gollum (Fairlight); Publisher: Fairlight
- Lethal Zone (1991) — Music: Markus Schneider
- Xiphoids (1992) — Music: Markus Schneider; Published in Magic Disk 64

## X-Ample Intro Architect (1989)

- Code: Joachim Fräder
- Music: Markus Schneider + Stefan Hartwig + Thomas Detert
- Contains 12 SID files (1 Detert + 11 Hartwig numbered)

## Key SID Technical Details for Schneider's X-Ample Era Tunes

### Rolling Ronny (1991)
- HVSC: `/MUSICIANS/S/Schneider_Markus/Rolling_Ronny.sid`
- Load: $2000 / Init: $2003 / Play: $2000
- Songs: 4, SID: 6581, PAL, Data: 4864 bytes ($1300)

### Lethal Zone (1991)
- HVSC: `/MUSICIANS/S/Schneider_Markus/Lethal_Zone.sid`
- Load: $1000 / Init: $1003 / Play: $1000
- Songs: 10, SID: 6581, PAL, Data: 7873 bytes ($1EC1)

### Xiphoids (1992)
- HVSC: `/MUSICIANS/S/Schneider_Markus/Xiphoids.sid`
- Load: $AA80 / Init: $AA83 / Play: $AA80
- Songs: 5, SID: 6581, PAL, Data: 4721 bytes ($1271)
