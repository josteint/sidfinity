# SID Duzz'It — Scene Technical Notes and Miscellaneous Forum Findings

<!-- provenance
  sources:
    - url: https://chipflip.wordpress.com/2009/09/23/more-soundchip-hacking-realtime-sid-delay/
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      author: Goto80 (Anders Carlsson)
      content_date: 23 September 2009
      reliability: secondary (blog, quotes GT directly)
    - url: https://www.tumblr.com/vimster/9544145674/sid-duzz-it
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      author: vimster (anonymous blogger)
      content_date: unknown (circa 2011–2014 based on Tumblr era)
      reliability: low (end-user impression, not technical)
    - url: https://www.pouet.net/prod.php?which=59065
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: secondary (demoscene production database)
    - url: https://woolyss.com/chipmusic-chiptrackers.php?s=Sid+Duzz+It+(SDI)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: secondary (chiptracker catalogue)
    - WebSearch snippets (Lemon64 threads not directly accessible, 503)
      fetch_date: 2026-06-13
      reliability: low-medium (search-snippet fragments only)
    - url: https://www.atlantis-prophecy.org/recollection/?load=articles&id=TheBriefHistoryofSID
      fetched_via: WebFetch (two passes)
      fetch_date: 2026-06-13
      author: Jan Harries (SIDwave / Sidwave)
      content_date: Vandalism News #64, June 2015
      reliability: secondary
    - url: https://csdb.dk/release/?id=33645 (GT's Musiceditor 1992)
      fetched_via: WebFetch
      fetch_date: 2026-06-13
      reliability: high
-->

---

## 1. NTSC Support Claim

From a Lemon64 search snippet (thread t=24039, "SDI (SID Duzz It) question", ~2007,
exact poster name not recovered):

> "SDI 2.0 beta is the only C64 based editor known to officially support NTSC."

**Reliability:** Low-medium (search snippet from inaccessible thread). However, the SDI
official documentation (`SDI.2.1.6-docs.txt`) does confirm dual PAL/NTSC support via
the SPD50 (speed) player's raster count formula: PAL raster = 312/speed, NTSC = 262/speed.
The N50 player (singlespeed) fires once per VBI and is PAL-tuned by default.

**RE implication:** HVSC tunes tagged with non-PAL clock speeds may use the SPD50 player
variant rather than N50. The PSID `speed` flag (bit per subtune) indicates whether CIA or
VBI timing is used — for SDI this maps to N50 vs SPD50.

---

## 2. Multispeed Mechanism — Confirmed Details

Sources: SDI official docs + SourceForge description + search snippets from Lemon64/ChipMusic.

The SDI multispeed system:

- **Entry point:** `$1009` is the "Speed play" entry — "sound update only, for multispeed".
  The main play routine at `$1003` handles the sequencer (track + sequence advancement);
  the speed entry at `$1009` handles only the effect tables (waveform + pulse programs).
- **Effect on tables:** "Multispeed plays the tables faster, and it's only wavetable and
  pulseprogram that runs on speed." The filter and vibrato programs appear to run at
  normal 50 Hz rate (not speed-multiplied).
- **Per-channel control:** "CBM+* marks the channels you want to use multispeed on" —
  multispeed can be selective per voice, not necessarily applied globally.
- **Timer:** The SPD50 player uses the CIA timer (`SDI21-SPD50.asm`). The raster count
  formula: PAL speed N → fires N times per VBI. Speed 1 = 50 Hz, speed 2 = 100 Hz, etc.

**Confirmed from player source files** (already downloaded in `src/`):
- `SRC_SDI21-N50.asm` — singlespeed player (VBI-fired, 1999 lines TASS)
- `SRC_SDI21-SPD50.asm` — multispeed player (CIA-timed, 2006 lines TASS)

---

## 3. Hard-Restart and ADSR Context

From Jan Harries (SIDwave), "Brief History of SID" (Recollection, Vandalism News #64, 2015):

> "JCH was the gift to '90s, what Hülsbeck was to '80s."
> JCH is credited with inventing the "hard-restart" technique: "a coding method ensuring
> synthesized sounds begin from the waveform's starting point rather than mid-cycle,
> preventing sound failure."

SDI's "gate timeout" system (`$00-$1F`, `$21-$3F`, `$41-$7F` instrument encoding bytes)
implements the hard-restart mechanism in SDI. The V2.1.7 release notes fix a specific
gate-timeout bug:

> "Starting a composition with gatetimeout settings of Ax, Cx, or Ex could prevent the
> initial note from triggering properly."

And SIDWAVE's CSDb comment on V2.0 Beta 8:

> "Use this player, it is ADSR bugfixed" [referring to "SDI V2.07 Player ADSR Fixed"]

These are two different bugs in the ADSR/gate-restart chain, fixed at different versions.

---

## 4. Player Feature Flags — End-User Friction

The player assembly-time flags (`rem_pu`, `rem_arp`, `rem_fi`, `rem_vib`, `rem_glid`)
strip unused effects to reduce player size. They are **disabled by default** (set to 0,
meaning all features are included by default in the source — but the comment from Vincenzo
suggests the opposite; this needs verification against the actual source in `src/`).

**Vincenzo (CSDb, 30 October 2021):**
> "SDI is a great music editor but the struggle with compiling the music is... why are
> player features set to disabled in the code by default?"

This suggests that in some versions or distributions, the `rem_*` flags were set to 1
(remove = yes) by default, requiring users to set them to 0 to enable features. This is
counter-intuitive (a "remove" flag set to 1 removes the feature; 0 keeps it).

**Psylicium's Cheat Sheet (rev 3)** added "player flags and TASS shortcuts" specifically
because this was confusing to users.

**RE implication:** When extracting SDI tunes for the pipeline, care must be taken about
which features are actually used. The pipeline should inspect the player binary's feature
flags, not assume all effects are active.

---

## 5. GT's Musiceditor (1992) — Relationship to SDI

From CSDb release #33645 comments (Geir Tjelta, "GT", own comment):

**GT:**
> "Editor crashes sometimes when changing subtunes due to its unfinished state."
> "Jingle #7 is probably the best thing I've ever written."

The jingle #7 from GT's Musiceditor was reused as the level-complete sound in
**Daze Before Christmas** (SNES, 1994). This is unrelated to SDI but documents GT's
commercial game work alongside his scene activity.

**Format note:** GT's Musiceditor is a SEPARATE FORMAT from SDI. SIDID classifies it as
`GT_Editor`. The two tools share authorship only; the binary formats are unrelated.

---

## 6. Psylicium Manual Background

From the PDF manual's background section (see also `csdb_manual.md`):

> "SDI is a music tracker for the C64/C128, built on ideas from:
> - JCH/Vibrants editor
> - Olav Morkrid/Panoramic 'Digitalizer' editor
> - Geir Tjelta/Shape/Moz(ic)art SID Systems"

**Source reliability:** Psylicium (Henrik Mortensen) is a long-time SDI user who combined
the official docs with his own corrections. The "built on ideas" list appears in the manual
as a historical note; GRG's comment "Thanks for doing this. Much obliged." on the PDF manual
release implicitly endorses the manual's accuracy (he would have corrected major errors).

---

## 7. Pouet.net: V2.0 Release (prod #59065)

URL: https://www.pouet.net/prod.php?which=59065
Released: 2009 by SHAPE. Code by: 6R6.

User comments:

**Morden** (5 April 2012, 13:26:43):
> "More SID trackers? Yes, please."

**tomaes** (5 April 2012, 13:31:30):
> "I want to have at least the more important sid trackers in the database. There are
> still some left to add. :)"

**(451)** (24 September 2012, 05:37:02):
> "Keep up the great work! Can't wait for the MIDI support!!!"

Note: Only 6R6 is credited on Pouet for the V2.0 code (not GT). This is consistent with
CSDb's credit for V2.0 Beta 8 (6R6 + GT both credited); Pouet may have incomplete credits.

---

## 8. Woolyss Chiptracker Entry

URL: https://woolyss.com/chipmusic-chiptrackers.php?s=Sid+Duzz+It+(SDI)

> "A popular chiptracker for Commodore 64 (C64). It uses the SID (MOS Technology 6581)
> soundchip. Status: Free software. MIDI support: No."

Audio demo credited to Glenn Rune Gallefoss. The "MIDI support: No" reflects the V2.1.x
stable branch; the V3.0 MIDI Preview branch has MIDI support but was never released as
a stable version.

---

## 9. Hex Interface Observation (End-User Perspective)

From Tumblr post by "vimster" (anonymous, circa 2011–2014):

> SID Duzz It is "more a tracker-style editor" than a synthesizer interface.
> "The programmers managed to squeeze stacks of commands and whatnot into every byte."
> The program comes with "thorough documentation covering all aspects."
> "figuring out pulse table entries" was the primary initial learning challenge.

This confirms that the dense hex encoding of the program tables (each byte carrying
multiple meaning depending on nibble) is SDI's main user-facing complexity, consistent
with the format spec.

---

## Leads to Follow

- **Lemon64 thread t=31585 "SDI and SID files"**: The most likely source of ripping/export
  technical discussion. Retry when rate-limit expires.

- **Lemon64 thread t=67248 "Comparison of C64 Music Editors"**: Forum discussion around
  Chordian's table; will contain community debate on SDI vs. JCH vs. GoatTracker features.

- **forum64.de thread 46876 "Musik mit dem C64 machen"**: German forum, HTTP 403 blocked.
  May reference SDI (search snippet suggested it does). Try via a proxy or manual browsing.

- **ADSR/gatetimeout clarification**: The two known bugs — "SDI V2.07 Player ADSR Fixed"
  (V2.0 era) and V2.1.7's "gatetimeout Ax/Cx/Ex initial note" — should be verified by
  reading the actual player source in `src/SRC_SDI21-N50.asm` (the gate-timeout handling
  routine). This is an RE task.

- **Olav Morkrid / "Digitalizer" editor**: Named as SDI design influence. Search CSDb for
  `Olav Morkrid` or `Panoramic Designs` releases. Geir Tjelta was a Panoramic Designs
  member (Demozoo confirms). This connection may be earlier than Moz(IC)art.

- **GRG "tiny" player variants**: SIDID lists `GRG_tiny_1`, `GRG_tiny_2`, `GRG_tiny_3`,
  `GRG_tiny_4`. These are mini-players for demo use. Find on CSDb to understand which
  effects they drop — informs the minimum viable player feature set.

- **ChipMusic.org topic 10911 "wav table question"**: Discusses waveform program table
  details. Retry with a browser-like user agent (current 403 may be bot-blocking).
