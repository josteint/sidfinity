"""USF → SID public entry point.

Two codegens live side by side during the composer rewrite (see
`docs/composer_rewrite_plan.md`):

1. **`pipelines.composer`** — the engine-model-driven composer. Each
   feature on the model has an emitter; the composer produces asm for
   the feature combination the USF declares. No shape selection. As
   phases land, more features land and the composer absorbs more USFs.
2. **`pipelines.universal_codegen`** — the legacy shape dispatcher.
   Handles USFs whose features the composer doesn't yet emit.

Dispatch: try the composer first via `composer.emit_sid_from_usf`;
fall back to the legacy path on the `NotImplementedError` the composer
raises for unsupported features. Both paths are USF-content-routed.
The composer wins back territory phase by phase.
"""

from __future__ import annotations

import os

from src.usf import parse_file, validate
from pipelines import universal_codegen, composer


def build_from_usf(usf_path: str, out_path: str, codec=None) -> str:
    """Read `usf_path` + its sample sidecars, produce a SID at `out_path`."""
    usf = parse_file(usf_path)
    usf_dir = os.path.dirname(os.path.abspath(usf_path))
    validate(usf, usf_dir=usf_dir)

    # Try the composer first. It raises NotImplementedError for USFs
    # whose features it doesn't yet emit — fall through to the legacy
    # path in that case.
    try:
        sid_bytes = composer.emit_sid_from_usf(usf)
    except NotImplementedError:
        sid_bytes = universal_codegen.emit_sid(usf, usf_dir=usf_dir)

    with open(out_path, 'wb') as f:
        f.write(sid_bytes)

    try:
        from src.sid_db import record_rebuild
        record_rebuild(out_path)
    except Exception:
        pass
    return out_path
