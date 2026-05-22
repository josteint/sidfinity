"""verify.py — verify a rebuilt SID against the original.

Captures every subtune of both SIDs through py65 and compares the
per-frame register-write stream. Each subtune is checked for `passes`
times its HVSC song length (PAL, 50 Hz) — so the window always covers
the whole subtune plus a loop or two, scaled to the actual song
rather than an arbitrary fixed frame count.

Every capture (each subtune, original and rebuilt, of every engine)
is an independent py65 run, so they all go into one parallel pool —
the longest single capture is the floor, not the sum.
"""

from __future__ import annotations

import os
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
FPS = 50  # PAL frames per second


def subtune_frames(config, passes: float = 2.5,
                   min_frames: int = 600) -> list[int]:
    """Per-subtune frame counts: `passes` x the HVSC duration x 50 Hz.
    Only the shipped subtunes (music + SFX) are returned."""
    durs = get_durations(config.sid_path, load_database(_DB))
    n_sub = len(config.subtunes) + (16 if config.has_sfx else 0)
    return [max(min_frames, round(passes * durs[st] * FPS))
            for st in range(min(n_sub, len(durs)))]


def _capture_hashes(args):
    """One capture job. Returns (job_id, per-frame hashes). A frame's
    hash is hash(tuple of its (reg, val) writes) — order-sensitive,
    matching the byte-exact comparison; a list of ints is cheap to
    pickle back from the worker."""
    job_id, sid, nf, subtune = args
    cap = capture(sid, n_frames=nf, subtune=subtune)
    return job_id, [hash(tuple(cap.raw_frames[k])) for k in range(nf)]


def verify_all(engine_jobs, passes: float = 2.5,
               min_frames: int = 600, jobs: int | None = None):
    """`engine_jobs`: [(config, rebuilt_path), ...]. Captures every
    subtune of every engine — original and rebuilt as separate jobs —
    in one parallel pool, then compares. Returns
    {engine_name: (results, all_exact)}, results = [(subtune, match,
    n_frames), ...]. `jobs` defaults to the core count."""
    cap_jobs, plan, jid = [], {}, 0
    for config, rebuilt in engine_jobs:
        plan[config.name] = []
        for st, nf in enumerate(subtune_frames(config, passes, min_frames)):
            cap_jobs.append((jid,     config.sid_path, nf, st))
            cap_jobs.append((jid + 1, rebuilt,         nf, st))
            plan[config.name].append((st, nf, jid, jid + 1))
            jid += 2
    cap_jobs.sort(key=lambda a: -a[2])      # longest captures dispatched first
    with Pool(jobs) as pool:
        caps = dict(pool.map(_capture_hashes, cap_jobs, chunksize=1))
    out = {}
    for name, subs in plan.items():
        results = [(st, sum(1 for k in range(nf)
                            if caps[oid][k] == caps[rid][k]), nf)
                   for st, nf, oid, rid in subs]
        out[name] = (results, all(m == nf for _, m, nf in results))
    return out


def verify(config, rebuilt_path: str, passes: float = 2.5,
           min_frames: int = 600, jobs: int | None = None):
    """Verify one engine — see verify_all. Returns (results, all_exact)."""
    return verify_all([(config, rebuilt_path)],
                      passes, min_frames, jobs)[config.name]
