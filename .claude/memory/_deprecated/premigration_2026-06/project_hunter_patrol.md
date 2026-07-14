---
name: project_hunter_patrol
description: Hunter Patrol — FULLY migrated to USF-only path. 1/1 subtune verifies md5-exact via py65 (11935 frames / 238s).
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *Hunter Patrol* (1985 Mastertronic). Load $A000, init
$AE1E, play $A006. 1 PSID subtune. 3 active voices. Disassembly:
`docs/hubbard_hunter_patrol_disassembly.s`.

**Status (2026-05-25): fully byte-exact through the USF-only path.**
All 11935 frames (1.1× HVSC duration = 238s) verify md5-exact.
Commit `34a7a5e` for the migration (single commit — no iteration arc
this time, the principle-driven scaffold + 4 audited deltas got it
right first try).

## Parameter deltas from defaults

```
speed_ctr_init=1     # $A418=$01 in binary; first note-load on frame 1
vib_onset=8          # $A194 CMP #$08; raw_dur >= 8 to vibrate
frame_ctr_init=0x1E  # $A426=$1E in binary; first INC -> $1F (odd parity)
incby2_step=-1       # skydive DECs v_fhi (not INC)
incby2_onset=12      # $A2D5 CMP #$0C; raw_dur >= 12 to skydive
incby2_late_gate=9   # $A2DC CMP #$09; v_dur < 9 to skydive (tail only)
```

Plus `engine_constants.HUNTER_PATROL`:
- `instr_base=$A427`, `instr_count=32`, `freq_table_base=$A32D`.
- `voice_starts={}` (all 3 voices active, defaults to V3-start).
- `seed_offsets`: same as Commando except `v_slide=238` (HP's v_fhi
  is at $A41B = freq_table_base + 238, one byte earlier than
  Commando's +239).

## New shared-core parameters added during this migration

Three new fields on the shared `EngineConfig` / `EngineConstants`,
each introduced parametrically (default preserves existing
engines' behavior):

- `frame_ctr_init` (default `$FF`) — initial value of the zp
  `frame_ctr`. Hunter Patrol's binary ships `$A426=$1E`, an OFF
  parity from the previous engines.
- `incby2_late_gate` (default `None`) — optional `v_dur < N` gate
  on the fx-bit-1 slide. Hunter Patrol's skydive only fires in
  the tail of long notes; previous engines didn't have this
  gating shape. Emitted via `%%INCBY2_LATE_GATE%%` sentinel
  substitution in `_emit_sid`.
- `seed_offsets` (default `None` = Commando layout) — per-engine
  offsets where the 6 per-voice state vars live in the freq-table
  region. Hunter Patrol's v_slide is at +238 instead of +239.

The first two flow through USF params (engine-time data); the
third lives on `EngineConstants` (engine mechanism — see
[[reference_audit_tool]] and the principle doc for the distinction).

## Effect audit verdicts — all Rule 1 collapse

| effect | verdict | parameters |
|---|---|---|
| drum (bit 0) | ≡ `freq_slide` | existing |
| skydive DEC (bit 1) | ≡ `fx_incby2` | step=-1, onset=12, late_gate=9 |
| table arp (bit 2) | ≡ `fx_arp` | period=2 (default), interval=12 |
| PWM mode-A (bit 3) | ≡ `fx_pwm` linear | linear_pw_or=0 (default) |

Hunter Patrol adds **two new** parameters (`frame_ctr_init`,
`incby2_late_gate`) to the schema. Both are musical / engine-
mechanism, both have sensible defaults for existing engines. Zero
new opaque kinds.

## Procedural notes

- Frame-count convention: ALWAYS use `subtune_frames(config, passes=1.1)`
  for diff windows, not arbitrary 6000-frame windows. The skill
  template had this bug; fixed in this session.
- Migration arc collapsed into one commit — Hunter Patrol's
  EngineConfig fit cleanly onto the shared core after Human Race
  had already added the principal new sites (statebuf layout,
  empty-orderlist, N_MUSIC). The shared core is getting more
  hardened with each migration.
