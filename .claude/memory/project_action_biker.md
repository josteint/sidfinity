---
name: action-biker-pipeline-engine
description: "Action Biker — MIGRATED to USF2 on the shared hubbard/ core, codegen 100% byte-exact on all 3 subtunes. Disassembly reference."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *Action Biker* (1985 Mastertronic). USF2 demo SID:
`demo/hubbard/Action_Biker_original.sid` (byte-identical to
`data/C64Music/MUSICIANS/H/Hubbard_Rob/Action_Biker.sid`).
Load $C000, init $CBBB, play $C00D. 3 music subtunes.

**USF2 status (2026-05-24): COMPLETE + on the USF-only pipeline.**
Action Biker migrated to the shared Hubbard '85 USF2 core
(`pipelines/action_biker/config.py` — an `EngineConfig`) and lifted
onto the USF-only build path (commit a27c65e). Voice + filter
byte-exact across all 3 subtunes.

**Status (2026-05-26, commit 667176a): under the stricter $D400-$D418
snapshot check, subtunes 1 and 2 fail at end-of-song**: orig writes
$D415=$80 / $D416=$80 / $D417=$80 in the final frame as filter
cleanup (filter cutoff lo/hi + resonance+routing). Our codegen
leaves them at $00. Subtune 1 first diverges at frame 3073 of 3410;
subtune 2 at frame 577 of 605. Inaudible (the song has ended and no
voice is gated on), but a real register-state diff. Subtune 0
(10395 frames) still byte-exact. Score: 1/3.

**Annotated disassembly: `docs/hubbard_action_biker_disassembly.s`.**
Freq table $C2FC, instrument table $CB5B (8-byte records). The
8-byte record IS the shared '85 layout — byte 6 is pwm_speed (the
disassembly's "vib_period" annotation is wrong; the PWM block at
$C1E4 reads it).

Config deltas vs Commando (all EngineConfig fields):
- `instr_base=0xCB5B, instr_count=12, freq_table_base=0xC2FC`.
- `arp_interval=12`. `vib_onset=8` (CMP #$08 at $C1B5).
- `speed_ctr_init=1` — the tick counter ($C3E7) starts at $01, so the
  first note-load is deferred to play frame 1. Frame 0 is effects.
- `first_frame_gate_off=True` — play frame 0 writes ctrl=0 to all 3
  voices (the $C28E first-frame setup runs in play, not init). Needs
  a once-only flag — frame_ctr is a byte and wraps every 256.
- `voice_starts=(1, 2, 2)` — subtune 0's voice loop starts at V2,
  skipping V3 ($C3F2 = 1 for subtune 0, else 2).
- `stop_fill=0x80` — the $FE orderlist marker ends the song by
  writing $80 to every voice register, then silence ($C2DC).

Because Action Biker runs effects on play frame 0 BEFORE any
note-load, the shared core now also seeds `v_instr` from the
freq-table overlap (freq+214), alongside v_ctrl/pwm_period/pwm_dir.

How to apply: Action Biker is done. For the next engine, same path —
seed the disassembly, write a config, build on the shared core, trace
deltas one diff at a time, each a config field, never a `*Kind`.
