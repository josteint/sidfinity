"""py65 trace of Hawkeye init + N frames of play().

Dumps per-voice runtime variables at $90C5..$913B and SID register
writes per frame. Output infers variable roles from update patterns
(Cybernoid II names) and saves to `trace_subtune<N>.txt`.

Anchored variable names per `RE_NOTES.md`'s tentative layout. The
trace verifies (or refutes) that layout.

Usage:
    PYTHONPATH=tools/py65_lib python3 pipelines/future_composer/hawkeye/trace.py
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'tools', 'py65_lib'))

from py65.devices.mpu6502 import MPU

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
SID_PATH = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'T', 'Tel_Jeroen',
                        'Hawkeye.sid')

# Anchored at $90C5 per the signature scan. The variable layout is
# Cybernoid II's verbatim sequence; the trace tells us where each
# array actually lives in Hawkeye.
VAR_LAYOUT = [
    # (offset_from_90C5, size_per_voice, name)
    (0x00, 3, 'tabcount'),       # sequence-read pos per voice
    (0x03, 3, 'begcount'),       # pattern-read pos per voice
    (0x06, 3, 'nootcount'),      # frames-remaining on current note
    (0x09, 3, 'nootleng'),       # total length of current note
    (0x0c, 3, 'wavesto'),        # current waveform ctrl byte
    (0x0f, 3, 'noothoogt'),      # note pitch high?
    (0x12, 3, 'noho'),
    (0x15, 3, 'wavecount'),      # wave-table cursor
    (0x18, 3, 'hinotesto'),
    (0x1b, 3, 'hinotesto2'),
    (0x1e, 3, 'lonotesto'),
    (0x21, 3, 'glidetest'),
    (0x24, 3, 'glidetest2'),
    (0x27, 3, 'pulsestolo'),
    (0x2a, 3, 'pulsehisto'),
    (0x2d, 3, 'pulsehitemp'),
    (0x30, 1, 'pulsecountup'),
    (0x31, 3, 'counter2'),       # incremented at top of play
    (0x34, 3, 'toneadd'),        # transpose offset
    (0x37, 3, 'vibstore1'),
    (0x3a, 3, 'vibstore2'),
    (0x3d, 3, 'vibstore3'),
    (0x40, 3, 'tonearpcounter'),
    (0x43, 3, 'arpieoklo'),
    (0x46, 3, 'arpieokhi'),
    (0x49, 1, 'st2'),
    (0x4a, 1, 'st'),
    (0x4b, 3, 'filter'),
    (0x4e, 3, 'filtercount'),
    (0x51, 1, 'speedsto'),       # global speed counter (Hawkeye $9116)
    # rest of region: repeatsto, stod404, ... voiceinc
    (0x53, 3, 'repeatsto'),      # Hawkeye $9118
    (0x56, 3, 'stod404'),
    (0x59, 3, 'newnote'),
    (0x5c, 1, 'strfiltest'),
    (0x5d, 3, 'tempglide'),
    (0x60, 3, 'glidedelay'),
    (0x63, 1, 'strafil'),
    (0x64, 3, 'd400'),
    (0x67, 3, 'd401'),
    (0x6a, 3, 'voiceinc'),       # Hawkeye $9139
]
VAR_BASE = 0x90C5
SID_BASE = 0xD400
SID_END  = 0xD418  # inclusive


def load_sid(sid_path):
    """Return (load_addr, init_addr, play_addr, code_bytes) from PSID."""
    with open(sid_path, 'rb') as f:
        d = f.read()
    assert d[:4] == b'PSID', 'not a PSID'
    hl = struct.unpack('>H', d[6:8])[0]
    la = struct.unpack('>H', d[8:10])[0]
    init = struct.unpack('>H', d[10:12])[0]
    play = struct.unpack('>H', d[12:14])[0]
    code = d[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    return la, init, play, code


def setup_mpu(load_addr, code):
    mem = bytearray(65536)
    mem[load_addr:load_addr + len(code)] = code
    # BRK at $FFF0 so RTS lands on BRK and we can stop the stepper
    mem[0xFFF0] = 0x00
    m = MPU()
    m.memory = bytearray(mem)
    return m


def call(m, addr, a=0, max_steps=200000):
    """Push BRK return, set PC, run until BRK."""
    m.stPush(0xFF)
    m.stPush(0xEF)
    m.pc = addr
    m.a = a
    for n in range(max_steps):
        if m.memory[m.pc] == 0x00:  # BRK
            return n
        m.step()
    raise RuntimeError(f'overran {max_steps} steps at PC={m.pc:04X}')


class SidWriteCapture:
    """Watch writes to $D400..$D418 by snapshotting before+after."""
    def __init__(self, m):
        self.m = m
        self.before = bytes(m.memory[SID_BASE:SID_END + 1])

    def capture(self):
        after = bytes(self.m.memory[SID_BASE:SID_END + 1])
        diffs = []
        for i, (b, a) in enumerate(zip(self.before, after)):
            if b != a:
                diffs.append((SID_BASE + i, b, a))
        self.before = after
        return diffs


def dump_vars(mem):
    return bytes(mem[VAR_BASE:VAR_BASE + 0x77])


def format_diff(old, new, voice_count=3):
    lines = []
    for offset, size, name in VAR_LAYOUT:
        slc = slice(offset, offset + size)
        ob = old[slc]
        nb = new[slc]
        if ob == nb:
            continue
        per_voice = []
        for v in range(size):
            if ob[v] != nb[v]:
                per_voice.append(f'V{v}:${ob[v]:02X}->${nb[v]:02X}')
            else:
                per_voice.append(f'V{v}:${ob[v]:02X}')
        lines.append(f'  {name:16s} {" ".join(per_voice)}')
    return lines


def trace_subtune(subtune, n_frames=15):
    print(f'\n{"="*70}')
    print(f'Subtune {subtune}  ({n_frames} frames)')
    print('=' * 70)
    load_addr, init_addr, play_addr, code = load_sid(SID_PATH)
    print(f'load=${load_addr:04X}  init=${init_addr:04X}  play=${play_addr:04X}')
    m = setup_mpu(load_addr, code)

    # Init
    init_steps = call(m, init_addr, a=subtune)
    print(f'init: {init_steps} steps')

    print(f'\nState after init (only non-zero bytes in $90C5..$913B):')
    state = dump_vars(m.memory)
    for offset, size, name in VAR_LAYOUT:
        slc = slice(offset, offset + size)
        b = state[slc]
        if any(b):
            print(f'  {name:16s} {" ".join(f"${x:02X}" for x in b)}')

    # SMC sites we know about
    smc_sites = [
        (0x7B99, 'testbyte (play dispatcher state)'),
        (0x7AFE, 'speedbyte'),
        (0x910A, 'st2 scratch (or repeats?)'),
        (0x9116, 'speedsto global counter'),
    ]
    print(f'\nKnown SMC / global sites:')
    for addr, label in smc_sites:
        print(f'  ${addr:04X}: ${m.memory[addr]:02X}  ({label})')

    # Frame-by-frame play()
    cap = SidWriteCapture(m)
    prev_state = dump_vars(m.memory)
    for frame in range(n_frames):
        steps = call(m, play_addr)
        new_state = dump_vars(m.memory)
        sid_writes = cap.capture()
        print(f'\n--- frame {frame:2d}  ({steps} cycles) ---')
        diffs = format_diff(prev_state, new_state)
        if diffs:
            print('  variable changes:')
            for line in diffs:
                print('  ' + line)
        else:
            print('  (no variable changes)')
        if sid_writes:
            print('  SID writes:')
            grouped = {}
            for addr, old, new in sid_writes:
                reg = addr - SID_BASE
                grouped.setdefault(reg, (old, new))
            for reg in sorted(grouped):
                old, new = grouped[reg]
                print(f'    $D4{reg:02X}: ${old:02X} -> ${new:02X}')
        for addr, label in smc_sites:
            if m.memory[addr] != 0 or label.startswith('testbyte'):
                pass  # could spot SMC drift
        prev_state = new_state


def main():
    # Trace subtune 0 first; we can extend to others.
    trace_subtune(0, n_frames=10)


if __name__ == '__main__':
    main()
