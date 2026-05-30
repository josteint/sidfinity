---
name: project_confuzion
description: "Confuzion (Hubbard 1985 Incentive) — voice+filter byte-exact; song-end $D418 fade missing"
metadata:
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Confuzion (Rob Hubbard, 1985 Incentive Software) is the eleventh
Hubbard '85 engine on the [[project_usf2_refactor]] USF-only path.
Voice registers + filter ($D400-$D417) byte-exact across all 13998
frames; **subtune 0 fails verify_all** under the stricter $D400-$D418
snapshot check because our codegen doesn't reproduce the song-end
$D418 fade (orig steps $0F → $01 across frames 12727-13861).
Commits: b1c916b (initial migration), 667176a (the verify check that
exposed the fade gap).

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

`pipelines/confuzion/config.py`:
- `vib_onset=8`
- `speed_ctr_init=2` — first note-load deferred two frames; the
  engine ticks vibrato twice before reading the pattern.

No shared-core changes. Every other Hubbard '85 knob (arp_period,
incby2_step, frame_ctr_init, …) defaults to the right value because
Confuzion's runtime simply never exercises those paths.

## Song-end $D418 fade — the verify_all gap

Orig writes $D418 with values $0F → $0E → ... → $01 across frames
12727-13861 (steps every ~87 frames = ~1.74s, total fade duration
22.7 seconds). Our codegen sets $D418=$0F in init and never modifies
it. This is the same engine feature seen in
[[project_thing_on_a_spring]] — see [[project_hubbard_song_end_fade]]
for the cross-engine summary and implementation sketch.

The fade is driven by a counter at $0BC2 in the orig binary, but the
init code NOPs out the trigger via self-modifying `LDA #$EA; STA
$08B9`, hiding where the fade ARMs in the disassembly. Need deeper
trace to find the increment path.

Voice + filter ($D400-$D417) match 100.0% across 13998 frames. Only
the master-VOL fade in the last 22s diverges. Listening test will
expose the missing fade-out at the very end of the song.
