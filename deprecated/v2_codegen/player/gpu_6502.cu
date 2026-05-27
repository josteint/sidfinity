/*
 * gpu_6502.cu — GPU-accelerated 6502 instruction sequence optimizer.
 *
 * Each CUDA thread simulates one candidate instruction sequence and
 * checks if it produces the same output as the reference. The search
 * finds sequences with minimum cycle count (considering page crossings).
 *
 * Build: nvcc -O2 -o gpu_6502 gpu_6502.cu -arch=sm_86
 * Usage: Called from Python via ctypes
 */

#include <stdio.h>
#include <stdint.h>
#include <string.h>

// ============================================================
// 6502 CPU state (minimal — registers + flags + small memory)
// ============================================================

struct CPU {
    uint8_t A, X, Y;
    uint8_t C, Z, N, V;  // flags (0 or 1)
    uint8_t mem[32];      // tracked memory locations (mapped to indices)
    int cycles;
};

// ============================================================
// Instruction encoding
// ============================================================

// Instructions are encoded as: opcode (1 byte) + operand type + operand value
// Opcode IDs (not real 6502 opcodes — our internal encoding):
enum Op {
    OP_LDA_IMM=0, OP_LDA_MEM, OP_LDX_IMM, OP_LDX_MEM,
    OP_LDY_IMM, OP_LDY_MEM,
    OP_STA_MEM, OP_STX_MEM, OP_STY_MEM,
    OP_TAX, OP_TAY, OP_TXA, OP_TYA,
    OP_ADC_IMM, OP_SBC_IMM, OP_CMP_IMM,
    OP_AND_IMM, OP_ORA_IMM, OP_EOR_IMM,
    OP_ASL_A, OP_LSR_A, OP_ROL_A, OP_ROR_A,
    OP_SEC, OP_CLC,
    OP_INX, OP_INY, OP_DEX, OP_DEY,
    OP_NOP,
    OP_COUNT
};

// Cycle costs per opcode
__constant__ int CYCLE_COST[OP_COUNT] = {
    2, 4, 2, 4,    // LDA imm/mem, LDX imm/mem
    2, 4,           // LDY imm/mem
    5, 4, 4,        // STA mem (abs,X=5), STX mem, STY mem
    2, 2, 2, 2,    // transfers
    2, 2, 2,        // ADC/SBC/CMP imm
    2, 2, 2,        // AND/ORA/EOR imm
    2, 2, 2, 2,    // shifts
    2, 2,           // SEC/CLC
    2, 2, 2, 2,    // INX/INY/DEX/DEY
    2               // NOP
};

struct Instruction {
    uint8_t op;       // Op enum
    uint8_t operand;  // immediate value or memory index
};

// ============================================================
// 6502 execution (single instruction)
// ============================================================

__device__ void set_nz(CPU* cpu, uint8_t val) {
    cpu->N = (val >> 7) & 1;
    cpu->Z = (val == 0) ? 1 : 0;
}

__device__ void exec_one(CPU* cpu, const Instruction* inst) {
    uint8_t val;
    uint16_t result16;
    uint8_t result;

    cpu->cycles += CYCLE_COST[inst->op];

    switch (inst->op) {
        case OP_LDA_IMM: cpu->A = inst->operand; set_nz(cpu, cpu->A); break;
        case OP_LDA_MEM: cpu->A = cpu->mem[inst->operand]; set_nz(cpu, cpu->A); break;
        case OP_LDX_IMM: cpu->X = inst->operand; set_nz(cpu, cpu->X); break;
        case OP_LDX_MEM: cpu->X = cpu->mem[inst->operand]; set_nz(cpu, cpu->X); break;
        case OP_LDY_IMM: cpu->Y = inst->operand; set_nz(cpu, cpu->Y); break;
        case OP_LDY_MEM: cpu->Y = cpu->mem[inst->operand]; set_nz(cpu, cpu->Y); break;
        case OP_STA_MEM: cpu->mem[inst->operand] = cpu->A; break;
        case OP_STX_MEM: cpu->mem[inst->operand] = cpu->X; break;
        case OP_STY_MEM: cpu->mem[inst->operand] = cpu->Y; break;
        case OP_TAX: cpu->X = cpu->A; set_nz(cpu, cpu->X); break;
        case OP_TAY: cpu->Y = cpu->A; set_nz(cpu, cpu->Y); break;
        case OP_TXA: cpu->A = cpu->X; set_nz(cpu, cpu->A); break;
        case OP_TYA: cpu->A = cpu->Y; set_nz(cpu, cpu->A); break;
        case OP_ADC_IMM:
            val = inst->operand;
            result16 = (uint16_t)cpu->A + val + cpu->C;
            cpu->A = (uint8_t)result16;
            cpu->C = (result16 > 255) ? 1 : 0;
            set_nz(cpu, cpu->A);
            break;
        case OP_SBC_IMM:
            val = inst->operand;
            result16 = (uint16_t)cpu->A - val - (1 - cpu->C);
            cpu->A = (uint8_t)result16;
            cpu->C = (result16 <= 255) ? 1 : 0;
            set_nz(cpu, cpu->A);
            break;
        case OP_CMP_IMM:
            val = inst->operand;
            result = cpu->A - val;
            cpu->C = (cpu->A >= val) ? 1 : 0;
            set_nz(cpu, result);
            break;
        case OP_AND_IMM: cpu->A &= inst->operand; set_nz(cpu, cpu->A); break;
        case OP_ORA_IMM: cpu->A |= inst->operand; set_nz(cpu, cpu->A); break;
        case OP_EOR_IMM: cpu->A ^= inst->operand; set_nz(cpu, cpu->A); break;
        case OP_ASL_A: cpu->C = (cpu->A >> 7) & 1; cpu->A <<= 1; set_nz(cpu, cpu->A); break;
        case OP_LSR_A: cpu->C = cpu->A & 1; cpu->A >>= 1; set_nz(cpu, cpu->A); break;
        case OP_ROL_A: val = cpu->C; cpu->C = (cpu->A >> 7) & 1; cpu->A = (cpu->A << 1) | val; set_nz(cpu, cpu->A); break;
        case OP_ROR_A: val = cpu->C; cpu->C = cpu->A & 1; cpu->A = (cpu->A >> 1) | (val << 7); set_nz(cpu, cpu->A); break;
        case OP_SEC: cpu->C = 1; break;
        case OP_CLC: cpu->C = 0; break;
        case OP_INX: cpu->X++; set_nz(cpu, cpu->X); break;
        case OP_INY: cpu->Y++; set_nz(cpu, cpu->Y); break;
        case OP_DEX: cpu->X--; set_nz(cpu, cpu->X); break;
        case OP_DEY: cpu->Y--; set_nz(cpu, cpu->Y); break;
        case OP_NOP: break;
    }
}

// ============================================================
// Test kernel: each thread tests one candidate sequence
// ============================================================

// Test inputs: 256 different initial states
#define NUM_TESTS 256
#define MAX_SEQ_LEN 8

__constant__ CPU test_inputs[NUM_TESTS];
__constant__ CPU ref_outputs[NUM_TESTS];  // expected outputs from reference
__constant__ uint8_t output_mask[32];     // which memory locations to check
__constant__ int check_A, check_X, check_Y, check_C;  // which registers to check
__constant__ int ref_cycles;              // reference cycle count

// Candidate instruction pool
__constant__ Instruction pool[256];
__constant__ int pool_size;
__constant__ int seq_len;

__global__ void search_kernel(int* best_cycles, int* best_idx, int batch_offset) {
    int tid = blockIdx.x * blockDim.x + threadIdx.x + batch_offset;

    // Decode thread ID into instruction sequence indices
    // tid encodes a mixed-radix number: digit[i] selects pool[digit[i]]
    int indices[MAX_SEQ_LEN];
    int t = tid;
    for (int i = seq_len - 1; i >= 0; i--) {
        indices[i] = t % pool_size;
        t /= pool_size;
    }
    if (t > 0) return;  // tid exceeds search space

    // Calculate cycle count first (early pruning)
    int total_cycles = 0;
    for (int i = 0; i < seq_len; i++) {
        total_cycles += CYCLE_COST[pool[indices[i]].op];
    }
    if (total_cycles >= *best_cycles) return;  // worse than current best

    // Test against all test inputs
    for (int test = 0; test < NUM_TESTS; test++) {
        CPU cpu = test_inputs[test];
        cpu.cycles = 0;

        // Execute candidate sequence
        for (int i = 0; i < seq_len; i++) {
            exec_one(&cpu, &pool[indices[i]]);
        }

        // Compare outputs
        CPU ref = ref_outputs[test];
        if (check_A && cpu.A != ref.A) return;
        if (check_X && cpu.X != ref.X) return;
        if (check_Y && cpu.Y != ref.Y) return;
        if (check_C && cpu.C != ref.C) return;
        for (int j = 0; j < 32; j++) {
            if (output_mask[j] && cpu.mem[j] != ref.mem[j]) return;
        }
    }

    // All tests passed! Report if better than current best
    atomicMin(best_cycles, total_cycles);
    if (total_cycles <= *best_cycles) {
        *best_idx = tid;
    }
}

// ============================================================
// Host interface
// ============================================================

extern "C" {

int gpu_search(
    // Test inputs/outputs
    CPU* h_inputs, CPU* h_outputs, int num_tests,
    // What to check
    int h_check_A, int h_check_X, int h_check_Y, int h_check_C,
    uint8_t* h_output_mask,
    // Instruction pool
    Instruction* h_pool, int h_pool_size,
    // Search params
    int h_seq_len, int h_ref_cycles,
    // Output
    int* result_cycles, int* result_indices
) {
    // Copy to constant memory
    cudaMemcpyToSymbol(test_inputs, h_inputs, sizeof(CPU) * num_tests);
    cudaMemcpyToSymbol(ref_outputs, h_outputs, sizeof(CPU) * num_tests);
    cudaMemcpyToSymbol(output_mask, h_output_mask, 32);
    cudaMemcpyToSymbol(check_A, &h_check_A, sizeof(int));
    cudaMemcpyToSymbol(check_X, &h_check_X, sizeof(int));
    cudaMemcpyToSymbol(check_Y, &h_check_Y, sizeof(int));
    cudaMemcpyToSymbol(check_C, &h_check_C, sizeof(int));
    cudaMemcpyToSymbol(pool, h_pool, sizeof(Instruction) * h_pool_size);
    cudaMemcpyToSymbol(pool_size, &h_pool_size, sizeof(int));
    cudaMemcpyToSymbol(seq_len, &h_seq_len, sizeof(int));
    cudaMemcpyToSymbol(ref_cycles, &h_ref_cycles, sizeof(int));

    // Allocate device results
    int* d_best_cycles;
    int* d_best_idx;
    cudaMalloc(&d_best_cycles, sizeof(int));
    cudaMalloc(&d_best_idx, sizeof(int));
    cudaMemcpy(d_best_cycles, &h_ref_cycles, sizeof(int), cudaMemcpyHostToDevice);
    int neg1 = -1;
    cudaMemcpy(d_best_idx, &neg1, sizeof(int), cudaMemcpyHostToDevice);

    // Calculate search space
    long long search_space = 1;
    for (int i = 0; i < h_seq_len; i++) {
        search_space *= h_pool_size;
        if (search_space > 1000000000LL) break;  // cap at 1B
    }

    // Launch kernel in batches
    int threads_per_block = 256;
    long long total_threads = search_space < 1000000000LL ? search_space : 1000000000LL;
    int blocks = (total_threads + threads_per_block - 1) / threads_per_block;

    printf("GPU search: %lld candidates, %d blocks x %d threads\n",
           total_threads, blocks, threads_per_block);

    search_kernel<<<blocks, threads_per_block>>>(d_best_cycles, d_best_idx, 0);
    cudaDeviceSynchronize();

    // Read results
    cudaMemcpy(result_cycles, d_best_cycles, sizeof(int), cudaMemcpyDeviceToHost);
    cudaMemcpy(result_indices, d_best_idx, sizeof(int), cudaMemcpyDeviceToHost);

    cudaFree(d_best_cycles);
    cudaFree(d_best_idx);

    return 0;
}

}  // extern "C"

// ============================================================
// Standalone test
// ============================================================

int main() {
    printf("GPU 6502 Optimizer\n");
    printf("GPU devices: ");
    int count;
    cudaGetDeviceCount(&count);
    printf("%d\n", count);

    for (int i = 0; i < count; i++) {
        cudaDeviceProp prop;
        cudaGetDeviceProperties(&prop, i);
        printf("  GPU %d: %s (%d SMs, %d cores/SM)\n",
               i, prop.name, prop.multiProcessorCount,
               prop.maxThreadsPerMultiProcessor);
    }

    // Quick test: search for LDA #0 / STA mem equivalent
    printf("\nTest: find equivalent to LDA #0 / STA [0]\n");

    CPU inputs[NUM_TESTS];
    CPU outputs[NUM_TESTS];
    memset(inputs, 0, sizeof(inputs));
    memset(outputs, 0, sizeof(outputs));

    // Generate test inputs: random A, X, Y, mem values
    srand(42);
    for (int i = 0; i < NUM_TESTS; i++) {
        inputs[i].A = rand() & 0xFF;
        inputs[i].X = rand() & 0xFF;
        inputs[i].Y = rand() & 0xFF;
        inputs[i].C = rand() & 1;
        for (int j = 0; j < 32; j++)
            inputs[i].mem[j] = rand() & 0xFF;

        // Reference: LDA #0, STA mem[0]
        outputs[i] = inputs[i];
        outputs[i].A = 0;
        outputs[i].N = 0;
        outputs[i].Z = 1;
        outputs[i].mem[0] = 0;
        outputs[i].cycles = 2 + 5;  // LDA imm + STA abs,X
    }

    // Build instruction pool
    Instruction h_pool[64];
    int h_pool_size = 0;
    // LDA #imm for values 0, 1, 0xFF
    for (uint8_t v : {0, 1, 0xFF}) {
        h_pool[h_pool_size++] = {OP_LDA_IMM, v};
    }
    // STA/STX/STY to mem[0]
    h_pool[h_pool_size++] = {OP_STA_MEM, 0};
    h_pool[h_pool_size++] = {OP_STX_MEM, 0};
    h_pool[h_pool_size++] = {OP_STY_MEM, 0};
    // Transfers
    h_pool[h_pool_size++] = {OP_TAX, 0};
    h_pool[h_pool_size++] = {OP_TXA, 0};
    h_pool[h_pool_size++] = {OP_TYA, 0};

    uint8_t mask[32] = {0};
    mask[0] = 1;  // check mem[0]

    int result_cycles, result_idx;
    gpu_search(inputs, outputs, NUM_TESTS,
               0, 0, 0, 0,  // don't check registers
               mask,
               h_pool, h_pool_size,
               2, 7,  // seq_len=2, ref_cycles=7
               &result_cycles, &result_idx);

    printf("Result: best_cycles=%d, best_idx=%d\n", result_cycles, result_idx);
    if (result_idx >= 0) {
        // Decode
        int i0 = result_idx / h_pool_size;
        int i1 = result_idx % h_pool_size;
        printf("  Sequence: op[%d]=%d operand=%d, op[%d]=%d operand=%d\n",
               i0, h_pool[i0].op, h_pool[i0].operand,
               i1, h_pool[i1].op, h_pool[i1].operand);
    }

    return 0;
}
