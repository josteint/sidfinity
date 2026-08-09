# Devils Galop pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

> **Status (2026-06-07): BYTE-EXACT via the write-log verdict (verify_all
> 1/1).** The last divergence was the master volume: the engine writes
> `$D418 = $0F` on EVERY note-load (per voice that advances a pattern entry,
> from `$13B7` inline in the pattern-advance path, clamp NOP'd so the value is
> constant). Fixed with the `master_vol_every_note` config/USF knob. NOTE: the
> "Diagnosis"/"TODO" sections below describe the OLD snapshot-grade (Trap A,
> per-frame register snapshot) and its cycle-pad — that grading was retired;
> the verdict is now the SID write-log stream and the cycle-pad is irrelevant
> to it. Treat those sections as historical.

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
| Rebuild output | `pipelines/hubbard/devils_galop/build/devils_galop.sid` (~5.9 KB) |
| **Writelog grade** | **A (98.3%, 1474/1500 snapshots)** |
| **py65 engine grade** | **A+ (500/500 = 100.00%)** — engine is byte-perfect identical to the original |
| Annotated disassembly | `pipelines/hubbard/devils_galop/disassembly.s` |

The path from B to A: a tiny cycle-pad before V1's processing.

**Diagnosis**: py65 confirmed engine state matches the original
byte-for-byte at every play() invocation (500/500 = 100%). The
writelog_grade gap was sidplayfp's CSV-snapshot boundary placement,
not engine semantics.

Looking at writelog cycles: the original's V1 freq writes happen at
cycle 79-88 of *the next* sidplayfp frame (i.e. they spill past the
VBI boundary at ~19656). Our codegen ran V1 faster, finishing within
the same frame at cycle 18125. That mismatch caused sidplayfp to
record an extra empty frame for our rebuild whenever a frame got
close to the boundary, accumulating a 1-frame drift visible as ~30-
frame clusters of CSV-snapshot divergence.

**Fix**: a 5-byte delay loop in `emitPlayVoiceStep` before the LAST
voice's JSR (= V1, processed last per voiceOrder `[2,1,0]`):

```
LDX #$14          ; 2 cyc
pad: DEX          ; 2 cyc per iter
     BNE pad      ; 3 cyc taken
```

20 iterations × ~5 cyc = ~101 cycles padded before V1 begins.
That's enough to push V1's freq writes past the VBI boundary into
the next sidplayfp frame — matching the original's timing exactly.
The pad does *not* change engine semantics (py65 still 100%).

The grade rose from B 94.9% to A 98.3% with this one tweak.

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
   Mirrors the original engine's $178B gate. The byte lives at zero-page
   $51 (BIT zp is 1 cycle cheaper than BIT abs). Init leaves it $00;
   set to $FF at every `exec_voice` tail. Each note-load SID write is
   preceded by an inline `BIT $51; BPL +3` gate (see `emitDrumPrioGate`).
   On the very first frame, V3 (first voice) reads $00 from the gate
   and its inst-record SID writes are skipped — matching the original.

5. **Pre-V1 cycle-pad** (B 94.9% → **A 98.3%**). 5-byte delay loop
   (`LDX #$14; loop: DEX; BNE loop`, ~101 cycles) inserted in
   `emitPlayVoiceStep` before the *last* voice's JSR. Pushes V1's
   freq writes past sidplayfp's PAL VBI boundary so they land in
   the next siddump frame — matching the original's per-frame
   write distribution. The pad is cycle-only; engine semantics
   unchanged (py65 still 100%).

## Engine notes

Devils Galop uses the same 1985-era Hubbard driver as Action Biker /
Commando, with a couple of distinctive quirks documented in
`pipelines/hubbard/devils_galop/disassembly.s`:

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

Identical to Commando — see `pipelines/hubbard/commando/README.md` for the
layout explanation.

## How to run

Regenerate `SongData.lean` from the original SID:

```bash
python3 -m pipelines.hubbard.devils_galop.extract            # subtune 0
```

Build and run:

```bash
lake build sidgen_devils_galop
.lake/build/bin/sidgen_devils_galop
```

Grade the rebuild against the original:

```bash
python3 src/writelog_grade.py \
    hvsc85/MUSICIANS/H/Hubbard_Rob/Devils_Galop.sid \
    pipelines/hubbard/devils_galop/build/devils_galop.sid
```

## TODO

* The remaining 26-frame gap (1500 − 1474 at A 98.3%) is a handful of
  late-song note transitions where the cycle-pad doesn't perfectly
  align. The pad value (`LDX #$14`) was chosen empirically; a song-
  specific calibration sweep found it from a {10, 20, 30, 40, 50, 60, 80}
  range. Other Hubbard SIDs cloned from this pipeline may need a
  different value.
* The `Properties.lean` proof times out at `whnf` heartbeat 200000 (a
  Monty-clone artefact, not Devils-Galop-specific); the executable
  builds without it.

## References

* Annotated 6502 disassembly: `pipelines/hubbard/devils_galop/disassembly.s`
* Seed disassembler: `tools/seed_disassembly.py`
