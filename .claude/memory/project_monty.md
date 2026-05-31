---
name: monty-on-the-run-pipeline-engine
description: "Monty on the Run — MIGRATED to USF2 on the shared hubbard/ core, codegen 100% byte-exact on all 3 subtunes. Disassembly reference."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *Monty on the Run* (1985 Gremlin Graphics). USF2 demo
SID: `demo/hubbard/Monty_on_the_Run_original.sid` (5694 bytes; byte-
identical to `data/C64Music/MUSICIANS/H/Hubbard_Rob/Monty_on_the_Run.sid`).
Load $8000, init $8000 (JMP $95A0), play $8012. 19 PSID subtunes — 3
music (0-2), 16 SFX (3-18).

**SFX (2026-05-22): DONE — all 16 SFX byte-exact, all 19 subtunes.**
`pipelines/monty/extract/sfx.py` — Monty's 16 SFX at $9454, freq
table $8400, the Hubbard '85 SFX format (shared `pipelines/hubbard/
sfx.py`). Monty's SFX init $8506 is structurally Commando's $53A5
sub-engine. `has_sfx=True`. SFX 11 and 13 swept off the 96-entry freq
table into Monty's SFX engine state ($84FB-$8500) — fixed by the
codegen relocating the SFX-state block into the freq-table off-table
region: `sfx_state_ofs=251` (the state block) + `sfx_framectr_ofs=250`
($84FA, the SFX-readable frame counter INC'd each play call). The USF
SoundEffect records are untouched — the fix is pure codegen plumbing.
Commits 603617d, f312540.

**USF2 status (2026-05-22): MIGRATED — codegen 100% byte-exact.**
Monty is `pipelines/monty/config.py` (an `EngineConfig`) + the
existing `extract/engine_model.py`, on the shared Hubbard '85 core
(see [[project_usf2_refactor]]). All 3 subtunes 25000/25000 byte-exact
through the full codegen pipeline (6376-byte SID); song_interp 100%
too. Commits up to 70b3e1b.

**Annotated disassembly: `pipelines/hubbard/monty/disassembly.s`** — full
engine layout, the $84C0-$8505 variable map, frame structure, effect
constants. Read it before any Monty work.

Config deltas vs Commando (all in the EngineConfig):
- `instr_base=0x93B4, instr_count=20, freq_table_base=0x8400`.
- `arp_interval=12` (= Commando). `vib_onset=8` (CMP #$08 at $8201).
- `incby2_step=-1` (fx bit1 DECs v_freq_hi on odd frames, $831A).
- `freeze_on_stop=True` — the $FE end-of-song semantics (below).

**The notenum / freq-table overlap.** The engine's per-voice
variables sit directly past the 96-entry freq table at $84C0, so
v_ctrl[V1/V2/V3] = $84D0/D1/D2 = freq entries 104-105. A pitch-104
note loads freq from there; the variables are seeded from the
binary's load-time bytes. The shared core seeds v_ctrl, pwm_period
($84E5) and pwm_dir ($84E8) from `freq_bytes` (offsets 208/229/232).

**The $FE freeze.** Monty's $FE orderlist marker is NOT an end — it
freezes the voice. On a tick the engine JMPs $837d, so the play call
aborts at that voice; on a non-tick every voice still runs its
effects. A frozen voice's duration counter ($84CA) keeps cycling as
a signed byte (256-tick period): while bit7 is set it aborts, while
clear it sustains + hard-restarts at the zero-crossing + runs fx.
The song never gates off. Modelled by `freeze_on_stop` + `v_frozen`
in song_interp and the codegen.

Four shared-core improvements came out of Monty: the adaptive note
codec (DUR_BITS/INST_BITS), column-major instrument tables (no
instrument-count ceiling), the overlap-variable seeding, and the
freeze model. All are config-gated and inert for Commando/Devils
Galop.

How to apply: Monty is done. For the next Hubbard engine, same path —
seed the disassembly (`tools/seed_disassembly.py`), write a config,
build on the shared core, trace deltas one diff at a time, each a
config field (never a `*Kind` enum).
