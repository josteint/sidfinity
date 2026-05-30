---
name: human-race-pipeline-engine
description: "Human Race — FULLY migrated to USF-only path. All 5 subtunes verify md5-exact via py65. Final commit 7af60ed."
metadata:
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *The Human Race* (1985 Mastertronic). Load $0980, init
$0980 (trampoline to $1A9C), play $0986. 5 PSID subtunes, all music.
V3 is unused for music in the PSID; V1+V2 only. Disassembly:
`docs/hubbard_human_race_disassembly.s`.

**Status (2026-05-25): fully byte-exact through the USF-only path.**
`demo/hubbard/Human_Race.usf` + `Human_Race.sid` committed.
`verify_all` md5-exact across all 5 subtunes (1.1× HVSC duration each).
Audible spot-check confirms tempo matches the original (after the
PSID speed-bitmask fix in `325d211`).

## Migration arc (in commits)

| commit | change | result |
|---|---|---|
| `b3454e5` | Migration plumbing (engine_constants entry, to_usf_v2 wrapper, empty-orderlist→stop) | subtune 0 OK |
| `325d211` | Propagate PSID `speed` bitmask end-to-end | tempo matches original |
| `d877833` | `arp_period=8` (drumarp audit) | no test gain (subtune 0 didn't exercise drumarp) |
| `b11a324` | `incby2_step=1, incby2_onset=17` (skydive audit) | no test gain |
| `9b47815` | `linear_pw_or=$40` (PWmode audit) | subtune 1 OK |
| `60c2d00` | `N_MUSIC` parameterization (init dispatch threshold) | subtunes 3, 4 OK |
| `7af60ed` | Data-driven `build_statebuf` + HR state layout | subtune 2 OK |

## HR's EngineConfig (the parametric distinctions from Commando)

```
vib_onset=9              # gate = (encoded_dur >= 8) = (playback_dur >= 9)
voice_starts=(1,1,1,1,1) # skip V3 (silent across all subtunes)
seed_overlap=False       # $1A9C init zeros per-voice state at runtime
arp_period=8             # drumarp: 1 base + 7 +octave per cycle
incby2_step=1            # skydive: INC by 1 per fire
incby2_onset=17          # skydive: (v_flags & $1F) >= $11 long-note gate
linear_pw_or=0x40        # linear PWM ORs $40 each frame
```

Plus `engine_constants.HUMAN_RACE`:
- `instr_base=$0DE3`, `instr_count=23`, `freq_table_base=$0CE4`.
- `voice_starts={0:1,1:1,2:1,3:1,4:1}` (USF-only path uses this dict).
- `state_layout=HUMAN_RACE_STATE_LAYOUT` (off-table arp mirror).

## Effect audit verdicts — all Rule 1 collapse

See [[project_human_race_audit]] for details. Summary:
- downslide (bit 0) ≡ shared `freq_slide`
- skydive  (bit 1) ≡ shared `fx_incby2` (with HR parameters)
- drumarp  (bit 2) ≡ shared `fx_arp` (period=8)
- PWmode   (bit 3) ≡ shared `fx_pwm` mode=linear (linear_pw_or=$40)
- per-note slide ≡ shared `fx_drumslide` (already wired)

**Zero new USF parameters added for HR.** Every musical primitive
landed in the existing schema. The principle doc held up under a
fresh engine.

## Surfacing shared-core latent bugs

HR's migration uncovered 6 hidden hardcodes in the shared core (see
[[feedback_migration_as_stress_test]]). The "right by coincidence
for the first 5 engines" assumptions all got parameterised. The
next engine (Hunter Patrol etc.) starts from a stronger base.

## Notes for future work

- The audible ear-test caught the PSID speed bug that md5-exact
  verify could not — see [[feedback_py65_misses_dispatch_bugs]].
- The principle doc's "engine may hold mechanism" had to actually
  be exercised for the off-table arp state layout. The data-driven
  `StatebufLayout` is the principled implementation.
