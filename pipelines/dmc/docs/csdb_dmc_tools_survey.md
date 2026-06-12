---
source_url: https://csdb.dk/search/?seinsel=releases&search=DMC + https://csdb.dk/search/?seinsel=all&search=DMC+player + https://csdb.dk/release/?id=2629 + https://csdb.dk/release/?id=10758 + https://csdb.dk/release/?id=2627 + https://csdb.dk/release/?id=46815 + https://csdb.dk/release/?id=251057 + https://www.pouet.net/prod.php?which=13452
fetched_via: direct
fetch_date: 2026-06-12
author: CSDb community (various)
content_date: releases 1991-2025; comments 2005-2025
reliability: secondary (release metadata + scene-participant comments)
---

# CSDb survey: every DMC tool/player/relocator/packer release found

Goal of this survey: locate format-knowledge-bearing tools (anything that
relocates, packs, depacks, scans or plays DMC data must understand the
layout) and any source-code release. **No "player source" or disassembly
release exists on CSDb for DMC** — knowledge is embedded in these tools:

## Tool releases (CSDb release search "DMC", music-editor-related only)

| Release | Group/Author | Year | CSDb id | Why it matters |
|---|---|---|---|---|
| DMC Relocator | Brian/Graffity | 1991 | 10758 | relocates player+data; zips: Music Mania.zip, DMC 2 Relocator.zip, DMC 4 Relocator.zip |
| DMC Relocator | The Imperium Arts | ? | 206652 | |
| DMC Relocator V2 | Graffity | ? | 236894 | (page fetch failed twice — retry) |
| DMC V4.0 Relokator V2 | Caution | ? | 95145 | |
| DMC V4.0b Relocator | Agemixer | ? | 50611 | (page fetch failed — retry) |
| DMC V1.2+++ | Shazam! | ? | 25228 | early variant |
| DMC V2.1 Double/Quadro Speed | Keen Acid | ~1991 | 2624, 2625 | multispeed hacks |
| DMC V4.0 Double/Quadro Speed | Keen Acid | ~1991 | 2604, 2605 | multispeed hacks of V4 player |
| DMC V4.0 Six Speed | Graffity | ? | 2606 | |
| DMC 4 25Hz | MultiStyle Labs | ? | 193910 | half-speed variant |
| DMC V4.1A | The Ancient Temple | ? | 216165 | |
| DMC V4.2 | Sonic Screams | ? | 35088 | |
| DMC V5.0 Scaner | Keen Acid | ? | 40290 | memory scanner — layout heuristics |
| DMC V5.01B | Chaos | ? | 236892 | |
| DMC V5.1 Packer | Zeux | ? | 236893 | packer — packed format |
| DMC V5.4 Packer | Samar Productions | ? | 137786 | V5.4's packer (noted buggy in HVMEC lore) |
| DMC Pro. Music Player V4.01(+) | XL/Xlcus (+Motiv 8) | 1995/96 | 62329, 98581, 2627 | standalone V4 player; zip fetched: dmc4.01+.zip |
| DMC Multi Music Player 3 | Xlcus | 1995 | 250026 | multi-tune player |
| DMC V4.0 Double Player | Yardies | 1995 | 93870 | plays two V4 tunes at once |
| DMC 4.y Player | Onslaught | 1996 | 46812 | |
| DMC 5.1 Player | Morbid/Onslaught | 1997 | 46815 | standalone V5.1 player; zip fetched: DMC_5.1_Player_ONS.zip |
| DMC V2.0+ | Collision | 1992 | 17200 | |
| DMC 4 Editor 1.0 / 1.1 | Logan/Slackers | 2025 | 250645, 251057 | cross-platform editor; embeds Brian's V4 player (see dmc4editor_embedded_player_notes.md) |

## DMC V7.0 release page (id=2629) — comments verbatim-ish

- Credits: code Axl (Area Team/Unreal), **Brian (Graffity/The Imperium
  Arts)**, Ray (Area Team/Unreal).
- **Ray (2005-12-02):** based on an earlier version [V4]; team added
  "1-5 multiple songs, multi channel play" and cassette/turbotape support.
  "Because added code grows up to 50% of original Brian's size, it becomes
  nightmare to make new improvements." Team later created TFX instead.
- **The Syndrom (2005-11-07):** "Please don't get it wrong - it's not
  really Version 7 of the famous DMC, the latest official version was
  v6.0." — V7 is "an adopted v4.0, which someone released as v7.0 without
  permission."
- Downloads: ftp://c64.rulez.org/pub/c64/Tools/Music/Editor/DMC_V7.zip,
  http://www.unreal64.net/downloads/c64/dmc7_0.prg,
  http://csdb.dk/getinternalfile.php/64791/dmc7_0.prg

**Implication for us:** V7 SIDs should parse with the V4 extractor
(player code is Brian's V4 + editor-side additions); the V5 branch is the
separate format (8-byte instruments, 2-byte tables).

## Pouet DMC 4.0 (prod 13452) comment links

- FUNET mirror of editors: http://www.funet.fi/pub/cbm/c64/audio/editors/
  → resolves today to http://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/
  which carries: `demo_music_creator_v2.1db.prg`, `v2.1qd.prg`,
  `v4.0qu.prg`, `v4.0sx.prg`, `DMC-v4.0.prg`, `dmc4.0.prg` (no docs/source).
- HVMEC editor control list (old lycos URL dead; current:
  https://hvmec.altervista.org).

## HVMEC version inventory (https://hvmec.altervista.org/blog/?p=700)

Versions hosted/known: v2.0, v2.1+ [1x/2x/4x], v4.0 [1x/2x/4x], v4.0 pro,
v4.0y, v4.3, v4.3++, v4.G, v4.Y pro, v5.0, v5.0+, v5.01B, v5.1, v5.1+,
v5.1 [14x], v5.1x, v5.1Y, v5.4, v5.Z [6x], v7.0, v7.1beta, GMC V1.0/1.6/2.0.
Key quote: "The last official release was 5.1, and there's a still
unreleased 6.0 ... All the so called 7.x versions are hacked 4.0 editors."
Downloads fetched: DMC_V5.prg, DMC-V5.0-Packer (Motiv 8), DMC_V5_Depacker,
dmc_5_docs.txt (→ hvmec_dmc5_manual.md).

## Archive.org

- `d64_DMC_v5.0_Toolkit_2002_CreaMD-DMagic` — CreaMD DMC v5.0+ toolkit
  d64 (fetched; contains DMC5.0+ editor, V5 packer, "DMC 5.0 INFO/SYN"
  noter, TFX27 test files; no source).
- `d64_Demo_Music_Creator_v5.1Y_19xx_-` — v5.1Y editor disk (not fetched).
