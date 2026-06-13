## GMC / Superiors - Game Music Creator (446 tunes)

> **⚠ 2026-06-13 — see [`README.md`](README.md)** + `forum_gmc_dmc_lineage.md` + `spec_extraction_plan.md`. Headline: GMC is the **direct predecessor of DMC** (same author Brian/Graffity, 8 weeks apart) — so the already-migrated **DMC pipeline largely transfers** (shared Tracks→Sectors model, $1000/$1003 entry, 8-subtune table; GMC just needs fresh instrument-decode, its sounds are 16 bytes vs DMC V4's 11). Closed engine (no public source) → byte-level layout is OPEN, RE during migration. "Superiors" = Graffity's internal "Superiors Aural Department" label, not a cracker group. V2.0 is a modern revival (9 HVSC tunes, 2010-23); the 446 are V1.

- **Author:** Balazs Farkas (Brian) of Graffity (Hungary)
- **Year:** 1990
- **Source:** Not public
- **CSDb:** #7268
- **Predecessor to DMC** (Demo Music Creator)

### Entry Points
- Init: $1000, Play: $1003

### Data Structure
Two-level hierarchy: Tracks -> Sectors.

**Track level:** Up to 8 tunes per file. Tracks reference sectors with transpose controls.

**Sector level (per step):**
- DUR: duration
- SND: sound/instrument number
- APM: amplitude/modulation
- GLD: glide/portamento
- HLD: hold duration
- CONT: continuation/tie flag
- END: terminator

Sound definitions: 16 bytes each (indexed via 4x ASL A = multiply by 16).

### SIDId Variants
GMC/Superiors (V1.0), GMC_V2.0/Superiors.

---
