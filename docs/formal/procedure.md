# SIDfinity: Mathematical Methods Procedure

How to use the tested mathematical tools in practice.

## When to Use What

### Increasing Grade A Count (highest priority)

**Tool: Trace equivalence analysis** (`src/formal/trace_equivalence.py`, `src/sid_compare.py`)

When: after any pipeline change, or periodically to mine for new tolerance rules.

Procedure:
1. Run `src/formal/trace_equivalence.py` — check mathematical properties (symmetry, reflexivity, monotonicity)
2. If a property violation is found, fix `sid_compare.py`
3. Sample 50 Grade B songs, classify the `note_wrong` / `wave_wrong` frames
4. Look for patterns: are these differences genuinely audible?
5. If a common inaudible pattern is found, add a tolerance rule
6. Run full GT2 batch (`python3 src/gt2_triage.py`) to measure Grade A change
7. Run regression (`python3 src/player/regression_test.py`) to verify zero regressions
8. Rebuild regression registry if Grade A count increased

Track record: +233 (EarlyNoteStart symmetry), +5 (FrameShift symmetry), +155 (both-gates-off release) = **+393 songs** from three rule changes.

### Preparing USF for ML Training

**Tool: USF normalization** (based on experiment 5 results)

When: before tokenizing USF for transformer training.

Procedure:
1. Apply 4 rewrite rules in order:
   - Duration merging: consecutive rests → single rest with summed duration
   - Instrument dedup: merge instruments with identical (AD, SR, waveform, wave_table)
   - Pattern dedup: merge identical event sequences
   - Transpose normalization: inline transposes into note values (when it reduces tokens)
2. Re-verify Grade A after normalization (expect ~1% measurement-artifact regressions)
3. Tokenize the normalized USF

Expected: 22% average token reduction. Rest merging fires on 100% of songs.

### Fast Development Iteration

**Tool: Formal USF semantics** (`src/formal/usf_semantics.py`)

When: testing codegen changes, triaging bugs, quick validation.

Procedure:
1. Convert SID to USF: `song = gt2_to_usf(sid_path)`
2. Run formal player: `player = USFPlayer(song); trace = player.run(500)`
3. Compare with siddump output of rebuilt SID
4. If formal and V2 agree but both differ from original → USF extraction bug
5. If formal differs from V2 → possible codegen bug (verify with siddump)

Speed: 13ms per song (15x faster than siddump roundtrip). Use as pre-commit smoke test.

Limitations: 84% frame accuracy (±5 tolerance). Not accurate enough for grading — always confirm with siddump for final Grade assessment.

### Cracking New Engine Types

**Tool: Taint tracking** (based on experiment 3, `/tmp/symbolic_exec.py`)

When: encountering a new SID player engine for the first time.

Procedure:
1. Load the SID into py65 (6502 emulator)
2. Run the play routine for 50 frames with taint tracking
3. For each SID register write, examine the read dependencies:
   - Reads from a contiguous memory region → data table (freq, instrument, etc.)
   - Reads from zero page with varying addresses → table index variable
   - Reads from code region → self-modifying code (need SMC tracking)
4. Classify the engine architecture:
   - Table-based ADSR + SMC freq → GT2-style
   - Table-based freq + inline ADSR → Hubbard-style
   - Indexed X=0,7,14 loop → standard voice loop
   - Separate per-voice routines → Hubbard/custom
5. Use the discovered structure to bootstrap a format-specific parser

**Tool: Abstract interpreter** (`src/formal/abstract_interp.py`)

Complementary to taint tracking. Faster (no execution needed) but misses indirect addressing.

Procedure:
1. Run: `python3 src/formal/abstract_interp.py <sid_path>`
2. Check output: voice loop type, SID write count, tempo counter, freq table (if found)
3. Use voice loop type to determine parser structure
4. Use SID write count to estimate player complexity

### Assessing USF Efficiency

**Tool: Information theory metrics** (based on experiment 9)

When: evaluating tokenization strategies for ML, comparing USF versions.

Key metrics:
- Per-token entropy: 5.67 bits (current). Lower = more predictable = easier for transformer.
- Rest tokens: 42% of stream. Run-length encoding could reduce this.
- Voice mutual information: 31%. Joint voice modeling could exploit this.
- USF gzip vs SID gzip: USF is 12% smaller. USF is an efficient structural representation.

## Tools NOT Recommended

| Tool | Why Not |
|------|---------|
| Z3 inverse solver for GT2 | Static parser already extracts custom freq tables. Z3 finds same answers slower. |
| CEGIS auto-fix | Grade C/F errors are systematic pipeline bugs. Fixing individual notes treats symptoms. |
| Lean 4 formalization | Z3 already verifies instruction equivalence. Real bugs are in decompiler logic, not 6502 semantics. |

## Decision Framework

When facing a new problem, ask:

1. **Is it a grading/comparison problem?** → Trace equivalence analysis. Check for mathematical property violations, add tolerance rules.

2. **Is it a new engine to crack?** → Taint tracking + abstract interpretation. Discover driver structure before writing parser.

3. **Is it an ML training quality problem?** → USF normalization + information theory metrics. Reduce tokens, measure redundancy.

4. **Is it a development speed problem?** → Formal semantics player. Fast smoke testing, bug triage.

5. **Is it an individual wrong note/byte?** → Don't use CEGIS. Fix the root cause in the pipeline instead.
