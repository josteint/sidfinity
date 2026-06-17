---
source_url: https://www.vgmpf.com/Wiki/index.php/Jason_Brooke
fetched_via: direct (WebFetch 2026-06-17)
fetch_date: 2026-06-17
author: VGMPF contributors (attributed to Jason Brooke interview + research)
content_date: unknown (wiki page, likely 2022–2023)
reliability: secondary (wiki; attributed to Brooke's own interview statements)
---

# VGMPF: Jason Brooke — C64/CPC driver rewrite for David Whittaker

Full URL: https://www.vgmpf.com/Wiki/index.php/Jason_Brooke

Jason Brooke is the programmer who rewrote David Whittaker's C64/CPC driver in
June 1986, producing the version used in the vast majority of HVSC Whittaker SIDs.

---

## The June 1986 rewrite

**Context:** Binary Design's game programmers complained that both Whittaker's
original C64 driver and his CPC driver were **too slow** (presumably in terms of
CPU time / rastertime consumed per frame).

**What Brooke changed:**
- Made the driver "much shorter, faster, and more flexible"
- Added: "much more flexible chords, envelopes, and combining pitch bends with chords"
- Retroactively dated June 1986

**Propagation:** "This driver got adapted to more platforms and released by late
September [1986]." Platforms: C64 (adapted back by one of them), ZX Spectrum,
Amstrad CPC, MSX.

**Who adapted it back to C64:** "One of them converted it back to the C64" — not
clear whether Brooke or Whittaker did the final C64 adaptation.

---

## Brooke's workflow

- **Assembler:** Mikes Assembler
- **Development machine:** Einstein computer (Tatung Einstein, a Z80-based British
  home computer)
- **Setup:** Einstein wired to target systems for testing
- **Methodology:** "A sound driver was programmed once per platform, and songs and
  sound effects were arranged by typing numbers and labels into the driver's
  source code"
- **Cross-platform testing:** Einstein directly ran ZX Spectrum 128K, CPC, and MSX
  code since "those platforms have the same CPU [Z80] and audio chip [AY-3-8910],
  only differently tuned"

---

## Driver format: macro-based assembly

From Brooke's description, the composition workflow was:
1. Write a platform-specific player driver (once, in assembly)
2. Compose music by entering **numbers and labels** (macro arguments) directly
   into the driver source file
3. Assemble to produce the final binary

This is why:
- The format is not a standard module: player + data are one assembled binary
- The format is consistent across platforms: same macro names, same numerical
  conventions, just different player backends
- Porting music = reusing the same numbers/labels with a different platform driver

This precisely matches what Bansai observed in the Xenon ZX128→C64 conversion:
"pattern commands were parsed and converted automatically" and "subsong and track
pointers are the same exact format as C64."

---

## Brooke as Whittaker successor

After the rewrite, Brooke became Binary Design's primary musician in late April
1987. He composed music in the same framework (Mikes Assembler, Einstein,
same macro system) that he had built for Whittaker. This means:

- Late Binary Design games (from ~April 1987 onward) used **Brooke's own music**
  in a **Brooke-written driver** — but structurally identical to the Whittaker
  driver (same format, same assembler, same macros)
- Any SID from Binary Design games in this period that is attributed to
  Brooke (not Whittaker) uses the same player format

---

## Implication for C64 driver variants

The VGMPF timeline (and sidid/player-id signatures) suggest:

**Pre-Brooke (Whittaker original, late 1985 – mid 1986):**
- Minimalist
- 424 Hz tuning (a specific, nonstandard A=424 Hz instead of 440 Hz)
- Some filter use
- Known games: possibly Lazy Jones (1984), very early Terminal/Binary titles

**Post-Brooke (Brooke rewrite, late September 1986 onward):**
- Faster (fewer raster cycles per frame)
- More flexible chords (enhanced arpeggio or chord commands)
- More flexible envelopes (ADSR command added or improved)
- Pitch bends (portamento/glide more capable)
- Used until ~1991 without further updates

Panther (1986, Mastertronic) is right at the boundary — it loads at $9000, has
the full CommandTable with $80–$93, full arpeggio table with 13 entries, glide,
PWM sweep, and hard-restart gate timing. This is consistent with the post-Brooke
driver.

---

## Leads to follow

- Jason Brooke c64.com interview (SSL issue): https://www.c64.com/gt_display_interview.php?interview=21
  → Try via `curl -k` or Wayback Machine
- AtariCrypt blog post about Brooke: https://ataricrypt.blogspot.com/2018/11/jason-c-brooke.html
  (search result found; not yet fetched — may have more technical details)
- Brooke's own games on Binary Design: check HVSC for
  `MUSICIANS/B/Brooke_Jason/` — same format as Whittaker
- The "Mikes Assembler" mentioned by Brooke: may constrain how macros were
  structured; understanding the macro system could explain the exact
  cross-platform data layout
