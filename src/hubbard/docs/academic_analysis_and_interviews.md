---
source_url: multiple
sources:
  - http://www.1xn.org/text/C64/rob_hubbards_music.txt
  - https://codebase64.org/doku.php?id=magazines:chacking5
  - https://c64audio.com/products/master-of-magic-softography
  - http://www.atlantis-prophecy.org/recollection/?load=online_issues&issue=2&sub=article&id=19
  - https://www.gamejournal.it/driving-the-sid-chip-assembly-language-composition-and-sound-design-for-the-c64/
  - http://www.sidmusic.org/sid/rhubbard.html
  - https://www.c64.com/interviews/hubbard.html
  - https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/
fetched_via: compiled from multiple sources
fetch_date: 2026-04-11
author: local compilation (sources attributed individually)
content_date: 1993–2024
reliability: secondary
---
# Rob Hubbard Driver — Academic Analysis and Interview Sources

## Primary Technical Sources

### 1. C=Hacking Issue #5 (March 7, 1993) — McSweeney Disassembly
- **Author:** Anthony McSweeney
- **Content:** Complete annotated 6502 disassembly of the Monty on the Run driver
- **Online mirror:** http://www.1xn.org/text/C64/rob_hubbards_music.txt
- **Codebase64 wiki:** https://codebase64.org/doku.php?id=magazines:chacking5
- **Status:** The definitive technical reference for the "classic" (Phase 2) driver.
  Covers all subroutines, data format, effects implementation. See
  `monty_on_the_run_disassembly.md` and `data_format_reference.md` for extracted details.

### 2. "Master of Magic" — Official Rob Hubbard Softography (2023 book)
- **Author:** Chris Abbott (C64Audio.com)
- **Publisher:** C64Audio.com — https://c64audio.com/products/master-of-magic-softography
- **Content:** 6-year research project. Full-colour illustrated softography with:
  - History and interviews
  - 6502 assembly driver excerpts
  - Sections devoted to discussing driver variants and techniques
  - Game-by-game technical analysis
- **Blog excerpts:**
  - https://c64audio.com/blogs/rob-hubbard-master-of-magic/rob-hubbard-1985-on-the-run
  - https://c64audio.com/blogs/rob-hubbard-master-of-magic/rob-hubbard-thrusts-into-1986
- **Key revelation:** Cross-pollination between Atari POKEY driver and C64 driver —
  "vectors, wavetables, and function pointers" from Atari work integrated into the
  Hollywood or Bust experimental C64 driver.

### 3. Recollection Issue 2 — "Rob Hubbard's Music"
- **URL:** http://www.atlantis-prophecy.org/recollection/?load=online_issues&issue=2&sub=article&id=19
- **Content:** Technical analysis of driver architecture, including:
  - ~900-1000 byte code size
  - NoteWork/SoundWork dual-layer processing
  - Instrument 8-byte structure with effects flags
  - Drum synthesis technique (square-then-noise with frequency sweep)
  - Multi-song capability within single module
  - Historical significance: "ripped off by many famous groups"

### 4. "Driving the SID Chip" — Academic Article (G|A|M|E Journal)
- **URL:** https://www.gamejournal.it/driving-the-sid-chip-assembly-language-composition-and-sound-design-for-the-c64/
- **Framework:** Newman's affordance theory applied to SID chip programming
- **Key technical content:**
  - Driver size: "just 900-1000 bytes of code"
  - Two processing layers: Notework (pitch) + Soundwork (synthesis)
  - Main loop executes 3x per frame at 50Hz
  - 8-byte instrument definitions
  - Drum synthesis: bit 0 flag in effects byte
  - Reference to logarithmic vibrato using adjacent semitone frequency differences
  - Comparison with Martin Galway's approach: "Rob's sound emphasized rhythmic complexity
    and drum synthesis, while Galway's approach prioritized waveform manipulation and ring
    modulation"
  - Sample playback: Galway discovered DC offset glitch; Hubbard implemented independently
    later with loop-in-middle capability

### 5. ChipMusic.org Forum Thread
- **URL:** https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/
- **Content:** Community discussion of the driver (2 pages, access blocked by 403 at time
  of research). Referenced in multiple other sources.

## Interviews with Rob Hubbard

### SID Music Interview
- **URL:** http://www.sidmusic.org/sid/rhubbard.html
- **Key quotes about the driver:**
  - Changed driver code "fairly often to either add or delete some features"
  - "Conscious that the code had to be as quick as possible"
  - Would "optimize it for either space or processor speed"
  - "Although using a standard program format for the routine"

### c64.com Interview
- **URL:** https://www.c64.com/interviews/hubbard.html
- **Key quotes:**
  - "Most of it was simply done by multiplexing the three channels"
  - If the lead has rests, "put a fill or some effect in there"
  - Composed on paper first, wrote hex alongside notes, typed into assembler

### Remix64 Interview with Jason Page (2002)
- **URL:** https://remix64.com/interviews/interview-jason-page.html
- **Full transcript:** `remix64_jason_page_interview_full.txt`
- **Note:** Jason Page ("Jay") is a British game composer (Graftgold, Sony). He is NOT
  4mat (Matt Simmonds). Jason Page later created RobTracker (based on Hubbard's Digi
  routine). The 4mat GoatTracker converter (`lemon64_4mat_converter_thread.md`) is
  a separate project by a different person.
- **Key technical observations from the interview:**
  - MON (Maniacs of Noise) drums were superior because they used "lookup tables of
    pitch and waveform data" for rapid cycling, vs. simple triangle/noise flip
  - "You could tell if a tune was by Rob Hubbard or Martin Galway just by the sound
    of it. Not the actual notes, but how their audio routines were playing the SID."
  - Jason composed using multiple drivers: Sound Monitor, Rock Monitor, a MON-variant,
    Steve Turner's Graftgold routine, his own custom routine, ElectroSound
  - ElectroSound had bugs in the audio data code
- **Other Remix64 interviews of interest:**
  - Martin Galway: https://remix64.com/interviews/interview-martin-galway-by-claudio-sanchez.html
  - Rob Hubbard (multi-composer): https://remix64.com/interviews/c64-music-scene-by-steve-drysdale.html
  - Neil Brennan (Beam Software coder+composer): https://remix64.com/interviews/an-interview-with-neil-brennan.html

## Detection and Identification Tools

### SIDID (Cadaver)
- **GitHub:** https://github.com/cadaver/sidid
- **Config:** sidid.cfg contains 6 main Rob_Hubbard signatures plus sub-signatures
  for Digi, Giulio_Zicchi, and Bjerregaard variants
- **Details:** See `sidid_signatures.md`

### Player-ID (WilfredC64)
- **GitHub:** https://github.com/WilfredC64/player-id
- **Approach:** BNDM search algorithm, multi-core, uses sidid.cfg-compatible config
- **Signature contributors:** Wilfred Bos, iAN CooG, Professor Chaos, Cadaver, Ninja,
  Ice00, Yodelking

### SIDdecompiler (Galfodo / Prosonix)
- **GitHub:** https://github.com/Galfodo/SIDdecompiler
- **Approach:** Tracing 6502 emulator, generates relocatable assembly
- **Hubbard-specific:** `STHubbardRipper.cpp` with known instruction patterns
- **Details:** See `github_siddecompiler_hubbard_ripper.md`

## HVSC Collection Statistics

Rob Hubbard's HVSC directory (`MUSICIANS/H/Hubbard_Rob/`) contains 96 SID files.
Player identification breakdown:
- 82 (85%): Rob_Hubbard (standard player)
- 5 (5%): Jason_Page/RobTracker (digi variant cross-detection)
- 4 (4%): SidTracker64 (modern recreations, e.g., "New Frontier" from 2014)
- 2 (2%): Companion (early non-Hubbard-driver works)
- 3 (3%): Other engines

## Key Insight for Decompiler Work

The "classic" driver (Phase 2) covers the largest number of songs (~30+) and has the
best-documented data format. A decompiler targeting this format first would cover the
most ground. The later driver (Phase 4, ACE II era) adds table-based drums and PWM but
the exact byte-level format of those extensions is not publicly documented — it requires
reverse engineering from the SID files themselves.

The frequency table trick (out-of-range pitches addressing player variables) means the
decompiler must handle pitch values beyond the normal musical range gracefully. This is
used in Commando for the "galloping staccato" effect and potentially in other songs.
