# CLAUDE.md — Instructions for continuing development

## Key References

- **`docs/PLAN.md`** — Full roadmap and current status
- **`docs/usf_spec.md`** — USF specification (update when USF changes, then update all converters)
- **`src/sidxray/METHODOLOGY.md`** — How to reverse-engineer any SID player. **Read this before cracking a new player. Update it after with lessons learned.**

## Project Goal

Build the SIDfinity universal SID music player and ML pipeline. See `docs/PLAN.md` for the full roadmap and current status.

**Current task:** "Continue with `docs/next_session_plan.md` — launch all 5 tracks in parallel." Fix decompiler bugs to get from 61/103 to 90+ Grade A. Then unblock Group C (572 songs) and expand coverage.

**What's done:** V2 per-song code generator enabled and passing 103-song regression (61 Grade A). Register-level validation (100% on 56,936 files), 642 player engines analyzed, 48 documented.

**After decompiler fixes:** Expand to 500+ songs, then DMC and JCH transpilers, then ML training.

## CRITICAL: Do Not Break These Invariants

### Wave table +2 extraction offset — DO NOT CHANGE

`gt2_parse_direct.py` line 380 uses `table_operands[1] + 2` for the wave_right start. This looks wrong (mathematically +1 is correct) but it compensates for the GT2 player's `INY` before note column read. The V2 codegen reads notes BEFORE INY, so the +2 extraction and pre-INY read cancel out. **Changing either one without changing the other breaks ALL songs.**

Verified: changing +2 to +1 breaks 42/43 songs. The paired system is self-consistent.

### Wave table bias chain — THREE interdependent transformations

1. **Decompiler** extracts packed bytes (may include +$10 bias)
2. **gt2_to_usf** subtracts bias when `nowavedelay=False`: `sng_l = packed_l - $10`
3. **Packer** adds bias back when `nowavedelay=True` (hardcoded in usf_to_sid.py)
4. **V2 player** without WAVE_DELAY stores directly (no subtract — needs actual SID values)
5. **V2 player** with WAVE_DELAY does `CMP #$10; BCS; SBC #$10`
6. **Packer** `skip_bias` flag skips step 3 for V2 without WAVE_DELAY

If `nowavedelay` is wrong, the chain breaks. Do NOT change `skip_bias` without understanding the full chain. Radar_Love.sid fails because `nowavedelay` is misdetected.

### Group A pulse speed — naive doubling REGRESSES songs

Group A GT2 players use `ASL` to double pulse speed before adding. Naively doubling all Group A pulse_right bytes in gt2_to_usf.py regressed 12 songs. The fix needs to be conditional on the EXACT code path (ASL vs CLC, modulation vs set-pulse entries). See `docs/next_session_plan.md` Track 4.

### siddump frame boundary drift — measurement artifact, not a bug

siddump uses 19688 cycles/frame (19656 + 32 margin). This causes the VBI to drift relative to siddump's frame boundary. Register diffs from this drift are classified as jitter (inaudible) in gt2_compare.py. Do NOT try to "fix" these diffs by changing player cycle counts.

## Original Goal (completed)

Lossless `sid -> symbolic -> sid` pipeline validated against all ~56,676 single-SID PSID files in HVSC #84. **Achieved: 100% pass rate on 56,936 files.**

## Build Environment Setup

The development server is a 64-core EPYC with 512GB RAM. No sudo — everything builds from source in-tree.

### Step-by-step setup

```bash
# Source the environment
source src/env.sh

# Build xa65 (6502 assembler)
cd tools
git clone https://github.com/af65/xa65.git xa65/xa
cd xa65/xa && make -j$(nproc)
cd ../..

# Build libsidplayfp from source
git clone https://github.com/libsidplayfp/libsidplayfp.git
cd libsidplayfp

# Create src/config.h (libsidplayfp needs this since we skip autotools):
cat > src/config.h << 'CONF'
#ifndef CONFIG_H
#define CONFIG_H
#define VERSION "3.0.0"
#define PACKAGE "libsidplayfp"
#define PACKAGE_URL "https://github.com/libsidplayfp/libsidplayfp/"
#define HAVE_STRCASECMP 1
#define SIZEOF_SHORT 2
#define SIZEOF_INT 4
#define HAVE_CXX14 1
#define HAVE_CXX11 1
#define HAVE_CXX17 1
#define SHLIBEXT ".so"
#endif
CONF

# Create src/sidplayfp/sidversion.h from .in template:
cat > src/sidplayfp/sidversion.h << 'VER'
#ifndef SIDVERSION_H
#define SIDVERSION_H
#define LIBSIDPLAYFP_VERSION_MAJ 3
#define LIBSIDPLAYFP_VERSION_MIN 0
#define LIBSIDPLAYFP_VERSION_LEV "0a2"
#endif
VER

# Create SIDLite builder defs:
cat > src/builders/sidlite-builder/sidlite/sl_defs.h << 'DEFS'
#ifndef SL_DEFS_H
#define SL_DEFS_H
#define HAVE_BUILTIN_EXPECT 1
#endif
DEFS

# Generate .bin files from .a65 assembly (psiddrv needs these):
cd src
for f in psiddrv.a65 reloc65.a65; do
    base="${f%.a65}"
    ../../xa65/xa/xa -o "${base}.bin" "$f" 2>/dev/null || true
done
# Convert .bin to C arrays:
for f in psiddrv.bin reloc65.bin; do
    base="${f%.bin}"
    xxd -i "$f" > "${base}_bin.h"
done
cd ..

# Build all .cpp files into static library
mkdir -p build && cd build
SRCS=$(find ../src -name "*.cpp" | grep -v test | grep -v utils | grep -v exsid | grep -v residfp | grep -v usbsid | sort)
for f in $SRCS; do
    oname="$(echo $f | sed 's|^\.\./||; s|/|_|g; s|\.cpp$|.o|')"
    g++ -std=c++17 -O2 -DNDEBUG -DHAVE_CONFIG_H -I../src -I../src/builders/sidlite-builder -c "$f" -o "$oname"
done
ar rcs libsidplayfp.a *.o
cd ../../..

# Build siddump
bash tools/build.sh

# Download HVSC #84
mkdir -p data && cd data
wget https://hvsc.de/downloads/C64Music.7z
../tools/7zz x C64Music.7z
cd ..

# Verify: run siddump on a test file
tools/siddump data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid --duration 5 2>/dev/null | head -3
```

## Current State

### What works
- `tools/siddump` — dumps SID registers frame-by-frame via libsidplayfp emulation
  - JSON metadata with proper escaping (non-ASCII → `\uXXXX`)
  - `--subtune N`, `--duration N`, `--timeout N`, `--raw`, `--digi` flags
  - Skips RSID (exit 3) and multi-SID (exit 3)
  - Silent tune detection (exit 2)
  - `--digi`: captures intra-frame register writes via instrumented `c64sid::poke()`, appended as `|D:cycle:reg:val,...`
- `src/sid_symbolic.py` — converts between register CSV and symbolic format
  - Subcommands: `to-symbolic`, `to-regs`, `roundtrip`
  - Lossless roundtrip verified on 575 curated PSID files (0 failures)
  - Handles: frequency→note conversion with raw freq_reg preservation, all waveforms, gate/sync/ring/test bits, pulse width (always stored), ADSR, filter (cutoff, resonance, routing including external, mode, volume, voice 3 mute)
- `src/sid_builder.py` — builds PSID v2 .sid files from register CSV
  - Uses xa65 assembler for 6502 player code
  - Current limitation: raw encoding (25 bytes/frame), max ~2400 frames (48s)

### What needs to be built

#### 1. Songlengths parser (`src/songlengths.py`)
~80 lines. Parse `data/C64Music/DOCUMENTS/Songlengths.md5`.

Format: `; /path/to/file.sid` then `md5hash=m:ss m:ss ...` (space-separated durations per subtune).

Functions needed:
- `load_database(path) -> dict` — parse entire file, key by MD5 hash
- `get_durations(sid_path, db) -> list[float]` — compute MD5 of .sid file, look up durations in seconds

#### 2. Delta-encoded player (`src/sid_builder.py` rewrite)
The biggest change. Current raw encoding maxes out at ~48s. Delta encoding stores only changed registers per frame.

**Delta format:**
```
Per frame:
  byte 0: N = number of changed registers (0-25)
  If N > 0: N × 2 bytes (register_index, new_value)
  If N == 0: nothing (repeat previous frame)
```

Measured compression: ~38-53% of raw → ~5000-6300 frames (100-126s at 50fps).

**New memory layout:**
- Player code at `$0800` (~100 bytes)
- Variables at `$0880` (data pointer, frame counter, total frames, shadow regs)
- Data at `$0900`
- Usable: `$0900` to `$CFFF` = ~49KB (below I/O at $D000)
- Extended: bank out BASIC ($A000-$BFFF) and kernal ($E000-$FFFF) for ~63KB total

The 6502 player: on each frame, read N, then loop N times reading (reg, val) pairs and writing to $D400+reg. Keep shadow copy of all 25 regs in zero page or player area.

PSID v2 header, single subtune, correct clock/model flags from metadata.

#### 3. Batch validation tool (`src/validate_hvsc.py`)
~250 lines. Run the full pipeline on every single-SID PSID in HVSC.

**Per-file workflow:**
1. Look up duration from Songlengths
2. Run `siddump --duration N --timeout 120` via subprocess
3. Parse CSV → `decode_frame()` → `encode_frame()` → compare (with bit masking)
4. Record result in SQLite: `path, subtune, duration_s, frames, status, error_count, elapsed_s`

**Status values:** `pass`, `fail`, `crash`, `timeout`, `silent`, `overflow`, `digi_overflow`

**Parallelism:** `multiprocessing.Pool(workers=64)` — use all cores.

**Features:**
- `--resume` — skip already-processed files (check SQLite)
- `--filter PATTERN` — only matching paths
- `--jobs N` — worker count (default: number of CPUs)
- Summary report at end

**Expected runtime:** ~60k files ÷ 64 cores × ~2s/file ≈ 30 minutes

#### 4. Fix failures iteratively
Run validation, analyze failures by category, fix, re-run. Expected issues:
- JSON parse errors (should be fixed already)
- Timeouts (classify as known-bad)
- Silent tunes (broken PSID)
- Overflow (truncate with warning)
- Register mismatches (investigate encoding bugs)

Target: >99% pass rate on single-SID PSID files.

#### 5. Voice 4 / digi sample database (`src/sample_db.py`)
For tunes using the volume register trick ($D418 rapid writes for digitized audio):
- Extract intra-frame $D418 write sequences from siddump `--digi` output
- Segment into individual samples (silence gaps)
- Hash and deduplicate into SQLite `samples.db`
- Reference samples by ID in symbolic format: `| DIGI: S123@340 S45@8200`
- For ML: model learns to place samples rather than generating PCM

The `--digi` flag and `c64sid.h` write logging are already implemented. The cycle offsets are currently 0 (placeholder) — needs wiring to the event scheduler for accurate timing. See `tools/libsidplayfp/src/c64/c64sid.h` (the `m_currentCycle` field).

## Key Files

| File | Purpose |
|------|---------|
| `tools/siddump.cpp` | C++ register dumper using libsidplayfp |
| `tools/build.sh` | Build script for libsidplayfp + siddump |
| `tools/libsidplayfp/src/c64/c64sid.h` | Modified: write log in `poke()` for digi capture |
| `src/sid_symbolic.py` | Register CSV ↔ symbolic format |
| `src/sid_builder.py` | Build .sid from register data (needs delta encoding) |
| `src/env.sh` | Environment setup script |

## Testing

```bash
# Quick roundtrip test on a single file
source src/env.sh
tools/siddump some_file.sid --duration 10 2>/dev/null > /tmp/test.csv
python3 src/sid_symbolic.py roundtrip /tmp/test.csv

# Full symbolic roundtrip
tools/siddump some_file.sid --duration 10 2>/dev/null > /tmp/test.csv
python3 src/sid_symbolic.py to-symbolic /tmp/test.csv -o /tmp/test.sym
python3 src/sid_symbolic.py to-regs /tmp/test.sym -o /tmp/test_recon.csv
# Compare /tmp/test.csv and /tmp/test_recon.csv

# Build .sid from dump
tools/siddump some_file.sid --duration 10 2>/dev/null > /tmp/test.csv
python3 src/sid_builder.py /tmp/test.csv -o /tmp/rebuilt.sid
```

## Curated test set

Download from: https://trondal.com/sid/CujosCuratedSIDs.7z (613 SIDs, 574 PSID + 39 RSID)
Extract to `data/CujosCuratedSIDs/`. Good for quick validation before running full HVSC.
