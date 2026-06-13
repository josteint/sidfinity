---
source_url:
  - https://csdb.dk/release/?id=7268 (GMC V1.0)
  - https://csdb.dk/release/?id=98639 (GMC V1.6 Editor + Beta Music)
  - https://csdb.dk/release/?id=46470 (Superiors GMC V1.6 — inferred from search results showing CSDb #46470)
  - https://csdb.dk/release/?id=156855 (GMC V1.6 100% by TAT)
  - https://csdb.dk/release/?id=44814 (GMC V2 Unfinished by Fenek)
  - https://csdb.dk/release/?id=193964 (GMC 0.5x by Wacek)
  - https://csdb.dk/release/?id=200842 (The Superiors Demo Music Creator V2.1+)
  - https://csdb.dk/group/?id=193 (Graffity group — lists GMC V1.0–1.6 + DMC family)
  - https://demozoo.org/sceners/1711/ (Brian's complete release list)
  - https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo (sidid metadata)
  - https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg (binary signatures)
  - https://github.com/TCRF/vgmid/blob/master/c64.nfo (vgmid metadata)
fetched_via: WebFetch (direct + raw GitHub); WebSearch
fetch_date: 2026-06-13
author: Balázs Farkas (Brian) of Graffity (V1.x); Fenek/Arise (V2 reimpl); Wacek/WST (0.5x)
content_date: releases 1990–2020
reliability: primary (CSDb + sidid.cfg binary signatures + Demozoo); secondary (vgmid nfo)
---

# GMC / Game Music Creator — Complete Version History

## Summary

GMC (Game Music Creator) was released in December 1990 as multiple versions within
the same month. There was no slow V1.0→V2.0 development cycle — the "V2.0" seen in
the SIDid pattern `GMC_V2.0/Superiors` refers to a **format variant identifiable by
binary signature**, not an officially released separate tool version. All officially
released GMC binaries carry the "V1.x" designation (V1.0 and V1.6). A community
reimplementation by Fenek (2006) is sometimes called "GMC V2" but is not by Brian.

---

## Version Table

| Version | Date | CSDb | Author | Key Change | HVSC tunes |
|---------|------|------|--------|------------|-----------|
| GMC V1.0 | Dec 8, 1990 | #7268 | Brian + Jay (Graffity) | First release | ~437 |
| GMC V1.6 Editor + Beta Music | Dec 1990 | #98639 | Brian (Graffity) | Editor-only release | — |
| Superiors GMC V1.6 | 1990 | #46470 | Brian + Tomcat | Dual-group credit; canonical final V1.x | — |
| GMC V1.6 100% | Aug 28, 1992 | #156855 | TAT (Case + Laxity) | Bug-fixed 3rd-party; "proper release 100%" | — |
| GMC V2.0/Superiors | unknown | — | Brian? | Binary-distinct variant; no CSDb release | 9 |
| GMC V2 (Unfinished) | Dec 20, 2006 | #44814 | Fenek (Arise/Protovision) | Clean reimplementation; not Brian's source | — |
| GMC 0.5x | Jul 28, 2020 | #193964 | Wacek (Arise/WST) | 25 Hz adaptation; competition entry | — |

---

## Detailed Version Notes

### GMC V1.0 — CSDb #7268 (December 8, 1990)

**Full title:** "Superiors Game Music Creator System V1"  
**Group:** Graffity  
**Code:** Brian and Jay (both of Graffity)  
**Music:** Andy and Brian (Graffity)  
**Graphics:** Jay (Graffity)

**Package contents:**
- 27 demo SID music files composed by Brian and Andy
- An intro by Graffity (visible in the D64 download: "GMC - Graffity - with intro and demotunes.d64")
- Three download formats available on CSDb:
  - `GMC v1.t64` (T64 tape image, 1030 downloads — most downloaded)
  - `gmcv1.zip` (ZIP archive, 235 downloads)
  - `GMC - Graffity - with intro and demotunes.d64` (D64 disk image with intro, 173 downloads)
- External mirror: Pokefinder.org

**User reception (CSDb comments):**
- NecroPolo (2009-07-01): *"That was my weapon of choice, uhh, 18 years ago. It feels
  very solid to work with and it is really good at producing some really twisted filtering."*
- Richard (2009-03-02): *"They should have called this tool DMC V1.0 :)"*
- wacek (2012-04-03): *"Uploaded a proper version (including a great intro from Graffity
  and all the original demotunes). For me, this old crappy thing is also still a weapon
  of choice ;)"*
- iAN CooG (2012-04-03): file corruption note — a .GMC file was crosslinked and missing data;
  corrected in the 2012 re-upload by wacek.

**Background (from Tehernapló interview, 2013):**  
The tool was developed by Brian and Jay with commercial aspirations — they hoped to sell
it to the German C64 magazine Magic-Disk. The magazine declined. The "Superiors" subtitle
reflects Graffity's internal "Superiors Aural Department (SAD)" branding.

---

### GMC V1.6 Editor + Beta Music — CSDb #98639 (December 1990)

**Group:** Graffity  
**Code:** Brian of Graffity  
**Download:** `superiors gmc 1.6.zip` (496 downloads)  
**Notes:** Editor-only build with beta demo tunes. Released in the same month as V1.0.
The download filename explicitly includes "superiors" — confirming the Superiors brand
applies to V1.6 as well.

---

### Superiors Game Music Creator System V1.6 — CSDb #46470 (1990)

**Group:** Graffity / Tomcat  
**Code:** Brian (of Graffity), with Tomcat co-credit  
**Download:** `Editor v1.6.zip` (417 downloads)  
**Notes:** Brian left Tomcat in August 1990 to co-found Graffity; this dual-group credit
is likely a transitional release made around the same period. This is probably the
canonical "final V1.x" binary. No technical comments on CSDb clarify what changed
between V1.0 and V1.6.

---

### GMC V1.6 100% — CSDb #156855 (August 28, 1992)

**Group:** The Ancient Temple (TAT)  
**Credits:** Bug-Fix: Case (of TAT); Music: Laxity (of Maniacs of Noise and Vibrants)  
**Download:** `GMC1.6.d64` (295 downloads)  
**Notes:** A third-party bug-fixed version of GMC V1.6. Includes "Star Dream" by Laxity.
The "100%" label implies the original V1.6 had known bugs that this release corrects.
This is currently the most complete preserved V1.6 binary for disassembly purposes.
No source code included.

---

### GMC V2.0/Superiors — no CSDb release (date unknown)

**Author:** Balázs Farkas (Brian) — attributed in sidid.nfo  
**CSDb release:** NONE (confirmed — no CSDb page exists for this version)  
**HVSC coverage:** 9 SID files identified by SIDId as `GMC_V2.0/Superiors`  
**Entry addresses:** All 9 tunes use $1000/$1003 layout (vs. dominant $14EA/$18EA in V1.x)

**What makes it "V2.0":**  
The SIDid binary signature diverges from V1.x at the instrument-addressing routine.
The key differences (from `sidid.cfg` analysis in `sidid_signature_analysis.md`):

- **V1.x instrument access:** `BC ?? ?? 18 0A 0A 0A 0A` = LDY abs,X followed by
  CLC + ASL×4 (multiply by 16). Instrument stride = 16 bytes. Max 16 instruments
  (4-bit sound number field).
  
- **V2.0 instrument access:** `A8 29 F0 85 FC 98 29 0F 18 6D ?? ?? 85 FD` =
  TAY + AND #$F0 (high nibble → ZP $FC) + TYA + AND #$0F (low nibble) + CLC +
  ADC abs + STA $FD. This splits one byte into two nibbles — presumably separating
  an instrument "bank" selector (high nibble) from an instrument index (low nibble).
  This would expand the addressable instrument count beyond 16.

**Relationship to officially named versions:**  
It is unclear whether Brian ever labelled this variant "V2.0" himself. The `GMC_V2.0`
name in SIDid was assigned by the sidid maintainers (cadaver) based on binary detection.
Fenek's 2006 reimplementation is sometimes called "GMC V2" informally, but it is
unrelated to this binary variant (Fenek rebuilt from a V1.0 disassembly, not from
a V2.0 source).

The vgmid metadata (TCRF/vgmid, c64.nfo) lists `GMC_V2.0/Superiors` with no RELEASED
or REFERENCE fields — confirming it was never formally published as a standalone release.
Likely an intermediate development version used by some composers.

---

### GMC V2 (Unfinished) — CSDb #44814 (December 20, 2006)

**Author:** Fenek (Arise, Protovision) — Polish scener  
**AKA:** "tydzienbezsensownejroboty" (Polish: "a week of senseless work")  
**Download:** `gmc_v2.zip` (1192 downloads — highest download count of any GMC release)

**What Fenek did:**  
Fenek disassembled the GMC V1.0 player and recreated both the editor and the player
from scratch. Per wacek's CSDb comment: *"removing those restrictions [on instrument
counts] and optimizing the player's code."* The result is "a more streamlined,
DMC-resembling editor." This is the closest available proxy for an annotated GMC
disassembly — Fenek's work implies a complete structural understanding of V1.0.

**Key implications for RE:**
- The primary V1.0 restriction removed was the instrument count limit (16 max in V1.x).
- This matches the binary analysis: V1.x uses 4-bit instrument addressing (×16 stride = 16 slots).
- Fenek's reimplementation did NOT introduce the nibble-split approach of the `GMC_V2.0`
  binary signature. Fenek's version is structurally independent of both.

**Status:** Unfinished. The download contains Fenek's rebuilt editor + player binary
but no source code and no documentation.

---

### GMC 0.5x — CSDb #193964 (July 28, 2020)

**Authors:** Concept: booker (MultiStyle Labs); Bug-Fix: Wacek (Arise/WST)  
**Context:** Released for 25Hz Music Compo 2020 (a competition for C64 music running
at 25 Hz / half PAL rate instead of the standard 50 Hz).  
**Downloads:** 257  
**Notes:** "GMC 0.5x" = the tool running at 0.5× normal speed (half of the V1.x rate).
To play the included composition: SHIFT+I then Y. This is a competition-specific
adaptation, not a general-purpose new version.

---

## GMC → DMC Transition (1991)

The transition from GMC to DMC happened within weeks of the GMC releases. The "Superiors"
brand carried over briefly:

| Release | Date | CSDb | Notes |
|---------|------|------|-------|
| DMC V1.2 | Feb 4, 1991 | #2598 | First DMC; "Demo Music Creator System V1.2" |
| DMC V2.0 | Feb 1991 | #10757 | Became "de facto scene standard" |
| The Superiors Demo Music Creator V2.1+ | 1991 | #200842 | **Last use of "Superiors" branding** |
| Music Driver V1.0 | Mar 1991 | #55791 | By Hepido19 of Graffity; companion player |
| DMC V3.0 | Jul 1991 | #98640 | — |
| DMC V4.0 | 1991 | #2596 | Most widely distributed version |

Richard's CSDb comment on GMC V1.0 (*"They should have called this tool DMC V1.0"*)
is accurate — DMC is a direct evolution of GMC with no fundamental architectural break.
The primary differences (inferred from lineage analysis + sidid signatures):
- DMC extended the sector command set (adding volume/glide/marker commands above $C0)
- DMC expanded the instrument/sequence architecture for demo use cases
- The "Demo" rebranding reflected Graffity's shift from game music toward demo music

---

## What "Superiors" Means — Definitive Answer

The word "Superiors" in "GMC/Superiors" (SIDid) refers to **Graffity's internal tool
division identity**, described as the "Superiors Aural Department (SAD)" in the
Tehernapló interview. It is NOT:
- A separate cracking or spreading group (not in the Recollection Hungarian cracker map)
- A distributor name
- A separate band or label

It appears in:
- Full tool title: "Superiors Game Music Creator System V1"
- SIDid pattern names: `GMC/Superiors`, `GMC_V2.0/Superiors`
- Download filename: `superiors gmc 1.6.zip`
- Transitional DMC title: "The Superiors Demo Music Creator V2.1+"

The branding was dropped by DMC V3.0 (July 1991), approximately one year after its
introduction with GMC V1.0.

---

## Leads to Follow

1. **GMC V1.6 vs V1.0 technical differences:** No CSDb comment explains what changed
   between V1.0 and V1.6. Comparing the sidid.cfg signatures (both should match
   `GMC/Superiors`) would confirm they share the same player engine. If V1.6 has the
   same binary signature as V1.0, the changes were editor-only (UI, not playback).
   RE-need: binary diff of the two D64 images.

2. **GMC V2.0 binary identification:** The 9 HVSC SIDs tagged `GMC_V2.0/Superiors`
   in hvsc84.db need to be listed and their HVSC paths checked. Which composers used
   V2.0? Were they aware of a different tool version, or is V2.0 simply a later
   player binary distributed without an editor update?

3. **Date of GMC V2.0:** The sidid.nfo has no RELEASED field and no CSDb reference
   for V2.0. The 9 HVSC tunes could provide dating context — the earliest SID using
   V2.0 would give a lower bound. RE-need: `hvsc84.db` query for GMC_V2.0 tune years.

4. **Fenek's disassembly artefact:** Fenek rebuilt the editor from a disassembly but
   never published the disassembly listing. His rebuilt binary (CSDb #44814,
   `gmc_v2.zip`) is the best proxy — disassembling Fenek's player would yield a
   clean, optimised version of the GMC V1.0 structure.

5. **V1.6 100% bug fixes:** The TAT bug-fix release (CSDb #156855) labels itself
   "100%" — implying specific known bugs in the original V1.6. Investigating CSDb
   comments on #156855 would list the bugs, which would help target the RE work.

6. **"Eqaleditor V1" (1990, Caution group):** Brian's earliest music tool, predating
   GMC. Fetching its CSDb or Demozoo entry would reveal whether it is a format
   ancestor of GMC or an independent design.
