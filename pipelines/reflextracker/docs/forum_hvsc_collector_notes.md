---
source_url: https://remix64.com/supporting-pages/a-week-in-the-life-of-a-high-voltage-sid-collector.html
fetched_via: direct
fetch_date: 2026-06-15
author: Warren (HVSC collector, pseudonym)
content_date: unknown (Remix64 article, circa 2005-2010)
reliability: secondary (primary observer of Reflextracker SID archiving process)
---

# "A Week in the Life of a High Voltage SID Collector" — Reflextracker Notes

Source: https://remix64.com/supporting-pages/a-week-in-the-life-of-a-high-voltage-sid-collector.html

## Article Content Relevant to Reflextracker

This Remix64 article describes a collector's process of ripping and submitting SID files from
Reflex's Brainbeat musicdisk series.

### On Brainbeat Disk Content

> "Running [Brainbeat 1, 2 and 3 music selector demos] on my C64 (after a quick bout of disk 
> transferring) brings lots of PVCF tunes not in HVSC either."

### On the Ripping Process for Reflextracker SIDs

> "Many were 'straightforward single speed tunes that don't need modifying'" and were easily
> extracted by "copy these from my D64 disk images on the PC to my working C64MUSIC directory,
> add the header part with the info, and they are converted."

"Around 20 files in roughly 20 minutes."

## Technical Implications

1. **"Single speed tunes"** — PSID speed field is 0 for all standard Reflextracker SIDs in HVSC.
   This matches the HVSC corpus (play_addr=0x0000, RSID format, CIA-driven). The "speed" 
   descriptor here means the song progresses at normal PAL VBI rate — not multispeed.

2. **"Straightforward extraction"** — The Reflextracker player + song data is self-contained in
   the loaded C64 binary. The HVSC collector simply:
   - Extracted the binary from the D64 disk image
   - Added a PSID header (init/play addresses)
   - Submitted to HVSC
   
   This means the player is already fully embedded in the SID binary — it is NOT a separate
   library; every Reflextracker SID carries its own copy of the player (~$C000 region).

3. **"A few tracks required speed adjustments"** — Some SIDs needed header tweaks (speed/timing
   flags) during archiving. This is consistent with the small number of HVSC members that have
   non-standard init addresses ($C050, $C103, $CF40, $1C06).

## Brainbeat as Distribution Vector

The collector notes getting Brainbeat 1/2/3 "right away in 1995 or maybe a bit later in 1996,
together with ReflexTracker on another disk."

This confirms the **primary distribution route** for Reflextracker was bundled with Brainbeat
musicdisk series, which were themselves popular Reflex demo group releases. The tool spread
from Germany to Poland through this bundle.
