"""Thin facade so callers can ``from ...extract.engine_model import extract``.

The heavy lifting lives in decompile.py. This module wraps it with a
default SID-path lookup and is the entry the CLI / tests use.
"""

from __future__ import annotations

import os
from pathlib import Path

from .decompile import decompile
from .types import EngineModel


def _default_sid_path() -> Path:
    here = Path(__file__).resolve()
    repo_root = here.parents[3]
    return repo_root / 'hvsc84' / 'MUSICIANS' / 'H' / 'Hubbard_Rob' \
        / 'Last_V8_C128_version.sid'


def extract(sid_path: str | os.PathLike | None = None,
            subtune: int | None = None) -> EngineModel:
    """Parse the SID and return the engine model.

    `subtune` is accepted for parity with sibling pipelines' API but is
    not used here: the model describes the whole binary at once and
    callers pick which subtune they care about from `model.routes`.
    """
    path = Path(sid_path) if sid_path else _default_sid_path()
    if not path.exists():
        raise FileNotFoundError(path)
    model = decompile(path)
    if subtune is not None and not (0 <= subtune < model.header.songs):
        raise ValueError(
            f'subtune {subtune} out of range (0..{model.header.songs - 1})'
        )
    return model
