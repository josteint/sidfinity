---
source_url: multiple — see per-section source URLs
fetched_via: WebFetch/WebSearch
fetch_date: 2026-06-15
author: various (Allister Brimble, Matt Gray, Barry Leitch, etc.)
content_date: varies (2001–2020 interviews)
reliability: secondary (composer recollection in interviews)
---

# Ariston — Composer Testimony

Gathered from interviews and wiki pages. No composer has published detailed technical
documentation of the Ariston format. The summaries below are what is publicly available.

---

## Allister Brimble

**Source:** https://remix64.com/interviews/interview-allister-brimble.html (interview 2001ish)
**Source:** https://www.c64-wiki.de/wiki/Interview_mit_Allister_Brimble
**Source:** https://www.vgmpf.com/Wiki/index.php/Allister_Brimble

Key quotes (paraphrased from interview summaries — originals not reproducible verbatim due to
access restrictions, but the following is the factual record as returned by WebFetch):

- Initially used **Wally Beben's driver** (= the Ariston Wally_Beben variant) "with his permission."
  Brimble received "software where he could type notes in one at a time" from Beben.
  This means the Ariston/Beben player required entering music data as numbers/labels directly
  in assembly — there was no interactive editor in Beben's version.
- Later switched to the Ariston Music Editor (Brabbin GUI) described by VGMPF as: "First, Brimble
  used Ariston, and later, a driver and editor written for him by his friend Michael Delaney."
- In the C64-Wiki interview: Brimble described his C64 workflow as composing on Amiga and
  "copy the notes by hand into a C64 assembler, taking care to optimize the song data for best
  memory usage."
- He confirmed using "ADSR's, drum tables, vibrato's, filters" — features his later (Delaney)
  editor exposed explicitly. These same capabilities existed in Ariston/Beben but were less
  accessible via the assembly workflow.
- Confirmed Ariston SIDs: Mean_Machine, Panic_Dizzy, Prince_Clumsy, Slightly_Magic (4 SIDs).

**Technical implication:** Brimble used Beben's assembly version of Ariston (no GUI),
entering note data as hex numbers into the assembler source. This confirms the "assembler-first"
workflow attested by VGMPF for the Ariston engine generally.

---

## Matt Gray

**Source:** https://www.vgmpf.com/Wiki/index.php/Matt_Gray (wiki summary)
**Source:** Matt Gray interviews on Arcade Attack, Retro Games Master (no Ariston mention in text)

VGMPF states: "Initially, Gray used Soundmonitor and the Ariston driver, sometimes optimized by
game programmers and at that sometimes with declined quality. Soon after, the founders of
Codemasters convinced him to write his own driver."

- Gray used Ariston early in his career, before writing his own driver for Codemasters.
- He jammed on a "Casio MT-45 and typed the data in assembly" (Retro Games Master interview) —
  confirming the assembler-input workflow.
- The "sometimes optimized by game programmers with declined quality" comment suggests the Ariston
  player was being modified/integrated by each game's developer, sometimes with bugs introduced.
- Ariston Gray SIDs in HVSC: Fruit_Machine_Simulator, Mean_Streak_Loader, Quedex (9 subtunes),
  Mean_Streak_v1.

---

## Barry Leitch

**Source:** https://www.vgmpf.com/Wiki/index.php?title=Barry_Leitch
**Source:** https://www.gamedeveloper.com/audio/interviewing-veteran-composer-barry-leitch-part-ii-*

VGMPF states (verbatim): "On Marauder (C64), the driver was Ariston. It is unknown how he got it."

- Only 2 Ariston SIDs: Captain_Courageous, Marauder [6 subtunes].
- Barry Leitch has given multiple interviews but none (fetched 2026-06-15) mention Ariston by name.
- The general comment "by the time we got our music drivers to sound professional enough it was
  too late in the day" (Remix64 interview) suggests he quickly moved to other tools.

---

## Jonathan Dunn

**Source:** https://www.vgmpf.com/Wiki/index.php/Jonathan_Dunn
**Source:** https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=92 (interview)

VGMPF states: "On his first two games (of which Subterranea was delayed), the music driver is
Ariston, and the sound effect driver is likely Dunn's own."

From interview (Recollection #3): Dunn mentions he used Martin Galway's driver first at Ocean,
then Paul Hughes' driver — but does NOT mention Ariston by name. The wiki attribution is based on
SID analysis, not Dunn's own testimony.

- Ariston Dunn SIDs in HVSC: Matchday_II, Subterranea (2 SIDs).

---

## Steve Barrett

**Source:** https://www.vgmpf.com/Wiki/index.php?title=Steve_Barrett
**Source:** https://remix64.com/interviews/interview-steve-barrett.html

VGMPF states: "Barrett used Ariston." and "For most of his work, Barrett programmed his own
format, SB."

- Barrett used Ariston early (likely for game work), then developed his own "SB" format.
- 21 Ariston SIDs in HVSC (largest single-composer Ariston count after Wilson and Beben).
- Interview (Remix64): Barrett mentions using Electrosound initially (1986), then his own tools.
  No Ariston mention in interview text.

---

## Wally Beben

**Source:** https://www.vgmpf.com/Wiki/index.php/Wally_Beben

VGMPF (verbatim): "Beben helped Ian Crabtree to write Ariston."
"In 1988, Beben ported Ariston to Atari ST and Amiga with assistance from a very good friend,
game programmer Chris from Bury St Edmunds, Suffolk."

Beben on his Amiga composition workflow (from VGMPF, for Pool of Radiance):
"I wrote it (if I remember) initially using soundtracker for which I had a little program I'd
written to convert the data into blocks that I could use within my own player that I'd
migrated/converted from my C64 player."

- Confirms the Amiga/ST player was DERIVED from the C64 Ariston player.
- Beben wrote a converter from Soundtracker format to his own player's data blocks.
- This means the Amiga/ST version shared the SAME player architecture as C64 Ariston, just
  running on the ST/Amiga with YM/Paula hardware instead of SID.
- Beben's SID chip usage: "used the SID chip's unstable filter on only one game, namely
  Total Eclipse (C64)" — selective use of advanced SID features.

**Key Maniacs of Noise interaction (VGMPF):**
"In late 1987, Maniacs of Noise asked Beben how he did the 'phasing' effect. After Beben
sent them the source code, they added better drums and sent it back."
This is documented in sidid signatures as the Wally_Beben variant.

---

## Allister Brimble on Ariston vs Wally Beben's Driver (disambiguation)

IMPORTANT: Multiple sources conflate "Ariston" with "Wally Beben's driver." They are the SAME
engine. Brimble explicitly received Beben's version of Ariston (i.e., the Wally_Beben variant
with phasing), not the earlier Crabtree-only version. When sources say "Brimble used Wally
Beben's driver," that IS Ariston. The sidid Wally_Beben sub-fingerprint covers Brimble's SIDs.

Confirmed by sidid signature scan: Mean_Machine.sid → has Ariston primary + Wally_Beben sub-sig.

---

## No Composer Has Published Format Documentation

As of 2026-06-15:
- No composer interview describes the binary format (instrument table layout, command bytes,
  effect codes, note encoding).
- The VGMPF pages contain no format specification.
- The CSDb crack releases are binary-only (no source, no format docs).
- The closest to format documentation is the sidid.cfg signature analysis (see
  sidid_signature_analysis.md and github_cadaver_sidid.md).
- The JC64dis tool (https://iceteam.itch.io/jc64dis) has an Ariston example project
  (Dark Side by Wally Beben, 1988 Incentive) in its doc/example/ directory, but the .dis
  file is a JC64dis binary project format (gzip-compressed), not a text disassembly.
  The example can be opened in JC64dis to produce a disassembly.
