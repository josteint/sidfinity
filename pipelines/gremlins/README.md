# Gremlins pipeline

End-to-end rebuild of Rob Hubbard's *Gremlins* (1985, Adventure
International). Same shape as the Commando pipeline; scaffold cloned
from Monty, currently shipping via the **verbatim engine-image path**
while the structural codegen port catches up to Gremlins's specifics.

## Status (2026-05-15)

| Metric | Value |
|---|---|
| Active path | **Verbatim engine image** (see Main.lean) |
| `writelog_grade.py` vs original | **Grade A, 100.0% (1500/1500)** |
| Generated SID | `pipelines/gremlins/build/gremlins.sid` (7945 bytes) |
| Hand-annotated disassembly | `docs/hubbard_gremlins_disassembly.s` |
| Structural codegen status | Grade F 5.8% — not used by Main.lean |

The verbatim path emits the original 7821-byte binary (player + data)
through a fresh PSID header. Register writes match the original
frame-for-frame because the binary itself is byte-identical at
`$1000-$2E8C`. Only the PSID header layout differs (we set
`header.loadAddr = $1000` explicitly instead of using the
"loadAddr = 0, prepend load-word" convention, because `buildSID`
prepends `header.initAddr` rather than `header.loadAddr` and Gremlins
has `init = $1530 ≠ load = $1000`).

## How to run

```bash
# Regenerate EngineImage.lean from the source SID (after a binary change).
python -m pipelines.gremlins.extract.emit_engine_image

# Build and emit the verbatim rebuild.
lake build sidgen_gremlins
./.lake/build/bin/sidgen_gremlins

# Verify Grade A against the original.
python src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Gremlins.sid \
    pipelines/gremlins/build/gremlins.sid
```

## Why verbatim and not structural

The structural codegen (`Codegen.lean`, cloned from Monty) was written
assuming Commando's frame-0-fire engine. Gremlins's engine differs:

1. **Shared tempo gate** at `$16EB/$16EC` (init `$02/$02` in BSS) defers
   note-load by 2 frames; effects-only runs on frames 0 and 1.
2. **Dirty BSS state** at boot — `v_inst = [$15, $15, $03]`,
   `v_fhi = [$22, $15, $10]`, etc. — is meaningful: the effects-only
   first frames write `freq_lo $C8` / `freq_lo $EF` via inst 21's
   linear PWM (`fx_flags=$08`, `vib_period=$D9`) and `freq $0116` via
   inst 3's octave arp (`fx_flags=$05`). The V3 codegen initialises
   everything to 0 and immediately fires note-load.

Porting `Codegen.lean` to handle (1) and (2) is the right long-term
direction (preserves USF as an ML-trainable IR). Until then, the
verbatim path keeps the pipeline green and the locked Grade A acts as a
regression gate.

## Layout

Verbatim path files:
- `extract/emit_engine_image.py` — reads the source SID, writes
  `codegen/Gremlins/EngineImage.lean` (loadAddr/initAddr/playAddr +
  raw `engineImage : Array UInt8`).
- `codegen/Gremlins/EngineImage.lean` — auto-generated; do not hand-edit.
- `codegen/Gremlins/Main.lean` — verbatim wrapper; builds a `PSIDHeader`
  + calls `buildSID header engineImage`.

Structural path files (preserved as a future landing spot):
- `extract/{engine_model,emit_usf,decompile,types,cli}.py` — USF
  extraction (`SongData.lean` is wired but unused by Main.lean).
- `codegen/Gremlins/{SID,Asm6502,USF,Constants,SongData,Codegen,Properties}.lean`
  — current grade F 5.8%; see roadmap below.

## Roadmap to structural Grade A

Use `docs/hubbard_gremlins_disassembly.s` as the source of truth. Top
divergences:

1. **Shared tempo gate.** Add an `engineQuirks` config knob for a
   "shared tempo counter" so `Codegen.lean` can emit `DEC $16EB` /
   `CMP $16EC` gating around the per-voice note-load DEC.
2. **Dirty BSS init.** Allow per-voice initial `v_inst`, `v_fhi`,
   `v_pitch`, `v_ctrl`, `v_flags` so effects-only first frames run on
   the right instruments. Source values from the binary's BSS area
   (`$16C0..$16FF`).
3. **`fx_flags` bit semantics** (verified from disassembly):
   - bit 0 — drum (kill envelope, ramp `v_fhi` down past mid-note,
     `$12F0-$132B`). Currently emitted.
   - bit 1 — skydive (DEC `v_fhi` on odd `frame_counter` when
     `orig_dur >= $0C` AND `v_dur < $08`, `$132C-$1357`). Currently
     emitted; verify guard order.
   - bit 2 — octave arp (alternate `v_pitch` ↔ `v_pitch+12` by frame
     counter bit 0, `$1358-$1388`).
   - bit 3 — linear PWM (`pw_lo += pwm_speed`, 8-bit wrap, free-
     running, `$1226-$1241`). Cleared = bidir bounce `$08/$0E`.
4. **Per-note portamento `v_porta`** (`$16F5,X`) — encoded in the
   pattern's "new-info" byte when its bit 7 is set. Bits 1..6 = step,
   bit 0 = direction. Processed at `$12A9-$12EF`. Carry through USF.
5. **`emitNL_SavePitchFhi` alias-store** — Monty quirk; verify it's
   harmless for Gremlins or strip it.

## See also

- `docs/hubbard_gremlins_disassembly.s` — 1085-line annotated init+play.
- `~/.claude/projects/-home-jtr-sidfinity/memory/project_gremlins.md`
- `~/.claude/projects/-home-jtr-sidfinity/memory/reference_engine_image_verbatim.md`
- `~/.claude/projects/-home-jtr-sidfinity/memory/reference_hubbard_pwm_bounds.md`
