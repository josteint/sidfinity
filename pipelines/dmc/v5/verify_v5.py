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
    writelog_capture, compare_instruction_stream,
)
from src.songlengths import load_database, get_durations
from src.usf.parser import parse_file
from pipelines.dmc.v5.config import DMCV5Config
from pipelines.dmc.v5.extract.to_usf import write_v5_usf
from pipelines.dmc.v5.from_usf import usf_to_model
from pipelines.dmc.v5.composer_v5 import build_v5_sid


def build_from_cfg(cfg: DMCV5Config, hvsc_root: str | None = None) -> bytes:
    """SID -> USF -> SID (always through USF)."""
    root = hvsc_root or os.path.join(_ROOT, 'hvsc84')
    with tempfile.TemporaryDirectory() as td:
        usf_path = write_v5_usf(cfg, td, hvsc_root=root)
        return build_v5_sid(usf_to_model(parse_file(usf_path)))


def verify_v5(cfg: DMCV5Config, hvsc_root: str | None = None) -> dict:
    root = hvsc_root or os.path.join(_ROOT, 'hvsc84')
    orig = os.path.join(root, cfg.sid_path)
    rebuilt = build_from_cfg(cfg, hvsc_root=root)
    db = load_database(os.path.join(root, 'DOCUMENTS', 'Songlengths.md5'))
    durs = get_durations(orig, db)
    from seed_disassembly import parse_psid
    n = parse_psid(orig)['songs']
    with tempfile.NamedTemporaryFile(suffix='.sid', delete=False) as f:
        f.write(rebuilt)
        tmp = f.name
    out = {'subtunes': {}, 'ok': True}
    try:
        for sub in range(n):
            dur = (durs[sub] if durs and sub < len(durs) else 110) * 1.1
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


if __name__ == '__main__':
    from pipelines.dmc.v5.config import KATUSHA
    import json
    print(json.dumps(verify_v5(KATUSHA), indent=2))
