"""Dataclasses for the Last V8 (C128) engine model.

Last V8 is NOT a Hubbard tracker in the Commando/Monty sense. It bundles
two engines under one PSID and dispatches per-subtune at init time. The
engine model below captures what we can extract statically from the
binary; lifting the tracker music to a USFSong is left to a later pass
(see README — "what isn't done yet").
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ----- RSID header -------------------------------------------------------

@dataclass
class RSIDHeader:
    """Fields read from the RSID/PSID v2 header."""

    magic: str             # 'RSID' or 'PSID'
    version: int
    load_addr: int         # actual load address (resolved if header.load=0)
    init_addr: int
    play_addr: int         # 0 for RSID — play is IRQ-driven
    songs: int
    start_song: int        # 1-indexed in the header
    name: str
    author: str
    released: str


# ----- subtune dispatch --------------------------------------------------

@dataclass
class SubtuneRoute:
    """Where a single subtune routes at init time.

    `kind` is one of:
      'music'   — init via $8C53 (tracker setup) → IRQ play body at $8022
      'sample'  — init via relocator + JSR $C000 (one-shot digi playback)
      'sfx'     — init via $8C85/$8C71 (sound-effect arming on V1+V2)
    """

    subtune: int           # 0-indexed
    kind: str


# ----- sample-player records --------------------------------------------

@dataclass
class SampleRecord:
    """A one-shot sample played by the relocated $C000 player.

    The 4-byte records live at binary offset $7D40 + 4*sample_index. The
    relocator copies them to $C200 before JSR-ing into the player.
    """

    subtune: int           # 0-indexed subtune this sample fires on
    start: int             # 16-bit start address in the binary
    end: int               # 16-bit end address in the binary (exclusive)
    rate_constant: int = 0xC0  # CIA2 Timer A threshold from $C30A

    @property
    def length_bytes(self) -> int:
        return self.end - self.start


# ----- instrument records ----------------------------------------------

@dataclass
class Instrument:
    """One 8-byte instrument record from the table at $85A1.

    Offsets match what the music driver reads at $8149-$815E and
    $81BA-$81C9:
      0  pulse_lo
      1  pulse_hi
      2  ctrl       — SID waveform / gate / sync / ring bits
      3  ad         — attack/decay
      4  sr         — sustain/release
      5  vib_shift  — vibrato depth, LSR count (smaller = wider)
      6  pwm        — PWM byte; low 5 bits = step counter, high 3 = step
      7  fx_flags
                       bit 0 = portamento
                       bit 1 = note-cut on release
                       bit 2 = arpeggio from frame-counter phase
                       bit 3 = pulse-arp (deltas drive PW instead of freq)
    """

    id: int
    pulse_width: int          # 16-bit LE
    ctrl: int
    ad: int
    sr: int
    vib_shift: int
    pwm: int
    fx_flags: int

    @property
    def has_portamento(self) -> bool: return bool(self.fx_flags & 0x01)
    @property
    def has_note_cut(self)   -> bool: return bool(self.fx_flags & 0x02)
    @property
    def has_arpeggio(self)   -> bool: return bool(self.fx_flags & 0x04)
    @property
    def has_pulse_arp(self)  -> bool: return bool(self.fx_flags & 0x08)

    @property
    def is_empty(self) -> bool:
        return (self.pulse_width == 0 and self.ctrl == 0 and self.ad == 0
                and self.sr == 0 and self.vib_shift == 0 and self.pwm == 0
                and self.fx_flags == 0)


# ----- pattern / orderlist / music subtune ------------------------------

@dataclass
class PatternEvent:
    """One event in a Hubbard pattern.

    The hold byte (always present) encodes:
      bit 7  has_fx       — next byte is the FX byte
      bit 6  tie          — sustain current note; no FX, no pitch byte
      bit 5  no_release   — when hold expires, don't auto-release
      bits 4-0  hold      — frames to hold (decremented at tempo-tick rate)

    The FX byte, when present, is either an instrument id (bit 7 = 0) or
    an arp/pulse-mode mask (bit 7 = 1, stored at $8530,x in the driver).
    `pitch` is an index into the freq table at $843B (None for tie events).
    """

    kind: str                # 'note' | 'tie'
    hold_byte: int           # raw byte
    hold: int                # bits 4-0 of hold_byte
    no_release: bool         # bit 5
    pitch: int | None        # index into freq table; None for tie
    instrument: int | None = None  # FX byte if its bit 7 was clear
    arp_mode: int | None = None    # FX byte if its bit 7 was set


@dataclass
class Pattern:
    """One pattern: ordered events terminated by $FF."""

    index: int                       # pattern number (referenced from orderlists)
    addr: int                        # source address in the binary
    events: list[PatternEvent]
    end_addr: int                    # one past the $FF terminator


@dataclass
class Orderlist:
    """One voice's orderlist: pattern indices + terminator."""

    voice: int                       # 0, 1, or 2
    addr: int                        # source address
    indices: list[int]               # pattern indices, in play order
    terminator: str                  # 'restart' ($FF) | 'end_song' ($FE)


@dataclass
class MusicSubtune:
    """A music subtune: three voices with orderlists."""

    subtune: int                     # 0-indexed
    voices: list[Orderlist]          # always 3 entries: V0, V1, V2


# ----- music-driver tables ---------------------------------------------

@dataclass
class MusicTables:
    """Hard-coded addresses of the tracker driver's static tables.

    Discovered from the disassembly (docs/hubbard_last_v8_c128_disassembly.s).
    These are absolute addresses inside the SID binary at load.
    """

    freq_table_addr: int           # $843B — 96 semitones, 2-byte LE
    instrument_table_addr: int     # $85A1 — 8-byte records
    sfx_table_addr: int            # $8699 — 16-byte records
    orderlist_ptrs_addr: int       # $8791 — 6 bytes per music subtune
    pattern_ptr_lo_addr: int       # $87A9 — pattern LSBs indexed by note FX
    pattern_ptr_hi_addr: int       # $87C6 — pattern MSBs


# ----- top-level engine model -------------------------------------------

@dataclass
class EngineModel:
    """Everything extract/ knows about this SID after one parse."""

    header: RSIDHeader
    payload_start: int             # binary offset within the file
    payload_bytes: bytes           # raw memory image starting at load_addr

    relocator_src: int             # $7B40
    relocator_len: int             # $0400
    relocator_dst: int             # $C000

    routes: list[SubtuneRoute]     # one entry per subtune (0..songs-1)
    samples: list[SampleRecord]    # one entry per sample subtune
    music: MusicTables
    patterns: list[Pattern]        # 28 patterns indexed by orderlist values
    music_subtunes: list[MusicSubtune]  # one entry per 'music'-routed subtune
    instruments: list[Instrument]  # populated entries from $85A1, padding trimmed

    @property
    def freq_table(self) -> list[tuple[int, int]]:
        """The 96-semitone (lo, hi) table at $843B."""
        return _read_lo_hi_pairs(self.payload_bytes,
                                 self.music.freq_table_addr,
                                 self.header.load_addr,
                                 count=96)

def _read_lo_hi_pairs(buf: bytes, addr: int, load: int,
                      count: int) -> list[tuple[int, int]]:
    off = addr - load
    return [(buf[off + 2 * i], buf[off + 2 * i + 1]) for i in range(count)]
