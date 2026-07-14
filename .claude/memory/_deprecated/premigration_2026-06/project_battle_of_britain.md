---
name: project_battle_of_britain
description: Battle of Britain (Hubbard 1985) — fully byte-exact via shared core; surfaced tie-preserves-slide bug
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Battle of Britain (Rob Hubbard, 1985 Personal Software Services) is the
tenth Hubbard '85 engine on the [[project_usf2_refactor]] USF-only path.
ALL 1/1 subtune verifies md5-exact via py65 across 12705 frames
(commit 94cddf4).

Engine fingerprint:
- load $8000  init $8EAA  play $8006  freq table $8326  instr base $8420 (19×8)
- frame counter at $841F (= freq_table_base + 249; default Commando is +253,
  but our codegen's frame_ctr lives at freqtab+253 regardless — only the
  initial value matters: BoB ships $DC at $841F)
- PSID speed flag $01 (CIA timer)
- Shares Hubbard '85's standard effect opcodes — bit 0 every-frame
  skydive / bit 1 slow-skydive / bit 2 arp +12 / bit 3 PW linear /
  bidirectional PWM via the rest.

## Config

`pipelines/battle_of_britain/config.py` adds four knobs beyond the
Commando defaults; nothing else.

- `frame_ctr_init=0xDC` — engine binary value at $841F
- `arp_period=8` — engine's `frame_ctr & 7 == 0` (not Commando's `& 1`)
- `incby2_step=-1, incby2_onset=12` — engine DEC v_fhi gated on
  `v_durfield & $1F >= $0C` (CMP #$0C at $82D5) and `frame_ctr & $01`
- `vib_onset=8` — engine `CMP #$08` at $8194; also kills a vib_carry
  PW-step drift on shorter notes

## Shared-core fix it surfaced

note_codec.py and song_interp.py were CLEARING `v_drumtrig` /
`rt.drum_trig` on every note load. The engine's tie path
(BVS $80C0 at $807A) jumps OVER both the v_slide clear AND the
slide-load — so a tie note must NEVER touch the running slide.

Fix: only clear / reload on non-tie notes. Without this, slides set
on a sustained note (held by ties) would vanish at the first tie.
Pre-fix: 22.6%. Post-fix: 43.3%. Post all config knobs: 100.0%.

All nine prior engines remain byte-exact (84/84 subtunes total).
