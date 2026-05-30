---
name: Hubbard notenum / freq table overlap
description: Hubbard's early player stores notenum INSIDE the freq table region, causing cross-voice coupling that breaks naive extract→rebuild
type: project
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
In Rob Hubbard's early player (Monty on the Run, Commando, etc. — first
~30 SIDs), the `notenum` byte triplet for V1/V2/V3 lives INSIDE the
note-frequency table — specifically at offsets that coincide with the
LO and HI bytes of pitches 105-106.

**Concrete example (Monty):**
  - Freq table base: $8400
  - Pitch 104: $84D0/$84D1 = $41/$41
  - Pitch 105: $84D2/$84D3
  - Pitch 106: $84D4/$84D5
  - `notenum !by $00,$00,$00` lives at $84D3/$84D4/$84D5

So `notenum[V1]` IS `freq_table[105].hi`. When the player executes
`sta notenum,x` during note-load, it overwrites part of the freq
table. Then when V2's vibrato reads `notefreqsh+2,y` for pitch 104
(`y=$D0`), it reads `mem[$84D3]` — which is V1's current notenum
byte, NOT a frequency!

**Why this matters:** vibrato for V2 with notenum=104 computes
`delta_hi = mem[$84D3] - mem[$84D1] = (V1 notenum) - $41`. The
runtime delta_hi varies based on V1's note. The audible result is
that V2's vibrato output couples to V1's pitch.

This means a "static freq table" extraction (which is what our
das_model_gen / discover.py produce) is FUNDAMENTALLY INCOMPLETE
for Hubbard SIDs that use pitches near where notenum lives. V2's
freq for note 104 will mismatch the orig unless our codegen
replicates the overlap: voice-N's notenum must live at the same
offset within our freq table.

**How to apply:** When ground-truth byte-matching Hubbard SIDs:

1. The extracted freq table beyond ~pitch 96 may contain values that
   are actually runtime scratch storage. Don't trust them as
   frequencies for vibrato.
2. To get byte-perfect rebuild, the codegen's notenum storage must
   alias into the freq table at the same offsets as the original.
3. Songs that only use pitches 0-95 won't hit this; only "out-of-range"
   pitch values (like Monty's pitch 104 = $4141 used as a special
   percussion-ish tone) trigger the cross-coupling.

**Concrete impact (2026-05-11):** V2 freq_hi divergence of 134 frames
out of 1500 in the Monty rebuild traces back here. With static freq
table, our V2 vibrato delta_hi is $05 (computed from extracted
($41,$46)) while orig's delta_hi was $15 (= V1 notenum $56 - $41).
