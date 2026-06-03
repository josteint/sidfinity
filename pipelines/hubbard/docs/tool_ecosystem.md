---
source_url: multiple
sources:
  - https://github.com/Galfodo/SIDdecompiler
  - https://github.com/cadaver/sidid
  - https://github.com/WilfredC64/player-id
  - https://github.com/c64cryptoboy/ChiptuneSAK
fetched_via: compiled from multiple sources
fetch_date: 2026-04-11
author: unknown
content_date: 2026-04
reliability: secondary
---
# Rob Hubbard Decompiler — Tool Ecosystem & GitHub Resources

Consolidated from GitHub searches, April 2026. Covers all known tools that parse,
identify, or work with Rob Hubbard's C64 SID music format.

## Tier 1: Directly Useful for Building Our Decompiler

### SIDdecompiler (Galfodo/SIDdecompiler)
- **URL:** https://github.com/Galfodo/SIDdecompiler
- **Language:** C++
- **Key file:** `src/SIDdisasm/STHubbardRipper.cpp`
- **What it does:** Traces 6502 execution in SID files, generates relocatable assembly.
  Has Hubbard-specific ripper that finds songs, instruments, sequences, and freq tables
  via instruction pattern matching.
- **Status:** Full source extracted in `github_siddecompiler_hubbard_ripper.md`
- **Value:** The pattern matching approach and data structure addresses are directly
  applicable to our decompiler. Same technique as our `gt2_parse_direct.py`.

### SIDID (cadaver/sidid)
- **URL:** https://github.com/cadaver/sidid
- **Config:** `sidid.cfg` contains byte signatures for Rob_Hubbard, Rob_Hubbard_Digi,
  Bjerregaard variant, Giulio_Zicchi variant, Paradroid/HubbardEd, Paradroid/Lameplayer
- **Status:** Full signatures extracted in `sidid_signatures.md`
- **Value:** Detection — confirm a SID uses Hubbard's engine before parsing.
  We already have local `tools/sidid` and `tools/sidid.cfg`.

### player-id (WilfredC64/player-id)
- **URL:** https://github.com/WilfredC64/player-id
- **Language:** Rust
- **What it does:** Multi-threaded SID player identification using BNDM search algorithm.
  Uses same sidid.cfg format. MIT licensed.
- **Value:** Faster alternative to sidid for batch scanning. Same signatures.

### ChiptuneSAK (c64cryptoboy/ChiptuneSAK)
- **URL:** https://github.com/c64cryptoboy/ChiptuneSAK
- **Language:** Python
- **What it does:** Universal SID music pipeline. Runs SID through 6502 emulator,
  captures SID register writes, converts to intermediate "chirp" representation.
  Supports PSID and some RSID. Can export to MIDI, GoatTracker, LilyPond, and other formats.
- **Key insight:** Their SID importer is based on Cadaver's siddump tool (same as ours).
  They capture register writes via emulation rather than parsing the data format directly.
- **Key modules:** `chiptunesak/sid.py` (SID register capture + note extraction),
  `chiptunesak/chirp.py` (intermediate representation), `chiptunesak/thin_c64_emulator.py`
  (6502 emulation with I/O tracking), `chiptunesak/emulator_6502.py` (CPU emulation).
- **Note event detection:** Triggers on: (1) first play call, (2) silent-to-active transition,
  (3) frequency change on active note, (4) gate toggle within play routine, (5) gate-off
  during release phase. Uses ADSR release time tables to track envelope state.
- **Freq-to-note conversion:** `midi_note = log2(freq_arch / base_freq) * 12 + offset`,
  with PAL/NTSC-aware tuning and vibrato margin to avoid false note changes.
- **Multispeed detection:** Compares CIA 1 timer A latch vs standard PAL/NTSC values;
  >30% deviation triggers multispeed mode.
- **Hubbard notes:** README lists "A Rob Hubbard engine" as a proposed exporter target,
  but it is NOT implemented. No Hubbard-specific parsing exists.
- **Value:** Validation oracle — run Hubbard SID through ChiptuneSAK, compare extracted
  notes against our decompiler output. Their note detection logic (especially the vibrato
  margin and gate-off tracking) could inform our comparison methodology.
- **Limitation:** Does NOT parse Hubbard's data format specifically; it's a generic
  register-level extraction. Won't give us instrument definitions or pattern structure.
  Instrument detection is a placeholder (all notes get instr_num=1).

### desidulate (anarkiwi/desidulate)
- **URL:** https://github.com/anarkiwi/desidulate
- **Language:** Python
- **What it does:** Analyzes SID register dumps from VICE emulator (-sounddev dump).
  Produces WAVs, MIDI, Pandas dataframes of SID "instruments" and performances.
- **Architecture:** Pandas-based pipeline: VICE dump -> reg2state (sidlib.py) -> state2ssfs
  (sidwrap.py) -> SSF dataframes -> MIDI/WAV/SidWizard output.
- **SSF concept:** "SID Sound Fragments" — discrete sound units bounded by gate transitions
  (GATE 0->1). Each SSF captures all register changes for a voice between gate triggers.
  Redundant register writes are eliminated.
- **Key modules:** `sidlib.py` (register parsing, reg2state, voice decoding, control bit
  extraction), `ssf.py` (SSF class with MIDI mapping, percussion detection, waveform
  analysis), `sidwrap.py` (SID emulation wrapper, pyresidfp, ADSR timing tables),
  `ssf2midi.py` / `ssf2wav.py` / `ssf2swi.py` (format converters).
- **Percussion detection:** Noise waveform + short duration + initial pitch drop >2
  semitones. Maps to MIDI drum types (kicks, snares, hi-hats) by frequency characteristics.
- **Register parsing:** Reads VICE `-sounddev dump` CSV, compresses consecutive writes,
  pivots to per-voice columns, decodes control bits (gate, sync, ring, test, tri, saw,
  pulse, noise), extracts 16-bit frequency from lo+hi registers.
- **Value:** Validation approach — compare register-level behavior. The SSF concept
  (gate-bounded sound fragments) maps well to Hubbard's note structure. Percussion
  detection could help classify Hubbard's drum instruments.
- **Limitation:** Register-level only, no format parsing. Not Hubbard-specific.

### Restore 64 (restore64.dev)
- **URL:** https://restore64.dev/ (also https://restore.datucker.nl/)
- **Language:** JavaScript (runs entirely in browser, no server upload)
- **What it does:** Browser-based C64 PRG disassembler with auto-depacking (370+ packers),
  SID player detection (787 signatures from SIDID database), and reassemblable assembly output.
- **Analysis features:** Multi-pass control flow tracing with register/flag state tracking,
  IRQ/NMI handler discovery, self-modifying code detection, jump table/RTS trick identification,
  hardware register decoding (250+ named registers with bitfield comments), PETSCII string
  recognition.
- **SID capabilities:** Automatic init/play address location via IRQ vector analysis,
  register write patterns, and call graph tracing. Multi-tune support with confidence
  scoring and SID data bounds detection.
- **Output formats:** KickAssembler (primary), ACME, 64tass — all with correct syntax,
  directives, and addressing mode notation.
- **Value:** Interactive disassembly of Hubbard SIDs in the browser. Can quickly examine
  any SID file's code structure, identify data regions, and see hardware register writes
  with full annotation. The 787 SIDID signatures should identify Hubbard's engine.
  Useful for spot-checking specific SIDs during decompiler development without needing
  to set up a local disassembler.
- **Limitation:** PRG-oriented (may need to strip PSID header first). No Hubbard-specific
  data structure labeling (unlike SIDdecompiler). Browser-only, not scriptable for batch use.

## Tier 2: Useful for Reference / Validation

### JC64dis (ice00/jc64)
- **URL:** https://github.com/ice00/jc64
- **Itch.io:** https://iceteam.itch.io/jc64dis
- **Language:** Java
- **What it does:** Iterative disassembler for SID, PRG, MUS, CRT, VSF files.
  GUI-based. Supports Rob Hubbard's Companion player format.
- **Value:** Could be used to manually disassemble specific Hubbard SIDs for
  comparison. The "iterative" approach (user guides disassembly) may reveal
  data boundaries that automated tools miss.
- **Limitation:** Not open about format-specific Hubbard support. GUI-only.

### SID Factory II (Chordian/sidfactory2)
- **URL:** https://github.com/Chordian/sidfactory2
- **Language:** C++
- **What it does:** Cross-platform SID music editor. Imports GoatTracker (.sng),
  CheeseCutter (.ct), and MOD files. Does NOT import raw SID files or
  Hubbard-format data.
- **Value:** Limited for our purposes. No Hubbard importer exists.
  The converter code handles only tracker formats, not player-specific data.

### DeepSID (Chordian/deepsid)
- **URL:** https://github.com/Chordian/deepsid
- **Language:** PHP/JavaScript
- **What it does:** Online SID player with HVSC browsing, player identification
  (uses sidid internally), per-song metadata.
- **Key file:** `php/sid_id.php` — wraps sidid for web use
- **Value:** The DeepSID website (https://deepsid.chordian.net/) is useful for
  quickly checking any Hubbard SID's metadata, player ID, and playback.
  Shows Rob Hubbard's complete HVSC directory at
  https://deepsid.chordian.net/?file=MUSICIANS/H/Hubbard_Rob/

### GoatTracker 2 (cadaver, various forks)
- **URL:** https://github.com/leafo/goattracker2 (fork)
- **URL:** https://github.com/jansalleine/gt2fork (fork)
- **URL:** https://github.com/jpage8580/GTUltra (extended fork)
- **What it does:** C64 music tracker/editor. Our entire existing pipeline is
  built around GT2's format. No Hubbard import capability.
- **Value:** None specific to Hubbard. Already thoroughly understood.

### CheeseCutter (theyamo/CheeseCutter)
- **URL:** https://github.com/theyamo/CheeseCutter
- **Language:** D
- **What it does:** SID music editor using reSID. No Hubbard import.
- **Value:** None for Hubbard decompiler.

### libsidplayfp (libsidplayfp/libsidplayfp)
- **URL:** https://github.com/libsidplayfp/libsidplayfp
- **What it does:** C++ SID emulation library. Has composer-specific filter tuning
  (Rob Hubbard: filter_range=0.700, filter_curve=0.35) but no format-level parsing.
- **Value:** We already use this (siddump is built on it). The filter parameters
  are useful for audio comparison accuracy.

## Tier 3: Historical / Community Resources

### C=Hacking Issue #5 Disassembly
- **URL:** https://www.1xn.org/text/C64/rob_hubbards_music.txt
- **Status:** Full content captured in `chacking_hubbard_disassembly.txt`
- **Value:** THE primary reference. Annotated 6502 disassembly of Monty on the Run.

### CSDb Rob Hubbard Editors
- Rob Hubbard Editor by Moz(IC)art (1989): https://csdb.dk/release/?id=75124
- Rob Hubbard Music Editor by Mirror (1988): https://csdb.dk/release/?id=222633
- The Rob Hubbard Sound Editor V2.0: https://csdb.dk/release/?id=129184
- **Value:** These are C64 native editors that understand the Hubbard format.
  Could be useful for testing — compose in editor, export, verify our decompiler
  can round-trip the data.

### Cadaver's Music Programming Essay
- **URL:** https://cadaver.github.io/rants/music.html
- **Value:** Discusses Hubbard's vibrato implementation (frequency difference to
  next semitone, compensated across octaves) and hard restart technique.
  Helpful for understanding the engineering behind the format.

### VGMPF Wiki
- **URL:** https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)
- **Status:** Key info captured in `vgmpf_driver_evolution.md`

## Summary: What Exists vs What We Need

### Already solved by others:
- Player DETECTION (sidid signatures identify Hubbard engine reliably)
- Data LOCATION (SIDdecompiler finds songs, instruments, sequences, freq table)
- Format DOCUMENTATION (C=Hacking #5 disassembly covers the early driver fully)

### NOT solved by others (our decompiler must do this):
- Complete DATA EXTRACTION from all ~82 Hubbard SIDs into structured format
- Handling VARIANT DIFFERENCES across 30+ games (later drivers with table-based
  drums, table-based PWM, filter control, arpeggio tables, transposition)
- Converting extracted data to USF for our rebuild pipeline
- Generating V2 player code that accurately reproduces all effects
- Handling the DIGI VARIANT (4-bit PCM via $D418)

### Recommended approach:
1. Use sidid to detect Rob_Hubbard vs Rob_Hubbard_Digi vs variants
2. Use SIDdecompiler's pattern matching to locate data structures
3. Parse data using format knowledge from C=Hacking disassembly
4. Handle variants by detecting which effects/features are present in each SID
5. Validate against register dumps (siddump/ChiptuneSAK/desidulate)
6. Use Restore 64 for interactive spot-checking of individual SIDs during development

### Validation strategy:
- **ChiptuneSAK:** Run Hubbard SID -> extract note events -> compare against our decompiler's
  extracted notes. Their vibrato margin and gate-off tracking are sophisticated enough to
  handle Hubbard's effects. No instrument data available from this path.
- **desidulate:** Run Hubbard SID through VICE -> dump registers -> extract SSFs -> compare
  instrument characteristics (ADSR, waveform sequences, PWM curves) against our parsed
  instrument data. The SSF concept maps directly to Hubbard's gate-bounded notes.
- **siddump:** Our existing approach — frame-by-frame register comparison with jitter
  tolerance. Most rigorous but also most sensitive to timing differences.
