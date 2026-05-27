# The Last V8 (C128 version) pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

Rob Hubbard's *The Last V8 (C128 version)* (1985 MAD/Mastertronic) —
binary at `hvsc84/MUSICIANS/H/Hubbard_Rob/Last_V8_C128_version.sid`.

## Status

| Metric | Value |
|---|---|
| Format | **RSID v2** (NOT PSID — needs real C64 KERNAL, IRQ vector, CIA) |
| Engine | Dual: tracker driver + relocated one-shot sample player |
| Subtunes (header) | 18 |
| Subtunes recovered | **0** — extract identifies layout, codegen is a tombstone |
| Rebuild grade | n/a (tombstone produces a 1-byte RTS payload) |
| Disassembly | `docs/hubbard_last_v8_c128_disassembly.s` ✓ |

This pipeline is honest about what's done. The current state is:

- **Extract** parses the RSID, classifies each subtune, extracts
  sample-player records and music-table addresses, decodes all 28
  patterns + 3 music-subtune orderlists (V0/V1/V2 of subtunes 0-2)
  into structured events, **and lifts all 19 instrument records**
  (pulse, ctrl, ADSR, vibrato shift, PWM, fx-flag bits). ✓
- **Codegen** is a tombstone — it preserves the original PSID metadata
  but emits a 1-byte `RTS` payload. Audio: silent.

A working byte-perfect rebuild is **substantial future work**. See
"What's not done" below.

## Layout (mirrors Commando / Monty)

```
last_v8_c128/
  extract/                      Python
    types.py                      Engine-specific dataclasses (NOT USFSong)
    decompile.py                  RSID parse + dispatcher categorisation
    engine_model.py               extract() facade for callers / tests
    emit_usf.py                   render → codegen/LastV8C128/SongData.lean
    cli.py / __main__.py          CLI entry
  codegen/                      Lean 4
    LastV8C128/
      Asm6502.lean                shared 6502 emission primitives
      PSIDFile.lean               shared PSID v2 file builder
      SID.lean                    shared SID register model
      USF.lean                    placeholder (no USF lift yet)
      Constants.lean              load/init/play addresses of the original
      SongData.lean               AUTO-GENERATED — engine model from extract
      Codegen.lean                generateTombstone (RTS payload)
      Properties.lean             tombstone invariants
      Main.lean                   lake exe entry
  tests/                        pytest tests against the real binary
  build/                        lake output lands here
```

## How to run

Regenerate `SongData.lean` from the original binary:

```bash
python3 -m pipelines.last_v8_c128.extract
# → pipelines/last_v8_c128/codegen/LastV8C128/SongData.lean
```

Build the Lean exe and produce the tombstone PSID:

```bash
lake build sidgen_last_v8_c128
./.lake/build/bin/sidgen_last_v8_c128
# → pipelines/last_v8_c128/build/last_v8_c128.sid (127 bytes)
```

Run the smoke tests:

```bash
PYTHONPATH=tools/py_test_lib tools/py_test_lib/bin/pytest \
    pipelines/last_v8_c128/tests/ -q
```

## What the engine looks like

The disassembly at `docs/hubbard_last_v8_c128_disassembly.s` has the
full annotation; the short version:

* **Load**: `$4800`. **Init**: `$7F40`. **Play**: `$0000` (RSID — the
  init installs a raster IRQ at `$0314/$0315 = $7F73`, sets `$D012=$80`,
  `$D01A=$81`, then CLIs).
* **Subtune dispatch** at `$7E80` (entered with A = subtune):

  | subtune | init route | per-IRQ tick |
  |---|---|---|
  | 0..2  | → `$8C53` (tracker setup) | `JMP $8022` (music driver) |
  | 3..5  | → relocator, then `JSR $C000` (blocking sample play) | `RTS` (noop) |
  | 6..17 | → `$8C85` / `$8C71` (SFX arming) | `JMP $8022` (music driver) |

* **Relocator** at `$7E91` copies four 256-byte pages from
  `$7B40-$7F3F` to `$C000-$C3FF` so the sample player can run from its
  expected address.
* **Sample records** at `$C200,X` with `X = (subtune-2)*4` give
  `(start_lo, start_hi, end_lo, end_hi)`. From this binary:

  | subtune | address span | length |
  |---|---|---|
  | 3 | `$4800-$582F` | 4144 B |
  | 4 | `$5830-$690D` | 4318 B |
  | 5 | `$690E-$7B2F` | 4642 B |

  Samples are clocked 1 bit per CIA2 Timer A wrap (`$DD04`); each bit
  selects between control bytes `$41` (pulse+gate) and `$49`
  (pulse+ringmod+gate) on voice 1. Classic Hubbard digital playback.
* **Music driver** at `$8022-$83B8` walks three voices, reading
  patterns at `$87A9/$87C6` (lo/hi ptr tables), instruments at `$85A1`,
  and a 96-entry freq table at `$843B`. Per-voice state lives at
  `$84xx-$85xx`. The driver runs unmodified for any of the 0..2 and
  6..17 subtunes — only the orderlist pointers in `$8791` and the SFX
  trigger byte at `$8537` change between them.

* **Pattern format** (decoded by extract from the consumer code at
  `$80CF..$816A`). Each pattern is a sequence of records terminated by
  `$FF`. A record's first byte is the *hold byte*:

  | bit | meaning |
  |---|---|
  | 7 | FX byte follows |
  | 6 | tie (no FX, no pitch byte — just sustain) |
  | 5 | no auto-release when hold expires |
  | 4-0 | hold counter (frames at tempo rate) |

  The optional FX byte is an instrument id (bit 7 = 0) or an
  arpeggio/pulse-mode mask (bit 7 = 1). The pitch byte (only present
  on non-tie records) is a 0-95 index into the freq table at `$843B`.
  Orderlists are bytes terminating in `$FF` (restart) or `$FE`
  (end-of-song).

## What's not done

1. **Tempo + per-frame modulators.** The pattern reader is decoded
   and instruments carry their fx-flag bits (portamento / note-cut /
   arpeggio / pulse-arp). What's still implicit is the **tempo
   divisor** (the value latched into `$8527` by the music init at
   `$8C53` — currently read from binary but not yet surfaced in
   `EngineModel`) and the **vibrato / slide / PWM update step
   formulas** at `$8128..$83A2`. These are needed for a faithful
   modulator emit, but a frame-accurate rebuild can start with
   constant-tempo + no-modulator playback first to get pitch/duration
   right, then layer effects.
2. **USF lift.** The pieces now in `EngineModel` (orderlists +
   patterns + instruments + freq table) match the shape of a
   `USFSong` closely enough that lifting subtunes 0-2 is the next
   reasonable step. The Lean codegen still emits a tombstone; a real
   `generateSID` needs to either reuse the V3 codegen (after writing
   an `EngineModel → USFSong` adapter) or emit a fresh tracker
   directly from `EngineModel`.
2. **Sample-player rebuild.** The 1-bit DAC loop is CIA-cycle-precise
   and very different from a `USFSong`. A faithful rebuild needs a
   dedicated emitter that allocates the same `$4800-$7B2F` sample
   region in the rebuilt PSID and emits the bit-loop with matching CIA
   timing.
3. **RSID emit.** The current PSIDFile.lean writes PSID magic. A real
   rebuild would need RSID output (different magic, no PSID `play`
   field, more strict environment expectations).
4. **A working grading run.** With no actual player code, `siddump
   --writelog` against the original will diverge from frame zero.

## Why not just clone Monty here

The original first-pass scaffolding for this SID copied the Monty
pipeline wholesale. That clone was misleading: README claimed
"Grade A 98.8% snapshot match", tests asserted Monty's 20 instruments
and skydive flags on instruments 10/12/13, and the codegen had inline
comments referencing Monty quirks. None of those facts apply to Last V8.

This pipeline is the *replacement* — a smaller, honest scaffold that
matches the directory layout of Commando/Monty so future work can grow
into it, but does not pretend to do anything it doesn't.

## See also

* `docs/hubbard_last_v8_c128_disassembly.s` — annotated 6502 of the
  whole binary, including the relocated `$C000` sample player.
* `docs/hubbard_1985_status.md` — top-level status of all 17 Hubbard
  1985 pipelines.
