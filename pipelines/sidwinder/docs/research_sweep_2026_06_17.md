---
source_url: multiple (see individual files)
fetched_via: websearch+direct
fetch_date: 2026-06-17
author: research sweep (automated)
content_date: 2026-06-17
reliability: secondary (synthesis)
---

# SIDwinder Research Sweep — 2026-06-17

## Key findings

### Identity

- **Engine:** SIDwinder (Taki's SIDwinder Music Editor)
- **Author:** Balázs Takács, handle "Taki", group Natural Beat, Hungary
- **Original code:** 1994 (internal, never released until 1999)
- **First public release:** 1999 (V01.22 binaries only; player source included)
- **GPL source release:** 2000-03-12 (V01.23, by TLC/Coroners as Plus/4 port)
- **CSDB:** https://csdb.dk/release/?id=66494 (V01.22)

### Sources obtained this session

| File | Location | Description |
|---|---|---|
| SIDW0122.txt | docs/src/ | Taki's original 804-line V01.22 user manual |
| GENERAL.txt | docs/src/ | Full story/history doc (TLC + Taki's section) |
| HISTORY.txt | docs/src/ | Version history editor/player/packer |
| SUMMARY.txt | docs/src/ | Feature summary and command reference |
| PROGRAMM.txt | docs/src/ | Programmer notes (cross-compilation guide) |
| README.txt | docs/src/ | Package README |
| PLAYER.ASM | docs/src/ | V01.23 player 6502 source (1167 lines, TASM syntax) |
| PLAY0122.ASM | docs/src/ | V01.22 player source (reconstructed) |

All from: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip

### Name collision warning

"SIDwinder V0.2 - Preview" (CSDB release #253271, 2025) by Raistlin/Genesis Project is
a completely **unrelated tool** — a visual SID music player/equalizer visualizer. The name
overlap is coincidental. Taki's SIDwinder is the music tracker/editor.

### Versions

| Version | Year | Status |
|---|---|---|
| V01.14 | 1994 | Never released |
| V01.20 | 1994 | Never released; source survives |
| V01.21 | 1994 | Never released; "nobody ever used this" |
| V01.22 | 1994/1999 | First public release; source mostly lost |
| V01.23 | 2000 | GPL source release; C64+Plus/4 dual-platform |
| V01.24 sub030 Enhanced | unknown | Unofficial; evidence via YouTube only |

### Sidid signature

```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```
(from cadaver/sidid sidid.cfg)

### Engine architecture summary

Three-voice SID tracker with flat sequence architecture:
- **Track layer**: 3 independent track tables with transpose, volume slide, sector-jumps
- **Sector layer**: instruction sequences (Snd/Dur/Gld/notes/Finish), 96 sectors max
- **Instrument layer**: 7-byte presets (AD, SR, gate-off-timer, 4 effect pointers)
- **Effect tables**: arpeggio/waveform, filter, pulse-width, vibrato/slide
  - All tables: repeat-count + data columns, $FF = jump
  - Arpeggio unique: $90..$FE = "repeat last waveform N more times" (space saving trick)
- **Glide table**: 16 entries of 16-bit absolute speeds (not note-adaptive — known limitation)
- **Multi-speed**: $1003 (first call/frame) + $1006 (subsequent), up to 16× in V01.23
- **Filter**: global, runs on voice 1 only; $D418 = volume OR filtertype
- **PAL only**: frequency tables hardcoded for 985248 Hz (C64) or 885 kHz (Plus/4)

### Key differences from other engines in this project

- **vs Hubbard '85**: no "init style" complication — standard PSID init+play model;
  much simpler track structure (flat sector pointers, no orderlist/pattern concept)
- **vs Future Composer**: completely different architecture; no global sequence/pattern
  system; effects are step-programmable tables not FC-style programs
- **vs DMC V4**: mentioned by Taki himself as inspiration (F4=liveplay, Gld.XX similar
  to DMC's, chord arpeggio concept); but cleaner separation of track/sector/sound layers;
  no per-frame Vol.XX/Rel.XX in sector (deliberately removed for rastertime)

### HVSC coverage

- existing research.md stub: 117 SIDwinder SIDs in HVSC84
- All by Taki/Natural Beat; no other composers identified using this engine

## Leads to follow

1. **Manual Wayback browse**: http://www.sch.bme.hu/~takinb — Taki's BME homepage
   (linked from V01.22 docs; may have snapshots showing extra releases or docs)

2. **V01.24 sub030 Enhanced**: YouTube video at https://www.youtube.com/watch?v=6ZsX3D_vUuY
   shows a "V01.24 sub030 Enhanced" version playing "Draxish". Source/binary not found
   on any FTP. Worth searching: CsDb, Hungarian C64 forums, c64.rulez.org

3. **c64.rulez.org FTP**: ftp://c64.rulez.org/pub/c64/Tools/Music/Editor/ — listed in
   V01.23 docs as official mirror; may have additional versions or related music files

4. **HVSC subfolder**: hvsc85/MUSICIANS/T/Taki/ — all 117 SIDwinder SIDs for disassembly
   candidates; run sidid on a sample to confirm signature match rate

5. **Plus/4 World discussion forums**: may have more detailed TLC/Taki correspondence
   about the format, known bugs, and planned V01.24 features

6. **Cubic Player d64**: ftp://c64.rulez.org/pub/c64/Demos/n/Natural_Beat/Cubic_Player.zip
   — contains 13 Taki demo songs in SIDwinder format; useful as reference corpus

7. **HVSC BUGlist / STIL entries**: check if any SIDwinder SIDs have known issues noted
   in HVSC's BUGlist.txt or STIL.txt (song title/info list)

8. **Disassemble PLAYER.ASM ZP map**: PLAYER.ASM is in docs/src/ — map out all ZP
   variable addresses (pt=$FB/$FC is documented; dur_dc, finish, acnote, etc. need
   to be extracted from the ASM) for the future extract/compose pass
