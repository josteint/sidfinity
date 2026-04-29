# Das Model Assumption Audit — Commando.sid

**Date:** 2026-04-29  
**Method:** py65 step-tracing both the original Hubbard binary and the Das Model output,
comparing SID register writes frame-by-frame.  
**Scope:** All 6 claims from the session plan, verified with precise frame numbers.

---

## CLAIM 1: "ADSR is 100% correct"

**Status: PARTIALLY WRONG — gate-off fires 1 frame late.**

### Hubbard hard restart sequence (verified by trace)

Hubbard uses a note counter `$54F2,X` (one per voice) that is decremented once per
tempo tick (every 3 frames for Commando). The hard restart code at `$5174` runs only
on tick frames. When `$54F2,X == 0`:

1. Gate is cleared: `LDA $54F8,X / AND #$FE / STA $D404,Y` (ctrl with gate bit 0)
2. ADSR zeroed: `LDA #$00 / STA $D405,Y / STA $D406,Y`

Both happen on the **same tick frame** when the counter reaches zero.

### Das Model gate-off timing

Das Model translates `note_duration` to `tick_ctr = (dur+1) * tempo` and then:

- ADSR zero when `tick_ctr == tempo` (= 3 for Commando)  
- Gate-off when `tick_ctr < tempo` (= tick_ctr in {2, 1, 0})

For a 1-tick note (`tick_ctr` starts at 6):

| Frame | Hubbard               | Das Model             |
|-------|-----------------------|-----------------------|
| 0     | note loads, gate ON   | note loads, gate ON   |
| 1     | gate ON               | gate ON               |
| 2     | gate ON               | gate ON               |
| 3     | ADSR zero, gate OFF   | ADSR zero, gate STILL ON ← BUG |
| 4     | gate still off        | gate finally OFF      |
| 5     | gate still off        | gate OFF              |
| 6     | new note loads        | new note loads        |

**The gate-off is exactly 1 frame late** — on the ADSR-zero frame, Hubbard writes
`ctrl & $FE` (gate 0), but Das Model's `bcs v{v}gon` branch keeps gate on because
`tick_ctr == 3 >= 3` passes the `bcs`.

### Fix

Change the gate-off condition from `tick_ctr < 3` to `tick_ctr <= 3` (i.e., from
`CMP #3 / BCS gate_on` to `CMP #4 / BCS gate_on`). ADSR zero at `tick_ctr == 3`
and gate-off at `tick_ctr == 3` can then fire together, matching Hubbard.

### Observed impact

3 gate-only mismatches in 500 frames for V2 (fr168, fr288, fr360). Das Model has
`ctrl=41` (gate on) while original has `ctrl=40` (gate off).

---

## CLAIM 2: "V3 freq is 100% correct"

**Status: VERIFIED TRUE.**

Measured across 1500 frames: V3 `freq_hi` wrong = **0/1500 (0.0%)**.

---

## CLAIM 3: "Speed counter is equivalent to multiplying by tempo"

**Status: VERIFIED TRUE.**

Hubbard's `DEC $54F2,X` fires once per tempo-tick (every 3 frames). The note counter
decrements from `N` to `N-1, ..., 0, -1` = `N+1` total decrements before new note loads.
Das Model formula `tick_ctr = (dur+1) * tempo` (where `dur = note.duration` from decompiler,
and `note.duration = b0 & 0x1F` matches Hubbard's raw counter) produces the same frame count.

The speed counter gates the note decrement globally for all voices — all voices advance
on the same tick frame. Das Model's per-frame independent decrement per voice is equivalent
because all voices are processed with the same tempo.

No edge cases found at pattern boundaries or first-note initialization.

---

## CLAIM 4: "Tie notes are handled correctly"

**Status: WRONG — TIE notes retrigger gate.**

### Hubbard TIE behavior (disassembly-verified)

At `$50CF`: `BIT $5502 / BVS $5118` — checks bit 6 (the TIE flag) of the raw pattern byte.

For TIE notes, Hubbard jumps to `$5118` which executes `DEC $5501`. The variable `$5501`
is a gate mask initialized to `$FF` (all bits pass). After `DEC`: `$5501 = $FE`.

Later at `$5136`: `AND $5501` — the instrument `ctrl` byte is AND'd with `$FE = 11111110b`,
forcibly clearing the gate bit. Result: **gate stays OFF** for TIE notes.

TIE behavior:
1. Gate is NOT retriggered (gate mask clears bit 0)
2. PW is reloaded from instrument table (`$5140/$5144`)
3. ADSR is reloaded (`$514B/$5151`)
4. Freq is NOT updated (TIE continues previous pitch)

### Das Model TIE behavior

`extract()` creates a **separate note entry** with the previous pitch. This note goes
through the full note-load code path, which:

1. Restarts the W program pointer to step 0 (= `ctrl | 0x01` = gate ON)
2. Triggers gate-on via the W program
3. Reloads ADSR

The W program step 0 write on TIE notes causes gate retrigger — this is wrong.

### Known trade-off

The session notes mention merging ties into the previous note's duration drops ADSR
accuracy from 99.6% to 98.8% (single hard restart vs per-segment restarts). The current
code does NOT merge — ties create separate entries and retrigger the gate.

---

## CLAIM 5: "W program loop behavior matches"

**Status: VERIFIED TRUE for drum instruments.**

Drum W program `[$15, $80, $80, $14]` with loop at step 3 produces the exact ctrl sequence:

| Frame (relative to note-load) | Hubbard ctrl | Das Model ctrl |
|-------------------------------|--------------|----------------|
| 0 (note load)                 | `$15`        | `$15` ✓        |
| 1                             | `$80`        | `$80` ✓        |
| 2                             | `$80`        | `$80` ✓        |
| 3+ (loop at step 3)           | `$14`        | `$14` ✓        |

W program advances every frame (not every tick). Das Model `inc w_ptr` in the eval
section executes every frame, matching Hubbard's per-frame waveform updates.

---

## CLAIM 5 ADDENDUM: Drum sequence fires for silent notes — BUG

**Status: BUG FOUND.**

### Root cause

Hubbard conditions the drum sequence on `$551A,X != 0`. This variable is set to `freq_hi`
of the note pitch during note-load. For **silent notes** (pitch=0, `freq_hi=0`), `$551A,X`
stays 0 and the drum sequence is skipped (`BEQ $5336`).

Code path: `$5301: LDA $551A,X / $5304: BEQ -> $5336` (skip if zero = silent note).

### Das Model bug

Das Model creates the drum W program `[$15,$80,$80,$14]` for ANY instrument with
`has_drum=True`, regardless of the note's pitch. For silent notes (pitch=0), the
W program still fires `$80` at steps 1 and 2.

### Evidence

- V2 first note at frame 0: `freq=0` (silent), `$551A[1]=0` → Hubbard skips drum → V2 stays `$43`
- Das Model: V2 W program step 1 fires → writes `$80` at fr1, fr2
- Observed mismatches: **fr1 V2 orig=`43` das=`80`, fr2 V2 orig=`43` das=`80`**

- V2 note at frame 6: `freq_hi=$43` (nonzero) → Hubbard fires drum → `$80` at fr7, fr8 ✓
- Das Model: `$80` at fr7, fr8 ✓ (correct for nonzero freq notes)

### Fix

In `extract()` (or `generate_asm()`): before using the drum W program `[$15,$80,$80,$14]`,
check whether `freq_hi(note.pitch) == 0`. If so, use the non-drum W program `[ctrl|0x01]`.
The condition must be per-note, not per-instrument.

---

## CLAIM 6: "Notes are processed in the right order within each pattern"

**Status: PLAUSIBLY CORRECT.**

`decode_pattern()` correctly handles variable-length Hubbard records (1, 2, or 3 bytes)
for TIE vs non-TIE, with/without modifier byte. The decompiler produces separate note
entries in sequential order. `extract()` converts these to 3-byte fixed records.

No ordering discrepancy was found. The pattern byte offset tracking (`hub_off`) is
a separate mechanism for T[100] extended freq table; it is not related to note ordering.

---

## Summary

| Claim | Status | Impact |
|-------|--------|--------|
| ADSR 100% correct | **WRONG** — gate-off 1 frame late | 3 gate mismatches / 500 frames |
| V3 freq 100% all frames | **VERIFIED** | 0/1500 frames wrong |
| Speed counter = multiply | **VERIFIED** | exact frame counts match |
| TIE notes correct | **WRONG** — gate retrigger | unknown % but real |
| W program loop | **VERIFIED** for drums | 0 drum waveform errors |
| Drum on silent notes | **BUG** (not in original claims) | 2 waveform mismatches / 500 frames |
| Note ordering | **PLAUSIBLY CORRECT** | no discrepancy found |

### Prioritized fixes

1. **Drum silent note bug (BUG A):** Per-note check `freq_hi == 0` → use non-drum W program.
   2 mismatches per silent drum note, easily reproducible.

2. **Gate-off 1-frame delay (BUG B):** Change `CMP #3 / BCS gate_on` to `CMP #4 / BCS gate_on`
   in `generate_asm()`. Affects all non-drum voices at note boundaries.

3. **TIE gate retrigger (CLAIM 4):** TIE notes must not reset W program to step 0.
   Requires new note type in Das Model (or merging tie duration into previous note
   and tracking gate separately).
