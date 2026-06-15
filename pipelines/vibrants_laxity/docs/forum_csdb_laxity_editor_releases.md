---
source_url: https://csdb.dk/release/?id=122333
fetched_via: direct
fetch_date: 2026-06-15
author: CSDb community
content_date: 1990 (tool), 2022 (most recent comment)
reliability: secondary
---

# CSDb — Laxity Editor Releases

## Laxity Editor v/32-3.34 (CSDb #122333)

- **Year:** 1990
- **Developer:** Thomas Egeskov Petersen (Laxity), Germany/Denmark
- **Type:** C64 Tool
- **Downloads:** T64 format + D64 format (with 5 demo tunes)

### Demo tunes bundled

| Title | Author |
|-------|--------|
| DXYCP Scroll | Scortia |
| Fast Stuff 1 | Laxity |
| In the Mood Mix | Scortia |
| Lethal C. | Scortia |
| Spacemilk | Scortia |

All available in HVSC under the `Vibrants/Laxity` engine tag.

### Technical context from comments

- A D64 with 5 demo tunes made in this version is available (March 2022 comment)
- No technical documentation was released with the editor

---

## TFA Editor V3.24 (CSDb #215790)

- **Year:** 1989
- **Group:** The Flexible Arts (Laxity's earlier group)
- **Code/Music:** Laxity (Starion at the time), Zenox (additional contribution)
- **Type:** C64 Tool (precursor to Laxity Editor)

### Notes from CSDb

> "TFA Editor #3.24 is the precursor to Laxity Editor v/32-3.34, Laxity Editor v/33-3.35
> and Laxity Editor v/34-3.35"

Demo tunes included: "Def Con One", "Nu' det jul igen", "Tainted Love 8-bit"

### What this tells us about format lineage

The TFA Editor (1989) → Laxity Editor v/32-3.34 (1990) → Laxity Editor v/34-3.35 (1990)
form a single lineage. The player binary used in all three is the "Vibrants/Laxity"
engine that SIDId identifies with the 5-line OR signature. The format predates JCH's
editor (JCH started composing in LAXITY's player in June 1988, then built his own
after 1989).

---

## Version numbering grammar

The editor version strings use a "v/XX-Y.YY" format:
- `v/32-3.34` = major version 32, semantic version 3.34
- `v/34-3.35` = major version 34, semantic version 3.35

The major version (32, 33, 34) appears to be a build counter, not a musical feature revision.
This is Laxity's own versioning scheme, distinct from JCH's "NP20.G4" / "NP21.G5" naming.

---

## Laxity Relocator releases (undated)

- Laxity Relocator V1.18
- Laxity Relocator V1.20

These relocators were needed because the Vibrants/Laxity player loads at a fixed address
($1000 canonical). The relocator tools support moving the player to alternate bases —
consistent with the 7.7% of HVSC Vibrants/Laxity SIDs that use non-standard base addresses.

---

## JCH timeline data on the Laxity editor origin

From JCH's computer timeline at blog.chordian.net/computer-timeline/:

- **June 1988**: JCH reverse-engineered Laxity's C64 music player and started composing in it
- **March 17, 1989**: JCH converted "Popcorn" into the Laxity player format
- **March 3, 1989**: Six OldPlayer-based tunes documented in JCH-SELEC #2

This means JCH used the Laxity player extensively from mid-1988 until late 1989 (when
he developed his own editor after Laxity told him to stop using Laxity's tools).
The JCH_OldPlayer SIDId signature (see forum_sidid_signatures.md) refers to JCH's
initial compositions done in Laxity's format — NOT in his own NewPlayer engine.

The JCH OldPlayer signature:
```
48 18 4A 4A 4A 4A 29 07 0A 0A 0A 48 0A 8D ?? ?? 68 18 6D ?? ?? 8D ?? ?? 68
```
This is a nibble-extraction + SID write sequence characteristic of JCH's early compositions
in the Laxity format, potentially with JCH's own minor modifications.
