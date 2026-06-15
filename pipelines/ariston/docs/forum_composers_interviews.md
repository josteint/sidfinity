---
source_url: multiple (see per-section headers)
fetched_via: direct
fetch_date: 2026-06-15
author: various interviewers/forum participants
content_date: 2000s–2020s
reliability: primary (direct composer statements) / secondary (wiki summaries)
---

# Ariston Composer Interviews and Forum Discussion Synthesis

This document collects statements from composers who used the Ariston driver,
drawn from interviews, forum threads, and wiki pages. No single forum thread
was found that discusses Ariston as a subject; information comes from
incidental mentions in composer profiles and interviews.

---

## Allister Brimble

Sources:
- https://remix64.com/interviews/interview-allister-brimble.html
- https://www.vgmpf.com/Wiki/index.php/Allister_Brimble
- Various (Retro Hour, RVG, Baker76 — no Ariston mention in those)

Key quotes (Remix64 interview):
> "You'll probably notice that my earlier SIDS use [Wally Beben's driver]."
> "I used my own editor written by Michael Delaney. This was every bit as good
> as Robs [Rob Hubbard's] editor."
> Features mentioned in Delaney's editor: "ADSR's, drum tables, vibrato's,
> filters etc."

VGMPF summary:
> "First, Brimble used Ariston, and later, a driver and editor written for him
> by his friend Michael Delaney."

Analysis: Brimble refers to Ariston as "Wally Beben's driver" — confirming that
from a composer's perspective, Beben's version was the face of the system.
The explicit features listed (ADSR tables, drum tables, vibrato, filters) in
Delaney's replacement editor give an indirect indication of what Ariston-class
drivers supported. The Brimble → Ariston → Delaney transition happened
sometime in the late 1987–1989 window.

---

## Barry Leitch

Sources:
- https://www.vgmpf.com/Wiki/index.php/Barry_Leitch
- https://remix64.com/interviews/interview-barry-leitch.html
- https://www.retrovideogamer.co.uk/rvg-interviews-barry-leitch/

VGMPF quote:
> "Initially, he solely arranged using Electrosound 64. By 1989, he composed
> with trackers on an Amiga while working on C64 music. He used multiple sound
> drivers: Ariston (for Marauder), a custom driver by an unidentified programmer
> using Turbo Ass (1988–1989), Axel Brown's driver (during Xenophobe), and
> Charles Deenen's driver (from 1991)."

Remix64 interview quote:
> "I still like my Marauder music, even though the driver was very basic I
> really felt like I had accomplished something in creating a piece of music
> that was complete in that it flowed from the quiet introduction and built
> up…"

(No further technical detail about Ariston itself from Leitch.)

Analysis: Leitch used Ariston for Marauder only — one known title. He moved to
custom drivers immediately after. He called it "very basic" retroactively, which
may reflect the assembler-only workflow vs later editor tools.

---

## Jonathan Dunn

Sources:
- https://www.vgmpf.com/Wiki/index.php/Jonathan_Dunn
- https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=92

VGMPF quote:
> "On his first two games (of which Subterranea was delayed), the music driver
> is Ariston, and the sound effect driver is likely Dunn's own."
> "It is unknown how Ariston was available to Dunn and other users."
> Dunn "arranged audio by entering numbers and labels into an audio driver"

Ocean Software progression:
> "The first music player I used at Ocean was one of Martin Galway's, later I
> used one by Paul Hughes, but eventually I wrote my own driver."

Analysis: Dunn used Ariston only on his first two games (pre-Ocean). Once he
joined Ocean Software (1987), he switched entirely to Ocean-internal drivers.
The "entering numbers and labels into an audio driver" description confirms the
assembler-data-entry workflow documented by VGMPF.

---

## Matt Gray

Sources:
- https://www.vgmpf.com/Wiki/index.php/Matt_Gray
- https://mattgray64.wordpress.com/ (no direct Ariston mention, but tooling context)
- https://www.arcadeattack.co.uk/matt-gray-interview/ (no Ariston mention)

VGMPF quote:
> "Initially, Gray used Soundmonitor and the Ariston driver, sometimes optimized
> by game programmers and at that sometimes with declined quality."
> "The founders of Codemasters convinced him to write his own driver."

C64 gameography (VGMPF) — titles where Ariston likely used (pre-Codemasters own driver):
- Driller (1987)
- Fruit Machine Simulator (1987)
- Hunter's Moon (1987)
- Mind-Roll (1987)
- Quedex (1987)

(After Codemasters, Gray developed his own driver; Last Ninja 2 (1988) and
later titles are presumed post-Ariston.)

Note: VGMPF says "optimized by game programmers" with "sometimes declined quality" —
suggests Ariston was modified per-game by coders who didn't fully understand it,
introducing bugs. This is consistent with the "multiple modified versions" mentioned
in the main Ariston article.

---

## Steve Barrett

Source: https://www.vgmpf.com/Wiki/index.php?title=Steve_Barrett

VGMPF note: "Barrett used Ariston." No specific games identified.

---

## Paul Meredith, Mark Wilson

No information found in any public source.

---

## Wally Beben (co-author)

Sources:
- https://www.vgmpf.com/Wiki/index.php/Wally_Beben
- https://www.atari-forum.com/viewtopic.php?t=21588
- https://amp.dascene.net/detail.php?view=8087

Key facts:
- Beben co-wrote the Ariston driver with Ian Crabtree (1987).
- Beben ported the driver to Atari ST and Amiga (1988) with game programmer
  "Chris from Bury St Edmunds, Suffolk."
- Beben **lost all Atari ST and Amiga source code** due to hard drive crashes
  (confirmed in Atari-Forum thread, 2004 era).
- For Amiga: "I wrote it (if I remember) initially using soundtracker for which
  I had a little program I'd written to convert the data into blocks that I
  could use within my own player that I'd migrated/converted from my C64 player."
  (VGMPF, citing Beben directly.)
- Beben's Amiga player became a distinct rip format labeled "WB" (Wally Beben)
  by later rippers.
- Atari-Forum reverse engineering (2004): a thread was started to RE Beben's
  Atari ST R-Type music replayer; "not being a musician, I wouldn't have a
  clue about how his note data is stored" — the format remained opaque as of
  that effort. Attachments (R_TYPE.W_B.zip, Wally Beben rips by Xerud.rar)
  were created but are not publicly accessible.
- BBS: Beben ran "Sounds Digital" BBS from Thetford, Norfolk (August 1991).

---

## Maniacs of Noise interaction

Source: https://www.vgmpf.com/Wiki/index.php?title=Ariston

> "In late 1987, Maniacs of Noise asked Beben how he did the 'phasing' effect.
> After Beben sent them the source code, they added better drums and sent it back."

This is the primary documented technical exchange about the driver. The
"phasing" effect is presumably a pitch-modulation or register-cycling technique.
The drum enhancement by Maniacs of Noise likely improved the noise/percussion
waveform sequencing.

---

## Ian Crabtree biography

Source: https://www.vgmpf.com/Wiki/index.php?title=Ian_Crabtree

- 1988: residing in Newbold, Greater Manchester
- 2007: residing in Whitworth, Lancashire
- 2015: released Quantarallax (C64) — shows continued C64 activity
- Created the Ariston driver; used the Ariston Music Editor for his own C64 work
- Exception: Summer Olympiad (C64, Tynesoft 1988) — "probably arranged in
  assembly using Wally Beben's Ariston version"
- Tuning: 433.5 Hz PAL, 450 Hz NTSC, consistent across SID chips

Known C64 gameography:
- Summer Olympiad (1988, Tynesoft) — unused soundtrack
- Quantarallax (2015) — in-game soundtrack
