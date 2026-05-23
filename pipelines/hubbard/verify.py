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

_DB = os.path.join(ROOT, 'data', 'C64Music', 'DOCUMENTS', 'Songlengths.md5')
_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '.verify_cache.pkl')
FPS = 50  # PAL frames per second


def subtune_frames(config, passes: float = 1.1,
                   min_frames: int = 600) -> list[int]:
    """Per-subtune frame counts: `passes` x the HVSC duration x 50 Hz."""
    durs = get_durations(config.sid_path, load_database(_DB))
    n_sub = (len(config.subtunes)
             + (16 if config.has_sfx else 0)
             + len(config.digi_subtunes or ()))
    return [max(min_frames, round(passes * durs[st] * FPS))
            for st in range(min(n_sub, len(durs)))]


def _file_md5(path: str) -> str:
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def _checksum(args):
    """One subtune -> one checksum. Capture it, then fold each frame's
    ordered (register, value) writes into a running md5 — folded in
    frame order, so a reordered or duplicated frame changes the digest
    (a plain XOR would not — XOR is commutative)."""
    key, sid, nf, subtune = args
    cap = capture(sid, n_frames=nf, subtune=subtune)
    h = hashlib.md5()
    for k in range(nf):
        h.update(repr(cap.raw_frames[k]).encode())
        h.update(b'\n')                       # frame delimiter
    return key, h.hexdigest()


def _checksum_digi(args):
    """One digi subtune -> one cycle-strict checksum via siddump
    --writelog. Each frame's full (cycle, reg, val) write list is
    folded in cycle order, so any byte AND any cycle of divergence
    flips the digest. Use this — not `_checksum` — for digi subtunes.
    """
    key, sid, nf, subtune, is_rsid = args
    duration = nf / FPS
    frames = writelog_capture(sid, subtune=subtune, duration=duration,
                              force_rsid=is_rsid)
    h = hashlib.md5()
    # The writelog tool sometimes emits a few extra frames at the end;
    # truncate to the requested nf so both files hash the same window.
    for k in range(min(nf, len(frames))):
        h.update(repr(frames[k]).encode())
        h.update(b'\n')
    # If the capture is shorter than nf (siddump terminated early),
    # pad with empty frames so a truncated capture is distinguishable.
    for k in range(len(frames), nf):
        h.update(b'[]\n')
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
    for name, subs in plan.items():
        results = [(st, cache[ok_key] == cache[rb_key])
                   for st, ok_key, rb_key in subs]
        out[name] = (results, all(ok for _, ok in results))
    return out


def verify(config, rebuilt_path: str, passes: float = 1.1,
           min_frames: int = 600, jobs: int | None = None):
    """Verify one engine — see verify_all. Returns (results, all_ok)."""
    return verify_all([(config, rebuilt_path)],
                      passes, min_frames, jobs)[config.name]
