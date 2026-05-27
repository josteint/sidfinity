"""Commando → USF v2 — thin wrapper over the shared adapter.

3 music subtunes + 16 SFX subtunes. Same shape as Monty, on the
shared Hubbard '85 SFX core.
"""

from pipelines.hubbard.to_usf_v2 import write_usf


def write_commando_usf(config, out_dir: str) -> str:
    """Write Commando.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
