---
source_url: multiple (see individual csdb_*.md files)
fetched_via: direct
fetch_date: 2026-06-17
author: research synthesis
content_date: 2026-06-17
reliability: primary (synthesized from primary sources)
---

# SIDwinder — Research Summary

## Identity

| Field | Value |
|-------|-------|
| Engine name | SIDwinder |
| Author | Balázs Takács ("Taki") / Natural Beat |
| Country | Hungary |
| Initial development | 1994 (unreleased) |
| Public release (V01.22) | 1999 |
| Final release (V01.23) | 2000-03-15 |
| Plus/4 port by | Levente Hársfalvi (TLC) / Coroners |
| License | GPL (first open-source release at V01.23) |
| HVSC count | 117 SID files |
| CSDb IDs | 66494 (V01.22), 101758 (V01.23) |

## Version History

| Version | Year | Notes |
|---------|------|-------|
| V01.20 | ~1994 | Earliest known (in `PRE_0123/0120` subdir of source) |
| V01.22 | 1994/1999 | Original C64 release; "unreleased until later"; first public |
| REANIM | ~1994-1999 | Intermediate version (in `PRE_0123/REANIM` subdir) |
| V01.23 | 2000 | TLC Plus/4 port; new packer; GPL release; includes PLAYER.ASM |
| V01.23 Enhanced | 2011 | PCH fork; added live piano ("M" key); dropped GPL note |

## What It Is

SIDwinder is a native C64 music composition package with three components:
1. **Editor** — native C64 tracker with track/sector/instrument editing
2. **Packer** — compresses song data into a standalone PSID-compatible binary
3. **Player** — the runtime playroutine embedded in the packed output

The editor uses a three-level hierarchy:
- **Tracks** → sequence of sector references + transpose/volume commands per voice
- **Sectors** → melodic phrases (instrument + note + effect commands)
- **Instruments** → ADSR + 4 effect table pointers (wave/arp, filter, pulse, slide)

## Format Capabilities

- Up to 32 subtunes
- Up to 96 sectors per song (256 commands per sector)
- Up to 64 instruments
- Up to 16× multi-speed support
- 4 effect tables: wave/arpeggio, filter, pulse width, slide/vibrato
- Each table uses a `$FF` = jump / loop mechanism
- PAL only
- Packer embeds a 32-character identity field in the binary

## Key Technical Details

**Zero-page:** `$FB–$FC` (default); change to `$FC` on Plus/4 (Kernal conflict)

**Track commands:** `...XX` (play sector), `Tr+XX`/`Tr-XX` (transpose), `VolXX`, `IncXX`/`DecXX` (vol slide), `HltVS`, `JmpXX`

**Sector commands in order:** `Snd.XX` (instrument), `Dur.XX` (duration), [note or `Gld.XX`/`-------`/`+++++++`], `Finish`

**Packer bug:** confirmed in V01.23 — endpoint/glide/slide offsets corrupt in long songs. Fixed packer released separately by TLC.

## Source Code Availability

The source is available at:
- **Zimmers.net:** `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip` (341KB)
- Rulez.org, ko2000, commodore.ca (mirrors)

Source archive contains: `ED.ASM`, `PACKER.ASM`, `PLAYER.ASM`, `SIDR.ASM`, `VIEWER.ASM`, `PLAY0122.ASM`, documentation (`COPYING`, `README`, `SUMMARY`, `GENERAL`, `HISTORY`, `PROGRAM`, `PLUS4`, `SIDW0122`).

## Player Fingerprint (sidid.cfg)

```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

This identifies the sector dispatch loop: LDA table → BEQ → DEC → DEY → JMP → LDA,Y → CMP → BCC → BEQ → LDA,Y → STA → TAY.

## Unrelated "SIDwinder" (2025)

CSDb ID 253271 is a completely different tool by Raistlin/Genesis Project — a modern SID
visualizer/player tool with no relation to Taki's SIDwinder.
Source: https://github.com/RobertTroughton/SIDwinder/

## Key People

| Person | Role |
|--------|------|
| Balázs Takács (Taki) | Original author; musician; Hungary |
| Levente Hársfalvi (TLC/Coroners) | Plus/4 port; rewrote packer; GPL release |
| Luca Carrafiello (Luca/FIRE) | Beta tester; found the packer bug |
| PCH (KGB'92/Unreal) | 2011 Enhanced fork |

## Pouet Presence

Natural Beat is **not listed on Pouet.net** — they were a pure music group (no demos),
so they never appeared in the demo-focused Pouet database.

## Research Gaps / Leads

See csdb_source_links.md for download URLs. The most valuable next step is downloading
and examining:
1. `SIDwinder_V0123_src.zip` → `PLAYER.ASM` (the runtime player — this is what HVSC SIDs contain)
2. The HISTORY and SUMMARY doc files inside the zip (version changelog, format spec)
3. The fixed packer from Plus/4 World / Othersi.de
