# SIDfinity

Generate C64 SID music with neural nets. Train on the entire HVSC collection, output playable `.sid` files for real hardware.

## What We're Building

A pipeline that understands C64 music at the deepest level — not just the sound output, but the actual music engines that produce it. The goal is a neural net that generates music in the style of any C64 composer, packaged as authentic `.sid` files using a universal "god player" called the SIDfinity Player.

```
                    ┌─────────────┐
   MP3/MIDI/Text ──>│ Transcriber │
                    └──────┬──────┘
                           v
                    ┌─────────────┐
                    │  Universal  │
                    │  Symbolic   │<── Original SID (via player-specific parsers)
                    │  Format     │
                    └──────┬──────┘
                           v
                    ┌─────────────┐
                    │ Style/Sound │  "make it sound like Rob Hubbard"
                    │  Transfer   │  "use GoatTracker instruments"
                    │   Model     │
                    └──────┬──────┘
                           v
                    ┌─────────────┐
                    │  SIDfinity  │  Universal 6502 player
                    │  Player     │  plays on real C64 hardware
                    └──────┬──────┘
                           v
                         .sid
```

## Key Achievements

### 100% Lossless Register Roundtrip

Every single-SID PSID file in HVSC #84 passes our register-level validation:

| | Count |
|---|---:|
| **Pass** | 56,936 |
| **Skip** (RSID/multi-SID) | 3,636 |
| **Fail** | 0 |
| **Total** | 60,572 |

The symbolic format captures all 25 SID registers per frame with zero information loss.

### 642 Player Engines Analyzed

Using [sidid](https://github.com/cadaver/sidid) for identification and our custom `analyze_player.py` for behavior analysis, we've profiled every significant SID music engine in existence:

| Player | Tunes | Type |
|--------|------:|------|
| DMC (Demo Music Creator) | 10,738 | Tracker |
| GoatTracker V2 | 7,550 | Tracker (open source) |
| Music Assembler | 6,403 | Assembler/compiler |
| Future Composer (MoN) | 4,085 | Tracker |
| JCH NewPlayer | 3,678 | Tracker (source available) |
| Soundmonitor | 3,663 | Bar/block editor |
| GoatTracker V1 | 1,384 | Tracker (open source) |
| HardTrack Composer | 1,170 | Tracker (source available) |
| Master Composer | 1,075 | Page/block editor |
| SID-Wizard (Hermit) | 1,074 | Tracker (open source) |
| SIDDuzz'It | 994 | Tracker (source available) |
| SoedeSoft / Soundmaster | 950 | Editor |
| Digitalizer | 680 | Editor |
| RoMuzak | 593 | Editor |
| Rob Hubbard (custom) | 289 | Hand-coded 6502 |
| David Whittaker (custom) | 117 | Hand-coded MML |
| + 626 more engines | ~20,000 | Various |
| **Total identified** | **59,267** | **97.8% of HVSC** |

Full documentation for 48 major players in `docs/players/`.

### Empirical Player Behavior Data

Cycle-accurate write-log analysis on 1,714 sample tunes across all 642 player variants:

**Hard restart methods** (how players prepare for clean note attacks):
- 54.5% -- No hard restart (direct note change)
- 31.8% -- Gate-off HR (classic gate toggle + ADSR clear)
- 11.8% -- Test-bit HR ($08/$09 oscillator reset, used by GoatTracker)
- 2.0% -- ADSR manipulation only

**Other characteristics:**
- 5.5% of tunes use multispeed (2x-8x frame rate)
- Median 12.5 register writes per frame
- Median 563 cycle write span within frame
- Register write order varies significantly across engines

### SID Chip Model Distribution

| Model | Tunes | % |
|-------|------:|---:|
| 8580 | 25,138 | 41.5% |
| 6581 | 24,410 | 40.3% |
| Unknown | 10,300 | 17.0% |
| Both | 724 | 1.2% |

Nearly equal split -- the neural net must learn both timbral vocabularies. Clock is 89.3% PAL.

## Tools

| Tool | Purpose |
|------|---------|
| `tools/siddump` | C++ register dumper with cycle-accurate write logging (`--writelog`) |
| `tools/sidid` | Player identification (758 signature patterns) |
| `src/sid_symbolic.py` | Register CSV to/from symbolic format (lossless) |
| `src/validate_hvsc.py` | Parallel batch validation (64-core, ~42 min for all HVSC) |
| `src/songlengths.py` | HVSC Songlengths.md5 parser |
| `src/gt_parser.py` | GoatTracker V2 SID binary parser |
| `src/analyze_player.py` | Player behavior analyzer (write order, HR detection, multispeed) |
| `src/sid_builder.py` | Build .sid files from register data |

## Project Structure

```
src/                        Python tools and parsers
tools/                      C++ tools (siddump, sidid)
  libsidplayfp/             SID emulation library (built from source)
  libsidplayfp-overlay/     Our modifications (cycle-accurate write logging)
  xa65/                     6502 cross-assembler
docs/
  PLAN.md                   Development roadmap
  players/                  Documentation for 48 major SID player engines
    README.md               Coverage summary with source availability
    rob_hubbard.md          Rob Hubbard's engine (C=Hacking #5 disassembly reference)
    goattracker.md          GoatTracker V1/V2 (full .sng and packed SID format)
    dmc.md                  Demo Music Creator (11-byte instruments, sector format)
    jch_newplayer.md        JCH NewPlayer (wave/pulse/filter tables, super table)
    future_composer.md      Future Composer / MoN family
    soundmonitor.md         Chris Huelsbeck's Soundmonitor
    music_assembler.md      Music Assembler (assembler/compiler architecture)
    sidwizard.md            SID-Wizard (SWM format spec, open source)
    sidduzzit.md            SIDDuzz'It (65KB docs, source available)
    ...and 7 more files covering 30+ additional engines
data/                       (gitignored except analysis results)
  C64Music/                 HVSC #84 (60,572 SID files)
  validation.db             SQLite: 100% pass rate validation results
  sidid_full.txt            Player identification for all 60,572 files
  player_analysis_all.json  Behavior analysis of 1,714 tunes / 642 players
```

## The SIDfinity Player (planned)

A universal 6502 music player designed to reproduce the behavior of all 642 identified engines:

- Programmable wave/pulse/filter tables (micro-programs per instrument)
- All 3 hard restart methods (gate-off, test-bit, ADSR-only)
- Configurable register write order
- Single and multispeed (1x-8x)
- ~1.5-2KB of 6502 code
- Targets both 6581 and 8580 SID chips
- Plays on real C64 hardware

## Build

```bash
source src/env.sh
bash tools/build.sh       # builds libsidplayfp + siddump
```

Requires: g++ (C++17), Python 3.10+, no sudo. See `CLAUDE.md` for detailed setup.

## Quick Test

```bash
# Dump registers from a SID file
tools/siddump data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid --duration 10 > /tmp/test.csv

# Verify lossless symbolic roundtrip
python3 src/sid_symbolic.py roundtrip /tmp/test.csv

# Identify what player engine a SID uses
tools/sidid -ctools/sidid.cfg data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid

# Analyze a player's register write behavior
python3 src/analyze_player.py data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid

# Parse GoatTracker SID to extract native music data
python3 src/gt_parser.py data/C64Music/MUSICIANS/C/Cadaver/Dojo.sid -v
```
