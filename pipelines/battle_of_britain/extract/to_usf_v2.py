"""Battle of Britain → USF v2 — thin wrapper over the shared adapter."""

from __future__ import annotations

from pipelines.hubbard.to_usf_v2 import write_usf


def write_battle_of_britain_usf(config, out_dir: str) -> str:
    """Write Battle_of_Britain.usf to `out_dir`."""
    return write_usf(config, out_dir)
