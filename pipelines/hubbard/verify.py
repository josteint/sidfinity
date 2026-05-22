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
from songlengths import load_database, get_durations        # noqa: E402

_DB = os.path.join(ROOT, 'data', 'C64Music', 'DOCUMENTS', 'Songlengths.md5')
_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                      '.verify_cache.pkl')
FPS = 50  # PAL frames per second


def subtune_frames(config, passes: float = 1.1,
                   min_frames: int = 600) -> list[int]:
    """Per-subtune frame counts: `passes` x the HVSC duration x 50 Hz."""
    durs = get_durations(config.sid_path, load_database(_DB))
    n_sub = len(config.subtunes) + (16 if config.has_sfx else 0)
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

    def key_for(sid: str, nf: int, st: int):
        if sid not in md5s:
            md5s[sid] = _file_md5(sid)
        return (md5s[sid], st, nf)

    need: dict = {}        # cache_key -> (sid, nf, subtune)
    plan: dict = {}        # engine_name -> [(st, orig_key, reb_key)]
    for config, rebuilt in engine_jobs:
        plan[config.name] = []
        for st, nf in enumerate(subtune_frames(config, passes, min_frames)):
            ok_key = key_for(config.sid_path, nf, st)
            rb_key = key_for(rebuilt, nf, st)
            for key, sid in ((ok_key, config.sid_path), (rb_key, rebuilt)):
                if key not in cache and key not in need:
                    need[key] = (sid, nf, st)
            plan[config.name].append((st, ok_key, rb_key))

    if need:
        items = [(key, sid, nf, st) for key, (sid, nf, st) in need.items()]
        items.sort(key=lambda a: -a[2])       # longest captures first
        with Pool(jobs) as pool:
            for key, digest in pool.map(_checksum, items, chunksize=1):
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
