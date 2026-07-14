---
name: project-usf-instrument-ml-target
description: "Punch list for the phase-5 instrument representation refactor. Current instrument schema (post principled-instrument refactor) is engine-neutral but still carries packed register bytes, engine-fixed values per-instrument, and raw values alongside derived musical forms. Six concrete improvements identified during the 2026-06-02 Chimera walkthrough."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5de7672a-c130-4ad2-aabb-e29393a10065
---

The instrument schema reached "engine-neutral typed config" on 2026-06-01 via [[project-principled-instrument-refactor]] (5 per-engine-bookkeeping leaks removed). The next step — ML-target representation — is deferred to phase 5 of [[project-migration-sequence]]. This memory is the concrete punch list so phase 5 has something specific to act on.

Reference example throughout — Chimera's instrument 1 in current form:

```
instrument 1 {
  waveform: $41
  loop:     0
  pwm:      mode=linear speed=4 init=$0742 min_hi=8 max_hi=14 lo_or_mask=$40
  adsr:     $69 $86
  arp:      offsets=[0] period=8
  vibrato:  scale=2 onset=8 depth_semitones=0.375
  envelope: release_ctrl=$40
}
```

### Six opportunities, ranked roughly by ML impact

**1. Unpack `waveform: $41` into named binary features.**
The byte encodes 4 independent waveform-select bits + 3 modulation flags + gate (always 1 in an instrument). Replace with `waveform: pulse` (or whichever combination is on) with absent bits meaning off. Gate becomes implicit. **High impact — waveform is the single most semantically loaded byte.**

**2. Unpack `adsr: $69 $86` into named fields, dual-form like vibrato.**
Hex nibbles are anti-ML. Target form:
```
adsr: attack=6 decay=9 sustain=8 release=6
      attack_ms=24 decay_ms=750 sustain_level=0.53 release_ms=114
```
Composer reads raw nibbles; ML reads descriptive form. Same pattern `vibrato.depth_semitones` already follows. ADSR ladder is non-linear — derivation tables already exist in the SID datasheet; need to wire them into to_usf and a build-time inverse.

**3. PWM raw register values → musical units.**
`pwm: init=$0742` → `pwm: initial_duty=0.454` (45.4% duty cycle). `speed=4` could keep its raw integer (it's already a per-frame increment, semantically meaningful), or pair with `speed_per_second` derived. Composer derives raw values at build time.

**4. Hoist engine-fixed values out of per-instrument config.**
`pwm: min_hi=8 max_hi=14 lo_or_mask=$40` are HARDCODED Hubbard '85 values per [[reference-hubbard-pwm-bounds]]. They appear identically in every linear-PWM instrument in every Hubbard '85 tune — zero variance, pure noise to ML. Move to `engine_constants.py`; when `pwm: mode=linear`, the engine_constants lookup provides the bounds.

**5. Default-elide no-op blocks.**
`arp: offsets=[0] period=8` is "no arp animation" — should be absent. `vibrato: scale=0` is "no vibrato" — should be absent. Run-length-compress repeated arp offsets: `[0, 12, 12, 12, 12, 12, 12, 12]` → `[0, 12*7]` or equivalent. Aligns with [[project-usf-ml-optimality]] default-elision principle.

**6. Rename register encodings to musical concepts.**
`envelope: release_ctrl=$40` → `envelope: silence_on_release=true`. The `$40` byte (test bit + no waveform) is just the register-level encoding of a binary musical choice. Same shape may apply to other register-byte fields if any survived the principled-instrument refactor.

### Tension to resolve during phase 5

Some raw values are load-bearing for byte-exact rebuild — the composer needs `scale=2`, not just `depth_semitones=0.375`, to emit the exact same engine bytes. Two design options:

- **Derive at build time.** Composer computes raw from descriptive via inverse functions. Cleanest, aligns with [[feedback-schema-addition-discipline]] (don't carry derivable data). Works when the inverse is unique and round-trip-stable.
- **Split into `musical` + `build` sub-blocks.** USF carries both views explicitly. ML reads `musical`; composer reads `build`. Safer for non-injective parameters but heavier format.

Phase 5 will need to pick one, possibly per-field. ADSR is the trickiest case because the SID's envelope ladder is non-linear and quantized.

### Why this fits at phase 5

Touches **every engine**, not just Hubbard '85 — bigger blast radius than the phase 4 spillover refactor. Sequenced after phase 4 so the slimming methodology is validated on a bounded scope first. See [[project-migration-sequence]] for the full ordering and timing rationale.

**How to apply:** Don't propose any of these changes mid-migration (phases 1-3). When phase 5 begins, this punch list is the starting point — but it's not exhaustive; the migration will surface more opportunities as new engines reveal more instrument variation. Revisit and extend.
