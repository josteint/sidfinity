"""Smoke tests for the Sample Music from I. Karate extract pipeline.

Run from repo root:  pytest pipelines/sample_music_i_karate/tests/

These tests assert the extract module wires up end-to-end and produces
plausibly-shaped output. They were inherited from the Action Biker
template and the per-instrument expectations (skydive / PWM bounds)
have NOT yet been re-derived for I. Karate. The non-shape tests are
marked xfail until the engine model is tuned for this SID.
"""
from __future__ import annotations

import pytest

from pipelines.sample_music_i_karate.extract.engine_model import extract


def test_extract_returns_song_with_expected_shape() -> None:
    song = extract(subtune=0)
    assert song.freq_table is not None
    assert len(song.freq_table) >= 96
    assert len(song.instruments) > 0
    assert song.score.tempo > 0
    assert len(song.score.voices) == 3


@pytest.mark.xfail(reason="skydive instrument set inherited from Action Biker; not validated for Karate")
def test_skydive_instruments_are_detected() -> None:
    song = extract(subtune=0)
    skydive_ids = {i.id for i in song.instruments if i.has_skydive}
    assert skydive_ids == {10, 12, 13}


@pytest.mark.xfail(reason="PWM bounds inherited from Action Biker (Hubbard hardcoded $08/$0E); revalidate for Karate")
def test_pw_bounds_are_hubbard_hardcoded() -> None:
    song = extract(subtune=0)
    for inst in song.instruments:
        if inst.pwm.mode == 'bidirectional':
            assert inst.pwm.min_hi == 0x08
            assert inst.pwm.max_hi == 0x0E


def test_subtune_out_of_range_raises_value_error() -> None:
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=99)


def test_subtune_zero_extracts() -> None:
    song = extract(subtune=0)
    assert len(song.score.voices) == 3
    for voice in song.score.voices:
        assert len(voice.orderlist) > 0
