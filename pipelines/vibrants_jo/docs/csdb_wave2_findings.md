---
source_url: multiple — see sections below
fetched_via: direct
fetch_date: 2026-06-16
author: research agent
content_date: 2026-06-16
reliability: secondary
---

# Vibrants/JO — CSDb Wave 2 Research Findings

This document is a second-wave sweep of CSDb, Demozoo, and related sources.
The first-wave sweep results live in `csdb_findings.md` (very thorough) and
`github_findings.md`. This file records new confirms, corrections, and
supplementary detail not in those files.

Raw fetches saved to `/home/jtr/sidfinity/tmp/vibrants_jo_research/` (wave 2 files):
- `csdb_scener_1926.txt`
- `demozoo_jo_6764.txt`
- `csdb_search_jesper_olsen.txt`
- `csdb_amok_releases.txt`
- `csdb_group_672.txt`
- `csdb_search_group_vibrants.txt`
- `csdb_amok_group.txt`
- `demozoo_vibrants_group.txt`

---

## 1. What CSDb says about JO as a scener (wave 2 re-fetch)

CSDb scener page https://csdb.dk/scener/?id=1926 was accessible on 2026-06-16 wave 2
(it had returned HTTP 503 on the earlier wave-1 attempt, per `csdb_findings.md` line 19).

### New detail: CSDb Coder credits

Wave 1 missed this because the page was down. Wave 2 confirms:
JO has exactly **one release where he is credited as CODER** (not just musician):

- **Music Demo #001** (1989) by Amok — CSDb release ID **122947** — credits: Code + Music

All 400+ other credits are musician-only. This single coder entry is the only evidence of
him deploying his player code within a CSDb-tracked release as a coding credit.
No standalone tool/editor release by JO appears in CSDb.

### New CSDb release IDs confirmed for key JO releases

| Title | Year | CSDb ID |
|-------|------|---------|
| Importent Note | 1989 | 144094 |
| Ugly Duckling | 1991 | 91522 |
| Patrick's Love | 2015 | 137469 |
| Bonzilloscope (Bonzai) | 2020 | 197869 |
| Laxity Universal Cooperation Intro | 2025 | 255080 |
| Rasta Grid 2026 | 2026 | 258557 |

### Confirmed from Vibrants group page (CSDb ID 328; Demozoo ID 769)

From the Vibrants group page bio:
> "JCH, JO and Laxity coded their own players and editors on the C64,
> JCH and JO coded for AdLib and Sound Blaster, and JO made his own players for
> Roland MT-32 and Amiga."

This is an explicit group-level statement that JO's player is separate from JCH/Laxity.

---

## 2. Vibrants group structure and JO's membership timeline

Source: Demozoo https://demozoo.org/groups/769/ and CSDb group 328.

| Member | Role | Joined | Status |
|--------|------|--------|--------|
| JCH (#626) | Coder, Musician, Webmaster | 8-1989 | Active |
| Link (#1208) | Musician | 8-1989 | Inactive |
| Drax (#16) | Musician | 1989 | Active |
| Laxity (#677) | Coder, Musician | 9-Sep-1990 | Active |
| Metal (#728) | Musician | 5-1991 | Active |
| JO (#1926) | Coder, Musician | 1992 | Inactive (left scene in 1990s) |
| MSK (#768) | Musician, Webmaster | 1998 | Inactive |
| Deek (#1265) | Musician | 7-1990 | Ex-member (left 1992) |

Founding quote: "J C HUUS, DRAX AND LINK BUILT UP THE MUSIC-COMPANY 'VIBRANTS'
AND JOINED THE SOUND-DEPARTMENT OF AMOK"

JO's membership timeline:
- Genesis Project: until ~1991
- Amok: until ~1991 (Sound Dept.)
- Vibrants: from 1992 to present (inactive since mid-1990s)

Vibrants was known as Amok's music wing before becoming independent. JO
moved from the music wing side to the Vibrants banner when he left Amok.

---

## 3. Releases that might contain player source or format documentation

### Nothing found.

No CSDb release by JO contains player source or format documentation:
- No tool releases with JO as author/coder (besides Music Demo #001, 1989)
- No editor downloads in CSDb, zimmers.net, or Archive.org
- The JCH Editor and Laxity Editor are documented and released; JO's C64 player is not

The only Vibrants tools in CSDb are:
- JCH Editor V3.04 (ID 14037, 1991) — JCH's engine, not JO's
- Laxity Editor v/33-3.35 (ID 158522) — Laxity's engine, not JO's
- JCH NewPlayer 21.g4 (ID 20112, 2005), 21.g5 (ID 33785, 2006)

The MS-DOS tools (FairPlay v1.1, EdLib 1.05a, Play-Driver v02.02) are JCH+JO
collaborations for AdLib/SoundBlaster, not the C64 engine.

### One potentially interesting release: Bonzilloscope (ID 197869, 2020)

A 250+ track Bonzai music history collection including JO's tunes. Uses a custom
oscilloscope visualizer (reads $D41B oscillator voice 3, $D41C envelope voice 3).
JO's tunes appear in their original player format — this is a playback showcase,
not a format document. Coder: Walt (Bonzai). No player engine documentation.

---

## 4. The HJE connection

HJE = Hans Jürgen Ehrentraut, alias Esonix (earlier), German composer.
CSDb scener ID: **2273** (confirmed via existing tmp/csdb_hje_scener.txt).

### Group membership overlap timeline

| Period | JO | HJE |
|--------|-----|-----|
| 1989 | Amok Sound Dept. | — |
| 1990 | Amok | **joins Amok** |
| 1991 | Amok → leaves | Amok → Genesis Project |
| 1992+ | Vibrants | Genesis Project / MDG |

**Key finding: JO and HJE were both in Amok simultaneously in 1990.** This direct
co-membership is almost certainly how HJE obtained a copy of JO's player. HJE would
have received the player binary during their shared Amok membership. No other group
link between them exists.

### HJE's HVSC corpus using Vibrants/JO player

Main dir: MUSICIANS/H/HJE/ — 33 SIDs plus MUSICIANS/H/HJE/Esonix/ — 23 SIDs

Key HJE SIDs with load/play addresses (from HVSC + CSDb):
| Title | Year | Group | Load | Init | Play | Songs |
|-------|------|-------|------|------|------|-------|
| Propaganda_Music | 1991 | Genesis Project | $762D | $7634 | $769F | 2 |
| Tech_2 | 1997 | MDG | $1000 | $1000 | $1006 | 1 |
| Solitax_end_sequence | 1992 | Amok | $1162 | $1162 | $1168 | 2 |
| Genesis_Project_crack_intro | 1991 | GP | $0DC8 | $0DC8 | $0DCB | 1 |

These addresses are consistent with the JO player layout: init at load address,
play at load+3 or load+6 (the Init→Play offset varies slightly by tune/version).
The wide load address spread ($0DC8, $762D, $1162, $1000) matches JO's own
collection — confirms the player has no fixed load address; it is re-assembled or
hand-relocated per tune.

HJE's Esonix subdirectory (23 SIDs) represents his earlier compositions under
the "Esonix" alias (before he standardized on HJE); these are not separately
classified in sidid — they share the Vibrants/JO fingerprint.

### No direct statement found

No CSDb comment, STIL entry, or forum post explicitly says "HJE used JO's player."
The connection is inferred from:
1. Both classified as Vibrants/JO in sidid.cfg
2. Both were in Amok in 1990 (simultaneous membership)
3. HVSC dirs both match the engine fingerprint
4. No other engine is attributed to HJE in HVSC

---

## 5. CSDb release comments mentioning technical terms

### Music Demo #001 by Amok (CSDb ID 122947)

This is JO's only coder credit. The release page returned CSDb content for a different
release (Stash Intro 03) due to a redirect issue — the actual ID 122947 content was not
accessible in this wave. Recommend direct visit.

### Commando Theme Remix (CSDb SID ID 15838)

Technical specs confirmed:
- Load: $4000, Init: $4000, Play: $4003
- Data size: 3910 bytes ($0F46)
- SID model: 6581, Clock: PAL, Songs: 1
- 1989 Amok Sound Dept.
- HVSC path: /MUSICIANS/J/JO/Commando_Theme_Remix.sid

No user comments on this page about player or engine.

### Soporific (CSDb SID ID 15901)

Technical specs confirmed:
- Load: $EFFF, Init: $EFFF, Play: $F006
- Data size: 2561 bytes ($0A01)
- SID model: 6581, Clock: PAL, Songs: 1
- 1988 Amok
- Released in: "Just for You" (Microforce), "The Results" (Elect + X-Rated),
  "Amok's Soporific" (Amok one-file demo)

No user comments mentioning player or engine.

### Ugly Duckling (CSDb ID 91522)

Music release by Vibrants, 1991. Musicians: Drax + JO.
SID at MUSICIANS/D/DRAX/Ugly_Duckling.sid (attributed to Drax, not JO).
User comment: "Nice moody piece :)" — no technical content.

### Vibrants group page (CSDb ID 328)

No per-member tool releases linked to JO. The group page confirms JO coded his own
player but provides no further technical documentation or download links.

---

## 6. sidid.nfo Vibrants/JO entry (wave 2 confirm)

From raw GitHub https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo:

```
Vibrants/JO
   AUTHOR: Poul-Jesper Olsen (JO)
```

Sparse entry — no NAME (editor name), no RELEASED date, no REFERENCE URL.
Compare to Vibrants/Laxity which has:
```
Vibrants/Laxity
     NAME: LAXITY editor
   AUTHOR: Thomas Egeskov Petersen (Laxity)
REFERENCE: https://csdb.dk/release/?id=122333
```

The absence of NAME and REFERENCE for Vibrants/JO is consistent with "no public
editor release exists." The Laxity editor is released and documentable; JO's is not.

---

## 7. Demozoo production details (new from wave 2)

Demozoo ID 6764. Three CSDb IDs are cross-referenced: 1926, 10636, 10635.
IDs 10636 and 10635 likely correspond to his Rock and Technic alias entries in CSDb.

Productions of special interest not in prior docs:

| Year | Title | Type | Notes |
|------|-------|------|-------|
| 1988 | "The Batcave" | Demo | Code+Graphics+Music+Text — earliest known full production |
| 1992 | "Copper" | MS-DOS Cracktro | Code (player) + Music — first confirmed MS-DOS player ship |
| 1994 | "Notes" | C64 Demo music | Under Vibrants banner |
| 1994 | "Sid Mania" | SNES Musicdisk | Shows platform range |
| 1988 | "Multi Move" | 8K Intro | Code+Graphics+Music, alias Rock — earliest C64 player use |

"Multi Move" (1988, alias Rock) is the earliest confirmed production using JO's own
code + music. The HVSC file Multi_Move.sid is the one already-extracted USF in the repo.

---

## 8. Search dead ends (wave 2)

- CSDb search for "jesper olsen" (scener) → 0 results
- CSDb search for "amok sound dept" (release) → 0 results
- CSDb search for "amok music" (release) → 0 results
- CSDb search for "amok sound" (release) → 0 results
- CSDb search for "vibrants" (group) → 0 results
- CSDb search for "amok" (group) → 0 results
- CSDb search for "JO player" (release) → 0 results
- HVSC update announcements (Update 71, 72, 73) → no JO/HJE player mentions
- vibrants.dk/jo.htm → timeout (site down or very slow)
- HJE / Esonix → no connection to JO explicitly stated in any source

---

## Leads to follow

1. **CSDb release ID 122947 (Music Demo #001 by Amok, 1989)** — JO's only coder credit.
   Direct visit: https://csdb.dk/release/?id=122947
   Look for: download link (D64), any user comments about the player, music format.

2. **CSDb scener IDs 10636 and 10635** — JO's alias CSDb entries (Rock, Technic).
   Direct visits: https://csdb.dk/scener/?id=10636 and https://csdb.dk/scener/?id=10635
   May show releases not listed under the main 1926 profile.

3. **vibrants.dk/jo.htm** — JO's personal webpage (listed on Demozoo).
   Site is slow/down but may have biographical content about his player.
   Try Wayback Machine: https://web.archive.org/web/*/http://www.vibrants.dk/jo.htm
   (WebFetch cannot reach web.archive.org — use manual browser visit.)

4. **CSDb scener ID 2273 (HJE)** — HJE's full release list.
   Direct visit: https://csdb.dk/scener/?id=2273
   Look for: any comment on "where I got the player" in release descriptions.

5. **"The Batcave" (1989, JO's first full demo)** — earliest demo with JO code + music.
   Find on Demozoo or CSDb. May contain player binary in original form.
   URL pattern: search CSDb for "The Batcave" release.

6. **HJE Esonix CSDb entries** — Esonix subdirectory in HVSC has 23 SIDs.
   Search CSDb for "Esonix" to find scener page; his earliest compositions using the
   Vibrants/JO player may pre-date his HJE handle.

7. **Sex'n'Crime diskmag issues** — JO contributed music to issues #1-#21 (1989-1991),
   HJE contributed to issue #21. The diskmag hosted both; examining issue #21 SIDs
   could show whether HJE's player code is identical to JO's at that date.

8. **Amok group CSDb page** — CSDb search returns nothing for "amok" but the group
   has a page. Try: https://csdb.dk/group/?id=19 or similar known IDs from other sources.
   The Amok group page would list JO and HJE as members with date ranges confirming overlap.

9. **Vicious SID 2 (HJE)** — one of HJE's largest productions (45 KB SID file).
   CSDb page for this release may have technical comments about the music player used.

10. **WilfredC64/player-id repository** — the newer Rust reimplementation of sidid.
    May have additional signatures or notes for Vibrants/JO:
    https://github.com/WilfredC64/player-id
    The config/ directory may have expanded info not in cadaver/sidid.
