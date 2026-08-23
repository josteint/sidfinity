#!/usr/bin/env python3
"""pattern_stream_decode.py — decode FC family pattern stream bytes as
a human-readable command list.

FC engines (Future Composer / Hubbard '85) interpret pattern bytes as:
  $00-$3F  NOTE                  (pitch index into freq table)
  $40-$5F  cmd $40-$5F           (repeat counter / per-engine semantics)
  $60-$7F  cmd $60-$7F           (voice-inc / arp select)
  $70-$7F  cmd $70-$7F           (arp select on some engines)
  $80-$BF  setlength             (note duration extension, low 6 bits)
  $C0-$DF  wave/inst adjust      (set wavecount)
  $E0-$EF  glide                 (3-byte: $Ex delay target)
  $F0      noglide marker        (next byte = note without glide)
  $F1      filterset             (next byte → $D417)
  $FE      end of song           (terminate playback)
  $FF      end of pattern        (advance to next seq step)

The seq stream uses the same byte ranges but with different
interpretation:
  $00-$3F  pattern jump          (look up pattern_ptr_table[byte*2])
  $40-$7F  cmd                   (repeatsto / voiceinc)
  $80-$FF  cmd                   (toneadd / transpose)
  $FE      end of song
  $FF      loop to start

Usage:
    python3 pipelines/future_composer/pattern_stream_decode.py SID --addr HEX [--max-bytes N]

    # FC family canned: decode V<voice>'s seq+pattern for a subtune
    python3 pipelines/future_composer/pattern_stream_decode.py SID --engine fc \
        --subtune N --voice {1|2|3} [--frame F]

Outputs a side-by-side: hex bytes + decoded command + offset position
within the pattern.
"""
from __future__ import annotations

import argparse
import os
import struct
import sys


def _decode_pattern(bytes_seq: list[int], start_offset: int = 0,
                    label: str = '') -> str:
    """Decode a sequence of pattern bytes as FC pattern commands.
    Stops at $FF (end of pattern) or end of input."""
    lines = []
    if label:
        lines.append(f'# {label}')
    i = 0
    while i < len(bytes_seq):
        b = bytes_seq[i]
        off = start_offset + i
        desc = _classify(b)
        # Multi-byte commands consume extra bytes
        if 0xE0 <= b <= 0xEF:
            # glide: 3 bytes total ($Ex + delay + target)
            extra = bytes_seq[i+1:i+3] if i + 2 < len(bytes_seq) else []
            extra_s = ' '.join(f'{x:02X}' for x in extra)
            target = bytes_seq[i+2] if i + 2 < len(bytes_seq) else None
            tgt_s = f', target=${target:02X}' if target is not None else ''
            lines.append(f'  +${off:02X}:  {b:02X} {extra_s:6s}  '
                          f'GLIDE delay=${bytes_seq[i+1]:02X}{tgt_s}'
                          if i + 2 < len(bytes_seq) else
                          f'  +${off:02X}:  {b:02X}        GLIDE (truncated)')
            i += 3
            continue
        if b == 0xF0 and i + 1 < len(bytes_seq):
            note = bytes_seq[i + 1]
            lines.append(f'  +${off:02X}:  {b:02X} {note:02X}     '
                          f'NOGLIDE note=${note:02X}')
            i += 2
            continue
        if b == 0xF1 and i + 1 < len(bytes_seq):
            val = bytes_seq[i + 1]
            lines.append(f'  +${off:02X}:  {b:02X} {val:02X}     '
                          f'FILTERSET $D417=${val:02X}')
            i += 2
            continue
        lines.append(f'  +${off:02X}:  {b:02X}        {desc}')
        if b == 0xFF or b == 0xFE:
            break
        i += 1
    return '\n'.join(lines)


def _classify(b: int) -> str:
    if 0x00 <= b <= 0x3F:
        return f'NOTE (pitch idx ${b:02X})'
    if 0x40 <= b <= 0x5F:
        return f'cmd_40-5F (val=${b & 0x3F:02X})'
    if 0x60 <= b <= 0x6F:
        return f'cmd_60-6F (val=${b & 0x0F:02X})'
    if 0x70 <= b <= 0x7F:
        return f'ARP-select (idx ${b & 0x0F:02X})'
    if 0x80 <= b <= 0xBF:
        return f'SETLENGTH (+${b & 0x3F:02X} frames)'
    if 0xC0 <= b <= 0xDF:
        return f'WAVE/INST (idx ${b & 0x1F:02X})'
    if 0xE0 <= b <= 0xEF:
        return 'GLIDE (start)'
    if b == 0xF0:
        return 'NOGLIDE marker'
    if b == 0xF1:
        return 'FILTERSET'
    if b == 0xFE:
        return 'END OF SONG'
    if b == 0xFF:
        return 'END OF PATTERN'
    return f'unknown ${b:02X}'


def _decode_seq(bytes_seq: list[int], start_offset: int = 0) -> str:
    """Decode a sequence (song-level) stream — note that pattern jumps
    are $00-$3F, and the ranges above $3F are seq-specific commands."""
    lines = ['# seq stream:']
    i = 0
    while i < len(bytes_seq):
        b = bytes_seq[i]
        off = start_offset + i
        if 0x00 <= b <= 0x3F:
            desc = f'PATTERN-JUMP id=${b:02X} (ptr_table[${b:02X}*2])'
        elif 0x40 <= b <= 0x5F:
            desc = f'REPEAT-cmd (val=${b & 0x3F:02X})'
        elif 0x60 <= b <= 0x7F:
            desc = f'VOICEINC-cmd (val=${b & 0x0F:02X})'
        elif 0x80 <= b <= 0xFF:
            desc = f'TONEADD-cmd (val=${b & 0x1F:02X})'
        if b == 0xFE:
            desc = 'END OF SONG'
        elif b == 0xFF:
            desc = 'LOOP TO START'
        lines.append(f'  +${off:02X}:  {b:02X}        {desc}')
        if b in (0xFE, 0xFF):
            break
        i += 1
    return '\n'.join(lines)


def _load_sid_image(path: str) -> tuple[int, bytes]:
    """Load a PSID file and return (load_addr, full_memory_bytes)."""
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


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('sid')
    p.add_argument('--addr', help='Hex address of pattern stream start (e.g. 9015)')
    p.add_argument('--max-bytes', type=int, default=80,
                   help='Maximum bytes to decode (default 80)')
    p.add_argument('--seq', action='store_true',
                   help='Decode as seq stream (different cmd ranges)')
    p.add_argument('--label', default='', help='Label for the output')
    args = p.parse_args()
    if not os.path.exists(args.sid):
        print(f'sid not found: {args.sid}', file=sys.stderr); return 1
    if not args.addr:
        print('--addr required', file=sys.stderr); return 1
    addr = int(args.addr, 16)
    _, mem = _load_sid_image(args.sid)
    bytes_seq = list(mem[addr:addr + args.max_bytes])
    if args.seq:
        print(_decode_seq(bytes_seq, start_offset=addr))
    else:
        label = args.label or f'pattern @ ${addr:04X}'
        print(_decode_pattern(bytes_seq, start_offset=addr, label=label))
    return 0


if __name__ == '__main__':
    sys.exit(main())
