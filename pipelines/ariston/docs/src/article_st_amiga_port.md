---
source_url: https://www.atari-forum.com/viewtopic.php?t=21588
fetched_via: direct
fetch_date: 2026-06-15
author: Mug UK (original 2004 RE); Maartau (revised version)
content_date: 2011 (forum post date); original RE 2004
reliability: secondary (forum post; attachments not publicly readable)
---

# Atari ST Wally Beben player reverse engineering — atari-forum.com

## Summary

Thread at atari-forum.com/viewtopic.php?t=21588 documents a reverse
engineering effort of Wally Beben's R-Type music player on the Atari ST.

Key facts:
- Original RE done in 2004 by "Mug UK"
- Primary target: the R-Type ST music replayer ("Wally B's R-Type music replayer")
- Maartau released a modified version of the RE'd source
- Xerud ripped other Beben tunes from their respective ST games
- Memory addresses documented for "Easyrider" debugger use

## Technical limitations of this source

- Actual source code is in file attachments not accessible in the page text
- The original poster notes "not being a musician, I wouldn't have a clue
  about how his note data is stored" — so the note/data format was NOT fully
  decoded in 2004/2011

## Connection to C64 Ariston

From Wally Beben (VGMPF, Wally_Beben page):
"I wrote it initially using soundtracker for which I had a little program I'd
written to convert the data into blocks that I could use within my own player
that I'd migrated/converted from my C64 player."

This confirms:
1. The ST/Amiga player is a 68000 port of the C64 6502 player code
2. The data format was partially converted from Soundtracker MOD blocks
3. The conversion tool was custom-written by Beben

Beben lost all ST/Amiga music driver source code in hard drive crashes,
making RE the only recovery path.

## Implications for C64 reverse engineering

If the ST player is architecturally a port of the C64 player, a successful
ST RE would reveal the C64 data format. The R-Type ST RE (2004 by Mug UK)
is the most accessible prior work.

The ST YM2149F has 3 voices + noise (vs SID's 3 voices + filter). The
frequency encoding would differ (YM register values vs SID frequency words).
But structural elements (channel loop, instrument tables, pattern/sequence
ordering) would be shared.
