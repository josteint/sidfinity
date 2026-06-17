---
source_url: https://www.zimmers.net/anonftp/pub/cbm/c64/ALLFILES.html
fetched_via: direct
fetch_date: 2026-06-17
author: Zimmers.net
content_date: 2009
reliability: primary
---

# FTP Mirror Findings for SIDwinder

## Confirmed FTP paths (from SIDwinder documentation)

The following FTP paths are listed in the V01.23 README and GENERAL docs as official distribution points:

### Natural Beat / Taki's homepage
- http://www.sch.bme.hu/~takinb — almost certainly dead (BME student server, circa 1999-2001)
- Wayback Machine: https://web.archive.org/web/*/www.sch.bme.hu/~takinb* (worth checking)

### c64.rulez.org FTP
- ftp://c64.rulez.org/pub/c64/Demos/n/Natural_Beat/Cubic_Player.zip
- ftp://c64.rulez.org/pub/c64/Tools/Music/Editor/ (SIDwinder tool location)
- ftp://c64.rulez.org/pub/plus4/Tools/Music/ (Plus/4 version)

### Funet FTP
- ftp://ftp.funet.fi/pub/cbm/c64/audio/editors/ (confirmed: SIDwinder files present via Zimmers mirror)
- ftp://ftp.funet.fi/pub/cbm/plus4/Tools/Music/ (Plus/4 version)

### padua.org FTP
- ftp://ftp.padua.org/pub/c64/Demos/pal/natural_beat/cubicplayer_NB.zip

## Zimmers.net mirror (live as of 2026-06-17)

Zimmers.net mirrors Funet. These files are confirmed present and downloadable:

| Path | Size |
|---|---|
| https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_C64.d64.gz | 73,918 bytes |
| https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip | 341,456 bytes |

The src.zip was retrieved and extracted in this session. Content is confirmed complete.

## Wayback Machine notes

- Direct Wayback fetches failed (HTTP 403 from this research session's fetch tool)
- Recommended manual check: https://web.archive.org/web/*/www.sch.bme.hu/~takinb
- Recommended manual check: https://web.archive.org/web/*/ftp.funet.fi/pub/cbm/c64/audio/editors/sidwinder*
- Recommended manual check: https://web.archive.org/web/*/naturalbeat* (Natural Beat homepage)

## YouTube evidence of V1.24

A YouTube video "SIDWinder v1.24 sub030 Enhanced - Draxish" (URL: https://www.youtube.com/watch?v=6ZsX3D_vUuY)
was found in web search results, indicating a V1.24 ("sub030 Enhanced") release exists.
This version is NOT documented in the source tree (which only goes to V1.23) and was not
found on any FTP archive in this sweep. It may be an unofficial enhancement by a third party.
"sub030" suggests a sub-version number (build 030). "Draxish" is one of Taki's demo songs.

## Leads to follow

- Manual Wayback Machine browse for http://www.sch.bme.hu/~takinb
- Search YouTube for other SIDwinder demo videos — may reveal V1.24 download source
- Check Plus/4 World mirrors: https://plus4world.powweb.com/software/SIDwinder_V01_23
- Check if c64.rulez.org FTP is still accessible (Hungarian C64 scene server)
- Search CSDb for V1.24 release: https://csdb.dk/search/?stype=release&q=sidwinder+v1.24
