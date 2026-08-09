# Provenance log — OdinTracker research sweep (2026-06-15)

Every URL/source attempted, so future waves don't re-fetch.
Status: ✅ fetched & saved · 📄 read only · ⚠️ partial/blocked · ❌ failed · 🔜 lead (not chased — migration phase)

## Fetched & saved (primary — the player source)
- ✅ `OdinTracker113src.zip` — CSDb #2628 getinternalfile.php/154684 + zimmers.net mirror → unzipped to `tmp/odintracker_research/`; full DASM source copied to `docs/src/`: `vplayer.s`, `defines.s`, `eplayer.s`, `tracker.s`, `help.txt`/`help/help.in`, `HISTORY.txt`, `freqtab/freqtab.cpp`, `vibrato/vibrato.s`, `c64pack/depacker.s`, `README`, `file_id.diz`
- ✅ `Odin_Tracker_100.zip` — CSDb #12577 (v1.00, binary + monolithic `tracker.s`) → `tmp/`; v1.00 memory-map header → `src/tracker_v100_header.s`
- ✅ v1.12 HISTORY → `src/HISTORY_v112.txt`

## Fetched & saved (analysis / secondary)
- ✅ CSDb release pages — all 8 versions (v1.00..v1.13) IDs/dates/download URLs → `csdb_releases.md`, `github_odintracker_csdb_release.md`, `src/archive_csdb_odintracker_113.md`
- ✅ https://github.com/cadaver/sidid (`sidid.cfg`) — canonical OdinTracker signature (corrects local `C0 0F` → `29 0F`) → `sidid_signature.md`, `src/github_sidid_signature.md`
- ✅ Wayback `http://www.inf.bme.hu/~zed/tracker/` (50+ snapshots, June 2001) — intro/news/faq/history/future/download/songs/source pages → `src/archive_zed_homepage_wayback.md`, `src/archive_odintracker_faq.md`, `src/archive_odintracker_changelog.md`, `src/archive_odintracker_songs_page.md`, `src/archive_odintracker_help_manual.md`, `src/archive_odintracker_format_defines.md`, `src/archive_odintracker_player_internals.md`
- ✅ Lemon64 thread t=55408 (Monk collab — slidearps, speed-cmd incompatibility) → `forum_lemon64_c64_amiga.md`
- ✅ comp.sys.cbm Usenet (3 threads 2000–2002) → `forum_usenet_comp_sys_cbm.md`
- ✅ ChipFlip 2009 SounDemoN interview → `forum_chipmusic_soundemon_interview.md`
- ✅ HVMEC / woolyss listings → `article_hvmec_and_web.md`
- 📄 local `deprecated/gt2_pipeline/tools/sidid.cfg`, `hvsc85/DOCUMENTS/*` (grep: zero OdinTracker mentions), `hvsc84.db` (read-only corpus census) → `hvsc_corpus.md`, `csdb_hvsc_corpus.md`

## Negative results (confirmed absent — don't re-search)
- ❌ No GitHub repo for OdinTracker (Zed never published there)
- ❌ No third-party parser (libsidplayfp/VICE/DeepSID/SF2/GoatTracker/CheeseCutter — all generic PSID)
- ❌ No Codebase64 article, no chordian.net comparison entry, no sidpreservation.6581.org entry
- ❌ No scene-magazine article (Vandalism/Domination/Hugi/Attitude/etc.)
- ⚠️ web.archive.org intermittently blocked via WebFetch; recovered via direct/CDX
- ⚠️ narkive comp.sys.cbm mirror returned 503

## Leads NOT chased — migration phase / optional (out of research scope)
- 🔜 Dat2Sid v1.4 win32 (Wayback: …/download/dat2sid-1.4-win32.zip) — PSID-wrapping convention; only needed if rebuilding the wrap
- 🔜 Wayback song `.prg` corpus (`songs/10x/`, `songs/11x/`) — binary format-validation examples for the extractor
- 🔜 `tracker.s` packer section (savetables/savetracks, ~lines 3416–3500 / 5650–6250) — exact packed-binary serialization order (read at migration time; it's already in-tree)
- 🔜 `freqtab/freqtab.cpp` — extract the generated freq table + the v1.12 PAL tuning fix for cross-check
- 🔜 CSDb `OdinPack V1.2` (#153113) — standalone packer/PSID utility; purpose unconfirmed
- 🔜 v1.01–1.03 binary zips — HISTORY files only; confirm v1.0x format details if any v1.0x SIDs found
