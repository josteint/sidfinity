"""DMC family write-log verification.

Verdict = `compare_instruction_stream(mode='trichotomy')` per subtune
at full songlength × 1.1 (Check A end-of-init SID state + Check B play
stream), via siddump --writelog (libsidplayfp ground truth).
"""
from __future__ import annotations

import os
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.jobs import default_jobs
from pipelines.hubbard.verify_cycle import (
    writelog_capture, compare_instruction_stream,
)
from src.songlengths import load_database, get_durations
from src.usf.parser import parse_file
from pipelines.dmc.v4.config import DMCV4Config
from pipelines.dmc.v4.extract.to_usf import write_dmc_usf
from pipelines.dmc.composer_asm import build_dmc_sid

_ROOT = str(Path(__file__).resolve().parents[2])


def build_from_cfg(cfg: DMCV4Config, hvsc_root: str | None = None) -> bytes:
    """SID → USF → SID (always through USF)."""
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    with tempfile.TemporaryDirectory() as td:
        usf_path = write_dmc_usf(cfg, td, hvsc_root=root)
        return build_dmc_sid(parse_file(usf_path))


def verify_dmc(cfg: DMCV4Config, hvsc_root: str | None = None) -> dict:
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    orig = os.path.join(root, cfg.sid_path)
    rebuilt = build_from_cfg(cfg, hvsc_root=root)
    db = load_database(os.path.join(root, 'DOCUMENTS', 'Songlengths.md5'))
    durs = get_durations(orig, db)
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        f.write(rebuilt)
        tmp = f.name
    out = {'subtunes': {}, 'ok': True}
    cia = bool(cfg.cia_period)
    try:
        from seed_disassembly import parse_psid
        from pipelines.hubbard.verify_cycle import writelog_per_irq_capture
        n = parse_psid(orig)['songs']
        _cap = writelog_per_irq_capture if cia else writelog_capture
        # An RSID original is SKIPPED by siddump unless forced, and a skipped
        # capture is EMPTY — which reads as a partial with nothing to
        # localize rather than as a failure to capture. Force it for the
        # orig; the rebuild is always PSID, so the flag is a no-op there.
        rsid = open(orig, 'rb').read(4) == b'RSID'

        def _capture(path, **kw):
            return _cap(path, force_rsid=rsid and path == orig, **kw)

        # Subtunes are independent, and within one subtune the orig and
        # rebuild captures are independent siddump runs over different files.
        # Both were serialized. THREADS, not a Pool: the work is subprocess-
        # bound, and this is called from inside a regression Pool worker where
        # a nested Pool is illegal (daemonic) — see src/jobs.py.
        def _one(sub: int):
            dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
            with ThreadPoolExecutor(max_workers=2) as ex2:
                fa = ex2.submit(_capture, orig, subtune=sub, duration=dur)
                fb = ex2.submit(_capture, tmp, subtune=sub, duration=dur)
                a, b = fa.result(), fb.result()
            if cia:
                # CIA multispeed: the original is driven by a CIA timer at
                # 2-6x. Capture BOTH per play() invocation (the rebuild
                # programs the same latch, so both run at the same rate)
                # and flat-compare the play streams over their overlap +
                # a one-frame length tolerance (Trap C / CIA bucketing).
                r = compare_instruction_stream(a, b)
                la, lb = r['len_all_a'], r['len_all_b']
                # match_all == min(len) already proves the shorter stream
                # is a full prefix of the longer; the length tolerance only
                # guards against a rebuild that HALTS early. At a multispeed
                # rate the capture boundary lands a couple frames off, so
                # the tolerance is relative (0.5%, min 128 writes).
                full = (r['match_all'] == min(la, lb)
                        and abs(la - lb) <= max(128, max(la, lb) // 200))
                return sub, {
                    'is_full': full, 'match': r['match_all'],
                    'overlap': min(la, lb), 'len_a': la, 'len_b': lb,
                }, full
            else:
                r = compare_instruction_stream(a, b, mode='trichotomy')
                return sub, {
                    'is_full': r['is_full'], 'state_match': r['state_match'],
                    'play_match': r['play_match'], 'overlap': r['play_overlap'],
                    'first_play_diff': r.get('first_play_diff'),
                }, r['is_full']

        if n > 1:
            with ThreadPoolExecutor(max_workers=default_jobs(cap=n)) as ex:
                rows = list(ex.map(_one, range(n)))
        else:
            rows = [_one(s) for s in range(n)]
        for sub, entry, full in rows:          # re-assembled in subtune order
            out['subtunes'][sub] = entry
            out['ok'] &= bool(full)
    finally:
        os.unlink(tmp)
    return out
