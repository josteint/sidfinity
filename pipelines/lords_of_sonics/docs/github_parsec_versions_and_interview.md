---
source_url: multiple (see body)
fetched_via: direct
fetch_date: 2026-06-16
author: research agent
content_date: 2026-06-16
reliability: primary/secondary
---

# LordsOfSonics/MS — Parsec Music Editor Versions + Author Interview Details

## Summary

Supplementary research session 2026-06-16. Corroborates and extends existing findings.
All core sidid signature data was already captured in github_findings.md and
github_wilfred_deepsid.md. This file adds:
- Parsec Music Editor release catalogue from CSDb
- Author interview technical details (Remix64)
- sidid.nfo attribution for the engine
- Confirmation that no dedicated open-source decompiler/parser exists

---

## 1. Parsec Music Editor — Release Catalogue (CSDb)

The engine was called "The Parsec Music Editor" in its public form.

| Release | CSDb ID | Year | Group | Notes |
|---------|---------|------|-------|-------|
| The Parsec Music Editor V5.1 | 10744 | 1989 | Mnemonic Designs | Original release with intro. Code by ADT + Markus Schneider + Nic. Music by Jeroen Tel ("Tomcat"). Bug-fix & docs by SMC (Pretzel Logic). |
| The Parsec Music Editor V5.1 (crack) | 10745 | 1991 | Genesis Project | |
| The Parsec Music Editor V5.1 (crack) | 127349 | 1991 | Topaz Beerline | |
| The Parsec Music Editor V5.1 (crack) | 130650 | 1991 | Raiders of the Lost Empire | |
| The Parsec Music Editor V5.1 (crack) | 169438 | ~1991 | Raiders of the Lost Empire | |
| The Parsec Music Editor V5.1 (crack) | 200549 | Feb 1991 | X-Plicit | Found via Acidchild's archive (2024 submission) |

Source: https://csdb.dk/release/?id=10744 and search results.

Key observation: Only **one** original release (MCD, 1989, V5.1). All other entries are
1991-era cracks — suggesting the editor was actively circulating in 1991 when the scene
cracked it for redistribution. The version number "5.1" is the only known public version.
No V1.x through V4.x releases are known.

### Parsec Music Editor credits
- **Code:** Markus Schneider (SMC = his initials alias in some releases), Nic (co-programmer), ADT
- **Released:** 1989 by Mnemonic Designs
- **Group association:** Mnemonic Designs (not Lords of Sonics directly)
- **Demo/intro tune:** Jeroen Tel's "Tomcat" (HVSC: Tel_Jeroen/Tomcat.sid)

This confirms the Parsec Music Editor was a collaboration beyond just Lords of Sonics,
involving at least three coders. The engine name "LordsOfSonics/MS" in sidid.cfg reflects
its origins (LOS = group, MS = Markus Schneider as primary engine author).

---

## 2. Parsec 10 V0.1 (1991)

Source: https://csdb.dk/release/?id=223413

This is **NOT** a version of the Parsec Music Editor. "Parsec 10" is a music rip (single
composition titled "FAME on the Run (2)" by Holly/F.A.M.E./Triad) that was labeled/distributed
as "Parsec 10" — likely referring to a music disk issue number or release number, not the
editor version. Not relevant to engine research.

---

## 3. sidid.nfo — Author Attribution

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo (and WilfredC64 mirror)

The sidid.nfo file contains human-readable attribution for each engine signature, including:

### LordsOfSonics/MS
- **Author:** Markus Schneider

### Compotech V2.x (under X-Ample)
- **Name:** Compotech
- **Authors:** Markus Schneider & Helge Kozielek
- **Released:** 1990 X-Ample Architectures
- **CSDb reference:** https://csdb.dk/release/?id=122614

### Parsec (as listed in nfo)
- **Name:** The Parsec Music Editor
- **Authors:** Markus Schneider (SMC), Nic & ADT
- **Released:** 1989 Mnemonic Designs
- **CSDb reference:** https://csdb.dk/release/?id=10744

The nfo confirms Compotech was released in **1990** (CSDb entry says August 1995 for Compotech
V2.1, so the 1990 date in nfo likely refers to the initial internal X-Ample tool, with V2.1
being the 1995 public release).

---

## 4. Author Interview — Technical Details (Remix64)

Source: https://remix64.com/interviews/interview-markus-schneider.html

Key technical quotes (paraphrased from interview; original at source URL):

- Schneider co-founded Lords of Sonics with Jens Blidon after classmates requested C64 game scoring
- He spent ~2 months in 1988 writing a sound driver for Blidon — this became the LordsOfSonics/MS engine
- He initially used "Chris Hülsbeck's well known soundmonitor" but found it limiting
- In 1989, he drove to X-Ample Architectures and spent ~7 weeks merging his driver tech with theirs
- X-Ample then invited him to join as composer and programmer (March 1989)
- After joining X-Ample, UI programmer was Joachim Fräder; optimizations by Helge Kozielek and Mario van Zeist
- In 1990, Chris Hülsbeck gave him a special TFMX-Editor for free (for Amiga work)
- In early 1991, someone (possibly Mario Knezovic) was programming a DOS driver (TBSA) for him

Technical implication: The "Parsec Music Editor" = the driver Schneider wrote in 1988, later
co-developed by Nic and ADT for the MCD release in 1989. The X-Ample merger produced Compotech.
Compotech V2.1's 1995 release date suggests the Compotech player persisted commercially for years.

---

## 5. Engine Usage in Games

Source: https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider + CSDb

Games confirmed to use Schneider's music engine (from HVSC sidid classification and VGMPF data):

| Game | Year | Classification in HVSC |
|------|------|----------------------|
| Rolling Ronny | 1991 | LordsOfSonics/MS (confirmed by sidid) |
| No Mercy | 1989 | LordsOfSonics/MS |
| Lethal Zone | 1991 | LordsOfSonics/MS (2-voice level tunes) |
| Xiphoids | 1992 | LordsOfSonics/MS |

Schneider noted (interview) that for the Rolling Ronny C64 version, he composed music "at home
far away" and delivery of the soundtrack was done separately from the development team (Mario
Knezovic, programmer).

---

## 6. Compotech V2.1 (Public Release)

Source: https://csdb.dk/release/?id=122614

- Title: Compotech V2.1 (also titled "Comptech V2.1" in some entries)
- Released: August 1995 by X-Ample Architectures
- Credits: Chap Bizarre, Joachim Fräder, Markus Schneider (code)
- Format: D64 disk image (Comptech_2.1.d64)
- Downloads: 451

Note: "Chap Bizarre" is a handle for a programmer who was part of X-Ample. This is the
evolved/public version of the driver that started as LordsOfSonics/MS Parsec in 1988–1989.
The engine classified as X-Ample/Compotech_V2.x in sidid.cfg corresponds to this release.

---

## 7. Open-Source Tools Survey — Null Results

No dedicated parser, importer, or decompiler for the LordsOfSonics/MS format was found in:

- **SIDFactory II** (https://github.com/Chordian/sidfactory2) — imports only GoatTracker,
  CheeseCutter, and MOD formats. No LordsOfSonics/Parsec importer.
- **realdmx/c64_6581_sid_players** — reverse-engineered players for Galway, Hubbard, Gray,
  Dunn, Bjerregaard, Tel, Deenen, etc. No LordsOfSonics/MS player present.
- **libsidplayfp** (https://github.com/libsidplayfp/sidplayfp) — generic SID player, no
  format-specific handling for LordsOfSonics/MS.
- **SIDdecompiler** (https://github.com/Galfodo/SIDdecompiler) — generic relocatable ASM
  output; not format-specific.
- **DeepSID** (https://github.com/Chordian/deepsid) — uses sidid.cfg for classification;
  no LordsOfSonics-specific handling beyond player name display.

**Conclusion:** No existing open-source tool parses the LordsOfSonics/MS data format.
The sidid.cfg signatures are the only structured external knowledge about the engine's
binary shape. A decompiler must be built from scratch from sidid signature analysis +
HVSC SID disassembly.

---

## Leads to Follow

1. **Download and inspect Parsec Music Editor V5.1 D64** (CSDb ID 10744) — the disk image
   likely contains both the editor and a player stub. Disassembling the player stub would give
   the authoritative play-routine structure. URL: https://csdb.dk/release/?id=10744

2. **Download and inspect Compotech V2.1 D64** (CSDb ID 122614) — to compare Compotech's
   player format vs LordsOfSonics/MS; identify what changed between the two engines.

3. **Parsec V5.1 version number puzzle** — why is the only known release "V5.1" (not V1.x)?
   Likely internal versioning starting from some earlier date. The tool may have been in use
   internally since ~1987–1988 before the 1989 public release.

4. **Run sidid locally on all Schneider_Markus/ SIDs** — determine exact split between
   LordsOfSonics/MS vs X-Ample vs Compotech engines per file.

5. **Check CSDb SID entry #25598 (Lingo)** — https://csdb.dk/sid/?id=25598 — an early
   LOS SID that should be classified as LordsOfSonics/MS; CSDb SID entries sometimes record
   which editor was used.

6. **Check No_Mercy.sid structure** — it's 32KB with 13 subtunes, load at $0F52 with init at
   $8C4A and play at $0000 (unusual — play at $0000 may be self-modifying or a thunk). This
   is atypical for a simple player and worth examining to understand the engine's init/play model.

7. **A-Man / Babyface composers** — these composers have 10+ LordsOfSonics/MS SIDs each in HVSC
   (as noted in github_findings.md). Their CSDb pages may identify when and how they obtained
   the Parsec Music Editor.
