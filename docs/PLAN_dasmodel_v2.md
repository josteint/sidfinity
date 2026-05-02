# Das Model v2 — Formal Specification and Verified Compiler

## Vision

A Lean 4 verified compiler that transforms universal SID music descriptions (USF)
into instruction streams that produce perfect audio on the SID chip. The compiler
IS the specification — correctness by construction, not by testing.

## Architecture

```
ANY SID binary                    Lean 4 formal spec
     │                            ┌──────────────────┐
     ▼                            │  SID.lean         │
Engine-specific decompiler        │  - 25 registers   │
(Python, untrusted)               │  - CtrlBits       │
     │                            │  - Instrument     │
     ▼                            │  - EffectChain    │
    USF                           │  - Song           │
(universal music format)          │  - compile()      │
     │                            └────────┬─────────┘
     ▼                                     │
Verified compile (Lean → C)                │
     │                                     │
     ▼                                     │
Instruction Stream ◄──────────────── proven correct
     │
     ▼
6502 codegen (emit LDA/STA from stream)
     │
     ▼
Playable .SID file
```

Decompilers are VERIFIED by: `compile(decompile(original_stream)) == original_stream`.
Each passing song proves correctness for that song. No formal proof of decompilers needed.

## Checklist

### Phase 1: Lean Foundation (current)

- [x] Define SIDReg type (all 25 writable registers)
- [x] Define CtrlBits (gate, sync, ring, test, triangle, sawtooth, pulse, noise)
- [x] Define SIDWrite and FrameStream types
- [x] Define NoteOn with write order
- [x] Define effect specs (Vibrato, Arp, PW, Filter, FreqSlide, HardRestart, Digi)
- [x] Define Instrument (behavioral spec with effect chain and write order)
- [x] Define Song (T, I, S + voice order)
- [x] Define compile type signature
- [x] Separate engine-specific code (decompilers) from formal spec
- [ ] Add FreqTable with static vs dynamic entries
- [ ] Add extended table semantics (T[96+] computed from engine state)
- [ ] Add tick/speed model (how note durations map to frames)

### Phase 2: Implement compile in Lean

- [ ] Implement per-voice frame evaluation
  - [ ] Tick counter decrement and note load
  - [ ] Effect chain evaluation (vibrato → freqSlide → arp, each writes to stream)
  - [ ] W program stepping (waveform sequence with loop)
  - [ ] PW modulation (linear, bidirectional, table)
  - [ ] ADSR zeroing (hard restart)
  - [ ] Note-load write order (freq → ctrl → pw → adsr)
  - [ ] Effects skip on note-load frames
- [ ] Implement voice processing order (configurable, e.g., V3→V2→V1)
- [ ] Implement shared mutable PW state (write-back to instrument table)
- [ ] Implement dynamic T entries (hub_off tracking, ctrl_byte tracking)
- [ ] Implement filter modulation (cutoff sweep, table-driven)
- [ ] Implement digi playback (rapid $D418 writes at sample rate)

### Phase 3: Extract and verify

- [ ] Extract Lean compile to C (Lean 4 native compilation)
- [ ] Wrap extracted C in Python (ctypes or cffi)
- [ ] Test: compile Commando USF → stream → compare to hubbard_emu.py stream
- [ ] Target: 100% match on Commando (11,779 frames)
- [ ] Test on 5 more Hubbard songs
- [ ] Test on 10 GT2 songs (using gt2_decompile → USF → compile → stream)
- [ ] Test on 5 JCH songs

### Phase 4: Prove properties

- [ ] Prove compile is total (always terminates, produces valid stream)
- [ ] Prove compile is deterministic (same Song → same stream)
- [ ] Prove NoteOn.toStream respects write order
- [ ] Prove effect chain writes are correctly ordered
- [ ] Prove gate-before-ADSR invariant (prevents ADSR malfunction)
- [ ] Prove PW shared state consistency
- [ ] Prove extended table computation correctness

### Phase 5: Scale to HVSC

- [ ] Run verification on all 4,968 GT2 Grade A songs
- [ ] Run verification on all Hubbard songs (~95)
- [ ] Run verification on JCH songs (~3,678)
- [ ] Identify failing songs → missing USF features → extend Lean spec
- [ ] Target: 10,000+ verified songs
- [ ] Add CIA timer / multispeed support
- [ ] Add filter table support
- [ ] Add digi support

### Phase 6: ML training

- [ ] Only VERIFIED songs go into training data
- [ ] Tokenize USF with hierarchical scheme (~400 vocab, ~800 tokens/song)
- [ ] Train GPT-2 nano (12M params) on verified USF corpus
- [ ] Grammar-constrained decoding (generated USF must type-check)
- [ ] Generated Songs compiled by verified Lean compiler
- [ ] Output: playable .SID files, correct by construction

### Phase 7: Novel music

- [ ] Generate instruments with novel effect chains
  (e.g., Hubbard-style vibrato + GT2-style filter sweep)
- [ ] Fine-tune on specific composer styles
- [ ] Interactive composition: user provides structure, model fills details
- [ ] Multi-subtune generation (games need multiple tracks)

## Key Principles

1. **The instruction stream is the ground truth.** Not register values at frame
   boundaries — the FULL ordered sequence of writes, including intermediate values.

2. **The sound IS the composition.** USF encodes everything about how the music
   sounds. No "engine selection" — the instrument behavioral spec determines the sound.

3. **Decompilers are untrusted.** Only compile is verified. Decompilers are tested
   empirically: compile(decompile(stream)) == stream.

4. **Math finds bugs.** DFT found PW was correct. Information theory found shared
   mutable PW. Temporal logic found accum-then-write. Group theory solved T[100].
   Bisimulation found freq skip. Keep using math.

5. **Extract, don't reconstruct.** Grab behavior directly from the original binary.
   Every reconstruction step is lossy. The user taught us this.

6. **Question implausible explanations.** If an explanation requires the original
   composer to have done something implausible, the explanation is wrong — look
   for a missing feature. The user taught us this too.

## Current State (as of session)

- Commando instruction stream: 100% match through 2500 frames, ~62% at 5000 frames
- Remaining mismatches: write ordering in specific code paths
- SID.lean: types defined, compile not yet implemented
- Python das_model_gen.py: working but has subtle bugs that Lean would prevent
- 19 research agents completed: ML architecture, tokenization, training pipeline,
  HVSC coverage (39,861 songs addressable), universal decompiler design, etc.
- hubbard_emu.py: 100% verified Python emulator (ground truth)
