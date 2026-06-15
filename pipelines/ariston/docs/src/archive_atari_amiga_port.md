---
source_url: https://www.atari-forum.com/viewtopic.php?t=21588 ; http://www.atarimania.com/list_games_atari-st-beben-wally-hagar_team_1775_S_G.html
fetched_via: direct 2026-06-15
fetch_date: 2026-06-15
author: Atari Forum community; Atarimania
content_date: thread from ~2004; database ongoing
reliability: secondary
---

# Ariston — Atari ST and Amiga Port (1988)

## Background

In 1988, Wally Beben ported the Ariston music system to Atari ST and Amiga.
The port was done with the help of "a very good friend, game programmer Chris from
Bury St Edmunds, Suffolk" (per VGMPF Ariston article).

Key fact: Wally Beben **lost all ST and Amiga music driver source code** in hard drive
failures. This is documented in the Atari Forum thread (t=21588) where community members
tried to reconstruct the format.

## Atari Forum Reverse-Engineering Thread (c. 2004)

Thread: "Wally 'Hagar' Beben's music driver" — https://www.atari-forum.com/viewtopic.php?t=21588

Key participants:
- **Mug UK** — reverse-engineered Beben's R-Type music replayer (~2004)
- **Xerud** — created "rips" of Beben compositions from memory addresses
- **Maartau** — modified Mug UK's original code rip

Key quote: "However, not being a musician, I wouldn't have a clue about how his note
data is stored." — indicating the format was partially recovered at code level but
the data format was not fully understood.

Status: Partial reverse-engineering; driver code recovered but data format not
documented in the thread.

## Atarimania — Wally Beben Atari ST Game Credits (72 titles found)

The Atarimania database (atarimania.com/list_games_atari-st-beben-wally-hagar_team_1775)
lists 72 Atari ST games credited to Wally Beben, including (partial list from page 1):
- Ball Game (The)
- Circus Games
- Dark Side (1988 Incentive — this is the same SID analysed in Ariston.dis)
- Elite
- Foundations Waste
- Future Sport
- Hammerfist
- Hawkeye
- Hellraiser
- Hyperdome
- I, Ball
- Lancaster

Dark Side specifically confirms the cross-platform connection: the C64 version uses the
Wally_Beben Ariston variant (per the JC64dis disassembly of Dark_Side.sid), and the
Atari ST version was composed by Beben using his ported player.

## Amiga Workflow

From VGMPF/Wally Beben:
"Beben wrote music initially using soundtracker, for which he had written a little
program to convert the data into blocks that he could use within his own player that
he'd migrated/converted from his C64 player. He found it difficult using soundtracker
stuff in those days since memory was at a premium, and using self-penned player code
was always the most efficient both in terms of processor usage and memory."

This means:
- Amiga music data was authored in Soundtracker (ProTracker-style MOD format)
- Beben's conversion tool produced a proprietary block format
- A custom Amiga player (derived from the C64 Ariston player) played back these blocks

The Amiga format is therefore NOT a standard MOD/IFF/TFMX format — it's a custom
Ariston-derived format specific to Beben's tool. It will not appear in ModLand/UADE
under a standard name.

## Atari ST Format Status

The ST replayer code was partially reverse-engineered (Mug UK, ~2004) but:
- Note data format not documented
- Source code lost by author
- Format not in SNDH/SC68 catalogues under an "Ariston" name
- ExoticA/UnExoticA access blocked (Cloudflare) — unable to verify listing

## Search Status

- ExoticA.org.uk: Cloudflare-blocked, no content accessible
- ModLand: Not searched directly (would require http://modland.com browser access)
- UADE format list: Not searched directly
- Atarimania: 72 titles found but no format documentation

The ST/Amiga Ariston port format remains undocumented in publicly available archives.
Further investigation requires direct access to one of the 72 ST game executables
and memory-dumping the music data at runtime.
