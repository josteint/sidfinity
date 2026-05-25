---
source_url: https://iceteam.itch.io/jc64dis
fetched_via: WebFetch direct
fetch_date: 2026-05-25
author: Ice Team (ice00) — JC64dis is the de facto next-generation
  C64 disassembler with player-engine recognition
content_date: ongoing project, current as of 2026
reliability: primary for engine identification claims (ice00 is the
  one whose CSDb comment identifies Murray's variant on Hubbard's
  C64 Music Examples)
---

# JC64dis — what it says about the Companion family

## Quoted from the JC64dis itch.io page

JC64dis recognises 70+ distinct music engines. Among them, it
**explicitly lists three engines that all belong to the Companion
family**:

- **Rob Hubbard's Companion player** — example tune: *Synth Sample
  III* (tune 3 of Hubbard's *Commodore 64 Music Examples*, 1985)
- **Chris Murray's player** — reverse-engineered from *Henry's House*
  (1984 English Software)
- **Keith Bowden's player** — example tune: *Roundabout* (1984 Pan
  Books)

These three are catalogued separately by JC64dis, which means ice00
considers them all variants/derivatives of one engine lineage but
not byte-identical.

## Implication for SIDfinity

This independently confirms the chain:

  Keith Bowden book listing (1984)
    → Hubbard adopts and adapts ("his own version of") (1984)
    → Chris Murray adapts with different freq tuning (1984)

All three are reverse-engineered and disassembled inside JC64dis.
The JC64dis project itself is the best available external source
for engine details — its GitHub repo (linked from the itch.io
page) likely contains the recognition signatures and possibly
documented disassemblies.

## YouTube video

`https://www.youtube.com/watch?v=_rEFdiC8LFM` — "JC64Dis (Next
Generation Disassembler): get Chris Murray player" — recorded
disassembly session showing the Murray variant being recovered
from Henry's House. Not fetched in this session; recommended as a
follow-up if we need to reproduce the Murray-variant disassembly
procedure.
