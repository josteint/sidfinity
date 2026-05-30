---
name: feedback_migration_as_stress_test
description: "Migrating a new engine is the most reliable way to surface hardcoded assumptions in the shared core. Treat the first divergence as a probe, not just a bug."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

The biggest payoff of migrating Human Race wasn't HR itself — it was
the bugs HR surfaced in the shared core that had been "right by
coincidence" for the first 5 engines:

| latent bug | broke when |
|---|---|
| `cmp #$03` dispatch threshold hardcoded | HR has 5 music subtunes (3+) → dispatched to SFX init |
| `linear_pw_or` defaulted to 0 | HR linear PWM ORs $40 (no engine had touched this) |
| PSID `speed` field hardcoded to $00 | HR's original is $0F (multispeed) |
| `seed_overlap` not propagated from USF | HR has `seed_overlap=False` (no other engine did) |
| `build_statebuf` Commando-specific layout | HR's state region has different offsets |
| Empty orderlist not handled in USF grammar | HR's V3 is silent across all 5 subtunes |

Each was a quiet "the first 5 engines happen to share this default"
assumption. The first 5 engines had ≤3 music subtunes, default
`linear_pw_or=0`, `speed=$00`, `seed_overlap=True`, Commando-style
state region, and at least one note per voice per subtune.

**Why:** new engines have different *boundary values* on assumptions
that the codebase silently encodes. Migrating them isn't just "add
support for another tune" — it's the cheapest fuzzer we have.

**How to apply:**
1. When you start a new engine migration and hit a verify_all
   failure, don't assume the bug is in the new engine's data. Check
   first whether the shared core has hardcoded a value or skipped
   propagating a config that the new engine needs to differ from.
2. When the migration surfaces a hidden assumption, fix it
   *parametrically* (add an `EngineConfig` field, generalise the
   relevant codegen line) — not by patching the new engine to match
   the shared core's hardcode. Each fix raises the floor for the
   next engine.
3. The list of "things to suspect" when a new engine fails:
   - Hardcoded subtune counts / dispatch thresholds
   - Hardcoded PSID header fields (speed, flags)
   - Hardcoded state-region layout (`build_statebuf`)
   - Codegen knobs that don't flow through USF params

**Related:** [[reference_audit_tool]] for verifying the bug class
once suspected. [[feedback_py65_misses_dispatch_bugs]] for the
class of bugs verify_all can't see.
