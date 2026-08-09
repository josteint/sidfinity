"""Read Hawkeye's data sections from the loaded binary and decode
them. Verifies the data layout proposed in RE_NOTES.md.

Reads:
- Per-subtune speedbyte table at $83FC
- Per-subtune sequence-pointer tables at $83F5 / $7AFF
- Per-pattern sequence-pointer table at $8409 (pat_id*2 → addr)
- Freq table at $8337 (lo) / $8396 (hi) — 96 entries each
- Instrument table columns at $8580 / $8589 (low + high bytes)
- Per-instrument 8-byte records at $860C..$861?

Walks the sequence stream for voice 1 of subtune 0 to validate
the sequence command byte semantics. Walks pattern 0 to validate
the pattern byte semantics.

Usage:
    PYTHONPATH=tools/py65_lib python3 \\
        pipelines/future_composer/hawkeye/data_dump.py
"""
import os
import struct
import sys

sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'tools', 'py65_lib'))

from py65.devices.mpu6502 import MPU

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
SID_PATH = os.path.join(ROOT, 'hvsc85', 'MUSICIANS', 'T', 'Tel_Jeroen',
                        'Hawkeye.sid')


def load_sid(sid_path):
    with open(sid_path, 'rb') as f:
        d = f.read()
    hl = struct.unpack('>H', d[6:8])[0]
    la = struct.unpack('>H', d[8:10])[0]
    init = struct.unpack('>H', d[10:12])[0]
    play = struct.unpack('>H', d[12:14])[0]
    n_songs = struct.unpack('>H', d[14:16])[0]
    code = d[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    return la, init, play, n_songs, code


def setup_mpu(load_addr, code, run_init_subtune=None):
    mem = bytearray(65536)
    mem[load_addr:load_addr + len(code)] = code
    mem[0xFFF0] = 0x00  # BRK at $FFF0
    m = MPU()
    m.memory = bytearray(mem)
    if run_init_subtune is not None:
        m.stPush(0xFF); m.stPush(0xEF)
        m.pc = load_addr  # init = load_addr for Hawkeye
        m.a = run_init_subtune
        for _ in range(200000):
            if m.memory[m.pc] == 0x00:
                break
            m.step()
    return m


def dump_bytes(mem, base, count, per_row=16, label=None):
    if label:
        print(f'\n=== {label} ===')
    for r in range(0, count, per_row):
        row = mem[base + r:base + r + per_row]
        addr = base + r
        hex_str = ' '.join(f'{b:02X}' for b in row)
        ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in row)
        print(f'${addr:04X}: {hex_str:<{per_row*3-1}}  {ascii_str}')


def main():
    load_addr, init_addr, play_addr, n_songs, code = load_sid(SID_PATH)
    print(f'Hawkeye: load=${load_addr:04X} init=${init_addr:04X} '
          f'play=${play_addr:04X} songs={n_songs}')
    print(f'Code size: {len(code)} bytes (covers ${load_addr:04X}..'
          f'${load_addr + len(code) - 1:04X})')

    # Pre-init: data tables as stored in the binary (before init's
    # per-subtune overwrites at $8403).
    m = setup_mpu(load_addr, code, run_init_subtune=None)
    mem = m.memory

    # === Per-subtune tables (per RE_NOTES guesses) ===
    # $83FC = speedbyte per subtune (n_songs entries?)
    dump_bytes(mem, 0x83FC, 12, label='$83FC: per-subtune speedbyte (12 subs)')

    # $83F5 = something per subtune (per `BD F5 83` at $7B73)
    dump_bytes(mem, 0x83F5, 12, label='$83F5: per-subtune ??? (12 subs)')

    # $7AFF = something per subtune (per `BD FF 7A` at $7B79)
    dump_bytes(mem, 0x7AFF, 12, label='$7AFF: per-subtune ??? (12 subs)')

    # $7B2C = 6-byte template copied to $8403 in init
    dump_bytes(mem, 0x7B2C, 6, label='$7B2C: 6-byte template → $8403')

    # === Sequence pointer table ($8409) ===
    # Each entry: 2 bytes (lo, hi) addressing a pattern's byte stream
    print('\n=== $8409: pattern-pointer table (lo,hi pairs) ===')
    for i in range(40):  # show first 40 entries
        lo = mem[0x8409 + i*2]
        hi = mem[0x840A + i*2]
        addr = lo | (hi << 8)
        if addr < load_addr or addr > load_addr + len(code):
            # Stop when we see clearly-non-pattern addresses
            print(f'  pat {i:3d}: ${addr:04X}  (out of range, stopping)')
            break
        print(f'  pat {i:3d}: ${addr:04X}')

    # === Freq tables ===
    # $8337 (lo) and $8396 (hi), 95 entries each (per Cybernoid II)
    print('\n=== $8337: freq table lo (96 entries) ===')
    for r in range(0, 96, 16):
        row = mem[0x8337 + r:0x8337 + r + 16]
        print(f'  +{r:3d}: ' + ' '.join(f'{b:02X}' for b in row))

    print('\n=== $8396: freq table hi (96 entries) ===')
    for r in range(0, 96, 16):
        row = mem[0x8396 + r:0x8396 + r + 16]
        print(f'  +{r:3d}: ' + ' '.join(f'{b:02X}' for b in row))

    # Sanity: PAL middle-A (a-4 = note 33) should be ~$1C37
    a4_lo = mem[0x8337 + 33]
    a4_hi = mem[0x8396 + 33]
    print(f'\n  note 33 (a-4 PAL=0x1C37 expected): '
          f'${a4_hi:02X}{a4_lo:02X}')

    # === Instrument table ===
    # From L_7CD0: $8580 / $8589 are column tables (16 instruments?)
    dump_bytes(mem, 0x8580, 16, label='$8580: instrument col 1 (16?)')
    dump_bytes(mem, 0x8589, 16, label='$8589: instrument col 2 (16?)')

    # From L_7D60..L_7D7C: $860C..$8610,x are read indexed by ($DA,x)*8
    # — that means the per-instrument 8-byte record starts at $860C
    dump_bytes(mem, 0x860C, 64, label='$860C: per-instrument 8-byte records (8 insts?)')

    # === Sequence stream ($8FC5) ===
    # Per L_7BE3: `LDA $8FC5,y` reads sequence byte where y=tabcount,x
    # So $8FC5 is the BASE of the sequence stream area. Voice's start
    # offset = the lo/hi pair from $7B2C → $8403.
    dump_bytes(mem, 0x8403, 6, label='$8403: per-voice seq pointer (3 lo + 3 hi)')

    # The lo/hi pair at $8403/$8406 is for V0. Read the sequence stream.
    # Per the trace, V0's tabcount advanced 0→2 in frame 0, meaning V0
    # processed 2 sequence bytes that resolved to commands but not
    # pattern jumps yet (?), then a 3rd byte triggered the pattern jump.
    print('\n=== sequence stream start (per-voice) ===')
    for v in range(3):
        seq_lo = mem[0x8403 + v]
        seq_hi = mem[0x8406 + v]
        seq_addr = seq_lo | (seq_hi << 8)
        print(f'  V{v}: seq base = ${seq_addr:04X}')
        # Show first 16 bytes
        print(f'    ' + ' '.join(f'{mem[seq_addr + i]:02X}' for i in range(16)))

    # Now run init for subtune 0 and re-read these tables — the init
    # path copies per-subtune data INTO $8403..$8408.
    print('\n=== after init(subtune=0): $8403..$8408 ===')
    m2 = setup_mpu(load_addr, code, run_init_subtune=0)
    mem2 = m2.memory
    dump_bytes(mem2, 0x8403, 6, label='$8403 after init(sub=0)')
    print('\n=== sequence stream start AFTER init ===')
    for v in range(3):
        seq_lo = mem2[0x8403 + v]
        seq_hi = mem2[0x8406 + v]
        seq_addr = seq_lo | (seq_hi << 8)
        print(f'  V{v}: seq base = ${seq_addr:04X}')
        print(f'    ' + ' '.join(f'{mem2[seq_addr + i]:02X}' for i in range(16)))


if __name__ == '__main__':
    main()
