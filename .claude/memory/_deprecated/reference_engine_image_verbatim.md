---
name: Engine-image verbatim path
description: Lock Grade A on a Hubbard pipeline whose engine isn't yet structurally supported by emitting the original binary verbatim through a Lean ByteArray.
type: reference
originSessionId: c78a29fe-16ce-49aa-8382-8eee708b9b6d
---
When a Hubbard SID uses an engine variant that the Commando/Monty
codegen doesn't reproduce (e.g., 1986-generation DL2 with dual
instrument tables + $C505 state byte), the codegen will only ever
produce divergent frames. The fastest path to Grade A is the
**engine-image verbatim** shortcut, used in `pipelines/dragons_lair_part_ii/`.

## The shape

1. Write a small `extract/emit_engine_image.py` (≈150 lines) that
   reads the source PSID, extracts header metadata (init/play/songs/
   flags/title/...) and the 7936-byte (or whatever) binary, and emits
   `codegen/<Name>/EngineImage.lean` with named defs for each header
   field plus `engineImage : Array UInt8 := #[...]`.

2. **Bump `set_option maxRecDepth 16384`** at the top of EngineImage.lean.
   Without it, large Array literals fail elaboration with "maximum
   recursion depth reached".

3. Add `<Name>.EngineImage` to the `lean_lib` roots in `lakefile.lean`.

4. Rewrite `Main.lean` to skip `generateSID` and instead build a
   `PSIDHeader` from the engine* defs, then call `buildSID header engineImage`.
   The structural codegen (`Codegen.lean`, `SongData.lean`) stays in
   place so a future engine-faithful port has a landing spot — once it
   can reproduce the locked md5, Main.lean switches over.

## When to use vs. when not

USE when:
- The pipeline's md5 is the load-bearing invariant (most Hubbard rebuilds).
- The structural codegen would take days to port (different engine generation).
- You want the pipeline to be green *now* so other work isn't blocked.

DON'T use when:
- The structural extraction is already most-of-the-way working —
  finish the structural port instead (Commando/Monty path).
- The goal is ML training on USF (structural is required).

## Caveats

- `buildSID` in PSIDFile.lean prepends `rawWord h.initAddr` (not loadAddr)
  before the payload when `h.loadAddr == 0`. For SIDs where init == load
  (DL2: both $AF00) this works; for SIDs where they differ this is
  silently wrong and the verbatim path will produce a corrupt SID. Check
  load == init before using as-is, or fix PSIDFile.lean to use loadAddr.

- A 7936-byte Array literal elaborates in ~7s on first build and is
  cached thereafter. Larger images may need a higher maxRecDepth.

- The `extract/__main__.py` (structural emit) still runs and writes
  SongData.lean. That's fine — the verbatim Main.lean ignores it.
  Calling out in the README that the structural fields aren't engine-
  faithful prevents confusion.
