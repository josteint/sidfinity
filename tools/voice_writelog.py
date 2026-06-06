#!/usr/bin/env python3
"""voice_writelog.py — filter siddump --writelog to one voice with
effect-attribution heuristics.

When investigating a Mode 1 divergence on a specific voice (e.g. "V2
freq hi diverges"), the full writelog is noisy — interleaved across
3 voices + filter writes. This tool filters to a single voice's
writes and tags each write with the engine routine most likely to
have produced it.

Usage:
    python3 tools/voice_writelog.py SID --voice {1|2|3} \
                                    [--subtune N] [--duration S] \
                                    [--start-frame F] [--end-frame F] \
                                    [--diff-against OTHER.sid]

Output: tagged writelog stream for the chosen voice, including filter/
$D418 writes (which often relate to the same drum/SFX events).

Attribution heuristics are based on FC-family + Hubbard '85 idioms.
NOT authoritative — they're hints. If wrong, fall back to the writelog
+ orig disasm flow per feedback_writelog_divergence_recipe.

Effect-attribution rules (per write):
  D40_ AD/SR (5/6, 12/13, 19/20):    nolengset (new-note inst reload)
  D40_ PW lo/hi (2/3, 9/10, 16/17):  pp_store / fx_pulse_prog / fx_pulse_run / nolengset
  D40_ freq lo/hi (0/1, 7/8, 14/15): nolengset / glide / vibrato / fx_drum / noise-tick
  D40_ ctrl:
      $X1 or $X9 (gate bit set):     nolengset gate-on   OR  fx_drum gate-strobe
      $X0 or $X8 (gate bit clear):   h11 release OR h10 held-note release
      $8_ (noise high nibble):       fx_drum / fx_noise_tick (Hawkeye-style)
      $_8 (test bit):                fx_strange_filter
  $D415/$D416 cutoff:                fx_filter_prog OR fm2 cleanup
  $D417 res/route:                   $F1 filter set pattern cmd OR init
  $D418 vol/filter mode:             master vol OR fx_filter_prog OR fm2
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipelines.hubbard.verify_cycle import writelog_capture  # noqa: E402


# Voice register ranges within $D400-$D414. Each voice has 7 regs.
_VOICE_REG_RANGES = {
    1: (0x00, 0x06),
    2: (0x07, 0x0D),
    3: (0x0E, 0x14),
}
_VOICE_REG_NAMES = ['freq lo', 'freq hi', 'PW lo', 'PW hi',
                    'ctrl', 'AD', 'SR']
_SHARED_REG_NAMES = {
    0x15: 'filter cutoff lo',
    0x16: 'filter cutoff hi',
    0x17: 'filter res/route',
    0x18: 'vol/filter mode',
}


def voice_register_name(reg: int, voice: int) -> str | None:
    """Return human-readable name for a register IF it belongs to the
    given voice, otherwise None."""
    if reg in _SHARED_REG_NAMES:
        return _SHARED_REG_NAMES[reg]
    lo, hi = _VOICE_REG_RANGES[voice]
    if lo <= reg <= hi:
        return f'V{voice} {_VOICE_REG_NAMES[reg - lo]}'
    return None


def attribute_write(reg: int, val: int, voice: int,
                    prev_ctrl: dict[int, int]) -> str:
    """Heuristic: which engine routine most likely produced this write?"""
    lo, hi = _VOICE_REG_RANGES[voice]
    if lo <= reg <= hi:
        role = reg - lo
        if role in (5, 6):
            return 'nolengset (AD/SR — full inst reload)'
        if role in (0, 1):
            return 'nolengset|glide|vibrato|fx_drum (freq lookup)'
        if role in (2, 3):
            return 'pp_store|fx_pulse_prog|fx_pulse_run|nolengset (PW)'
        if role == 4:  # ctrl
            prev = prev_ctrl.get(voice, 0)
            gate_was = prev & 0x01
            gate_now = val & 0x01
            tags = []
            if val & 0x80:
                tags.append('fx_drum|noise_tick (noise wave)')
            if val & 0x08:
                tags.append('fx_strange_filter (test bit)')
            if gate_now and not gate_was:
                tags.append('nolengset gate-on')
            elif gate_was and not gate_now:
                tags.append('h11|h10 release (gate-off)')
            else:
                tags.append('nextvoice ctrl shadow')
            return ' / '.join(tags)
    elif reg in _SHARED_REG_NAMES:
        if reg == 0x18:
            return 'master vol|fx_filter_prog|fm2 cleanup'
        if reg == 0x16 or reg == 0x15:
            return 'fx_filter_prog|fm2 cleanup'
        if reg == 0x17:
            return '$F1 filterset pattern cmd | init'
    return '?'


def filter_voice(frames, voice: int):
    """Yield (frame_idx, cycle, reg, val, name) for writes that belong
    to this voice (voice regs + filter/vol shared regs)."""
    voice_lo, voice_hi = _VOICE_REG_RANGES[voice]
    for f, fr in enumerate(frames):
        for c, reg, val in fr:
            name = voice_register_name(reg, voice)
            if name is None:
                continue
            yield f, c, reg, val, name


def format_writelog(frames, voice: int, start_frame: int = 0,
                    end_frame: int | None = None) -> str:
    lines = []
    prev_ctrl = {1: 0, 2: 0, 3: 0}
    n = len(frames)
    if end_frame is None or end_frame > n:
        end_frame = n
    lines.append(f'# V{voice} writelog (filtered) — frames '
                 f'{start_frame}..{end_frame}')
    lines.append('# frame  cycle  reg   value  role'
                 '            attribution')
    last_frame = -1
    for f, c, reg, val, name in filter_voice(frames, voice):
        if f < start_frame or f >= end_frame:
            continue
        if f != last_frame:
            lines.append(f'--- frame {f} ---')
            last_frame = f
        attr = attribute_write(reg, val, voice, prev_ctrl)
        ctrl_lo, ctrl_hi = _VOICE_REG_RANGES[voice]
        if reg == ctrl_lo + 4:  # this is V's ctrl
            prev_ctrl[voice] = val
        lines.append(f'  f{f:<6} c{c:<5}  $D4{reg:02X}  ${val:02X}    '
                     f'{name:<18}  {attr}')
    return '\n'.join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('sid', help='Path to .sid file')
    p.add_argument('--voice', type=int, choices=[1, 2, 3], required=True)
    p.add_argument('--subtune', type=int, default=0,
                   help='0-indexed (default 0)')
    p.add_argument('--duration', type=float, default=10.0)
    p.add_argument('--start-frame', type=int, default=0)
    p.add_argument('--end-frame', type=int, default=None)
    p.add_argument('--diff-against', default=None,
                   help='If provided, also dump the other SID\'s V<voice> '
                        'writelog and show side-by-side diff at frames where '
                        'they differ.')
    args = p.parse_args()
    if not os.path.exists(args.sid):
        print(f'sid not found: {args.sid}', file=sys.stderr); return 1
    frames = writelog_capture(args.sid, subtune=args.subtune,
                              duration=args.duration)
    print(format_writelog(frames, args.voice, args.start_frame,
                          args.end_frame))
    if args.diff_against:
        if not os.path.exists(args.diff_against):
            print(f'diff-against not found: {args.diff_against}',
                  file=sys.stderr); return 1
        other = writelog_capture(args.diff_against, subtune=args.subtune,
                                  duration=args.duration)
        print()
        print('=' * 60)
        print(f'DIFF AGAINST: {args.diff_against}')
        print('=' * 60)
        print(format_writelog(other, args.voice, args.start_frame,
                              args.end_frame))
    return 0


if __name__ == '__main__':
    sys.exit(main())
