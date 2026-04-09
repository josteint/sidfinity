# GPU-Accelerated 6502 Superoptimizer — Design Document

## Problem Statement

The V2 codegen player (`codegen_v2.py`) generates ~500-900 bytes of 6502 code.
Any byte-count change shifts all subsequent addresses, changing page-crossing
penalties (+1 cycle) and causing ~1% of songs to change grade. We need
**same-byte-count, fewer-cycle** replacements for hot code blocks.

The existing Z3-based synthesizer (`z3_synth.py`) works but hits a wall at
sequence length 4+: Z3 verification takes seconds per candidate, and the
combinatorial explosion makes length-5+ synthesis impractical on CPU.

GPU brute-force flips this: instead of Z3 symbolic verification, we run
concrete test vectors through a tiny 6502 simulator — one CUDA thread per
candidate sequence. Test-vector equivalence is not a proof, but with 256
random inputs the false-positive rate is astronomically low (2^-2048 for
8-bit outputs).

## Hardware

- 2x NVIDIA GeForce RTX 3090 with NVLink (4x 14 GB/s links)
- 82 SMs per GPU, 10,496 CUDA cores per GPU, 20,992 total
- 125,952 max concurrent threads per GPU (48 warps x 32 threads x 82 SMs)
- 24 GB VRAM each, 48 GB total
- Compute capability 8.6, CUDA 12.0 toolkit installed
- NVLink enables peer-to-peer memory access — can split search space across GPUs

## Architecture Overview

```
Host (Python + ctypes)
  |
  |-- Generate test vectors (run reference code on CPU, 256 input sets)
  |-- Enumerate candidate sequences (restricted opcode set)
  |-- Upload batches of candidates to GPU
  |-- Collect results: (sequence_id, cycle_count, match_bitmap)
  |
  v
Device (CUDA kernel)
  |
  |-- Each thread: one candidate sequence
  |-- Load candidate from global memory (max 16 bytes)
  |-- For each of 256 test inputs (from shared memory):
  |     Execute candidate on simulated 6502
  |     Compare output state against expected
  |-- If all 256 match: atomically report as valid
  |-- Track minimum cycle count across all valid sequences
```

## CUDA Kernel Design

### Thread Organization

```
Grid:  (num_candidates / 256) blocks
Block: 256 threads (8 warps, good occupancy on SM 8.6)
```

Each thread tests one candidate sequence against all 256 test inputs.

### Shared Memory Layout (per block)

Shared memory holds the test vectors so all 256 threads in a block can read
them without global memory traffic. At 100 KB per SM (configurable on 8.6),
we have ample room.

```
Offset  Size   Contents
0x000   256B   test_input_A[256]      — initial A register
0x100   256B   test_input_X[256]      — initial X register
0x200   256B   test_input_Y[256]      — initial Y register
0x300   256B   test_input_flags[256]  — initial flags (NVZC packed)
0x400   N*256B test_input_mem[N][256] — initial memory values (N locations)
--- expected outputs (same layout) ---
0x400+N*256  256B   expected_A[256]
...          256B   expected_X[256]
...          256B   expected_Y[256]
...          256B   expected_flags[256]
...          N*256B expected_mem[N][256]

Total: (4 + N) * 256 * 2 bytes for inputs+outputs
       With N=8 memory locations: 6,144 bytes — trivially fits
```

### Global Memory Layout

```
candidates[]:      uint8[num_candidates][MAX_SEQ_LEN]  — packed instruction bytes
candidate_len[]:   uint8[num_candidates]               — length of each sequence
results[]:         uint32[num_candidates]               — 0 = no match, else cycle count
best_cycles:       uint32 (atomic min)                  — global minimum
best_index:        uint32 (atomic CAS)                  — index of best candidate
```

### Kernel Pseudocode

```c
__global__ void test_sequences(
    const uint8_t* candidates,     // [N][MAX_SEQ]
    const uint8_t* candidate_lens, // [N]
    const TestVectors* tv,         // test inputs/outputs in constant memory
    uint32_t* results,             // [N] output: 0 or cycle count
    uint32_t* best_cycles,         // atomic min
    uint32_t* best_index,          // index of best
    int num_candidates,
    int num_tests,                 // 256
    int num_mem_locs,              // how many memory locations to track
    int byte_budget                // required output byte count (0 = don't care)
) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x;
    if (tid >= num_candidates) return;

    // Load candidate into registers
    uint8_t seq[MAX_SEQ_LEN];  // MAX_SEQ_LEN = 16
    int seq_len = candidate_lens[tid];
    for (int i = 0; i < seq_len; i++)
        seq[i] = candidates[tid * MAX_SEQ_LEN + i];

    // Optional: early reject if byte count != budget
    if (byte_budget > 0) {
        int bytes = compute_byte_count(seq, seq_len);
        if (bytes != byte_budget) { results[tid] = 0; return; }
    }

    // Compute cycle count for this sequence
    int cycles = compute_cycle_count(seq, seq_len);

    // Early reject if cycles >= current best
    if (cycles >= atomicMin(best_cycles, 0xFFFFFFFF))  // read current best
        { results[tid] = 0; return; }  // can't improve

    // Test against all test vectors
    int all_match = 1;
    for (int t = 0; t < num_tests && all_match; t++) {
        // Initialize CPU state from test vector
        uint8_t A = tv->input_A[t];
        uint8_t X = tv->input_X[t];
        uint8_t Y = tv->input_Y[t];
        uint8_t flags = tv->input_flags[t];
        uint8_t mem[MAX_MEM_LOCS];
        for (int m = 0; m < num_mem_locs; m++)
            mem[m] = tv->input_mem[m][t];

        // Execute sequence
        for (int i = 0; i < seq_len; i++) {
            execute_insn(seq[i], &A, &X, &Y, &flags, mem);
        }

        // Compare outputs
        if (A != tv->expected_A[t]) { all_match = 0; break; }
        if (X != tv->expected_X[t]) { all_match = 0; break; }
        if (Y != tv->expected_Y[t]) { all_match = 0; break; }
        // Only check flags that the reference block actually affects
        if ((flags & tv->flags_mask) != tv->expected_flags[t]) { all_match = 0; break; }
        for (int m = 0; m < num_mem_locs; m++)
            if (mem[m] != tv->expected_mem[m][t]) { all_match = 0; break; }
    }

    if (all_match) {
        results[tid] = cycles;
        atomicMin(best_cycles, cycles);
        // CAS to record index (only if we're actually the new best)
    }
}
```

### 6502 Instruction Simulation

Each "instruction" in the candidate is encoded as a single byte index into a
restricted instruction table. The `execute_insn` function is a switch statement
over ~60 entries (not all 256 6502 opcodes — only those used by the player).

```c
__device__ void execute_insn(
    uint8_t insn_id,
    uint8_t* A, uint8_t* X, uint8_t* Y, uint8_t* flags,
    uint8_t* mem
) {
    // insn_id indexes into INSN_TABLE which encodes:
    //   opcode, addressing mode, operand reference
    //
    // Example entries:
    //   0: LDA #imm0   (immediate, value = imm_table[0])
    //   1: LDA #imm1   (immediate, value = imm_table[1])
    //   2: LDA mem[0]  (absolute, location 0)
    //   3: STA mem[0]  (absolute, location 0)
    //   4: TAX
    //   5: TAY
    //   6: CLC
    //   7: SEC
    //   8: ADC #imm0
    //   ...

    switch (insn_id) {
        case OP_LDA_IMM(v):
            *A = v;
            SET_NZ(flags, *A);
            break;
        case OP_LDA_MEM(loc):
            *A = mem[loc];
            SET_NZ(flags, *A);
            break;
        case OP_STA_MEM(loc):
            mem[loc] = *A;
            break;
        case OP_TAX:
            *X = *A;
            SET_NZ(flags, *X);
            break;
        case OP_ADC_IMM(v): {
            int carry = (*flags & FLAG_C) ? 1 : 0;
            int result = *A + v + carry;
            // Set C, V, N, Z
            *flags = (*flags & ~(FLAG_C|FLAG_V|FLAG_N|FLAG_Z));
            if (result > 255) *flags |= FLAG_C;
            if (~(*A ^ v) & (*A ^ result) & 0x80) *flags |= FLAG_V;
            *A = result & 0xFF;
            SET_NZ(flags, *A);
            break;
        }
        // ... ~60 total cases
    }
}
```

This compiles to ~50 CUDA instructions per 6502 instruction simulated (the
switch becomes a jump table, each case is 3-10 instructions).

## Restricted Instruction Set

Only the opcodes that appear in the V2 player are candidates. From analysis
of `codegen_v2.py`, the relevant set is:

```
Loads:     LDA imm/zp/abs/absx/indy, LDX imm/zp/abs, LDY imm/zp/abs/absx
Stores:    STA zp/abs/absx/indy, STX zp/abs, STY zp/abs
Arithmetic: ADC imm/zp/abs, SBC imm/zp/abs, CMP imm/abs, CPX imm, CPY imm
Logic:     AND imm/abs, ORA imm/abs, EOR imm/abs
Shifts:    ASL acc/zp, LSR acc/zp, ROL acc, ROR acc
RMW:       INC zp/abs, DEC zp/abs
Transfer:  TAX, TAY, TXA, TYA
Flags:     CLC, SEC
Stack:     PHA, PLA
Inc/Dec:   INX, INY, DEX, DEY
Other:     NOP, BIT zp/abs
```

For a given code block with M memory operands and K immediate values, the
concrete instruction count per position is:

```
  Loads:   3*K (imm) + 3*M (mem) = 3*(K+M)
  Stores:  3*M
  Arith:   3*K (imm) + 3*M (abs) = 3*(K+M)
  Logic:   3*K + 3*M = 3*(K+M)
  Shifts:  6 (ASL/LSR/ROL/ROR acc + ASL/LSR zp*M)
  Transfer: 4 (TAX/TAY/TXA/TYA)
  Flags:   2 (CLC/SEC)
  Stack:   2 (PHA/PLA)
  Inc/Dec: 4 + 2*M (INX/INY/DEX/DEY + INC/DEC per loc)
  Other:   1 + M (NOP + BIT per loc)
```

Typical block: K=4 immediate values, M=4 memory locations:
  3*8 + 3*4 + 3*8 + 3*8 + 6+4*4 + 4 + 2 + 2 + 4+2*4 + 1+4 = ~120 options/position

## Feasibility Analysis

### Throughput Model

Per thread work: execute N instructions on 256 test vectors.
- N instructions * ~8 CUDA instructions each * 256 tests = 2048*N CUDA instructions
- For N=5: ~10,240 instructions per thread
- At ~1.7 GHz boost clock, 82 SMs, 1536 threads/SM:
  - Throughput per GPU: 82 * 1536 * 1.7e9 / 10240 ~ 21 billion tests/sec (idealized)
  - Real throughput (memory latency, divergence, occupancy): ~10-20% = **2-4 billion/sec**
  - Conservative estimate: **100M-500M candidates/sec per GPU**

### Search Space by Sequence Length

With P=120 options per position:

| Length | Candidates | Time @ 200M/sec/GPU | Time (2 GPUs) |
|--------|------------|---------------------|----------------|
| 1      | 120        | instant             | instant        |
| 2      | 14,400     | instant             | instant        |
| 3      | 1.7M       | 0.009 sec           | 0.004 sec      |
| 4      | 207M       | 1.0 sec             | 0.5 sec        |
| 5      | 24.9B      | 124 sec (2 min)     | 62 sec (1 min) |
| 6      | 2.99T      | 14,900 sec (4.1 hr) | 2 hours        |
| 7      | 358T       | infeasible          | infeasible     |

### Pruning Strategies (10-100x reduction)

1. **Cycle budget pruning**: Skip sequences whose cumulative cycles already
   exceed the reference. Since we enumerate in a tree, prune entire subtrees.
   Expected 5-10x reduction.

2. **Dead code elimination**: Skip sequences that write a register then
   overwrite it without reading. Detectable statically. ~2x reduction.

3. **Canonical ordering**: For commutative operations (two independent STAs),
   enforce lexicographic order. ~2x for blocks with independent stores.

4. **Must-write filter**: If the reference writes to memory locations A, B, C,
   the candidate must contain at least one store to each. Skip candidates
   missing required stores. ~5x reduction for store-heavy blocks.

5. **Operand type match**: STA to memory location X can only store from A (or
   STX/STY for X/Y). Restrict store operands to matching register loads.

6. **Same-byte-count constraint**: For the layout-shift problem, we need the
   replacement to be EXACTLY the same byte count. This dramatically prunes:
   a sequence of all 1-byte implied instructions can't equal a sequence with
   3-byte absolute addressing unless they happen to sum correctly.

With pruning, length 5 becomes ~seconds, length 6 becomes ~minutes, and
length 7 might be reachable for small operand sets.

### Batching Strategy

Rather than generating all candidates on CPU then uploading, generate them
on-GPU using a grid-stride enumeration:

```c
// Thread tid generates candidate by treating tid as a mixed-radix number
// tid = i0 * P^(N-1) + i1 * P^(N-2) + ... + i(N-1)
// where each i_k indexes into the instruction pool
int tmp = tid;
for (int i = N-1; i >= 0; i--) {
    seq[i] = tmp % pool_size;
    tmp /= pool_size;
}
```

This eliminates CPU-GPU candidate transfer entirely. The GPU enumerates
and tests in one kernel launch.

## Target Code Blocks

Analysis of `codegen_v2.py` hot paths, sorted by cycle-savings potential.
The "hot path" is the normal tick (counter > 0): wave table + effects + pulse
+ register writes. This runs 3x per frame (once per channel), every frame.

### Block 1: Frequency Add (ce_fxadd) — 30 cycles, 16 bytes

```
CLC          2cy  1B
LDA abs,X    4cy  3B    ; mt_chnfreqlo,x
ADC abs      4cy  3B    ; mt_temp1
STA abs,X    5cy  3B    ; mt_chnfreqlo,x
LDA abs,X    4cy  3B    ; mt_chnfreqhi,x
ADC abs      4cy  3B    ; mt_temp2 (carry from low byte)
STA abs,X    5cy  3B    ; mt_chnfreqhi,x
```

This is a textbook 16-bit add. Already minimal for 6502 — unlikely to improve.
**Skip.**

### Block 2: Frequency Sub (ce_fxsub) — 30 cycles, 16 bytes

Same as Block 1 but with SEC/SBC. Also minimal. **Skip.**

### Block 3: Register Writes (ce_ldregs) — 46-56 cycles, 25-33 bytes

```
LDA abs,X    4cy  3B    ; mt_chnpulselo,x
STA abs,X    5cy  3B    ; SIDBASE+2,x
LDA abs,X    4cy  3B    ; mt_chnpulsehi,x
STA abs,X    5cy  3B    ; SIDBASE+3,x
LDA abs,X    4cy  3B    ; mt_chnsr,x
STA abs,X    5cy  3B    ; SIDBASE+6,x
LDA abs,X    4cy  3B    ; mt_chnad,x
STA abs,X    5cy  3B    ; SIDBASE+5,x
LDA abs,X    4cy  3B    ; mt_chnfreqlo,x
STA abs,X    5cy  3B    ; SIDBASE,x
LDA abs,X    4cy  3B    ; mt_chnfreqhi,x
STA abs,X    5cy  3B    ; SIDBASE+1,x
LDA abs,X    4cy  3B    ; mt_chnwave,x
AND abs,X    4cy  3B    ; mt_chngate,x
STA abs,X    5cy  3B    ; SIDBASE+4,x
RTS          6cy  1B
```

This is a straight load-store chain. The only optimization is reordering
to share register values (e.g., if two stores use the same source). But
the sources are all different, so this is also minimal. **Skip** (but
reordering variants are worth checking for page-crossing avoidance).

### Block 4: Wave Table Pointer Advance — 22 cycles, 14 bytes

```
LDA abs,Y    4cy  3B    ; mt_wavetbl,y
CMP imm      2cy  2B    ; #LOOPTBL
BNE +5       2cy  2B    ; ce_wnj (not taken = 2cy)
LDA abs,Y    4cy  3B    ; mt_notetbl,y
STA abs,X    5cy  3B    ; mt_chnwaveptr,x
---
INY          2cy  1B    ; ce_wnj
TYA          2cy  1B
STA abs,X    5cy  3B    ; mt_chnwaveptr,x
```

The taken/not-taken paths are different lengths. Not amenable to simple
superoptimization. **Skip.**

### Block 5: Pulse Modulation Core (ce_pmod) — 25-29 cycles, 18 bytes

```
LDA abs,Y    4cy  3B    ; mt_pulsespdtbl-1,y
CLC          2cy  1B
BPL +3       2cy  2B    ; ce_pup (taken = 3cy)
DEC abs,X    7cy  3B    ; mt_chnpulsehi,x
ADC abs,X    4cy  3B    ; mt_chnpulselo,x    [ce_pup]
STA abs,X    5cy  3B    ; mt_chnpulselo,x
BCC +3       2cy  2B    ; ce_pnoc
INC abs,X    7cy  3B    ; mt_chnpulsehi,x
```

Contains branches — not a straight-line block. **Skip** (would need
branch-aware simulation, much more complex).

### Block 6: Speed Table Load — 16 cycles, 11 bytes

```
LDA abs,Y    4cy  3B    ; mt_speedlefttbl-1,y
BPL/BMI      2cy  2B    ; (branch)
STA abs      4cy  3B    ; mt_temp2
LDA abs,Y    4cy  3B    ; mt_speedrighttbl-1,y
STA abs      4cy  3B    ; mt_temp1
```

Minimal for two table lookups + two stores. **Skip.**

### Block 7: New Note Init (ce_newn) — 24-30 cycles, 14-18 bytes

```
SEC          2cy  1B
SBC imm      2cy  2B    ; #NOTE ($60)
STA abs,X    5cy  3B    ; mt_chnnote,x
LDA imm      2cy  2B    ; #0
STA abs,X    5cy  3B    ; mt_chnfx,x
STA abs,X    5cy  3B    ; mt_chnnewnote,x
```

The SEC/SBC/#$60 is needed (subtract NOTE base). LDA #0 then two STAs is
already optimal for clearing two locations. The Z3 synthesizer already
verified this block (Block 1 in z3_synth.py). **Skip.**

### Block 8: Vibrato Phase Update (ce_v4r..ce_v4st) — ~20 cycles, ~14 bytes

```
LDA abs,X    4cy  3B    ; mt_chnvibtime,x
BMI +N       2cy  2B    ; ce_v4nc
CMP abs      4cy  3B    ; mt_fx_spd
BEQ +N       2cy  2B    ; ce_v4nc
BCC +N       2cy  2B    ; ce_v4n2
EOR imm      2cy  2B    ; #$FF
CLC          2cy  1B    ; ce_v4nc
ADC imm      2cy  2B    ; #2
STA abs,X    5cy  3B    ; mt_chnvibtime,x  [ce_v4st]
LSR acc      2cy  1B
BCS ce_fxsub 2cy  2B
```

This is the vibrato triangle-wave generator. Complex control flow with
multiple branch targets. **High value** but needs branch-aware simulation.
A simplified version (straight-line after branch resolution) could work
for specific cases.

### Block 9: Toneporta Distance Check — 38 cycles, 24 bytes

```
LDA abs,X    4cy  3B    ; mt_chnnote,x
TAY          2cy  1B
SEC          2cy  1B
LDA abs,X    4cy  3B    ; mt_chnfreqlo,x
SBC abs,Y    4cy  3B    ; mt_freqtbllo,y
STA abs      4cy  3B    ; mt_temp1
LDA abs,X    4cy  3B    ; mt_chnfreqhi,x
SBC abs,Y    4cy  3B    ; mt_freqtblhi,y
STA abs      4cy  3B    ; mt_temp2
BMI ...      2cy  2B
```

16-bit subtract with table lookup. Already minimal. **Skip.**

### RECOMMENDED TARGETS: Same-Byte-Count NOP Substitution

The real value isn't replacing entire code blocks — it's finding sequences
where we can **swap instruction order or use equivalent instructions** to
avoid page-crossing penalties, keeping the exact same byte count.

For example:
- `LDA abs,X` (4 cycles) vs `LDA abs,X` at a different address (5 cycles
  due to page crossing) — reordering two independent LDA/STA pairs can
  move the page-crossing one to a non-penalty position.
- `JMP` (3 bytes) vs `BRA`-equivalent using `BNE`+known-flag (2 bytes + NOP
  = 3 bytes, same count, saves 1 cycle if branch is always taken).

**Target: enumerate all possible instruction orderings within a basic block
(permutations of independent operations), compute page-crossing penalties
for each ordering at every possible base address, find the ordering with
minimum worst-case cycles.**

This changes the problem: instead of testing 120^N candidates, we test
N! permutations of N instructions (~40,320 for 8 instructions), each
evaluated at 256 base addresses. That is trivially GPU-parallelizable.

## Implementation Plan

### Phase 1: Straight-Line Superoptimizer (same byte count)

**Kernel:** For each candidate (same opcodes, different instruction order),
simulate and verify equivalence. Also compute cycle count at all base
addresses in [0x1000, 0x1FFF] to find minimum page-crossing penalty.

**Host:** Extract basic blocks from V2 assembly, identify independent
instruction pairs, generate permutations.

### Phase 2: Opcode-Substitution Superoptimizer

**Kernel:** For each position in a basic block, try all opcodes that produce
the same result with the same byte count. E.g., `CLC; ADC #0` (3 bytes,
4 cycles) vs `AND #$FF` (2 bytes, 2 cycles) — different byte count so
rejected, but `ORA #0` (2 bytes, 2 cycles) same byte count and same
NZ flags but doesn't affect carry. Whether it's valid depends on whether
carry is observed downstream.

### Phase 3: Full Synthesis (different byte count)

For blocks where same-byte-count can't help, do full length-N synthesis
with the byte-count constraint relaxed. Use a NOP-padding strategy: if
we find an N-1 byte sequence that's equivalent, pad with NOP to match
N bytes. Saves cycles if the NOP cost is less than the original's excess.

## Build Instructions

```bash
# Compile the CUDA kernel
nvcc -O3 -arch=sm_86 \
    -o superopt_kernel.so --shared -Xcompiler -fPIC \
    superopt_kernel.cu

# Python ctypes binding
import ctypes
lib = ctypes.CDLL('./superopt_kernel.so')

# Launch
lib.launch_superopt(
    candidates_ptr, candidate_lens_ptr,
    test_vectors_ptr, results_ptr,
    best_cycles_ptr, best_index_ptr,
    num_candidates, num_tests, num_mem_locs, byte_budget
)
```

### File Structure

```
src/player/
  gpu_optimizer_design.md    -- this document
  gpu_superopt.cu            -- CUDA kernel (Phase 1)
  gpu_superopt.py            -- Python host: block extraction, enumeration, launch
  gpu_insn_table.py          -- restricted instruction set definition (shared)
```

### Dependencies

- CUDA Toolkit 12.0 (`/usr/bin/nvcc`)
- Python 3 with ctypes (standard library)
- numpy (for test vector generation)

## Appendix: Page-Crossing Penalty Model

On 6502, indexed reads (`LDA abs,X` / `LDA abs,Y` / `LDA (zp),Y`) take
+1 cycle when `(base_addr + index) & 0xFF00 != base_addr & 0xFF00`. Writes
(`STA abs,X`) never have this penalty.

For our player, X is always 0, 7, or 14 (channel offset). So:
- `STA $1234,X` with X=14 writes to $1242 — crosses page if $1234 is in
  $12F2-$12FF range.
- `LDA $1234,X` with X=14 reads from $1242 — +1 cycle if page crossed.

The penalty depends on where the label lands in the assembled binary.
Moving code earlier or later shifts all labels, changing which ones cross
page boundaries. This is why same-byte-count replacement is critical:
it preserves the exact layout of everything downstream.

The GPU kernel for Phase 1 (permutation search) evaluates each permutation
at base addresses 0x1000 through 0x1FFF (4096 possibilities) and computes
the cycle count at each, returning the permutation with the best worst-case
or best average cycle count.
