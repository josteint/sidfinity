# SIDfinity Development Plan

## Vision

Build a neural net that generates authentic C64 SID music, packaged as playable .sid files.

The pipeline: input (text prompt, MP3, MIDI, or style reference) → neural net → symbolic representation → SIDfinity player → .sid file that plays on real C64 hardware.

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
                    │ Style/Sound │  "make it sound like Hubbard"
                    │  Transfer   │  "use GoatTracker instruments"
                    │   Model     │
                    └──────┬──────┘
                           v
                    ┌─────────────┐
                    │  SIDfinity  │  Universal 6502 player
                    │  Player     │  (or target-specific exporter)
                    └──────┬──────┘
                           v
                         .sid
```

## Goals

1. **Lossless roundtrip:** orig_sid → symbolic → new_sid where new_sid produces identical register writes
2. **Style transfer:** Commando's music with GoatTracker instruments, or vice versa
3. **Generation:** Neural net outputs original SID music in various styles
4. **Real hardware:** Output .sid files play correctly on actual C64

## Completed Work

### Register-level pipeline (100% validated)
- `tools/siddump` — C++ register dumper with cycle-accurate write logging (--writelog)
- `src/sid_symbolic.py` — register CSV ↔ symbolic format (lossless roundtrip)
- `src/validate_hvsc.py` — validated 56,936 PSID files at 100% pass rate
- `src/songlengths.py` — HVSC songlengths database parser

### Player identification and research
- `tools/sidid` — identifies 97.8% of HVSC (59,267 / 60,572 files)
- `docs/players/` — documentation for 48 player engines covering 84.8% of HVSC
- Player distribution: DMC (10,738), GoatTracker V2 (7,550), Music Assembler (6,403), Future Composer (4,085), JCH NewPlayer (3,678), Soundmonitor (3,663), + 42 more

### GoatTracker parser (first native format parser)
- `src/gt_parser.py` — extracts instruments, orderlists, patterns from GT2 SID binaries
- Works on ~30% of GT2 files, needs freq table detection improvements

### Cycle-accurate write logging
- Modified libsidplayfp to record cycle offsets for every SID register write
- `siddump --writelog` captures full write log per frame with real timing

## Next Steps (in order)

### Phase 1: Deep player analysis tools

Build tools to understand how each player engine works at the register level, without needing to reverse-engineer 6502 code manually.

#### 1a. CPU instruction tracer
Add trace mode to libsidplayfp's 6502 CPU (mos6510.cpp) that logs:
- Program counter, opcode, operands for every instruction
- Memory reads/writes with addresses and values
- SID register writes correlated to PC address

This tells us which code in any player controls which SID behavior. Post-process traces to extract: call graph, data table locations, register write patterns.

#### 1b. Bit-flipper / differential analysis tool
Systematically mutate bytes in a SID file's data section and observe changes in register output:
- Change one byte → re-run siddump → diff the register dumps
- Maps data bytes to their effect on SID registers
- Reveals: instrument table boundaries, pattern encoding, table formats

#### 1c. Write pattern analyzer
Analyze --writelog output across many tunes to classify:
- Register write order per frame (which registers written first/last)
- Hard restart timing patterns (how many frames before note, which regs cleared)
- Multispeed detection (multiple play calls per frame)
- Common vs rare register write sequences

### Phase 2: Systematic player analysis

Use Phase 1 tools to analyze each of the 48 documented players:

1. Start with GoatTracker V2 (best-documented, can validate against source code)
2. Then DMC, JCH NewPlayer, Future Composer (top 3 by tune count after GT)
3. Then remaining players in order of HVSC tune count

For each player, produce a structured spec:
- Instrument engine: what tables/programs control waveform, frequency, pulse, filter
- Timing: frame rate, multispeed, hard restart sequence
- Register write order and cycle timing
- Data format: table sizes, pattern encoding, limits
- What the SIDfinity player needs to support to reproduce this player's sounds

### Phase 3: SIDfinity player design

Based on Phase 2 analysis, design the universal 6502 player:
- GoatTracker-style programmable tables (wave, pulse, filter) as the core
- Configurable hard restart timing
- Multispeed support
- Precise register write ordering
- Target: ~1.5-2KB of 6502 code, fits most songs in <64KB

### Phase 4: Native format parsers + transpilers

For each major player, build:
- A parser that extracts native music data from the SID binary
- A transpiler that converts native data → SIDfinity format
- Validation: compare register output of original vs transpiled version

Priority order (by tune count): DMC, GoatTracker, Music Assembler, Future Composer, JCH, Soundmonitor

### Phase 5: Universal symbolic format

Design the symbolic format for ML training:
- Captures musical structure (patterns, sequences, instruments) not just registers
- Tokenization scheme for transformer training
- Encodes enough information for lossless roundtrip through any target player

### Phase 6: Neural net training

- Tokenize the symbolic corpus from Phase 4
- Train transformer model on the tokenized data
- Experiment with: unconditional generation, style-conditioned generation, MP3-to-SID transfer

### Phase 7: Audio comparison metric

- Generate audio from original and rebuilt SIDs using libsidplayfp
- Compare waveforms (cross-correlation, spectral similarity, perceptual metrics)
- Use as validation metric and potentially as training signal

## Key Design Decisions (to be made)

- SIDfinity player table sizes and limits
- Symbolic format schema (JSON? Custom binary? Token vocabulary?)
- Which transformer architecture (GPT-style decoder, encoder-decoder, etc.)
- Training data: all 48 players or focus on top 5?
- How to handle the ~15% of HVSC with undocumented players
