---
source_url: https://www.lemon64.com/forum/viewtopic.php?t=20873
fetched_via: direct
fetch_date: 2026-06-17
author: Multiple (Lasse Öörni "Lasse" and scene community)
content_date: 2006-08-30 to ~2011
reliability: primary
---

# Lemon64 Forum: NinjaTracker V2.0 Thread

Source: https://www.lemon64.com/forum/viewtopic.php?t=20873

## Initial Release Announcement (Lasse, 30 Aug 2006)

Lasse announced: "New version (actually totally rewritten) of the quite minimal
C64 music editor. May be even somewhat easier to use."

He noted the playroutine performance trade-off:
"Of course the playroutine is slower than the previous versions"

Download link provided: http://covertbitops.c64.org/tools/ninjatr2.zip

Lasse mentioned example compositions were converted from GT2 format and welcomed
higher-quality contributions.

## Version Updates (Sep 2-3, 2006)

V2.01 & V2.02 released with editor improvements. V2.02 warning:
"slightly slower and bigger playroutine."

V2.03 featured "sexy hardrestart" and attempted rastertime optimization, though
"the player is yet bigger."

Downloads (per forum posts at the time):
- http://covertbitops.c64.org/tools/ninjatr201.zip
- http://covertbitops.c64.org/tools/ninjatr202.zip
- http://covertbitops.c64.org/tools/ninjatr203.zip

### Attack fluctuation handling
Lasse explained: "hides the fluctuation of the attack by using silent first
frame of note."

## Design Philosophy (from Page 3 discussion)

Lasse explained NinjaTracker V1's original purpose:
"Ninjatracker V1's original purpose was to provide low-rastertime, low-memory
music for MW4 [Metal Warrior 4], and in such way that the playroutine was stored
only once within the game code."

On the "raw" design philosophy:
"The basic version should remain quite raw and encourage customization."

## Community Context

The tool was praised specifically for game development use cases:
- Rastertime savings critical for demo/game coders sharing VBI with game logic
- The "gamemusic mode" (shared playroutine, many data modules) designed for
  games with many music tracks (the specific use case: MW4)

## Download History (per CSDb)

V2.0 downloads: ~817
V2.03 downloads: ~1330 (most downloaded V2 sub-version before V2.04)
V2.04 downloads: ~1118

## Technical: Player Interface (from nt2play.s NFO description)

Normal mode:
- Playroutine saved with musicdata
- Standard calls for init and playback
- Requires 2 bytes of zero-page memory

Gamemusic mode:
- Choose startaddress; playroutine is NOT saved with music data
- Saves diskspace in a game with many music modules (one shared player)
- This is the mode designed for MW4-style game usage

## Related Thread: "New minimal music player (Ninjatracker 1 style)"
URL: https://www.lemon64.com/forum/viewtopic.php?t=67012
Date: Feb 5, 2018

Lasse announced miniplayer (later miniplayer2) as spiritually inspired by
NinjaTracker V1 style. Key facts:
- 9 rasterlines max (NinjaTracker V1: 11 rasterlines)
- Conversion tool from GT2 format included
- Sound FX support: PLAYER_SFX configuration variable
- Forum context: this is a CROSS-PLATFORM player (not a native C64 editor)
  built from the same philosophy as NinjaTracker V1
