## X-Ample / Compotech (387 tunes)

> **⚠ 2026-06-13 — see [`README.md`](README.md)** + `csdb_manual.md` (the annotated V3.2 player source, summarised) + `sidid_variant_taxonomy.md`. Notable: an **annotated V3.2 TurboAss player source** ships on the Compotech V2.1 D64 (CSDb #122614) as a game-dev integration reference — names all effect routines. XTracker (V3.1/V4.1x/V4.2x) is by **Tufan Uysal (SoNiC)**, a SEPARATE author — but its V3.1 player is **byte-identical to Compotech V2.1**, so one data format likely covers most non-Digi variants. **X-Ample_Digi** = CIA2-NMI sample (Mode-2, out of scope; 0 confirmed in HVSC). **Reflextracker is a DIFFERENT engine** (Polish, all RSID) — not X-Ample, don't conflate. Byte-level data layout still OPEN → RE during migration.

- **Authors:** Markus Schneider (driver), Helge Kozielek (optimizations), Joachim Fräder (editor UI) — X-Ample Architectures (Germany)
- **Year:** 1989-1995
- **Source:** Not public
- **CSDb:** #122614 (Compotech V2.1)

### Evolution
Schneider's driver -> Parsec Music Editor -> Compotech editor (full tracker).

### Architecture
Player iterates 3 voices via bitmask, calls per-voice subroutine, advances SID register base by 7 per voice ($D400, $D407, $D40E).

### SIDId Variants (6+)
Compotech_V2.x, Sonic/SDS, Thomas_Detert, XTracker_V4.1x, XTracker_V4.2x, X-Ample_Digi.

### Notable Users
Thomas Detert (177 SIDs), Stefan Hartwig (134 SIDs), Markus Schneider (105 SIDs).

---
