---
name: usf-init-sid-block
description: "USF carries SID-chip priming as `init.sid { master_vol, filter, voice N { envelope_prime, pw_init } }`. Composer reads it; shape detection deleted. Bowden migrated as the proof case (2026-05-31)."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

## Current state

USF v3 grammar carries an `init.sid {}` sub-block for SID-chip
priming, separate from `init.voice {}` (engine-state priming /
voice runtime state, mostly Hubbard-shaped).

**Why:** the init trichotomy — see [[init-trichotomy]] — requires
typed musical-parameter fields for priming so the composer can
read them directly without engine-name dispatch or shape
detection.

**How to apply:** when migrating a new engine that writes SID
state during init, populate `init.sid` from the engine binary
during extract. The composer's `_emit_init` reads from USF and
emits the writes — no per-engine init code needed.

## Schema

```
init {
  sid {
    master_vol: $XX                           ; default $0F if omitted
    filter {
      cutoff_lo: $XX
      cutoff_hi: $XX
      res_routing: $XX
    }
    voice N {
      envelope_prime: ($ad, $sr)              ; writes $D405/$D406 etc.
      pw_init: $XXXX                          ; 16-bit pulse-width
    }
  }
  voice N { ... }                             ; engine-state priming
                                              ; (Hubbard's ctrl/dur_field/
                                              ;  pwm_period/pwm_dir/instr/
                                              ;  slide_v fields)
}
```

All fields optional; missing = "don't prime this slot." The
composer's universal init does silence-clear + `$D418=$0F`
baseline, then layers on priming from USF.

## Implementation

- `src/usf/types.py` — `InitSid`, `InitSidVoice`, `InitFilter`
  dataclasses; `InitState` gains `sid: Optional[InitSid]`.
- `src/usf/grammar.lark` — `init_block` accepts mix of `init_voice`
  and `init_sid_block`.
- `src/usf/parser.py` / `writer.py` — handlers.
- `pipelines/engine_model.py` — `_init_sid_writes_for_engine(usf)`
  reads from `usf.init.sid`, expands into flat `(reg, val)` list
  the composer's `_emit_init` iterates over.
- `pipelines/composer.py` — `_emit_init` reads
  `model.init_sid_writes` and emits a `lda #$XX / sta $d4XX`
  pair per entry, after the silence-clear loop + master-vol baseline.

## Migration done

Bowden engine (Berry_Vic ×10 + Melonmania ×1):
- Extract path
  `pipelines/companion/bowden_canonical/extract/to_usf.py`
  reads from `BOWDEN_INIT_SID_WRITES` (engine_constants) and
  emits `init.sid.voice 1.envelope_prime: ($09, $00)` +
  `voice 2.envelope_prime: ($09, $00)` per the engine binary's
  init at `$C064-$C075`.
- All Bowden USFs regenerated with `init.sid` populated.
- Shape-detection fallback in `engine_model._init_sid_writes_for_engine`
  DELETED — no more "if carry_leak quirk present, inject Bowden's
  primes" inference. The composer reads USF directly.

Verified: Bach_Sonata + Atonal_Music + … + Melonmania (all 3 subs)
instruction-sequence exact (`match_all = full`) via the new init.sid path.
Melonmania sub 1's previously-known partial (a carry-leak from the
synthetic `[$81,$FF]` orderlist for V1) was later resolved by the
per-subtune `voice_enable_mask` USF param — see
[[project_bowden_canonical]].

## What's left

- **Universal-reset composer init**: currently the composer's
  `_emit_init` does silence-clear + `$D418=$0F` + per-voice
  timbre fills + orderlist setup. Eventually it could become
  truly universal (just reset + USF priming + voice_state
  setup), enabling structurally-different init bytes between
  rebuild and original. That breaks `match_all`-based
  verification — needs the strict Check A from
  [[init-trichotomy]] (cycle-precise py65 init-RTS capture
  at extract time).
- **More engine migrations**: any engine with non-default
  $D418, filter init, or per-voice envelope/pulsewidth priming
  is a candidate. From the 100-engine survey: ~50% non-default
  $D418, ~37% filter init.
- **Phase A (strict Check A) verification** is parked — see
  task #75 in the session task list.

## See also

- [[init-trichotomy]] — the load-bearing principle this implements.
- [[composer-dissolution]] — composer.py architecture; init lives
  in `_emit_init` for the bowden+companion paths,
  `_emit_hubbard_init` for the Hubbard '85 path.
