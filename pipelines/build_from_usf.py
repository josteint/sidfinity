"""USF → SID public entry point.

Thin wrapper around `pipelines.universal_codegen.emit_sid` — the
universal codegen handles all engine families via USF-content routing.
This module exists to keep the public `build_from_usf` API stable for
external callers while the universal codegen is the actual engine.
"""

from __future__ import annotations

import os

from src.usf import parse_file, validate
from pipelines import universal_codegen


def build_from_usf(usf_path: str, out_path: str, codec=None) -> str:
    """Read `usf_path` + its sample sidecars, produce a SID at `out_path`.

    Dispatch is by USF content (see `universal_codegen.applies_to`),
    never by engine name. Music-only USFs build straight through; USFs
    carrying digi subtunes need the surrounding directory so the
    universal codegen can locate the sample FLAC sidecars.

    `codec` is accepted for backwards compatibility but ignored — the
    universal codegen owns codec choice internally.
    """
    usf = parse_file(usf_path)
    usf_dir = os.path.dirname(os.path.abspath(usf_path))
    validate(usf, usf_dir=usf_dir)

    sid_bytes = universal_codegen.emit_sid(usf, usf_dir=usf_dir)
    with open(out_path, 'wb') as f:
        f.write(sid_bytes)

    try:
        from src.sid_db import record_rebuild
        record_rebuild(out_path)
    except Exception:
        pass
    return out_path
