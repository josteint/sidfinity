# GoatTracker V1 research — provenance log

Wave 1: 2026-06-29 (`research-player`, 5 leaf agents on sonnet).

| Source | Status | Notes |
|---|---|---|
| `deprecated/gt2_pipeline/GoatTracker_2.77/src/gsong.c` (local) | ✅ read | GT2's GTS! importer (lines ~329-806) — PRIMARY decode of every V1 byte. |
| `deprecated/gt2_pipeline/GoatTracker_2.*/src/` (local) | ✅ read | GTS! loader cross-checked across versions; sngspli2.c orderlist encoding. |
| `cadaver.github.io/tools/goattrk.zip` | ✅ fetched | GoatTracker V1.53 (latest V1, 2006) → player1/player2/gmusic .s + readme_153. |
| `cadaver.github.io/tools/goatold.zip` | ✅ fetched | GoatTracker V1.25 (2002) → player1_125/player2_125 .s + readme_125. |
| `archive.org/download/goattrk_zip/goattrk.zip` | ✅ fetched | V1.52 archive copy (corroboration). |
| `cadaver.github.io/tools.html`, `.../rants/music.html` | ✅ fetched | Cadaver tool list + music-routine notes. |
| `csdb.dk` (Cadaver scener / V1.25 release id=6072) | ✅ fetched | Version history, format lineage. |
| `deprecated/gt2_pipeline/tools/sidid.cfg` (local) | ✅ read | V1.x + GT_V1.4_2SID + GT_V1.5_2SID signatures. |
| Codebase64 / Lemon64 / pouet (forums) | ✅ searched | Mostly corroborated readmes; little net-new V1 detail. |
| `web.archive.org` Wayback (direct WebFetch) | ❌ blocked | WebFetch errored on web.archive.org; live cadaver.github.io served current versions. |
| `cadaver.github.io/tools/gstereo.zip` | ⏭ not fetched | Stereo/2SID variant — out of scope (12 tunes, exclude). |
| `github.com/Chordian/sidfactory2` GT V1 importer | ⏭ lead | Not chased — GT2 gsong.c + V1 source already authoritative. |

Holy grail obtained (player source + manuals + GT2 importer) → no second wave.
