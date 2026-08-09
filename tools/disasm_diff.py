#!/usr/bin/env python3
"""disasm_diff.py — side-by-side compare an orig disasm region against
the composer emitter.

When a writelog divergence points to a specific effect, the recipe
(feedback_writelog_divergence_recipe) says "diff orig's effect code
against the composer emitter line by line." This tool does that
mechanically: given (orig.sid, addr range, composer file, function/
label), emits two columns side-by-side with diff markers.

Usage:
    python3 tools/disasm_diff.py --orig SID --orig-range HEX-HEX \\
                                  --composer FILE [--composer-label LABEL]

Examples:
    # Compare orig pulse_run at $ACE4-$AD30 against composer's
    # _emit_fx_pulse_run function:
    python3 tools/disasm_diff.py \\
        --orig hvsc85/MUSICIANS/T/Tel_Jeroen/Cybernoid_II.sid \\
        --orig-range ACE4-AD30 \\
        --composer pipelines/future_composer/composer_asm.py \\
        --composer-label fx_pulse_run

Output: two columns. Left = orig disassembly. Right = composer source
lines tagged with the label. Each line of orig is matched to its
likely composer counterpart (instruction mnemonic). NOT semantic —
this is a *visual aid* for spotting structural differences. Read
both columns yourself and ignore the auto-pairing.
"""
from __future__ import annotations

import argparse
import os
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _load_sid_image(path: str) -> tuple[int, bytes]:
    with open(path, 'rb') as f:
        d = f.read()
    data_off = struct.unpack('>H', d[6:8])[0]
    psid_load = struct.unpack('>H', d[8:10])[0]
    if psid_load == 0:
        load = struct.unpack('<H', d[data_off:data_off+2])[0]
        body = d[data_off+2:]
    else:
        load = psid_load
        body = d[data_off:]
    mem = bytearray(0x10000)
    mem[load:load + len(body)] = body
    return load, bytes(mem)


def _disassemble_range(mem: bytes, start: int, end: int) -> list[str]:
    """Disassemble mem[start:end] using py65."""
    sys.path.insert(0, str(ROOT / 'tools/py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.disassembler import Disassembler
    mpu = MPU()
    mpu.memory = bytearray(mem)
    da = Disassembler(mpu)
    lines = []
    addr = start
    while addr < end:
        length, line = da.instruction_at(addr)
        lines.append(f'${addr:04X}:  {line}')
        addr += length
    return lines


def _composer_lines(composer_file: str, label: str | None) -> list[str]:
    """Extract lines from composer file, optionally narrowed to a label.

    For `_emit_*` functions in the composer (which return asm strings),
    pull out just the asm string content from the triple-quoted return
    so we can diff actual asm against orig disasm, not the Python
    wrapper.
    """
    with open(composer_file) as f:
        full_text = f.read()
    lines = full_text.split('\n')
    if not label:
        return lines

    # If it's an _emit_* function, extract the triple-quoted return
    # string(s) and use those lines.
    if label.startswith('_emit_') or label.startswith('def '):
        fn_name = label.removeprefix('def ').strip().rstrip(':')
        # Match `def fn_name(...)` body up to the next top-level `def`
        m = re.search(
            r'(?:^|\n)def\s+' + re.escape(fn_name) + r'\b'
            r'(.*?)(?=\n(?:def|\Z))',
            full_text, re.DOTALL)
        if m:
            body = m.group(1)
            # Pull out triple-quoted strings (the asm bodies)
            asm_chunks = re.findall(r'"""(.*?)"""', body, re.DOTALL)
            if asm_chunks:
                return [ln for chunk in asm_chunks
                        for ln in chunk.split('\n')]

    # Fallback: find an asm label line (e.g., `fx_pulse_run:`) and pull
    # until the next top-level label.
    out = []
    in_label = False
    label_re = re.compile(r'^\s*' + re.escape(label) + r':\s*$')
    next_label_re = re.compile(r'^\s*[a-z_][a-z0-9_]*:\s*$')
    for line in lines:
        if not in_label:
            if label_re.match(line):
                in_label = True
                out.append(line)
        else:
            stripped = line.strip()
            if (next_label_re.match(line) and stripped != f'{label}:'
                and not stripped.startswith('#')):
                break
            out.append(line)
    return out


def _mnemonic(line: str) -> str:
    """Extract a normalized mnemonic from an asm line for pairing."""
    line = line.strip()
    # Strip comment
    if ';' in line:
        line = line.split(';', 1)[0].strip()
    # Strip label
    if ':' in line and ' ' not in line.split(':', 1)[0]:
        line = line.split(':', 1)[1].strip()
    # Take first 3 letters (mnemonic)
    tok = line.split(None, 1)
    if not tok:
        return ''
    return tok[0].upper()


def _format_side_by_side(left: list[str], right: list[str],
                         width: int = 80) -> str:
    out = []
    n = max(len(left), len(right))
    for i in range(n):
        l = left[i] if i < len(left) else ''
        r = right[i] if i < len(right) else ''
        l_truncated = l[:width].ljust(width)
        # mark possible mismatches
        m_l = _mnemonic(l)
        m_r = _mnemonic(r)
        marker = ' |' if m_l == m_r and m_l else '<>'
        out.append(f'{l_truncated} {marker} {r}')
    return '\n'.join(out)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--orig', required=True, help='Path to orig .sid file')
    p.add_argument('--orig-range', required=True,
                   help='Address range HEX-HEX (e.g. ACE4-AD30)')
    p.add_argument('--composer', required=True,
                   help='Composer file (typically pipelines/future_composer/composer_asm.py)')
    p.add_argument('--composer-label', default=None,
                   help='Narrow composer to a specific label/function')
    p.add_argument('--width', type=int, default=60,
                   help='Column width (default 60)')
    args = p.parse_args()
    if not os.path.exists(args.orig):
        print(f'orig not found: {args.orig}', file=sys.stderr); return 1
    if not os.path.exists(args.composer):
        print(f'composer not found: {args.composer}', file=sys.stderr); return 1
    if '-' not in args.orig_range:
        print('--orig-range must be HEX-HEX', file=sys.stderr); return 1
    start_s, end_s = args.orig_range.split('-')
    start, end = int(start_s, 16), int(end_s, 16)
    _, mem = _load_sid_image(args.orig)
    orig_lines = _disassemble_range(mem, start, end)
    composer_lines = _composer_lines(args.composer, args.composer_label)
    print(f'# orig: {args.orig} ${start:04X}-${end:04X}')
    print(f'# composer: {args.composer}'
          + (f' :: {args.composer_label}' if args.composer_label else ''))
    print(f"# Marker ' |' = mnemonic match. '<>' = mismatch or padding.")
    print()
    print(_format_side_by_side(orig_lines, composer_lines, args.width))
    return 0


if __name__ == '__main__':
    sys.exit(main())
