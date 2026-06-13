# Provenance log — RoMuzak research

Every URL/source attempted during the 2026-06-13/14 sweep. ✅ fetched · ⚠️ partial ·
❌ failed/unavailable · ⏭ identified but deferred (RE / binary).

## CSDb (csdb.dk)
- ✅ release #17814 (RoMuzak V6.3, 1989), #17819 (RoMuzak V7.96, 1990-03-15) —
  pages, comments, credits, download links
- ✅ ROM scener page (#10213/#10214), Digital Marketing publisher context
- ✅ **`csdb.dk/getinternalfile.php/36832/vacsid.zip`** (416 KB) — contained the
  prize: **ROMUZAK.DOC** (29.9 KB German editor manual, V6.2+V7.9x) →
  `src/romuzak_doc_vacsid_bundle.txt`; also VACUUM.NFO + a Mekka-prerelease
  VACSID.DOC → `src/vacuum_nfo_mekka_prerelease.txt`
- ✅ `csdb.dk/...vsid159.zip` — VACSID.DOC V1.59 → `src/vacsid_v159_doc.txt`
- ✅ ROM's Fix (companion SFX editor), Converter/standalone-player releases

## sidid / player-ID (GitHub)
- ✅ `github.com/cadaver/sidid` + `github.com/WilfredC64/player-id` — RoMuzak_V6.x
  + RoMuzak_V7.x signatures (note-dispatch routine) → `src/sidid_romuzak_blocks.txt`
- ✅ surveyed DeepSID, libsidplayfp, JSIDPlay2, OpenMPT, NostalgicPlayer — NO
  RoMuzak format handler anywhere (generic PSID playback only)

## Future Composer cross-reference (local)
- ✅ local read of `pipelines/future_composer/docs/` (research.md, README.md,
  csdb_format_inferences.md, csdb_fc_editor_binaries.md, wiki_fc_v41_manual.md,
  github_fc14_amiga_spec.md) — to bound RoMuzak's data model from the FC V1.0 side
- Note: relevant FC = **C64 Future Composer V1.0 / "0.18"** (Finnish Gold 1988),
  NOT the Amiga Hippel FC14 (`SMOD`/`FC14` big-endian) in OpenMPT's Load_fc.cpp

## Archive.org / German scene
- ✅ `archive.org/details/d64_Romuzak_Music_Demo-Editor_1989_ACT_501` +
  `..._Analyser-Play_Construction_Kit_...` — two editor D64 images located (PRG
  extraction = RE phase)
- ✅ ASM (Aktueller Software Markt) 7/89 — DM/X-Ample relationship (article PDF located)
- ❌ web.archive.org — WebFetch blocked all session; some pages reached via curl
- ✅ Blasnik author trail: Bingen am Rhein, VacSID w/ Simon Kissel (SCAMP),
  DM game catalogue (Hydrogenese, Bamboo, Logo, Twintris)

## Forums / diskmags
- ⚠️ **c64scene.pl/viewtopic.php?t=112** (skull's 2009 V6.3 disasm, Polish) —
  fetched via WebFetch (summarised, not verbatim); per-voice structure + ~20
  raster/channel + copyright-validation routine captured, but **no hex addresses
  preserved** → OPEN: re-`curl` for verbatim post text
- ⚠️ Forum64.de thread #15654 "Romuzak" — HTTP 403 direct; Google snippet only
- ✅ VGMPF (ROM's Fix, known V6.3 first-note-mute bug), Lemon64/STIL, Remix64
- ❌ Codebase64, chipmusic.org, Usenet comp.sys.cbm, 64'er Magazin (not text-searchable) — no RoMuzak technical content

## Local
- read-only `hvsc84.db` — 569 RoMuzak_V6.x + 22 RoMuzak_V7.x
- `tools/sidid.cfg` / `src/sidid.py` — NOT present in this repo
- HVSC `DOCUMENTS/` — no RoMuzak-specific doc

## Deferred to RE (binaries / images already locatable)
- ⏭ V6.3 player disasm from HVSC SIDs → numeric sector-command dispatch bytes,
  exact effect register formulas, copyright-validation address
- ⏭ Editor D64 images (archive.org) — extract PRG for the song-data writer/format
- ⏭ verbatim c64scene.pl skull post (curl) for any hex addresses
