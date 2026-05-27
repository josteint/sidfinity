"""Smoke tests for the Commando extract pipeline.

Run from repo root:  pytest pipelines/hubbard/commando/tests/
"""
from __future__ import annotations

from pipelines.hubbard.commando.extract.engine_model import extract


def test_extract_returns_song_with_expected_shape() -> None:
    song = extract(subtune=0)
    assert song.freq_table is not None
    assert len(song.freq_table) >= 96       # at least standard PAL table
    assert len(song.instruments) == 13      # Commando has 13 distinct instruments
    assert song.score.tempo > 0
    assert len(song.score.voices) == 3      # SID = three voices, always


def test_instruments_have_typed_subfields() -> None:
    song = extract(subtune=0)
    inst = song.instruments[0]
    # Sanity-check the nested dataclasses exist with named fields
    assert inst.waveform.steps                # non-empty list
    assert inst.waveform.loop >= 0
    assert inst.envelope.ad >= 0
    assert inst.envelope.sr >= 0
    assert inst.pwm.mode in {'none', 'linear', 'bidirectional'}


def test_subtune_out_of_range_raises_value_error() -> None:
    import pytest
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=99)


def test_all_three_subtunes_extract() -> None:
    # Commando has 3 music subtunes (0=game, 1=title, 2=intro).
    for s in (0, 1, 2):
        song = extract(subtune=s)
        assert len(song.score.voices) == 3
        # Every voice references at least one pattern
        for voice in song.score.voices:
            assert len(voice.orderlist) > 0
