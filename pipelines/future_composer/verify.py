"""FC family frame-equivalence verification via siddump --writelog.

The asm composer (when complete) won't produce byte-exact rebuild —
it composes engine code from USF features and its layout choices will
differ from HVSC's. The composer's correctness verdict shifts from
"md5 matches HVSC" to "the SID write stream the chip receives matches
HVSC's, frame-by-frame."

**Frame-exact (not cycle-exact) for music.** The comparator
(`compare_instruction_stream`) drops within-frame cycle timestamps;
the (reg, val) sequence per frame must match but WHEN within the
frame those writes happen is unconstrained. Cycle-strict comparison
is only needed for digi (where the sample timing within the frame
IS the signal — that's `compare_strict` in verify_cycle.py). FC
canaries don't have digi, so frame-exact is the verdict.

This module wraps `pipelines.hubbard.verify_cycle` (engine-agnostic;
used by Hubbard, Companion, and now FC) with FC-specific helpers:

  - `verify_baseline(cfg)` — captures original and rebuilt writelogs
    for every subtune and compares. Sanity baseline: when the rebuild
    is byte-identical (the current binary-patch composer state), the
    writelogs must also match.
  - `verify_asm(cfg)` — same but uses the asm-pipeline composer. The
    real verdict for feature-driven asm work that doesn't preserve
    byte equivalence.

Both return a per-subtune dict with `is_full` (frame stream match) +
the position of the first divergence + total stream lengths.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
from pathlib import Path

from pipelines.hubbard.verify_cycle import (
    writelog_capture, compare_instruction_stream,
)
from pipelines.future_composer.config import FCConfig
from pipelines.future_composer.composer import build_canary
from pipelines.future_composer.composer_asm import (
    build_via_asm, build_via_asm_featuredriven,
)


_ROOT = str(Path(__file__).resolve().parents[2])


def _capture_pair(orig_path: str, rebuilt_bytes: bytes,
                  subtune: int, duration: float) -> dict:
    """Capture writelogs from `orig_path` and a temp file holding
    `rebuilt_bytes`; return the compare_instruction_stream verdict."""
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        f.write(rebuilt_bytes)
        tmp_path = f.name
    try:
        a = writelog_capture(orig_path, subtune=subtune, duration=duration)
        b = writelog_capture(tmp_path, subtune=subtune, duration=duration)
        # Init-trichotomy verdict: the composer emits its OWN init (universal
        # reset + typed priming), so the init write SEQUENCE need not match —
        # only the end-of-init STATE (Check A) + the play stream (Check B).
        # Reduces to a full prefix match when inits already coincide, so
        # verbatim-init canaries (Cyb II, Hawkeye) are unaffected.
        return compare_instruction_stream(a, b, mode='trichotomy')
    finally:
        os.unlink(tmp_path)


def verify_canary(cfg: FCConfig, build_fn, root: str | None = None,
                  duration: float | None = None,
                  subtunes: list[int] | None = None) -> dict:
    """Run the writelog comparison across every subtune.

    `build_fn(cfg)` produces the rebuilt SID bytes. Use
    `composer.build_canary` (binary-patch) or `composer_asm.build_via_asm`.

    Returns a dict keyed by subtune number with the per-subtune verdict.
    Overall `ok` is True iff every subtune is `is_full`.
    """
    if root is None:
        root = _ROOT
    sid_path = str(Path(root) / cfg.sid_path)

    # Read PSID songs count to know how many subtunes to test
    import struct
    with open(sid_path, 'rb') as f:
        d = f.read()
    n_songs = struct.unpack('>H', d[14:16])[0]

    if subtunes is None:
        subtunes = list(range(n_songs))

    rebuilt = build_fn(cfg)
    if isinstance(rebuilt, tuple):       # build_canary returns (bytes, usf_path)
        rebuilt = rebuilt[0]

    md5_orig = hashlib.md5(open(sid_path, 'rb').read()).hexdigest()
    md5_new = hashlib.md5(rebuilt).hexdigest()

    # Resolve per-subtune durations. If `duration` is None (or
    # call-time wants per-sub songlength coverage), read HVSC's
    # Songlengths.md5 for this SID and use songlen * 1.1 + 1s margin
    # per subtune. Matches the project convention from
    # feedback_subtune_frames_not_arbitrary — testing with a fixed
    # short duration hides divergences past that point.
    songlen_path = str(Path(root) / 'hvsc84' / 'DOCUMENTS' / 'Songlengths.md5')
    per_sub_durations: dict[int, float] = {}
    if duration is None:
        with open(songlen_path) as f:
            for line in f:
                if line.startswith(md5_orig):
                    parts = line.rstrip().split('=', 1)[1].split()
                    for i, p in enumerate(parts):
                        m, s = p.split(':')
                        # Songlengths entries may carry millis ("0:19.813")
                        per_sub_durations[i] = int(m) * 60 + float(s)
                    break

    per_sub = {}
    for s in subtunes:
        sub_dur = (per_sub_durations.get(s, 2.0) * 1.1 + 1.0
                   if duration is None else duration)
        per_sub[s] = _capture_pair(sid_path, rebuilt, s, sub_dur)
        per_sub[s]['duration_used'] = sub_dur

    all_full = all(v['is_full'] for v in per_sub.values())
    return {
        'cfg': cfg.name, 'duration': duration, 'subtunes': per_sub,
        'all_full': all_full, 'md5_match': md5_orig == md5_new,
        'md5_orig': md5_orig, 'md5_new': md5_new,
    }


def verify_baseline(cfg: FCConfig, **kw) -> dict:
    """Verify cycle-equivalence using the binary-patch composer.

    Because the binary-patch composer produces byte-identical output
    to HVSC, this MUST report all subtunes is_full. If it doesn't,
    the writelog harness itself is misconfigured (siddump path, FC
    subtune numbering, etc.) — debug there first.
    """
    return verify_canary(cfg, build_canary, **kw)


def verify_asm(cfg: FCConfig, **kw) -> dict:
    """Verify frame-equivalence using the byte-preserving asm
    composer (verbatim engine bytes + USF-derived data tables).

    Since the rebuild is byte-identical to HVSC, this is redundant
    with the md5 check. Kept for symmetry.
    """
    return verify_canary(cfg, build_via_asm, **kw)


def verify_featuredriven(cfg: FCConfig, **kw) -> dict:
    """Verify frame-equivalence using the FEATUREDRIVEN asm composer
    (engine code emitted from USF features; data tables USF-derived).

    The rebuild does NOT byte-match HVSC — the composer chooses its
    own layout. The verdict is per-subtune frame-by-frame writelog
    match.

    Incremental: this WILL report partial progress while engine
    emitters are being filled in. Frame 0 should match (init writes)
    once the song init routine is wired; frame 1+ stays divergent
    until playirq's effect chain is emitted.
    """
    return verify_canary(cfg, build_via_asm_featuredriven, **kw)


def _format_verdict(result: dict) -> str:
    """One-line per-subtune summary for human reading."""
    lines = []
    lines.append(f'=== {result["cfg"]} '
                 f'(md5 {"=" if result["md5_match"] else "≠"}, '
                 f'duration {result["duration"]}s) ===')
    for s, v in sorted(result['subtunes'].items()):
        verdict = '✓' if v['is_full'] else '✗'
        if v.get('mode') == 'trichotomy':
            extra = '' if v['state_match'] else f' STATE≠ {v["state_diff"]}'
            # audio-equivalence flag: ✓ = canonical init boundary → register
            # match provably implies identical audio; ! = non-canonical →
            # ear-test recommended.
            audio = ' audio✓' if v.get('audio_guaranteed') else (
                ' audio?(non-canonical init — ear-test)'
                if v['is_full'] and not v.get('init_canonical') else '')
            lines.append(
                f'  sub {s:2d}  {verdict}  play={v["play_match"]}/'
                f'{v["play_overlap"]} shift={v["shift_d"]} '
                f'init=({v["init_len_a"]},{v["init_len_b"]}) '
                f'post_len=({v["len_post_a"]},{v["len_post_b"]}){extra}{audio}')
        else:
            match = v['match']
            len_a = max(v['len_all_a'], v['len_post_a'])
            len_b = max(v['len_all_b'], v['len_post_b'])
            lines.append(f'  sub {s:2d}  {verdict}  match={match} '
                         f'orig_len={len_a} reb_len={len_b}')
    lines.append(f'  ALL_FULL: {result["all_full"]}')
    return '\n'.join(lines)


if __name__ == '__main__':
    from pipelines.future_composer.hawkeye.config import HAWKEYE
    from pipelines.future_composer.cybernoid_ii.config import CYBERNOID_II

    for cfg in [CYBERNOID_II, HAWKEYE]:
        print('\nBINARY-PATCH PATH:')
        print(_format_verdict(verify_baseline(cfg)))
        print('\nASM PATH:')
        print(_format_verdict(verify_asm(cfg)))
