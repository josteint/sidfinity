---
name: project-bttf-banking-trampoline
description: "Back_to_the_Future.sid (Clever_Music) — banking-trampoline variant, byte-exact (2/2) via three composer/extract fixes. Surfaced 1) the py65 stop-guard bug, 2) the optional-init-master-vol need, and 3) cmd-stream multi-subtune support."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce060f8a-e40f-4b55-9551-2d4fc0bb3028
---

`Back_to_the_Future.sid` (hvsc84/MUSICIANS/C/Clever_Music/Back_to_the_Future.sid) is a relocated Clever_Music variant. Init at `$C500` banks RAM, copies `$B000-$BFFF → $A000-$AFFF` (4 KB) and `$C400-$C4FF → $2C00-$2CFF` (256 bytes), then `JMP $2C53`. Play at `$C535` re-banks and `JMP $C03A` (Fairlight's play loop). The relocated init at `$2C53` does the real per-voice state setup — clear `$D400-$D418`, write `$C1C0-$C1C3` (tempo/song_pos), then a copy loop pulling per-subtune tables from `$2CA1`/`$2CCB` (subtune 0) or `$2CB6`/`$2CE0` (subtune 1) into `$C217+X` and `$C22F+X`.

**Why three fixes were needed for the rebuild to match orig instruction-stream:**

1. **py65 stop guard** (pipelines/companion/clever_music/extract/engine_model.py:_run_init). The old guard `while load <= PC < load+len(body)` exited as soon as `JMP $2C53` fired, so the relocated init never ran in the emulator and the extract read static SID-file values from `$C217+` instead of post-relocation values. Fix: stop on `PC == $FEFF` (the sentinel-RTS target from the stack we seed before init). Same exit point works for non-trampoline Clever_Music engines too.

2. **Optional `init_master_vol`** (pipelines/engine_model.py:MasterVolConfig.init_value; pipelines/composer.py:_emit_cmd_init). Fairlight/Gyroscope init writes `$D418=$0A` after the silence loop; BTTF init writes nothing after the clear. Added `init_value: Optional[int]` — None → skip the `lda init_master_vol_tab,x; sta $d418` in cmd-init. USF carries this via top-level param `init_master_vol: -1` (sentinel for "no init write"); extract derives it from `_run_init`'s captured `$D418` writes (count the writes past the first one).

3. **Multi-subtune cmd-stream composer** (pipelines/composer.py:_emit_cmd_orderlists, _emit_cmd_song_table, _emit_cmd_init). The single-subtune layout used const labels `ptn_v1/v2/v3` and a const `song_table` pointing at them. Multi-subtune emits `ptn_s{N}_v{V}` per subtune, `song_table_s{N}` per subtune, plus selector tables `song_table_ptr_lo/hi`. The runtime `song_table` becomes a 12-byte RAM buffer; init copies the chosen subtune's block via `(zp_ptr_lo),y` after `init_silence`. Engine's load_note then reads `song_table+N` exactly as before.

**How to apply:** For another banking-trampoline Clever_Music variant, the three fixes already in place should handle it — only investigate further if the engine's relocated init does something other than copy-per-voice-state-from-tables (e.g. writes `$D418` to a non-`$0A` value, or uses a different engine memory layout than `$C1C0`/`$C217`/`$C22F`). Verified at duration=8.0s in regression (the rebuild's init-clear lands one frame earlier than orig's so the 6s default truncation would falsely diverge by ~8 writes; the content matches by 8s).

Other SIDs in `hvsc84/MUSICIANS/C/Clever_Music/` (Blade_Runner, Ian_Bothams_Test_Match, Plasmatron, Rocky_Horror_Show, Shao-Lins_Road, Soundwave_Tubular_Bells, Space_Doubt, Wizardry) are NOT Clever_Music engine variants — PSID init/play addresses range $13D7..$F600. "Clever Music" is a musician credit, not a single-engine folder; each remaining SID needs its own RE pass.

Related: [[project_clever_music]] (the base Fairlight/Gyroscope strain), [[feedback_deconstruct_not_reproduce]] (the BTTF rebuild reproduces the instruction stream, not the relocation mechanism — composer emits the engine at fixed addresses, no banking).
