---
source_url: multiple (see per-section citations)
fetched_via: WebSearch + WebFetch
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: primary (negative finding — no SongSmith-specific parsers found)
---

# GitHub + Open-Source Parser / Converter Search for Loadstar SongSmith

## Summary Verdict

**No GitHub repository, open-source tool, or interactive disassembler provides a parser,
decompiler, or converter specifically for the Loadstar SongSmith format.**
The format has no public implementation outside of the original binary on the
`Songsmith-Loadstar.d64` disk image (CSDb release id=122855).

---

## 1. Direct GitHub Searches

### Query: "SongSmith" C64 SID parser converter
- Source: https://github.com/search?q=SongSmith+C64
- **Result: Zero relevant hits.** The name "SongSmith" on GitHub is dominated by
  Microsoft Research Songsmith (an entirely unrelated modern AI music tool).
  No C64-specific SongSmith repository exists.

### Query: site:github.com "SongSmith" OR "loadstar_songsmith" C64 music
- **Result: Zero hits** for any C64 SongSmith repository.
  The only Loadstar-related GitHub results are:
  - `ZeratuLx/C64-music` — general C64 music in BASIC/other tools; no SongSmith.
  - `MartinGalway/C64_music` — 1980s game music sources; no SongSmith.
  - General sidplay/player repos with no SongSmith handling.

---

## 2. SIDFactory II (Chordian/sidfactory2)
- URL: https://github.com/Chordian/sidfactory2
- **Importers present:** GoatTracker, CheeseCutter, MOD/SNG files.
- **SongSmith: NOT supported.** No mention in changelog, README, or issues.
- Source: https://github.com/Chordian/sidfactory2 (fetched 2026-06-14)

---

## 3. ChiptuneSAK (c64cryptoboy/ChiptuneSAK)
- URL: https://github.com/c64cryptoboy/ChiptuneSAK
- **Current importers:** MIDI, PSID/RSID SID files, GoatTracker 2, GoatTracker 2 Stereo.
- **Proposed (not implemented):** COMPUTE!'s Sidplayer MUS format is listed as a
  proposed future importer — but this is the Chamberlain MUS format, not SongSmith.
- **SongSmith: NOT listed** even as proposed.
- Source: https://chiptunesak.readthedocs.io/en/latest/sid.html (fetched 2026-06-14)

---

## 4. desidulate (anarkiwi/desidulate)
- URL: https://github.com/anarkiwi/desidulate
- Tools for analyzing C64 SID music using VICE SID register dumps.
- Works at the register-log level (engine-agnostic). No SongSmith-specific code.
- Source: https://github.com/anarkiwi/desidulate (fetched 2026-06-14)

---

## 5. sidtool (olefriis/sidtool)
- URL: https://github.com/olefriis/sidtool
- Converts SID files to MIDI. 6502 emulation-based (engine-agnostic).
- No SongSmith-specific handling.

---

## 6. c64_6581_sid_players (realdmx)
- URL: https://github.com/realdmx/c64_6581_sid_players
- Original + reverse-engineered player sources for Hubbard, Galway, Tel, etc.
- **SongSmith: NOT included.** Directory listing confirms only major commercial
  game composers (Hubbard, Galway, Gray, Tel, etc.).
- Source: https://github.com/realdmx/c64_6581_sid_players (fetched 2026-06-14)

---

## 7. ComputeSidPlayerC64Source (MyDeveloperThoughts)
- URL: https://github.com/MyDeveloperThoughts/ComputeSidPlayerC64Source
- Disassembled Kick Assembler source code of COMPUTE!'s Enhanced Sidplayer.
- This is the **Chamberlain MUS-format player**, NOT SongSmith.
- Contains detailed MUS file format documentation (see github_sidplayer_mus_format.md).
- **No SongSmith handling** — this is a completely separate engine.
- Source: https://github.com/MyDeveloperThoughts/ComputeSidPlayerC64Source (fetched 2026-06-14)

---

## 8. player-id (WilfredC64/player-id)
- URL: https://github.com/WilfredC64/player-id
- Rust reimplementation of cadaver's sidid C64 player-identification tool.
- Uses `config/sidid.cfg` — a signature database that **includes all four
  Loadstar_SongSmith variants** (v1, v2, v3, unversioned).
- This is an IDENTIFIER, not a parser/decompiler. It reports "this SID uses
  SongSmith" but cannot extract note/instrument data.
- Contributors: Wilfred Bos, iAN CooG, Professor Chaos, Cadaver, Ninja, Ice00, Yodelking.
- Source: https://github.com/WilfredC64/player-id (fetched 2026-06-14)

---

## 9. cadaver/sidid
- URL: https://github.com/cadaver/sidid
- The canonical C64 playroutine identity scanner.
- `sidid.cfg` contains all four Loadstar_SongSmith signatures.
- `sidid.nfo` references CSDb release id=122855 as the Songsmith provenance record.
- Again: identifier only, not a format parser.
- Source: https://github.com/cadaver/sidid (fetched 2026-06-14)

---

## 10. HVSC Count (from hvsc84.db)

| sidid Engine Tag | SID Count |
|---|---|
| Loadstar_SongSmith | 308 |
| Loadstar_SongSmith_v1 | 19 |
| Loadstar_SongSmith_v3 | 3 |
| Loadstar_SongSmith_v2 | 1 |
| Song_Writer (related?) | 6 |
| **Total** | **337** |

SIDs span 15 musician directory groups. Heaviest cluster: MUSICIANS/O (Mario Oropesa,
many classical transcriptions). Song_Writer entries are all by Jeremy Thorne
(`MUSICIANS/T/Thorne_Jeremy/Song_Writer-*.sid`) — possibly a different editor
or an earlier Loadstar precursor tool, but shares the "song writer" conceptual space.

---

## Leads to Follow

1. **The CSDb D64 binary** at `http://csdb.dk/getinternalfile.php/121491/Songsmith-Loadstar.d64`
   is the only known source of the player code and editor. Fetch + mount in VICE for RE.
2. **ChiptuneSAK's proposed MUS importer** — if ever implemented, it would provide
   a model for parsing a similar (but distinct) C64 data-driven music format. Watch
   https://github.com/c64cryptoboy/ChiptuneSAK for MUS-format PRs.
3. **Song_Writer (Jeremy Thorne)** — check if this is the Joe Garrett / Alan Gardner
   precursor tool from Loadstar issues 27-28 (referenced in comp.sys.cbm Loadstar #168
   thread). sidid may have a separate entry for it. OPEN.
4. **Loadstar archive on Archive.org** — `https://archive.org/details/loadstar_disk`
   has 331 disk images. Mounting them in VICE or c1541 could surface the SongSmith
   program in its original context (editor + manual text + jukebox player).
