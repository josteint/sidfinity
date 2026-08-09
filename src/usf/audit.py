"""PC-traced SID-write audit for engine reverse-engineering.

The procedure-of-record for resolving Rule 1 collapse questions (does
effect X in engine A produce the same writes as effect Y in engine
B?). Plain writelog comparison conflates V1/V2/V3 writes on the same
$D400-$D418 range; the audit needs PC-attribution to identify which
engine code wrote each byte.

`audit_writes` runs the SID's init+play through py65 with a memory
write observer that captures `(frame, pc, addr, value)` for every SID
write. The CLI prints the trace as a table, optionally cross-
referenced against a disassembly file for label attribution.

Usage:

  python -m src.usf.audit hvsc85/MUSICIANS/H/Hubbard_Rob/Human_Race.sid \\
      --subtune 1 --frames 225:235 --voice 0 \\
      --disasm pipelines/hubbard/human_race/disassembly.s
"""

from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass
from typing import Optional

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from py65.devices.mpu6502 import MPU            # noqa: E402
from py65.memory import ObservableMemory         # noqa: E402

VOICE_RANGES = [(0xD400, 0xD406), (0xD407, 0xD40D), (0xD40E, 0xD414)]
REG_NAMES = ('freq_lo', 'freq_hi', 'pw_lo', 'pw_hi', 'ctrl', 'ad', 'sr')


@dataclass
class Write:
    """One SID register write captured by the audit."""
    frame: int
    pc: int
    addr: int
    value: int

    @property
    def voice(self) -> Optional[int]:
        """Which voice (0/1/2) this register belongs to, or None if it's
        outside the per-voice range (e.g. $D418 master vol, $D415 filter)."""
        for v, (lo, hi) in enumerate(VOICE_RANGES):
            if lo <= self.addr <= hi:
                return v
        return None

    @property
    def reg_name(self) -> str:
        v = self.voice
        if v is None:
            return f'${self.addr:04X}'
        return f'V{v + 1}.{REG_NAMES[self.addr - VOICE_RANGES[v][0]]}'


def _load_sid(sid_path: str) -> tuple[int, int, int, bytes]:
    """Return (load_addr, init_addr, play_addr, body_bytes)."""
    data = open(sid_path, 'rb').read()
    hdr_len = int.from_bytes(data[6:8], 'big')
    load = int.from_bytes(data[8:10], 'big')
    init = int.from_bytes(data[10:12], 'big')
    play = int.from_bytes(data[12:14], 'big')
    if load == 0:
        load = int.from_bytes(data[hdr_len:hdr_len + 2], 'little')
        body = data[hdr_len + 2:]
    else:
        body = data[hdr_len:]
    return load, init, play, body


def audit_writes(sid_path: str, subtune: int, frame_start: int,
                 frame_end: int, voice: Optional[int] = None) -> list[Write]:
    """Run the SID through py65 and capture SID register writes for the
    requested frame range. `voice` filters to one voice (0/1/2) or None
    for all.

    Frame indices are 0-based, matching the convention of
    `inst_program.capture` and `verify_cycle.writelog_capture` after
    its +1 fix. `frame_end` is exclusive.

    Subtune is 0-indexed (PSID convention).
    """
    load, init, play, body = _load_sid(sid_path)
    mem = ObservableMemory()
    for i, b in enumerate(body):
        mem[load + i] = b
    # Stub the KERNAL IRQ exit as RTS so RSID-style players can call
    # `jmp $EA31` and return cleanly.
    mem[0xEA31] = 0x60

    mpu = MPU()
    mpu.memory = mem

    captured: list[Write] = []
    current_frame = [0]   # nonlocal-ish via list

    def observer(address, value):
        if 0xD400 <= address <= 0xD418:
            captured.append(Write(frame=current_frame[0], pc=mpu.pc,
                                  addr=address, value=value))

    mem.subscribe_to_write(range(0xD400, 0xD419), observer)

    def call(entry: int, a: int = 0) -> None:
        """Run from `entry` until the routine returns to the stack-pushed
        $F000-1 sentinel (or hits a BRK byte / runaway). Captures any SID
        writes that happen via the registered observer."""
        mpu.a = a
        mpu.pc = entry
        mem[0x01FF] = 0xF0
        mem[0x01FE] = 0xFF
        mpu.sp = 0xFD
        cycles = 0
        while mpu.pc != 0xF000 and mem[mpu.pc] != 0x00:
            mpu.step()
            cycles += 1
            if cycles > 200_000:
                raise RuntimeError(
                    f'audit_writes: routine at ${entry:04X} did not return '
                    f'(stuck at ${mpu.pc:04X} after {cycles} cycles)')

    # init runs once; A = subtune (engine-specific convention, but
    # 0-indexed for all migrated Hubbard '85 engines).
    call(init, a=subtune)
    captured.clear()   # drop init-time writes; the audit is per-frame play()

    # Advance to frame_start, discarding captures.
    for f in range(frame_start):
        current_frame[0] = f
        captured_len_before = len(captured)
        call(play)
        # Discard pre-window captures
        del captured[captured_len_before:]

    # Capture from frame_start (inclusive) to frame_end (exclusive).
    for f in range(frame_start, frame_end):
        current_frame[0] = f
        call(play)

    if voice is not None:
        captured = [w for w in captured if w.voice == voice]
    return captured


# ---------------------------------------------------------------------------
# Disassembly cross-reference — parse a .s file for `L_xxxx` / `$xxxx:`
# labels so we can attribute writes to engine code.
# ---------------------------------------------------------------------------

_LABEL_LINE = re.compile(
    r'^\s*\$([0-9A-Fa-f]{4}):\s+[0-9A-Fa-f ]+\s+(\w+)')
_NAMED_LABEL = re.compile(r'^(L_[0-9A-Fa-f]+):')


def load_disasm_labels(disasm_path: str) -> list[tuple[int, str]]:
    """Parse a disassembly file for `$xxxx:` lines, returning a sorted
    list of (pc, line_summary). Used to attribute a PC to the nearest
    labeled instruction below it."""
    labels: list[tuple[int, str]] = []
    if not os.path.isfile(disasm_path):
        return labels
    with open(disasm_path) as f:
        for line in f:
            m = _LABEL_LINE.match(line)
            if m:
                pc = int(m.group(1), 16)
                # Strip the address prefix to get the disassembled mnemonic
                # + operands + comment.
                rest = line[line.index(':') + 1:].strip()
                labels.append((pc, rest))
    labels.sort()
    return labels


def label_for_pc(labels: list[tuple[int, str]],
                 pc: int) -> Optional[str]:
    """Return the disassembly line for `pc`, or the nearest line below it."""
    # Binary search would be faster but the lists are small.
    best = None
    for entry_pc, line in labels:
        if entry_pc > pc:
            break
        best = (entry_pc, line)
    if best is None:
        return None
    entry_pc, line = best
    if entry_pc == pc:
        return line
    return f'(near ${entry_pc:04X}) {line}'


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> None:
    import argparse
    p = argparse.ArgumentParser(
        description='PC-traced SID-write audit for engine reverse-engineering.')
    p.add_argument('sid_path',
                   help='Path to the SID file (PSID or RSID).')
    p.add_argument('--subtune', type=int, default=0,
                   help='Subtune index, 0-based (default 0).')
    p.add_argument('--frames', default='0:10',
                   help='Frame range "start:end" (end exclusive). '
                        'Default 0:10.')
    p.add_argument('--voice', type=int, choices=(0, 1, 2), default=None,
                   help='Filter to one voice (0=V1, 1=V2, 2=V3). '
                        'Default: all voices.')
    p.add_argument('--disasm', default=None,
                   help='Disassembly .s file for PC label attribution.')
    args = p.parse_args(argv)

    frame_start, frame_end = (int(x) for x in args.frames.split(':'))
    labels = (load_disasm_labels(args.disasm)
              if args.disasm is not None else [])

    writes = audit_writes(args.sid_path, args.subtune,
                          frame_start, frame_end,
                          voice=args.voice)

    # Print as a table grouped by frame.
    print(f'SID: {args.sid_path}')
    print(f'Subtune {args.subtune}, frames {frame_start}..{frame_end - 1}'
          + (f' (voice V{args.voice + 1} only)' if args.voice is not None
             else ''))
    print(f'{len(writes)} writes captured.\n')

    label_w = 60 if labels else 0
    header = f'{"frame":>5} {"PC":>6} {"reg":<14} {"val":>4}'
    if labels:
        header += f'  {"disasm":<{label_w}}'
    print(header)
    print('-' * len(header))
    last_frame = None
    for w in writes:
        if last_frame is not None and w.frame != last_frame:
            print()
        line = f'{w.frame:>5} ${w.pc:04X} {w.reg_name:<14} ${w.value:02X}'
        if labels:
            lab = label_for_pc(labels, w.pc) or ''
            line += f'  {lab[:label_w]}'
        print(line)
        last_frame = w.frame


if __name__ == '__main__':
    main(sys.argv[1:])
