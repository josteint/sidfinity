"""Engine constants for the Clever Music Companion engine.

The 128-entry freq table is identical between Fairlight and Gyroscope
(extracted post-init from either). Stored here as the engine constant.
"""

from __future__ import annotations


# 16-bit freq values, indexed by note byte (0..127). Identical between
# Fairlight and Gyroscope — same engine, same tuning table.
CLEVER_FREQ_HI = bytes.fromhex(
    '010101010101010101010101000000000202020202020203030303030000000004040404050505060607070700000000'
    '080809090a0b0b0c0d0e0e0f00000000'
    '10111213151617191a1c1d1f00000000'
    '212325272a2c2f3235383b3f00000000'
    '43474b4f54595e646a70777e00000000'
    '868e969fa8b3bdc8d4e1eefd00000000'
)
CLEVER_FREQ_LO = bytes.fromhex(
    '0c1c2d4051667b91a9c3ddfa00000000'
    '18385a7da3ccf6235386bbf400000000'
    '3070b4fb4798ed47a70c77e900000000'
    '61e168f78f30da8f4e18efd200000000'
    'c3c3d1ef1f60b51e9c31dfa500000000'
    '8786a2df3ec16b3c3963be4b00000000'
    '0f0c45bf7d83d67973c77c9700000000'
    '1e188b7efa06acf3e68ff82e00000000'
)
assert len(CLEVER_FREQ_HI) == 128
assert len(CLEVER_FREQ_LO) == 128


# Note name → semitone index.
SEMITONE_OF = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11,
}
SEMITONE_NAME = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def pitch_to_note_byte(name: str, octave: int) -> int:
    return (octave << 4) | SEMITONE_OF[name]


def note_byte_to_pitch(b: int) -> tuple[str, int]:
    semi = b & 0x0F
    octave = (b >> 4) & 0x07
    if semi >= 12:
        raise ValueError(f'note byte ${b:02X} has invalid semitone {semi}')
    return SEMITONE_NAME[semi], octave
