---
source_url: https://www.lemon64.com/forum/viewtopic.php?t=77549 ; https://www.lemon64.com/forum/viewtopic.php?t=72438 ; https://amazingdiy.wordpress.com/projects/quadsid/
fetched_via: direct (all three)
fetch_date: 2026-06-15
author: Multiple Lemon64 users; amazingdiy blog author
content_date: 2015-2020 (Lemon64 threads); 2005 (amazingdiy build)
reliability: secondary
---

# QuadSID Context for Reflextracker Research

## Background: What is QuadSID?

From the Lemon64 "Any quad SID demo's running around?" thread (t=77549):

- **"QuadSID"** in C64 scene context = 4 SID chips in one machine
- Common multi-SID address maps: D400, D420, D500, D520 (or configurable via jumpers)
- User Chordian: "There are several 4SID, one 8SID and even one 10SID. And a ton of 2SID and 3SID."
- Standard PSID format "only supports up to 3 SIDs" (3SID = PSID v3)
- PSID v3+ multi-SID SIDs do exist in HVSC but are very rare

## QuadSID Hardware (2005 Build)

From amazingdiy.wordpress.com:
- QuadSID = 4 SID chips in a C64 breadbox
- Controlled via full Midibox SID control surface
- MIDI-based command interface
- This is a HARDWARE project; unrelated to Reflextracker's "QuadSID" mode

## PVCF's QuadSID in Reflextracker Context

PVCF's statement (Lemon64 thread #4872, 2003-06-30):

> "its a reflextracker (PC) song, with quadrasid. it only can be recorded as a midi stream."

This refers to a **PC-side simulation of QuadSID** within Reflextracker:
- Reflextracker on PC can compose with up to 10 SID voices
- On PC, this is simulated (multiple SID emulators running simultaneously)
- Exporting to real C64 hardware requires physical multi-SID hardware
- The only export that preserves the multi-SID content is "as a MIDI stream" (recording to MIDI)
- Standard .SID format cannot carry multi-SID data for >3 chips

## What "Up to 10 Channels" Means

PVCF's "Bladeswede" example: "up to 10 channels to 3 channels" reduction.
- 10 channels = likely 3 SID chips × 3 voices + 1 extra = 10, or 4 chips × 2-3 voices
- 3 channels = standard C64 single-SID output
- The reduction is manual recomposition using DMC + Polonus digieditor

## Reflextracker in HVSC = Single-SID Only

All 137 Reflextracker SIDs in HVSC are single-SID (PSID v1/v2, no multi-SID header).
The QuadSID capability of Reflextracker has NO representation in HVSC's archived collection.

## Multi-SID Addressing

From Lemon64 thread #72438 (multi-SID trackers):
- SID-Wizard supports 3SID
- Standard 3SID address: $D400, $D500, $D420 (or variations)
- Reflextracker (according to this thread) is not mentioned as a multi-SID tracker available
  for contemporary use — it is primarily historical

## Takeaway for USF Pipeline

The Reflextracker USF pipeline targets only the single-SID corpus (all 137 HVSC members).
The QuadSID format is unarchived and would require:
1. A multi-SID Reflextracker project file (not a .SID file)
2. Hardware-specific address maps for 4+ SID chips
3. A USF extension for multi-SID (not yet designed)

This is out of scope for the initial migration.
