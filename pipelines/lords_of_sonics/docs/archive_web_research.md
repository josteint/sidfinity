---
source_url: multiple (see per-section headers)
fetched_via: direct web fetch + web search
fetch_date: 2026-06-16
author: research agent
content_date: 2026-06-16
reliability: secondary (web sources) / primary (sidid.nfo, csdb.dk)
---

# LordsOfSonics/MS — Archive.org / Wayback Machine / Web Research

## Scope note

Archive.org search pages do not render JavaScript content via direct fetch; CDX API calls to
web.archive.org also failed (connection refused from the fetching environment). This file
therefore documents findings from:
1. CDX API attempts (all failed — noted as dead ends)
2. Web search + direct fetches of live and archived pages
3. sidid.nfo (primary source — human-readable player registry)
4. CSDb, VGMPF, Remix64, Chordian.net

Wayback Machine archived URLs tried (all failed with "unable to fetch from web.archive.org"):
- https://web.archive.org/cdx/search/cdx?url=*.lords-of-sonics.*&output=json&limit=20
- https://web.archive.org/cdx/search/cdx?url=*x-ample*&output=json&limit=30
- https://web.archive.org/web/*/http://www.lords-of-sonics.de/
- https://web.archive.org/web/*/http://lords-of-sonics.de/
- https://web.archive.org/web/*/http://www.markus-schneider.de/
- https://web.archive.org/web/*/http://www.x-ample.de/

Archive.org search pages tried (returned no rendered content):
- https://archive.org/search?query=%22Lords+of+Sonics%22
- https://archive.org/search?query=%22Parsec+Music+Editor%22

---

## 1. sidid.nfo — Canonical Player Registry

---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
fetched_via: direct
fetch_date: 2026-06-16
author: HVSC contributors (Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos)
content_date: ongoing (file in active repo)
reliability: primary
---

The sidid.nfo provides human-readable metadata for each player identified in sidid.cfg.
Verbatim extract for all LordsOfSonics / Compotech / X-Ample related entries:

```
LordsOfSonics/MS
   AUTHOR: Markus Schneider

(Compotech_V2.x)
     NAME: Compotech
   AUTHOR: Markus Schneider & Helge Kozielek
 RELEASED: 1990 X-Ample Architectures
REFERENCE: https://csdb.dk/release/?id=122614

(Parsec)
     NAME: The Parsec Music Editor
   AUTHOR: Markus Schneider (SMC), Nic & ADT
 RELEASED: 1989 Mnemonic Designs
REFERENCE: https://csdb.dk/release/?id=10744
```

```
Geir_Tjelta/Comptech-X
     NAME: Comptech-X
   AUTHOR: Geir Tjelta
 RELEASED: 2019 <?>
  COMMENT: First used in 2019 by Geir Tjelta and Markus Schneider, probably
           private player for X-Ample members.
```

### Key facts derived from sidid.nfo

1. **LordsOfSonics/MS** author = Markus Schneider only (no co-author for the base engine).

2. **The Parsec Music Editor** (the sub-variant detected by sidid as `(Parsec)`):
   - Authors: Markus Schneider (alias SMC), Nic, ADT
   - Released 1989 by Mnemonic Designs
   - CSDb: https://csdb.dk/release/?id=10744

3. **Compotech** (= X-Ample sub-variant, NOT LordsOfSonics/MS):
   - Authors: Markus Schneider & **Helge Kozielek**
   - Released **1990** by X-Ample Architectures
   - CSDb: https://csdb.dk/release/?id=122614
   - NOTE: CSDb release page lists Compotech V2.1 as August 1995 with THREE authors
     (Chap Bizarre, Joachim Fräder, Markus Schneider) — the 1990 date in sidid.nfo
     likely refers to the FIRST Compotech release; the CSDb entry is V2.1 (1995).

4. **Comptech-X** (Geir_Tjelta variant, NOT LordsOfSonics/MS):
   - Separate engine, first used 2019 by Geir Tjelta + Markus Schneider
   - Described as "probably private player for X-Ample members"
   - Relevant: 4 Schneider_Markus/ SIDs in HVSC are classified under this engine

---

## 2. Remix64 Interview with Markus Schneider

---
source_url: https://remix64.com/interviews/interview-markus-schneider.html
fetched_via: direct
fetch_date: 2026-06-16
author: Remix64 (interviewer unknown), Markus Schneider (interviewee)
content_date: May 11, 2001
reliability: primary
---

Interview confirmed biographical details (handle: Diflex, born 1970, Germany).
The interview did NOT mention: "Lords of Sonics", "Parsec Music Editor", "Compotech", or
technical details about his SID driver format.

Key quote about sound driver origin (paraphrased from the interview):
> "He [Jens Blidon] did some tunes with Chris Huelsbeck's well known soundmonitor but Jens
> didn't like soundmonitor that much. I promised him I'd write a better player."

This confirms the driver was written as a replacement for Soundmonitor, starting 1988.

Career note from interview: Schneider worked as CEO of a hardware company by 2001 and was no
longer commercially composing. He planned to begin remixing his C64 compositions.

---

## 3. VGMPF Wiki — Markus Schneider

---
source_url: https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider
fetched_via: direct
fetch_date: 2026-06-16
author: VGMPF contributors
content_date: unknown (wiki, likely 2020s)
reliability: secondary
---

Full biography extract (paraphrased from page):

- Born: November 3, 1970 in Winsen, Lower Saxony, West Germany
- Aliases: Markus of Parsec, M. Schneider/X-ample, Diflex (1988–??), Synth-Man (1987–1988)
- Met Jens Blidon at Hermann-Billung-Gymnasium during a school project week (around 1987–1988)
- Blidon was composing with Soundmonitor; Schneider "spent 2 months in 1988 writing him a
  better sound driver" — this is the LordsOfSonics/MS engine
- Together they founded **Lords of Sonics**
- First commercial project: Timezone (Kingsoft/CP Verlag, Germany)
- In 1989, Blidon enlisted (military service); Schneider then collaborated with X-Ample
  Architectures, spending "7 weeks" merging sound drivers
- "One night in 1989, X-Ample invited Schneider to join as a composer and programmer"

Audio development tools noted:
- C64: "his own driver which evolved into The Parsec Music Editor and Compotech"
- Amiga: Chris Hülsbeck gave Schneider "a special version of TFMX-Editor for free" in 1990
- C64 SFX: used "ROM's Fix" for sound effects in Timezone

Self-described best C64 works: Rolling Ronny, No Mercy, Lethal Zone, Xiphoids

Aliases confirm "Parsec" name: alias "Markus of Parsec" — the Parsec Music Editor was central
enough to his identity that he adopted it as an alias.

---

## 4. CSDb — Lords of Sonics Group Page

---
source_url: https://csdb.dk/group/?id=757
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: ongoing
reliability: primary
---

Group: Lords of Sonics (LOS), Germany
Founded: 1988
Type: Demo Group + Music Group
User rating: 8.5/10 (9 votes)

Members:
- Jens Blidon (ex-member, 1988–) — Musician
- Markus Schneider (ex-member, 1988–) — Musician

Releases (7 total, all downloadable as D64/PRG):

| Title | Year | Type |
|-------|------|------|
| Demo Musics | 1989 | Music |
| Double Density | 1989 | Music |
| No Mercy Music | 1989 | Music |
| No Mercy Title | 1989 | Music |
| Babylon Five | 1988 | One-File Demo |
| Beyond the Zero | 1988 | Music |
| The Music of Platou | 1988 | Music |

NOTE: All these releases are downloadable from CSDb. The D64 disk images contain the actual
LordsOfSonics/MS player binary embedded — primary source for disassembly.

---

## 5. CSDb — The Parsec Music Editor V5.1

---
source_url: https://csdb.dk/release/?id=10744
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: 1989 (tool), ongoing (database entry)
reliability: primary
---

- Title: The Parsec Music Editor V5.1
- Released: 1989 by Mnemonic Designs
- Type: C64 Tool

Credits:
- Code: ADT, Markus Schneider (Lords of Sonics, X-Ample Architectures), Nic
- Music (demo): Jeroen Tel (Maniacs of Noise) — tune "Tomcat" used in editor release
- Graphics: Kee
- Bug-Fix & Docs: SMC (Pretzel Logic)

IMPORTANT: "SMC" in the credits (Bug-Fix & Docs) is distinct from Markus Schneider (Code).
The sidid.nfo credits Schneider as "SMC" but the CSDb credits list "SMC" separately from
Schneider — this may mean sidid.nfo's "(SMC)" is incorrect, or SMC = another handle.

Downloads available:
- Parsec_5_1-Mnemonic_Designs.d64 (389 downloads as of 2026-06-16)
- Parsec_4_info.t64 (137 downloads, alternate version from Ruthless Music Disk)
- External mirror: pokefinder.org

Version numbers: V5.1 confirmed as the main release. A V4 version also exists (Parsec_4_info.t64).

Additional CSDb entries for Parsec:
- CSDb #169438: Parsec Music Editor V5.1 — crack by Raiders of the Lost Empire (1991)
- CSDb #200549: Parsec Music Editor V5.1 — crack by X-Plicit (February 1991)

The crack dates (1991) confirm the tool was in active circulation in the scene at least through
1991, roughly 2 years after its 1989 release.

---

## 6. CSDb — Compotech V2.1

---
source_url: https://csdb.dk/release/?id=122614
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: August 1995 (tool), ongoing (database entry)
reliability: primary
---

- Title: Compotech V2.1 (also listed as Comptech V2.1)
- Released: August 1995 by X-Ample Architectures
- Type: C64 Tool
- Downloads: 451 (D64 disk image)
- External mirror: pokefinder.org

Credits:
- Code: Chap Bizarre (X-Ample Architectures)
- Code: Joachim Fräder (X-Ample Architectures)
- Code: Markus Schneider (Lords of Sonics, X-Ample Architectures)

DISCREPANCY: sidid.nfo credits Compotech to "Markus Schneider & Helge Kozielek, 1990".
The CSDb V2.1 entry (1995) credits Chap Bizarre + Joachim Fräder + Markus Schneider —
Helge Kozielek not listed. Likely the 1990 first version had different authorship than V2.1.

Helge Kozielek is listed as a former/inactive member of X-Ample Architectures in their group
CSDb page — this is consistent with him coding an earlier Compotech version.

---

## 7. CSDb — X-Ample Architectures Group Page

---
source_url: https://csdb.dk/group/?id=245
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: ongoing
reliability: primary
---

- Founded: July 1988, Germany
- Tagline: "Bit For Bit A Hit"
- Total releases: 92 (1988–2017)

Active members including Markus Schneider:
- Markus Schneider (Coder/Musician, from March 1989) — joined after Lords of Sonics era
- Thomas Detert (Musician, July 1988–) — has own X-Ample sidid variant "(Thomas_Detert)"
- Michael Detert (Graphician, July 1988–)
- Joachim Multermann (Coder, 1989–)
- Thomas Heinrich (Graphician, July 1988–)

Inactive/former: Helge Kozielek, Mr. Cursor, Cameron, Chap Bizarre, General X, Joachim Fräder,
ME, Plasticman, Stephen Taylor, Takashi, The Viking, Tomcat, TPA

Tool release: Compotech V2.1 (August 1995) is listed as one of X-Ample's releases.

Note: "Double Density" was their commercial publishing imprint, created by Walter Konrad.
Not to be confused with Lords of Sonics' "Double Density" music release (1989).

---

## 8. CSDb — Markus Schneider Scener Page

---
source_url: https://csdb.dk/scener/?id=6003
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: ongoing
reliability: primary
---

Aliases:
- Handle: Markus Schneider (MS)
- Other: Diflex (1988–??), Synth-Man (1987–1988)
- Country: Germany
- Professions: Coder, Musician

Group affiliations:
- X-Ample Architectures (from March 1989 — current/primary)
- Lords of Sonics (1988–) — founding member
- Elite (former)

Notable quote: "I hate Disco Tunes! But i do what people want."

Music releases (partial, 1990–1992 era):
- Crown Music, Magic Mouse Music, Think Cross Music, Lethal Zone Music, Rolling Ronny Music,
  Transworld Music, Turn It II Music, Monster Business Music, Warrior of Darkness Music,
  Xiphoids Music, Disco Techno Music

Tool releases:
- Compotech (1992) — listed as a C64 Tool
- Compotech V2.1 (1995) — updated version

Note: Two Compotech entries exist on his scener page: 1992 and 1995. The 1992 entry may be
the first public release (aligns with "1990" in sidid.nfo as initial development, 1992 as
first public tool release, 1995 as V2.1 update). This resolves the sidid.nfo date discrepancy.

Total release count: 200+ releases between 1990–2026 (games, demos, diskmags, music collections).

---

## 9. CSDb — SID Technical Data (No Mercy)

---
source_url: https://csdb.dk/sid/?id=25604
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: ongoing
reliability: primary
---

No_Mercy.sid (Markus Schneider, 1989):
- Load Address: $0F52
- Init Address: $8C4A
- Play Address: $0000 (interrupt-driven)
- Songs: 13
- SID model: 6581
- Clock: PAL
- Data Size: 32,060 bytes ($7D3C)
- HVSC path: /MUSICIANS/S/Schneider_Markus/No_Mercy.sid

Play address $0000 = interrupt-driven player (NMI or IRQ vector; play called automatically
by the hardware timer, not by the calling program). This is the RSID/real-hardware style.

The load address $0F52 and init at $8C4A with a 32KB binary suggests the engine + all 13
subtunes (music data) are packed into one large SID file. This is consistent with a
multi-subtune game music dump.

---

## 10. CSDb — SID Technical Data (Lingo)

---
source_url: https://csdb.dk/sid/?id=25598
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: ongoing
reliability: primary
---

Lingo.sid (Markus Schneider, 1989):
- Load Address: $A000
- Init Address: $A003
- Play Address: $A000
- Songs: 1
- SID model: 6581
- Clock: PAL
- Data Size: 2,448 bytes ($0990)
- HVSC path: /MUSICIANS/S/Schneider_Markus/Lingo.sid

Play address = load address ($A000) — the play routine starts at the very beginning of the
loaded block. Single-song, small (2.4KB). This is a simpler single-tune format compared
to the large multi-subtune No_Mercy.

---

## 11. CSDb — SID Technical Data (Crockett's Theme by Jens Blidon)

---
source_url: https://csdb.dk/sid/?id=3847
fetched_via: direct
fetch_date: 2026-06-16
author: CSDb contributors
content_date: ongoing
reliability: primary
---

Crocketts_Theme.sid (Jens Blidon, 1987 — Lords of Sonics):
- Load Address: $A000
- Init Address: $C000
- Play Address: $C475
- Songs: 1
- SID model: 6581
- Clock: PAL
- Data Size: 11,349 bytes ($2C55)
- HVSC path: /MUSICIANS/B/Blidon_Jens/Crocketts_Theme.sid

NOTE: Dated 1987 (pre-Lords of Sonics founding by one year per VGMPF; group founded 1988).
This may use Soundmonitor (Blidon's original tool) rather than the LordsOfSonics/MS engine.
The init/play addresses ($C000/$C475) differ structurally from the Lingo addresses ($A000/$A003).
Load starts at $A000 but play is at $C475 — the engine is large (~11KB), consistent with
a multi-part structure or early Soundmonitor format.

The 1987 date predates Schneider writing the driver — confirms this is likely Soundmonitor,
NOT LordsOfSonics/MS. This SID in HVSC should be classified under a different engine.

---

## 12. VGMPF/Remix64/Web — Game Credits Using LordsOfSonics/MS

---
source_url: multiple
fetched_via: direct + web search
fetch_date: 2026-06-16
reliability: secondary
---

Games confirmed to use Markus Schneider music (1988–1992):

| Game | Year | Publisher | Notes |
|------|------|-----------|-------|
| Timezone | 1989 | Kingsoft / CP Verlag (Germany) | First commercial; co-composed with Jens Blidon |
| No Mercy | 1989 | Golden Disk 64 / CP Verlag | 13 subtunes; 32KB SID |
| Magic Events | 1988 | — | Co-composed with Johann Hartmut Stoeten |
| Babylon Four | 1988 | — | With Jens Blidon |
| Platou | 1988 | — | With Jens Blidon |
| Gravrace | ~1989 | — | Solo |
| Timerunner | ~1989 | — | Solo |
| Rolling Ronny | 1991–92 | Virgin Games | Schneider's stated best work |
| Lethal Zone | 1991 | Golden Disk 64 | Cybernoid-style; Schneider's stated best |
| Xiphoids | 1992 | Magic Disk 64 | Multi-scrolling shooter; stated best |
| Dick Tracy | 1990 | — | Arranged from Amiga version |
| Project S.O.L. | ~1991 | — | |
| Django | 1990-09 | — | |
| Crown | ~1992 | — | |
| Gilded Age | ~1992 | — | |

For Amiga work (from 1989–1990 onward): used TFMX-Editor (not his own C64 engine).

The pre-1989 games (Timezone, No Mercy, Platou, Babylon Four) almost certainly use the
LordsOfSonics/MS engine. The 1990+ titles may use Compotech (X-Ample era engine).

---

## 13. Chordian.net — C64 Music Editors List

---
source_url: http://chordian.net/c64editors.htm
fetched_via: direct
fetch_date: 2026-06-16
author: Chordian (blog.chordian.net)
content_date: as of Feb 2018 post; no longer updated
reliability: secondary
---

The comparison table does NOT include Parsec Music Editor or Compotech among its 14 compared
editors. A blog post (https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/)
notes a user comment by Deejay/XAP (April 11, 2018):

> "There is one editor missing: The Compotech Editor from X-Ample & Lords of Sonic"
> (with link to CSDb #122614)

The post adds: "This table will no longer be updated with additional editors or newer editor
updates. Most of its information has been moved to the list of editors in DeepSID."

Action: The DeepSID editor list (https://deepsid.chordian.net/?tab=player) may have a
Compotech/Parsec entry. DeepSID is actively maintained.

---

## 14. HVSC Musicians.txt

---
source_url: https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/Musicians.txt
fetched_via: direct
fetch_date: 2026-06-16
author: HVSC contributors
content_date: ongoing (HVSC #84)
reliability: primary
---

Verbatim entries found:

```
Schneider, Markus / Lords of Sonics / Warriors of Darkness - GERMANY
Blidon, Jens / Lords of Sonics - GERMANY
```

Group entry:
```
Lords of Sonics (LoS)
```

Notes:
- Schneider is listed as member of "Warriors of Darkness" group in addition to Lords of Sonics
  (this may be a game/demo he coded for)
- Blidon is listed as Lords of Sonics only
- The "(LoS)" abbreviation in the groups section confirms the HVSC abbreviation used

---

## 15. Rolling Ronny — Developer Interview

---
source_url: https://commodoreformatarchive.com/the-making-of-rolling-ronny/
fetched_via: direct
fetch_date: 2026-06-16
author: Commodore Format Archive
content_date: unknown (archive interview)
reliability: secondary
---

Quote from Oliver (game developer):
> "Markus composed the new tunes at home far away and we had some issues with the delivery.
> Nevertheless the whole soundtrack reached us in time and its implementation went smoothly."

Memory constraints note:
> "there was not a single byte left for menu screens and such"

No technical information about the music driver/player used. The "implementation went smoothly"
suggests Schneider delivered pre-assembled SID binaries (not source) — consistent with a
self-contained player + data block that the game code simply called.

---

## Dead Ends / Failed Fetches Summary

| URL | Result |
|-----|--------|
| web.archive.org CDX API (all variants) | Connection refused — environment cannot reach web.archive.org |
| archive.org/search?query=... | Returns only page navigation, no rendered results |
| http://www.xample-music.com/sids.html | ECONNREFUSED (domain dead) |
| http://artscene.textfiles.com/music/c64/HVSC/Schneider_Markus/ | Timeout (60s) |
| https://deepsid.chordian.net/ (player tab) | Cannot retrieve dynamic JS-rendered player tabs |

---

## Leads to Follow

1. **Download Parsec Music Editor V5.1 disk image** from CSDb #10744:
   `Parsec_5_1-Mnemonic_Designs.d64` (389 downloads) — this is the primary source for
   the actual player binary. Disassembling this .d64 will reveal the full player source.
   URL: https://csdb.dk/release/?id=10744

2. **Download Compotech V2.1 disk image** from CSDb #122614 — D64 available.
   May contain the evolved engine with better-commented data structures.

3. **Download Lords of Sonics releases from CSDb** — 7 releases, all have downloads:
   - No Mercy Music (1989): https://csdb.dk/release/?id=<look up>
   - Double Density (1989): https://csdb.dk/release/?id=<look up>
   - The Music of Platou (1988): earliest confirmed LOS release
   Each D64 contains the embedded player binary + music data → primary decompilation target.

4. **DeepSID player tab** — navigate to a LordsOfSonics/MS SID in DeepSID and check the
   "Players" tab: https://deepsid.chordian.net/?file=MUSICIANS%2FS%2FSchneider_Markus%2FLingo.sid&tab=player
   May show player name, version, and any human-readable metadata from DeepSID's database.

5. **Crockett's Theme engine check** — HVSC classifies this under Jens Blidon / Lords of Sonics
   but the 1987 date + different address layout suggests it may be Soundmonitor, not LordsOfSonics/MS.
   Run sidid on `MUSICIANS/B/Blidon_Jens/Crocketts_Theme.sid` to confirm engine classification.

6. **WilfredC64/player-id sidid.nfo** — fetch the raw .nfo from WilfredC64 repo to see if it
   has any additional LordsOfSonics notes beyond the cadaver version:
   https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.nfo

7. **Archive.org game disk images** — search for the actual game disk images containing
   Schneider's music. These would embed the player binary directly:
   - Rolling Ronny: https://archive.org/search?query=%22Rolling+Ronny%22+C64
   - No Mercy: https://archive.org/search?query=%22No+Mercy%22+C64+Kingsoft
   - Lethal Zone / Xiphoids: similar searches
   These are better than SID dumps for studying the player in its natural habitat.

8. **X-Ample website** (www.xample-music.com / xap64.de) — these domains appear dead
   (ECONNREFUSED) but may be archived in Wayback Machine. Try:
   https://web.archive.org/web/*/www.xample-music.com/
   (requires a browser environment that can reach web.archive.org)

9. **CSDb release IDs for LOS music** — look up the specific CSDb release IDs for the 7 Lords
   of Sonics releases to get their direct D64 download links. The group page
   (https://csdb.dk/group/?id=757) lists all 7 with download links.

10. **Markus Schneider CSDb SID list** — https://csdb.dk/scener/?id=6003 shows his full
    composition list. Identify which SIDs are pre-1989 (LordsOfSonics/MS) vs 1989+ (X-Ample)
    and cross-check with sidid detection results from the local HVSC corpus.

11. **Compotech 1992 vs 1995** — the scener page lists Compotech (1992) and Compotech V2.1
    (1995) as separate tool entries. The 1992 entry may have its own CSDb page with D64 image.
    Search CSDb for "Compotech 1992" to find this earlier version.

12. **8Bit Mayhem podcast** — has a Lords of Sonics track (Birthday 1988) in Episode #6 but
    no technical content. The actual audio episode mp3 may contain scene discussion.
    URL: https://www.atlantis-prophecy.org/recollection/?load=8bit_mayhem
