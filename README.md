# sidfinity

Generate C64 SID music files. Input: (author, title, year). Output: a `.sid` file in that composer's style.

## Architecture

The project has two phases:

1. **Lossless pipeline** (current focus): `.sid → register dump → symbolic format → .sid` — validated against all of HVSC
2. **Neural net training** (future): Train a model on the symbolic format to generate new SID music

## Pipeline

```
Original .sid
    ↓  siddump (C++, libsidplayfp emulation)
Register CSV (25 SID regs per frame, 50fps PAL / 60fps NTSC)
    ↓  sid_symbolic.py to-symbolic
Human-readable symbolic format (notes, waveforms, ADSR, filter)
    ↓  sid_symbolic.py to-regs
Register CSV (reconstructed)
    ↓  sid_builder.py
Rebuilt .sid (PSID v2 with 6502 replay player)
```

The pipeline must be **lossless**: for every frame and register, the rebuilt `.sid` matches the original dump (with unused-bit masking).

## Current Status

- **siddump**: Working. JSON escaping, RSID/multi-SID skip (exit 3), `--timeout`, `--duration`, `--digi` (intra-frame write logging for voice 4). Tested on 575 PSID files from curated collection — 0 failures.
- **sid_symbolic.py**: Working. Lossless roundtrip on all 575 curated PSIDs. Handles all 25 registers including filter external routing bit.
- **sid_builder.py**: Working but uses raw encoding (25 bytes/frame). Needs delta encoding for longer tunes.
- **Batch validation on full HVSC**: Not yet done. This is the next major step.

## What Needs To Happen Next

See `CLAUDE.md` for detailed instructions. Summary:

1. **Set up build environment** — build libsidplayfp and xa65 from source (no sudo needed)
2. **Download HVSC #84** — 60,572 SID files
3. **Implement Songlengths parser** (`src/songlengths.py`) — parse per-subtune durations
4. **Implement delta-encoded player** in `sid_builder.py` — compress register data to fit in C64 RAM
5. **Build batch validation tool** (`src/validate_hvsc.py`) — run pipeline on all ~56,676 single-SID PSID files using all CPU cores
6. **Run validation, fix failures iteratively** — target >99% pass rate

## Directory Structure

```
src/
  sid_symbolic.py    # Register CSV ↔ symbolic format conversion
  sid_builder.py     # Build .sid files from register data
  env.sh             # Environment setup (source this)
tools/
  siddump.cpp        # C++ register dumper (uses libsidplayfp)
  build.sh           # Build script for siddump + libsidplayfp
  test_libsid.cpp    # Minimal libsidplayfp test
data/                # (gitignored) HVSC collection, curated SIDs
```

## Build Requirements

- g++ with C++17 support
- Python 3.10+
- No sudo required — everything builds from source in-tree

### Building from scratch

```bash
# 1. Build 7-zip (needed to extract HVSC .7z archive)
mkdir -p tools && cd tools
git clone https://github.com/p7zip-project/p7zip.git xa65/xa/7zip-src  # or download
cd xa65/xa/7zip-src/CPP/7zip/Bundles/Alone2
mkdir -p b/g && cd b/g
make -f ../../makefile -j$(nproc)
cp 7zz ../../../../../..  # -> tools/7zz

# 2. Build xa65 (6502 cross-assembler, needed by sid_builder.py)
cd tools
git clone https://github.com/af65/xa65.git xa65/xa
cd xa65/xa && make -j$(nproc)

# 3. Build libsidplayfp (SID emulation library)
cd tools
git clone https://github.com/libsidplayfp/libsidplayfp.git
cd libsidplayfp
# Create config files (see CLAUDE.md for details)
mkdir build && cd build
# Compile all sources (see tools/build.sh)

# 4. Build siddump
cd tools && bash build.sh

# 5. Download HVSC
cd data
wget https://hvsc.de/downloads/C64Music.7z
../tools/7zz x C64Music.7z

# 6. Set up Python env
source src/env.sh
```

## Hardware Target

- ASROCK ROMED8-2T, 64-core EPYC CPU, dual 3090s NVLink, 512GB RAM
- Batch validation should use all 64 cores via multiprocessing

## Key Technical Details

### SID Chip Registers
25 writable registers at $D400-$D418:
- 3 voices × 7 registers each (frequency, pulse width, control, ADSR)
- Filter cutoff (11-bit), resonance, routing, mode
- Master volume (4-bit, shared with filter mode)

### Voice 4 / Digi Trick
Some tunes rapidly write $D418 (volume register) within a single frame to produce digitized audio (drums, speech). The `--digi` flag in siddump captures these intra-frame writes via instrumented `c64sid::poke()`. Format: `|D:cycle:reg:val,...` appended to frame lines.

### Unused Bit Masking
- PW_HI registers (3, 10, 17): upper 4 bits ignored (mask 0x0F)
- FILT_LO register (21): upper 5 bits ignored (mask 0x07)

### Scope
- Target: 56,676 single-SID PSID files
- Dropped: 3,896 RSID (need kernal ROM), 341 multi-SID (2SID/3SID)
