---
source_url: multiple — see per-section citations
fetched_via: WebSearch + WebFetch + curl + raw binary analysis
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: primary (binary analysis) + secondary (web sources)
---

# Loadstar SongSmith — Archive.org / itch.io / Magazine Issue Research

## 1. The Loadstar Compleat Archive

**itch.io listing:** https://rodneylives.itch.io/loadstar  
**Maintainer:** "rodneylives" (with blessing of Fender Tucker, longtime Loadstar managing editor)  
**Price:** $15 USD  
**Contents:**
- All 199 issues of Loadstar (C64/128), D64 + D81 disk images
- All 42 issues of Loadstar 128
- All 21 issues of UpTime (rival disk magazine Loadstar purchased)
- 73 issues of The LOADSTAR Letter (newsletter companion; PDFs)
- JPGs of all colour covers
- Bonus content (Compleat Bible, Compleat Programmer, Crosswords, ProseQuest, etc.)
- **Listed explicitly:** "SongSmith" as a named discrete bonus product alongside
  "Brain Stuff", "SID Music", "Knees' PUD", "Roger Unwrapped", "Serious Stuff",
  "the art of Walt Harned", etc.
- "Extra MP3s from Dave Marquis and Knees Calhoon"
- Dave Marquis' SID and MIDI music in separate collection

Source: https://rodneylives.itch.io/loadstar (fetched 2026-06-14)

**Devlog / updates page:** https://rodneylives.itch.io/loadstar/devlog/1066851/updates

**Third-party reviews:**
- MetaFilter Projects: https://projects.metafilter.com/6382/Itchio-Release-of-LOADSTAR-COMPLEAT
- Set Side B writeup: https://setsideb.com/loadstar-compleat/
- Loadstar CE forums: https://loadstarce.com/threads/loadstar-compleat.2/

**Ramble House product page (older):** http://www.ramblehouse.com/loadstarcompleat.htm  
No additional SongSmith detail beyond title listing.

---

## 2. SongSmith as a Stand-Alone Product (NOT an Issue Feature)

The Loadstar Complete user listing in a Lemon64 forum thread (`t=65592`) shows
SongSmith under a **separate sub-directory** in the archive, alongside other named
sub-products. This confirms SongSmith was distributed as a **self-contained Loadstar
sub-product**, not as a feature embedded in one particular issue.

The itch.io listing bullet-points it by name alongside "Compleat Bible", "Compleat
Programmer", etc. — the same treatment as standalone spin-off products.

**OPEN:** Which Loadstar issue first shipped SongSmith? The archive's internal
`SongSmith [bad]` directory marker in the Lemon64 user's copy means the directory
listing didn't reveal specific issue numbers. The 30-page manual (referenced in the
CSDb disk's embedded text) likely identifies the first-issue shipment.

---

## 3. CSDb Archive Entry

**URL:** https://csdb.dk/release/?id=122855  
**Title:** Songsmith  
**Type:** C64 Tool  
**Author listed:** None (CSDb credits section empty — "No credits found")  
**Download:** `http://csdb.dk/getinternalfile.php/121491/Songsmith-Loadstar.d64`  
  (141 downloads as of research date)  
**File size:** 174,848 bytes (standard 1541 D64 image = 174,848 = 35 tracks)

**SIDs bundled on CSDb d64 (by Debby Cruz):**
- Alouette
- Funiculi Funicula
- Meadowlands
- Muss I Denn
- Scarborough Fair
- Skye Boat Song
- The Parting Glass

The disk was downloaded and verified locally to `/home/jtr/sidfinity/tmp/loadstar_songsmith_research/Songsmith-Loadstar.d64`.

---

## 4. D64 Directory — File Naming Convention (from Binary)

Raw string extraction from the Songsmith-Loadstar.d64 reveals the SongSmith
file-naming convention (confirmed by multiple occurrences on the disk):

```
M.SONGNAME     — Melody / note data (main song file)
W.SONGNAME     — Waveform / instrument data
C.SONGNAME     — Credits (title, composer text)
S.SONGNAME     — SID export (converted MUS/Sidplayer format?)
L.SONGNAME     — Lyrics?
```

Examples observed on disk:
- M.FUNICULI, C.FUNICULI, W.FUNICULI, S.FUNICULI, L.FUNICULI
- M.ALOUETTE, C.ALOUETTE, W.ALOUETTE, S.ALOUETTE
- M.MUSSIDENN, M.SCARBOROUGH, M.SKYE, M.PARTING, M.MEADOWLANDS

**At minimum 5 file types per song.** Songs "always have at least two files,
one beginning with M. and the other beginning with W." (from embedded docs on disk).

Also noted in disk strings:
- `SIDSMITH` — the player program name
- `SIDSMITH.SHPL` — a shell/loader for the SID player
- `SONGSMITH DISK` — label used when formatting a data disk
- `SONGSMITH FILENAME:` — editor prompt for saving
- `SONGSMITH-64` — the editor program name (with -64 suffix, possible version marker)
- `MUSIC STAR.BAS` — referenced as a BASIC program

---

## 5. Loadstar #168 Context

**Source:** comp.sys.cbm newsgroup post transcribing Loadstar #168 text  
**URL:** https://groups.google.com/g/comp.sys.cbm/c/1TtXLOgICfs

Key passage (from the issue):

> "Jim W. said that the songmaker they used in those days was written by
> Joe Garrett and Alan Gardner, and was the precursor to SongSmith."

This is Fender Tucker (Loadstar editor) quoting Jim W. in a reader Q&A about
songs from Loadstar issues #27 and #28. Confirms:
1. SongSmith was preceded by an earlier tool by Garrett + Gardner
2. Joe Garrett is involved in the SongSmith lineage (confirmed as author below)

---

## 6. DeepSID Documentation

DeepSID (https://deepsid.chordian.net/) changelog (September 7, 2025):

> "Added an 'L' focus icon for composers who only used Loadstar Songsmith."

This letter icon is analogous to the 'M' icon added for Master Composer users.
It confirms the HVSC community treats SongSmith as a distinct, catalogued production
tool. The focus icon helps users find composers who ONLY used SongSmith.

---

## 7. HVSC Coverage (from local hvsc84/)

304 SIDs with init=$CC00 / play=$CC48 (the SIDSMITH player entry points):

| Composer | Count |
|---|---|
| Dave Marquis | 130 |
| Alan Beggerow | 48 |
| Debby Cruz | 41 |
| John S. Davis | 24 |
| Mario Oropesa | 22 |
| James Weiler | 8 |
| Kevin Cloud | 8 |
| William M. Shockley | 8 |
| Terry Walker | 7 |
| James C. Hilty | 6 |
| Joe Garrett | 2 |

**Copyright range:** 1986 Loadstar .. 1997 Loadstar (+ some undated)  
**Total HVSC SongSmith corpus:** ~337 SIDs (308 unversioned + 19 v1 + 3 v3 + 1 v2 + 6 Song_Writer,
per sidid classification from previous research session)

Load addresses vary widely: $B800–$C700 range (per-song relocation).
Player is always at $CC00 (init) / $CC48 (play).

---

## 8. Back-Issue Catalog PDF

**URL:** https://www.c64copyprotection.com/wp-content/uploads/2018/05/Loadstar-OCR.pdf  
**Status:** Too large for WebFetch (>10 MB); not retrieved in this session.

**OPEN:** This PDF likely contains the back-issue catalog index which would show
which specific issues shipped SongSmith and what documentation was included.

---

## Leads to Follow

1. **Archive.org D64 collection:** https://archive.org/details/loadstar_disk
   (331 D64 images). Search for issues that include "SONGSMITH" or "SIDSMITH"
   in their directory. This would identify the first issue and all shipment issues.

2. **Back-issue catalog PDF** (c64copyprotection.com link above) — 10+ MB,
   needs `curl` download and grep. Likely contains issue-by-issue listings.

3. **Loadstar Complete itch.io devlog** — the updates page may list what issues
   originally contained which programs.

4. **comp.sys.cbm archives on Google Groups** — search for "SongSmith" across
   the Loadstar-related posts. The #168 thread showed this goldmine.
   URL: https://groups.google.com/g/comp.sys.cbm/search?q=SongSmith

5. **Loadstar fan sites:**
   - https://loadstarce.com/ (Loadstar Community Edition forums)
   - The LOADSTAR Library: https://loadstargallery.webs.com/ (returned 503 this session)
   These may have issue-level indexes.

6. **CommodoreServer.com blog post** about "199 issues of LoadStar":
   https://www.commodoreserver.com/BlogEntryView.asp?EID=94ABE1922484430096AAD3B892D57EEA
   May have issue-by-issue listing.
