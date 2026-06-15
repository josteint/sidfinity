---
source_url: https://chipflip.wordpress.com/2009/07/06/interview-with-soundemon-the-sound-chip-hacker/
fetched_via: direct
fetch_date: 2026-06-15
author: chipflip.wordpress.com (interviewer unknown), SounDemoN (Otto Järvinen)
content_date: 2009-07-06
reliability: secondary (interview, 2009)
---

# ChipFlip Interview with SounDemoN (2009) — OdinTracker Usage

Source: https://chipflip.wordpress.com/2009/07/06/interview-with-soundemon-the-sound-chip-hacker/

## Key quote on tools used

> "I don't even have my own software. When using my own routines I just use
> Turbo Assembler to edit the player source and music data."

SounDemoN states he does NOT use tracker software as his primary tool —
he hand-assembles music data. This context is important for understanding
his OdinTracker involvement.

## Implication for OdinTracker corpus

SounDemoN is credited with music in OdinTracker 1.11, 1.12, and 1.13 releases
(on CSDb). This was likely collaboration/demonstration music written for Zed's
tracker releases, not his primary composition workflow.

The 50 OdinTracker-classified SIDs attributed to SounDemoN in HVSC may have
been composed with OdinTracker (as demo/example compositions) rather than
with his hand-assembled technique — or they may have been imported/embedded
from other tools. This creates uncertainty about whether these SIDs represent
"typical" OdinTracker usage patterns.

## Context on SounDemoN

- Finnish C64 musician
- Notable for "4 rasterline player" (per CSDb CyberBrain note)
- Groups: Church 64, Dekadence, Onslaught
- The 2009 interview predates his use of Turbo Assembler as his only tool

## Relevance to USF conversion

SounDemoN's 50 SIDs (~31% of the OdinTracker corpus) are a major fraction.
If these are genuinely OdinTracker-produced (the sidid signature confirms the
player is embedded), they should be convertible via the standard vplayer
extraction path. His "own routines" comment suggests he may have sometimes
REPLACED the vplayer with his own player while keeping the OdinTracker
music data format — but the HVSC sidid classification confirms the vplayer
signature is present in his classified SIDs.
