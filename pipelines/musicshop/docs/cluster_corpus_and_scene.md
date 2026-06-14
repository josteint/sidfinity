## MusicShop — HVSC Corpus Shape, Historical Context, and Scene Position

```
provenance:
  sources:
    - url: hvsc84.db (read-only SQLite query)
      fetched_via: python3 sqlite3, mode=ro URI
      fetch_date: 2026-06-14
      reliability: authoritative (HVSC #84 canonical metadata)
    - url: https://www.atarimagazines.com/compute/issue60/217_1_NEWS_PRODUCTS_64_Music_Program.php
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: 1985-05 (COMPUTE! issue 60 product announcement)
      reliability: contemporary review
    - url: http://c64-music.blogspot.com/2009/06/music-shop.html
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: 2009
      reliability: secondary (enthusiast blog, appears accurate)
    - url: https://www.lemon64.com/forum/viewtopic.php?t=45281
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: ~2012 forum thread
      reliability: secondary (community)
    - url: https://www.lemon64.com/forum/viewtopic.php?t=36765
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: ~2013 forum thread
      reliability: secondary (community; confirmed MIDI variant details)
    - url: https://archive.org/details/The_Music_Shop_Don_Williams_Broderbund_09-27-1984
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: 2021 upload (original 1984)
      reliability: primary artifact
    - url: https://csdb.dk/release/?id=82453
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: 1988
      reliability: secondary (crack release, not the original)
    - url: https://en.wikipedia.org/wiki/Broderbund
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: tertiary (Wikipedia)
  author: sidfinity research agent
```

---

## 1. HVSC Corpus Overview

Total MusicShop-tagged SIDs in HVSC #84: **182**
All are PSID version 2.
All are single-subtune (n_subtunes = 1) **except** Karateka (20 subtunes — see §4).
No CIA-timed (speed != 0) tunes detected; all run on the VBL interrupt.
Total approximate play time: ~3.9 hours across the corpus.

---

## 2. Address Cluster Table

| init_addr (hex) | init_addr (dec) | play_addr (hex) | play_addr (dec) | count | notes |
|---|---|---|---|---|---|
| $A04D | 41037 | $575A | 22362 | **180** | Standard Music Shop rip — fixed commercial program layout |
| $1000 | 4096 | $1003 | 4099 | 1 | Karateka (Broderbund/Ariolasoft, 1985) — 20 subtunes, likely Music Shop data at a relocated load |
| $7FF9 | 32761 | $80A0 | 32928 | 1 | Größenwarnsinnig Boulder Dash (Rockford-FD, 1993) — fan-made BD variant |

**Conclusion: essentially one fixed program layout.** 180 of 182 tunes (98.9%) share the identical init=$A04D, play=$575A addresses. This is the signature of the Music Shop runtime being ripped in-place from the commercial program: each `.sid` file is the Music Shop player binary concatenated with the encoded song data, loaded at a fixed origin. The player is NOT relocatable and was never designed as a standalone SID player; HVSC captures the program's playback stub at fixed RAM addresses.

The two exceptions are almost certainly misclassified or unusual variants:
- **Karateka** ($1000): Broderbund's 1985 game, 20 subtunes (the full game soundtrack), different load address — may use a stripped version of the Music Shop engine that was relocated for game integration. Francis Mechner (father of Karateka creator Jordan Mechner) composed the music, reportedly using The Music Shop tool itself on C64. The 20-subtune structure suggests the full game OST packed together.
- **Größenwarnsinnig Boulder Dash** ($7FF9): 1993 fan-made Boulder Dash variant from Rockford-FD; the Music Shop tag suggests the author used the software but presumably at a different load address or patched layout.

---

## 3. HVSC Folder Distribution

| HVSC path prefix | count | interpretation |
|---|---|---|
| `DEMOS/UNKNOWN/Music_Shop/` | **121** | Songs by unknown authors made with the program; HVSC groups them as "demos" with unknown provenance |
| `MUSICIANS/W/Williams_Don/` | 28 | Don Williams (the program's author) — the bundled demo songs that shipped with the retail product |
| `MUSICIANS/S/Safavy_Mehdi/` | 20 | Mehdi Safavy (Iran) — prolific user, undated original compositions |
| `MUSICIANS/E/Ewens_Louis/` | 3 | Louis Ewens — released 1984, Brøderbund Software credit (possibly additional Broderbund-supplied demo songs) |
| `MUSICIANS/A/Ace64/` | 3 | Ace64 — 1987 originals |
| `MUSICIANS/G/Gregfeel/` | 2 | Grzegorz Struminski (Gregfeel) — 1990s |
| `GAMES/G-L/` | 2 | Karateka + Größenwarnsinnig Boulder Dash |
| `DEMOS/A-F/` | 1 | City of New Orleans (E.T, 1986) |
| `DEMOS/M-R/` | 2 | Maenner (Ratti, undated); My Lovely Tune (T. Mierzwa, 1984) |

### What is the DEMOS/UNKNOWN/Music_Shop group?

This is almost certainly **songs composed by unidentified C64 users** who owned The Music Shop and shared their compositions via disk trading, bulletin boards, or magazines. They were collected by HVSC contributors who knew the player format but could not identify the authors. The repertoire is a culturally mixed European-American set: classical standards (Bach, Beethoven, Pachelbel, Offenbach), contemporary 1980s pop (Axel F, Ghostbusters, Rock Me Amadeus, Careless Whisper), folk, and original pieces. A significant Polish-language cluster exists (Bal w Przedszkolu, Baranek, Choinka, Ida Dzieci, Kicia, etc.), suggesting a Polish user community. The dates cluster in `198? <?>` (90 tunes) and `19?? <?>` (28 tunes) — consistent with mid-to-late 1980s activity before the demoscene adopted dedicated tracker tools.

These are NOT the program's bundled demo songs — those are credited to Don Williams (28) and Louis Ewens (3) in `MUSICIANS/`. The 121 UNKNOWN group represents community-created content from program users.

---

## 4. Composer/Author Concentration

| author (HVSC field) | count | context |
|---|---|---|
| `<?>` (unknown) | 121 | Community-created, author lost |
| `Don Williams <?>` | 28 | Program author; these are the retail demo songs (all released 1984 Brøderbund Software) |
| `Mehdi Safavy` | 20 | Iranian user, undated; 20 original compositions, titles in Farsi (Bedad, Elahe Naz, Esdahan, Golnar, Iran, Mahoor, etc.) — a remarkable non-European user community |
| `Louis Ewens` | 3 | Also credited 1984 Brøderbund Software (Elephant Trot, Kajun Klog, Oogie Boogie) — likely additional Broderbund staff/contractor demo songs |
| `Ace64` | 3 | 1987 originals |
| `Grzegorz Struminski (Gregfeel)` | 2 | 1990s; Billie Jean + Meluzyna |
| Others (E.T, Ratti, T. Mierzwa, Marek & Olaf Roth, Francis Mechner) | 5 | Scattered; Mechner = Karateka |

---

## 5. Year / Release Distribution

| year group | count | notes |
|---|---|---|
| 1984 | 34 | Authentic 1984 releases: 31 × "1984 Brøderbund Software" (Williams + Ewens) + 3 × "1984 <?>" |
| 1985 | 2 | At the Hop (date uncertain); Karateka (Ariolasoft) |
| 1986 | 1 | City of New Orleans (E.T) |
| 1987 | 3 | Ace64 trio |
| 198x (year uncertain) | 90 | Bulk of community-created content |
| 1993 | 1 | Größenwarnsinnig Boulder Dash |
| 199x | 2 | Gregfeel |
| 19?? | 49 | Mehdi Safavy (20) + other unknown |

The 1984 cluster (34) is the hard foundation: the retail product and its bundled content. The long `198x`/`19??` tail (139 tunes) is user-created material trickling in through the late 1980s and beyond.

---

## 6. Songlength Distribution

| bucket | count |
|---|---|
| < 30 s | 48 |
| 30–60 s | 55 |
| 1–2 min | 35 |
| 2–5 min | 42 |
| > 5 min | 2 |

Min: 9 s (West Side Story — likely a very short fragment), Max: 385 s = 6.4 min (Canon in D — Don Williams). Mean: 77.6 s. The median is in the 30–60 s bucket; the corpus is biased towards shorter pieces, consistent with a notation editor aimed at hobbyist music entry rather than full-length arrangements.

---

## 7. Historical and Commercial Context

### The software

The Music Shop was published by **Brøderbund Software** (Eugene, Oregon), released **September 27, 1984** for the Commodore 64. The developer is credited in the Archive.org disk image as **Don Williams** (also sometimes rendered "Dan Williams" in the archive metadata — same person). It was priced at **$44.95** (disk).

It is a **commercial music notation / composition program**, not a demoscene tool. The interface presents a traditional music staff with drop-down menus (Tools, THE MUSIC SHOP, Capture), supports 1- or 2-staff layouts, standard key signatures, dotted notes, ties, repeat bars, cut/copy/paste editing, and score save/load/print. Each of the three SID voices (V1, V2, V3) can be assigned independent instruments, envelopes, and waveforms.

A COMPUTE! Magazine product announcement (issue 60, May 1985) described it as enabling users to "create, store, and edit compositions and print out sheet music" with the synthesizer component able to add "sound textures." The same article noted upcoming IBM PCjr and Apple Macintosh versions for spring 1985.

The 1985 MIDI variant (**The Music Shop for MIDI**, co-published with Passport) added MIDI output via a Passport-compatible MIDI interface. Interestingly, the MIDI-version manual reportedly still described the original non-MIDI program without any MIDI-specific documentation — suggesting the MIDI variant was a late add-on to the existing codebase rather than a redesign.

Contemporary commentary (c64-music blog, 2009; Lemon64 forums) positioned it against Activision's **Music Studio**: both accomplished similar goals, but Music Shop targeted "the serious music composer" with a menu-driven, notation-based interface, while Music Studio used an icon-based approach.

### The player format (high-level; from Lemon64 forum RE thread)

The Music Shop's native data format (extension `.seq` on-disk) **stores the visual notation layout rather than raw pitch/duration data**: each symbol (quarter note, sharp, flat, position on staff, etc.) has its own bytecode, and the vertical placement of each symbol is encoded. This is a rendering-model format, not a semantic pitch-duration stream. It was designed to conserve space on the 170 KB C64 floppy; MIDI file compatibility was not a design goal. No public converter exists.

The fixed PSID layout ($A04D init, $575A play) is the program's runtime playback stub ripped in-place from the commercial binary. When the Music Shop software is running, it interprets this notation data and drives the SID chip. HVSC packagers captured this by taking the program + a loaded song and writing a PSID header pointing at the existing init/play vectors.

### Broderbund context

Brøderbund (founded 1980 by Doug and Gary Carlston) was at its peak commercial period in 1984, producing software for nearly all home computer platforms simultaneously. The Music Shop belongs to its non-game productivity/educational line alongside The Print Shop. The company is not traditionally associated with demoscene music tooling; Music Shop was sold in retail boxes. The Karateka connection (same publisher, same player engine) is notable: Francis Mechner reportedly composed the Karateka C64 soundtrack *using* The Music Shop, explaining why that SID file is tagged MusicShop in HVSC.

### Louis Ewens

Three SIDs credited to Louis Ewens under `MUSICIANS/E/Ewens_Louis/` carry the "1984 Brøderbund Software" release tag (Elephant Trot, Kajun Klog, Oogie Boogie). This strongly suggests Ewens was a Broderbund staff member or contractor who contributed additional demo songs that shipped with the product beyond Don Williams's 28 pieces. Note that "Kajun Klog" also appears as a DEMOS/UNKNOWN entry ("Kajun Klog 2") — likely a variant transcription.

### Mehdi Safavy

Twenty SIDs attributed to Mehdi Safavy (Iran), all undated (`19?? Mehdi Safavy`). The titles are in Farsi romanisation (Bedad, Elahe Naz, Esdahan, Fantezy, Gold Sleeps, Golnar, Golrokh, Happy, Iran, Kabory, Khatereh, Mahoor, Rang, Roomy, Sang Tarashoon, Sary Galeen, Shahr Ashoob, To Setoony, Zarby, Zohal). This is the only clearly non-European-origin user cluster in the HVSC MusicShop corpus, demonstrating the program's reach. The songlengths range from 12 s to 143 s, predominantly original compositions (no obvious Western pop covers in the Farsi titles).

---

## 8. Key Observations for Migration Planning

1. **Single fixed program layout (98.9%)**. The player is not relocatable; all 180 standard SIDs share init=$A04D, play=$575A. The migration will deal with one binary layout for the runtime, not a relocation family.

2. **No multi-subtune complexity** (for the 180 standard SIDs). All are n_subtunes=1. The one exception (Karateka, n=20) is at a different address and is effectively a different integration.

3. **No CIA tunes**. All VBL-timed (psid speed bit = 0 implied). Straightforward frame-based play() timing.

4. **PSID v2 throughout**. All 182 are PSID version 2.

5. **Data format is notation-visual, not pitch-duration semantic**. The `.seq` bytecode encodes staff symbols and vertical positions. This is the core RE challenge: extracting a semantically-equivalent musical description from a visual-layout encoding.

6. **The Don Williams 28 + Ewens 3 = 31 retail bundle songs** are well-identified, classically-oriented, and have known authorship. They form a clean reference set.

7. **The 121 UNKNOWN group** is user community content from the mid-to-late 1980s, primarily European with notable Polish and German-language content. Author attribution is lost. HVSC treats them as "demos" by convention.

8. **Karateka** (20 subtunes, $1000/$1003) may be the clearest case for a "Music Shop player relocated for game integration" and is the most technically complex member. Its 20 subtunes cover the full game OST.

---

## Leads to Follow

- **Manual scan for the data format**: the Archive.org user manual (`https://archive.org/stream/The_Music_Shop_Users_Manual`) reportedly documents the `.seq` file layout and note encoding. The sibling agent covering the data format should start here. The Lemon64 thread (t=45281) has a community RE of the `.seq` format ("three entries per column," symbol codes for each notation element, vertical placement bytes) that is a direct starting point.

- **Karateka's Music Shop integration**: how did Francis Mechner / Broderbund relocate the player to $1000 for game use? Jordan Mechner's published source archives and "The Making of Karateka" documentary (2025) may contain primary source material about the tool's role in Karateka's development. The Archive.org unprotected evaluation disk (`Karateka_Jordan_Mechner_Copy_1985-05-02`) may contain the pre-release music files.

- **CSDb entry #82453**: the CSDb entry returned by a direct fetch was a 1988 crack release by "Garcisoft Ltd." (Agent 16 / The Electronic Knights), NOT the original Broderbund product. This crack is presumably the propagation vector for most of the DEMOS/UNKNOWN content. Checking the crack's file list may reveal which demo songs were bundled.

- **Louis Ewens role**: was Ewens a Broderbund employee, or is the "1984 Brøderbund Software" release credit an HVSC convention? His three songs (Elephant Trot, Kajun Klog, Oogie Boogie) have a folk/ragtime character consistent with the bundled demo content.

- **Polish user cluster**: ~20 DEMOS/UNKNOWN entries have Polish titles (Bal w Przedszkolu, Baranek, Bialy Walczyk, Choinka, Ida Dzieci, etc.). This suggests a Polish C64 user scene that distributed Music Shop compositions through local channels. Whether there is a known Polish C64 community document cataloguing this is worth checking.

- **The Music Shop for MIDI (1985)**: Passport-co-published MIDI variant. Whether the `.seq` data format is identical between the MIDI and non-MIDI versions, and whether any HVSC SIDs originate from the MIDI version's player binary (which might differ in detail at the SID driver level), is unconfirmed.

- **Größenwarnsinnig Boulder Dash (1993, $7FF9)**: a 1993 fan BD variant at a non-standard address. How did the Music Shop player end up integrated into a fan game nine years after the original? Was the player stripped and relocated, or does the game embed a full Music Shop copy?

- **MobyGames entry**: not yet checked; may have boxart, release date confirmation, platform list, and developer credits. Search `mobygames.com "music shop" broderbund commodore`.
