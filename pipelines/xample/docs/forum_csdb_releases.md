# X-Ample / Compotech — CSDb Release Records

**source_url:** https://csdb.dk/
**fetched_via:** WebFetch per-release + WebSearch
**fetch_date:** 2026-06-13
**reliability:** primary (CSDb is the authoritative C64 scene database)

---

## Compotech (1992)

- **CSDb ID:** 122614 (V2.1 entry; V1 may lack a separate entry)
- **URL:** https://csdb.dk/release/?id=122614
- **Title:** Compotech V2.1 (also spelled "Comptech V2.1" on the disk label)
- **Year:** August 1995
- **Type:** C64 Tool
- **Group:** X-Ample Architectures
- **Credits (code):** Chap Bizarre, Joachim Fräder, Markus Schneider
  (Markus Schneider also listed as Lords of Sonics, X-Ample Architectures)
- **Downloads:** 451 (as of 2026-06-13)

**Note from the CSDb group listing:** Compotech and Compotech V2.1 appear as
two separate tool entries in the X-Ample Architectures group release list —
1992 and 1995 respectively. This implies V1 shipped in 1992, V2.1 in 1995.

No user comments with technical details appear on the CSDb page. The release
awaits voting.

---

## The Parsec Music Editor V5.1 (1989)

- **CSDb ID:** 10744
- **URL:** https://csdb.dk/release/?id=10744
- **Year:** 1989
- **Type:** C64 Tool
- **Group:** Mnemonic Designs
- **Credits:**
  - Code: ADT, Markus Schneider (Lords of Sonics, X-Ample Architectures), Nic
  - Music: Jeroen Tel (Maniacs of Noise) — included tune "Tomcat"
  - Graphics: Kee
  - Bug-Fix & Documentation: SMC (Pretzel Logic)
- **Downloads:** 389 (D64), 137 (T64)

**User comments (verbatim):**
- A user noted "the original release of the Parsec 5.1 editor with intro" was
  uploaded, distinguishing it from a version "without intro distributed via the
  Ruthless Music Disk."
- Another user asked which ADT programmed the tool; the answer was added to
  the scener record.

**Technical notes from comments:** None. No format documentation.

**Context:** Parsec Music Editor V5.1 (1989) is the immediate predecessor to
the Compotech editor. It was developed by Mnemonic Designs (not yet X-Ample).
The ".5.1" version number implies earlier versions existed (V1–V4). The
sidid.nfo entry for `(Parsec)` says it was released by Mnemonic Designs.

---

## The Ultimate X-Tracker V3.1 (April 1996)

- **CSDb ID:** 17708
- **URL:** https://csdb.dk/release/?id=17708
- **Year:** April 1996
- **Type:** C64 Tool
- **Groups:** Smash Designs, The Art Project Studios
- **Credits (all roles):** SoNiC (Tufan Uysal) of The Art Project Studios
  and The Obsessed Maniacs
- **Downloads:** 1,132 (as of 2026-06-13) — the most downloaded X-Tracker release

**User comments (verbatim, all):**

> **Fred, October 12, 2013:**
> "The player of this editor is 100% identical to Compotech V2.1"

> **Richard, April 9, 2005:**
> "Kind of reminds me of the good old DMC player, but this one is even cooler :)"

**Technical significance:**
Fred's comment is the single most important public technical statement about
XTracker's relationship to Compotech: the **play routine is byte-for-byte
identical to Compotech V2.1**. This means XTracker V3.1 is a new editor
front-end wrapping the existing Compotech V2.1 player, NOT a new music engine.
The data format is therefore the same as Compotech V2.1.

Richard's DMC comparison suggests the dispatch/sequencing feel resembles DMC
(Digital Music Creator), though the sidid signatures are clearly different
engines.

---

## The Ultimate X-Tracker V4.13 (1996)

- **CSDb ID:** 82320
- **URL:** https://csdb.dk/release/?id=82320
- **Year:** 1996
- **Type:** C64 Tool
- **Groups:** The Art Project Studios, Smash Designs, The Obsessed Maniacs
- **Credits:** SoNiC (all roles: code, music, concept)
- **Downloads:** 510 (as of 2026-06-13)

**Included SIDs (9 tracks by SoNiC):**
1. APS-Mag (mag extended)
2. Audio Wave (blue system mix)
3. Double Dragon (the dragon mix)
4. Experimental
5. Hit Dance
6. Shorty (short cut)
7. Totally Freaked Up
8. Tufan Uysal's Mahogany Dub
9. Twingo (red colour mix)

**User comments:** None on the CSDb page.

**Technical note:** V4.13 is a subversion of V4.1x. The sidid fingerprint for
`(XTracker_V4.1x)` covers 4.13 and other 4.1x releases. The fingerprint
shows an unrolled 3-voice dispatch (three separate `A2 xx / JSR` pairs)
rather than a bitmask loop — a structural change from V3.1/Compotech.

**OPEN:** Whether V4.1x introduced a new data format (different from
Compotech V2.1) or retained the same data format with only a new player
routine is unknown from public sources. The sidid signature change strongly
suggests at minimum a different player; data format change is unconfirmed.

---

## X-Tracker V4.00 Beta (1996)

- **CSDb entry exists** (confirmed from Thomas Detert's scener page, listed
  as a tool credit with year 1996)
- **Author:** Thomas Detert (credited with music; coder unknown — possibly
  SoNiC or Detert himself)
- No separate CSDb release ID identified in this research pass.

**Context:** This beta version predates V4.13. Thomas Detert's involvement
with the beta may explain why the `(Thomas_Detert)` sidid variant exists as
a fork of Compotech — he was testing early XTracker while using his own
modified player for production.

---

## Compotech V2.x — Author attribution in sidid.nfo

From `sidid/sidid.nfo` (verbatim):

```
(Compotech_V2.x)
     NAME: Compotech
   AUTHOR: Markus Schneider & Helge Kozielek
 RELEASED: 1990 X-Ample Architectures
REFERENCE: https://csdb.dk/release/?id=122614
```

Note the released year is 1990 in sidid.nfo but the CSDb page shows
"August 1995" for V2.1. The 1990 date in sidid.nfo likely refers to the
**first** Compotech version (V1, 1990 per group releases list → "Compotech
1992" in the CSDb group tools list — exact year uncertain). V2.1 is 1995.

---

## Geir_Tjelta/Comptech-X (2019)

From `sidid/sidid.nfo` (verbatim):

```
Geir_Tjelta/Comptech-X
     NAME: Comptech-X
   AUTHOR: Geir Tjelta
 RELEASED: 2019 <?>
  COMMENT: First used in 2019 by Geir Tjelta and Markus Schneider, probably
           private player for X-Ample members.
```

**Significance:** Confirms Markus Schneider was still active in C64 music in
2019 (consistent with the 2017 "Veterans of Style" group release and
2025+ music credits on CSDb). Comptech-X is a private/modern successor to
Compotech, not in public release.

---

## X-Ample Architectures Group (CSDb group ID: 245)

- **URL:** https://csdb.dk/group/?id=245
- **Founded:** July 1988
- **Tagline:** "Bit For Bit A Hit"
- **Founders (per CSDb):** Stephen Taylor, Takashi, General X, Chap Bizarre
- **Closed:** 1997 (rebranded to Büttner GmbH, 1997-2000)
- **Total releases:** 92

**Music-related tool releases (confirmed in tool list):**
- X-Ample Intro Architect (1989) — by Joachim Fräder
- Compotech (1992)
- Compotech V2.1 (1995)

**Key composers listed:**
- Thomas Detert (co-founder)
- Markus Schneider (joined March 1989)
- Tufan Uysal (SoNiC) — external composer who became the largest X-Ample user
  with 123 X-Ample-engine SIDs in HVSC

**Groups note:** The CSDb group page shows different founder list than the
c64.ch mirror (c64.ch lists: General X, Takashi, Chap Bizarre, Stephen
Taylor, and Markus Schneider with join date March 1989). Thomas Detert is
confirmed as a co-founder by VGMPF ("in summer 1988 founded the demo groups
Omega 8 and X-Ample Architectures"). The discrepancy may reflect
CSDb's focus on the demo-group incarnation vs the game-dev company.

---

## Markus Schneider CSDb scener record

- **URL:** https://csdb.dk/scener/?id=6003
- **Handle(s):** Markus Schneider (MS), Diflex (1988-??), Synth-Man (1987-1988)
- **Group:** X-Ample Architectures (member since March 1989)
- **Functions:** Coder, Musician

**Notable Quote (verbatim from CSDb):**
> "I hate Disco Tunes! But i do what people want."

**Tool credits:**
- Compotech (1992) — Code
- Compotech V2.1 (1995) — Code

**Game music credits:** Extensive (40+ games, 1988-1992), including
Magic Mouse in Goblin Land (1992), Rolling Ronny (1991), Transworld (1991).

---

## Thomas Detert CSDb scener record

- **URL:** https://csdb.dk/scener/?id=1312
- **Handle(s):** Stephen Taylor, B.U.C.K (also Thomas Detert as real name)
- **Group:** X-Ample Architectures (from July 1988)

**Tool credits relevant to X-Ample player:**
- X-Tracker V4.00 Beta (1996) — Music
- Compotech (1992) — (music use implied; not listed as coder)
- X-Ample Intro Architect (1989) — (tool by Joachim Fräder; Detert was a user)

**Note from Thomas Detert interview (Remix64, verbatim extract):**
> "the Routine took too much time to use it in games or bigger demoparts,
> so our programmer Helge Kozieleck created together with Markus Schneider
> the X-ample Music Player."

The "Routine" here refers to Chris Hülsbeck's Soundmonitor, which Detert
used for his earliest work (confirmed by HVSC engine tags: his pre-1989
SIDs are `Soundmonitor`).
