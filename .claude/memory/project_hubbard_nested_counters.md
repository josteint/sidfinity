---
name: Hubbard nested speed counter analysis
description: Root cause of 28+ F-grade songs — nested DEC/BPL speed counters cause wrong tempo. Outer values 3-11 actively affect timing.
type: project
---

**28 songs have active nested speed counters (outer value <= 15).**

The Hubbard driver has two DEC/BPL counters:
- Inner: `DEC inner_ctr / BPL inner_target / LDA resetspd / STA inner_ctr`
- Outer: `DEC outer_ctr / BPL → inner / LDA #outer_val / STA outer_ctr / JMP past_inner`

When outer fires, it **JMPs past** the inner DEC — skipping one inner tick. The note duration counter decrements on both inner AND outer tick events. This makes the effective frames-per-note different from `(D+1) * (inner_speed+1)`.

**find_speed detects the INNER counter speed**, which is correct for non-nested songs but wrong for nested ones. The outer counter's guard `<= 5` rejects most active nesting.

**Key groups:**
- outer=3, inner=1: 9 songs (ACE_II is Grade A, 8 are F)
- outer=4, inner=1: 4 songs (all F)
- outer=8, inner=1: 3 songs (W_A_R etc)
- outer=11, inner=1: 7 songs (After_8, Mr_Meaner, etc — worst scores)

**Why ACE_II (outer=3) works but others don't:** Phase alignment (±15 frame cross-correlation) catches the small drift for outer=3. Larger outer values cause more drift than the alignment window can absorb.

**Fix needed:** Either:
1. Run the actual player for ~50 frames and measure the true tick rate empirically
2. Model the nested counter interaction: effective_tick_rate = f(outer, inner)
3. Add outer counter value to RHDecompiled and let rh_to_usf adjust durations

**C=Hacking disassembly confirmed:** The standard formula `(D+1) * (speed+1)` is correct for single-counter variants. The disassembly is from Monty on the Run which has no active outer counter.
