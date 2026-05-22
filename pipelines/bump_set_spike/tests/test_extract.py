"""Smoke tests for the Bump Set Spike extract pipeline.

These tests verify the SCAFFOLD: that the extractor runs against the
binary without crashing and returns the expected high-level shape.
They do NOT verify musical correctness — the codegen still treats the
extracted data as Monty's and currently produces a Grade F rebuild.

Run from repo root:  pytest pipelines/bump_set_spike/tests/
"""
from __future__ import annotations

from pipelines.bump_set_spike.extract.engine_model import extract


def test_extract_returns_song_with_expected_shape() -> None:
    song = extract(subtune=0)
    assert song.freq_table is not None
    # Bump Set Spike's freq table starts at $B3FF, 96 semitones.
    assert len(song.freq_table) >= 96
    # First entry = $0116 (lo=$16, hi=$01), verified from the binary.
    assert song.freq_table[0] == 0x0116, hex(song.freq_table[0])
    # Engine has 3 voices.
    assert len(song.score.voices) == 3
    assert song.score.tempo > 0


def test_pw_bounds_are_hubbard_hardcoded() -> None:
    """Bump Set Spike's player CMPs against $08 / $0E for bidir PWM bounds
    (verified at $B2D3 and $B2ED in the binary disassembly). The extractor
    must default to those values."""
    song = extract(subtune=0)
    for inst in song.instruments:
        if inst.pwm.mode == 'bidirectional':
            assert inst.pwm.min_hi == 0x08, f"inst {inst.id}: pwm.min_hi={inst.pwm.min_hi}"
            assert inst.pwm.max_hi == 0x0E, f"inst {inst.id}: pwm.max_hi={inst.pwm.max_hi}"


def test_subtune_out_of_range_raises_value_error() -> None:
    import pytest
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=99)


def test_both_subtunes_extract() -> None:
    """Bump Set Spike PSID claims 2 subtunes; the extract path should
    return three voices for each one."""
    for s in (0, 1):
        song = extract(subtune=s)
        assert len(song.score.voices) == 3
        for voice in song.score.voices:
            assert len(voice.orderlist) > 0
