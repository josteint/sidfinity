# Provenance log — Vibrants/Laxity research sweep (2026-06-15)

Every URL/source attempted during the `research-player` sweep, so future waves don't re-fetch.
Status: ✅ fetched & saved · 📄 read only · ⚠️ partial/blocked · ❌ failed · 🔜 lead (not chased — RE/migration phase)

## Fetched & saved (primary)
- ✅ https://github.com/Chordian/sidfactory2 — cloned to `tmp/.../sidfactory2/`; C++ parser + driver notes → `github_sf2_driver.md`, `src/sf2_*.cpp/.h`, `src/sf2_notes_driver11..16.txt`
- ✅ chordian.net JCH C64 Editor v3.04 package (`jch_c64.zip`) → `src/jch_editor37_source.txt` (ED37_SRC, 96KB), `src/jch_np20g4_full_instructions.txt`, `src/jch_np15g6_full_instructions.txt`, `src/jch_ed3_keyguide.txt`, ed_texts/*, d64_files/*
- ✅ CSDb #101622 `SRC_JCH_Glover.zip` → `src/jch_np21g4_source_glover.txt`, `src/jch_np21g5_source_glover.txt`, `src/jch_np21g6_glover_notes.txt`
- ✅ CheeseCutter player source (NP21.G4-based) → `src/cheesecutter_player_v4.acme`, `src/disasm_cheesecutter_player_v4_annotations.md`
- ✅ zimmers.net `/pub/cbm/c64/audio/Vibrants/laxity_orig/` → `src/laxity_orig_dat/*.DAT` + README (authentic original-Laxity 1988 data)
- ✅ CSDb #39519 SID Factory 0.5 docs → `src/laxity_sf05_driver5_docs.txt`, `src/laxity_sf05_driver6_docs.txt`, `archive_sidfactory05_alpha_drivers.md`
- ✅ CSDb #210571 SID Factory II / drivers 11–16 → `archive_sidfactory2_drivers.md`
- 📄 local `deprecated/gt2_pipeline/tools/sidid.cfg` — all 12 family signatures → `sidid_signatures.md`, `sidid_opcode_analysis.md`, `forum_sidid_signatures.md`, `csdb_player_detection.md`
- ✅ https://github.com/cadaver/sidid (`sidid.nfo`) → `wiki_sidid_nfo_authorship.md` (confirms Vibrants/JO = Poul-Jesper Olsen, distinct)
- ✅ https://blog.chordian.net/computer-timeline/ → `wiki_chordian_jch_timeline.md`, `external_sources.md`
- ✅ https://blog.chordian.net/ SF2 sequence/instrument tutorials → `forum_sidfactory2_blog_instruments.md`
- ✅ Codebase64 JCH 20.G4 file-format article → `wiki_codebase64_jch20g4_format.md`, `src/article_codebase64_jch20g4_format.md`
- ✅ CSDb #122333 (Laxity Editor v/32-3.34), #142168 (v/34-3.35), #215790 (TFA v3.24), #26563 (NP21.G4), #100406 (NP22-25/Dane) → `csdb_release_notes.md`, `csdb_version_history.md`, `forum_csdb_laxity_editor_releases.md`
- ✅ sidpreservation.6581.org tracker entry → `wiki_sidpreservation_tracker_entry.md`
- 📄 local `hvsc84/DOCUMENTS/*` (grep Laxity/Vibrants/JCH; STIL.txt) → no technical comments found; counts → `hvsc_engine_taxonomy.md`

## Partial / blocked
- ⚠️ SF2 User Manual PDF (files.chordian.net/sf2/…User_Manual.pdf) — only pp.1–12 read; Danish intro content; pp.13+ per-driver byte detail NOT extracted
- ⚠️ DeepSID player-detection tab — JS-rendered; WebFetch got generic content only (would need a browser)
- ⚠️ laxity.c64.org — TLS error, not fetched (`tmp/.../laxity_homepage.html` is a partial)
- ❌ archive.org `jch_c64.zip` direct download returned 0 bytes (chordian.net mirror used instead)

## Leads NOT chased — belong to migration/RE phase (out of research scope)
- 🔜 `tmp/.../jch_editor_zip/d64_files/JCH_SRC.D64` — v17/v19/v20.G4 player source + NP-Packer v5.3 (disassembly/extraction = RE)
- 🔜 `Laxity_Editor_V32-3_34.d64`, `TFA_Editor_3_24.d64` (downloaded) — contain the original player binary; extracting it is RE
- 🔜 zimmers `3x-player/3xplayer.prg` (97 bytes) — compact original-player dispatch stub; disassembly = RE
- 🔜 decode `src/laxity_orig_dat/*.DAT` byte layout — the original data format; RE
- 🔜 CSDb #14037 `v-c64ed.zip` (older NP12/14/17 sources + packer); #100406 `NP22-25 docs.doc`; #66496 RAM-X Toolcollection (editor binary); #152993 Laxity 2017 "Memory+Editor"
- 🔜 Usenet comp.sys.cbm (Google Groups) 1989–1993 — not surfaced via web search; low expected yield
- 🔜 Frantic's "Beginner's Guide to the JCH Editor" PDF / DisC=overy #1 (Pappalardo) — newcomer guides, low byte-level yield
