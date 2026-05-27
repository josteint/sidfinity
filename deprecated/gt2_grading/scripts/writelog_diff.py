"""writelog_diff.py — Frame-by-frame diff of the SID register write stream.

The acceptance test for the USF instrument-program refactor
(`docs/usf_instrument_program_plan.md`). For two SIDs A and B, runs
`siddump --writelog --raw` on both and compares each frame's
`(register, value)` write sequence. Cycle counters within a frame are
ignored (the codegen is allowed to differ from the original 6502 in
where within a frame writes happen, as long as the resulting per-frame
write SEQUENCE is identical).

Output:
  - one-line summary: total frames, matching frames, divergent frames.
  - first N divergent frames with reg/val deltas.
  - per-register-index divergence count.

Exit code: 0 if all frames match register-write sequences, 1 otherwise.

Usage:
  python3 src/writelog_diff.py <orig.sid> <rebuilt.sid> [--duration N]
                                                       [--frames-shown K]
                                                       [--ignore-order]
"""
from __future__ import annotations

import argparse
import subprocess
import sys

SIDDUMP = '/home/jtr/sidfinity/tools/siddump'


def _run_siddump(sid_path: str, duration: int) -> list[str]:
    out = subprocess.run(
        [SIDDUMP, sid_path, '--writelog', '--force-rsid',
         '--duration', str(duration), '--raw'],
        capture_output=True, text=True, timeout=120,
    )
    if out.returncode != 0:
        raise RuntimeError(f'siddump failed for {sid_path}: {out.stderr[:200]}')
    # Strip leading metadata + CSV header. Each data line is one frame.
    return [line for line in out.stdout.split('\n') if line.strip()][2:]


def _parse_writes(frame_line: str) -> list[tuple[int, int]]:
    """Return list of (register, value) writes for this frame, in order
    (cycle counters discarded). Empty list if the frame has no writes."""
    if '|' not in frame_line:
        return []
    _, w = frame_line.split('|', 1)
    if not w.startswith('W:'):
        return []
    parts = w[2:].split(':')
    out: list[tuple[int, int]] = []
    for i in range(0, len(parts) - 2, 3):
        try:
            reg = int(parts[i + 1], 16)
            val = int(parts[i + 2], 16)
            out.append((reg, val))
        except (ValueError, IndexError):
            break
    return out


_REG_NAMES = {
    0x00: 'V1_freq_lo', 0x01: 'V1_freq_hi',
    0x02: 'V1_pw_lo',   0x03: 'V1_pw_hi',
    0x04: 'V1_ctrl',    0x05: 'V1_ad',    0x06: 'V1_sr',
    0x07: 'V2_freq_lo', 0x08: 'V2_freq_hi',
    0x09: 'V2_pw_lo',   0x0A: 'V2_pw_hi',
    0x0B: 'V2_ctrl',    0x0C: 'V2_ad',    0x0D: 'V2_sr',
    0x0E: 'V3_freq_lo', 0x0F: 'V3_freq_hi',
    0x10: 'V3_pw_lo',   0x11: 'V3_pw_hi',
    0x12: 'V3_ctrl',    0x13: 'V3_ad',    0x14: 'V3_sr',
    0x15: 'fc_lo',      0x16: 'fc_hi',
    0x17: 'res_filt',   0x18: 'vol',
}


def _fmt_writes(writes: list[tuple[int, int]]) -> str:
    if not writes:
        return '(no writes)'
    return ' '.join(f'{_REG_NAMES.get(r, f"${r:02X}")}=${v:02X}' for r, v in writes)


def diff(orig_sid: str, rebuilt_sid: str, duration: int = 30,
         frames_shown: int = 5, ignore_order: bool = False) -> int:
    orig_frames = _run_siddump(orig_sid, duration)
    new_frames = _run_siddump(rebuilt_sid, duration)
    n = min(len(orig_frames), len(new_frames))

    matched = 0
    divergent: list[tuple[int, list[tuple[int, int]], list[tuple[int, int]]]] = []
    per_reg_diff: dict[int, int] = {}

    for i in range(n):
        ow = _parse_writes(orig_frames[i])
        nw = _parse_writes(new_frames[i])
        same = (sorted(ow) == sorted(nw)) if ignore_order else (ow == nw)
        if same:
            matched += 1
        else:
            divergent.append((i, ow, nw))
            # Tally per-register diffs based on multi-set difference
            ow_ms = {}
            for r, v in ow:
                ow_ms[(r, v)] = ow_ms.get((r, v), 0) + 1
            nw_ms = {}
            for r, v in nw:
                nw_ms[(r, v)] = nw_ms.get((r, v), 0) + 1
            seen_regs = set()
            for kv in set(ow_ms) | set(nw_ms):
                if ow_ms.get(kv, 0) != nw_ms.get(kv, 0):
                    seen_regs.add(kv[0])
            for r in seen_regs:
                per_reg_diff[r] = per_reg_diff.get(r, 0) + 1

    pct = 100.0 * matched / max(n, 1)
    mode = 'ordered' if not ignore_order else 'order-independent'
    print(f'Writelog write-sequence match ({mode}):  '
          f'{matched}/{n} = {pct:.2f}%  ({len(divergent)} divergent)')

    if divergent:
        print()
        print(f'First {min(frames_shown, len(divergent))} divergent frames:')
        for i, ow, nw in divergent[:frames_shown]:
            print(f'  frame {i}:')
            print(f'    orig: {_fmt_writes(ow)[:240]}')
            print(f'    new:  {_fmt_writes(nw)[:240]}')

    if per_reg_diff:
        print()
        print('Per-register divergence (frames affected):')
        for r, n_div in sorted(per_reg_diff.items(), key=lambda kv: -kv[1])[:10]:
            print(f'  ${r:02X} {_REG_NAMES.get(r, ""):<14}  {n_div}')

    return 0 if not divergent else 1


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('orig')
    p.add_argument('rebuilt')
    p.add_argument('--duration', type=int, default=30,
                   help='Seconds to render (default 30 = 1500 PAL frames)')
    p.add_argument('--frames-shown', type=int, default=5,
                   help='First N divergent frames to dump in detail')
    p.add_argument('--ignore-order', action='store_true',
                   help='Treat per-frame writes as a multiset (ignore order)')
    args = p.parse_args()
    sys.exit(diff(args.orig, args.rebuilt, args.duration,
                  args.frames_shown, args.ignore_order))


if __name__ == '__main__':
    main()
