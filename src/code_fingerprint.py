"""code_fingerprint.py — content hash of an engine's build+verify dependency
set, used by the family batches to invalidate resume-cache rows whose verdict
predates a code change.

A batch's results jsonl is a persisted verdict store: on resume it skips
already-done paths. That is a palimpsest trap — a member recorded FULL under
older code silently carries its stale verdict across a fix, and later surfaces
as a phantom "my fix regressed N FULLs". The cure: stamp every result row with
`code_fingerprint(engine)` and, on resume, reuse a row ONLY if its stored
code_hash equals the current fingerprint. Any code change to the engine's
dependency set re-runs exactly the members it could have affected.

This is safe-by-construction (no need to remember to delete the jsonl) AND
correct under parallel sessions on different engines: a SHARED-code edit
(src/usf, verify_cycle) changes every dependent engine's fingerprint so each
re-verifies; an OTHER-engine edit is not in this engine's dependency set, so it
does not needlessly invalidate this one. Keep each DEPS entry to what THAT
engine actually imports — over-broad is safe (just wastes re-verification) but
over-broad ACROSS engines re-runs a batch when a sibling engine changed.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Shared build+verify dependencies every batched engine imports.
_SHARED = ['src/usf', 'pipelines/hubbard/verify_cycle.py']

# Per-engine dependency roots. A directory is hashed recursively over its *.py;
# a file is hashed directly.
DEPS: dict[str, list[str]] = {
    'dmc_v4':         ['pipelines/dmc'] + _SHARED,
    'dmc_v5':         ['pipelines/dmc'] + _SHARED,
    'fc_standard':    ['pipelines/future_composer'] + _SHARED,
    'goattracker_v1': ['pipelines/goattracker/v1'] + _SHARED,
    'basic_program':  ['pipelines/basic_program'] + _SHARED,
    'music_assembler': ['pipelines/music_assembler'] + _SHARED,
}


def _iter_files(root: Path):
    if root.is_file():
        yield root
    elif root.is_dir():
        yield from sorted(root.rglob('*.py'))


def code_fingerprint(engine: str) -> str:
    """16-hex-char content hash of `engine`'s dependency file set. Deterministic
    across processes (sorted paths, path + bytes hashed)."""
    try:
        roots = DEPS[engine]
    except KeyError:
        raise KeyError(f'unknown engine {engine!r}; add it to '
                       f'code_fingerprint.DEPS') from None
    h = hashlib.sha256()
    for rel in roots:
        for f in _iter_files(ROOT / rel):
            h.update(f.relative_to(ROOT).as_posix().encode())
            h.update(b'\0')
            h.update(f.read_bytes())
            h.update(b'\0')
    return h.hexdigest()[:16]
