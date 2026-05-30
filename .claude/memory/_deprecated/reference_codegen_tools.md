---
name: Codegen analysis and optimization tools
description: Tools in src/player/ for analyzing, optimizing, and verifying V2 codegen output
type: reference
---

## Active tools

- **cycle_model.py** — static cycle counting with path tracing. Use for estimates, not exact timing (halting problem — use siddump --writelog for dynamic counting).
- **layout_opt.py** — JMP/branch distance analysis on assembled binary.
- **peephole.py** — post-generation optimizer (ACTIVE, integrated into codegen_v2). Converts branch-over-JMP to inverted branches. ~12 bytes/song.
- **z3_6502.py** — 6502 CPU model for Z3 SMT solver. Formally verifies instruction equivalence.
- **z3_synth.py** — sequence synthesizer using Z3. Expensive — use for small (3-8 instruction) blocks.
- **gpu_6502.cu + gpu_optimize.py** — CUDA brute-force on dual 3090s. Confirmed code blocks are at 6502 minimum.

## When to use
- Before changing codegen: cycle_model for current budget
- After changing codegen: peephole runs automatically, then regression test (33 sec)
- For new optimizations: Z3 to verify, GPU for exhaustive search
- For exact timing: siddump --writelog (dynamic execution, not static analysis)
