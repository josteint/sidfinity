---
name: use-6502-programming-mindset
description: "All major bugs have been pointer/addressing errors — need flat memory mental model, not modern abstractions"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4994dfd8-7bf7-414e-a073-16595cdd2a38
---

Every major bug in this project's extraction/composition pipelines (from the GT2 era onward) has been a pointer/addressing error in flat memory layout. Modern programming abstractions (named fields, bounds-checked arrays, automatic alignment) don't exist on the 6502. Need to think like a 1980s programmer: exact byte positions, hand-verified address arithmetic, memory maps with explicit offsets.

**Why:** The user observed that the pervasive problem class is always "pointer problems" — wrong offsets, shifted tables, misidentified boundaries. This comes from treating data layout abstractly rather than tracking exact byte counts.

**How to apply:** When building or debugging 6502 data layouts:
1. Draw the memory map with exact byte addresses
2. Verify every label resolves to the expected byte
3. Don't approximate sizes — count bytes explicitly
4. When something goes wrong, dump the actual bytes at the addresses the code references
5. Think in terms of base+offset, not named fields
