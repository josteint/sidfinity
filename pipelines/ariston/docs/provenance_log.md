# Provenance log — Ariston research sweep (2026-06-15)

Every URL/source attempted, so future waves don't re-fetch.
Status: ✅ fetched & saved · 📄 read only · ⚠️ partial/blocked · ❌ failed/absent · 🔜 lead (not chased — migration phase)

## Fetched & saved (primary — the format)
- ✅ JC64dis repo `github.com/ice00/jc64` → cloned to `tmp/ariston_research/jc64/`; `doc/example/Ariston.dis` = annotated disassembly project of Beben's *Dark Side* (by Stefano Tognon). Decoded → `src/archive_jc64dis_disassembly.md`, `src/archive_format_summary.md`; project preserved → `src/jc64dis_DarkSide_project.dis.gz`
- ✅ CSDb #29914 `ariston_illusion.d64` + #119920 `ariston_cic.d64` → `tmp/`; editor PRG + embedded credit/UI strings → `csdb_binary_analysis.md`, `csdb_editor_ui_strings.md`
- ✅ `github.com/cadaver/sidid` (`sidid.cfg`/`sidid.nfo`) → cloned `tmp/ariston_research/sidid/`; 4 sub-signatures verbatim + decoded → `sidid_signature_analysis.md`, `disasm_sidid_signatures.md`, `archive_sidid_fingerprints.md`, `github_cadaver_sidid.md` (incl. 132/147 Beben-sig census)

## Fetched & saved (secondary)
- ✅ VGMPF wiki — Ariston, Ian_Crabtree, Wally_Beben + composer pages (Leitch/Dunn/Brimble/Gray/Barrett) → `wiki_vgmpf_ariston.md`, `csdb_vgmpf_ariston.md`, `article_vgmpf_ariston.md`, `src/archive_vgmpf_ariston.md`, `wiki_vgmpf_composers.md` (REDUNDANT set — `archive_format_summary.md` + `engine_overview.md` are canonical)
- ✅ CSDb release/scener pages (#29914, #119920, #23212; Beben profile; Crabtree SID entries) → `csdb_releases.md`, `csdb_sceners.md`, `csdb_composer_games.md`, `csdb_corpus_analysis.md`, `wiki_csdb_ariston_editor.md`, `article_csdb_releases.md`
- ✅ Composer testimony (Brimble/Gray/Leitch/Dunn/Barrett interviews — "typed notes in assembler") → `composer_testimony.md`, `forum_composers_interviews.md`
- ✅ Atari-Forum t=21588 (Mug UK 2004 R-Type ST RE; Beben source lost) → `csdb_atari_forum.md`, `forum_atari_beben_driver.md`, `atari_st_amiga_port.md`, `article_st_amiga_port.md`, `src/archive_atari_amiga_port.md`
- ✅ Recollection "brief history of SID" (single Ariston mention) → `article_recollection_brief_history_sid.md`
- 📄 local `deprecated/gt2_pipeline/tools/sidid.cfg`, `hvsc85/DOCUMENTS/*` (STIL: only the name-origin note on RoboCop; no technical comments), `hvsc84.db` (read-only census) → `hvsc_corpus_census.md`, `article_hvsc_corpus.md`

## Negative results (confirmed absent — don't re-search)
- ❌ No GitHub repo with Ariston SOURCE; no published plain-text C64 disassembly (only the JC64dis project)
- ❌ No third-party parser (libsidplayfp/VICE/DeepSID); no DeepSID-specific label beyond sidid
- ❌ No Pouet productions; no magazine review/scan (semi-private commercial driver, not in Zzap!64)
- ❌ Original source LOST (Beben HDD failure, incl. ST/Amiga port)

## Leads NOT chased — migration phase / optional (out of research scope)
- 🔜 Run JC64dis / `seed_disassembly.py` on a Crabtree **V1** (`Outrun.sid`, `Angel_Meadows.sid`) + **V2** tune to map those variants vs the Beben spec
- 🔜 Resolve VOL = $FC vs $FD ambiguity on the binary
- 🔜 Atari-Forum locked attachments (`R_TYPE.W_B.zip` Mug-UK ST RE; "Xerud Beben rips") — login-gated; a 2nd independent engine copy (68k)
- 🔜 SNDH archive `sndh.atari.org` — Beben ST replayers (YM-adapted copy of the engine); AtariMania lists 72 Beben ST games
- 🔜 Run the cracked editor D64s in VICE to observe the editor UI / dump player at $0801
- 🔜 Contact living composer Wally Beben (ran "Sounds Digital" BBS, Thetford)
- 🔜 Verify VGMPF's "Charles Deenen contributed to Ariston" (likely a cataloguing error)
