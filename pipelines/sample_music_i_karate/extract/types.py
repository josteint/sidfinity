"""Dataclasses for SampleMusicIKarate's extracted (T, instruments, score) representation.

Mirrors Commando's shape with one SampleMusicIKarate-specific addition: each instrument
carries a `has_skydive` flag (fx_flags bit 1) so the emitter can propagate
the engine quirk into the Lean source.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Waveform:
    """Sequence of SID control-register bytes plus a loop index."""

    steps: list[int]
    loop: int


@dataclass
class PWMConfig:
    """Pulse-width modulation parameters for one instrument."""

    speed: int
    mode: str  # 'none' | 'linear' | 'bidirectional'
    min_hi: int
    max_hi: int
    init_pw: int


@dataclass
class Envelope:
    """ADSR + hard-restart timing for one instrument."""

    ad: int
    sr: int
    gate_off_delta: int
    adsr_zero_delta: int


@dataclass
class Instrument:
    """One Hubbard instrument lifted into universal das_model form."""

    id: int
    waveform: Waveform
    pwm: PWMConfig
    envelope: Envelope
    arp_offset: int = 0
    vibrato_scale: int = 0
    has_bit0: bool = False
    has_skydive: bool = False  # SampleMusicIKarate extension: fx_flags bit 1


@dataclass
class Note:
    """One note inside a pattern."""

    pitch: int
    duration: int
    instrument: int
    tie: bool
    drum_trig: int


@dataclass
class Voice:
    """One voice's orderlist + patterns + loop point."""

    orderlist: list[int] = field(default_factory=list)
    patterns: dict[int, list[Note]] = field(default_factory=dict)
    loop: int = -1


@dataclass
class Score:
    """Tempo (frames per tick) and voices for one subtune."""

    tempo: int
    voices: list[Voice] = field(default_factory=list)


@dataclass
class ExtractedSong:
    """The complete (T, instruments, score) extracted from a Hubbard SID."""

    freq_table: list[int]
    instruments: list[Instrument]
    score: Score
