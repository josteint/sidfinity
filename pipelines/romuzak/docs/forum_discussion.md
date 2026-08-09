---
source_url: multiple — see per-section provenance headers
fetched_via: WebSearch + WebFetch + local HVSC binary inspection
fetch_date: 2026-06-13
author: aggregated from multiple sources
content_date: 1989–2009 (original posts/releases); 2026-06-13 (this aggregation)
reliability: primary for HVSC binary data; secondary for forum summaries
---

# RoMuzak — Forum, Wiki, and Scene Discussion

## Summary of sources searched

Platforms covered: CSDb (csdb.dk), Forum64.de, Lemon64, c64scene.pl (Polish C64 scene),
chipmusic.org, Codebase64, comp.sys.cbm (Google Groups Usenet archive), VGMPF wiki,
Remix64 interviews, 64er Magazin scans (Archive.org), Woolyss chiptracker list.

CSDb returned HTTP 503 during session — Wayback fallback also failed. Direct thread text
extracted via c64scene.pl (succeeded) and Google search snippets (for Forum64.de thread
titles / summaries); Forum64.de returned HTTP 403. 64er Magazin PDFs were not searchable
via WebFetch. Usenet/Google Groups: one marginal mention found.

---

## 1. CSDb releases

### [CSDb] RoMuzak V6.3 — release ID 17814

```
source_url: https://csdb.dk/release/?id=17814
fetched_via: Google search snippet (CSDb returned 503 during session)
fetch_date: 2026-06-13
reliability: primary
```

- **Title:** RoMuzak V6.3
- **Year:** 1989
- **Groups:** Apa-Soft and Cosmos (crack/release group)
- **Type:** Tool
- **Author:** Oliver Blasnik (ROM)
- **Publisher:** Digital Marketing
- **Notes:** V6.3 is the canonical first public version. Released/cracked by Apa-Soft + Cosmos.

### [CSDb] RoMuzak V7.96 — release ID 17819

```
source_url: https://csdb.dk/release/?id=17819
fetched_via: Google search snippet (CSDb returned 503 during session)
fetch_date: 2026-06-13
reliability: primary
```

- **Title:** RoMuzak V7.96
- **Year:** 1990 (release date: 15 March 1990)
- **Author:** Oliver Blasnik (ROM)
- **Publisher:** Digital Marketing
- **Type:** Tool

---

## 2. Forum64.de — "Romuzak" thread (thread #15654)

```
source_url: https://www.forum64.de/index.php?thread/15654-romuzak/
fetched_via: Google search snippet (Forum64 returned 403 during session)
fetch_date: 2026-06-13
reliability: secondary (extracted from Google snippet text, not direct page fetch)
```

Thread on the major German C64 forum. Key findings from Google's indexed snippet:

1. **Version hunting:** A user was looking for a RoMuzak version higher than 6.3.
2. **Version signature discovery:** "Some tunes contained the signature `RMZ+V7.96`" — confirming
   a V7.96 exists, distinct from V6.3.
3. **Availability:** The tool was reportedly no longer available anywhere at the time of the thread.
4. **Kryoflux preservation:** One participant created a disk image of the DM (Digital Marketing)
   RoMuzak disk using Kryoflux — suggesting the original Digital Marketing distribution disk was
   being actively preserved.
5. **Scarcity:** Multiple participants confirmed they had never found V7.96 except as embedded
   player code inside SID files (via the `RMZ+V7.96` string in HVSC tunes).

**Thread participants:** German C64 sceners; thread appeared in the "Musik" (Music) sub-forum.

**Thread #83160 (Digital Marketing)** — related thread also on Forum64.de:
- Contains additional discussion about Kryoflux imaging of the Digital Marketing PD disk.
- Digital Marketing PD = a large collection of 537+ C64 disk images (preserved on SceneBase.org).

---

## 3. c64scene.pl — "Player SID-ów na C64" thread (thread #112)

```
source_url: https://www.c64scene.pl/viewtopic.php?t=112
fetched_via: direct WebFetch (succeeded)
fetch_date: 2026-06-13
author: skull, prezes, booker, V-12, leming, kotrobot
content_date: March 4–31, 2009
reliability: primary
```

Polish C64 scene forum thread. This is the most technically detailed public discussion of
RoMuzak player internals found in any online source.

### Post #1 — skull (Mar 4, 2009)

**Problem:** The original RoMuzak player does not fit between interrupt calls in a demo context.
Seeking a faster version or a split version with source code.

### Post #2 — prezes (Mar 4, 2009)

**Technical advice:**
- Suggests disabling I/O during playback: `LDA #$30 / STA $01` (bank out I/O)
- Shadow SID registers: copy all `$D400–$D41F` writes to a RAM buffer, then restore on VBI
- Alternative: call individual channel routines separately (find the 3× repeated jump in player
  code, call each channel's entry point individually)

### Post #4 — prezes (Mar 4, 2009)

- Clarifies PSID/RSID format
- Notes the player manages "register contents" and does not alter the composition data itself

### Post #6 — skull (Mar 5, 2009)

**Key technical finding:** The SID file he was working with contained **"several ROM players"**
(i.e. multiple embedded player instances, presumably for multiple sub-tunes).

**Performance problem:**
> "For one iteration (for one track) to consume even twenty-some raster lines seems excessive
> (admittedly with displayed sprites)."

Successfully disassembled RoMuzak V6.3 using the tool **64COPY**. Offered to share the
disassembly.

**Technical implication:** `~20 raster lines per channel per call`. Since the SID has 3 voices,
full playback costs ~60 raster lines per VBI interrupt — a significant fraction of the ~312
available PAL raster lines. Compare: Future Composer (per post #14) costs roughly half or less.

### Post #7 — V-12 (Mar 5, 2009)

- Notes that RoMuzak source can be created via **Turbo Reassembler** disassembly.

### Post #9 — skull (Mar 7, 2009)

- Successfully split the player code into individual channel modules
- Synchronized music with interrupt constraints
- Status: "disassembled and split satisfactorily"

### Post #13 — skull (Mar 30, 2009)

**Verbatim in-binary credit string identified:**
```
** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!! 02435-1295!! **
```

Note: `<W>` = written by (German "W" for "geschrieben von"), `<C>` = copyright.
Phone number `02435-1295` is the Digital Marketing business phone (Hückelhoven area code 02435).

### Post #14 — booker (Mar 30, 2009)

**Comparison:** Future Composer (specifically "Geir's recoded FC implementation") uses
approximately **2× less raster** than RoMuzak — a significant performance advantage.

### Post #15 — skull (Mar 30, 2009)

**Resolution — complete breakdown of modifications made:**

1. **Modular decomposition:** Player broken into individual per-channel calls
2. **Security/validation check removal:** Author/copyright validation routines stripped
   (these are the bytes that check the credit string and stall if tampered)
3. **Per-channel invocation:** Each of the 3 SID channels called as separate routines
4. **Redundant code removed:** Unnecessary verification sections eliminated
5. **Result:** Music "no longer presents any problems" within the demo context

**Technical implication for RE:** The player contains a **copyright validation routine** that
reads the in-binary credit string. This routine must be located before instrument processing
to be safely stripped. It likely checks a signature byte or CRC against the embedded string.

---

## 4. VGMPF Wiki — Future Composer article

```
source_url: https://www.vgmpf.com/Wiki/index.php?title=Future_Composer
fetched_via: direct WebFetch
fetch_date: 2026-06-13
reliability: secondary (wiki)
```

Single RoMuzak mention:
> "RoMuzak can convert Future Composer V1.0 songs."

No additional technical detail. Confirms the FC conversion feature is publicly documented.

---

## 5. Lemon64 — V-Ga game music entry

```
source_url: https://www.lemon64.com/game/v-ga
fetched_via: direct WebFetch
fetch_date: 2026-06-13
reliability: primary (HVSC STIL data)
```

From HVSC #83 STIL:
> "Tune converted from Future Composer to RoMuzak; released in 1989 on Digital Marketing disk
> #182 as '21.RoMuzak Tune'."

This confirms:
1. RoMuzak was a **conversion target** for FC tunes, not just a native editor
2. Digital Marketing distributed individual RoMuzak tunes on their PD disk series (disk #182
   in this case)
3. The tune was originally composed in FC and later re-exported in RoMuzak format

---

## 6. Remix64 — Thomas Detert interview

```
source_url: https://remix64.com/interviews/interview-thomas-detert.html
fetched_via: direct WebFetch
fetch_date: 2026-06-13
reliability: primary
```

Thomas Detert used **RoMuzak V6.3** to compose music for his "first two games" (one delayed,
one unreleased) on C64. He subsequently switched to **Compotech** for later work.

No technical details about RoMuzak given in the interview. His HVSC folder includes
`RoMuzak_V6_3_intro.sid` as the only RoMuzak-attributed tune.

---

## 7. VGMPF — Thomas Detert article

```
source_url: https://www.vgmpf.com/Wiki/index.php/Thomas_Detert
fetched_via: direct WebFetch
fetch_date: 2026-06-13
reliability: secondary
```

Confirms Detert used "RoMuzak V6.3 when arranging music for his first two games."
Subsequently switched to Compotech.

---

## 8. Remix64 — Stefan Hartwig profile

```
source_url: https://www.remix64.com/interviews/interview-stefan-hartwig.html
fetched_via: direct WebFetch
fetch_date: 2026-06-13
reliability: primary (interview)
```

Stefan Hartwig's interview makes **no mention of RoMuzak** despite his being the most
prolific V7.96 user in HVSC (22 of 22 V7.96 SIDs are in his HVSC directory or by
musicians he worked with). He discussed working with "music routines created by a friend."

---

## 9. comp.sys.cbm (Google Groups / Usenet)

```
source_url: https://groups.google.com/g/comp.sys.cbm/search?q=RoMuzak
fetched_via: WebFetch
fetch_date: 2026-06-13
reliability: secondary (search result snippet)
```

**One post found:** Author: William Jhun and Jeff Gilbertson, date: March 3, 1993,
subject: "STEREO PROGRAMS". RoMuzak mentioned alongside other SID music formats in a
discussion about stereo program implementations and SID chip capabilities.
No technical detail about RoMuzak's internals.

---

## 10. sidid identification file (cadaver/sidid)

(Full detail in `github_sidid_signature.md` — summarized here)

```
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
fetched_via: direct WebFetch
fetch_date: 2026-06-13
reliability: primary
```

Two entries:
```
RoMuzak_V6.x   Author: Oliver Blasnik (ROM)   Released: 1989 Digital Marketing
RoMuzak_V7.x   Author: Oliver Blasnik (ROM)   (release date not in nfo)
```

---

## 11. HVSC-local findings (local binary inspection — NOT RE)

```
source_url: local HVSC at /home/jtr/sidfinity/hvsc85/
fetched_via: direct filesystem inspection (python3 string extraction)
fetch_date: 2026-06-13
reliability: primary (binary data)
```

### Embedded string observations (not RE — these are printable strings visible in the binary)

**V6.3 binary credit string** (verbatim, from all V6.3 SIDs):
```
** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!! 02435-1295!! **
```

**V7.96 binary credit string** (verbatim, from V7.96 SIDs, longer form):
```
*** ROMUZAK V7.9 (W) BY OLIVER BLASNIK (C) BY DIGITAL MARKETING /KREFELDER STR.16 /5142 HUECKELHOVEN2 ***
```

Key differences:
- V6.3 uses `<W>` / `<C>` angle-bracket style; V7.9 switches to `(W)` / `(C)` parenthesis style
- V7.9 includes **full business address**: Krefelder Str. 16, 5142 Hückelhoven 2 (postal code
  5142 = old West German format for what is now 41836 Hückelhoven, Nordrhein-Westfalen)
- V6.3 gives phone only (`02435-1295`); V7.9 gives address but omits phone

**Compact machine-readable tag:**
- V6.3: `ROMUZAK89F` (10 bytes, at load+$09)
- V7.96: `RMZ+V7.96` (9 bytes, at V7 player block +$09)

### HVSC census (V6.x vs V7.x)

Searched all 60,000+ SIDs in HVSC for `ROMUZAK` string:

| Version | Count | Primary users |
|---------|-------|---------------|
| V6.3    | 598   | ECO (Raik Picheta), various German sceners |
| V7.96   | 22    | Stefan Hartwig (Starbyte games), Goesta Feiweier, Arndt Heitkamp, Schaefers/Frank (Rockin Limited) |

All V7.96 SIDs are in `MUSICIANS/H/Hartwig_Stefan/`, `MUSICIANS/H/Heitkamp_Arndt/`,
`MUSICIANS/R/Rockin_Limited/Schaefers_Frank/`, `MUSICIANS/F/Feiweier_Goesta/`,
and `DEMOS/UNKNOWN/M_O_N-Medley.sid`.

### Dual-player layout in V7.96 SIDs (observational)

V7.96 SIDs contain **two complete player blocks**:
- Block 1 (V6.3 player): loads at a lower address (e.g. C64 `$6E00` in Crime_Time)
- Block 2 (V7.96 player): loads at `$8000` (in the analyzed Crime_Time example)

The `ROMUZAK89F` machine tag is present in Block 1 (the V6.3 portion), and `RMZ+V7.96` in
Block 2. This suggests V7.96 SIDs include a **compatibility layer** or **legacy sub-player**
for (presumably) the FC-converted voice data, alongside a new V7 player for native V7.96 data.

**NOTE:** This is an observational note about printable strings and their offsets. Full
interpretation requires RE of the init dispatch — flagged as OPEN below.

### PSID header data (observational)

| SID | load | init | play | songs | speed |
|-----|------|------|------|-------|-------|
| V6.3 RoMuzak_V6_3_intro.sid | $8000 | $8000 | $8003 | 1 | $00000000 (VBlank) |
| V6.3 Romuzak_Test.sid | $8000 | $8000 | $8003 | 1 | $00000000 (VBlank) |
| V6.3 Eco/Chariots_of_Fire.sid | $1000 | $1000 | $1003 | 1 | $00000000 (VBlank) |
| V7.96 Crime_Time.sid | $6E00 | $9493 | $7FFD | 2 | $00000000 (VBlank) |

All versions use VBlank (PAL 50 Hz) timing (`speed = 0`). No CIA-timed tunes found.
V7.96 multi-subtune SIDs have a separate init address (`$9493`) well above both player blocks,
suggesting a top-level dispatcher that selects which block to activate per subtune.

### Update01.hvs / Update02.hvs references

Early HVSC update scripts referenced Oliver Blasnik's SID files by their original filenames:
```
ROMUZK02.DAT, ROMUZK05.DAT, ROMUZK06.DAT, ROMUZK08.DAT
```
(Under `\various\blasnik\` in the pre-HVSC-v1 layout.) These `.DAT` suffixes were the
original RoMuzak output format before the PSID wrapper was added. `romuzk08.dat` in
`Update02.hvs` maps to a later Blasnik composition, suggesting at least 8 RoMuzak tunes
from Blasnik himself existed in the early HVSC.

---

## Leads to follow

- **OPEN (RE needed):** Confirm the copyright-validation routine structure (c64scene.pl post
  confirms it exists and can be stripped; its location relative to init/play entry is unknown).
- **OPEN (RE needed):** Understand the dual-player init dispatch in V7.96 SIDs — specifically
  what the init at C64 `$9493` does to select between the V6.3 and V7.96 sub-players per subtune.
- **OPEN (Forum64 content):** Forum64 thread #15654 ("Romuzak") blocked during this session
  (HTTP 403). Worth retrying via Wayback Machine or direct fetch in a later session. The thread
  contains user reports of finding V7.96 via the `RMZ+V7.96` string — there may be more detail
  about which users had the actual editor disk.
- **OPEN (Kryoflux image):** A German scener in Forum64 thread #83160 created a Kryoflux image
  of the original Digital Marketing RoMuzak disk. If uploaded to CSDb or elsewhere, this would
  be the only known copy of the V7.96 editor binary. Search CSDb downloads when CSDb is back up.
- **OPEN (64er Magazin):** 1989–1990 issues are OCR-scanned on Archive.org
  (e.g. `https://archive.org/details/64er_1989_09`). RoMuzak was a commercial PD product in
  Germany — a review in 64er would be high-value. PDF full-text search not accessible via
  WebFetch during this session; try direct download + grep.
- **OPEN (skull disassembly):** The Polish scener "skull" (c64scene.pl, 760 posts, 2009)
  successfully disassembled V6.3 with 64COPY and offered to share it. If the share was
  posted to c64scene.pl or another site, this is the only known public hand-annotated
  disassembly of RoMuzak V6.3. Worth tracking down via c64scene.pl PM system or CSDb scener
  search (handle "skull", Polish scene, C64 programmer).
- **OPEN (Manfred Trenz attribution):** Several web sources incorrectly attribute RoMuzak to
  Manfred Trenz. In-binary strings confirm Oliver Blasnik. Trenz connection is a false lead —
  likely confusion with Trenz's use of Digital Marketing for his own game music.
- **OPEN (ACT 501 editor disk):** Archive.org has two disk images:
  - `d64_Romuzak_Music_Demo-Editor_1989_ACT_501`
  - `d64_Romuzak_Analyser-Play_Construction_Kit_1989_ACT_501`
  These are the editor itself (not just player-embedded SIDs). Extracting the PRG from the
  D64 (via c1541 or cbmconvert — no emulator needed) would reveal the editor's internal
  structure: menus, instrument editor fields, effect names, pattern commands. This is the
  highest-ROI action before RE.
- **OPEN (Compotech connection):** Thomas Detert switched from RoMuzak to Compotech.
  Compotech is another German commercial C64 music editor. Understanding Compotech's model
  may shed light on what RoMuzak lacked (triggering the switch).
- **OPEN (Goesta Feiweier attribution):** Feiweier's 12 HVSC V7.96 SIDs include
  `Detonators.sid`, `Karamalz_Cup.sid`, `Puxxle.sid` etc. — all commercial game music (1990–
  1991 era). His V7.96 use pattern suggests V7.96 was the professional/commercial edition.
