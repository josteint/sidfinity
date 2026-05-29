"""verify_cycle.py — cycle-accurate verification via siddump --writelog.

py65's `inst_program.capture` is frame-granular and physically cannot
see cycle-timed playback (and would blow its step budget on a blocking
digi routine). This harness drives `siddump --writelog`, the cycle-
timed `(cycle, reg, val)` write stream from libsidplayfp — the
project's ground truth for what the SID chip actually receives.

Two comparisons:

- `compare_instruction_stream` — the music comparator. Concatenates
  all writes across all frames in cycle order, drops the init
  invocation, compares the (reg, val) sequence. The SID chip sees a
  continuous stream of writes; siddump's VBI-frame bucketing is
  reporting, not part of what the chip receives — so per-frame
  comparisons spuriously flag cycle-drift across frame boundaries as
  "divergence" when the actual instruction stream is identical.

- `compare_strict` — full per-frame (cycle, reg, val) equality. The
  right comparison for digi, where the cycle within the frame IS the
  signal (sample bits are timed cycle-precise).
"""

from __future__ import annotations

import os
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
SIDDUMP = os.path.join(ROOT, 'tools', 'siddump')

# A frame's writes: ordered list of (cycle_in_frame, reg, val).
Frame = list[tuple[int, int, int]]


def writelog_capture(sid_path: str, subtune: int = 0,
                     duration: float = 2.0,
                     force_rsid: bool = False) -> list[Frame]:
    """Run `siddump --writelog` and parse the per-frame cycle-timed
    register writes.

    `subtune` is 0-indexed (PSID/`inst_program.capture` convention): 0 =
    the first subtune. Internally we add 1 to match siddump's 1-indexed
    `--subtune` argument (where 0 is a sentinel for `startSong`).
    """
    cmd = [SIDDUMP, sid_path, '--subtune', str(subtune + 1),
           '--duration', str(duration), '--writelog', '--raw']
    if force_rsid:
        cmd.append('--force-rsid')
    r = subprocess.run(cmd, capture_output=True, text=True)
    frames: list[Frame] = []
    for line in r.stdout.splitlines():
        if '|W:' not in line:
            continue
        _, w = line.split('|W:', 1)
        toks = w.strip().split(':')
        writes: Frame = []
        for i in range(0, len(toks) - 2, 3):
            try:
                writes.append((int(toks[i]), int(toks[i + 1], 16),
                               int(toks[i + 2], 16)))
            except ValueError:
                # malformed write — skip; siddump shouldn't emit them
                # but defend against truncation.
                pass
        frames.append(writes)
    return frames


def compare_strict(a: list[Frame], b: list[Frame]) -> dict:
    """Cycle-exact comparison: every (cycle, reg, val) tuple identical.
    The right comparison for digi."""
    n = min(len(a), len(b))
    match = 0
    first_diff = None
    for k in range(n):
        if a[k] == b[k]:
            match += 1
        elif first_diff is None:
            first_diff = (k, a[k], b[k])
    return {'frames': n, 'match': match, 'first_diff': first_diff,
            'len_a': len(a), 'len_b': len(b)}


def compare_instruction_stream(a: list[Frame], b: list[Frame],
                                skip_init: bool = True) -> dict:
    """Global cycle-ordered comparison of the (reg, val) sequence the
    SID actually receives.

    siddump's VBI-frame bucketing of writes is an OBSERVATION artifact:
    writes near frame boundaries can shift bucket when total play()
    cycle count drifts by even a few cycles. The SID chip itself just
    receives a stream of writes in cycle order — the bucketing is
    siddump's reporting choice, not part of the music.

    This compare concatenates all writes across all frames in cycle
    order, then matches the (reg, val) sequence position-by-position.

    `skip_init=True` (default) drops frame 0 — the init invocation —
    from both sides before comparing. Engine-specific init order
    (e.g. silence direction, pre-D418 write, AD/SR ordering) can vary
    while still producing the same final SID state and the same music.
    For verifying "the rebuild plays the same music as the original,"
    music-only is the right comparison.

    Returns the longest matching prefix length plus both stream totals.
    A clean run produces match == min(len_a, len_b). A length mismatch
    with full-prefix match means init duration drifted by a few
    cycles and the test window contains a different number of music
    ticks on each side — equivalent musically, just truncated
    differently.
    """
    def flatten(stream):
        return [(reg, val)
                for k, frame in enumerate(stream)
                if (not skip_init or k > 0)
                for _, reg, val in frame]
    flat_a = flatten(a)
    flat_b = flatten(b)
    n = min(len(flat_a), len(flat_b))
    match = 0
    for i in range(n):
        if flat_a[i] == flat_b[i]:
            match += 1
        else:
            break
    return {'match': match, 'len_a': len(flat_a), 'len_b': len(flat_b)}


