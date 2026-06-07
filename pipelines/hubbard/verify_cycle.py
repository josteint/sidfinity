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


def writelog_per_irq_capture(sid_path: str, subtune: int = 0,
                             duration: float = 2.0,
                             force_rsid: bool = False) -> list[Frame]:
    """Run `siddump --writelog-per-irq` and parse the per-PSID-`play()`
    register writes — one `Frame` per play() invocation instead of one per
    siddump 50 Hz frame.

    This is the verdict capture for CIA-timed tunes (PSID `speed != 0`).
    Such tunes' play() invocations do not align with siddump's 19656-cycle
    frame buckets, so the flat `--writelog` capture buckets the init + first
    play() differently for the original vs a rebuild whose init has a
    different length (different CIA phase) — making the flat streams
    "diverge at position 0" even when every play()'s write sequence is
    identical (Trap C specialised to CIA tunes). The per-irq tool:

      * splits writes by play-entry cycle (so each `|I` chunk = one play),
      * drops the tune's init writes (those preceding the FIRST play entry
        of the run), which differ in count between orig and rebuild.

    The returned frames therefore start at play[0]; flattening them and
    comparing with `compare_instruction_stream` aligns orig vs rebuild
    play-for-play. Validated against the `--pc-trace` oracle (Human_Race
    54/54, Battle_of_Britain 54/54).

    `subtune` is 0-indexed (as in `writelog_capture`).
    """
    cmd = [SIDDUMP, sid_path, '--subtune', str(subtune + 1),
           '--duration', str(duration), '--writelog-per-irq', '--raw']
    if force_rsid:
        cmd.append('--force-rsid')
    r = subprocess.run(cmd, capture_output=True, text=True)
    frames: list[Frame] = []
    for line in r.stdout.splitlines():
        if '|I' not in line:
            continue
        # A line may carry MULTIPLE |I chunks (multiple play()s per siddump
        # frame under CIA). Each chunk = :cyc:reg:val:cyc:reg:val...
        for chunk in line.split('|I')[1:]:
            toks = [t for t in chunk.split(':') if t != '']
            writes: Frame = []
            for i in range(0, len(toks) - 2, 3):
                try:
                    writes.append((int(toks[i]), int(toks[i + 1], 16),
                                   int(toks[i + 2], 16)))
                except ValueError:
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
                                skip_init: bool = True,
                                mode: str = 'legacy') -> dict:
    """Compare the (reg, val) sequence the SID receives in two runs.

    Two modes:

    `mode='play_plus_state'` — DRAFT. The principled verdict per
    the init trichotomy (`docs/sid_init_report.md §5`). Two checks:

      A. **Check A — SID state at end of init.** Strict
         register-by-register comparison of $D400-$D418 final
         values.

      B. **Check B — play stream from frame 1 onward.**
         Position-by-position match.

      `is_full = state_match AND play_full`.

    **Known issue**: as currently implemented, Check A compares
    "last value written during siddump frame 0," which is a VBI
    clock boundary, not a CPU `init RTS` event. Tunes whose init
    completes early in a VBI period have play() writes spilling
    into frame 0; the rebuild's init may take a different cycle
    count, putting a different count of play() writes into frame
    0 vs frame 1. Check A's snapshot then differs even when both
    runs produce byte-identical streams. See `legacy` mode for
    the current verdict.

    The principled fix is to capture the original's true
    end-of-init chip state via py65 cycle-precise emulation
    (stopping at init's RTS), store it in USF priming, and have
    the composer's universal init reproduce it. This is the next
    phase of the rewrite (universal-reset composer init); strict
    Check A becomes meaningful at that point.

    `mode='legacy'` (default) — the current verdict for in-tree
    callers. Returns `match`, `match_all`, `match_post_init`, and
    the corresponding `len_*` fields. `is_full` is True if EITHER
    `match_all` or `match_post_init` is a full match.

    The `skip_init` argument is honored in legacy mode only; it
    has no effect in `play_plus_state` mode.
    """
    flat_all_a = [(reg, val) for frame in a for _, reg, val in frame]
    flat_all_b = [(reg, val) for frame in b for _, reg, val in frame]
    flat_post_a = [(reg, val) for k, frame in enumerate(a)
                   if k > 0 for _, reg, val in frame]
    flat_post_b = [(reg, val) for k, frame in enumerate(b)
                   if k > 0 for _, reg, val in frame]

    def _prefix(x, y):
        n = min(len(x), len(y))
        for i in range(n):
            if x[i] != y[i]:
                return i
        return n

    if mode == 'play_plus_state':
        # Check A: strict register-by-register comparison of the LAST
        # value written to each $D400-$D418 register during frame 0
        # (default 0 if unwritten in that frame).
        def end_state(frames):
            state = [0] * 0x19
            if frames:
                for _, reg, val in frames[0]:
                    if 0 <= reg < 0x19:
                        state[reg] = val
            return state
        state_a = end_state(a)
        state_b = end_state(b)
        state_match = state_a == state_b
        state_diff = [
            (r, state_a[r], state_b[r]) for r in range(0x19)
            if state_a[r] != state_b[r]]

        # Check B: play stream from frame 1 onward.
        play_match = _prefix(flat_post_a, flat_post_b)
        play_len_a = len(flat_post_a)
        play_len_b = len(flat_post_b)
        play_full = (play_match == play_len_a == play_len_b)

        return {
            'mode': 'play_plus_state',
            'state_match': state_match,
            'state_diff': state_diff,        # list of (reg, orig_val, reb_val)
            'play_match': play_match,
            'play_len_a': play_len_a,
            'play_len_b': play_len_b,
            'play_full': play_full,
            'is_full': state_match and play_full,
        }

    # Legacy mode.
    match_all = _prefix(flat_all_a, flat_all_b)
    match_post = _prefix(flat_post_a, flat_post_b)
    flat_a = flat_post_a if skip_init else flat_all_a
    flat_b = flat_post_b if skip_init else flat_all_b
    is_full = (
        (match_all == len(flat_all_a) == len(flat_all_b)) or
        (match_post == len(flat_post_a) == len(flat_post_b)))
    return {
        'mode': 'legacy',
        'match': max(match_all, match_post),
        'match_all': match_all,
        'match_post_init': match_post,
        'len_a': len(flat_a),
        'len_b': len(flat_b),
        'len_all_a': len(flat_all_a),
        'len_all_b': len(flat_all_b),
        'len_post_a': len(flat_post_a),
        'len_post_b': len(flat_post_b),
        'is_full': is_full,
    }


