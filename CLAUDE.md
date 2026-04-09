# CLAUDE.md — Instructions for continuing development

## Key References

- **`docs/PLAN.md`** — Full roadmap
- **`docs/decisions.md`** — Dead ends and settled architectural decisions. **Read before investigating a bug you think might have been tried before.**
- **`docs/benchmark.csv`** — Grade A count over time. **Append a row after each batch improvement.**
- **`docs/usf_spec.md`** — USF specification (update when USF changes, then update all converters)
- **`docs/gt2_data_layout.md`** — Byte-level GT2 data layout (read before touching the packer)
- **`src/sidxray/METHODOLOGY.md`** — How to reverse-engineer any SID player

## Working Conventions

### Keep things current
- After fixing a bug that changes the Grade A count, update the pipeline status memory and CLAUDE.md status line.
- After finding a new measurement artifact, improve `gt2_compare.py` BEFORE investigating further — don't chase false positives.
- Before ending a session, check if any memories have become stale or wrong. Update or remove them.
- After adding a new tool or capability, add it to the Key Files table in this file.

### Automate repeated work
- If you do the same manual analysis 3+ times, write a reusable tool for it (like `gt2_triage.py` was born from manual F-grade sampling).
- If you're running a multi-step pipeline by hand, make it a script.
- Prefer 64-core parallel batch runs over sequential sampling.

### Test everything
- Run the full regression (`python3 src/player/regression_test.py`, 20 seconds) before EVERY commit that touches pipeline code.
- If a fix causes ANY regression (even 1 song), investigate before accepting it.
- When the Grade A count increases, rebuild the regression registry so new songs are protected.

### Be skeptical
- Challenge assumptions, even ones that seem well-established. The toneporta "init timing" investigation wasted hours because we assumed the init frame was the cause — it wasn't.
- When a theory doesn't produce results after 2-3 attempts, stop and reconsider the premise. Read `docs/decisions.md` for known dead ends.
- When you don't know something, acknowledge it. Ask: where can we get more knowledge? Check the GT2 player source, siddump --writelog output, py65 step-debug, or audio_compare ground truth.
- Verify claims against real data. "The player is 1 frame late" means nothing without frame-by-frame register dumps showing the exact offset.

### Fix bugs, not symptoms
- When register comparison shows differences, first determine if the difference is AUDIBLE. Use `audio_compare.py` for ground truth if unsure.
- Don't widen comparison tolerance to hide real bugs. Only classify as jitter what is genuinely inaudible (silent voice, phase drift of same notes, ±frame timing shift).
- Use the investigation methodology: pick ONE song, trace the EXACT wrong frame, find root cause. See memory `feedback_bug_investigation.md`.

## Project Goal

Build the SIDfinity universal SID music player and ML pipeline. See `docs/PLAN.md` for the full roadmap and current status.

**Status:** 1,843/3,481 Grade A (52.9%) on full HVSC batch. 3,478-song regression suite runs in 33 seconds on 48 cores. Superoptimizer complete. Toneporta fixed. Multi-song support added. Comparison methodology handles timing jitter from layout shifts.

**Next steps (in priority order):**
1. Investigate remaining ~1,294 F-grade GT2 SIDs — 90% fail at init timing (frames 10-15)
2. Fix num_columns=2 undercount for 155 Group A fixedparams=1 songs (col_data has correct data but blind use causes regressions — needs targeted validation)
3. Start ML training on 1,843 Grade A songs (USF tokenization)
4. Expand to DMC (10,738 SIDs) and JCH (3,678 SIDs) player engines

**Key insights:**
- V2 player code blocks are at 6502 minimum cycle counts. Further Grade A gains come from fixing decompiler/player BUGS, not cycle optimization.
- V2 init timing is 2-7 frames behind GT2 (no channel exec during init). This is a design choice. Changing V2 init was tried: 115 regressions. The comparison init grace (10 frames) absorbs most of this, but songs with higher tempos (12+) or longer gate timers still fail.
- Any byte-count change in the V2 player shifts 6502 addresses, causing ±1 frame timing jitter from page-crossing cycle penalties. This is handled by the comparison methodology (see below), not by avoiding code changes.
- To investigate F-grade songs: pick the highest-scoring one, trace the first wrong frame, classify the error, fix root cause, batch test. See memory `feedback_bug_investigation.md`.

## Comparison Methodology (gt2_compare.py)

The comparison classifies each frame difference as audible or inaudible:

**Audible (counts toward grade):** `note_wrong`, `wave_wrong`
**Weakly audible:** `env_wrong` (tolerated up to 1% for Grade A — ADSR write-order timing)
**Inaudible:** `note_jitter`, `wave_jitter`, `gate_diff`, `env_jitter`, `freq_fine`, `pulse_diff`, `pulse_jitter`

**Jitter detection layers (in order):**
1. **±3 frame window** — rebuilt's freq_hi found in original's nearby frames
2. **1-frame transient** — both neighbors match (isolated glitch)
3. **Test-bit waveform** — $08/$09 near gate transitions is HR artifact
4. **Silent voice** — freq diffs when waveform bits are all 0 (oscillator off)
5. **Sequence-level** — same note-change-event sequence in different order (95% LCS match)
6. **Global value set** — both streams use identical set of freq_hi values (arpeggio phase drift)
7. **Vibrato phase drift** — ±8 frame window, both values appear in each other's window (50% threshold)
8. **Init/end grace** — first 10 frames and last 2 frames excluded

**Grading:** A = zero note_wrong + wave_wrong (env_wrong < 1%). B = < 2% audible. C = < 10%. F = >= 10%.

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

If `nowavedelay` is wrong, the chain breaks. Do NOT change `skip_bias` without understanding the full chain.

### Group A pulse speed — naive doubling REGRESSES songs

Group A GT2 players use `ASL` to double pulse speed before adding. Naively doubling all Group A pulse_right bytes in gt2_to_usf.py regressed 12 songs. The fix needs to be conditional on the EXACT code path (ASL vs CLC, modulation vs set-pulse entries).

### siddump frame boundary drift — measurement artifact, not a bug

siddump uses 19688 cycles/frame (19656 + 32 margin). This causes the VBI to drift relative to siddump's frame boundary. Register diffs from this drift are classified as jitter (inaudible) in gt2_compare.py. Do NOT try to "fix" these diffs by changing player cycle counts.

## Pipeline

```
GT2 SID → gt2_decompile → gt2_to_usf → USF Song → usf_to_sid → rebuilt SID
                                                       ↓
                                              codegen_v2 (V2 player)
                                                       ↓
                                              sidfinity_pack (xa65 assembly)
```

**Comparison:** `gt2_compare.py` dumps both original and rebuilt SIDs via `siddump`, compares register output frame-by-frame with jitter tolerance.

## Build Environment

64-core EPYC, 512GB RAM, dual 3090 GPUs. No sudo — everything from source in-tree.

```bash
source src/env.sh        # set up PATH
bash tools/build.sh      # build libsidplayfp + siddump
```

xa65 assembler at `tools/xa65/xa/xa`. CUDA toolkit at `/usr/bin/nvcc`.

## Testing

```bash
# Full regression (3,478 GT2 songs, 33 seconds)
source src/env.sh
python3 src/player/regression_test.py

# Single song through pipeline
python3 -c "
import sys; sys.path.insert(0, 'src')
from gt2_to_usf import gt2_to_usf
from usf_to_sid import usf_to_sid
from gt2_compare import compare_sids_tolerant
song = gt2_to_usf('path/to/song.sid')
usf_to_sid(song, '/tmp/rebuilt.sid')
comp = compare_sids_tolerant('path/to/song.sid', '/tmp/rebuilt.sid', 10)
print(f'Grade: {comp[\"grade\"]} Score: {comp[\"score\"]:.1f}')
"
```

## Key Files

### GT2 Pipeline (active)
| File | Purpose |
|------|---------|
| `src/gt2_to_usf.py` | GT2 SID → USF converter |
| `src/usf_to_sid.py` | USF → rebuilt SID (via V2 codegen) |
| `src/usf.py` | Universal Symbolic Format data structures |
| `src/gt2_decompile.py` | GT2 binary decompiler |
| `src/gt2_parse_direct.py` | Operand-based GT2 parser (finds columns via 6502 instruction analysis) |
| `src/gt2_detect_version.py` | Player group (A/B/C/D) + feature flag detection |
| `src/gt2_compare.py` | Register-level comparison with 8-layer jitter tolerance |
| `src/gt_parser.py` | Low-level GT2 binary parser (freq tables, PSID header) |
| `src/gt2_packer.py` | GT2 freq tables + packing constants |
| `src/detect_flags.py` | GT2 compilation flag detection (legacy packer path) |
| `src/sidfinity_pack.py` | SIDfinity player packer (xa65 assembly) |

### V2 Player Codegen + Optimization
| File | Purpose |
|------|---------|
| `src/player/codegen_v2.py` | V2 per-song 6502 code generator |
| `src/player/codegen.py` | Feature detection for codegen |
| `src/player/peephole.py` | Post-generation branch-over-JMP optimizer (ACTIVE) |
| `src/player/cycle_model.py` | Static cycle counting + path tracing (estimates only) |
| `src/player/layout_opt.py` | JMP/branch distance analysis |
| `src/player/z3_6502.py` | Z3 SMT 6502 model for formal verification |
| `src/player/z3_synth.py` | Z3-based instruction sequence synthesizer |
| `src/player/gpu_6502.cu` | CUDA brute-force 6502 optimizer (dual 3090) |
| `src/player/gpu_optimize.py` | Python interface for GPU optimizer |
| `src/player/regression_test.py` | 3,478-song parallel regression suite (20 sec) |

### Player Reverse-Engineering (sidxray)
| File | Purpose |
|------|---------|
| `src/sidxray/trace.py` | Capture memory traces via `siddump --memtrace` |
| `src/sidxray/analyze.py` | Autocorrelation, periodicity detection, tempo detection, table identification |
| `src/sidxray/xray.py` | Data region discovery from memory access patterns |
| `src/sidxray/gt2_detect.py` | GT2 layout detection from traces |
| `src/sid_data_extractor.py` | Universal SID data table discovery (any player engine) |

### Future Engine Support
| File | Purpose |
|------|---------|
| `src/dmc_parser.py` | DMC (Demo Music Creator) SID parser |
| `src/dmc_to_usf.py` | DMC → USF converter (partial) |

### Analysis + Debugging
| File | Purpose |
|------|---------|
| `src/audio_compare.py` | Audio A/B comparison (PCM cross-correlation + spectral similarity) |
| `src/gt2_triage.py` | Automated F-grade categorization (64-core, ~30 seconds) |
| `src/sidid.py` | Player engine identification wrapper (uses tools/sidid) |
| `src/player/emu_test.py` | py65 6502 emulator test harness (step-debug V2 player) |

### Utilities
| File | Purpose |
|------|---------|
| `src/usf_text.py` | Human-readable USF text serialization |
| `src/songlengths.py` | HVSC Songlengths.md5 database parser |
| `tools/siddump.cpp` | C++ register dumper (libsidplayfp, `--writelog` for cycle timing) |
| `tools/sidrender.cpp` | SID → raw PCM audio renderer |
| `tools/build.sh` | Build script for libsidplayfp + siddump |
| `src/env.sh` | Environment setup (PATH for tools) |

## Project Structure

```
src/                    Active source code
  player/               V2 player codegen + optimization tools
  sidxray/              Player reverse-engineering tools
docs/                   Specifications and reference docs
tools/                  Build tools (xa65, siddump, libsidplayfp)
data/                   HVSC collection (not in git)
deprecated/             Earlier development phases (with READMEs)
```
