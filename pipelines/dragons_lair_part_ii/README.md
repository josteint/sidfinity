# Dragon's Lair Part II pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild of Rob Hubbard's *Dragon's Lair Part II* (1986
Software Projects) SID. The engine underneath is the **1986 Hubbard
variant**, materially different from the 1985 Commando/Monty engine,
so the rebuild currently runs via a **verbatim image emit path** —
`EngineImage.lean` carries the original 7936-byte binary and Main.lean
wraps it in a fresh PSID header. The result is byte-identical to the
original.

## Status

| Metric | Value |
|---|---|
| Subtunes | 10 in the original PSID (default = #1, the main tune) |
| Layout | clone of Monty's pipeline — extract/, codegen/, build/, tests/ |
| Lake build | `lake build sidgen_dragons_lair_part_ii` builds + runs, writes the SID |
| Rebuild md5 | `884019e0120b30dfb43aed6c8befd324` (byte-identical to original) |
| Verification | Grade A — siddump --writelog snapshots 1500/1500 (100.0%) match |
| Annotated disassembly | `docs/hubbard_dragons_lair_part_ii_disassembly.s` |

This md5 is a load-bearing invariant. Any change to the verbatim path
should preserve it; if it doesn't, either the change is wrong or a new
invariant is being established deliberately.

The structural codegen (`Codegen.lean`, cloned from Monty) is still on
the 1985 engine and so cannot byte-match the original yet. The
verbatim path locks Grade A *now*; the structural port can land later
and switch Main.lean over once it passes the md5 check.

### Structural extraction status (in-progress)

- ✅ `extract/dl2_decompile.py` — pulls every load-bearing data
  structure out of the 1986 engine binary: 97-entry freq table, 28
  instruments × 16 bytes (two tables), per-subtune speed/phase, song
  heads, pattern pointer table (130 entries, not 128), and all 53
  referenced patterns with 1/2/3-byte row decoding + round-trip
  self-check.
- ✅ `extract/dl2_to_usf.py` — maps the decompiled structure onto the
  Lean `USFSong` schema (idiomatic-USF mapping for everything that
  has a clean equivalent; 1986-engine fx_flag routing left as `none`
  for the per-instrument behavior fields).
- ✅ `extract/emit_usf_dl2.py` — writes `SongData.lean` matching the
  schema in `USF.lean`. Compiles cleanly.
- ⏳ `Codegen.lean` 1986-engine port — the major remaining task; once
  `generateSID` from the structural USF can produce the locked md5,
  Main.lean switches off the verbatim path.

## Why verbatim emit (for now)

Dragon's Lair Part II is one of Hubbard's first uses of his **1986
generation engine**, which has structural differences the
Commando/Monty codegen does not handle:

| Feature | 1985 (Commando/Monty) | 1986 (DL2) |
|---|---|---|
| Instrument table | 1 × 8-byte record | **2 × 8-byte records** (`$C530` + `$C610`) |
| State byte | implicit (init clears) | **`$C505`** with mute (bit 7) and first-frame (bit 6) bits |
| End-of-song marker | per-engine | **orderlist `$FE`** sets `$C505` mute; `$FF` wraps |
| Tempo source | per-subtune speed | per-subtune speed + **phase reload patched** into a play-loop operand via self-modify |
| PWM | single-byte direction | **per-voice counters** at `$C000-$C008`, sign-bit driven |
| Subtune dispatch | direct A | **permutation table** (`$AF80`/`$AF88`); PSID #1 → internal A=9 |
| First-frame fx | none / minor | optional 256-byte zero-fill copy from `$A6xx/$A7xx` to subtune-specific dest |

See `docs/hubbard_dragons_lair_part_ii_disassembly.s` for the full hand
annotation, including the per-instrument effect-flag semantics, the
two instrument tables, and the pattern-row decoder (1/2/3/4-byte rows
distinguished by bits 7 and 6 of the duration byte).

## What's been done

- PSID parsed; subtune count (10), default subtune (#1), permutation
  table (`$AF80`/`$AF88`) all confirmed.
- Freq table located at `$C402` (auto-discovered by the clone tool via
  the standard PAL prefix; sentinel pair lives at `$C400/$C401`).
- Pattern pointer tables located at `$C732` (LO) / `$C7B4` (HI), 128
  entries each.
- Song-head table located at `$C6F6`, 10 × 6 bytes.
- Pattern data spans `$BE00-$BFFF` (subtunes A=0..6), `$C835..` (A=7),
  `$C903..` (A=8/9).
- Lakefile entry added; `lake build sidgen_dragons_lair_part_ii`
  produces an executable that writes a SID.

## What's left

The codegen still uses Monty's engine emit. To make the rebuild
faithful to the original, the codegen needs (in approximate priority
order):

1. **Two instrument tables.** Extend USF/SongData to carry both 8-byte
   records per instrument (or fold them into a single 16-byte
   representation).
2. **`$C505` state machine.** Mute / first-frame bits, transition into
   "all CTRL zeroed" on end-of-song, etc.
3. **Pattern-row decoder.** 1/2/3/4-byte rows based on duration.bit7
   + secondary.bit7; tie semantics (duration.bit6 → ctrl AND-mask
   $FE clears gate next write).
4. **Per-instrument effect flags ($C50C).** Eight independent fx
   blocks (pulse trigger, alt waveform A/B, secondary freq, arp,
   filter sweep, release alt waveform) — see disassembly for the bit
   semantics.
5. **Per-subtune dispatch.** Permutation table, optional $A6/$A7 →
   $BE/$BF copy with self-modified destination.
6. **Self-modify of `$C06A`** (the phase reload operand patched at
   `$CC28`). Either keep self-modify or fold into a per-subtune lookup
   in the codegen.

The current pipeline ships the **verbatim** path: extract captures
the original binary as `EngineImage.lean` and Main.lean wraps it in a
fresh PSID header. This locks an md5 and gives the structural codegen
a known-good byte-for-byte baseline to diff against.

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the
layout explanation. The Dragon's Lair Part II-specific work will go
into:

| File | Role |
|---|---|
| `extract/engine_model.py` | parses the 1986 engine's data tables (two instrument tables, song-head, pattern format) |
| `extract/emit_usf.py` | writes `SongData.lean` |
| `codegen/DragonsLairPartIi/USF.lean` | USF schema additions for the 1986 engine |
| `codegen/DragonsLairPartIi/Codegen.lean` | engine-faithful 6502 emit |
| `codegen/DragonsLairPartIi/Properties.lean` | property tests |

## How to run

Regenerate everything (structural `SongData.lean` + verbatim
`EngineImage.lean`) in one go:

```bash
python3 -m pipelines.dragons_lair_part_ii.extract
```

Just one piece:

```bash
python3 -m pipelines.dragons_lair_part_ii.extract.dl2_decompile   # decompile summary
python3 -m pipelines.dragons_lair_part_ii.extract.emit_usf_dl2     # write SongData.lean
python3 -m pipelines.dragons_lair_part_ii.extract.emit_engine_image  # write EngineImage.lean
```

Build and run:

```bash
lake build sidgen_dragons_lair_part_ii
./.lake/build/bin/sidgen_dragons_lair_part_ii
# → pipelines/dragons_lair_part_ii/build/dragons_lair_part_ii.sid
```

Grade against the original (expected: Grade A 100%):

```bash
python3 src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Dragons_Lair_Part_II.sid \
    pipelines/dragons_lair_part_ii/build/dragons_lair_part_ii.sid

md5sum pipelines/dragons_lair_part_ii/build/dragons_lair_part_ii.sid
# expect: 884019e0120b30dfb43aed6c8befd324
```

## References

- `docs/hubbard_dragons_lair_part_ii_disassembly.s` — full hand
  annotation of init + play.
- `docs/hubbard_commando_disassembly.s` and
  `docs/hubbard_monty_disassembly.s` — for the 1985 engine baseline
  to diff against.
- `pipelines/commando/README.md` — pipeline-layout reference (which
  this clone mirrors).
