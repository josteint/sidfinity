---
source_url: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/
fetched_via: direct
fetch_date: 2026-06-17
author: Zimmers.net archive maintainers
content_date: 2009-08-18 (file dates)
reliability: primary
---

# Archive Survey: SIDwinder on FTP and Web Archives

## Zimmers.net (primary FTP mirror of Funet)

URL: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/

Two SIDwinder files found:

| Filename | Size | Description |
|---|---|---|
| SIDwinder_V0123_C64.d64.gz | 73,918 bytes | SIDwinder v1.23 disk image for C64 |
| SIDwinder_V0123_src.zip | 341,456 bytes | Source code of SIDwinder v1.23 |

Both files dated 2009-08-18 in the archive index. Both confirmed downloadable.

## ALLFILES.html entries

From https://www.zimmers.net/anonftp/pub/cbm/c64/ALLFILES.html:

```
audio/editors/SIDwinder_V0123_C64.d64.gz    "SIDWinder v1.23"
audio/editors/SIDwinder_V0123_src.zip       "Source code of SIDwinder v1.23."
```

## CSDb download (V01.22 d64)

- URL: `http://csdb.dk/getinternalfile.php/59266/SIDWinder v01.22 (1994)(Natural Beat).d64`
- 391 downloads recorded
- Binary d64 disk image; contains readable documentation text embedded
- Key text extracted: up to 32 subtunes, 96 sectors, 64 instruments, GPL licensed

## Plus/4 World entry

URL: https://plus4world.powweb.com/software/SIDwinder_V01_23

The Plus/4 port (V01.23, by TLC/Coroners) is documented on Plus/4 World:
- Rating: 9.0/10 (11 votes)
- Release date: March 15, 2000
- Mirrors: Plus/4 World, Rulez.org, Zimmers, ko2000, commodore.ca, Othersi.de
- The Plus/4 version requires a Synergy SID card at $fd40

## Archive.org

- https://archive.org/details/18_Years_Clarence_19xx_Natural_Beat — Natural Beat demo (not SIDwinder itself)
- No dedicated SIDwinder disk image items found on Archive.org directly
- The Wayback Machine cannot be scraped directly (HTTP 403 from this session)

## Source code contents (extracted locally from SIDwinder_V0123_src.zip)

The zip contained:
```
README          — top-level overview, GPL notice, copyright, song list
GENERAL         — full story/history/GENERAL info doc (by TLC, with Taki's section)
HISTORY         — version history for editor, player, packer (V00.xx through V01.23)
SIDW0122        — original SIDwinder V01.22 documentation by Taki (804 lines)
SUMMARY         — feature summary, keys, commands (based on Taki's doc)
PROGRAMM        — programmer notes (cross-compilation, code structure)
PLUS4           — Plus/4-specific information
COPYING         — GNU GPL v2

SRC/
  ED.ASM        — Editor source (6502, TASM syntax)
  PLAYER.ASM    — Player source (6502, TASM syntax, 1167 lines)
  PACKER.ASM    — Packer source
  SIDR.ASM      — SID reader / utility
  VIEWER.ASM    — ASCII viewer source
  CHARS.BIN     — Character set binary
  MASKS.BIN     — Mask data binary
  SECTORS.BIN   — Sector data binary
  TRACKS.BIN    — Track data binary
  VCHARS.BIN    — Viewer character set

PRE_0123/
  0122/PLAY0122.ASM   — Player V01.22 source
  0122/PLAY0122.SEQ   — SEQ (PETSCII) version of V01.22 player
  0120/ED1.ASM etc.   — Editor V01.20 split into 3 pieces (Turbo Assembler limit)
  0120/PLAY0120.ASM   — Player V01.20 source
  REANIM/             — "Reanimated" (reconstructed) intermediate sources

TOOLS/
  FREQ.C        — Frequency table generator (C source)
  STRIPCR.PAS   — Strip CR utility (Pascal)
  ABS.PAS, CLC_RS.PAS, D2.PAS, DIFF.PAS — Build utilities
  README        — Tools documentation
```

## Leads to follow

- Download and extract the actual SIDwinder d64 disk images from Zimmers to read PETSCII docs
- ftp://c64.rulez.org/pub/c64/Tools/Music/Editor/ — additional FTP mirror for SIDwinder
- ftp://ftp.funet.fi/pub/cbm/c64/audio/editors/ — the original Funet path (confirmed in docs)
- ftp://ftp.funet.fi/pub/cbm/plus4/Tools/Music/ — Plus/4 version on Funet
- http://www.sch.bme.hu/~takinb — Taki's BME homepage (almost certainly dead; Wayback worth checking)
