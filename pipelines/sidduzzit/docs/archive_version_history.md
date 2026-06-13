# SID Duzz'It — Version History

<!-- provenance
  sources:
    - url: https://csdb.dk/group/?id=142&show=tools
      fetched_via: direct
      fetch_date: 2026-06-13
      content_date: 2026-06-13
      reliability: high (CSDb is the canonical C64 scene archive)
    - url: https://sourceforge.net/projects/sidduzzit/files/
      fetched_via: direct
      fetch_date: 2026-06-13
      reliability: high (official SourceForge project, registered 2014-11-07)
    - url: https://csdb.dk/release/?id=133692  (V2.1.7)
      fetched_via: direct
      fetch_date: 2026-06-13
      reliability: high
    - url: https://csdb.dk/release/?id=114693  (V2.1.6)
      fetched_via: direct
      fetch_date: 2026-06-13
      reliability: high
    - url: https://csdb.dk/release/?id=132363  (V2.1)
      fetched_via: direct
      fetch_date: 2026-06-13
      reliability: high
    - url: https://master.dl.sourceforge.net/project/sidduzzit/sdi217_releasenotes_README.txt
      fetched_via: direct (via SourceForge redirect)
      fetch_date: 2026-06-13
      reliability: high (official release note, 477 bytes verbatim)
    - url: https://master.dl.sourceforge.net/project/sidduzzit/SDI.2.1.6-docs.txt
      fetched_via: direct (via SourceForge redirect)
      fetch_date: 2026-06-13
      content_date: 2013-05-18
      reliability: high (official 65 KB documentation file)
    - hvsc84.db PSID metadata
      fetched_via: local sqlite query
      fetch_date: 2026-06-13
      reliability: high (HVSC #84 ground truth)
-->

## Summary

SID Duzz'It (SDI) is a 3+1 channel music tracker for C64/C128, created by
**Geir Tjelta** (handle **GT**) and **Glenn Rune Gallefoss** (handle **6R6** /
GRG) of the Norwegian scene group **SHAPE**. Development spans 1992–2014
across roughly 14 discrete public releases, with a V3.0 MIDI branch started in
2013 that was not formally completed.

- **HVSC #84 count:** 934 SID files (engine tag `Geir_Tjelta/SIDDuzz'It`)
- **Author spread (HVSC):** Fredrik (143), Glenn Rune Gallefoss (141),
  Jan D. Arent Harries / SIDwave (117), Joe Barwick / Stainless Steel (53),
  and ~30 other composers
- **Active years in HVSC:** 1992–2025
- **Peak HVSC year:** 2006 (103 tunes), followed by 2010 (91 tunes)

---

## Version Table

| Version | CSDb ID | Date | Key authors | Notes |
|---------|---------|------|-------------|-------|
| GT's Musiceditor (precursor) | 33645 | 1992 | GT | Unfinished personal editor; includes work-tunes; GT notes "crashes sometimes when changing subtunes". NOT the SDI format. |
| Editor Preview (precursor) | 134608 | ~1992–95 | GT | Unpublished preview; predecessor to V1. No date visible on CSDb. |
| **V1** | 161716 | 1996 | GT (code + music) | First public release. Sole author GT. Distributed as `SID_Duzz_IT_V1-Geir_Tjelta_1996.d64`. |
| **V0.98** | 121615 | April 1998 | GT (code), 6R6 (docs) | Pre-1.0 "beta" re-release; 6R6 joined to write documentation. Player source in TASS format. |
| **V0.98A** | 6106 | September 1999 | GT (code), 6R6 (docs) | Minor update to V0.98. Old SDI home page listed: `http://home.eunet.no/~ggallefo/sdi/` (now dead; Wayback inaccessible). |
| **V1.3** | 121619 | 21 April 2001 | 6R6 + GT | V1.x branch resumes; 6R6 now co-coder. Docs: 6R6. Sample tracks by "Tjelta Geir and Glenn Gallefoss from Blues Muz'". |
| **V1.5** | 121622 | 22 May 2002 | 6R6 + GT | Bundled with 9 composition examples by Glenn Rune Gallefoss (Blues Muz' catalogue). |
| **V1.801** | 7175 | October 2002 | 6R6 + GT | Last V1.x release. Old SDI home page still listed: `http://home.eunet.no/~ggallefo/sdi/`. CSDb upload in 2008 as preservation (Mace: "in case Glenn's website fails"). **NOTE:** A CSDb comment on V2.0 Beta 7 says "this release can't read 1.8 files, nor can 1.8 read 2.17 files" — the V1.x and V2.x formats are BINARY-INCOMPATIBLE. |
| **V2.0 Beta 7** | 76999 | 19 May 2006 | 6R6 + GT | First public V2.x beta. Bundled "SDI 1.8 tunes converted to 2.0.zip" suggesting a converter tool was released alongside. CSDb notes the converter had a bug (seq #11 in Super Monaco GP). Frequency table changed: V1.8 used NTSC-derived tables, V2.x uses PAL — converted tunes will be detuned if PAL freq table is selected in V2. V2.07 player with ADSR fix mentioned in comments. |
| **V2.0 Beta 8** | 84874 | 2009 | 6R6 + GT | Second V2.x beta. Users recommended upgrading to "SDI V2.07 Player ADSR Fixed" (separate player-only fix). |
| **V1 [2009 re-release]** | 78942 | 19 May 2009 | GT | GT published a previously unreleased V1 variant ("That version wasn't released until now"). Includes "Blue Mazda 323" composition. |
| **V2.1** | 132363 | 15 January 2013 | 6R6 + GT | First stable V2.1; "entry restored for archival purpose only" on CSDb — superseded quickly by V2.1.6. |
| **V2.1.6** | 114693 | 18 May 2013 | 6R6 + GT | Documentation-accompanied stable release. Ships `SDI.2.1.6-docs.txt` (64.9 KB), `SDI.2.1.6-keys.txt`, `SDI.2.1.6-note_tables.txt`, keyboard reference JPG. 6R6: "Uploaded the last update that fixes the most annoying bugs." Rated 9.9/10 on CSDb. **The format doc version used as the canonical reference for HVSC tunes.** |
| **V3.0 MIDI Preview** | 118973 | 19 May 2013 | 6R6 + GT | Parallel MIDI branch. Supports Steinberg Research, Datel, JMS, Sequential Circuits MIDI interfaces. H/B note selection. Users noted "very responsive" latency on real hardware; much worse on emulator. 6R6: "Added some stuff. Removed some stuff and optimized some stuff." |
| **V3.0 MIDI Preview 2** | 119228 | 31 May 2013 | 6R6 + GT | Minor update to MIDI branch; shipped with `sdiMidi.txt` documentation. |
| **V2.1.7** | 133692 | 12 October 2014 | 6R6 + GT | FINAL release. SourceForge zip `Sid_Duzz_It_v2.1.7-shape.zip` (96.4 KB). **Exactly two bug fixes** (see below). Greetings signed "GRG and GT of SHAPE". |

**V2.1.7 release notes (verbatim, 477 bytes total):**
> The filtercutoff routine was missing a small compare routine for fast downwards
> subtraction.
>
> Starting a composition with gatetimeout settings of Ax, Cx, or Ex could prevent
> the initial note from triggering properly.
>
> Greetings from GRG and GT of SHAPE.

---

## V1.x vs V2.x Format Incompatibility

From CSDb user comments on the V2.0 Beta 7 release:

- **Binary incompatible:** "this release can't read 1.8 files, nor can 1.8 read 2.17 files"
- **Frequency tables changed:** V1.8 used NTSC-derived frequency tables; V2.x uses PAL.
  When "SDI 1.8 tunes converted to 2.0" bundles are played with PAL freq tables selected,
  the tunes will be detuned.
- **Converter provided:** SHAPE shipped a V1.8→V2.0 converter alongside V2.0 Beta 7,
  but it had at least one known bug (sequence #11 in Super Monaco GP).

This means **any HVSC tune dated 1992–2002** (created during the V1.x era) was either
composed in V1.x and converted, or composed in one of the interim editor versions.
The 1992 tunes (earliest HVSC: `Haakon_92.sid`) were composed in GT's early private
editor before V1 was released.

---

## HVSC Entry-Point Layout Distribution

From HVSC #84 PSID headers (934 tunes):

| init addr | play addr | count | interpretation |
|-----------|-----------|-------|----------------|
| $0FFF | $1003 | 480 | Standard V2.x layout, init = base-1 |
| $1000 | $1003 | 129 | Standard V2.x layout, init = base |
| $E8FF | $E903 | 71 | Older layout (V1.x or early V2.x relocated to $E900) |
| $0FCB / $0FDE | various | 13 | Non-standard; possibly special versions |
| $1FFF / $2003 | $2003 | 11 | Player relocated to $2000 |
| $3FFF / $4003 | various | 10 | Player relocated to $4000 |
| $E000 / $E003 | various | 10 | Player relocated to $E000 |
| various others | various | ~210 | Other relocations |

Key observations:

1. **Standard layout dominant:** `init=$0FFF, play=$1003` (51%) matches V2.1.6 docs
   "assembled at $1000". `init=$0FFF` = base-1 as written by some PSID packers; the
   alternative `init=$1000` (14%) is the same player with a direct init pointer.

2. **1992-era tunes use V2.x layout:** Even `Darkstorm.sid` (1992, "K. Røstøen &
   G. R. Gallefoss") has `init=$0FFF, play=$1003`. This means either (a) the 1992
   tunes were re-packed with a V2.x player when submitted to HVSC, or (b) GT's private
   1992 editor already used the $1000 base — predating the V1 1996 public release.

3. **Anomalous 1992 tune:** `Haakon_92.sid` has `init=$29FF, play=$1003` — suggesting
   a relocated player or different packing. Warrants closer inspection.

4. **$E8FF/$E903 cluster (71 tunes):** Player assembled at $E900. Likely represents
   V1.x-era files or tunes packed for memory compatibility, not a different format.

5. **Corporation.sid and Remark_Music.sid (1992):** Have `init=$1003, play=$1000` —
   the init and play pointers are *swapped* relative to the standard layout. Possibly
   a different PSID-packing convention or init = JSR target, play = start of player.

---

## Documentation Artefacts on SourceForge (as of 2014-11-07)

All four files uploaded simultaneously on 2014-11-07:

| Filename | Size | Downloads | Content |
|----------|------|-----------|---------|
| `Sid_Duzz_It_v2.1.7-shape.zip` | 96.4 KB | 197 | Binary: editor + player TASS source |
| `SDI.2.1.6-docs.txt` | 64.9 KB | 70 | Full user manual (basis of Psylicium PDF) |
| `SDI.2.1.6-note_tables.txt` | 3.3 KB | 40 | PAL/NTSC note frequency tables |
| `sdi217_releasenotes_README.txt` | 477 bytes | 45 | V2.1.7 bug-fix notes (verbatim above) |

**Note:** The docs file is versioned `SDI.2.1.6` even in the V2.1.7 SourceForge
release — the format itself did not change between 2.1.6 and 2.1.7; only the
player binary was patched.

---

## Third-Party Documentation

| Item | CSDb ID | Date | Author | Notes |
|------|---------|------|--------|-------|
| SID Duzz'It PDF Manual (SDI 2.1.7) | 153760 | 19 Feb 2017 | Psylicium (Atlantis/F4CG) | "text from official docs (SDI 2.1.6) + corrections based on newer versions and my own experiences". Available at `files.psylicium.dk/sdi_217_manual.pdf` (328 ext. downloads + 888 via CSDb). Revised 26 Feb 2017 with arpeggio chapter edits. |

---

## Leads to follow

- **V1.x format spec:** No document explicitly describes the V1.x binary format.
  The only route is disassembly of the V1 player (`SID_Duzz_IT_V1-Geir_Tjelta_1996.d64`)
  from CSDb ID 161716, or V1.801 from CSDb ID 7175.
- **V1.8→V2.0 converter:** Was bundled in V2.0 Beta 7 (CSDb ID 76999).
  Its algorithm would reveal the mapping between V1.x and V2.x data structures.
  Worth downloading and inspecting.
- **Wayback SDI home page:** `http://home.eunet.no/~ggallefo/sdi/` was live circa
  1999–2008 (EUnet Norway personal hosting). Wayback Machine was blocked during
  this research session — try again via a proxy or alternate fetcher. May contain
  older version docs, changelog, or download history.
- **ADSR bug in V2.0 Betas:** The "V2.07 Player ADSR Fixed" variant is mentioned in
  CSDb comments but has no separate CSDb release entry found. The V2.1.7 README fixes
  gate-timeout init — possibly the same bug class.
- **NTSC vs PAL frequency tables:** The V2.x player supports both. HVSC tunes are
  predominantly PAL. The 1.8→2.0 conversion issue with NTSC tables suggests some
  V1.x-era tunes in HVSC may sound detuned on a PAL V2.x player if not reconverted.
  Worth checking a sample of pre-2003 tunes.
