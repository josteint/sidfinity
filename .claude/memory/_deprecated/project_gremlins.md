---
name: Gremlins pipeline state
description: pipelines/gremlins/ scaffold-clone status; engine quirks from hand-annotated disassembly; codegen gap analysis vs Commando/Monty
type: project
originSessionId: 9cba5a5f-0510-422f-a817-ea9350fa94b3
---
Hubbard's *Gremlins* (1985, Adventure International). Same scaffold
pattern as Chimera / Crazy Comets / Devils Galop — `pipelines/gremlins/`
was bulk-cloned from the Monty pipeline in commit cbb86f6 and the
README's "Grade A 98.8%" claim was stale Monty boilerplate, not
measured. `lake build sidgen_gremlins` runs clean; `writelog_grade.py`
returns **Grade F, 5.8% (87/1500)** vs the original.

Disassembly committed to `docs/hubbard_gremlins_disassembly.s` (1085
lines, hand-annotated). Use it as the source of truth for engine
semantics.

**A verbatim engine-image path was tried and reverted (commit ab034bd
reverts 94a5a4d).** The verbatim path bypasses USF — Main.lean wraps
the original binary in a fresh PSID header without going through
SongData.lean or Codegen.lean. Grade A 100% writelog match but
fails the "always through USF" requirement (defeats ML training
purpose, same critique as writelog-replay). Do NOT use it for Gremlins;
the proper path is the structural Codegen.lean port below.

**Why:** continuing the 1985-Hubbard scaffold-to-working sweep. Gremlins
is in the same engine family as Action Biker / Commando / Monty but
with its own quirks (skydive, octave-arp, full sfx dispatcher).

**Engine vectors / state:**
- Load $1000, init $1530, play $1012.
- PSID jump table at $1000-$100F: $1000→$198A (music subtune setup),
  $1003→$19B8 (silence music), $1006→$19BE (clear sfx flag),
  $100F→$19CC (sfx dispatcher).
- 26 PSID subtunes: 0..6 = music, 7..25 = sfx.
- State byte $16EE: bit 7 = silenced, bit 6 = first-frame pending.
- Frame counter $16FA (reset at first-frame setup).
- SHARED tempo counter $16EB / reload $16EC ($02 / $02 in binary).
- Per-voice state $16C0-$16FF. Critical dirty-BSS initial values:
  - $16D6..$16D8 v_inst = $15, $15, $03 (V1, V2, V3)
  - $16EF..$16F1 v_fhi = $22, $15, $10
  - $16CD..$16CF v_flags = $05, $05, $83
  - $16D0..$16D2 v_ctrl = $41, $41, $81
- Instrument table at $1784 (8 bytes/record); freq table at $1600
  (2-byte semitone entries, 96+ extended).

**`fx_flags` bit semantics** (verified from `$11B5..$1388` in the
disassembly; matches `pipelines/gremlins/extract/engine_model.py`):
- bit 0 ($01) — drum: same as Action Biker; ramp `v_fhi` down past
  mid-note and kill ctrl gate ($12F0-$132B).
- bit 1 ($02) — skydive: DEC `v_fhi` on odd `frame_counter` when
  `orig_dur >= $0C` AND `v_dur < $08` AND `v_fhi != 0`
  ($132C-$1357). Falling-pitch tail on long notes.
- bit 2 ($04) — octave arp: alternate `v_pitch` ↔ `v_pitch+12` by
  frame counter bit 0 ($1358-$1388).
- bit 3 ($08) — linear PWM: `pw_lo += pwm_speed`, 8-bit wrap, free-
  running ($1226-$1241). Cleared = bidirectional bounce in `pw_hi`
  between hardcoded $08 / $0E ($1242-$12A8).

**Per-note portamento ("skydive command")** — NOT a flag. When the
pattern's new-info byte has bit 7 set, the byte is stored at
`v_porta,X = $16F5,X` (bits 1..6 = step delta, bit 0 = direction).
Processed every frame at `$12A9-$12EF` as `v_flo/v_fhi += signed_step`.
Bit 7 clear on the same byte means "new instrument index" instead.

**Frame-0 divergence pattern (observed 2026-05-15):**
- Original frame 0: V3 writes freq $0116 (from inst 3's octave-arp,
  `fx=$05`), V1/V2 write pw_lo $C8/$EF (from inst 21's linear PWM,
  `fx=$08`, `vib_period=$D9`: $16+$D9=$EF on V2, $EF+$D9=$C8 on V1).
  Effects-only — note-load gated off because $16EB DEC'd from $02 to
  $01 doesn't match $16EC=$02.
- Rebuilt frame 0: fires full instrument loads for all voices
  (PW, AD, SR, CTRL=$40 all written). V3 codegen fires note-load
  unconditionally on frame 0 with v_inst=v_pitch=0.

**Roadmap to structural Grade A** (in priority order):
1. Add an `engineQuirks` knob for a shared tempo counter that gates
   note-load uniformly across voices. Mirror `$16EB`/`$16EC` ($02/$02).
2. Per-voice BSS init values for `v_inst`, `v_fhi`, `v_flags`,
   `v_ctrl` so effects-only first frames run on the right
   instruments (sourced from the binary's BSS at `$16C0-$16FF`).
3. Verify skydive emit block guards match `$132F-$1357`.
4. Verify octave-arp emit block matches `$1358-$1388`.
5. Verify linear-vs-bidir PWM branch matches `$1226-$12A8`.
6. Audit `emitNL_SavePitchFhi`'s freq-table alias-store — Monty
   quirk; probably harmless or remove for Gremlins (no overlap at
   `freq_table + 105/106 = $16CA..$16CC` because instrument fx-bytes
   at `$1789..$178B` live elsewhere).
7. Iterate against `writelog_grade.py` until Grade A.
