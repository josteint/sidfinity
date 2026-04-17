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
    cycle_delay: int = 0       # Sub-frame delay in CPU cycles before applying this step.
                               # 0 = normal frame-based timing.
                               # >0 = delay N cycles within the current frame.
                               # Enables cycle-precise waveform changes for sync/phase tricks
                               # (e.g., enable hard sync for exactly 200 cycles then disable).


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

    When type='params', value = resonance<<4 | routing, where routing is:
      bit 0 = voice 1 filter enable
      bit 1 = voice 2 filter enable
      bit 2 = voice 3 filter enable
      bit 3 = external audio input (EXT IN) filter enable
    This maps directly to SID register $D417 (filter mode/volume):
      bits 4-7 = resonance, bits 0-3 = filter routing.
    """
    type: str = 'cutoff'       # 'cutoff', 'modulate', 'params', 'loop'
    value: int = 0             # cutoff value, speed, or resonance<<4|routing
    duration: int = 1          # modulation frame count
    is_loop: bool = False
    loop_target: int = 0
    cutoff_low: int = 0        # low 3 bits of filter cutoff ($D415, bits 0-2)
                               # Only used when type='cutoff'. Default 0 = 8-bit resolution
                               # (GT2 behavior). Non-zero enables full 11-bit precision
                               # for demo-scene players that write both $D415 and $D416.


@dataclass
class ModulationRoute:
    """Route oscillator 3 or envelope 3 output to a parameter.

    The SID chip allows reading voice 3's oscillator output ($D41B) and
    envelope output ($D41C). Advanced player engines use these as modulation
    sources — setting voice 3's frequency and waveform to create an LFO,
    then reading the output each frame to modulate filter cutoff, pulse
    width, frequency, or volume on any voice.

    When active, the player reads the source register each frame, applies
    scaling (arithmetic shift right by `scale` bits) and offset, then writes
    the result to the target parameter.
    """
    source: str = 'osc3'       # 'osc3' ($D41B) or 'env3' ($D41C)
    target: str = 'filter_cutoff'  # 'filter_cutoff', 'pulse_width', 'frequency', 'volume'
    voice: int = -1            # Target voice (0-2, -1=global for filter/volume)
    scale: int = 0             # Scaling factor (shift right N bits, 0=no scaling)
    offset: int = 0            # Signed offset added after scaling
    active: bool = True        # Can be toggled by pattern commands


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
class Sample:
    """A 4-bit audio sample for digi playback via SID volume register ($D418).

    The SID's master volume register can be abused as a 4-bit DAC by rapidly
    writing sample values to the low nibble. This technique was used by
    Mahoney, Martin Galway, THCM, and many others for speech, drums, and
    sampled instruments.

    Data is packed 2 samples per byte (high nibble first). At 8000 Hz on PAL
    (50 fps), each frame needs 160 samples = 80 bytes of packed data.
    """
    id: int = 0
    name: str = ''
    data: bytes = b''          # 4-bit samples packed: 2 samples per byte (high nibble first)
    rate: int = 8000           # Playback rate in Hz (typical: 4000-8000 for C64)
    loop_start: int = -1       # Loop point in samples (-1 = no loop)
    loop_end: int = -1         # Loop end point in samples (-1 = end of sample)


@dataclass
class NoteEvent:
    """A single note/rest/control event in a pattern.

    command=None means no effect processing on this row.
    command=0 means effect 0 (instrument vibrato reload in GT2).
    These are distinct: None emits no FX byte, 0 emits $40/$50.
    """
    type: str = 'note'         # note, rest, off, on, tie, digi
    note: int = 0              # note number 0-95 (C0=0, C4=48); for digi: sample_id
    duration: int = 1          # duration in ticks
    instrument: int = -1       # instrument change (-1 = no change)
    command: object = None     # pattern command 0-15, or None for no command
    command_val: int = 0       # command parameter byte (for digi: rate override, 0=use sample default)


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
CMD_SET_FILTCTL = 0x0B   # set filter control (resonance<<4 | routing)
                         # routing: bit0=voice1, bit1=voice2, bit2=voice3, bit3=EXT IN
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
class PaddleRoute:
    """Route paddle input to a music parameter for real-time control.

    The SID chip has two read-only paddle (potentiometer) registers:
      $D419 (POTX) — Paddle X analog input (0-255)
      $D41A (POTY) — Paddle Y analog input (0-255)

    Some engines read these to allow real-time performance control,
    modulating filter cutoff, tempo, or other parameters based on
    paddle position. This is extremely niche but exists in the SID ecosystem.
    """
    source: str = 'potx'          # 'potx' ($D419) or 'poty' ($D41A)
    target: str = 'filter_cutoff' # Parameter to modulate
    voice: int = -1               # Target voice (-1=global)
    min_val: int = 0              # Minimum output value
    max_val: int = 255            # Maximum output value


@dataclass
class Song:
    """Complete song in USF."""
    title: str = ''
    author: str = ''
    sid_model: str = '6581'    # 6581 or 8580
    clock: str = 'PAL'         # PAL or NTSC
    tempo: int = 6             # default ticks per row
    samples: list = field(default_factory=list)          # list of Sample (4-bit digi samples)
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
    filter_cutoff_low: int = 0  # default $D415 value (low 3 bits of filter cutoff, usually 0)
                               # GT2 always writes 0. Demo-scene players may set this globally.
    ext_audio_in: bool = False  # True if song uses external audio input (filter routing bit 3)
    multiplier: int = 0        # multispeed: 0=normal, 2-8=CIA timer multiplier (2.1% of GT2 files)
    psid_flags: int = 0x0014   # PSID header flags: clock + SID model (GT2-specific)
    songs: int = 1             # number of subtunes (NUMSONGS)
    # Extra orderlists for multi-song files (songs > 1).
    # Layout: extra_orderlists[i] for i in range((songs-1)*3).
    extra_orderlists: list = field(default_factory=list)
    extra_orderlist_restart: list = field(default_factory=list)
    # Oscillator 3 / Envelope 3 modulation routing
    modulation_routes: list = field(default_factory=list)  # list of ModulationRoute
    voice3_as_modulator: bool = False  # True = voice 3 is used as modulation source, not audio
    paddle_routes: list = field(default_factory=list)  # list of PaddleRoute
    cycle_precise: bool = False    # True = player uses cycle-counted timing for wave table steps


# ============================================================
# Helpers
# ============================================================

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

WAVEFORM_NAMES = {
    'tri': 0x11, 'saw': 0x21, 'pulse': 0x41, 'noise': 0x81,
    'tri_gate': 0x11, 'saw_gate': 0x21, 'pulse_gate': 0x41, 'noise_gate': 0x81,
    # Ring modulation (bit 2 of $D404)
    'tri_ring': 0x15, 'saw_ring': 0x25, 'pulse_ring': 0x45,
    'tri_ring_gate': 0x15, 'saw_ring_gate': 0x25, 'pulse_ring_gate': 0x45,
    # Hard sync (bit 1 of $D404)
    'tri_sync': 0x13, 'saw_sync': 0x23, 'pulse_sync': 0x43,
    'tri_sync_gate': 0x13, 'saw_sync_gate': 0x23, 'pulse_sync_gate': 0x43,
    # Ring + sync combined
    'tri_ring_sync': 0x17, 'saw_ring_sync': 0x27, 'pulse_ring_sync': 0x47,
    'tri_ring_sync_gate': 0x17, 'saw_ring_sync_gate': 0x27, 'pulse_ring_sync_gate': 0x47,
}

WAVEFORM_TOKENS = {
    0x10: 'TRI', 0x11: 'TRI', 0x20: 'SAW', 0x21: 'SAW',
    0x40: 'PUL', 0x41: 'PUL', 0x80: 'NOI', 0x81: 'NOI',
    # Ring modulation variants
    0x14: 'TRR', 0x15: 'TRR', 0x24: 'SAR', 0x25: 'SAR',
    0x44: 'PUR', 0x45: 'PUR',
    # Hard sync variants
    0x12: 'TRS', 0x13: 'TRS', 0x22: 'SAS', 0x23: 'SAS',
    0x42: 'PUS', 0x43: 'PUS',
    # Ring + sync combined
    0x16: 'TXS', 0x17: 'TXS', 0x26: 'SXS', 0x27: 'SXS',
    0x46: 'PXS', 0x47: 'PXS',
}

# Reverse map: token string -> waveform name (for detokenize)
TOKEN_TO_WAVEFORM = {
    'TRI': 'tri', 'SAW': 'saw', 'PUL': 'pulse', 'NOI': 'noise',
    'TRR': 'tri_ring', 'SAR': 'saw_ring', 'PUR': 'pulse_ring',
    'TRS': 'tri_sync', 'SAS': 'saw_sync', 'PUS': 'pulse_sync',
    'TXS': 'tri_ring_sync', 'SXS': 'saw_ring_sync', 'PXS': 'pulse_ring_sync',
}


def waveform_from_byte(sid_byte):
    """Derive USF waveform name from a SID control register byte ($D404).

    Extracts waveform select (bits 7-4), ring mod (bit 2), and sync (bit 1).
    Gate (bit 0) and test (bit 3) are ignored for waveform naming.

    Returns a waveform string like 'pulse', 'tri_ring', 'saw_sync', etc.
    """
    wave_bits = (sid_byte >> 4) & 0xF
    ring = bool(sid_byte & 0x04)
    sync = bool(sid_byte & 0x02)
    base = {1: 'tri', 2: 'saw', 4: 'pulse', 8: 'noise'}.get(wave_bits, 'pulse')
    if ring and sync:
        return f'{base}_ring_sync'
    elif ring:
        return f'{base}_ring'
    elif sync:
        return f'{base}_sync'
    return base


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
