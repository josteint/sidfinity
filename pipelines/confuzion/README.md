# Confuzion pipeline

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end byte-perfect rebuild of Rob Hubbard's *Confuzion* (1985
Incentive) SID. The pipeline emits a Lean program that consumes USF
data (`SongData.lean`) and synthesizes a SID file byte-identical to
the original at md5 `680cc6ec4c157d23400700ffae35fb49`.

## Status

| Metric | Value |
|---|---|
| Subtunes rebuilt | 1 (PSID claims 1; single-shot tune with no orderlist loop) |
| Byte-equality | md5 match with original `Confuzion.sid` |
| Writelog grade | A — 1500/1500 snapshots (100%) |
| Build / run | `lake build sidgen_confuzion` → `pipelines/confuzion/build/confuzion.sid` |
| USF round-trip | song data (freq table, instruments, orderlists, patterns) ✓ |

## Engine model

Confuzion's player loads at `$0858` and is structurally a raster-IRQ
handler. Init at `$0867` does self-modifying patching to turn it into
a PSID-callable subroutine (patches `CLI`→`RTS`, `SEI`→`NOP`, and
`JMP $EA81` (KERNAL IRQ exit) →`RTS`). The annotated disassembly is
`docs/hubbard_confuzion_disassembly.s`; key behaviors:

- `$A2` is repurposed as a per-call frame counter via self-modifying
  immediate at `$085C` (driving the triangle-LFO vibrato).
- Note-load gate at `$0BE8 == $0BE9` (tick reload value, = speed).
- HR threshold = 0: at duration end, gate cleared AND envelope zeroed.
- Master vol = clamp(`$A0 - $0BC2`, `$0F`).
- PWM bounds `$08`/`$0E` (Hubbard post-1986 hardcoded thresholds).
- No skydive / drum / table-arp — stripped-down classic engine.
- Single-shot orderlist: first voice to hit `$FF` triggers song-end.

## Codegen architecture

`pipelines/confuzion/codegen/Confuzion/Codegen.lean`'s `generateSID`
emits the 2382-byte payload as a concatenation of:

| Bytes | Region | Source |
|---|---|---|
| 677 | `$0858-$0AFC` engine code | verbatim literal extracted from original |
| 192 | `$0AFD-$0BBC` freq table | `song.freqTable.entries[0..96]` |
| 3 | `$0BBD-$0BBF` voice base offsets | constants `[$00, $07, $0E]` |
| 49 | `$0BC0-$0BF0` voice-state RAM seed | verbatim literal (engine RAM init) |
| 6 | `$0BF1-$0BF6` orderlist pointers | layout `orderlistAddrs` |
| 60 | `$0BF7-$0C32` pattern_lo/hi tables | layout `patternAddrs` |
| 241 | `$0C33-$0D23` V1/V2/V3 orderlists | `song.subtunes[0].voices[*].orderlist` |
| 1058 | `$0D24-$1145` pattern bytes | `song.patterns` via USF→Hubbard encoder |
| 96 | `$1146-$11A5` instrument table | `song.instruments` fields |

PSID header: `loadAddr=0` (embedded form), `embeddedLoad=$0858`,
`initAddr=$0867`, `playAddr=$0858`, `speed=1` (CIA-driven, matches
original), `flags=$0014` (PAL + 6581).

## USF→Hubbard pattern encoder

`encodeNote` maps `USFNoteEvent` to Hubbard row bytes:

| Hubbard cmd bit | USF source |
|---|---|
| bit 7 (new_inst) | NOT (USF `instrument` bit 7) |
| bit 6 (tie) | `kind = .tie` OR USF `instrument` bit 6 |
| bit 5 (no_release) | USF `instrument` bit 5 |
| bits 0-4 (dur) | `(durationFrames / tempo) - 1` |

Then optionally an inst byte (if new_inst), optionally a pitch byte
(if not tie), and an `$FF` terminator after the last row of each
pattern. Validated round-trip on all 25 live patterns.

## How to run

```bash
# (One-time per source change) regenerate SongData.lean from the SID:
python3 -m pipelines.confuzion.extract.emit_usf

# Build and run the codegen:
source src/env.sh
lake build sidgen_confuzion
./.lake/build/bin/sidgen_confuzion          # writes pipelines/confuzion/build/confuzion.sid

# Verify byte-perfection:
md5sum pipelines/confuzion/build/confuzion.sid \
       hvsc84/MUSICIANS/H/Hubbard_Rob/Confuzion.sid

# Verify writelog grade:
python3 src/writelog_grade.py \
    hvsc84/MUSICIANS/H/Hubbard_Rob/Confuzion.sid \
    pipelines/confuzion/build/confuzion.sid
# Grade A, 1500/1500 snapshots
```

## Differences from Commando / Action Biker

The Commando pipeline assembles its player from scratch in Lean
(`Asm6502.lean` + emit functions in `Codegen.lean`), producing a SID
that loads at `$C000` with its own self-consistent engine. Confuzion
keeps the original 677-byte engine code as a verbatim literal because
re-deriving it from Lean would only change which bytes encode the
same machine code without affecting correctness — and we'd lose md5
match in the process. The structural difference (load address,
self-modifying init, raster-IRQ shape) made the inherited Commando-
style codegen impossible to adapt; Confuzion needs its own engine.

See `docs/hubbard_confuzion_disassembly.s` for the engine specifics
and `docs/hubbard_1985_status.md` for cross-pipeline context.
