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
    """One step in a wave table program."""
    waveform: int = 0x41       # SID waveform byte (e.g. $41 = pulse+gate)
    note_offset: int = 0       # relative semitone offset (negative = down)
    absolute_note: int = -1    # if >= 0, absolute note instead of relative
    is_loop: bool = False      # if True, this is a loop-to target
    loop_target: int = 0       # loop destination step index


@dataclass
class Instrument:
    """Instrument definition."""
    id: int = 0
    ad: int = 0x09             # attack/decay
    sr: int = 0x00             # sustain/release
    waveform: str = 'pulse'    # tri, saw, pulse, noise
    gate_timer: int = 2        # hard restart lead time (frames)
    hr_method: str = 'gate'    # none, gate, test, adsr
    wave_table: list = field(default_factory=list)  # list of WaveTableStep
    pulse_width: int = 0x0808  # initial pulse width (16-bit)


@dataclass
class NoteEvent:
    """A single note/rest/control event in a pattern."""
    type: str = 'note'         # note, rest, off, on, tie
    note: int = 0              # note number 0-95 (C0=0, C4=48)
    duration: int = 1          # duration in ticks
    instrument: int = -1       # instrument change (-1 = no change)


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
    instruments: list = field(default_factory=list)  # list of Instrument
    patterns: list = field(default_factory=list)      # list of Pattern
    orderlists: list = field(default_factory=lambda: [[], [], []])  # 3 voices
    # Each orderlist entry: (pattern_id, transpose)
    freq_lo: bytes = None       # custom frequency table lo (96 bytes), or None for PAL
    freq_hi: bytes = None       # custom frequency table hi (96 bytes), or None for PAL


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

        # Wave table
        if inst.wave_table:
            tokens.append('WT[')
            for step in inst.wave_table:
                if step.is_loop:
                    tokens.append(f'L{step.loop_target}')
                elif step.absolute_note >= 0:
                    tokens.append(f'{WAVEFORM_TOKENS.get(step.waveform, "?")}'
                                  f'={note_name(step.absolute_note)}')
                else:
                    off = step.note_offset
                    sign = '+' if off >= 0 else ''
                    tokens.append(f'{WAVEFORM_TOKENS.get(step.waveform, "?")}'
                                  f'{sign}{off}')
            tokens.append(']WT')

        tokens.append('/INST')

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
                elif t2.startswith('GT'):
                    inst.gate_timer = int(t2[2:], 16)
                elif t2 == 'WT[':
                    i += 1
                    while i < len(tokens) and tokens[i] != ']WT':
                        wt = tokens[i]
                        step = WaveTableStep()
                        if wt.startswith('L'):
                            step.is_loop = True
                            step.loop_target = int(wt[1:])
                        elif '=' in wt:
                            # Absolute note: PUL=C4
                            parts = wt.split('=')
                            step.waveform = WAVEFORM_NAMES.get(parts[0].lower() + '_gate', 0x41)
                            step.absolute_note = note_from_name(parts[1])
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
