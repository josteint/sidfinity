# SIDfinity

![alpha](https://img.shields.io/badge/status-alpha-orange)

> **Note:** This README was written by Claude (Anthropic's AI assistant). The project is in alpha — things work but rough edges remain.

A pipeline for decompiling C64 SID music into a universal symbolic format, with the goal of training a neural net to generate new SID tunes as playable `.sid` files.

## What it does

SIDfinity takes existing SID tunes from the [HVSC](https://hvsc.de/) collection (~60,000 files), decompiles them into a musical representation (notes, instruments, patterns, effects), and rebuilds them with a custom 6502 player. The rebuilt SIDs are validated frame-by-frame against the originals.

```
  GT2 SID ──→ decompile ──→ USF ──→ SIDfinity player ──→ rebuilt .sid
       │                                                       │
       └───────────── register comparison ─────────────────────┘
```

The eventual goal is to train a transformer model on the extracted musical data to generate new C64 music.

## Current state

**GoatTracker V2 pipeline:** 1,688 out of 3,478 GT2 SIDs (48.5%) achieve Grade A — zero audible differences from the original. The full regression suite tests all 3,478 GT2 SIDs in 33 seconds on 48 cores. GT2 accounts for roughly 7,000 of the ~60,000 SIDs in HVSC.

The pipeline correctly handles:
- All 4 GT2 player groups (A through D, versions 2.65–2.77)
- Ghost register mode (Group C)
- Toneportamento, portamento, vibrato, funktempo
- Wave/pulse/filter/speed table extraction and playback
- Per-song V2 6502 code generation with peephole optimization

**Other engines:** DMC and JCH parsers exist in early form. 48 player engines are documented in `docs/players/`.

## Build

```bash
source src/env.sh
bash tools/build.sh    # builds libsidplayfp + siddump
```

Requires: g++ (C++17), Python 3.10+, xa65 assembler (built in-tree).
Optional: nvcc (CUDA 12+) for GPU optimizer, Z3 for SMT verification.

Hardware: developed on 64-core EPYC with dual 3090 GPUs, but runs on any Linux machine.

## Test

```bash
source src/env.sh
python3 src/player/regression_test.py    # 3,478 songs, ~33 seconds
```

## Docs

- [USF Specification](docs/usf_spec.md) — the universal symbolic format
- [Development Plan](docs/PLAN.md) — roadmap and status
- [GT2 Data Layout](docs/gt2_data_layout.md) — byte-level binary format
- [Player Engine Docs](docs/players/) — documentation for 48 SID engines

## Project structure

```
src/                    Pipeline source code
  player/               V2 6502 code generator + optimization tools
  sidxray/              Player reverse-engineering tools
docs/                   Specifications and references
tools/                  Build tools (xa65, siddump, libsidplayfp)
data/                   HVSC collection (not in git)
deprecated/             Earlier development phases
```

## Acknowledgments

The SIDfinity player implements algorithms from Lasse Öörni's GoatTracker V2 playroutine — wave table execution, effect dispatch, pattern reading, hard restart timing. The V2 code generator (`codegen_v2.py`) was written from scratch in Python but the player logic it generates faithfully follows Lasse Öörni's design. A copy of the original GT2 playroutine source is preserved in `deprecated/old_player/sidfinity_gt2.asm`. Lasse Öörni's license: free for any purpose, commercial or noncommercial.

libsidplayfp is used under its existing license for SID emulation and register dumping.
