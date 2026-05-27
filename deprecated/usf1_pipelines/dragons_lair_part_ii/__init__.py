"""Dragon's Lair Part II pipeline: scaffold for the 1986-era Hubbard engine.

This is **not** a byte-perfect rebuild yet. The directory is laid out so
future codegen work can fill in the 1986 engine semantics (two 8-byte
instrument tables, $C505 state byte, $FE/$FF orderlist markers, 1/2/3/4-byte
pattern rows). See `pipelines/dragons_lair_part_ii/README.md` and the
annotated disassembly at `docs/hubbard_dragons_lair_part_ii_disassembly.s`.
"""
