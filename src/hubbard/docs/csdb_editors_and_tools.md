---
source_url: multiple
# https://csdb.dk/release/?id=75124
# https://csdb.dk/release/?id=66495
# https://csdb.dk/release/?id=222633
# https://csdb.dk/release/?id=129184
# https://csdb.dk/release/?id=101594
# https://www.lemon64.com/forum/viewtopic.php?t=8111
# https://www.lemon64.com/forum/viewtopic.php?t=62157
fetched_via: compiled from multiple sources
fetch_date: 2026-04-11
author: unknown (compiled from CSDb release pages and forum threads)
content_date: 1988-2017
reliability: secondary
---
# Rob Hubbard Format — CSDb Editors and Tools

## Overview

Several editors were built around Rob Hubbard's player engine by scene members in the late
1980s. Hubbard himself never used an editor — he composed by editing hex data directly in
his Mikro Assembler source code. These third-party tools wrap various versions of his player
with a composition UI.

## Editors on CSDb

### Rob Hubbard Editor by Moz(IC)art (1989)
- **CSDb:** https://csdb.dk/release/?id=75124
- **Author:** Predator (Moz(IC)art / SHAPE / Suppliers)
- **Player base:** ACE II variant (1987 driver, Phase 4)
- **Downloads:**
  - `predator_-_hubbard_editor.d64.gz` (579 downloads)
  - `Rob_Hubbard_Editor_with_example-Predator.d64` (223 downloads)
  - `rhed+docs.d64` (87 downloads) -- includes documentation file
- **Comments (all 8):**
  - GT (27 Jan 2009): "Rob Hubbards Ace 2 player. Many Moz(Ic)art tunes from 1989 were
    composed in this tool."
  - Conrad (2 Jul 2010): "Ace 2 player? The one from 1987? Well, you certainly pushed its
    limits if you made your 1989 tunes from it."
  - Stainless Steel (9 Dec 2012): "Just take a listen to 'Niggling' by geir from 1989 to
    hear what he squeezed out of that player. Total awesomeness."
  - mstram (8 Feb 2015): "Any docs 'hidden' on another release somewhere?"
  - SIDWAVE (8 Feb 2015): "press space to go into editor, f keys to switch voices/sound
    edit. its all made there, with codes, that nobody knows."
  - 4mat (8 Feb 2015): "There's a disassembly/description of Rob Hubbard's early routine
    on the net. Possibly some of the same control codes work in this though it uses a later
    revision of the player. I used that to convert Goat Tracker songs to the Hubbard format,
    much easier than writing in source."
  - mstram (8 Feb 2015): Referenced Laxity's post on CSDb release #122333 for format info.
    Described the editor as "very fragile" — locks up in VICE when fed invalid data. Also
    investigating BHT editor (#66495).
- **Forum thread (4 posts):** https://csdb.dk/forums/?csdbentrytype=release&csdbentry=75124&entrytopic=1
- **Key insight:** The ACE II driver uses table-based features. Many Moz(IC)art / Geir Tjelta
  tunes from 1989 were composed with this tool. Geir Tjelta's "Niggling" is cited as
  pushing the player to its limits.

### Robb Hubbard Music Editor V1.5 by Breakpoint Hacking Techniques (1989)
- **CSDb:** https://csdb.dk/release/?id=66495
- **Authors:** Greeny (BHT) and Huddy (Anticom Cracking Technique / BHT)
- **Music credit:** Rob Hubbard (Zoolook included)
- **Downloads:**
  - `Rob_Hubbard_Editor.D64` (976 downloads)
  - `The Robb Hubbard Music Editor V1.5.BHT.d64` (172 downloads)
- **Forum thread (7 posts):** https://csdb.dk/forums/?csdbentrytype=release&csdbentry=66495&entrytopic=1
- **Comments/Forum highlights:**
  - SIDWAVE (3 Feb 2015): CTRL key on Commodore = TAB on PC (VICE mapping). "No docs" exist.
  - SIDWAVE (8 Feb 2015): "No instrument page. You directly set waveforms+effects in this
    block, followed by notes."
  - mstram (8 Feb 2015): Asks about instrument page; confirms there is none from disassembly.
  - Acidchild (8 Nov 2017): Uploaded a version with an information file.
  - mstram (8 Nov 2017): Quotes the info file documenting the block format:
    ```
    85 01 30
    85 = duration (80-BF)
    01 = sound number (00-20)
    30 = pitch (00-60)
    FF = end of block
    ```
    A typical drum block: `85 00 2D 85 01 2D 83 00 2D 83 00 2D 85 01 2D FF`
    Note: The loaded example song contains hex codes beyond just '8x' range --
    presumably instrument definitions using different command bytes.
- **Key insight:** This is a VERY early/simple format -- just triplets of (duration, sound#,
  pitch) in hex blocks. No separate instrument page; waveform/effect data is inline. Different
  from the later table-based ACE II format used by Moz(IC)art editor.

### Rob Hubbard Music Editor by Mirror (1988)
- **CSDb:** https://csdb.dk/release/?id=222633
- **Released by:** Mirror (group)
- **SIDs included:** IK+ (`/MUSICIANS/H/Hubbard_Rob/IK_plus.sid`) and Star Paws
  (`/MUSICIANS/H/Hubbard_Rob/Star_Paws.sid`)
- **Download:** `RHME.d64` (110 downloads)
- **Notes:** No user comments. No forum posts. Minimal documentation. IK+ and Star Paws
  are both late-era Hubbard driver songs (1987), suggesting this editor wraps the later
  table-based driver variant. One of the earliest Hubbard editors (1988).

### The Rob Hubbard Sound Editor V2.0
- **CSDb:** https://csdb.dk/release/?id=129184
- **Type:** Listed as "C64 Crack" (not a tool)
- **Music credit:** Rob Hubbard
- **SIDs in memory:** Monty on the Run (`/MUSICIANS/H/Hubbard_Rob/Monty_on_the_Run.sid`)
  and Human Race (`/MUSICIANS/H/Hubbard_Rob/Human_Race.sid`)
- **Download:** `The_Rob_Hubbard_Sound_Editor_V2.d64` (369 downloads)
- **Comments (2):**
  - Fred (20 Feb 2014): "Doesn't seem to be a tool since you cannot do anything. In memory
    there is Monty on the Run music and music from The Human Race."
  - hedning (27 Sep 2015): "Not released by Amazing Cracking Conspiracy according to
    Cronos. Must be another ACC."
- **Notes:** NOT a functional editor despite the name. Classified as a crack, not a tool.
  No editing capability. Contains two Hubbard songs as data -- possibly a sound test or
  music player rip that was mislabeled as an editor.

### The Rob Hubbard Soundeditor V1.3 by Paradroid (1991)
- **CSDb:** https://csdb.dk/release/?id=101594
- **Author:** Paradroid (Online / Producing Cracking Service)
- **Release Date:** May 1991
- **Download:** `Hubbard.Edit.1.3-PAD.zip` (368 downloads)
- **Comments (1):**
  - iAN CooG (26 Aug 2011): "example songs are plain conversions from known hubbard songs,
    or songs using hubbard-derived players." Lists matches:
    - ROB.FEEBLE -> /MUSICIANS/T/Tjelta_Geir/Deceptive.sid (98%)
    - ROB.BANG.KNIGHTS -> /MUSICIANS/H/Hubbard_Rob/Bangkok_Knights.sid (76%)
    - ROB.ZOOLOOK MIX -> /MUSICIANS/T/Tjelta_Geir/Zoolook_mix.sid
    - ROB.I BALL -> /MUSICIANS/H/Hubbard_Rob/I-Ball.sid (80%)
    - ROB.MONTY ON RUN -> /MUSICIANS/H/Hubbard_Rob/Monty_on_the_Run.sid (79%)
    - ROB.FLASH GORDON -> /MUSICIANS/H/Hubbard_Rob/Flash_Gordon.sid (77%)
    - ROB.SHWAY RIDER -> /MUSICIANS/H/Hubbard_Rob/Shockway_Rider.sid (82%)
    - ROB.THANATOS -> /MUSICIANS/H/Hubbard_Rob/Thanatos.sid (90%)
    - ROB.DECEPTIVE -> /MUSICIANS/T/Tjelta_Geir/Complaisance.sid
- **Key insight:** This is the editor behind the `Paradroid/HubbardEd` SIDID signature.
  Paradroid built it around the Hubbard driver and bundled converted songs as examples.
  The example songs include both actual Hubbard originals AND Geir Tjelta tunes composed
  with the Moz(IC)art editor, confirming format compatibility between these editors.
  This is the "V1.3" -- there may have been earlier versions.

### BZ Utils Tape Editor (early, on cassette)
- **Source:** Lemon64 thread https://www.lemon64.com/forum/viewtopic.php?t=8111
- **Notes:** Distributed on BZPD range cassette. Built around the Zoolook tune. TMR
  (Lemon64): "it's on the CD in the Utils section" and "Hubbard himself never used a
  utility, he'd edit the data directly into the source code."

## Related Tools (Not Hubbard-Specific)

### Laxity Editor / TFA Editor (1989-1990)
- **CSDb:** https://csdb.dk/release/?id=122333 (v32-3.34), https://csdb.dk/release/?id=215790 (TFA v3.24)
- **Authors:** Laxity / The Flexible Arts
- **Notes:** These are Laxity's own player, NOT based on Hubbard's format. The TFA Editor
  is the precursor to later Laxity Editor versions. Mentioned in some discussions alongside
  the Hubbard editors but use a different data format.

### GoatTracker-to-Hubbard Converter (unreleased)
- **Source:** Lemon64 thread https://www.lemon64.com/forum/viewtopic.php?t=62157
- **Author:** 4mat (Jason Page)
- **Notes:** Converts GoatTracker compositions to Rob Hubbard's driver format. 4mat: "I
  always wanted to try out Rob's driver after hearing the great Judges and Demon demos in
  the '80s, but without having to compose directly in assembly." Video demo on YouTube.
  **NOT publicly released** — 4mat stated: "Not releasing this one as it was just a fun
  project."

### SIDdecompiler
- **GitHub:** https://github.com/Galfodo/SIDdecompiler
- **Author:** Stein Pedersen (Galfodo) / Prosonix
- **Notes:** Originally conceived as a Rob Hubbard plugin for the Prosonix SID tracker.
  Uses a tracing 6502 emulator to generate relocatable assembly. Hubbard tunes get
  enhanced label names for known data structures. Contains `STHubbardRipper.cpp` with
  Hubbard-specific pattern matching. See `github_siddecompiler_hubbard_ripper.md`.

## Complete Editor Inventory on CSDb

All known Hubbard editor releases found via CSDb search:

| Release ID | Name | Author | Year | Type |
|-----------|------|--------|------|------|
| 75124 | Rob Hubbard Editor | Predator / Moz(IC)art | 1989 | ACE II driver wrapper |
| 66495 | Robb Hubbard Music Editor V1.5 | Greeny+Huddy / BHT | 1989 | Block-triplet format |
| 222633 | Rob Hubbard Music Editor | Mirror | 1988 | Late driver (IK+/Star Paws) |
| 129184 | Rob Hubbard Sound Editor V2.0 | unknown (ACC?) | unknown | NOT an editor (music rip) |
| 101594 | Rob Hubbard Soundeditor V1.3 | Paradroid | 1991 | HubbardEd variant |

No CSDb results were found for "Hubbard source code", "Hubbard driver assembly", or
"Hubbard player routine" beyond the editor releases listed above.

## Key Takeaway for Decompiler Development

All functional editors use the SAME underlying data format documented in `data_format_reference.md`.
The player code varies between the "early" (~30 songs) and "later" (ACE II era) drivers, but
the fundamental data structures (8-byte instruments, variable-length note encoding, pattern/track
hierarchy) remain consistent. The editors are wrappers around specific driver binaries — they
don't define their own format.

The BHT editor (V1.5) reveals the simplest data encoding: duration-sound-pitch triplets in hex,
with $80-$BF for duration, $00-$20 for sound number, $00-$60 for pitch, and $FF for block end.
This aligns with the note encoding documented in the disassemblies.

The ACE II-based editors (Moz(IC)art editor) use the later 1987 driver with table-based drums
and PWM, which adds additional data structures beyond the early 8-byte instrument format.
These extensions are not well-documented publicly and would need reverse engineering from
the editor disk images.

The Paradroid Soundeditor V1.3 (1991) is the latest editor and bundles both real Hubbard
songs and Geir Tjelta tunes as examples, confirming full format compatibility between
the different editor variants.
