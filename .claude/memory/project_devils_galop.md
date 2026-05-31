---
name: Devils Galop pipeline + engine
description: Devils Galop — MIGRATED to USF2 on the shared Hubbard '85 core, codegen 100% byte-exact. Disassembly reference.
type: project
originSessionId: 567e7893-306e-4610-b017-b0de0b776163
---
Rob Hubbard's *Devils Galop* (1985). USF2 demo SID:
`demo/hubbard/Devils_Galop_original.sid` (3933 bytes).
Load $0A18, init → $18B3, play → $12FD. 1 subtune.

**USF2 status (2026-05-24): COMPLETE + on the USF-only pipeline.**
Devils Galop migrated to the shared Hubbard '85 USF2 core
(`pipelines/hubbard/`, see [[project_usf2_refactor]]) and lifted onto
the USF-only build path (commit a27c65e): `pipelines/devils_galop/
extract/to_usf_v2.py` writes `Devils_Galop.usf` (no sample sidecars
— no SFX, no digi); `pipelines/hubbard/build_from_usf.py` reads it
back and produces a SID with no peek at the original. Verified via
verify_all (1/1 subtune).

The OLD das-model / Lean pipeline (`Codegen.lean`, py65 A+ / writelog
B 94.3%) is SUPERSEDED — ignore its old grading notes.

Three per-engine deltas vs Commando, all in the EngineConfig (the
shared core is untouched, Commando stays 19/19):
- `arp_interval=24` — `ADC #$18`, not 12.
- `incby2_step=-1, incby2_every_frame=True` — the fx-bit1 slide. Init
  patches INC→DEC at $15C1; it ramps -1 every frame (Commando +2 odd).
- `suppress_first_notestart=True` — the $178B drum-priority gate drops
  V3's f0 note-start SID *writes* (state kept). In the codegen,
  `note_start` gates only the `$d4xx` stores, never the v_ctrlbyte /
  v_slide state — V2's off-table vibrato reads V3's v_ctrlbyte, so
  dropping the state desyncs it (the bug that cost the last 48 frames).
- `vib_onset=8` — vibrato gate `CMP #$08` (Commando 6). This is
  `VibratoSpec.onset_dur`, a real per-instrument USF param. Applied
  per the representation principle: same parametric vibrato as
  Commando, a different point — NOT a `vibratoKind`. The disassembly
  summary said "no dur gate" — wrong; the round-trip test pinned 8.

The off-table pitch-104 case (V2's vibrato reads the v_ctrl triple
past the 96-entry freq table — the "notenum/freq overlap" trick)
needed NO Devils-Galop-specific code: the Hubbard '85 engine-state
layout relative to the freq base is family-shared, so the shared
`song_interp._read_state` / the codegen `statebuf` handle it.

**Disassembly reference.** `pipelines/hubbard/devils_galop/disassembly.s`
(hand-annotated). The engine variant uses heavy self-modifying init:
init at $18B3 patches operand bytes in the play loop to
$0A1E/$0A21/$0A24/$0A50, redirecting reads into the "data gap"
$0A1E-$12EA where the orderlists, pattern-address table and pattern
data live. Init also: copies 120 bytes $183B→$1799 (15 instrument
records × 8 bytes — the shared 8-byte Hubbard '85 layout); flips
skydive INC→DEC at $15C1; pins volume $0F; sets $1782=$40. Freq table
at $1694, 96 semitones. Do NOT trust `LDA $1795,X` etc. in the static
disassembly — those operands are rewritten by init.

How to apply: the engine is done. For the NEXT Hubbard engine, follow
the same path — write `pipelines/<engine>/config.py`, build on the
shared core, trace the per-engine deltas one diff at a time, each
delta a config field (never a `*Kind` enum).
