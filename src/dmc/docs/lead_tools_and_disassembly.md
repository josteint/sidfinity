---
source_url: https://restore64.dev/, https://github.com/Galfodo/SIDdecompiler, https://sidpreservation.6581.org/sid-editors/, https://www.doussis.com/sidtoolbox/, https://dflund.se/~triad/krad/sidmidi.html
fetched_via: direct
fetch_date: 2026-04-11
author: multiple sources (Galfodo/Stein Pedersen for SIDdecompiler; Linus Walleij/Triad for sidmidi.html; unknown for restore64.dev and doussis.com)
content_date: 2017-10-19 (SIDdecompiler v0.5 release); unknown for others
reliability: secondary
---

# Lead: External Tools and Disassembly Resources for DMC Research

Research date: 2026-04-11

## 1. Restore64.dev

**URL:** https://restore64.dev/

### What it is
Browser-based C64 PRG disassembler. Runs entirely client-side (no API, no server
component). Auto-depacks 370+ packer formats and detects **787 SID player
signatures** from the SIDID database.

### Key capabilities
- Emulates a full 6502 CPU to run decompression stubs (not heuristic-based).
- Detects SID routines by analyzing IRQ vectors, register write patterns, and
  call graphs. Supports multi-tune programs with confidence scoring.
- Output format: **KickAssembler v5.25+ syntax** (primary). Also supports ACME
  and 64tass dialects with minor adjustments.
- Includes a curated collection of **300 top-downloaded C64 crack intros**,
  fully disassembled with syntax highlighting and label navigation.

### DMC relevance
- No explicit DMC mention on the site, but its SIDID database with 787
  signatures almost certainly includes DMC variants (SIDID is the standard
  C64 player identification database and DMC is one of the most common players).
- **Usage for our project:** We can drag-and-drop a DMC SID into Restore64 to
  get a KickAssembler disassembly with auto-detected code vs data regions. This
  is useful for verifying our own disassembly against a second opinion.
- **Limitation:** No API — purely browser-based, so we cannot batch-process
  DMC SIDs. Manual one-at-a-time analysis only.

### Action items
- [ ] Test with a known DMC SID (e.g., Laxity tune) to confirm it identifies
  the player engine and produces useful annotated output.
- [ ] Check if the "Top 300" collection includes any DMC tunes.


## 2. SIDdecompiler by Galfodo (Stein Pedersen / Prosonix)

**URL:** https://github.com/Galfodo/SIDdecompiler
**CSDb:** https://csdb.dk/release/?id=159804

### What it is
C++ tool (V0.5, released 2017-10-19) that takes a SID file, runs it through a
6502 emulator, and produces a **relocatable 6502 assembly source file**. Output
tested with 64tass assembler.

### How it works
1. Loads the SID, calls init and play via emulation.
2. Traces all executed instructions to distinguish code from data.
3. Tracks address operands to enable relocation.
4. Generates assembly source where all executed code is disassembled and all
   data references are made relocatable.

### Player-specific annotations
- **Rob Hubbard tunes only:** produces "slightly better documented" output with
  "non-generic label names for data of known purpose."
- No DMC-specific detection or annotations.
- No general player engine identification.

### Build
- CMake-based. Directories: `src/` (C++ source), `gcc/`, `vs2012/`, `vs2017/`,
  `vs2019/`. Pre-built binaries for Windows (32/64-bit), Linux x86_64, macOS.
- Source subdirectories: `HueUtil`, `SIDcompare`, `SIDdisasm`, `libsasm`,
  `libsasmdisasm`, `libsasmemu`, `sasm`, `sasmSIDdump`.
- Based on Lasse Oorni's (Cadaver) siddump 6502 emulator.

### Known limitations
- Very conservative: unexecuted code stays as data bytes.
- No timer-based sample playback support.
- Poor handling of multiple driver instances in one file.
- SIDs with IRQ setup or non-returning init not supported.
- Partial undocumented opcode support.

### DMC relevance
- **Useful for us:** Can produce a relocatable disassembly of any DMC SID that
  uses standard init/play calling convention. The traced-execution approach means
  we get accurate code/data separation.
- **Limitation:** No DMC-specific annotations. Output will have generic labels
  (`L1234`, `D5678`). We would need to overlay our own knowledge of DMC data
  structures onto the output.
- **Can we run it?** Pre-built Linux binary available. Worth building from
  source to have it in our toolchain.

### Action items
- [ ] Build SIDdecompiler from source or download Linux binary.
- [ ] Run it on 5-10 DMC SIDs and compare output to our own `dmc_parser.py`
  disassembly to cross-validate code/data boundaries.
- [ ] Check if the relocatable output helps us understand how DMC relocates
  its data tables.


## 3. SID Preservation Editors Page

**URL:** https://sidpreservation.6581.org/sid-editors/

### Status
**Site is temporarily down** (503 error, "This site has been temporarily
disabled, please try again later"). Wayback Machine also failed to retrieve
a cached version.

### Expected content
This site is known to host information about C64 SID music editors, including
DMC versions, download links, and historical documentation. It was previously
a key reference for SID editor preservation.

### Action items
- [ ] Retry periodically — the site may come back online.
- [ ] Search Wayback Machine with specific date ranges if direct access fails.
- [ ] Check if content is mirrored on CSDb or other C64 preservation sites.


## 4. SID Toolbox

**URL:** https://www.doussis.com/sidtoolbox/

### What it is
Browser-based SID file **header/metadata editor**. Supports PSID/RSID formats,
versions 1 through 4.

### Capabilities
- Drag-and-drop editing of SID file headers (title, author, copyright, load
  address, init address, play address, etc.).
- Raw hex editing of SID binary data.
- PSID vs RSID selection.
- Auto-generates filenames following HVSC naming conventions.
- Version 3/4 support for multi-SID chip compositions.

### DMC relevance
- **Not directly useful.** This is a header/metadata editor only — it does not
  understand any music format internals (no DMC, no GoatTracker, no player
  engine awareness).
- Could be marginally useful for inspecting/fixing SID headers on DMC files,
  but we already have our own PSID header parsing in `gt_parser.py`.

### Verdict
Low priority for DMC research. Skip.


## 5. Triad SID Player Routine (Linus Walleij)

**URL:** https://dflund.se/~triad/krad/sidmidi.html

### What it is
Pseudo-code documentation of a generic SID player routine, written by Linus
Walleij (Triad) based on his experience writing MIDIslave and using many C64
editors including SoundMonitor, Future Composer, JCH Editor, and others.

### Key algorithms documented

#### Hard restart
- Write `$00` to registers `$d400`-`$d406` exactly **2 frames (2/50 sec)**
  before next attack.
- Minimum time: **33 ms = 2^15 cycles** (per Dag Lem / reSID).
- Alternative: set test bit (`$08`) in waveform register `$d404`.
- Only needed for 6581 chip, not 8580.
- JCH player cited as exemplary implementation.

#### Waveform macro system
- Lookup table, can loop from a specific point OR end with a terminal byte.
- Updates register `$d404 + offset` each tick.
- Can modify ring modulation and sync bits.
- Speed is configurable (default divisor = 8 at 400 Hz processing = 50 Hz
  effective macro rate).
- Gate bit (bit 0) is OR'd from `note_is_on[]` state.

#### Arpeggio
- Lookup table of semitone offsets (upward from base note).
- Example: `$00, $03, $07` = minor chord.
- Tables can loop or terminate.
- Updates `$d400/$d401` with frequency from note table + offset.

#### Vibrato
- Additive curve modulation over base frequency (`$d400/$d401`).
- Parameters: amplitude and period, both per-instrument.
- Configurable delay before vibrato starts.
- Period is relative to processing frequency.

#### Pulse width vibrato
- Same structure as frequency vibrato but modulates `$d402/$d403`.
- Typically uses larger amplitude than frequency vibrato.
- Can use LFO (sinus, sawtooth, square) for modulation curve.

#### Filter modulation
- Can be macro-driven or wheel-driven.
- Registers: `$d415` (lo cutoff), `$d416` (hi cutoff), `$d417` (resonance).
- Most C64 players use only the high byte for filter cutoff.
- Resonance is 4-bit (high nybble of `$d417`); low nybble masked to `$0F`.
- Modulation shapes: sinus, sawtooth, square wave.

#### Note frequency table
Complete 95-note table provided (C-0 through B-7):
- Two arrays: `note_hi[95]` and `note_lo[95]` for 16-bit SID frequency values.
- Index 0 = C-0, Index 36 = C-3, Index 57 = A-4.
- Note: the document states "numbers in the C64 hardware reference manual are
  simply WRONG" and provides corrected values.

### DMC relevance
- **Highly relevant as architectural reference.** DMC uses the same fundamental
  architecture: waveform tables, arpeggio tables, pulse modulation, filter
  tables, hard restart. The pseudo-code describes the generic C64 player
  paradigm that DMC implements.
- **Key insight:** The processing hierarchy is:
  1. Instrument setup (one-time on note-on)
  2. Per-tick macro processing (waveform, arpeggio, pulse, filter)
  3. Per-tick continuous modulation (vibrato, pulse vibrato)
  4. Gate management on note-off
- This matches what we see in DMC player disassembly.
- **Caution:** DMC has its own specific implementation details (table formats,
  command encoding, tempo system) that differ from this generic description.
  Use this as conceptual reference, not as DMC specification.

### Action items
- [ ] Cross-reference these algorithms with our DMC disassembly to confirm
  which features DMC implements and how they map.
- [ ] Use the frequency table as a validation reference when decoding DMC
  note values.


## Summary of tool usefulness for DMC research

| Tool | Usefulness | Priority |
|------|-----------|----------|
| Restore64.dev | Cross-validation of disassembly, player ID confirmation | Medium |
| SIDdecompiler | Relocatable disassembly, code/data separation validation | Medium |
| SID Preservation | Historical DMC documentation (site currently down) | Low (retry) |
| SID Toolbox | Header editing only, no format awareness | Skip |
| Triad SID player | Architectural reference for player algorithms | High |

**Key finding:** None of these tools have DMC-specific support. Our own
`dmc_parser.py` and `dmc_to_usf.py` remain the primary DMC analysis path.
The external tools are useful for cross-validation and architectural reference,
not as primary DMC analysis engines.
