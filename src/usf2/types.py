"""USF v2 — AST / model dataclasses.

These are what the parser yields and the writer accepts. See
docs/usf_v2_format.md for the on-disk format the dataclasses
correspond to.

Conventions:
- Integers are Python ints. The on-disk distinction between decimal
  and hex is purely lexical — the writer chooses a format based on
  the field (addresses + masks → hex, counts + durations → decimal).
- Instrument refs in note rows are `InstrumentRef` (id or name);
  reference resolution to a concrete instrument happens during
  validation, not parsing.
- Pitch is `Pitch` (note name + octave) or the rest sentinel.
- `dur_field`, `pwm_period`, `slide_v`, etc. are 8-bit raw values;
  the typing is `int` and the writer emits as hex.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Union


# ---------------------------------------------------------------------------
# Pitch + instrument refs (used inside note rows)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Pitch:
    """A note name + octave, or rest."""
    name: str         # 'C', 'D#', 'F', ... or '---' for rest
    octave: int       # 0-7, ignored for rest

    @property
    def is_rest(self) -> bool:
        return self.name == '---'

    @classmethod
    def rest(cls) -> 'Pitch':
        return cls(name='---', octave=0)

    def __str__(self) -> str:
        if self.is_rest:
            return '---'
        # `C-5` for natural, `C#5` for sharp
        sep = self.name[1] if len(self.name) == 2 else '-'
        letter = self.name[0]
        return f'{letter}{sep}{self.octave}'


@dataclass(frozen=True)
class InstrumentRef:
    """A reference to an instrument by id (`i1`) or name (`i:lead`).

    Resolution to a concrete `Instrument` happens during validation.
    """
    id: Optional[int] = None
    name: Optional[str] = None

    def __post_init__(self):
        if (self.id is None) == (self.name is None):
            raise ValueError('InstrumentRef must have exactly one of id/name')

    def __str__(self) -> str:
        return f'i{self.id}' if self.id is not None else f'i:{self.name}'


# ---------------------------------------------------------------------------
# Pattern + note rows
# ---------------------------------------------------------------------------

@dataclass
class NoteRow:
    """One row inside a pattern body."""
    pitch: Pitch
    duration: int
    instr: Optional[InstrumentRef] = None
    fx_flags: tuple = ()  # tuple of strings — 'tie', 'fx:drum', etc.


@dataclass
class Pattern:
    """A named pattern inside a voice block."""
    id: int
    length: int          # declared length in ticks (validated against sum of durations)
    rows: list[NoteRow] = field(default_factory=list)


@dataclass
class Orderlist:
    """A voice's orderlist of pattern ids, with loop/stop terminator."""
    entries: list[int] = field(default_factory=list)
    loop_to: Optional[int] = None      # position to jump to after the list
    stop: bool = False                  # true iff terminator is `stop`

    def __post_init__(self):
        if self.loop_to is not None and self.stop:
            raise ValueError('Orderlist cannot be both looping and stopping')


@dataclass
class VoiceBlock:
    """One of the three voice blocks inside a music subtune."""
    id: int                  # 1, 2, or 3
    orderlist: Orderlist
    patterns: list[Pattern] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Subtunes
# ---------------------------------------------------------------------------

@dataclass
class MusicSubtune:
    """A 3-voice music subtune."""
    id: int
    tempo: int
    voices: list[VoiceBlock] = field(default_factory=list)
    kind: str = 'music'


@dataclass
class DigiSubtune:
    """A digi subtune — a single sample reference."""
    id: int
    sample: str          # filename, relative to the .usf file
    kind: str = 'digi'


@dataclass
class SfxSubtune:
    """A Hubbard '85 sound-effect subtune.

    The engine's SFX record is a 2-voice SID-register snapshot + a
    freq-table pitch sweep. The 16-byte raw record is decomposed into
    these semantic fields:

    `v1` and `v2` are 6 bytes each — freq_hi, pw_lo, pw_hi, ctrl, ad,
    sr. The v1.freq_lo byte is aliased with `start_index`, so it's
    derived not stored. The v2.freq_lo byte is aliased with the gate
    flags + `v2_offset`, so it's also derived.

    `start_index` / `end_index` index into the engine's freq table for
    the sweep. `rate` is 0-15 (the sweep advances every `rate+1`
    frames). `direction` is 'up' or 'down'. `v2_offset` is 0-63 —
    V2's freq-table offset relative to V1's sweep index.

    Flags (booleans): `toggle_v1`, `toggle_v2` retrigger each voice's
    gate per sweep step; `skip_v1`, `skip_both` suppress freq writes.
    """
    id: int
    v1: tuple = (0, 0, 0, 0, 0, 0)       # freq_hi, pw_lo, pw_hi, ctrl, ad, sr
    v2: tuple = (0, 0, 0, 0, 0, 0)
    start_index: int = 0
    end_index: int = 0
    rate: int = 0                         # 0..15
    direction: str = 'down'               # 'up' or 'down'
    v2_offset: int = 0                    # 0..63
    toggle_v1: bool = False
    toggle_v2: bool = False
    skip_v1: bool = False
    skip_both: bool = False
    kind: str = 'sfx'


Subtune = Union[MusicSubtune, DigiSubtune, SfxSubtune]


# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------

@dataclass
class PwmConfig:
    mode: str = 'none'           # 'none' | 'linear' | 'bidirectional'
    speed: int = 0
    init: int = 0
    min_hi: int = 0
    max_hi: int = 0


@dataclass
class ArpConfig:
    offsets: list[int] = field(default_factory=list)
    period: int = 1


@dataclass
class VibratoConfig:
    scale: int = 0


@dataclass
class EnvelopeConfig:
    gate_off_delta: int = 0
    adsr_zero_delta: int = 0


@dataclass
class Instrument:
    id: int
    name: Optional[str] = None
    waveform: list[int] = field(default_factory=list)
    loop: int = 0
    pwm: PwmConfig = field(default_factory=PwmConfig)
    adsr: tuple = (0, 0)             # (ad, sr)
    arp: ArpConfig = field(default_factory=ArpConfig)
    vibrato: VibratoConfig = field(default_factory=VibratoConfig)
    envelope: EnvelopeConfig = field(default_factory=EnvelopeConfig)
    # Per-instrument behavioral flags. Hubbard '85 has 4 such bits
    # in the engine's fx_flags byte: bit 0 (freq_slide / skydive),
    # bit 1 (inc_by2 / freq-hi ramp), bit 2 (arpeggio enabled), bit 3
    # (pwm mode = linear). Bits 2 and 3 are derived from arp.offsets
    # and pwm.mode; the other two are stored explicitly.
    freq_slide: bool = False
    inc_by2: bool = False


# ---------------------------------------------------------------------------
# Init state + params + psid
# ---------------------------------------------------------------------------

@dataclass
class InitVoice:
    """Per-voice initial state at engine init. Field set is a superset
    of what any one engine needs — unused fields stay at their defaults
    and the codegen ignores them.
    """
    id: int
    ctrl: int = 0
    dur_field: int = 0
    pwm_period: int = 0
    pwm_dir: str = 'up'          # 'up' or 'down'
    instr: Optional[InstrumentRef] = None
    slide_v: int = 0


@dataclass
class InitState:
    voices: list[InitVoice] = field(default_factory=list)


@dataclass
class Params:
    """Engine-specific config. Stored as `dict[str, Any]` to keep the
    schema flexible across engines; the codegen knows its required
    keys and types.
    """
    fields: dict = field(default_factory=dict)


@dataclass
class PsidMeta:
    title: str = ''
    author: str = ''
    released: str = ''
    clock: str = 'PAL'           # 'PAL' | 'NTSC' | 'both' | 'unknown'
    sid: int = 6581              # 6581 | 8580 (0 = unknown, both = ?)
    start_song: int = 1


# ---------------------------------------------------------------------------
# Top-level USF file
# ---------------------------------------------------------------------------

@dataclass
class UsfFile:
    """The full in-memory representation of a .usf file."""
    version: int
    engine: str
    psid: PsidMeta
    params: Params
    init: InitState
    instruments: list[Instrument] = field(default_factory=list)
    subtunes: list[Subtune] = field(default_factory=list)
