"""
usf.format — Pure data structures for Universal Symbolic Format.

Contains dataclasses, constants, and helpers (note_name, note_from_name, usf_to_json).
NO tokenize/detokenize — those live in adapters.usf_tokens.
"""

from dataclasses import dataclass, field
from typing import Optional
import json


# ============================================================
# Data structures
# ============================================================

@dataclass
class WaveTableStep:
    """One step in a wave table program.

    Values are stored in .sng-equivalent format (pre-transform, musical intent).

    .sng left column ranges:
      $00=no wave change, $01-$0F=delay N frames, $10-$DF=waveform,
      $E0-$EF=inaudible/silent wave command, $F0-$FE=commands, $FF=jump/loop

    .sng right column ranges:
      $00-$5F=relative note up, $60-$7F=relative note down (signed offset+$80),
      $80=keep freq (no change), $81-$DF=absolute note

    Packed format transforms (applied by greloc.c, reversed during parse):
      Left:  waveforms $10-$DF get +$10 added (only when NOWAVEDELAY=0)
             silent waves $E0-$EF masked to low nibble then +$10
      Right: non-command entries XOR $80 (flips relative/absolute sense)
             command entries ($F0-$FE left): table index remap, no XOR
             jump entries ($FF left): table index remap, no XOR

    The encoder (usf_to_sid.py) re-applies these transforms when packing.
    """
    waveform: int = 0x41       # SID waveform byte (e.g. $41 = pulse+gate)
    note_offset: int = 0       # relative semitone offset (negative = down)
    absolute_note: int = -1    # if >= 0, absolute note instead of relative
    is_loop: bool = False      # if True, this is a loop/jump command
    loop_target: int = 0       # loop destination step index (within this instrument's WT)
    delay: int = 0             # if > 0, delay N frames before applying this step
    keep_freq: bool = False    # if True, don't change frequency ($80 in right column)
    freq_slide: int = 0        # signed per-frame freq_hi delta (-128..+127, 0=no slide)
                               # Hubbard drums: -4 typical (rapid pitch descent)
                               # Applied by V2 player AFTER note/freq resolution each frame


@dataclass
class PulseTableStep:
    """One step in a pulse table program.

    GT2 pulse table left column:
      $01-$7F=modulate for N frames, $8x=set pulse width (right=low byte),
      $FF=jump/loop
    GT2 pulse table right column:
      signed speed (modulation) or low 8 bits (set)
    """
    is_set: bool = False       # True=set pulse width, False=modulate
    value: int = 0             # set: pulse width high nib | modulate: signed speed
    low_byte: int = 0          # set: pulse width low byte
    duration: int = 1          # modulate: number of frames
    is_loop: bool = False
    loop_target: int = 0


@dataclass
class FilterTableStep:
    """One step in a filter table program.

    GT2 filter table left column:
      $00=set cutoff (right=cutoff value),
      $01-$7F=modulate for N frames (right=signed speed),
      $80-$8F=set filter params (right=resonance<<4 | routing),
      $FF=jump/loop
    """
    type: str = 'cutoff'       # 'cutoff', 'modulate', 'params', 'loop'
    value: int = 0             # cutoff value, speed, or resonance<<4|routing
    duration: int = 1          # modulation frame count
    is_loop: bool = False
    loop_target: int = 0


@dataclass
class SpeedTableEntry:
    """One entry in the speed table.

    GT2 speed table is used for vibrato, portamento, and funktempo:
      Vibrato: left=speed (bit 7=note-independent), right=depth
      Portamento: left=MSB, right=LSB (16-bit speed)
      Funktempo: left=tempo even rows, right=tempo odd rows
    """
    left: int = 0
    right: int = 0


@dataclass
class Instrument:
    """Instrument definition.

    Maps to GT2 instrument columns:
      AD, SR, wave_ptr, pulse_ptr, filter_ptr, vib_param, vib_delay,
      gate_timer, first_wave
    """
    id: int = 0
    ad: int = 0x09             # attack/decay
    sr: int = 0x00             # sustain/release
    waveform: str = 'pulse'    # primary waveform: tri, saw, pulse, noise
    first_wave: int = -1       # first-frame waveform override ($00=skip, -1=derive from waveform)
    gate_timer: int = 2        # hard restart lead time (frames, bits 0-5)
    hr_method: str = 'gate'    # none, gate, test, adsr
    legato: bool = False       # if True, don't retrigger ADSR (gate_timer bit 6 in GT2)
    wave_table: list = field(default_factory=list)    # list of WaveTableStep
    pulse_table: list = field(default_factory=list)   # list of PulseTableStep
    filter_table: list = field(default_factory=list)  # list of FilterTableStep
    pulse_width: int = 0x0808  # initial pulse width (16-bit)
    wave_ptr: int = 0          # index into shared wave table (0=none, 1-based)
    vib_speed_idx: int = 0     # speed table index for vibrato (0=none)
    vib_delay: int = 0         # vibrato delay in frames
    vib_logarithmic: bool = False  # True=logarithmic vibrato (Hubbard-style: delta scales with pitch)
                                   # False=linear vibrato (GT2-style: fixed delta)
    pulse_ptr: int = 0         # pulse table index (0=no pulse mod)
    filter_ptr: int = 0        # filter table index (0=no filter mod)


@dataclass
class NoteEvent:
    """A single note/rest/control event in a pattern.

    command=None means no effect processing on this row.
    command=0 means effect 0 (instrument vibrato reload in GT2).
    These are distinct: None emits no FX byte, 0 emits $40/$50.
    """
    type: str = 'note'         # note, rest, off, on, tie
    note: int = 0              # note number 0-95 (C0=0, C4=48)
    duration: int = 1          # duration in ticks
    instrument: int = -1       # instrument change (-1 = no change)
    command: object = None     # pattern command 0-15, or None for no command
    command_val: int = 0       # command parameter byte


# Pattern command constants (match GT2)
CMD_NONE        = 0x00   # do nothing / instrument vibrato
CMD_PORTA_UP    = 0x01   # portamento up (speed table index)
CMD_PORTA_DOWN  = 0x02   # portamento down (speed table index)
CMD_TONE_PORTA  = 0x03   # tone portamento (speed table index, $00=tie)
CMD_VIBRATO     = 0x04   # vibrato (speed table index)
CMD_SET_AD      = 0x05   # set attack/decay
CMD_SET_SR      = 0x06   # set sustain/release
CMD_SET_WAVE    = 0x07   # set waveform
CMD_SET_WAVEPTR = 0x08   # set wave table pointer
CMD_SET_PULPTR  = 0x09   # set pulse table pointer
CMD_SET_FILTPTR = 0x0A   # set filter table pointer
CMD_SET_FILTCTL = 0x0B   # set filter control (resonance|routing)
CMD_SET_FILTCUT = 0x0C   # set filter cutoff
CMD_SET_MASTERVOL = 0x0D # set master volume ($00-$0F)
CMD_FUNKTEMPO   = 0x0E   # funktempo (speed table index)
CMD_SET_TEMPO   = 0x0F   # set tempo ($03-$7F=global, $83-$FF=channel)


@dataclass
class Pattern:
    """A pattern containing events for one voice."""
    id: int = 0
    events: list = field(default_factory=list)  # list of NoteEvent


@dataclass
class Song:
    """Complete song in USF."""
    title: str = ''
    author: str = ''
    sid_model: str = '6581'    # 6581 or 8580
    clock: str = 'PAL'         # PAL or NTSC
    tempo: int = 6             # default ticks per row
    instruments: list = field(default_factory=list)    # list of Instrument
    patterns: list = field(default_factory=list)        # list of Pattern
    orderlists: list = field(default_factory=lambda: [[], [], []])  # 3 voices
    # Each orderlist entry: (pattern_id, transpose)
    orderlist_restart: list = field(default_factory=lambda: [0, 0, 0])  # loop-back pattern entry index per voice
    speed_table: list = field(default_factory=list)    # list of SpeedTableEntry
    # Shared tables: list of (left_byte, right_byte) pairs in .sng format.
    # Instruments reference positions via wave_ptr, pulse_ptr, filter_ptr.
    # Wave table values are pre-transform (.sng-equivalent); the encoder
    # re-applies packed format transforms (left +$10, right XOR $80).
    shared_wave_table: list = field(default_factory=list)
    shared_pulse_table: list = field(default_factory=list)
    shared_filter_table: list = field(default_factory=list)
    freq_lo: bytes = None      # custom frequency table lo (96 bytes), or None for PAL
    freq_hi: bytes = None      # custom frequency table hi (96 bytes), or None for PAL
    first_note: int = 0        # first note in freq table (FIRSTNOTE optimization)
    nowavedelay: bool = True   # True=no wave delay (direct SID values), False=has +$10 bias
    # Player behavior group — determines how the player processes audio.
    # See docs/gt2_player_versions.md for full details.
    # Groups: A (v2.65-2.67), B (v2.68-2.72), C (v2.73-2.74), D (v2.76-2.77)
    gt2_player_group: str = ''  # 'A', 'B', 'C', 'D', or '' if unknown/not GT2
    # Hard restart ADSR parameters.
    # ADPARAM: AD value written during hard restart (default $0F).
    # SRPARAM: SR value written during hard restart (default $00).
    ad_param: int = 0x0F
    sr_param: int = 0x00
    # --- Player behavior fields ---
    # These control how the SIDfinity player processes audio. They are
    # generic (not GT2-specific) — any source format populates them.
    # ADSR register write order during hard restart and new-note init.
    # 'ad_first' = write AD then SR (GT2 Group A)
    # 'sr_first' = write SR then AD (GT2 Groups B/C/D, default)
    adsr_write_order: str = 'sr_first'
    # ADSR write order in per-frame buffered register writes (loadregs).
    # Group C reverted to 'ad_first' here while keeping 'sr_first' elsewhere.
    loadregs_adsr_order: str = 'sr_first'
    # Which registers are written on the new-note frame.
    # 'all_regs' = freq+pulse+ADSR+wave (GT2 with BUFFEREDWRITES, most common)
    # 'wave_only' = only waveform+gate, defer rest to next frame (GT2 non-buffered)
    newnote_reg_scope: str = 'all_regs'
    # Ghost register mode: shadow buffer flushed at frame start.
    # 'none' = direct SID writes (most files)
    # 'full' = 25-byte shadow buffer in RAM
    # 'zp' = shadow buffer in zero page
    ghost_regs: str = 'none'
    # Vibrato parameter zeroing fix. When True, zero the vibrato param
    # when instrument has no vibrato but pattern command does.
    # False = Groups A/B/C (stale accumulator possible), True = Group D
    vibrato_param_fix: bool = False
    # NOCALCULATEDSPEED: True = original binary does not support calculated speed.
    # Speed table left byte with bit 7 set is just a regular high byte, not a
    # "use calculated speed" flag. False = calculated speed supported (default).
    nocalculatedspeed: bool = False
    # Pulse speed ASL: original player uses ASL to double pulse speed before
    # adding to accumulator. False = CLC (no doubling, default).
    pulse_speed_asl: bool = False
    multiplier: int = 0        # multispeed: 0=normal, 2-8=CIA timer multiplier (2.1% of GT2 files)
    psid_flags: int = 0x0014   # PSID header flags: clock + SID model (GT2-specific)
    songs: int = 1             # number of subtunes (NUMSONGS)
    # Extra orderlists for multi-song files (songs > 1).
    # Layout: extra_orderlists[i] for i in range((songs-1)*3).
    extra_orderlists: list = field(default_factory=list)
    extra_orderlist_restart: list = field(default_factory=list)


# ============================================================
# Helpers
# ============================================================

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

WAVEFORM_NAMES = {
    'tri': 0x11, 'saw': 0x21, 'pulse': 0x41, 'noise': 0x81,
    'tri_gate': 0x11, 'saw_gate': 0x21, 'pulse_gate': 0x41, 'noise_gate': 0x81,
}

WAVEFORM_TOKENS = {0x10: 'TRI', 0x11: 'TRI', 0x20: 'SAW', 0x21: 'SAW',
                   0x40: 'PUL', 0x41: 'PUL', 0x80: 'NOI', 0x81: 'NOI'}


def note_name(n):
    """Convert note number (0-95) to name like C4."""
    if n < 0 or n > 95:
        return f'?{n}'
    return f'{NOTE_NAMES[n % 12]}{n // 12}'


def note_from_name(name):
    """Convert note name like C4, C#3 to number."""
    for i, n in enumerate(NOTE_NAMES):
        if name.startswith(n) and name[len(n):].isdigit():
            return i + int(name[len(n):]) * 12
    return -1


# ============================================================
# Conversion helpers
# ============================================================

def usf_to_json(song):
    """Serialize Song to JSON."""
    def obj_to_dict(obj):
        if hasattr(obj, '__dataclass_fields__'):
            return {k: obj_to_dict(v) for k, v in obj.__dict__.items()}
        elif isinstance(obj, list):
            return [obj_to_dict(x) for x in obj]
        elif isinstance(obj, tuple):
            return list(obj)
        return obj
    return json.dumps(obj_to_dict(song), indent=2)
