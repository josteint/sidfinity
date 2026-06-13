---
source_url: multiple CSDb pages (see per-section citations); hvsc84.db (local); pipelines/dmc/docs/tnd_dmc_tutorial.txt
fetched_via: WebFetch (CSDb), Python sqlite3 (hvsc84.db READ-ONLY), local grep
fetch_date: 2026-06-13
author: Balázs Farkas (Brian) of Graffity (primary); Fenek, Wacek (community extensions)
content_date: releases 1990–2020; DB query 2026-06-13
reliability: primary (CSDb release pages + sidid.cfg binary signatures + hvsc84.db metadata)
---

# GMC / Game Music Creator — Releases, Versions, and GMC→DMC Lineage

## 1. Tool family overview

GMC (Game Music Creator) is a C64 music editor created by **Balázs Farkas (Brian)** of
**Graffity** (Hungary, group ID 193), released 8 December 1990 (CSDb #7268). The "Superiors"
in the sidid name reflects the editor's subtitle: "Superiors Game Music Creator System." It
is the **direct predecessor of DMC (Demo Music Creator)**, as confirmed by multiple CSDb
comments and explicitly stated in the TND DMC tutorial (pipeline/dmc/docs/tnd_dmc_tutorial.txt,
line 161): *"The predecessor of DMC is the GMC - Game Music Creator, written by Brian of Graffity too."*

The Graffity group page (CSDb group #193) states that DMC 2.0 "became a de facto scene
standard" — the same codebase author, same group, continuous development path.

## 2. Releases by version

### 2a. GMC V1.0 — CSDb #7268
- **Title:** "Superiors Game Music Creator System V1"
- **Released:** 8 December 1990
- **Group:** Graffity (Hungary)
- **Code:** Brian and Jay (both of Graffity)
- **Music in package:** Andy and Brian (of Graffity)
- **Graphics:** Jay (of Graffity)
- **Package contents:** 27 demo SID music files; three download formats (T64: 1030 DL,
  ZIP: 235 DL, D64-with-intro: 173 DL).
- **Forum posts (7):** File-preservation discussion only; no technical format discussion.
- **User comments:**
  - NecroPolo (2009-07-01): *"That was my weapon of choice, uhh, 18 years ago. It feels
    very solid to work with and it is really good at producing some really twisted filtering."*
  - Richard (2009-03-02): *"They should have called this tool DMC V1.0 :)"* (lineage
    confirmation from a DMC expert)
  - wacek (2012-04-03): *"Uploaded a proper version (including a great intro from Graffity
    and all the original demotunes). For me, this old crappy thing is also still a weapon of choice ;)"*
  - iAN CooG (2012-04-03): file corruption note (crosslinked .GMC file corrected in 2012 re-upload)
- **Source:** Not public (no source release found on CSDb or GitHub).

### 2b. GMC V1.6 Editor + Beta Music — CSDb #98639
- **Released:** December 1990
- **Group:** Graffity
- **Code:** Brian of Graffity
- **Download:** 496 DL
- **Notes:** Separate from the V1.0 package; editor-only + beta demo tunes. No user
  comments with technical content on CSDb.

### 2c. Superiors Game Music Creator System V1.6 — CSDb #46470
- **Released:** 1990
- **Group:** Graffity / Tomcat (Brian was simultaneously in both)
- **Code:** Brian of Graffity, Tomcat
- **Download:** Editor v1.6.zip (417 DL)
- **Notes:** This is a third V1.6 entry in CSDb — differs from #98639 by the dual-group
  credit. Likely the canonical "final V1.x" release. The "Tomcat" co-credit reflects Brian's
  concurrent membership in Tomcat before he left for Graffity (he left Tomcat in August 1990).
  No technical comments on CSDb.

### 2d. GMC V1.6 100% — CSDb #156855
- **Released:** 28 August 1992
- **Group:** The Ancient Temple (TAT)
- **Credits:** Bug-Fix: Case (of TAT); Music: Laxity (of Maniacs of Noise and Vibrants)
- **Download:** GMC1.6.d64 (295 DL)
- **Notes:** Bug-fixed version of V1.6 by a third party. "Star Dream" by Laxity included.
  "Proper release: 100%." This is the most complete preserved V1.6 binary.

### 2e. GMC V2 (Unfinished) — CSDb #44814
- **Released:** 20 December 2006
- **Author:** Fenek (Arise, Protovision)
- **AKA:** "tydzienbezsensownejroboty" (Polish: "week of senseless work")
- **Download:** gmc_v2.zip (1192 DL)
- **Technical detail:** Fenek *disassembled* the GMC V1.0 player and *recreated* editor and
  player from scratch, *"removing those restrictions [on instrument counts] and optimizing
  the player's code"* (wacek comment). The editor was described as *"more streamlined,
  DMC-resembling"*. Key: this is a clean reimplementation, not the original source.
  The number of instruments was a primary V1.0 restriction removed.
- **Status:** Unfinished / not production-ready.
- **Source:** The download contains Fenek's reimplemented editor + player (disassembly
  artefact, not Brian's original source).

### 2f. GMC 0.5x — CSDb #193964
- **Released:** 28 July 2020
- **Author:** Wacek (Arise, WST); Concept: booker (MultiStyle Labs)
- **Context:** Released at 25Hz Music Compo 2020 — a demoscene competition specifically
  for 25 Hz (half-speed PAL) music. "GMC 0.5x" = GMC at half the normal 50 Hz rate.
- **Credits:** Concept: booker; Bug-Fix: Wacek
- **Download:** 257 DL
- **Notes:** A 25 Hz adaptation of the GMC player; humorous naming ("0.5x" = half speed
  relative to V1.x). SHIFT+I then Y to play the included compo contribution.

## 3. GMC→DMC lineage — complete chronology

The following is the COMPLETE tool succession from GMC to the full DMC family,
all by Brian of Graffity unless noted otherwise:

| CSDb ID | Title | Year | Notes |
|---------|-------|------|-------|
| 7268 | GMC V1.0 | Dec 1990 | First release; "Superiors" subtitle |
| 98639 | GMC V1.6 Editor + Beta Music | Dec 1990 | Editor-only release |
| 46470 | Superiors Game Music Creator System V1.6 | 1990 | Final canonical V1.x |
| 44465 | Digieditor V1.3 | 1990 | Co-authored by Andrew John Fletcher; digital sample editor (companion tool) |
| 2598 | DMC V1.2 | 4 Feb 1991 | **First DMC**; "Demo Music Creator System V1.2" |
| 10757 | DMC V2.0 | Feb 1991 | Became "de facto scene standard" |
| 200842 | The Superiors Demo Music Creator V2.1+ | 1991 | Transitional name still uses "Superiors" brand |
| 55791 | Music Driver V1.0 | Mar 1991 | By Hepido19 of Graffity; standalone player/driver |
| 98640 | DMC V3.0 | Jul 1991 | |
| 2596 | DMC V4.0 | 1991 | Most widely used version; TND tutorial covers V4+V7 |
| 2597 | DMC V4.05 | 1992 | |
| 2603 | DMC 4.0 Professional | 1995 | Brian + Onslaught |
| 2594 | DMC V5.0 | 1993 | |
| 2599/2600 | DMC V5.1 Package / V5.1+ | 1994 | With Motiv 8 |
| — | DMC V6.0 | 2018 | Brian (The Imperium Arts); modern revival |

Community forks/cracks omitted above (TAT V4.1A, Sonic Screams V4.2, Chromance V2.0 crack, etc.)

Key lineage quote from TND tutorial (secondary source, 2009):
> *"The predecessor of DMC is the GMC - Game Music Creator, written by Brian of Graffity too.
> You will find some similar elements in that editor too, but the following DMC versions
> are more improved."*

## 4. HVSC coverage — from hvsc84.db (READ-ONLY)

- **GMC/Superiors (V1.x):** 446 SID files
- **GMC_V2.0/Superiors:** 9 SID files
- **Total GMC family:** 455 SID files

Top composers by tune count (V1+V2 combined):
1. Adam Waclawski (Wacek) — 97
2. Péter Nagy-Miklós (NecroPolo) — 36
3. Ádám Papp (Paco) — 35
4. Balázs Farkas (Brian) — 33 (the creator)
5. Rene Griebel (Bleed Into One) — 32
6. Kai Lehmann (Ass It) — 26
7. Andor Cseh (DOS) — 20
8. Sasha Stojanovic (Dalton) — 19

Active years: 1990 (Graffity origin) through 2024 (still used).

## 5. Entry point and layout patterns (from hvsc84.db)

Two dominant architectures in the wild:

### Layout A — canonical GMC V1.x (289 of 446 V1.x tunes)
- **init:** `$18EA`, **play:** `$14EA`
- Difference: init = play + `$400` (1024 bytes)
- Interpretation: the player body begins at `$14EA`; the init wrapper/song-select code
  sits `$400` bytes higher at `$18EA`.
- **Relocatable:** sidid sees tunes at many other offsets sharing this -`$400` pattern:
  `$A8EA/$A4EA` (×6), `$E8EA/$E4EA` (×5), `$88EA/$84EA` (×3), `$48EA/$44EA` (×2), etc.
  All end in `0xEA` for the play address (low byte `$EA` = 234).
- **Conclusion:** The player binary is relocatable; `$14EA` is the standard load target.
  The `$EA` low byte is a sidid fingerprint anchor.

### Layout B — compact/flat layout (114 of 446 V1.x tunes; 7 of 9 V2.0 tunes)
- **init:** `$1000`, **play:** `$1003`
- Difference: play = init + 3 (a `JMP init_body` at `$1000` and `JMP play_body` at `$1003`).
- This matches the sidid task description's note: *"Entry $1000 init/$1003 play."*
- **Note:** The research.md stub only records Layout B. Layout A (the dominant layout)
  is the one to reverse-engineer first (289 tunes).

### GMC V2.0 layouts
All 9 V2.0 tunes use Layout B-style (+3 offset): `$1000/$1003` (×7), `$1B90/$1B93`,
`$5000/$5003`. No V2.0 tunes use the -`$400` Layout A pattern.

## 6. sidid binary detection signatures

From `/home/jtr/sidfinity/tmp/dmc_hunt/sidid/sidid.cfg`:

```
GMC/Superiors
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? BD ?? ?? 9D ?? ?? BC ?? ?? 18 0A 0A 0A 0A 85 ?? AD ?? ?? 69 00 85 ?? A0 00 B1 END

GMC_V2.0/Superiors
E1 EE FD BD ?? ?? 9D ?? ?? A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? BD ?? ?? 9D ?? ?? A8 29 F0 85 FC 98 29 0F 18 6D ?? ?? 85 FD A0 00 98 9D END
```

The two signatures share a long common prefix (first ~40 bytes identical), then diverge:
- V1.x: `BC ?? ?? 18 0A 0A 0A 0A 85 ?? AD ?? ?? 69 00 85 ?? A0 00 B1`
- V2.0: `A8 29 F0 85 FC 98 29 0F 18 6D ?? ?? 85 FD A0 00 98 9D`

The common prefix is a 3-voice init loop:
- `BD ?? ?? 9D ?? ??` — LDA abs,X / STA abs,X (copy voice data)
- `A8` — TAY
- `B9 ?? ?? 9D ?? ??` — LDA abs,Y / STA abs,X (repeated for 3 voice params)

The V1.x divergence: `BC ?? ?? 18 0A 0A 0A 0A` = LDY abs,X + CLC + ASL×4 = multiply
by 16 (the sound definition indexing: "indexed via 4× ASL A = multiply by 16" as noted
in research.md). Then `AD ?? ?? 69 00` = LDA addr + ADC #0 (carry-based page calc).

The V2.0 divergence: `29 F0 85 FC 98 29 0F 18 6D ?? ?? 85 FD` = AND #$F0 + STA zp +
TYA + AND #$0F + CLC + ADC abs + STA zp — nibble extraction (high/low nibble separation).
This is a more refined instrument-number decomposition than the V1.x 4×ASL approach.

Also note in sidid.cfg: a separate "Graffity/Brian" pattern (unrelated to GMC format — it
appears to be a Graffity/Brian one-off player, not the main GMC engine):
```
Graffity/Brian
A9 00 95 2F 95 2C 95 95 95 96 95 97 END
```

## 7. The `CONT` / format field names

From research.md (pre-existing stub, not overwritten):
> Sector level (per step): DUR, SND, APM, GLD, HLD, CONT, END

These are the field names as they appear in the GMC editor UI:
- **DUR** — duration (step length)
- **SND** — sound/instrument number (0–15 in V1.x, expanded in V2.0/Fenek's reimpl.)
- **APM** — amplitude/modulation (volume/envelope modulation)
- **GLD** — glide/portamento
- **HLD** — hold duration
- **CONT** — continuation/tie flag (whether the note continues into the next step)
- **END** — sector terminator

Sound definitions: 16 bytes each. V1.x indexes with 4×ASL A (multiply by 16 = 0x10).
Max instruments in V1.x: 16 (4-bit field → 16 slots × 16 bytes = 256 bytes instrument table).
Fenek's V2 reimplementation removed this 16-instrument cap.

## 8. Key open questions (RE-needs → OPEN items)

See "## Leads to follow" at the end of this document.
