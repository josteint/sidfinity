"""DMC family write-log verification.

Verdict = `compare_instruction_stream(mode='trichotomy')` per subtune
at full songlength × 1.1 (Check A end-of-init SID state + Check B play
stream), via siddump --writelog (libsidplayfp ground truth).
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

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
    root = hvsc_root or os.path.join(_ROOT, 'hvsc84')
    with tempfile.TemporaryDirectory() as td:
        usf_path = write_dmc_usf(cfg, td, hvsc_root=root)
        return build_dmc_sid(parse_file(usf_path))


def verify_dmc(cfg: DMCV4Config, hvsc_root: str | None = None) -> dict:
    root = hvsc_root or os.path.join(_ROOT, 'hvsc84')
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
        for sub in range(n):
            dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
            if cia:
                # CIA multispeed: the original is driven by a CIA timer at
                # 2-6x. Capture BOTH per play() invocation (the rebuild
                # programs the same latch, so both run at the same rate)
                # and flat-compare the play streams over their overlap +
                # a one-frame length tolerance (Trap C / CIA bucketing).
                a = writelog_per_irq_capture(orig, subtune=sub, duration=dur)
                b = writelog_per_irq_capture(tmp, subtune=sub, duration=dur)
                r = compare_instruction_stream(a, b)
                la, lb = r['len_all_a'], r['len_all_b']
                # match_all == min(len) already proves the shorter stream
                # is a full prefix of the longer; the length tolerance only
                # guards against a rebuild that HALTS early. At a multispeed
                # rate the capture boundary lands a couple frames off, so
                # the tolerance is relative (0.5%, min 128 writes).
                full = (r['match_all'] == min(la, lb)
                        and abs(la - lb) <= max(128, max(la, lb) // 200))
                out['subtunes'][sub] = {
                    'is_full': full, 'match': r['match_all'],
                    'overlap': min(la, lb), 'len_a': la, 'len_b': lb,
                }
                out['ok'] &= full
            else:
                a = writelog_capture(orig, subtune=sub, duration=dur)
                b = writelog_capture(tmp, subtune=sub, duration=dur)
                r = compare_instruction_stream(a, b, mode='trichotomy')
                out['subtunes'][sub] = {
                    'is_full': r['is_full'], 'state_match': r['state_match'],
                    'play_match': r['play_match'], 'overlap': r['play_overlap'],
                    'first_play_diff': r.get('first_play_diff'),
                }
                out['ok'] &= r['is_full']
    finally:
        os.unlink(tmp)
    return out
