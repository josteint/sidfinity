# SIDfinity

> **Note:** This README was written by AI. This project is a work in progress and little if anything is working yet.

Neural net–generated C64 SID music, output as playable `.sid` files for real hardware.

## Abstract

SIDfinity parses existing SID tunes from the [HVSC](https://hvsc.de/) collection into a universal symbolic format (USF), trains a transformer model on that data, and generates new music packaged with a universal 6502 player. The output is a standard `.sid` file that plays on real C64 hardware or any SID emulator.

## The Idea

There are ~60,000 SID tunes in the wild, written using 642 different music engines. Each engine stores music differently — different instrument formats, pattern encodings, table structures. To train a neural net on all of them, we need a single representation that captures what every engine can express.

USF (Universal Symbolic Format) is that representation. It's event-based, compact (~3000 tokens for a typical tune), and covers the full feature set of GoatTracker V2 — the most capable open-source SID tracker. Other engines (DMC, JCH, Future Composer, etc.) map into the same format.

The pipeline:

```
  Any SID ──→ parser ──→ USF ──→ ML training data
                                        │
  Prompt ──→ transformer ──→ USF ──→ SIDfinity player ──→ .sid
```

## Goals

- **Parse every SID engine** into USF (642 engines, starting with GT2 and DMC)
- **Lossless roundtrip** for at least GoatTracker: GT2 → USF → SID should produce identical register output
- **Train a transformer** on the full HVSC as USF token sequences
- **Generate new tunes** in the style of any composer, packaged as `.sid` files
- **Play on real C64 hardware** via the SIDfinity universal 6502 player

## Current State

Very early. The USF spec covers GT2 fully. DMC parsing partially works. Register-level validation infrastructure exists (100% pass rate on HVSC for the simpler register-dump roundtrip). The GT2→USF→SID roundtrip is the next milestone.

## Docs

- [USF Specification](docs/usf_spec.md) — the universal symbolic format
- [Development Plan](docs/PLAN.md) — roadmap and current status
- [SIDfinity Player Spec](docs/sidfinity_player_spec.md) — the universal 6502 player
- [Player Engine Docs](docs/players/) — documentation for 48 major SID engines

## Build

```bash
source src/env.sh
bash tools/build.sh
```

Requires g++ (C++17), Python 3.10+. See `CLAUDE.md` for full setup.
