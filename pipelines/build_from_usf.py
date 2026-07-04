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
from src.exclusions import check_or_raise
from pipelines import composer


def build_from_usf(usf_path: str, out_path: str, codec=None) -> str:
    """Read `usf_path` + its sample sidecars, produce a SID at `out_path`.

    Refuses excluded SIDs (see `tools/excluded_sids.json`). The check
    runs on the original .sid path inferred from the .usf path; if
    the .sid is in the exclusion list, raises `PipelineExclusionError`.
    """
    # The exclusion list is keyed by SID path (the source-of-truth
    # file). Infer the .sid path from the .usf path by swapping suffix.
    sid_candidate = usf_path[:-4] + '.sid' if usf_path.endswith('.usf') else usf_path
    check_or_raise(sid_candidate)

    usf = parse_file(usf_path)
    usf_dir = os.path.dirname(os.path.abspath(usf_path))
    validate(usf, usf_dir=usf_dir)

    sid_bytes = composer.emit_sid_from_usf(usf, usf_dir=usf_dir)
    with open(out_path, 'wb') as f:
        f.write(sid_bytes)

    return out_path
