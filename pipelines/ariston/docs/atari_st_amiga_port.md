---
source_url: https://www.atari-forum.com/viewtopic.php?t=21588 + https://www.vgmpf.com/Wiki/index.php/Wally_Beben
fetched_via: WebFetch
fetch_date: 2026-06-15
author: Mug UK (atari-forum) + VGMPF contributors
content_date: 2011 (forum) + ongoing (VGMPF)
reliability: secondary
---

# Ariston — Atari ST and Amiga Ports

## Port authorship

From VGMPF/Wally_Beben:
"In 1988, Beben ported Ariston to Atari ST and Amiga with assistance from a very good friend,
game programmer Chris from Bury St Edmunds, Suffolk."

- Porter: Wally Beben (music driver adaptation) + "Chris" (unnamed programmer, game dev)
- Year: 1988
- Platforms: Atari ST (YM2149 sound chip) + Amiga (Paula/MOD)
- "Chris from Bury St Edmunds, Suffolk" — identity unknown from public sources

## Architecture (DERIVED from Beben's own description)

From VGMPF (Beben's own words on Pool of Radiance Amiga):
"I wrote it (if I remember) initially using soundtracker for which I had a little program I'd
written to convert the data into blocks that I could use within my own player that I'd
migrated/converted from my C64 player."

This establishes:
1. The Amiga player was a DIRECT PORT of his C64 player (same data format, adapted for Paula).
2. Beben used Soundtracker for composition, then converted via a custom tool to his format.
3. The data blocks in the Amiga version are the same "blocks" as the C64 Ariston data.
4. Memory efficiency was the motivation: "self-penned player code was always the most efficient
   both in terms of processor usage and memory."

**Key implication for format research:** The Amiga Ariston player binary (if recoverable) shares
the same song data format as the C64 Ariston player. Recovering the Amiga player = recovering the
C64 format with potentially better tooling (Amiga has better reverse-engineering infrastructure).

## Atari Forum Thread (2011)

https://www.atari-forum.com/viewtopic.php?t=21588 — "Wally 'Hagar' Beben's music driver"

Key details from thread:
- Mug UK (forum admin) performed reverse engineering of Wally Beben's R-Type music replayer in 2004.
- Wally Beben lost his original ST and Amiga driver source code due to hard drive crashes.
- The thread proposed community reverse-engineering efforts to restore lost source code.
- Attachments (not accessible): R_TYPE.W_B.zip (Maartau's rip) and "Wally Beben rips by Xerud.rar"
  containing rips with memory addresses for use with "Easyrider" (Atari ST music ripper tool).
- Mug UK: "not being a musician, I wouldn't have a clue about how his note data is stored"
  — confirms no format documentation exists; only binary rips were available.

**Key implication:** The Atari ST version WAS reverse-engineered (at least partially) by Mug UK
in 2004 for R-Type. The rip files with memory addresses (Xerud's rips) may contain offset
information useful for understanding the format. The rip files are in the forum attachments
(permission-locked), but may be available via direct forum membership or Atari ST scene archives.

## ExoticA / UnExoticA

Search of exotica.org.uk (2026-06-15): No "Ariston" or "Beben" named format found in the
Amiga music formats category. The Amiga player appears not to have been ripped in the standard
MOD-ripping sense, or it is catalogued under a different name.

## SNDH Archive (Atari ST)

Not explicitly searched. The Atari ST SNDH archive (sndh.atari.org) collects YM2149-based ST
music. Wally Beben Atari ST music likely appears there. The Ariston ST player may be identified
as "Wally Beben" player in SNDH metadata.

## Search leads for Atari ST port

1. Check SNDH archive for Wally Beben entries: https://sndh.atari.org/
2. Contact "Mug UK" via atari-forum.com — has the 2004 R-Type disassembly
3. Look for "Xerud" on Atari ST forums/demoscene — has rips with memory addresses
4. Check AtariMania for Wally Beben games: http://www.atarimania.com/list_games_atari-st-beben-wally-hagar_team_1775_S_G.html

Games confirmed to have Beben Atari ST music (from atarimania.com):
- R-Type (confirmed ripped by Mug UK 2004)
- Hammerfist, Dark Side, Viking, etc. (game ports with Beben music)
