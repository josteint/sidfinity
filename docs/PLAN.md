# SIDfinity Development Plan

## Vision

Build a neural net that generates authentic C64 SID music, packaged as playable .sid files.

The pipeline: input (text prompt, MP3, MIDI, or style reference) -> neural net -> symbolic representation -> SIDfinity player -> .sid file that plays on real C64 hardware.

## Architecture

```
                    ┌─────────────┐
   MP3/MIDI/Text ──>│ Transcriber │
                    └──────┬──────┘
                           v
                    ┌─────────────┐
                    │  Universal  │
                    │  Symbolic   │<──── Original SID (via player-specific parsers)
                    │  Format     │
                    └──────┬──────┘
                           v
                    ┌─────────────┐
                    │ Style/Sound │ "make it sound like Hubbard"
                    │  Transfer   │ "use GoatTracker instruments"
                    │   Model     │
                    └──────┬──────┘
                           v
                    ┌─────────────┐
                    │  SIDfinity  │ Universal 6502 player
                    │  Player     │
                    └──────┬──────┘
                           v
                         .sid
```

## Current Status (2026-03-30)

### Completed

1. **Register-level pipeline** - 100% lossless roundtrip validated on 56,936 PSID files
2. **Player identification** - sidid identifies 97.8% of HVSC (59,267/60,572 files, 758 signatures)
3. **Player documentation** - 48 major engines documented in `docs/players/` (84.8% of HVSC)
4. **Player behavior analysis** - 642 engines analyzed via cycle-accurate write logs (1,714 sample tunes)
   - Hard restart: 54.5% none, 31.8% gate-off, 11.8% test-bit, 2.0% ADSR-only
   - 5.5% multispeed, median 12.5 writes/frame, median 563 cycle span
5. **SID chip stats** - 41.5% target 8580, 40.3% target 6581, 89.3% PAL
6. **Cycle-accurate write logging** - libsidplayfp modified to record real cycle offsets per SID write
7. **GoatTracker V2 parser** - `src/gt_parser.py` and `src/gt_roundtrip.py`
   - Binary section roundtrip: 5,792/7,006 clean single-SID PSID files match byte-for-byte (82.7%)
   - 722 skip (freq table not found), 492 fail (section ordering edge cases)
   - Extracts: player code, freq tables, song table, pattern table, instruments+tables, orderlists, patterns
8. **SIDfinity player spec** - `docs/sidfinity_player_spec.md`
9. **SIDfinity player prototype** - `src/player/sidfinity.asm` (64tass, 623 bytes, 3 voices working, pattern reader has bugs)
10. **Tooling** - 64tass V1.60 and ACME V0.96 cross-assemblers built and available

### Step 1: GoatTracker Encoder (DONE)

GT2 SID -> parse -> high-level data -> serialize -> byte-for-byte identical SID.
5,922/7,006 clean files validated. Can modify data (transpose) and produce playable SIDs.

Key files: `src/gt_parser.py`, `src/gt_encoder.py`, `src/gt_roundtrip.py`, `src/gt_modify.py`

### Step 2: Universal Data Extractor (DONE)

`src/sid_data_extractor.py` discovers all data tables in ANY SID file by analyzing
6502 player code address references. Tested on GoatTracker, DMC V4, DMC V5, Rob Hubbard,
JCH NewPlayer — finds 11-29 data tables per file regardless of player.

### Step 3: DMC -> SIDfinity Transpiler (IN PROGRESS)

Strategy: use GoatTracker's player as the SIDfinity player foundation. GT2 player.s
is forked into `src/player/sidfinity_player.s` (free license).

The transpiler pipeline: DMC SID -> parse -> transpile to GT2 format -> GT2 player -> output SID

**Where we left off:**
- DMC sector data DECODED successfully (Turrican_32k: 55 sectors with real music)
- DMC sector pointer table found via universal address analysis
- DMC instrument table found at freq_hi + $0248 (works for ~96% of files)
- DMC has two main versions: V4 (fhi at +$06A8) and V5 (fhi at +$0770)
- The universal extractor handles both versions

**Next steps (pick up here):**
1. Build complete DMC parser using universal extractor + sector/track decoding
2. Map DMC instruments to GT2 instruments (11-byte -> 9-byte + wave/pulse/filter tables)
3. Map DMC sectors to GT2 packed patterns (different note/duration encoding)
4. Map DMC tracks to GT2 orderlists
5. Assemble with GT2 player blob
6. Validate: siddump comparison original DMC vs rebuilt GT2 SID

### Step 4: Scale to More Players

Take parsed GT2 data from `gt_parser.py` and convert to SIDfinity format:
- Map GT2 instruments (9 bytes + name) to SIDfinity instruments (12 bytes)
- Convert GT2 wave/pulse/filter/speed tables to SIDfinity table format
- Convert GT2 packed patterns to SIDfinity packed patterns (very similar encoding)
- Convert GT2 orderlists to SIDfinity orderlists

Validate: run siddump on original GT2 SID and transpiled SIDfinity SID, compare register output frame-by-frame. Target: exact match on most frames.

First improve `gt_parser.py` freq table detection to handle more than 30% of GT2 SIDs.

### Step 3: DMC and JCH Transpilers

Same approach for the next two biggest players:
- DMC (10,738 tunes): parse 11-byte instruments, sector-based patterns, track orderlists
- JCH NewPlayer (3,678 tunes): parse 8-byte instruments, wave/pulse/filter tables, sequences

After this step, ~22,000 tunes go through SIDfinity.

### Step 4: Audio Comparison Tool

Generate audio from original and SIDfinity SIDs using libsidplayfp:
- Cross-correlation of waveforms
- Spectral similarity (FFT comparison)
- Perceptual metric (loudness-weighted)
- Use as validation and potentially training signal

### Step 5: Universal Symbolic Format

Design tokenization for transformer training based on SIDfinity data structures:
- Instrument definitions as token sequences
- Pattern data as token sequences (note, instrument, command events)
- Orderlists as song structure tokens
- SID model and clock as conditioning tokens

### Step 6: Neural Net Training

- Tokenize all transpiled songs from steps 2-3
- Train transformer model (GPT-style decoder)
- Experiment: unconditional generation, style-conditioned, MP3-to-SID transfer
- Output: token sequences -> SIDfinity data -> package with player -> .sid file

### Step 7: Additional Transpilers

Extend coverage to remaining players:
- Music Assembler (6,403), Future Composer (4,085), Soundmonitor (3,663)
- GoatTracker V1 (1,384), HardTrack (1,170), Master Composer (1,075)
- SidWizard (1,074), SIDDuzz'It (994), SoedeSoft (950)
- And the long tail of 600+ smaller players

## Key Files

| File | Purpose |
|------|---------|
| `src/player/sidfinity.a65` | The 6502 player (xa65 assembly) |
| `src/player/test_build.py` | Test SID builder for the player |
| `docs/sidfinity_player_spec.md` | Complete player data format specification |
| `src/gt_parser.py` | GoatTracker V2 SID binary parser |
| `src/analyze_player.py` | Player behavior analyzer (write logs) |
| `src/validate_hvsc.py` | Batch validation tool (register roundtrip) |
| `src/sid_symbolic.py` | Register CSV <-> symbolic format |
| `tools/siddump.cpp` | C++ register dumper with --writelog |
| `data/player_analysis_all.json` | Behavior data for 642 players |
| `data/sidid_full.txt` | Player ID for all 60,572 HVSC files |
| `docs/players/` | Documentation for 48 player engines |

## Build Environment

64-core EPYC, 512GB RAM. No sudo. Everything from source in-tree.

```bash
source src/env.sh
bash tools/build.sh    # builds libsidplayfp + siddump
```

xa65 assembler at `tools/xa65/xa/xa`. Note: xa65 requires standalone comments at column 1 (no leading whitespace before `;`).
