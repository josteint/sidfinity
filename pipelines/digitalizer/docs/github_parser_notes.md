---
source_url: https://csdb.dk/scener/?id=8158 ; https://demozoo.org/sceners/1261/ ; https://csdb.dk/release/?id=33646..33650 ; https://c64.rulez.org/pub/c64/Tools/Music/Editor/ ; https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=129
fetched_via: direct
fetch_date: 2026-06-13
author: CSDb community; Demozoo; Zimmers; Recollection
content_date: 1989–2026
reliability: secondary
---

# Digitalizer — Parser Notes and Open Questions from GitHub Survey

## Version History (confirmed from CSDb)

| Version | Year  | CSDb ID | Coder(s)                                    | Group(s)                    | Downloads |
|---------|-------|---------|---------------------------------------------|-----------------------------|-----------|
| V2.2    | 1989  | 33646   | Olav Mørkrid                               | Panoramic Designs           | 676       |
| V2.5    | 1989  | 33647   | Olav Mørkrid                               | Panoramic Designs           | 700       |
| V2.7    | ????  | 108478  | Olav Mørkrid                               | Panoramic Designs           | 393       |
| V2.8    | 1991  | 33648   | Olav Mørkrid                               | Panoramic Designs           | 714       |
| V3.0    | 1992  | 33649   | Olav Mørkrid                               | Panoramic Designs           | 376       |
| V3.5    | 1995  | 33650   | Olav Mørkrid + 6R6 + Kjell Nordbo          | Panoramic Designs + SHAPE   | 1418      |

V3.0 is also known as "v2.9 (FF)" — suggests internal version confusion or a beta
designation used within Panoramic Designs.

V3.5 is the highest-download version and the last. The collaboration with Blues Muz'/SHAPE
members (6R6 and Kjell Nordbo) brought in external contributors.

### Notable: Blues Muz Player V1.0 (Jun 1994)

Olav Mørkrid coded the "Blues Muz Player V1.0" for group "Regina" (listed on Demozoo
under "Earwax Music V2.05", Oct 1993 = musicdisk where he coded the player). This is
a SEPARATE player tool, not the Digitalizer editor itself.

---

## What GitHub Search Found (and Did Not Find)

### FOUND in open-source tools:
1. `cadaver/sidid`: `Digitalizer_V3.0` (32-byte exact) + `Digitalizer_V2.x` (7-byte loose)
   + `Olav_Moerkrid` (3 chained patterns) + `Panorama` (single pattern)
2. `WilfredC64/player-id`: Same Digitalizer entries; different `Olav_Moerkrid` pattern
3. `Chordian/deepsid`: `'Olav_Moerkrid'` pretty-name only; no Digitalizer-specific code
4. Binary archives: V2.8 disk images at Zimmers FTP; V2.2/V2.5/V2.7/V2.8/V3.0/V3.5 at CSDb

### NOT FOUND in any open-source tool:
- No format specification or documentation file
- No parser, converter, or decompiler for Digitalizer format
- No "Digitalizer_V3.5" sidid signature (gap — this version has most downloads)
- No SIDFactory II, GoatTracker, CheeseCutter, or SID-Wizard import of Digitalizer format
- No Python/JS/Rust reader of the Digitalizer data format
- No VICE or libsidplayfp special case
- No public disassembly of any Digitalizer version on GitHub

---

## Inferences from sidid Signatures (NO RE Performed)

### V3.0 Signature Analysis

The 32-byte V3.0 signature contains fixed absolute addresses:
- `$033A` — appears twice (loop counter/index in stack page)
- `$033D` — output target 1
- `$0340` — output target 2
- ZP `$FB`/`$FC` — data pointer (16-bit)

OPEN (RE needed): What is the V3.0 player load address?

The bytes describe a sample-processing loop with:
- Indirect indexed read via ZP pointer
- Two comparison thresholds: `$80` (mid-scale) and `$C0` (upper quarter)  
- Two absolute stores (possibly L/R or two SID registers)
- A `$3F` end-of-buffer sentinel

**This strongly suggests V3.0 is primarily a DIGI/sample player** (digital sample
playback engine) rather than a pure tracker. The name "Digitalizer" aligns — it digitizes
audio samples and plays them back on the C64 SID chip (via volume register $D418 or
similar technique).

### V2.x Signature Analysis

The 7-byte pattern `9D ?? ?? 0A 90 ?? B9`:
- `STA $????,X` + `ASL A` + `BCC` + `LDA $????,Y`
- Wildcard addresses mean it IS relocatable
- Very minimal — could be just the innermost sample-write loop

### Olav_Moerkrid Signature Analysis

The 3-chained patterns in cadaver's version suggest a MORE COMPLEX engine than
sample-only:
- Pattern B shows `EOR #$01 / AND #$01` — **gate bit toggling** (note on/off)
- Pattern C shows `INC $0C,X` + ZP pointer `$FC` + sentinel `$7F` — **sequence data with $7F end marker**
- Pattern A shows ADC-based frequency accumulation — **frequency/pitch handling**

The Olav_Moerkrid entry may detect later Digitalizer-generated SIDs where the player
embeds a more capable music engine (V2.x era?), while Digitalizer_V3.0 detects the
sample playback component.

OPEN (RE needed): Are these two separate runtime components (a synth sequencer + a
sample player), or does the Olav_Moerkrid signature detect a completely different tool
that Olav wrote?

### Panorama Signature Analysis

```
AD ?? ?? D0 03 4C ?? ?? [×3] AD ?? ?? 29 01 D0
```
This is a **3-voice voice-skipping dispatcher** — each voice has an "active" flag;
if non-zero, skip to next handler via JMP. The final `AND #$01 / BNE` checks a gate/flag bit.
This is a PLAY routine entry — the dispatcher that routes to per-voice handlers.

OPEN (RE needed): Is "Panorama" in sidid.cfg the Panoramic Designs group's house player
(used in demos/musicdisks), or is it the embedded player generated BY Digitalizer?

---

## Olav Mørkrid Background (Relevant Context)

From Demozoo + CSDb + Recollection interview:
- Born early 1990s into scene (started coding C64 in ~1987 with The Shadows)
- Norwegian; later co-founded Funcom (1993) — the Daze Before Christmas / Snowman's Land developer
- Handles: Omega Supreme, The Disk Ripper
- In interview (Recollection #2 by Jazzcat): mentions borrowing from "Stein Pedersen's
  music editor" as inspiration. Stein Pedersen = another Norwegian C64 coder.
  OPEN: Is Digitalizer derived from Stein Pedersen's editor? This would explain
  the Norwegian scene-private nature of the format.
- 1993: joined Funcom; C64 activity reduced
- 2026: still active in demo scene (Blood Eye Vision, Jan 2026)

---

## Files Available for Binary Analysis (RE needed, not done here)

All links are CSDB getinternalfile links — these would require downloading ZIP/D64:

| Version | URL                                                            | Size |
|---------|----------------------------------------------------------------|------|
| V2.2    | csdb.dk/getinternalfile.php/23398/Digitalizer_V2.2.zip        | ?    |
| V2.5    | csdb.dk/getinternalfile.php/25553/DISK5171.ZIP                 | ?    |
| V2.7    | csdb.dk (d64.gz format)                                        | ?    |
| V2.8    | csdb.dk/getinternalfile.php/23400/Digitalizer_v2.8.zip        | 8.3K |
| V2.8    | c64.rulez.org/.../Olav_M0rkrids_Digitalizer_v2,8[Panoramic].zip | 8.3K |
| V3.0    | csdb.dk/getinternalfile.php (see release 33649)               | ?    |
| V3.5    | csdb.dk/getinternalfile.php/23372/DIGITALIZER-V35.zip         | ?    |

The V2.8 (8.3K) and V3.0 (with converted help text file, per 6R6's comment)
are the most actionable starting points for format RE.

---

## HVSC84 Corpus Count (from hvsc84.db — already classified by sidid)

```
Digitalizer_V2.x   542 SIDs
Digitalizer_V3.0    77 SIDs
Olav_Moerkrid       38 SIDs
Panorama             0 SIDs (not found — "Panorama" may not be the sidid engine name)
```

Total target corpus: **657 SIDs** across all Digitalizer/Olav engine tags in HVSC84.
V2.x is the dominant variant (82% of corpus). V3.0 is 12%. Olav_Moerkrid is 6%.

Note: The `Panorama` sidid entry produces 0 matches in HVSC84 — either the pattern
is too conservative, or those SIDs aren't in HVSC. The "Panorama" player may be used
in demo data files not submitted to HVSC.

## Leads to Follow

1. **Download V2.8 and V3.0 binaries from CSDb** — these are publicly available.
   V3.0 has a converted help text file (uploaded by 6R6 in July 2013) that may
   contain format documentation.
   URL: csdb.dk/getinternalfile.php/23372/ for V3.5;
   see csdb.dk/release/?id=33649 for V3.0 download link.

2. **Search HVSC STIL.txt for Digitalizer mentions** — STIL (SID Tune Information List)
   may have comments from composers noting "made with Digitalizer V3.0" or similar.
   HVSC STIL.txt is available at:
   https://www.sannic.nl/hvsc/C64Music/DOCUMENTS/STIL.txt (mirror)

3. **Search HVSC SIDId results** — HVSC runs sidid over its collection and publishes
   results. How many SIDs match `Digitalizer_V3.0` / `Digitalizer_V2.x` / `Olav_Moerkrid`?
   This gives the corpus size. HVSC's own `SIDIDLIST` or classification file.

4. **sidid.nfo binary (45.2KB)** — the large sidid.nfo fetched as binary contains the
   full human-readable database (cadaver's notes, author credits, CSDB links per player).
   The Digitalizer entries are in there. Needs download + text extraction:
   URL: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo

5. **Blues Muz player search** — V3.5 contributors 6R6 and Kjell Nordbo coded Blues Muz
   Player V1.0. Is there a "Blues_Muz" sidid signature? If so it may detect V3.5-era SIDs.
   Search: grep "Blues" in cadaver/sidid/sidid.cfg.

6. **Stein Pedersen's music editor** — Olav explicitly cited this as his inspiration
   (Recollection interview). Stein Pedersen is a Norwegian C64 coder; his editor predates
   Digitalizer (pre-1989). If this editor's format is known, it constrains Digitalizer's
   design space. Search CSDb for Stein Pedersen.

7. **HVSC classification by engine** — hvsc84.db in this repo may already have Digitalizer
   SIDs classified under "Olav_Moerkrid" or "Digitalizer_V3.0" if sidid was run over HVSC84.
   Query: `SELECT path, engine FROM sids WHERE engine LIKE '%Digitaliz%' OR engine LIKE '%Olav%'`
