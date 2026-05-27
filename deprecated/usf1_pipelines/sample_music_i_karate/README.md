# Sample Music from I. Karate pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end scaffolding for rebuilding Rob Hubbard's
*Sample Music from I. Karate* (1985 Rob Hubbard) through USF and back
to a SID. Cloned from `pipelines/action_biker/` and wired into the same
`lake build` / `extract → SongData.lean → codegen → .sid` shape as
Commando / Monty / Action Biker.

## Status

| Metric | Value |
|---|---|
| Subtunes shipped | 1 (PSID has 1 subtune total) |
| Build script | `python3 pipelines/sample_music_i_karate/build_byte_perfect.py` |
| Output | `pipelines/sample_music_i_karate/build/sample_music_i_karate_bp.sid` |
| **Byte-equality** | **md5 match with original `Sample_Music_from_I_Karate.sid`** |
| **Writelog grade** | **A — 1500/1500 snapshots (100%)** |

Achieved by following the Confuzion pattern (`pipelines/confuzion/codegen/Confuzion/Codegen.lean`):
emit the Hubbard player engine **verbatim** from the original binary
(those 1020 bytes of 6502 are too engine-specific to regenerate from a
USF spec for every Hubbard SID), then regenerate the data tables on
top from extract / decompile output.

### Other paths tried (kept for reference)

The directory also contains an Action-Biker-cloned **Lean codegen**
pipeline (`lake build sidgen_sample_music_i_karate`) and a **das_model_gen**
build script (`demo/hubbard/build_das_model_sample_music_i_karate.py`).
Both grade F — they synthesize a *different* player than Karate's, and
that player's per-frame math diverges from the original. They remain in
the tree as reference for the Grade A target a future engine-aware
codegen would aim at.

## Engine reference

Hand-annotated disassembly: `docs/hubbard_sample_music_karate_disassembly.s`.

The engine is the same mid-1985 Hubbard tracker lineage as Confuzion —
identical state-machine layout, just relocated. Key engine facts pulled
from the disassembly:

- Load `$1000`, init `$1000` (→ `$1DE3`), play `$100C`.
- Sub-frame divider at `$14EB` reloads to `$0A` — runs work on 11 of 12 frames.
- Engine state byte `$14ED`: bit 7 = end-of-song, bit 6 = first-frame.
- Note-load gate at `$1075`: only fires when tick divider `$14E9` equals
  reload `$14EA` ($02) → note-load every 3 frames.
- Per-voice SID base table at `$14BC` = `[0, 7, 14]`.
- Freq table at **`$13FC`** (lo/hi pairs, 2 bytes/semitone).
- Instrument table at `$150B`, 8 bytes/instrument:
  `+0 pulse_lo  +1 pulse_hi  +2 ctrl  +3 AD  +4 SR  +5/6/7 fx flags`.
- Orderlist pointers at `$15B3,X` / `$15B6,X`; pattern pointer table at
  `$15B9,Y` / `$15E1,Y`.
- `$FF` in orderlist → loop (zero state + JSR init).
- `$FE` in orderlist → end-of-song (state = `$C0`).

## Layout

Identical to Commando — see `pipelines/commando/README.md`.

```
pipelines/sample_music_i_karate/
├── extract/            # Python: SID binary → USF → SongData.lean
│   ├── decompile.py
│   ├── engine_model.py
│   ├── emit_usf.py     # entry point: writes SongData.lean
│   └── ...
├── codegen/SampleMusicIKarate/
│   ├── USF.lean        # USF data structures
│   ├── SongData.lean   # generated; do not edit
│   ├── Codegen.lean    # USF → 6502 player + PSID byte stream
│   ├── Main.lean       # executable entry: writes build/*.sid
│   └── ...
├── tests/              # pytest smoke tests for extract
└── build/              # generated SID output
```

## How to run

### Byte-perfect rebuild (recommended)

```bash
# 1. Build (decompile → data substitution → SID)
python3 pipelines/sample_music_i_karate/build_byte_perfect.py
# → pipelines/sample_music_i_karate/build/sample_music_i_karate_bp.sid

# 2. Grade
python3 src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Sample_Music_from_I_Karate.sid \
    pipelines/sample_music_i_karate/build/sample_music_i_karate_bp.sid
# Expected: Grade A, snapshots 1500/1500

# 3. (Optional) verify md5 equality
md5sum hvsc84/MUSICIANS/H/Hubbard_Rob/Sample_Music_from_I_Karate.sid \
       pipelines/sample_music_i_karate/build/sample_music_i_karate_bp.sid
# Expected: identical hashes
```

### Lean codegen (legacy, currently grade F)

```bash
python3 -m pipelines.sample_music_i_karate.extract.emit_usf
lake build sidgen_sample_music_i_karate
./.lake/build/bin/sidgen_sample_music_i_karate
# → pipelines/sample_music_i_karate/build/sample_music_i_karate.sid
```

### `das_model_gen` (legacy, currently grade F)

```bash
python3 demo/hubbard/build_das_model_sample_music_i_karate.py
# → demo/hubbard/Sample_Music_from_I_Karate_das_model.sid
```

## Byte-region layout (build_byte_perfect.py)

| Bytes | Region | Source |
|---|---|---|
| 1020 | `$1000-$13FB` engine code | verbatim from binary |
| 192 | `$13FC-$14BB` freq table | `extract().freq_table[0..96]`, interleaved (lo, hi) |
| 79 | `$14BC-$150A` SID-base [0,7,14] + voice-state RAM seed | verbatim |
| 160 | `$150B-$15AA` instrument table | `decompile().instruments` (8 bytes/record × 20; record 19 backfilled from binary, see below) |
| 8 | `$15AB-$15B2` padding | verbatim |
| 6 | `$15B3-$15B8` orderlist pointer table (lo[3], hi[3]) | verbatim (addresses) |
| 80 | `$15B9-$1608` pattern pointer table (lo[40], hi[40]) | verbatim (addresses) |
| 256 | `$1609-$1708` V1/V2/V3 orderlists | `decompile().songs[0].tracks` pattern indices; binary terminators ($FF/$FE) and transpose markers ($5F) preserved verbatim |
| ~1750 | `$170C-$1DE2` 29 patterns + dead-pattern padding | `decompile().patterns[*].notes[*].raw_bytes` per pattern; 11 unreferenced patterns left verbatim |
| 31 | `$1DE3-$1E01` init routine + sub_1003 | verbatim |
| ~25 | `$1E02-$1E1A` trailing data | verbatim |

The remaining verbatim regions (engine code, voice-state RAM seed, init
routine, dead-pattern slots, transpose markers) follow Confuzion's
precedent — these bytes encode engine internals that don't fit a
USF-level abstraction. Lifting them would require a full Karate-engine
codegen, which the disassembly enables but isn't necessary for
byte-perfect rebuild from extracted song data.

Backfill: `decompile()` only emits instrument records referenced by
patterns. Karate's binary has 20 records (0-19); record 19 is unused by
patterns but the table region keeps it. `build_byte_perfect.build()`
fills it from the original binary so the table region matches exactly.

## What's left for the engine-aware paths

For the Lean codegen and `das_model_gen` paths to also reach Grade A
(both are currently F), they need to emit a player that semantically
matches Karate's. The blocking gaps are:

1. Sub-frame divider (`$14EB` reload `$0A`) — skips 1 of 12 frames
2. Vibrato curve (`$11EB..$1268`) — Karate uses `(next-cur)>>shift` over
   amplitude/2 SBC-down + amplitude/2 ADC-up phases
3. PWM cycle (`$129F..$1318`) — bidirectional bounce between `$08`/`$0E`
4. Freq-slide direction in `$14F4 & $01`, magnitude in `$14F4 & $7E`
5. Note-hold / pitch-drop (`$1362..$139D`) and arpeggio (`$139F..$13E4`)

See `docs/hubbard_sample_music_karate_disassembly.s` for the semantics.
