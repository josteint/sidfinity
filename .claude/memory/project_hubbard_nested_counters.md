---
name: hubbard-nested-speed-counter-analysis
description: Hubbard engine quirk — nested DEC/BPL speed counters change the effective tempo. Outer values 3-11 actively affect timing; a single-counter model gets frames-per-note wrong.
metadata: 
  node_type: memory
  type: project
  originSessionId: 4994dfd8-7bf7-414e-a073-16595cdd2a38
---

(Written in the GT2-grading era; the counter MECHANISM below is the
load-bearing part for any Hubbard extraction. ~28 HVSC Hubbard songs
have active nesting, outer value <= 15.)

The Hubbard driver has two DEC/BPL counters:
- Inner: `DEC inner_ctr / BPL inner_target / LDA resetspd / STA inner_ctr`
- Outer: `DEC outer_ctr / BPL → inner / LDA #outer_val / STA outer_ctr / JMP past_inner`

When outer fires, it **JMPs past** the inner DEC — skipping one inner tick. The note duration counter decrements on both inner AND outer tick events. This makes the effective frames-per-note different from `(D+1) * (inner_speed+1)`.

**find_speed detects the INNER counter speed**, which is correct for non-nested songs but wrong for nested ones. The outer counter's guard `<= 5` rejects most active nesting.

**Affected songs (GT2-era census):** outer=3 ×9 (ACE_II, ...), outer=4 ×4, outer=8 ×3 (W_A_R, ...), outer=11 ×7 (After_8, Mr_Meaner, ...).

**If this resurfaces in a byte-exact extraction:** model the nested
counter interaction exactly (or measure the true tick rate empirically
by running the player) — the single-counter formula silently gives the
wrong note durations for these songs. (The original "fix needed" list
referenced GT2-era code — RHDecompiled/rh_to_usf — now in deprecated/.)

**C=Hacking disassembly confirmed:** The standard formula `(D+1) * (speed+1)` is correct for single-counter variants. The disassembly is from Monty on the Run which has no active outer counter.
