---
name: project-usf-ml-optimality
description: "USF design goal includes ML-training optimality alongside round-trip fidelity; schema slimming (default elision, zero-state dedup, per-voice → params hoisting) is the endgame activity once HVSC→USF coverage is complete, NOT to be done piecemeal mid-migration."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 5de7672a-c130-4ad2-aabb-e29393a10065
---

USF is being designed for two simultaneous goals:

1. **Round-trip fidelity** — byte-exact rebuild of the original SID. The non-negotiable foundation.
2. **ML-training optimality** — less clutter, cleaner signal. The format should make the *musical* content prominent and the *structural noise* minimal, so a model learns notes/instruments/effects rather than schema boilerplate.

Concrete slimming opportunities the user is already thinking about:

- **Default elision.** USF should adopt "absent = schema default" so e.g. Bowden init voices stop emitting `dur_field: $00  pwm_period: $00  pwm_dir: up  slide_v: $00` — all zero/default. Less noise per record. Chimera's empty `init { }` is the limit case of this rule applied correctly.
- **Hoisting engine-wide constants up to `params`.** E.g. if every Bowden voice starts with `ctrl: $40`, that's an engine-wide startup posture, not per-voice authorial state. It belongs at `params` level (one declaration) not repeated three times in init.
- **(Adjacent, not the same)** Shared structural data like Hubbard's PAL freq_table currently inlines into every Hubbard '85 USF — open question whether ML training should see that as duplicated content or shared/dedup'd via an engine-constants reference. Different design space, worth raising at the same time.

**Why:** The user wants USF to be the ML training corpus, not just a verification artifact. Clutter dilutes the signal — every default-valued field is a token the model has to learn to ignore. Less clutter = better attention budget on actual musical structure.

**How to apply:** Do NOT propose schema slimming mid-migration. The HVSC→USF conversion needs the regression set (~89 subtunes byte-exact today) stable to detect rebuild errors. Slimming the schema while migrating new engines would couple two unrelated risks. The natural moment is "when this big first stage of the project nears completion: converting HVSC to USF" (user, 2026-06-02). Until then: note slimming opportunities as they come up but don't act on them. Adjacent: [[reference_tokenization]] — tokenization is a separate downstream concern; this memory is about the USF format itself before tokenization.
