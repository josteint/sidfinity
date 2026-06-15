---
source_url: https://www.atari-forum.com/viewtopic.php?t=21588
fetched_via: direct
fetch_date: 2026-06-15
author: Mug UK (thread starter), community contributors
content_date: ~2011 (thread opened)
reliability: primary (direct community reverse-engineering discussion)
---

# Wally Beben's Atari ST Music Driver — Atari-Forum Thread

## Thread summary

Thread title: "Wally 'Hagar' Beben's music driver"
Opened by: Mug UK (forum administrator)
Context: A 2004 reverse-engineering effort by Mug UK on Beben's R-Type Atari ST
replayer was shared and a call was made for community collaboration to recover
other tunes.

## Key findings

1. **Source code lost:** Beben confirmed to the community that he "lost all of
   his ST (and Amiga) music driver source code a long time ago with various
   h/drive crashes."

2. **Reverse-engineering material exists:**
   - "Maartau's revised version" of the R-Type music replayer rip
   - "Xerud's collection" of other tune extractions with memory addresses
     documented for the Easyrider debugger
   - Attachment: R_TYPE.W_B.zip, Wally Beben rips by Xerud.rar
   (These attachments require forum login; content not directly accessible.)

3. **Note data format unclear:** Mug UK states: "not being a musician, I
   wouldn't have a clue about how his note data is stored." This indicates
   the Atari ST variant's note encoding is not publicly documented.

4. **Goal:** Community hoped to reverse-engineer other Beben compositions
   and restore them to source-code format, analogous to the R-Type work.

## Implication for C64 Ariston research

The Atari ST player is described as a direct port of the C64 Ariston player.
Beben said he "migrated/converted from my C64 player." The fact that the
note data structure was opaque even to reverse engineers in 2011 suggests
the Ariston format is a custom binary encoding, not a documented tracker
format. Understanding the Atari ST port's memory layout could cross-illuminate
the C64 binary format.

## Related links

- Atari ST games by Wally Beben: http://www.atarimania.com/list_games_atari-st-beben-wally-hagar_team_1775_S_G.html
- Atari ST demos by Wally Beben: https://www.atarimania.com/list_demos_atari-st-beben-wally-hagar_team_1775_S_D.html
- AMP entry: https://amp.dascene.net/detail.php?view=8087 (13 modules listed;
  no interviews; AddWare Ltd. affiliation; handles: Hagar, Wal Beban)
