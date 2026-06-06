#!/usr/bin/env python3
"""effect_chain_profiler.py — attribute each SID write to its CPU PC.

For each write to a target SID register (or all $D4xx), find the CPU
PC at the cycle of that write. Lets you answer "which routine wrote
this $D408 = $47?" in one command, without having to manually trace
through the engine code.

Internally runs `siddump --writelog --pc-trace` over a chosen frame
range, then matches each write's cycle to the corresponding PC trace
entry.

Usage:
    python3 tools/effect_chain_profiler.py SID --subtune N \\
        --frames START-END [--register HEX[,HEX,...]]

    # Examples:
    # Tag every $D408 write in Hawkeye sub 1 frames 145-152:
    python3 tools/effect_chain_profiler.py \\
        hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid \\
        --subtune 1 --frames 145-152 --register D408

    # Tag ALL writes in a frame range (omit --register):
    python3 tools/effect_chain_profiler.py SID --subtune 0 --frames 1-3

Output format:
    f<frame>  c<cycle>  $D4XX = $VV  PC=$YYYY  (instruction mnemonic)
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIDDUMP = ROOT / 'tools' / 'siddump'


_CYCLES_PER_FRAME_PAL = 63 * 312 + 32  # 19688


def _capture_writelog_and_pc(sid_path: str, subtune: int,
                              start_frame: int, end_frame: int
                              ) -> tuple[list[tuple], list[tuple[int, int]]]:
    """Run siddump capturing writelog + pc-trace for the frame range.

    Returns (writes, pc_samples):
      writes — list of (frame, abs_cycle, reg, val) tuples where
               abs_cycle is converted to the same cycle scheme as PC trace.
      pc_samples — sorted list of (abs_cycle, PC) tuples.
    """
    duration = (end_frame + 2) / 50.0
    with tempfile.NamedTemporaryFile(suffix='.pc', delete=False) as f:
        pc_path = f.name
    try:
        r = subprocess.run(
            [str(SIDDUMP), sid_path,
             '--subtune', str(subtune + 1),
             '--duration', str(duration),
             '--writelog', '--raw',
             '--pc-trace', pc_path,
             str(start_frame), str(end_frame)],
            capture_output=True, text=True)
        if r.returncode not in (0, 2):
            print(f'siddump error (rc={r.returncode}):\n{r.stderr}',
                  file=sys.stderr)
            return [], []
        # Parse pc-trace FIRST so we can determine the per-frame cycle base.
        # Format pair-of-lines:
        #   header: " PC  I  A  X  ...  Instruction (CYCLE)"
        #   data:   "PCPC f ..."
        pc_samples: list[tuple[int, int]] = []
        with open(pc_path) as f:
            current_cycle: int | None = None
            for tline in f:
                m_cycle = re.search(r'\((\d+)\)', tline)
                if m_cycle:
                    current_cycle = int(m_cycle.group(1))
                    continue
                m_pc = re.match(r'\s*([0-9a-fA-F]{4})\b', tline)
                if m_pc and current_cycle is not None:
                    try:
                        pc_samples.append(
                            (current_cycle, int(m_pc.group(1), 16)))
                    except ValueError:
                        pass
                    current_cycle = None
        pc_samples.sort()
        # First absolute cycle in pc-trace ≈ absolute cycle at the start of
        # `start_frame`. Compute per-frame base cycles for alignment.
        abs_at_start_frame = pc_samples[0][0] if pc_samples else 0

        # Parse writelog. The writelog cycle field is RELATIVE to each
        # siddump frame's play() invocation; convert to absolute and
        # filter to the pc-trace range so cycles match the PC samples.
        writes = []
        f_idx = -1
        for line in r.stdout.splitlines():
            stripped = line.strip()
            # Treat each output line as one frame, even if it has no |W:.
            if not stripped or stripped.startswith('{') or stripped.startswith('V1_'):
                # JSON header / column header — skip without counting as frame
                continue
            f_idx += 1
            if not (start_frame <= f_idx <= end_frame):
                continue
            if '|W:' not in line:
                continue
            _, w = line.split('|W:', 1)
            # Strip trailing |M / |P / |I sections so toks only has writes
            w_section = w.strip().split('|', 1)[0]
            toks = w_section.split(':')
            for i in range(0, len(toks) - 2, 3):
                try:
                    rel_cycle = int(toks[i])
                    reg = int(toks[i + 1], 16)
                    val = int(toks[i + 2], 16)
                    # Frame f_idx's start abs cycle = abs_at_start_frame
                    # + (f_idx - start_frame) * cycles_per_frame.
                    abs_cycle = (abs_at_start_frame
                                 + (f_idx - start_frame) * _CYCLES_PER_FRAME_PAL
                                 + rel_cycle)
                    writes.append((f_idx, abs_cycle, reg, val))
                except ValueError:
                    pass
        return writes, pc_samples
    finally:
        os.unlink(pc_path)


def _find_pc_for_cycle(pc_samples: list[tuple[int, int]],
                       abs_cycle: int) -> int | None:
    """Binary search for the latest PC trace entry at or before abs_cycle."""
    if not pc_samples:
        return None
    lo, hi = 0, len(pc_samples) - 1
    best = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if pc_samples[mid][0] <= abs_cycle:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    if best < 0:
        return None
    return pc_samples[best][1]


def _voice_role(reg: int) -> str:
    if 0x00 <= reg <= 0x14:
        v = reg // 7 + 1
        roles = ['freq lo', 'freq hi', 'PW lo', 'PW hi', 'ctrl', 'AD', 'SR']
        return f'V{v} {roles[reg % 7]}'
    return {
        0x15: 'filter cutoff lo',
        0x16: 'filter cutoff hi',
        0x17: 'filter res/route',
        0x18: 'vol/filter mode',
    }.get(reg, f'reg ${reg:02X}')


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('sid')
    p.add_argument('--subtune', type=int, default=0,
                   help='0-indexed (default 0)')
    p.add_argument('--frames', required=True,
                   help='Frame range START-END (e.g. 145-152)')
    p.add_argument('--register', default=None,
                   help='Filter to specific $D4xx register(s), '
                        'comma-separated hex (e.g. D408 or 02,03)')
    args = p.parse_args()
    if not os.path.exists(args.sid):
        print(f'sid not found: {args.sid}', file=sys.stderr); return 1
    if '-' not in args.frames:
        print('--frames must be START-END', file=sys.stderr); return 1
    sf_s, ef_s = args.frames.split('-')
    sf, ef = int(sf_s), int(ef_s)

    reg_filter: set[int] | None = None
    if args.register:
        reg_filter = set()
        for tok in args.register.split(','):
            tok = tok.strip()
            # Allow either D408 or just 08 — strip the leading $D4 if present
            v = int(tok, 16)
            if v >= 0xD400:
                v -= 0xD400
            reg_filter.add(v)

    writes, pc_samples = _capture_writelog_and_pc(args.sid, args.subtune,
                                                    sf, ef)
    if not writes:
        print(f'No writes captured. siddump stderr above may explain.',
              file=sys.stderr)
        return 1
    print(f'# {args.sid} subtune {args.subtune} frames {sf}-{ef}')
    print(f'# {len(writes)} write(s), {len(pc_samples)} PC samples')
    print()
    print(f'  frame  abs_cycle  register         val   PC')
    for f_idx, abs_cycle, reg, val in writes:
        if reg_filter is not None and reg not in reg_filter:
            continue
        pc = _find_pc_for_cycle(pc_samples, abs_cycle)
        pc_s = f'${pc:04X}' if pc is not None else '?????'
        print(f'  f{f_idx:<4}  c{abs_cycle:<10}  '
              f'$D4{reg:02X} {_voice_role(reg):<18}  ${val:02X}    {pc_s}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
