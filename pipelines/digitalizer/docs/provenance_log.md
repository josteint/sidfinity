# Provenance log — Digitalizer research

Every URL/source attempted during the 2026-06-13 sweep. ✅ fetched · ⚠️ partial ·
❌ failed/unavailable · ⏭ identified but deferred (RE / binary).

## CSDb (csdb.dk)
- ✅ release #33646 (Digitalizer V2.2, 1989), #33647 (V2.5), #108478 (V2.7),
  #33648 (V2.8, 1991), #33649 (V3.0, 1992), #33650 (V3.5, 1995) — pages, comments,
  download links, credits
- ✅ release #237762 (DTZ2SDI — Digitalizer V3.x → SDI converter) — provenance
  (binary credits "DJ GRUBY / TRIAD 2023"; CSDb lists 6R6/SHAPE)
- ✅ release #179618 (SteinTronic / Prosonix Music Editor, Stein Pedersen) — ancestor
- ✅ V3.0 help zip `csdb.dk/getinternalfile.php/118523/Digitalizer-2.9(ff) v3.0.zip`
  → `src/digitalizer_v3.0_instructions.txt` (the only surviving official doc)
- ✅ CSDb forum threads for V3.5 (4 posts — non-technical) + Recollection #2 interview excerpt
- ✅ CSDb webservice / scener pages: Olav Mørkrid, Panoramic Designs, Blues Muz', GRG, Kjell Nordbø

## sidid / player-ID (GitHub)
- ✅ `github.com/cadaver/sidid` `sidid.cfg` — Digitalizer_V2.x, Digitalizer_V3.0,
  Olav_Moerkrid, OmegaSupreme_Digi, Panorama, Prosonix/Prosonix_new/Prosonix_tiny
- ✅ `github.com/WilfredC64/player-id` — second Olav_Moerkrid variant (sentinel $FF)
  → both saved verbatim to `src/sidid_signatures_raw.txt`
- ✅ surveyed: libsidplayfp, JSIDPlay2, SIDdecompiler, DeepSID (Chordian) — no
  Digitalizer format handling beyond detection

## SID Duzz' It (SDI — the format proxy)
- ✅ SDI 2.1.6 docs `SDI.2.1.6-docs.txt` (64.9 KB) — full format/effect spec
  → distilled into `sdi_format_spec.md` / `sdi_effect_reference.md` /
  `src/sdi_2.1.6_docs_summary.md`
- ⚠️ SDI SourceForge project ("glennrg64") — docs fetched; player .asm
  (`s.sdi21-n49`, `s.sdi21-spd49`) identified but not parsed (RE-phase)

## Archive.org / Wayback / HVMEC
- ❌ web.archive.org — all fetches blocked this session
- ✅ HVMEC (HVSC Musician/Editor docs) — version comparison (V2.2/V2.8 no filter;
  V3.0 adds filter; V3.5 newplayer)
- ⚠️ disk-image string extraction (DTL35-EDITOR.D64 etc.) — field names/headers
  recovered (in `archive_documentation.md`); binaries NOT disassembled
- ❌ Blues Muz' 1994 intro + "82 Ditties" archive.org items — no Digitalizer docs

## Forums / diskmags / Usenet
- ✅ Lemon64 / codebase64 / CSDb forums searched — no deep technical thread found
- ❌ Usenet comp.sys.cbm(.programmer) — no Digitalizer-internals posts found
- ⏭ diskmag interviews (World News #11, Hotshot #04, Internal #27) — not fetched;
  may hold the JCH-influence detail

## Local
- read-only `hvsc84.db` — 542 Digitalizer_V2.x + 77 Digitalizer_V3.0
- `tools/sidid.cfg` / `src/sidid.py` — NOT present in this repo (no local sidid)
- HVSC `DOCUMENTS/` — no Digitalizer-specific doc

## Deferred to RE (binaries already in hand)
- ⏭ `tmp/digitalizer_research/DTZ2SDI.zip` — `.d64`; needs c1541 extract + disasm
- ⏭ V3.0 player disasm from HVSC SIDs (Blues_Muz V3.0 tunes)
- ⏭ SteinTronic1.d64 (ancestor) — only if V2.x RE stalls
