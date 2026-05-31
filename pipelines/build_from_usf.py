"""USF → SID public entry point.

Single dispatch: `pipelines.composer.emit_sid_from_usf` owns the build
path. The composer reads the USF, builds an EngineModel from features,
and emits asm per the model's feature combination. No engine identity
anywhere in the build path.

The composer's hubbard85 branch is the feature-driven asm
composition path — see `pipelines/composer.py` and
[[project_composer_dissolution]] for the architecture.
"""

from __future__ import annotations

import os

from src.usf import parse_file, validate
from pipelines import composer


def build_from_usf(usf_path: str, out_path: str, codec=None) -> str:
    """Read `usf_path` + its sample sidecars, produce a SID at `out_path`."""
    usf = parse_file(usf_path)
    usf_dir = os.path.dirname(os.path.abspath(usf_path))
    validate(usf, usf_dir=usf_dir)

    sid_bytes = composer.emit_sid_from_usf(usf, usf_dir=usf_dir)
    with open(out_path, 'wb') as f:
        f.write(sid_bytes)

    try:
        from src.sid_db import record_rebuild
        record_rebuild(out_path)
    except Exception:
        pass
    return out_path
