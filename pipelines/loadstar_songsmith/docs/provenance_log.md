# Provenance log — Loadstar SongSmith research

Every URL/source attempted during the 2026-06-14 sweep. ✅ fetched · ⚠️ partial ·
❌ failed/unavailable · ⏭ identified but deferred (RE / binary).

## Loadstar magazine archives (the primary source)
- ✅ discmaster.textfiles.com `5218/237.d81` (Loadstar #237, 2004) — recovered
  `t.songsmith` (Moorman doc) → `src/loadstar237_t_songsmith_extracted.md`;
  `t.sidsmith` + `t.smithsid` (converter docs) → `src/loadstar237_converter_docs_extracted.md`
- ✅ CSDb release #122855 "Songsmith" tool — `getinternalfile.php/121491/Songsmith-Loadstar.d64`
  downloaded to `tmp/loadstar_songsmith_research/`; string-dumped (instrument names,
  hot keys, init disasm) → `src/d64_documentation_text.txt`
- ⚠️ itch.io "Loadstar Compleat" — located; SongSmith shipped as a standalone
  Softdisk product (#069525), not in a regular issue until #237; 30-page manual was
  PRINTED (not on disk) → likely unrecoverable online
- ⏭ archive.org Loadstar #27–28 d64 (the Garrett/Gardner precursor "songmaker")

## sidid / player-ID
- ✅ `github.com/cadaver/sidid` + `github.com/WilfredC64/player-id` — all four
  variants (`Loadstar_SongSmith`, `_v1`, `_v2`, `_v3`) byte-decoded →
  `src/sidid_loadstar_songsmith_signatures.txt`
- ✅ surveyed DeepSID, libsidplayfp, JSIDPlay2, SIDFactory II converters,
  ChiptuneSAK, desidulate — NO SongSmith-specific handler / parser anywhere
- ✅ Chamberlain `.MUS` / Enhanced Sidplayer spec (GitHub) → `github_sidplayer_mus_format.md`
  (kept as CONTRAST — SongSmith is definitively NOT a .MUS-family tool)

## Forums / community / Usenet
- ✅ comp.sys.cbm (Loadstar #168 thread) — Fender Tucker attributes the precursor
  to Joe Garrett + Alan Gardner → `src/compsyscbm_loadstar168_extracted.md`
- ✅ eLoadstar / eloadstar.com — `b.songsmith` loader confirms Joe Garrett (© 2005)
- ✅ converter authorship: SIDSmith (Debby Cruz + Scott Resh, 1988), SmithSID (Doreen Horne)
- ✅ DeepSID 'L' icon (2025) for SongSmith-only composers — reads HVSC engine strings
- ⏭ AmigaLove Fender Tucker interview (viewtopic t=1726) — not fetched
- ⏭ Alan Beggerow personal site (Commodore-composing reminiscences) — partial

## Local
- read-only `hvsc84.db` — 308 + 19 + 3 + 1 = 331 across the four engine tags
- HVSC `DOCUMENTS/` — no SongSmith-specific doc

## Deferred to RE (binary in hand)
- ⏭ disasm mature player ($CC00/$CC48) → exact m-file note/duration interleave + freq table
- ⏭ v1 (ZP-indirect) early engine — separate structure
- ⏭ verify Dave Marquis SIDs really are SongSmith (attribution discrepancy)

## Note
`research.md` was enriched in-place by a wave-1 agent (corrected author/count);
content is accurate and superseded by this README as the authoritative index.
