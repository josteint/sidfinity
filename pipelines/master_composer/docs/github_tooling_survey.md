# Master Composer — GitHub / tooling survey

> **Provenance**
> - source_url: see per-tool links below (GitHub, readthedocs, CSDb); plus `local: tmp/jc64/` (JC64dis checkout) and `local: tools/libsidplayfp` (in-tree libsidplayfp)
> - fetched_via: WebSearch + WebFetch (ChiptuneSAK docs, VGMPF wiki, GitHub), local grep of in-tree libsidplayfp/siddump and the JC64dis distribution
> - fetch_date: 2026-06-13
> - author: survey by SIDfinity research pass; tools authored as credited
> - content_date: 2026-06 (tool snapshots); engine 1983–1984
> - reliability: secondary (third-party tools) — but the **negatives are high-confidence**, verified against source/docs.

**Bottom line: there is NO format-aware Master Composer parser/converter in any surveyed open tool.** Master Composer's binary format (3-tier pages/blocks/bars + per-block SID-register snapshot tables) has, as far as this survey found, never been decoded into a structured parser. The only structured RE artifact known is the **JC64dis hand-annotation** (covered in `github_jc64dis_local_disasm.md`). Everything else is either engine-blind (SID emulation → register-output analysis) or doesn't touch SID at all.

## Tool-by-tool

### ChiptuneSAK — `c64cryptoboy/ChiptuneSAK` (NEGATIVE: engine-blind)
- https://github.com/c64cryptoboy/ChiptuneSAK , docs: https://chiptunesak.readthedocs.io/en/latest/sid.html
- The SID importer "was originally based on Lasse Öörni's (Cadaver) and Stein Pedersen's SIDDump tool"; its `emulator_6502.py` "is very close in functionality to SIDDump's cpu.c". It **emulates the 6502 and analyses the resulting SID register writes**, producing RChirp — it does **not** recognise Master Composer (or any specific tracker) binary structures. No mention of Master Composer / Kleimeyer anywhere in its docs.
- Relevance to us: same paradigm as the project's rejected "writelog replay" path — not what we want (we extract structured musical data, not a played register trace). Useful only as a cross-check oracle.

### sid2midi (NEGATIVE: engine-blind, closed, abandoned)
- Closed source, Windows-only, last updated ~2007, won't process RSIDs. Converts SID→MIDI by emulating a C64 and analysing SID output (same engine-blind approach as ChiptuneSAK). No format-specific Master Composer support; no source to reuse.

### libsidplayfp / libsidtune (NEGATIVE: format-blind by design — confirmed in-tree)
- In-tree at `tools/libsidplayfp/`. Grepping the whole tree for `master.composer` / `kleimeyer` → **no hits** (only `tools/engine_docs.json`, a SIDfinity metadata file, not library code).
- libsidtune parses the **PSID/RSID container** (header, load/init/play, relocation) only; it has **zero** knowledge of the player engine inside. It runs the 6502 and lets the engine drive the SID. This is exactly why it's the project's ground-truth: it is engine-agnostic. It will play any Master Composer SID correctly but tells us nothing structural about the format.
- This is the tool behind `tools/siddump` (`--writelog`, `--writelog-per-irq`, `--pc-trace`), our capture/verification backbone.

### JC64dis — Ice Team (Stefano Tognon) (POSITIVE, but a manual RE artifact, not a parser)
- Project page: https://iceteam.itch.io/jc64dis ; checkout in `tmp/jc64/` (Java; `src/`, `doc/example/*.dis`). JC64 itself is a Java C64 emulator (© Ice Team 1999–2001); the companion **jc64dis** is an interactive disassembler whose project files are the `*.dis` in `doc/example/`.
- It ships a **hand-annotated `Master_Composer.dis`** (the Maniac tune) — labels, per-`$D4xx`-write comments, data-table markers. This is the single best structured source on the format and is fully decoded in `github_jc64dis_local_disasm.md`. JC64dis is a *manual* RE environment, not an automatic Master Composer parser — but its output is reusable as the ground-truth annotation.
- Note: JC64dis distributes annotated `.dis` projects for ~80 players (see `tmp/jc64/doc/example/List.txt`), several already migrated/researched in this repo (Future Composer, Clever Music, Aleatory Composer, etc.) — a recurring high-value source for new families.

### Acid64 / acid64c, sid-device — `WilfredC64/*` (NEGATIVE for parsing; player only)
- https://github.com/WilfredC64/acid64c — a SID **player** (console) using a real/emulated SID. No format extraction.
- Same author ships **player-id** (the signature DB) — covered in `github_sidid_signatures.md`.

### SID Factory II — `Chordian/sidfactory2` (NEGATIVE: different engine, no MC import)
- https://github.com/Chordian/sidfactory2 — a modern composer/editor with its own driver; surfaced in searches as a C64 music tool. Does not import or parse Master Composer files.

## What would have to be built

A structured Master Composer extractor (binary → USF) does not exist and must be written. The good news: the format is small and fully decoded (see the companion disasm doc). An extractor needs to:
1. Read the PSID load address, compute the relocation delta from canonical $7580.
2. Lift the per-block SID-register tables (19 columns × ≤64 blocks), the freq lo/hi tables (by value), the page tables (start/end block, CIA-tempo columns), the per-block #notes/note-start columns, the bar-duration table, and the 64-byte-stride bar/measure note data (3 voice rows × 16 sixteenth-note slots).
3. Emit pages→orderlist, blocks→timbre presets, bars→16-step patterns, with the `$00`=hold / `$64`=gate-release / `1..$63`=note semantics.

No existing code does any of this; the JC64dis annotation + the in-tree `seed_disassembly.py`/`siddump --writelog` are the inputs.

## Sources
- ChiptuneSAK SID docs — https://chiptunesak.readthedocs.io/en/latest/sid.html
- ChiptuneSAK repo — https://github.com/c64cryptoboy/ChiptuneSAK
- JC64dis (Ice Team) — https://iceteam.itch.io/jc64dis
- WilfredC64/acid64c — https://github.com/WilfredC64/acid64c
- Chordian/sidfactory2 — https://github.com/Chordian/sidfactory2
- sid2midi (Remix64 note) — https://remix64.com/news/new-sid2midi-version.html
- In-tree: `tools/libsidplayfp/`, `tools/siddump.cpp`, `tmp/jc64/` (local, read-only)
