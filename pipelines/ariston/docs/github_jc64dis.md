---
source_url: https://github.com/ice00/jc64 + https://iceteam.itch.io/jc64dis
fetched_via: git clone (external); repo cloned to /home/jtr/sidfinity/tmp/ariston_research/jc64/
fetch_date: 2026-06-15
author: ice00 (IceTeam)
content_date: ongoing
reliability: secondary (tool reference; no raw disassembly text available without running the tool)
---

# JC64dis — Ariston Example

## Repository

Cloned to: `/home/jtr/sidfinity/tmp/ariston_research/jc64/`

## Ariston Example File

Path in repo: `doc/example/Ariston.dis`
- Size: 250,250 bytes
- Format: gzip-compressed JC64dis project file (not plain text disassembly)
- Content: JC64dis project for Wally Beben's "Dark Side" (1988, Incentive)

## List.txt Entry (verbatim)

```
* Ariston music editor (tune "Dark Side" by Wally Beben (c) 1988 Incentive)
```

This is listed among ~80 reverse-engineered SID/PRG examples included with JC64dis.
The Ariston.dis project can be opened in JC64dis (Java GUI) to produce a labelled 6502
disassembly with cross-references and type annotations.

## How to Use

JC64dis is available at https://iceteam.itch.io/jc64dis (Windows/macOS/Linux).
Opening `Ariston.dis` in JC64dis will show:
- The labelled player code (with auto-generated labels from iterative disassembly)
- Cross-references to SID register writes
- Data/code type annotations applied by the original creator

This is the ONLY known tool-assisted disassembly of an Ariston SID in public repositories.

## Note on Dark_Side.sid

`MUSICIANS/B/Beben_Wally/Dark_Side.sid` in HVSC #84:
- Load address: $0900
- Init: $1628
- Play: $0901
- Songs: 1
- Data size: $0D2E (~3374 bytes)

This SID has both the Ariston primary signature and Wally_Beben sub-signature, confirming
it's the canonical Wally_Beben variant. It is the recommended first target for manual
disassembly work.

## Other example files of interest (from doc/example/)

`doc/example/BarryLeitch.dis` — Barry Leitch player (separate from Ariston, tune "Visage" 1988).
Confirms Barry Leitch had his OWN player engine separate from Ariston. The HVSC Ariston-classified
Barry Leitch SIDs (Captain_Courageous, Marauder) predate his own player.
