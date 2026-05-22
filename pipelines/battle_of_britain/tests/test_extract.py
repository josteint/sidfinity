"""Smoke tests for the Battle of Britain extract pipeline.

Run from repo root:  pytest pipelines/battle_of_britain/tests/

These tests assert the shape of what `extract()` lifts out of the
original BoB PSID. They guard against accidental Monty-clone drift
(the BoB pipeline is currently a Monty fork — see ../README.md).
"""
from __future__ import annotations

from pipelines.battle_of_britain.extract.engine_model import extract

BOB_FT_BASE = 0x8326  # freq table base in the original BoB binary


def _song():
    return extract(subtune=0, ft_base=BOB_FT_BASE,
                   default_pw_min=0x08, default_pw_max=0x0E)


def test_extract_returns_song_with_expected_shape() -> None:
    song = _song()
    assert song.freq_table is not None
    # BoB's real freq table is 96 entries ($8326-$83E5). Extract reads
    # a few bytes past the boundary into the SID-base table; we accept
    # any size >= 96 and trust emit_usf to truncate.
    assert len(song.freq_table) >= 96
    # Original BoB has 19 instruments in the table at $8420.
    assert len(song.instruments) == 19
    assert song.score.tempo > 0
    assert len(song.score.voices) == 3


def test_skydive_instruments_are_detected() -> None:
    """BoB sets fx_flags bit 1 (skydive) on instruments 4 and 18."""
    song = _song()
    skydive_ids = {i.id for i in song.instruments if i.has_skydive}
    assert skydive_ids == {4, 18}, (
        f"expected skydive on instruments 4 and 18, got {skydive_ids}"
    )


def test_pw_bounds_are_hubbard_hardcoded() -> None:
    """Hubbard's pulsework uses cmp #$08 / #$0E for bidir PWM bounds —
    every BoB extraction must default to those values."""
    song = _song()
    for inst in song.instruments:
        if inst.pwm.mode == 'bidirectional':
            assert inst.pwm.min_hi == 0x08, (
                f"inst {inst.id}: pwm.min_hi={inst.pwm.min_hi}")
            assert inst.pwm.max_hi == 0x0E, (
                f"inst {inst.id}: pwm.max_hi={inst.pwm.max_hi}")


def test_subtune_out_of_range_raises_value_error() -> None:
    import pytest
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=99, ft_base=BOB_FT_BASE,
                default_pw_min=0x08, default_pw_max=0x0E)


def test_only_one_psid_subtune() -> None:
    """The HVSC BoB PSID is the stripped one-track version; the
    original 19-entry game ROM was split into music + SFX. Only
    subtune 0 should be extractable here."""
    import pytest
    song = _song()
    assert len(song.score.voices) == 3
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=1, ft_base=BOB_FT_BASE,
                default_pw_min=0x08, default_pw_max=0x0E)


def test_freq_table_starts_at_0x0116() -> None:
    """First semitone of BoB's freq table is $0116 (lo=$16, hi=$01).
    Sanity check the extract is reading the correct binary region."""
    song = _song()
    assert song.freq_table[0] == 0x0116
    assert song.freq_table[1] == 0x0127
    assert song.freq_table[2] == 0x0138
