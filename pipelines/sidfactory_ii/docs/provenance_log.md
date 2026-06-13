# Provenance log — SID Factory II research

Every URL attempted during the 2026-06-13 sweep, fetched or failed, so future
waves don't re-fetch. Status: ✅ fetched · ⚠️ partial · ❌ failed/unavailable.

## GitHub — Chordian/sidfactory2 (GPL v2, primary source)
- ✅ `raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/datasource/datasource_sequence.{h,cpp}` — sequence pack/unpack → `src/datasource_sequence.*`
- ✅ `.../datasource/datasource_orderlist.{h,cpp}` — order-list pack/unpack → `src/datasource_orderlist.*`
- ✅ `.../runtime/editor/driver/driver_info.{h,cpp}` — descriptor block chain → `src/driver_info*.{h,cpp}`
- ✅ `.../driver/driver_utils.{h,cpp}` — address calc / IRQ insertion → `src/driver_utils*.cpp`
- ✅ `.../utils/sf2_interface.{h,cpp}` — converter API / reader-writer → `src/sf2_interface.*`
- ✅ `.../converters/converter_jch.cpp` — NP20 (JCH) format decode → `src/converter_jch.cpp`
- ⚠️ `.../converters/converter_gt.cpp` — GoatTracker SNG→SF2 (stub only fetched)
- ✅ `.../utils/packer.cpp` + `packing_utils.cpp` + `packer.h` — export/relocation → `src/packer_cpp.cpp`
- ✅ `.../utils/c64file.cpp`, `psidfile.cpp` — PSID wrapper → `src/psidfile_cpp.cpp`
- ✅ `.../editor/auxilarydata/auxilary_data_collection.cpp`, `auxilary_data_songs.cpp`, `auxilary_data.cpp` → `src/auxilary_data_*_cpp.cpp`
- ✅ `.../runtime/editor/driver/driver_architecture_sidfactory2.cpp` → `src/driver_architecture_sidfactory2_cpp.cpp`
- ✅ Repo driver notes `notes_driver11.txt`–`notes_driver16.txt` → `src/notes_driver*.txt`

## Official manual / website (files.chordian.net, blog.chordian.net)
- ✅ `http://files.chordian.net/sf2/SIDFactoryII_20260314_User_Manual.pdf` → pdftotext → `src/user_manual_20260314.txt`
- ✅ `https://blog.chordian.net/sf2/` — release/tutorial index (link harvest)
- ⚠️ `https://files.chordian.net/sf2/` (release zips, .prg binaries) — downloaded to `tmp/sidfactory_ii_research/`; .prg NOT disassembled (out of scope)

## CSDb
- ✅ release pages #210571, #210570, #210568, #213369, #222255, #224223, #235968, #260181 — build chronology, credits, changes
- ✅ JCH NewPlayer / NP20.Gx + Laxity (Vibrants) scene pages — lineage
- (CSDb webservice API `csdb.dk/webservice/` available; not heavily used)

## Other
- ✅ `github.com/cadaver/sidid` — sidid signature for `SidFactory_II/Laxity`
- ✅ codebase64 SID freq-table calc + freq-table gist — for note→freq context
- Local: `hvsc84.db` (read-only) — 377 `SidFactory_II/Laxity`, 39 `SidFactory/Laxity`
- Local: `tools/sidid.cfg`, HVSC `DOCUMENTS/` — no SF2-specific signature/doc present

## Failed / not chased
- ❌ 6502 driver `.asm` source — does NOT exist in the public repo (binaries only).
  → migration phase RE.
- ⏭ YouTube SF2 tutorials (Vincenzo / StrayBoom) — video; technical substance
  already covered by manual. Not fetched.
- ⏭ DeepSID `github.com/Chordian/deepsid` SF2 playback notes — not fetched (low
  marginal value; format already fully covered).
