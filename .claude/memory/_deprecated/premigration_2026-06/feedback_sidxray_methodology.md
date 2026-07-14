---
name: Update sidxray methodology when cracking players
description: When reverse-engineering a player, read METHODOLOGY.md first and update it with new findings after
type: feedback
---

When working on reverse-engineering any SID player (for building X→USF converters):

1. **Before starting**: Read `src/sidxray/METHODOLOGY.md` for the current heuristic
2. **While working**: Use sidxray as the primary tool, follow the methodology steps
3. **After cracking**: Add a "Lessons Learned: PlayerName" section with what worked, what failed, and any new techniques discovered

**Why:** We spent hours on GT2 with static analysis before discovering that memtrace co-occurrence analysis was the reliable approach. The methodology captures these hard-won insights so we don't repeat mistakes.

**How to apply:** Any time the task involves parsing a new player format, understanding a player's data layout, or debugging an X→USF converter.
