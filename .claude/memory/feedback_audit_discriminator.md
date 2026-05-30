---
name: feedback_audit_discriminator
description: "For per-instrument audits, use a unique fx_flags value (or other unique signature) as the discriminator — never ADSR alone. Multiple instruments can share AD/SR."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

When running [[reference_audit_tool]] to audit a specific
instrument's effects, the choice of *discriminator* (the byte that
tells you "this is the inst you want, not its lookalike") matters.

**Use as discriminator:**
- The engine's fx_flags cache write (e.g. HR's `$0DE0`) — unique per
  instrument by construction if the engines's fx layout is sane.
- Direct probe of `v_instr,x` (HR: `$0DB9,x`) — captures the inst
  index directly.

**Avoid as discriminator:**
- ADSR alone — multiple instruments often share `(ad, sr)` values.
  Hubbard reuses ADSR patterns across instruments that differ only
  in waveform / fx_flags.
- pw_lo / pw_hi alone — often shared between instruments.

**The slip:** during the HR skydive audit I matched on `V.sr=$9A`
in subtune 1 and got many hits. They were all *inst 8*
(drumarp+downslide+PWmode), not the inst 21 (skydive+PWmode only)
I wanted. Both insts have `ad=$0A, sr=$9A` — identical ADSR. I had
to switch to watching writes to `$0DE0` (HR's fx_flags cache) for
the specific value `$0A` to find inst 21's frames.

**How to apply:** before running an audit, derive a discriminator
that's *guaranteed unique* to the target instrument across all
instruments in the corpus. Confirm uniqueness by listing all insts
that match the proposed discriminator value — if more than one
inst matches, refine the discriminator.

Related: [[project_human_race_audit]] records the specific HR
audit results; [[reference_audit_tool]] is the audit tooling.
