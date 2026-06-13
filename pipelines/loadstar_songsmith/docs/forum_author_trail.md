---
source_url: multiple (see per-section headers)
fetched_via: WebSearch + WebFetch
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: secondary (synthesized from primary sources)
---

# Loadstar SongSmith — Author & Community Trail

## Summary

SongSmith is a Loadstar in-house music tool by **Joe Garrett**. It evolved from an
earlier songmaker (1987-era) also by Garrett plus Alan Gardner. The tool was distributed
as a standalone Softdisk product and also appeared in Loadstar issues (confirmed: issue
237, ~2004). Key community figures: Debby Cruz (composer + SIDSmith co-creator), Scott
Resh (Loadstar staffer + SIDSmith co-creator), Dave Moorman (Loadstar editor, wrote
documentation), Doreen Horne (SmithSID reverse converter).

---

## Joe Garrett — SongSmith Author

**Source:** `b.songsmith` BASIC loader file from Loadstar 237 (Discmaster, 237.d81)

The BASIC loader for SongSmith contains:
```
data"by [JOE] [GARRETT]
data"(c) 2005 by mid$ & asc publishing, right$ nc.
data"www.eloadstar.com
```
(The text "mid$ & asc publishing, right$ nc." is BASIC keyword collision artifacts;
the actual copyright string is "(c) 2005 by Softdisk Publishing, Inc." or similar
— the BASIC tokenizer converted substrings to BASIC commands.)

**Confirmed:** Joe Garrett is the SongSmith author. Copyright 2005. Published via
eloadstar.com.

Also from HVSC Musicians.txt: Joe Garrett — USA (listed; no additional detail).

**Prior role:** Garrett also co-wrote the PREDECESSOR songmaker with Alan Gardner,
used in Loadstar issues #27–28 (~1987–1988). Source: comp.sys.cbm Loadstar #168 thread
(Fender Tucker quote, see forum_discussion.md).

---

## Alan Gardner — Precursor Co-Author

**Source:** comp.sys.cbm thread "Text From The Brand New LOADSTAR #168"
(https://groups.google.com/g/comp.sys.cbm/c/1TtXLOgICfs)

Alan Gardner co-wrote the original songmaker with Joe Garrett. This was used for
Loadstar issues #27–#28, predating SongSmith proper.

From HVSC Musicians.txt: Alan Gardner — USA (listed; no additional detail).

OPEN: Confirm whether Gardner also contributed to SongSmith proper, or only to the precursor.

---

## Debby Cruz — Composer + SIDSmith Co-Creator

**Source 1:** CSDb release id=122855 (SongSmith C64 Tool) — seven demo tunes by Cruz, Debby.
**Source 2:** t.sidsmith documentation, Loadstar 237 (Discmaster 237.d81):
> "SIDSmith: Converts music files from SONGSMITH format into SID PLAYER format.
> Developed by Debby Cruz and Scott Resh."

Debby Cruz is simultaneously:
1. A SongSmith-era composer (folk/classical transcriptions for Loadstar)
2. Co-creator of SIDSmith (the SongSmith→SID Player converter)

CSDb confirms: Cruz, Debby composed "Battle Cry of Freedom" for Loadstar (1989),
load address $C200, init $CC00, play $CC48, data size $0DE5.

From HVSC Musicians.txt: Cruz, Debby (listed; no country; no additional detail).

---

## Scott Resh — Loadstar Staff + SIDSmith Co-Creator

**Source 1:** Search results confirm Scott E. Resh was Loadstar staff alongside Jeff Jones,
working with Fender Tucker.
**Source 2:** t.sidsmith documentation, Loadstar 237:
> "SIDSmith... Developed by Debby Cruz and Scott Resh."
**Source 3:** t.smithsid documentation, Loadstar 237:
> "SmithSID is the reverse counterpart to SIDSMITH (created by Scott Resh and Debbie Cruz
> in 1988)."

Scott Resh's SIDSmith was created **1988** — this predates SongSmith's copyright year
of 2005, suggesting either:
(a) SIDSmith was written for an earlier version of SongSmith (the precursor format), or
(b) The converter was updated in the 2005 era to match current SongSmith.

OPEN: Verify SIDSmith creation date. The "1988" date in SmithSID's docs refers to the
ORIGINAL creation of SIDSmith, making it contemporary with the Garrett/Gardner precursor
era. The Loadstar 237 release (2004/2005) may be a revised version of SIDSmith.

---

## Doreen Horne — SmithSID Creator

**Source:** t.smithsid documentation, Loadstar 237 (Discmaster 237.d81)

Doreen Horne created **SmithSID** — converts SID Player format (.mus files) back to
SongSmith format (m./w. prefix files). She is otherwise unknown in publicly searchable
databases.

---

## Dave Moorman — Loadstar Editor & SongSmith Documentation Author

**Source 1:** t.songsmith documentation, Loadstar 237: "text by Dave Moorman"
**Source 2:** Dave Moorman biography (C64-Wiki + portcommodore.com)

Dave Moorman took over Loadstar from Fender Tucker at issue 200 (2001) and published
through issue ~249 (~2006/2007). He wrote the Loadstar 237 article documenting SongSmith.
He is also the author of:
- PRESTO (issue #128) — "a sophisticated music processor featuring a byte-stream memory
  system with dual stacks for editing capabilities" (his own music tool, separate from SongSmith)
- DotBASIC (a BASIC extension)
- Various games and utilities

Moorman's personal site: https://themoormanfiles.com/ (covers his orchestral composition
work, not C64 tools).

---

## Fender Tucker — Loadstar Managing Editor (1987–2000)

**Source:** commodore.ca Fender Tucker article; comp.sys.cbm Loadstar #168 thread

Fender Tucker was managing editor of Loadstar issues #47–199. He confirmed the
Garrett/Gardner precursor history in print (Loadstar #168, 1998) and used "SID EDITOR"
(a separate commercial tool from Parsec, P.O. Box 111, Salem MA 01970-0111) to examine
Dave Marquis's compositions.

Tucker spent 25 years as a guitar player before switching to C64. After Loadstar, he
published works under Ramble House imprint and continues to offer Loadstar Compleat.

---

## Dave Marquis — Heavy Composer (NOT a SongSmith user)

**Source:** comp.sys.cbm Loadstar #168 thread; Ramble House Loadstar Compleat page

Dave Marquis is the most prolific Loadstar music contributor, known for classical
transcriptions (Bach, Mozart, Vivaldi, Rossini, etc.). He used **SID EDITOR** (by
Parsec, Salem MA), NOT SongSmith. His compositions came with the Loadstar Compleat
as SID + MIDI files.

From HVSC Musicians.txt: Marquis, Dave — USA (listed).

OPEN: Confirm which sidid engine tag Marquis's SIDs use. If they're NOT Loadstar_SongSmith,
they belong to a separate pipeline.

---

## Alan Beggerow — Composer (SongSmith status unconfirmed)

**Source:** HVSC Musicians.txt (USA); DeepSID link to Oldsmobile.sid and Bill_Bailey.sid

Alan Beggerow has SIDs in HVSC at MUSICIANS/B/Beggerow_Alan/. The prior research
session notes he's in HVSC but STIL entries were not retrieved.

OPEN: Confirm via sidid whether his SIDs use Loadstar_SongSmith engine tag. If yes,
he is one of the heavier SongSmith composers.

---

## John S. Davis — Composer (SongSmith status unconfirmed)

**Source:** HVSC Musicians.txt (USA)

Listed in HVSC musicians. Sidid engine tag unconfirmed for his SIDs.

OPEN: Query hvsc84.db for Davis_John_S SIDs and check engine field.

---

## Leads to Follow

1. **Joe Garrett's full programmer background**: Was he a Softdisk employee, or a
   Loadstar reader/contributor? The "(c) 2005 by... Softdisk Publishing" suggests employee.
   Check Softdisk masthead in Loadstar issues circa 2000–2005.

2. **SIDSmith 1988 vs 2005**: The "created in 1988" date in SmithSID docs is key —
   if SIDSmith was ORIGINALLY written in 1988, it was written for the Garrett/Gardner
   precursor format, not SongSmith proper. This has implications for whether the
   SongSmith format is the SAME as the 1988 precursor format or evolved.

3. **Dave Marquis's actual SID engine**: His 126+ SIDs are in HVSC. If sidid tags them
   as something other than Loadstar_SongSmith, they are out of scope. If they ARE tagged
   Loadstar_SongSmith, he is by far the heaviest user.

4. **PRESTO (Dave Moorman, issue #128)**: "byte-stream memory system with dual stacks"
   sounds like a tracker/step-sequencer. Could PRESTO songs appear in HVSC under a
   different engine tag? Check Moorman's HVSC presence.

5. **Fender Tucker direct contact**: Tucker is active in the Ramble House book community
   and online. He may be reachable via Ramble House (ramblehouse.com) for a direct
   interview about SongSmith's technical model.

6. **Scott Resh contact**: As a former Loadstar staffer who co-wrote SIDSmith, he may
   have source code or format documentation. No current contact info found.
