# Old Player Files

Earlier versions of the SIDfinity 6502 player and code generation tools. All superseded by the V2 per-song code generator (codegen_v2.py).

- `blocks.py` — block-based code generator (predecessor to codegen_v2.py)
- `interface_verify.py` — block interface verifier (for blocks.py)
- `sidfinity.asm` — first xa65 player prototype (3 voices, basic)
- `sidfinity_defines.asm` — defines for the prototype
- `sidfinity_player.s` — monolithic player source (GoatTracker fork)
- `sidfinity_gt2.asm` — GT2 v2.68 player fork (reference implementation)
- `test_songs.py` — test song generator for the old player
- `gpu_optimizer_design.md` — design doc for GPU brute-force optimizer (implemented in gpu_6502.cu)

## Acknowledgment — GT2 playroutine

The V2 SIDfinity player (deprecated, see `deprecated/v2_codegen/`) implements
algorithms from Lasse Öörni's GoatTracker V2 playroutine — wave table execution,
effect dispatch, pattern reading, hard restart timing. The V2 code generator
(`codegen_v2.py`) was written from scratch in Python but the player logic it
generates faithfully follows Lasse Öörni's design. A copy of the original GT2
playroutine source is preserved here as `sidfinity_gt2.asm`. Lasse Öörni's
license: *"free for any purpose, commercial or noncommercial."*

SIDfinity pivoted away from this approach in its pre-alpha stage, but Lasse's
playroutine was load-bearing for the project's earliest work.
