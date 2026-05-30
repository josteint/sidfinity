---
name: das_model.s is the reference oracle for Hubbard player codegen
description: When CodegenV3 (Lean) diverges from Commando, read demo/hubbard/Commando_das_model.s. The Python das_model achieves 89% writelog match; its asm shows exactly how each effect should fire and what state structures Hubbard uses.
type: reference
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
`demo/hubbard/Commando_das_model.s` (2123 lines) is the assembly produced by the Python `das_model_gen.py` pipeline, which achieves **89.4% writelog frame-perfect** match against `Commando_original.sid` (per `siddump --writelog`).

When the Lean `CodegenV3.lean` diverges, read the corresponding section of das_model.s **before** speculating about Hubbard semantics. It encodes Hubbard-specific quirks that aren't documented elsewhere.

**Key landmarks (das_model voice numbering: V0/V1/V2 = SID V1/V2/V3):**
- `vplay1`/`vplay2`/`vplay3`: top-level voice handlers
- `v2eval` (line 235): V3 sustain effects (gate-off check, vibrato, PW, drum, bit0 slide, arp)
- `v2nt` (line 134): V3 note-load body
- Per-voice registers (V3): `$A8` = countdown, `$AE` = dur*3 - 3, `$B0` = pitch, `$B6` = inst, `$B8` = slide_fhi
- Pattern data: 4 bytes per note (pitch, dur_ticks, inst_byte, drum_byte)
- Inst byte: bits 0-5 = instrument index (mask `& $3F`); bit 6 = legato; bit 7 = reuse-old-inst
- Drum byte: bit 7 = "no drum effect", bit 0 = direction, bits 1-6 (`& $7E`) = step size

**Hubbard semantics that came directly from reading this file:**
- PW state (`i_pwlo`/`i_pwhi`) is **per-instrument and mutable**, not per-voice. Each PW step reads, modifies, stores back to `i_pwlo,Y` where Y=inst. Re-triggering an instrument resumes its counter.
- Vibrato fires only when note dur*3 >= 21 frames (`cmp #21 / bcs v2vlong`). Shorter notes write base freq.
- Vibrato shift count = `i_vib + 1` (encoded as `iny / dey / bne` loop). Triangle LFO = `(frame_counter & 7)` then mirror.
- Bit-0 slide skips entirely when countdown < 4 (covers gate-off frame and release).
- Linear PW: `lda i_pwlo,Y / clc / adc speed / sta i_pwlo,Y / sta $D410` — speed is the full byte.
- Bidir PW: speed is byte's upper 3 bits (`& $E0`); step interval is lower 5 bits (`& $1F`); min hi hardcoded $08; max from `i_pwmax,Y`. Direction flag is mutable per-instrument.
- `i_pws[7] = $00` for cv3I7 (no PW) - matches our USF.
- Effect order matters: gate-off check (`cmp #3` against post-DEC countdown) fires inline within the chain; PW/vibrato/etc still run on the gate-off frame.

**Common pitfalls caught by reading this file:**
- Bit 6 of inst byte was being preserved (`& $7F`) instead of stripped (`& $3F`), corrupting v_inst with values 64+ that overflowed PW table indexing.
- Per-voice PW state reset on instrument change, instead of per-instrument continuation.
- Slide running on gate-off frame for percussion (countdown<4 skip wasn't applied).
