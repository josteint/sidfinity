# Reverse Engineering SID Player Engines

## Approaches (investigated April 2026)

Nine approaches were evaluated for parsing SID binaries where static analysis fails (no freq table, non-standard player layout, runtime-computed data). Results below.

### Proven Techniques

**1. Control Flow Analysis (`src/code_flow.py`)**
- Recursive descent from init_addr/play_addr to find all reachable code
- 99.7% success rate on no-freq SIDs
- Code_end is typically ~24 bytes before freq table on standard GT2
- Wired into `parse_gt2_direct` as fallback when `find_freq_table` returns None

**2. Register Trace → USF (`src/regtrace_to_usf.py`)**
- Runs siddump, captures register output, reconstructs USF Song
- Works for ANY player engine — no binary parsing needed
- Current quality: ~3% Grade A on GT2 songs (main loss: wave table cycling, tempo detection)
- Successfully produces output for all 231 unparseable GT2 SIDs
- Key limitation: duration encoding must use NoteEvent.duration field (not one-event-per-tick) to avoid C64 memory exhaustion

**3. Memory Read Tracing (sidxray, `siddump --memtrace`)**
- Already exists in sidxray module
- Identifies instrument columns, ni, table regions from read access patterns
- Works on no-freq SIDs (tested)
- Missing automation: column classification now added to `sidxray/analyze.py`

**4. Memory Diff Analysis (`src/memdiff.py`)**
- Three snapshots via `siddump --memdump`: after init, after 1s, after 5s
- Classifies memory as static (tables, song data) vs dynamic (player state)
- Useful for finding data layout without understanding the player code

**5. Frequency Reconstruction (`src/freq_reconstruct.py`)**
- Extracts played frequencies from siddump output
- Clusters into 12-TET semitones, detects tuning (PAL/NTSC/custom)
- Can search binary for reconstructed table bytes

### Supplementary Techniques

**6. sidid Signature Anchoring**
- GT2 sidid signature is ~750±250 bytes before freq table (93% consistency)
- Can estimate code/data boundary when other methods fail
- GT2-specific, doesn't generalize to other engines

**7. Binary Entropy Analysis**
- Freq tables have distinctive entropy spike (~5.7)
- Code and data entropy ranges overlap too much for standalone use
- Useful as supplementary signal combined with other methods

### Infrastructure

**8. siddump --memdump**
- Dumps 64KB of C64 memory after emulation
- Added `readMemByte()` to libsidplayfp API
- Required by memdiff.py and freq_reconstruct.py (binary search mode)

## Key Architectural Insights

1. **231 GT2 SIDs have no freq table anywhere** — not in the binary, not in post-init memory. The player computes frequencies from note numbers using math (shifts, adds). Static parsing cannot handle these; only the register trace path works.

2. **219 GT2 SIDs are "stripped players"** — they only write freq_lo to SID, no ADSR at all. These use hardcoded ADSR values or external control. Not recoverable by any parsing approach.

3. **Two-region players exist** — code → freq table → data → more code. The `code_end = freq_table_offset` assumption is wrong for ~35 songs. Control flow analysis handles this correctly.

4. **py65 is too simple** for many SIDs — no CIA timer emulation, no IRQ handling. Songs that use interrupt-driven playback produce silence in py65. Use libsidplayfp (via siddump) for full C64 emulation.

## Generalization to Other Engines

For DMC, JCH, and other engines, the recommended approach order:
1. Try static parsing with engine-specific knowledge (like gt2_to_usf)
2. Fall back to register trace → USF (regtrace_to_usf) — works universally
3. Use sidxray for semi-automated reverse engineering of unknown engines
4. Use memdiff + freq_reconstruct for diagnostic analysis
