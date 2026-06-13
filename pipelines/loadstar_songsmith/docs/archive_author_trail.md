---
source_url: multiple — see per-section citations
fetched_via: WebSearch + WebFetch + raw binary analysis of Songsmith-Loadstar.d64 + HVSC SID headers
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: primary (binary evidence) + secondary (comp.sys.cbm + itch.io)
---

# Loadstar SongSmith — Author Trail and Composer Credits

## Confirmed Author: Joe Garrett (deceased)

From the embedded documentation text on the CSDb D64 disk (`Songsmith-Loadstar.d64`),
raw-string extracted at offset 0x014500–0x01C000:

```
  E RESPECTFULLY DEDICATE
 THIS DISK TO THE LATE OE ARRETT,
 THE MASTERMIND BEHIND .
```

(PETSCII encoding drops the 'J' initial character before 'OE' = 'JOE'; and blanks
the program name. Full decode: "We respectfully dedicate this disk to the late
**JOE GARRETT**, the mastermind behind **[SONGSMITH]**.")

**Conclusion:** Joe Garrett is the creator of SongSmith and was already deceased
at the time this version of the disk was produced.

---

## Precursor Tool — Joe Garrett + Alan Gardner

From Loadstar #168 (comp.sys.cbm transcription):

> "Jim W. said that the songmaker they used in those days [Loadstar issues #27-28]
> was written by Joe Garrett and Alan Gardner, and was the precursor to SongSmith."

This earlier tool (tentatively labeled "Song_Writer" in HVSC sidid taxonomy,
6 SIDs by Jeremy Thorne) predates SongSmith and used a different data format.
SongSmith was built as a successor/replacement.

---

## Demo Songs — Debby Cruz (Ryan)

From the disk's embedded welcome text:

```
 MASTER SONGSTRESS, EBBY RUZ OF
  RIARWOOD,
 [AND/BY]
 MASTER SONGSTRESS, DEBBY CRUZ RYAN.
```

(PETSCII: "Master Songstress, Debby Cruz of Briarwood [location], / and
the sample jukebox program [songs] by Master Songstress, Debby Cruz Ryan.")

**Debby Cruz** (also credited as Debby Cruz Ryan) was the primary demo-song
author for SongSmith. She contributed:
- Alouette (French folk song)
- Funiculi Funicula (Italian)
- Meadowlands (Russian folk song: "A very old Russian folk song which cannot be
  credited to any particular time")
- Muss I Denn (German folk song)
- Scarborough Fair
- Skye Boat Song
- The Parting Glass (Irish drinking song)

These 7 songs appear in the CSDb D64 and form the reference corpus.

From disk embedded text: "Funiculi Funicula — written in 1880 to commemorate the
opening of the funicular railway to the top of Vesuvius."
"Meadowlands — a very old Russian folk song whose melody is an old tune from France
[sic — the text has charset corruption here]." "The Parting Glass — Irish drinking
song, their standard farewell song."

---

## HVSC Composer Breakdown (304 SIDs, init=$CC00/play=$CC48)

Dave Marquis (130 SIDs, copyrights 1987–1994 Loadstar) — largest contributor.
  - Specialties: marches, classical transcriptions, rags, seasonal music.
  - First Loadstar appearance: Air_on_the_G_String (copyright '1987 Loadstar')
  - Notable: Four Seasons (Spring), multiple march transcriptions.

Alan Beggerow (48 SIDs, 1990–1993 Loadstar) — second largest.
  - Classic parlour songs, vaudeville, American standards (After the Ball,
    Alexander's Ragtime Band, etc.)

Debby Cruz (41 SIDs, ~1986-1989 Loadstar) — earliest and most prolific
  pre-Beggerow contributor.

John S. Davis (24 SIDs)
Mario Oropesa (22 SIDs) — Cuban classical transcriptions
James Weiler (8), Kevin Cloud (8), William M. Shockley (8), Terry Walker (7)
James C. Hilty (6) — also appears under "Creative Pixels/JC Hilty"
Joe Garrett (2 SIDs) — the author himself contributed 2 songs

---

## Fender Tucker (Loadstar Managing Editor)

Not the SongSmith author but the editorial guardian of the Loadstar archive.
- Real name Fender Tucker; Loadstar editor for most of the magazine's run.
- The Loadstar Compleat itch.io archive was created with his blessing.
- He answers reader questions about SongSmith in issues (Loadstar #168).
- Contact for historical questions: loadstarce.com community.

---

## CSDb Credits Status

The CSDb release page (id=122855) lists NO author credits ("No credits found").
This means Joe Garrett's name does not appear in the CSDb metadata — only in the
binary documentation text on the disk itself. Future CSDb contributors should
update the author field to "Joe Garrett".

---

## Leads to Follow

1. **Who is "Jim W." in Loadstar #168?** — Fender Tucker quotes him as providing
   the Garrett/Gardner attribution. Possibly a longtime Loadstar staffer.

2. **What happened to Joe Garrett?** — The disk says "the late Joe Garrett", implying
   he died before this version shipped. Narrowing the date would confirm which version
   this disk represents. The copyright dates on the SIDs (1986-1989 for Debby Cruz)
   suggest Joe Garrett died before ~1989.

3. **Alan Gardner** — co-author of the precursor tool. No other references found.
   May have been a Softdisk staffer.

4. **Debby Cruz / Debby Cruz Ryan** — "of Briarwood" (Briarwood = neighborhood
   in a US city, possibly Shreveport LA given Softdisk's location). She contributed
   the demo songs for the reference disk. Not a known HVSC demoscene name.

5. **Dave Marquis** — 130 SIDs, earliest from 1987. Was he a Loadstar subscriber
   contributing tunes or a staffer? His HVSC entry says USA.

6. **Search comp.sys.cbm for Joe Garrett obituary / SongSmith authorship credits**
   — Google Groups query: `site:groups.google.com/g/comp.sys.cbm "Joe Garrett"`
