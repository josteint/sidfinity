"""Smoke tests for the One Man and his Droid extract pipeline.

Run from repo root:  python3 -m pytest pipelines/hubbard/one_man_and_his_droid/tests/
"""
from __future__ import annotations

from pipelines.hubbard.one_man_and_his_droid.extract.engine_model import extract


def test_extract_returns_song_with_expected_shape() -> None:
    song = extract(subtune=0)
    assert song.freq_table is not None
    assert len(song.freq_table) >= 96
    # OMHD subtune 0 yields 15 distinct instruments via the current
    # extractor. This is the observed baseline; revisit if the
    # engine_model logic changes.
    assert len(song.instruments) == 15
    assert song.score.tempo > 0
    assert len(song.score.voices) == 3


def test_skydive_instruments_are_detected() -> None:
    """fx_flags bit 1 = "skydive" (alt-slide). Extractor flags it."""
    song = extract(subtune=0)
    skydive_ids = {i.id for i in song.instruments if i.has_skydive}
    # Verified against the raw instrument table at $1588 — insts 0/1/8
    # have flags byte $0A (bit 1 set).
    assert skydive_ids == {0, 1, 8}, (
        f"expected skydive on instruments 0/1/8, got {skydive_ids}"
    )


def test_pw_bounds_are_hubbard_hardcoded() -> None:
    """Hubbard's pulsework uses cmp #$08 / #$0E for bidir PWM bounds —
    every OMHD extraction must default to those values (verified in
    docs/hubbard_one_man_and_his_droid_disassembly.s at $1271/$128B)."""
    song = extract(subtune=0)
    for inst in song.instruments:
        if inst.pwm.mode == 'bidirectional':
            assert inst.pwm.min_hi == 0x08, f"inst {inst.id}: pwm.min_hi={inst.pwm.min_hi}"
            assert inst.pwm.max_hi == 0x0E, f"inst {inst.id}: pwm.max_hi={inst.pwm.max_hi}"
