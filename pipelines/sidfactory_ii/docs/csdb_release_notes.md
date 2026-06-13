---
source_url: https://csdb.dk/release/?id=210571 (and subsequent release pages)
fetched_via: direct
fetch_date: 2026-06-13
author: various (JCH/Chordian, Laxity, Youth)
content_date: 2020-07-16 through 2026-03-14
reliability: primary
---

# SID Factory II — CSDb Release Notes

## Release Chronology

All CSDb entries use type "Other Platform C64 Tool".

### SID Factory 0.5 (alpha 1) — CSDb #39519
- **Date:** 2 September 2006
- **Author:** Laxity (Maniacs of Noise / Vibrants)
- **Source:** https://csdb.dk/release/?id=39519
- **Notes:** First public release of the pre-II editor. Contains multiple driver versions:
  - Driver 5.02: Updated, now has portamento functionality
  - Driver 6.03: Corrected severe bug in Driver 6.02
  - Includes 4 demo SID files. Full-screen pattern editing, pointer tables per voice.
  - JCH compatibility noted: easy migration from JCH format. Tempo table alongside multispeed.

### SID Factory II build 20200604 — (first alpha, private)
- **Date:** July 2019 (private Laxity alpha); June 2020 (documented first build)
- **Notes:** Laxity released the first alpha in a private group in July 2019. JCH joined in May 2020.

### SID Factory II build 20200716 — CSDb #210571
- **Date:** 16 July 2020
- **Source:** https://csdb.dk/release/?id=210571
- **Credits:**
  - Code: Laxity (Bonzai, Maniacs of Noise, Vibrants)
  - Music: JCH (Vibrants)
  - Help: JCH (Vibrants), Youth (Heatwave)
- **Platforms:** Win32, macOS
- **Drivers shipped:** 11–16 (test compositions included for each)
- **Notes:** First CSDb-listed public release. 17 music tracks included as driver capability demos.
  Key demo SIDs: "Driver 11 Test (Arpeggio)", "Driver 12 Test (The Barber)", "ICC2019 Intro".
  Rating awaiting 8 votes at time of scrape.

### SID Factory II build 20200718 — CSDb #210570
- **Date:** 18 July 2020
- **Source:** https://csdb.dk/release/?id=210570
- **Credits:**
  - Code: Laxity (Bonzai, Maniacs of Noise, Vibrants)
  - Music: JCH (Vibrants)
  - Help: JCH, Youth
- **Platforms:** Win32, macOS, source code zip
- **Includes:** NP20 source tunes (NP20_Source_Tunes_v1.zip — 59 downloads)
- **Driver capabilities per included test SIDs:**
  - Driver 11: Arpeggio, Tie Notes, Filter
  - Driver 12: Minimal ("The Barber")
  - Driver 13: Hubbard-style driver
  - Driver 14: Heavy/Medieval/Long Sequence
  - Driver 15: Mood composition test
  - Driver 16: Busy pattern test

### SID Factory II build 20200911
- **Date:** 11 September 2020
- **Key additions (from blog.chordian.net changelog):**
  - Help overlay (F12)
  - Color schemes (Ctrl+F7)
  - Driver 11.02 release

### SID Factory II build 20210104 — CSDb #210568
- **Date:** 4 January 2021
- **Source:** https://csdb.dk/release/?id=210568
- **Credits:** Code: JCH, Laxity, Youth (Heatwave)
- **Platforms:** Win32, macOS, Linux
- **Key additions (from blog.chordian.net):**
  - Embedded SF2Converter (load MOD, SNG, CT directly in editor)
  - Duplicate sequence hotkeys
  - Filter enable capability
- **Driver update:** Driver 11.02 now default (commands: pulse program index, tempo change, main volume)

### SID Factory II build 20211230 — CSDb #213369
- **Date:** 13 January 2022
- **Source:** https://csdb.dk/release/?id=213369
- **Credits:**
  - Code/Music/Docs: JCH (Vibrants)
  - Code/Music/Design/Concept: Laxity (Bonzai, Maniacs of Noise, Vibrants)
  - Code/Music: Youth
  - Music: Yavin (Heatwave)
- **Platforms:** Win32 (357 dl), Linux (89 dl), macOS (77 dl)
- **Key additions:**
  - Song list descriptions
  - Zero page address specification in packer
  - Driver 11.04: note delay (0-F ticks)
  - macOS M1 compatibility fix
  - Linux compilation fixes
  - Filter table stability fix
- **Developer comment:** Youth: "Source code and changelog at https://github.com/Chordian/sidfactory2"
- **Rating:** 10/10 (8 votes)

### SID Factory II build 20220914 — CSDb #222255
- **Date:** 14 September 2022
- **Source:** https://csdb.dk/release/?id=222255
- **Credits:**
  - Code: JCH, Laxity, Youth
  - Music: Animal (Mahna Mahna), JCH, Laxity, Vincenzo, Yavin, Youth
  - Design: JCH, Laxity; Bug-Fix: kb, Vincenzo; Docs: JCH
- **Known as:** "The multisong release"
- **Key additions (from blog.chordian.net):**
  - Multi-song support (shared sequence libraries)
  - Sequence copy/paste
  - Configurable virtual piano layout
- **Changelog:** Full details at https://github.com/Chordian/sidfactory2

### SID Factory II build 20221007 — CSDb #224223
- **Date:** 7 October 2022
- **Source:** https://csdb.dk/release/?id=224223
- **Credits:** Code: JCH, Laxity, Youth (Bug-Fix); Music: Animal, Vincenzo, Yavin; Design/Docs: JCH, Laxity
- **Key fixes (from Youth's comment):**
  - Crash when converting NP20 and GT tunes
  - Crash when using a loop point beyond position 128
  - Bug where editing sequences was blocked before hitting play
- **Platforms:** Win32 (307 dl), Linux (78 dl), macOS (63 dl)

### SID Factory II build 20231002 — CSDb #235968
- **Date:** 2 October 2023
- **Source:** https://csdb.dk/release/?id=235968
- **Credits:**
  - Code: JCH, Laxity, Youth
  - Music: Animal, JCH, Laxity, Vincenzo, Yavin, Youth
  - Design: JCH, Laxity; Docs: JCH
- **Platforms:** Win32 (577 dl), Linux (131 dl), macOS (79 dl)
- **Key additions:**
  - Pulse width visualizers for all 3 channels
  - Filter cutoff visualization
  - Per-channel filtering indicators
  - New config option: `Visualizer.PulseWidth.Style`
  - New default driver: **11.05.00**
  - `Disk.Hide.Extensions` config: hides .sid/.wav/.mp3 in file browser
  - Window.Scale expanded from max 4.0 to 10.0

### SID Factory II build 20260314 — CSDb #260181
- **Date:** 14 March 2026
- **Source:** https://csdb.dk/release/?id=260181
- **Credits:**
  - Code/Music/Design/Concept/Docs: JCH (Vibrants)
  - Code/Music/Graphics/Design/Concept: Laxity (Bonzai, Maniacs of Noise, MultiStyle Labs, Vibrants)
  - Code: tubesockor (new contributor)
  - Code/Music: Youth
- **Platforms:** Windows, Linux, Linux ALSA, macOS, + PDF User Manual (106 dl)
- **Key additions:**
  - **ASID support**: Real hardware SID device playback via ASID/MIDI (thanks to tubesockor)
  - Fullscreen mode (Alt+Enter toggle)
  - Optional C64 ROM font (half height = twice the rows)
  - Integration with LouD's UsbSID-Pico firmware
- **Rating:** 10/10 (11 votes)

---

## Driver Version Progression (Driver 11 lineage)

| Driver Version | Key New Capability |
|---|---|
| 11.00 (sf2driver11_00.prg) | Baseline: pulse/filter/wave tables, arpeggio table, 12-bit PWM |
| 11.01 | (details not recovered from sources) |
| 11.02 | Commands: pulse program index, tempo change, main volume |
| 11.03 | Filter enable flag bit in instruments |
| 11.04 | Note delay (0-F ticks per row) |
| 11.04.01 | (patch to 11.04) |
| 11.05 / 11.05.00 | Pulse reset flag; became new default as of build 20231002 |

Other driver families (each with .prg variants):
- **12.x**: Minimal/simple driver
- **13.x**: Rob Hubbard emulation driver
- **14.x**: Short gate-off variant of driver 11
- **15.x**: Tiny driver mark I
- **16.x**: Tiny driver mark II (no commands)
- **np20.x**: NP20 (JCH NewPlayer 20) compatibility driver

Full list of .prg files in `SIDFactoryII/drivers/`:
```
sf2driver11_00.prg  sf2driver11_01.prg  sf2driver11_02.prg
sf2driver11_03.prg  sf2driver11_04.prg  sf2driver11_04_01.prg
sf2driver11_05.prg  sf2driver12_00.prg  sf2driver12_00_01.prg
sf2driver13_00.prg  sf2driver13_00_01.prg  sf2driver14_00.prg
sf2driver14_00_01.prg  sf2driver15_00.prg  sf2driver15_01.prg
sf2driver15_02.prg  sf2driver16_00.prg  sf2driver16_01.prg
sf2driver16_01_01.prg  sf2driver_np20_00.prg
```

## Leads to follow

- Download `SIDFactoryII_Win32_20211230.zip` (csdb.dk/getinternalfile.php/223870/) and extract the `documentation/` subfolder — each driver has a `.txt` file with its exact format specification.
- The most recent user manual PDF: `SIDFactoryII_20260314_User_Manual.pdf` (106 downloads from CSDb #260181).
- Source tunes: `NP20_Source_Tunes_v1.zip` (from build 20210104 release) — real NP20-format files for format validation.
- CSDb forum thread #142903 (roomid=14): SF2 developer discussion — was 503 at scrape time, retry.
- CSDb forum thread #152049: "Music Editor for Oldschool Mind" — retrieved 503, may have lineage discussion.
