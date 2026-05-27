---
source_url: https://c64audio.com/blogs/rob-hubbard-master-of-magic/rob-hubbard-the-beginning
fetched_via: WebFetch direct
fetch_date: 2026-05-25
author: C64Audio (Chris Abbott et al., authoritative Hubbard biographer)
content_date: blog post, contemporary biographical interviewing
reliability: secondary; cites primary interview material
---

# Rob Hubbard — how he started, and the first driver

## Pre-C64

- Played keyboards in band Muffin during the 1970s.
- Touring + studio work + home recording on Roland TB-303, Korg
  Polysix.

## Entry to C64

- Bought a C64 in **November 1983**, after reading reviews in
  *Electronics & Music Magazine* and after the C64 price cut.
- Initial plan: educational music software. Could not find
  commercial interest.

## First paid C64 job — Up Up and Away

- April 1984: contract with Starcade for "simple tune conversions"
  on the C64 version of *Up Up and Away*. (See gtw64_up_up_and_away.md
  for game-level provenance.)
- This is the SID our pipeline currently identifies as `Companion`.
- After this: contract with Ubik on a Weetabix-themed sequel,
  *Paranoid Pete*, which collapsed due to licensing issues.

## The transition off Companion

- **October 1984**: Hubbard tried a self-marketing campaign,
  initially unsuccessfully.
- He then **completely rewrote his music driver** to properly play
  Mozart's *Rondo alla Turca* as his marketing demo. This is the
  driver that becomes his signature engine (Thing on a Spring,
  Monty on the Run, Commando, etc.).
- Micro Projects discovered him and hired him — leading to Thing on
  a Spring and Monty on the Run.

## What we DIDN'T find in this source

The c64audio article does not explicitly name "The Companion to the
Commodore 64" as the source of Hubbard's first driver. That
identification comes from:
- VGMPF's Rob Hubbard wiki page: "In 1984, Hubbard used his own
  version of The Companion to the Commodore 64."
- The fact that "Roundabout" by Keith Bowden (1984 Pan Books)
  matches the same sidid signature.
- JC64dis grouping Hubbard's "Companion player" together with
  Keith Bowden's player as related engines.

## Significance for SIDfinity

The Companion engine is **Hubbard's first driver**, not his second.
The pipelines/hubbard/commando/ engine (etc.) corresponds to his SECOND
driver written from scratch in late 1984. The Companion engine is
older, simpler (no arpeggio/vibrato/PWM per our local
disassembly), and corresponds to a different lineage. It cannot
be migrated via the existing Hubbard pipeline — it needs its own.
