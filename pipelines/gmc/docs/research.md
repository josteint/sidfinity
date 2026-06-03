## GMC / Superiors - Game Music Creator (446 tunes)

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
