---
name: Crazy Comets pipeline state
description: Grade C 87.6% (V1 89.5% / V2 98.5% / V3 99.4%). V2/V3 essentially solved; V1 gap is freq-write timing in effects-loop interactions.
type: project
originSessionId: 5e2721dd-e65d-4aae-872c-a65b0931da4e
---
Current: Grade C, 1314/1500 snapshots (87.6%). Reached via 4 sharp commits walking F 3.9% → C 87.6%:

1. `61d366a` initialDur=1 (F 3.9 → F 7.4): first DEC v_dur takes sustain.
2. `e79b599` binary v_inst/v_fhi cache (F 7.4 → D 61.8): seed `[$01,$13,$10]` and `[$00,$01,$06]` in Codegen.lean data section; Hubbard's $5016 zeroes only v_olpos/v_patpos/v_dur/v_pitch, NOT v_inst/v_fhi.
3. `3a8a599` HR threshold v_dur==2 (D 61.8 → C 72.5): 3-frame tick divider means CMP #2 fires HR 3 frames before note-load (was CMP #1).
4. `876f212` skydive dur gate (C 72.5 → C 87.6): Hubbard's $532A also requires `(v_flags & $1F) >= $11`; for tempo=3 that's v_durfield >= 51.

**Per-voice:** V1 89.5%, V2 98.5%, V3 99.4% (over 1500 frames).

**Residual V1 gap (158 frames, all FREQ_LO/FREQ_HI):**
Investigation 2026-05-15: V1's note at F497 (CTRL=$11 AD=$0F SR=$FF = inst 10, vib_depth=$01) holds at $684C for 23 frames; codegen vibrates it. Both engines must produce the same output because per-voice 98.5% on V2 (same inst 10 plays correctly). Hypotheses tried + REJECTED:
- HR threshold CMP #0 (instead of #2): dropped all voices, V2 75.3% / V1 83.7% / V3 95.7%. CMP #2 is genuinely correct globally.
- Vibrato onset threshold CMP #24 (instead of #21): no song notes have dur in 21..23 range, threshold doesn't matter.
- Disabling inst 10 vibrato: dropped to D 58.3% — confirms inst 10 DOES vibrate (V2 vibrates).
- Identifying V2's octave-arp source: trace shows V2 alternates $4E20/$9C40 (octave apart), but inst 10 has fx_flags=$02 (bit 1 only). Codegen still reproduces this somehow, so the codegen IS internally consistent.

The V1 issue is NOT a simple threshold or effect-flag mistake — it's some interaction in the codegen's effect-dispatch that doesn't match Hubbard's `effectOrder` semantics. Next investigation needs to instrument the codegen to log per-frame which effects fire for V1.

**Out-of-scope but documented:** dual-engine init at $6100, monotonic PWM at $5222, SFX engine $539B+sub_5514. SFX subtunes 2-16 silent.

PSID header: load=$5000, init=$6100, play=$500C, 17 subtunes (default 1). State block at $54CF-$5513, freq table at $540F (96 semitones × 2 bytes), inst table at $5574 (8-byte records, same offsets as Action Biker).
