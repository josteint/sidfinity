---
source_url: https://web.archive.org/web/20210708043156/http://tehernaplo.blog.hu/2013/05/28/lavor_a_felyetekre, https://csdb.dk/release/?id=10758, https://csdb.dk/release/?id=2629, https://csdb.dk/release/?id=24719, https://demozoo.org/sceners/1711/
fetched_via: wayback 2021-07-08
fetch_date: 2026-04-11
author: multiple sources (Brian/Graffity interview via tehernaplo.blog.hu 2013; CSDb community; Demozoo)
content_date: 2013-05-28 (Graffity interview); 1991-1997 (CSDb release dates)
reliability: primary
---

# DMC Variants, Relocators, and People

Research compiled from CSDb, Demozoo, scene.hu, and Wayback Machine archives.

---

## 1. DMC Relocator by Graffity (1991)

**URL:** https://csdb.dk/release/?id=10758
**Author:** Brian / Graffity
**Year:** 1991

The original DMC Relocator, written by Brian himself. This is significant because a relocator must understand the complete memory layout to patch all address references. Three slightly different versions are available as downloads:

- `Music Mania.zip` (original package)
- `DMC 2 Relocator.zip` (for DMC V2)
- `DMC 4 Relocator.zip` (for DMC V4)

The existence of separate V2 and V4 relocators confirms that the data layout changed between these major versions. The relocator binaries themselves could be disassembled to determine exactly which memory regions contain relocatable addresses.

**User comment (bugjam, 2011-01-15):** "Added 2 other slightly different versions; if someone thinks they should get their own entries, please go ahead."

**Downloads to investigate:**
- https://csdb.dk/download.php?id=7935
- https://csdb.dk/download.php?id=122309 (DMC 2 Relocator)
- https://csdb.dk/download.php?id=122310 (DMC 4 Relocator)

---

## 2. DMC V4.0 Relocator V2.0 by Warriors of the Wasteland (1993)

**URL:** https://csdb.dk/release/?id=4386
**Authors:** Stormlord / Warriors of the Wasteland (code), The Syndrom / Crest (code + concept)
**Year:** 1993

A third-party relocator for DMC V4.0, written by Stormlord and The Syndrom. The Syndrom is significant -- he later wrote the editor for DMC V6 (per Brian's interview comments). The Syndrom having deep knowledge of DMC V4 internals (enough to write a relocator) makes sense given he later collaborated with Brian on editor code.

**Download:** https://csdb.dk/download.php?id=31904

---

## 3. DMC 4.0 Professional by Graffity and Onslaught (1995)

**URL:** https://csdb.dk/release/?id=2603
**AKA:** Demo Music Creator V4.0 pro
**Authors:** Brian / Graffity (code), Morbid / Onslaught (code + crack)
**Year:** 1995
**Groups:** Graffity, Onslaught

This is a "Pro" variant of DMC V4.0, a collaboration between Brian (original author) and Morbid. Morbid is credited for both "Code" and "Crack", suggesting he reverse-engineered parts of DMC V4.0 and added features. The fact that Brian is also credited means this was a semi-official enhancement.

No user comments or production notes are available on CSDb. The download could reveal what "Professional" features were added vs. standard V4.0.

**Download:** https://csdb.dk/download.php?id=10613

---

## 4. DMC 4.G by Samar Productions (1997)

**URL:** https://csdb.dk/release/?id=121358
**AKA:** Demo Music Creator System V4.G
**Authors:** Brian / Graffity (code), Glover / Samar Productions (code)
**Year:** 1997
**Group:** Samar Productions

"G" likely stands for "Glover" -- this is Glover's personal modification of DMC V4. Brian is still credited as the original coder. Samar Productions (Polish group) was active in the mid-to-late 1990s C64 scene.

Glover also released:
- **DMC V5.4** (https://csdb.dk/release/?id=36658) by Samar Productions
- **DMC V5.4 Packer** (https://csdb.dk/release/?id=137786) by Samar Productions

This suggests Glover was deeply familiar with DMC internals across multiple versions and made Polish-scene-oriented modifications.

**Download:** https://csdb.dk/download.php?id=151257

---

## 5. DMC V5.01B by Chaos (undated)

**URL:** https://csdb.dk/release/?id=236892
**AKA:** Demo Music Creator V5.01B
**Authors:** Brian / Graffity, The Imperium Arts, Tomcat (code); Zeux (bug-fix)
**Group:** Chaos

A late bugfixed variant of DMC V5.0. Notable details:
- Brian is credited under THREE groups: Graffity, The Imperium Arts, AND Tomcat (his early gymnasium group)
- **Zeux** is credited specifically for "Bug-Fix" -- confirming this is a patched version of the official V5
- Zeux also released a separate **DMC V5.1 Packer** (https://csdb.dk/release/?id=236893)

**Download:** https://csdb.dk/download.php?id=290907

---

## 6. DMC V7.0 by Unreal (1995) -- CRITICAL TECHNICAL DETAILS

**URL:** https://csdb.dk/release/?id=2629
**Authors:** Axl / Unreal (code), Brian / Graffity (original code), Ray / Unreal (code)
**Year:** 1995
**Group:** Unreal (Hungarian group)

### Summary (by Ray, 2002-02-17):
"Enhanced DMC 4.xx series by multiframing (up to 5 speeds), some pattern effects, bufixes and cassete support :)"

### Production Info (by Ray, 2005-12-02):
"Yes, this version have roots in V4. V5/V6 wasn't good as old V4 for our musicians, so, we decided to improve it and add new functions. For ex. 1-5 frames zaks, multiple channel plays and mainly, nicer editor. You can play from any note/line, see sector playing time, etc etc.... Later, TFX was born, because added code was 50% of original, so, it become nightmare to improve anything. There is also DMC 7.1 which includes many played improvemens (new commands and cappabilities). Early versions of TFX looks similar to DMC4, before PG changed it completly."

### User Comments:

**The Syndrom (2005-11-07):** "Please don't get it wrong - it's not really Version 7 of the famous DMC, the latest official version was v6.0. this one is still an adopted v4.0, which someone released as v7.0 without permission."

**Ray (2005-12-02):** "Yes, it have roots in DMC V4. In that time, there was V5/V6 allready, but they weren't good as original V4 from Brian. At least for our musicians. So, we decided to improve old V4 and we used V7. We added many new functions, from 1-5 multiple songs, multi channel play up to bigger editor improvements. You can play from any line or note, you see sector length, etc etc. Cassete recorder is also supported :) Because added code grows up to 50% of original Brian's size, it becomes nightmare to make new improvements. So, we decided to make TFX. Early versions of TFX looks like DMC, before PG completly changes it. **There also exists DMC V7.1. This release utilizes many player improvements. New commands and possibilites, mainly around filters and direct AD/SR sets.** 7.0 improves editor itselfs."

**Manex (2016-02-12):** "My first music editor for C64. This is probably the only editor with turbotape support, and in ninetees I had no diskdrive."

### Key technical takeaways:
1. **V7.0 is based on V4.0 player**, NOT V5/V6. The V4 player was preferred by musicians.
2. **"1-5 frames zaks"** = multiframe/multispeed support (1x to 5x per frame)
3. **"multi channel play"** = polyphonic playback?
4. **V7.1 adds PLAYER improvements** specifically:
   - **Filter commands** (new sector commands for SID filter control)
   - **Direct AD/SR sets** (new sector commands for direct ADSR register writes)
   - These are NEW SECTOR COMMANDS not present in V4.0
5. **TFX lineage:** TFX (The Final Expander) was born when V7 code got too bloated. Early TFX looked like DMC V4.

### SIDs used in the V7.0 release:
All by Vincenzo, confirming V7 was used by Hungarian musicians:
- 1 Minute Jamm, 20 Minutes, Binary Flow, Gazfroeccs, Kill Me, Non+Ultra (tunes 1-2), Soul Cemetary 2, Tavaly Charlie, Xtrafroccs

---

## 7. DMC V7.1 Beta by Unreal (1995)

**URL:** https://csdb.dk/release/?id=24719
**Authors:** Brian / Graffity (original code, credited), Axl + Ray / Unreal (modifications)
**Year:** 1995
**Group:** Unreal

The beta version with the player improvements Ray described.

### User Comments:

**Cybortech (2011-01-21):** "it's not with Graffity's official permission. it's an extended V4!"

**Ray (2005-12-02):** "This V7 have roots in V4. Please, see DMC V7.0 for more details. **This version improves mainly player and allow up to 6-speed musics.** It was never finished, because TFX was started instead of continuing improving original Brians's DMC."

### Key technical takeaways:
1. **Up to 6-speed** (6 calls per frame) -- extends V7.0's 5-speed limit
2. Player improvements include filter commands and direct ADSR sets (per Ray's V7.0 comments)
3. Never finished -- development moved to TFX instead
4. Based on V4 player, NOT V5/V6

**Downloads:**
- https://csdb.dk/download.php?id=27386 (from unreal64.net)
- https://csdb.dk/download.php?id=87726 (CSDb mirror)

---

## 8. Scene.hu / Tehernaplo Graffity Interview (2013)

**URL:** https://www.scene.hu/2013/05/30/lavor-a-felyetekre-graffity-megainterju-a-tehernaplon/
**Interview links (Wayback Machine):**
- Part 1: https://web.archive.org/web/20210708043156/http://tehernaplo.blog.hu/2013/05/28/lavor_a_felyetekre
- Part 2: https://web.archive.org/web/20130616104344/http://tehernaplo.blog.hu/2013/05/29/lavor_a_felyetekre_ii_resz

**Original links (may be down):**
- http://tehernaplo.blog.hu/2013/05/28/lavor_a_felyetekre
- http://tehernaplo.blog.hu/2013/05/29/lavor_a_felyetekre_ii_resz

A very long Hungarian-language interview with Graffity members (Brian, Jay, Cybortech, Maxwell, Cheesion, Clarence, Matrix). The interview is in two parts. Below are all DMC-relevant technical details, translated/summarized from Hungarian:

### Brian on the DMC lineage:

1. **GMC (Game Music Creator)** came first, created by Brian and Jay under "Superiors Aural Department (SAD)" within Graffity. They tried to sell it to Magic-Disk magazine but it was rejected.

2. **Mini Music Editor** existed before GMC (per Cybortech), released under Tomcat (Brian's pre-Graffity group).

3. **The "Sosperec" (Pretzel):** A secret, highly advanced music editor/player that only a few selected musicians got access to. Used only 8 raster lines. Brian describes it as "code-wise much more advanced than the DMC versions at that time (V2.x)." The Sosperec was NOT widely distributed -- "they sat on it, had no intention of distributing it" -- which is why DMC became more famous.

4. **SID datalogging technique:** Brian describes a technique used in the Sosperec: "We made a graphics viewer that turned off the SID, called the music player, read out the SID [registers], turned it back on, wrote back what it read, and displayed the music with sprites. This way we 'saw' what we heard -- what it actually means in the background. We stole the better effects from the big guys' music players, or at least learned how sounds are produced." Brian says he adopted this SID datalogging technique for DMC V5.

5. **DMC V5 design goals (Brian's own words):**
   - "I set the most important goal for DMC5: fit into $18 raster lines (3 characters) -- at that time almost every player consumed this much or even more!"
   - "And know every effect (from Hubbard to MON) that I'd encountered"
   - "The whole thing, editor and player, didn't take longer than a week"
   - "A graphical piano was planned for the bottom of the screen (like in earlier DMCs) but that was cut"
   - NOTE: $18 = 24 decimal raster lines

6. **DMC V6 (Brian's own words):**
   - "DMC6 was already in the picture (a max 8-line player)" -- meaning 8 raster lines maximum
   - "which we'd use when there's not enough time to compose music"
   - "The two players (5 and 6) were not far apart in time"
   - "For 6, I didn't feel like writing the editor, so I passed it to Syndrom who made something nicer and better than I ever would have :)"
   - "DMC6 was already such that during editing it consumed many rasters, but after packing it didn't"
   - "I believe 6 has not been released to this day, many people don't even know about its existence. In fact, older DMCs were modded and released with version number 6."

7. **Frequency table difference:** Maxwell notes: "The DMC ran with CGKOTY frequency tables while the Sosperec and AEINRW [used different ones], so Brian's music played a quarter tone lower than Trayse's in demos." This confirms different frequency table variants exist across DMC versions.

### Cybortech on Brian and The Imperium Arts:
"Around 93-94, Brian still collaborated with Syndrom on new players and music (The Imperium Arts), but no serious demo coding happened."

### Cybortech on the ADSR group and Sosperec player analysis:
"The Dynax demo group had a music division called ADSR, led by Cane. They were the only ones who got the Sosperec as a friendly gesture. [...] At some party, someone very tastelessly idolized the man [Brian] and his player, saying it makes sounds (e.g. filters) that no other player can. I thought I'd look into it. I examined one of their codes, extracted a Griff tune with player, and my jaw dropped -- it consumed a gigantic amount of raster time, I don't remember but at peak 3x as much as say DMC 2."

This confirms:
- The Sosperec player was very cycle-expensive (3x DMC V2)
- It had filter capabilities others lacked
- It was technically superior but impractical for demos

---

## 9. Brian's Demozoo Profile

**URL:** https://demozoo.org/sceners/1711/
**Handle:** Brian / GRF ^ TIA (Graffity, The Imperium Arts)
**Website:** http://bpstudio.hu/ (active, music-focused with SoundCloud/Bandcamp)

**Bio:** "Brian coded the sample editor DigiEditor V1.3 (90), and several versions of the Demo Music Creator (DMC)."

### Group memberships:
- Graffity (primary)
- The Imperium Arts (primary)
- Absolute! (previous)
- Axioma (previous)
- Soc. Brigade (previous)
- Tomcat (previous -- his gymnasium/school group)
- Toxic Volume (previous)

### DMC-related productions listed on Demozoo:
- **DMC v4.0** (https://demozoo.org/productions/350258/) -- Commodore 64 Tool
- **Demo Music Creator (DMC) System V1.2** (https://demozoo.org/productions/364586/) -- Commodore 64 Tool, credited as "Code (tool)"
- **The Superiors Demo Music Creator V2.1+** (https://demozoo.org/productions/364420/) -- Commodore 64 Tool
- **Superiors Game Music Creator (GMC) System V1** (https://demozoo.org/productions/364292/) -- Commodore 64 Tool
- **DigiEditor V1.3** (mentioned in bio, 1990) -- sample editor

### External links:
- SoundCloud: https://soundcloud.com/bpstudio/
- Facebook: https://www.facebook.com/bpstudiomusic/
- CSDb: https://csdb.dk/scener/?id=367
- Pouet: https://www.pouet.net/user.php?who=99105
- AMP: https://amp.dascene.net/detail.php?view=810
- Bandcamp: http://bpstudio.bandcamp.com

Brian has 103 productions on Demozoo. He is still active as of recent years (productions from 2024+).

---

## 10. Additional V5.x Variants Found on CSDb

From searching CSDb for "DMC V5":
- **DMC V5.0 Scaner** (https://csdb.dk/release/?id=40290) by Keen Acid (KA) -- a scanner/viewer tool
- **DMC V5.01B** (https://csdb.dk/release/?id=236892) by Chaos -- bugfixed by Zeux (see section 5)
- **DMC V5.1 Package** (https://csdb.dk/release/?id=129434) by Motiv 8 -- tool collection
- **DMC V5.1 Packer** (https://csdb.dk/release/?id=236893) by Zeux -- standalone packer
- **DMC V5.4** (https://csdb.dk/release/?id=36658) by Samar Productions (Glover) -- modified version
- **DMC V5.4 Packer** (https://csdb.dk/release/?id=137786) by Samar Productions -- packer for V5.4

---

## Summary of Version Lineage (Technical)

```
GMC V1 (Game Music Creator) -- Brian, ~1990, first attempt
  |
Mini Music Editor -- Brian, Tomcat era, pre-GMC
  |
DMC V1.2 -- Brian, early
  |
DMC V2.1+ -- Brian (as "The Superiors")
  |
DMC V4.0 -- Brian, THE canonical version
  |   |
  |   +-- DMC V4.0 Pro (1995, Brian + Morbid/Onslaught)
  |   +-- DMC V4.0 Relocator V2.0 (1993, Syndrom + Stormlord/WoW)
  |   +-- DMC 4.G (1997, Glover/Samar -- "G" for Glover)
  |   +-- DMC V7.0 (1995, Axl+Ray/Unreal -- enhanced editor, 1-5 speed)
  |        +-- DMC V7.1 Beta (1995, Unreal -- player improvements: filters, ADSR, 6-speed)
  |             +-- TFX (born from V7 codebase, later completely rewritten by PG)
  |
DMC V5.0 -- Brian, ~1993-94, fits in $18 (24) raster lines, "knows every effect"
  |   |
  |   +-- DMC V5.01B (Zeux bugfix)
  |   +-- DMC V5.1 (Motiv 8 package, Zeux packer)
  |   +-- DMC V5.4 (Glover/Samar)
  |
DMC V6.0 -- Brian, ~1993-94, max 8 raster lines, editor by Syndrom
  |          (never officially released per Brian!)
  |
"Sosperec" (Pretzel) -- Brian, private/secret, 8 raster lines, filters,
                        3x raster time of DMC V2, SID datalogging technique
```

### Key facts for SIDfinity implementation:
1. **V4 is the canonical base** for the most widely-used variants. V5/V6 are different player designs.
2. **V7.x is V4-based** with added features (multispeed, filter commands, direct ADSR). NOT a continuation of V5/V6.
3. **V5 player = 24 raster lines** ($18), V6 player = max 8 raster lines. Different optimization levels.
4. **V6 was never officially released** -- versions calling themselves V6 are likely modded V4 or V5.
5. **Frequency tables vary**: "CGKOTY" tables in some DMC versions vs different tables in Sosperec/AEINRW, causing quarter-tone pitch differences.
6. **The V4 Relocator binaries** are the best resource for understanding which addresses need relocation (= which memory regions contain pointers).
7. **V7.1 Beta new player commands**: filter control + direct AD/SR register sets. These would appear as new sector command bytes not present in V4.0.
8. **Brian is still active** at bpstudio.hu and could potentially be contacted for technical details.
