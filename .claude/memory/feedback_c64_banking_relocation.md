---
name: c64-banking-relocation
description: "When relocating C64 code into $A000-$BFFF, audit every sta $01 inside that code: a banking flip happens on the very next fetch, and if that fetch is also in the banked range, it reads ROM instead of your RAM."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

When relocating a routine into the $A000-$BFFF range (BASIC-ROM
banked region) — e.g. moving a player from $C000 to $B093 to recover
zero-padding — audit **every** `sta $01` inside that routine. The
6510 banking flip takes effect on the very next instruction fetch. If
that next fetch is also in $A000-$BFFF, it reads BASIC ROM, not the
bytes you wrote.

**Why:** The exact bug we hit (Chimera digi player, 2026-05-27): the
cleanup did `lda #$03 ; ora $01 ; sta $01 ; rts`. At `player_base =
$C000` (always RAM) it worked. At `player_base = $B093` (BASIC-banked
under $37), the RTS at $B19B was *fetched from BASIC ROM* — not our
$60 RTS in RAM. The CPU executed BASIC ROM bytes, walked through the
driver data area, and re-entered the dispatcher init, producing a
phantom ping at ~3.1s. First "fix attempt" (commit 7c0abd7) moved the
restore to *just before* RTS — same bug, one byte later. Real fix
(commit 1b68da3): don't restore banking inside the relocated routine
at all; let psiddrv (whose code is in $04xx, RAM under any banking)
do it.

The same trap exists in reverse — `lda #$36 ; sta $01` to map RAM
*in* over BASIC ROM is safe wherever it lives (you're switching to
RAM), but the moment you switch back you must be outside the banked
range.

**How to apply:**
- Before relocating any code into $A000-$BFFF, list every `sta $01`
  inside it.
- If a `sta $01` flips $36→$37 (or $34→$35, $35→$37, etc — anything
  that maps BASIC or KERNAL back over RAM), confirm that EVERY
  subsequent instruction in that routine — including the RTS / JMP
  / branch target — lives outside the range the banking just hid.
- The only fully-safe option for in-RAM routines in $A000-$BFFF is
  to not write `$01` at all, and let the caller (whose code is
  outside the banked range — psiddrv's $04xx, or anything ≥ $C000)
  restore banking after RTS.

**Related:** [[reference_pc_trace_tool]] — the diagnostic that
revealed the BRK-walk chain when this triggered. Reach for it any
time you suspect "PC went somewhere wrong" — py65 and writelog can't
see this, only siddump's CPU debug stream can.

**Wider lesson:** when relocating ANY code in this project, audit
the new address range's hardware semantics (banking, I/O overlap,
KERNAL trap addresses like $A7AE BASIC warm-start). Don't just copy
patterns that worked at the old location — verify each pattern
remains valid under the new placement.
