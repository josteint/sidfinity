"""Smoke tests for the Hunter Patrol extract pipeline.

Run from repo root:  pytest pipelines/hubbard/hunter_patrol/tests/
"""
from __future__ import annotations

from pipelines.hubbard.hunter_patrol.extract.engine_model import extract


def test_extract_returns_song_with_expected_shape() -> None:
    song = extract(subtune=0)
    assert song.freq_table is not None
    assert len(song.freq_table) >= 96
    # Hunter Patrol's instrument table at $A427 holds 15 non-zero records.
    assert len(song.instruments) == 15
    # Tempo is the engine's $A419+1 = 2+1 = 3 frames per tick.
    assert song.score.tempo == 3
    assert len(song.score.voices) == 3


def test_skydive_instruments_are_detected() -> None:
    """Hunter Patrol only uses skydive on instrument 4 (fx_flags bit 1)."""
    song = extract(subtune=0)
    skydive_ids = {i.id for i in song.instruments if i.has_skydive}
    assert skydive_ids == {4}, (
        f"expected skydive on instrument 4, got {skydive_ids}"
    )


def test_pw_bounds_are_hubbard_hardcoded() -> None:
    """Hubbard's pulsework uses cmp #$08 / #$0E for bidir PWM bounds —
    every Hunter Patrol extraction must default to those values."""
    song = extract(subtune=0)
    for inst in song.instruments:
        if inst.pwm.mode == 'bidirectional':
            assert inst.pwm.min_hi == 0x08, f"inst {inst.id}: pwm.min_hi={inst.pwm.min_hi}"
            assert inst.pwm.max_hi == 0x0E, f"inst {inst.id}: pwm.max_hi={inst.pwm.max_hi}"


def test_subtune_out_of_range_raises_value_error() -> None:
    """Hunter Patrol's PSID declares a single subtune. Anything ≥ 1 must fail."""
    import pytest
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=1)


def test_v1_v2_orderlists_are_paired() -> None:
    """V1 and V2 in Hunter Patrol play paired (off-by-one) patterns —
    a classic Hubbard harmony layout. V2 patterns = V1 patterns + 1."""
    song = extract(subtune=0)
    v1 = song.score.voices[0].orderlist
    v2 = song.score.voices[1].orderlist
    assert len(v1) == len(v2)
    for a, b in zip(v1, v2):
        assert b == a + 1, f"V1={v1!r}, V2={v2!r}"
