# Master Composer — manual & format documentation

> **Provenance**
> - **source_url:**
>   - VGMPF wiki: https://www.vgmpf.com/Wiki/index.php?title=Master_Composer
>   - Period review: https://archive.org/stream/commodore-64-and-128-music-software-guide/Commodore64And128MusicSoftwareGuide_djvu.txt
>   - Manual-scan search lead: https://www.lemon64.com/forum/viewtopic.php?t=55611 ("Master composer manual scan?")
> - **fetched_via:** WebFetch (VGMPF, archive.org djvu); Lemon64 thread NOT retrievable this
>   session (HTTP 503, Retry-After 3600 — anti-bot block on both WebFetch and curl). Its
>   existence + topic confirmed via WebSearch result snippet.
> - **fetch_date:** 2026-06-13
> - **author (engine):** Paul Kleimeyer / Access Software Inc., 1983–1984, $39.95
> - **content_date:** VGMPF wiki (current); Music Software Guide = 1986; Lemon64 thread = 2015
> - **reliability:** MEDIUM-HIGH. VGMPF is a curated preservation wiki (it cites no primary
>   source for the format claims, so treat the page/block/bar numbers as best-available
>   secondary, to be confirmed against the d64 + a disasm). The 1986 Software Guide blurb is a
>   verbatim primary period source but light on format. **No scanned printed manual was found.**

---

## Bottom line on the printed manual

**No scanned copy of the Access Software Master Composer printed manual is available online**
(as of 2026-06-13). Evidence:

1. **Lemon64 thread "Master composer manual scan?" (t=55611, 2015)** — a user is *asking* for
   a scan, indicating none was circulating then.
2. **CSDb 215363 comment (Paladin, 2022):** "I never could quite figure out how to use this
   one… I wonder if ESI did any docs for this?" — corroborates scarcity a decade later.
3. **archive.org** has no Master Composer (Access Software) manual item. (Note: archive.org's
   "Music Composer (1982)(Commodore)" is a *different, unrelated* Commodore cartridge product —
   do not confuse with Access Software's "Master Composer".)
4. **VGMPF** hosts box / loading / "entering notes" screenshots but **no scanned manual** and
   cites no manual in references.

The closest surviving documentation is therefore (a) the **in-program "Press H" help screen**
(shipped on every disk — CSDb 31047 comment), and (b) the secondary descriptions below.

> **Lead:** if a manual ever surfaces it is most likely via Lemon64's museum
> (`lemon64.com/museum`, genre=manualmisc), the C64 preservation Discords, or a US C64
> software-box collector — Access Software was a US boxed-software house. Retry Lemon64
> t=55611 from a non-blocked egress.

---

## Format / usage model (VGMPF, the most detailed secondary source)

The VGMPF wiki describes the editor's three-tier model — it matches `research.md`'s
Pages→Blocks→Bars hierarchy. Key points reproduced/paraphrased:

### Composition capacity & display
- Up to **127 bars**, each holding up to **16 notes** (16th-note resolution).
- One bar shown at a time, vertically scrollable.
- Display is a **hybrid of traditional notation and piano-roll**; **each voice has its own
  colour**.

### Programming mode — Blocks (the SID-register layer)
- Up to **64 blocks**.
- "Bars do not have to be played in order." In a block you set:
  - **all SID chip registers** for the 3 voices **except combined waveforms** (a known
    limitation — the editor can't drive combined-wave settings),
  - **tempo**,
  - the **start and end bar** *and* the **start/end sixteenth-note position** within those bars.
- Starting a new block reconfigures all SID parameters at once (like switching instrument).

### Pages (the sequencing layer)
- Up to **23 pages**, each specifying a start/end **block** range.
- Pages play **sequentially** until the final page; the last page ends the song.
- Page duplication is how arrangers extended songs (the engine has no orderlist loop concept
  beyond the page list — so very long pieces ≈20 min were built by repeating pages).

### What the engine does NOT have
- **No built-in effects**: no vibrato, no arpeggio, no PWM. Some arrangers **manually added
  pulse-width modulation** by hand (this is the sidid `(Lope_Pulse_Sweep)` sub-variant — see
  `csdb_releases.md`). The page also likens its arpeggio/tuplet limits to the later AdLib
  *Visual Composer*.
- **No combined waveforms** in the block editor (above).

### Tuning / timing
- Song retune function; default tuning **450 Hz (NTSC) / 433.5 Hz (PAL)**.
- **Interrupt-driven (VBlank)** player → music can run in the background of BASIC or
  machine-language programs.

### Integration / output features (from the box copy & guide)
- Music files can be **linked or relocated** (relocatable driver).
- "Easy to add to BASIC and machine code programs."
- **Hard-copy printing** of scores via graphics-capable dot-matrix printers.

### Known bug
- "Only known bug": songs sometimes end with a **lingering/decaying humming sound** after the
  final page completes (matches the `research.md` "decaying hum after final page" note — a
  gate/voice not silenced at song end).

### Historical placement
- By **1986** it was being superseded by **Sidplayer** in the US market.

---

## Verbatim period review — *Commodore 64 & 128 Music Software Guide* (1986)

Found in both the "Composition/Transcription" and "Programming Utilities" sections:

> "This utility program allows users to produce all types of music. By experimenting with
> different arrangements and instrument sounds, one can create both simple melodies and
> intricate compositions. The program is interrupt driven, so music created with it may be
> added to BASIC or machine language programs. Music files may also be linked or relocated.
> Hard copies can be obtained with graphics-capable dot matrix printers. $39.95. Available
> from ACCESS SOFTWARE."

This is the strongest *primary* period text located. It confirms: interrupt-driven, embeddable
in BASIC/ML, linkable/relocatable music files, printable scores, $39.95, Access Software.

---

## Cross-check against `research.md` (prior derived knowledge)

The web sources **independently corroborate** the memory-doc's model on every checkable point:
- 3-tier Pages(≤23) → Blocks(≤64, full SID register snapshot) → Bars(≤127, ≤16 notes) ✓
- VBlank/interrupt-driven, relocatable, init≈`$7580` / play≈`$7587` (SYS 30120 = `$75A8`) ✓
- No effects engine; direct per-block register writes; manual PWM only ✓
- Default tuning 450 Hz NTSC / 433.5 Hz PAL ✓
- Decaying-hum end bug ✓
- `$01..$63` note range bounds (`CMP #$64` in sidid sig) ✓

No web source was found that contradicts `research.md`. No web source gives the **exact memory
offsets** in `research.md` (those came from a binary inspection, not from any public doc) —
they remain to be re-confirmed against the d64 + a disassembly.
