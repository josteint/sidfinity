# X-Ample / Compotech — Developer Interviews

**source_url:** https://remix64.com/interviews/interview-markus-schneider.html
                https://remix64.com/interviews/interview-thomas-detert.html
**fetched_via:** WebFetch
**fetch_date:** 2026-06-13
**content_date:** unknown (Remix64 interviews, approximate 2000s-era)
**reliability:** secondary (interview transcripts; self-reported)

---

## Markus Schneider Interview (Remix64)

**URL:** https://remix64.com/interviews/interview-markus-schneider.html

### On the X-Ample player development (verbatim extract):

> "The last soundplayer based on my old player. Helge Kozielek and Mario van
> Zeist did some corrections to optimise the speed. At the same time Joachim
> Fraeder programmed the surface."

**Technical interpretation:**
- "The last soundplayer" = the Compotech editor player (as used up to
  Compotech V2.1, 1995).
- "Based on my old player" = the lineage is Schneider's original Parsec
  Music Editor driver (1989) → X-Ample player → Compotech player.
- "Helge Kozielek" confirmed as the optimizer (corroborates sidid.nfo
  authorship: "Markus Schneider & Helge Kozielek").
- "Mario van Zeist" is an additional contributor not listed in sidid.nfo.
- "Joachim Fraeder programmed the surface" = Fräder coded the editor UI
  (not the player). This cleanly separates the player (Schneider + Kozielek)
  from the editor front-end (Fräder).

### On driver evolution:

The VGMPF wiki (https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider)
paraphrases the interview:
> "Schneider spent 2 months in 1988 writing him a better sound driver"
> "spent 7 weeks on it in 1989 when merging with X-Ample Architectures' sound
> driver"

**Interpretation:** The "2 months in 1988" driver became the Parsec Music
Editor. The "7 weeks in 1989" effort is when Schneider merged/integrated with
the nascent X-Ample group and unified the player code — resulting in the
Compotech V1 player.

### On TFMX (Amiga):

Schneider received Chris Hülsbeck's TFMX editor "for free" for Amiga work
(the Tusker game). This is unrelated to the C64 X-Ample format but
establishes the X-Ample→TFMX→Amiga career transition.

---

## Thomas Detert Interview (Remix64)

**URL:** https://remix64.com/interviews/interview-thomas-detert.html

### On the X-Ample player origin (verbatim extract):

> "the Routine took too much time to use it in games or bigger demoparts,
> so our programmer Helge Kozieleck created together with Markus Schneider
> the X-ample Music Player."

**Context:** "the Routine" = Chris Hülsbeck's Soundmonitor, which Detert
originally used (his pre-1989 HVSC SIDs are tagged `Soundmonitor`).
Soundmonitor was too slow for games — the X-Ample player was created
specifically to be fast enough for embedded game use.

**Attribution:** Detert's account matches Schneider's: Kozielek + Schneider
built the player. Detert was the composer user, not the coder of the player.

### Other interview context:

Thomas Detert (born 1969, Germany). Co-founder of X-Ample Architectures
(July 1988, with Michael Detert, Helge Kozielek, Thomas Heinrich per
c64-wiki.de). Composed music for X-Ample games from ~1989 to 1996.
Left C64 to do professional dance/trance/house music from 1993 (founded
ACTIVATE music productions 1993, then AIRBASE media GmbH).

---

## comp.sys.cbm Usenet — X-Ample mentions

**Source:** Google Groups, comp.sys.cbm archive search
**URL:** https://groups.google.com/g/comp.sys.cbm

No posts specifically discussing Compotech, XTracker, or X-Ample player
internals were found. The following tangential mentions exist:

1. **1997-12-21, Per Bolmstedt** — mentions "Intromaker is X-Ample's Intro
   Architect, coded by Joachim Freader" as "the most flexible and advanced
   Intromaker" encountered. This confirms Joachim Fräder as the Intro
   Architect coder (separate from Compotech).

2. **1997-05-23, WaD** — inquires about "the X-Ample game" and "what
   happened to X-Ample" — confirming X-Ample became inactive by ~1997.

3. **1993-06-23, Tony Clark** — mentions "Detret/X-Ample about uploading
   and distributing some of his PD games." (Likely "Detert/X-Ample.")

4. **1993-04-13, msma...@cc.helsinki.fi** — references "Crest, Xample,
   Fairlight (DEMO)" in a music/copyright discussion.

**Assessment:** Usenet has no substantive technical discussion of the
X-Ample player format. The player was commercial/embedded; format
documentation was never publicly posted to Usenet.

---

## forum64.de — X-Ample mentions

**Searches performed:** "X-Ample Compotech XTracker SID", "Markus Schneider
OR Thomas Detert Musik Editor SID player C64"

**Result:** No dedicated forum64.de threads about Compotech/XTracker/X-Ample
internals were found in indexed search results. forum64.de returned 403
(Forbidden) on direct board-listing fetches, blocking direct browse.

The "Sidplayer für den echten C64?" thread (forum64.de, thread 156247) was
found in search results but returned HTTP 403 when fetched.

**Assessment:** forum64.de likely has passing X-Ample mentions in discussions
about C64 music players, but no thread dedicated to reverse-engineering or
documenting the X-Ample format was found.

---

## Lemon64 — X-Ample mentions

**Searches performed:** Multiple queries targeting Lemon64 Compotech/XTracker
threads and the "Comparison of C64 Music Editors" thread (viewtopic.php?t=67248).

**Result:** Lemon64 returned HTTP 503 (Service Unavailable) on all direct
fetch attempts during this session. The "C64 Music tracker software" thread
(t=71942) and "Comparison of C64 Music Editors" thread (t=67248) both
returned 503.

From search result snippets only: the Chordian comparison-of-editors blog
post references "The Compotech Editor from X-Ample & Lords of Sonic" as a
comment addition to the comparison table, but the table itself only covers
modern editors (GoatTracker, CheeseCutter, SID-Wizard, etc.) — Compotech
is not in the main table.

**Assessment:** Lemon64 is temporarily unavailable; a future session should
attempt these threads directly.

---

## Codebase64 — X-Ample mentions

**Search performed:** "Codebase64 Compotech OR X-Ample music OR XTracker
SID player format"

**Result:** No Codebase64 wiki article about X-Ample, Compotech, or XTracker
was found. Codebase64 has SID programming docs (https://codebase64.net/
doku.php?id=base:sid_programming) but nothing X-Ample-specific.

---

## X-Ample official site mentions

- **http://www.xample-music.com/sids.html** — X-Ample SID archive: returned
  ECONNREFUSED (domain appears inactive as of 2026-06-13).
- **http://sids.xap64.de/** — mirror: returned ECONNREFUSED.
- **http://artscene.textfiles.com/music/c64/HVSC/Schneider_Markus/** —
  Textfiles.com HVSC mirror of Schneider's SID files (confirmed accessible
  in search results).
