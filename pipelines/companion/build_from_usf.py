"""USF → SID build path for the Companion family.

Unified entry point for all 5 Companion strains. Reads a USF file,
dispatches to the strain's codegen based on `usf.engine`, writes the
resulting PSID to disk.

The strains have fundamentally different play loops (1-byte events
vs 2-byte (note,dur) vs duration counters with embedded commands vs
1-voice stripped variant), so each one's 6502 asm generation lives in
its own subfolder. What's unified here is the public surface: one
`build_from_usf(usf_path, out_path)` for any Companion tune, no
engine-name handling at the caller side.

Each strain exposes `emit_sid(usf) -> bytes` and the dispatcher table
below maps `usf.engine` to that function.
"""

from __future__ import annotations

import os

from src.usf import parse_file, UsfFile


def _strain_dispatch() -> dict:
    """Lazy registry of strain → `emit_sid(usf) -> bytes`. Each entry's
    import is deferred so unrelated strains don't drag in their
    dependencies just to build one tune.
    """
    def _uupa(usf: UsfFile) -> bytes:
        from pipelines.companion.up_up_and_away.codegen import emit_sid
        return emit_sid(usf)
    def _bowden(usf: UsfFile) -> bytes:
        from pipelines.companion.bowden_canonical.codegen import emit_sid
        return emit_sid(usf)
    def _clever(usf: UsfFile) -> bytes:
        from pipelines.companion.clever_music.codegen import emit_sid
        return emit_sid(usf)
    def _yes_tune(usf: UsfFile) -> bytes:
        from pipelines.companion.yes_tune.codegen import emit_sid
        return emit_sid(usf)
    def _henrys(usf: UsfFile) -> bytes:
        from pipelines.companion.henrys_house.codegen import emit_sid
        return emit_sid(usf)
    return {
        'companion':         _uupa,
        'bowden_canonical':  _bowden,
        'clever_music':      _clever,
        'yes_tune':          _yes_tune,
        'henrys_house':      _henrys,
    }


def build_from_usf(usf_path: str, out_path: str | None = None) -> str:
    """Build a Companion-family SID from `usf_path`.

    Routes to the correct strain by `usf.engine`. Default `out_path` is
    the .usf path with `.sidfinity.sid` extension.
    """
    if out_path is None:
        base, _ = os.path.splitext(usf_path)
        out_path = base + '.sidfinity.sid'

    usf = parse_file(usf_path)
    dispatch = _strain_dispatch()
    if usf.engine not in dispatch:
        raise ValueError(
            f"unknown Companion strain {usf.engine!r}; "
            f"known strains: {sorted(dispatch.keys())}")
    sid_bytes = dispatch[usf.engine](usf)
    with open(out_path, 'wb') as f:
        f.write(sid_bytes)
    try:
        from src.sid_db import record_rebuild
        record_rebuild(out_path)
    except Exception:
        pass    # db update is best-effort; never break the build
    return out_path


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print('usage: python -m pipelines.companion.build_from_usf <usf_path> [out_path]')
        sys.exit(1)
    out = build_from_usf(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f'wrote {out} ({os.path.getsize(out)} bytes)')
