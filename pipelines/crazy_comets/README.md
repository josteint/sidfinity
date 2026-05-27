# Crazy Comets pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild of Rob Hubbard's *Crazy Comets* (1985 Martech) SID.
Original is parsed, lifted into structured USF, then re-emitted as a
fresh PSID driven by our own V3 player. Same shape as the Commando and
Monty pipelines.

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 2 (PSID #1 + #2, the two music tracks; subtunes 2-16 are SFX, not shipped) |
| Build | end-to-end clean: `python -m pipelines.crazy_comets.extract.emit_usf 0,1` → `lake build sidgen_crazy_comets` → SID at `pipelines/crazy_comets/build/crazy_comets.sid` |
| Grade | C (1314/1500 snapshots, 87.6%) — V1 89.5% / V2 98.5% / V3 99.4% per voice |

## Recent progress

Started at Grade F 3.9% on bulk-clone scaffold. Reached Grade C 87.6%
via four targeted fixes derived from the annotated disassembly:

1. **`initialDur := 1`** (3.9% → 7.4%). Crazy Comets's tick divider
   ($54FA/$54FB at $5054-$5061) gates note-load to every 3rd frame
   starting from frame 1. Seeding v_dur=1 in init makes the first DEC
   take the sustain branch so note-load fires on play-frame 1 like
   orig.

2. **Binary-loaded effect cache** (7.4% → 61.8%). Hubbard's first-frame
   init at $5016 zeroes v_olpos/v_patpos/v_dur/v_pitch but NOT v_inst
   or v_fhi — the binary's load image (v_inst=[$01,$13,$10],
   v_fhi=[$00,$01,$06]) flows into frame-0 effects. Seeded these in
   Codegen.lean's data section.

3. **HR threshold v_dur==2** (61.8% → 72.5%). Crazy Comets's 3-frame
   tick divider means Hubbard's "v_dur==0 in ticks" maps to
   "v_dur==2 in our per-frame v_dur" — HR fires 3 frames before
   note-load, not 2.

4. **Skydive duration gate** (72.5% → 87.6%). Hubbard's $532A slow
   freq-down also requires `(v_flags & $1F) >= $11` (note duration
   ≥ 17 ticks). The codegen's skydive block was firing on short
   notes that should hold steady; added CMP #51 (= 17 × tempo).

The original PSID claims 17 subtunes; the other 15 are sound effects
this pipeline doesn't ship yet (the SFX engine at $539B + sub_5514 is
unimplemented — see disassembly).

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the
layout walkthrough. Crazy-Comets-specific bits live in:

| File | Crazy-Comets-only content |
|---|---|
| `extract/engine_model.py` | `SID_PATH` points at `Crazy_Comets.sid`; `has_skydive` propagated from fx_flags bit 1 |
| `extract/emit_usf.py` | `CRAZY_COMETS_FT_BASE = 0x540F` (freq table); 2-subtune default (subtunes 0 + 1); `engineQuirks.dynamicFreqEntries = []` |
| `codegen/CrazyComets/USF.lean` | `skydive` field on `USFInstrument` |
| `codegen/CrazyComets/Codegen.lean` | Skydive emit block; v_pitch alias-store; PWM bounds $08/$0E |

The annotated disassembly that drives engine understanding is at
`docs/hubbard_crazy_comets_disassembly.s` (1027 lines: full reachable
disassembly from init+play with hand-annotated commentary on the
dual-engine architecture, freq/inst tables, and the three new effect
blocks not present in Action Biker).

## How to run

Regenerate `SongData.lean` from the original (default = both music
subtunes; pass `0` for just the first):

```bash
python -m pipelines.crazy_comets.extract.emit_usf            # 0,1
python -m pipelines.crazy_comets.extract.emit_usf 0          # subtune 0 only
```

Build and run:

```bash
lake build sidgen_crazy_comets
./.lake/build/bin/sidgen_crazy_comets
```

Grade against the original:

```bash
source src/env.sh
python3 src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Crazy_Comets.sid \
    pipelines/crazy_comets/build/crazy_comets.sid
# Currently: Grade C, snapshots 1314/1500 (87.6%)
```

## Remaining divergences (work items)

V2 (98.5%) and V3 (99.4%) are essentially solved. V1 (89.5%) carries
all remaining gap and is dominated by FREQ_LO/FREQ_HI write-timing
drift (one-frame phase offset in some vibrato/arpeggio sequences).
Candidate root causes, lowest-risk first:

1. **Drum-slide ($52EE) duration gate.** Symmetric to the skydive
   fix we just applied: Hubbard's drum-slide block reads v_flags,
   v_fhi, v_dur sentinel checks but our codegen's freqSlide block
   ignores the raw-duration field. Add `v_durfield >= 51` (= 17 × 3)
   to the bit0 path at line 1126.

2. **Arpeggio at $52A7 (NEW vs Action Biker).** Per-voice state at
   `$5501,X` / `$5504,X` drives a per-frame additive freq slide. Set
   from optional 2nd pattern byte with bit 7 set on note-load. The
   codegen's pattern extraction (extract/decompile.py) may swallow
   that byte as an inst-change byte, mis-numbering instruments later.

3. **fx-flags bit 2 octave-arp at $534F.** Alternates freq[pitch] and
   freq[pitch+12] every other frame. The codegen has arpeggio with
   intervals=[0,12] but does not gate on a duration threshold; orig
   may have an analogous gate.

Out-of-scope for the music subtunes 0/1 but documented for completeness:

4. **Dual-engine init dispatch.** `init` at $6100 compares A to 2:
   `A < 2` → music engine; `A >= 2` → SFX engine. Only the music path
   is wired; SFX subtunes 2-16 are silent.

5. **Mid-PWM "monotonic" path at $5222.** `fx_flags` bit 3 = simple
   `pw_lo += vib_period | $40` with no bounds. Not in the codegen.

6. **SFX engine ($539B-$540C + sub_5514).** Self-modifies opcode at
   $53C5, bulk-copies 14 descriptor bytes into $D400.., toggles V1/V2
   gates each step. Disjoint from the music engine and unimplemented.

See `docs/hubbard_crazy_comets_disassembly.s` HIGH-LEVEL FLOW for the
state-block mapping vs Action Biker and the per-block walkthrough each
of the items above ties back to.

## Why a separate pipeline from Commando / Monty / Action Biker

Hubbard's 1985 player ships in subtly-incompatible binaries across
these SIDs: PWM bounds, fx-flag semantics, first-frame init quirks,
extra effect blocks, and (for Crazy Comets) a co-resident SFX engine
all differ. Cloning the pipeline rather than parameterising it keeps
the byte-perfect Commando invariant locked while Crazy Comets is being
brought up. The pipelines can be merged once Crazy Comets grades A.

See also: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
and `reference_hubbard_pwm_bounds.md`.
