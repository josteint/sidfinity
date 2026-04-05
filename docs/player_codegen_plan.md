# Per-Song Code Generator Plan for SIDfinity 6502 Player

**Status:** Phase 1 complete, Phase 3.1 complete. V2 codegen produces 878 bytes (Covfefe). VBI timing issue blocks VBI-mode activation. CIA mode works.
**Goal:** Replace monolithic `sidfinity_player.s` with a Python code generator that emits only the code blocks a specific song needs. Target: ~400-500 bytes for simple songs (Covfefe), ~900 bytes full features.

## Architecture

```
USF Song → FeatureDetector → BlockSelector → BlockSorter → LabelResolver → AssemblyEmitter → xa65
```

The generator models the player as a set of **blocks** — small units of 6502 assembly with declared interfaces. For each song, it selects needed blocks, sorts for fall-through, resolves labels, and emits minimal assembly.

---

## Phase 1: Foundation — Block-Based Code Generator

- [x] **1.1 Define `Block` dataclass** (M) — `src/player/codegen.py` — `name, code, provides, requires, feature_flags, anti_flags, byte_estimate, cycle_estimate, order_hint, fall_through_to`
- [x] **1.2 Decompose `sidfinity_player.s` into ~30 blocks** (L) — superseded by V2 instruction-level codegen `src/player/codegen_v2.py` — Parse the monolithic source into blocks at section boundaries. Each block is a Python string of xa65 assembly.
- [x] **1.3 Build `FeatureDetector`** (M) — 24 flags, dependency lattice with transitive closure — Analyze USF Song, produce feature flag set. ~30 flags (see Phase 2 for the full list).
- [x] **1.4 Build `BlockSelector`** (S) — in codegen.py
- [x] **1.5 Build `BlockSorter`** (S) — superseded by V2 linear emit
- [x] **1.6 Build `LabelResolver`** (S) — xa65 handles this
- [x] **1.7 Build `AssemblyEmitter`** (M) — codegen_v2.py emit functions
- [ ] **1.8 Integrate with `sidfinity_pack.py`** (M) — wired but disabled. VBI timing issue: different binary layout causes different register output. See `memory/reference_vbi_timing.md`.
- [ ] **1.9 Regression validation** (M) — blocked by 1.8. Monolithic passes 43/43 at 99.8%.

## Phase 2: Immediate Optimizations — Fine-Grained Flags

Each adds a feature flag the detector can disable per song. Savings are code bytes stripped.

### 2.1 Effect Flags
- [ ] **NOVIBRATO** (S) — Strip fx0 + fx4 blocks. ~80 bytes.
- [ ] **NOPORTAMENTO** (S) — Strip portamento speed loading. ~20 bytes.
- [ ] **NOTONEPORTA** (S) — Strip fx3 block (largest single effect). ~100 bytes.
- [ ] **NOCALCULATEDSPEED** (S) — Strip note-relative speed calculation. ~40 bytes.
- [ ] **NOFUNKTEMPO** (S) — Strip funktempo toggle in counter reload. ~15 bytes.

### 2.2 Wave/Pulse/Filter Flags
- [ ] **NOWAVEDELAY** (S) — Strip wave delay handling. ~20 bytes.
- [ ] **NOWAVECMD** (S) — Strip wave command dispatch ($E0-$EF). ~30 bytes.
- [ ] **NOPULSEMOD** (S) — Strip pulse table execution entirely. ~60 bytes.
- [ ] **NOFILTER** (S) — Already implemented. ~55 bytes.

### 2.3 Orderlist/Tick-0 Flags
- [ ] **NOTRANS** (S) — Strip orderlist transpose. ~12 bytes.
- [ ] **NOREPEAT** (S) — Strip orderlist repeat. ~20 bytes.
- [ ] **NOSETAD through NOSETTEMPO** (S each) — Strip individual tick-0 FX handlers. ~4-8 bytes each.

### 2.4 Data-Level Optimizations
- [ ] **Pre-bake transposes** (M) — Apply transpose to note bytes at pack time. Eliminates `adc mt_chntrans,x` at runtime.
- [ ] **Pre-resolve wave note entries to frequencies** (L) — Replace runtime freq table lookup with precomputed values for absolute notes.
- [ ] **Shared `freq_lookup` subroutine** (S) — Extract into subroutine, called from 4-5 sites. Saves ~16-23 bytes net.
- [ ] **Inline SID writes** (M) — For BW=0, eliminate shadow variables entirely.

## Phase 3: Mathematical Framework

### 3.1 Formal Block Model
- [x] **6502 cycle counter** (M) — `src/player/cycle_model.py`. Parses xa65 assembly, counts cycles per addressing mode, detects page-crossing penalties, traces execution paths. Proved player takes 628 cycles (budget 8,500).
- [ ] **Page-crossing analysis on CODE addresses** (M) — Extend cycle_model to analyze JSR/JMP/branch targets for page-crossing penalties. This is the suspected cause of the VBI timing difference between V2 and monolithic.
- [x] **Feature dependency lattice** (M) — `close_features()` in codegen.py. Transitive closure of implications.
- [ ] **Define block interfaces formally** (M) — Input/output registers, memory reads/writes, SID side effects.
- [ ] **Postcondition/precondition checking** (L) — For each block transition, verify output registers satisfy next block's input requirements.
- [x] **Boolean SAT for flag consistency** (M) — Handled by `close_features()` + `select_blocks()` validation.

### 3.2 Layout Optimization
- [ ] **Topological sort with branch-distance awareness** (M) — Keep conditional-branch-connected blocks within 127 bytes.
- [ ] **Fall-through chain optimization** (M) — Maximize length of fall-through chains to minimize JMP count.
- [ ] **JMP elision pass** (S) — After layout, remove JMPs where target is the next instruction.

## Phase 4: Advanced Optimizations (Research Projects)

### 4.1 Superoptimization
- [ ] **SAT/SMT superoptimization using z3** (XL) — Encode 6502 semantics as SMT constraints. Find shorter instruction sequences for hot blocks (wave exec, pulse exec, freq add/sub, loadregs). Target: 3-5 instruction blocks.
- [ ] **Include undocumented opcodes** (M) — LAX (load A+X), SAX (store A AND X), DCP (DEC+CMP), ALR (AND+LSR), SBX (A AND X minus immediate). z3 can discover uses a human wouldn't think of.
- [ ] **Peephole optimizer post-pass** (L) — Pattern-match inefficiencies in emitted assembly. Redundant loads, JMP-to-next-instruction, etc.

### 4.2 Channel Unrolling
- [ ] **3 separate channel routines** (XL) — Hardcoded SID addresses. Eliminates all `,x` indexed STA overhead (1 cycle per store). Code size 3x but cycle count reduced.
- [ ] **Per-channel specialization** (XL) — If CH1 uses vibrato but CH2 doesn't, CH2's routine omits vibrato code. The code generator can detect this per channel.

### 4.3 Search-Based Optimization
- [ ] **Genetic algorithm for block ordering** (L) — Chromosome = block permutation. Fitness = assembled size. Mutation = swap/move blocks. Find orderings that save bytes via better fall-through.
- [ ] **STOKE-style stochastic search** (XL) — Random mutations of instruction sequences. Fast correctness oracle via siddump comparison. Can find solutions SAT misses.

### 4.4 Runtime Optimizations
- [ ] **Delta encoding of SID registers** (L) — Compare before writing, skip unchanged registers. Saves cycles on sustained notes, costs cycles on fast modulation.
- [ ] **Interleaved channel processing** (XL) — Process wave for all 3 channels, then pulse for all 3, then loadregs for all 3. Spreads SID writes across the frame.
- [ ] **Self-modifying code for data addresses** (M) — Patch LDA operands at init time (like MiniPlayer does). Eliminates indirect addressing during playback.

### 4.5 Data-Side Optimizations
- [ ] **Pre-expanded wavetable sequences** (L) — For instruments without pitch modulation, flatten wave table into a simple byte stream. Eliminates the wave table interpreter.
- [ ] **Destination-compare for pulse/filter** (L) — MiniPlayer technique: compare current value against target instead of time counter. Eliminates `pulsetime` variable.
- [ ] **Note+instrument packing** (M) — MiniPlayer packs note+instrument into one byte (LSB = has instrument). Halves pattern data for many songs.

### 4.6 Profiling
- [ ] **HVSC corpus feature statistics** (M) — Analyze all ~7000 GT2 SIDs. What % use each feature? What's the average byte savings per flag? Data-driven optimization priority.
- [ ] **Per-frame cycle profiling** (M) — Measure actual cycles per block on representative songs. Identify the real bottlenecks.

## Phase 5: Testing and Validation

- [ ] **5.1 Regression: 43/43 SIDs pass with codegen** (M)
- [ ] **5.2 Byte count verification per block** (M) — Assembled size matches estimate.
- [ ] **5.3 Cycle count verification per block** (L) — Worst-case/best-case cycle counts.
- [ ] **5.4 A/B comparison: codegen vs monolithic** (M) — Binary diff + siddump comparison.
- [ ] **5.5 Audio comparison** (M) — Spectral similarity > 0.999.
- [ ] **5.6 Size reduction report** (S) — Per-song savings analysis.
- [ ] **5.7 Expand regression to 100+ SIDs** (M) — Cover every feature flag.

## Implementation Order

```
Phase 1 (foundation)
  ├── Phase 2 (flags, parallel)
  │     └── Phase 4.6 (HVSC profiling, informs priorities)
  ├── Phase 3 (math framework, parallel)
  │     └── Phase 4.1 (SAT superoptimization)
  ├── Phase 5 (testing, continuous)
  └── Phase 4.2-4.5 (advanced, after foundation solid)
```

## Key Design Decisions

1. **Template + fixup**: Blocks are literal xa65 assembly strings. Python handles selection/ordering; xa65 handles address resolution.
2. **Continuation passing**: Each block declares register contracts. Composition is verified automatically.
3. **Partial evaluation**: The generator specializes a generic player to a specific song at pack time.
4. **xa65 backend**: Output is human-readable assembly. Debuggable, inspectable.
5. **Backward compatibility**: Monolithic path remains available via `use_codegen=False`.
