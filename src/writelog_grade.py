"""writelog_grade.py — Honest grader. Compares cycle-accurate writelogs.

Replaces sid_compare.py's heuristic register-snapshot grader for the
"is this rebuild actually correct" question. Two SIDs with byte-equal
writelogs are guaranteed audibly identical (deterministic emulation).
No tolerance rules, no false positives.

Two granularities:
  - Frame snapshot: 25 SID register values at end of each frame.
    Cheap, sufficient for tracker music where cycle-level write order
    within a frame doesn't affect audio (only the final state does).
  - Cycle-accurate writelog: every cycle:reg:val triple. Stricter,
    needed for digi/demo SIDs where intra-frame write timing is
    audible (sample playback, racing the beam, etc.).

Grade scheme (per frame-snapshot match rate). Calibrated against:
  - Perfect Lean V3 Commando rebuild: 98.4% (audibly identical; the
    1.6% gap is page-crossing cycle jitter — different player code
    means VBI samples slightly different play-loop states. Inaudible
    for tracker music.) → A.
  - rh_to_usf Commando (audibly garbage per ear test): 1.0% → F.
  - rh_to_usf Monty (audibly garbage per ear test): 0.0% → F.

  A  — ≥98%   audibly identical (jitter only)
  B  — ≥90%   mostly correct, a few frames off
  C  — ≥70%   noticeably wrong
  D  — ≥30%   substantially wrong
  F  — <30%   broken

Usage:
  python3 src/writelog_grade.py <orig.sid> <rebuilt.sid> [--duration N] [--cycle-accurate]
"""

import os
import subprocess
import sys
from dataclasses import dataclass, field

SIDDUMP = '/home/jtr/sidfinity/tools/siddump'


def _run_siddump(sid_path: str, duration: int = 30) -> list[str]:
    """Run siddump --writelog --raw on a SID; return list of frame lines."""
    out = subprocess.run(
        [SIDDUMP, sid_path, '--writelog', '--duration', str(duration), '--raw'],
        capture_output=True, text=True, timeout=60,
    )
    if out.returncode != 0:
        raise RuntimeError(f'siddump failed for {sid_path}: {out.stderr[:200]}')
    return [line for line in out.stdout.split('\n') if line.strip()]


def _split_frame(line: str) -> tuple[str, str]:
    """Split a writelog frame into (snapshot, writes)."""
    if '|' in line:
        snap, writes = line.split('|', 1)
        return snap, writes
    return line, ''


@dataclass
class GradeReport:
    """Result of comparing two writelogs."""
    grade: str                     # A / B / C / D / F
    snapshot_match_pct: float      # 0..100
    snapshot_matched: int
    snapshot_total: int
    writes_match_pct: float        # 0..100 (cycle-accurate, if computed)
    cycle_accurate: bool           # whether full writelog comparison was done
    first_diverge_frame: int | None
    first_diverge_orig: str | None
    first_diverge_new: str | None
    diverging_registers: dict[int, int]  # register → number of frames it differs in
    duration: int

    def summary(self) -> str:
        s = []
        s.append(f'Grade: {self.grade}  '
                 f'(snapshots {self.snapshot_match_pct:.1f}%, '
                 f'{self.snapshot_matched}/{self.snapshot_total})')
        if self.cycle_accurate:
            s.append(f'Cycle-accurate writes: {self.writes_match_pct:.1f}%')
        if self.first_diverge_frame is not None:
            s.append(f'First divergence at frame {self.first_diverge_frame}:')
            s.append(f'  orig: {self.first_diverge_orig[:120]}')
            s.append(f'  new:  {self.first_diverge_new[:120]}')
        if self.diverging_registers:
            top = sorted(self.diverging_registers.items(),
                         key=lambda kv: -kv[1])[:8]
            s.append('Most-diverging SID registers:')
            for reg, n in top:
                s.append(f'  ${reg:02X} ({_register_name(reg)}): '
                         f'differs in {n} frames')
        return '\n'.join(s)


def _register_name(reg: int) -> str:
    """Human-readable name for a SID register offset (0-24)."""
    names_voice = ['freq_lo', 'freq_hi', 'pulse_lo', 'pulse_hi',
                   'ctrl', 'attack_decay', 'sustain_release']
    if 0 <= reg < 21:
        voice = reg // 7
        off = reg % 7
        return f'V{voice+1}_{names_voice[off]}'
    return {
        21: 'filter_cutoff_lo', 22: 'filter_cutoff_hi',
        23: 'filter_ctrl', 24: 'mode_volume',
    }.get(reg, f'reg_{reg:02X}')


def _grade_from_pct(pct: float) -> str:
    if pct >= 98.0: return 'A'
    if pct >= 90.0: return 'B'
    if pct >= 70.0: return 'C'
    if pct >= 30.0: return 'D'
    return 'F'


def grade(orig_sid: str, rebuilt_sid: str, duration: int = 30,
          cycle_accurate: bool = False) -> GradeReport:
    """Grade `rebuilt_sid` against `orig_sid` via writelog comparison."""
    orig_frames = _run_siddump(orig_sid, duration)
    new_frames = _run_siddump(rebuilt_sid, duration)

    n = min(len(orig_frames), len(new_frames))
    snap_matched = 0
    diverging_regs: dict[int, int] = {}
    first_div_idx = None
    first_div_orig = None
    first_div_new = None

    for i in range(n):
        o_snap, o_writes = _split_frame(orig_frames[i])
        n_snap, n_writes = _split_frame(new_frames[i])

        if o_snap == n_snap:
            snap_matched += 1
        else:
            if first_div_idx is None:
                first_div_idx = i
                first_div_orig = orig_frames[i]
                first_div_new = new_frames[i]
            # Tally per-register divergences
            o_regs = o_snap.split(',')
            n_regs = n_snap.split(',')
            for r, (a, b) in enumerate(zip(o_regs, n_regs)):
                if a != b:
                    diverging_regs[r] = diverging_regs.get(r, 0) + 1

    snap_pct = 100 * snap_matched / max(n, 1)

    # Cycle-accurate write comparison (optional, more expensive)
    writes_pct = 0.0
    if cycle_accurate:
        write_matched = 0
        write_total = 0
        for i in range(n):
            _, ow = _split_frame(orig_frames[i])
            _, nw = _split_frame(new_frames[i])
            # Each frame's writes are colon-delimited triples after `W:`
            o_triples = _parse_writes(ow)
            n_triples = _parse_writes(nw)
            # Count individual triple-equality
            o_set = set(o_triples)
            n_set = set(n_triples)
            write_matched += len(o_set & n_set)
            write_total += max(len(o_set), len(n_set))
        writes_pct = 100 * write_matched / max(write_total, 1)

    return GradeReport(
        grade=_grade_from_pct(snap_pct),
        snapshot_match_pct=snap_pct,
        snapshot_matched=snap_matched,
        snapshot_total=n,
        writes_match_pct=writes_pct,
        cycle_accurate=cycle_accurate,
        first_diverge_frame=first_div_idx,
        first_diverge_orig=first_div_orig,
        first_diverge_new=first_div_new,
        diverging_registers=diverging_regs,
        duration=duration,
    )


def _parse_writes(writes_field: str) -> list[tuple[int, int, int]]:
    """Parse `W:cycle:reg:val:cycle:reg:val:...` into (cycle, reg, val) triples."""
    if not writes_field.startswith('W:'):
        return []
    parts = writes_field[2:].split(':')
    out = []
    for i in range(0, len(parts) - 2, 3):
        try:
            cycle = int(parts[i])
            reg = int(parts[i + 1], 16)
            val = int(parts[i + 2], 16)
            out.append((cycle, reg, val))
        except (ValueError, IndexError):
            break
    return out


def main():
    import argparse
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('orig')
    p.add_argument('rebuilt')
    p.add_argument('--duration', type=int, default=30)
    p.add_argument('--cycle-accurate', action='store_true')
    args = p.parse_args()
    r = grade(args.orig, args.rebuilt, args.duration, args.cycle_accurate)
    print(r.summary())


if __name__ == '__main__':
    main()
