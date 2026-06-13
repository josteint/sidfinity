# SID-Wizard upstream source (third-party reference)

This is the **original SID-Wizard source**, kept in-repo as reference for the
migration — NOT our code. Per the project core tenet we compose our own engine
to match the write-log; we read this source to (a) write the extractor (it's the
inverse of `exporter.asm`) and (b) learn the exact effect semantics / write model.

- **Upstream:** github.com/anarkiwi/sid-wizard (mirror of the SourceForge
  `sid-wizard` SVN tree), fetched 2026-06-13.
- **Author:** Hermit (Mihály Horváth). **License:** WTFPL (do-anything).
- The analysis docs in the parent dir cite these files by `file:line` (e.g.
  `player.asm` rev ~390, `exporter.asm`, `SWM-spec.src` rev ~382). Kept here so
  those citations don't rot when upstream HEAD moves.

| File | What it is | Migration relevance |
|------|-----------|---------------------|
| `exporter.asm` | editor data → exported `$1000` SID binary | **highest** — the extractor is its inverse; resolves the pointer-table offset-map OPEN |
| `player.asm` | the 6502 replay routine | **high** — write-model oracle (effect semantics, ghost flush, MULPLY); has the lean-emitter/table-stepping detail truncated in the analysis docs |
| `SWM-spec.src`, `swm.h` | native SWM format spec | medium — field semantics (native format; HVSC uses the exported form) |
| `datawriter.inc`, `commonsubs.inc`, `altplayers.inc`, `playadapter.inc` | player/driver includes | per-driver-variant tables (`PlrEnds`/`PlrDatP`/…), needed for exact MUSICDATA offsets |
| `editor.asm` | the editor | FX/opcode semantics + DrvType naming live here |
| `SWMconvert.c` | PC-side format converter | parsing reference |
| `Makefile` | build | documents the driver-variant build matrix |

(`tree.json` = a GitHub API directory listing, and `settings.cfg` = editor runtime
config — both dropped as non-source.)
