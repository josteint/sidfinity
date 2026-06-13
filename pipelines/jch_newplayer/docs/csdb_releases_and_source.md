# JCH NewPlayer — CSDb releases, released player source & editor lineage

> **Provenance**
> - **source_url:** CSDb release pages (`csdb.dk/release/?id=…`) — see per-entry IDs below; CheeseCutter source on GitHub (`github.com/theyamo/CheeseCutter`); Internet Archive (`archive.org/details/d64_JCH_Editor_v3.04_19xx_Onslaught`); vintageisthenewold.com; pouet.net.
> - **fetched_via:** WebSearch + WebFetch (CSDb returned **HTTP 503 / Retry-After: 3600** to BOTH curl-with-Firefox-UA and WebFetch, and to the `noname.c64.org` mirror which 301-redirects to csdb.dk — so CSDb release notes here are reconstructed from search snippets + cross-source corroboration, NOT direct page reads). CheeseCutter source fetched via raw.githubusercontent.com (curl, Firefox UA) — **full source obtained**.
> - **fetch_date:** 2026-06-13
> - **author:** JCH (Jens-Christian Huus) / Vibrants; players maintained by Laxity (Vibrants) & Dane (Booze Design); CheeseCutter port by Abaddon (Fairlight).
> - **content_date:** editor 1988→2010s; CheeseCutter player asm `cc4.07` (man page Nov 2018); JCH-editor 3.1 + NP22-25 = 2010s.
> - **reliability:** HIGH for the CheeseCutter source listing (direct from repo). MEDIUM for CSDb release metadata (snippet-only, CSDb unreachable). HIGH for the existence/identity of the releases (multiple corroborating sources).

---

## 1. The actually-obtained player SOURCE — CheeseCutter `player_v4.acme`

**This is the single most useful artifact found.** The CheeseCutter v2 repo ships its C64 player as ACME-assembler source, and its header states it is a direct descendant of JCH's player:

```
;;; CCUTTER 2.x musicplayer by abad
;;; Based on JCH NP 21.G4 by Laxity/VIB
```

- **Repo:** https://github.com/theyamo/CheeseCutter (maintainer: theyamo; player by "abad" = Abaddon/Fairlight).
- **Player source:** `src/c64/player_v4.acme` (1763 lines, full ACME source — obtained in full this session).
- **Binary serializer (= on-disk table layout):** `src/ct/dump.d` — the function `dumpData(Song)` writes out, in order: `arp1, arp2, filttab(4-byte rows), pulstab(4-byte rows), inst0..inst7 (column-major, 48 stride), seqlo, seqhi, cmd1/cmd2/cmd3 (3×64), songsets (per-subtune: 3 track pointers + speed,7), track<i>_<voice> (order lists), s00..sNN (sequences), chord, chordindex`.
- **Data-structure source:** `src/ct/base.d` (1882 lines) — `Offsets` enum (file header/pointer layout), `NOTES` (C-0..B-7), constants (`MAX_SEQ_ROWS=0x40`, `MAX_SEQ_NUM=0x80`, `SEQ_END_MARK=0xbf`, `SUBTUNE_MAX=32`, `SONG_REVISION=12`), wave-table loop/relocation logic, order-list transpose/jump packing.
- **Player reference doc:** CheeseCutter ships none in-repo (the in-app help `src/ui/help.d` says *"Check out the player reference guide from the CheeseCutter homepage"* → http://theyamo.kapsi.fi/ccutter — that page returned **401** this session; mirror `theyamo.kapsi.fi/ccutter/oldsite/about.html` returned 401 too).

→ Full table layout, byte-field semantics, effect encodings, the per-frame `setsid` $D400-$D418 write order, and the PAL frequency table are all transcribed in **`csdb_codebase64_format_spec.md`** (§3, §6-§12) from this source. **Caveat:** CheeseCutter is a *reimplementation* of the NP21.G4 lineage; its in-RAM packing is its own (single-byte sequence tokens, `$BF` end-mark, 48 insts, column-major instrument table). JCH's own NP20/NP21 binaries (the HVSC majority) should be confirmed against a real binary — see leads.

`doc/ccutter.1` (man page, Nov 2018): CheeseCutter (C) 2009-17 Abaddon, GNU GPL; CLI flags only (SID model, filter preset, NTSC, playback freq) — no format detail. `ChangeLog` is a stub pointing to the homepage.

---

## 2. CSDb releases (player/editor/docs) — metadata

> CSDb was unreachable (503) all session; IDs + identities below are from search snippets and corroborating sources. **Verify the release notes directly when CSDb is back.**

| CSDb ID | Title | Group(s) | By | Date | Type | Notes |
|---|---|---|---|---|---|---|
| **165426** | **JCH NP20.g2 Docs by Deek** | — | Deek | — | Docs | Dedicated **NP20** documentation release. **HIGH-value** — likely the cleanest NP20-era format doc. Unread (CSDb down). |
| **100406** | **JCH-editor 3.1 + NP22-25** | Booze Design | **Dane** | 2010s | Tool | Editor 3.1 bundling **several players NP22/23/24/25**; documented raster-time-vs-flexibility tradeoff ("some players use little raster-time but are not that flexible; others have more options but use more time"); **comprehensive English manual included**. The successor to JCH's original editor. |
| **26563** | **JCH NewPlayer 21.g4 Final** | Maniacs of Noise + Vibrants | (Laxity/JCH) | 16 Jan 2006 | Tool | Final release of the NP21.G4 player line — the lineage CheeseCutter's `player_v4.acme` is based on. |
| **20112** | **JCH NewPlayer 21.g4 beta (21.b4)** | Maniacs of Noise + Vibrants | (Laxity/JCH) | 27 Aug 2005 | Tool | Beta of NP21.G4. |

**Search-derived facts (corroborated):**
- "JCH uses player NP20.g4" (the standard/default player).
- "Dane of Booze Design released a new version of the JCH editor … consists of several players … some use little raster-time but are not that flexible, others have more options but use more time … very comprehensive manual (English) included."
- NP21.G4 is co-credited Maniacs of Noise + Vibrants; the player code is by **Laxity/VIB** (per CheeseCutter header).

**Other releases to chase on CSDb (by name; IDs unknown):** the original **JCH Music Editor v1/v2/v3** (Vibrants, 1988+), **NewPlayer Tools** packers/converters (see §3 — Crescent), and any "JCH NewPlayer source" / "Vibrants" tool releases that include JCH's *native* asm.

---

## 3. NewPlayer Tools (pouet + CSDb) — packers/converters

**pouet.net/prod.php?which=61826 — "NewPlayer Tools" by Crescent, Sept 2013 (C64 demotool).**
User comments (verbatim):
- **Wisdom (2013-09-02):** *"This is a pack of tools for JCH's Music Editor. The depacker is integrated into the editor and allows you to load your old, packed tunes easily. It can also convert song data from one player to another. The packers are known to be quite robust."*
- **CHEF-KOCH (2013-09-02):** rated it excellent ("demotool (:rulez").
- **ɧ4ɾɗվ. (2013-09-03):** *"I still love JCHs tracker! Good additions there, nice job!"*

**Significance for the decompiler:** confirms (a) HVSC tunes exist in **packed** form (editor regions stripped) — so a parser must handle stripped tunes (no `$0E00`/`$0F00` blocks, rely on fingerprint), and (b) **cross-player conversion** existed — a single HVSC .sid may have been authored in one NP version and re-packed for another, so the player *binary* fingerprint (not the table data) is what identifies the runtime write model.

---

## 4. Editor / disk-image sources

- **Internet Archive: `d64_JCH_Editor_v3.04_19xx_Onslaught`** — D64 disk image (910 KB), JCH Editor v3.04 (Onslaught crack), uploaded 2021-03-09, VICE-runnable, 8 screenshots. Contains the editor + player binaries on-disk. **Download the .d64 and extract** to inspect a real native JCH player binary + any on-disk docs. (No text docs surfaced via the IA web page.)
- **vintageisthenewold.com/jch-editor-3-1-np22-25** — blog post mirroring CSDb id=100406 (Dane's editor 3.1 + NP22-25); confirms the multi-player bundle + English manual; links back to CSDb.
- **blog.chordian.net** (JCH's own site) — "From JCH's Special Collection" (2018) covers the *earliest* JCH Music Editor v1 (Nov 1988): *"No sequences, no instrument editor – just pure tracker notes"* — a single continuous note stream; sequences were added in a later major version. Confirms 3 major editor versions. (No NP-version format detail in that post.) JCH also runs **DeepSID** (deepsid.chordian.net) and authored **SID Factory II** (github.com/Chordian/sidfactory2), the modern successor with "drivers made by Laxity and JCH."

---

## 5. Lineage summary (who made what)

```
DMC (Demo Music Creator)  ──►  JCH Music Editor v1 (1988, JCH/Vibrants, no sequences)
                                     │
                                     ▼
                          JCH editor v2/v3 + NewPlayer NP17.G0 … NP20.G4 (standard) / NP20.Q0 (multispeed)
                                     │  (player code: JCH, later Laxity/Vibrants)
                                     ▼
                          NP21.G4-G6  (Laxity/VIB; Maniacs of Noise + Vibrants, 2005-06)
                                     │
                ┌────────────────────┼─────────────────────────────┐
                ▼                    ▼                             ▼
   CheeseCutter (Abaddon/FLT,   JCH-editor 3.1 + NP22-25      SID Factory II
   open-source port,            (Dane/Booze Design,           (JCH/Chordian, modern,
   player_v4.acme "based on     multi-player bundle +         "driver 11" = NP-style,
   JCH NP21.G4 by Laxity/VIB")  English manual)               divergent re-encoding)
```

- **HVSC population:** ~3,611 JCH NewPlayer tunes (SIDId reports **21 distinct signature variants**: V1-V20, V0x, plus a `Dane_NewPlayer` variant). The bulk are NP17-NP21 era authored in JCH's/Vibrants' editor; some NP22-25 (Dane). Fingerprint the player binary to pick the correct table-layout + write-model branch.

---

## Leads to follow

- **CSDb (re-fetch when 503 clears — Retry-After was 3600s):**
  - `id=165426` "JCH NP20.g2 Docs by Deek" — pull in full; cleanest NP20 format doc.
  - `id=100406` JCH-editor 3.1 + NP22-25 — get the **English manual** (definitive NP22-25 player-difference + multispeed reference).
  - `id=26563` / `id=20112` (NP21.G4 final/beta) — release notes + whether the **original Laxity/Vibrants asm source** is attached as a downloadable.
  - Search CSDb for "JCH Music Editor" / "Vibrants" tool releases that bundle **JCH's native NewPlayer asm source** (the ground-truth packing for HVSC binaries, vs CheeseCutter's reimplementation).
- **Internet Archive D64** (`d64_JCH_Editor_v3.04_19xx_Onslaught`) — download + cbmdisk-extract; dump a native NP player binary and diff its table layout against CheeseCutter's `player_v4.acme` to nail JCH-native vs CC-port packing differences.
- **theyamo.kapsi.fi/ccutter** "player reference guide" — currently 401; retry / find a mirror (web.archive.org). It's the doc CheeseCutter's in-app help points to for the format.
- **SID Factory II** driver sources + manual (github.com/Chordian/sidfactory2, files.chordian.net/sf2/) — for confirming effect *semantics* by JCH himself (not for the HVSC binary layout; its driver 11 uses flag-byte instruments, a re-encoding).
- Identify the **SIDId fingerprints** for each NP variant (21 of them) and map to the table-layout/write-model branch table in `csdb_codebase64_format_spec.md` §13 before extraction.
