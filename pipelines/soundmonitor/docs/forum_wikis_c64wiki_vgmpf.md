# Soundmonitor — wikis (C64-Wiki / VGMPF / Wikipedia)

Cluster: forums + wikis + Usenet (the **wikis** leg).
Carries: (a) plain-English corroboration of the track/step table semantics
useful for parsing the binary; (b) the MusicMaster name-collision warning;
(c) the version + lineage + successor (TFMP) facts.

---

## Source A — VGMPF wiki, "Soundmonitor"

```
source_url:   https://www.vgmpf.com/Wiki/index.php?title=Soundmonitor
fetched_via:  WebFetch (Claude Code)
fetch_date:   2026-06-13
author:       VGMPF wiki contributors (mirrors namelessalgorithm reverse-engineering)
content_date: page ~2010s
reliability:  secondary
```

**Most useful technical corroboration** — the master track/step table, in
plain English (verbatim):

> "on every row (step), you set a tempo, length, volume, fade-out speed; in
> each cell (SID channel in a step), a bar, transpose, instrument set."

> Individual notes support "an instrument and whether to disable transpose and
> enable portamento and arpeggio."

This independently confirms the `SP TRKx TR ST 00` row decomposition already in
`research.md`:
- **SP** (step params) = tempo + length + volume + fade-out speed (one row =
  one step; the four params are per-step, NOT per-cell).
- per **cell** (one per SID channel) = { **bar pointer** (TRKx, 16-bit),
  **transpose** (TR), **instrument/sound set** (ST) }.
- per **note** = instrument + a flag group { disable-transpose, portamento,
  arpeggio (+ the 4th, sound-transpose, per `research.md`) }.

Driver / effects (verbatim):

> The built-in music driver "was made for use in games and supported almost all
> known effects at the time: transpose, detune, portamento, vibrato, pulse
> width modulation, filter modulation, and arpeggios (a first in an editor)."

Constraints + successor (verbatim):

> "Songs were always over 10 KB, and the driver was slow and unrelocatable,
> leading several programmers to modify the driver and compress songs."

> By 1987, Hülsbeck developed "**The Final Musicplayer**" as "an optimized
> driver," though distribution was limited to **Georg Brandt**.

Other (verbatim):
> "You can also record bars on the computer keyboard with quantization."
> "requires basic knowledge of the C64's memory map and hexadecimal system"

Reference cited on the page: `archive.org/details/64er_1986_10/page/n49`
(the original 64'er 10/1986 listing, pp. 53-64).

### Significance
- Confirms **unrelocatable** + **>10 KB songs** (matches the fixed
  $C000/$C020 entry pair and the funet "SM-Relocator" tool — see
  `forum_usenet_csbm.md`).
- "arpeggios (a first in an editor)" + "detune" — the effect catalogue the
  replayer's per-frame SID writes must reproduce: transpose, detune,
  portamento, vibrato, PWM, filter modulation, arpeggio.
- **The Final Musicplayer (TFMP)** is the optimized Hülsbeck successor driver
  (precursor to TFMX). It is a *different* engine, not a Soundmonitor variant —
  don't fold TFMP-driven tunes into the Soundmonitor bucket.

---

## Source B — C64-Wiki (de), "Soundmonitor"

```
source_url:   https://www.c64-wiki.de/wiki/Soundmonitor
fetched_via:  WebFetch (Claude Code)
fetch_date:   2026-06-13
author:       C64-Wiki contributors
content_date: page ~2010s-2020s
reliability:  secondary
```

Thin on byte-level format, but gives concrete **UI / entry-point commands**
that bound the runtime:

- `SYS 4096` ($1000) = restart the editor.
- `SYS 49152` ($C000) = **play the exported song** — confirms the
  **init/play replayer lives at $C000** (the standard `init=$C000`,
  `play=$C020` PSID pair).
- SHIFT+L / SHIFT+S = load/save; F7 toggles keyboard input mode; Y/U select
  track ranges when saving.
- Versions listed: **1.0 (1986), 1.1 (1986), 1.3 (1987)**; Rockmonitor noted as
  the unofficial sample-supporting enhancement (April 1987).
- The page warns its keyboard table is incomplete
  ("Folgende Tastenbelegung gibt es (zur Zeit unvollständig!)").

Reference: original 64'er 10/1986, pp. 53-64; CSDb #59929 (V1.0), #10198 (V1.1).

---

## Source C — Wikipedia (de), "Soundmonitor"

```
source_url:   https://de.wikipedia.org/wiki/Soundmonitor
fetched_via:  WebFetch (Claude Code)
fetch_date:   2026-06-13
author:       de.wikipedia contributors
content_date: current
reliability:  secondary
```

Arpeggio technique (verbatim German):
> "Mit dieser Technik können sehr schnell aufeinanderfolgende Tonfolgen bei
> Verwendung nur eines Stimmen-Kanals festgelegt und somit Akkorde simuliert
> werden" — rapid note sequences on ONE voice channel simulate chords; the
> tones rotate in rhythm.

Origin (verbatim): published as "**Listing des Monats**" in 64'er **10/1986**,
following Hülsbeck's win in the magazine's music competition with the tune
**"Shades"**.

MusicMaster replayer (verbatim intent):
> the embedded MusicMaster routine lets one play "ein Musikstück außerhalb des
> Soundmonitors parallel zu einem anderen Programm" (a tune outside Soundmonitor,
> alongside another program). **Crucially: Hülsbeck wrote the MusicMaster
> routine BEFORE Soundmonitor** — so MusicMaster is the replayer core, and
> Soundmonitor is the editor built around it.

Derivatives: the "**Rockmonitor-Serie**" added sound-sample capability the
original lacked; the article calls Soundmonitor a conceptual basis for later
Amiga/PC tracker software.

---

## ⚠️ Name-collision trap — the OTHER "MusicMaster"

```
source_url:   https://www.c64-wiki.de/wiki/MusicMaster
fetched_via:  WebFetch (Claude Code)
fetch_date:   2026-06-13
reliability:  secondary
```

The C64-Wiki page titled **"MusicMaster"** is **NOT** the Soundmonitor replayer.
It is a *different, unrelated* 1983 program:

> "Das Programm simuliert ein Keyboard ... auf dem man real Melodien oder Lieder
> auf der C64-Tastatur spielen kann."

- Authors: **Chris Metcalf, Marc Sugiyama** (California).
- Published: **Compute! magazine, Issue 37 (June 1983)**, BASIC + 2 asm routines.
- A live-play keyboard simulator (voice 1-8, octave 1-8, waveforms, ADSR,
  chords, slides). **No relation to Hülsbeck / Soundmonitor / SID-tracker data.**

→ When the literature says Soundmonitor's replayer is "MusicMaster" (a.k.a.
"Music Master"), that is the **Hülsbeck embedded driver**, identified by
init=$C000 / play=$C020 and the Soundmonitor data format — never this 1983
Compute! keyboard program. Disambiguate by entry point + format, not by name.

---

## Net technical takeaways for the parser / write model

| Fact | Source(s) | Use |
|---|---|---|
| init=$C000, play=$C020, not relocatable | C64-Wiki `SYS 49152`; VGMPF "unrelocatable" | engine signature + dispatch |
| Step row = {tempo, length, volume, fade-out} | VGMPF | parse `SP` byte(s) per row |
| Cell = {bar ptr (16-bit), transpose, instrument set} | VGMPF | parse `TRKx/TR/ST` per cell |
| Note flags = {transpose-disable, portamento, arpeggio (+sound-transpose)} | VGMPF + research.md | decode the 4-bit options nibble |
| Effects: transpose, detune, portamento, vibrato, PWM, filter mod, arpeggio | VGMPF | the per-frame SID-write effect set to reproduce |
| Songs >10 KB; data spans large region | VGMPF | sizing / region scan |
| MusicMaster (Hülsbeck) == Soundmonitor replayer core | de.wikipedia + tracker-history | unify, don't split |
| The Final Musicplayer = SEPARATE optimized successor | VGMPF | exclude from Soundmonitor bucket |
| Compute!-1983 "MusicMaster" = unrelated program | C64-Wiki MusicMaster | name-collision guard |

## Leads to follow

- **64'er 10/1986 listing pp. 53-64** (`archive.org/details/64er_1986_10`,
  begins ~page n49) — the German type-in article is the PRIMARY source for the
  exact byte layout, sound-patch parameter table, and the editor's data views
  (SP / TRK / AR-S DATA). This is the highest-value remaining doc for the
  binary-parsing priority; OCR the format/listing pages.
- **Rockmonitor 3 / Rockmonitor-Serie wiki pages** are stubs — the per-version
  digi-channel detail must come from disassembly of the rockmonitor-N.prg
  binaries (see `forum_usenet_csbm.md` for the funet copies).
- Confirm by disassembly that **HVSC "MusicMaster" classification == $C000/$C020
  Soundmonitor core** (sanity-check the name-collision guard against real tunes).
