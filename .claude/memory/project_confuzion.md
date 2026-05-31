---
name: project_confuzion
description: "Confuzion (Hubbard 1985 Incentive) — byte-exact across all subtunes; stripped runtime (vibrato + bidirectional PWM only)."
metadata:
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Confuzion (Rob Hubbard, 1985 Incentive Software) is the eleventh
Hubbard '85 engine on the shared composer path. Voice registers +
filter + master-VOL ($D400-$D418) byte-exact across all 13998 frames
after the fade was implemented — see [[project_hubbard_song_end_fade]]
for the cross-engine fade story.

Engine fingerprint:
- load $0858  init $0867  play $0858  freq table $0AFD  instr base $1146 (12×8)
- frame counter in zero page $A2, advanced by self-modifying
  `INC $085C` (the operand byte of `LDA #imm; STA $A2`)
- 1 subtune. PSID speed flag $01 (CIA timer).
- 2382-byte binary — tiny. Engine code is ~648 reachable bytes.

## Stripped runtime

Unlike Battle of Britain / Commando / etc., Confuzion's per-frame
effect dispatch only runs vibrato + bidirectional PWM. The runtime
never reads fx_flags bits 0/1/2 — no skydive, no slow-skydive, no
arp +12. It never reads bit 3 either — no linear PW path. Just:

- vibrato (depth, phase via `$A2 & 7` mapped to a triangle, gated on
  `v_durfield & $1F >= 8`)
- bidirectional PWM (per-inst speed encoded `high_3_bits | period_5`,
  $08/$0E bounds)

## Config

`pipelines/hubbard/confuzion/config.py`:
- `vib_onset=8`
- `speed_ctr_init=2` — first note-load deferred two frames; the
  engine ticks vibrato twice before reading the pattern.
- `master_vol_subtrahend_voice=1`, `master_vol_base=0xA0` — drives
  the song-end fade ($D418 from $0F down to $00 over the final ~22s).
- `master_vol_underflow_clamp=True` — Confuzion's V2 ends past
  BASE+1, so the SBC clamp asm needs explicit underflow handling
  (otherwise $D418 jumps back to $0F on the first inst-change after
  vol_progress > $A0).
- `loop_silences_song=True` — orig's $FF handler unconditionally
  silences the song (sets $D418=0, song-running flag=0). Without this
  the song keeps playing past natural song-end.

No shared-core branches. Every other Hubbard '85 knob (arp_period,
incby2_step, frame_ctr_init, …) defaults to the right value because
Confuzion's runtime simply never exercises those paths.
