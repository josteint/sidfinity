#!/usr/bin/env python3
"""find_first_divergence.py — locate the first writelog mismatch between
an HVSC original and a rebuilt SID. This is the Mode 1 ground truth
localizer.

Wraps the writelog → flat-stream → prefix-mismatch flow so a bug
investigation can jump straight to "what register, what frame, what
value" instead of writing the diagnostic from scratch.

Mode 1 verdict (per `feedback_verification_modes`): the rebuild matches
iff the per-`play()` write sequence matches the original frame by
frame. This tool flattens writes across frames and finds the first
`(reg, val)` mismatch. Robust against siddump frame-bucket drift
(Trap C) because the flat sequence is invariant under bucket-boundary
shifts.

Within-frame cycle position is OBSERVATION only — same writes in the
same order at different cycles within a frame are equivalent (Trap B).
The `cycle` field in the output is for context, NOT a divergence signal.

Usage:
    python3 tools/find_first_divergence.py ORIG.sid REBUILD.sid [opts]

Options:
    --subtune N        Subtune to compare (default 0)
    --duration S       Duration in seconds (default: per-subtune
                       songlength from HVSC's Songlengths.md5)
    --context N        Writes of context around the divergence (default 8)
    --skip-init        Skip frame 0 of both runs (default on)
    --include-init     Compare from frame 0 (overrides --skip-init)

Output:
    First divergence position in the (reg, val) flat stream + the
    frame number, cycle offset (observation only — see Trap B above),
    register, both values, and the register's voice + role.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipelines.hubbard.verify_cycle import writelog_capture  # noqa: E402


# Register → (voice, role) cheat sheet. Regs 0-6 = V1, 7-13 = V2,
# 14-20 = V3; regs 21-24 = filter / volume. Voice register block:
# 0 freq lo, 1 freq hi, 2 PW lo, 3 PW hi, 4 ctrl, 5 AD, 6 SR.
_VOICE_ROLES = ['freq lo', 'freq hi', 'PW lo', 'PW hi', 'ctrl',
                'AD', 'SR']
_FILTER_ROLES = {
    0x15: 'filter cutoff lo',
    0x16: 'filter cutoff hi',
    0x17: 'filter res/route',
    0x18: 'vol/filter mode',
}


def describe_reg(reg: int) -> str:
    """Return 'V1 PW hi' / 'vol/filter mode' / etc. for a $D4xx reg.
    Multi-SID writelogs tag each write's chip as reg = chip*0x20 + reg;
    chip 2/3 regs get a 'chip N' prefix (voices numbered through the
    chips: chip 2 V1 = global voice 4)."""
    chip, r = reg >> 5, reg & 0x1F
    prefix = f'chip {chip + 1} ' if 0 < chip < 3 else ''
    if chip < 3:
        if 0x00 <= r <= 0x14:
            voice = r // 7 + 1
            return f'{prefix}V{voice} {_VOICE_ROLES[r % 7]}'
        if r in _FILTER_ROLES:
            return prefix + _FILTER_ROLES[r]
    return f'reg ${reg:02X}'


def _resolve_duration(orig_path: str, subtune: int,
                      duration: float | None) -> float:
    """Per-subtune songlength from HVSC's Songlengths.md5, or the
    explicit value passed in. Mirrors verify.verify_canary's logic."""
    if duration is not None:
        return duration
    md5 = hashlib.md5(open(orig_path, 'rb').read()).hexdigest()
    songlen_path = ROOT / 'hvsc85' / 'DOCUMENTS' / 'Songlengths.md5'
    if not songlen_path.exists():
        print(f'warning: no Songlengths.md5 at {songlen_path} — '
              f'using 60s default', file=sys.stderr)
        return 60.0
    with open(songlen_path) as f:
        for line in f:
            if line.startswith(md5):
                parts = line.rstrip().split('=', 1)[1].split()
                if subtune < len(parts):
                    # Songlengths.md5 uses M:SS or M:SS.mmm (fractional secs).
                    m, s = parts[subtune].split(':')
                    return (int(m) * 60 + float(s)) * 1.1 + 1.0
                break
    print(f'warning: subtune {subtune} not in Songlengths.md5 — '
          f'using 60s default', file=sys.stderr)
    return 60.0


def _flatten(frames, skip_init: bool):
    """Flatten frames into [(reg, val, frame_idx, cycle), ...]."""
    out = []
    for k, fr in enumerate(frames):
        if skip_init and k == 0:
            continue
        for c, reg, val in fr:
            out.append((reg, val, k, c))
    return out


def find_first_divergence(orig_path: str, rebuild_path: str,
                          subtune: int = 0,
                          duration: float | None = None,
                          skip_init: bool = True) -> dict:
    """Capture writelogs from both SIDs and return the first
    (reg, val) divergence in the flat stream."""
    dur = _resolve_duration(orig_path, subtune, duration)
    o = writelog_capture(orig_path, subtune=subtune, duration=dur)
    r = writelog_capture(rebuild_path, subtune=subtune, duration=dur)
    fo = _flatten(o, skip_init)
    fr = _flatten(r, skip_init)
    n = min(len(fo), len(fr))
    div_at = None
    for i in range(n):
        if fo[i][:2] != fr[i][:2]:
            div_at = i
            break
    return {
        'duration_s': dur,
        'orig_writes': len(fo),
        'rebuild_writes': len(fr),
        'match_prefix': div_at if div_at is not None else n,
        'first_div': div_at,
        'orig_flat': fo,
        'rebuild_flat': fr,
    }


def _format_div(result: dict, context: int) -> str:
    lines = []
    dur = result['duration_s']
    lo = result['orig_writes']
    lr = result['rebuild_writes']
    mp = result['match_prefix']
    div = result['first_div']
    lines.append(f'duration: {dur:.1f}s')
    lines.append(f'orig writes:    {lo:>8}')
    lines.append(f'rebuild writes: {lr:>8}')
    lines.append(f'match prefix:   {mp:>8} (= {100*mp/max(lo,lr):.2f}%)')
    if div is None:
        lines.append('NO DIVERGENCE in matching prefix — '
                     '(check len_a vs len_b if not full match)')
        return '\n'.join(lines)
    fo = result['orig_flat']
    fr = result['rebuild_flat']
    o_reg, o_val, o_f, o_c = fo[div]
    r_reg, r_val, r_f, r_c = fr[div]
    lines.append('')
    lines.append(f'FIRST DIVERGENCE at flat position {div}:')
    lines.append(f'  orig:    $D4{o_reg:02X} = ${o_val:02X}  '
                 f'({describe_reg(o_reg)})  '
                 f'@ frame {o_f}, cycle {o_c}')
    lines.append(f'  rebuild: $D4{r_reg:02X} = ${r_val:02X}  '
                 f'({describe_reg(r_reg)})  '
                 f'@ frame {r_f}, cycle {r_c}')
    lines.append('')
    lines.append(f'Context (±{context} writes):')
    n = min(len(fo), len(fr))
    for k in range(max(0, div - context), min(n, div + context + 1)):
        oR, oV, oF, oC = fo[k]
        rR, rV, rF, rC = fr[k]
        diff = oR != rR or oV != rV
        mark = ' <-' if diff else ''
        lines.append(
            f'  [{k:>7}] orig $D4{oR:02X}=${oV:02X} (f{oF},c{oC:>5}) '
            f'{describe_reg(oR):<17} | '
            f'rebuild $D4{rR:02X}=${rV:02X} (f{rF},c{rC:>5}) '
            f'{describe_reg(rR):<17}{mark}')
    lines.append('')
    lines.append('Next steps (per feedback_writelog_divergence_recipe):')
    lines.append('  1. Identify which engine effect writes $D4'
                 f'{o_reg:02X} ({describe_reg(o_reg)}) for that voice.')
    lines.append('  2. Disassemble orig\'s code for that effect near '
                 f'the frame (frame {o_f}).')
    lines.append('  3. Diff orig\'s effect code vs the composer\'s emitter '
                 'line by line.')
    return '\n'.join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('orig', help='HVSC original .sid path')
    p.add_argument('rebuild', help='Rebuilt .sid path (composer output)')
    p.add_argument('--subtune', type=int, default=0)
    p.add_argument('--duration', type=float, default=None,
                   help='seconds (default: per-subtune songlength)')
    p.add_argument('--context', type=int, default=8,
                   help='writes of context around divergence (default 8)')
    p.add_argument('--include-init', action='store_true',
                   help='include frame 0 in comparison')
    args = p.parse_args()
    if not os.path.exists(args.orig):
        print(f'error: orig not found: {args.orig}', file=sys.stderr)
        return 1
    if not os.path.exists(args.rebuild):
        print(f'error: rebuild not found: {args.rebuild}', file=sys.stderr)
        return 1
    result = find_first_divergence(
        args.orig, args.rebuild, args.subtune, args.duration,
        skip_init=not args.include_init)
    print(_format_div(result, args.context))
    return 0 if result['first_div'] is None else 2


if __name__ == '__main__':
    sys.exit(main())
