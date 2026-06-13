# Music Assembler ↔ VoiceTracker shared compression (Lemon64 + JC64dis family)

> **source_url:** https://www.lemon64.com/forum/viewtopic.php?t=2029 ("Looking for a copy
>   of Voicetracker for music work") and https://www.lemon64.com/forum/viewtopic.php?t=5712
>   ("making music on c64"); cross-ref https://iceteam.itch.io/jc64dis
> **fetched_via:** WebSearch (Lemon64 itself returned HTTP 503/403 to direct WebFetch on
>   2026-06-13 — content below is from the search-engine snippet/abstract of those threads).
> **fetch_date:** 2026-06-13
> **author/handle:** Lemon64 forum posters (handles not resolvable from the snippet; the
>   threads are ~2004–2010 era).
> **content_date:** Lemon64 threads ~2004–2010.
> **reliability:** secondary (forum hearsay) — but the compression-equivalence claim is
>   independently corroborated by JC64dis/SIDId (separate, authoritative sources below).

## The load-bearing claim: VoiceTracker REUSES the Music Assembler player/compression

Verbatim (Lemon64, surfaced via search of t=5712 / t=2029):

> "Voicetracker doesn't use much raster-time and uses the same sort of compression
>  as Dutch USA Team's music assembler."

This is the key cross-format fact for the migration:

- **One decoder covers two (probably five) editors.** VoiceTracker's data is packed
  with "the same sort of compression as ... music assembler." JITT64 (see
  `forum_jitt64_importer.md`) bundles MA + VoiceTracker into a *single* importer,
  confirming a shared on-disk model.
- Corroborated by SIDId (`forum_sidid_signatures.md`): SIDId's `.nfo` says
  VoiceTracker (1991), Music Mixer (1991), DoubleTracker (1993) and Ten Tracker (1991)
  are each "Editor based on the Music Assembler player." So the MA packed format +
  runtime is the common substrate; DoubleTracker = multispeed, Ten Tracker = 10×.

**Practical consequence:** building one MA-format extractor likely unlocks the
VoiceTracker / Music Mixer / Double­Tracker / Ten Tracker HVSC tunes too — a much
larger slice than the ~6,351 "Music_Assembler"-tagged SIDs. Treat the speed
variants (Double/Ten Tracker) as dispatch-rate variants of the same write-model
(cf. CLAUDE.md Trap C / CIA-tune handling), not new formats.

## JC64dis: the Music Assembler player family it recognises (with example tunes)

> **source_url:** https://iceteam.itch.io/jc64dis ; source: https://github.com/ice00/jc64
>   (GPL-2.0, Java; recognition driven by `src/sw_emulator/software/SidId.java` +
>   a `sidid` package — i.e. it uses the SIDId signature DB).
> **reliability:** secondary (tool documentation), HIGH confidence — names concrete
>   HVSC member tunes per player, useful as canary/representative picks.

JC64dis (an iterative C64 disassembler that auto-recognises the SID playroutine)
lists these related players with worked example tunes:

- **Music Assembler player** — examples:
  - "MC_01" by **Marco Swagerman (c) 1988 Dutch USA Team**  (predates the 1989 release!)
  - "Magazine Intro Tune" by **Reyn Ouwehand (c) 1989**
- **Music Mixer player** — example: "Michael" by Arkadiusz Zych
- **Voice Tracker player** — example: "3LUX Intro" by The Bill
- Other **Dutch USA Team** players recognised: **Rockmonitor II**, **RockMonitor V**
  (separate engines by the same group — NOT the Music Assembler format).

Notes:
- "MC_01 (c) 1988" shows Swagerman's MA player existed in **1988**, a year before the
  Markt+Technik V1.0 commercial release (1989). Expect a pre-release/dev variant.
- Reyn Ouwehand authored MA tunes too — widen the HVSC author net beyond MC/OPM.
- JC64dis 2.8 devlog (https://iceteam.itch.io/jc64dis/devlog/651862) added:
  "Add data relocation table reference (base+destination)" and
  "Add SidId player searcher" — i.e. it can track a player's relocatable data-pointer
  table (base→destination), the exact mechanism an MA player uses to find its packed
  presets/sequences/tracks after relocation. The jc64 source (SidId.java + the
  relocation logic) is the place to read how it resolves those pointers.

## Author primary-source contact (for format gaps)

> **source_url:** https://amiga.cafe/forum/main-forum/aan-de-bar/24653-dutch-usa-team-music-assembler
> **fetched_via:** WebFetch  ·  **fetch_date:** 2026-06-13  ·  **reliability:** primary (the author).

**Marco Swagerman himself posts as handle "MC-DusaT"** on amiga.cafe, as recently as
**17-09-2025**. He still has (somewhere) Amiga diskettes with "mijn sourcecodes en
Devpac" (my source code and Devpac files). Verbatim:

> Post #13 (17-09-2025): "Er is zeker een werkende versie. Ik weet alleen niet of ik
>  die nog heb. Ik heb ergens een doosje met Amiga diskettes ... Waarschijnlijk staan
>  daar mijn sourcecodes en Devpac nog op maar ik weet het niet 100% zeker."
>  (≈ "There's definitely a working version. I have a box of Amiga diskettes somewhere
>   ... my source code and Devpac are probably on them, but I'm not 100% sure.")
> Post #14 (17-09-2025): "Ik was destijds niet erg onder de indruk van de Amiga qua
>  Paula chip ... Amiga Music-Assembler is dan ook verder nooit doorontwikkeld."
>  (≈ unimpressed by the Amiga's Paula; the Amiga MA port was never further developed.)

The thread also establishes: the module file extension is **`.MA`**, and a **C64
version 1.4** existed (beyond the V1.0 in HVSC/CSDb). MC = Marco Swagerman,
OPM = Oscar Giesen. **If the packed C64 format proves intractable from binaries
alone, the original author is reachable and may hold the C64 player source.**
(No C64 player source/format spec was posted in-thread — only the existence claims.)
