---
name: Full decompile before working on a new Hubbard SID
description: Always do a full annotated 6502 disassembly of init+play before touching a new Hubbard pipeline. Reverse engineer first, code second.
type: feedback
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
When starting work on a new (or under-investigated) Hubbard SID, the first
step is a full annotated disassembly of the player's init + play routines,
like `pipelines/hubbard/commando/disassembly.s` does for Commando.

**Why:** Hubbard hand-tuned every game. Each SID has its own counter
machinery, init/play handoff, voice ordering, freq computation quirks.
Skipping the decompile means burning hours guessing what the player does
from siddump output. The disassembly is the source of truth; everything
else (extract, codegen, grade) flows from it.

**How to apply:** Before changing extract config or composer logic for a
new Hubbard pipeline, produce an annotated
`pipelines/hubbard/<engine>/disassembly.s` (seed it with
`tools/seed_disassembly.py`, then hand-annotate) covering at least
init + play + the per-voice exec routine. Use that document to drive
extract parameters and composer quirks.
