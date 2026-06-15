# Provenance log — Reflextracker research sweep (2026-06-15)

Every URL/source attempted, so future waves don't re-fetch.
Status: ✅ fetched & saved · 📄 read only · ⚠️ partial/blocked · ❌ failed/absent · 🔜 lead (not chased — migration phase)

## Fetched & saved (primary — the tool + player + format)
- ✅ CSDb #43348 Reflex-Tracker V1.1 — both download zips + c64.rulez.org mirror → `tmp/reflextracker_research/`; D64 images (side1 tracker+player+drivers+demo songs, side2 54 samples)
- ✅ `RFXT PLAYER V1.1` (2048 B, $C000) → `src/RFXT_PLAYER_V1.1.prg` + annotated disasm `src/disasm_rfxt_player.md`
- ✅ `BESCHREIBUNG` German manual (28 KB) → `src/BESCHREIBUNG.prg`; decoded → `beschreibung_translation.md`, `beschreibung_german_manual.md`
- ✅ RFX1 demo modules → `src/MOD.TRANCE202.prg`, `src/MOD.ENDLOSCHOOR.prg` (+ Access2/B in tmp)
- ✅ Disk directory + format synthesis → `player_format.md` (canonical), `format_analysis.md`, `disk_contents.md`, `disk_contents_and_format.md`, `src/module_format.md`, `src/player_architecture.md`

## Fetched & saved (secondary)
- ✅ `github.com/cadaver/sidid` signature (matches local; no version split) → `sidid_signature.md`, `sidid_analysis.md`, `player_signature_and_hvsc.md`, `src/sidid_signature.md`
- ✅ CSDb release/scener pages (kb #655, Quiss #844, PVCF #836, Zorc #3677, Reflex group #3; related LSD #118872, Brainbeat) → `csdb_release_43348.md`, `csdb_sceners.md`, `csdb_related_releases.md`, `csdb_and_scene_sources.md`
- ✅ Lemon64 thread #4872 + #31273 (PVCF technical quotes; iAN CooG digi-tracker classification) → `csdb_lemon64_thread_4872.md`, `forum_lemon64_trackers_with_digi.md`
- ✅ Pouet #59064 ("2 channel digi tracker") → `csdb_pouet_notes.md`, `pouet_and_scene_notes.md`
- ✅ North Party 10 (2006) Reflextracker compo report; Remix64 HVSC-collector notes → `forum_north_party_10_report.md`, `forum_hvsc_collector_notes.md`, `forum_scene_spread_and_competition_history.md`, `forum_csdb_comments_compilation.md`
- ✅ kb author profile / 2014 interview (no Reflextracker mention; TinySID author) → `wiki_kb_author_profile.md`, `github_author_search.md`, `author_sites_and_releases.md`
- ✅ QuadSID/multi-SID context (MIDI-only, 0 in HVSC) → `wiki_quadsid_and_multi_sid_context.md`
- ✅ Wayback CDX for reflex-studio.de / kebby.org / quiss.org; Brainbeat 3 (1994, "FTRAC V1") → `archive_wayback_and_scene_mirrors.md`, `archive_brainbeat3_1994.md`
- 📄 local `hvsc84/DOCUMENTS/*` (STIL: 5 PVCF technical notes — "2 channel sampletracker" etc.; no other hits), `deprecated/gt2_pipeline/tools/sidid.cfg`, `hvsc84.db` (read-only census) → `stil_notes.md`, `hvsc_corpus_census.md`, `hvsc_sid_layout.md`

## Negative results (confirmed absent — don't re-search)
- ❌ No tracker/player SOURCE anywhere (GitHub kebby/matthiaskramm/quiss.org — none; predates GitHub, DOS-era)
- ❌ No third-party parser (libsidplayfp/VICE/DeepSID); no JC64dis example (.dis) for Reflextracker
- ❌ No QuadSID/multi-SID .sid in HVSC (MIDI-only export)
- ❌ No comp.sys.cbm Usenet posts (circulated via disk-swap, not Usenet)

## Leads NOT chased — migration phase / optional (out of research scope)
- 🔜 Decode RFX1 internal byte layout (instrument/sample table + pattern stream offsets) on `src/MOD.*.prg`
- 🔜 Verify ~6702 Hz CIA rate + the init SMC sample-rate patch ($F2CF note→period sub) — the Mode-2 timing crux
- 🔜 Insider #6 (Reflex diskmag) ch.10 "TRACKERINSTR." = English manual — mount in VICE
- 🔜 Brainbeat 4 side B + Polish North-Party competition disks — more RFX1 modules; LSD (1997) as format cross-ref
- 🔜 PVCF / CJ Warlock (CSDb) for the original distribution disk + reflex-studio.com Wayback content
- 🔜 The $C050 init-variant group + the $1C06 relocated outlier (Jonny/Future_Come.sid) — player-build variants
