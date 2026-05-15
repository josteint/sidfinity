# Crazy Comets pipeline

End-to-end rebuild of Rob Hubbard's *Crazy Comets* (1985 Martech) SID.
Original is parsed, lifted into structured USF, then re-emitted as a
fresh PSID driven by our own V3 player. Same shape as the Commando and
Monty pipelines.

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 2 (PSID #1 + #2, the two music tracks; subtunes 2-16 are SFX, not shipped) |
| Build | end-to-end clean: `python -m pipelines.crazy_comets.extract.emit_usf 0,1` → `lake build sidgen_crazy_comets` → SID at `pipelines/crazy_comets/build/crazy_comets.sid` |
| Grade | F (58/1500 snapshots, 3.9%) — starting state, not byte-faithful |

This is the **bring-up state** of the pipeline: scaffolding is in place,
the Hubbard binary parses, the Lean codegen produces a SID, and grading
runs. The rebuild does not yet match the original musically — see
**Known divergences** below.

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
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Crazy_Comets.sid \
    pipelines/crazy_comets/build/crazy_comets.sid
# Currently: Grade F, snapshots 58/1500 (3.9%)
```

## Known divergences (work items)

The Codegen.lean is a near-copy of Commando's (~200 lines diff out of
1638). Crazy Comets's player at $500C..$540C extends Action Biker's
engine in three structural ways that the codegen does not yet model;
this is where most of the F-grade frame-by-frame mismatch comes from.

1. **Arpeggio / freq-slide block at $52A7.** New per-voice state at
   `$5501,X` (v_freq_lo) and `$5504,X` (arp_dir flags) drives a
   per-frame additive freq slide. Bit 0 of `$5504,X` picks direction
   (ADD/SUB); bits 1-6 are step amount ×2. The slide is enabled by an
   optional second pattern byte with bit 7 set on note-load (where
   Action Biker would have placed an inst-change byte). Not in the
   codegen.

2. **fx-flags bit 1 slow freq-down ($532A).** When the instrument's
   `fx_flags` bit 1 is set, the note's original duration is >= $11,
   and the global frame counter's bit 0 is set, decrement v_fhi by 1.
   Half-speed companion to the drum slide. Not in the codegen.

3. **fx-flags bit 2 octave-arp ($534F).** Alternates between
   freq\[pitch\] and freq\[pitch+12\] every other frame — a coarse
   two-note octave trill. Not in the codegen.

Also non-trivial but lower priority:

4. **Dual-engine init dispatch.** `init` at $6100 compares A to 2:
   `A < 2` → music engine (`$5000` → `$60A7`); `A >= 2` → SFX engine
   (`$5009` → `$60DE` then `$5003` → `$60D8`). Only the music path is
   handled today; SFX subtunes are silent.

5. **Mid-PWM "monotonic" path at $5222.** `fx_flags` bit 3 = simple
   `pw_lo += vib_period | $40` with no bounds check or direction
   flip (the normal $5240+ PWM applies the $08/$0E bounds). Not in
   the codegen.

6. **SFX engine ($539B-$540C + sub_5514).** Self-modifies opcode at
   $53C5 between `INC` and `DEC` based on descriptor flags, bulk-copies
   14 descriptor bytes into $D400.. as voicing seed, toggles V1/V2
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
