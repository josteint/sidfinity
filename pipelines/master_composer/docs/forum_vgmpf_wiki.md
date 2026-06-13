# Master Composer — VGMPF Wiki (Video Game Music Preservation Foundation)

Provenance
- source_url: https://www.vgmpf.com/Wiki/index.php?title=Master_Composer
- fetched_via: WebFetch
- fetch_date: 2026-06-13
- author/handle: VGMPF wiki contributors (community)
- content_date: undated wiki article (references 1983/1984 product)
- reliability: MEDIUM-HIGH — VGMPF is a curated preservation wiki, generally accurate on retro
  music tools; the technical specifics below match the existing repo `research.md` and HVSC docs.

---

## Creator & publication
- Author: **Paul Kleimeyer**
- Publisher: **Access Software**
- Written: **1983**; Released: **1984** (approximate)
- Platform: Commodore 64

## Music data structure (the 3-tier hierarchy, confirmed)
- **Pages:** up to **23**; each page defines a starting/ending block.
- **Blocks:** up to **64** (in "Programming mode"); each block "sets SID chip registers
  (**except combined waves**), tempo, and bar/sixteenth note range".
- **Bars:** up to **127**; displayed one at a time with scrolling.
- **Notes:** up to **16 notes per bar**.
- Display: *"cross between traditional notation and a piano roll, and each voice has its own color."*

> Note the two NEW details vs the repo's `research.md`: (1) a block sets registers **except
> combined waveforms** — i.e. the editor would not let a block select a combined-waveform value;
> (2) a block also carries **tempo** and a **bar / sixteenth-note range** alongside the register
> snapshot. These belong in the block model, not just "all SID register values".

## Technical capabilities
- SID register access: **all registers except combined waves**.
- **Relocatable** driver (advertised) — lets songs integrate into BASIC and machine-code programs.
- **Background execution** supported (interrupt-driven, per repo notes).
- Default tuning: **450 Hz (NTSC) / 433.5 Hz (PAL)** — matches `research.md`.

## Effects & limitations
- **Built-in effects: NONE** (no vibrato / arpeggio / PWM in the editor).
- Workaround: some users added *"pulse width modulation in BASIC or machine code"* externally.
- Arpeggio / tuplet constraints likened to the later AdLib Visual Composer.

## The "decaying hum" bug — VERBATIM
> *"After the last page, the song ends (sometimes with a decaying hum, Master Composer's only
> known bug)."*

- The wiki calls it **Master Composer's only known bug** and locates it at song end ("after the
  last page"). It does **not** explain the mechanism. (The mechanism is corroborated as living in
  the player's *end-of-tune code* by the HVSC Update #80 / Prg2Sid 1.15 changelog — see
  `forum_hvsc_docs.md`.)

## Song extension — VERBATIM
> *"A few arrangers copy-pasted pages to last about 20 minutes, and a few programmers handled
> looping themselves."*

- So long tunes are made by **duplicating pages** (no native loop), and any looping is
  hand-coded externally — consistent with "no loop command" in the page model.

## Composers / arrangers who USED Master Composer (per the wiki)
The wiki lists these names as **users of the editor** (composers/arrangers), NOT as authors of
engine variants:
1. **Charles Callet**
2. **Graham Marsh**
3. **Mark Darin**
4. **Patrick Payne**  ← see the name-collision note below
5. **Systems Editoriale**
6. **Tommy Dunbar**

> (A second fetch of the same page rendered the list slightly differently — Charles Callet,
> Graham Marsh, Patrick Payne, Tommy Dunbar consistently appear; Mark Darin and Systems
> Editoriale appeared once. Treat the four consistent names as solid.)

## Not present on this page
- No version history / version differences.
- No frame-by-frame / interrupt-level playback description, no memory map, no file sizes.
- **No 4th voice, no sampled drums, no digi.**
- **No mention of TFMX, Chris Hülsbeck, or any separate "MasterComposer"** — confirms the
  name-collision is external to this product (see the dedicated note file).

## Patrick Payne — clarification
On VGMPF, **Patrick Payne is listed among the composers/arrangers who used Master Composer**,
i.e. a *musician* who made tunes with it — **not** the author of a "(Patrick_Payne)" engine
variant. The HVSC `(Patrick_Payne)` parenthetical is therefore a **credit/attribution** (the
person who made or ripped the tune), not a distinct engine. See `forum_namecollision_payne.md`
for the full reasoning + the TFMX/MasterComposer disambiguation.
