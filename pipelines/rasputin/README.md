# Rasputin on the Run pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild of Rob Hubbard's *Rasputin on the Run* (1985) SID.
Same shape as the Commando pipeline; the bulk-clone scaffold from
commit cbb86f6 plus several Rasputin-specific engine fixes documented
below.

See `docs/hubbard_rasputin_disassembly.s` for a 1008-line hand-annotated
6502 disassembly that documents the engine's outer/inner counter pair,
the `$FE`/`$FD`/`$FF` orderlist markers, and the fx_flags bit layout
(bit 0 = skydive, bit 1 = waveform shimmer, bit 2 = arpeggio +0/+12,
bit 3 = PWM linear vs bidirectional).

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 1 (PSID #1, the title music) |
| Verification | siddump writelog grade |
| Grade | D (67.0%, 1005/1500 snapshots matching) |

The remaining ~33% snapshot gap is mostly cycle-accuracy drift: our V2
player codegen emits straightforward LDA/STA sequences that run ~600+
cycles longer per frame than Hubbard's hand-tuned engine, so a few SID
register writes per note land in the next snapshot frame. The actual
SID output is correct semantically — the sequence of (freq, ctrl, pw,
ad/sr) writes matches, but the timing within each PAL frame doesn't.
Closing to Grade A would require cycle-tuned codegen or a more
jitter-tolerant grader.

The original PSID claims 19 subtunes; PSID #2 is a second music track
(same engine, A=1 to `init`) and the remaining 16 are sound effects
that share register space with the music engine (A=2..17 trigger the
`$CFA1` SFX-init path). This pipeline only rebuilds the title music.

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the
layout explanation. The Rasputin-specific differences:

| File | Rasputin-only addition |
|---|---|
| `codegen/Rasputin/USF.lean` | `shimmer : Bool` field + `subFrameDivider : Option USFByte` in `USFEngineQuirks` |
| `codegen/Rasputin/Codegen.lean` | Sub-frame divider play prelude (DEC/BPL/reload/RTS for 1-in-(N+1) SFX-only frames); waveform shimmer emit block (EOR ctrl `$18` every 2 music frames); skydive Path-A threshold `v_durfield - 3`; arpeggio reads bit 1 (not bit 0) of frame counter |
| `extract/decompile.py` | `$FE` orderlist marker treated as speed-change (consume next byte, continue) not "stop"; `$FD` as song-end |
| `extract/engine_model.py` | Tempo derived from py65 post-init steady-state ($C53B inner + $C539 outer); `subFrameDivider` stashed on Score for emit_usf |
| `extract/emit_usf.py` | Emits `shimmer := true/false`; injects `subFrameDivider := some ⟨N, by omega⟩` into engineQuirks |

## How to run

Regenerate `SongData.lean` from the original — by default rebuilds subtune 0
(the title music PSID #1). Pass comma-separated 0-indexed subtune numbers
to override:

```bash
python -m pipelines.rasputin.extract.emit_usf            # subtune 0 only
python -m pipelines.rasputin.extract.emit_usf 0,1,2       # all three music tracks
```

Build and run:

```bash
lake build sidgen_rasputin
./.lake/build/bin/sidgen_rasputin
```

Grade against the original:

```bash
python3 src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Rasputin.sid \
    pipelines/rasputin/build/rasputin.sid
# Expected: Grade D, snapshots 67.0% (1005/1500)
```

## Why a separate pipeline from Commando

Two Hubbard SIDs from the same player era still differ in load-bearing
ways (PW bounds, pulsedelay init, fx-flag semantics). Cloning the
pipeline rather than parameterising it kept the Commando byte-perfect
invariant safe while Rasputin was being developed. The two pipelines can
be merged once a third Hubbard SID is wired through to validate the
abstraction.

See also: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_notenum_overlap.md`
and `reference_hubbard_pwm_bounds.md` for the load-bearing quirks.
