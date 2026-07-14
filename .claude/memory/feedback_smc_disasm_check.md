---
name: feedback_smc_disasm_check
description: "TRIPWIRE — before trusting a 6502 disasm at face value, scan for STA into instruction-operand bytes. SMC means the static disasm lies about runtime behavior. Anchoring on the static reading wastes sessions chasing the wrong conclusion."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

When reading a disassembly to understand engine logic, **scan for STA
into nearby code memory before trusting the static instruction
sequence**. Self-modifying code is canonical in 6502 engine work —
HVSC's Hubbard, Tel, and Bowden engines all patch operands at runtime.

The classic SMC pattern:
```
$XX_a: STA $XX_b      ; stores a computed value into $XX_b
...
$XX_b - 1: <opcode> ?? ; the byte at $XX_b is the operand of THIS instruction
```

When `$XX_b` is `(instr_address + 1)`, the STA is patching that
instruction's immediate operand. Common variants:
- `STA target+1` patches an `LDA #imm` / `CMP #imm` operand
- `STA target+1, STA target+2` patches a 16-bit `LDA $xxxx` / `JMP $xxxx`
- `LDA #imm / STA target+1` is the patching site

**Why:** the static disasm shows the LITERAL bytes. If those bytes are
patched at runtime, the disasm reading is wrong. I anchored on a
literal `CMP #$00` reading in Hawkeye's $7DE8 across three sessions,
concluding "BCS always taken" and writing that into RE_NOTES — which
was the wrong baseline. py65 step trace revealed the operand was
patched per-voice to $00/$08/$1E. The correct interpretation is
"threshold-based gate clear" — totally different semantics.

**How to apply:**
1. Before drawing conclusions from any disasm fragment, grep the
   surrounding ~50 lines for `STA $X` where `$X` falls within nearby
   code memory.
2. For each match, check whether the target is the operand of an
   instruction (i.e., `target = instr_addr + 1` or `+2`).
3. If yes, the disasm shows the INITIAL operand, not the running one.
   Use py65 trace to find what the operand becomes at runtime.
4. When emitting your own asm for the same effect, prefer ZP indirect
   pointers (`lda (ptr_lo),y`) over SMC — the [[project_composer_dissolution]]
   composer already uses this convention for fx_filter_prog and
   fx_pulse_prog. SMC is fine in the original engine; reproducing it
   isn't required.

**Cross-reference:** [[feedback_deconstruct_not_reproduce]] — reproduce
the exact instruction stream, but don't reproduce the SMC mechanism
itself. The trick to avoid is the SMC; the output is what matters.
