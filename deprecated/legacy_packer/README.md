# Legacy Packer Path

The original GT2 packer used the monolithic GoatTracker player source (sidfinity_gt2.asm) with compilation flags detected from the binary. Superseded by the V2 per-song code generator (codegen_v2.py) which emits custom 6502 assembly for each song.

- `sidfinity_packer.py` — old packer using monolithic player
- `sidfinity_builder.py` — old SID file builder
- `gt2_test_pipeline.py` — end-to-end test for the legacy path
