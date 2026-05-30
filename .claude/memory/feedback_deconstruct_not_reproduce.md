---
name: feedback_deconstruct_not_reproduce
description: "Reproduce the exact instruction stream via straightforward clean code. The \"trick\" to avoid is Hubbard's space-saving implementation MECHANISM, not the output."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

When a Hubbard instrument's behaviour involves a space-saving
implementation trick (a 96-entry freq table the octave arpeggio reads
off the end of; an `ADC` with no preceding `CLC` that inherits stray
6502 carry), the trick is the *how*, not the *what*.

The instruction stream — the SID register writes, instruction by
instruction (register, value, order) — is deterministic and IS the
target. Reproduce it exactly.

- Do NOT reproduce the trick's *mechanism* (the table/state overlap,
  the missing CLC).
- DO reproduce the trick's *output* — write straightforward clean code
  that computes the identical values. This is always possible because
  the stream is deterministic.

The trick affects HOW the original was implemented, never WHAT it
outputs. Clean code can always produce the same WHAT without the HOW.

**Don't dismiss odd behaviour as "garbage to discard."** Investigate
first: confirm what it actually reads, confirm whether it is audible.
Only an effect that is both unintentional AND inaudible can be dropped.
The user's ear is the final judge.

Example (Commando inst 7, 2026-05-20): its octave arpeggio does
`freq_table[pitch+12]`; at pitch 88 that runs past the 96-entry table
into `$54F0/$54F1` = voices 1 & 2's note-index bytes, written as a
"frequency." CONFIRMED by py65 trace. It is audible (toggles voice 0
between ~2.6 kHz and ~50-240 Hz every frame) and is part of Commando as
shipped. The clean implementation does not overlap a table with state —
it explicitly reads the other voices' note indices and writes them as
freq. Same stream, no trick. inst 7 is therefore a genuinely
cross-voice-coupled instrument; that is fine, the USF2 schema has
`otherVoice*` references for exactly this.
