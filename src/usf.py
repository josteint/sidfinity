"""
usf.py - Universal Symbolic Format for SID music.

The intermediate representation between any SID player's native format
and the SIDfinity player output. Also the tokenization format for ML training.

Design goals:
- Compact: a 3-minute tune = 2000-4000 tokens
- Event-based with durations (not grid-based per-frame)
- Explicit structure: instruments defined once, patterns reused, orderlists reference patterns
- Fixed vocabulary for transformer tokenization (~300 tokens)

Token vocabulary:
  Song:     SONG_START SONG_END SID_6581 SID_8580 CLOCK_PAL CLOCK_NTSC
  Inst:     INST_DEF INST_END AD_00..AD_FF SR_00..SR_FF WAVE_TRI WAVE_SAW WAVE_PULSE WAVE_NOISE
            HR_NONE HR_GATE HR_TEST HR_ADSR GATE_TIMER_0..GATE_TIMER_F
            WT_START WT_END WT_LOOP WT_REL_0..WT_REL_B WT_ABS_C0..WT_ABS_B7
  Pattern:  PAT_START PAT_END
  Voice:    V1 V2 V3
  Notes:    C0..B7 (96 note tokens)
  Duration: D1..D32 (duration in ticks)
  Control:  REST OFF ON TIE
  Effects:  PORTA_UP PORTA_DN VIBRATO GLIDE
  Order:    ORDER_START ORDER_END LOOP PAT_REF_0..PAT_REF_FF TRANS_N8..TRANS_P7
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
    # Player behavior group — determines how the player processes audio.
    # See docs/gt2_player_versions.md for full details.
    # Groups: A (v2.65-2.67), B (v2.68-2.72), C (v2.73-2.74), D (v2.76-2.77)
    gt2_player_group: str = ''  # 'A', 'B', 'C', 'D', or '' if unknown/not GT2
    # Hard restart ADSR parameters (GT2-specific).
    # ADPARAM: AD value written during hard restart (default $0F).
    # SRPARAM: SR value written during hard restart (default $00).
    ad_param: int = 0x0F
    sr_param: int = 0x00


# ============================================================
# Tokenization
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


def tokenize(song):
    """Convert a Song to a list of string tokens.

    This is the format used for ML training.
    """
    tokens = []

    # Song header
    tokens.append('SONG')
    tokens.append(f'SID_{song.sid_model}')
    tokens.append(song.clock)
    tokens.append(f'T{song.tempo}')

    # Instruments
    for inst in song.instruments:
        tokens.append('INST')
        tokens.append(f'AD{inst.ad:02X}')
        tokens.append(f'SR{inst.sr:02X}')
        tokens.append(inst.waveform.upper()[:3])
        tokens.append(f'HR_{inst.hr_method.upper()}')
        tokens.append(f'GT{inst.gate_timer:X}')
        if inst.legato:
            tokens.append('LEG')
        if inst.vib_speed_idx > 0:
            tokens.append(f'VIB{inst.vib_speed_idx:X}')
        if inst.vib_delay > 0:
            tokens.append(f'VD{inst.vib_delay:X}')
        if inst.first_wave >= 0:
            tokens.append(f'FW{inst.first_wave:02X}')

        # Wave table
        if inst.wave_table:
            tokens.append('WT[')
            for step in inst.wave_table:
                if step.is_loop:
                    tokens.append(f'L{step.loop_target}')
                elif step.keep_freq:
                    wt = WAVEFORM_TOKENS.get(step.waveform, f'${step.waveform:02X}')
                    tokens.append(f'{wt}~')  # ~ means keep freq
                elif step.delay > 0:
                    tokens.append(f'W{step.delay}')  # delay N frames
                elif step.absolute_note >= 0:
                    wt = WAVEFORM_TOKENS.get(step.waveform, f'${step.waveform:02X}')
                    tokens.append(f'{wt}={note_name(step.absolute_note)}')
                else:
                    off = step.note_offset
                    sign = '+' if off >= 0 else ''
                    wt = WAVEFORM_TOKENS.get(step.waveform, f'${step.waveform:02X}')
                    tokens.append(f'{wt}{sign}{off}')
            tokens.append(']WT')

        # Pulse table
        if inst.pulse_table:
            tokens.append('PT[')
            for step in inst.pulse_table:
                if step.is_loop:
                    tokens.append(f'L{step.loop_target}')
                elif step.is_set:
                    tokens.append(f'={step.value:02X}{step.low_byte:02X}')
                else:
                    tokens.append(f'm{step.value:+d}x{step.duration}')
            tokens.append(']PT')

        # Filter table
        if inst.filter_table:
            tokens.append('FT[')
            for step in inst.filter_table:
                if step.is_loop:
                    tokens.append(f'L{step.loop_target}')
                elif step.type == 'cutoff':
                    tokens.append(f'C{step.value:02X}')
                elif step.type == 'modulate':
                    tokens.append(f'm{step.value:+d}x{step.duration}')
                elif step.type == 'params':
                    tokens.append(f'R{step.value:02X}')
            tokens.append(']FT')

        tokens.append('/INST')

    # Speed table
    if song.speed_table:
        tokens.append('SPD[')
        for entry in song.speed_table:
            tokens.append(f'{entry.left:02X}{entry.right:02X}')
        tokens.append(']SPD')

    # Patterns
    for patt in song.patterns:
        tokens.append(f'PAT{patt.id}')

        current_inst = -1
        for event in patt.events:
            if event.instrument >= 0 and event.instrument != current_inst:
                tokens.append(f'I{event.instrument}')
                current_inst = event.instrument

            if event.type == 'note':
                tokens.append(note_name(event.note))
            elif event.type == 'rest':
                tokens.append('.')
            elif event.type == 'off':
                tokens.append('OFF')
            elif event.type == 'on':
                tokens.append('ON')
            elif event.type == 'tie':
                tokens.append('TIE')

            if event.command is not None and event.command > 0:
                tokens.append(f'x{event.command:X}{event.command_val:02X}')

            if event.duration > 1:
                tokens.append(f'd{event.duration}')

        tokens.append('/PAT')

    # Orderlists
    tokens.append('ORD')
    for vi in range(3):
        tokens.append(f'V{vi + 1}')
        for patt_id, transpose in song.orderlists[vi]:
            if transpose != 0:
                tokens.append(f'T{"+" if transpose > 0 else ""}{transpose}')
            tokens.append(f'P{patt_id}')
        tokens.append(f'/V{vi + 1}')
    tokens.append('/ORD')

    tokens.append('/SONG')
    return tokens


def detokenize(tokens):
    """Convert a list of tokens back to a Song.

    Inverse of tokenize().
    """
    song = Song()
    i = 0

    while i < len(tokens):
        t = tokens[i]

        if t == 'SONG':
            pass
        elif t.startswith('SID_'):
            song.sid_model = t[4:]
        elif t in ('PAL', 'NTSC'):
            song.clock = t
        elif t.startswith('T') and t[1:].isdigit():
            song.tempo = int(t[1:])
        elif t == 'INST':
            inst = Instrument(id=len(song.instruments))
            i += 1
            while i < len(tokens) and tokens[i] != '/INST':
                t2 = tokens[i]
                if t2.startswith('AD'):
                    inst.ad = int(t2[2:], 16)
                elif t2.startswith('SR'):
                    inst.sr = int(t2[2:], 16)
                elif t2 in ('TRI', 'SAW', 'PUL', 'NOI'):
                    inst.waveform = {'TRI': 'tri', 'SAW': 'saw', 'PUL': 'pulse', 'NOI': 'noise'}[t2]
                elif t2.startswith('HR_'):
                    inst.hr_method = t2[3:].lower()
                elif t2.startswith('GT') and len(t2) <= 4:
                    inst.gate_timer = int(t2[2:], 16)
                elif t2 == 'LEG':
                    inst.legato = True
                elif t2.startswith('VIB') and t2 != 'VIBRATO':
                    inst.vib_speed_idx = int(t2[3:], 16)
                elif t2.startswith('VD'):
                    inst.vib_delay = int(t2[2:], 16)
                elif t2.startswith('FW'):
                    inst.first_wave = int(t2[2:], 16)
                elif t2 == 'PT[':
                    i += 1
                    while i < len(tokens) and tokens[i] != ']PT':
                        pt = tokens[i]
                        step = PulseTableStep()
                        if pt.startswith('L'):
                            step.is_loop = True
                            step.loop_target = int(pt[1:])
                        elif pt.startswith('='):
                            step.is_set = True
                            step.value = int(pt[1:3], 16)
                            step.low_byte = int(pt[3:5], 16)
                        elif pt.startswith('m'):
                            # m+3x5 = modulate speed +3 for 5 frames
                            parts = pt[1:].split('x')
                            step.value = int(parts[0])
                            step.duration = int(parts[1]) if len(parts) > 1 else 1
                        inst.pulse_table.append(step)
                        i += 1
                elif t2 == 'FT[':
                    i += 1
                    while i < len(tokens) and tokens[i] != ']FT':
                        ft = tokens[i]
                        step = FilterTableStep()
                        if ft.startswith('L'):
                            step.is_loop = True
                            step.loop_target = int(ft[1:])
                        elif ft.startswith('C'):
                            step.type = 'cutoff'
                            step.value = int(ft[1:], 16)
                        elif ft.startswith('R'):
                            step.type = 'params'
                            step.value = int(ft[1:], 16)
                        elif ft.startswith('m'):
                            step.type = 'modulate'
                            parts = ft[1:].split('x')
                            step.value = int(parts[0])
                            step.duration = int(parts[1]) if len(parts) > 1 else 1
                        inst.filter_table.append(step)
                        i += 1
                elif t2 == 'WT[':
                    i += 1
                    while i < len(tokens) and tokens[i] != ']WT':
                        wt = tokens[i]
                        step = WaveTableStep()
                        if wt.startswith('L'):
                            step.is_loop = True
                            step.loop_target = int(wt[1:])
                        elif wt.startswith('W') and wt[1:].isdigit():
                            step.delay = int(wt[1:])
                        elif wt.endswith('~'):
                            # Keep freq: PUL~ SAW~ etc.
                            wn = wt[:-1]
                            step.waveform = WAVEFORM_NAMES.get(wn.lower() + '_gate', 0x41)
                            step.keep_freq = True
                        elif '=' in wt:
                            # Absolute note: PUL=C4
                            parts = wt.split('=')
                            step.waveform = WAVEFORM_NAMES.get(parts[0].lower() + '_gate', 0x41)
                            step.absolute_note = note_from_name(parts[1])
                        elif wt.startswith('$'):
                            # Raw hex waveform: $30+0
                            rest = wt[1:]
                            for sep in ('+', '-'):
                                if sep in rest:
                                    parts = rest.split(sep, 1)
                                    step.waveform = int(parts[0], 16)
                                    step.note_offset = int(sep + parts[1])
                                    break
                        else:
                            # Relative: PUL+4 or PUL-2 or PUL+0
                            for wn, wv in [('PUL', 0x41), ('SAW', 0x21), ('TRI', 0x11), ('NOI', 0x81)]:
                                if wt.startswith(wn):
                                    step.waveform = wv
                                    step.note_offset = int(wt[len(wn):])
                                    break
                        inst.wave_table.append(step)
                        i += 1
                i += 1
            song.instruments.append(inst)

        elif t.startswith('PAT'):
            patt_id = int(t[3:])
            patt = Pattern(id=patt_id)
            i += 1
            current_inst = -1
            while i < len(tokens) and tokens[i] != '/PAT':
                t2 = tokens[i]
                if t2.startswith('I') and t2[1:].isdigit():
                    current_inst = int(t2[1:])
                elif t2 == '.':
                    patt.events.append(NoteEvent(type='rest', instrument=current_inst))
                    current_inst = -1  # only set once
                elif t2 == 'OFF':
                    patt.events.append(NoteEvent(type='off'))
                elif t2 == 'ON':
                    patt.events.append(NoteEvent(type='on'))
                elif t2 == 'TIE':
                    patt.events.append(NoteEvent(type='tie'))
                elif t2.startswith('x') and len(t2) >= 4:
                    # Command: x1FF = command 1, param $FF
                    if patt.events:
                        patt.events[-1].command = int(t2[1], 16)
                        patt.events[-1].command_val = int(t2[2:4], 16)
                elif t2.startswith('d') and t2[1:].isdigit():
                    # Duration modifier for previous event
                    if patt.events:
                        patt.events[-1].duration = int(t2[1:])
                else:
                    # Try as note name
                    n = note_from_name(t2)
                    if n >= 0:
                        patt.events.append(NoteEvent(type='note', note=n,
                                                      instrument=current_inst))
                        current_inst = -1
                i += 1
            song.patterns.append(patt)

        elif t == 'ORD':
            pass
        elif t.startswith('V') and len(t) == 2 and t[1].isdigit():
            vi = int(t[1]) - 1
            i += 1
            current_trans = 0
            while i < len(tokens) and not tokens[i].startswith('/V'):
                t2 = tokens[i]
                if t2.startswith('T') and (t2[1] == '+' or t2[1] == '-' or t2[1:].lstrip('+-').isdigit()):
                    current_trans = int(t2[1:])
                elif t2.startswith('P') and t2[1:].isdigit():
                    patt_id = int(t2[1:])
                    song.orderlists[vi].append((patt_id, current_trans))
                    current_trans = 0
                i += 1

        elif t == 'SPD[':
            i += 1
            while i < len(tokens) and tokens[i] != ']SPD':
                s = tokens[i]
                if len(s) == 4:
                    song.speed_table.append(SpeedTableEntry(
                        left=int(s[:2], 16), right=int(s[2:], 16)))
                i += 1

        elif t == '/SONG':
            break

        i += 1

    return song


def to_text(tokens):
    """Convert token list to readable text with line breaks."""
    lines = []
    indent = 0
    line = []

    for t in tokens:
        if t.startswith('/'):
            if line:
                lines.append('  ' * indent + ' '.join(line))
                line = []
            indent = max(0, indent - 1)
            lines.append('  ' * indent + t)
        elif t in ('SONG', 'INST', 'ORD') or t.startswith('PAT') or (t.startswith('V') and len(t) == 2):
            if line:
                lines.append('  ' * indent + ' '.join(line))
                line = []
            lines.append('  ' * indent + t)
            indent += 1
        else:
            line.append(t)

    if line:
        lines.append('  ' * indent + ' '.join(line))

    return '\n'.join(lines)


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


# ============================================================
# Main: demo
# ============================================================

def main():
    """Create a demo USF song and show tokenization."""
    song = Song(
        title='Demo Song',
        author='SIDfinity',
        sid_model='6581',
        clock='PAL',
        tempo=6,
        instruments=[
            Instrument(id=0, ad=0x09, sr=0x00, waveform='pulse', hr_method='test',
                       gate_timer=2, wave_table=[
                           WaveTableStep(waveform=0x41, note_offset=0),
                           WaveTableStep(waveform=0x41, note_offset=4),
                           WaveTableStep(waveform=0x41, note_offset=7),
                           WaveTableStep(is_loop=True, loop_target=0),
                       ]),
            Instrument(id=1, ad=0x0A, sr=0xD9, waveform='saw', hr_method='gate',
                       gate_timer=2),
            Instrument(id=2, ad=0x0F, sr=0xE8, waveform='noise', hr_method='none',
                       gate_timer=0),
        ],
        patterns=[
            Pattern(id=0, events=[
                NoteEvent(type='note', note=48, duration=4, instrument=0),  # C4
                NoteEvent(type='note', note=52, duration=4),                 # E4
                NoteEvent(type='note', note=55, duration=4),                 # G4
                NoteEvent(type='note', note=60, duration=4),                 # C5
            ]),
            Pattern(id=1, events=[
                NoteEvent(type='note', note=24, duration=8, instrument=1),  # C2
                NoteEvent(type='note', note=29, duration=8),                 # F2
            ]),
            Pattern(id=2, events=[
                NoteEvent(type='note', note=36, duration=2, instrument=2),  # C3
                NoteEvent(type='off', duration=2),
                NoteEvent(type='note', note=36, duration=2),
                NoteEvent(type='off', duration=2),
            ]),
        ],
        orderlists=[
            [(0, 0), (0, 0), (0, 5), (0, 0)],   # V1: pattern 0, repeat, transpose +5, back
            [(1, 0), (1, 0), (1, 0), (1, 0)],     # V2: pattern 1 × 4
            [(2, 0), (2, 0), (2, 0), (2, 0)],     # V3: pattern 2 × 4
        ],
    )

    tokens = tokenize(song)
    print(f'Token count: {len(tokens)}')
    print(f'Vocabulary: {len(set(tokens))} unique tokens')
    print()
    print(to_text(tokens))
    print()

    # Roundtrip test
    song2 = detokenize(tokens)
    tokens2 = tokenize(song2)
    if tokens == tokens2:
        print('Roundtrip: PASS')
    else:
        print('Roundtrip: FAIL')
        for i, (a, b) in enumerate(zip(tokens, tokens2)):
            if a != b:
                print(f'  Diff at {i}: {a!r} vs {b!r}')
                break


if __name__ == '__main__':
    main()
