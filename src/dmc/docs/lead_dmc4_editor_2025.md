---
source_url: https://csdb.dk/release/?id=250645, https://csdb.dk/release/?id=251057, https://www.lemon64.com/forum/viewtopic.php?t=86611
fetched_via: direct
fetch_date: 2026-04-11
author: Logan (Slackers), Brian (Graffity / The Imperium Arts)
content_date: 2025-03-03 (v1.0 release); 2025-03-15 (v1.1 release)
reliability: secondary
---
# DMC 4 Editor 2025 — Research Lead

## Summary

A modern cross-platform PC recreation of the original DMC V4.0 music editor was released in March 2025 by Logan (Slackers) and Brian (Graffity / The Imperium Arts). It targets Windows (64-bit, 32-bit, and XP-compatible builds). The editor is notable for its ability to **import existing PRG / SID files** composed with DMC V4.0, V7.0A, and V7.0B players — which is directly relevant to our DMC parser project.

---

## Release Information

### DMC 4 Editor 1.0
- **CSDb:** https://csdb.dk/release/?id=250645
- **Released:** 3 March 2025
- **Authors:** Logan (Slackers), Brian (Graffity / The Imperium Arts)
- **Category:** Other Platform C64 Tool

**Downloads:**
- Win64: `dmc4editor10_win64.zip` (278 downloads) — https://csdb.dk/getinternalfile.php/266649/dmc4editor10_win64.zip
- Win32: `dmc4editor10_win32.zip` (72 downloads) — https://csdb.dk/getinternalfile.php/266648/dmc4editor10_win32.zip
- WinXP: `dmc4editor10_winxp.zip` (58 downloads) — https://csdb.dk/getinternalfile.php/266662/dmc4editor10_winxp.zip

**CSDb Comments (verbatim):**
- **Raf** (5 March 2025): Posted YouTube demo — https://www.youtube.com/watch?v=a-BgREkkjcg
- **Richard** (5 March 2025): "This is really cool. My favourite music composer DMC V4 springing back to life again :)"
- **Comos** (3 March 2025): "Any chance to rebuild the exe in VC2017 for XP compatibility? The dlls are compiled in VC2015 so should not be a problem."
- **Jammer** (3 March 2025): "And 6x speed! At least! Now that's a cool surprise :O"
- **psych** (3 March 2025): "Holy shit, I didn't expect that! Now, go and make a full DMC version with all these nice/new and very much needed features :) PLEASE!"
- **Slajerek** (3 March 2025): "Nice :)"

**Key comment: Jammer mentions "6x speed"** — this refers to the PC editor running at 6x the original C64 playback speed (since the C64 player runs at 1x on real hardware).

### DMC 4 Editor 1.1
- **CSDb:** https://csdb.dk/release/?id=251057
- **Released:** 15 March 2025
- **Authors:** Same (Brian / Graffity, The Imperium Arts; Logan / Slackers)

**Downloads:**
- Win64: `dmc4editor11_win64.zip` (262 downloads)
- Win32 (XP compatible): `dmc4editor11_win32(xp_compatible).zip` (136 downloads)

**v1.1 Changelog (verbatim from CSDb):**
> Import Music → read and display the music word message/credits
> Export PRG → added music relocator / change save music words message/credits
> Sector Editor → added Octave Up/Down (selection or cursor position) and Voice on/off in popup menu
> Sector Editor → Display Sector Duration
> Sound Editor → put/change names of sounds
> Added View menu for larger fonts
> Added Sound menu for import/export sounds banks
> Track Editor → play from selected position via spacebar
> Track Editor → Display music time and current playing position
> Fixed many minor bugs

**CSDb Comments:**
- **apprentix** (16 March 2025): "Fantastic!"
- **Yogibear** (22 March 2025): "Nice!"

---

## Editor Feature Set (from all sources)

The editor is a GUI recreation of DMC V4.0 with the following editors/screens:

| Screen | Function |
|--------|----------|
| Sound Editor (Instruments) | ADSR, wave table, waveform+arpeggio (WFARP) commands, sound names (added v1.1) |
| Wave Editor | Wave table entries (2 bytes/row: waveform + gate) |
| Filter Editor | Filter table entries |
| Sector Editor | Pattern data — 64 sectors (00-3F), up to 256 rows each; Octave Up/Down, Voice on/off, sector duration display |
| Track Editor | Order list — 3 channels; play from selected position; music time/position display |
| Sequence Editor | High-level song arrangement |

**Import/Export:**
- Import PRG / SID files from: DMC V4.0, V7.0A, V7.0B
- Export PRG with music relocator and credits editing
- Import/export sound banks (v1.1)

---

## DMC V4 Data Format (from Chordian comparison table + Turkish manual)

These are the structural limits of the original DMC V4.x format (the new editor is constrained by these):

| Parameter | DMC V4.x | DMC V5.x (1993) |
|-----------|----------|-----------------|
| Instruments/sounds | Not yet confirmed for V4; V5 = 32 | 32 |
| Sub-tunes | 8 | 8 |
| Sectors (patterns) | 64 (00-3F) | 96 (up to 250 rows each) |
| Rows per sector | 256 | 250 |
| Channels | 3 | 3 |
| Table rows | 2 bytes/row (wave, pulse, filter, cmd) | same |
| Player size | ~2000 bytes | ~2000 bytes |
| Zero page usage | Minimal | At least 2 ($F8-$F9) |
| CPU time (1x) | ~23-27 rasterlines | ~23-27 rasterlines |
| PAL/NTSC | PAL only | PAL only |
| Playback speeds | 1x (and 4x in V7) | 1x |

**Table structure (V4/V5):**
- Wave table: 2 bytes per row (waveform byte + gating)
- Pulse table: 2 bytes per row
- Filter table: 2 bytes per row
- Command table: 2 bytes per row

**Duration-based patterns:** DMC does NOT use tick-based patterns. Patterns can be any length; no inter-channel synchronization is enforced. This is a key architectural difference from trackers like GoatTracker. (Source: Tobias on Lemon64, July 2025)

---

## DMC V7 Context

- DMC V7 was created by "unreal" using DMC V4 code as a base, adding extra features including **4x speed playback**
- The new editor supports importing V7.0A and V7.0B SID files
- V7.0A and V7.0B are likely slightly different player variants (same data format, different player code)
- DMC V7 is the version most commonly used in productions from mid-1990s onward

---

## Author Profiles

### Logan (Slackers) — CSDb: https://csdb.dk/scener/?id=6117
- Active in scene since early 2000s
- Groups: Slackers (current), Onslaught, Samar Productions, Mad Squad, Apidya
- SID-related tools: DMC 4 Editor 1.0 (2025), DMC 4 Editor 1.1 (2025)
- Other 2025 work: "Sphere of Laziness" intro (Slackers)
- Primary role: Code

### Brian (Graffity / The Imperium Arts)
- Original author of DMC V4.0 (1991) and V5.0 (1993)
- Also created Digieditor v1.3 (digitized music editor)
- sidid signature: "Balazs Farkas (Brian)"
- CSDb original DMC 4.0: https://csdb.dk/release/?id=2596

---

## Community Reception

The release was enthusiastically received, with several longtime DMC users expressing that they had been waiting for exactly this. The Lemon64 thread ("DMC V4 is back in 2025") confirmed:
- Richard of TND (The New Dimension) announced it and intends to use it for future productions
- Pattern synchronization was a question from users — answered: DMC is duration-based, no sync required/possible by design
- v1.1 was noted as improving pattern synchronization workflows

---

## Relevance to SIDfinity DMC Parser

1. **Import format confirmed:** The editor imports PRG and SID files made with DMC V4.0, V7.0A, V7.0B. This confirms all three are compatible data formats for our parser.

2. **Editor download:** The editor itself (especially the import code) is a ground-truth implementation for parsing DMC V4/V7 SID files. **Downloading and reverse-engineering or simply running the importer could validate our parser.**

3. **V7.0A vs V7.0B distinction:** The editor distinguishes these as separate import targets — we should detect which sub-variant a file is.

4. **Sound bank import/export (v1.1):** Suggests sounds/instruments are stored as a separable bank — potentially a self-contained block in the SID binary.

5. **64 sectors × 256 rows:** These are hard limits in the V4 data format. Our parser should enforce/validate these bounds.

6. **Duration-based pattern system:** NOT tick-based. Each note command carries its own duration value — this affects how we parse sector row data vs. how we'd parse a standard tracker.

---

## YouTube Demo

- **URL:** https://www.youtube.com/watch?v=a-BgREkkjcg
- **Posted by:** Raf (C64 scene member)
- **Context:** Posted in CSDb comments for DMC 4 Editor 1.0 on 5 March 2025
- The video shows the editor in action and reveals UI layout, but YouTube did not render fully — visit directly for UI screenshots.

---

## Sources

- CSDb v1.0: https://csdb.dk/release/?id=250645
- CSDb v1.1: https://csdb.dk/release/?id=251057
- Lemon64 thread: https://www.lemon64.com/forum/viewtopic.php?t=86611
- Chordian C64 editors comparison: http://chordian.net/c64editors.htm
- Original DMC 4.0 CSDb: https://csdb.dk/release/?id=2596
- sidid.nfo (player detection): https://github.com/cadaver/sidid/blob/master/sidid.nfo
- DMC 4.0 manual PDF (Turkish): https://silo.tips/download/demo-music-creator-40
- Zimmers archive (actual PRG files): https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/
- Logan/Slackers scener profile: https://csdb.dk/scener/?id=6117
