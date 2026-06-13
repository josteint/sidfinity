---
source_url: https://csdb.dk/release/?id=17814 (V6.3), https://csdb.dk/release/?id=17819 (V7.96), https://csdb.dk/webservice/?type=release&id=17814&depth=2, https://csdb.dk/webservice/?type=release&id=17819&depth=2, https://csdb.dk/webservice/?type=scener&id=10213&depth=2
fetched_via: csdb webservice XML (csdb.dk 503 for HTML pages; webservice returned XML)
fetch_date: 2026-06-13
author: CSDb contributors
content_date: 1989–2021
reliability: primary
---

# CSDb Release Notes — RoMuzak V6.3 and V7.96

## RoMuzak V6.3 — CSDb ID #17814

**Title:** RoMuzak V6.3
**Type:** C64 Crack
**Release year:** 1989
**Releasing group:** Cosmos (Austria, founded 1988-07-17, dissolved 1990-07)
**Crackers/importers:**
- Crack: Antitrack (Austria — coder/cracker/swapper)
- Import: Apa-Soft / Apa-Software (Poland — cracker/importer)

**Download:**
- URL: http://csdb.dk/getinternalfile.php/31380/ro-muzak.d64.gz
- Filename: ro-muzak.d64.gz
- Downloads (as of fetch): 636
- Status: Ok

**Screenshot:** https://csdb.dk/gfx/releases/17000/17814.png

**CSDb comments (one comment recorded):**
- Commenter: Karmic (ID 6532, Canada), date 01.05.2015
- Text: *"This is actually a version of Cosmos's crack by APA-Software."*

**Notes:**
- This is the cracked/imported copy that circulated in the scene. The original commercial release
  was by Digital Marketing (Germany); this CSDb entry records the crack by Cosmos/Antitrack with
  Apa-Soft import.
- "C64 Crack" type indicates this is not the original binary but a cracked distribution copy.

---

## RoMuzak V7.96 — CSDb ID #17819

**Title:** RoMuzak V7.96
**Type:** C64 Tool
**Release date:** 1990-03-15
**Author/Coder:** ROM (CSDb handle ID 10213), Germany

**Downloads:**
- Two separate download entries (SYS28672.zip: 105 downloads; D64 disk image: 34 downloads)
- Both marked status: Ok

**SID used in editor intro:**
- Title: M.O.N.-Medley (1990, Lazer Cybernetix release)
- Load address: 32768 ($8000), PAL, 6581 model

**CSDb comments (reconstructed from webservice):**
- User "Fred" (2021): *"Editor found by extracting it from release <release id=17818>."*
  *"Run it with SYS 28672."*
- Credit given to Professor Chaos for discovery/upload.
- Earlier inquiry (2015) requesting upload of V7.96 — confirmed it was not previously available.

**Extraction source:** CSDb release ID 17818 = **VacSID V0.88 [dos]** (released 1996-03-30).
The RoMuzak V7.96 editor was embedded within or shipped alongside VacSID V0.88.

**VacSID V0.88 credits (CSDb ID 17818):**
- Coder: ROM (ID 10213) — Germany, roles: coder + musician
- Coder: Scamp (ID 10214) — Germany, roles: coder, graphician, musician, organizer, PR, webmaster
- Download: http://csdb.dk/getinternalfile.php/36832/vacsid.zip (484 downloads)

**VacSID ZIP contents (confirmed via direct fetch):**
- VACSID.EXE — main player application
- VACSETUP.EXE — setup/installation executable
- RTM.EXE — runtime module
- VACSID.DOC — player documentation (text file — **not yet fetched; likely describes SID player
  features and may reference RoMuzak compatibility**)
- VACUUM.NFO — archive info/credits
- FILE_ID.DIZ — standard BBS file description

**Startup note:** Editor runs with `SYS 28672` (decimal) = `SYS $7000`, consistent with the
known V7.96 load address of $7000.

---

## ROM scener profile — CSDb ID #10213

**Handle:** ROM
**Real name:** Oliver Blasnik (confirmed via sidid.nfo, VGMPF, and in-binary string)
**Country:** Germany
**Currently active (per CSDb):** Yes
**Roles:** Coder, Musician

**All releases with CSDb code credit:**

| CSDb ID | Title | Type | Date |
|---------|-------|------|------|
| 17819 | RoMuzak V7.96 | C64 Tool | 1990-03-15 |
| 17818 | VacSID V0.88 [dos] | Other Platform C64 Tool | 1996-03-30 |
| 17815 | VacSID V1.58 [dos] | Other Platform C64 Tool | 1997-03-02 |
| 141869 | VacSID V1.57 [dos] | Other Platform C64 Tool | 1997-01-11 |
| 17817 | VacSID V1.59 [dos] | Other Platform C64 Tool | 1997-10-19 |
| 136923 | VacSID V1.51 [dos] | Other Platform C64 Tool | 1996-11-03 (Wired 1996 party, Belgium) |

**Notes:**
- V6.3 (#17814) is not listed under ROM's code credit — that entry is credited to Cosmos/Antitrack
  (the crackers), not the original author. This is normal for cracked-tool CSDb entries.
- VacSID is a DOS-based SID file player (SID format player for PC). ROM and Scamp co-developed it
  through multiple versions (V0.88 → V1.59) from 1996 to 1997.
- ROM appears to have left the scene after VacSID V1.59 (1997). No C64 or PC releases after that.

---

## Publisher: Digital Marketing

**Type:** Commercial German software publisher, late 1980s–early 1990s.
**Role:** Original copyright holder of RoMuzak V6.3 and V7.96.
**In-binary strings (two confirmed):**

From github_parser_notes.md (compact banner):
```
** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!!
```

From Polish C64 scene forum c64scene.pl/viewtopic.php?t=112 (skull post #13 — extended version):
```
OLIVER BLASNIK, <C> DIGITAL MARKETING!! 02435-1295!!
```
(where `<W>` = written-by marker, `<C>` = copyright marker, `02435-1295` = Oliver Blasnik's phone
number; area code 02435 = Bedburg/Erftkreis, North Rhine-Westphalia, Germany)

**Known Digital Marketing C64 releases (not exhaustive):**
- RoMuzak V6.3 (music editor, 1989)
- RoMuzak V7.96 (music editor update, 1990-03)
- ROM's Fix (sound effects editor, 1989, bundled with RoMuzak V6.3)
- Logo (puzzle game, 1990, published by Starbyte — developed by Digital Marketing's team)
  - Coder: Thomas Koncina; Graphics: Arndt Heitkamp; Music: Stefan Hartwig
- No Mercy — attributed to Digital Marketing in one source (c64.com); separately also listed
  under Golden Disk 64 / CP Verlag. Ambiguous — may be publisher vs. developer distinction.
- Ultimate Intro Studio (demo tool, 1989) — referenced in Lemon64 forum as "by Digital Marketing"

**Oliver Blasnik as programmer (beyond RoMuzak):**
- Credited as uncredited programmer on Clik Clak (C64, 1992, Idea publisher) — confirmed via
  VGMPF Clik_Clak_(C64) page.
- MobyGames lists him with credits 1990–1991.
- Described on VGMPF as working with "Rainbow Arts Software GmbH" in addition to Digital Marketing.

---

## Leads to follow

- **OPEN:** CSDb was returning HTTP 503 during this research session. The HTML release pages
  (#17814, #17819) may contain additional user comments not captured here. Re-fetch when CSDb
  is stable: https://csdb.dk/release/?id=17814 and https://csdb.dk/release/?id=17819
- **OPEN:** Fetch VACSID.DOC from the VacSID ZIP (URL:
  http://csdb.dk/getinternalfile.php/36832/vacsid.zip) — decompress and read. This player
  documentation is likely to describe which SID formats VacSID supports, potentially including
  RoMuzak compatibility notes or version info.
- **OPEN:** CSDb scener profile for Scamp (ID 10214) — co-developer of VacSID; may have additional
  context on Digital Marketing or RoMuzak.
- **OPEN:** The "Forum64 Digital Marketing thread" (https://www.forum64.de/index.php?thread/83160-digital-marketing/)
  returned HTTP 403. This thread was described in search snippets as discussing RoMuzak and its
  copy protection (including "Kryoflux image" mention). Try fetching via a different path or
  user-agent when possible.
- **OPEN:** MobyGames Oliver Blasnik page (https://www.mobygames.com/developer/sheet/view/developerId,119354)
  returned HTTP 403. Contains full game credits 1990–1991. Should be revisited.
- **OPEN:** Verify "No Mercy" publisher — CSDb #6707 credits Markus Schneider for music; c64.com
  lists "Digital Marketing" as maker; Lemon64 lists "Golden Disk 64 / CP Verlag". The game uses
  Markus Schneider's own driver (not RoMuzak) — but Digital Marketing may have co-published or
  co-developed.
- **OPEN:** Archive.org has both D64 disk images:
  - Music Demo-Editor: https://archive.org/download/d64_Romuzak_Music_Demo-Editor_1989_ACT_501/Romuzak_Music_Demo-Editor_1989_ACT_501.d64
  - Analyser/Play Construction Kit: https://archive.org/download/d64_Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501/Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501.d64
  These are the actual editor binaries. Extract PRG files from the D64 (using `d64dump` or
  similar tool) and read documentation text files if any are present on disk.
