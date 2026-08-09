"""Dump per-subtune engine state + pattern bytes for C64 Music Examples.

For each Family A subtune (0, 2, 3, 4-14), runs init in py65 and
captures the post-init engine state + pattern data. Sub 1 (Family B)
gets a minimal entry (data shape TBD).

Output: pipelines/companion/c64_music_examples/_extracted/sub{N}.json

This is a starter intermediate format — NOT the final USF. Next
iteration will convert these JSON dumps into proper USF entries once
the schema is designed.
"""

from __future__ import annotations
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, 'tools/py65_lib')
from py65.devices.mpu6502 import MPU

from pipelines.companion.c64_music_examples.extract.engine_model import (
    FAMILY_A_INSTANCES, FamilyABindings,
)


SID_PATH = 'hvsc85/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid'


def run_init(subtune: int) -> bytearray:
    raw = Path(SID_PATH).read_bytes()
    body = raw[0x7C+2:]
    load = struct.unpack('<H', raw[0x7C:0x7C+2])[0]
    mpu = MPU()
    mpu.memory = bytearray(0x10000)
    mpu.memory[load:load+len(body)] = body
    mpu.a = subtune; mpu.x = 0; mpu.y = 0; mpu.p = 0x20; mpu.sp = 0xFD
    mpu.memory[0x01FF] = 0xFE; mpu.memory[0x01FE] = 0xFE
    mpu.pc = 0x087C
    for _ in range(200000):
        if mpu.pc == 0xFEFF:
            break
        mpu.step()
    return mpu.memory


def walk_pattern(mem: bytearray, start_addr: int, max_bytes: int = 2000
                 ) -> list[int]:
    """Walk pattern bytes until $8E (loop) or $0F (end), inclusive."""
    out = []
    addr = start_addr
    for _ in range(max_bytes):
        b = mem[addr]
        out.append(b)
        addr = (addr + 1) & 0xFFFF
        if b in (0x0F, 0x8E):
            break
    return out


def freq_tables(mem: bytearray) -> dict:
    """Family A freq tables — at $0B5F (one ref) / $0BDF (other ref).
    The note-play path stores $0B5F[note] to $D401+X (= freq HI per
    SID layout) and $0BDF[note] to $D400+X (= freq LO). Despite the
    label, $0B5F = freq HI table, $0BDF = freq LO table."""
    return {
        'hi_addr': 0x0B5F,
        'lo_addr': 0x0BDF,
        'hi': list(mem[0x0B5F:0x0B5F + 128]),
        'lo': list(mem[0x0BDF:0x0BDF + 128]),
    }


def extract_family_a_subtune(subtune: int) -> dict:
    """Extract one Family A subtune's per-instance state + pattern data."""
    b = FAMILY_A_INSTANCES.get(subtune) or FAMILY_A_INSTANCES['shared']
    mem = run_init(subtune)
    sb = b.state_base
    state32 = list(mem[sb:sb + 32])
    # Pattern pointers from zp (initialized by engine init from state +24..+29)
    v1_ptr = mem[0x1C] | (mem[0x1D] << 8)
    v2_ptr = mem[0x1E] | (mem[0x1F] << 8)
    v3_ptr = mem[0x20] | (mem[0x21] << 8)
    return {
        'subtune': subtune,
        'family': 'A',
        'shared_handler': subtune >= 4,
        'handler_addr': f'${b.handler_addr:04X}',
        'state_base': f'${b.state_base:04X}',
        'pwm_sign_base': f'${b.pwm_sign_base:04X}',
        'current_note_addr': f'${b.current_note_addr:04X}',
        'state_32_bytes': [f'${x:02X}' for x in state32],
        'tempo': state32[21],
        'alt_tempo': state32[22],
        'frame_ctr_init': state32[23],
        'v1_pw_init': state32[3],
        'v3_pw_init': state32[17],
        'v3_pwm_ctr_init': state32[30],
        'v1_pwm_ctr_init': state32[31],
        'v1_pattern_ptr': f'${v1_ptr:04X}',
        'v2_pattern_ptr': f'${v2_ptr:04X}',
        'v3_pattern_ptr': f'${v3_ptr:04X}',
        'v1_pattern_bytes': [f'${x:02X}' for x in walk_pattern(mem, v1_ptr)],
        'v2_pattern_bytes': [f'${x:02X}' for x in walk_pattern(mem, v2_ptr)],
        'v3_pattern_bytes': [f'${x:02X}' for x in walk_pattern(mem, v3_ptr)],
        'current_note_init': mem[b.current_note_addr],
    }


def extract_family_b_subtune() -> dict:
    """Sub 1 — Family B engine at $1119. Different opcodes; full RE
    pending. Just dump the handler bytes for now."""
    mem = run_init(1)
    handler_bytes = list(mem[0x1119:0x1119 + 200])
    return {
        'subtune': 1,
        'family': 'B',
        'handler_addr': '$1119',
        'note': 'Pattern-jump engine, distinct from Family A. Full RE pending.',
        'handler_bytes': [f'${x:02X}' for x in handler_bytes],
    }


def main():
    out_dir = Path('pipelines/companion/c64_music_examples/_extracted')
    out_dir.mkdir(exist_ok=True)

    # Shared freq tables — write once for the whole engine family
    mem0 = run_init(0)
    with open(out_dir / 'family_a_freq_tables.json', 'w') as f:
        ft = freq_tables(mem0)
        json.dump({k: ([f'${x:02X}' for x in v] if isinstance(v, list) else v)
                   for k, v in ft.items()}, f, indent=2)

    for st in range(15):
        if st == 1:
            data = extract_family_b_subtune()
        else:
            data = extract_family_a_subtune(st)
        path = out_dir / f'sub{st:02d}.json'
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        v1n = len(data.get('v1_pattern_bytes', []))
        v2n = len(data.get('v2_pattern_bytes', []))
        v3n = len(data.get('v3_pattern_bytes', []))
        if data['family'] == 'A':
            print(f"  sub {st:2d} ({data['family']}): handler {data['handler_addr']} "
                  f"tempo={data['tempo']:2d} alt={data['alt_tempo']:2d} "
                  f"V1={v1n:4d} V2={v2n:4d} V3={v3n:4d} bytes")
        else:
            print(f"  sub {st:2d} ({data['family']}): handler {data['handler_addr']}")


if __name__ == '__main__':
    main()
