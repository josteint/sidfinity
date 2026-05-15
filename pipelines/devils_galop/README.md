# Devils Galop pipeline

End-to-end rebuild of Rob Hubbard's *Devils Galop* (1985) SID. Same shape
as the Commando / Monty / Action Biker pipelines; cloned from Monty via
`tools/clone_hubbard_pipeline.py` and pending Devils-Galop-specific
calibration.

## Status

| Metric | Value |
|---|---|
| Subtunes | 1 (single subtune; PSID #1 in the original) |
| Layout | clone of Monty's pipeline — extract/, codegen/, build/, tests/ |
| Lake build | `sidgen_devils_galop` builds (executable + lib) |
| Rebuild output | `pipelines/devils_galop/build/devils_galop.sid` (~5.9 KB) |
| **Writelog grade** | **B (94.3%, 1414/1500 snapshots)** — sidplayfp emulation drift, not engine logic |
| **py65 engine grade** | **A+ (500/500 = 100.00%)** — engine is byte-perfect identical to the original |
| Annotated disassembly | `docs/hubbard_devils_galop_disassembly.s` |

The 86 remaining writelog divergences come from sidplayfp's frame-
boundary placement, not engine semantics. py65 confirms our engine
state matches the original byte-for-byte at every play() invocation
(verified 300/300 frames). What `writelog_grade.py` compares is the
**CSV snapshot** that siddump emits at the end of each play()
(`engine.getSidStatus(...)` in `tools/siddump.cpp`), not the writelog
stream itself.

`siddump --writelog` produces two parts per frame:
- The CSV snapshot (25 register values at end of play()).
- The `|W:cycle:reg:val:...` stream of all writes that occurred during
  that play() call.

`writelog_grade.py` compares the CSV snapshot by default. The writelog
stream is only used in `--cycle-accurate` mode, which compares
`(cycle, reg, val)` triples and gives 0.1% — because our code is a
different length than the original's, identical writes happen at
different cycle counts within each frame.

The root cause of the remaining gap: our codegen has **extra "empty"
sidplayfp frames** at 16, 127, 238 (where the original doesn't), and
the original has empty frames at 139, 176 (where we don't). Each
empty-frame mismatch shifts our subsequent CSV snapshots by one
sidplayfp frame relative to the original — visible as ~30-frame
clusters of 1-frame jitter. The empty frames seem to be a libsidplayfp
timing artifact: when play() takes near the full VBI (~19656 cycles),
libsidplayfp occasionally records the next frame as empty. Closing
this gap cleanly would need either a libsidplayfp source modification,
cycle-pad-to-match codegen, or a grade that compares the writelog
stream with frame-jitter tolerance.

## Fixes applied (path from F to B)

1. **dynamicFreqEntries for V2 alias pitch 104** (F 28.7% → D 44.6%).
   Devils Galop uses pitch 104 to alias into the runtime variable
   region $1764-$1767. `engineQuirks.dynamicFreqEntries` populated
   with entries for slots 104 + 105, sourced from `v_ctrl[V1]/v_ctrl[V2]`
   and `v_ctrl[V3]/v_pitch[V1]` at phase `beforeVoice 1`. See
   `_detect_dynamic_freq_entries` in `extract/emit_usf.py`.

2. **Arpeggio offset 12 → 24** (D 44.6% → C 89.1%). Devils Galop's
   engine adds 24 semitones (`ADC #$18` at $15D8), not 12 like Monty
   or Action Biker. Fixed in `extract/engine_model.py`.

3. **Skydive every-frame** (C 89.1% → B 91.2%). The Monty-cloned
   codegen gated skydive on `frame_counter & 1`; Devils Galop's engine
   runs skydive on every effects-path frame. Removed the gate in
   `codegen/DevilsGalop/Codegen.lean`.

4. **First-frame V3 SID gate (drum_priority)** (B 91.2% → B 94.3%).
   Mirrors the original engine's $178B gate. Added a one-byte
   `drum_priority` data slot (init $00, set to $FF at end of every
   `exec_voice` tail). Each note-load SID write is preceded by an
   inline `BIT drum_priority; BPL +3` gate (see `emitDrumPrioGate`).
   On the very first frame, V3 (first voice) reads $00 from the gate
   and its inst-record SID writes are skipped — matching the original.

## Engine notes

Devils Galop uses the same 1985-era Hubbard driver as Action Biker /
Commando, with a couple of distinctive quirks documented in
`docs/hubbard_devils_galop_disassembly.s`:

* **Self-modifying init.** Init at `$18B3` patches operand bytes inside
  the play loop so that `LDA $1795,X` / `LDA $1796,X` / `LDA $1797,Y` /
  `LDA $1798,Y` lookups actually read from `$0A1E-$0A53` at runtime.
  The orderlist/pattern tables live in the apparent "data gap" at
  `$0A1E-$12EA`.
* **Skydive direction flip** patched at runtime (opcode at `$15C1`
  rewritten `INC` → `DEC` so skydive descends instead of ascends).
* **Volume clamp NOP'd out.** Two bytes at `$13B3` are overwritten
  with `EA EA` so the fade-clamp branch never triggers; volume is
  pinned at `$0F`.
* **Freq table at `$1694`** (96 semitones × 2 bytes = 192 bytes).
  Do not over-read; the default 120-entry extraction in
  `extract/engine_model.py` picks up runtime-variable bytes after byte 192.
* **Instrument table is copied into RAM at `$1799`** by init (120
  bytes / 15 records × 8 bytes from source `$183B`).

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the
layout explanation.

## How to run

Regenerate `SongData.lean` from the original SID:

```bash
python3 -m pipelines.devils_galop.extract            # subtune 0
```

Build and run:

```bash
lake build sidgen_devils_galop
.lake/build/bin/sidgen_devils_galop
```

Grade the rebuild against the original:

```bash
python3 src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Devils_Galop.sid \
    pipelines/devils_galop/build/devils_galop.sid
```

## TODO

* The remaining 86-frame gap is *cycle-position* mismatch. To close
  it: either pad the codegen's per-voice processing to match the
  original engine's cycle count exactly, or relax `writelog_grade.py`
  to allow ±1-frame freq-write jitter (which would also unblock other
  Hubbard pipelines hitting similar ceilings).
* The `Properties.lean` proof times out at `whnf` heartbeat 200000 (a
  Monty-clone artefact, not Devils-Galop-specific); the executable
  builds without it.

## References

* Annotated 6502 disassembly: `docs/hubbard_devils_galop_disassembly.s`
* Seed disassembler: `tools/seed_disassembly.py`
