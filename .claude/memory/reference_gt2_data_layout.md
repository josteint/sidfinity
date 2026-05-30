---
name: GT2 packed data layout reference
description: Exact byte-level memory layout for GT2 SID files — read docs/gt2_data_layout.md before touching the packer
type: reference
---

The complete GT2 packed SID data layout is documented in `docs/gt2_data_layout.md`. This was produced by studying greloc.c line by line.

Key rules for the packer:
1. Data from packed binaries is already transformed — don't re-transform
2. Column presence is flag-dependent — wrong flags shift ALL subsequent data
3. Empty tables = 0 bytes between labels, not placeholder bytes
4. Speed table $00 prefix only when speed features used AND table has entries
5. Use assembler address expressions, not pre-computed addresses
6. Song/pattern table uses `.BYTE (label % 256)` for address resolution
