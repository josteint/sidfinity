"""GoatTracker V1 — build + writelog-verify a tune through the full pipeline.

SID -> extract -> USF model -> compose -> SID, then flat-stream compare the
rebuild's $D400-$D418 writes against the original (instruction-sequence exact,
[[feedback_verification_modes]]). For canary bring-up + first-divergence
localisation.
"""
from __future__ import annotations

from pipelines.goattracker.v1.extract.engine_model import parse_sid, extract
from pipelines.goattracker.v1.extract.to_usf import model_to_usf
from pipelines.goattracker.v1.composer import build_v1_sid
from pipelines.hubbard.verify_cycle import writelog_capture


def _flat(frames):
    return [(r, v) for f in frames[1:] for (c, r, v) in f]


def _songlength(orig_path: str):
    """Authoritative capture length: HVSC songlength (s). NB a bare duration=None
    makes siddump capture ZERO frames → a vacuous FULL false-pass; the verdict
    MUST span the whole song ([[feedback_subtune_frames_not_arbitrary]])."""
    rel = orig_path[len('hvsc84/'):] if orig_path.startswith('hvsc84/') else orig_path
    try:
        from src import sid_db
        r = sid_db.query("SELECT songlength_s FROM sids WHERE path=?", [rel])
        if r and r[0][0]:
            return float(r[0][0])
    except Exception:
        pass
    return None


def verify(orig_path: str, duration: float | None = None, out: str | None = None):
    usf = model_to_usf(extract(parse_sid(orig_path)))
    sid = build_v1_sid(usf)
    out = out or 'tmp/_gtv1_verify.sid'
    open(out, 'wb').write(sid)
    if duration is None:                     # songlength × 1.1 (never None→0 frames)
        sl = _songlength(orig_path)
        duration = max(8.0, sl * 1.1) if sl else 30.0
    a = _flat(writelog_capture(orig_path, 0, duration=duration))
    b = _flat(writelog_capture(out, 0, duration=duration))
    n = min(len(a), len(b))
    first = next((i for i in range(n) if a[i] != b[i]), None)
    full = first is None and len(a) == len(b)
    return {
        'orig_len': len(a), 'reb_len': len(b),
        'first_div': first, 'is_full': full,
        'match_frac': (first if first is not None else n) / max(len(a), 1),
    }


if __name__ == '__main__':
    import sys
    p = sys.argv[1] if len(sys.argv) > 1 else 'hvsc84/MUSICIANS/T/Topaz/Joker.sid'
    print(p, verify(p))
