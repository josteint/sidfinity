---
source_url: multiple (see ## Archived URLs)
fetched_via: direct
fetch_date: 2026-06-17
author: Lasse Öörni (Cadaver / Covert Bitops); compilation by research agent
content_date: 2002–2026
reliability: primary
---

# NinjaTracker — Research Findings

## Overview

NinjaTracker is a native Commodore 64 music editor and associated playroutine
by Lasse Öörni (handle: Cadaver), sole programmer of the two-person group
Covert Bitops (the other member, Olli Niemitalo "Yehar", contributes music).

The defining design goal is MINIMAL RASTERTIME: the player is intended for use
in C64 games and demos where the VBI (vertical blank interrupt) is shared with
game logic. The V1 series achieves 11 rasterlines max; the related miniplayer
tools achieve 9 rasterlines.

NinjaTracker is a NATIVE C64 EDITOR — it runs on the actual C64 hardware/
emulator, not cross-platform. The companion conversion tools (GT→NT converters,
miniplayer) run on PC.

The player was ORIGINALLY created for Metal Warrior 4 (MW4), Cadaver's own C64
game. The "gamemusic mode" (a single shared playroutine with separately loadable
music data modules) was designed specifically for this use case — a game with
many music tracks stored as separate files that share one copy of the player
code in RAM.

The format was later rewritten completely for V2 (2006), which is a different,
incompatible engine from V1.

---

## Versions Found

### V1 Series (Oct 2002 — Jan 2004)

| Version | Date | CSDb ID | Notes |
|---------|------|---------|-------|
| V1.0 | 31/10-2002 | 7206 | Initial release |
| V1.01 | 10/11-2002 | 7310 | — |
| V1.01 Gamemusic Version | 10/11-2002 | 7258 | Separate release with gamemusic-mode player |
| V1.02 | 14/11-2002 | 7261 | — |
| V1.03 | 23/11-2002 | 7257 | — |
| V1.04 | 5/3-2003 | 8661 | — |
| V1.05 | 6/1-2004 | 39500 | Slide duration calculator added; editing of sector 0 (init sector) |
| V1.1 | 25/1-2004 | 39501 | Hardrestart fix ($00/$00 on both AD/SR); INS in pulse/filtertable; pointer adjustment on INS/DEL; movement speed-optimized |

Legacy downloads still available as of 2026:
- ninjatrk.zip  (V1.1)  — https://cadaver.github.io/tools/ninjatrk.zip
- ninja102.zip  (V1.02) — https://cadaver.github.io/tools/ninja102.zip

### V2 Series (Aug 2006 — Jun 2013)

V2 is a COMPLETE REWRITE of V1 — incompatible format, different engine.
"Actually totally rewritten" — Lasse, announcement post.

| Version | Date | CSDb ID | Notes |
|---------|------|---------|-------|
| V2.0 | 30/8-2006 | 39374 | Initial V2 release; new: commands (= instruments), 2-col tables, slide-to-target |
| V2.01 | 2/9-2006 | 39498 | Editor improvements |
| V2.02 | 2/9-2006 | 39499 | Editor improvements; playroutine slightly slower and bigger |
| V2.03 | 3/9-2006 | 39571 | Hard restart; rastertime optimization attempt; "the player is yet bigger" |
| V2.04 | 19/6-2013 | 119721 | Fixes transpose not resetting when playback started from beginning. FINAL RELEASE. |

Current download: ninjatr204.zip — https://cadaver.github.io/tools/ninjatr204.zip

### Related: GoatTracker → NinjaTracker Converters

| Version | Date | CSDb ID | Notes |
|---------|------|---------|-------|
| GT1→NT converter | 24/1-2003 | 7833 | Converts GoatTracker V1.x to NinjaTracker V1 format. Idea: Puterman/Fairlight. |
| GT2→NT2 Converter V1.0 | 3/2-2013 | 115448 | Initial GT2 to NT2 converter |
| GT2→NT2 Converter V1.02 | 3/10-2015 | 152424 | Update |
| GT2→NT2 Converter V1.03 | 11/9-2021 | — | Adds source mode converter (no need to use native NT2 to save playable modules) |

Current download: gt2nt2.zip — https://cadaver.github.io/tools/gt2nt2.zip

### Third-party modification

NinjaTracker MOD V2.04 by Spider Jerusalem (10/1-2017, CSDb #152640):
- Removed DMC-style keyboard layout
- Added pause for long directories
- F2/F5 play from mark, F3/F4 stop playing (GoatTracker/SidWizard style)
- Changed colour scheme behaviour
- Playroutine UNCHANGED — full compatibility with official V2.04

---

## Format / Player Design Notes

### V1 Format ("Sectors" terminology)

The V1 documentation uses different terminology from V2:

- **Songs**: up to 16, each with 3 tracks
- **Sectors** (= patterns in V2): THREE-COLUMN format
  - Column 1: note OR command (Wave, AD, SR, Filter)
  - Column 2: wavetable pointer
  - Column 3: duration
- **Wavetable**: THREE columns (waveform, note, pointer)
- **Pulsetable**: THREE columns
- **Filtertable**: THREE columns (similar to pulsetable)
- **Track data**: loops, sector indices, transpose commands (same overall
  structure as V2 — 16 songs, 3 tracks, 127 sectors)
- **Rastertime**: 11 lines max
- **Playroutine size**: "small" (emphasis in docs)
- **ZP requirement**: unspecified in available docs

Init sector (sector 0) was a special editing target added in V1.05.

Hard restart in V1.1: sets BOTH Attack/Decay AND Sustain/Release to $00.

The "gamemusic mode" was available as early as V1.01 (separate CSDb release
for the gamemusic-mode variant), then presumably merged into later builds.

### V2 Format ("Patterns" terminology)

V2 is a complete redesign:

- **Songs**: up to 16, each with 3 tracks
- **Shared across all songs**: 127 patterns, tables, commands
- **Patterns**: FOUR-COLUMN format (changed from V1's three-column sectors)
  - Column 1: note / keyoff / keyon
  - Column 2: command number
  - Column 3: duration (minimum: 2 frames)
  - Column 4: command name (display only?)
  - Notes range: C-1 to B-7
- **Tables** (wave/pulse/filter): TWO-COLUMN format (changed from V1's three)
  - Contains jump destinations and modulation parameters
- **Commands**: serve double duty as INSTRUMENTS and pattern modifiers
  - Set ADSR
  - Set wave/pulse/filter table pointers
  - "General purpose" (not dedicated instruments)
- **Track data encoding**:
  - 00: loop
  - 01-7F: patterns
  - 80-BF: transpose downward
  - C0-FF: transpose upward

**Key V2 design changes vs V1**:
1. Tables are now 2-column (not 3-column)
2. Patterns are 4-column (not 3-column)
3. Commands serve as instruments (unified concept)
4. Slide function aware of target pitch (stops when reached)
5. Attack fluctuation hidden by silent first frame of note (V2.03+)
6. Hard restart: "sexy hardrestart" in V2.03 description

**Rastertime note**: Lasse stated V2.0's playroutine is "slower than the
previous [V1] versions". V2.03 attempted to reclaim rastertime but remained
larger than V2.01.

### nt2play.s — The V2 Gamemusic Player

Package contents (V2.04 zip, ~95KB zip / ~200KB uncompressed):
- ninjatr2.d64    — disk image (editor + example tunes)
- example.prg    — gamemusic player example
- nt2play.s      — DASM-format source for the gamemusic player
- ins2nt2.exe    — Windows utility: converts GT1/GT2 instruments to NT2 commands
- ins2nt2.c      — Source for the above
- /src           — Editor source + example source
- readme.txt     — Documentation
- makefile       — Build config

Build requirements (from NFO): DASM assembler, Pucrunch, c64tools package
from covertbitops.c64.org.

**Normal mode vs Gamemusic mode**:
- Normal: playroutine compiled into the music file. Self-contained PRG.
  Requires 2 bytes of ZP. Init + play calls standard.
- Gamemusic: music data saved WITHOUT the player. The game code holds one
  copy of nt2play.s compiled playroutine; each music module is a separate
  data file. Designed for games with many music tracks (MW4 use case).

**Player interface** (from miniplayer2 as proxy, same conceptual model):

    ; Init / start subtune N:
    lda #subtune+1   ; 1 = first subtune
    sta PlayRoutine+1

    ; Play one frame:
    jsr PlayRoutine

    ; Silence:
    lda #$ff
    sta PlayRoutine+1

### Miniplayer / Miniplayer2 — NinjaTracker V1 Spiritual Successor

Cadaver released two cross-platform players explicitly described as
"NinjaTracker 1 style":

**miniplayer** (https://github.com/cadaver/miniplayer)
- Announced: 2018-02-05 on Lemon64
- Target: 9 rasterlines (vs NT1's 11)
- Format: DASM, GT2 converter included (effects 1,2,3,4,F supported)
- Sound FX: PLAYER_SFX config variable

**miniplayer2** (https://github.com/cadaver/miniplayer2)
- Updated version with additional features
- Target: 9-10 rasterlines
- Sound FX: PLAYER_SFX = 2
- Multi-module: "similar to NinjaTracker gamemusic mode"
- Hard restart: gate off 1 frame, S/R = $0f
- ZP: configurable (default: 23 bytes; fast-path optimization available)
- GT2 effects supported: 1,2,3,4,5,6,7,F (no funktempo)
- Effect 3 (toneportamento): calculated slide duration (may not be exact
  with transposed patterns)
- Player.s: ~860 lines DASM assembly
- Tables: 2-column "next column" navigation (no jump bytes)
- Pulse/filter tables: max 127 steps (high bit = init step)
- Music must be page-aligned (address lowbyte = 0)
- License: MIT

These are NOT NinjaTracker. They are separate tools that share the design
philosophy of minimal rastertime / minimal featureset.

---

## Distribution History

**Where distributed**:
- Primary: http://covertbitops.c64.org/tools/ (original site, now archived)
- Current: https://cadaver.github.io/tools.html (GitHub Pages mirror, active 2026)
- CSDb: internal file hosting for each release
- Pokefinder.org: mirror (mentioned in CSDb pages)
- Archive.org: NinjaTracker v1.02 preserved as
  d64_NinjaTracker_v1.02_19xx_CovertBitops (uploaded 2021-03-10 by "Sketch the Cow")
- Pouet.net: V2.0 listed as demotool (#26206); V1.1 (#13462)

**Package filenames** (historical URLs on covertbitops.c64.org):
- V2.0:   ninjatr2.zip   → tools/ninjatr2.zip
- V2.01:  ninjatr201.zip → tools/ninjatr201.zip
- V2.02:  ninjatr202.zip → tools/ninjatr202.zip
- V2.03:  ninjatr203.zip → tools/ninjatr203.zip
- V2.04:  ninjatr204.zip → tools/ninjatr204.zip  (current)
- V1.1:   ninjatrk.zip   → tools/ninjatrk.zip    (still available)
- V1.02:  ninja102.zip   → tools/ninja102.zip     (still available)
- GT1→NT: goatninj.zip   → tools/goatninj.zip
- GT2→NT2: gt2nt2.zip   → tools/gt2nt2.zip       (current)

**License**: Freeware. Customization allowed and encouraged.

**Author contact** (from NFO files):
- V1.1 era: loorni`student.oulu.fi (student email, Oulu University)
- V2.0+:   loorni@gmail.com
- Website:  http://covertbitops.c64.org (original) → https://cadaver.github.io (current)

---

## Archived URLs (all fetched 2026-06-17)

| URL | Status | Notes |
|-----|--------|-------|
| https://cadaver.github.io/tools.html | 200 OK | Current tools page, lists all downloads |
| https://cadaver.github.io/main.html | 200 OK | About page — Covert Bitops description |
| https://cadaver.github.io/update.html | 200 OK | Update history (earliest entry 2018; older entries not present) |
| https://cadaver.github.io/tools/ninjatr204.zip | 200 OK | V2.04 download (~95KB zip) |
| https://csdb.dk/release/?id=7206 | 200 OK | NT V1.0 |
| https://csdb.dk/release/?id=7310 | 200 OK | NT V1.01 |
| https://csdb.dk/release/?id=7258 | 200 OK | NT V1.01 Gamemusic Version |
| https://csdb.dk/release/?id=7261 | 200 OK | NT V1.02 |
| https://csdb.dk/release/?id=7257 | 200 OK | NT V1.03 |
| https://csdb.dk/release/?id=8661 | 200 OK | NT V1.04 |
| https://csdb.dk/release/?id=39500 | 200 OK | NT V1.05 |
| https://csdb.dk/release/?id=39501 | 200 OK | NT V1.1 |
| https://csdb.dk/release/?id=39374 | 200 OK | NT V2.0 |
| https://csdb.dk/release/?id=39498 | 200 OK | NT V2.01 |
| https://csdb.dk/release/?id=39499 | 200 OK | NT V2.02 |
| https://csdb.dk/release/?id=39571 | 200 OK | NT V2.03 |
| https://csdb.dk/release/?id=119721 | 200 OK | NT V2.04 |
| https://csdb.dk/release/?id=152640 | 200 OK | NT MOD V2.04 (Spider Jerusalem) |
| https://csdb.dk/release/?id=115448 | 200 OK | GT2→NT2 V1.0 |
| https://csdb.dk/release/?id=152424 | 200 OK | GT2→NT2 V1.02 |
| https://csdb.dk/release/?id=7833 | 200 OK | GT1→NT converter |
| https://csdb.dk/search/?stype=all&search=ninjatracker | 200 OK | Full CSDb search results |
| https://www.pouet.net/prod.php?which=26206 | 200 OK | Pouet NT V2.0 |
| https://www.pouet.net/prod_nfo.php?which=26206&font=none | 200 OK | NT V2.0 NFO (full text) |
| https://www.pouet.net/prod_nfo.php?which=13462&font=none | 200 OK | NT V1.1 NFO (full text with version history) |
| https://www.lemon64.com/forum/viewtopic.php?t=20873 | 200 OK | V2.0 announcement thread |
| https://www.lemon64.com/forum/viewtopic.php?t=67012 | 200 OK | miniplayer "NinjaTracker 1 style" thread |
| https://archive.org/details/d64_NinjaTracker_v1.02_19xx_CovertBitops | 200 OK | Archive.org: NT V1.02 disk image |
| https://github.com/localhost/NinjaTracker | 200 OK | Custom fork with modifications to NT2 |
| https://github.com/cadaver/miniplayer | 200 OK | Original miniplayer (2018) |
| https://github.com/cadaver/miniplayer2 | 200 OK | Miniplayer2 (2021/2026) |
| https://github.com/cadaver/miniplayer2/blob/master/README.md | 200 OK | Full README |

**web.archive.org CDX API**: returned "unable to fetch" (Wayback CDX is blocked
from this environment). Wayback snapshots not accessible for fetching.

---

## Leads to Follow

### DONE — source files extracted and saved to docs/src/

The following high-priority items are COMPLETE:

1. **ninjatr204.zip extracted** — all files in
   `/home/jtr/sidfinity/tmp/ninjatracker_research/extracted_v204/`
   Key files saved to `docs/src/`:
   - `archive_nt2play_v204.s` — V2 gamemusic player (primary format spec)
   - `archive_v204_readme.txt` — V2.04 full readme with version history
   See `docs/src/archive_player_sources_index.md` for detailed format analysis.

2. **ninjatrk.zip (V1.1) extracted** — files in
   `/home/jtr/sidfinity/tmp/ninjatracker_research/extracted_v11/`
   Key files saved:
   - `archive_ntplay_v11.s` — V1 gamemusic player
   - `archive_v11_readme.txt` — V1 full readme
   - `archive_v11_readgam.txt` — V1 gamemusic mode docs

3. **gt2nt2.zip extracted** — files in
   `/home/jtr/sidfinity/tmp/ninjatracker_research/extracted_gt2nt2/`
   (gt2nt2.c contains the GT2→NT2 conversion logic; not yet copied to docs/src)

### Remaining leads

4. **Read gt2nt2.c** — the GT2→NT2 converter source documents exactly
   which GT2 fields map to which NT2 fields (format cross-reference).
   File: `/home/jtr/sidfinity/tmp/ninjatracker_research/extracted_gt2nt2/gt2nt2.c`

5. **Read miniplayer2/player.s raw** from
   https://raw.githubusercontent.com/cadaver/miniplayer2/master/player.s
   ~860 lines of DASM — contains all ZP address assignments and data layout
   comments. Good proxy for understanding NT-family player structure.

6. **Read miniplayer2/gt2mini2.c raw** from
   https://raw.githubusercontent.com/cadaver/miniplayer2/master/gt2mini2.c
   The GT2→miniplayer2 conversion C code fully documents the data format.

### Medium priority — community / usage documentation
8. **ninjatr2.odf** in the localhost/NinjaTracker GitHub fork:
   https://github.com/localhost/NinjaTracker/blob/custom/ninjatr2.odf
   This is an ODF document (18.1 KB) — the V2 user manual. Download raw
   and convert with LibreOffice/antiword to extract text.

9. **Wayback Machine snapshots** of covertbitops.c64.org (blocked in this
   session). Try later:
   - https://web.archive.org/web/20100601/http://covertbitops.c64.org/
   - https://web.archive.org/web/20060901/http://covertbitops.c64.org/

10. **HVSC SID file inventory** — check how many HVSC SIDs use NinjaTracker
    format. sidid tool at https://github.com/cadaver/sidid may have a
    NinjaTracker signature. Run:
    `sidid --list-engines | grep -i ninja`

11. **Archive.org disk image** for V1.02:
    https://archive.org/details/d64_NinjaTracker_v1.02_19xx_CovertBitops
    Can be played in VICE emulator to inspect actual format on-disk.

### Low priority
12. Pouet prod listing for V1.0 (prod # unknown — search pouet for
    "ninjatracker covert bitops" filtered to 2002)
13. CSDb forum threads for V1.x releases — may have technical commentary

---

## Key Facts for SIDfinity Pipeline Assessment

1. **NinjaTracker is not in HVSC** as a major player family (it is primarily
   used for game music, not HVSC SID releases). The single CSDb SID in
   NinjaTracker format is "D'Oh! (Ninjatracker)" by Mermaid/Vision (2007).
   HVSC coverage is expected to be very low.

2. **Two incompatible formats exist**: V1 (2002-2004) and V2 (2006-2013).
   V2 is a complete rewrite. Any pipeline work needs to choose which to target,
   or implement both.

3. **The playroutine source is available**: nt2play.s (DASM, V2) is in the
   public package. This gives full player source for reverse engineering.

4. **Minimal feature set** = simpler pipeline than GoatTracker:
   - Commands double as instruments (no separate instrument list concept)
   - 2-column tables (V2) vs GT2's complex multi-column tables
   - No funktempo, no complex effects
   - Slide stops at target (not continuous)
   - Max 16 songs, 127 patterns/tables/commands

5. **Rastertime as primary metric** — this was the design north star.
   Not audio fidelity, not feature richness. Important context for USF
   representation: the format encodes "what is needed with minimal CPU cost".

6. **Gamemusic mode** is directly analogous to USF's "one player, many data
   modules" philosophy — already well-matched to the SIDfinity pipeline design.
