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


# Register indices into a $D400-$D418 state vector.
_VOICE_FREQ_LO = (0x00, 0x07, 0x0E)
_VOICE_FREQ_HI = (0x01, 0x08, 0x0F)
_VOICE_CTRL = (0x04, 0x0B, 0x12)


def init_boundary_is_canonical(state: list) -> bool:
    """Does this end-of-init $D400-$D418 register state put the SID's
    INTERNAL analog state into its canonical reset?

    The register write-log can't observe the chip's internal analog state
    (oscillator phase accumulators, envelope-generator counters, filter
    integrators). But when, at the moment play() takes over, every voice has
    its GATE off (so envelopes are idle → output 0) AND its FREQUENCY 0 (so
    the phase accumulator is frozen, not advancing), the internal state is
    pinned to its power-on/reset condition regardless of how the init got
    there. Under that condition, two runs that reach an IDENTICAL register
    state (Check A) and then emit an IDENTICAL play stream (Check B) have
    IDENTICAL internal-state evolution too — so the audio is provably the
    same, even though we replaced the engine's init with our own.

    When this returns False (e.g. an engine that leaves a voice gated or at
    a non-zero frequency at the init boundary), register-state match alone no
    longer guarantees the internal state matches — the first note's attack
    can depend on init-length-dependent phase/envelope history — so that
    subtune wants an ear test, not just the write-log verdict.
    """
    gates_off = all((state[c] & 0x01) == 0 for c in _VOICE_CTRL)
    freq_zero = all(state[r] == 0 for r in _VOICE_FREQ_LO + _VOICE_FREQ_HI)
    return gates_off and freq_zero


def _trichotomy_compare(fa: list, fb: list, close_tol: int = 64,
                        max_init: int = 4096, win: int = 64) -> dict:
    """Init-trichotomy comparison of two flat (reg, val) streams.

    `fa`, `fb` are the full flattened write streams (init + play). The play
    (music) substreams are assumed identical; the streams differ only by a
    short init PREFIX of differing length/content.

    Returns Check A (`state_match`) + Check B (`play_full`, `close`), with
    `is_full = state_match and play_full and close`. Also reports the
    recovered `shift_d`, per-side init lengths, and a `state_diff` /
    `first_play_diff` for localisation.
    """
    la, lb = len(fa), len(fb)

    def aligned_run(d: int, start_a: int) -> int:
        """Length of the matching run of fa[start_a:] vs fb[start_a+d:]."""
        ib = start_a + d
        k = 0
        while start_a + k < la and ib + k < lb and fa[start_a + k] == fb[ib + k]:
            k += 1
        return k

    # 1. Recover the global play-stream shift d = (init_len_b - init_len_a)
    #    via a landmark window deep in the music. Prefer the smallest |d|.
    d = None
    n = min(la, lb)
    if n >= win:
        p = n // 2
        landmark = fa[p:p + win]
        for cand in sorted(range(-max_init, max_init + 1), key=abs):
            j = p + cand
            if 0 <= j and j + win <= lb and fb[j:j + win] == landmark:
                d = cand
                break
    if d is None:
        # No alignment: total mismatch (or streams too short). Fall back to a
        # plain prefix match so the verdict is still meaningful.
        m = 0
        for i in range(n):
            if fa[i] != fb[i]:
                break
            m += 1
        return {
            'mode': 'trichotomy', 'shift_d': None,
            'init_len_a': 0, 'init_len_b': 0,
            'state_match': False, 'state_diff': [],
            'play_match': m, 'play_overlap': n,
            'play_full': m == n == la == lb, 'close': la == lb,
            'len_post_a': la, 'len_post_b': lb,
            'is_full': m == n == la == lb,
        }

    # 2. Find ia = first index where the shifted match begins (music start).
    #    The init prefixes differ, so the match only kicks in after both inits.
    ia = max(0, -d)
    limit = min(la - win, ia + max_init)
    while ia <= limit:
        if fa[ia:ia + win] == fb[ia + d:ia + d + win]:
            break
        ia += 1
    else:
        ia = max(0, -d)
    ib = ia + d

    # Check B: aligned play stream.
    play_match = aligned_run(d, ia)
    overlap = min(la - ia, lb - ib)
    play_full = play_match == overlap
    post_a, post_b = la - ia, lb - ib
    close = abs(post_a - post_b) <= close_tol
    first_play_diff = None
    if not play_full:
        k = play_match
        first_play_diff = (k, fa[ia + k], fb[ib + k])

    # Check A: end-of-init chip state (the priming result).
    def end_state(flat, end):
        st = [0] * 0x19
        for reg, val in flat[:end]:
            if 0 <= reg < 0x19:
                st[reg] = val
        return st
    sa, sb = end_state(fa, ia), end_state(fb, ib)
    state_match = sa == sb
    state_diff = [(r, sa[r], sb[r]) for r in range(0x19) if sa[r] != sb[r]]

    # Audio-equivalence guarantee: if the init boundary is canonical (gates
    # off + freq 0) on BOTH sides, the chip's internal analog state is pinned
    # to reset, so Check A + Check B imply identical audio — replacing the
    # init introduced no audible change. Otherwise flag for an ear test.
    canon_a = init_boundary_is_canonical(sa)
    canon_b = init_boundary_is_canonical(sb)
    init_canonical = canon_a and canon_b

    return {
        'mode': 'trichotomy', 'shift_d': d,
        'init_len_a': ia, 'init_len_b': ib,
        'state_match': state_match, 'state_diff': state_diff,
        'play_match': play_match, 'play_overlap': overlap,
        'play_full': play_full, 'close': close,
        'first_play_diff': first_play_diff,
        'len_post_a': post_a, 'len_post_b': post_b,
        'init_canonical': init_canonical,
        'init_canonical_orig': canon_a, 'init_canonical_reb': canon_b,
        'audio_guaranteed': state_match and play_full and close and init_canonical,
        'is_full': state_match and play_full and close,
    }


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

    if mode == 'trichotomy':
        # PRINCIPLED init-trichotomy verdict (docs/sid_init_report.md §5),
        # robust to a multi-frame init whose write SEQUENCE differs between
        # orig and rebuild (e.g. Adrenalin: orig clears via a 2-frame $01/$00
        # sweep, the rebuild via a one-shot universal reset). The two streams
        # share an IDENTICAL play (music) stream; only a short init PREFIX —
        # different in length and content — separates them.
        #
        #   Check A  end-of-init chip STATE matches (the priming result).
        #   Check B  the aligned play streams match + lengths are close.
        #
        # When the inits already coincide (shift 0, no init prefix) this
        # reduces to a full prefix match — so engines that reproduce their
        # init verbatim (Cyb II, Hawkeye) are unaffected.
        return _trichotomy_compare(flat_all_a, flat_all_b)

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


