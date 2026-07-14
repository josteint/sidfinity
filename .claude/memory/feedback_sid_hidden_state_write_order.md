---
name: feedback_sid_hidden_state_write_order
description: TRIPWIRE — within-frame SID write ORDER matters audibly. Multiset-equal frames are NOT a safe verification verdict. Per-voice register write order must be parameterised per engine; the comparator must remain cycle-ordered (init-skipping).
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

**This memory operationalises Mode 1's within-frame ORDER constraint.**
See [[feedback_verification_modes]] for the full framing — Mode 1 says
per-`play()` write sequences must match frame by frame; cycle position
WITHIN a frame is observation, but ORDER within a frame is signal.

When rebuilding a SID through USF, the within-frame ORDER of writes to
the SID chip is audibly significant — not only the multiset. Multiset
equality is **not** a safe correctness criterion. Verification must
stay cycle-ordered (the existing `compare_instruction_stream` is fine
because it preserves per-frame order; only its CYCLE TIMESTAMPS are
relaxed for music).

**Why:** the 6581/8580 carries hidden state that observes writes in
order:

- Per-voice gate bit ($D404/$D40B/$D412 bit 0): a 0→1 edge starts
  attack, a 1→0 starts release. Two writes in different order = two
  envelope events vs zero events.
- Test bit (bit 3 of ctrl): rising edge resets phase accumulator AND
  noise LFSR; sequence "test→clear→note" is the canonical hard-restart.
- ADSR delay bug: writing AD/SR while envelope is active can stall the
  counter for thousands of cycles; whether the gate write happens before
  or after the AD/SR write determines whether the bug triggers.
- $D418 master vol clicks: changing the volume between two waveform
  writes injects an audible click that you can hear in production tunes
  (sample-playback engines deliberately exploit this).

**How to apply:** Every engine in `pipelines/<family>/` declares its
nextvoice write order on its config (e.g. FCConfig's
`nextvoice_write_order: tuple = (4, 0, 1, 2, 3)` — meaning ctrl, freq
lo, freq hi, pw lo, pw hi). The composer's `_emit_nextvoice_writes`
emits the asm chunks in that order. When migrating a new engine,
disassemble its nextvoice (or its functional equivalent) and add its
order to the per-tune config. **Do not** relax the comparator to
multiset to "fix" a divergence — that hides the real bug. See
[[project_hawkeye_writelog_progress]] for the Hawkeye case study (match
count 55 → 88 once the order was made per-cfg).

For digi, the cycle-strict comparator (`compare_strict`) stays in
force; this guidance only relaxes WHEN within the frame, not the order.
