"""USF v2 → SID for the Bowden-canonical Companion engine.

The USF is the source of truth. This script reads it, runs codegen,
and writes a complete PSID. The original SID file is not consulted.
"""

from __future__ import annotations

import os

from src.usf import parse_file
from pipelines.companion.bowden_canonical import codegen


def build_from_usf(usf_path: str, out_path: str | None = None) -> str:
    """Read a Bowden-canonical USF, emit a rebuilt PSID."""
    usf = parse_file(usf_path)
    if usf.engine != 'bowden_canonical':
        raise ValueError(
            f"expected engine 'bowden_canonical', got {usf.engine!r}")

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
        'hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.usf'
    out = sys.argv[2] if len(sys.argv) > 2 else None
    p = build_from_usf(usf, out)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
