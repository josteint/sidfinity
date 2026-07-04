"""SID exclusion list — SIDs deliberately kept out of the USF pipeline.

Some SIDs / engine families can't fit into the principled USF
representation without dragging engine-mechanism bookkeeping into
the schema. Rather than pollute USF, those SIDs are listed in
`tools/excluded_sids.json` with a reason; the pipeline (`write_usf` /
`build_from_usf`) refuses them with a clear error pointing back to
the list.

Use:

    from src.exclusions import is_excluded, exclusion_reason
    if is_excluded(sid_path):
        raise PipelineError(f'{sid_path}: {exclusion_reason(sid_path)}')

The exclusion data also flows into the index (`hvsc84.parquet`) via
`tools/build_sid_db.py` (columns `excluded` + `exclusion_reason`)
so queries like "how many SIDs are excluded, and why?" work
without re-reading the JSON.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache


_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_EXCLUSIONS_JSON = os.path.join(_REPO_ROOT, 'tools', 'excluded_sids.json')


class PipelineExclusionError(RuntimeError):
    """Raised when the pipeline is asked to process an excluded SID.

    Message includes the path + reason so the caller can surface it
    directly to the user.
    """
    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(
            f'{path} is excluded from the pipeline.\n'
            f'  Reason: {reason}\n'
            f'  Listed in: tools/excluded_sids.json')


@lru_cache(maxsize=1)
def _load() -> dict[str, str]:
    """Return `{normalized_path: reason}` for all excluded SIDs."""
    try:
        with open(_EXCLUSIONS_JSON) as f:
            data = json.load(f)
    except FileNotFoundError:
        return {}
    return {
        _normalize_path(entry['path']): entry['reason']
        for entry in data.get('entries', [])
    }


def _normalize_path(path: str) -> str:
    """Normalize a SID path for lookup. Strips repo-root prefix and
    leading `./`, returns the rest. So both
    `/abs/.../hvsc84/X.sid` and `hvsc84/X.sid` match the JSON's
    relative paths.
    """
    p = os.path.normpath(path)
    if os.path.isabs(p):
        try:
            p = os.path.relpath(p, _REPO_ROOT)
        except ValueError:
            # Different drive on Windows etc. — fallback to basename.
            p = os.path.basename(p)
    return p.replace(os.sep, '/')


def is_excluded(sid_path: str) -> bool:
    """True iff `sid_path` (absolute or relative) is in the exclusion
    list."""
    return _normalize_path(sid_path) in _load()


def exclusion_reason(sid_path: str) -> str | None:
    """Return the exclusion reason for `sid_path`, or None if not
    excluded."""
    return _load().get(_normalize_path(sid_path))


def all_excluded() -> dict[str, str]:
    """Return `{path: reason}` for every excluded SID. Used by the DB
    builder + diagnostic queries."""
    return dict(_load())


def check_or_raise(sid_path: str) -> None:
    """Raise `PipelineExclusionError` if `sid_path` is excluded; else
    return silently. Pipeline entry points (`write_usf`,
    `build_from_usf`) call this early to fail loud with a clear
    message pointing at the JSON.
    """
    reason = exclusion_reason(sid_path)
    if reason is not None:
        raise PipelineExclusionError(sid_path, reason)
