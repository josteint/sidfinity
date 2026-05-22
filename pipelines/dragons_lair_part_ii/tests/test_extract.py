"""Smoke tests for the Dragon's Lair Part II extract pipeline.

Run from repo root:  pytest pipelines/dragons_lair_part_ii/tests/

These tests are **scaffold-level** only. They assert that the extract
runs without crashing and produces a song-shaped result — they do
*not* assert engine-faithful values, because the codegen is still on
Monty's 1985 engine while the original is the 1986 Hubbard variant.

The Monty-specific assertions (skydive instruments, PWM bounds) that
the clone tool emits are deliberately omitted here. Add real engine
checks once the codegen has been ported to the 1986 engine — see
`pipelines/dragons_lair_part_ii/README.md` for the work list.
"""
from __future__ import annotations

from pipelines.dragons_lair_part_ii.extract.engine_model import extract


def test_extract_returns_song_shape() -> None:
    song = extract(subtune=0)
    assert song.freq_table is not None
    assert len(song.freq_table) >= 96
    assert len(song.instruments) > 0
    assert song.score.tempo > 0
    assert len(song.score.voices) == 3
    for voice in song.score.voices:
        assert len(voice.orderlist) > 0
