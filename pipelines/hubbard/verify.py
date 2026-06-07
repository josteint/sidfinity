"""verify.py — verify a rebuilt SID against the original.

The verdict is the SID WRITE-LOG STREAM (the CORE TENET), captured via
`siddump --writelog` (libsidplayfp, the project's ground truth) for 1.5x
each subtune's HVSC song length (PAL, 50 Hz). A subtune passes iff the
rebuild's `(reg, val)` write sequence matches the original's at every
write they both produce — the same overlap comparison `find_first_divergence`
uses. This catches within-frame write-order and dispatch/multispeed
divergences that a per-frame register SNAPSHOT cannot see (snapshots are
Trap A in CLAUDE.md — they lose write order and can't model multispeed,
so py65-snapshot verdicts false-pass real bugs). This file used to do
exactly that; it no longer does.

The 1.5x window catches post-songlength divergences that 1.1x missed
(e.g. master-VOL fade-counter wrap on loop). See
`tools/audit_d418_fade.py` for the audit that surfaced the gap.

Captured write-logs are cached on disk keyed by the SID file's md5, so a
subtune is only ever re-captured for a SID whose bytes changed.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import sys
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

from pipelines.hubbard.verify_cycle import (                 # noqa: E402
    writelog_capture, compare_instruction_stream)
# songlengths lives at src/songlengths.py; resolved via the ROOT/src
# entry pushed onto sys.path above (no package prefix in the import).
from songlengths import load_database, get_durations        # noqa: E402

_DB = os.path.join(ROOT, 'hvsc84', 'DOCUMENTS', 'Songlengths.md5')
_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '.verify_cache.pkl')
FPS = 50  # PAL frames per second


def subtune_frames(config, passes: float = 1.5,
                   min_frames: int = 600) -> list[int]:
    """Per-subtune frame counts: `passes` x the HVSC duration x 50 Hz.

    `min_frames` is a fallback floor used in two cases:
      * music subtunes whose HVSC Songlengths entry is 0 / missing
      * digi subtunes (always) — the sample's full register-write stream
        needs a buffer past the nominal HVSC duration to capture the
        rebuilt PSID's dispatcher overhead (otherwise we cut off the
        tail of the sample and false-fail on partial captures).

    For music subtunes with a known non-zero songlength we use exactly
    `passes` x duration (trust the HVSC database) — honouring the floor
    there causes false-positive verify failures on short subtunes whose
    post-song-end behaviour legitimately diverges from the original
    (the engine reads garbage notes past its $8D / $FE sentinel, and
    that garbage isn't part of the song)."""
    durs = get_durations(config.sid_path, load_database(_DB))
    n_sub = (len(config.subtunes)
             + (16 if config.has_sfx else 0)
             + len(config.digi_subtunes or ()))
    digi_set = set(config.digi_subtunes or ())
    frames = []
    for st in range(min(n_sub, len(durs))):
        is_digi = st in digi_set
        natural = round(passes * durs[st] * FPS) if durs[st] > 0 else 0
        if is_digi or natural == 0:
            frames.append(max(min_frames, natural))
        else:
            frames.append(natural)
    return frames


def _file_md5(path: str) -> str:
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def _capture_music(args):
    """One music subtune -> its captured write-log frames (via siddump,
    libsidplayfp ground truth). The original is captured in its native
    RSID/PSID mode; the verdict (in `verify_all`) compares the rebuild's
    write sequence against it over their overlap."""
    key, sid, nf, subtune, force_rsid = args
    frames = writelog_capture(sid, subtune=subtune, duration=nf / FPS,
                              force_rsid=force_rsid)
    return key, frames


def _music_ok(orig_frames, reb_frames) -> bool:
    """Write-log verdict for a music subtune: the rebuild matches the
    original at every write they BOTH produce (find_first_divergence
    overlap semantics), on either the full stream or the post-init play
    stream (the universal-reset init writes legitimately differ from
    HVSC's). Also require the two captures end within one play-frame of
    each other, so a rebuild that stops short still fails."""
    r = compare_instruction_stream(orig_frames, reb_frames)
    overlap_ok = (
        r['match_all'] == min(r['len_all_a'], r['len_all_b'])
        or r['match_post_init'] == min(r['len_post_a'], r['len_post_b']))
    # One busy 3-voice play() frame is well under this; a stopped-early
    # rebuild differs by thousands. This is capture cut-off granularity,
    # not a snapshot fudge.
    close = abs(r['len_all_a'] - r['len_all_b']) <= 64
    return overlap_ok and close


def _checksum_digi(args):
    """One digi subtune -> one content checksum via siddump --writelog.

    Hashes the *flattened (reg, val) write sequence* across all frames,
    ignoring the per-write cycle and the per-frame boundary. Two
    rationale layers:

      - Digi playback is paced by CIA2, not by the per-frame play()
        boundary. The dispatcher's instruction count between init and
        the player's CIA2-start affects when writes happen relative to
        siddump's 19656-cycle frame window, but does NOT affect the
        audio content. A PSID dispatcher with different cycle count
        than the RSID original shifts all writes by a constant offset;
        the (reg, val) sequence itself is identical.

      - This makes the check robust against future dispatcher rewrites
        while still catching real content bugs (wrong vol byte,
        missing or extra bit, wrong sample placement, off-by-one
        boundary read).
    """
    key, sid, nf, subtune, is_rsid = args
    duration = nf / FPS
    frames = writelog_capture(sid, subtune=subtune, duration=duration,
                              force_rsid=is_rsid)
    h = hashlib.md5()
    for frame in frames:
        for _, reg, val in frame:
            h.update(bytes([reg, val]))
    return key, h.hexdigest()


def verify_all(engine_jobs, passes: float = 1.5,
               min_frames: int = 600, jobs: int | None = None):
    """`engine_jobs`: [(config, rebuilt_path), ...]. For every shipped
    subtune of every engine, checksum the original and the rebuilt and
    compare. Checksums are cached keyed by (file md5, subtune, frames);
    only changed SIDs are re-captured, and the misses run in one
    parallel pool. Returns {engine_name: (results, all_ok)}, where
    results = [(subtune, ok), ...]."""
    try:
        with open(_CACHE, 'rb') as f:
            cache = pickle.load(f)
    except Exception:
        cache = {}

    md5s: dict[str, str] = {}

    def key_for(sid: str, nf: int, st: int, kind: str):
        if sid not in md5s:
            md5s[sid] = _file_md5(sid)
        return (md5s[sid], st, nf, kind)

    # Two capture kinds, both via siddump --writelog (libsidplayfp ground
    # truth): 'music_wl' stores the captured frames (compared by overlap in
    # _music_ok); 'digi' stores a flattened-(reg,val) md5 (compared by
    # equality). The kind is part of the cache key. The 'music_wl' tag also
    # invalidates any pre-write-log 'music' (py65 snapshot) cache entries.
    need_music: dict = {}
    need_digi: dict = {}
    plan: dict = {}
    for config, rebuilt in engine_jobs:
        plan[config.name] = []
        digi_set = set(config.digi_subtunes or ())
        for st, nf in enumerate(subtune_frames(config, passes, min_frames)):
            is_digi = st in digi_set
            kind = 'digi' if is_digi else 'music_wl'
            ok_key = key_for(config.sid_path, nf, st, kind)
            rb_key = key_for(rebuilt, nf, st, kind)
            need = need_digi if is_digi else need_music
            # Original captured in its native mode (force_rsid for RSID
            # SIDs). Digi keeps forcing RSID on the rebuild too (CIA-paced
            # digi timing — preserves the prior digi verdict); music captures
            # the rebuild as the PSID it is.
            rb_frsid = config.is_rsid if is_digi else False
            for key, sid, frsid in ((ok_key, config.sid_path, config.is_rsid),
                                    (rb_key, rebuilt, rb_frsid)):
                if key not in cache and key not in need:
                    need[key] = (sid, nf, st, frsid)
            plan[config.name].append((st, ok_key, rb_key, is_digi))

    if need_music or need_digi:
        with Pool(jobs) as pool:
            if need_music:
                items = [(k, *v) for k, v in need_music.items()]
                items.sort(key=lambda a: -a[2])
                for key, frames in pool.map(_capture_music, items,
                                            chunksize=1):
                    cache[key] = frames
            if need_digi:
                items = [(k, *v) for k, v in need_digi.items()]
                items.sort(key=lambda a: -a[2])
                for key, digest in pool.map(_checksum_digi, items,
                                            chunksize=1):
                    cache[key] = digest
        with open(_CACHE, 'wb') as f:
            pickle.dump(cache, f)

    out = {}
    # Need the rebuilt path per engine to write back into hvsc84.db, but
    # plan[name] only carries (st, ok_key, rb_key). Map from name → rebuilt
    # path via the original engine_jobs list.
    rebuilt_paths = {config.name: rebuilt for config, rebuilt in engine_jobs}
    for name, subs in plan.items():
        results = []
        for st, ok_key, rb_key, is_digi in subs:
            if is_digi:
                ok = cache[ok_key] == cache[rb_key]
            else:
                ok = _music_ok(cache[ok_key], cache[rb_key])
            results.append((st, ok))
        out[name] = (results, all(ok for _, ok in results))
        try:
            from src.sid_db import record_verify
            record_verify(rebuilt_paths[name], results)
        except Exception:
            pass    # db update is best-effort; never break verify
    return out


def verify(config, rebuilt_path: str, passes: float = 1.5,
           min_frames: int = 600, jobs: int | None = None):
    """Verify one engine — see verify_all. Returns (results, all_ok)."""
    return verify_all([(config, rebuilt_path)],
                      passes, min_frames, jobs)[config.name]
