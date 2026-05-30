"""USF v2 → SID for the Clever Music Companion engine."""

from __future__ import annotations

import os

from src.usf import parse_file
from pipelines.companion.clever_music import codegen


def build_from_usf(usf_path: str, out_path: str | None = None) -> str:
    usf = parse_file(usf_path)
    if usf.engine != 'clever_music':
        raise ValueError(
            f"expected engine 'clever_music', got {usf.engine!r}")
    if out_path is None:
        base, _ = os.path.splitext(usf_path)
        out_path = base + '.sidfinity.sid'
    sid_bytes = codegen.emit_sid(usf)
    with open(out_path, 'wb') as f:
        f.write(sid_bytes)
    try:
        from src.sid_db import record_rebuild
        record_rebuild(out_path)
    except Exception:
        pass
    return out_path


if __name__ == '__main__':
    import sys
    usf = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/C/Clever_Music/Fairlight.usf'
    out = sys.argv[2] if len(sys.argv) > 2 else None
    p = build_from_usf(usf, out)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
