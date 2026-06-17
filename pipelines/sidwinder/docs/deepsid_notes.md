---
source_url: https://deepsid.chordian.net + https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/
fetched_via: WebFetch direct
fetch_date: 2026-06-17
author: Chordian (Thomas Eberle)
content_date: 2018 (editor comparison post) / ongoing (DeepSID)
reliability: secondary
---

# SidWinder — DeepSID / Chordian Findings

## DeepSID player detection

DeepSID's main page and its embedded documentation contain **no mention of
SidWinder** as a named player type. The site's player-detection system focuses
on runtime emulator selection (reSID, JSIDPlay2, WebSid, Hermit, ASID) rather
than composer/editor classification, so engine names like SidWinder would not
necessarily appear in DeepSID's UI documentation.

DeepSID does display HVSC sidid engine tags when browsing individual SID files
(shown in the file info panel). A SidWinder-classified SID browsed in DeepSID
would show "SidWinder" as the engine label — this is sourced from HVSC's sidid
classification, not DeepSID's own detection.

## Comparison of C64 Music Editors (blog.chordian.net, 2018)

The 2018 comparison article lists editors evaluated by the author, including:
Blackbird, DMC, DefleMask, SID Duzz It, SidTracker 64, GoatTracker.
**SidWinder is absent from this list.** The author notes the table was frozen
and would not be updated further; later additions are managed within DeepSID
itself.

This absence is consistent with SidWinder's obscurity outside the
Hungarian/Central-European demoscene: the tool was coded 1994, unreleased until
1999 V01.22, then GPL'd as V01.23 in 2000 — by which time the C64 scene was
much smaller. Only 117 HVSC SIDs carry the SidWinder tag, concentrated among
a small number of composers (Factor6, Luca, Taki, Eclipse).

## Plus4World entry

Plus4World (`plus4world.powweb.com/software/SIDwinder_V01_23`) carries a
catalogue entry for SIDwinder V01.23 and identifies it as:

- Music composer package with editor, packer, and ASCII viewer
- Up to 32 subtunes in one file; up to 96 sectors (256 instructions/sector);
  up to 64 instruments; up to 16x music speed
- Adapted for Plus/4 (with SID card at $fd40) by Levente Hársfalvi (TLC) of
  Coroners
- Original C64 author: Balázs Takács (Taki / Natural Beat), Hungary
- PAL only
- GPL licensed (V01.23)

## PlanetEmu entry

PlanetEmu (`www.planetemu.net/rom/commodore-c64-applications-d64/sidwinder-v01-23-1994-natural-beat`)
hosts the D64 disk image as a 72 KB archive. The "(1994)" in the filename refers
to the player's creation year (coded 1994), even though first public release was
1999.

## Key gap

No DeepSID-specific SidWinder technical notes, player-detection threshold, or
SID count were found. DeepSID does not publish a structured engine catalogue
with per-engine statistics (unlike HVSC's `Musicians.txt`/sidid).

## Leads to follow

- Browse a concrete SidWinder SID in DeepSID to confirm the engine label is
  displayed:
  `https://deepsid.chordian.net/?file=MUSICIANS/T/Taki/Speed_Up.sid`
- Chordian maintains SID Factory II as a separate C64 music editor
  (`blog.chordian.net/sf2/`) — no connection to SidWinder found.
- SID Preservation project (`sidpreservation.6581.org/sid-trackers/`) lists
  several trackers but does NOT mention SidWinder as of the fetched content.
  May be worth a targeted search on that site for updates.
