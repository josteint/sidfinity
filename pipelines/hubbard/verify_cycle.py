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
import re
import subprocess
import tempfile

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
    # Retry on failure/empty: under heavy parallel load a siddump run can die
    # (fork/OOM) with empty stdout, which would silently read as "the SID emits
    # nothing" and corrupt the verdict (false too_few/diverge).
    for _try in range(3):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout:
            break
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
                             force_rsid: bool = False,
                             keep_init: bool = False) -> list[Frame]:
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

    `keep_init=True` prepends the tune's init writes (siddump's `|N`
    chunks — the prefix the `|I` stream drops) as one leading frame. Use
    with `compare_instruction_stream(mode='trichotomy')`: with the init
    prefix present on BOTH sides, the shift recovery aligns past both
    inits and Check A compares the REAL end-of-init chip states. Without
    it, an original that DEFERS a chip's init burst into an early play()
    (Kordiaukis_01_2SID chip 2) has its burst captured while the
    rebuild's init-time writes are invisible — Check A then compares
    primed state vs defaults, a pure observation artifact (ledger C21).
    """
    cmd = [SIDDUMP, sid_path, '--subtune', str(subtune + 1),
           '--duration', str(duration), '--writelog-per-irq', '--raw']
    if force_rsid:
        cmd.append('--force-rsid')
    r = subprocess.run(cmd, capture_output=True, text=True)
    frames: list[Frame] = []
    init_writes: Frame = []

    def _parse(chunk: str) -> Frame:
        toks = [t for t in chunk.split(':') if t != '']
        writes: Frame = []
        for i in range(0, len(toks) - 2, 3):
            try:
                writes.append((int(toks[i]), int(toks[i + 1], 16),
                               int(toks[i + 2], 16)))
            except ValueError:
                pass
        return writes

    for line in r.stdout.splitlines():
        if '|' not in line:
            continue
        # A line may carry MULTIPLE |I chunks (multiple play()s per siddump
        # frame under CIA), plus |N init-prefix chunks. Each chunk =
        # :cyc:reg:val:cyc:reg:val...
        for seg in line.split('|')[1:]:
            if seg.startswith('I'):
                frames.append(_parse(seg[1:]))
            elif seg.startswith('N') and keep_init:
                init_writes += _parse(seg[1:])
    if keep_init and init_writes:
        frames.insert(0, init_writes)
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


# ---------------------------------------------------------------------------
# Straddle-free per-play() capture (from the libsidplayfp pc-trace).
#
# writelog_per_irq_capture buckets writes by play-ENTRY CYCLE, so a CIA play()
# whose execution spans a siddump-frame boundary has its writes split across two
# chunks (a "straddle tail") — noisy for phase observation. This buckets by CPU
# INVOCATION instead (writes executed between consecutive PC==play_addr entries),
# which never straddles. Ground truth (libsidplayfp) — works for CIA/IRQ-armed
# members py65 cannot run.
# ---------------------------------------------------------------------------
_PCT_LINE = re.compile(r'^\s*([0-9a-fA-F]{4})\s+\S\s+'
                       r'([0-9a-fA-F]{2})\s+([0-9a-fA-F]{2})\s+([0-9a-fA-F]{2})\b')
_PCT_STORE = re.compile(r'\b(ST[AXY])\w*', re.I)
_PCT_IDX = re.compile(r'\[d4([0-9a-fA-F]{2})\]', re.I)      # indexed, resolved
_PCT_ABS = re.compile(r'\bST[AXY]a?\s+d4([0-9a-fA-F]{2})\b', re.I)  # absolute


def pctrace_per_play_capture(sid_path: str, subtune: int, play_addr: int,
                             n_frames: int = 12, watch_pcs=None) -> list[Frame]:
    """Straddle-free per-PSID-`play()` write buckets, read off the libsidplayfp
    pc-trace. Each returned frame is the ordered `(reg, val)` `$D400-$D418`
    stores executed by ONE play() invocation (writes between consecutive
    PC==`play_addr` entries; the init prefix before the first entry is
    excluded). No cycle in the tuples — the store's value is read directly off
    the trace (STA→A, STX→X, STY→Y; effective reg from the resolved `[d4XX]`
    for indexed stores or the operand for absolute ones).

    `subtune` is 0-indexed. `n_frames` is siddump 50 Hz frames to trace (~2
    play() invocations each under 2× CIA). `watch_pcs` (optional set of code
    addresses): when given, returns `(plays, hits)` where `hits[i]` is True
    iff invocation i executed any watched PC — used by the DMC play-phase
    observer to classify F by frame-entry reachability. May also be a dict
    {name: set}; `hits[i]` is then the SET of names whose PCs invocation i
    executed (several entry points watched in one trace)."""
    fd, tmp = tempfile.mkstemp(suffix='.pctrace')
    os.close(fd)
    try:
        subprocess.run([SIDDUMP, sid_path, '--subtune', str(subtune + 1),
                        '--pc-trace', tmp, '0', str(n_frames)],
                       capture_output=True, text=True)
        plays: list[Frame] = []
        hits: list[bool] = []
        cur = None
        with open(tmp) as f:
            for line in f:
                m = _PCT_LINE.match(line)
                if not m:
                    continue
                pc = int(m.group(1), 16)
                if pc == play_addr:
                    cur = []
                    plays.append(cur)
                    hits.append(set() if isinstance(watch_pcs, dict)
                                else False)
                if cur is None:
                    continue
                if watch_pcs:
                    if isinstance(watch_pcs, dict):
                        for wk, wset in watch_pcs.items():
                            if pc in wset:
                                hits[-1].add(wk)
                    elif pc in watch_pcs:
                        hits[-1] = True
                st = _PCT_STORE.search(line)
                if not st:
                    continue
                mi = _PCT_IDX.search(line)
                if mi:
                    reg = int(mi.group(1), 16)
                else:
                    ma = _PCT_ABS.search(line)
                    if not ma:
                        continue
                    reg = int(ma.group(1), 16)
                if reg > 0x18:
                    continue
                a, x, y = (int(m.group(2), 16), int(m.group(3), 16),
                           int(m.group(4), 16))
                mn = st.group(1).upper()
                val = x if mn == 'STX' else y if mn == 'STY' else a
                cur.append((reg, val))
        return (plays, hits) if watch_pcs is not None else plays
    finally:
        try:
            os.unlink(tmp)
        except OSError:
            pass


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


def _trichotomy_compare(fa: list, fb: list, close_tol: int = 176,
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
        # Expose the prefix-break point so an alignment failure stays
        # LOCALISABLE (diagnostic only — verdict fields unchanged). Without
        # this, run_member records first_diff=[sub, False] for these, which is
        # indistinguishable from a true Check-A state diff and mis-buckets in
        # divergence_census. The init prefixes usually match here (d=0), so m
        # is the real first play-stream divergence.
        first_play_diff = (m, fa[m], fb[m]) if m < min(la, lb) else None
        return {
            'mode': 'trichotomy', 'shift_d': None,
            'init_len_a': 0, 'init_len_b': 0,
            # An EMPTY-on-both-sides stream (a chip a subtune does not sound)
            # has no alignment to recover but trivially identical end-of-init
            # state — report that honestly instead of a bare False, which
            # mis-buckets in divergence_census as a Check-A state failure.
            'state_match': la == lb == 0, 'state_diff': [],
            'play_match': m, 'play_overlap': n,
            'play_full': m == n == la == lb, 'close': la == lb,
            'len_post_a': la, 'len_post_b': lb,
            'first_play_diff': first_play_diff,
            # A chip that a subtune does not sound has an EMPTY substream on
            # both sides: no alignment to recover, but a trivially exact
            # (and trivially audio-safe) match. Keep the full key set so the
            # multi-chip aggregation below can read it unconditionally.
            'init_canonical': la == lb == 0,
            'init_canonical_orig': la == 0, 'init_canonical_reb': lb == 0,
            'audio_guaranteed': m == n == la == lb,
            'is_full': m == n == la == lb,
        }

    # 2. Find ia = first index where the shifted match begins (music start).
    #    The init prefixes differ, so the match only kicks in after both inits.
    #    Several candidate boundaries can window-match when the init ends in
    #    a run of identical writes (a $01/$00 strobe whose $00 half mirrors
    #    the rebuild's zero clear — Crocketts_Theme): prefer the first
    #    candidate whose end-of-init STATE also matches (Check A), falling
    #    back to the first window match. The state at the TRUE boundary is
    #    reached once the whole strobe is inside the init prefix.
    # Multi-chip: writelog regs are chip-tagged (chip*0x20 + reg), so the
    # state spans 3 chips' register files; a single-chip stream only ever
    # touches [0, 0x19) and the extra entries cancel (equal defaults both
    # sides).
    def _state_at(end_a, end_b):
        sa_ = [0] * 0x60
        sa_[0x18] = sa_[0x38] = sa_[0x58] = 0x0F
        sb_ = list(sa_)
        for reg, val in fa[:end_a]:
            if 0 <= reg < 0x60 and (reg & 0x1F) < 0x19:
                sa_[reg] = val
        for reg, val in fb[:end_b]:
            if 0 <= reg < 0x60 and (reg & 0x1F) < 0x19:
                sb_[reg] = val
        return sa_ == sb_

    ia = max(0, -d)
    limit = min(la - win, ia + max_init)
    first_hit = None
    while ia <= limit:
        if fa[ia:ia + win] == fb[ia + d:ia + d + win]:
            if first_hit is None:
                first_hit = ia
            if _state_at(ia, ia + d):
                break
        ia += 1
    else:
        ia = first_hit if first_hit is not None else max(0, -d)
    ib = ia + d

    # Check B: aligned play stream.
    play_match = aligned_run(d, ia)
    overlap = min(la - ia, lb - ib)
    play_full = play_match == overlap
    post_a, post_b = la - ia, lb - ib
    # `close`: the overlapping play streams match (play_full); this only guards
    # against the rebuild's TAIL (writes past the orig's capture end) being wildly
    # off — a sign of a real loop/dispatch bug. The tail delta is a fixed boundary
    # effect (the rebuild's differing init length shifts where the last play()
    # falls at the duration cutoff), NOT proportional to song length, so a flat
    # absolute tolerance is the right shape. The MAGNITUDE scales with multispeed:
    # at 4x CIA (DMC) the cutoff straddles a few play()s of ~17+ steady writes
    # each, so the band is ~2-4x a 1x tune's. 176 clears the 9 DMC CIA close-tail
    # members (|tail| 85-170, all full play+state match) and the longest FC tune
    # (World_Record_1: 1.66M writes, 66-write tail) without masking a genuinely
    # divergent loop (a real loop/dispatch bug is thousands of writes off, not
    # <176). Bumped 80->176 2026-06-22 (was 64->80 for World_Record_1).
    close = abs(post_a - post_b) <= close_tol
    first_play_diff = None
    if not play_full:
        k = play_match
        first_play_diff = (k, fa[ia + k], fb[ib + k])

    # Check A: end-of-init chip state (the priming result). The unwritten
    # default is the HOST-reset state, not all-zeros: libsidplayfp's psiddrv
    # writes $D418=$0F BEFORE calling init (the_trichotomy.md §1), so a
    # deferred-init engine (zero frame-0 writes) really sits at $D418=$0F —
    # identical to a rebuild that explicitly primes $0F.
    def end_state(flat, end):
        st = [0] * 0x60
        st[0x18] = st[0x38] = st[0x58] = 0x0F
        for reg, val in flat[:end]:
            if 0 <= reg < 0x60 and (reg & 0x1F) < 0x19:
                st[reg] = val
        return st
    sa, sb = end_state(fa, ia), end_state(fb, ib)
    state_match = sa == sb
    state_diff = [(r, sa[r], sb[r]) for r in range(0x60) if sa[r] != sb[r]]

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
                                mode: str = 'legacy',
                                close_tol: int = 176,
                                n_chips: int = 1) -> dict:
    """Compare the (reg, val) sequence the SID receives in two runs.

    `n_chips > 1` (multi-SID: 2SID/3SID) compares EACH chip's stream
    independently and reports full iff every chip is full. Two SID chips are
    independent hardware, so the ORDER of a write to chip 1 vs chip 2 within a
    frame is physically unobservable — the merged chip-tagged stream (reg =
    chip*0x20 + reg&0x1F) must NOT be prefix-compared directly, or an inaudible
    cross-chip reorder reads as a divergence (e.g. Nice_Dream_2SID redirects
    chip 2's res write onto chip 1's $D417, whose position relative to chip 2's
    body the cycle-sorted merge places inconsistently between orig and rebuild).
    Splitting by chip removes cross-chip order from the verdict while keeping
    every within-chip order and value fully checked. On a failing chip the
    returned dict carries THAT chip's localisation fields; when all pass, the
    tail/audio-safety fields are aggregated conservatively (worst tail, AND of
    audio_guaranteed) so a caller's playback-safety gate still sees the worst
    chip.

    Two modes:

    `mode='play_plus_state'` — DRAFT. The principled verdict per
    the init trichotomy (`docs/the_trichotomy.md §5`). Two checks:

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
    if n_chips > 1:
        def _chip(frames, ch):
            lo, hi = ch * 0x20, ch * 0x20 + 0x20
            return [[w for w in fr if lo <= w[1] < hi] for fr in frames]
        rs = [compare_instruction_stream(_chip(a, ch), _chip(b, ch),
                                         skip_init=skip_init, mode=mode,
                                         close_tol=close_tol)
              for ch in range(n_chips)]
        fail = next((r for r in rs if not r['is_full']), None)
        if fail is not None:
            agg = dict(fail)                 # localise on the failing chip
            agg['is_full'] = False
        else:
            # Represent the run by the MOST INFORMATIVE chip, not chip 1: a
            # subtune need not sound every chip (C27), and an unsounded chip's
            # substream is empty on both sides, so `rs[0]` would report
            # play_match=0 / overlap=0 for a member that is exactly correct.
            agg = dict(max(rs, key=lambda r: r['play_overlap']))
            if mode == 'trichotomy':
                # Conservative aggregation for the caller's safety gates.
                agg['audio_guaranteed'] = all(r['audio_guaranteed'] for r in rs)
                worst = max(rs, key=lambda r: abs(r['len_post_a']
                                                  - r['len_post_b']))
                agg['len_post_a'] = worst['len_post_a']
                agg['len_post_b'] = worst['len_post_b']
        agg['per_chip_full'] = [r['is_full'] for r in rs]
        return agg

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
            state = [0] * 0x60
            if frames:
                for _, reg, val in frames[0]:
                    if 0 <= reg < 0x60 and (reg & 0x1F) < 0x19:
                        state[reg] = val
            return state
        state_a = end_state(a)
        state_b = end_state(b)
        state_match = state_a == state_b
        state_diff = [
            (r, state_a[r], state_b[r]) for r in range(0x60)
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
        # PRINCIPLED init-trichotomy verdict (docs/the_trichotomy.md §5),
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
        return _trichotomy_compare(flat_all_a, flat_all_b, close_tol=close_tol)

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




# ---------------------------------------------------------------------------
# THE SPLIT VERDICT — one member, two verification modes, split by REGISTER.
#
# A member that plays digi CONCURRENTLY with music carries both modes in one
# stream: the digi is Mode 2 (cycle-strict — the write timing IS the
# waveform) and the music is Mode 1 (flat `(reg,val)`; within-frame cycle
# position is observation, core tenet Trap B).  This is the C27/C28 shape —
# "split the stream, verify each substream in its own mode, because the two
# halves are physically independent" — applied to REGISTER OWNERSHIP instead
# of chip tag.  Proposed in `docs/digi_parametrization_proposal.md` §5.
#
# ⚠ THE SPLIT IS ONLY SOUND WHERE OWNERSHIP IS EXCLUSIVE, and that is a
# MEASUREMENT, not an assumption.  `tools/register_ownership.py` makes it:
# it pc-traces the busiest window and asks which code writes each register.
# Measured 2026-09-01 over the 92 Digi-Organizer music-paired members:
#
#     69  exclusive        the digi core is the only $D418 writer  -> split OK
#     16  shared           the MUSIC player writes $D418 too       -> see below
#      7  no_fast_writer   no kHz-rate writer in the busy window
#
# So the proposal's premise ("the digi engine owns $D418 exclusively") holds
# for three quarters of the population and NOT for the rest.  For a `shared`
# member the music's own $D418 write lands INSIDE the digi's sample stream,
# so it is a sample slot like any other and belongs on the cycle-strict side
# — which is what this function does.  That is a real, harder constraint on
# the composer (a music-side write it must place cycle-exactly), not a flaw
# in the verdict.  Callers should record the measured ownership class beside
# the verdict rather than assume it.
# ---------------------------------------------------------------------------

DIGI_REGS_D418 = frozenset({0x18})


def compare_split_by_register(a: list[Frame], b: list[Frame],
                              strict_regs=DIGI_REGS_D418,
                              mode: str = 'legacy',
                              close_tol: int = 176,
                              n_chips: int = 1) -> dict:
    """Verify a music+digi capture with each substream in its own mode.

    `strict_regs` — the registers the DIGI engine owns.  Their writes are
    compared cycle-strictly (`compare_strict`); every other register's
    writes are compared as a flat instruction stream
    (`compare_instruction_stream`).

    ⚠ WHERE `strict_regs` COMES FROM IS A PRINCIPLE QUESTION, and it should
    be settled before the first caller rather than after.  The register a
    digi engine owns FOLLOWS FROM ITS TECHNIQUE, and the technique is
    already musical content in the schema (`digi { technique: volume_4bit }`
    ⇒ $D418).  So derive it from the USF's digi declaration.  Do NOT supply
    it from a per-engine table keyed on which player the member came from:
    that is Principle §8's shape — a verdict that needs engine identity —
    even though §8 is written about the composer, and it would put back
    exactly the engine-library indexing the digi schema was designed to
    remove.  A family constant (like `n_chips`, which the pipeline knows
    from the PSID header) is acceptable; an engine name is not.

    Degenerate cases reduce exactly, and both are asserted by the tool's
    self-test:
      * `strict_regs=frozenset()`  -> pure `compare_instruction_stream`
      * `strict_regs` = all 0x00-0x1F over a single-chip capture, on a
        member with no music writes -> pure `compare_strict`

    Returns the two sub-verdicts plus a combined `is_full`.  The register
    masks are matched on `reg & 0x1F`, so a chip-tagged multi-SID capture
    (reg = chip*0x20 + reg&0x1F, ledger C27) splits correctly on every chip.
    """
    strict_regs = frozenset(r & 0x1F for r in strict_regs)

    def _keep(frames, want_strict):
        return [[w for w in fr if ((w[1] & 0x1F) in strict_regs) is want_strict]
                for fr in frames]

    digi = compare_strict(_keep(a, True), _keep(b, True))
    music = compare_instruction_stream(_keep(a, False), _keep(b, False),
                                       mode=mode, close_tol=close_tol,
                                       n_chips=n_chips)

    # compare_strict has no `is_full`: it is full iff every frame's
    # (cycle, reg, val) list matched AND neither side has extra frames.
    digi_full = (digi['match'] == digi['frames']
                 and digi['len_a'] == digi['len_b'])
    return {
        'mode': 'split_by_register',
        'strict_regs': sorted(f'{r:02X}' for r in strict_regs),
        'digi': digi,
        'digi_full': digi_full,
        'music': music,
        'music_full': bool(music['is_full']),
        'is_full': digi_full and bool(music['is_full']),
    }
