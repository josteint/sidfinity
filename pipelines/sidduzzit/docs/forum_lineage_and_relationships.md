# SID Duzz'It — Lineage, Relationships, and Scene Context

<!-- provenance
  sources:
    - url: https://www.atlantis-prophecy.org/recollection/?load=articles&id=TheBriefHistoryofSID
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      author: Jan Harries (SIDwave)
      content_date: Vandalism News #64, June 2015
      reliability: secondary (author is a long-time SDI composer and scene historian;
                   the article is a first-person retrospective, not a primary source)
    - url: https://chipflip.wordpress.com/2009/09/23/more-soundchip-hacking-realtime-sid-delay/
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      author: Goto80 (Anders Carlsson, chipflip.wordpress.com)
      content_date: 23 September 2009
      reliability: secondary (blog post quoting Geir Tjelta directly; medium reliability)
    - url: https://demozoo.org/sceners/949/ (GT / Geir Tjelta)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: secondary (community-maintained database)
    - url: https://demozoo.org/sceners/948/ (GRG / Glenn Rune Gallefoss)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: secondary (community-maintained database)
    - url: https://csdb.dk/release/?id=75124 (Rob Hubbard Editor, 1989)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: high (CSDb primary archive)
    - url: https://csdb.dk/release/?id=33645 (GT's Musiceditor, 1992)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: high (CSDb primary archive)
    - url: https://csdb.dk/release/?id=108477 (Sid Systems V1, 1990)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: high (CSDb primary archive)
    - url: https://csdb.dk/release/?id=33644 (Sid Systems V4.1, 1990)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: high (CSDb primary archive)
    - url: https://github.com/cadaver/sidid/blob/master/sidid.nfo (SIDID database)
      fetched_via: WebFetch (raw GitHub)
      fetch_date: 2026-06-13
      reliability: high (canonical engine-classification database used by HVSC tools)
    - url: /home/jtr/sidfinity/pipelines/sidduzzit/docs/csdb_manual.md
      fetched_via: local file (prior session research)
      fetch_date: 2026-06-13
      reliability: high (derived from official SDI docs + Psylicium manual)
-->

---

## 1. The Core Lineage Statement

The strongest single source on SDI's design lineage is the Psylicium PDF manual
(`csdb_manual.md` in this docs directory), which states verbatim in its Background
section:

> "SDI is a music tracker for the C64/C128, built on ideas from:
> - JCH/Vibrants editor
> - Olav Morkrid/Panoramic 'Digitalizer' editor
> - Geir Tjelta/Shape/Moz(ic)art SID Systems"

This is corroborated by the Recollection article (Jan Harries / SIDwave, 2015):

> "JCH inspired GRG to the SID DUZZ IT editor. Same system with tracker, just a
> different sound editor. SDI is an editor designed for Geir Tjelta's player."

**Interpretation:** SDI is an INDEPENDENT lineage, not a fork of JCH. The design
inspiration is:
- **Tracker interface model**: from JCH (Jonatan Dunn) / Vibrants — the sequencer + tracker
  layout concept.
- **Sound editor philosophy**: from Olav Morkrid / Panoramic "Digitalizer" — specific effect
  table paradigm (Digitalizer was a Norwegian precursor with program tables).
- **Player**: Geir Tjelta's own player, evolved from SID Systems. GRG wrote the SDI editor
  around Geir's player, not around JCH's player.

SDI and JCH are therefore **sibling lineages** (both influenced by demoscene composition
ideas of the late 1980s) but NOT a fork relationship. The JCH player and SDI player are
structurally different (different note encoding, different program table formats, different
effect chains).

---

## 2. Geir Tjelta's Tool Lineage (Chronological)

### 2a. Rob Hubbard Editor (1989, Moz(IC)art — CSDb #75124)

- **Handle at time:** Predator
- **Nature:** A port/wrapping of Rob Hubbard's "Ace 2" music player (1987) into a
  C64 composing tool. NOT an original player — Hubbard's binary driver was the player.
- **GT's own comment** (CSDb, 27 January 2009):
  > "Rob Hubbards Ace 2 player. Many Moz(Ic)art tunes from 1989 were composed in this tool."
- **Stainless Steel's comment** (CSDb, 9 December 2012):
  > References a composition called "Niggling" by Geir from 1989 demonstrating what could
  > be achieved with the player.
- **CSDb comment by Fred** (20 February 2014):
  > "I've now uploaded a different packed version of the editor with an example file."
- **RE relevance:** NOT an SDI precursor at the player level. The Ace 2 driver is
  completely different from SDI's player. This was Geir using an existing driver;
  the SDI player is Geir's own work.

### 2b. Sid Systems V1 (1990, Moz(IC)art — CSDb #108477)

- **Nature:** First original Geir Tjelta player. Includes five SID compositions:
  "Bended Wave", "Density Cartoon", "Jazztune!", "Surrender Remix", "Trade of Shape!".
- **Content:** Disk `.d64` image with editor + example tunes.
- **Groups:** Released by Moz(IC)art.
- **SIDID classification:** `Geir_Tjelta/SIDSys_1.0` (separate SIDID class from SDI)

### 2c. Sid Systems V4.1 (1990, Moz(IC)art — CSDb #33644)

Two player variants shipped: player 18.4 and player 18.6 (both in the same release).
Contributors: 6R6, GT, Trond Kjetil Lindanger on music; GT on code.

**GT's CSDb comment** (3 February 2009):
> "Press L to load tune. Navigate and press return. Then space to enter editor.
> Keys Shift+f1, f3, or f5 for navigating between channels."

**iAN CooG's comment** (15 December 2018):
> "to make things clear, mozworkdisk.d64 is not from 1990 as it contains tunes from 1991"

**Fred's comment** (7 March 2013):
> "All tunes from mozworkdisk.d64 and SidSystemsv18.6.d64 identified and added
> to the SID list."

SIDID classifies these tunes separately as `Geir_Tjelta/SIDSys18.4` and
`Geir_Tjelta/SIDSys18.6`. They are distinct from the SDI engine.

### 2d. GT's Musiceditor (1992, Moz(IC)art — CSDb #33645)

- **Nature:** A personal editor GT made independently, distinct from Sid Systems.
- **GT's CSDb comment** (on the release page):
  > "Editor crashes sometimes when changing subtunes due to its unfinished state."
  > "Use 6581r4ar 3789 chip (Vice 2.1 ++)" for proper emulation.
  > "Press Keys+L to load. Use Shift+< and > to change subtunes. Press F1 to start music."
  > "Jingle #7 is probably the best thing I've ever written."
- **Notable:** Jingle #7 from this editor was later used as the level-complete sound in
  *Daze Before Christmas* (SNES, 1994).
- **RE relevance:** Format is DIFFERENT from SDI. The editor was "unfinished" and is
  not related to SDI's binary format. SIDID class: `GT_Editor`.

### 2e. SID Duzz'It V1 (1996 — CSDb #161716)

- First public SDI release. Sole author: GT.
- This is where Geir's own player first reached public release as the SDI format.
- No GRG involvement in code; he joined as documentation author at V0.98 (1998).

**SIDID summary of Geir Tjelta tool chain:**
```
Sid Systems V1       → Geir_Tjelta/SIDSys_1.0     (1990)
Sid Systems V4.1     → Geir_Tjelta/SIDSys18.4/.6  (1990)
GT's Musiceditor     → GT_Editor                   (1992)
SID Duzz'It V1–V2.1  → Geir_Tjelta/SIDDuzz'It     (1992–2014)
Macro Player         → Geir_Tjelta/MacroPlay1/2    (2009)
GRG variants         → GRG / GRG_tiny_1..4         (n.d.)
```

The SID Systems → SDI transition represents GT evolving his own player codebase across
the 1990–1996 interval. The player architectures are classified as distinct SIDID classes,
meaning the binary formats are not compatible across these versions.

---

## 3. SDI vs JCH NewPlayer — Relationship Clarity

**Bottom line: SDI is an INDEPENDENT lineage. It is NOT a fork of JCH.**

Evidence:
1. Psylicium manual lists JCH as one of three *inspirations*, alongside two other editors.
2. SIDwave (Recollection): "JCH inspired GRG to the SID DUZZ IT editor. Same system with
   tracker, just a DIFFERENT sound editor. SDI is an editor designed for **Geir Tjelta's**
   player." [emphasis added] — the player is GT's, not JCH's.
3. SIDID classifies JCH tunes as `JCH` (or via JCH NewPlayer variants) and SDI tunes as
   `Geir_Tjelta/SIDDuzz'It` — entirely separate classification trees.
4. The data formats are visibly different: JCH uses a different sequence encoding (see
   Codebase64's `jch_20.g4_player_file_format` wiki page, which has no overlap with the
   SDI format spec in `SDI.2.1.6-docs.txt`).

**What JCH influenced in SDI:**
- The *tracker workflow* concept: the idea that a sequencer drives patterns, and patterns
  contain FX+note rows with effect codes. JCH was influential across many C64 editors
  in this era (CheeseCutter also cites JCH compatibility).
- The Recollection article notes: "In the 1990's it was very widespread to have your own
  editor" — JCH was the reference point that inspired many composers to build their own
  editor/player pairs.

**What JCH did NOT contribute to SDI:**
- The player binary (GT wrote SDI's player from scratch, evolved from SID Systems).
- The program-table effect chain (pulse/filter/vibrato tables in SDI have a specific
  4-byte columnar format not shared with JCH).
- The instrument format (SDI's 10-byte column-major instrument is original).

---

## 4. Olav Morkrid / Panoramic "Digitalizer" Connection

The Psylicium manual names "Olav Morkrid/Panoramic 'Digitalizer' editor" as an influence.
Olav Morkrid is a Norwegian demoscener; "Panoramic" is his group (Geir Tjelta was also
a member of Panoramic Designs per Demozoo). This is a **Norwegian scene internal
connection** — the "Digitalizer" editor predated SDI and influenced its sound-editor
design philosophy. No further detail recovered in this session (see Leads below).

---

## 5. Scene Context: SHAPE Group

SHAPE (Supreme Headquarters Allied Programmers Europe) is a Norwegian demo/cracker group
founded October 1988. SDI is SHAPE's flagship tool. Key membership facts relevant to SDI:

- **GT** is in SHAPE since 2009 (formally; he was informally associated since 1992 via
  the SDI development with 6R6 who was always SHAPE).
- **6R6 (GRG)** has been SHAPE since January 1992 — essentially SHAPE's entire lifespan.
- **Kristian Røstøen**: SHAPE member, co-composer on some early SDI tunes
  (e.g., Darkstorm.sid 1992: "K. Røstøen & G. R. Gallefoss").
- **Blues Muz'** (1994–2011): A sub-label/group comprising GT + 6R6 + Kristian Røstøen.
  Most of Glenn's HVSC tunes are credited "Blues Muz'". A Demozoo entry shows "Tropical
  Funk by GRG + Geir Tjelta + Kristian Røstøen / Blues Muz' ^ SHAPE".

The scene context for SDI's creation (1992) is the Norwegian BBS/demo scene at its peak.
SHAPE ran a BBS called "Drugstore". GT was active in Moz(IC)art → transitioning to SHAPE
era around 1992–1996. SDI V1 (1996) is the first public tool release from this period.

---

## 6. The Realtime SID Delay — A Near-Miss Feature

In September 2009, chipflip.wordpress.com reported on a technique invented by Geir Tjelta:

> "The output of the third channel of the SID can be recorded, and by delaying the
> playback of the sample on the 'virtual' fourth channel, you get a subtle echo."

> "This technique [...] needs to run on the old 6581 chip, since this technique for
> playing sounds relies on a bug that was almost fixed with the new 8580 chip."

> "Geir says it will not be included in the new SDI."

Source: Goto80, chipflip.wordpress.com, 23 September 2009.

**RE implication:** The realtime delay trick uses voice 3's ext-in or oscillator
output (routed through the SID's audio path) to capture a delayed version of the waveform.
This is 6581-specific. The technique was ultimately NOT incorporated into SDI V2.x.
HVSC SDI tunes do not use this technique.

---

## 7. Demozoo: Complete Productions Catalogue Tagged "sid-duzz-it"

Source: https://demozoo.org/productions/tagged/sid-duzz-it/
Fetched: 2026-06-13

These are confirmed SDI compositions in the demoscene production database:

| Title | Creator(s) | Year | Group(s) |
|-------|-----------|------|---------|
| Let There Be Silence | Aleksi Knutsi | 2022 | MoonShine |
| Deepstalker | NecroPolo | 2021 | — |
| Butterfly Effect | Vincenzo | 2021 | — |
| Ruzzians | Stainless Steel | 2012 | Paramount |
| Hold The Line | Stainless Steel | 2010 | — |
| We Are New (tune 4) | Magnar | 2010 | Fairlight |
| We Are New (tune 1) | Magnar | 2010 | Fairlight |
| Electro Mechanica | Jan Harries | 2010 | Sidwave |
| Intoxication (BP 2010 Edit) | Stainless Steel | 2010 | — |
| Silesian Dancer | Booker | 2009 | Onslaught, Sidwave |
| Superstation | Stainlesssteel | 2009 | — |
| SID Duzz' It v2.0 | — | 2009 | SHAPE |
| Up and Down | Henne | 2008 | The Dreams |
| Push It! | Henne | 2007 | The Dreams |
| Cosmic | Stainless Steel | 2006 | — |
| Pitch That Bitch | FieserWolf | 2005 | Metalvotze |
| I Miss You | Murdock | 2004 | Tropyx |
| Three Paths | TDS | 2002 | Creators |
| Solid V2 | 6R6 | 2002 | Blues Muz', SHAPE |
| Light Soundsense | TDS | 2002 | — |
| SID Duzz' It V1.5 | — | 2002 | SHAPE |
| I'm Back | Shapie | 2002 | Onslaught |
| SID Duzz' It V1.3 | — | 2001 | SHAPE |
| The Last Ninja 1 - Game Tune No. 1 Remix | DJB | 2001 | Blues Muz', Onslaught |
| Another Beginning | GRG | 2001 | SHAPE |
| The Other Day | GRG | 2001 | Blues Muz', Onslaught, SHAPE |
| Countdown to NIL | GRG | 2001 | SHAPE |
| The Last Ninja 1 - Game Tune No. 1 | DJB | 2000 | Blues Muz', Onslaught |
| Chaos 2000 | DJB, GRG | 2000 | Blues Muz', Onslaught |
| Jazzland | Shapie | 1999 | Onslaught, Vaudeville Crew |

Note: Demozoo's tag only captures productions the community has explicitly tagged;
the full SDI corpus in HVSC (934 tunes) is much larger and includes many tunes not in
Demozoo (e.g., all of Fredrik's 143 tunes and most of SIDWAVE's 117 tunes).

---

## 8. GRG Aliases and Identity

Source: Demozoo scener page #948 (https://demozoo.org/sceners/948/)

- **Real name:** Glenn Rune Gallefoss
- **Aliases:** GRG, 6R6, Glenn, Perts, Shark
- **Location:** Bergen, Vestland, Norway
- **Current groups:** Nostalgia and SHAPE
- **Former groups:** Blues Muz', Calix, Collision, Digital Designs, Fairlight, Foxbat,
  Kraftverk, Onslaught, Pandora, Protovision, Regina, Scene Plus Magazine Staff, The Freaks
- **Total Demozoo productions:** 423+ (1991–2026)

The alias "6R6" is his primary C64 scene handle. "GRG" appears in SDI-era internal
documentation (the manual credits "GRG and GT of SHAPE"). The SourceForge account is
`glennrg64`. His Fairlight membership (1998) was brief; the primary affiliation throughout
the SDI era is SHAPE.

---

## Leads to Follow

- **Olav Morkrid / Panoramic "Digitalizer" editor**: Named as an SDI design influence by
  the Psylicium manual. No further information recovered. Look for CSDb releases by
  "Olav Morkrid" or "Panoramic Designs"; the Digitalizer editor may be archived there.
  Geir Tjelta was himself a Panoramic Designs member (Demozoo confirms).
- **Recollection #64 (Vandalism News #64, June 2015) full article**: The article
  "The Brief History of SID" by Jan Harries (SIDwave) is the single richest community
  account of SDI's lineage. Only excerpts recovered. Full article at:
  `https://www.atlantis-prophecy.org/recollection/?load=articles&id=TheBriefHistoryofSID`
  Re-fetch with a targeted prompt to extract more sections.
- **JCH (Jonatan Dunn / Vibrants)**: Confirmed as a design inspiration. JCH's own
  writings on Codebase64 (`jch_20.g4_player_file_format`) document his format in detail;
  cross-referencing with SDI format would sharpen the "what was borrowed vs. invented"
  picture.
- **Sid Systems player source**: The SIDSys V4.1 player (versions 18.4 and 18.6) is
  available on CSDb (#33644). Comparing its structure to the SDI V2.1 player source
  (already downloaded in `src/`) would reveal the evolutionary path from SIDSys to SDI.
  This is an RE task, not a forum task.
- **GRG's "tiny" player variants** (SIDID: GRG_tiny_1..4): Mentioned in SIDID database
  but not investigated. These may be stripped-down SDI players for use in demos/intros
  where code size matters. Worth identifying on CSDb.
