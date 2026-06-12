---
source_url: https://csdb.dk/release/?id=251057 (DMC 4 Editor 1.1 win64 zip, download "dmc4editor11_win64.zip")
fetched_via: direct (zip downloaded from CSDb; player blob carved out of dmc4editor.exe)
fetch_date: 2026-06-12
author: editor by Logan/Slackers, embedded player by Brian/Graffity ("code contributions from Brian" per CSDb credits; blob self-identifies "player by brian of graffity 91")
content_date: player 1991; editor build 2025-03-15
reliability: primary (the actual DMC4 player binary, blessed by the original author)
---

# DMC4 reference player binary, carved from DMC 4 Editor 1.1 (Windows)

**No community-annotated disassembly of the DMC4/5 player exists anywhere
public (GitHub, codebase64, CSDb, archive.org — all checked 2026-06-12).**
The best available substitute is the *original player binary itself*, which
the modern cross-platform "DMC 4 Editor" by Logan/Slackers embeds for its
PRG-export / playback path. Logan's editor credits Brian/Graffity for code,
so this blob is the canonical V4 player.

## Extraction

- File: `dmc4editor11_win64.zip` → `win64/dmc4editor.exe` (883,200 bytes,
  build 2025-03-15)
- The exe contains the player image **at exe file offset `0x7F300`**,
  load address `$1000`, found by matching the sidid DMC V4.x signature
  (`FE ?? ?? BD ?? ?? 18 7D ...` hits at exe offsets 0x7F87C and 0x8028C)
  and scanning back for the JMP table.
- Saved here as **`dmc4_player_embedded_1000.bin`** (0x1000 bytes carved;
  the player + tables occupy roughly $1000-$18FF, the tail of the carve
  beyond the music-data start is editor scratch — trim against a real rip
  when doing the disassembly).
- A **second** copy of the play routine exists in the exe (sig hit at
  0x8028C ≈ carve offset +$F8C) — i.e. another player variant without the
  standard $1000 jump table immediately before it (likely the editor's
  preview/2x variant). Not carved; revisit if the first blob mismatches
  HVSC rips.

## Blob structure (verified against the carve)

| Offset ($1000-rel) | Content |
|---|---|
| +$00 | `JMP $101D` (init: A=subtune) |
| +$03 | `JMP $1085` (play) |
| +$06 | `JMP $162F` (extra entry 1) |
| +$09 | `JMP $163E` (extra entry 2) |
| +$0C | player variables: `00 00 00 FE FE FE 18 3C 37 02 05 03 01 00 00 00 00` |
| +$1D.. | screen-coded text `"-player by brian of graffity 91-"` |
| +$6A8 (per layout docs) | freq table hi — carve shows `01 01 01 01 01 01 01 01 01 01 01 02` at +$6A8 ✓ matches the documented V4 layout in research.md |

Note: research.md's "Entry Points" table (init at +$0000, tune select at
+$001D) and this blob agree once you see +$0000 *jumps to* $101D — the
init/tune-select routine IS at +$1D..$84, play code at +$85. The four-entry
JMP table ($101D/$1085/$162F/$163E) matches the editor-saved layout.

## Why this matters

- This is a clean, unrelocated, unpacked V4 player at the canonical $1000
  base — the ideal seed for `tools/seed_disassembly.py` and a
  hand-annotated `pipelines/dmc/<engine>/disassembly.s`.
- The Windows editor itself is a battle-tested closed-source parser of the
  whole format (it has a "DMC Tune Seeker" that scans HVSC and imports DMC
  tunes from SID/PRG, plus PRG export with relocation). Its ReadMe is in
  `tmp/dmc_hunt/dmc4editor_x/win64/ReadMe.txt`. If a format edge case is
  ambiguous, diffing our extractor's accept/reject set against the Tune
  Seeker's is a practical oracle.

## Companion binaries fetched this wave (all in tmp/dmc_hunt/)

| File | What | Source |
|---|---|---|
| `DMC_V5.prg_` | DMC V5.0 editor PRG | hvmec.altervista.org |
| `DMC-V5.0-Packer-19xxMotiv-8.prg_` | V5 packer | hvmec.altervista.org |
| `DMC_V5_Depacker.prg_` | **V5 depacker** (must know packed layout — disassembly target) | hvmec.altervista.org |
| `DMC_5.0_SCANNER.prg` | V5 scanner (finds DMC data in memory — encodes layout heuristics) | TND editors disk |
| `dmc4.01plus_x/dmc4.01+.d64` → `DMC PRO4` | "DMC Pro. Music Player V4.01+" by XL/Xlcus (standalone player+linker) | csdb.dk/release/?id=2627 |
| `DMC_5.1_Player_ONS_x/DMC 5.1 PLAY_[O]` | "DMC 5.1 Player" by Morbid/Onslaught, SYS2063, copies player data from $0C66-up to $0400/$0500 region | csdb.dk/release/?id=46815 |
| `dmc5_toolkit.d64` | CreaMD "DMC v5.0+ Toolkit" (2002): DMC5.0+, V5 packer, info noter, TFX test files | archive.org d64_DMC_v5.0_Toolkit_2002_CreaMD-DMagic |
| `DMC Music Editors[TND].d64` | TND pack: V2.1, V4.0 + V4 docs noter, V5.0, V5.0+, V5 packer, V5 scanner, V7.0 | tnd64 (prior wave) |
