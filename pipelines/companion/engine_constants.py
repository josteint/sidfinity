"""Engine-level constants for the Companion engine.

These bytes are the same across every Companion tune — they belong to
the engine, not to any individual song. Keeping them here means the
USF v2 representation of a Companion tune doesn't have to carry the
freq table redundantly; `build_from_usf.py` reads from this module.

Source: extracted from the freq tables at $C000/$C080 in
Hubbard's Up,up&Away! binary (the Hubbard-extended Companion variant).
PAL tuning, A4 = 423.8 Hz.
"""

# 128-entry tables indexed by Companion's note byte format
# (octave << 4) | semitone, semitone 0..11 valid; bytes 12-15 of
# each octave row are zeros (unused).
COMPANION_FREQ_HI = bytes.fromhex(
    "01010101010101010101010100000000"
    "02020202020202020303030300000000"
    "04040404050505060607070700000000"
    "080809090a0b0b0c0d0e0e0f00000000"
    "10111213151617191a1c1d1f00000000"
    "212325272a2c2f3235383b3f00000000"
    "43474b4f54595e646a70777e00000000"
    "868e969fa8b3bdc8d4e1eefd00000000"
)
COMPANION_FREQ_LO = bytes.fromhex(
    "0c1c2d4051667b91a9c3ddfa00000000"
    "18385a7da3ccf6235386bbf400000000"
    "3070b4fb4798ed47a70c77e900000000"
    "61e168f78f30da8f4e18efd200000000"
    "c3c3d1ef1f60b51e9c31dfa500000000"
    "8786a2df3ec16b3c3963be4b00000000"
    "0f0c45bf7d83d67973c77c9700000000"
    "1e188b7efa06acf3e68ff82e00000000"
)
assert len(COMPANION_FREQ_HI) == 128
assert len(COMPANION_FREQ_LO) == 128
