# X-Ample / Compotech — Group History (Wiki Sources)

**source_url:** https://www.c64-wiki.de/wiki/X-ample_Architectures
                https://c64.ch/groups/377/X-Ample_Architectures
                https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider
                https://www.vgmpf.com/Wiki/index.php?title=Thomas_Detert
                https://www.c64-wiki.de/wiki/Thomas_Detert
                https://csdb.dk/group/?id=245
**fetched_via:** WebFetch
**fetch_date:** 2026-06-13
**reliability:** secondary (fan wikis and aggregators; cross-checked against primary CSDb)

---

## X-Ample Architectures — Group Overview

**Founded:** July 1988
**Closed:** 1997 (rebranded to Büttner GmbH, 1997-2000)
**Location:** Germany
**Tagline:** "Bit For Bit A Hit"
**Name meaning:** Stands for "Example" (confirmed in 1988 release "Blade Runner")
**Rating (CSDb):** 8.8/10 (22 votes)

---

## Membership

From c64-wiki.de (verbatim + translation):

> "X-Ample (kurz: XAP / gesprochen wie 'example') startete in den 1980ern als
> Demogruppe und wurde in den 1990ern eines der aktivsten Spiele-Entwickler-Teams
> auf dem C64."

Translation: "X-Ample (abbreviated XAP / pronounced like 'example') started
in the 1980s as a demo group and became one of the most active game development
teams on the C64 in the 1990s."

**Founders per c64-wiki.de:** Thomas Detert, Michael Detert, Helge Kozielek,
Thomas Heinrich

**Founders per CSDb (group #245):** Stephen Taylor, Takashi, General X,
Chap Bizarre

**Discrepancy note:** The c64-wiki.de and CSDb lists differ. Likely explanation:
the CSDb group page lists the *demo group* founders (1988 demo era: Stephen
Taylor, Takashi, General X, Chap Bizarre), while c64-wiki.de lists the
*core music/tech team* who drove the sound system (Detert, Kozielek, etc.).
Thomas Detert co-founded X-Ample per VGMPF ("in summer 1988 founded the demo
groups Omega 8 and X-Ample Architectures") but this appears in the "music team"
framing rather than the demo-group founding.

**Key personnel from c64-wiki.de (verbatim list):**
- Helge Kozielek (Programmer)
- Thomas Detert (Musician)
- Michael Detert (Graphics)
- Thomas Heinrich (Graphics)
- Joachim Fräder (Programmer)
- Ivo Herzeg (Programmer)
- Andreas Becker (Programmer)
- Markus Schneider (Musician)
- Michael Büttner (credited as Buttner)

**c64.ch member table (confirmed, verbatim):**

| Name | Role(s) | Joined |
|---|---|---|
| General X | Graphician | July 1988 |
| Takashi | Coder, Musician, Graphician | July 1988 |
| Chap Bizarre | Coder, Graphician | July 1988 |
| Stephen Taylor | Musician | July 1988 |
| Markus Schneider | Musician, Coder | March 1989 |

---

## Key facts for SID player context

1. **Helge Kozielek** was the primary programmer of the X-Ample player (per
   Thomas Detert interview: "Helge Kozieleck created together with Markus
   Schneider the X-ample Music Player"). He also appears in the c64-wiki.de
   member list as "Programmer."

2. **Joachim Fräder** built the *editor* surface (Compotech UI), not the
   player. Also coded the X-Ample Intro Architect (1989), confirmed by
   comp.sys.cbm Usenet post (1997): "Intromaker is X-Ample's Intro Architect,
   coded by Joachim Freader."

3. **Markus Schneider** joined March 1989 (post-founding). He brought the
   Parsec Music Editor player code. He is both the engine author AND a
   Compotech V2.1 co-coder.

4. **Thomas Detert** is a co-founder (July 1988) and the main composer.
   He used Chris Hülsbeck's Soundmonitor early on, then switched to the
   X-Ample player. His 92 X-Ample HVSC SIDs all post-date 1989.

5. **Tufan Uysal (SoNiC)** is NOT an X-Ample Architectures member. He was
   in Smash Designs, The Art Project Studios, and The Obsessed Maniacs.
   He became the largest producer of X-Ample-format SIDs (123 tunes in HVSC)
   via his XTracker editor.

---

## Thomas Detert biography (c64-wiki.de + VGMPF, synthesized)

- **Born:** 1969, Germany
- **C64 active:** 1988-1996 (HVSC SIDs run through this period)
- **Post-C64:** Professional dance/trance/house music producer from 1993
  (ACTIVATE music productions 1993; AIRBASE media GmbH CEO from 1993)
- **Considered by community:** "one of the best German C64 musicians"
  (c64-wiki.de paraphrase)
- **Style:** Authentic SID instruments and drums; game music specialist

From c64-wiki.de (verbatim, translated):
> "Thomas Detert gehört für viele zu den besten deutschen C64-Musikern. In
> den späten 80ern komponierte er Stücke im Soundmonitor."
Translation: "Thomas Detert is considered by many to be one of the best
German C64 musicians. In the late 80s he composed pieces in Soundmonitor."

His player preference evolution (from HVSC engine tags):
1. Soundmonitor (pre-1989 work)
2. X-Ample player (1989 onward) — after Kozielek+Schneider developed it
3. XTracker V4.00 Beta (1996) — beta tester/contributor

**Detert's personal player fork** (`Thomas_Detert` sidid variant) has
these distinguishing characteristics (from sidid.cfg analysis):
- `09 0F / 8D 18 D4` — forces master volume nibble = $F (15 = max volume),
  not just ORing in whatever filter state variable contains
- `F0 03 / 20 ?? ??` — BEQ-always used as a 2-byte JMP (saves 1 byte)
- `8D 16 D4` — explicit writes to filter cutoff high ($D416)
These are all sound-mixing optimizations for game use, where maximum volume
and filter control were priorities.

---

## Markus Schneider biography (VGMPF, synthesized)

- **Handles:** Markus Schneider (MS), Diflex (1988-??), Synth-Man (1987-1988)
- **Joined X-Ample:** March 1989
- **Roles:** Musician AND Coder (unusual — he both wrote music and coded players)
- **Post-C64:** Amiga music (TFMX, Tusker game for System 3); DOS driver work
  (TBSA, ~1991, possibly by Mario Knezovic)
- **2019:** Still active — Geir Tjelta/Comptech-X "probably private player for
  X-Ample members" (sidid.nfo)

**Quote (CSDb, verbatim):**
> "I hate Disco Tunes! But i do what people want."

(Schneider's most-downloaded HVSC SID is probably "No Mercy" — a Katakis-
era game tune)

---

## X-Ample notable releases (music/tool context)

From CSDb group #245 (92 total releases):

**Demos (music context):**
- Art Exhibition (1988) — early group identity piece
- Artists of Time (1988) — 8,758 downloads, most downloaded X-Ample demo
- Breeze of Diogenes (1989) — 6,883 downloads
- Spirit of Art (1989) — earliest known X-Ample music showcase
- Veterans of Style (2017) — collaboration with Digital Excess, showing
  the group remained active into the modern era

**Games (SID music embedded):**
- Blue Angel 69 (1989) — Thomas Detert music; an early SID showcase
- Gordian Tomb (1990) — CP Verlag; Thomas Detert music
- Another World (1990) — CP Verlag; Thomas Detert music
- B-Bobs (1990) — CP Verlag
- Starforce (1991) / Mega Starforce (1993) — Thomas Detert music
- Parsec (1993) — the game named after the music editor
- Quadrant (1993) — Thomas Detert music; includes Detert's "Quadrant.sid"
  (Bacco_Digi engine per hvsc84.db — a DIFFERENT digi player, not X-Ample_Digi)

**Note on "Double Density" label:** Per CSDb: "Double Density was NOT X-Ample's
commercial label but rather a label created by Walter Konrad (formerly of Seven
Eleven), who managed Software Acquisition at CP Verlag." X-Ample's publishing
was through CP Verlag, not a self-owned label.

---

## Productions and external publishers

- CP Verlag (publisher of Magic Disk 64, Game On, Golden Disk 64 — major
  German C64 magazine/software publisher)
- X-Ample tunes appeared extensively in Magic Disk 64 menus (Thomas Detert
  credited for numerous "Magic Disk 64 (YYYY/MM)" tunes in HVSC)
- After 1997 disbandment, Michael Büttner (Büttner GmbH) ran the company
  until 2000

---

## CSDb user comments about X-Ample group (verbatim)

From the CSDb group page comments:

> **Comos (2011):** "Indeed"

> **Rough (2011):** "Those guys made some brilliantly designed demos in 88/89."

These comments confirm the group's artistic reputation in the demo era,
separate from their later game development work.
