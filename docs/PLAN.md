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
7. **GoatTracker V2 parser** - `src/gt_parser.py` extracts instruments/patterns/orderlists (~30% success rate, needs freq table detection improvements)
8. **SIDfinity player skeleton** - `src/player/sidfinity.a65` assembles to 364 bytes, plays through siddump
9. **SIDfinity player spec** - `docs/sidfinity_player_spec.md` (12-byte instruments, wave/pulse/filter tables, packed patterns, all 3 HR methods)

### Step 1: Finish SIDfinity Player (IN PROGRESS)

The player skeleton at `src/player/sidfinity.a65` has the frame loop and SID register writes working. Still needs:

- **Pattern reader** - decode packed pattern format ($00=end, $01-$3F=instrument, $40-$4F=FX+note, $50-$5F=FX+rest, $60-$BC=note, $BD=rest, $BE=keyoff, $BF=keyon, $C0-$FF=packed rests)
- **Orderlist sequencer** - advance through pattern list with transpose, handle repeats and loops
- **Instrument loader** - read 12-byte instrument definitions, set AD/SR/wave/pulse/filter table pointers, configure HR method
- **Wave table stepper** - step through waveform+pitch program per tick
- **Pulse table stepper** - step through pulse width modulation program
- **Filter table stepper** - step through filter cutoff/resonance/mode program (global, not per-voice)
- **Hard restart engine** - implement all 3 methods (gate-off, test-bit, ADSR-only) with configurable lead time
- **Vibrato/portamento** - via speed table lookup

Test by manually creating a song in the native format and verifying through siddump.

The data format is specified in `docs/sidfinity_player_spec.md`. Key design: X register = voice offset (0/7/14) used for both SID register addressing and channel variable indexing (stride 7). Wave/pulse/filter tables use 2-3 bytes per row with jump/loop commands.

### Step 2: GoatTracker Transpiler

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
