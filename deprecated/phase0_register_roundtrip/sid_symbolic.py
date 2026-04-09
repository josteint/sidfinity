"""
sid_symbolic.py - Convert SID register dumps to/from a symbolic music format.

The symbolic format represents SID music as a sequence of events per frame,
capturing musical intent rather than raw register values.

SID Register Map (per voice, offsets 0-6 / 7-13 / 14-20):
  0,1: Frequency (16-bit, lo/hi) -> musical pitch
  2,3: Pulse Width (12-bit, lo + hi&0x0F) -> timbre parameter
  4:   Control register:
         bit 0: Gate (trigger attack/release)
         bit 1: Sync (hard sync with modulator voice)
         bit 2: Ring Mod (ring modulate with modulator voice)
         bit 3: Test (reset oscillator, used in some tricks)
         bit 4: Triangle waveform
         bit 5: Sawtooth waveform
         bit 6: Pulse waveform
         bit 7: Noise waveform
  5:   Attack (hi nybble) / Decay (lo nybble)
  6:   Sustain (hi nybble) / Release (lo nybble)

Filter/Volume registers (21-24):
  21:  Filter cutoff lo (bits 0-2 only)
  22:  Filter cutoff hi (8 bits) -> 11-bit cutoff = (hi << 3) | lo
  23:  Filter control:
         bits 0-2: route voice 1/2/3 through filter
         bit 3: route external input through filter
         bits 4-7: resonance (4 bits)
  24:  Mode/Volume:
         bits 0-3: master volume
         bit 4: low-pass filter
         bit 5: band-pass filter
         bit 6: high-pass filter
         bit 7: mute voice 3 output

Frequency to note conversion:
  SID freq register -> Hz: freq_hz = freq_reg * cpu_clock / 16777216
  PAL cpu_clock = 985248, NTSC = 1022727
  Then Hz -> MIDI note: midi = 69 + 12 * log2(freq_hz / 440)
"""

import json
import math
import sys
from dataclasses import dataclass, field
from typing import TextIO


# SID frequency -> Hz conversion factor
PAL_CLOCK = 985248
NTSC_CLOCK = 1022727

# MIDI note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Waveform bit masks in control register
WAVE_TRIANGLE = 0x10
WAVE_SAWTOOTH = 0x20
WAVE_PULSE    = 0x40
WAVE_NOISE    = 0x80
GATE_BIT      = 0x01
SYNC_BIT      = 0x02
RING_BIT      = 0x04
TEST_BIT      = 0x08


def freq_to_note(freq_reg: int, clock: int = PAL_CLOCK) -> tuple[str, int]:
    """Convert SID frequency register value to note name and cents deviation.
    Returns (note_string, cents_off) e.g. ("C-4", -12) meaning 12 cents flat."""
    if freq_reg == 0:
        return ("---", 0)
    freq_hz = freq_reg * clock / 16777216.0
    if freq_hz < 1.0:
        return ("---", 0)
    midi_float = 69.0 + 12.0 * math.log2(freq_hz / 440.0)
    midi = round(midi_float)
    cents = round((midi_float - midi) * 100)
    if midi < 0 or midi > 127:
        return ("---", 0)
    octave = (midi // 12) - 1
    name = NOTE_NAMES[midi % 12]
    return (f"{name:>2s}-{octave}", cents)


def note_to_freq(note_str: str, cents: int = 0, clock: int = PAL_CLOCK) -> int:
    """Convert note string back to SID frequency register value.
    note_str like 'C-4', 'A#-3', etc."""
    if note_str.strip() == '---':
        return 0
    note_str = note_str.strip()
    if '-' in note_str:
        parts = note_str.rsplit('-', 1)
        note_name = parts[0].strip()
        octave = int(parts[1])
    else:
        return 0
    try:
        note_idx = NOTE_NAMES.index(note_name)
    except ValueError:
        return 0
    midi = (octave + 1) * 12 + note_idx
    midi_float = midi + cents / 100.0
    freq_hz = 440.0 * (2.0 ** ((midi_float - 69.0) / 12.0))
    freq_reg = round(freq_hz * 16777216.0 / clock)
    return max(0, min(65535, freq_reg))


def decode_waveform(ctrl: int) -> str:
    """Decode control register waveform bits to a string."""
    waves = []
    if ctrl & WAVE_TRIANGLE: waves.append('T')
    if ctrl & WAVE_SAWTOOTH: waves.append('S')
    if ctrl & WAVE_PULSE:    waves.append('P')
    if ctrl & WAVE_NOISE:    waves.append('N')
    if not waves:
        return '-'
    return ''.join(waves)


def encode_waveform(wave_str: str) -> int:
    """Encode waveform string back to control register bits (waveform only)."""
    bits = 0
    if 'T' in wave_str: bits |= WAVE_TRIANGLE
    if 'S' in wave_str: bits |= WAVE_SAWTOOTH
    if 'P' in wave_str: bits |= WAVE_PULSE
    if 'N' in wave_str: bits |= WAVE_NOISE
    return bits


def decode_filter_mode(mode_vol: int) -> str:
    """Decode filter mode bits to string."""
    modes = []
    if mode_vol & 0x10: modes.append('LP')
    if mode_vol & 0x20: modes.append('BP')
    if mode_vol & 0x40: modes.append('HP')
    if not modes:
        return '-'
    return '+'.join(modes)


def encode_filter_mode(mode_str: str) -> int:
    """Encode filter mode string back to bits."""
    bits = 0
    if 'LP' in mode_str: bits |= 0x10
    if 'BP' in mode_str: bits |= 0x20
    if 'HP' in mode_str: bits |= 0x40
    return bits


@dataclass
class VoiceState:
    """Decoded state of one SID voice for a single frame."""
    note: str = '---'
    cents: int = 0
    freq_reg: int = 0
    gate: bool = False
    waveform: str = '-'
    sync: bool = False
    ring: bool = False
    test: bool = False
    pulse_width: int = 0  # 12-bit
    attack: int = 0       # 0-15
    decay: int = 0        # 0-15
    sustain: int = 0      # 0-15
    release: int = 0      # 0-15


@dataclass
class FilterState:
    """Decoded state of SID filter/volume for a single frame."""
    cutoff: int = 0       # 11-bit
    resonance: int = 0    # 0-15
    route_v1: bool = False
    route_v2: bool = False
    route_v3: bool = False
    route_ext: bool = False
    mode: str = '-'
    volume: int = 0       # 0-15
    mute_v3: bool = False


@dataclass
class Frame:
    """One frame of decoded SID state."""
    voices: list = field(default_factory=lambda: [VoiceState(), VoiceState(), VoiceState()])
    filt: FilterState = field(default_factory=FilterState)


def decode_frame(regs: list[int], clock: int = PAL_CLOCK) -> Frame:
    """Decode 25 raw register values into a Frame."""
    f = Frame()
    for v in range(3):
        base = v * 7
        freq_reg = regs[base] | (regs[base + 1] << 8)
        pw = regs[base + 2] | ((regs[base + 3] & 0x0F) << 8)
        ctrl = regs[base + 4]
        ad = regs[base + 5]
        sr = regs[base + 6]

        note, cents = freq_to_note(freq_reg, clock)
        f.voices[v] = VoiceState(
            note=note, cents=cents, freq_reg=freq_reg,
            gate=bool(ctrl & GATE_BIT),
            waveform=decode_waveform(ctrl),
            sync=bool(ctrl & SYNC_BIT),
            ring=bool(ctrl & RING_BIT),
            test=bool(ctrl & TEST_BIT),
            pulse_width=pw,
            attack=(ad >> 4) & 0x0F,
            decay=ad & 0x0F,
            sustain=(sr >> 4) & 0x0F,
            release=sr & 0x0F,
        )

    filt_lo = regs[21]
    filt_hi = regs[22]
    filt_ctrl = regs[23]
    mode_vol = regs[24]

    f.filt = FilterState(
        cutoff=(filt_hi << 3) | (filt_lo & 0x07),
        resonance=(filt_ctrl >> 4) & 0x0F,
        route_v1=bool(filt_ctrl & 0x01),
        route_v2=bool(filt_ctrl & 0x02),
        route_v3=bool(filt_ctrl & 0x04),
        route_ext=bool(filt_ctrl & 0x08),
        mode=decode_filter_mode(mode_vol),
        volume=mode_vol & 0x0F,
        mute_v3=bool(mode_vol & 0x80),
    )
    return f


def encode_frame(frame: Frame, clock: int = PAL_CLOCK) -> list[int]:
    """Encode a Frame back into 25 raw register values."""
    regs = [0] * 25
    for v in range(3):
        base = v * 7
        vs = frame.voices[v]

        # Use stored freq_reg if available, otherwise convert from note
        freq = vs.freq_reg if vs.freq_reg else note_to_freq(vs.note, vs.cents, clock)
        regs[base] = freq & 0xFF
        regs[base + 1] = (freq >> 8) & 0xFF
        regs[base + 2] = vs.pulse_width & 0xFF
        regs[base + 3] = (vs.pulse_width >> 8) & 0x0F

        ctrl = encode_waveform(vs.waveform)
        if vs.gate: ctrl |= GATE_BIT
        if vs.sync: ctrl |= SYNC_BIT
        if vs.ring: ctrl |= RING_BIT
        if vs.test: ctrl |= TEST_BIT
        regs[base + 4] = ctrl

        regs[base + 5] = (vs.attack << 4) | vs.decay
        regs[base + 6] = (vs.sustain << 4) | vs.release

    fs = frame.filt
    regs[21] = fs.cutoff & 0x07
    regs[22] = (fs.cutoff >> 3) & 0xFF
    filt_ctrl = (fs.resonance << 4)
    if fs.route_v1: filt_ctrl |= 0x01
    if fs.route_v2: filt_ctrl |= 0x02
    if fs.route_v3: filt_ctrl |= 0x04
    if fs.route_ext: filt_ctrl |= 0x08
    regs[23] = filt_ctrl

    mode_vol = fs.volume & 0x0F
    mode_vol |= encode_filter_mode(fs.mode)
    if fs.mute_v3: mode_vol |= 0x80
    regs[24] = mode_vol

    return regs


def parse_dump(input: TextIO) -> tuple[dict, list[Frame]]:
    """Parse siddump output into metadata and list of Frames."""
    metadata_line = input.readline().strip()
    metadata = json.loads(metadata_line)
    clock = PAL_CLOCK if metadata.get('clock') == 'PAL' else NTSC_CLOCK

    # Skip header line
    input.readline()

    frames = []
    for line in input:
        line = line.strip()
        if not line:
            continue
        hex_vals = line.split(',')
        regs = [int(h, 16) for h in hex_vals]
        frames.append(decode_frame(regs, clock))

    return metadata, frames


def format_symbolic(metadata: dict, frames: list[Frame], output: TextIO):
    """Write frames in human-readable symbolic format.

    Format per frame line:
    FRAME_NUM | V1: note wave gate pw adsr [flags] | V2: ... | V3: ... | F: cutoff res route mode vol
    """
    clock_str = metadata.get('clock', 'PAL')

    # Write metadata header
    output.write(f"# {metadata.get('title','')} - {metadata.get('author','')}"
                 f" ({metadata.get('released','')})\n")
    output.write(f"# clock={clock_str} model={metadata.get('sid_model','6581')}"
                 f" subtune={metadata.get('subtune',1)} songs={metadata.get('songs',1)}\n")
    output.write(f"# frames={len(frames)} fps={metadata.get('fps',50)}\n")
    output.write("#\n")

    prev = None
    for i, frame in enumerate(frames):
        parts = [f"{i:05d}"]
        for v in range(3):
            vs = frame.voices[v]
            gate_ch = '+' if vs.gate else '.'
            flags = ''
            if vs.sync: flags += 'S'
            if vs.ring: flags += 'R'
            if vs.test: flags += 'X'
            pw_str = f"{vs.pulse_width:03X}"
            adsr_str = f"{vs.attack:X}{vs.decay:X}{vs.sustain:X}{vs.release:X}"
            parts.append(
                f"{vs.note} {vs.freq_reg:04X} {vs.waveform:>2s}{gate_ch} {pw_str} {adsr_str}{flags}"
            )

        fs = frame.filt
        route = ''
        if fs.route_v1: route += '1'
        if fs.route_v2: route += '2'
        if fs.route_v3: route += '3'
        if fs.route_ext: route += 'E'
        if not route: route = '-'

        parts.append(
            f"{fs.cutoff:04X} {fs.resonance:X} {route:>3s} {fs.mode:>5s} {fs.volume:X}"
        )

        output.write(' | '.join(parts) + '\n')
    prev = frame


def parse_symbolic(input: TextIO) -> tuple[dict, list[Frame]]:
    """Parse symbolic format back into metadata and Frames."""
    metadata = {}
    frames = []

    for line in input:
        line = line.rstrip('\n')

        # Parse comment/header lines
        if line.startswith('#'):
            if 'clock=' in line:
                for token in line.split():
                    if token.startswith('clock='):
                        metadata['clock'] = token.split('=')[1]
                    elif token.startswith('model='):
                        metadata['sid_model'] = token.split('=')[1]
                    elif token.startswith('subtune='):
                        metadata['subtune'] = int(token.split('=')[1])
                    elif token.startswith('songs='):
                        metadata['songs'] = int(token.split('=')[1])
                    elif token.startswith('fps='):
                        metadata['fps'] = int(token.split('=')[1])
            if line.startswith('# ') and ' - ' in line and 'clock=' not in line and 'frames=' not in line:
                rest = line[2:]
                if ' (' in rest:
                    title_author, released = rest.rsplit(' (', 1)
                    released = released.rstrip(')')
                    if ' - ' in title_author:
                        title, author = title_author.split(' - ', 1)
                        metadata['title'] = title
                        metadata['author'] = author
                        metadata['released'] = released
            continue

        if not line.strip():
            continue

        # Parse frame line
        segments = line.split(' | ')
        if len(segments) < 5:
            continue

        clock = PAL_CLOCK if metadata.get('clock', 'PAL') == 'PAL' else NTSC_CLOCK
        frame = Frame()

        # Parse each voice segment
        for v in range(3):
            seg = segments[v + 1].strip()
            # Format: "note freq_hex wave+/. pw adsr[flags]"
            tokens = seg.split()
            if len(tokens) < 5:
                continue

            # Note: may be multi-char like "C#-4" or "---"
            note_str = tokens[0]

            # Raw frequency register (hex)
            freq_reg = int(tokens[1], 16)

            # Waveform + gate: e.g. "P+" or "S." or "TP+"
            wg = tokens[2]
            gate = wg.endswith('+')
            wave_str = wg[:-1]  # strip gate char

            # Pulse width (always hex)
            pw_str = tokens[3]
            pw = int(pw_str, 16)

            # ADSR + flags
            adsr_flags = tokens[4]
            adsr = adsr_flags[:4]
            flags = adsr_flags[4:]

            vs = frame.voices[v]
            vs.note = note_str
            vs.freq_reg = freq_reg
            vs.gate = gate
            vs.waveform = wave_str if wave_str != '-' else '-'
            vs.pulse_width = pw
            vs.attack = int(adsr[0], 16)
            vs.decay = int(adsr[1], 16)
            vs.sustain = int(adsr[2], 16)
            vs.release = int(adsr[3], 16)
            vs.sync = 'S' in flags
            vs.ring = 'R' in flags
            vs.test = 'X' in flags

        # Parse filter segment
        fseg = segments[4].strip()
        ftokens = fseg.split()
        if len(ftokens) >= 5:
            fs = frame.filt
            fs.cutoff = int(ftokens[0], 16)
            fs.resonance = int(ftokens[1], 16)
            route = ftokens[2]
            fs.route_v1 = '1' in route
            fs.route_v2 = '2' in route
            fs.route_v3 = '3' in route
            fs.route_ext = 'E' in route
            fs.mode = ftokens[3]
            fs.volume = int(ftokens[4], 16)

        frames.append(frame)

    return metadata, frames


def frames_to_regdump(metadata: dict, frames: list[Frame]) -> list[list[int]]:
    """Convert frames back to raw register values (list of 25-int lists)."""
    clock = PAL_CLOCK if metadata.get('clock', 'PAL') == 'PAL' else NTSC_CLOCK
    return [encode_frame(f, clock) for f in frames]


# ── CLI ──────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='SID register dump <-> symbolic format converter')
    sub = parser.add_subparsers(dest='command')

    # dump -> symbolic
    p_sym = sub.add_parser('to-symbolic', help='Convert siddump CSV to symbolic format')
    p_sym.add_argument('input', help='siddump output file (- for stdin)')
    p_sym.add_argument('-o', '--output', default='-', help='output file (- for stdout)')

    # symbolic -> dump
    p_reg = sub.add_parser('to-regs', help='Convert symbolic format back to register CSV')
    p_reg.add_argument('input', help='symbolic format file (- for stdin)')
    p_reg.add_argument('-o', '--output', default='-', help='output file (- for stdout)')

    # roundtrip test
    p_rt = sub.add_parser('roundtrip', help='Test roundtrip: dump -> symbolic -> dump, report errors')
    p_rt.add_argument('input', help='siddump output file (- for stdin)')

    args = parser.parse_args()

    if args.command == 'to-symbolic':
        inp = sys.stdin if args.input == '-' else open(args.input)
        out = sys.stdout if args.output == '-' else open(args.output, 'w')
        metadata, frames = parse_dump(inp)
        format_symbolic(metadata, frames, out)
        if args.input != '-': inp.close()
        if args.output != '-': out.close()

    elif args.command == 'to-regs':
        inp = sys.stdin if args.input == '-' else open(args.input)
        out = sys.stdout if args.output == '-' else open(args.output, 'w')
        metadata, frames = parse_symbolic(inp)
        clock = PAL_CLOCK if metadata.get('clock', 'PAL') == 'PAL' else NTSC_CLOCK
        # Write metadata JSON
        out.write(json.dumps(metadata) + '\n')
        # Write header
        out.write('V1_FREQ_LO,V1_FREQ_HI,V1_PW_LO,V1_PW_HI,V1_CTRL,V1_AD,V1_SR,'
                  'V2_FREQ_LO,V2_FREQ_HI,V2_PW_LO,V2_PW_HI,V2_CTRL,V2_AD,V2_SR,'
                  'V3_FREQ_LO,V3_FREQ_HI,V3_PW_LO,V3_PW_HI,V3_CTRL,V3_AD,V3_SR,'
                  'FILT_LO,FILT_HI,FILT_CTRL,FILT_MODE_VOL\n')
        for frame in frames:
            regs = encode_frame(frame, clock)
            out.write(','.join(f'{r:02X}' for r in regs) + '\n')
        if args.input != '-': inp.close()
        if args.output != '-': out.close()

    elif args.command == 'roundtrip':
        inp = sys.stdin if args.input == '-' else open(args.input)
        metadata, frames = parse_dump(inp)
        if args.input != '-': inp.close()

        clock = PAL_CLOCK if metadata.get('clock', 'PAL') == 'PAL' else NTSC_CLOCK

        # Re-read original register values
        inp2 = sys.stdin if args.input == '-' else open(args.input)
        inp2.readline()  # metadata
        inp2.readline()  # header
        orig_regs = []
        for line in inp2:
            line = line.strip()
            if line:
                orig_regs.append([int(h, 16) for h in line.split(',')])
        if args.input != '-': inp2.close()

        # Encode frames back to registers
        recon_regs = [encode_frame(f, clock) for f in frames]

        # Mask for bits that actually matter to the SID chip
        # PW_HI registers (indices 3, 10, 17) only use lower 4 bits
        # Filter cutoff lo (index 21) only uses lower 3 bits
        reg_mask = [0xFF] * 25
        for pw_reg in (3, 10, 17):
            reg_mask[pw_reg] = 0x0F
        reg_mask[21] = 0x07

        # Compare
        total_errors = 0
        total_values = 0
        max_diff = 0
        error_by_reg = [0] * 25
        for i, (orig, recon) in enumerate(zip(orig_regs, recon_regs)):
            for r in range(25):
                total_values += 1
                diff = abs((orig[r] & reg_mask[r]) - (recon[r] & reg_mask[r]))
                if diff > 0:
                    total_errors += 1
                    error_by_reg[r] += diff
                    if diff > max_diff:
                        max_diff = diff

        print(f"Frames: {len(orig_regs)}")
        print(f"Total register values: {total_values}")
        print(f"Values with error: {total_errors} ({100*total_errors/total_values:.2f}%)")
        print(f"Max single-register difference: {max_diff}")
        print(f"Error-free: {total_errors == 0}")

        if total_errors > 0:
            reg_names = [
                "V1_FLO","V1_FHI","V1_PWLO","V1_PWHI","V1_CTRL","V1_AD","V1_SR",
                "V2_FLO","V2_FHI","V2_PWLO","V2_PWHI","V2_CTRL","V2_AD","V2_SR",
                "V3_FLO","V3_FHI","V3_PWLO","V3_PWHI","V3_CTRL","V3_AD","V3_SR",
                "FLT_LO","FLT_HI","FLT_CTL","FLT_MV"
            ]
            print("\nError by register (total absolute diff):")
            for r in range(25):
                if error_by_reg[r] > 0:
                    print(f"  {reg_names[r]:>8s}: {error_by_reg[r]}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
