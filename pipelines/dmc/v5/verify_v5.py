"""DMC V5 write-log verification THROUGH USF.

Build path: cfg -> extract -> to_usf -> .usf -> parse_file -> from_usf ->
V5Model -> build_v5_sid (the composer is model-driven and unchanged).
Verdict = `compare_instruction_stream(mode='trichotomy')` per subtune at
full songlength x 1.1 (Check A end-of-init SID state + Check B play
stream), via siddump --writelog (libsidplayfp ground truth).
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[3])
sys.path.insert(0, os.path.join(_ROOT, 'tools'))
sys.path.insert(0, os.path.join(_ROOT, 'tools', 'py65_lib'))

from pipelines.hubbard.verify_cycle import (
    writelog_capture, writelog_per_irq_capture, compare_instruction_stream,
)
from src.songlengths import load_database, get_durations
from src.usf.parser import parse_file
from pipelines.dmc.v5.config import DMCV5Config
from pipelines.dmc.v5.extract.to_usf import write_v5_usf
from pipelines.dmc.v5.from_usf import usf_to_model
from pipelines.dmc.v5.composer_v5 import build_v5_sid


def build_from_cfg(cfg: DMCV5Config, hvsc_root: str | None = None) -> bytes:
    """SID -> USF -> SID (always through USF)."""
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    with tempfile.TemporaryDirectory() as td:
        usf_path = write_v5_usf(cfg, td, hvsc_root=root)
        return build_v5_sid(usf_to_model(parse_file(usf_path)))


def verify_v5(cfg: DMCV5Config, hvsc_root: str | None = None) -> dict:
    root = hvsc_root or os.path.join(_ROOT, 'hvsc85')
    orig = os.path.join(root, cfg.sid_path)
    rebuilt = build_from_cfg(cfg, hvsc_root=root)
    db = load_database(os.path.join(root, 'DOCUMENTS', 'Songlengths.md5'))
    durs = get_durations(orig, db)
    from seed_disassembly import parse_psid
    n = parse_psid(orig)['songs']
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        f.write(rebuilt)
        tmp = f.name
    # family-4's short orig-init fits play1 in siddump frame 0; our longer
    # universal-reset init pushes play1 to frame 1, so the flat per-frame
    # capture misaligns the play streams by one frame (Trap C via differing
    # init length). Capture per play() (drops init prefix, init-length-robust).
    cap = (writelog_per_irq_capture if getattr(cfg, 'family4', False)
           else writelog_capture)
    out = {'subtunes': {}, 'ok': True}
    try:
        for sub in range(n):
            dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
            a = cap(orig, subtune=sub, duration=dur)
            b = cap(tmp, subtune=sub, duration=dur)
            r = compare_instruction_stream(a, b, mode='trichotomy')
            if not r['is_full']:
                # C21 RETRY (ported from v4's verify.py, 2026-08-22): an orig
                # whose INIT SPILLS past the frame-0 bucket makes the flat
                # trichotomy compare misalign from write 0 — Check A compares
                # a partial init against a complete one and the member reports
                # "diverges at position 0" with a meaningless first_diff.
                # Measured on the v5 baseline: 280 of 681 partials (41%) sat
                # in that bucket, and River_Racers' Check A flips False->True
                # under the per-play() capture, where the init prefix is
                # everything before the first play ENTRY and is immune to
                # bucket spill. Re-verify there, then apply the ratified
                # play-stream verdict.
                # ZERO-REGRESSION BY CONSTRUCTION: only reached when the
                # primary compare already failed; a flip to full carries the
                # same strict flat play-stream evidence as every CIA member.
                a2 = writelog_per_irq_capture(orig, subtune=sub, duration=dur,
                                              keep_init=True)
                b2 = writelog_per_irq_capture(tmp, subtune=sub, duration=dur,
                                              keep_init=True)

                def _st(ch):                      # end-of-init chip state
                    st = {}
                    for (_c, reg, val) in (ch[0] if ch else []):
                        st[reg] = val
                    return st
                state2 = _st(a2) == _st(b2)
                r2 = compare_instruction_stream(a2[1:], b2[1:])
                la, lb = r2['len_all_a'], r2['len_all_b']
                if (state2 and r2['match_all'] == min(la, lb)
                        and abs(la - lb) <= max(128, max(la, lb) // 200)):
                    out['subtunes'][sub] = {
                        'is_full': True, 'state_match': True,
                        'play_match': r2['match_all'], 'overlap': min(la, lb),
                        'via': 'per_irq_retry',
                    }
                    continue
                # not FULL either way — but the per-IRQ numbers are the
                # HONEST diagnosis (the flat ones are alignment noise), so
                # report those for the census to cluster on.
                out['ok'] = False
                out['subtunes'][sub] = {
                    'is_full': False, 'state_match': state2,
                    'play_match': r2['match_all'], 'overlap': min(la, lb),
                    'first_play_diff': r2.get('first_diff'),
                    'via': 'per_irq_diag',
                }
                continue
            out['subtunes'][sub] = {
                'is_full': r['is_full'], 'state_match': r['state_match'],
                'play_match': r['play_match'], 'overlap': r['play_overlap'],
                'first_play_diff': r.get('first_play_diff'),
            }
            out['ok'] &= r['is_full']
    finally:
        os.unlink(tmp)
    return out


if __name__ == '__main__':
    from pipelines.dmc.v5.config import KATUSHA
    import json
    print(json.dumps(verify_v5(KATUSHA), indent=2))
