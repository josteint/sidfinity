# Provenance log — Basic_Program research sweep (2026-06-22)

Per-source URLs + reliability live in each `cN_*.md` file's provenance header and
in their "## Leads to follow" sections. This log records the sweep structure and the
primary/local sources used, so a future wave doesn't repeat the same work.

## Local primary sources (highest reliability)
- `hvsc85/` — the 486 `Basic_Program` SID files themselves (the BASIC source archive).
- `hvsc85/DOCUMENTS/SID_file_format.txt` — RSID BASIC-flag + `$030C` semantics (C5).
- `hvsc84.csv` (via DuckDB) — corpus characterization: origins, authors, subtune counts (C1).
- `deprecated/gt2_pipeline/tools/sidid.cfg` — the `Basic_Program` signature bytes (recon).
- `tools/siddump.cpp` + `tools/libsidplayfp/src/sidplayfp/sidplayfp.h` — the `setRoms()` gap (C5).
- `~/.local/share/sidplayfp/{kernal,basic,chargen}` — canonical C64 ROMs, MD5-verified (C5).
- `deprecated/gt2_pipeline/` — the universal register-trace → USF prior art (C6).
- Full-corpus detokenize scan (orchestrator) — exact feature counts, parse_fail 0/486.

## External source clusters swept (see each cN file for exact URLs)
- **C1 scene origin:** CSDb, archive.org (Family Computing / COMPUTE! / Commodore PRG
  guide / James Vogel C64 Music Book scans), joeylatimer.com.
- **C2 tokenization:** C64 Programmer's Reference Guide, Mapping the C64, codebase64,
  VICE `petcat`, cbmbasic detokenizer sources.
- **C3 interpreter/timing:** annotated C64 BASIC ROM disassembly (Lee Davison /
  pagetable.com), codebase64, KERNAL IRQ/CIA timing references.
- **C4 floating point:** BASIC ROM FP routine disassemblies, Steil `cbmbasic` (mist64),
  VICE FP code, Hart "Computer Approximations" (polynomial coeffs).
- **C5 playback/ROMs:** libsidplayfp docs/source, sidplayfp ROM-loading mechanism,
  MEGA65 OpenROMs, DeepSID/jsSID, VICE monitor trace recipe.
- **C6 extraction:** in-repo `docs/the_principle.md` + CLAUDE.md +
  `deprecated/gt2_pipeline`; general SID-register→note semantics (codebase64, SID datasheet).

## Method notes
- 6 leaf agents (sonnet), each hard-constrained: no sub-spawning, no git, write-only to
  `pipelines/basic_program/docs/`, read-only DB. Per the research-player skill.
- Orchestrator (Opus) did local recon + the full-corpus feature scan + this synthesis.
- Outstanding leads are aggregated under "Gaps / still-open" in `README.md` and in each
  cluster file's "## Leads to follow".
