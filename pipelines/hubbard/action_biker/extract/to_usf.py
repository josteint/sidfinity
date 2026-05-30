"""Action Biker → USF v2 — thin wrapper over the shared adapter.

No SFX, no digi. 3 music subtunes; voice_starts override (subtune 0
skips V3, subtunes 1/2 start at V3) — captured in the engine
constants, not the USF.
"""

from pipelines.hubbard.to_usf import write_usf


def write_action_biker_usf(config, out_dir: str) -> str:
    """Write Action_Biker.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
