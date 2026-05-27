"""Smoke tests for the Monty on the Run extract pipeline.

Run from repo root:  pytest pipelines/hubbard/monty/tests/
"""
from __future__ import annotations

from pipelines.hubbard.monty.extract.engine_model import extract


def test_extract_returns_song_with_expected_shape() -> None:
    song = extract(subtune=0)
    assert song.freq_table is not None
    assert len(song.freq_table) >= 96
    assert len(song.instruments) == 20      # Monty has 20 distinct instruments
    assert song.score.tempo > 0
    assert len(song.score.voices) == 3


def test_skydive_instruments_are_detected() -> None:
    """Monty's instruments 10, 12, 13 have fx_flags bit 1 set (skydive)."""
    song = extract(subtune=0)
    skydive_ids = {i.id for i in song.instruments if i.has_skydive}
    assert skydive_ids == {10, 12, 13}, (
        f"expected skydive on instruments 10/12/13, got {skydive_ids}"
    )


def test_pw_bounds_are_hubbard_hardcoded() -> None:
    """Hubbard's pulsework uses cmp #$08 / #$0E for bidir PWM bounds —
    every Monty extraction must default to those values."""
    song = extract(subtune=0)
    for inst in song.instruments:
        if inst.pwm.mode == 'bidirectional':
            assert inst.pwm.min_hi == 0x08, f"inst {inst.id}: pwm.min_hi={inst.pwm.min_hi}"
            assert inst.pwm.max_hi == 0x0E, f"inst {inst.id}: pwm.max_hi={inst.pwm.max_hi}"


def test_subtune_out_of_range_raises_value_error() -> None:
    import pytest
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=99)


def test_three_music_subtunes_extract() -> None:
    for s in (0, 1, 2):
        song = extract(subtune=s)
        assert len(song.score.voices) == 3
        for voice in song.score.voices:
            assert len(voice.orderlist) > 0
