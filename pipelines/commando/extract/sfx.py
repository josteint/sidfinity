"""sfx.py — Commando sound-effect extraction + reference interpreter.

Commando has 19 PSID subtunes: 0/1/2 are music, 3-18 are sound effects.
A SFX is driven by the `$53A5` sub-engine (which the music subtunes
leave gated off). It is NOT instrument-plus-score — it is a 2-voice
SID register snapshot plus a freq-table pitch sweep.

The 16 SFX records live at `$55F9`, 16 bytes each:
  byte 0     flags  — rate (bits 0-3), direction (bits 4-5 == $20 -> up),
                      skip-V1-freq (bit 6), skip-both-freq (bit 7)
  bytes 1-7  V1 SID register block (freq_lo, freq_hi, pw_lo, pw_hi,
             ctrl, ad, sr) — written verbatim to $D400-$D406
  bytes 8-14 V2 SID register block -> $D407-$D40D
  byte 15    sweep end index

Hubbard aliases storage: byte 1 is both V1's freq_lo and the sweep
start index; byte 8 is both V2's freq_lo and the gate-flags/V2-offset.
This module splits those back into separate named fields.

The engine each frame: decrement a step counter; when it expires,
advance an index from start towards end through the freq table
(`$5428`), writing V1 freq from freqtab[index*2] and V2 freq from
freqtab[index*2 - v2_byte_offset]; optionally toggle the V1/V2 gate.
When the index reaches `end` it gates V1/V2 off — the SFX is done.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

SFX_TABLE = 0x55F9      # 16 SFX x 16 bytes
FREQ_TABLE = 0x5428     # the shared note-frequency table
NUM_SFX = 16

# SID register offsets within a voice (0..6)
R_FREQ_LO, R_FREQ_HI, R_CTRL = 0, 1, 4


@dataclass
class SoundEffect:
    """One Commando sound effect as USF behavioral parameters."""
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


def extract_sfx(sid_path: str) -> tuple[list[SoundEffect], bytes]:
    """Decode all 16 SFX and return them with the raw freq-table bytes."""
    from src.hubbard_emu import load_sid
    _, binary, load = load_sid(sid_path)

    def b(addr):
        return binary[addr - load]

    sfx = []
    for s in range(NUM_SFX):
        base = SFX_TABLE + s * 16
        sfx.append(decode_sfx(s, [b(base + i) for i in range(16)]))
    # the SFX engine reads $5428,Y (and $5429,Y for freq_hi); Y is a
    # byte 0..255, so reads span $5428..$5528. Grab a generous window —
    # past entry 96 it runs into engine state (the off-table trick).
    freq_bytes = bytes(b(FREQ_TABLE + i) for i in range(320))
    return sfx, freq_bytes


# ----------------------------------------------------------------------
# reference interpreter
# ----------------------------------------------------------------------

class SfxInterp:
    """Reproduces one SFX subtune's per-frame SID register writes —
    a faithful model of the $5038 play path + the $53A5 engine."""

    def __init__(self, sfx: SoundEffect, freq_bytes: bytes):
        self.sfx = sfx
        self.ftab = freq_bytes
        self.index = sfx.start_index
        self.step_ctr = 0                # $552A — fires immediately
        self.v1_gate = sfx.v1[R_CTRL]    # $552E — live V1 ctrl
        self.v2_gate = sfx.v2[R_CTRL]    # $552F — live V2 ctrl
        self.done = False
        self.frame_no = -1

    def _ftab(self, off: int) -> int:
        """The freq-table byte at $5428+off. Past the musical entries
        the sweep overflows into live engine state — Hubbard's trick,
        same as the music's off-table reads. The three live bytes a
        sweep can land on are reproduced here."""
        addr = 0x5428 + off
        if addr == 0x5519:          # mode byte — $5038 forces it $80
            return 0x80
        if addr == 0x5525:          # the play() frame counter (INC'd once
            return (self.ftab[253] + self.frame_no + 1) & 0xFF   # per call)
        if addr == 0x5527:          # SFX state — the index during a sweep
            return self.sfx.index & 0xFF
        if addr == 0x5528:          # drum_enable — $53A5 forces it $FF
            return 0xFF
        return self.ftab[off]

    def step(self) -> list[tuple[int, int]]:
        """One play() call -> this frame's (reg 0..20, val) writes."""
        self.frame_no += 1
        w: list[tuple[int, int]] = []

        if self.frame_no == 0:
            # $5038 — the SFX play path gates all three voices off once
            w += [(0 * 7 + R_CTRL, 0), (1 * 7 + R_CTRL, 0),
                  (2 * 7 + R_CTRL, 0)]
            # $5531 trigger — gate V1/V2 off, then the 14-byte block
            w += [(0 * 7 + R_CTRL, 0), (1 * 7 + R_CTRL, 0)]
            for r in range(7):
                w.append((0 * 7 + r, self.sfx.v1[r]))
            for r in range(7):
                w.append((1 * 7 + r, self.sfx.v2[r]))

        if self.done:
            return w

        # $53BA — step counter; a step fires when it goes negative
        self.step_ctr -= 1
        if self.step_ctr >= 0:
            return w
        self.step_ctr = self.sfx.rate
        return w + self._sweep_step()

    def _sweep_step(self) -> list[tuple[int, int]]:
        sfx = self.sfx
        # $53C7 — index reached the end: gate V1/V2 off, SFX over
        if self.index == sfx.end_index:
            self.done = True
            return [(0 * 7 + R_CTRL, 0), (1 * 7 + R_CTRL, 0)]

        w: list[tuple[int, int]] = []
        y = (self.index * 2) & 0xFF
        if not sfx.skip_both:
            if not sfx.skip_v1:
                # freq_lo at $5428,Y; freq_hi at $5429,Y — the +1 is a
                # 16-bit address step, it does NOT wrap at the page.
                w.append((0 * 7 + R_FREQ_LO, self._ftab(y)))
                w.append((0 * 7 + R_FREQ_HI, self._ftab(y + 1)))
            yv2 = (y - sfx.v2_byte_offset) & 0xFF
            w.append((1 * 7 + R_FREQ_LO, self._ftab(yv2)))
            w.append((1 * 7 + R_FREQ_HI, self._ftab(yv2 + 1)))
        if sfx.toggle_v1:
            self.v1_gate ^= 0x01
            w.append((0 * 7 + R_CTRL, self.v1_gate))
        if sfx.toggle_v2:
            self.v2_gate ^= 0x01
            w.append((1 * 7 + R_CTRL, self.v2_gate))

        # $53DE — advance the index (self-modified DEC/INC)
        if sfx.direction == 'up':
            self.index = (self.index + 1) & 0xFF
        else:
            self.index = (self.index - 1) & 0xFF
        return w


# ----------------------------------------------------------------------
# verification
# ----------------------------------------------------------------------

def verify(sid_path: str, n_frames: int = 200) -> None:
    """Run all 16 SFX through the interpreter, diff vs the py65 capture."""
    from pipelines.hubbard.inst_program import capture, REG_NAMES

    sfx, freq_bytes = extract_sfx(sid_path)
    all_ok = True
    for s in range(NUM_SFX):
        subtune = s + 3                       # PSID subtune = SFX index + 3
        cap = capture(sid_path, n_frames=n_frames, subtune=subtune)
        si = SfxInterp(sfx[s], freq_bytes)
        match = 0
        first = None
        for k in range(n_frames):
            got = si.step()
            want = cap.raw_frames[k]
            if got == want:
                match += 1
            elif first is None:
                first = (k, want, got)
        pct = 100.0 * match / n_frames
        status = 'OK ' if match == n_frames else 'FAIL'
        print(f'  SFX {s:2d} (subtune {subtune:2d}): {status} '
              f'{match}/{n_frames} = {pct:.1f}%')
        if first:
            all_ok = False
            k, want, got = first

            def fmt(fw):
                return ' '.join(
                    f'{["V1","V2","V3"][o // 7]}.{REG_NAMES[o % 7]}={v:02X}'
                    for o, v in fw) or '-'
            print(f'      first diff f{k}:  orig: {fmt(want)}')
            print(f'                       interp: {fmt(got)}')
    print('  ALL 16 SFX byte-exact' if all_ok else '  *** mismatches above')


def main(argv: list[str]) -> None:
    from pipelines.hubbard.inst_program import SID_PATH
    verify(SID_PATH, int(argv[0]) if argv else 200)


if __name__ == '__main__':
    main(sys.argv[1:])
