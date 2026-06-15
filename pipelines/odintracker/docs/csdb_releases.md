---
source_url: https://csdb.dk/search/?seinsel=releases&search=Odin+Tracker&Go=Go + individual release pages
fetched_via: direct 2026-06-15
fetch_date: 2026-06-15
author: Zed (Zoltan Konyha)
content_date: 2000-02-15 to 2001-04-17
reliability: primary
---

# OdinTracker — CSDb Release Inventory

All 8 releases by Zed (Zoltan Konyha), all classified as "C64 Tool".
Official website (now likely dead): http://www.inf.bme.hu/~zed/tracker/
Author email: zed@kempelen.inf.bme.hu / zed@inf.bme.hu

## Releases (oldest first)

| Version | CSDb ID | Date | Download (internal) | Notes |
|---------|---------|------|---------------------|-------|
| 1.00 | 12577 | 15 Feb 2000 | getinternalfile.php/31883/Odin_Tracker_100.zip | First release. Contains .d64 + tracker.s (full monolithic source) |
| 1.01 | 12576 | 17 Feb 2000 | getinternalfile.php/75925/Odin_Tracker_1.01.zip | Minor UI/keyboard fixes |
| 1.02 | 12575 | 28 Feb 2000 | getinternalfile.php/75924/Odin_Tracker_1.02.zip | +hard restart, save-player hack; music by Cadaver |
| 1.03 | 12574 | 29 Feb 2000 | getinternalfile.php/75923/Odin_Tracker_1.03.zip | Bugfix only (orderlist delete) |
| 1.10 | 153114 | 27 Mar 2000 | getinternalfile.php/154683/Odin_Tracker_1.10.zip | **Major**: packer, filter table, new file format (incompatible with 1.0x) |
| 1.11 | 12572 | 31 Mar 2000 | getinternalfile.php/75693/Odin_Tracker_1.11.zip | Bugfix: track transpose had no effect on arpeggio |
| 1.12 | 12571 | 20 Mar 2001 | getinternalfile.php/15294/OdinTracker112.zip | +filter table block editor; freq table PAL fix; vibrato depth scale refined |
| 1.13 | 2628 | 17 Apr 2001 | getinternalfile.php/154684/OdinTracker113src.zip (src) + getinternalfile.php/60709/odintracker.zip (binary) | +RLE song saves; bugfixes (slide, vibrato depth, save last byte); **SOURCE RELEASED** |

## File format versions

Two incompatible on-disk song formats exist:
- **Format 1.0x**: v1.00–v1.03. No filter table (no $4E00 region). Instruments are 16 bytes but no filter table fields.
- **Format 1.1x**: v1.10–v1.13. Adds filter table at $4E00–$4F00. Instrument bytes 13–15 are filter table start/end/loop. v1.12+ saves songs RLE-packed.

The v1.10 README notes: "Please note that all three songs were made with 1.0x versions of the tracker. Import them as such."
The v1.10+ tracker has an "Import 1.0x song" option that imports old format (without filter settings).

## Key format change: v1.00→v1.10

From HISTORY:
- v1.10 adds filter table (new region $4E00–$4F00), adds instrument filter table start/end/loop fields (bytes 13–15)
- Vibrato was reworked: "pitch-independent vibrato had to go"
- Pulse width modulation refined

## CSDb notes from release pages

v1.13 page notes:
- v1.13 introduces RLE encoding for song saves, backward-compatible format
- v1.13 fixes: slide effect ignored parameter; vibrato depth max bug; song save omitted final byte
- Two downloads: binary (1,273 dl) and source (188 dl)
- External mirror: Pokefinder.org

## HVSC coverage

159 SIDs in HVSC #84 with engine='OdinTracker'.
Key composers: SounDemoN (Zed's collaborator, ~40+ tunes), Hoffmann Michal (~20 tunes),
LordNikon, Monk, Factor6, FieserWolF, Hukka, Ahti, Cadaver, Jammer, Rebb, Sidder.
