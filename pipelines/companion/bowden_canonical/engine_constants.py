"""Engine constants for the Bowden-canonical Companion variant.

The 256-byte freq table (128 hi + 128 lo) is shared across all known
tunes in this cluster: the table is identical in the 96 chromatic slots
(8 octaves × 12 semitones) plus all 32 padding slots. Only the very
last byte ($CAFF, semitone 15 of octave 7) differs across tunes — a
dead byte that no orderlist ever indexes. We use one canonical table.

These are *engine* constants, not USF data: the USF carries the music
(pitches as note names), and the codegen looks pitches up in this
table. No tune-specific tuning information lives here.
"""

from __future__ import annotations


# 16-bit freq values per (octave, semitone). Standard PAL Companion
# tuning matching the engine's hardcoded table at $CA00/$CA80. Values
# below are extracted from Bach_Sonata.sid (which represents the
# canonical table — the 11 other Vic Berry tunes have an identical
# musically-meaningful set).
#
# Layout: 8 octaves × 16 slots; only slots 0..11 are musically valid
# (C..B); slots 12..15 are zero padding.
BOWDEN_FREQ_TABLE_PAL = [
    # oct 0
    0x010C, 0x011C, 0x012D, 0x0140, 0x0151, 0x0166, 0x017B, 0x0191,
    0x01A9, 0x01C3, 0x01DD, 0x01FA, 0x0000, 0x0000, 0x0000, 0x0000,
    # oct 1
    0x0218, 0x0238, 0x025A, 0x027D, 0x02A3, 0x02CC, 0x02F6, 0x0323,
    0x0353, 0x0386, 0x03BB, 0x03F4, 0x0000, 0x0000, 0x0000, 0x0000,
    # oct 2
    0x0430, 0x0470, 0x04B4, 0x04FB, 0x0547, 0x0598, 0x05ED, 0x0647,
    0x06A7, 0x070C, 0x0777, 0x07E9, 0x0000, 0x0000, 0x0000, 0x0000,
    # oct 3
    0x0861, 0x08E1, 0x0968, 0x09F7, 0x0A8F, 0x0B30, 0x0BDA, 0x0C8F,
    0x0D4E, 0x0E18, 0x0EEF, 0x0FD2, 0x0000, 0x0000, 0x0000, 0x0000,
    # oct 4
    0x10C3, 0x11C3, 0x12D1, 0x13EF, 0x151F, 0x1660, 0x17B5, 0x191E,
    0x1A9C, 0x1C31, 0x1DDF, 0x1FA5, 0x0000, 0x0000, 0x0000, 0x0000,
    # oct 5
    0x2187, 0x2386, 0x25A2, 0x27DF, 0x2A3E, 0x2CC1, 0x2F6B, 0x323C,
    0x3539, 0x3863, 0x3BBE, 0x3F4B, 0x0000, 0x0000, 0x0000, 0x0000,
    # oct 6
    0x430F, 0x470C, 0x4B45, 0x4FBF, 0x547D, 0x5983, 0x5ED6, 0x6479,
    0x6A73, 0x70C7, 0x777C, 0x7E97, 0x0000, 0x0000, 0x0000, 0x0000,
    # oct 7
    0x861E, 0x8E18, 0x968B, 0x9F7E, 0xA8FA, 0xB306, 0xBDAC, 0xC8F3,
    0xD4E6, 0xE18F, 0xEEF8, 0xFD2E, 0x0000, 0x0000, 0x0000, 0x00F0,
]
assert len(BOWDEN_FREQ_TABLE_PAL) == 128


def freq_tables() -> tuple[bytes, bytes]:
    """Split the canonical 16-bit table into (hi, lo) byte tables."""
    hi = bytes((v >> 8) & 0xFF for v in BOWDEN_FREQ_TABLE_PAL)
    lo = bytes(v & 0xFF for v in BOWDEN_FREQ_TABLE_PAL)
    return hi, lo


# Note-name → semitone index. 12-tone chromatic.
SEMITONE_OF = {
    'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
    'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11,
}
SEMITONE_NAME = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def pitch_to_note_byte(name: str, octave: int) -> int:
    """USF note name + octave → engine's (oct<<4)|semitone byte."""
    return (octave << 4) | SEMITONE_OF[name]


def note_byte_to_pitch(b: int) -> tuple[str, int]:
    """Inverse of pitch_to_note_byte. Raises if semitone >= 12."""
    semi = b & 0x0F
    octave = (b >> 4) & 0x07
    if semi >= 12:
        raise ValueError(f'note byte ${b:02X} has invalid semitone {semi}')
    return SEMITONE_NAME[semi], octave
