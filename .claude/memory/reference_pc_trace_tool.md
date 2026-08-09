---
name: pc-trace-tool
description: "tools/siddump --pc-trace FILE START END dumps libsidplayfp CPU PC trace. Use when a SID misbehaves in sidplayfp but py65/writelog can't see where the CPU actually goes."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`tools/siddump --pc-trace OUTFILE START_FRAME END_FRAME` writes the
full libsidplayfp CPU debug trace (PC, registers, opcode, disasm) for
absolute frames in [START, END). The file has one block per instruction
fetched.

Added in commit 1b68da3 to diagnose the Chimera digi `$B093` phantom-
ping bug — what made the diagnosis possible.

## When to use

- A SID plays wrong in sidplayfp (or siddump) but py65 + writelog show
  the expected register stream. py65 is frame-granular and can't see
  intra-frame PC drift; the writelog only sees SID writes, not where
  the CPU is when it makes them.
- Suspected stack corruption, RTI/RTS landing somewhere unexpected,
  CPU walking through data area, BRK-walks, or IRQ vector mis-routing.
- Anything that says "the dispatcher init seemed to run twice".

## How to read the output

Each fetched instruction is one record:

```
PC  I  A  X  Y  SP  DR PR NV-BDIZC  Instruction
b1c1 f 37 f0 00 01fa 2f 37 00110101  00        BRK
```

- `PC` — program counter (where the opcode was fetched FROM, i.e.
  reflects current banking $01 = PR column)
- `I` — IRQ asserted pin
- `A X Y` — registers
- `SP` — full $0100 + sp
- `DR` — $00 (data direction register)
- `PR` — $01 (banking byte) — **critical**: tells you whether ROM or
  RAM was visible at PC at fetch time
- Then status bits and the actual byte fetched + disasm

Look for `JMPi (xxxx) [yyyy]` to see indirect jumps resolve. RTI lines
are followed by a separator (`****`) and the next PC = what RTI popped
from stack (very useful to find "where did I return to").

## How to find absolute frame number

Writelog filters out silent frames, so writelog_capture frame N ≠
absolute siddump frame N. Run a `--writelog --raw` pass and count
SID-write occurrences in the raw siddump output (one line per absolute
frame, optional `|W:` only on frames with writes); locate your phenomenon,
then trace that window with `--pc-trace`.

## Quick example

```
tools/siddump hvsc85/MUSICIANS/H/Hubbard_Rob/Chimera.sid --subtune 4 \
    --duration 10 --writelog --raw --pc-trace tmp/pc.txt 155 157
grep -n "9f80" tmp/pc.txt | head    # find init re-entry
grep -nE "^03[0-9a-f][0-9a-f] " tmp/pc.txt | head  # find PC drift
```

Related: [[reference_audit_tool]] (PC-traced per-voice SID-write
capture) and [[feedback_writelog_divergence_recipe]].
