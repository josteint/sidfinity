---
source_url: multiple (see per-section headers)
fetched_via: WebSearch + WebFetch
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: secondary (synthesized from primary Usenet/forum/disk sources)
---

# Loadstar SongSmith — Forum, Usenet, and Community Discussion

## Session Overview

This file records all forum/community/Usenet/disk-text sources found for SongSmith.
The prior research session (same date) covered GitHub, sidid signatures, and version
archaeology. This session focused on the **Loadstar community, Usenet comp.sys.cbm,
forum discussion, and the actual program text on Loadstar 237** (Discmaster).

---

## 1. Discmaster — Loadstar 237 Disk (PRIMARY SOURCE)

**Disk:** 237.d81 (Loadstar issue 237, circa 2004-2005)
**Discmaster path:** https://discmaster.textfiles.com/browse/5218/237.d81
**File count:** 128 files total
**reliability:** primary (actual disk content)

### SongSmith-relevant files on Loadstar 237:

| File | Type | Size | Notes |
|------|------|------|-------|
| songsmith | Packed C64 PRG | 32.0 KB | Main SongSmith editor/player binary |
| songsmith.080d | Packed C64 PRG | 41.3 KB | Unpacked version inside songsmith/ subdir |
| songsmith.1b39 | Unknown | 62.0 KB | Data component inside songsmith/ subdir |
| b.songsmith | Commodore BASIC | 1.2 KB | Loader; credits Joe Garrett, © 2005 |
| t.songsmith | Text | 2.1 KB (79 lines) | Dave Moorman documentation (see below) |
| smithsid | Packed C64 PRG | 13.9 KB | SmithSID: .mus → SongSmith converter |
| b.smithsid | Commodore BASIC | 1.2 KB | SmithSID loader |
| t.smithsid | Text | — | SmithSID documentation (Doreen Horne) |
| b.sidsmith | Commodore BASIC | 4.5 KB | SIDSmith: SongSmith → .mus converter |
| t.sidsmith | Text | — | SIDSmith documentation |
| b.midi player | Commodore BASIC | 1.2 KB | MIDI player loader |
| t.midi player | Text | — | MIDI player documentation |
| stereoplayerv10 | Commodore BASIC | 27.5 KB | Stereo SID Player V1.0 |

Also present: 10 music SID files with **.mus** extension (Jewish/Russian folk tunes
by Ken Barsky, using Stereo SID Player format — these are NOT SongSmith format):
- ayneyloheynu.mus (326 bytes, 1m9s)
- belz.mus (1.5 KB, 2m44s)
- chad gadya.mus (760 bytes, 3m)
- etc.

**NOTE:** The .mus files on Loadstar 237 are Stereo SID Player files (Chamberlain format),
NOT SongSmith format. The SongSmith files would use m./w. prefix naming.

---

## 2. t.songsmith — Dave Moorman's Documentation Article

**Source URL:** https://discmaster.textfiles.com/view/5218/237.d81/t.songsmith
**Author:** Dave Moorman (text); Joe Garrett (program)
**Date:** 2004-01-01 (disk date)
**reliability:** primary

Key facts extracted (see forum_musical_model.md for full analysis):

- SongSmith "never appeared on a regular issue of LOADSTAR" — it was "a stand-alone
  music package Softdisk sold on the side -- with the docs in a booklet."
- Program loads with a bluegrass demo piece.
- Main Menu: Key Signature (<K>), Time Signature (<T>), Speed (<S>), New (<N>)
- Voice selection: keys 1, 2, 3
- Duration keys: W (whole), H (half), Q (quarter), E (eighth), S (sixteenth)
- D = dotted note; R = rest
- Backslash navigates between screens
- Beats-per-voice tracking prevents overfilling measures
- Tied-note workaround: long Release (14–15) + rest at measure start
- Article text: "the best way to learn it is to play with it. Try everything!"

---

## 3. t.sidsmith — SIDSmith Documentation

**Source URL:** https://discmaster.textfiles.com/view/5218/237.d81/t.sidsmith
**Authors:** Debby Cruz and Scott Resh (program); unattributed (text)
**Date:** 2004-01-01 (disk date)
**reliability:** primary

Full extracted content (as summarized by WebFetch):

SIDSmith converts SongSmith format → SID Player format. Key facts:

- **SongSmith files**: use "m." and "w." prefixes
- **SID Player files**: use ".mus" suffix (Chamberlain/Bratt format)
- Framing: "SongSmith is easier to enter; SID Player has thousands of users and more
  powerful capabilities (triplets, filtering)"
- Conversion options: measure markers, credit preservation, key transposition, tempo
- Processing: "all done at ML speeds"
- Use case: "quickly and easily entered in SONGSMITH" → "translate into SID format
  for the final touches" in SID EDITOR

---

## 4. t.smithsid — SmithSID Documentation

**Source URL:** https://discmaster.textfiles.com/view/5218/237.d81/t.smithsid
**Author:** Doreen Horne (program); unattributed (text)
**Date:** 2004-01-01 (disk date)
**reliability:** primary

Full extracted content (as summarized by WebFetch):

SmithSID converts SID Player .mus → SongSmith format. Key facts:

- **Input:** SID music files (ending in ".mus")
- **Output:** SongSmith format files (beginning with "m." and "w.")
  - The "w." file: 1-block file, stores ADSR values and timbre information
- Reverse counterpart to SIDSmith (Scott Resh + Debbie Cruz, 1988)
- Performance: SuperCPU users get faster conversion; standard C64 may take 1 minute
  per medium-sized file
- Limitation: converted music may sound degraded "especially if there are a lot of
  enhanced sounds in the original SID file"
- Use case: access the large library of online .mus files in SongSmith's simpler editor

---

## 5. comp.sys.cbm — Loadstar #168 Thread (Usenet, 1998)

**Source URL:** https://groups.google.com/g/comp.sys.cbm/c/1TtXLOgICfs
**Title:** "Text From The Brand New LOADSTAR #168. Just hitting the streets now [1/8]"
**Date:** 1998 (Loadstar #168)
**reliability:** primary (direct Usenet post by Fender Tucker)

### Key SongSmith-relevant quotes from Fender Tucker:

**On the precursor to SongSmith (re: Loadstar issues #27–#28):**
> "Jim W. said that the songmaker they used in those days was written by Joe Garrett
> and Alan Gardner, and was the precursor to SongSmith."

Tucker also noted:
> "there's probably programming wizards who could reverse-engineer the song codes...
> but there's little chance of anyone wanting to."

**On Dave Marquis's ADSR technique (NOT SongSmith — uses "SID EDITOR"):**
Tucker loaded a Dave Marquis composition ("Trumpeter's Lullaby" from LS #167) in
SID EDITOR to check Voice 1:
> Attack = 5 / Decay = 0 / Sustain = 15 / Release = 0
> "changes as the song goes on"

SID EDITOR is a separate commercial tool sold by Parsec, P.O. Box 111, Salem MA 01970-0111.
Dave Marquis does NOT use SongSmith — he uses SID EDITOR.

**On Kenneth Barsky's Music Lists (LS #168):**
Kenneth Barsky created comprehensive catalogs of songs published across Loadstar's history.
Tucker condensed them to ~300 blocks for the issue.

---

## 6. Loadstar Compleat (Itch.io) — Content Inventory

**Source URL:** https://rodneylives.itch.io/loadstar
**Author:** rodneylives (John David Valois)
**Date:** 2024 (current)
**reliability:** secondary

SongSmith appears as a NAMED SEPARATE COLLECTION within the 680 MB Loadstar Compleat:
> "Plus: Brain Stuff, Compleat Bible, Compleat Programmer, Crosswords, Flags & Anthems,
> Knees' PUD, Loadstar Gourmet, Maurice Jones' card games, SID Music, ProseQuest,
> Roger Unwrapped, Serious Stuff, **SongSmith** and the art of Walt Harned!"

Also confirmed: "extra MP3s from Dave Marquis and Knees Calhoon" — Marquis's music
is available as MP3 + SID + MIDI in the archive, again confirming he is NOT a SongSmith
user (his songs have separate MIDI representations suggesting SID Editor → MIDI pipeline).

---

## 7. Lemon64 — "Loadstar Complete [SOLVED]" Thread

**Source URL:** https://www.lemon64.com/forum/viewtopic.php?t=65592
**reliability:** tertiary (partial finding only)

The thread's directory listing includes: **"SongSmith [bad]"** — confirming SongSmith
was a distinct directory in the Loadstar Compleat archive, but the archived version was
corrupted/incomplete in that user's copy. No technical discussion.

---

## 8. DeepSID — 'L' Focus Icon (Sep 2025)

**Source URL:** https://deepsid.chordian.net/
**Author:** Jens-Christian Huus (Chordian)
**Date:** September 7, 2025 (changelog)
**reliability:** primary

DeepSID added an 'L' focus icon specifically for:
> "composers who only used Loadstar Songsmith"

This is a September 2025 feature. It confirms that the Loadstar SongSmith composer
community is distinct enough to warrant a dedicated UI marker. The specific composers
who receive the 'L' icon are not listed in the changelog; they are derived from HVSC
engine metadata.

OPEN: Which HVSC engine strings trigger the 'L' icon? The four variants are:
Loadstar_SongSmith, Loadstar_SongSmith_v1, Loadstar_SongSmith_v2, Loadstar_SongSmith_v3.

---

## 9. AmigaLove — Fender Tucker Interview

**Source URL:** https://www.amigalove.com/viewtopic.php?t=1726
**reliability:** secondary (not fetched — listed in search results but not opened)

This interview with Tucker may contain additional SongSmith/Loadstar music context.

OPEN: Fetch this interview for any SongSmith or music tool references.

---

## 10. Commodore.ca — Fender Tucker Profile

**Source URL:** https://www.commodore.ca/commodore-history/fender-tucker-the-commodore-loadstar-man/
**reliability:** n/a — returned HTTP 403 Forbidden; could not be fetched.

OPEN: Try via Wayback Machine or alternative access.

---

## What Was NOT Found

- No discussion of SongSmith technical internals on Lemon64, commodore.ca, denial, or AtariAge
- No comp.sys.cbm threads specifically about SongSmith format (beyond the #168 thread)
- No Alan Beggerow personal website or blog discussing C64 composing
- No technical documentation of SongSmith format other than the converter docs above
- Dave Marquis's classical transcriptions are confirmed to use SID EDITOR (not SongSmith)

---

## Leads to Follow

1. **AmigaLove Fender Tucker interview** (https://www.amigalove.com/viewtopic.php?t=1726)
   — may contain SongSmith discussion.

2. **Loadstar Compleat (itch.io, $15)** — SongSmith is a named collection inside.
   The SongSmith directory likely contains all SongSmith-format songs as m./w. files,
   plus the editor binary with the full manual. This is the primary RE target.

3. **CSDb .d64 download** — `http://csdb.dk/getinternalfile.php/121491/Songsmith-Loadstar.d64`
   — the canonical Songsmith distribution disk. Contains editor + 8 demo tunes + 30-page
   manual (possibly as SEQ file). Fetch and mount in VICE.

4. **Alan Beggerow's HVSC STIL entry** — download STIL.txt and grep for
   `MUSICIANS/B/Beggerow_Alan/`. May contain curator notes about which tool he used.

5. **Loadstar 237 b.sidsmith BASIC loader** (4.5 KB — larger than other loaders)
   — fetch this file; it may contain embedded format constants or documentation about
   the conversion process that reveals m./w. file structure.

6. **Dave Marquis HVSC engine tag** — query hvsc84.db:
   `SELECT engine, COUNT(*) FROM sids WHERE path LIKE '%Marquis_Dave%' GROUP BY engine`
   — determines whether Marquis is in-scope for the SongSmith pipeline.

7. **Loadstar Letter back-issue catalog** (c64copyprotection.com PDF, too large to fetch)
   — may list which Loadstar issues first featured SongSmith as an in-issue program,
   vs the standalone product listing.

8. **comp.sys.cbm full search** — search Google Groups comp.sys.cbm for "SongSmith"
   directly via https://groups.google.com/g/comp.sys.cbm/search?q=SongSmith for
   additional threads not surfaced by web search.

9. **PRESTO (Dave Moorman, Loadstar #128)** — "sophisticated music processor, byte-stream
   memory system with dual stacks." This could be a separate C64 music tool with its
   own format. Check HVSC for any Moorman SIDs and their sidid engine tag.
