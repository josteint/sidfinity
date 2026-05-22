"""sfx.py — the Hubbard '85 sound-effect record format (shared core).

A Hubbard engine's sound effects are NOT instrument-plus-score — each
is a 2-voice SID register snapshot plus a freq-table pitch sweep,
stored as a 16-byte record. The format is shared across the engine
family (Commando, Monty, ...); only the table address and the freq-
table address differ per engine, so `extract_sfx` takes them as
arguments and each engine's pipeline wraps it.

16-byte SFX record:
  byte 0     flags  — rate (bits 0-3), direction (bits 4-5 == $20 -> up),
                      skip-V1-freq (bit 6), skip-both-freq (bit 7)
  bytes 1-7  V1 SID register block (freq_lo, freq_hi, pw_lo, pw_hi,
             ctrl, ad, sr) — written verbatim to $D400-$D406
  bytes 8-14 V2 SID register block -> $D407-$D40D
  byte 15    sweep end index

Hubbard aliases storage: byte 1 is both V1's freq_lo and the sweep
start index; byte 8 is both V2's freq_lo and the gate-flags / V2
freq-table offset. `decode_sfx` splits those into named fields.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))

NUM_SFX = 16

# SID register offsets within a voice (0..6)
R_FREQ_LO, R_FREQ_HI, R_CTRL = 0, 1, 4


@dataclass
class SoundEffect:
    """One sound effect as USF behavioral parameters."""
    index: int                       # 0..15
    v1: list[int] = field(default_factory=list)   # 7 SID regs (freq..sr)
    v2: list[int] = field(default_factory=list)   # 7 SID regs
    start_index: int = 0             # freq-table index the sweep starts at
    end_index: int = 0               # the sweep stops when index reaches this
    rate: int = 0                    # extra frames per step (step every rate+1)
    direction: str = 'down'          # 'down' or 'up'
    skip_v1: bool = False            # don't write V1 freq during the sweep
    skip_both: bool = False          # don't write either voice's freq
    v2_byte_offset: int = 0          # V2 reads freqtab at index*2 - this
    toggle_v1: bool = False          # retrigger V1's gate each step
    toggle_v2: bool = False          # retrigger V2's gate each step


def decode_sfx(index: int, d: list[int]) -> SoundEffect:
    """Decode one 16-byte SFX record."""
    flags = d[0]
    gate_byte = d[8]
    return SoundEffect(
        index=index,
        v1=list(d[1:8]),
        v2=list(d[8:15]),
        start_index=d[1],                       # aliased with v1[0]
        end_index=d[15],
        rate=flags & 0x0F,
        direction='up' if (flags & 0x30) == 0x20 else 'down',
        skip_v1=bool(flags & 0x40),
        skip_both=bool(flags & 0x80),
        v2_byte_offset=gate_byte & 0x3F,        # aliased with v2[0]
        toggle_v1=bool(gate_byte & 0x80),
        toggle_v2=bool(gate_byte & 0x40),
    )


def extract_sfx(sid_path: str, sfx_table: int, freq_table: int,
                num_sfx: int = NUM_SFX) -> tuple[list[SoundEffect], bytes]:
    """Decode all SFX records from `sfx_table` and return them with a
    generous window of raw freq-table bytes from `freq_table`."""
    from src.hubbard_emu import load_sid
    _, binary, load = load_sid(sid_path)

    def b(addr):
        return binary[addr - load]

    sfx = [decode_sfx(s, [b(sfx_table + s * 16 + i) for i in range(16)])
           for s in range(num_sfx)]
    # the sweep reads freqtab,Y for Y up to 255 — grab 320 bytes; past
    # entry 96 it runs into engine state (the off-table trick).
    freq_bytes = bytes(b(freq_table + i) for i in range(320))
    return sfx, freq_bytes
