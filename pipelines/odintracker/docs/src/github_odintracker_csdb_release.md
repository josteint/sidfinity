---
source_url: https://csdb.dk/release/?id=2628
fetched_via: direct
fetch_date: 2026-06-15
author: Zoltán Konyha (Zed)
content_date: 2001-04-17
reliability: primary
---

# OdinTracker 1.13 — CSDb Release Page

## Release summary

- **Tool name:** Odin Tracker 1.13 (alt: Odintracker)
- **Author:** Zed (Zoltán Konyha), zed@kempelen.inf.bme.hu
- **Released:** 17 April 2001
- **Type:** C64 Tool (music tracker / player)
- **Homepage (historical):** http://www.inf.bme.hu/~zed/tracker

## Downloads (CSDb internal)

| File | URL | Downloads |
|------|-----|-----------|
| odintracker.zip (binary) | http://csdb.dk/getinternalfile.php/60709/odintracker.zip | 1,273 |
| OdinTracker113src.zip (source) | http://csdb.dk/getinternalfile.php/154684/OdinTracker113src.zip | 188 |

Also mirrored at zimmers.net:
- https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/OdinTracker113.zip
- https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/OdinTracker113src.zip

## Credits

- **Code:** Zed
- **Music:** SounDemoN (demo SID: "Martin Hubbabubba")

## Binary package contents

- odintracker113.prg — the editor
- help.txt — ASCII help file
- hubbabub.prg — example song (Martin Hubbabubba by SounDemoN)
- HISTORY — changelog
- README

## Source package contents (OdinTracker113src.zip)

```
6510.s          Byte counts for all 6510 instructions (for the packer)
defines.s       Global constants (memory map, instrument offsets, zeropage)
eplayer.s       Editor's player (not saved with song; includes keyjazz, mute)
kernal.s        C64 KERNAL entry points + keycodes
tracker.s       Editor main module (~8163 lines)
vplayer.s       Relocatable player (~1222 lines) — THIS IS WHAT GOES INTO SIDS
vplayeri.s      Stub: tells relocator where player code ends
testirq.s       IRQ test
c64pack/        C64 binary packer (PC-side C++ tool + C64 depacker)
font/           Font bitmap generator
freqtab/        Frequency table generator (C++ → freqtab.s)
vibrato/        Vibrato table generator
help/           Help text compiler
labels.awk      DASM symbol dump → VICE label file
Makefile / makefile.unx/vc/wc
```

Assembler: DASM (from Cadaver's page).

## All versions released

1. 1.00 — 15 Feb 2000 (first release)
2. 1.01 — 17 Feb 2000
3. 1.02 — 28 Feb 2000 (added hard restart)
4. 1.03 — 29 Feb 2000
5. 1.10 — 27 Mar 2000 (packer; new file format; filter table; multi-song)
6. 1.11 — 31 Mar 2000
7. 1.12 — 20 Mar 2001
8. 1.13 — 17 Apr 2001 (RLE save; $FF wave table special; final release)

**Source only available for 1.13.** The format changed at 1.10 (old 1.0x songs can be imported but not the reverse).
