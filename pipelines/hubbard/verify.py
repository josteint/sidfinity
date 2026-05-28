"""verify.py — verify a rebuilt SID against the original.

Each subtune is reduced to one md5 checksum: capture it through py65
for 1.1x its HVSC song length (PAL, 50 Hz), then fold every frame's
register writes, in order, into a running md5. Two SIDs agree on a
subtune iff the checksums match.

Checksums are cached on disk keyed by the SID file's md5, so a
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

from pipelines.hubbard.inst_program import capture          # noqa: E402
from pipelines.hubbard.verify_cycle import writelog_capture  # noqa: E402
from songlengths import load_database, get_durations        # noqa: E402

_DB = os.path.join(ROOT, 'hvsc84', 'DOCUMENTS', 'Songlengths.md5')
_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '.verify_cache.pkl')
FPS = 50  # PAL frames per second


def subtune_frames(config, passes: float = 1.1,
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


def _checksum(args):
    """One subtune -> one checksum. The comparison is on the SID's
    END-OF-FRAME REGISTER STATE — every byte of $D400..$D418 at the
    boundary of each play() call. Snapshots fold in writes from init
    and every play call up to that frame, so a register the play loop
    doesn't re-assert (e.g. $D418 set once in init) still gets
    compared. Two captures match exactly when the SID sees identical
    state at the same frame boundary."""
    key, sid, nf, subtune = args
    cap = capture(sid, n_frames=nf, subtune=subtune)
    h = hashlib.md5()
    for snap in cap.snapshots:
        h.update(snap)
        h.update(b'\n')                       # frame delimiter
    return key, h.hexdigest()


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


def verify_all(engine_jobs, passes: float = 1.1,
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

    # Two pools: 'music' (py65 frame capture) and 'digi' (siddump
    # --writelog cycle capture). Cache keys include the kind so the
    # two checksums of the same (sid, st, nf) never collide.
    need_music: dict = {}
    need_digi: dict = {}
    plan: dict = {}
    for config, rebuilt in engine_jobs:
        plan[config.name] = []
        digi_set = set(config.digi_subtunes or ())
        for st, nf in enumerate(subtune_frames(config, passes, min_frames)):
            kind = 'digi' if st in digi_set else 'music'
            ok_key = key_for(config.sid_path, nf, st, kind)
            rb_key = key_for(rebuilt, nf, st, kind)
            need = need_digi if kind == 'digi' else need_music
            for key, sid in ((ok_key, config.sid_path), (rb_key, rebuilt)):
                if key not in cache and key not in need:
                    if kind == 'digi':
                        need[key] = (sid, nf, st, config.is_rsid)
                    else:
                        need[key] = (sid, nf, st)
            plan[config.name].append((st, ok_key, rb_key))

    if need_music or need_digi:
        with Pool(jobs) as pool:
            if need_music:
                items = [(k, *v) for k, v in need_music.items()]
                items.sort(key=lambda a: -a[2])
                for key, digest in pool.map(_checksum, items, chunksize=1):
                    cache[key] = digest
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
        results = [(st, cache[ok_key] == cache[rb_key])
                   for st, ok_key, rb_key in subs]
        out[name] = (results, all(ok for _, ok in results))
        try:
            from src.sid_db import record_verify
            record_verify(rebuilt_paths[name], results)
        except Exception:
            pass    # db update is best-effort; never break verify
    return out


def verify(config, rebuilt_path: str, passes: float = 1.1,
           min_frames: int = 600, jobs: int | None = None):
    """Verify one engine — see verify_all. Returns (results, all_ok)."""
    return verify_all([(config, rebuilt_path)],
                      passes, min_frames, jobs)[config.name]
