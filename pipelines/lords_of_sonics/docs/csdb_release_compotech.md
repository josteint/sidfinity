---
source_url: https://csdb.dk/release/?id=130599
fetched_via: direct
fetch_date: 2026-06-16
author: unknown
content_date: 1992
reliability: primary
---

# Compotech — CSDb Release Pages

## Summary

Compotech is the X-Ample Architectures successor to the Parsec Music Editor, maintaining the same underlying LordsOfSonics/MS player while adding a new composition and packing workflow.

---

## Original Release — Compotech (ID: 130599)

**URL:** https://csdb.dk/release/?id=130599
**Type:** C64 Tool
**Year:** July 1992
**Developer Group:** X-Ample Architectures (XAP)

### Credits
| Role | Person | Groups |
|------|--------|--------|
| Code | Chap Bizarre | X-Ample Architectures |
| Code | Joachim Fräder | X-Ample Architectures |
| Code | Markus Schneider | Lords of Sonics, X-Ample Architectures |
| Music | Thomas Detert | X-Ample Architectures |

### Music in Tool
- Thomas Detert composition from Magic Disk 64 (1992/06)

### Download
- `Compotech-X-Ample.d64`: 430 downloads via CSDb
- External: Pokefinder.org

---

## Updated Release — Compotech V2.1 (ID: 122614)

**URL:** https://csdb.dk/release/?id=122614
**Type:** C64 Tool
**Year:** August 1995
**Developer Group:** X-Ample Architectures (XAP)
**Alternative Name:** Comptech V2.1

### Credits
| Role | Person |
|------|--------|
| Code | Chap Bizarre |
| Code | Joachim Fräder |
| Code | Markus Schneider |

### Download
- `Comptech_2.1.d64`: 451 downloads via CSDb
- External: Pokefinder.org

---

## Cracked Versions

| ID | Group | Year |
|----|-------|------|
| 82103 | The Force | 1992 |
| 170243 | Extacy | 1995 |

---

## Docs 2 Compotech (ID: 253740)

**URL:** https://csdb.dk/release/?id=253740
**Type:** C64 Misc.
**Group:** Astral

### Credits
- Music: Xayne (Beat Machine, Crest)
- Documentation: Mister Giga

### Notes
Contains documentation for the Compotech music editor. Two disk images available:
- `Compotech The Force full release.d64` (94 downloads)
- `d2ct.d64` (41 downloads)

The "The Force full release" image is linked to the 1992 cracked version by The Force.

---

## Critical Technical Detail (from Compotech crack comments)

From user comment on the 1992 The Force crack (ID: 82103):

> "I had to use Compotech V2.1 to load the demo tune, **save as turboass format** and **merge to the provided '.PLAYER-ROUTINE'** to be able to generate a working executable, **because this version does only save the packed data**."

This is the key architectural fact about Compotech:
1. **Compotech composes and outputs PACKED DATA only** — not a standalone SID or executable
2. A **separate `.PLAYER-ROUTINE` file** must be merged with the packed data to create a playable program
3. Compotech V2.1 added a **turboass format** save option for assembly-level integration
4. This workflow is different from the Parsec Music Editor, which appears to produce standalone SID-playable output

This two-part (data + player routine) architecture is consistent with the HVSC sidid engine classification: the player routine is a fixed binary that the packed song data is appended to or referenced by.

---

## Engine Lineage Timeline

```
1988       Lords of Sonics Music Editor (Markus Schneider)
            ↓ internal format evolved
1989       The Parsec Music Editor V5.1
             - Published via Mnemonic Designs
             - Code: ADT + Markus Schneider + Nic
             - Bug-fix & docs: SMC (Pretzel Logic)
             - Music: Jeroen Tel ("Tomcat")
             - Widely cracked and distributed 1989–1991
            ↓ Schneider joins X-Ample Architectures (March 1989)
1992       Compotech (X-Ample Architectures)
             - Code: Chap Bizarre + Joachim Fräder + Markus Schneider
             - Workflow: compose → packed data + separate player routine
             - Music: Thomas Detert
1995       Compotech V2.1 (X-Ample Architectures)
             - Same coders
             - Adds turboass export format
             - Final known version
2023       Lords of Sonics Music Editor v1.0 (Bansai, modern reconstruction)
             - Uses same player code as Parsec V5.1
             - Contains 105+ SIDs: A-Man, Blidon, Schneider
```

---

## Composer Users of Compotech

From various CSDb listings and the 2023 LOS Editor release:
- Markus Schneider (MS) — engine author
- Jens Blidon — original LOS co-founder
- Steven Diemer (A-Man) — prolific user
- Kagan Demir (Babyface) — SIDs under `/MUSICIANS/B/Babyface/`
- Jesper Spang — SIDs under `/MUSICIANS/S/Spang_Jesper/`
- Stefan Toftevall (Ice) — SIDs under `/MUSICIANS/I/Ice/`
- Mc Olly — SIDs under `/MUSICIANS/M/Mc_Olly/`
- SMC (Pretzel Logic) — bug-fix & docs credit on Parsec V5.1
- Thomas Detert — contributed music to the tools themselves
