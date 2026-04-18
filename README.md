# SIDfinity

![alpha](https://img.shields.io/badge/status-alpha-orange)
![phase](https://img.shields.io/badge/phase_1-SID_→_USF_→_SID-blue)

A pipeline for decompiling C64 SID music into a universal symbolic format (USF), rebuilding them with a custom 6502 player, and eventually training a neural net to generate new SID tunes as playable `.sid` files.

**Current focus (Phase 1):** get as many of the ~60,000 HVSC SIDs as possible through the pipeline at Grade A (no audible difference from the original).

## What it does

SIDfinity takes existing SID tunes from the [HVSC](https://hvsc.de/) collection, decompiles them into a musical representation (notes, instruments, patterns, effects), and rebuilds them with a custom 6502 player. The rebuilt SIDs are validated frame-by-frame against the originals.

```
  Any SID ──→ decompile ──→ USF ──→ SIDfinity player ──→ rebuilt .sid
       │                                                       │
       └───────────── register comparison ─────────────────────┘
```

## Current state

<!-- BEGIN DASHBOARD -->
```
HVSC Coverage Dashboard — 59,861 SIDs
══════════════════════════════════════════════════════════════════════════════

Engine               SIDs       S     A     B     C     F  │   USF PARSE    ID
──────────────────────────────────────────────────────────────────────────────
GoatTracker V2       7549      45  4415     —     —     —  │  2257   537   295
DMC                 10676       —     —     —     —     —  │ 10631     9    36
Rob Hubbard           289       2    56    20    41   166  │     2     —     2
JCH NewPlayer        3678       —     —     —     —     —  │     —     —  3678
──────────────────────────────────────────────────────────────────────────────
Unprocessed         37669   (62.9%)
```
<!-- END DASHBOARD -->

**Grading:** S = bit-identical register output. A = no audible differences. B/C/F = increasing audible errors.

**GoatTracker V2** is the most mature pipeline — 4,460 out of 7,549 GT2 SIDs (59%) at Grade A or S. The pipeline handles all 4 player groups (A–D), toneportamento, vibrato, funktempo, wave/pulse/filter tables, and per-song 6502 code generation with peephole optimization.

**Other engines:** DMC (10,676 SIDs) has a parser and USF converter. Rob Hubbard and JCH NewPlayer are identified but not yet fully pipelined. 48 player engines are documented in `docs/players/`.

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

## License

The SIDfinity pipeline (Python code, USF format, V2 code generator) is released under the **MIT License**. See [LICENSE](LICENSE).

The C/C++ tools (`siddump`, `sidrender`, `gt2asm`) link against GPL v2 libraries and are distributed under **GPL v2**. See [tools/LICENSE](tools/LICENSE).

## Acknowledgments

The SIDfinity player implements algorithms from Lasse Öörni's GoatTracker V2 playroutine — wave table execution, effect dispatch, pattern reading, hard restart timing. The V2 code generator (`codegen_v2.py`) was written from scratch in Python but the player logic it generates faithfully follows Lasse Öörni's design. A copy of the original GT2 playroutine source is preserved in `deprecated/old_player/sidfinity_gt2.asm`. Lasse Öörni's license: *"free for any purpose, commercial or noncommercial."*

[libsidplayfp](https://github.com/libsidplayfp/libsidplayfp) is used for SID emulation (GPL v2). [xa65](https://github.com/af65/xa65) is used for 6502 assembly (GPL v2).
