"""Dataclass types for the Commando extract pipeline.

Defines the universal das_model representation produced by `extract()` and
consumed by `emit_usf.py`:

    ExtractedSong
      ├── freq_table : list[int]    -- 128 16-bit PAL freq entries + runtime
      ├── instruments: list[Instrument]
      └── score      : Score
              ├── tempo : int
              └── voices: list[Voice]

These are mutable dataclasses (not frozen) — extract() builds them piece by
piece. Field names are snake_case (waveform / pwm / envelope) instead of the
single-letter W/P/E used in the earlier dict-based shape.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Waveform:
    """Per-instrument waveform-step program (sequence of ctrl bytes + loop point)."""

    steps: list[int]
    loop: int


@dataclass
class PWMConfig:
    """Per-instrument pulse-width modulation configuration."""

    speed: int
    mode: str  # 'none' | 'linear' | 'bidirectional'
    min_hi: int
    max_hi: int
    init_pw: int


@dataclass
class Envelope:
    """Per-instrument ADSR envelope + hard-restart timing."""

    ad: int
    sr: int
    gate_off_delta: int
    adsr_zero_delta: int


@dataclass
class Instrument:
    """A single Hubbard-engine instrument program."""

    id: int
    waveform: Waveform
    pwm: PWMConfig
    envelope: Envelope
    arp_offset: int = 0
    vibrato_scale: int = 0
    has_bit0: bool = False


@dataclass
class Note:
    """One note inside a pattern. Duration is in ticks; emit_usf converts to frames."""

    pitch: int
    duration: int
    instrument: int
    tie: bool
    drum_trig: int


@dataclass
class Voice:
    """One voice (channel) of a subtune: pattern order + pattern bodies + loop point."""

    orderlist: list[int] = field(default_factory=list)
    patterns: dict[int, list[Note]] = field(default_factory=dict)
    loop: int = -1
    stop: bool = False          # the orderlist ends with $FE (end-of-song,
                                # no loop) rather than $FF (loop to `loop`)


@dataclass
class Score:
    """A subtune score: tempo (frames per tick) + per-voice pattern data."""

    tempo: int
    voices: list[Voice] = field(default_factory=list)


@dataclass
class ExtractedSong:
    """The full output of extract(): freq table + instruments + score."""

    freq_table: list[int]
    instruments: list[Instrument]
    score: Score
